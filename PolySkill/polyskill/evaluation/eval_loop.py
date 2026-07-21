"""Run a single BrowserGym example and write a clean, self-contained trajectory.

The rollout uses only public BrowserGym: a gymnasium env created from a
``browsergym/...`` id, driven by an agent built via :func:`polyskill.agents.make_agent`.
Each step is pickled to ``step_{i}.pkl.gz`` and a final ``summary_info.json`` is always
written, so the downstream judge always has a trajectory to read -- even on failure.
"""
from __future__ import annotations

import gzip
import json
import logging
import os
import pickle
import time
from typing import List, Optional

import gymnasium as gym  # module global so tests can monkeypatch eval_loop.gym.make

from .eval_config import AgentConfig, BenchmarkConfig

# Lazy/optional: agents live in Phase 6. Bound as a module global so this module
# imports today and tests can monkeypatch ``eval_loop.make_agent``.
try:
    from polyskill.agents import make_agent  # type: ignore
except ImportError:  # pragma: no cover - exercised once agents land
    make_agent = None  # type: ignore

logger = logging.getLogger(__name__)


def _extract_goal(obs: dict) -> str:
    """Extract a plain-text goal from an observation dict.

    Prefers the legacy ``goal`` string; otherwise flattens the openai-style
    ``goal_object`` (a list/tuple of message dicts) into text.
    """
    goal = obs.get("goal")
    if goal:
        return goal if isinstance(goal, str) else str(goal)
    parts: List[str] = []
    for msg in obs.get("goal_object") or []:
        if isinstance(msg, dict):
            text = msg.get("text")
            if text:
                parts.append(str(text))
        elif msg:
            parts.append(str(msg))
    return "\n".join(parts)


def run_example(
    env_id: str,
    task_kwargs: Optional[dict],
    agent_config: AgentConfig,
    benchmark_config: BenchmarkConfig,
    debug_dirs: Optional[List[str]] = None,
    timeout: int = 600,
    seed: Optional[int] = None,
) -> float:
    """Roll out one episode of ``env_id`` and return the cumulative reward.

    Always writes ``summary_info.json`` (and one ``step_*.pkl.gz`` per step) into the
    output directory. On any error the episode ends gracefully with ``cum_reward=0.0``
    and the error recorded in the summary, so the caller always gets a trajectory.
    """
    out_dir = (debug_dirs or ["./results"])[0]
    os.makedirs(out_dir, exist_ok=True)

    cum_reward = 0.0
    n_steps = 0
    goal = ""
    error: Optional[str] = None
    env = None

    try:
        if make_agent is None:
            raise ImportError(
                "polyskill.agents.make_agent is unavailable; agents are added in a later phase."
            )
        agent = make_agent(agent_config)

        make_kwargs = {
            "action_mapping": agent.action_set.to_python_code,
            "max_episode_steps": benchmark_config.max_steps,
            "headless": benchmark_config.headless,
            "disable_env_checker": True,
        }
        # ``task_kwargs`` carries harness-level metadata (task_id, website, goal)
        # alongside the BrowserGym task parameters. The openended task only accepts
        # ``start_url`` (and an optional ``goal``), so forward just those keys --
        # passing task_id/website through would blow up OpenEndedTask.__init__.
        override_goal = ""
        if task_kwargs:
            override_goal = task_kwargs.get("goal") or ""
            bg_task_kwargs = {}
            if task_kwargs.get("start_url"):
                bg_task_kwargs["start_url"] = task_kwargs["start_url"]
            if override_goal:
                bg_task_kwargs["goal"] = override_goal
            if bg_task_kwargs:
                make_kwargs["task_kwargs"] = bg_task_kwargs
        env = gym.make(env_id, **make_kwargs)

        obs, info = env.reset(seed=seed)

        # Reset the agent so the hierarchical planner has its state (goal +
        # screenshot/axtree) before the first get_action(). Without this the
        # planner reads unset attributes, raises, and silently no-ops, so the
        # executor only ever sees the full goal. A reset failure must not abort
        # the episode, but it is expected to succeed.
        # Prefer the harness-provided task text (e.g. the Mind2Web goal). The
        # openended obs carries whatever goal we passed into the task, but the
        # override guarantees the agent + trajectory + judge see the real task
        # even if the env surfaces an empty/chat-based goal.
        initial_goal = override_goal or _extract_goal(obs)
        goal = initial_goal
        if hasattr(agent, "reset"):
            try:
                agent.reset(goal=initial_goal, screenshot=obs.get("screenshot"))
            except Exception:  # noqa: BLE001 - a reset failure should not end the run
                logger.exception("agent.reset failed for %s; continuing.", env_id)

        start = time.time()
        for i in range(benchmark_config.max_steps):
            if time.time() - start > timeout:
                logger.warning("Wall-clock timeout (%ss) reached on %s.", timeout, env_id)
                error = f"Wall-clock timeout ({timeout}s)"
                break

            goal = override_goal or _extract_goal(obs)
            screenshot = obs.get("screenshot")
            err = obs.get("last_action_error", "")

            action, agent_info = agent.get_action(obs)

            step = {
                "step": i,
                "action": action,
                "reward": 0.0,
                "obs": {"goal": goal, "screenshot": screenshot, "last_action_error": err},
            }
            with gzip.open(os.path.join(out_dir, f"step_{i}.pkl.gz"), "wb") as f:
                pickle.dump(step, f)
            n_steps = i + 1

            obs, reward, terminated, truncated, info = env.step(action)
            cum_reward += float(reward or 0)
            if terminated or truncated:
                break

    except Exception as e:  # noqa: BLE001 - always produce a trajectory for the judge
        error = repr(e)
        cum_reward = 0.0
        logger.exception("run_example failed for %s", env_id)

    finally:
        summary = {"cum_reward": cum_reward, "n_steps": n_steps, "goal": goal}
        if error is not None:
            summary["error"] = error
        try:
            with open(os.path.join(out_dir, "summary_info.json"), "w") as f:
                json.dump(summary, f)
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to write summary_info.json for %s", env_id)
        if env is not None:
            try:
                env.close()
            except Exception:  # pragma: no cover - defensive
                logger.warning("Failed to close env for %s", env_id)

    return cum_reward
