import pytest
from polyskill.core.inducers.polymorphic_inducer import PolymorphicInducer

def _mk():
    from polyskill.core.inducers.llm_inducer import LLMInducerConfig, LLMConfig, LLMProvider
    cfg = LLMInducerConfig(llm_config=LLMConfig(provider=LLMProvider.LITELLM, model_name="gpt-4.1"))
    return PolymorphicInducer(cfg)

def test_prompt_is_abstract_first():
    ind = _mk()
    p = ind.build_induction_prompt(
        task="search for a switch game and add to cart",
        trajectory_actions=["click('12')", "fill('12','switch')", "keyboard_press('Enter')"],
        domain="shopping", site="webarena_shopping",
        abstract_methods=["search_product", "add_to_cart"])
    assert "Abstract" in p and "ShoppingSite" in p.replace(" ", "")
    assert "webarena_shopping" in p.lower() or "WebarenaShopping" in p.replace("_", "")
    assert "search_product" in p and "add_to_cart" in p

def test_split_abstract_and_concrete():
    ind = _mk()
    code = (
        "class AbstractShoppingSite:\n"
        "    def search_product(self, query: str):\n        \"\"\"Searches.\"\"\"\n\n"
        "class WebarenaShopping(AbstractShoppingSite):\n"
        "    def search_product(self, query: str):\n        click('12'); fill('12', query)\n")
    abs, conc, method = ind._split_abstract_and_concrete(code)
    assert "AbstractShoppingSite" in abs
    assert "WebarenaShopping" in conc
    assert method == "search_product"

@pytest.mark.llm
def test_induce_real(tmp_path):
    import os
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("needs OPENAI_API_KEY")
    ind = _mk()
    res = ind.induce(task="search for a switch game",
                     trajectory_actions=["click('12')", "fill('12','switch')", "keyboard_press('Enter')"],
                     domain="shopping", site="webarena_shopping")
    # returns a Skill (or SkillInductionResult containing one) whose content defines a subclass method
    assert res is not None
