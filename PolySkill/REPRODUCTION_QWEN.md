# Qwen reproduction

This setup assigns the requested model roles as follows:

| Role | Model | Endpoint |
| --- | --- | --- |
| HSM planner/executor | Qwen3-Coder-480B-A35B-Instruct | `http://127.0.0.1:8002/v1` |
| trajectory judge | Qwen3-Coder-480B-A35B-Instruct | `http://127.0.0.1:8002/v1` |
| polymorphic skill induction | Qwen3.5-9B | `http://127.0.0.1:8003/v1` |

The full cross-task config is
`examples/configs/mind2web_polyskill_qwen480b_judge_qwen480b_induce_qwen3_5_9b.yaml`.
The one-task Apple validation config is
`examples/configs/mind2web_qwen480b_qwen3_5_9b_smoke.yaml`.

## Run

```bash
../.venv/bin/python -m pip install ninja
bash scripts/host_qwen_reproduction_models.sh

curl --noproxy '*' http://127.0.0.1:8002/v1/models
curl --noproxy '*' http://127.0.0.1:8003/v1/models

bash scripts/run_mind2web_qwen_reproduction.sh
```

For the one-task smoke run:

```bash
CONFIG=examples/configs/mind2web_qwen480b_qwen3_5_9b_smoke.yaml \
  bash scripts/run_mind2web_qwen_reproduction.sh
```

On a machine with root access, install Chromium dependencies once with
`playwright install-deps chromium`. On this host they were extracted under the
ignored `.local-browser-deps/` directory, which the run script detects.

## Judge limitation

Qwen3-Coder-480B-A35B-Instruct is text-only. The configured judge therefore uses
the Mind2Web WebJudge final rubric with task key points and action history, but
does not send screenshots. This is the closest executable form of the requested
judge assignment; using screenshot evidence requires a vision-capable judge.
