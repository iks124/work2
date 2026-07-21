def test_make_agent_hsm(monkeypatch):
    from polyskill.model import fm

    monkeypatch.setattr(fm.FoundationModel, "generate", lambda self, **kw: "noop()")
    from polyskill.agents import make_agent
    from polyskill.evaluation.eval_config import AgentConfig, ModelConfig

    a = make_agent(
        AgentConfig(name="hsm_v3", model=ModelConfig(provider="openai", name="gpt-4.1"))
    )
    from polyskill.agents.agent.vlm_based import HsmV3ASIAgentWithInduction

    assert isinstance(a, HsmV3ASIAgentWithInduction)
    import pytest

    with pytest.raises(ValueError):
        make_agent(AgentConfig(name="totally-unknown"))


def test_make_agent_preserves_local_endpoint_and_text_only_mode():
    from polyskill.agents import make_agent
    from polyskill.evaluation.eval_config import AgentConfig, ModelConfig

    a = make_agent(AgentConfig(name="hsm_v3", model=ModelConfig(
        provider="local", name="Qwen3-Coder-480B-A35B-Instruct",
        base_url="http://127.0.0.1:8002/v1", api_key="EMPTY",
        supports_vision=False,
    )))
    assert a.executor.model.base_url == "http://127.0.0.1:8002/v1"
    assert a.planner.model.base_url == "http://127.0.0.1:8002/v1"
    assert a.planner.supports_vision is False
