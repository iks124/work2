"""Load Mind2Web test-split files for live BrowserGym evaluation.

The PolySkill harness evaluates Mind2Web by *executing* each task live in an
``browsergym/openended`` environment (start URL + goal text) and judging success
with an automatic GPT-4.1 WebJudge -- the benchmark ships only human trajectories,
so success is measured by the judge both during skill induction and at test time.

Split files are produced by ``scripts/prepare_mind2web.py`` (see docs/MIND2WEB.md)
and land in ``data/mind2web/{cross_task,cross_website,cross_domain}.json``. Each is a
JSON array of records::

    {"task_id": ..., "task": ..., "website": ..., "domain": ...,
     "subdomain": ..., "url": ...}
"""
from __future__ import annotations

import json
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

# Human-friendly setting name -> split file basename.
SETTING_FILES = {
    "cross-task": "cross_task.json",
    "cross-website": "cross_website.json",
    "cross-domain": "cross_domain.json",
}


def load_mind2web_split(setting: str, split_dir: str = "data/mind2web") -> List[dict]:
    """Return the list of task records for a Mind2Web ``setting``.

    Args:
        setting: one of ``cross-task`` / ``cross-website`` / ``cross-domain``.
        split_dir: directory holding the split JSON files (default ``data/mind2web``).

    Raises:
        ValueError: if ``setting`` is not a recognised split.
        FileNotFoundError: if the split file is missing (with a hint to run the
            ``scripts/prepare_mind2web.py`` generator).

    Records missing a ``task_id``/``task``/``url`` or with an empty ``url`` are
    skipped with a warning so a partially-prepared file still yields the usable
    tasks rather than crashing the run.
    """
    if setting not in SETTING_FILES:
        valid = ", ".join(sorted(SETTING_FILES))
        raise ValueError(
            f"Unknown Mind2Web setting {setting!r}; valid options are: {valid}."
        )

    path = os.path.join(split_dir, SETTING_FILES[setting])
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Mind2Web split file not found: {path}. "
            f"Generate it by running `python scripts/prepare_mind2web.py` "
            f"(see docs/MIND2WEB.md)."
        )

    with open(path, "r") as f:
        records = json.load(f)

    tasks: List[dict] = []
    for rec in records:
        if not isinstance(rec, dict):
            logger.warning("Skipping non-dict Mind2Web record: %r", rec)
            continue
        task_id = rec.get("task_id")
        task = rec.get("task")
        url = rec.get("url")
        if not task_id or not task or not url or not str(url).strip():
            logger.warning(
                "Skipping Mind2Web record with missing task_id/task/url (task_id=%r).",
                task_id,
            )
            continue
        tasks.append(rec)

    return tasks
