#!/usr/bin/env bash
# ============================================================================
# Evaluate one checkpoint on the held-out test set.
# Non-Slurm analogue of slurm/20_evaluate.slurm.
#
# Args are KEY=VALUE OR env vars:
#   MODEL  model name (e.g. efficientnet_b0)   [required]
#   CKPT   path to the .pth checkpoint          [required]
#   OUT    output json  (default reports/results/${MODEL}_metrics.json)
#   GPU    physical GPU id / "auto" / "cpu"     (default auto)
#
# Usage:
#   bash run/evaluate.sh MODEL=mobilenetv3_large \
#        CKPT=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_0/checkpoints/best_model.pth
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "evaluate"
activate_venv
select_gpu

: "${MODEL:?MODEL env var required (e.g. efficientnet_b0)}"
: "${CKPT:?CKPT env var required (path to .pth)}"
OUT="${OUT:-reports/results/${MODEL}_metrics.json}"

echo "[run] Evaluating ${MODEL} from ${CKPT} -> ${OUT}"
mkdir -p "$(dirname "${OUT}")"
python scripts/evaluate.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --output "${OUT}"
echo "[run] DONE"
