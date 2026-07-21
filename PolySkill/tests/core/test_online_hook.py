"""Tests for online_hook helper functions (Task 4.4)."""
import pytest
import polyskill.core.online_hook as _hook_mod

from polyskill.core.online_hook import (
    get_skill_inducer,
    get_current_skills,
    get_skills_summary,
    process_task_for_skills_sync,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the module-level singleton between tests to avoid cross-pollution."""
    _hook_mod._skill_inducer_instance = None
    yield
    _hook_mod._skill_inducer_instance = None


def test_hook_helpers(tmp_path):
    sp = str(tmp_path / "skills")
    ind = get_skill_inducer(storage_path=sp)
    assert ind is not None
    assert isinstance(get_current_skills(sp), list)
    assert isinstance(get_skills_summary(sp), str)
    # non-existent trajectory must return None, not raise
    out = process_task_for_skills_sync(
        trajectory_path=str(tmp_path / "nope"),
        task="t",
        reward=0.0,
        skill_config={"enabled": True},
    )
    assert out is None


def test_get_skill_inducer_returns_simple_inducer(tmp_path):
    from polyskill.core.simple_inducer import SimpleSkillInducer

    sp = str(tmp_path / "skills")
    ind = get_skill_inducer(storage_path=sp)
    assert isinstance(ind, SimpleSkillInducer)


def test_get_current_skills_empty(tmp_path):
    sp = str(tmp_path / "skills_empty")
    skills = get_current_skills(sp)
    assert skills == []


def test_get_skills_summary_no_skills(tmp_path):
    sp = str(tmp_path / "skills_empty")
    summary = get_skills_summary(sp)
    assert isinstance(summary, str)
    # Should mention 'No skills' or be otherwise non-empty
    assert len(summary) > 0


def test_process_task_disabled(tmp_path):
    out = process_task_for_skills_sync(
        trajectory_path=str(tmp_path / "irrelevant"),
        task="anything",
        reward=1.0,
        skill_config={"enabled": False},
    )
    assert out is None


def test_process_task_missing_trajectory(tmp_path):
    out = process_task_for_skills_sync(
        trajectory_path=str(tmp_path / "does_not_exist.json"),
        task="some task",
        reward=1.0,
        skill_config={"enabled": True},
    )
    assert out is None


def test_local_polymorphic_inducer_uses_foundation_model(tmp_path):
    from polyskill.model.fm import FoundationModel

    ind = get_skill_inducer(
        storage_path=str(tmp_path / "poly"),
        use_polymorphism=True,
        judge_model={"provider": "local", "name": "Qwen3.5-9B"},
    )
    assert isinstance(ind.llm_client, FoundationModel)
    assert ind.llm_client.provider == "local"
    assert ind.llm_client._model_string() == "openai/Qwen3.5-9B"


def test_polymorphic_inducer_uses_dedicated_induction_model(tmp_path):
    ind = get_skill_inducer(
        storage_path=str(tmp_path / "poly_split_models"),
        use_polymorphism=True,
        judge_model={"provider": "local", "name": "Qwen3-Coder-480B-A35B-Instruct",
                     "base_url": "http://127.0.0.1:8002/v1"},
        induction_model={"provider": "local", "name": "Qwen3.5-9B",
                         "base_url": "http://127.0.0.1:8003/v1"},
    )
    assert ind.llm_client.name == "Qwen3.5-9B"
    assert ind.llm_client.base_url == "http://127.0.0.1:8003/v1"


def test_judge_result_saved_inside_task_directory(tmp_path):
    import json

    task_dir = tmp_path / "0001_task"
    task_dir.mkdir()
    _hook_mod._save_judge_result(
        str(task_dir),
        {"task": "do it", "final_evaluation": "Status: failure"},
        False,
    )
    result_path = task_dir / "judge_result.json"
    assert result_path.exists()
    assert json.loads(result_path.read_text())["success"] is False
    assert not (tmp_path / "judge_result.json").exists()


def test_polymorphic_storage_is_loaded_for_injection(tmp_path):
    from polyskill.core.base import Skill, SkillFormat, SkillMetadata, SkillType
    from polyskill.core.skill_storage import EnhancedSkillStorage

    storage_path = str(tmp_path / "poly_store")
    skill = Skill(
        id="poly_demo_search",
        name="search",
        skill_type=SkillType.CODE,
        format=SkillFormat.PYTHON_FUNCTION,
        content="class Demo:\n    def search(self):\n        click('1')",
        description="Search the site",
        metadata=SkillMetadata(source="PolymorphicInducer"),
    )
    assert EnhancedSkillStorage(storage_path).store_skill(skill)
    loaded = get_current_skills(storage_path)
    assert len(loaded) == 1
    assert loaded[0].name == "search"
    assert "click('1')" in loaded[0].content
