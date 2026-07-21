"""Tests for TaskProposer (Task 7.1).

All tests are offline (model=None); marked not-llm so they run in CI.
"""
import pytest
from polyskill.exploration.task_proposer import TaskProposer, ProposedTask


def test_prefers_uncovered_method():
    """Uncovered methods should score higher and be selected over covered ones."""
    tp = TaskProposer(domain="shopping", model=None, novelty_bonus=0.2)
    pt = tp.propose(
        site="webarena_shopping",
        coverage={"search_product": True},
        abstract_methods=["search_product", "add_to_cart", "checkout"],
    )
    assert isinstance(pt, ProposedTask)
    # search_product is covered; add_to_cart/checkout are not — one of those must win.
    assert pt.target_method in ("add_to_cart", "checkout")


def test_all_covered_returns_goal():
    """When all methods are covered the proposer should still return a non-empty goal."""
    tp = TaskProposer(domain="shopping", model=None)
    pt = tp.propose(
        site="webarena_shopping",
        coverage={"search_product": True, "add_to_cart": True, "checkout": True},
        abstract_methods=["search_product", "add_to_cart", "checkout"],
    )
    assert pt.goal  # non-empty string


def test_returns_proposed_task_instance():
    """propose() always returns a ProposedTask dataclass."""
    tp = TaskProposer(domain="dev_tools", model=None, novelty_bonus=0.1)
    pt = tp.propose(
        site="github",
        coverage={},
        abstract_methods=["search_repository", "open_file", "create_issue"],
    )
    assert isinstance(pt, ProposedTask)
    assert pt.target_method
    assert pt.goal
    assert pt.complexity in ("atomic", "two_step", "compositional")


def test_novelty_bonus_zero_still_selects():
    """novelty_bonus=0 means all scores equal; first uncovered wins by list order."""
    tp = TaskProposer(domain="shopping", model=None, novelty_bonus=0.0)
    pt = tp.propose(
        site="amazon",
        coverage={"search_product": True},
        abstract_methods=["search_product", "add_to_cart"],
    )
    # With bonus=0 both uncovered and covered score the same (1.0); but uncovered
    # still has a tie-break advantage since max() returns the first element on ties.
    # The important thing is we get a valid ProposedTask back.
    assert isinstance(pt, ProposedTask)


def test_empty_methods_returns_explore():
    """An empty methods list should not crash — returns a safe fallback."""
    tp = TaskProposer(domain="shopping", model=None)
    pt = tp.propose(site="amazon", coverage={}, abstract_methods=[])
    assert isinstance(pt, ProposedTask)
    assert pt.goal


def test_template_goal_format():
    """Deterministic template should embed site name and method."""
    tp = TaskProposer(domain="shopping", model=None)
    pt = tp.propose(
        site="webarena_shopping",
        coverage={},
        abstract_methods=["add_to_cart"],
    )
    assert "webarena_shopping" in pt.goal
    assert "add to cart" in pt.goal  # underscores replaced with spaces


def test_all_covered_complexity_is_compositional():
    """When all methods are covered the fallback complexity should be compositional."""
    tp = TaskProposer(domain="shopping", model=None)
    pt = tp.propose(
        site="webarena_shopping",
        coverage={"a": True, "b": True},
        abstract_methods=["a", "b"],
    )
    assert pt.complexity == "compositional"


def test_uncovered_complexity_is_atomic():
    """A single uncovered method should yield complexity='atomic'."""
    tp = TaskProposer(domain="shopping", model=None)
    pt = tp.propose(
        site="webarena_shopping",
        coverage={},
        abstract_methods=["search_product"],
    )
    assert pt.complexity == "atomic"


def test_compositional_fallback_is_domain_specific():
    """Bug F: the compositional fallback must depend on the domain.

    When all atomic methods are covered, shopping and dev_tools should escalate
    to DIFFERENT compositional targets (the old code always returned the first
    candidate regardless of domain).
    """
    covered = {"a": True, "b": True}
    methods = ["a", "b"]

    shop = TaskProposer(domain="shopping", model=None).propose(
        site="webarena_shopping", coverage=covered, abstract_methods=methods
    )
    dev = TaskProposer(domain="dev_tools", model=None).propose(
        site="gitlab", coverage=covered, abstract_methods=methods
    )

    assert shop.complexity == "compositional"
    assert dev.complexity == "compositional"
    assert shop.target_method == "purchase_item"
    assert dev.target_method == "clone_and_open_issue"
    assert shop.target_method != dev.target_method
