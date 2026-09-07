#!/usr/bin/env bash
# ============================================================================
# POC smoke test — end-to-end pipeline check on SYNTHETIC data (no ISIC needed).
# Merges the three former POC jobs into one script with a STAGE selector.
#
# Synthetic images carry a learnable color bias (benign=greenish,
# malignant=reddish) so a 2-epoch run should reach AUC > 0.5 — that is the
# signal that data -> model -> loss -> gradients -> metrics all wire up.
#
# Args are KEY=VALUE OR env vars:
#   STAGE    all | prepare | teacher | student   (default all)
#   TEACHER  teacher backbone     (default efficientnetv2_m)
#   STUDENT  student backbone     (default mobilenetv4_conv_medium)
#   GPU      physical GPU id / "auto" / "cpu"    (default auto — freest GPU)
#   EXTRA    extra Hydra overrides, space-separated & verbatim, e.g.
#            EXTRA="cudnn_deterministic=false training.batch_size=8"
#
# Usage:
#   bash run/poc.sh                                     # prepare + teacher + student
#   bash run/poc.sh STAGE=prepare
#   bash run/poc.sh STAGE=teacher TEACHER=convnextv2_base
#   bash run/poc.sh STAGE=student STUDENT=fastvit_sa12 TEACHER=convnextv2_base
#
# Output: data/processed/poc/, data/splits/poc/, experiments/poc/…
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "poc"
activate_venv
select_gpu

STAGE="${STAGE:-all}"
TEACHER="${TEACHER:-efficientnetv2_m}"
STUDENT="${STUDENT:-mobilenetv4_conv_medium}"
EXTRA="${EXTRA:-}"
DEVICE_OVERRIDE=""
[ "${GPU:-auto}" = "cpu" ] && DEVICE_OVERRIDE="device=cpu"

case "${STAGE}" in
  all|prepare|teacher|student) : ;;
  *) echo "[run] ERROR: unknown STAGE='${STAGE}' (use all|prepare|teacher|student)" >&2; exit 2 ;;
esac

command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true

if [ "${STAGE}" = "all" ] || [ "${STAGE}" = "prepare" ]; then
    echo "[run] === POC step 1: generating synthetic data ==="
    python scripts/prepare_poc_data.py
    ls -la data/processed/poc/benign | head -3
    ls -la data/processed/poc/malignant | head -3
    ls -la data/splits/poc/fold_0/
    ls -la data/splits/poc/test_split.csv
fi

if [ "${STAGE}" = "all" ] || [ "${STAGE}" = "teacher" ]; then
    echo "[run] === POC step 2: teacher ${TEACHER} (2 epochs) ==="
    python scripts/train_teacher.py --config-name config_poc \
        "teacher=${TEACHER}" ${DEVICE_OVERRIDE} ${EXTRA}
fi

if [ "${STAGE}" = "all" ] || [ "${STAGE}" = "student" ]; then
    echo "[run] === POC step 3: KD ${TEACHER} -> ${STUDENT} (2 epochs) ==="
    python scripts/train_student.py --config-name config_poc \
        "student=${STUDENT}" "teacher=${TEACHER}" ${DEVICE_OVERRIDE} ${EXTRA}
fi

echo "[run] DONE"
