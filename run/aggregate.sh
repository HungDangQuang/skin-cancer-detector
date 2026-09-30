#!/usr/bin/env bash
# ============================================================================
# Aggregate the 5 fold_*/test_metrics.json under a run dir into mean ± std.
#
# Usage:  bash run/aggregate.sh RUN_DIR=experiments/runs/teacher/efficientnetv2_m
#         bash run/aggregate.sh RUN_DIR=<run> METRICS_NAME=test_metrics_auprc.json
# Output: <RUN_DIR>/aggregated.json  +  <RUN_DIR>/aggregated.md
#         (METRICS_NAME=test_metrics_<m>.json -> aggregated_<m>.{json,md}, the
#          best-by-val-<m> checkpoint of training.callbacks.checkpoint.extra_monitors)
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "aggregate"
activate_venv

: "${RUN_DIR:?RUN_DIR env var required, e.g. RUN_DIR=experiments/runs/teacher/efficientnetv2_m}"
METRICS_NAME="${METRICS_NAME:-test_metrics.json}"
echo "[run] Aggregating fold_*/${METRICS_NAME} under ${RUN_DIR}"
python scripts/aggregate_folds.py --run-dir "${RUN_DIR}" --metrics-name "${METRICS_NAME}"
echo "[run] DONE"
