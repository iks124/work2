#!/bin/bash
# Script to host GLM-4.5 model using SGLang
# This needs to be running before starting experiments with this model
#
# The served model name MUST match the POLYSKILL_GLM_SERVED_NAME env var
# (default: glm-4.5) configured in your PolySkill environment.
# Set MODEL_PATH to the local HuggingFace checkpoint for GLM-4.5.

set -e

# Configuration
# Set MODEL_PATH to the local checkpoint for GLM-4.5
MODEL_PATH="${POLYSKILL_GLM_MODEL_PATH:-/path/to/GLM-4.5}"
# The served model name must match POLYSKILL_GLM_SERVED_NAME (used by litellm routing)
SERVED_NAME="${POLYSKILL_GLM_SERVED_NAME:-glm-4.5}"
PORT=30001
HOST="0.0.0.0"
TP_SIZE=4  # Tensor parallel size - adjust based on your GPU count

# Check if SGLang is installed
if ! python -c "import sglang" &> /dev/null; then
    echo "Error: SGLang is not installed. Please install it first:"
    echo "pip install 'sglang[all]'"
    exit 1
fi

echo "Starting GLM-4.5 model server on port ${PORT}..."
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
    2>&1 | tee glm4_server.log

# Note: The server will run in the foreground
# To run in background, add '&' at the end or use screen/tmux
