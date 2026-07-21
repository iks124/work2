from typing import Dict, Tuple

import torch
from torch import Tensor, nn
import torch.nn.functional as F

from config import ExperimentConfig


class ConditionBase(nn.Module):
    def __init__(self, config: ExperimentConfig) -> None:
        super().__init__()
        self.config = config
        self.prototypes = nn.Parameter(
            torch.randn(config.num_classes, config.embedding_dim)
        )
        self.log_temperature = nn.Parameter(torch.zeros(()))

    def classify(self, features: Tensor) -> Tensor:
        features = F.normalize(features, dim=-1)
        prototypes = F.normalize(self.prototypes, dim=-1)
        temperature = self.log_temperature.exp().clamp_min(1e-8)
        return features @ prototypes.t() / temperature

    def compute_loss(
        self,
        logits: Tensor,
        labels: Tensor,
        auxiliary: Dict[str, Tensor],
    ) -> Tensor:
        return F.cross_entropy(logits, labels)

    def stored_parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.parameters())

    def active_flops(self, batch_size: int, token_count: int) -> int:
        return (
            2
            * batch_size
            * self.config.embedding_dim
            * self.config.num_classes
        )


class SignedTop2BasisMemory(ConditionBase):
    def __init__(self, config: ExperimentConfig) -> None:
        super().__init__(config)
        m, d, r = (
            config.basis_count,
            config.embedding_dim,
            config.basis_rank,
        )
        self.keys = nn.Parameter(torch.randn(m, d))
        self.basis_a = nn.Parameter(torch.randn(m, d, r) * 0.02)
        self.basis_b = nn.Parameter(torch.randn(m, r, d) * 0.02)

    def forward(
        self,
        tokens: Tensor,
    ) -> Tuple[Tensor, Dict[str, Tensor]]:
        query = F.normalize(tokens[:, 0], dim=-1)
        scores = query @ F.normalize(self.keys, dim=-1).t()
        scores = scores / self.config.router_temperature

        _, indices = scores.abs().topk(2, dim=-1)
        selected = scores.gather(1, indices)
        coefficients = selected / selected.abs().sum(
            dim=1, keepdim=True
        ).clamp_min(1e-8)
        route = torch.zeros_like(scores).scatter(
            1, indices, coefficients
        )

        selected_a = self.basis_a[indices]
        selected_b = self.basis_b[indices]
        projected = torch.einsum(
            "bnd,bkdr->bknr", tokens, selected_a
        )
        hidden = F.gelu(projected)
        outputs = torch.einsum(
            "bknr,bkrd->bknd", hidden, selected_b
        )
        delta = (
            outputs * coefficients[:, :, None, None]
        ).sum(dim=1)

        logits = self.classify((tokens + delta)[:, 0])
        return logits, {
            "route": route,
            "coefficients": coefficients,
        }

    def active_flops(self, batch_size: int, token_count: int) -> int:
        router = (
            2
            * batch_size
            * self.config.embedding_dim
            * self.config.basis_count
        )
        adapters = (
            8
            * batch_size
            * token_count
            * self.config.embedding_dim
            * self.config.basis_rank
        )
        return (
            super().active_flops(batch_size, token_count)
            + router
            + adapters
        )


class HardTop2AdapterMixture(ConditionBase):
    def __init__(self, config: ExperimentConfig) -> None:
        super().__init__(config)
        m, d, r = (
            config.basis_count,
            config.embedding_dim,
            config.adapter_rank,
        )
        self.keys = nn.Parameter(torch.randn(m, d))
        self.adapter_a = nn.Parameter(torch.randn(m, d, r) * 0.02)
        self.adapter_b = nn.Parameter(torch.randn(m, r, d) * 0.02)

    def forward(
        self,
        tokens: Tensor,
    ) -> Tuple[Tensor, Dict[str, Tensor]]:
        query = F.normalize(tokens[:, 0], dim=-1)
        scores = query @ F.normalize(self.keys, dim=-1).t()
        values, indices = scores.topk(2, dim=-1)
        weights = values.softmax(dim=-1)
        route = torch.zeros_like(scores).scatter(1, indices, weights)

        selected_a = self.adapter_a[indices]
        selected_b = self.adapter_b[indices]
        projected = torch.einsum(
            "bnd,bkdr->bknr", tokens, selected_a
        )
        hidden = F.gelu(projected)
        outputs = torch.einsum(
            "bknr,bkrd->bknd", hidden, selected_b
        )
        delta = (
            outputs * weights[:, :, None, None]
        ).sum(dim=1)

        logits = self.classify((tokens + delta)[:, 0])
        return logits, {"route": route}

    def active_flops(self, batch_size: int, token_count: int) -> int:
        router = (
            2
            * batch_size
            * self.config.embedding_dim
            * self.config.basis_count
        )
        adapters = (
            8
            * batch_size
            * token_count
            * self.config.embedding_dim
            * self.config.adapter_rank
        )
        return (
            super().active_flops(batch_size, token_count)
            + router
            + adapters
        )


class DenseSoftmaxAdapterMixture(HardTop2AdapterMixture):
    def forward(
        self,
        tokens: Tensor,
    ) -> Tuple[Tensor, Dict[str, Tensor]]:
        query = F.normalize(tokens[:, 0], dim=-1)
        scores = query @ F.normalize(self.keys, dim=-1).t()
        route = scores.softmax(dim=-1)

        projected = torch.einsum(
            "bnd,mdr->bmnr", tokens, self.adapter_a
        )
        hidden = F.gelu(projected)
        outputs = torch.einsum(
            "bmnr,mrd->bmnd", hidden, self.adapter_b
        )
        delta = (
            outputs * route[:, :, None, None]
        ).sum(dim=1)

        logits = self.classify((tokens + delta)[:, 0])
        return logits, {"route": route}

    def active_flops(self, batch_size: int, token_count: int) -> int:
        router = (
            2
            * batch_size
            * self.config.embedding_dim
            * self.config.basis_count
        )
        adapters = (
            4
            * batch_size
            * token_count
            * self.config.embedding_dim
            * self.config.adapter_rank
            * self.config.basis_count
        )
        return (
            ConditionBase.active_flops(
                self, batch_size, token_count
            )
            + router
            + adapters
        )