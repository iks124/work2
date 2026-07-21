"""End-to-end pipeline smoke tests.

`test_full_pipeline_stubbed` drives the REAL PolySkill stack
(make_agent -> HsmV3ASIAgentWithInduction -> eval_loop.run_example -> trajectory
-> load_trajectory -> skill induction) with ONLY the LLM and the browser stubbed.
It needs no API keys and no MiniWoB HTML, and proves the harness wiring is intact.

`test_webarena_real` runs a genuine BrowserGym WebArena shopping episode with a
real model; skipped unless OPENAI_API_KEY and WA_SHOPPING are set.

`test_mind2web_real` runs a live Mind2Web openended task (best-effort guessed URL)
and asserts the harness degrades gracefully into a readable, judge-able trajectory;
skipped unless OPENAI_API_KEY is set and data/mind2web/cross_task.json exists.
"""
import os
import numpy as np
import pytest

from polyskill.evaluation import eval_loop
from polyskill.evaluation.eval_config import AgentConfig, BenchmarkConfig
from polyskill.trajectory import load_trajectory

_M2W_SPLIT = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "mind2web", "cross_task.json"
)


class _FakeEnv:
    """Minimal BrowserGym-shaped env: terminates with reward 1.0 after one step."""

    def __init__(self, *args, **kwargs):
        self._n = 0

    def _obs(self):
        return {
            "goal": "search for a switch game and open it",
            "axtree_txt": "RootWebArea\n  textbox 'Search' [3]\n  button 'OK' [5]",
            "screenshot": np.zeros((4, 4, 3), dtype=np.uint8),
            "last_action_error": "",
        }

    def reset(self, *a, **k):
        return self._obs(), {}

    def step(self, action):
        # Terminate after two steps so the induced skill clears the inducer's
        # min_actions=2 threshold (a 1-action trajectory is too short to store).
        self._n += 1
        terminated = self._n >= 2
        reward = 1.0 if terminated else 0.0
        return self._obs(), reward, terminated, False, {}

    def close(self):
        pass


def test_full_pipeline_stubbed(tmp_path, monkeypatch):
    # Stub the LLM everywhere (planner + executor share FoundationModel.generate).
    # The response carries BOTH a ```...``` plan (consumed by the planner) and an
    # <action> payload (consumed by the executor) so the hierarchical planner is
    # actually exercised end-to-end (Bug C regression).
    from polyskill.model import fm
    stub_response = (
        "Plan: locate the search box and submit the query.\n"
        "```type the game name into the search box```\n"
        "<action>click('5')</action>"
    )
    monkeypatch.setattr(
        fm.FoundationModel, "generate",
        lambda self, **kw: stub_response, raising=True,
    )
    # Stub the browser: real make_agent/run_example, fake env.
    monkeypatch.setattr(eval_loop.gym, "make", lambda *a, **k: _FakeEnv(), raising=True)

    out_dir = tmp_path / "wa_smoke"

    # Capture the agent so we can assert the planner ran (eval_loop.make_agent is
    # the real factory; we wrap it to grab the constructed agent instance).
    captured = {}
    real_make_agent = eval_loop.make_agent

    def _capturing_make_agent(cfg):
        agent = real_make_agent(cfg)
        captured["agent"] = agent
        return agent

    monkeypatch.setattr(eval_loop, "make_agent", _capturing_make_agent, raising=True)

    reward = eval_loop.run_example(
        "browsergym/miniwob.click-test",
        None,
        AgentConfig(name="hsm_v3", model_config_name=None,
                    model={"provider": "openai", "name": "gpt-4.1"}),
        BenchmarkConfig(dataset="miniwob", max_steps=3, headless=True),
        debug_dirs=[str(out_dir)],
        timeout=30,
    )
    assert reward == 1.0

    # Bug C: the hierarchical planner must have actually run (non-None subtask),
    # i.e. eval_loop reset the agent and the planner did not silently no-op.
    agent = captured["agent"]
    action, info = agent.get_action(_FakeEnv()._obs())
    assert info.get("subtask") is not None
    assert "search box" in info["subtask"]

    # The harness wrote a clean trajectory the judge/induction can read.
    traj = load_trajectory(str(out_dir))
    assert traj.success is True
    assert len(traj.actions) >= 2

    # Real induction over the real trajectory's actions -> a skill is stored.
    from polyskill.core.simple_inducer import SimpleSkillInducer
    inducer = SimpleSkillInducer(storage_path=str(tmp_path / "skills"))
    skill = inducer.induce_skills_from_agent_state(
        actions=traj.actions, task=traj.goal, success=True)
    stats = inducer.get_comprehensive_stats()
    assert isinstance(stats, dict)
    # The full online pipeline produced a stored, reusable skill.
    assert skill is not None
    assert stats.get("total_skills", 0) >= 1
    assert len(inducer.get_skills()) >= 1


