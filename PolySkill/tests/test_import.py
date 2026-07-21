"""Top-level import smoke tests — closes the core of issue #1."""


def test_top_level_imports():
    import polyskill
    from polyskill import SkillInductionCore, PolySkillStorage

    assert SkillInductionCore is not None
    assert PolySkillStorage is not None


def test_storage_alias_is_enhanced():
    from polyskill.core.skill_storage import PolySkillStorage, EnhancedSkillStorage

    assert PolySkillStorage is EnhancedSkillStorage
