import pytest
from polyskill.core.judge.trajectory_judge import TrajectoryJudge


def test_extract_success_parsing():
    j = TrajectoryJudge({"provider": "openai", "name": "gpt-4.1", "temperature": 0})
    assert j._extract_success_from_evaluation("Thoughts: looks done\nStatus: success") is True
    assert j._extract_success_from_evaluation("Thoughts: nope\nStatus: failure") is False
    assert j._extract_success_from_evaluation(
        "I considered Status: success, but the task is incomplete.\nStatus: failure"
    ) is False
    assert j._extract_success_from_evaluation(
        "Status: failure\nAfter checking again:\nStatus: 'success'"
    ) is True
    assert j._extract_success_from_evaluation("status: success appears in prose") is False
