"""Mock tests for the self-proposing exploration loop (Task 7.3).

No browser or LLM is required — all I/O is faked via execute_fn/judge_fn seams.
"""
from __future__ import annotations

import gzip
import json
import os
import pickle

import numpy as np
import pytest

from polyskill.exploration.explore_loop import (
    run_self_proposing_exploration,
    _resolve_env_id_for_site,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_traj(dirp: str) -> None:
    """Write a minimal valid trajectory into *dirp*."""
    os.makedirs(dirp, exist_ok=True)
    shot = np.zeros((2, 2, 3), dtype="uint8")
    for i, a in enumerate(["click('1')", "fill('2','x')"]):
        step = {
            "step": i,
            "action": a,
            "reward": 0.0,
            "obs": {
                "goal": "g",
                "screenshot": shot,
                "last_action_error": "",
            },
        }
        with gzip.open(os.path.join(dirp, f"step_{i}.pkl.gz"), "wb") as f:
            pickle.dump(step, f)
    with open(os.path.join(dirp, "summary_info.json"), "w") as f:
        json.dump({"cum_reward": 1.0, "n_steps": 2}, f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_loop_runs_and_induces(tmp_path):
    """The canonical mock test from the spec: 3 iterations, all succeed."""
    calls = {"n": 0}

    def exec_fn(site, pt, i):
        d = str(tmp_path / f"it{i}")
        _fake_traj(d)
        calls["n"] += 1
        return 1.0, d

    stats = run_self_proposing_exploration(
        domain="shopping",
        iterations=3,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["webarena_shopping"],
        execute_fn=exec_fn,
        judge_fn=lambda d, g: True,
    )
    assert calls["n"] == 3
    assert stats["successes"] == 3
    # At least one skill should be induced OR coverage advanced.
    assert stats["skills"]["total_skills"] >= 1 or len(stats["coverage"]) >= 1


def test_stats_keys_present(tmp_path):
    """Return dict has all required keys."""
    stats = run_self_proposing_exploration(
        domain="shopping",
        iterations=1,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["webarena_shopping"],
        execute_fn=lambda site, pt, i: (1.0, None),
        judge_fn=lambda d, g: True,
    )
    for key in ("iterations", "proposals", "skills", "coverage", "successes"):
        assert key in stats, f"Missing key: {key}"


def test_no_success_no_skill(tmp_path):
    """When all tasks fail no skills should be induced."""
    stats = run_self_proposing_exploration(
        domain="shopping",
        iterations=3,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["webarena_shopping"],
        execute_fn=lambda site, pt, i: (0.0, None),
        judge_fn=lambda d, g: False,
    )
    assert stats["successes"] == 0
    assert stats["skills"]["total_skills"] == 0


def test_coverage_advances_on_success(tmp_path):
    """Successful proposals mark target_method as covered."""

    def exec_fn(site, pt, i):
        d = str(tmp_path / f"it{i}")
        _fake_traj(d)
        return 1.0, d

    stats = run_self_proposing_exploration(
        domain="shopping",
        iterations=3,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["webarena_shopping"],
        execute_fn=exec_fn,
        judge_fn=lambda d, g: True,
    )
    # After 3 successful iterations on 3 methods, all three should be covered.
    assert len(stats["coverage"]) >= 1
    for method, covered in stats["coverage"].items():
        assert covered is True


def test_proposals_recorded(tmp_path):
    """proposals list has one entry per iteration."""
    n_iters = 5
    stats = run_self_proposing_exploration(
        domain="shopping",
        iterations=n_iters,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["webarena_shopping"],
        execute_fn=lambda site, pt, i: (0.0, None),
        judge_fn=lambda d, g: False,
    )
    assert len(stats["proposals"]) == n_iters


def test_dev_tools_domain(tmp_path):
    """The dev_tools domain should use its own abstract_methods defaults."""
    calls = {"n": 0}

    def exec_fn(site, pt, i):
        calls["n"] += 1
        return 1.0, None

    stats = run_self_proposing_exploration(
        domain="dev_tools",
        iterations=2,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["gitlab"],
        execute_fn=exec_fn,
        judge_fn=lambda d, g: True,
    )
    assert calls["n"] == 2
    assert stats["successes"] == 2


def test_site_rotation(tmp_path):
    """Sites should be rotated round-robin across iterations."""
    sites_seen = []

    def exec_fn(site, pt, i):
        sites_seen.append(site)
        return 0.0, None

    run_self_proposing_exploration(
        domain="shopping",
        iterations=4,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["site_a", "site_b"],
        execute_fn=exec_fn,
        judge_fn=lambda d, g: False,
    )
    assert sites_seen == ["site_a", "site_b", "site_a", "site_b"]


def test_trajectory_actions_used_for_induction(tmp_path):
    """Actions from the fake trajectory should feed the inducer and produce skills."""

    def exec_fn(site, pt, i):
        d = str(tmp_path / f"it{i}")
        _fake_traj(d)
        return 1.0, d

    stats = run_self_proposing_exploration(
        domain="shopping",
        iterations=2,
        model_config=None,
        storage_path=str(tmp_path / "skills"),
        websites=["webarena_shopping"],
        execute_fn=exec_fn,
        judge_fn=lambda d, g: True,
    )
    # With 2 successful 2-action trajectories, at least one skill should exist.
    assert stats["skills"]["total_skills"] >= 1


# ---------------------------------------------------------------------------
# Bug H: default execute_fn must build a REAL env id, not browsergym/<site>.
# ---------------------------------------------------------------------------


def test_resolve_env_id_maps_known_site(monkeypatch):
    """A known site resolves to whatever get_env_ids_and_task_kwargs returns."""
    import polyskill.evaluation.eval_runner as runner

    captured = {}

    def fake_get(benchmark_config, shuffle_seed=None):
        captured["category"] = benchmark_config.category
        captured["dataset"] = benchmark_config.dataset
        return (["browsergym/webarena.117"], None)

    monkeypatch.setattr(runner, "get_env_ids_and_task_kwargs", fake_get, raising=True)

    env_id = _resolve_env_id_for_site("webarena_shopping")
    assert env_id == "browsergym/webarena.117"
    assert captured["dataset"] == "webarena"
    assert captured["category"] == "shopping"
    # The bug was building this unregistered id:
    assert env_id != "browsergym/webarena_shopping"


def test_resolve_env_id_unmapped_site_raises():
    """An unmappable site (e.g. live amazon) raises a clear NotImplementedError."""
    with pytest.raises(NotImplementedError) as exc:
        _resolve_env_id_for_site("amazon")
    assert "amazon" in str(exc.value)


def test_resolve_env_id_live_if_webarena_available():
    """When the webarena package is installed, resolution returns a real env id."""
    try:
        env_id = _resolve_env_id_for_site("webarena_shopping")
    except NotImplementedError:
        pytest.skip("webarena env ids not registered in this environment")
    assert env_id.startswith("browsergym/webarena.")
