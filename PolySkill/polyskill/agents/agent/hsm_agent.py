"""Clean-room hierarchical (planner + executor) HSM agent.

``HsmV3ASIAgent`` couples a high-level :class:`BasicLLMPlanner` with a low-level
:class:`_ExecutorAgent` that emits concrete BrowserGym actions.  The design is a
pragmatic, faithful planner+executor HSM: on every step the planner proposes a
natural-language subtask and the executor grounds it into a single BrowserGym
action against the current accessibility tree.

The agent is deliberately robust — any failure in the planner or executor LLM
path degrades to ``noop()`` rather than raising, so a rollout always produces a
usable trajectory.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from polyskill.agents.base import Agent, BasicFMAgent
from polyskill.model import FoundationModel
from polyskill.agents.agent.asi_utils.utils import (
    parse_model_configs,
    initialize_custom_action_set,
    ASIAgentMixin,
)
from polyskill.agents.planner import BasicLLMPlanner

logger = logging.getLogger(__name__)


def _axtree_from_obs(obs: Any) -> str:
    """Best-effort extraction of an accessibility-tree string from *obs*."""
    if obs is None:
        return ""
    if isinstance(obs, dict):
        # Prefer a pre-flattened axtree string when present.
        txt = obs.get("axtree_txt")
        if txt:
            return str(txt)
        axtree_object = obs.get("axtree_object")
        if axtree_object is not None:
            try:
                from browsergym.utils.obs import flatten_axtree_to_str

                return flatten_axtree_to_str(axtree_object)
            except Exception:  # noqa: BLE001 - fall through to str()
                return str(axtree_object)
        # Fall back to anything resembling page text.
        for key in ("pruned_html", "dom_txt", "goal"):
            if obs.get(key):
                return str(obs.get(key))
    return str(obs)


def _normalize_model_configs(model_configs: dict) -> dict:
    """Flatten the ``{"main": {...}, "planner": {...}, "executor": {...}}`` shape
    into the flat ``{provider, name, ..., "planner": {...}, "executor": {...}}``
    shape that :func:`parse_model_configs` expects.

    ``parse_model_configs`` pops ``planner``/``executor`` off the top-level dict
    and treats the *remainder* as the main config; it does not unwrap a nested
    ``main`` key.  We therefore lift ``main`` to the top level here, preserving
    any sibling ``planner``/``executor`` overrides.
    """
    if not isinstance(model_configs, dict):
        return model_configs
    if "main" not in model_configs:
        return model_configs
    flat = dict(model_configs["main"] or {})
    if model_configs.get("planner") is not None:
        flat["planner"] = model_configs["planner"]
    if model_configs.get("executor") is not None:
        flat["executor"] = model_configs["executor"]
    return flat


_EXECUTOR_PROMPT = """\
You are a precise web agent. Your overall goal is:
{goal}

The immediate subtask to accomplish right now is:
{subtask}

Here is the set of actions you can use, given as Python function documentation:
{actions}

Here is the current accessibility tree of the page (numbers in [] are element
bids you pass as string arguments):
{axtree}

