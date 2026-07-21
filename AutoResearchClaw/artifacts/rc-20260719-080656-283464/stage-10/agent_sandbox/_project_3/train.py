from __future__ import annotations

import math
import time

import numpy as np
import torch
import torch.nn.functional as F

from config import ExperimentConfig
from data import SyntheticTokenFixture
from model import (
    BoundedDamageAwareAllocateOrWrite,
    SignedTop2BasisMemory,
)


class ContinualTrainer:
    def __init__(
        self,
        config: ExperimentConfig,
        device="cpu",
        harness=None,
        max_optimization_steps=5000,
    ) -> None:
        self.config = config
        self.device = torch.device(device)
        self.harness = harness
        self.max_optimization_steps = (
            max_optimization_steps
        )
        self.steps = 0

    def train_checkpoint(
        self,
        model,
        loader,
        optimizer,
        checkpoint,
        deadline,
    ) -> dict:
        model.train()
        seen_classes = (
            checkpoint
            * self.config.classes_per_task
        )
        losses = []

        for inputs, labels in loader:
            if (
                time.monotonic() >= deadline
                or self.steps
                >= self.max_optimization_steps
            ):
                break
            if (
                self.harness is not None
                and self.harness.should_stop()
            ):
                break

            inputs = inputs.to(self.device)
            labels = labels.to(self.device)
            optimizer.zero_grad(set_to_none=True)
            output = model(inputs, seen_classes)
            loss, _ = model.condition_loss(
                {"labels": labels},
                output,
                {},
            )
            value = float(loss.detach())
            if (
                not math.isfinite(value)
                or value > 100
            ):
                print(
                    "FAIL: NaN/divergence detected",
                    flush=True,
                )
                raise FloatingPointError(
                    "Divergent loss"
                )

            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                self.config.gradient_clip_norm,
            )
            optimizer.step()
            self.steps += 1
            losses.append(value)

            model.update_prototypes(
                output["features"],
                labels,
            )
            if isinstance(
                model,
                SignedTop2BasisMemory,
            ):
                model.update_route_ema(
                    labels,
                    output["route"],
                )
            elif isinstance(
                model,
                BoundedDamageAwareAllocateOrWrite,
            ):
                model.memory_step(
                    output["features"].detach(),
                    output[
                        "candidate_write"
                    ].detach(),
                    output[
                        "erase_logits"
                    ].detach(),
                    current_task=checkpoint - 1,
                )

        return {
            "processed_steps": len(losses),
            "mean_loss": (
                float(np.mean(losses))
                if losses
                else None
            ),
        }

    @torch.no_grad()
    def evaluate_checkpoint(
        self,
        model,
        loader,
        checkpoint,
    ) -> dict:
        model.eval()
        seen_classes = (
            checkpoint
            * self.config.classes_per_task
        )
        total = 0
        correct = 0

        for inputs, labels in loader:
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)
            logits = model(
                inputs,
                seen_classes,
            )["logits"]
            correct += int(
                (
                    logits.argmax(-1)
                    == labels
                ).sum()
            )
            total += labels.numel()

        return {
            "top1_accuracy": (
                100 * correct / max(total, 1)
            )
        }

    def run_smoke(
        self,
        model,
        seed=0,
    ) -> dict:
        fixture = SyntheticTokenFixture()
        fixture.assert_permitted_use(
            [
                "output_shape_matches_num_classes",
                "all_forward_values_finite",
                "stored_parameter_count",
                "analytical_active_flops",
            ]
        )
        batch = fixture.make_batch(seed)
        model.to(self.device)

        with torch.no_grad():
            model.class_prototypes[:10].copy_(
                batch["class_prototypes"].to(
                    self.device
                )
            )
            model.prototype_counts[:10].fill_(1)

        tokens = batch["tokens"].to(self.device)
        labels = batch["labels"].to(self.device)
        output = model(tokens, 10)

        if output["logits"].shape != (4, 10):
            raise AssertionError(
                "Invalid logits shape"
            )
        if output["adapter_residual"].shape != (
            4,
            17,
            64,
        ):
            raise AssertionError(
                "Invalid residual shape"
            )

        loss, _ = model.condition_loss(
            {"labels": labels},
            output,
            {},
        )
        if not torch.isfinite(loss):
            raise FloatingPointError(
                "Nonfinite smoke loss"
            )
        loss.backward()

        gradients = [
            parameter.grad
            for parameter in model.parameters()
            if parameter.grad is not None
        ]
        if (
            not gradients
            or not all(
                torch.isfinite(gradient).all()
                for gradient in gradients
            )
        ):
            raise AssertionError(
                "Invalid gradients"
            )
        if not any(
            float(gradient.norm()) > 0
            for gradient in gradients
        ):
            raise AssertionError(
                "No nonzero gradient"
            )

        if isinstance(
            model,
            SignedTop2BasisMemory,
        ):
            if output[
                "route_indices"
            ].shape != (4, 2):
                raise AssertionError(
                    "Top-2 routing failed"
                )
            norms = (
                output["route_coefficients"]
                .abs()
                .sum(-1)
            )
            if not torch.allclose(
                norms,
                torch.ones_like(norms),
                atol=1e-5,
            ):
                raise AssertionError(
                    "Signed coefficients are not normalized"
                )

        if isinstance(
            model,
            BoundedDamageAwareAllocateOrWrite,
        ):
            candidate = output[
                "candidate_write"
            ].detach()
            erase = output[
                "erase_logits"
            ].detach()

            for task in range(
                model.config.slot_count + 2
            ):
                model.memory_step(
                    output["features"].detach(),
                    candidate,
                    erase,
                    current_task=task,
                )

            if int(model.occupied.sum()) > (
                model.config.slot_count
            ):
                raise AssertionError(
                    "Capacity exceeded"
                )

            slot = int(
                model.occupied.nonzero()[0]
            )
            _, diagnostic = (
                model.bounded_erase_add(
                    slot,
                    erase[slot],
                    candidate,
                )
            )
            if float(diagnostic["erase"]) > (
                model.config.erase_gate_max
                + 1e-7
            ):
                raise AssertionError(
                    "Erase bound exceeded"
                )
            if float(
                diagnostic["add_norm"]
            ) > (
                model.config.add_norm_max
                + 1e-7
            ):
                raise AssertionError(
                    "Add bound exceeded"
                )

            before = (
                model.adapter_a.detach().clone()
            )
            result = model.memory_step(
                output["features"].detach(),
                candidate,
                erase,
                force_reject=True,
            )
            if (
                result["committed"]
                or not torch.equal(
                    before,
                    model.adapter_a,
                )
            ):
                raise AssertionError(
                    "Transactional rollback failed"
                )

        return {
            "status": "pass",
            "stored_parameter_count": (
                model.stored_parameter_count()
            ),
            "analytical_active_flops": (
                model.analytical_active_flops(
                    4,
                    17,
                )
            ),
        }

    def verify_budget_match(
        self,
        left,
        right,
        batch_size=4,
        token_count=17,
    ):
        left_parameters = (
            left.stored_parameter_count()["total"]
        )
        right_parameters = (
            right.stored_parameter_count()["total"]
        )
        parameter_error = (
            200
            * abs(
                left_parameters
                - right_parameters
            )
            / max(
                left_parameters
                + right_parameters,
                1,
            )
        )
        left_flops = (
            left.analytical_active_flops(
                batch_size,
                token_count,
            )
        )
        right_flops = (
            right.analytical_active_flops(
                batch_size,
                token_count,
            )
        )
        flop_error = (
            200
            * abs(left_flops - right_flops)
            / max(
                left_flops + right_flops,
                1,
            )
        )
        return {
            "parameter_error_percent": (
                parameter_error
            ),
            "active_flop_error_percent": (
                flop_error
            ),
        }


