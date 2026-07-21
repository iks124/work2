from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExperimentConfig:
    mode: str = "smoke"
    output_path: str = "results.json"
    seeds: Tuple[int, ...] = (0, 1, 2)
    batch_size: int = 4
    token_count: int = 17
    embedding_dim: int = 64
    num_classes: int = 10
    basis_count: int = 8
    active_bases: int = 2
    basis_rank: int = 2
    adapter_rank: int = 4
    router_temperature: float = 0.2
    time_limit_seconds: int = 300

    def __post_init__(self) -> None:
        if self.mode != "smoke":
            raise ValueError("This entry point executes the validated smoke stage")
        if self.seeds != (0, 1, 2):
            raise ValueError("Exactly seeds 0, 1, and 2 are required")
        if self.active_bases != 2:
            raise ValueError("Signed and hard routing require exactly two bases")
        if self.basis_count < self.active_bases:
            raise ValueError("basis_count must be at least active_bases")
        if min(
            self.batch_size,
            self.token_count,
            self.embedding_dim,
            self.num_classes,
            self.basis_rank,
            self.adapter_rank,
        ) <= 0:
            raise ValueError("Dimensions and ranks must be positive")

    def condition_names(self) -> Tuple[str, ...]:
        return (
            "signed_top2_basis_memory",
            "hard_top2_adapter_mixture",
            "dense_softmax_adapter_mixture",
        )