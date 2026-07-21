#!/usr/bin/env bash
# Fails if any banned Orby-internal term survives in the released tree.
# A narrow allowlist permits the user-sanctioned compute-sponsor acknowledgment in README.
set -uo pipefail
cd "$(dirname "$0")/../.."
BANNED='orby|orbot|digitalagent|mosaic-vllm|mosaic_vllm|s3://orby-llm|cmu\.litellm\.ai|orby-ai-engineering|fm\.trajectory_data_pb2|fm\.llm_data_pb2|fm\.action_data_pb2|from fm import|pb\.v1alpha1'
# Sanctioned exception (user-approved): the README acknowledgment crediting the compute sponsor.
ALLOW='README\.md:[0-9]+:.*orby\.ai'
HITS=$(grep -rInE "$BANNED" \
  --include='*.py' --include='*.yaml' --include='*.yml' --include='*.md' --include='*.sh' --include='*.txt' \
  --include='*.js' --include='*.json' --include='*.html' --include='*.cfg' --include='*.toml' --include='*.ini' \
  --exclude-dir='.git' --exclude-dir='__pycache__' --exclude-dir='baselines' \
  --exclude-dir='superpowers' --exclude-dir='issue-responses' \
  --exclude='scrub_check.sh' \
  . 2>/dev/null | grep -vE "$ALLOW")
if [ -n "$HITS" ]; then echo "SCRUB FAIL — banned terms found:"; echo "$HITS"; exit 1; fi
echo "SCRUB OK — no banned terms (README sponsor acknowledgment allowlisted)"
