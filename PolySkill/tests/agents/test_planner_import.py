"""Regression test for the planner circular-import bug (Bug A).

Importing ``BasicLLMPlanner`` from the documented symbol path
``polyskill.agents.planner`` must succeed even when it is the FIRST thing a
fresh interpreter imports. Previously this raised ``ImportError`` because the
import chain cycled through ``polyskill.agents.agent`` ->
``vlm_based`` -> ``hsm_agent`` -> ``polyskill.agents.planner`` (partial).

To make the "fresh interpreter, first import" guarantee meaningful (pytest has
already imported half the package by the time this test body runs) we also
re-run the import in a brand-new subprocess with an empty module cache.
"""
import subprocess
import sys


def test_planner_import_is_first_thing():
    # This line must not raise even though pytest may have imported other
    # polyskill modules earlier in the session.
    from polyskill.agents.planner import BasicLLMPlanner

    assert BasicLLMPlanner is not None


def test_planner_import_in_fresh_interpreter():
    """Prove the import works with a completely cold module cache."""
    proc = subprocess.run(
        [sys.executable, "-c",
         "from polyskill.agents.planner import BasicLLMPlanner; print('ok')"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"fresh-interpreter planner import failed:\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    assert proc.stdout.strip() == "ok"
