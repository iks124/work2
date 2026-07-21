#!/usr/bin/env python3
"""Build the Mind2Web test-split files used by the PolySkill harness.

Downloads task metadata (no HTML, no screenshots) from the public
`osunlp/Multimodal-Mind2Web` dataset via its auto-converted parquet shards,
reading ONLY the metadata columns over HTTP range requests (a few MB total),
dedupes action-level rows into tasks, and writes one JSON file per split:

    data/mind2web/cross_task.json      (177 tasks)
    data/mind2web/cross_website.json   (142 tasks)
    data/mind2web/cross_domain.json    (694 tasks)

(The Multimodal-Mind2Web release is a subset of the original Mind2Web test splits,
which had 252/177/912 tasks — see data/mind2web/README.md.)

Each record: {"task_id", "task", "website", "domain", "subdomain", "url"}.

The ``url`` field is a BEST-EFFORT guess (https://www.<website>.com, or
https://<website> when the name already contains a dot). Mind2Web is a live-web
benchmark: verify/override start URLs for the sites you evaluate, either by
editing the JSON or passing ``--url-map your_map.json`` ({"website": "url"}).

Attribution: Mind2Web (Deng et al., 2023), CC BY 4.0 — https://osu-nlp-group.github.io/Mind2Web/

Usage:
    python scripts/prepare_mind2web.py [--out data/mind2web] [--url-map map.json]
"""
import argparse
import json
import os
import sys

COLUMNS = ["annotation_id", "website", "domain", "subdomain", "confirmed_task"]
SPLITS = {  # HF split name -> output file (PolySkill setting name)
    "test_task": "cross_task.json",
    "test_website": "cross_website.json",
    "test_domain": "cross_domain.json",
}
PARQUET_INDEX = "https://huggingface.co/api/datasets/osunlp/Multimodal-Mind2Web/parquet"


_KNOWN_TLDS = {"com", "org", "net", "gov", "edu", "us", "uk", "io", "co", "fm", "info", "tv", "ai", "me"}


def guess_url(website: str) -> str:
    website = website.strip().lower()
    if "." in website:
        # e.g. "akc.org" / "ca.gov" already end in a TLD; "careers.walmart" /
        # "us.megabus" are subdomains that still need ".com" appended.
        if website.rsplit(".", 1)[-1] in _KNOWN_TLDS:
            return f"https://{website}"
        return f"https://{website}.com"
    return f"https://www.{website}.com"


def fetch_split_tasks(shard_urls, url_map):
    import fsspec
    import pyarrow.parquet as pq

    tasks = {}
    for url in shard_urls:
        with fsspec.open(url, "rb") as f:
            table = pq.read_table(f, columns=COLUMNS)
        for rec in table.to_pylist():
            tid = rec["annotation_id"]
            if tid in tasks:
                continue
            website = rec["website"]
            tasks[tid] = {
                "task_id": tid,
                "task": rec["confirmed_task"],
                "website": website,
                "domain": rec["domain"],
                "subdomain": rec["subdomain"],
                "url": url_map.get(website, guess_url(website)),
            }
    return list(tasks.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/mind2web", help="output directory")
    parser.add_argument("--url-map", default=None,
                        help="JSON file mapping website name -> start URL (overrides guesses)")
    args = parser.parse_args()

    url_map = {}
    if args.url_map:
        url_map = json.load(open(args.url_map))

    import requests
    index = requests.get(PARQUET_INDEX, timeout=60).json()
    shards_by_split = index["default"]

    os.makedirs(args.out, exist_ok=True)
    for hf_split, out_name in SPLITS.items():
        shard_urls = shards_by_split.get(hf_split, [])
        if not shard_urls:
            print(f"WARNING: no parquet shards for split {hf_split}; skipping")
            continue
        print(f"[{hf_split}] reading {len(shard_urls)} shard(s) (metadata columns only)...")
        tasks = fetch_split_tasks(shard_urls, url_map)
        tasks.sort(key=lambda t: t["task_id"])
        out_path = os.path.join(args.out, out_name)
        with open(out_path, "w") as f:
            json.dump(tasks, f, indent=1, ensure_ascii=False)
        print(f"[{hf_split}] wrote {len(tasks)} tasks -> {out_path}")
    print("Done. Review the best-effort `url` fields before running live evaluation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
