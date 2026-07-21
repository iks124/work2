import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from torch import Tensor

from experiment_config import ExperimentConfig
from methods import ReadOnlyAdapterModel, SignedTop2BasisMemory

def smoke_test(
    model: ReadOnlyAdapterModel,
    tokens: Tensor,
    labels: Tensor,
    config: ExperimentConfig,
) -> Dict[str, object]:
    before = model.memory_digest()
    optimizer = torch.optim.Adam(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=config.learning_rate,
    )
    optimizer.zero_grad(set_to_none=True)
    logits, auxiliary = model(tokens)
    loss = model.loss(logits, labels, auxiliary)
    if not torch.isfinite(loss) or float(loss.detach()) > 100:
        raise FloatingPointError("FAIL: NaN/divergence detected")
    loss.backward()

    query_gradient = model.query_projection.weight.grad
    if query_gradient is None or not torch.isfinite(query_gradient).all():
        raise AssertionError("Router gradient missing or nonfinite")
    if float(query_gradient.abs().sum()) == 0:
        raise AssertionError("Router gradient is zero")
    for name, buffer in model.named_buffers():
        if name.startswith("memory_") and buffer.grad is not None:
            raise AssertionError("Read-only memory unexpectedly received gradients")

    torch.nn.utils.clip_grad_norm_(model.parameters(), config.gradient_clip_norm)
    optimizer.step()
    after = model.memory_digest()
    if before != after:
        raise AssertionError("Read-only memory changed after optimizer step")

    route = auxiliary["route"]
    if isinstance(model, SignedTop2BasisMemory):
        if not torch.all((route != 0).sum(1) == 2):
            raise AssertionError("Signed Top-2 sparsity failed")
        if not torch.allclose(
            route.abs().sum(1),
            torch.ones(route.shape[0]),
            atol=1e-5,
        ):
            raise AssertionError("Signed coefficients are not normalized")

    return {
        "passed": True,
        "stored_parameters": model.stored_parameter_count(),
        "active_flops": model.active_flops(
            tokens.shape[0],
            tokens.shape[1],
        ),
    }

@torch.no_grad()
def accuracy(
    model: ReadOnlyAdapterModel,
    features: np.ndarray,
    labels: np.ndarray,
    seen_classes: np.ndarray,
) -> float:
    model.eval()
    inputs = torch.from_numpy(features)
    targets = torch.from_numpy(labels)
    logits, _ = model(inputs)
    masked = torch.full_like(logits, -torch.inf)
    indices = torch.from_numpy(seen_classes.astype(np.int64))
    masked[:, indices] = logits[:, indices]
    return float((masked.argmax(1) == targets).float().mean())

def primary_metric(checkpoint_accuracies: List[float]) -> float:
    if len(checkpoint_accuracies) != 10:
        raise ValueError("Primary metric requires ten task checkpoints")
    return -100.0 * float(np.mean(np.asarray(checkpoint_accuracies)))

def atomic_write(path: str, document: Dict[str, object]) -> None:
    destination = Path(path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=destination.parent,
            delete=False,
        ) as stream:
            temporary = stream.name
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
        raise