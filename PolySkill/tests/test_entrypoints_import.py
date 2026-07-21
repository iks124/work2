import importlib


def test_entrypoints_import():
    for m in [
        "polyskill.experiments.run_eval_with_skill_induction",
        "polyskill.experiments.webarena.run_webarena",
        "polyskill.experiments.mind2web.run_mind2web",
        "polyskill.experiments.self_proposing.run_self_proposing",
    ]:
        importlib.import_module(m)
