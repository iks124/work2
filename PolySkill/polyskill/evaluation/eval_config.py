"""Pydantic configuration schema for the PolySkill evaluation harness.

Designed so the *documented* surface validates: a benchmark is selected by
``dataset`` plus the human-friendly ``category`` (WebArena) / ``setting`` (Mind2Web)
that the README and example commands use. Unknown keys are ignored (``extra="ignore"``)
so older/looser configs don't crash construction.
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    provider: str
    name: str
    temperature: float = 0.0
    max_tokens: int = 512
    timeout: int = 120
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    supports_vision: bool = True
    planner: Optional["ModelConfig"] = None
    executor: Optional["ModelConfig"] = None
    grounder: Optional["ModelConfig"] = None


class BenchmarkConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: Optional[str] = None
    dataset: str                      # "webarena" | "miniwob" | "mind2web"
    category: Optional[str] = None    # webarena: shopping/admin/reddit/gitlab/map/cross/all
    setting: Optional[str] = None     # mind2web: cross-task/cross-website/cross-domain
    split_dir: Optional[str] = None   # mind2web: dir with split JSONs (default data/mind2web)
    max_examples: int = -1
    max_steps: int = 30
    headless: bool = True
    reset_env: bool = True
    example_ids: List[str] = []


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    model: Optional[ModelConfig] = None
    model_config_name: Optional[str] = None
    action_file_path: Optional[str] = None
    enable_skill_induction: Optional[bool] = None
    skill_storage_path: Optional[str] = None
    min_skill_complexity: Optional[int] = None
    max_skill_complexity: Optional[int] = None
    max_actions_per_step: Optional[int] = 5
    skill_induction_config: Optional[Dict[str, Any]] = None


class RunnerConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    threads: int = 8
    output_dir: Optional[str] = None
    output_dirs: Optional[List[str]] = None
    seed: Optional[int] = 42
    timeout_secs: int = 600

    def get_output_dirs(self) -> List[str]:
        if self.output_dirs:
            return self.output_dirs
        if self.output_dir:
            return [self.output_dir]
        return []


class EvalConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    run_name: Optional[str] = None
    run_id: Optional[str] = None
    runner: RunnerConfig
    benchmarks: Dict[str, BenchmarkConfig]
    agents: Dict[str, AgentConfig]
    model_configs: Dict[str, ModelConfig] = {}
