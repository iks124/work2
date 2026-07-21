import json

from polyskill.evaluation.eval_config import EvalConfig, BenchmarkConfig, RunnerConfig, ModelConfig
from polyskill.evaluation import eval_runner


def test_miniwob_ids():
    ids, tk = eval_runner.get_env_ids_and_task_kwargs(
        BenchmarkConfig(dataset="miniwob", max_examples=3), shuffle_seed=42
    )
    assert len(ids) == 3 and all("miniwob" in i for i in ids) and tk is None


def _write_mind2web_split(tmp_path, records):
    (tmp_path / "cross_task.json").write_text(json.dumps(records))
    return str(tmp_path)


def test_mind2web_resolves_openended_env_ids(tmp_path):
    records = [
        {"task_id": "t1", "task": "book a car", "website": "budget",
         "url": "https://www.budget.com"},
        {"task_id": "t2", "task": "find a hotel", "website": "airbnb",
         "url": "https://www.airbnb.com"},
        {"task_id": "t3", "task": "rent a truck", "website": "budgettruck",
         "url": "https://www.budgettruck.com"},
    ]
    split_dir = _write_mind2web_split(tmp_path, records)

    ids, tk = eval_runner.get_env_ids_and_task_kwargs(
        BenchmarkConfig(dataset="mind2web", setting="cross-task",
                        split_dir=split_dir, max_examples=2),
        shuffle_seed=None,
    )
    assert ids == ["browsergym/openended", "browsergym/openended"]
    assert tk is not None and len(tk) == 2
    # task_kwargs aligns with the (untruncated head of the) split records.
    assert tk[0] == {"start_url": "https://www.budget.com", "goal": "book a car",
                     "task_id": "t1", "website": "budget"}
    assert tk[1]["task_id"] == "t2"


def test_mind2web_missing_setting_raises(tmp_path):
    import pytest
    with pytest.raises(ValueError) as exc:
        eval_runner.get_env_ids_and_task_kwargs(
            BenchmarkConfig(dataset="mind2web", split_dir=str(tmp_path))
        )
    assert "setting" in str(exc.value)


def test_output_dirs(tmp_path):
    ec = EvalConfig(run_name="r1", runner=RunnerConfig(output_dir=str(tmp_path)),
                    benchmarks={}, agents={})
    dirs = eval_runner._get_output_dirs_for_run(ec, benchmark_name="b", agent_name="a")
    assert dirs[0].endswith("r1/b_a") and __import__("os").path.isdir(dirs[0])


def test_wait_for_models_hosted_noop():
    eval_runner.wait_for_models(ModelConfig(provider="openai", name="gpt-4.1"))  # returns, no raise


def test_webarena_category_filter():
    ids, tk = eval_runner.get_env_ids_and_task_kwargs(
        BenchmarkConfig(dataset="webarena", category="reddit", max_examples=5),
        shuffle_seed=7,
    )
    assert tk is None
    assert 0 < len(ids) <= 5
    assert all(i.startswith("browsergym/webarena.") for i in ids)


def test_webarena_all_no_filter():
    ids, tk = eval_runner.get_env_ids_and_task_kwargs(
        BenchmarkConfig(dataset="webarena", category="all", max_examples=10),
        shuffle_seed=7,
    )
    assert len(ids) == 10
