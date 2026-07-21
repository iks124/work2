"""Gradual complexity curriculum for self-proposing exploration (PolySkill paper §4.3).

``task_complexity_schedule="gradual"`` starts with atomic single-method goals,
then ramps to two-step and finally compositional goals as the exploration
budget is consumed.
"""
from __future__ import annotations


class GradualCurriculum:
    """Monotonically increasing complexity schedule over a fixed iteration budget.

    The budget is divided into three equal thirds:
    - ``[0, 1/3)``  → ``"atomic"``        (tier 1)
    - ``[1/3, 2/3)``→ ``"two_step"``      (tier 2)
    - ``[2/3, 1]``  → ``"compositional"`` (tier 3)

    Args:
        max_iterations: Total number of exploration iterations (≥ 1).
    """

    _THRESHOLDS = (1 / 3, 2 / 3)  # fractions of budget
    _LABELS = ("atomic", "two_step", "compositional")
    _TIERS = (1, 2, 3)

    def __init__(self, max_iterations: int) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1.")
        self.max_iterations = max_iterations

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def complexity_at(self, iteration: int) -> str:
        """Return the complexity label for *iteration*.

        Args:
            iteration: Zero-based iteration index in ``[0, max_iterations)``.

        Returns:
            One of ``"atomic"``, ``"two_step"``, ``"compositional"``.
        """
        frac = self._fraction(iteration)
        if frac < self._THRESHOLDS[0]:
            return "atomic"
        if frac < self._THRESHOLDS[1]:
            return "two_step"
        return "compositional"

    def max_complexity(self, iteration: int) -> int:
        """Return an integer complexity tier (1/2/3) for *iteration*.

        The returned value is monotonically non-decreasing across iterations.

        Returns:
            ``1`` (atomic), ``2`` (two_step), or ``3`` (compositional).
        """
        label = self.complexity_at(iteration)
        return self._LABELS.index(label) + 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fraction(self, iteration: int) -> float:
        """Normalise *iteration* to ``[0, 1]``."""
        # Clamp to valid range.
        it = max(0, min(iteration, self.max_iterations - 1))
        # When max_iterations==1 every fraction is 0.0 → "atomic".
        return it / max(self.max_iterations - 1, 1)
