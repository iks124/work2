"""Self-proposing exploration loop (PolySkill paper §3.4/4.3).

Runs the agent in a task-free setting: for each iteration the TaskProposer
selects a goal (biased toward uncovered abstract-class methods), the agent
attempts it, and on success the SimpleSkillInducer extracts a reusable skill.

Design principles
-----------------
- Clear **seams** via ``execute_fn`` and ``judge_fn`` so the loop is fully
  testable without a browser.
- Default ``execute_fn`` delegates to
  :func:`polyskill.evaluation.eval_loop.run_example`; default ``judge_fn``
  uses the trajectory reward.
- ``SimpleSkillInducer`` is updated after every success (online induction).
"""
from __future__ import annotations

import logging
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

from polyskill.core.simple_inducer import SimpleSkillInducer
from polyskill.exploration.curriculum import GradualCurriculum
from polyskill.exploration.task_proposer import ProposedTask, TaskProposer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain defaults
# ---------------------------------------------------------------------------

_DOMAIN_METHODS: Dict[str, List[str]] = {
    "shopping": ["search_product", "add_to_cart", "checkout"],
    "dev_tools": ["search_repository", "open_file", "create_issue"],
}
_DEFAULT_METHODS = ["navigate", "interact", "extract"]

_DOMAIN_WEBSITES: Dict[str, List[str]] = {
    "shopping": ["webarena_shopping"],
    "dev_tools": ["gitlab"],
}

# ---------------------------------------------------------------------------
# Default seam implementations
# ---------------------------------------------------------------------------


# Map exploration site identifiers to a WebArena category we can resolve a real
# registered ``browsergym/webarena.<N>`` env id for. ``f"browsergym/{site}"`` is
# NOT a real env id (e.g. ``browsergym/webarena_shopping`` is unregistered), so we
# pick a representative task in the right category instead. Live Amazon / Target /
# GitHub exploration would need dedicated, non-WebArena sites (not yet wired).
_SITE_TO_WEBARENA_CATEGORY: Dict[str, str] = {
    "webarena_shopping": "shopping",
    "shopping": "shopping",
    "gitlab": "gitlab",
    "webarena_gitlab": "gitlab",
    "reddit": "reddit",
    "webarena_reddit": "reddit",
    "map": "map",
    "webarena_map": "map",
    "shopping_admin": "admin",
    "admin": "admin",
}


def _resolve_env_id_for_site(site: str) -> str:
    """Resolve a representative real BrowserGym env id for an exploration *site*.

    Raises ``NotImplementedError`` for sites we can't map to a registered env id
    (e.g. live ``amazon``/``target``/``github`` need dedicated sites that this
    release does not ship).
    """
    category = _SITE_TO_WEBARENA_CATEGORY.get(site)
    if category is None:
        raise NotImplementedError(
            f"No registered BrowserGym env id is known for exploration site "
            f"{site!r}. Map it in _SITE_TO_WEBARENA_CATEGORY, or wire a dedicated "
            f"site (live Amazon/Target/GitHub exploration is not shipped)."
        )

    from polyskill.evaluation.eval_runner import get_env_ids_and_task_kwargs
    from polyskill.evaluation.eval_config import BenchmarkConfig

    env_ids, _ = get_env_ids_and_task_kwargs(
        BenchmarkConfig(dataset="webarena", category=category, max_examples=1)
    )
    if not env_ids:
        raise NotImplementedError(
            f"Could not resolve any WebArena env id for site {site!r} "
            f"(category={category!r}); is the 'webarena' package installed?"
        )
    return env_ids[0]


def _default_execute_fn(
    site: str,
    proposed_task: ProposedTask,
    iteration: int,
    storage_path: str,
    agent_config: Any,
    benchmark_config: Any,
) -> Tuple[float, Optional[str]]:
    """Default executor: calls run_example and writes to a per-iteration dir."""
    from polyskill.evaluation.eval_loop import run_example

    iter_dir = os.path.join(storage_path, f"iter_{iteration:04d}")
    os.makedirs(iter_dir, exist_ok=True)

    env_id = _resolve_env_id_for_site(site)
    task_kwargs = {"goal": proposed_task.goal}

    reward = run_example(
        env_id=env_id,
        task_kwargs=task_kwargs,
        agent_config=agent_config,
        benchmark_config=benchmark_config,
        debug_dirs=[iter_dir],
    )
    return reward, iter_dir


def _default_judge_fn(result_dir: Optional[str], goal: str, reward: float) -> bool:
    """Default judge: use reward > 0 as success signal."""
    if result_dir is not None:
        summary_path = os.path.join(result_dir, "summary_info.json")
        if os.path.exists(summary_path):
            import json

            try:
                summary = json.loads(open(summary_path).read())
                return float(summary.get("cum_reward", 0) or 0) > 0
            except Exception:
                pass
    return reward > 0


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------


