"""Bug B regression: online skill induction must actually fire on the WebArena
entrypoint, and per-task trajectories must not overwrite each other.

We exercise ``SkillInductionEvaluator._run_and_induce`` directly with:
  * ``eval_loop.run_example`` monkeypatched to write a real fake per-task
    trajectory directory (2 steps + summary cum_reward=1.0) into the dir the
    method actually passes as ``debug_dirs[0]``, and
  * the LLM judge stubbed to success (so we keep the REAL induction path:
    load_trajectory(dir) -> SimpleSkillInducer.induce_skill -> a stored skill).

Asserts a skill is stored AND that two different env_ids write to two different
directories (the original bug reused output_dirs[0] for every task and read back
a nonexistent ``<env_id>/trajectory.pb.xz``, so induction never ran).
"""
import gzip
import json
import os
import pickle

from polyskill.evaluation import eval_loop
from polyskill.evaluation.eval_config import RunnerConfig
from polyskill.experiments.run_eval_with_skill_induction import SkillInductionEvaluator


def _write_fake_trajectory(out_dir: str) -> None:
    """Write a 2-step, reward-1.0 trajectory exactly where run_example would."""
    os.makedirs(out_dir, exist_ok=True)
    for i, action in enumerate(["click('3')", "fill('3', 'switch game')"]):
        step = {
            "step": i,
            "action": action,
            "reward": 0.0,
            "obs": {"goal": "find a switch game", "screenshot": None, "last_action_error": ""},
        }
        with gzip.open(os.path.join(out_dir, f"step_{i}.pkl.gz"), "wb") as f:
            pickle.dump(step, f)
    with open(os.path.join(out_dir, "summary_info.json"), "w") as f:
        json.dump({"cum_reward": 1.0, "n_steps": 2, "goal": "find a switch game"}, f)


def _make_evaluator(storage_path: str) -> SkillInductionEvaluator:
    """Build an evaluator without going through YAML config loading."""
    ev = SkillInductionEvaluator.__new__(SkillInductionEvaluator)
    ev.skill_config = {
        "enabled": True,
        "use_reward_signal": False,
        "judge_method": "webjudge_general",
        "score_threshold": 3,
        "storage_path": storage_path,
        "min_actions": 2,
        "max_actions": 8,
        "judge_model": {"provider": "openai", "name": "gpt-4o", "temperature": 0.0},
    }

    class _Cfg:
        runner = RunnerConfig(threads=1, seed=7, timeout_secs=60)

    ev.eval_config = _Cfg()
    return ev


def test_induction_fires_and_dirs_are_per_task(tmp_path, monkeypatch):
    storage = str(tmp_path / "skills")
    output_dir = str(tmp_path / "run_out")
    os.makedirs(output_dir, exist_ok=True)

    # Reset the cached inducer singleton so this test gets a fresh storage.
    import polyskill.core.online_hook as oh
    monkeypatch.setattr(oh, "_skill_inducer_instance", None, raising=False)

    seen_seeds = []
    written_dirs = []

    def fake_run_example(env_id, task_kwargs, agent_config, benchmark_config,
                         debug_dirs=None, timeout=600, seed=None):
        out_dir = debug_dirs[0]
        written_dirs.append(out_dir)
        seen_seeds.append(seed)
        _write_fake_trajectory(out_dir)
        return 1.0

    monkeypatch.setattr(eval_loop, "run_example", fake_run_example, raising=True)

    # Stub the LLM judge to success, keeping the real induction path intact.
    async def _judge_ok(*a, **k):
        return True

    monkeypatch.setattr(oh, "judge_trajectory_success", _judge_ok, raising=True)

    ev = _make_evaluator(storage)

    # --- Task 1 ---
    reward1, skill1, judged1 = ev._run_and_induce(
        env_id="browsergym/webarena.21",
        task_kwargs=None,
        agent_config=None,
        benchmark_config=None,
        output_dir=output_dir,
        judge_method="webjudge_general",
        score_threshold=3,
    )
    assert reward1 == 1.0
    assert skill1 is not None, "induction did not fire for task 1"
    assert judged1 is True

    # --- Task 2 (different env_id) ---
    reward2, skill2, judged2 = ev._run_and_induce(
        env_id="browsergym/webarena.99",
        task_kwargs=None,
        agent_config=None,
        benchmark_config=None,
        output_dir=output_dir,
        judge_method="webjudge_general",
        score_threshold=3,
    )
    assert reward2 == 1.0

    # Two different env_ids -> two different per-task directories (no overwrite).
    assert len(written_dirs) == 2
    assert written_dirs[0] != written_dirs[1]
    assert written_dirs[0] == os.path.join(output_dir, "browsergym_webarena.21")
    assert written_dirs[1] == os.path.join(output_dir, "browsergym_webarena.99")
    # Both task dirs still hold their own step files (first wasn't clobbered).
    assert os.path.exists(os.path.join(written_dirs[0], "step_0.pkl.gz"))
    assert os.path.exists(os.path.join(written_dirs[1], "step_0.pkl.gz"))

    # The seed was wired through from eval_config.runner.seed (Bug E).
    assert seen_seeds == [7, 7]

    # A skill was actually stored on disk (online induction genuinely fired).
    from polyskill.core.simple_inducer import SimpleSkillInducer
    inducer = SimpleSkillInducer(storage_path=storage)
    assert len(inducer.get_skills()) >= 1


