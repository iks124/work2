# Running PolySkill on WebArena

WebArena provides Dockerized realistic websites across six categories. This guide covers
installation, standing up the sites, and running PolySkill experiments.

---

## 1. Installation

```bash
# Create and activate a conda environment
conda create -n polyskill python=3.10 -y
conda activate polyskill

# Install Python dependencies
pip install -r requirements.txt

# Install PolySkill in editable mode
pip install -e .

# Install the Playwright browser used by BrowserGym
playwright install chromium
```

---

## 2. Standing Up the WebArena Docker Sites

Follow the official WebArena setup guide to pull and start the Docker containers:
<https://github.com/web-arena-x/webarena/blob/main/environment_docker/README.md>

The short version:

1. Install Docker and `docker compose`.
2. Pull the images and start the services (the README above lists the exact `docker compose` commands).
3. Once the containers are running, export the site URLs as environment variables. A typical
   localhost deployment looks like:

```bash
export WA_SHOPPING=http://localhost:7770
export WA_SHOPPING_ADMIN=http://localhost:7780
export WA_REDDIT=http://localhost:9999
export WA_GITLAB=http://localhost:8023
export WA_WIKIPEDIA=http://localhost:8888
export WA_MAP=http://localhost:3000
export WA_HOMEPAGE=http://localhost:4399
```

Add these (with your actual hostnames/ports) to your `.env` file.

---

## 3. Running WebArena Experiments

### With GPT-4.1

```bash
python -m polyskill.experiments.webarena.run_webarena \
    --config examples/configs/webarena_polyskill_gpt4.yaml \
    --category shopping \
    --model gpt-4.1
```

Available `--category` values: `shopping`, `admin`, `reddit`, `gitlab`, `map`, `cross`, `all`.

### With Claude 3.7 Sonnet

```bash
python -m polyskill.experiments.webarena.run_webarena \
    --config examples/configs/webarena_polyskill_claude.yaml \
    --category shopping \
    --model claude-3-7-sonnet-20250219
```

### With Open-Source Models

See Section 4 below to bring up the model server first, then:

```bash
python -m polyskill.experiments.webarena.run_webarena \
    --config examples/configs/webarena_polyskill_qwen.yaml \
    --category shopping \
    --model qwen3-coder-480b-a35b
```

---

## 4. Open-Source Models: SGLang or OpenRouter

### Option A — Self-hosted SGLang server

Install SGLang, then start the Qwen3-Coder server (requires multi-GPU):

```bash
pip install "sglang[all]"

# In a screen/tmux session:
bash scripts/host_qwen3_coder.sh
```

The script reads `POLYSKILL_QWEN_MODEL_PATH` (path to the local checkpoint) and
`POLYSKILL_QWEN_SERVED_NAME` (default: `qwen3-coder-480b-a35b`). Set `TP_SIZE` inside
the script to match your GPU count. Then set:

```bash
export POLYSKILL_OSS_API_BASE=http://localhost:30000/v1
export POLYSKILL_OSS_API_KEY=EMPTY   # SGLang does not require a real key
```

### Option B — OpenRouter

No local GPU required. Set:

```bash
export POLYSKILL_OSS_API_BASE=https://openrouter.ai/api/v1
export POLYSKILL_OSS_API_KEY=<your-openrouter-key>
# Model names are forwarded as-is; the defaults match OpenRouter's naming.
```

---

## 5. Self-Proposing Exploration (WebArena Shopping backend)

```bash
python -m polyskill.experiments.self_proposing.run_self_proposing \
    --config examples/configs/self_proposing_shopping_gpt4.yaml \
    --domain shopping \
    --iterations 150 \
    --model gpt-4.1
```

---

## 6. Other Benchmarks

| Benchmark | Status | Notes |
|-----------|--------|-------|
| WebArena  | Supported | You self-host the Dockerized sites (this guide) and set the `WA_*` URLs |
| Mind2Web  | Supported | Live-web execution + GPT-4.1 WebJudge; splits provided — see [MIND2WEB.md](MIND2WEB.md) |

For an offline sanity check that needs no sites or API keys:

```bash
pytest -m "not llm" tests/   # includes a stubbed end-to-end pipeline test
```
