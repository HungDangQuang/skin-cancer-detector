#!/usr/bin/env bash
# ============================================================================
# Export a checkpoint to ExecuTorch (.pte) for Android on-device inference.
# CPU-only.
#
# Uses the ISOLATED export venv (./.venv-export) — deliberately NOT the training
# venv (activate_venv from common.sh). ExecuTorch pins its own torch build, so it
# lives in its own venv and can never perturb the training torch>=2.2.
# One-time setup first:  bash run/setup_export_env.sh
#
# Args are KEY=VALUE OR env vars:
#   MODEL    model name (must match MODEL_REGISTRY)   [required]
#   CKPT     path to best_model.pth                   [required]
#   BACKEND  xnnpack | none   (default xnnpack; `none` = portable-ops fallback
#            when XNNPACK cannot partition an architecture)
#   OUT      output .pte path (default exports/executorch/${MODEL}.pte)
#   EXPORT_VENV_DIR  override the export venv (default ./.venv-export)
#
# Usage:
#   bash run/export_executorch.sh MODEL=mobilenetv4_conv_medium \
#        CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
#   bash run/export_executorch.sh MODEL=fastvit_sa12 CKPT=... BACKEND=none
#
# Output: exports/executorch/<MODEL>.pte
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "export_executorch"
# NOTE: no activate_venv — this job needs the export venv, not the training one.
export CUDA_VISIBLE_DEVICES=""

EXPORT_VENV="${EXPORT_VENV_DIR:-${PROJECT_DIR}/.venv-export}"
if [ ! -d "${EXPORT_VENV}" ]; then
    echo "ERROR: export venv missing at ${EXPORT_VENV}" >&2
    echo "Run first:  bash run/setup_export_env.sh" >&2
    exit 2
fi
# shellcheck disable=SC1091
source "${EXPORT_VENV}/bin/activate"
echo "[run] Export venv: $(command -v python) ($(python --version 2>&1))"

: "${MODEL:?MODEL env var required (e.g. mobilenetv4_conv_medium)}"
: "${CKPT:?CKPT env var required (path to best_model.pth)}"
BACKEND="${BACKEND:-xnnpack}"
OUT="${OUT:-exports/executorch/${MODEL}.pte}"

if [ ! -s "${CKPT}" ]; then
    echo "[run] ERROR: checkpoint not found or empty: ${CKPT}" >&2
    exit 2
fi

mkdir -p "$(dirname "${OUT}")"
echo "[run] ExecuTorch export ${MODEL} (backend=${BACKEND}) from ${CKPT} -> ${OUT}"
python scripts/export_executorch.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --backend "${BACKEND}" \
    --output "${OUT}"

echo "[run] DONE"
