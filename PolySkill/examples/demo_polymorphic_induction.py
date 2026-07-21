#!/usr/bin/env python3
"""Demo: polymorphic abstract-class-first skill induction (the core PolySkill mechanism).

Given a successful trajectory, the ``PolymorphicInducer`` asks the LLM to
(1) register the new skill's *signature* on the domain's abstract interface
(e.g. ``AbstractShoppingSite``), then (2) implement it concretely in a
site-specific subclass (e.g. ``WebarenaShopping``). Compositional skills live
only on the abstract class and dispatch polymorphically.

Usage:
    # Offline (default) — no API key needed; a canned LLM response is fed
    # through the REAL induce() pipeline (prompt build -> parse -> Skill -> storage):
    python examples/demo_polymorphic_induction.py

    # Live — real LLM call via litellm (needs OPENAI_API_KEY):
    python examples/demo_polymorphic_induction.py --live

Module pointers:
    polyskill/core/inducers/polymorphic_inducer.py   (PolymorphicInducer)
    polyskill/prompts/induction/polymorphic.py       (abstract-first prompt)
    polyskill/core/online_hook.py                    (selected when skill_induction.use_polymorphism: true)
    tests/core/test_polymorphic_inducer.py           (unit tests)
"""
import argparse
import sys
import tempfile

from polyskill import PolymorphicInducer, PolySkillStorage
from polyskill.core.inducers.llm_inducer import LLMConfig, LLMInducerConfig, LLMProvider
from polyskill.prompts.induction.polymorphic import domain_to_class_name, site_to_class_name

TASK = "search for a nintendo switch game and open the first result"
TRAJECTORY_ACTIONS = [
    "click('search_box')",
    "fill('search_box', 'nintendo switch game')",
    "keyboard_press('Enter')",
    "click('result_0')",
]
DOMAIN = "shopping"
SITE = "webarena_shopping"
KNOWN_ABSTRACT_METHODS = ["add_to_cart", "checkout"]


def canned_llm_response(domain: str, site: str) -> str:
    """A model response of the exact shape the inducer expects (abstract-first)."""
    abstract_cls = domain_to_class_name(domain)
    concrete_cls = site_to_class_name(site)
    return f"""Here is the polymorphic skill for this trajectory:

```python
class {abstract_cls}:
    def search_and_open_product(self, query: str):
        \"\"\"Searches for a product and opens the first result.\"\"\"

    def add_to_cart(self, item_id: str, quantity: int = 1):
        \"\"\"Adds a specified item to the shopping cart.\"\"\"

    # Compositional skill: relies only on the abstract methods above.
    def search_and_add_to_cart(self, query: str, item_id: str):
        \"\"\"Finds a product and adds it to the cart.\"\"\"
        self.search_and_open_product(query)
        self.add_to_cart(item_id)


class {concrete_cls}({abstract_cls}):
    def search_and_open_product(self, query: str):
        click('search_box')
        fill('search_box', query)
        keyboard_press('Enter')
        click('result_0')
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true",
                        help="make a real LLM call via litellm (needs OPENAI_API_KEY)")
    parser.add_argument("--model", default="gpt-4.1", help="model for --live mode")
    parser.add_argument("--storage", default=None,
                        help="skill storage dir (default: a temp dir)")
    args = parser.parse_args()

    config = LLMInducerConfig(
        llm_config=LLMConfig(provider=LLMProvider.LITELLM, model_name=args.model)
    )
    inducer = PolymorphicInducer(config)

    print("=" * 70)
    print("PolySkill — polymorphic abstract-class-first induction demo")
    print("=" * 70)
    print(f"Task:       {TASK}")
    print(f"Trajectory: {TRAJECTORY_ACTIONS}")
    print(f"Domain:     {DOMAIN}  ->  {domain_to_class_name(DOMAIN)}")
    print(f"Site:       {SITE}  ->  {site_to_class_name(SITE)}")

    prompt = inducer.build_induction_prompt(
        task=TASK, trajectory_actions=TRAJECTORY_ACTIONS,
        domain=DOMAIN, site=SITE, abstract_methods=KNOWN_ABSTRACT_METHODS,
    )
    print("\n--- Induction prompt (first 600 chars) " + "-" * 24)
    print(prompt[:600] + ("..." if len(prompt) > 600 else ""))

    if not args.live:
        # Feed a canned model response through the REAL induce() pipeline.
        inducer._generate_polymorphic_responses = (
            lambda _prompt: [canned_llm_response(DOMAIN, SITE)]
        )
        print("\n[mode] offline — canned LLM response through the real pipeline")
    else:
        print(f"\n[mode] live — calling {args.model} via litellm")

    skill = inducer.induce(
        task=TASK, trajectory_actions=TRAJECTORY_ACTIONS,
        domain=DOMAIN, site=SITE, abstract_methods=KNOWN_ABSTRACT_METHODS,
    )
    if skill is None:
        print("\nFAILED: induction returned no skill")
        return 1

    extra = getattr(skill.metadata, "extra", {})
    print("\n--- Abstract interface (shared across the domain) " + "-" * 13)
    print(extra.get("abstract_source", "(n/a)"))
    print("--- Concrete implementation (this site) " + "-" * 23)
    print(skill.content)
    print("--- Induced Skill " + "-" * 46)
    print(f"name:        {skill.name}")
    print(f"description: {skill.description}")
    print(f"abstract:    {extra.get('abstract_class')}   concrete: {extra.get('concrete_class')}")

    storage_path = args.storage or tempfile.mkdtemp(prefix="polyskill_demo_")
    storage = PolySkillStorage(storage_path)
    if not storage.store_skill(skill):
        print("\nFAILED: could not store the skill")
        return 1
    print(f"\nSKILL STORED -> {storage_path} (skills.json + code/{skill.name}.py)")
    print("Done. This is the pipeline `skill_induction.use_polymorphism: true` runs online.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