def run_self_proposing_exploration(
    domain: str,
    iterations: int,
    model_config: Optional[Dict[str, Any]],
    storage_path: str,
    websites: Optional[List[str]] = None,
    allow_domain_switching: bool = False,
    execute_fn: Optional[Callable] = None,
    judge_fn: Optional[Callable] = None,
    agent_config: Any = None,
    benchmark_config: Any = None,
) -> Dict[str, Any]:
    """Run self-proposing exploration for *iterations* steps.

    Parameters
    ----------
    domain:
        Domain id (``"shopping"`` or ``"dev_tools"``).
    iterations:
        Fixed number of exploration iterations (paper: shopping=150, coding=100).
    model_config:
        Dict passed as ``**kwargs`` to :class:`~polyskill.model.FoundationModel`
        for the TaskProposer.  ``None`` disables LLM goal phrasing (offline mode).
    storage_path:
        Directory where per-iteration trajectories and the skill library are saved.
    websites:
        List of site identifiers to rotate through.  Defaults to the domain's
        canonical sites.
    allow_domain_switching:
        If ``True`` and multiple domains are available, the loop may switch
        domains across iterations (not yet implemented; reserved for future use).
    execute_fn:
        ``(site, proposed_task, iteration) -> (reward: float, result_dir: str|None)``.
        Defaults to calling :func:`~polyskill.evaluation.eval_loop.run_example`.
    judge_fn:
        ``(result_dir, goal) -> bool``.  Defaults to reward > 0.
    agent_config:
        Passed to the default ``execute_fn``.
    benchmark_config:
        Passed to the default ``execute_fn``.

    Returns
    -------
    dict with keys:
        ``"iterations"``, ``"proposals"``, ``"skills"``, ``"coverage"``,
        ``"successes"``.
    """
    os.makedirs(storage_path, exist_ok=True)

    # --- resolve domain defaults -------------------------------------------
    abstract_methods: List[str] = _DOMAIN_METHODS.get(domain, _DEFAULT_METHODS).copy()
    if websites is None:
        websites = _DOMAIN_WEBSITES.get(domain, [domain])

    # --- build components with seams ----------------------------------------
    if model_config:
        from polyskill.model.fm import FoundationModel

        model = FoundationModel(**model_config)
    else:
        model = None

    curriculum = GradualCurriculum(max_iterations=max(iterations, 1))
    proposer = TaskProposer(domain=domain, model=model)
    inducer = SimpleSkillInducer(storage_path=storage_path)

    # --- wrap execute_fn / judge_fn -----------------------------------------
    if execute_fn is None:
        _exec = lambda site, pt, i: _default_execute_fn(  # noqa: E731
            site, pt, i, storage_path, agent_config, benchmark_config
        )
    else:
        _exec = execute_fn

    if judge_fn is None:
        _judge = lambda result_dir, goal, reward=0.0: _default_judge_fn(  # noqa: E731
            result_dir, goal, reward
        )
    else:
        # Wrap caller's 2-arg judge so we can pass reward as a fallback.
        _judge = judge_fn  # caller's signature is (result_dir, goal) -> bool

    # --- main loop ----------------------------------------------------------
    coverage: Dict[str, bool] = {}
    history: List[Dict[str, Any]] = []
    proposals: List[Dict[str, Any]] = []
    successes = 0

    for i in range(iterations):
        # Pick site (round-robin).
        site = websites[i % len(websites)]

        # Build proposed task with curriculum complexity guidance.
        # (The proposer itself decides complexity based on coverage; the
        # curriculum gives a hint we log but don't override — consistent with
        # the paper which uses the schedule as a soft curriculum, not a hard
        # filter.)
        pt: ProposedTask = proposer.propose(
            site=site,
            coverage=coverage,
            abstract_methods=abstract_methods,
            history=history,
        )

        logger.info(
            "iter=%d site=%s target=%s complexity=%s goal=%r",
            i,
            site,
            pt.target_method,
            pt.complexity,
            pt.goal,
        )

        # Execute.
        reward, result_dir = _exec(site, pt, i)

        # Judge success.
        if judge_fn is None:
            success = _judge(result_dir, pt.goal, reward)
        else:
            # caller's judge is (result_dir, goal) → bool
            success = _judge(result_dir, pt.goal)

        if success:
            successes += 1
            # Load actions from trajectory if available.
            actions: List[str] = []
            if result_dir is not None:
                try:
                    from polyskill.trajectory import load_trajectory

                    traj = load_trajectory(result_dir)
                    actions = traj.actions
                except Exception as exc:
                    logger.warning("Could not load trajectory from %s: %s", result_dir, exc)

            # Induce skill from successful episode.
            inducer.induce_skills_from_agent_state(actions, pt.goal, success=True)

            # Mark method as covered.
            coverage[pt.target_method] = True

        # Record history for the proposer.
        entry: Dict[str, Any] = {
            "iteration": i,
            "site": site,
            "proposed_task": pt,
            "reward": reward,
            "success": success,
        }
        history.append(entry)
        proposals.append(
            {
                "iteration": i,
                "site": site,
                "goal": pt.goal,
                "target_method": pt.target_method,
                "complexity": pt.complexity,
                "success": success,
                "reward": reward,
            }
        )

    return {
        "iterations": iterations,
        "proposals": proposals,
        "skills": inducer.get_comprehensive_stats(),
        "coverage": coverage,
        "successes": successes,
    }
