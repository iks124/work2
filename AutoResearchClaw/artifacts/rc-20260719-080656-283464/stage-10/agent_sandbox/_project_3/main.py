import random
import time
from typing import Dict, Type

import numpy as np
import torch
from experiment_harness import ExperimentHarness

from config import ExperimentConfig
from data import SplitCIFAR100DataModule
from evaluate import run_smoke_tests, write_results
from methods import (
    ConditionBase,
    DenseSoftmaxAdapterMixture,
    HardTop2AdapterMixture,
    SignedTop2BasisMemory,
)


HYPERPARAMETERS = {
    "learning_rate": 0.001,
    "batch_size": 4,
    "token_count": 17,
    "embedding_dim": 64,
    "basis_count": 8,
    "active_bases": 2,
    "basis_rank": 2,
    "adapter_rank": 4,
    "router_temperature": 0.2,
    "time_limit_seconds": 300,
}
SEEDS = [0, 1, 2]

CONDITIONS: Dict[str, Type[ConditionBase]] = {
    "signed_top2_basis_memory": SignedTop2BasisMemory,
    "hard_top2_adapter_mixture": HardTop2AdapterMixture,
    "dense_softmax_adapter_mixture": DenseSoftmaxAdapterMixture,
}


def set_all_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_condition(
    condition_name: str,
    config: ExperimentConfig,
) -> ConditionBase:
    prohibited = ("ewc", "replay", "packnet", "lora", "cifar10c")
    if any(term in condition_name.lower() for term in prohibited):
        raise ValueError(f"Prohibited condition: {condition_name}")
    try:
        condition_class = CONDITIONS[condition_name]
    except KeyError as exc:
        raise KeyError(f"Unknown condition: {condition_name}") from exc
    return condition_class(config)


def validate_formal_prerequisites() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("Formal execution requires a detected CUDA GPU")
    raise RuntimeError(
        "Formal execution remains blocked until real CIFAR-100, saved class "
        "orders, and checksum-verified pretrained ViT weights are supplied"
    )


def main() -> None:
    config = ExperimentConfig(
        batch_size=int(HYPERPARAMETERS["batch_size"]),
        token_count=int(HYPERPARAMETERS["token_count"]),
        embedding_dim=int(HYPERPARAMETERS["embedding_dim"]),
        basis_count=int(HYPERPARAMETERS["basis_count"]),
        active_bases=int(HYPERPARAMETERS["active_bases"]),
        basis_rank=int(HYPERPARAMETERS["basis_rank"]),
        adapter_rank=int(HYPERPARAMETERS["adapter_rank"]),
        router_temperature=float(HYPERPARAMETERS["router_temperature"]),
        time_limit_seconds=int(HYPERPARAMETERS["time_limit_seconds"]),
    )
    harness = ExperimentHarness(time_budget=config.time_limit_seconds)
    data = SplitCIFAR100DataModule(config)
    condition_names = config.condition_names()

    print(
        "METRIC_DEF: smoke stage reports pass/fail, parameter count, and "
        "analytical FLOPs only",
        flush=True,
    )
    print("REGISTERED_CONDITIONS: " + ",".join(condition_names), flush=True)
    print("SEED_WARNING: only 3 seeds used due to time budget", flush=True)

    pilot_start = time.perf_counter()
    set_all_seeds(SEEDS[0])
    pilot_model = build_condition(condition_names[0], config)
    run_smoke_tests(pilot_model, data.smoke_fixture(SEEDS[0]), config)
    pilot_seconds = max(time.perf_counter() - pilot_start, 1e-6)
    estimate = pilot_seconds * len(condition_names) * len(SEEDS)
    print(f"TIME_ESTIMATE: {estimate:.3f}s", flush=True)

    started = time.monotonic()
    results: Dict[str, Dict[str, object]] = {}
    try:
        for condition_name in condition_names:
            results[condition_name] = {}
            parameter_values = []
            flop_values = []

            for seed in SEEDS:
                if (
                    harness.should_stop()
                    or time.monotonic() - started
                    >= 0.8 * config.time_limit_seconds
                ):
                    print("TIME_GUARD: saving partial results", flush=True)
                    break

                set_all_seeds(seed)
                model = build_condition(condition_name, config)
                result = run_smoke_tests(
                    model,
                    data.smoke_fixture(seed),
                    config,
                )
                results[condition_name][f"seed_{seed}"] = result
                parameter_values.append(result["stored_parameter_count"])
                flop_values.append(result["analytical_active_flops"])

                print(
                    f"condition={condition_name} seed={seed} "
                    f"passed: {result['passed']}",
                    flush=True,
                )
                harness.report_metric(
                    "stored_parameter_count",
                    result["stored_parameter_count"],
                )
                harness.report_metric(
                    "analytical_active_flops",
                    result["analytical_active_flops"],
                )

            if parameter_values:
                print(
                    f"condition={condition_name} stored_parameter_count_mean: "
                    f"{np.mean(parameter_values):.4f} "
                    f"stored_parameter_count_std: "
                    f"{np.std(parameter_values):.4f}",
                    flush=True,
                )
                print(
                    f"condition={condition_name} analytical_active_flops_mean: "
                    f"{np.mean(flop_values):.4f} "
                    f"analytical_active_flops_std: "
                    f"{np.std(flop_values):.4f}",
                    flush=True,
                )
    finally:
        write_results(
            config.output_path,
            {
                "hyperparameters": HYPERPARAMETERS,
                "conditions": results,
            },
        )
        harness.finalize()


if __name__ == "__main__":
    main()