class MetricTracker:
    def __init__(
        self,
        config: ExperimentConfig,
    ) -> None:
        self.config = config
        self.records: dict[
            int,
            dict[int, dict],
        ] = {}

    def update_checkpoint(
        self,
        checkpoint,
        seed,
        metrics,
        **kwargs,
    ):
        self.records.setdefault(
            seed,
            {},
        )[checkpoint] = {
            key: (
                value.detach().cpu().clone()
                if isinstance(
                    value,
                    torch.Tensor,
                )
                else value
            )
            for key, value in metrics.items()
        }

    def finalize_seed(self, seed):
        records = self.records[seed]
        accuracies = np.asarray(
            [
                records[index][
                    "top1_accuracy"
                ]
                for index in range(1, 11)
            ],
            dtype=np.float64,
        )
        return {
            "negative_average_incremental_accuracy": (
                -float(accuracies.mean())
            ),
            "final_top1_accuracy": float(
                accuracies[-1]
            ),
        }

    def paired_summary(
        self,
        left_results,
        right_results,
        metric_name,
    ):
        seeds = sorted(
            set(left_results)
            & set(right_results)
        )
        differences = np.asarray(
            [
                left_results[seed][metric_name]
                - right_results[seed][
                    metric_name
                ]
                for seed in seeds
            ],
            dtype=np.float64,
        )
        return {
            "paired_seeds": seeds,
            "difference_mean": float(
                differences.mean()
            ),
            "difference_std": float(
                differences.std(ddof=1)
            ),
        }


