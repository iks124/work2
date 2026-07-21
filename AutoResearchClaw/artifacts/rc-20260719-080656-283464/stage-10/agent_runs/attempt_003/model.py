from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from config import ExperimentConfig


def _init_adapter(a: torch.Tensor, b: torch.Tensor) -> None:
    nn.init.kaiming_uniform_(a, a=math.sqrt(5))
    nn.init.normal_(b, std=0.01)


class ContinualCondition(nn.Module):
    def __init__(
        self,
        config: ExperimentConfig,
        backbone: nn.Module | None,
        condition_name: str,
        embedding_dim: int | None = None,
    ) -> None:
        super().__init__()
        self.config = config
        self.backbone = backbone
        self.condition_name = condition_name
        self.embedding_dim = int(embedding_dim or config.embedding_dim)
        if backbone is not None:
            for parameter in backbone.parameters():
                parameter.requires_grad_(False)
        self.register_buffer(
            "class_prototypes",
            torch.zeros(config.total_classes, self.embedding_dim),
        )
        self.register_buffer(
            "prototype_sums",
            torch.zeros(config.total_classes, self.embedding_dim),
        )
        self.register_buffer(
            "prototype_counts",
            torch.zeros(config.total_classes),
        )
        self.log_temperature = nn.Parameter(torch.zeros(()))

    def encode(self, inputs: torch.Tensor):
        if inputs.ndim == 3:
            tokens = inputs
        elif inputs.ndim == 4:
            if self.backbone is None:
                raise RuntimeError("Image inputs require a verified backbone")
            try:
                output = self.backbone(pixel_values=inputs)
            except TypeError:
                output = self.backbone.forward_features(inputs)
            if hasattr(output, "last_hidden_state"):
                tokens = output.last_hidden_state
            elif isinstance(output, dict):
                tokens = output.get("last_hidden_state", output.get("x"))
            else:
                tokens = output
            if tokens.ndim == 2:
                tokens = tokens[:, None]
        else:
            raise ValueError("Inputs must be [B,T,D] or [B,3,224,224]")
        if tokens.shape[-1] != self.embedding_dim:
            raise ValueError("Backbone embedding dimension mismatch")
        query = F.normalize(tokens[:, 0], dim=-1, eps=1e-8)
        return tokens, query

    @torch.no_grad()
    def update_prototypes(
        self,
        features: torch.Tensor,
        labels: torch.Tensor,
        source: str = "train",
    ) -> None:
        if source != "train":
            raise ValueError("Only training data may update prototypes")
        detached = features.detach()
        for label in labels.unique():
            class_id = int(label)
            selected = detached[labels == label]
            self.prototype_sums[class_id].add_(selected.sum(0))
            self.prototype_counts[class_id].add_(selected.shape[0])
            mean = (
                self.prototype_sums[class_id]
                / self.prototype_counts[class_id]
            )
            self.class_prototypes[class_id].copy_(
                F.normalize(mean, dim=0)
            )

    def classify(
        self,
        features: torch.Tensor,
        seen_classes: int,
    ) -> torch.Tensor:
        query = F.normalize(features, dim=-1)
        prototypes = F.normalize(
            self.class_prototypes[:seen_classes],
            dim=-1,
            eps=1e-8,
        )
        temperature = self.log_temperature.exp().clamp(1e-3, 100)
        return query @ prototypes.T / temperature

    def forward(
        self,
        inputs: torch.Tensor,
        seen_classes: int,
    ) -> dict:
        tokens, query = self.encode(inputs)
        return {
            "logits": self.classify(query, seen_classes),
            "features": query,
            "tokens": tokens,
            "adapter_residual": torch.zeros_like(tokens),
            "regularizers": {},
        }

    def condition_loss(
        self,
        batch,
        output,
        training_state=None,
    ):
        labels = (
            batch["labels"]
            if isinstance(batch, dict)
            else batch[1]
        )
        loss = F.cross_entropy(output["logits"], labels)
        for value in output.get("regularizers", {}).values():
            loss = loss + value
        return loss, {"cross_entropy": loss}

    def stored_parameter_count(self) -> dict:
        components = {
            name: parameter.numel()
            for name, parameter in self.named_parameters()
            if not name.startswith("backbone.")
            and name != "log_temperature"
        }
        return {
            "components": components,
            "total": sum(components.values()),
        }

    def analytical_active_flops(
        self,
        batch_size: int,
        token_count: int,
    ) -> int:
        return (
            2
            * batch_size
            * self.embedding_dim
            * self.config.total_classes
        )


