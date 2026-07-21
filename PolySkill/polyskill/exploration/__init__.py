"""Self-proposing / self-guided exploration subsystem for PolySkill.

Implements structured, novelty-biased exploration (paper §3.4/4.3):
- TaskProposer: uses abstract-class schema to propose goals, biased by novelty
- GradualCurriculum: complexity scheduling (atomic → two_step → compositional)
- run_self_proposing_exploration: the main exploration loop
"""

from .task_proposer import TaskProposer, ProposedTask
from .curriculum import GradualCurriculum
from .explore_loop import run_self_proposing_exploration

__all__ = [
    "TaskProposer",
    "ProposedTask",
    "GradualCurriculum",
    "run_self_proposing_exploration",
]
