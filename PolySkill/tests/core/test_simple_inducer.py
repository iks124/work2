"""Tests for the extended SimpleSkillInducer API (Task 4.3)."""
import pytest
from polyskill.core.simple_inducer import SimpleSkillInducer


def test_extended_api_roundtrip(tmp_path):
    sp = str(tmp_path / "skills")
    ind = SimpleSkillInducer(storage_path=sp)

    # Induce a skill from agent state
    sk = ind.induce_skills_from_agent_state(
        actions=["click('1')", "fill('2','x')"],
        task="search for a product",
        success=True,
    )

    # save and reload
    ind.save_state()
    ind2 = SimpleSkillInducer(storage_path=sp)
    ind2.load_state()

    assert isinstance(ind2.get_skills_for_task("search", max_skills=5), list)
    assert isinstance(ind2.get_comprehensive_stats(), dict)
    assert isinstance(ind2.export_skills_as_actions(), str)
    assert isinstance(ind2.knowledge_base.get_tested_skills(), list)
    ind2.record_skill_usage("click('1')", True)  # must not raise
    assert isinstance(ind2.induction_history, list)


def test_induction_history_appended(tmp_path):
    ind = SimpleSkillInducer(storage_path=str(tmp_path / "skills"))
    # failed attempt — no skill should appear but history entry still added
    sk = ind.induce_skills_from_agent_state(
        actions=["click('x')", "fill('y','z')"],
        task="login to account",
        success=False,
    )
    assert sk is None
    assert len(ind.induction_history) == 1
    assert ind.induction_history[0]["success"] is False


def test_induction_success_and_history(tmp_path):
    ind = SimpleSkillInducer(storage_path=str(tmp_path / "skills"))
    sk = ind.induce_skills_from_agent_state(
        actions=["click('btn')", "fill('q','hello')"],
        task="search for a product",
        success=True,
    )
    assert len(ind.induction_history) == 1
    assert ind.induction_history[0]["success"] is True


def test_get_comprehensive_stats_keys(tmp_path):
    ind = SimpleSkillInducer(storage_path=str(tmp_path / "skills"))
    stats = ind.get_comprehensive_stats()
    for key in ("total_skills", "total_inductions", "total_usage", "storage_path"):
        assert key in stats


def test_export_skills_as_actions_no_skills(tmp_path):
    ind = SimpleSkillInducer(storage_path=str(tmp_path / "skills"))
    src = ind.export_skills_as_actions()
    assert isinstance(src, str)


def test_export_skills_as_actions_with_skills(tmp_path):
    ind = SimpleSkillInducer(storage_path=str(tmp_path / "skills"))
    ind.induce_skills_from_agent_state(
        actions=["click('a')", "fill('b','c')"],
        task="search for something",
        success=True,
    )
    src = ind.export_skills_as_actions()
    assert "def " in src


def test_knowledge_base_get_tested_skills(tmp_path):
    ind = SimpleSkillInducer(storage_path=str(tmp_path / "skills"))
    ind.induce_skills_from_agent_state(
        actions=["click('a')", "fill('b','c')"],
        task="search for something",
        success=True,
    )
    tested = ind.knowledge_base.get_tested_skills()
    assert isinstance(tested, list)
    assert len(tested) == len(ind.skills)


def test_save_load_state_roundtrip(tmp_path):
    sp = str(tmp_path / "skills")
    ind = SimpleSkillInducer(storage_path=sp)
    ind.induce_skills_from_agent_state(
        actions=["click('x')", "fill('y','z')"],
        task="login to account",
        success=True,
    )
    ind.save_state()

    ind2 = SimpleSkillInducer(storage_path=sp)
    ind2.load_state()
    assert len(ind2.induction_history) == len(ind.induction_history)
    assert len(ind2.skills) == len(ind.skills)