def test_mind2web_per_task_dirs_and_judged_sr(tmp_path, monkeypatch):
    """Mind2Web: two tasks share env id ``browsergym/openended`` but get distinct
    per-task dirs (keyed on task_id), and the judged SR comes from the judge verdicts.
    """
    storage = str(tmp_path / "skills_m2w")
    output_dir = str(tmp_path / "run_out_m2w")
    os.makedirs(output_dir, exist_ok=True)

    import polyskill.core.online_hook as oh
    monkeypatch.setattr(oh, "_skill_inducer_instance", None, raising=False)

    written_dirs = []

    def fake_run_example(env_id, task_kwargs, agent_config, benchmark_config,
                         debug_dirs=None, timeout=600, seed=None):
        out_dir = debug_dirs[0]
        written_dirs.append(out_dir)
        _write_fake_trajectory(out_dir)
        return 0.0  # openended gold reward is always 0.0

    monkeypatch.setattr(eval_loop, "run_example", fake_run_example, raising=True)

    # Judge success keyed on the trajectory path: task "good" passes, "bad" fails.
    async def _judge_by_path(trajectory_path, *a, **k):
        return "good" in trajectory_path

    monkeypatch.setattr(oh, "judge_trajectory_success", _judge_by_path, raising=True)

    ev = _make_evaluator(storage)

    common = dict(
        env_id="browsergym/openended",
        agent_config=None,
        benchmark_config=None,
        output_dir=output_dir,
        judge_method="webjudge_online_mind2web",
        score_threshold=3,
    )

    reward1, skill1, judged1 = ev._run_and_induce(
        task_kwargs={"start_url": "https://a.com", "goal": "do A", "task_id": "good-001"},
        index=0, **common,
    )
    reward2, skill2, judged2 = ev._run_and_induce(
        task_kwargs={"start_url": "https://b.com", "goal": "do B", "task_id": "bad-002"},
        index=1, **common,
    )

    # Gold reward is 0.0 for both; success is judge-based.
    assert reward1 == 0.0 and reward2 == 0.0
    assert judged1 is True and judged2 is False

    # Two distinct per-task dirs despite the shared env id (keyed on task_id).
    assert len(written_dirs) == 2
    assert written_dirs[0] != written_dirs[1]
    assert written_dirs[0] == os.path.join(output_dir, "0000_good-001")
    assert written_dirs[1] == os.path.join(output_dir, "0001_bad-002")

    # Judged SR is computed from the stubbed verdicts: 1 of 2.
    judged_successes = int(judged1) + int(judged2)
    assert judged_successes / 2 == 0.5

    # The judged-success task induced a skill; the judged-failure task did not.
    assert skill1 is not None
    assert skill2 is None
