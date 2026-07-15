#!/usr/bin/env bash
# ============================================================================
# Aggregate the 5 fold_*/test_metrics.json under a run dir into mean ± std.
# Non-Slurm analogue of slurm/22_aggregate_folds.slurm — CPU-only.
#
# Usage:  bash run/aggregate.sh RUN_DIR=experiments/runs/teacher/efficientnetv2_m
# Output: <RUN_DIR>/aggregated.json  +  <RUN_DIR>/aggregated.md
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "aggregate"
activate_venv

: "${RUN_DIR:?RUN_DIR env var required, e.g. RUN_DIR=experiments/runs/teacher/efficientnetv2_m}"
echo "[run] Aggregating folds under ${RUN_DIR}"
python scripts/aggregate_folds.py --run-dir "${RUN_DIR}"
echo "[run] DONE"
