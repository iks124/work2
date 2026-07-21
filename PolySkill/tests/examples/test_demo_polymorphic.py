"""The polymorphic demo must run offline end-to-end (it is the module's public showcase)."""
import os
import subprocess
import sys


def test_demo_runs_offline(tmp_path):
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    demo = os.path.join(repo_root, "examples", "demo_polymorphic_induction.py")
    result = subprocess.run(
        [sys.executable, demo, "--storage", str(tmp_path / "skills")],
        capture_output=True, text=True, timeout=120, cwd=repo_root,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SKILL STORED" in result.stdout
    assert "AbstractShoppingSite" in result.stdout
    assert (tmp_path / "skills" / "skills.json").exists()
