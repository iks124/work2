from typing import Dict

import torch
from torch import Tensor

from config import ExperimentConfig


class SplitCIFAR100DataModule:
    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config

    def smoke_fixture(self, seed: int) -> Dict[str, Tensor]:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        tokens = torch.randn(
            self.config.batch_size,
            self.config.token_count,
            self.config.embedding_dim,
            generator=generator,
            dtype=torch.float32,
        ).requires_grad_(True)
        labels = torch.randint(
            0,
            self.config.num_classes,
            (self.config.batch_size,),
            generator=generator,
        )
        return {"tokens": tokens, "labels": labels}