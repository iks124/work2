"""Clean-room agent base classes for PolySkill.

Defines the minimal :class:`Agent` interface every PolySkill agent implements
plus :class:`BasicFMAgent`, a thin convenience wrapper around a
:class:`~polyskill.model.FoundationModel` that handles prompting and extracting
a single ``<action>...</action>`` payload from the model response.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

from polyskill.model import FoundationModel

try:  # reuse the shared helpers when available
    from polyskill.utils.action_utils import remove_thinking
except Exception:  # pragma: no cover - defensive fallback
    def remove_thinking(response, cot_open_tag="<thinking>", cot_close_tag="</thinking>"):
        return re.sub(rf"{cot_open_tag}[\W\w]*?{cot_close_tag}", "", response)

try:
    from polyskill.utils.action_parsing_utils import extract_content_by_tags
except Exception:  # pragma: no cover - defensive fallback
    def extract_content_by_tags(text, tags):
        extracted = {}
        for tag in tags:
            match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
            extracted[tag] = match.group(1) if match else None
        return extracted


class Agent:
    """Base class for all PolySkill agents.

    Subclasses must implement :meth:`get_action`.  The remaining hooks have
    sensible no-op defaults so simple agents need only override what they use.
    """

    def obs_preprocessor(self, obs):
        """Return the observation unchanged by default."""
        return obs

    def reset(self, goal, html=None, screenshot=None, **kwargs):
        """Reset agent state for a new task, storing the goal."""
        self.goal = goal

    def update(self, html=None, screenshot=None, trace=None):
        """Update agent state after an environment step (no-op by default)."""
        return None

    def get_action(self, obs) -> Tuple[str, dict]:
        """Return ``(action_str, info_dict)`` for the given observation."""
        raise NotImplementedError


class BasicFMAgent(Agent):
    """Agent backed by a single :class:`FoundationModel`.

    Provides :meth:`act` (a direct passthrough to ``model.generate``) and
    :meth:`extract_action` which pulls the ``<action>...</action>`` payload from
    a model response.
    """

    def __init__(
        self,
        model: Optional[FoundationModel] = None,
        model_name: Optional[str] = None,
        model_provider: Optional[str] = None,
        **kw,
    ):
        if model is None:
            # Without a model instance we need at least a provider+name to build
            # one; otherwise FoundationModel._model_string() would crash on
            # None.lower(). Fail fast with a clear message instead.
            if not (model_provider and model_name):
                raise ValueError(
                    "BasicFMAgent requires a model or model_provider+model_name"
                )
            model = FoundationModel(provider=model_provider, name=model_name)
        self.model = model

    def act(
        self,
        prompt: Optional[str] = None,
        messages=None,
        images=None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        kwargs = {}
        if prompt is not None:
            kwargs["prompt"] = prompt
        if messages is not None:
            kwargs["messages"] = messages
        if images is not None:
            kwargs["images"] = images
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        return self.model.generate(**kwargs)

    def extract_action(self, text: str) -> str:
        """Extract the ``<action>...</action>`` payload, else return stripped text."""
        if text is None:
            return ""
        cleaned = remove_thinking(text)
        extracted = extract_content_by_tags(cleaned, ["action"]).get("action")
        if extracted is not None:
            return extracted.strip()
        return cleaned.strip()
