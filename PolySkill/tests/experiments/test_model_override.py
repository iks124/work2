"""The --model CLI flag must actually select the model (it used to be a no-op)."""
import pytest
import yaml

from polyskill.experiments.run_eval_with_skill_induction import SkillInductionEvaluator

_CONFIG = {
    "run_name": "t",
    "runner": {"threads": 1, "output_dir": "./results", "timeout_secs": 60},
    "model_configs": {
        "gpt4": {"provider": "openai", "name": "gpt-4.1"},
        "claude": {"provider": "anthropic", "name": "claude-3-7-sonnet-20250219"},
    },
    "benchmarks": {"b": {"dataset": "webarena", "category": "shopping", "max_steps": 5}},
    "agents": {"default": {"name": "hsm_v3", "model_config_name": "gpt4"}},
    "skill_induction": {"enabled": False},
}


def _write(tmp_path):
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump(_CONFIG))
    return str(p)


def test_model_override_by_name(tmp_path):
    ev = SkillInductionEvaluator(_write(tmp_path), model="claude-3-7-sonnet-20250219")
    assert ev.eval_config.agents["default"].model_config_name == "claude"


def test_model_override_by_key(tmp_path):
    ev = SkillInductionEvaluator(_write(tmp_path), model="claude")
    assert ev.eval_config.agents["default"].model_config_name == "claude"


def test_model_override_unknown_raises(tmp_path):
    with pytest.raises(ValueError, match="does not match any model_configs"):
        SkillInductionEvaluator(_write(tmp_path), model="gpt-5-turbo-max")


def test_no_override_keeps_config_default(tmp_path):
    ev = SkillInductionEvaluator(_write(tmp_path))
    assert ev.eval_config.agents["default"].model_config_name == "gpt4"


def test_core_all_names_resolve():
    import polyskill.core as c

    missing = [n for n in c.__all__ if not hasattr(c, n)]
    assert not missing, f"__all__ names missing from polyskill.core: {missing}"
