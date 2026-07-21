"""
Utility functions for processing digital agent trajectory data for LLM judging.
"""

import base64
import io
import os
from typing import List, Optional
from PIL import Image

from polyskill.trajectory import load_trajectory, Trajectory


def encode_image(image: Image.Image) -> str:
    """Convert a PIL image to base64 string."""
    if image.mode == "RGBA":
        image = image.convert("RGB")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def load_trajectory_data(trajectory_path: str) -> Trajectory:
    """
    Load trajectory data from a BrowserGym result directory.

    Args:
        trajectory_path: Path to the trajectory result directory

    Returns:
        Trajectory object
    """
    return load_trajectory(trajectory_path)


def extract_screenshots_from_trajectory(traj: Trajectory,
                                        save_dir: Optional[str] = None,
                                        max_images: int = 50) -> List[str]:
    """
    Extract screenshots from a Trajectory.

    Args:
        traj: Trajectory object
        save_dir: Directory to save screenshots (optional)
        max_images: Maximum number of images to extract

    Returns:
        List of image file paths
    """
    return traj.screenshots(save_dir=save_dir, max_images=max_images)


def get_final_response_from_trajectory(traj: Trajectory) -> str:
    """
    Extract the final response from a Trajectory.

    Args:
        traj: Trajectory object

    Returns:
        Final response string
    """
    return traj.final_response()


def extract_task_from_trajectory(traj: Trajectory) -> str:
    """
    Extract the task/goal from a Trajectory.

    Args:
        traj: Trajectory object

    Returns:
        Task description string
    """
    return traj.goal


def get_trajectory_success_status(traj: Trajectory) -> bool:
    """
    Determine if trajectory was successful.

    Args:
        traj: Trajectory object

    Returns:
        True if successful, False otherwise
    """
    return traj.success


def extract_actions_from_trajectory(traj: Trajectory) -> List[str]:
    """
    Extract action strings from a Trajectory.

    Args:
        traj: Trajectory object

    Returns:
        List of action strings
    """
    return traj.actions
