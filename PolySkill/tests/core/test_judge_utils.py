import gzip, json, pickle
import numpy as np
from polyskill.core.judge.utils import load_trajectory_data, extract_task_from_trajectory


def _write_fake(dirp):
    dirp.mkdir(parents=True, exist_ok=True)
    shot = np.zeros((4, 4, 3), dtype=np.uint8)
    for i, act in enumerate(["click('a1')", "fill('a2','x')"]):
        step = {"step": i, "action": act, "reward": 0.0,
                "obs": {"goal": "buy a switch game", "screenshot": shot, "last_action_error": ""}}
        with gzip.open(dirp / f"step_{i}.pkl.gz", "wb") as f:
            pickle.dump(step, f)
    (dirp / "summary_info.json").write_text(json.dumps({"cum_reward": 1.0, "n_steps": 2}))


def test_judge_utils_use_clean_loader(tmp_path):
    d = tmp_path / "webarena.21"; _write_fake(d)
    traj = load_trajectory_data(str(d))
    assert extract_task_from_trajectory(traj) == "buy a switch game"
