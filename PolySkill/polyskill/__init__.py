"""
PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction

Official implementation of the PolySkill framework for web agent skill learning.
"""

__version__ = "0.1.0"
__author__ = "Simon Yu, Gang Li, Weiyan Shi, Peng Qi"
__email__ = "yu.chi@northeastern.edu"

from polyskill.core import SkillInductionCore, PolymorphicInducer
from polyskill.core.skill_storage import PolySkillStorage

__all__ = [
    "SkillInductionCore",
    "PolySkillStorage",
    "PolymorphicInducer",
    "__version__",
]
