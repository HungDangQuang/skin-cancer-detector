#!/bin/bash
# ============================================================================
# Aggregate 5-fold CV results into mean ± std (CPU-only, ~10 seconds).
#
# Run AFTER the per-fold training array completes (all 5 fold_*/test_metrics.json
# must exist).
#
# Submit:
#   bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#       RUN_DIR=experiments/runs/teacher/efficientnet_b4
#   bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#       RUN_DIR=experiments/runs/kd_efficientnet_b4_to_mobilevit_s
#
# Outputs (in RUN_DIR):
#   aggregated.json   — mean/std/min/max/per-fold for each metric
#   aggregated.md     — short markdown table for thesis use
# ============================================================================
#SBATCH --job-name=aggregate_folds
#SBATCH --output=logs/aggregate_folds_%j.out
#SBATCH --error=logs/aggregate_folds_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
# No GPU needed — aggregation is pure JSON arithmetic.

: "${RUN_DIR:?RUN_DIR env var required, e.g. RUN_DIR=experiments/runs/teacher/efficientnet_b4}"

echo "[job] Aggregating folds under ${RUN_DIR}"
python scripts/aggregate_folds.py --run-dir "${RUN_DIR}"

echo "[job] DONE"
