#!/usr/bin/env python3
"""Build traceable knowledge cards directly from real API metadata."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: build_verified_knowledge_cards.py SHORTLIST.jsonl CARDS_DIR")
        return 2

    shortlist_path = Path(sys.argv[1])
    cards_dir = Path(sys.argv[2])
    cards_dir.mkdir(parents=True, exist_ok=True)
    for old_card in cards_dir.glob("card-*.md"):
        old_card.unlink()

    rows = [
        json.loads(line)
        for line in shortlist_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    for index, row in enumerate(rows, start=1):
        title = clean(row.get("title"))
        abstract = clean(row.get("abstract"))
        authors = ", ".join(
            clean(author.get("name"))
            for author in row.get("authors", [])
            if isinstance(author, dict) and clean(author.get("name"))
        )
        source_url = clean(row.get("url"))
        doi = clean(row.get("doi"))
        arxiv_id = clean(row.get("arxiv_id"))
        source = clean(row.get("source"))
        venue = clean(row.get("venue"))
        year = clean(row.get("year"))
        cite_key = clean(row.get("cite_key"))

        card = f"""# {title}

## Bibliographic record

- Authors: {authors or "Not provided by source"}
- Year: {year or "Unknown"}
- Venue: {venue or "Not provided by source"}
- DOI: {doi or "Not provided"}
- arXiv: {arxiv_id or "Not provided"}
- Source: {source or "Unknown"}
- Cite key: {cite_key or "Not provided"}
- URL: {source_url or "Not provided"}

## Verified abstract

{abstract or "The literature API did not provide an abstract. Consult the linked primary source before making methodological or empirical claims."}

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
"""
        (cards_dir / f"card-{index:02d}.md").write_text(card, encoding="utf-8")

    print(f"built {len(rows)} verified cards in {cards_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
