#!/usr/bin/env bash
# ============================================================================
# Train ONE teacher across all 5 CV folds, sequentially, in one process.
# Non-Slurm analogue of slurm/11_train_teacher.slurm.
#
# Args are KEY=VALUE (same style as the slurm submit wrapper) OR env vars:
#   TEACHER    teacher backbone (default efficientnetv2_m)
#              choices: efficientnetv2_m | convnextv2_base | maxvit_base | panderm
#              (panderm needs the PanDerm checkpoint — pass it via EXTRA, see below)
#   FOLDS      space-separated fold list (default "0 1 2 3 4")
#   AUG        light | heavy                (default light)
#   DROP_PATH  stochastic depth rate        (default 0.0)
#   GPU        physical GPU id / "auto" / "cpu"  (default auto — freest GPU)
#   EXTRA      extra Hydra overrides, space-separated & verbatim, e.g.
#              EXTRA="cudnn_deterministic=false training.batch_size=16"
#
# Examples:
#   bash run/train_teacher.sh                                   # efficientnetv2_m, all folds
#   bash run/train_teacher.sh TEACHER=convnextv2_base
#   bash run/train_teacher.sh TEACHER=maxvit_base GPU=1 FOLDS="0 1 2" \
#        EXTRA="cudnn_deterministic=false training.batch_size=16"
#   bash run/train_teacher.sh TEACHER=panderm \
#        EXTRA="teacher.weights_path=/abs/path/panderm_bb_data6_checkpoint-499.pth"
#   # privileged (LUPI) teacher (direction A) — needs prepare run with the SAME
#   # META_COLS and a *_privileged teacher name:
#   bash run/train_teacher.sh TEACHER=efficientnetv2_m_privileged PRIVILEGED=1 \
#        META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
#
# Output: experiments/runs/teacher/${TEACHER}/fold_{0..4}/
# Aggregate after all folds finish:
#   bash run/aggregate.sh RUN_DIR=experiments/runs/teacher/${TEACHER}
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
# Accept KEY=VALUE positional args (export them so the defaults below pick up).
for arg in "$@"; do export "${arg?}"; done

start_log "train_teacher"
activate_venv
select_gpu

TEACHER="${TEACHER:-efficientnetv2_m}"
FOLDS="${FOLDS:-0 1 2 3 4}"
AUG="${AUG:-light}"
DROP_PATH="${DROP_PATH:-0.0}"
EXTRA="${EXTRA:-}"
DEVICE_OVERRIDE=""
[ "${GPU:-auto}" = "cpu" ] && DEVICE_OVERRIDE="device=cpu"
# Privileged (LUPI) teacher (direction A): PRIVILEGED=1 feeds metadata into the
# teacher (requires TEACHER=<name>_privileged and prepare run with the same
# META_COLS). META_COLS must be comma-separated with NO spaces (word-split safe).
PRIVILEGED="${PRIVILEGED:-0}"
META_COLS="${META_COLS:-tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color,tbp_lv_areaMM2,tbp_lv_eccentricity,tbp_lv_deltaLBnorm}"
PRIV_ARGS=""
if [ "${PRIVILEGED}" = "1" ]; then
    PRIV_ARGS="data.metadata_as_input=true data.metadata_cols=[${META_COLS}]"
fi

echo "[run] Teacher ${TEACHER} | folds ${FOLDS} | aug=${AUG} drop_path=${DROP_PATH} | privileged=${PRIVILEGED} | extra='${EXTRA}'"
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true

# noglob so the unquoted ${PRIV_ARGS} 'data.metadata_cols=[...]' bracket token is
# passed to Hydra verbatim (word-split on spaces, never pathname-expanded).
set -f
for FOLD in ${FOLDS}; do
    echo "[run] === teacher ${TEACHER} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_teacher.py \
        "teacher=${TEACHER}" \
        "data.fold=${FOLD}" \
        "augmentation=${AUG}" \
        "teacher.drop_path_rate=${DROP_PATH}" \
        ${DEVICE_OVERRIDE} ${PRIV_ARGS} ${EXTRA}
done
set +f

echo "[run] DONE"
