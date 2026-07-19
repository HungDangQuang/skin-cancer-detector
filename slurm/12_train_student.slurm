#!/bin/bash
# ============================================================================
# Step 3 (FULL) — train ONE student across all 5 CV folds in a SINGLE job.
# The 5 folds run sequentially inside this one job (no Slurm array), so one
# model = one job. Pass STUDENT, TEACHER and (optionally) TRAINING via env vars.
# The KD student distills from experiments/runs/teacher/${TEACHER}/fold_${FOLD}/...
# so TEACHER must already be trained (11_train_teacher with the same TEACHER).
#
# Prereq:  11_train_teacher finished (all 5 folds) for the chosen TEACHER.
# Submit (baseline backbones, default teacher efficientnetv2_m):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2
# Submit (SOTA student distilled from a SOTA teacher):
#   bash slurm/submit.sh slurm/12_train_student.slurm \
#       STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m
#   STUDENT in {mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2, repvit_m1_0}
#   TEACHER in {efficientnetv2_m, convnextv2_base}   (maxvit_base retired from the KD matrix — see docs/SOTA_MODEL_DECISION_2026-07.md)
# Subset of folds (split a heavy run under the 72 h cap into two jobs):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TEACHER=maxvit_base FOLDS="0 1 2"
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TEACHER=maxvit_base FOLDS="3 4"
#
# Controlled comparison (no KD — works since 2026-06-04 via the use_kd flag):
#   bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium TRAINING=baseline
#
# Privileged (LUPI) teacher (direction A) — student stays image-only, distills the
# teacher's fused (image+tbp_lv_*) structure via RKD. Needs the privileged teacher
# already trained (11_train_teacher ... PRIVILEGED=1) and prepare run with the SAME
# META_COLS:
#   bash slurm/submit.sh slurm/12_train_student.slurm \
#       STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m_privileged \
#       TRAINING=distillation_privileged PRIVILEGED=1 \
#       META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
#   Output run-dir: experiments/runs/kd_efficientnetv2_m_privileged_to_<student>/
#   (compare against the plain kd_efficientnetv2_m_to_<student> — the ablation).
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

STUDENT="${STUDENT:-mobilenetv4_conv_medium}"
TEACHER="${TEACHER:-efficientnetv2_m}"
TRAINING="${TRAINING:-distillation}"
FOLDS="${FOLDS:-0 1 2 3 4}"
# Anti-overfit knobs (single-token → safe through submit.sh --export). Defaults
# reproduce the original behavior (augmentation=light, drop_path_rate=0.0).
#   AUG=heavy DROP_PATH=0.1   → stronger aug + stochastic depth on the student.
AUG="${AUG:-light}"
DROP_PATH="${DROP_PATH:-0.0}"
# Extra Hydra overrides (space-separated), passed verbatim — e.g. when the
# teacher is maxvit_base: EXTRA="cudnn_deterministic=false".
# Deliberately UNquoted at the call site so multiple overrides word-split.
EXTRA="${EXTRA:-}"
# Privileged (LUPI) teacher (direction A): PRIVILEGED=1 feeds metadata into the
# frozen teacher (student stays image-only). Requires TEACHER=<name>_privileged,
# TRAINING=distillation_privileged, and prepare run with the same META_COLS.
# META_COLS must be comma-separated with NO spaces (word-split safe).
PRIVILEGED="${PRIVILEGED:-0}"
META_COLS="${META_COLS:-tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color,tbp_lv_areaMM2,tbp_lv_eccentricity,tbp_lv_deltaLBnorm}"
PRIV_ARGS=""
if [ "${PRIVILEGED}" = "1" ]; then
    PRIV_ARGS="data.metadata_as_input=true data.metadata_cols=[${META_COLS}]"
fi
echo "[job] Student: ${STUDENT} | Teacher: ${TEACHER} | Training: ${TRAINING} | folds ${FOLDS} | aug=${AUG} drop_path=${DROP_PATH} | privileged=${PRIVILEGED} | extra='${EXTRA}'"
nvidia-smi || true
# noglob so the unquoted ${PRIV_ARGS} 'data.metadata_cols=[...]' bracket token
# is passed to Hydra verbatim (word-split on spaces, never pathname-expanded).
set -f
for FOLD in ${FOLDS}; do
    echo "[job] === ${TRAINING}: ${TEACHER} -> ${STUDENT} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_student.py "student=${STUDENT}" "teacher=${TEACHER}" "training=${TRAINING}" "data.fold=${FOLD}" "augmentation=${AUG}" "student.drop_path_rate=${DROP_PATH}" ${PRIV_ARGS} ${EXTRA}
done
set +f

echo "[job] DONE"
