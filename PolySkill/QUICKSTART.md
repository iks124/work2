# PolySkill Quick Start Guide

Get started with PolySkill in 5 minutes!

## Prerequisites

- Python 3.10+
- Chrome/Chromium browser
- An API key for OpenAI and/or Anthropic

## Step 1: Install

```bash
# Clone and navigate to directory
cd PolySkill

# Create and activate a conda environment
conda create -n polyskill python=3.10 -y
conda activate polyskill

# Install dependencies
pip install -r requirements.txt

# Install PolySkill
pip install -e .

# Install the Playwright browser used by BrowserGym
playwright install chromium
```

## Step 2: Set Up API Keys

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Minimum required entries:

```bash
OPENAI_API_KEY=your_openai_key_here
# and/or
ANTHROPIC_API_KEY=your_anthropic_key_here
```

For open-source models (Qwen3-Coder / GLM-4.5) via SGLang or OpenRouter, also set:

```bash
POLYSKILL_OSS_API_BASE=http://localhost:30000/v1   # SGLang, or OpenRouter URL
POLYSKILL_OSS_API_KEY=EMPTY
```

## Step 3: Smoke Test (no Docker needed)

Run the offline test suite to verify the install:

```bash
pytest -m "not llm" tests/
```

The offline suite includes a stubbed end-to-end pipeline test (real agent + harness +
skill induction, with the LLM and browser stubbed), so a green run means the full
pipeline is wired correctly — no API keys or live sites needed.

## Step 4: Run Your First WebArena Experiment

Stand up the WebArena Docker sites first — see [docs/WEBARENA.md](docs/WEBARENA.md) for
the full guide. Then export the site URLs and run:

```bash
python -m polyskill.experiments.webarena.run_webarena \
    --config examples/configs/webarena_polyskill_gpt4.yaml \
    --category shopping \
    --model gpt-4.1
```

Available `--category` values: `shopping`, `admin`, `reddit`, `gitlab`, `map`, `cross`, `all`.

## Step 5: Self-Proposing Exploration

Let the agent autonomously explore the shopping site and learn skills:

```bash
python -m polyskill.experiments.self_proposing.run_self_proposing \
    --config examples/configs/self_proposing_shopping_gpt4.yaml \
    --domain shopping \
    --iterations 50 \
    --model gpt-4.1
```

## Step 6: View Results

After completion, results are saved to:
- `./results/` — Experiment logs and trajectories
- `./results/*_skills/` — Learned polymorphic skills

## Common Issues & Solutions

### Issue: "Module not found"
**Solution:** Make sure you ran `pip install -e .`

### Issue: "API key not found"
**Solution:** Check your `.env` file has correct keys

### Issue: "Browser timeout"
**Solution:** Increase timeout in config:
```yaml
runner:
  timeout_secs: 600  # Increase from default
```

### Issue: WebArena site unreachable
**Solution:** Make sure all Docker containers are running and the `WA_*` env vars are set.
See [docs/WEBARENA.md](docs/WEBARENA.md).

## Next Steps

1. **Try a different model:**
   ```bash
   python -m polyskill.experiments.webarena.run_webarena \
       --config examples/configs/webarena_polyskill_claude.yaml \
       --category shopping \
       --model claude-3-7-sonnet-20250219
   ```

2. **Open-source models (Qwen3-Coder / GLM-4.5):**
   See [docs/WEBARENA.md](docs/WEBARENA.md) — Section 4 (SGLang or OpenRouter).

3. **Customize experiments:**
   - Edit configs in `examples/configs/`
   - Modify prompts in `polyskill/prompts/`

4. **Mind2Web (live-web evaluation):**
   ```bash
   python scripts/prepare_mind2web.py   # one-time: build the task splits
   python -m polyskill.experiments.mind2web.run_mind2web \
       --config examples/configs/mind2web_polyskill_gpt4.yaml \
       --setting cross-task \
       --model gpt-4.1
   ```
   See [docs/MIND2WEB.md](docs/MIND2WEB.md) for start-URL caveats and judge costs.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `pytest -m "not llm" tests/` | Offline unit tests (no API key needed) |
| `python -m polyskill.experiments.webarena.run_webarena` | WebArena experiment |
| `python -m polyskill.experiments.mind2web.run_mind2web` | Mind2Web live-web experiment |
| `python -m polyskill.experiments.self_proposing.run_self_proposing` | Autonomous exploration |
| `python scripts/prepare_mind2web.py` | Build the Mind2Web task splits |
| `bash scripts/host_qwen3_coder.sh` | Start SGLang server for Qwen3-Coder |

## Getting Help

- Read full [README.md](README.md)
- WebArena setup: [docs/WEBARENA.md](docs/WEBARENA.md)
- Mind2Web setup: [docs/MIND2WEB.md](docs/MIND2WEB.md)
- Report issues on GitHub
- Email: yu.chi@northeastern.edu
