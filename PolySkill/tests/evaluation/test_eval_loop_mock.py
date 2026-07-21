import gzip, pickle, types
from polyskill.evaluation import eval_loop
from polyskill.evaluation.eval_config import AgentConfig, BenchmarkConfig
from polyskill.trajectory import load_trajectory


class _DummyActionSet:
    def to_python_code(self, a):
        return a


class _DummyAgent:
    def __init__(self):
        self.action_set = _DummyActionSet()

    def get_action(self, obs):
        return "click('1')", {}


class _DummyEnv:
    def __init__(self):
        self._n = 0

    def reset(self, **kw):
        return ({"goal": "do the thing",
                 "screenshot": __import__("numpy").zeros((2, 2, 3), "uint8"),
                 "last_action_error": ""}, {})

    def step(self, action):
        self._n += 1
        return ({"goal": "do the thing",
                 "screenshot": __import__("numpy").zeros((2, 2, 3), "uint8"),
                 "last_action_error": ""}, 1.0, True, False, {})

    def close(self):
        pass


def test_run_example_writes_clean_trajectory(tmp_path, monkeypatch):
    monkeypatch.setattr(eval_loop, "make_agent", lambda cfg: _DummyAgent())
    monkeypatch.setattr(eval_loop.gym, "make", lambda *a, **k: _DummyEnv())
    r = eval_loop.run_example("browsergym/miniwob.click-test", None,
                              AgentConfig(name="hsm_v3"),
                              BenchmarkConfig(dataset="miniwob", max_steps=5),
                              debug_dirs=[str(tmp_path)], timeout=30)
    assert r == 1.0
    t = load_trajectory(str(tmp_path))
    assert t.actions == ["click('1')"] and t.success is True


def test_run_example_honors_task_kwargs(tmp_path, monkeypatch):
    """Mind2Web path: start_url reaches gym.make; the goal override wins."""
    monkeypatch.setattr(eval_loop, "make_agent", lambda cfg: _DummyAgent())

    captured = {}

    def _capturing_make(env_id, *a, **k):
        captured["env_id"] = env_id
        captured["kwargs"] = k
        return _DummyEnv()

    monkeypatch.setattr(eval_loop.gym, "make", _capturing_make)

    r = eval_loop.run_example(
        "browsergym/openended",
        {"start_url": "https://example.com", "goal": "book a rental truck",
         "task_id": "abc", "website": "budget"},
        AgentConfig(name="hsm_v3"),
        BenchmarkConfig(dataset="mind2web", max_steps=5),
        debug_dirs=[str(tmp_path)], timeout=30,
    )
    assert r == 1.0

    # Only the BrowserGym-valid task params were forwarded (no task_id/website).
    assert captured["env_id"] == "browsergym/openended"
    bg = captured["kwargs"]["task_kwargs"]
    assert bg == {"start_url": "https://example.com", "goal": "book a rental truck"}

    # The written trajectory carries the real task goal (override beats obs goal
    # "do the thing"), so the judge sees the right task text.
    t = load_trajectory(str(tmp_path))
    assert t.goal == "book a rental truck"
    assert t.success is True
