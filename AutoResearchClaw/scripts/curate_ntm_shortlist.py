#!/usr/bin/env python3
"""Curate the NTM/continual-learning literature shortlist from API results."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


EXACT_PRIORITIES = (
    "neural turing machines",
    "hybrid computing using a neural network with dynamic external memory",
    "scaling continual learning to 300+ tasks",
    "learning to prompt for continual learning",
    "dualprompt",
    "coda-prompt",
    "expandable subspace ensemble",
    "mos: model surgery",
    "moe-adapters++",
    "continual learning with hypernetworks",
    "continual learning with dependency preserving hypernetworks",
    "continual hypertransformer",
    "learning to route for dynamic adapter composition",
    "mixture of experts meets prompt-based continual learning",
    "training consistent mixture-of-experts-based prompt generator",
    "adaptive adapter routing",
    "adapter merging with centroid prototype mapping",
    "dynamic lora-experts",
    "evolving parameterized prompt memory",
    "scaling memory-augmented neural networks",
)


def relevance(row: dict[str, object]) -> float:
    title = str(row.get("title", "")).lower()
    abstract = str(row.get("abstract", "")).lower()
    text = f"{title} {abstract}"
    score = 0.0

    for rank, phrase in enumerate(EXACT_PRIORITIES):
        if phrase in title:
            score += 30.0 - 0.25 * rank

    for phrase, weight in (
        ("continual learning", 6.0),
        ("class-incremental", 6.0),
        ("incremental learning", 4.0),
        ("neural turing", 8.0),
        ("differentiable memory", 7.0),
        ("external memory", 4.0),
        ("adapter", 4.0),
        ("mixture of experts", 4.0),
        ("mixture-of-experts", 4.0),
        ("prompt", 2.5),
        ("hypernetwork", 4.0),
        ("task-agnostic", 3.0),
        ("vision transformer", 2.0),
    ):
        if phrase in title:
            score += weight
        elif phrase in abstract:
            score += weight * 0.35

    # Citations break ties but cannot rescue an irrelevant paper.
    citations = int(row.get("citation_count", 0) or 0)
    if score > 0:
        score += min(3.0, math.log10(citations + 1))
    return score


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: curate_ntm_shortlist.py CANDIDATES.jsonl SHORTLIST.jsonl")
        return 2

    source, destination = map(Path, sys.argv[1:])
    rows = [
        json.loads(line)
        for line in source.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ranked = sorted(rows, key=relevance, reverse=True)

    shortlist: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in ranked:
        score = relevance(row)
        title = str(row.get("title", "")).strip()
        key = title.casefold()
        if score < 8.0 or not title or key in seen:
            continue
        seen.add(key)
        curated = dict(row)
        curated["relevance_score"] = round(min(score / 40.0, 1.0), 3)
        curated["quality_score"] = round(
            min(0.55 + math.log10(int(row.get("citation_count", 0) or 0) + 1) / 8, 1.0),
            3,
        )
        curated["keep_reason"] = (
            "Curated from real API results for direct methodological, "
            "baseline, or foundational relevance."
        )
        shortlist.append(curated)
        if len(shortlist) >= 30:
            break

    destination.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in shortlist),
        encoding="utf-8",
    )
    print(f"selected {len(shortlist)} of {len(rows)} candidates")
    for row in shortlist:
        print(f"- {row['title']}")
    return 0 if len(shortlist) >= 15 else 1


if __name__ == "__main__":
    raise SystemExit(main())
