import types

from polyskill.agents.agent import hsm_agent


def test_hsm_get_action_stubbed(monkeypatch):
    # stub FoundationModel.generate everywhere it's used
    from polyskill.model import fm

    monkeypatch.setattr(
        fm.FoundationModel,
        "generate",
        lambda self, **kw: "<action>click('5')</action>",
    )
    agent = hsm_agent.HsmV3ASIAgent(
        model_configs={"main": {"provider": "openai", "name": "gpt-4.1"}},
        actions="custom",
        action_file_path=None,
    )
    agent.reset(goal="click the button", html=None, screenshot=None)
    obs = {
        "goal": "click the button",
        "axtree_txt": "button 'OK' [5]",
        "screenshot": None,
        "last_action_error": "",
    }
    action, info = agent.get_action(obs)
    assert isinstance(action, str) and isinstance(info, dict)
    assert hasattr(agent, "action_set") and hasattr(agent.action_set, "to_python_code")


def test_hsm_executor_degrades_to_noop(monkeypatch):
    from polyskill.model import fm

    # Model returns garbage with no <action> tag -> extract returns it; but if
    # the model raises, the executor must degrade to noop().
    def _boom(self, **kw):
        raise RuntimeError("model down")

    monkeypatch.setattr(fm.FoundationModel, "generate", _boom)
    agent = hsm_agent.HsmV3ASIAgent(
        model_configs={"main": {"provider": "openai", "name": "gpt-4.1"}},
        action_file_path=None,
    )
    obs = {"goal": "do something", "axtree_txt": "x", "last_action_error": ""}
    action, info = agent.get_action(obs)
    assert action == "noop()"
    assert isinstance(info, dict)


def test_executor_renders_injected_polymorphic_skills():
    executor = hsm_agent._ExecutorAgent(
        {"provider": "openai", "name": "gpt-4.1"}, action_set=None
    )
    executor.current_skills = [{
        "name": "search_products",
        "description": "Search a catalog",
        "content": "def search_products(query): fill('3', query)",
    }]
    context = executor._format_skill_context()
    assert "search_products" in context
    assert "fill('3', query)" in context


def test_planner_runs_without_explicit_reset(monkeypatch):
    """Bug C regression: the planner must NOT silently no-op.

    With NO call to ``reset()`` first, ``get_action`` must lazily self-init the
    agent and the planner must actually produce a subtask (non-None) rather than
    being swallowed by a try/except. The stubbed model returns both a backtick-
    delimited plan (consumed by the planner's ``_parse_output``) and an
    ``<action>`` payload (consumed by the executor).
    """
    from polyskill.model import fm

    response = (
        "Here is my plan, step by step.\n"
        "```open the search box and type the query```\n"
        "<action>click('5')</action>"
    )
    monkeypatch.setattr(fm.FoundationModel, "generate", lambda self, **kw: response)

    agent = hsm_agent.HsmV3ASIAgent(
        model_configs={"main": {"provider": "openai", "name": "gpt-4.1"}},
        action_file_path=None,
    )
    # Deliberately do NOT call agent.reset(...).
    assert agent._did_reset is False

    obs = {
        "goal": "search for a switch game and open it",
        "axtree_txt": "textbox 'Search' [3]\nbutton 'OK' [5]",
        "screenshot": None,
        "last_action_error": "",
    }
    action, info = agent.get_action(obs)  # must not raise

    assert agent._did_reset is True
    # The planner ran and produced a concrete subtask (the regression we lock in).
    assert info.get("subtask") is not None
    assert "search box" in info["subtask"]
    assert isinstance(action, str) and action
