from polyskill.agents.base import Agent, BasicFMAgent


class _StubModel:
    def generate(self, **kw):
        return "<action>click('7')</action>"


def test_basic_fm_agent_extract():
    a = BasicFMAgent(model=_StubModel())
    assert a.extract_action(a.act(prompt="x")) == "click('7')"


def test_basic_fm_agent_extract_plain_text():
    class _PlainModel:
        def generate(self, **kw):
            return "  click('3')  "

    a = BasicFMAgent(model=_PlainModel())
    assert a.extract_action(a.act(prompt="x")) == "click('3')"


def test_agent_get_action_not_implemented():
    import pytest

    agent = Agent()
    with pytest.raises(NotImplementedError):
        agent.get_action({})


def test_basic_fm_agent_requires_a_model():
    """Bug G: constructing with no model and no provider+name must fail clearly."""
    import pytest

    with pytest.raises(ValueError, match="requires a model or model_provider"):
        BasicFMAgent()


def test_basic_fm_agent_builds_from_provider_and_name():
    """Providing provider+name (no model instance) is still allowed."""
    a = BasicFMAgent(model_provider="openai", model_name="gpt-4.1")
    assert a.model is not None and a.model.provider == "openai"
