"""Back-compat shim for ``polyskill.skill_induction.online_hook``.

Re-exports the online skill-induction hooks from ``polyskill.core.online_hook``.
"""
from polyskill.core.online_hook import (  # noqa: F401
    get_skill_inducer,
    get_judge_instance,
    judge_trajectory_success,
    judge_trajectory_success_sync,
    process_task_for_skills,
    process_task_for_skills_sync,
    get_current_skills,
    get_skills_summary,
)

__all__ = [
    "get_skill_inducer",
    "get_judge_instance",
    "judge_trajectory_success",
    "judge_trajectory_success_sync",
    "process_task_for_skills",
    "process_task_for_skills_sync",
    "get_current_skills",
    "get_skills_summary",
]
