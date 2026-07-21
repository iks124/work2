import glob
import yaml
import pytest
from polyskill.evaluation.eval_config import EvalConfig


@pytest.mark.parametrize("path", sorted(glob.glob("examples/configs/*.yaml")))
def test_config_parses(path):
    d = yaml.safe_load(open(path).read())
    d.pop("skill_induction", None)
    d.pop("exploration", None)
    d.pop("exploration_domains", None)
    EvalConfig(**d)  # must not raise
