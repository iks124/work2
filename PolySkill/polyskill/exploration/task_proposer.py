"""Task proposer for self-guided exploration (PolySkill paper §3.4).

The learned abstract domain classes act as a SCHEMA giving a strong prior for
what to discover — the unfilled abstract-class methods on the current site
become the exploration goals (structured exploration).  A ``novelty_bonus``
biases the proposer toward not-yet-covered functionality.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class ProposedTask:
    """A single exploration task proposed by the TaskProposer.

    Attributes:
        goal: Natural-language goal string to present to the agent.
        target_method: The abstract-class method name this task targets.
        complexity: One of ``"atomic"``, ``"two_step"``, ``"compositional"``.
    """

    goal: str
    target_method: str
    complexity: str


class TaskProposer:
    """Propose exploration tasks biased toward uncovered abstract-class methods.

    Uses the abstract domain interface (e.g. ``AbstractShoppingSite``) as a
    schema of what to discover.  Uncovered methods (those absent from or
    falsy in ``coverage``) receive a score of ``1.0 + novelty_bonus``; covered
    methods receive ``1.0``.  The highest-scored method wins (ties broken by
    list order).

    If all methods are covered the proposer falls back to a compositional goal
    (e.g. ``"purchase_item"``).

    When a ``model`` is provided and ``use_abstract_classes=True`` the goal
    text is phrased by the LLM; otherwise a deterministic template is used so
    the class works offline without any API key.

    Args:
        domain: Domain id (e.g. ``"shopping"``, ``"dev_tools"``).
        model: Optional :class:`~polyskill.model.FoundationModel` instance.
        use_abstract_classes: Whether to prompt the model using abstract-class
            context. Only meaningful when *model* is set.
        novelty_bonus: Score boost for uncovered methods (default ``0.2``).
        temperature: LLM temperature for goal phrasing (default ``0.3``).
    """

    def __init__(
        self,
        domain: str,
        model: Optional[Any] = None,
        use_abstract_classes: bool = True,
        novelty_bonus: float = 0.2,
        temperature: float = 0.3,
    ) -> None:
        self.domain = domain
        self.model = model
        self.use_abstract_classes = use_abstract_classes
        self.novelty_bonus = novelty_bonus
        self.temperature = temperature

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def propose(
        self,
        site: str,
        coverage: Dict[str, Any],
        abstract_methods: List[str],
        history: Optional[List[Any]] = None,
    ) -> ProposedTask:
        """Propose the next exploration task for *site*.

        Args:
            site: Site identifier (e.g. ``"webarena_shopping"``).
            coverage: Mapping of method name → truthy value when covered.
            abstract_methods: Ordered list of abstract-class method names.
            history: Optional list of previously proposed tasks (unused by
                the base scoring logic but available for future extensions).

        Returns:
            A :class:`ProposedTask` with goal, target_method, and complexity.
        """
        history = history or []

        target_method, complexity = self._select_method(coverage, abstract_methods)
        goal = self._phrase_goal(site, target_method, complexity)
        return ProposedTask(goal=goal, target_method=target_method, complexity=complexity)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _score_method(self, method: str, coverage: Dict[str, Any]) -> float:
        """Return the exploration score for *method* given current *coverage*."""
        covered = bool(coverage.get(method))
        return 1.0 if covered else 1.0 + self.novelty_bonus

    def _select_method(
        self,
        coverage: Dict[str, Any],
        abstract_methods: List[str],
    ) -> tuple[str, str]:
        """Pick the best target method and its complexity label.

        Returns:
            ``(target_method, complexity)`` tuple.
        """
        if not abstract_methods:
            return "explore", "atomic"

        # Score all methods; keep order so ties go to the first one.
        scored = [(m, self._score_method(m, coverage)) for m in abstract_methods]
        best_method, best_score = max(scored, key=lambda x: x[1])

        # All covered when best score is 1.0 (no novelty bonus applied).
        if best_score <= 1.0:
            # Fallback: compositional goal.
            return self._compositional_fallback(abstract_methods), "compositional"

        # Determine complexity: uncovered single method → "atomic".
        return best_method, "atomic"

    # Per-domain compositional target chosen when all atomic methods are covered.
    _COMPOSITIONAL_TARGETS: Dict[str, str] = {
        "shopping": "purchase_item",
        "dev_tools": "clone_and_open_issue",
    }
    _DEFAULT_COMPOSITIONAL = "compositional"

    def _compositional_fallback(self, abstract_methods: List[str]) -> str:
        """Return a domain-appropriate compositional target method name.

        Once every atomic method on a site is covered, the proposer escalates to
        a multi-step (compositional) goal. The target depends on the domain, e.g.
        shopping → ``purchase_item`` (search + add + checkout), dev_tools →
        ``clone_and_open_issue``. Unknown domains fall back to a generic name.
        """
        return self._COMPOSITIONAL_TARGETS.get(self.domain, self._DEFAULT_COMPOSITIONAL)

    def _phrase_goal(self, site: str, target_method: str, complexity: str) -> str:
        """Return a natural-language goal string.

        If a model is available and ``use_abstract_classes`` is True, the LLM
        phrases the goal; otherwise a deterministic template is used.
        """
        if self.model is not None and self.use_abstract_classes:
            return self._llm_phrase_goal(site, target_method)
        return self._template_goal(site, target_method)

    def _template_goal(self, site: str, target_method: str) -> str:
        """Deterministic goal template (offline / no-model path)."""
        human_readable = target_method.replace("_", " ")
        return f"On {site}, accomplish: {human_readable}"

    def _llm_phrase_goal(self, site: str, target_method: str) -> str:
        """Ask the LLM to phrase a concrete natural-language goal."""
        from polyskill.prompts.induction.polymorphic import domain_to_class_name

        abstract_class = domain_to_class_name(self.domain)
        prompt = (
            f"You are helping a web agent explore the site '{site}'.\n"
            f"The domain interface is `{abstract_class}` and the target method is "
            f"`{target_method}`.\n"
            "Write a single, concrete natural-language goal sentence that an agent "
            "should attempt in order to exercise this method.  Output only the goal "
            "sentence, no explanation."
        )
        try:
            text = self.model.generate(prompt=prompt, temperature=self.temperature)
            return text.strip() if text else self._template_goal(site, target_method)
        except Exception:  # pragma: no cover - network / key errors in CI
            return self._template_goal(site, target_method)
