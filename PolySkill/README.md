<div align="center">
<h1>PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction</h1>

[![Paper](https://img.shields.io/badge/Paper-2510.15863-red?style=for-the-badge&logo=arxiv&logoColor=white)](https://arxiv.org/abs/2510.15863) [![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT) [![WebArena](https://img.shields.io/badge/Benchmark-WebArena-4d8cd8?style=for-the-badge)](https://webarena.dev/) [![Mind2Web](https://img.shields.io/badge/Benchmark-Mind2Web-4d8cd8?style=for-the-badge)](https://osu-nlp-group.github.io/Mind2Web/)

**Simon Yu**¹ · **Gang Li**² · **Weiyan Shi**¹ · **Peng Qi**²
¹Northeastern University · ²Uniphore
</div>

---

> [!IMPORTANT]
> This is a **clean-room re-release**: the original code drop depended on internal
> infrastructure that could not be open-sourced, so the harness has been rebuilt from
> scratch on public **[BrowserGym](https://github.com/ServiceNow/BrowserGym)** +
> **[litellm](https://github.com/BerriAI/litellm)** — zero internal dependencies.
> WebArena requires self-hosting the Dockerized sites; Mind2Web runs on the live web
> with your API keys. Issues and feedback are very welcome!

<p align="center">
  <a href="#installation">Install</a> |
  <a href="#quickstart">Quickstart</a> |
  <a href="#polymorphic-skill-induction--the-core-module">Polymorphic Module</a> |
  <a href="#reproducing-paper-results">Reproduce</a> |
  <a href="#architecture">Architecture</a> |
  <a href="#citation">Citation</a>
</p>

**PolySkill** enables web agents to learn **generalizable, compositional skills** by
separating a skill's *abstract goal* (what it accomplishes) from its *concrete
implementation* (how it's executed on a given website) — polymorphism, applied to agent
skill learning. Agents learn skills that transfer across websites, compose complex
behaviors from reusable parts, improve success rates with 1.3–1.8× skill-reuse gains
over prior methods, and self-improve through autonomous exploration.

## News

- **[2026-07]** 🔧 Clean-room re-release: harness rebuilt on public BrowserGym + litellm; Mind2Web live-eval splits bundled; runnable no-key polymorphic-induction demo.
- **[2025-11-10]** 🎉 PolySkill paper and code released! Check out the [arXiv paper](https://arxiv.org/abs/2510.15863).

## Installation

```bash
# Clone with baseline submodules
git clone --recursive https://github.com/simonucl/PolySkill.git
cd PolySkill

# Create an environment (Python 3.10+)
conda create -n polyskill python=3.10 -y
conda activate polyskill

# Install
pip install -r requirements.txt
pip install -e .
playwright install chromium   # browser used by BrowserGym
```

Then copy `.env.example` to `.env` and fill in what you need:

```bash
cp .env.example .env
```

```bash
# Proprietary model providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Open-source models (Qwen3-Coder / GLM-4.5) via SGLang or OpenRouter
POLYSKILL_OSS_API_BASE=http://localhost:30000/v1   # or https://openrouter.ai/api/v1
POLYSKILL_OSS_API_KEY=EMPTY                        # or your OpenRouter key

# WebArena site URLs (self-hosted — see docs/WEBARENA.md)
WA_SHOPPING=http://localhost:7770
# ... (full list in .env.example)
```

All four paper models route through one litellm client (`polyskill.model.FoundationModel`):
**GPT-4.1**, **Claude-3.7-Sonnet**, **Qwen3-Coder-480B-A35B**, **GLM-4.5**.

## Quickstart

### 1. See the core idea run — no API key, ~5 seconds

The polymorphic induction demo feeds a canned model response through the **real**
induction pipeline (prompt → abstract interface + concrete subclass → stored skill):

```bash
python examples/demo_polymorphic_induction.py          # offline, keyless
python examples/demo_polymorphic_induction.py --live   # real LLM call (OPENAI_API_KEY)
```

Verify the full install the same way — the offline suite includes a stubbed
end-to-end pipeline test (real agent + harness + skill induction):

```bash
pytest -m "not llm" tests/
```

### 2. WebArena (self-hosted sites)

Stand up the Dockerized WebArena sites and export the `WA_*` URLs first — full guide in
[docs/WEBARENA.md](docs/WEBARENA.md). Then:

```bash
python -m polyskill.experiments.webarena.run_webarena \
    --config examples/configs/webarena_polyskill_gpt4.yaml \
    --category shopping \
    --model gpt-4.1
```

`--category`: `shopping` · `admin` · `reddit` · `gitlab` · `map` · `cross` · `all`.

### 3. Mind2Web (live web + WebJudge)

Tasks execute on the live web and success is the GPT-4.1 WebJudge verdict, as in the
paper. Task splits are bundled in [`data/mind2web/`](data/mind2web/) (rebuild or
override start URLs with `python scripts/prepare_mind2web.py`):

```bash
python -m polyskill.experiments.mind2web.run_mind2web \
    --config examples/configs/mind2web_polyskill_gpt4.yaml \
    --setting cross-task \
    --model gpt-4.1
```

`--setting`: `cross-task` · `cross-website` · `cross-domain` (177 / 142 / 694 bundled
tasks). Start-URL caveats and judge costs: [docs/MIND2WEB.md](docs/MIND2WEB.md).

### 4. Self-proposing exploration (task-free)

The agent proposes its own goals from the abstract-class schema and learns skills from
its successes (WebArena shopping backend):

```bash
python -m polyskill.experiments.self_proposing.run_self_proposing \
    --config examples/configs/self_proposing_shopping_gpt4.yaml \
    --domain shopping \
    --iterations 150 \
    --model gpt-4.1
```

### Hosting the open-source models (optional)

To self-host **Qwen3-Coder-480B-A35B** / **GLM-4.5** with SGLang instead of using
OpenRouter (multi-GPU; adjust `TP_SIZE` in the scripts):

```bash
pip install uv && uv pip install "sglang" --prerelease=allow
./scripts/host_qwen3_coder.sh    # port 30000
./scripts/host_glm4.sh           # port 30001
```

Keep the servers running (e.g. in `tmux`) before starting experiments.

## Polymorphic Skill Induction — the core module

The paper's central mechanism — inducing an **abstract domain interface first**, then a
**site-specific concrete implementation** — is implemented and tested. Where to look:

| What | Where |
|---|---|
| Inducer (`PolymorphicInducer`) | [`polyskill/core/inducers/polymorphic_inducer.py`](polyskill/core/inducers/polymorphic_inducer.py) |
| Abstract-first induction prompt | [`polyskill/prompts/induction/polymorphic.py`](polyskill/prompts/induction/polymorphic.py) |
| Online selection (config-driven) | [`polyskill/core/online_hook.py`](polyskill/core/online_hook.py) — used when `skill_induction.use_polymorphism: true` |
| Runnable demo (no API key needed) | [`examples/demo_polymorphic_induction.py`](examples/demo_polymorphic_induction.py) |
| Unit tests | [`tests/core/test_polymorphic_inducer.py`](tests/core/test_polymorphic_inducer.py) |

From Python:

```python
from polyskill import PolymorphicInducer  # top-level export
```

What an induced skill looks like — the abstract class defines the interface and holds
compositional skills; concrete subclasses implement it per website:

```python
# Abstract class defines the interface
class AbstractShoppingSite:
    def search_product(self, query: str):
        """Searches for a product."""

    def add_to_cart(self, item_id: str, quantity: int):
        """Adds item to shopping cart."""

    # Compositional skill — relies only on the abstract methods
    def find_and_purchase(self, query: str, item_id: str):
        self.search_product(query)
        self.add_to_cart(item_id)
        self.checkout()

# Concrete implementation for a specific website
class AmazonWebsite(AbstractShoppingSite):
    def search_product(self, query: str):
        click(search_box_id)
        fill(search_box_id, query)
        keyboard_press('Enter')
```

## Reproducing Paper Results

### WebArena (Table 8)

```bash
for model in gpt-4.1 claude-3-7-sonnet-20250219 qwen3-coder-480b-a35b glm-4.5; do
    python -m polyskill.experiments.webarena.run_webarena \
        --config examples/configs/webarena_polyskill_gpt4.yaml \
        --category shopping \
        --model $model
done
```

### Mind2Web (Table 2, Figure 3)

Live-execution setting: tasks run on the real web; the reported success rate is the
GPT-4.1 WebJudge verdict (live tasks have no gold reward).

```bash
python scripts/prepare_mind2web.py   # one-time: build/refresh the task splits

for model_cfg in gpt4 claude qwen glm; do
    python -m polyskill.experiments.mind2web.run_mind2web \
        --config examples/configs/mind2web_polyskill_${model_cfg}.yaml \
        --setting cross-task \
        --model "$(python -c "print({'gpt4':'gpt-4.1','claude':'claude-3-7-sonnet-20250219','qwen':'qwen3-coder-480b-a35b','glm':'glm-4.5'}['${model_cfg}'])")"
done
```

The bundled splits come from the openly redistributable Multimodal-Mind2Web test release
(177 / 142 / 694 tasks — a subset of the original 252 / 177 / 912); see
[docs/MIND2WEB.md](docs/MIND2WEB.md) for details, start-URL caveats, and judge costs.

### Self-Proposing Exploration (Table 3, Table 9)

```bash
# Shopping domain
python -m polyskill.experiments.self_proposing.run_self_proposing \
    --config examples/configs/self_proposing_shopping_gpt4.yaml \
    --domain shopping --iterations 150 --model gpt-4.1

# Developer tools
python -m polyskill.experiments.self_proposing.run_self_proposing \
    --config examples/configs/self_proposing_git_gpt4.yaml \
    --domain dev_tools --iterations 100 --model gpt-4.1
```

## Running Baseline Methods

ASI and SkillWeaver are included as git submodules. Each is an independent project with
its own environment and WebArena URL configuration — **follow the submodule READMEs**
([`baselines/ASI/README.md`](baselines/ASI/README.md),
[`baselines/SkillWeaver/README.md`](baselines/SkillWeaver/README.md)); the commands
below are their real entrypoints at the pinned commits:

```bash
git submodule update --init --recursive   # if not cloned with --recursive

# ASI — online skill induction on WebArena shopping
cd baselines/ASI && pip install -r requirements.txt && cd asi
python run_online.py --experiment "asi" --website "shopping" --task_ids "21-25"

# SkillWeaver — attempt a task with a learned skill library
cd baselines/SkillWeaver && pip install -r requirements.txt
python -m skillweaver.attempt_task __SHOPPING__ "your task description" \
    --knowledge-base-path-prefix skill_library/shopping/kb
```

Overview: [baselines/README.md](baselines/README.md). PolySkill integrates and extends
ASI components in `polyskill/core/inducers/asi_inducer.py` and
`polyskill/agents/agent/asi_utils/`.

## Architecture

```
polyskill/
├── core/                       # Skill induction engine
│   ├── core.py                # Orchestrator (SkillInductionCore)
│   ├── skill_storage.py       # Skill storage (PolySkillStorage)
│   ├── simple_inducer.py      # Heuristic online inducer
│   ├── online_hook.py         # Online induction hook (selects the inducer)
│   ├── inducers/              # Skill induction strategies
│   │   ├── polymorphic_inducer.py  # ★ Polymorphic abstraction (paper core)
│   │   ├── pattern_inducer.py  # Pattern-based induction
│   │   └── asi_inducer.py     # ASI-based induction (adapted)
│   └── judge/                 # LLM/VLM task-success judge (WebJudge)
├── model/                      # Unified litellm model layer (FoundationModel)
├── evaluation/                 # BrowserGym eval harness (config / loop / runner)
├── trajectory/                 # BrowserGym-native trajectory format
├── agents/                     # Agent implementations
│   ├── base.py                # Agent / BasicFMAgent base classes
│   ├── agent/                 # HSM hierarchical agent + induction wrapper
│   └── planner/               # LLM task planner
├── exploration/                # Self-proposing exploration (proposer/curriculum/loop)
├── skill_induction/            # Back-compat import shims
├── experiments/                # Entrypoints (webarena / mind2web / self_proposing)
├── prompts/                    # Prompt templates (incl. induction/polymorphic.py)
└── utils/                      # Utility functions

data/mind2web/                  # Bundled Mind2Web test splits (task metadata)
baselines/                      # Baseline methods (git submodules)
├── ASI/                        # Agent Skill Induction baseline
└── SkillWeaver/                # SkillWeaver baseline
```

## Evaluation Metrics

Beyond task success rate, PolySkill introduces:

1. **Skill Reusability** — fraction of learned skills reused in new tasks
2. **Task Coverage** — fraction of tasks that used at least one skill
3. **Skill Compositionality** — how often new skills build on earlier ones
4. **Number of Steps** — actions per solved task (skill calls count as one step)

## Configuration

```yaml
# examples/configs/my_experiment.yaml
skill_induction:
  enabled: true
  use_polymorphism: true          # Enable polymorphic abstraction
  judge_method: webjudge_general  # or webjudge_online_mind2web
  storage_path: ./my_skills/

model_configs:
  default: {provider: openai, name: gpt-4.1, temperature: 0.1, max_tokens: 4096}

benchmarks:
  wa-shopping: {dataset: webarena, category: shopping, max_steps: 30}

agents:
  default: {name: hsm_v3, model_config_name: default}

runner: {threads: 1, output_dir: ./results, seed: 42, timeout_secs: 600}
```

See [`examples/configs/`](examples/configs/) for complete, validated examples
(per-model WebArena/Mind2Web configs and the self-proposing setup).

## Development

```bash
pytest -m "not llm" tests/           # offline suite (no API keys)
pytest -m llm tests/                 # tests that make real LLM calls
bash scripts/dev/scrub_check.sh      # release-hygiene gate
bash scripts/dev/import_check.sh     # entrypoint import gate
```

Contributions are welcome — please open an issue or PR.

## Citation

If you use PolySkill in your research, please cite:

```bibtex
@article{yu2025polyskill,
  title={PolySkill: Learning Generalizable Skills Through Polymorphic Abstraction},
  author={Yu, Simon and Li, Gang and Shi, Weiyan and Qi, Peng},
  journal={arXiv preprint arXiv:2510.15863},
  year={2025}
}
```

## Acknowledgments

We acknowledge **[Orby](https://www.orby.ai/)** (now part of Uniphore) for providing the computational resources and infrastructure support that made the experiments in this paper possible. We thank the authors of **[ASI (Agent Skill Induction)](https://github.com/zorazrw/agent-skill-induction)** and **[SkillWeaver](https://github.com/OSU-NLP-Group/SkillWeaver)** for their pioneering work on skill induction in web agents, which inspired and informed this research. We are grateful to **[SGLang](https://github.com/sgl-project/sglang)** for their exceptional day-0 support and rapid resolution of issues when hosting Qwen3-Coder and GLM-4.5 models. This work builds on **[BrowserGym](https://github.com/ServiceNow/BrowserGym)** for web agent evaluation, and leverages the **[Mind2Web](https://osu-nlp-group.github.io/Mind2Web/)** and **[WebArena](https://webarena.dev/)** benchmarks for rigorous evaluation.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contact

- **Simon Yu**: yu.chi@northeastern.edu
- **GitHub Issues**: https://github.com/simonucl/PolySkill/issues
- **Paper**: https://arxiv.org/abs/2510.15863 · **Docs**: [WebArena](docs/WEBARENA.md) · [Mind2Web](docs/MIND2WEB.md) · [Quickstart](QUICKSTART.md)
