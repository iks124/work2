"""Back-compat shim package.

The original (broken) release and the GitHub issues reference import paths like
``polyskill.skill_induction.online_hook`` and ``polyskill.skill_induction.judge.utils``.
The real implementations now live under ``polyskill.core``; this package re-exports
them so those documented paths keep working. New code should import from
``polyskill.core`` directly.
"""
from polyskill.core.simple_inducer import SimpleSkillInducer

__all__ = ["SimpleSkillInducer"]
