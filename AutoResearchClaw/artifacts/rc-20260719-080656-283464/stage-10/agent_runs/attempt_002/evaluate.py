import json
import math
import os
import tempfile
from pathlib import Path
from typing import Dict

import torch

from config import ExperimentConfig
from methods import ConditionBase, SignedTop2BasisMemory


def run_smoke_tests(
    model: ConditionBase,
    fixture: Dict[str, torch.Tensor],
    config: ExperimentConfig,
) -> Dict[str, object]:
    model.zero_grad(set_to_none=True)
    logits, auxiliary = model(fixture["tokens"])
    if logits.shape != (config.batch_size, config.num_classes):
        raise AssertionError(f"Unexpected logits shape: {tuple(logits.shape)}")
    if not torch.isfinite(logits).all():
        raise AssertionError("Nonfinite forward values")

    loss = model.compute_loss(logits, fixture["labels"], auxiliary)
    if loss.ndim or not torch.isfinite(loss) or float(loss.detach()) > 100:
        raise AssertionError("Nonfinite or divergent loss")
    loss.backward()

    gradients = [
        parameter.grad
        for parameter in model.parameters()
        if parameter.requires_grad and parameter.grad is not None
    ]
    if not gradients or not all(torch.isfinite(gradient).all() for gradient in gradients):
        raise AssertionError("Missing or nonfinite gradients")
    if not any(float(gradient.abs().sum()) > 0 for gradient in gradients):
        raise AssertionError("No nonzero model gradient")

    route = auxiliary["route"]
    if isinstance(model, SignedTop2BasisMemory):
        if not torch.all((route != 0).sum(1) == 2):
            raise AssertionError("Signed routing did not activate exactly two bases")
        if not torch.allclose(
            route.abs().sum(1),
            torch.ones(config.batch_size),
            atol=1e-5,
        ):
            raise AssertionError("Signed coefficients are not L1-normalized")

    count = model.stored_parameter_count()
    expected_count = sum(parameter.numel() for parameter in model.parameters())
    if count != expected_count:
        raise AssertionError("Stored parameter accounting mismatch")
    flops = model.active_flops(config.batch_size, config.token_count)
    if flops != model.active_flops(config.batch_size, config.token_count):
        raise AssertionError("FLOPs accounting is nondeterministic")

    return {
        "passed": True,
        "stored_parameter_count": count,
        "analytical_active_flops": flops,
    }


def write_results(path: str, document: Dict[str, object]) -> None:
    destination = Path(path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=destination.parent, delete=False
        ) as stream:
            temporary = stream.name
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        if temporary:
            Path(temporary).unlink(missing_ok=True)
        raise