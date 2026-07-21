#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=${PSP:-/Users/simonyu/opt/anaconda3/envs/polyskill/bin}/python
$PY -c "import polyskill; print('import polyskill OK')"
$PY -c "import polyskill.experiments.webarena.run_webarena as m; print('webarena entrypoint OK')"
$PY -c "import polyskill.experiments.mind2web.run_mind2web as m; print('mind2web entrypoint OK')"
$PY -c "import polyskill.experiments.self_proposing.run_self_proposing as m; print('self_proposing entrypoint OK')"
echo "IMPORT CHECK OK"
