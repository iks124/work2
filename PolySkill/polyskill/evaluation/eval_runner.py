"""Resolve BrowserGym env ids for a benchmark, plus model-readiness and output-dir helpers.

This module turns a :class:`BenchmarkConfig` into the concrete list of gymnasium
environment ids that the harness will roll out, applying ``example_ids`` filtering,
optional WebArena category filtering, deterministic shuffling, and ``max_examples``
truncation.

It builds only on the *public* BrowserGym packages:
``browsergym.miniwob`` and ``browsergym.webarena`` register their tasks under
``browsergym/miniwob.<task>`` and ``browsergym/webarena.<N>`` respectively.
"""
from __future__ import annotations

import logging
import os
import random
import time
from typing import List, Optional, Tuple

import gymnasium as gym

# Importing these packages registers their tasks in ``gymnasium.envs.registry``.
# ``browsergym.core`` also registers the ``browsergym/openended`` task used for
# Mind2Web (live start_url + goal); the two packages below import it transitively,
# but we depend on it explicitly to keep the registration intent clear.
import browsergym.core  # noqa: F401  (registers browsergym/openended)
import browsergym.miniwob  # noqa: F401
import browsergym.webarena  # noqa: F401

from .eval_config import BenchmarkConfig, EvalConfig, ModelConfig

logger = logging.getLogger(__name__)

# WebArena ``sites`` -> human-friendly category used in configs / README.
# Single-site tasks map to a single category; ``shopping_admin`` is exposed as
# ``admin``. Any task touching more than one site is treated as ``cross``.
_WEBARENA_SITE_TO_CATEGORY = {
    "shopping": "shopping",
    "shopping_admin": "admin",
    "gitlab": "gitlab",
    "reddit": "reddit",
    "map": "map",
    "wikipedia": "map",  # wikipedia only appears alongside map; treat as map otherwise cross
}


def _list_env_ids(prefix: str) -> List[str]:
    """All registered gymnasium env ids beginning with ``prefix``."""
    return sorted(e for e in gym.envs.registry if e.startswith(prefix))


def _load_webarena_task_sites() -> Optional[dict]:
    """Map ``task_id`` (int) -> tuple of WebArena sites, read from the public configs.

    The ``webarena`` package ships ``test.raw.json`` describing every task. Reading
    it requires no live WebArena server. Returns ``None`` if it cannot be loaded so
    callers can fall back to best-effort behaviour.
    """
    try:
        import importlib.resources
        import json

        import webarena

        raw = importlib.resources.files(webarena).joinpath("test.raw.json").read_text()
        configs = json.loads(raw)
        return {int(c["task_id"]): tuple(sorted(c["sites"])) for c in configs}
    except Exception as e:  # pragma: no cover - defensive
        logger.warning("Could not load WebArena task configs for category mapping: %r", e)
        return None


def _category_for_sites(sites: Tuple[str, ...]) -> str:
    """Derive a single category label from a task's ``sites`` tuple."""
    if len(sites) != 1:
        return "cross"
    return _WEBARENA_SITE_TO_CATEGORY.get(sites[0], "cross")


def _env_id_task_id(env_id: str) -> Optional[int]:
    """Extract the integer WebArena task id from ``browsergym/webarena.<N>``."""
    try:
        return int(env_id.rsplit(".", 1)[1])
    except (IndexError, ValueError):
        return None


def _apply_example_ids(env_ids: List[str], example_ids: List[str]) -> List[str]:
    """Keep only env ids whose id (or trailing task id) is in ``example_ids``."""
    if not example_ids:
        return env_ids
    wanted = set(str(x) for x in example_ids)
    kept = []
    for e in env_ids:
        tail = e.rsplit(".", 1)[1] if "." in e else e
        if e in wanted or tail in wanted:
            kept.append(e)
    return kept


def _shuffle_and_truncate(
    env_ids: List[str], shuffle_seed: Optional[int], max_examples: int
) -> List[str]:
    """Deterministically shuffle (if a seed is given), then truncate to ``max_examples``."""
    env_ids = list(env_ids)
    if shuffle_seed is not None:
        random.Random(shuffle_seed).shuffle(env_ids)
    if max_examples is not None and max_examples > 0:
        env_ids = env_ids[:max_examples]
    return env_ids


