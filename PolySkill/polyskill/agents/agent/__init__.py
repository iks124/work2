"""
PolySkill Agent Implementations

This package contains the core agent implementations for PolySkill:
- VLM-based agent: Vision-language model agent with skill induction
- LLM-based agent: Language model agent with chain-of-thought reasoning

``VLMAgent``/``LLMAgent`` are exposed lazily via :pep:`562` ``__getattr__`` so
that merely importing this package (or one of its submodules such as
``polyskill.agents.agent.utils``) does NOT eagerly pull in ``vlm_based`` ->
``hsm_agent`` -> ``polyskill.agents.planner``. That eager chain previously formed
a circular import whenever ``polyskill.agents.planner`` was imported first (it
imports ``polyskill.agents.agent.utils``, which ran this ``__init__``).
"""

__all__ = ["VLMAgent", "LLMAgent"]


def __getattr__(name):  # PEP 562: lazy attribute access at module level
    if name == "VLMAgent":
        from polyskill.agents.agent.vlm_based import HsmV3ASIAgentWithInduction

        return HsmV3ASIAgentWithInduction
    if name == "LLMAgent":
        from polyskill.agents.agent.llm_based import BasicCoTFMAgent

        return BasicCoTFMAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