class CalibratedFrozenViTNCM(ContinualCondition):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            "calibrated_frozen_vit_ncm",
            embedding_dim,
        )


class SingleSharedAdapter(ContinualCondition):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            "single_shared_adapter",
            embedding_dim,
        )
        self.adapter_a = nn.Parameter(
            torch.empty(
                self.embedding_dim,
                config.adapter_rank,
            )
        )
        self.adapter_b = nn.Parameter(
            torch.empty(
                config.adapter_rank,
                self.embedding_dim,
            )
        )
        _init_adapter(self.adapter_a, self.adapter_b)

    def forward(self, inputs, seen_classes):
        tokens, _ = self.encode(inputs)
        residual = (
            tokens
            @ self.adapter_a
            @ self.adapter_b
        )
        adapted = tokens + residual
        features = F.normalize(adapted[:, 0], dim=-1)
        return {
            "logits": self.classify(features, seen_classes),
            "features": features,
            "tokens": adapted,
            "adapter_residual": residual,
            "regularizers": {},
        }


class HardTop1AdapterMixture(ContinualCondition):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            "hard_top1_adapter_mixture",
            embedding_dim,
        )
        s = config.slot_count
        d = self.embedding_dim
        r = config.adapter_rank
        self.keys = nn.Parameter(
            torch.randn(s, d) / math.sqrt(d)
        )
        self.adapter_a = nn.Parameter(
            torch.empty(s, d, r)
        )
        self.adapter_b = nn.Parameter(
            torch.empty(s, r, d)
        )
        _init_adapter(self.adapter_a, self.adapter_b)

    def route(self, query):
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        )
        soft = F.softmax(
            scores / self.config.router_temperature,
            dim=-1,
        )
        hard = F.one_hot(
            soft.argmax(-1),
            self.config.slot_count,
        ).float()
        return hard + soft - soft.detach()

    def forward(self, inputs, seen_classes):
        tokens, query = self.encode(inputs)
        route = self.route(query)
        adapter_a = torch.einsum(
            "bs,sdr->bdr",
            route,
            self.adapter_a,
        )
        adapter_b = torch.einsum(
            "bs,srd->brd",
            route,
            self.adapter_b,
        )
        down = torch.einsum(
            "btd,bdr->btr",
            tokens,
            adapter_a,
        )
        residual = torch.einsum(
            "btr,brd->btd",
            down,
            adapter_b,
        )
        features = F.normalize(
            (tokens + residual)[:, 0],
            dim=-1,
        )
        return {
            "logits": self.classify(features, seen_classes),
            "features": features,
            "adapter_residual": residual,
            "route": route,
            "regularizers": {},
        }


class HardTopKAdapterMixture(HardTop1AdapterMixture):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = "hard_topk_adapter_mixture"

    def route(self, query):
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        )
        selected, indices = scores.topk(
            self.config.active_bases,
            dim=-1,
        )
        weights = F.softmax(
            selected / self.config.router_temperature,
            dim=-1,
        )
        return scores.new_zeros(scores.shape).scatter(
            1,
            indices,
            weights,
        )


class DenseSoftmaxAdapterMixture(HardTop1AdapterMixture):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
        **kwargs,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "dense_softmax_adapter_mixture"
        )

    def route(self, query):
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        )
        return F.softmax(
            scores / self.config.router_temperature,
            dim=-1,
        )


