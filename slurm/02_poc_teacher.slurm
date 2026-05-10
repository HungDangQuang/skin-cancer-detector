#!/bin/bash
# ============================================================================
# Step 2 (POC) — train teacher (EfficientNet-B4) for 2 epochs on synthetic data.
# Prereq:  Step 1 completed (data/splits/poc/ exists).
# Submit:  bash slurm/submit.sh slurm/02_poc_teacher.slurm
# Output:  experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth
# ============================================================================
#SBATCH --job-name=poc_teacher
#SBATCH --output=logs/poc_teacher_%j.out
#SBATCH --error=logs/poc_teacher_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:l40:2
#SBATCH --mem=8G
#SBATCH --time=01:00:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 8192     # 8 GB: B4 + batch 16 @ 224
setup_mps

echo "[job] GPU info"
nvidia-smi || true

echo "[job] Training POC teacher"
python scripts/train_teacher.py --config-name config_poc

echo "[job] DONE"
