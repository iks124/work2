#!/bin/bash
# Script to host Qwen3-Coder-480B-A35B model using SGLang
# This needs to be running before starting experiments with this model
#
# The served model name MUST match the POLYSKILL_QWEN_SERVED_NAME env var
# (default: qwen3-coder-480b-a35b) configured in your PolySkill environment.
# Set MODEL_PATH to the local HuggingFace checkpoint for Qwen3-Coder-480B-A35B.

set -e

# Configuration
# Set MODEL_PATH to the local checkpoint for Qwen3-Coder-480B-A35B
MODEL_PATH="${POLYSKILL_QWEN_MODEL_PATH:-/path/to/Qwen3-Coder-480B-A35B}"
# The served model name must match POLYSKILL_QWEN_SERVED_NAME (used by litellm routing)
SERVED_NAME="${POLYSKILL_QWEN_SERVED_NAME:-qwen3-coder-480b-a35b}"
PORT=30000
HOST="0.0.0.0"
TP_SIZE=8  # Tensor parallel size - adjust based on your GPU count

# Check if SGLang is installed
if ! python -c "import sglang" &> /dev/null; then
    echo "Error: SGLang is not installed. Please install it first:"
    echo "pip install 'sglang[all]'"
    exit 1
fi

echo "Starting Qwen3-Coder-480B-A35B model server on port ${PORT}..."
echo "Model path: ${MODEL_PATH}"
echo "Served name: ${SERVED_NAME}"
echo "Tensor Parallel Size: ${TP_SIZE}"

# Start the SGLang server
python -m sglang.launch_server \
    --model-path "${MODEL_PATH}" \
    --served-model-name "${SERVED_NAME}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --tp "${TP_SIZE}" \
    --trust-remote-code \
    --mem-fraction-static 0.85 \
    2>&1 | tee qwen3_server.log

# Note: The server will run in the foreground
# To run in background, add '&' at the end or use screen/tmux
