"""BrowserGym-native trajectory loader (replaces the internal protobuf format)."""
from __future__ import annotations
import os, gzip, json, pickle, glob
from typing import List, Optional
from PIL import Image
import numpy as np


class Trajectory:
    def __init__(self, result_dir: str, steps: List[dict], summary: dict):
        self.result_dir = result_dir
        self.steps = steps
        self.summary = summary

    @property
    def goal(self) -> str:
        for s in self.steps:
            g = (s.get("obs") or {}).get("goal")
            if g:
                return g if isinstance(g, str) else str(g)
        return self.summary.get("goal", "")

    @property
    def actions(self) -> List[str]:
        return [s["action"] for s in self.steps if s.get("action")]

    @property
    def success(self) -> bool:
        return float(self.summary.get("cum_reward", 0) or 0) > 0

    def screenshots(self, save_dir: Optional[str] = None, max_images: int = 50) -> List[str]:
        out: List[str] = []
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        for i, s in enumerate(self.steps):
            shot = (s.get("obs") or {}).get("screenshot")
            if shot is None:
                continue
            img = Image.fromarray(np.asarray(shot).astype("uint8"))
            p = os.path.join(save_dir or self.result_dir, f"screenshot_step_{i}.png")
            img.save(p)
            out.append(p)
            if len(out) >= max_images:
                break
        return out

    def final_response(self) -> str:
        for s in reversed(self.steps):
            a = s.get("action") or ""
            if "send_msg_to_user" in a:
                return a
        return ""


def load_trajectory(result_dir: str) -> Trajectory:
    step_files = sorted(glob.glob(os.path.join(result_dir, "step_*.pkl.gz")),
                        key=lambda p: int(p.rsplit("_", 1)[1].split(".")[0]))
    steps = []
    for p in step_files:
        with gzip.open(p, "rb") as f:
            steps.append(pickle.load(f))
    summary_path = os.path.join(result_dir, "summary_info.json")
    summary = json.loads(open(summary_path).read()) if os.path.exists(summary_path) else {}
    return Trajectory(result_dir, steps, summary)
