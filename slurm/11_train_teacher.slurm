#!/bin/bash
# ============================================================================
# Step 2 (FULL) — train teacher EfficientNet-B4 (50 epochs, batch 32).
# Prereq:  10_prepare_data finished.
# Submit:  bash slurm/submit.sh slurm/11_train_teacher.slurm
# Output:  experiments/runs/teacher/efficientnet_b4/checkpoints/best_model.pth
# ============================================================================
#SBATCH --job-name=train_teacher
#SBATCH --output=logs/train_teacher_%j.out
#SBATCH --error=logs/train_teacher_%j.err
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

echo "[job] Training teacher (full)"
nvidia-smi || true
python scripts/train_teacher.py

echo "[job] DONE"