class RouteAndDriftDiagnostics:
    def route_switch_rate(
        self,
        previous_routes,
        current_routes,
    ):
        shared = (
            set(previous_routes)
            & set(current_routes)
        )
        if not shared:
            return 0.0
        changed = sum(
            not torch.equal(
                previous_routes[index]
                .detach()
                .cpu(),
                current_routes[index]
                .detach()
                .cpu(),
            )
            for index in shared
        )
        return changed / len(shared)

    def old_prototype_cosine_drift(
        self,
        previous,
        current,
    ):
        previous = F.normalize(
            previous.detach(),
            dim=-1,
        )
        current = F.normalize(
            current.detach(),
            dim=-1,
        )
        return float(
            (
                1
                - (
                    previous
                    * current
                ).sum(-1)
            ).mean()
        )

    def expert_output_drift(
        self,
        previous,
        current,
    ):
        previous = previous.detach()
        current = current.detach()
        return float(
            (current - previous).norm()
            / previous.norm().clamp_min(1e-8)
        )

    def label_free_routing_gap(
        self,
        train_features,
        train_labels,
        eval_features,
        eval_labels,
        learned,
    ):
        classes = train_labels.unique(
            sorted=True
        )
        prototypes = torch.stack(
            [
                F.normalize(
                    train_features[
                        train_labels == label
                    ].mean(0),
                    dim=0,
                )
                for label in classes
            ]
        )
        predictions = classes[
            (
                F.normalize(
                    eval_features,
                    dim=-1,
                )
                @ prototypes.T
            ).argmax(-1)
        ]
        return {
            "label_free_routing_gap": float(
                (
                    predictions
                    == eval_labels
                ).float().mean()
                - (
                    learned
                    == eval_labels
                ).float().mean()
            )
        }

    def routing_causality_decomposition(
        self,
        normal,
        frozen_router,
        frozen_memory,
        frozen_both,
    ):
        stable = (
            normal["route_switch_rate"]
            < frozen_memory[
                "route_switch_rate"
            ]
        )
        accurate = (
            normal["top1_accuracy"]
            > frozen_memory[
                "top1_accuracy"
            ]
        )
        return {
            "routing_stability_causal_support": bool(
                stable and accurate
            ),
            "router_effect": (
                normal["top1_accuracy"]
                - frozen_router[
                    "top1_accuracy"
                ]
            ),
            "memory_effect": (
                normal["top1_accuracy"]
                - frozen_memory[
                    "top1_accuracy"
                ]
            ),
            "joint_effect": (
                normal["top1_accuracy"]
                - frozen_both[
                    "top1_accuracy"
                ]
            ),
        }