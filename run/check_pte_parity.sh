#!/usr/bin/env bash
# ============================================================================
# PC<->.pte numerical parity check (parity layer 1). CPU-only.
#
# Feeds the fixed benchmark set's fully-preprocessed inputs through the exported
# ExecuTorch program and compares the logits against the PyTorch reference
# (ref_<MODEL>.csv). Gate before ANY on-device number is reported: a .pte that
# computes different logits is a different model.
#
# Uses the ISOLATED export venv (./.venv-export) — deliberately NOT the training
# venv (activate_venv from common.sh), same as run/export_executorch.sh.
#
# Prereqs (in this order):
#   bash run/setup_export_env.sh
#   bash run/make_benchmark_set.sh N=100 MODEL=<m> CKPT=<ckpt>   # ref logits
#   bash run/export_executorch.sh  MODEL=<m> CKPT=<ckpt>         # the .pte
# The CKPT must be the SAME checkpoint in both — otherwise the check compares
# two different models and "fails parity" for the wrong reason.
#
# Args are KEY=VALUE OR env vars:
#   MODEL      model name (must match MODEL_REGISTRY)      [required]
#   PTE        .pte path        (default exports/executorch/${MODEL}.pte)
#   BENCH_DIR  benchmark set    (default data/benchmark_set)
#   TOL        max |dlogit|     (default 1e-3)
#   OUT        JSON report      (default reports/mobile_benchmark/parity_${MODEL}.json)
#   EXPORT_VENV_DIR  override the export venv (default ./.venv-export)
#
# Usage:
#   bash run/check_pte_parity.sh MODEL=mobilenetv4_conv_medium
#
# Exit codes: 0 = parity holds, 1 = parity FAILED, 2 = setup problem.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "check_pte_parity"
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
PTE="${PTE:-exports/executorch/${MODEL}.pte}"
BENCH_DIR="${BENCH_DIR:-data/benchmark_set}"
TOL="${TOL:-1e-3}"
OUT="${OUT:-reports/mobile_benchmark/parity_${MODEL}.json}"

if [ ! -s "${PTE}" ]; then
    echo "[run] ERROR: .pte not found or empty: ${PTE}" >&2
    echo "       Run first: bash run/export_executorch.sh MODEL=${MODEL} CKPT=..." >&2
    exit 2
fi
if [ ! -s "${BENCH_DIR}/ref_${MODEL}.csv" ]; then
    echo "[run] ERROR: reference logits missing: ${BENCH_DIR}/ref_${MODEL}.csv" >&2
    echo "       Run first: bash run/make_benchmark_set.sh N=100 MODEL=${MODEL} CKPT=..." >&2
    exit 2
fi

mkdir -p "$(dirname "${OUT}")"
echo "[run] Parity check ${MODEL} | pte=${PTE} bench=${BENCH_DIR} tol=${TOL}"
python scripts/check_pte_parity.py \
    --model-name "${MODEL}" \
    --pte "${PTE}" \
    --benchmark-dir "${BENCH_DIR}" \
    --tolerance "${TOL}" \
    --output "${OUT}"

echo "[run] DONE"
