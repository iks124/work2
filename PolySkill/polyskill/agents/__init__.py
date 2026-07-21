"""PolySkill agent package: the ``make_agent`` factory.

``make_agent`` maps a validated :class:`~polyskill.evaluation.eval_config.AgentConfig`
to a concrete agent instance.  Heavy agent classes are imported lazily inside the
factory so that ``import polyskill.agents`` stays cheap and side-effect free.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

_HSM_NAMES = {"hsm_v3", "hsm_v3_with_polyskill", "hsm_v3_explorer"}


def _model_to_dict(model) -> Dict[str, Any]:
    """Flatten a ModelConfig (or plain dict) into a FoundationModel kwargs dict."""
    if model is None:
        return {"provider": "openai", "name": "gpt-4.1"}
    if isinstance(model, dict):
        return {
            k: v for k, v in model.items()
            if k in (
                "provider", "name", "temperature", "max_tokens", "timeout",
                "base_url", "api_key", "supports_vision",
            )
        }
    out: Dict[str, Any] = {"provider": model.provider, "name": model.name}
    if getattr(model, "temperature", None) is not None:
        out["temperature"] = model.temperature
    if getattr(model, "max_tokens", None) is not None:
        out["max_tokens"] = model.max_tokens
    for key in ("timeout", "base_url", "api_key", "supports_vision"):
        value = getattr(model, key, None)
        if value is not None:
            out[key] = value
    return out


def _build_model_configs(model) -> Dict[str, Any]:
    """Build the ``{"main", "planner", "executor"}`` model_configs dict.

    Planner/executor default to the main config when not explicitly nested.
    """
    main = _model_to_dict(model)
    configs: Dict[str, Any] = {"main": main}

    planner = getattr(model, "planner", None) if model is not None else None
    executor = getattr(model, "executor", None) if model is not None else None
    configs["planner"] = _model_to_dict(planner) if planner is not None else dict(main)
    configs["executor"] = _model_to_dict(executor) if executor is not None else dict(main)
    return configs


def make_agent(agent_config):
    """Build and return an agent from an :class:`AgentConfig`.

    Currently supports the HSM-V3 family (``hsm_v3``, ``hsm_v3_with_polyskill``,
    ``hsm_v3_explorer``); unknown names raise :class:`ValueError`.
    """
    name = getattr(agent_config, "name", None)
    if name not in _HSM_NAMES:
        raise ValueError(f"Unknown agent name: {name!r}")

    from polyskill.agents.agent.vlm_based import HsmV3ASIAgentWithInduction

    model_configs = _build_model_configs(getattr(agent_config, "model", None))

    kwargs: Dict[str, Any] = {"model_configs": model_configs}

    # Pass through optional, explicitly-set agent_config fields.
    def _set(key, attr=None):
        attr = attr or key
        val = getattr(agent_config, attr, None)
        if val is not None:
            kwargs[key] = val

    _set("action_file_path")
    _set("enable_skill_induction")
    _set("skill_storage_path")
    _set("min_skill_complexity")
    _set("max_skill_complexity")

    agent = HsmV3ASIAgentWithInduction(**kwargs)

    # Online PolySkill injects the currently persisted rich Skill objects into
    # AgentConfig before constructing each task's agent.  Make that injection
    # operational by exposing the skills to the executor prompt.
    skill_cfg = getattr(agent_config, "skill_induction_config", None) or {}
    if hasattr(agent, "executor"):
        agent.executor.current_skills = list(skill_cfg.get("current_skills") or [])

    return agent


__all__ = ["make_agent"]
