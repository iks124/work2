import random
import time
from typing import Dict, Type

import numpy as np
import torch
from experiment_harness import ExperimentHarness

from data import (
    SplitCIFAR100Features,
    deterministic_batches,
    deterministic_smoke_fixture,
)
from evaluate import accuracy, atomic_write, primary_metric, smoke_test
from experiment_config import ExperimentConfig
from methods import (
    DenseSoftmaxAdapterMixture,
    HardTop2AdapterMixture,
    ReadOnlyAdapterModel,
    SignedTop2BasisMemory,
)

CONFIG = ExperimentConfig()
CONDITIONS: Dict[str, Type[ReadOnlyAdapterModel]] = {
    "signed_top2": SignedTop2BasisMemory,
    "hard_top2": HardTop2AdapterMixture,
    "dense_softmax": DenseSoftmaxAdapterMixture,
}

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)

def train_condition(
    model: ReadOnlyAdapterModel,
    dataset: SplitCIFAR100Features,
    order_index: int,
    seed: int,
    harness: ExperimentHarness,
    deadline: float,
) -> Dict[str, object]:
    optimizer = torch.optim.Adam(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=CONFIG.learning_rate,
    )
    checkpoint_accuracies = []

    for task in range(CONFIG.num_tasks):
        train_x, train_y, test_x, test_y = dataset.task_arrays(
            order_index,
            task,
            CONFIG.classes_per_task,
        )
        for epoch in range(CONFIG.epochs_per_task):
            for features, labels in deterministic_batches(
                train_x,
                train_y,
                CONFIG.batch_size,
                seed,
                task * CONFIG.epochs_per_task + epoch,
            ):
                if harness.should_stop() or time.monotonic() >= deadline:
                    raise TimeoutError("80% time guard reached")
                optimizer.zero_grad(set_to_none=True)
                logits, auxiliary = model(features)
                loss = model.loss(logits, labels, auxiliary)
                loss_value = float(loss.detach())
                if not np.isfinite(loss_value) or loss_value > 100:
                    print("FAIL: NaN/divergence detected", flush=True)
                    raise FloatingPointError("Invalid training loss")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    CONFIG.gradient_clip_norm,
                )
                before = model.memory_digest()
                optimizer.step()
                if before != model.memory_digest():
                    raise AssertionError("Read-only memory was modified")
                if isinstance(model, SignedTop2BasisMemory):
                    model.update_route_ema(auxiliary["route"], labels)

        seen = dataset.orders[
            order_index,
            : (task + 1) * CONFIG.classes_per_task,
        ]
        value = accuracy(model, test_x, test_y, seen)
        checkpoint_accuracies.append(value)
        print(
            f"condition={type(model).__name__} seed={seed} "
            f"task={task} accuracy={value:.6f}",
            flush=True,
        )

    metric = primary_metric(checkpoint_accuracies)
    return {
        "primary_metric": metric,
        "checkpoint_accuracies": checkpoint_accuracies,
    }

def main() -> None:
    harness = ExperimentHarness(time_budget=CONFIG.time_limit_seconds)
    started = time.monotonic()
    deadline = started + 0.8 * CONFIG.time_limit_seconds
    results: Dict[str, Dict[str, object]] = {}
    failures = []

    smoke_tokens, smoke_labels = deterministic_smoke_fixture()
    pilot_start = time.perf_counter()
    pilot_model = SignedTop2BasisMemory(CONFIG, 64)
    pilot = smoke_test(
        pilot_model,
        smoke_tokens,
        smoke_labels,
        CONFIG,
    )
    pilot_seconds = max(time.perf_counter() - pilot_start, 1e-6)
    estimate = pilot_seconds * len(CONDITIONS) * len(CONFIG.seeds)
    print(f"TIME_ESTIMATE: {estimate:.3f}s", flush=True)

    smoke_counts = {}
    for name, model_class in CONDITIONS.items():
        model = model_class(CONFIG, 64)
        smoke_counts[name] = smoke_test(
            model,
            smoke_tokens.detach().clone().requires_grad_(True),
            smoke_labels,
            CONFIG,
        )
        print(f"condition={name} smoke=PASS", flush=True)

    sparse_reference = smoke_counts["signed_top2"]
    hard_reference = smoke_counts["hard_top2"]
    stored_error = abs(
        hard_reference["stored_parameters"]
        - sparse_reference["stored_parameters"]
    ) / sparse_reference["stored_parameters"]
    compute_error = abs(
        hard_reference["active_flops"]
        - sparse_reference["active_flops"]
    ) / sparse_reference["active_flops"]
    if stored_error > 0.02 or compute_error > 0.05:
        raise AssertionError("Signed and Hard Top-2 matching tolerance failed")
    print(
        "DENSE_COMPUTE_NOTE: dense_softmax reports full dense FLOPs and is "
        "not described as latency- or active-compute-matched",
        flush=True,
    )

    try:
        dataset = SplitCIFAR100Features(CONFIG)
        for condition_name, model_class in CONDITIONS.items():
            results[condition_name] = {}
            values = []
            for order_index, seed in enumerate(CONFIG.seeds):
                if harness.should_stop() or time.monotonic() >= deadline:
                    raise TimeoutError("80% time guard reached")
                set_seed(seed)
                model = model_class(CONFIG, dataset.embedding_dim)
                run = train_condition(
                    model,
                    dataset,
                    order_index,
                    seed,
                    harness,
                    deadline,
                )
                results[condition_name][f"seed_{seed}"] = run
                values.append(run["primary_metric"])
                harness.report_metric(
                    f"{condition_name}_primary_metric",
                    run["primary_metric"],
                )
                print(
                    f"condition={condition_name} seed={seed} "
                    f"primary_metric={run['primary_metric']:.6f}",
                    flush=True,
                )
            if values:
                print(
                    f"condition={condition_name} primary_metric_mean="
                    f"{np.mean(values):.6f} primary_metric_std="
                    f"{np.std(values, ddof=1):.6f}",
                    flush=True,
                )
    except Exception as exc:
        failures.append({"type": type(exc).__name__, "message": str(exc)})
        print(f"FORMAL_STAGE_STOPPED: {exc}", flush=True)
    finally:
        atomic_write(
            CONFIG.output_path,
            {
                "protocol": {
                    "care_commit": (
                        dataset.care_commit
                        if "dataset" in locals()
                        else None
                    ),
                    "checkpoint_sha256": (
                        dataset.checkpoint_sha256
                        if "dataset" in locals()
                        else None
                    ),
                    "task_id_at_inference": False,
                    "memory_writable": False,
                    "conditions": list(CONDITIONS),
                },
                "smoke": smoke_counts,
                "conditions": results,
                "failures": failures,
            },
        )
        harness.finalize()

if __name__ == "__main__":
    main()