#!/bin/bash
# ============================================================================
# Step 3 (FULL) — train ONE student across all 5 CV folds in a SINGLE job.
# The 5 folds run sequentially inside this one job (no Slurm array), so one
# model = one job. Pass STUDENT, TEACHER and (optionally) TRAINING via env vars.
# The KD student distills from experiments/runs/teacher/${TEACHER}/fold_${FOLD}/...
# so TEACHER must already be trained (11_train_teacher with the same TEACHER).
#
# Prereq:  11_train_teacher finished (all 5 folds) for the chosen TEACHER.
# Submit (baseline backbones, default teacher efficientnet_b4):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s
# Submit (SOTA student distilled from a SOTA teacher):
#   bash slurm/submit.sh slurm/12_train_student.slurm \
#       STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m
#   STUDENT in {mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2}
#   TEACHER in {efficientnetv2_m, convnextv2_base, maxvit_base}
# Subset of folds (split a heavy run under the 72 h cap into two jobs):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TEACHER=maxvit_base FOLDS="0 1 2"
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TEACHER=maxvit_base FOLDS="3 4"
#
# Controlled comparison (no KD — works since 2026-06-04 via the use_kd flag):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0 TRAINING=baseline
#
# Output: experiments/runs/kd_<teacher>_to_<student>/fold_{0..4}/
#         ├── checkpoints/best_model.pth
#         └── test_metrics.json
# Aggregate after all 5 folds finish:
#   bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#       RUN_DIR=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium
# ============================================================================
#SBATCH --job-name=train_student
#SBATCH --output=logs/train_student_%j.out
#SBATCH --error=logs/train_student_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=mps:l40:4
#SBATCH --mem=16G
#SBATCH --time=72:00:00      # 5 folds run sequentially in one job — use the cap

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 22528      # frozen teacher (up to maxvit_base) + student + grads, batch 64
setup_mps

STUDENT="${STUDENT:-efficientnet_b0}"
TEACHER="${TEACHER:-efficientnet_b4}"
TRAINING="${TRAINING:-distillation}"
FOLDS="${FOLDS:-0 1 2 3 4}"
echo "[job] Student: ${STUDENT} | Teacher: ${TEACHER} | Training mode: ${TRAINING} | folds ${FOLDS}"
nvidia-smi || true
for FOLD in ${FOLDS}; do
    echo "[job] === ${TRAINING}: ${TEACHER} -> ${STUDENT} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_student.py "student=${STUDENT}" "teacher=${TEACHER}" "training=${TRAINING}" "data.fold=${FOLD}"
done

echo "[job] DONE"
