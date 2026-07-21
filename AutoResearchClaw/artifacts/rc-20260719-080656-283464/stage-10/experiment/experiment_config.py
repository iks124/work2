from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class ExperimentConfig:
    feature_path: str = "care_cifar100_features.npz"
    class_orders_path: str = "class_orders.npy"
    output_path: str = "results.json"
    seeds: Tuple[int, ...] = (0, 1, 2)
    conditions: Tuple[str, ...] = (
        "signed_top2",
        "hard_top2",
        "dense_softmax",
    )
    num_tasks: int = 10
    classes_per_task: int = 10
    basis_count: int = 8
    basis_rank: int = 2
    expert_rank: int = 1
    temperature: float = 0.2
    learning_rate: float = 1e-3
    epochs_per_task: int = 50
    batch_size: int = 128
    hysteresis_weight: float = 0.05
    load_balance_weight: float = 0.01
    route_ema_decay: float = 0.99
    gradient_clip_norm: float = 1.0
    time_limit_seconds: int = 300

    def __post_init__(self) -> None:
        if self.seeds != (0, 1, 2):
            raise ValueError("Exactly three paired seeds are required")
        if self.num_tasks * self.classes_per_task != 100:
            raise ValueError("The protocol must partition all 100 classes")
        if self.basis_count < 2:
            raise ValueError("At least two memory bases are required")
        if self.basis_rank != 2 or self.expert_rank != 1:
            raise ValueError(
                "Rank-2 composition and two active rank-1 experts provide "
                "matched active adapter multiply-add counts"
            )
        if self.temperature <= 0 or self.learning_rate <= 0:
            raise ValueError("Temperature and learning rate must be positive")