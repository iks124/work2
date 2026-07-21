from polyskill.evaluation.eval_config import EvalConfig


def test_parse_webarena_like_config():
    cfg = {
        "run_name": "x",
        "runner": {"threads": 1, "output_dir": "./results", "seed": 42, "timeout_secs": 600},
        "model_configs": {
            "gpt4": {"provider": "openai", "name": "gpt-4.1", "temperature": 0.1, "max_tokens": 4096}
        },
        "benchmarks": {
            "wa-shopping": {
                "dataset": "webarena", "category": "shopping",
                "max_examples": 187, "max_steps": 30, "headless": True, "reset_env": False,
            }
        },
        "agents": {"default": {"name": "hsm_v3", "model_config_name": "gpt4", "max_actions_per_step": 5}},
    }
    ec = EvalConfig(**cfg)
    assert ec.runner.threads == 1
    assert ec.runner.get_output_dirs() == ["./results"]
    assert ec.benchmarks["wa-shopping"].category == "shopping"
    assert ec.agents["default"].model_config_name == "gpt4"
    assert ec.model_configs["gpt4"].provider == "openai"


def test_extra_keys_ignored():
    cfg = {
        "runner": {"threads": 1, "bogus_runner_key": 1},
        "benchmarks": {"b": {"dataset": "miniwob", "unknown": 1}},
        "agents": {"a": {"name": "hsm_v3", "task_proposer": {"enabled": True}}},
        "model_configs": {},
        "exploration_domains": {"shopping": {}},  # extra top-level survives the pop+ignore
    }
    ec = EvalConfig(**cfg)
    assert ec.runner.threads == 1
    assert ec.benchmarks["b"].dataset == "miniwob"


def test_nested_model_config():
    mc = {"provider": "openai", "name": "gpt-4.1",
          "planner": {"provider": "openai", "name": "gpt-4.1"},
          "executor": {"provider": "anthropic", "name": "claude-3-7-sonnet-20250219"}}
    from polyskill.evaluation.eval_config import ModelConfig
    m = ModelConfig(**mc)
    assert m.planner.name == "gpt-4.1"
    assert m.executor.provider == "anthropic"


def test_local_model_endpoint_fields_are_preserved():
    from polyskill.evaluation.eval_config import ModelConfig
    m = ModelConfig(
        provider="local", name="Qwen3-Coder-480B-A35B-Instruct",
        base_url="http://127.0.0.1:8002/v1", api_key="EMPTY", timeout=600,
    )
    assert m.base_url == "http://127.0.0.1:8002/v1"
    assert m.api_key == "EMPTY"
    assert m.timeout == 600
