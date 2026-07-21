"""Back-compat shim for ``polyskill.skill_induction.judge``.

Re-exports the judge API from ``polyskill.core.judge``.
"""
from polyskill.core.judge import (  # noqa: F401
    TrajectoryJudge,
    extract_screenshots_from_trajectory,
    load_trajectory_data,
)

__all__ = [
    "TrajectoryJudge",
    "extract_screenshots_from_trajectory",
    "load_trajectory_data",
]