def get_env_ids_and_task_kwargs(
    benchmark_config: BenchmarkConfig, shuffle_seed: Optional[int] = None
) -> Tuple[List[str], Optional[dict]]:
    """Resolve the list of gymnasium env ids (and per-env task kwargs) for a benchmark.

    Returns ``(env_ids, task_kwargs)``. ``task_kwargs`` is ``None`` for both MiniWoB
    and WebArena (task parameters are baked into the registered env ids).
    """
    dataset = benchmark_config.dataset

    if dataset == "miniwob":
        env_ids = _list_env_ids("browsergym/miniwob.")
        env_ids = _apply_example_ids(env_ids, benchmark_config.example_ids)
        env_ids = _shuffle_and_truncate(env_ids, shuffle_seed, benchmark_config.max_examples)
        return env_ids, None

    if dataset == "webarena":
        env_ids = _list_env_ids("browsergym/webarena.")
        category = benchmark_config.category

        if category and category != "all":
            task_sites = _load_webarena_task_sites()
            if task_sites is None:
                logger.warning(
                    "WebArena category filtering is APPROXIMATE: could not load task->sites "
                    "metadata from the 'webarena' package; returning all WebArena env ids "
                    "truncated by max_examples instead of filtering by category=%r.",
                    category,
                )
            else:
                wanted = category.lower()
                filtered = []
                for e in env_ids:
                    tid = _env_id_task_id(e)
                    if tid is None or tid not in task_sites:
                        continue
                    if _category_for_sites(task_sites[tid]) == wanted:
                        filtered.append(e)
                if not filtered:
                    logger.warning(
                        "WebArena category=%r matched no tasks; returning all WebArena env "
                        "ids truncated by max_examples instead.",
                        category,
                    )
                else:
                    env_ids = filtered

        env_ids = _apply_example_ids(env_ids, benchmark_config.example_ids)
        env_ids = _shuffle_and_truncate(env_ids, shuffle_seed, benchmark_config.max_examples)
        return env_ids, None

    if dataset == "mind2web":
        from .mind2web import SETTING_FILES, load_mind2web_split

        setting = benchmark_config.setting
        if not setting:
            valid = ", ".join(sorted(SETTING_FILES))
            raise ValueError(
                "Mind2Web requires benchmark_config.setting "
                f"(one of: {valid}); none was provided."
            )
        split_dir = benchmark_config.split_dir or "data/mind2web"
        tasks = load_mind2web_split(setting, split_dir)

        # Honor example_ids (filter by task_id).
        if benchmark_config.example_ids:
            wanted = set(str(x) for x in benchmark_config.example_ids)
            tasks = [t for t in tasks if str(t["task_id"]) in wanted]

        # Deterministic shuffle, then truncate.
        if shuffle_seed is not None:
            random.Random(shuffle_seed).shuffle(tasks)
        if benchmark_config.max_examples is not None and benchmark_config.max_examples > 0:
            tasks = tasks[: benchmark_config.max_examples]

        # Every Mind2Web task runs live in the same openended env; the concrete
        # start_url + goal ride in per-task kwargs (unlike miniwob/webarena, whose
        # parameters are baked into the registered env id).
        env_ids = ["browsergym/openended"] * len(tasks)
        task_kwargs = [
            {
                "start_url": t["url"],
                "goal": t["task"],
                "task_id": t["task_id"],
                "website": t.get("website"),
            } | {
                key: t[key] for key in ("domain", "subdomain") if t.get(key)
            }
            for t in tasks
        ]
        return env_ids, task_kwargs

    raise ValueError(f"Unknown benchmark dataset: {dataset!r}")


# Providers whose readiness we can/should poll (OSS / OpenAI-compatible servers).
_OSS_PROVIDERS = {"oss", "openai-compatible", "openai_compatible", "vllm", "local", "sglang"}


def wait_for_models(model_config: ModelConfig) -> None:
    """Best-effort wait for a self-hosted, OpenAI-compatible model server to come up.

    Only polls when ``model_config.provider`` looks like an OSS / OpenAI-compatible
    provider AND ``POLYSKILL_OSS_API_BASE`` is set. Hosted providers (openai,
    anthropic, ...) return immediately. Never raises.
    """
    provider = (getattr(model_config, "provider", "") or "").lower()
    base = os.environ.get("POLYSKILL_OSS_API_BASE")
    if provider not in _OSS_PROVIDERS or not base:
        return

    base = base.rstrip("/")
    urls = [f"{base}/models", base]
    try:
        import urllib.request
    except Exception:  # pragma: no cover - stdlib always present
        return

    for attempt in range(10):
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    if getattr(resp, "status", 200) < 500:
                        logger.info("Model server ready at %s", url)
                        return
            except Exception:
                continue
        time.sleep(2)
    logger.warning(
        "Model server at %s did not become ready after polling; proceeding anyway.", base
    )


def _get_output_dirs_for_run(
    eval_config: EvalConfig, benchmark_name: str, agent_name: str
) -> List[str]:
    """Compute (and create) the output directory for one benchmark+agent run."""
    run_id = eval_config.run_id or eval_config.run_name or "run"
    base_dirs = eval_config.runner.get_output_dirs()
    base = base_dirs[0] if base_dirs else "./results"
    out_dir = os.path.join(base, run_id, f"{benchmark_name}_{agent_name}")
    os.makedirs(out_dir, exist_ok=True)
    return [out_dir]
