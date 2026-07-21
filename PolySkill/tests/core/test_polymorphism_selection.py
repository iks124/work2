import pytest
import polyskill.core.online_hook as _hook_mod


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the module-level singleton between tests to avoid cross-pollution."""
    _hook_mod._skill_inducer_instance = None
    yield
    _hook_mod._skill_inducer_instance = None


def test_use_polymorphism_selects_polymorphic_inducer(tmp_path):
    from polyskill.core.online_hook import get_skill_inducer
    from polyskill.core.inducers.polymorphic_inducer import PolymorphicInducer
    ind = get_skill_inducer(storage_path=str(tmp_path/"s"), use_polymorphism=True,
                            judge_model={"provider":"openai","name":"gpt-4.1","temperature":0.0})
    assert isinstance(ind, PolymorphicInducer)