class AppendOnlyKeyValueAdapterMemory(
    HardTopKAdapterMixture
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "append_only_key_value_adapter_memory"
        )
        self.register_buffer(
            "occupied",
            torch.zeros(
                config.slot_count,
                dtype=torch.bool,
            ),
        )

    def route(self, query):
        if not self.occupied.any():
            return query.new_zeros(
                query.shape[0],
                self.config.slot_count,
            )
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        )
        scores = scores.masked_fill(
            ~self.occupied[None],
            -torch.inf,
        )
        k = min(
            self.config.active_bases,
            int(self.occupied.sum()),
        )
        values, indices = scores.topk(k, dim=-1)
        weights = F.softmax(values, dim=-1)
        return scores.new_zeros(scores.shape).scatter(
            1,
            indices,
            weights,
        )

    @torch.no_grad()
    def memory_step(self, batch_summary, **kwargs):
        empty = (~self.occupied).nonzero().flatten()
        if empty.numel() == 0:
            return {
                "committed": False,
                "reason": "capacity_full",
            }
        slot = int(empty[0])
        self.keys[slot].copy_(
            F.normalize(
                batch_summary.mean(0),
                dim=0,
            )
        )
        self.occupied[slot] = True
        return {
            "committed": True,
            "slot": slot,
        }


class AllocateThenFreezeAdapterMemory(
    AppendOnlyKeyValueAdapterMemory
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "allocate_then_freeze_adapter_memory"
        )

    @torch.no_grad()
    def memory_step(self, batch_summary, **kwargs):
        result = super().memory_step(batch_summary)
        result["strategy"] = "allocate_then_freeze"
        return result


class BudgetMatchedCaREBilevelRouting(
    HardTopKAdapterMixture
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
        **kwargs,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "budget_matched_care_bilevel_routing"
        )
        self.group_router = nn.Linear(
            self.embedding_dim,
            2,
            bias=False,
        )

    def route(self, query):
        groups = F.softmax(
            self.group_router(query),
            dim=-1,
        )
        group = groups.argmax(-1)
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        )
        mask = torch.arange(
            self.config.slot_count,
            device=query.device,
        )[None]
        mask = (
            mask
            // (self.config.slot_count // 2)
        ) == group[:, None]
        scores = scores.masked_fill(
            ~mask,
            -torch.inf,
        )
        values, indices = scores.topk(
            self.config.active_bases,
            dim=-1,
        )
        weights = F.softmax(values, dim=-1)
        return scores.new_zeros(scores.shape).scatter(
            1,
            indices,
            weights,
        )


