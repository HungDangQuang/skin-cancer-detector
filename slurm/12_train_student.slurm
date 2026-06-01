#!/bin/bash
# ============================================================================
# Step 3 (FULL) — KD-train one student across 5 CV folds (Slurm array).
# Pass STUDENT and (optionally) TRAINING via env vars.
#
# Prereq:  11_train_teacher finished (all 5 folds).
# Submit:
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s
#
# Controlled comparison (no KD; currently broken — see CLAUDE.md gotcha
# "Baseline (no-KD) student training is broken"):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0 TRAINING=baseline
#
# Output: experiments/runs/kd_<teacher>_to_<student>/fold_${SLURM_ARRAY_TASK_ID}/
#         ├── checkpoints/best_model.pth
#         └── test_metrics.json
# Aggregate after all 5 folds finish:
#   bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#       RUN_DIR=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0
# ============================================================================
#SBATCH --job-name=train_student
#SBATCH --output=logs/train_student_%A_%a.out
#SBATCH --error=logs/train_student_%A_%a.err
#SBATCH --array=0-4%2
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
FOLD="${SLURM_ARRAY_TASK_ID:-0}"
echo "[job] Student: ${STUDENT} | Training mode: ${TRAINING} | fold ${FOLD}"
nvidia-smi || true
python scripts/train_student.py "student=${STUDENT}" "training=${TRAINING}" "data.fold=${FOLD}"

echo "[job] DONE"
