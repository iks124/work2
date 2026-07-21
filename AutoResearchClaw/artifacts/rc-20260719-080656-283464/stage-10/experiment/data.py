from pathlib import Path
from typing import Iterator, Tuple

import numpy as np
import torch
from torch import Tensor

from experiment_config import ExperimentConfig

class SplitCIFAR100Features:
    """
    Real features exported by the pinned official CaRE ViT implementation.

    The NPZ file must contain train_features, train_labels, test_features,
    test_labels, checkpoint_sha256, and care_commit. Formal execution fails
    closed when this provenance is absent.
    """

    def __init__(self, config: ExperimentConfig) -> None:
        feature_path = Path(config.feature_path)
        order_path = Path(config.class_orders_path)
        if not feature_path.is_file():
            raise FileNotFoundError(
                f"Missing official CaRE feature export: {feature_path}"
            )
        if not order_path.is_file():
            raise FileNotFoundError(f"Missing saved class orders: {order_path}")

        archive = np.load(feature_path, allow_pickle=False)
        required = {
            "train_features",
            "train_labels",
            "test_features",
            "test_labels",
            "checkpoint_sha256",
            "care_commit",
        }
        missing = required.difference(archive.files)
        if missing:
            raise ValueError(f"Feature export lacks provenance/data: {missing}")

        self.train_x = np.asarray(archive["train_features"], dtype=np.float32)
        self.train_y = np.asarray(archive["train_labels"], dtype=np.int64)
        self.test_x = np.asarray(archive["test_features"], dtype=np.float32)
        self.test_y = np.asarray(archive["test_labels"], dtype=np.int64)
        self.checkpoint_sha256 = str(archive["checkpoint_sha256"].item())
        self.care_commit = str(archive["care_commit"].item())
        self.orders = np.asarray(np.load(order_path), dtype=np.int64)

        if self.train_x.ndim != 2 or self.test_x.ndim != 2:
            raise ValueError("CaRE exports must be [samples, embedding_dim]")
        if self.train_x.shape[1] != self.test_x.shape[1]:
            raise ValueError("Train/test embedding dimensions differ")
        if self.train_y.shape != (self.train_x.shape[0],):
            raise ValueError("Invalid training labels")
        if self.test_y.shape != (self.test_x.shape[0],):
            raise ValueError("Invalid test labels")
        if len(self.checkpoint_sha256) != 64 or not self.care_commit:
            raise ValueError("Invalid checkpoint or CaRE commit provenance")
        if self.orders.ndim != 2 or self.orders.shape[1] != 100:
            raise ValueError("Class orders must have shape [orders,100]")
        if self.orders.shape[0] < 3:
            raise ValueError("At least three saved class orders are required")
        expected = np.arange(100)
        for order in self.orders:
            if not np.array_equal(np.sort(order), expected):
                raise ValueError("Every class order must permute 0..99")

    @property
    def embedding_dim(self) -> int:
        return int(self.train_x.shape[1])

    def task_arrays(
        self,
        order_index: int,
        task_index: int,
        classes_per_task: int,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        order = self.orders[order_index]
        current = order[
            task_index * classes_per_task:
            (task_index + 1) * classes_per_task
        ]
        seen = order[: (task_index + 1) * classes_per_task]
        train_mask = np.isin(self.train_y, current)
        test_mask = np.isin(self.test_y, seen)
        return (
            self.train_x[train_mask],
            self.train_y[train_mask],
            self.test_x[test_mask],
            self.test_y[test_mask],
        )

def deterministic_batches(
    features: np.ndarray,
    labels: np.ndarray,
    batch_size: int,
    seed: int,
    epoch: int,
) -> Iterator[Tuple[Tensor, Tensor]]:
    generator = np.random.default_rng(seed * 100_003 + epoch)
    indices = generator.permutation(features.shape[0])
    for start in range(0, indices.size, batch_size):
        selected = indices[start:start + batch_size]
        yield (
            torch.from_numpy(features[selected]),
            torch.from_numpy(labels[selected]),
        )

def deterministic_smoke_fixture() -> Tuple[Tensor, Tensor]:
    values = torch.arange(4 * 17 * 64, dtype=torch.float32)
    tokens = (values.reshape(4, 17, 64) / values.numel()).requires_grad_(True)
    labels = torch.tensor([0, 1, 2, 3], dtype=torch.long)
    return tokens, labels