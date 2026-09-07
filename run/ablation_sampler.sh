#!/usr/bin/env bash
# ============================================================================
# Ablation A — imbalance-SAMPLING strategy (data-strategy proof).
# Re-trains the BEST student (KD: efficientnetv2_m -> mobilenetv4_conv_medium)
# varying ONLY the DynamicUndersampledSampler, holding teacher/seed/folds/
# hparams/loss fixed. Isolates the sampler's contribution so we can prove (or
# refute) that 1:5 dynamic undersampling beats its alternatives.
#
# The teacher is REUSED (frozen soft-label source, NOT retrained) from
# experiments/runs/teacher/${TEACHER}/fold_${FOLD}/checkpoints/best_model.pth,
# so run/train_teacher.sh must already be done. run_suffix forks each arm into
# its own run-dir subtree so the main runs are never overwritten.
#
# SAMP selects the arm -> (sampler overrides + distinct run-dir suffix):
#   SAMP=off  -> data.use_weighted_sampler=false   (no resampling; natural ~1018:1)
#   SAMP=3    -> 1:3 malignant:benign
#   SAMP=10   -> 1:10
#   SAMP=5    == the MAIN run (kd_..._to_mobilenetv4_conv_medium); already trained.
#               Re-run only if you want a __ratio5 copy; otherwise reuse the main.
#
# Args are KEY=VALUE OR env vars:
#   SAMP     off | 3 | 5 | 10                 (default off)
#   STUDENT  student backbone                 (default mobilenetv4_conv_medium)
#   TEACHER  frozen teacher                   (default efficientnetv2_m)
#   FOLDS    space-separated fold list        (default "0 1 2 3 4")
#   GPU      physical GPU id / "auto" / "cpu" (default auto)
#   EXTRA    extra Hydra overrides, verbatim
#
# Usage (one arm = all 5 folds, sequential):
#   bash run/ablation_sampler.sh SAMP=off
#   bash run/ablation_sampler.sh SAMP=3
#   bash run/ablation_sampler.sh SAMP=10
#
# Output: experiments/runs/kd_<teacher>_to_<student>__<suffix>/fold_{0..4}/
#           ├── checkpoints/best_model.pth
#           ├── test_metrics.json   (incl. auprc + sens_at_90/95spec)
#           └── predictions.csv     (y_true,y_prob,y_pred,source)
# Aggregate each arm, then compare to the main ratio-5 run:
#   bash run/aggregate.sh \
#       RUN_DIR=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__samp_off
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "ablation_sampler"
activate_venv
select_gpu

STUDENT="${STUDENT:-mobilenetv4_conv_medium}"
TEACHER="${TEACHER:-efficientnetv2_m}"
SAMP="${SAMP:-off}"
FOLDS="${FOLDS:-0 1 2 3 4}"
EXTRA="${EXTRA:-}"
DEVICE_OVERRIDE=""
[ "${GPU:-auto}" = "cpu" ] && DEVICE_OVERRIDE="device=cpu"

# Map SAMP -> sampler overrides + run-dir suffix (keeps each arm isolated on disk).
case "${SAMP}" in
  off) SAMP_OVERRIDES="data.use_weighted_sampler=false"; SUFFIX="__samp_off" ;;
  3)   SAMP_OVERRIDES="data.use_weighted_sampler=true data.undersample_ratio=3";  SUFFIX="__ratio3" ;;
  5)   SAMP_OVERRIDES="data.use_weighted_sampler=true data.undersample_ratio=5";  SUFFIX="__ratio5" ;;
  10)  SAMP_OVERRIDES="data.use_weighted_sampler=true data.undersample_ratio=10"; SUFFIX="__ratio10" ;;
  *)   echo "[run] ERROR: unknown SAMP='${SAMP}' (use off|3|5|10)" >&2; exit 2 ;;
esac

echo "[run] Ablation sampler | student=${STUDENT} teacher=${TEACHER} SAMP=${SAMP} (${SUFFIX}) | folds ${FOLDS}"
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || true

# ${SAMP_OVERRIDES} is intentionally unquoted: it must split into separate Hydra args.
for FOLD in ${FOLDS}; do
    echo "[run] === sampler ${SAMP} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_student.py \
        "student=${STUDENT}" "teacher=${TEACHER}" "training=distillation" \
        "data.fold=${FOLD}" ${SAMP_OVERRIDES} "run_suffix=${SUFFIX}" \
        ${DEVICE_OVERRIDE} ${EXTRA}
done

echo "[run] DONE"
