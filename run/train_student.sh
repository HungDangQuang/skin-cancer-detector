#!/usr/bin/env bash
# ============================================================================
# Train ONE student across all 5 CV folds, sequentially, in one process.
# Non-Slurm analogue of slurm/12_train_student.slurm.
#
# The KD student distills from experiments/runs/teacher/${TEACHER}/fold_${FOLD}/,
# so that TEACHER must already be trained (run/train_teacher.sh with the same TEACHER).
#
# Args are KEY=VALUE (slurm-wrapper style) OR env vars:
#   STUDENT    student backbone (default mobilenetv4_conv_medium)
#              choices: mobilenetv4_conv_medium | fastvit_sa12 | efficientformerv2_s2 | repvit_m1_0
#   TEACHER    teacher to distill from (default efficientnetv2_m)
#   TRAINING   distillation | distillation_rkd | baseline    (default distillation; baseline = no KD)
#   FOLDS      space-separated fold list  (default "0 1 2 3 4")
#   AUG        light | heavy              (default light)
#   DROP_PATH  stochastic depth rate      (default 0.0)
#   GPU        physical GPU id / "auto" / "cpu"  (default auto)
#   EXTRA      extra Hydra overrides, verbatim (e.g. EXTRA="cudnn_deterministic=false")
#
# Examples:
#   bash run/train_student.sh STUDENT=fastvit_sa12
#   bash run/train_student.sh STUDENT=mobilenetv4_conv_medium TEACHER=convnextv2_base
#   bash run/train_student.sh STUDENT=efficientformerv2_s2 TRAINING=baseline    # no-KD control
#   # privileged (LUPI) teacher (direction A) — student stays image-only, distills
#   # the fused (image+tbp_lv_*) structure via RKD. Needs the privileged teacher
#   # already trained and prepare run with the SAME META_COLS:
#   bash run/train_student.sh STUDENT=mobilenetv4_conv_medium \
#        TEACHER=efficientnetv2_m_privileged TRAINING=distillation_privileged PRIVILEGED=1 \
#        META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
#
# Output: experiments/runs/kd_<teacher>_to_<student>/fold_{0..4}/   (or baseline_* dirs)
# Aggregate after all folds finish:
#   bash run/aggregate.sh RUN_DIR=experiments/runs/kd_${TEACHER}_to_${STUDENT}
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "train_student"
activate_venv
select_gpu

STUDENT="${STUDENT:-mobilenetv4_conv_medium}"
TEACHER="${TEACHER:-efficientnetv2_m}"
TRAINING="${TRAINING:-distillation}"
FOLDS="${FOLDS:-0 1 2 3 4}"
AUG="${AUG:-light}"
DROP_PATH="${DROP_PATH:-0.0}"
EXTRA="${EXTRA:-}"
DEVICE_OVERRIDE=""
[ "${GPU:-auto}" = "cpu" ] && DEVICE_OVERRIDE="device=cpu"
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

echo "[run] Student ${STUDENT} | Teacher ${TEACHER} | ${TRAINING} | folds ${FOLDS} | aug=${AUG} drop_path=${DROP_PATH} | privileged=${PRIVILEGED} | extra='${EXTRA}'"
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true

# noglob so the unquoted ${PRIV_ARGS} 'data.metadata_cols=[...]' bracket token is
# passed to Hydra verbatim (word-split on spaces, never pathname-expanded).
set -f
for FOLD in ${FOLDS}; do
    echo "[run] === ${TRAINING}: ${TEACHER} -> ${STUDENT} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_student.py \
        "student=${STUDENT}" \
        "teacher=${TEACHER}" \
        "training=${TRAINING}" \
        "data.fold=${FOLD}" \
        "augmentation=${AUG}" \
        "student.drop_path_rate=${DROP_PATH}" \
        ${DEVICE_OVERRIDE} ${PRIV_ARGS} ${EXTRA}
done
set +f

echo "[run] DONE"
