#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$REPO_DIR/../.venv/bin/python}"
CONFIG="${CONFIG:-examples/configs/mind2web_polyskill_qwen480b_judge_qwen480b_induce_qwen3_5_9b.yaml}"
SETTING="${SETTING:-cross-task}"

cd "$REPO_DIR"
export NO_PROXY="127.0.0.1,localhost${NO_PROXY:+,$NO_PROXY}"
export no_proxy="$NO_PROXY"

# This host does not provide the Playwright runtime packages system-wide. The
# local extraction is optional on machines where `playwright install-deps` ran.
LOCAL_LIB="$REPO_DIR/.local-browser-deps/root/usr/lib/x86_64-linux-gnu"
if [[ -d "$LOCAL_LIB" ]]; then
  export LD_LIBRARY_PATH="$LOCAL_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

exec "$PYTHON" -m polyskill.experiments.mind2web.run_mind2web \
  --config "$CONFIG" \
  --setting "$SETTING" \
  --model Qwen3-Coder-480B-A35B-Instruct
