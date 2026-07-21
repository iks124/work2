import gzip, json, pickle
from PIL import Image
import numpy as np
from polyskill.trajectory import load_trajectory

def _write_fake(dirp):
    dirp.mkdir(parents=True, exist_ok=True)
    shot = np.zeros((4, 4, 3), dtype=np.uint8)
    for i, act in enumerate(["click('a1')", "fill('a2','x')"]):
        step = {"step": i, "action": act, "reward": 0.0,
                "obs": {"goal": "buy a switch game", "screenshot": shot,
                        "last_action_error": ""}}
        with gzip.open(dirp / f"step_{i}.pkl.gz", "wb") as f:
            pickle.dump(step, f)
    (dirp / "summary_info.json").write_text(json.dumps({"cum_reward": 1.0, "n_steps": 2}))

def test_load_and_accessors(tmp_path):
    d = tmp_path / "webarena.21"
    _write_fake(d)
    t = load_trajectory(str(d))
    assert t.goal == "buy a switch game"
    assert t.actions == ["click('a1')", "fill('a2','x')"]
    assert t.success is True
    paths = t.screenshots(save_dir=str(tmp_path / "shots"), max_images=50)
    assert len(paths) == 2 and all(p.endswith(".png") for p in paths)
