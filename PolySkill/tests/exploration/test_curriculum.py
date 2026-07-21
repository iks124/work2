"""Tests for GradualCurriculum (Task 7.2)."""
import pytest
from polyskill.exploration.curriculum import GradualCurriculum


def test_schedule_monotonic():
    """Required test from the spec: atomic at start, compositional at end, tiers non-decreasing."""
    c = GradualCurriculum(max_iterations=150)
    assert c.complexity_at(0) == "atomic"
    assert c.complexity_at(149) == "compositional"
    tiers = [c.max_complexity(i) for i in range(0, 150, 10)]
    assert tiers == sorted(tiers)  # non-decreasing


def test_three_phases():
    """Check the three-phase boundaries for a 150-iteration curriculum."""
    c = GradualCurriculum(max_iterations=150)
    # First third: iterations 0..49 should be atomic
    for i in range(0, 50):
        assert c.complexity_at(i) == "atomic", f"Expected atomic at i={i}"
    # Middle third: iterations 50..99 should be two_step
    for i in range(50, 100):
        assert c.complexity_at(i) == "two_step", f"Expected two_step at i={i}"
    # Last third: iterations 100..149 should be compositional
    for i in range(100, 150):
        assert c.complexity_at(i) == "compositional", f"Expected compositional at i={i}"


def test_tier_values():
    """max_complexity() returns 1/2/3 mapping to atomic/two_step/compositional."""
    c = GradualCurriculum(max_iterations=150)
    assert c.max_complexity(0) == 1
    assert c.max_complexity(75) == 2
    assert c.max_complexity(149) == 3


def test_100_iteration_budget():
    """Coding domain: 100 iterations, still monotonic."""
    c = GradualCurriculum(max_iterations=100)
    assert c.complexity_at(0) == "atomic"
    assert c.complexity_at(99) == "compositional"
    tiers = [c.max_complexity(i) for i in range(0, 100, 5)]
    assert tiers == sorted(tiers)


def test_single_iteration():
    """Edge case: one iteration, should be atomic."""
    c = GradualCurriculum(max_iterations=1)
    assert c.complexity_at(0) == "atomic"
    assert c.max_complexity(0) == 1


def test_invalid_budget():
    """max_iterations < 1 should raise ValueError."""
    with pytest.raises(ValueError):
        GradualCurriculum(max_iterations=0)
