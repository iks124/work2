from hashlib import sha256
from typing import Dict, Tuple

import numpy as np
import torch
from torch import Tensor, nn
import torch.nn.functional as F

from experiment_config import ExperimentConfig

def immutable_tensor(shape: Tuple[int, ...], phase: float) -> Tensor:
    count = int(np.prod(shape))
    values = np.arange(count, dtype=np.float32)
    values = np.sin(values * 0.017 + phase).reshape(shape)
    return torch.from_numpy(values.copy())

class ReadOnlyAdapterModel(nn.Module):
    def __init__(
        self,
        config: ExperimentConfig,
        embedding_dim: int,
        num_classes: int = 100,
    ) -> None:
        super().__init__()
        self.config = config
        self.embedding_dim = embedding_dim
        self.num_classes = num_classes
        self.query_projection = nn.Linear(embedding_dim, embedding_dim, bias=False)
        self.classifier = nn.Linear(embedding_dim, num_classes, bias=False)
        self.log_temperature = nn.Parameter(torch.zeros(()))
        nn.init.eye_(self.query_projection.weight)
        nn.init.zeros_(self.classifier.weight)

    def features(self, inputs: Tensor) -> Tensor:
        if inputs.ndim == 3:
            return inputs[:, 0]
        if inputs.ndim == 2:
            return inputs
        raise ValueError("Inputs must be [B,D] or [B,N,D]")

    def classify(self, features: Tensor) -> Tensor:
        normalized_x = F.normalize(features, dim=-1)
        normalized_w = F.normalize(self.classifier.weight, dim=-1)
        temperature = self.log_temperature.exp().clamp_min(1e-4)
        return normalized_x @ normalized_w.t() / temperature

    def memory_digest(self) -> str:
        digest = sha256()
        for name, value in self.named_buffers():
            if name.startswith("memory_"):
                digest.update(value.detach().cpu().contiguous().numpy().tobytes())
        return digest.hexdigest()

    def stored_parameter_count(self) -> int:
        trainable = sum(parameter.numel() for parameter in self.parameters())
        memory = sum(
            value.numel()
            for name, value in self.named_buffers()
            if name.startswith("memory_")
        )
        return int(trainable + memory)

    def active_flops(self, batch: int, tokens: int) -> int:
        common = 2 * batch * self.embedding_dim * (
            self.embedding_dim + self.num_classes
        )
        return common + self.adapter_flops(batch, tokens)

    def adapter_flops(self, batch: int, tokens: int) -> int:
        raise RuntimeError("Concrete strategy must define adapter FLOPs")

    def loss(
        self,
        logits: Tensor,
        labels: Tensor,
        auxiliary: Dict[str, Tensor],
    ) -> Tensor:
        del auxiliary
        return F.cross_entropy(logits, labels)

