"""The shim package must expose the exact paths the GitHub issues named."""


def test_shim_paths_resolve():
    from polyskill.skill_induction.online_hook import (
        process_task_for_skills_sync,
        get_current_skills,
        get_skills_summary,
    )
    from polyskill.skill_induction.judge.utils import (
        load_trajectory_data,
        extract_task_from_trajectory,
    )
    from polyskill.skill_induction import SimpleSkillInducer

    assert SimpleSkillInducer is not None
    assert all(
        callable(x)
        for x in [
            process_task_for_skills_sync,
            get_current_skills,
            get_skills_summary,
            load_trajectory_data,
            extract_task_from_trajectory,
        ]
    )