class SignedTop2BasisMemory(ContinualCondition):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
        load_balance_weight=0.01,
    ):
        super().__init__(
            config,
            backbone,
            "signed_top2_basis_memory",
            embedding_dim,
        )
        s = config.basis_count
        d = self.embedding_dim
        r = config.basis_rank
        self.keys = nn.Parameter(
            torch.randn(s, d) / math.sqrt(d)
        )
        self.basis_a = nn.Parameter(
            torch.empty(s, d, r)
        )
        self.basis_b = nn.Parameter(
            torch.empty(s, r, d)
        )
        _init_adapter(self.basis_a, self.basis_b)
        self.load_balance_weight = load_balance_weight
        self.register_buffer(
            "route_ema",
            torch.full(
                (config.total_classes, s),
                1 / s,
            ),
        )

    def route(self, query):
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        )
        _, indices = scores.abs().topk(
            2,
            dim=-1,
        )
        selected = scores.gather(1, indices)
        coefficients = selected / (
            selected.abs()
            .sum(1, keepdim=True)
            .clamp_min(1e-8)
        )
        distribution = F.softmax(
            scores.abs()
            / self.config.router_temperature,
            dim=-1,
        )
        return indices, coefficients, distribution

    def forward(self, inputs, seen_classes):
        tokens, query = self.encode(inputs)
        indices, coefficients, distribution = (
            self.route(query)
        )
        weights = coefficients[:, :, None, None]
        adapter_a = (
            self.basis_a[indices] * weights
        ).sum(1)
        adapter_b = (
            self.basis_b[indices] * weights
        ).sum(1)
        down = torch.einsum(
            "btd,bdr->btr",
            tokens,
            adapter_a,
        )
        residual = torch.einsum(
            "btr,brd->btd",
            down,
            adapter_b,
        )
        features = F.normalize(
            (tokens + residual)[:, 0],
            dim=-1,
        )
        return {
            "logits": self.classify(
                features,
                seen_classes,
            ),
            "features": features,
            "adapter_residual": residual,
            "route": distribution,
            "route_indices": indices,
            "route_coefficients": coefficients,
            "regularizers": {},
        }

    def condition_loss(
        self,
        batch,
        output,
        training_state=None,
    ):
        labels = batch["labels"]
        cross_entropy = F.cross_entropy(
            output["logits"],
            labels,
        )
        current = output["route"].clamp_min(1e-8)
        target = (
            self.route_ema[labels]
            .detach()
            .clamp_min(1e-8)
        )
        midpoint = (current + target) / 2
        js = 0.5 * (
            (
                current
                * (
                    current.log()
                    - midpoint.log()
                )
            ).sum(-1)
            + (
                target
                * (
                    target.log()
                    - midpoint.log()
                )
            ).sum(-1)
        ).mean()
        balance = (
            current.mean(0)
            - 1 / current.shape[1]
        ).square().sum()
        loss = (
            cross_entropy
            + self.config.hysteresis_weight * js
            + self.load_balance_weight * balance
        )
        return loss, {
            "cross_entropy": cross_entropy,
            "hysteresis": js,
        }

    @torch.no_grad()
    def update_route_ema(self, labels, route):
        for label in labels.unique():
            class_id = int(label)
            value = (
                route[labels == label]
                .detach()
                .mean(0)
            )
            self.route_ema[class_id].mul_(
                self.config.route_ema_decay
            )
            self.route_ema[class_id].add_(
                value
                * (
                    1
                    - self.config.route_ema_decay
                )
            )
            self.route_ema[class_id].div_(
                self.route_ema[class_id].sum()
            )
        return {"updated": True}


class NoRouteHysteresis(SignedTop2BasisMemory):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
        **kwargs,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
            **kwargs,
        )
        self.condition_name = "no_route_hysteresis"

    def condition_loss(
        self,
        batch,
        output,
        training_state=None,
    ):
        cross_entropy = F.cross_entropy(
            output["logits"],
            batch["labels"],
        )
        balance = (
            output["route"].mean(0)
            - 1 / self.config.basis_count
        ).square().sum()
        return (
            cross_entropy
            + self.load_balance_weight * balance,
            {"cross_entropy": cross_entropy},
        )

    @torch.no_grad()
    def update_route_ema(self, labels, route):
        return {
            "updated": False,
            "reason": "disabled_by_strategy",
        }


class HardTop2UnsignedBasisRouting(
    SignedTop2BasisMemory
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
        **kwargs,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
            **kwargs,
        )
        self.condition_name = (
            "hard_top2_unsigned_basis_routing"
        )

    def route(self, query):
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        ).abs()
        selected, indices = scores.topk(
            2,
            dim=-1,
        )
        coefficients = selected / (
            selected.sum(1, keepdim=True)
            .clamp_min(1e-8)
        )
        return (
            indices,
            coefficients,
            F.softmax(scores, dim=-1),
        )