class SignedTop2BasisMemory(ReadOnlyAdapterModel):
    def __init__(self, config: ExperimentConfig, embedding_dim: int) -> None:
        super().__init__(config, embedding_dim)
        m, d, r = config.basis_count, embedding_dim, config.basis_rank
        self.register_buffer("memory_keys", immutable_tensor((m, d), 0.1))
        self.register_buffer("memory_a", immutable_tensor((m, d, r), 0.2) * 0.02)
        self.register_buffer("memory_b", immutable_tensor((m, r, d), 0.3) * 0.02)
        self.register_buffer("route_ema", torch.zeros(100, m))
        self.register_buffer("route_seen", torch.zeros(100, dtype=torch.bool))

    def route(self, query: Tensor) -> Tuple[Tensor, Tensor, Tensor]:
        scores = F.normalize(query, dim=-1) @ F.normalize(
            self.memory_keys, dim=-1
        ).t()
        scores = scores / self.config.temperature
        _, indices = scores.abs().topk(2, dim=-1)
        selected = scores.gather(1, indices)
        coefficients = selected / selected.abs().sum(
            1, keepdim=True
        ).clamp_min(1e-8)
        sparse = torch.zeros_like(scores).scatter(1, indices, coefficients)
        return sparse, indices, coefficients

    def compose_adapter(
        self,
        indices: Tensor,
        coefficients: Tensor,
    ) -> Tuple[Tensor, Tensor]:
        selected_a = self.memory_a[indices]
        selected_b = self.memory_b[indices]
        composed_a = torch.einsum("bk,bkdr->bdr", coefficients, selected_a)
        composed_b = torch.einsum("bk,bkrd->brd", coefficients, selected_b)
        return composed_a, composed_b

    def forward(self, inputs: Tensor) -> Tuple[Tensor, Dict[str, Tensor]]:
        base = self.features(inputs)
        query = self.query_projection(base)
        route, indices, coefficients = self.route(query)
        composed_a, composed_b = self.compose_adapter(indices, coefficients)
        hidden = F.gelu(torch.einsum("bd,bdr->br", base, composed_a))
        delta = torch.einsum("br,brd->bd", hidden, composed_b)
        logits = self.classify(base + delta)
        return logits, {"route": route, "adapted": base + delta}

    @torch.no_grad()
    def update_route_ema(self, route: Tensor, labels: Tensor) -> None:
        for label in labels.unique():
            class_id = int(label.item())
            mean_route = route[labels == label].detach().abs().mean(0)
            if self.route_seen[class_id]:
                self.route_ema[class_id].mul_(
                    self.config.route_ema_decay
                ).add_(mean_route, alpha=1 - self.config.route_ema_decay)
            else:
                self.route_ema[class_id].copy_(mean_route)
                self.route_seen[class_id] = True

    def loss(
        self,
        logits: Tensor,
        labels: Tensor,
        auxiliary: Dict[str, Tensor],
    ) -> Tensor:
        ce = F.cross_entropy(logits, labels)
        current = auxiliary["route"].abs()
        target = self.route_ema[labels].detach()
        valid = self.route_seen[labels]
        midpoint = 0.5 * (current + target)
        js = 0.5 * (
            F.kl_div(midpoint.clamp_min(1e-8).log(), current, reduction="none").sum(1)
            + F.kl_div(midpoint.clamp_min(1e-8).log(), target, reduction="none").sum(1)
        )
        hysteresis = js[valid].mean() if valid.any() else ce.new_zeros(())
        load = current.mean(0)
        balance = ((load - 1 / self.config.basis_count) ** 2).mean()
        return (
            ce
            + self.config.hysteresis_weight * hysteresis
            + self.config.load_balance_weight * balance
        )

    def adapter_flops(self, batch: int, tokens: int) -> int:
        del tokens
        return 4 * batch * self.embedding_dim * self.config.basis_rank

class HardTop2AdapterMixture(ReadOnlyAdapterModel):
    def __init__(self, config: ExperimentConfig, embedding_dim: int) -> None:
        super().__init__(config, embedding_dim)
        m, d, r = config.basis_count, embedding_dim, config.expert_rank
        self.register_buffer("memory_keys", immutable_tensor((m, d), 0.1))
        self.register_buffer("memory_a", immutable_tensor((m, d, r), 0.4) * 0.02)
        self.register_buffer("memory_b", immutable_tensor((m, r, d), 0.5) * 0.02)
        self.register_buffer(
            "memory_padding",
            torch.zeros(m * d * 2),
        )

    def forward(self, inputs: Tensor) -> Tuple[Tensor, Dict[str, Tensor]]:
        base = self.features(inputs)
        query = self.query_projection(base)
        scores = F.normalize(query, dim=-1) @ F.normalize(
            self.memory_keys, dim=-1
        ).t()
        scores = scores / self.config.temperature
        values, indices = scores.topk(2, dim=-1)
        weights = values.softmax(dim=-1)
        a = self.memory_a[indices]
        b = self.memory_b[indices]
        hidden = F.gelu(torch.einsum("bd,bkdr->bkr", base, a))
        outputs = torch.einsum("bkr,bkrd->bkd", hidden, b)
        delta = (outputs * weights[:, :, None]).sum(1)
        route = torch.zeros_like(scores).scatter(1, indices, weights)
        return self.classify(base + delta), {"route": route, "adapted": base + delta}

    def adapter_flops(self, batch: int, tokens: int) -> int:
        del tokens
        return 8 * batch * self.embedding_dim * self.config.expert_rank

class DenseSoftmaxAdapterMixture(HardTop2AdapterMixture):
    def forward(self, inputs: Tensor) -> Tuple[Tensor, Dict[str, Tensor]]:
        base = self.features(inputs)
        query = self.query_projection(base)
        scores = F.normalize(query, dim=-1) @ F.normalize(
            self.memory_keys, dim=-1
        ).t()
        scores = scores / self.config.temperature
        weights = scores.softmax(dim=-1)
        hidden = F.gelu(torch.einsum("bd,mdr->bmr", base, self.memory_a))
        outputs = torch.einsum("bmr,mrd->bmd", hidden, self.memory_b)
        delta = (outputs * weights[:, :, None]).sum(1)
        return self.classify(base + delta), {
            "route": weights,
            "adapted": base + delta,
        }

    def adapter_flops(self, batch: int, tokens: int) -> int:
        del tokens
        return (
            4
            * batch
            * self.embedding_dim
            * self.config.expert_rank
            * self.config.basis_count
        )