{error}
Respond with the SINGLE next action that makes progress on the subtask.
Format your answer exactly as:
<action>the python function call</action>"""


class _ExecutorAgent(BasicFMAgent):
    """Low-level executor that grounds a subtask into one BrowserGym action."""

    def __init__(
        self,
        model_config: dict,
        action_set=None,
        actions: str = "custom",
        limit_to_ctx: bool = True,
        **kw,
    ):
        model = FoundationModel(**model_config) if model_config else FoundationModel(
            provider="openai", name="gpt-4.1"
        )
        super().__init__(model=model)
        self.action_set = action_set
        self.actions = actions
        self.limit_to_ctx = limit_to_ctx
        self.goal = None
        self.current_skills = []
        # Pre-compute the action documentation string once.
        self.action_doc = ""
        if self.action_set is not None:
            try:
                self.action_doc = self.action_set.describe(
                    with_long_description=True, with_examples=True
                )
            except Exception:  # noqa: BLE001 - documentation is best-effort
                self.action_doc = ""

    def reset(self, goal, html=None, screenshot=None, **kw):
        self.goal = goal

    def act(self, subtask=None, obs=None, goal=None, **kwargs) -> Tuple[str, dict]:
        meta = {"subtask": subtask}
        try:
            goal = goal or self.goal or (obs.get("goal") if isinstance(obs, dict) else None) or ""
            axtree = _axtree_from_obs(obs)
            err = ""
            if isinstance(obs, dict) and obs.get("last_action_error"):
                err = (
                    f"The previous action produced this error, avoid repeating it:\n"
                    f"{obs.get('last_action_error')}\n"
                )
            skill_context = self._format_skill_context()
            prompt = _EXECUTOR_PROMPT.format(
                goal=goal,
                subtask=(subtask or goal) + skill_context,
                actions=self.action_doc or "(standard BrowserGym actions)",
                axtree=axtree,
                error=err,
            )
            response = self.act_model(prompt)
            action = self.extract_action(response)
            if not action:
                action = "noop()"
            return action, meta
        except Exception as e:  # noqa: BLE001 - never break the rollout
            logger.warning("Executor act failed (%s); emitting noop().", e)
            return "noop()", meta

    def _format_skill_context(self) -> str:
        """Render persisted polymorphic skills as reusable grounding guidance."""
        if not self.current_skills:
            return ""
        rendered = []
        remaining_chars = 6000
        for skill in self.current_skills[:8]:
            if isinstance(skill, dict):
                name = skill.get("name", "unnamed")
                description = skill.get("description", "")
                content = skill.get("content", "")
            else:
                name = getattr(skill, "name", "unnamed")
                description = getattr(skill, "description", "")
                content = getattr(skill, "content", "")
            entry = f"\nSkill {name}: {description}\n{content}"
            if len(entry) > remaining_chars:
                entry = entry[:remaining_chars]
            rendered.append(entry)
            remaining_chars -= len(entry)
            if remaining_chars <= 0:
                break
        return "\n\nReusable skills learned from prior successful tasks:" + "".join(rendered)

    def act_model(self, prompt: str) -> str:
        """Single-prompt model call (kept separate so subclasses can wrap)."""
        return self.model.generate(prompt=prompt)


class HsmV3ASIAgent(Agent, ASIAgentMixin):
    """Hierarchical planner + executor agent over the BrowserGym action set."""

    def __init__(
        self,
        model_configs: dict,
        actions: str = "custom",
        limit_to_ctx: bool = True,
        max_call_depth: int = 3,
        executor_cls: Type[_ExecutorAgent] = _ExecutorAgent,
        action_file_path: Optional[str] = None,
    ):
        ASIAgentMixin.__init__(self)

        main_cfg, planner_cfg, executor_cfg = parse_model_configs(
            _normalize_model_configs(model_configs)
        )
        self.main_cfg = main_cfg
        self.planner_cfg = planner_cfg
        self.executor_cfg = executor_cfg

        self.action_set = initialize_custom_action_set(action_file_path)

        self.planner = BasicLLMPlanner(
            model_config=planner_cfg,
        )
        self.executor = executor_cls(
            executor_cfg,
            action_set=self.action_set,
            actions=actions,
            limit_to_ctx=limit_to_ctx,
        )

        self.actions = actions
        self.limit_to_ctx = limit_to_ctx
        self.max_call_depth = max_call_depth
        self.action_history: List[str] = []
        self._current_subtask: Optional[str] = None
        self.goal = None
        # Tracks whether reset() has run. get_action() lazily self-resets if a
        # caller (e.g. eval_loop) forgets to, so the planner is never a no-op.
        self._did_reset = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def reset(self, goal, html=None, screenshot=None, goal_image_urls=None, task_id=None, **kwargs):
        self.goal = goal
        try:
            self.reset_common_state(goal, html, screenshot, goal_image_urls or [])
        except Exception:  # noqa: BLE001 - goal-image download is optional
            self.action_history = []
        # Planner.reset expects a base64 screenshot string; guard against None.
        try:
            self.planner.reset(goal, html, screenshot)
        except Exception as e:  # noqa: BLE001 - planner state is best-effort
            logger.debug("Planner reset skipped (%s).", e)
        self.executor.reset(goal, html, screenshot)
        self.action_history = []
        self._current_subtask = None
        self._did_reset = True

    def update(self, html=None, screenshot=None, trace=None):
        try:
            self.update_common_state(html, screenshot, trace)
        except Exception:  # noqa: BLE001
            pass

    def obs_preprocessor(self, obs):
        return obs

    # ------------------------------------------------------------------
    # Acting
    # ------------------------------------------------------------------
    def _plan_subtask(self, obs) -> Optional[str]:
        """Ask the planner for the next high-level subtask; tolerate failures."""
        try:
            subtask = self.planner.act(
                metadata={"goal": self.goal},
                past_actions=list(self.action_history),
            )
            if subtask:
                return str(subtask).strip()
        except Exception as e:  # noqa: BLE001 - planner is advisory only
            logger.debug("Planner act failed (%s); falling back to goal.", e)
        return None

    def get_action(self, obs) -> Tuple[str, dict]:
        # Safety net: if a caller drives the agent without ever calling reset()
        # the planner's state (screenshot_history/goal) is unset and act() would
        # raise -> the planner would silently no-op. Lazily self-init here so the
        # planner is always functional even when reset() was forgotten.
        if not self._did_reset:
            goal_from_obs = obs.get("goal") if isinstance(obs, dict) else None
            screenshot = obs.get("screenshot") if isinstance(obs, dict) else None
            try:
                self.reset(goal=goal_from_obs, screenshot=screenshot)
            except Exception as e:  # noqa: BLE001 - never break the rollout
                logger.debug("Lazy reset failed (%s); continuing.", e)
                self._did_reset = True
                if not self.goal:
                    self.goal = goal_from_obs
        elif not self.goal and isinstance(obs, dict):
            self.goal = obs.get("goal")

        self._current_subtask = self._plan_subtask(obs)
        subtask = self._current_subtask or self.goal

        action, meta = self.executor.act(subtask=subtask, obs=obs, goal=self.goal)
        self.action_history.append(action)

        info = {"subtask": self._current_subtask}
        info.update(meta or {})
        return action, info

    # ------------------------------------------------------------------
    # State (consumed by the skill-induction subclass)
    # ------------------------------------------------------------------
    def get_state_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "action_history": list(self.action_history),
            "current_subtask": self._current_subtask,
        }

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        self.goal = state_dict.get("goal", self.goal)
        self.action_history = list(state_dict.get("action_history", []))
        self._current_subtask = state_dict.get("current_subtask")
