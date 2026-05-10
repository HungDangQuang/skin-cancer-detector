#!/bin/bash
# ============================================================================
# Step 3 (FULL) — KD-train one student.
# Pass STUDENT and (optionally) TRAINING via env vars.
#
# Prereq:  11_train_teacher finished.
# Submit:
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s
#
# Controlled comparison (no KD):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0 TRAINING=baseline
# ============================================================================
#SBATCH --job-name=train_student
#SBATCH --output=logs/train_student_%j.out
#SBATCH --error=logs/train_student_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=mps:l40:4
#SBATCH --mem=16G
#SBATCH --time=18:00:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 18432      # teacher (frozen) + student + grads, batch 64
setup_mps

STUDENT="${STUDENT:-efficientnet_b0}"
TRAINING="${TRAINING:-distillation}"
echo "[job] Student: ${STUDENT} | Training mode: ${TRAINING}"
nvidia-smi || true
python scripts/train_student.py student="${STUDENT}" training="${TRAINING}"

echo "[job] DONE"