class BoundedDamageAwareAllocateOrWrite(
    HardTopKAdapterMixture
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "bounded_damage_aware_allocate_or_write"
        )
        parameter_size = (
            2
            * self.embedding_dim
            * config.adapter_rank
        )
        self.write_encoder = nn.Linear(
            self.embedding_dim,
            parameter_size,
        )
        self.erase_encoder = nn.Linear(
            self.embedding_dim,
            config.slot_count,
        )
        self.register_buffer(
            "occupied",
            torch.zeros(
                config.slot_count,
                dtype=torch.bool,
            ),
        )
        self.register_buffer(
            "allocation_task",
            torch.full(
                (config.slot_count,),
                -1,
                dtype=torch.long,
            ),
        )
        self.register_buffer(
            "allocation_values",
            torch.zeros(
                config.slot_count,
                parameter_size,
            ),
        )
        self.register_buffer(
            "cumulative_drift",
            torch.zeros(config.slot_count),
        )
        self.register_buffer(
            "protected_sketch",
            torch.randn(
                config.gradient_sketch_rank,
                parameter_size,
            ),
        )

    def route(self, query):
        if not self.occupied.any():
            return query.new_zeros(
                query.shape[0],
                self.config.slot_count,
            )
        scores = (
            query
            @ F.normalize(self.keys, dim=-1).T
        )
        scores = scores.masked_fill(
            ~self.occupied[None],
            -torch.inf,
        )
        k = min(2, int(self.occupied.sum()))
        values, indices = scores.topk(k, dim=-1)
        return scores.new_zeros(scores.shape).scatter(
            1,
            indices,
            F.softmax(values, dim=-1),
        )

    def forward(self, inputs, seen_classes):
        output = super().forward(
            inputs,
            seen_classes,
        )
        query = output["features"]
        candidate = self.write_encoder(
            query.mean(0)
        )
        output["candidate_write"] = candidate
        output["erase_logits"] = (
            self.erase_encoder(query.mean(0))
        )
        output["selected_damage"] = (
            candidate
            @ self.protected_sketch.detach().T
        ).square().mean().sqrt()
        return output

    def condition_loss(
        self,
        batch,
        output,
        training_state=None,
    ):
        cross_entropy = F.cross_entropy(
            output["logits"],
            batch["labels"],
        )
        hinge = F.relu(
            output["selected_damage"]
            - self.config.damage_threshold
        )
        write = (
            output["candidate_write"]
            .square()
            .sum()
        )
        loss = (
            cross_entropy
            + self.config.damage_weight * hinge
            + self.config.write_weight * write
        )
        return loss, {
            "cross_entropy": cross_entropy,
            "damage": hinge,
            "write": write,
        }

    def bounded_erase_add(
        self,
        slot,
        erase_raw,
        add_raw,
    ):
        current = torch.cat(
            [
                self.adapter_a[slot].flatten(),
                self.adapter_b[slot].flatten(),
            ]
        )
        erase = (
            self.config.erase_gate_max
            * torch.sigmoid(erase_raw)
        )
        add_scale = min(
            1.0,
            self.config.add_norm_max
            / max(float(add_raw.norm()), 1e-12),
        )
        add = add_raw * add_scale
        proposed = (1 - erase) * current + add
        origin = self.allocation_values[slot]
        delta = proposed - origin
        drift_scale = min(
            1.0,
            self.config.cumulative_slot_drift_max
            / max(float(delta.norm()), 1e-12),
        )
        delta = delta * drift_scale
        proposed = origin + delta
        return proposed, {
            "erase": erase,
            "add_norm": add.norm(),
            "drift": delta.norm(),
        }

    @torch.no_grad()
    def memory_step(
        self,
        batch_summary,
        candidate_write,
        erase_logits,
        current_task=0,
        force_reject=False,
        **kwargs,
    ):
        empty = (
            ~self.occupied
        ).nonzero().flatten()
        candidate = candidate_write.detach()

        if empty.numel():
            slot = int(empty[0])
            if (
                force_reject
                or not torch.isfinite(candidate).all()
            ):
                return {
                    "committed": False,
                    "reason": "rejected",
                }
            self.keys[slot].copy_(
                F.normalize(
                    batch_summary.mean(0),
                    dim=0,
                )
            )
            self.allocation_values[slot].copy_(
                candidate
            )
            a_size = self.adapter_a[slot].numel()
            self.adapter_a[slot].copy_(
                candidate[:a_size].reshape_as(
                    self.adapter_a[slot]
                )
            )
            self.adapter_b[slot].copy_(
                candidate[a_size:].reshape_as(
                    self.adapter_b[slot]
                )
            )
            self.occupied[slot] = True
            self.allocation_task[slot] = current_task
            return {
                "committed": True,
                "slot": slot,
                "reason": "allocate",
            }

        damage = torch.stack(
            [
                (
                    candidate
                    @ self.protected_sketch.detach().T
                ).square().mean().sqrt()
                for _ in range(
                    self.config.slot_count
                )
            ]
        )
        slot = int(damage.argmin())
        before = (
            self.adapter_a[slot].clone(),
            self.adapter_b[slot].clone(),
            self.cumulative_drift[slot].clone(),
        )
        try:
            proposed, diagnostic = (
                self.bounded_erase_add(
                    slot,
                    erase_logits[slot],
                    candidate,
                )
            )
            if force_reject:
                raise FloatingPointError
            a_size = self.adapter_a[slot].numel()
            self.adapter_a[slot].copy_(
                proposed[:a_size].reshape_as(
                    self.adapter_a[slot]
                )
            )
            self.adapter_b[slot].copy_(
                proposed[a_size:].reshape_as(
                    self.adapter_b[slot]
                )
            )
            self.cumulative_drift[slot].copy_(
                diagnostic["drift"]
            )
            return {
                "committed": True,
                "slot": slot,
                **diagnostic,
            }
        except FloatingPointError:
            self.adapter_a[slot].copy_(before[0])
            self.adapter_b[slot].copy_(before[1])
            self.cumulative_drift[slot].copy_(
                before[2]
            )
            return {
                "committed": False,
                "slot": slot,
                "reason": "rejected",
            }


