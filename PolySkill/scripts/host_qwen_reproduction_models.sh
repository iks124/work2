#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VLLM_PYTHON="${VLLM_PYTHON:-/data/GoEMem/vllm/bin/python}"
PROJECT_BIN="$ROOT_DIR/.venv/bin"
LOG_DIR="$ROOT_DIR/logs"

mkdir -p "$LOG_DIR"
export PATH="$PROJECT_BIN:/data/GoEMem/vllm/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

if [[ ! -x "$PROJECT_BIN/ninja" ]]; then
  echo "Missing $PROJECT_BIN/ninja; install it with: $PROJECT_BIN/python -m pip install ninja" >&2
  exit 1
fi

CUDA_VISIBLE_DEVICES=0,1,2,4 nohup "$VLLM_PYTHON" -m vllm.entrypoints.cli.main serve \
  /data/dingkun/swift/Qwen3-Coder-480B-A35B-Instruct-AWQ \
  --served-model-name Qwen3-Coder-480B-A35B-Instruct \
  --tensor-parallel-size 4 --max-model-len 32768 \
  --gpu-memory-utilization 0.90 --trust-remote-code \
  --host 0.0.0.0 --port 8002 \
  > "$LOG_DIR/qwen3-coder-480b-a35b-awq-tp4.log" 2>&1 &
echo "480B PID: $!"

CUDA_VISIBLE_DEVICES=5 nohup "$VLLM_PYTHON" -m vllm.entrypoints.cli.main serve \
  /data/GoEMem/Qwen3.5-9B \
  --served-model-name Qwen3.5-9B \
  --max-model-len 32768 --dtype bfloat16 \
  --gpu-memory-utilization 0.85 --trust-remote-code \
  --host 0.0.0.0 --port 8003 \
  > "$LOG_DIR/qwen3.5-9b-gpu5.log" 2>&1 &
echo "9B PID: $!"

echo "Watch startup with: tail -f $LOG_DIR/qwen3*.log"
