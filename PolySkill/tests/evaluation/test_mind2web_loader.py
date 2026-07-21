"""Tests for the Mind2Web split loader (``polyskill.evaluation.mind2web``).

Uses a tmp fixture JSON so it never depends on the real ``data/mind2web`` files.
"""
import json

import pytest

from polyskill.evaluation.mind2web import SETTING_FILES, load_mind2web_split


def _write_split(dir_path, name, records):
    p = dir_path / name
    p.write_text(json.dumps(records))
    return p


def test_load_valid_split(tmp_path):
    records = [
        {"task_id": "a1", "task": "book a car", "website": "budget",
         "domain": "Travel", "subdomain": "Car rental", "url": "https://www.budget.com"},
        {"task_id": "a2", "task": "find a hotel", "website": "airbnb",
         "domain": "Travel", "subdomain": "Hotel", "url": "https://www.airbnb.com"},
    ]
    _write_split(tmp_path, SETTING_FILES["cross-task"], records)

    tasks = load_mind2web_split("cross-task", str(tmp_path))
    assert len(tasks) == 2
    assert tasks[0]["task_id"] == "a1"
    assert tasks[0]["url"] == "https://www.budget.com"
    assert tasks[1]["task"] == "find a hotel"


def test_empty_url_records_skipped(tmp_path):
    records = [
        {"task_id": "ok", "task": "do it", "website": "budget", "url": "https://www.budget.com"},
        {"task_id": "bad", "task": "no url", "website": "x", "url": "   "},   # empty -> skipped
        {"task_id": "missing", "task": "no url key", "website": "y"},          # no url -> skipped
    ]
    _write_split(tmp_path, SETTING_FILES["cross-website"], records)

    tasks = load_mind2web_split("cross-website", str(tmp_path))
    assert [t["task_id"] for t in tasks] == ["ok"]


def test_bad_setting_raises(tmp_path):
    with pytest.raises((ValueError, KeyError)) as exc:
        load_mind2web_split("cross-galaxy", str(tmp_path))
    # The error names the valid options so the user can recover.
    msg = str(exc.value)
    assert "cross-task" in msg and "cross-website" in msg and "cross-domain" in msg


def test_missing_file_raises_with_prepare_hint(tmp_path):
    # Valid setting, but no file on disk.
    with pytest.raises(FileNotFoundError) as exc:
        load_mind2web_split("cross-domain", str(tmp_path))
    msg = str(exc.value)
    assert "prepare_mind2web.py" in msg
