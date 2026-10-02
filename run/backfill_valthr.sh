#!/usr/bin/env bash
# ============================================================================
# Back-fill the val-frozen threshold metrics (valthr_*) for runs trained before
# 2026-10-02. CPU-only, no inference, never writes inside the run-dirs.
#
# test_metrics*.json's sensitivity/specificity/f1_score/threshold use Youden's
# J fitted on the TEST set (optimistic). This recomputes them per fold at the
# Youden threshold of that fold's own val_predictions*.csv, side by side with
# the test-fitted numbers, split by `source` when predictions carry it.
#
# Args are KEY=VALUE OR env vars:
#   RESULTS_DIR  tree of run-dirs with fold_*/predictions*.csv   [required]
#                (symlinked trees are followed)
#   PRED_NAME    per-fold predictions file   (default predictions.csv;
#                predictions_auprc.csv = the best-by-val-AUPRC checkpoint)
#   VAL_PRED_NAME  threshold source           (default val_${PRED_NAME})
#   OUT_CSV      (default reports/valthr/<RESULTS_DIR basename>[_<tag>].csv)
#   OUT_MD       (default OUT_CSV with .md)
#
# Usage:
#   bash run/backfill_valthr.sh RESULTS_DIR=experiments/runs_newsplit_ddi
#   bash run/backfill_valthr.sh RESULTS_DIR=experiments/runs_newsplit_ddi \
#        PRED_NAME=predictions_auprc.csv
#
# Exit 1 when no fold could be scored. Folds missing VAL_PRED_NAME are listed
# under "Coverage" in the .md — check it before quoting a run.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "backfill_valthr"
activate_venv
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

: "${RESULTS_DIR:?RESULTS_DIR env var required (e.g. experiments/runs_newsplit_ddi)}"
PRED_NAME="${PRED_NAME:-predictions.csv}"
VAL_PRED_NAME="${VAL_PRED_NAME:-val_${PRED_NAME}}"
_tag="${PRED_NAME#predictions}"
_tag="${_tag%.csv}"
OUT_CSV="${OUT_CSV:-reports/valthr/$(basename "${RESULTS_DIR}")${_tag}.csv}"
OUT_MD="${OUT_MD:-${OUT_CSV%.csv}.md}"

if [ ! -d "${RESULTS_DIR}" ]; then
    echo "[run] ERROR: RESULTS_DIR not found: ${RESULTS_DIR}" >&2
    exit 2
fi

echo "[run] valthr back-fill | dir=${RESULTS_DIR} preds=${PRED_NAME} val=${VAL_PRED_NAME} -> ${OUT_CSV}"
python scripts/backfill_valthr.py \
    --results-dir "${RESULTS_DIR}" \
    --pred-name "${PRED_NAME}" \
    --val-pred-name "${VAL_PRED_NAME}" \
    --out-csv "${OUT_CSV}" \
    --out-md "${OUT_MD}"
echo "[run] DONE"
