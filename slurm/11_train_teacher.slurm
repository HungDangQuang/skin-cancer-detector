#!/bin/bash
# ============================================================================
# Step 2 (FULL) — train teacher EfficientNet-B4 (50 epochs, batch 32).
# Runs as a 5-fold Slurm array (folds 0..4, two folds at a time).
# Prereq:  10_prepare_data finished.
# Submit:  bash slurm/submit.sh slurm/11_train_teacher.slurm
# Output:  experiments/runs/teacher/efficientnet_b4/fold_${SLURM_ARRAY_TASK_ID}/
#          ├── checkpoints/best_model.pth
#          └── test_metrics.json
# Aggregate after all 5 folds finish:
#          bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#              RUN_DIR=experiments/runs/teacher/efficientnet_b4
# ============================================================================
#SBATCH --job-name=train_teacher
#SBATCH --output=logs/train_teacher_%A_%a.out
#SBATCH --error=logs/train_teacher_%A_%a.err
#SBATCH --array=0-4%2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=mps:l40:4
#SBATCH --mem=16G
#SBATCH --time=24:00:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 14336      # ~14 GB: B4 + batch 32 + AdamW state
setup_mps

FOLD="${SLURM_ARRAY_TASK_ID:-0}"
echo "[job] Training teacher (full) | fold ${FOLD}"
nvidia-smi || true
python scripts/train_teacher.py "data.fold=${FOLD}"

echo "[job] DONE"
