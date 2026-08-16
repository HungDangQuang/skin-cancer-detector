#!/usr/bin/env bash
# ============================================================================
# Ablation B — PAD-UFES-20 mixing (data-strategy proof).
# Trains with vs without PAD in the TRAIN+VAL data, on the IDENTICAL held-out
# combined test, to prove (or refute) that adding PAD smartphone images improves
# performance — especially on the PAD (smartphone) portion of the test.
#
# WHY BASELINE (no KD) BY DEFAULT: a KD teacher trained on ISIC+PAD would leak
# PAD knowledge into the "ISIC-only" arm via soft labels, contaminating the
# comparison. Baseline (focal loss, no teacher) isolates the single variable =
# whether PAD is in the training data. (KD is ablated separately.) If you DO run
# KD here, train a matched ISIC-only teacher first or the result is confounded.
#
# The held-out TEST is left fully combined (ISIC+PAD) for BOTH arms; its PAD
# portion is never trained on by either arm. Per-domain numbers come from the
# `source` column in predictions.csv — analyze with scripts/analyze_pad_ablation.py.
#
# ARM selects training data + a distinct run-dir suffix:
#   ARM=isic_only -> data.train_sources=[isic2024]   (PAD removed from train+val)
#   ARM=isic_pad  -> all sources (PAD kept)           (the current strategy)
#
# Args are KEY=VALUE OR env vars:
#   ARM       isic_only | isic_pad             (default isic_pad)
#   MODEL_KIND student | teacher               (default student)
#   STUDENT   student backbone                 (default mobilenetv4_conv_medium)
#   TEACHER   teacher backbone (MODEL_KIND=teacher) (default efficientnetv2_m)
#   TRAINING  baseline | distillation          (default baseline — see note above)
#   FOLDS     space-separated fold list        (default "0 1 2 3 4")
#   GPU       physical GPU id / "auto" / "cpu" (default auto)
#   EXTRA     extra Hydra overrides, verbatim
#
# Usage (run both arms, each = 5 folds sequential):
#   bash run/ablation_pad.sh ARM=isic_only
#   bash run/ablation_pad.sh ARM=isic_pad
#   bash run/ablation_pad.sh ARM=isic_only MODEL_KIND=teacher TEACHER=convnextv2_base
#
# Output:
#   student arm -> experiments/runs/baseline_<student>__train_<arm>/fold_{0..4}/
#   teacher arm -> experiments/runs_isic_only/teacher/<teacher>/fold_{0..4}/   (isic_only)
#                  experiments/runs/teacher/<teacher>/fold_{0..4}/             (isic_pad = the main run)
#   each with test_metrics.json (combined test; incl. auprc + sens_at_*spec)
#             + predictions.csv (y_true,y_prob,y_pred,source  <- per-domain)
# Aggregate each arm, then compare ISIC-only vs ISIC+PAD (focus: PAD-source rows):
#   bash run/aggregate.sh \
#       RUN_DIR=experiments/runs/baseline_mobilenetv4_conv_medium__train_isic_only
#   python scripts/analyze_pad_ablation.py --help
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "ablation_pad"
activate_venv
select_gpu

MODEL_KIND="${MODEL_KIND:-student}"
STUDENT="${STUDENT:-mobilenetv4_conv_medium}"
TEACHER="${TEACHER:-efficientnetv2_m}"
TRAINING="${TRAINING:-baseline}"
ARM="${ARM:-isic_pad}"
FOLDS="${FOLDS:-0 1 2 3 4}"
EXTRA="${EXTRA:-}"
DEVICE_OVERRIDE=""
[ "${GPU:-auto}" = "cpu" ] && DEVICE_OVERRIDE="device=cpu"

# Map ARM -> train-source override + an isolation knob per model kind.
#
# NOTE the asymmetry: scripts/train_student.py honours `run_suffix`
# (train_student.py:71/93) but scripts/train_teacher.py does NOT — its run_dir is
# hard-wired to <output_dir>/teacher/<name>/fold_N (train_teacher.py:39). So the
# teacher arm must be isolated with `output_dir=` instead, or it would silently
# OVERWRITE the main teacher run. That is why the trained ISIC-only teachers live
# under experiments/runs_isic_only/ rather than a __train_isic_only suffix.
case "${ARM}" in
  isic_only) ARM_OVERRIDES="data.train_sources=[isic2024]"; SUFFIX="__train_isic_only"; TEACHER_OUT="experiments/runs_isic_only" ;;
  isic_pad)  ARM_OVERRIDES="data.train_sources=null";       SUFFIX="__train_isic_pad";  TEACHER_OUT="experiments/runs" ;;
  *)         echo "[run] ERROR: unknown ARM='${ARM}' (use isic_only|isic_pad)" >&2; exit 2 ;;
esac

echo "[run] Ablation PAD | kind=${MODEL_KIND} student=${STUDENT} teacher=${TEACHER} training=${TRAINING} ARM=${ARM} (${SUFFIX}) | folds ${FOLDS}"
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true

# noglob so the 'data.train_sources=[isic2024]' bracket token reaches Hydra verbatim.
set -f
for FOLD in ${FOLDS}; do
    echo "[run] === PAD arm ${ARM} | fold ${FOLD} (start $(date '+%F %T')) ==="
    if [ "${MODEL_KIND}" = "teacher" ]; then
        python scripts/train_teacher.py \
            "teacher=${TEACHER}" \
            "data.fold=${FOLD}" "${ARM_OVERRIDES}" "output_dir=${TEACHER_OUT}" \
            ${DEVICE_OVERRIDE} ${EXTRA}
    else
        python scripts/train_student.py \
            "student=${STUDENT}" "training=${TRAINING}" \
            "data.fold=${FOLD}" "${ARM_OVERRIDES}" "run_suffix=${SUFFIX}" \
            ${DEVICE_OVERRIDE} ${EXTRA}
    fi
done
set +f

echo "[run] DONE"