@pytest.mark.llm
@pytest.mark.e2e
@pytest.mark.skipif(
    not (os.getenv("OPENAI_API_KEY") and os.getenv("WA_SHOPPING")),
    reason="needs OPENAI_API_KEY and WA_SHOPPING for a real WebArena shopping episode",
)
def test_webarena_real(tmp_path):
    from polyskill.evaluation import eval_runner

    env_ids, task_kwargs = eval_runner.get_env_ids_and_task_kwargs(
        BenchmarkConfig(dataset="webarena", category="shopping", max_examples=1),
        shuffle_seed=0,
    )
    assert env_ids, "no WebArena shopping env resolved"
    env_id = env_ids[0]

    reward = eval_loop.run_example(
        env_id,
        None if not task_kwargs else task_kwargs[0],
        AgentConfig(name="hsm_v3", model={"provider": "openai", "name": "gpt-4.1"}),
        BenchmarkConfig(dataset="webarena", category="shopping", max_steps=10, headless=True),
        debug_dirs=[str(tmp_path / "wa")], timeout=180,
    )
    # Runs and produces a readable trajectory regardless of solve outcome.
    traj = load_trajectory(str(tmp_path / "wa"))
    assert isinstance(reward, float)
    assert len(traj.steps) >= 1


@pytest.mark.llm
@pytest.mark.e2e
@pytest.mark.skipif(
    not (os.getenv("OPENAI_API_KEY") and os.path.exists(_M2W_SPLIT)),
    reason="needs OPENAI_API_KEY and data/mind2web/cross_task.json for a live Mind2Web task",
)
def test_mind2web_real(tmp_path):
    from polyskill.evaluation import eval_runner
    from polyskill.skill_induction.online_hook import judge_trajectory_success_sync

    env_ids, task_kwargs = eval_runner.get_env_ids_and_task_kwargs(
        BenchmarkConfig(dataset="mind2web", setting="cross-task", max_examples=1),
        shuffle_seed=0,
    )
    assert env_ids == ["browsergym/openended"]
    assert task_kwargs and task_kwargs[0].get("goal")

    out_dir = str(tmp_path / "m2w")
    reward = eval_loop.run_example(
        env_ids[0],
        task_kwargs[0],
        AgentConfig(name="hsm_v3", model={"provider": "openai", "name": "gpt-4.1"}),
        # Tight budget: the guessed start URL may not even load -- the harness must
        # still degrade gracefully into a trajectory dir with a summary.
        BenchmarkConfig(dataset="mind2web", setting="cross-task", max_steps=6, headless=True),
        debug_dirs=[out_dir], timeout=180,
    )
    assert isinstance(reward, float)
    # Harness produced a readable trajectory + summary even if the site failed.
    assert os.path.exists(os.path.join(out_dir, "summary_info.json"))
    traj = load_trajectory(out_dir)
    assert traj.goal == task_kwargs[0]["goal"]

    # The judge runs against the produced trajectory and returns a boolean verdict
    # (this is the paper's judge-based success signal).
    verdict = judge_trajectory_success_sync(
        trajectory_path=out_dir,
        judge_config={"provider": "openai", "name": "gpt-4.1", "temperature": 0.0},
        judge_method="webjudge_online_mind2web",
        score_threshold=3,
    )
    assert isinstance(verdict, bool)
