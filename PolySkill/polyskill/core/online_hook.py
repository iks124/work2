#!/usr/bin/env python3
"""
Online Skill Induction Hook

This module provides the hook that gets called after each task completes
to perform immediate skill induction based on LLM judge evaluation.
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from .simple_inducer import SimpleSkillInducer
from .judge.trajectory_judge import TrajectoryJudge
from .judge.utils import load_trajectory_data

logger = logging.getLogger(__name__)

# Global instances to avoid recreating components
_skill_inducer_instance = None
_judge_instance = None


def _build_polymorphic_inducer(storage_path: str, **kwargs):
    """Construct a PolymorphicInducer from online-hook kwargs.

    The LLM config is derived from ``induction_model``.  ``judge_model`` remains
    the fallback for older configs that used one model for both roles.
    """
    # Imported lazily to keep the default (SimpleSkillInducer) path import-light.
    from .inducers.polymorphic_inducer import PolymorphicInducer
    from .inducers.llm_inducer import LLMInducerConfig, LLMConfig, LLMProvider

    model_cfg = (
        kwargs.get("induction_model")
        or kwargs.get("judge_model")
        or kwargs.get("model")
        or {}
    )
    provider_raw = str(model_cfg.get("provider", "litellm")).lower()
    try:
        provider = LLMProvider(provider_raw)
    except ValueError:
        provider = LLMProvider.LITELLM

    llm_config = LLMConfig(
        provider=provider,
        model_name=model_cfg.get("name", "gpt-4.1"),
        temperature=model_cfg.get("temperature", 0.0),
        max_tokens=model_cfg.get("max_tokens", 4000),
        timeout=model_cfg.get("timeout", 120),
        base_url=model_cfg.get("base_url"),
        api_key=model_cfg.get("api_key"),
    )
    config = LLMInducerConfig(storage_path=storage_path, llm_config=llm_config)
    logger.info(f"Initialized polymorphic skill inducer with storage: {storage_path}")
    return PolymorphicInducer(config)


def get_skill_inducer(storage_path: str = "./learned_skills/", **kwargs):
    """Get or create a skill inducer instance.

    By default returns the cached :class:`SimpleSkillInducer` singleton. When
    ``use_polymorphism`` is truthy, returns a :class:`PolymorphicInducer` instead — the
    cache is keyed on the flag so the polymorphic inducer is never shadowed by a previously
    cached simple inducer (and vice versa).
    """
    global _skill_inducer_instance

    use_polymorphism = bool(kwargs.get("use_polymorphism"))

    if use_polymorphism:
        # Bypass the simple-inducer singleton; reuse a cached polymorphic one if present.
        if isinstance(_skill_inducer_instance, _polymorphic_type()):
            return _skill_inducer_instance
        _skill_inducer_instance = _build_polymorphic_inducer(storage_path, **kwargs)
        return _skill_inducer_instance

    if _skill_inducer_instance is None or not isinstance(_skill_inducer_instance, SimpleSkillInducer):
        _skill_inducer_instance = SimpleSkillInducer(
            storage_path=storage_path,
            min_actions=kwargs.get("min_actions", 2),
            max_actions=kwargs.get("max_actions", 8)
        )
        logger.info(f"Initialized skill inducer with storage: {storage_path}")

    return _skill_inducer_instance


def _polymorphic_type():
    """Lazily import the PolymorphicInducer type for isinstance checks."""
    from .inducers.polymorphic_inducer import PolymorphicInducer
    return PolymorphicInducer


def get_judge_instance(judge_config: Dict[str, Any]) -> TrajectoryJudge:
    """Get or create judge instance."""
    global _judge_instance
    
    if _judge_instance is None:
        _judge_instance = TrajectoryJudge(judge_config)
        logger.info(f"Initialized LLM judge: {judge_config.get('provider')}/{judge_config.get('name')}")

    return _judge_instance


def _trajectory_action_strings(trajectory_data: Any) -> list:
    """Extract ordered BrowserGym action strings from loaded trajectory data."""
    actions = []
    raw = None
    if hasattr(trajectory_data, "actions"):
        raw = trajectory_data.actions
    elif isinstance(trajectory_data, dict):
        raw = trajectory_data.get("actions", [])
    for item in raw or []:
        if isinstance(item, str):
            if item.strip():
                actions.append(item.strip())
        elif isinstance(item, dict):
            a = item.get("action", "")
            if a:
                actions.append(str(a).strip())
        elif hasattr(item, "action") and getattr(item, "action"):
            actions.append(str(getattr(item, "action")).strip())
    return actions


def _induce_polymorphic_skill(skill_inducer, trajectory_data: Any, task: str,
                              skill_config: Dict[str, Any]):
    """Drive the polymorphic inducer for a single trajectory.

    Resolves ``domain``/``site`` from skill_config (falling back to trajectory metadata),
    then calls :meth:`PolymorphicInducer.induce`.
    """
    action_strings = _trajectory_action_strings(trajectory_data)
    if not action_strings:
        logger.warning("Polymorphic induction: no actions in trajectory")
        return None

    meta = {}
    if isinstance(trajectory_data, dict):
        meta = trajectory_data.get("metadata", {}) or {}
    domain = skill_config.get("domain") or meta.get("domain") or "web"
    site = skill_config.get("site") or meta.get("site") or "site"

    return skill_inducer.induce(
        task=task,
        trajectory_actions=action_strings,
        domain=domain,
        site=site,
    )


async def judge_trajectory_success(trajectory_path: str, judge_config: Dict[str, Any],
                                 judge_method: str = "webjudge_general",
                                 score_threshold: int = 3) -> bool:
    """Use LLM judge to determine if trajectory was successful."""
    try:
        judge = get_judge_instance(judge_config)
        
        print(f"judge_path: {trajectory_path}")
        if judge_method == "webjudge_online_mind2web":
            # Use WebJudge Online Mind2Web method with score threshold
            result = await judge.judge_trajectory_webjudge_online_mind2web(
                trajectory_path=trajectory_path,
                score_threshold=score_threshold
            )
            success = result.get("trajectory_success", False)
            
        elif judge_method == "webjudge_general":
            # Use webjudge_general method with score threshold
            result = await judge.judge_trajectory_webjudge_general(
                trajectory_path=trajectory_path,
                score_threshold=score_threshold
            )
            success = result.get("trajectory_success", False)
        
        elif judge_method == "webvoyager":
            # Use WebVoyager method
            result = await judge.judge_trajectory_webvoyager(trajectory_path)
            success = result.get("trajectory_success", False)
        
        else:
            logger.error(f"Unknown judge method: {judge_method}")
            success = False
            result = {"error": f"Unknown judge method: {judge_method}"}
        
        # Simple logging to trajectory folder
        _save_judge_result(trajectory_path, result, success)
        return success
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"LLM judge failed for {trajectory_path} with method {judge_method}:")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Full traceback:\n{error_details}")
        return False


def judge_trajectory_success_sync(
    trajectory_path: str,
    judge_config: Dict[str, Any],
    judge_method: str = "webjudge_general",
    score_threshold: int = 3,
) -> bool:
    """Synchronous wrapper around :func:`judge_trajectory_success`.

    Looks the async judge up on the module at call time so test monkeypatches of
    ``judge_trajectory_success`` are honoured. Handles being called from within a
    running event loop by delegating to a worker thread.
    """
    async def _run():
        return await judge_trajectory_success(
            trajectory_path, judge_config, judge_method=judge_method,
            score_threshold=score_threshold,
        )

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_run())

    import concurrent.futures

    def run_in_thread():
        return asyncio.run(_run())

    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(run_in_thread).result()


def _save_judge_result(trajectory_path: str, result: dict, success: bool):
    """Save judge result to trajectory folder."""
    try:
        import json
        from pathlib import Path
        from datetime import datetime
        
        path = Path(trajectory_path)
        trajectory_dir = path if path.is_dir() else path.parent
        judge_file = trajectory_dir / "judge_result.json"
        
        # Extract key information for storage
        judge_data = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "task": result.get("task", ""),
            "key_points": result.get("key_points", ""),
            "num_screenshots": result.get("num_screenshots", 0),
            "num_high_score": result.get("num_high_score", 0),
            "final_evaluation": result.get("final_evaluation", result.get("evaluation", "")),
            "method_used": "webjudge" if "screenshot_judgments" in result else "webvoyager"
        }
        
        with open(judge_file, 'w') as f:
            json.dump(judge_data, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to save judge result: {e}")


async def process_task_for_skills(
    trajectory_path: str,
    task: str,
    reward: float,
    agent_config: Any = None,
    skill_config: Optional[Dict[str, Any]] = None,
    judged: Optional[bool] = None,
) -> Optional[Any]:
    """
    Process a completed task for skill induction.

    Args:
        trajectory_path: Path to the trajectory file
        task: Task description/goal
        reward: Task reward (may be ignored based on config)
        agent_config: Agent configuration
        skill_config: Skill induction configuration
        judged: Optional precomputed LLM-judge verdict. When provided, the internal
            judge call is skipped and this verdict decides induction -- lets a caller
            that already judged the trajectory (e.g. for success-rate tracking) avoid
            a second, redundant judge call.

    Returns:
        Induced skill or None
    """
    if not skill_config or not skill_config.get("enabled", True):
        return None
    
    # Check if trajectory file exists
    if not os.path.exists(trajectory_path):
        logger.warning(f"Trajectory file not found: {trajectory_path}")
        return None
    
    logger.info(f"Processing task for skills: {task}")
    
    try:
        # Optional reward pre-filtering (default: False - always judge)
        use_reward_signal = skill_config.get("use_reward_signal", False)
        if use_reward_signal and reward <= 0:
            logger.info(f"  Skipping (reward={reward}, use_reward_signal=True)")
            return None
        
        # Always use LLM Judge for final decision
        judge_config = skill_config.get("judge_model", {
            "provider": "openai",
            "name": "gpt-4o",
            "temperature": 0.0
        })
        
        # Get judge method and parameters
        judge_method = skill_config.get("judge_method", "webjudge_general")
        score_threshold = skill_config.get("score_threshold", 3)

        if judged is None:
            llm_success = await judge_trajectory_success(
                trajectory_path,
                judge_config,
                judge_method=judge_method,
                score_threshold=score_threshold
            )
        else:
            # Reuse a verdict the caller already computed for this trajectory.
            llm_success = bool(judged)

        print(f"Golden reward: {reward}, LLM Judge: {llm_success}. Match: {(reward > 0) == llm_success}")
        if not llm_success:
            logger.info(f"  LLM judge: FAILED - no skill induction")
            return None
        
        logger.info(f"  LLM judge: SUCCESS - inducing skills...")
        
        # Initialize skill inducer
        storage_path = skill_config.get("storage_path", "./learned_skills/")
        use_polymorphism = skill_config.get("use_polymorphism", False)
        skill_inducer = get_skill_inducer(
            storage_path=storage_path,
            min_actions=skill_config.get("min_actions", 2),
            max_actions=skill_config.get("max_actions", 8),
            use_polymorphism=use_polymorphism,
            judge_model=judge_config,
            induction_model=skill_config.get("induction_model"),
        )

        # Load trajectory and induce skill
        trajectory_data = load_trajectory_data(trajectory_path)
        if use_polymorphism:
            skill = _induce_polymorphic_skill(
                skill_inducer, trajectory_data, task, skill_config
            )
        else:
            skill = skill_inducer.induce_skill(trajectory_data, task)

        if skill:
            if use_polymorphism:
                # PolymorphicInducer returns a rich Skill object but, unlike the
                # legacy SimpleSkillInducer, does not persist it itself.
                from .skill_storage import EnhancedSkillStorage

                storage = EnhancedSkillStorage(storage_path)
                if not storage.store_skill(skill):
                    logger.error("Failed to persist induced polymorphic skill: %s", skill.name)
                    return None
            success_count = getattr(
                skill, "success_count", getattr(getattr(skill, "metadata", None), "success_count", 1)
            )
            logger.info(f"  ✓ Induced skill: {skill.name} (success_count: {success_count})")
            return skill
        else:
            logger.info(f"  - No skill induced from trajectory")
            return None
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Skill induction failed for task '{task}':")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Full traceback:\n{error_details}")
        return None


def process_task_for_skills_sync(
    trajectory_path: str,
    task: str,
    reward: float,
    agent_config: Any = None,
    skill_config: Optional[Dict[str, Any]] = None,
    judged: Optional[bool] = None,
) -> Optional[Any]:
    """Synchronous wrapper for skill processing."""
    async def _run():
        return await process_task_for_skills(
            trajectory_path=trajectory_path,
            task=task,
            reward=reward,
            agent_config=agent_config,
            skill_config=skill_config,
            judged=judged,
        )

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_run())

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        return executor.submit(lambda: asyncio.run(_run())).result()


def get_current_skills(storage_path: str = "./learned_skills/") -> list:
    """Get current skills for an agent to use."""
    try:
        # Enhanced polymorphic storage has an explicit schema version.  Load it
        # directly instead of replacing the cached polymorphic inducer with the
        # legacy SimpleSkillInducer (whose skills.json schema is incompatible).
        import json
        from pathlib import Path

        skills_file = Path(storage_path) / "skills.json"
        if skills_file.exists():
            with open(skills_file, "r") as f:
                data = json.load(f)
            if "version" in data:
                from .skill_storage import EnhancedSkillStorage

                skills = EnhancedSkillStorage(storage_path).retrieve_skills(include_content=True)
                logger.info(f"Loaded {len(skills)} polymorphic skills for agent")
                return skills
        skill_inducer = get_skill_inducer(storage_path=storage_path)
        skills = skill_inducer.get_skills()
        logger.info(f"Loaded {len(skills)} skills for agent")
        return skills
    except Exception as e:
        logger.error(f"Failed to load skills: {e}")
        return []


def get_skills_summary(storage_path: str = "./learned_skills/") -> str:
    """Get a summary of current skills."""
    try:
        import json
        from pathlib import Path

        skills_file = Path(storage_path) / "skills.json"
        if skills_file.exists():
            with open(skills_file, "r") as f:
                data = json.load(f)
            if "version" in data:
                skills = get_current_skills(storage_path)
                if not skills:
                    return "No skills available"
                return "\n".join(
                    f"- {getattr(skill, 'name', 'unnamed')}: "
                    f"{getattr(skill, 'description', '')}" for skill in skills
                )
        skill_inducer = get_skill_inducer(storage_path=storage_path)
        return skill_inducer.export_skills_summary()
    except Exception as e:
        logger.error(f"Failed to get skills summary: {e}")
        return "No skills available"
