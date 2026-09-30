#!/usr/bin/env bash
# ============================================================================
# Evaluate one checkpoint on the held-out test set.
#
# Args are KEY=VALUE OR env vars:
#   MODEL  model name (e.g. mobilenetv4_conv_medium)   [required]
#   CKPT   path to the .pth checkpoint          [required]
#   OUT    output json  (default reports/results/${MODEL}_metrics.json)
#   GPU    physical GPU id / "auto" / "cpu"     (default auto)
#
# Usage:
#   bash run/evaluate.sh MODEL=mobilenetv4_conv_medium \
#        CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "evaluate"
activate_venv
select_gpu

: "${MODEL:?MODEL env var required (e.g. mobilenetv4_conv_medium)}"
: "${CKPT:?CKPT env var required (path to .pth)}"
OUT="${OUT:-reports/results/${MODEL}_metrics.json}"

echo "[run] Evaluating ${MODEL} from ${CKPT} -> ${OUT}"
mkdir -p "$(dirname "${OUT}")"
python scripts/evaluate.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --output "${OUT}"
echo "[run] DONE"