class NoveltyGatedAllocateOrWrite(
    BoundedDamageAwareAllocateOrWrite
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "novelty_gated_allocate_or_write"
        )


class NearestSlotBoundedWrite(
    BoundedDamageAwareAllocateOrWrite
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "nearest_slot_bounded_write"
        )


class FrozenOldSlots(
    BoundedDamageAwareAllocateOrWrite
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = "frozen_old_slots"


class NoWriteAllocateThenFreeze(
    BoundedDamageAwareAllocateOrWrite
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "no_write_allocate_then_freeze"
        )


class FlatRouterForFrozenExperts(
    HardTopKAdapterMixture
):
    def __init__(
        self,
        config,
        backbone=None,
        embedding_dim=None,
        **kwargs,
    ):
        super().__init__(
            config,
            backbone,
            embedding_dim,
        )
        self.condition_name = (
            "flat_router_for_frozen_experts"
        )


class OfficialExternalMethodWrapper(
    ContinualCondition
):
    def __init__(
        self,
        config,
        backbone,
        method_name,
        official_model,
        provenance_manifest,
        embedding_dim=None,
        **kwargs,
    ):
        super().__init__(
            config,
            backbone,
            method_name,
            embedding_dim,
        )
        if official_model is None:
            raise ValueError(
                "A verified official model is required"
            )
        self.official_model = official_model
        self.provenance_manifest = (
            provenance_manifest
        )

    def forward(self, inputs, seen_classes):
        output = self.official_model(inputs)
        logits = (
            output["logits"]
            if isinstance(output, dict)
            else output
        )
        logits = logits[:, :seen_classes]
        if not torch.isfinite(logits).all():
            raise FloatingPointError(
                "Official model produced nonfinite logits"
            )
        return {
            "logits": logits,
            "features": None,
            "adapter_residual": torch.zeros(
                inputs.shape[0],
                1,
                self.embedding_dim,
                device=inputs.device,
            ),
            "regularizers": {},
        }