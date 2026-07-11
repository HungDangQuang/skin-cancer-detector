#!/usr/bin/env bash
# ============================================================================
# Train ONE teacher across all 5 CV folds, sequentially, in one process.
# Non-Slurm analogue of slurm/11_train_teacher.slurm.
#
# Args are KEY=VALUE (same style as the slurm submit wrapper) OR env vars:
#   TEACHER    teacher backbone (default efficientnet_b4)
#              SOTA: efficientnetv2_m | convnextv2_base | maxvit_base
#   FOLDS      space-separated fold list (default "0 1 2 3 4")
#   AUG        light | heavy                (default light)
#   DROP_PATH  stochastic depth rate        (default 0.0)
#   GPU        physical GPU id / "auto" / "cpu"  (default auto — freest GPU)
#   EXTRA      extra Hydra overrides, space-separated & verbatim, e.g.
#              EXTRA="cudnn_deterministic=false training.batch_size=16"
#
# Examples:
#   bash run/train_teacher.sh                                   # baseline B4, all folds
#   bash run/train_teacher.sh TEACHER=efficientnetv2_m
#   bash run/train_teacher.sh TEACHER=maxvit_base GPU=1 FOLDS="0 1 2" \
#        EXTRA="cudnn_deterministic=false training.batch_size=16"
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

TEACHER="${TEACHER:-efficientnet_b4}"
FOLDS="${FOLDS:-0 1 2 3 4}"
AUG="${AUG:-light}"
DROP_PATH="${DROP_PATH:-0.0}"
EXTRA="${EXTRA:-}"
DEVICE_OVERRIDE=""
[ "${GPU:-auto}" = "cpu" ] && DEVICE_OVERRIDE="device=cpu"

echo "[run] Teacher ${TEACHER} | folds ${FOLDS} | aug=${AUG} drop_path=${DROP_PATH} | extra='${EXTRA}'"
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true

for FOLD in ${FOLDS}; do
    echo "[run] === teacher ${TEACHER} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_teacher.py \
        "teacher=${TEACHER}" \
        "data.fold=${FOLD}" \
        "augmentation=${AUG}" \
        "teacher.drop_path_rate=${DROP_PATH}" \
        ${DEVICE_OVERRIDE} ${EXTRA}
done

echo "[run] DONE"
