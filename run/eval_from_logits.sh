#!/usr/bin/env bash
# ============================================================================
# Score a logits CSV against the bundle manifest -> metrics.json + table.md.
# The SHARED scorer: running it on both arms is what makes the two tables
# structurally identical (docs/MOBILE_EVAL_PIPELINE.md §6). CPU-only.
#
# Args (KEY=VALUE):
#   BUNDLE    bundle dir                 (default data/mobile_eval_bundle)
#   LOGITS    sample_id,logit,error CSV  [required unless COMPARE]
#   VALPRED   val_predictions.csv of the same run/fold -> frozen Youden threshold
#   THRESH    explicit threshold (skips VALPRED)
#   LABEL     arm tag: server | mobile | host-executorch   (default arm)
#   RUNTIME   e.g. pytorch-eager | executorch-1.4.0
#   DEVICE    e.g. cpu | "Pixel 6a (Tensor G1)"
#   OUTDIR    output dir                 [required]
#   COMPARE   "a/metrics.json b/metrics.json" -> comparison.md instead
#
# Usage:
#   bash run/eval_from_logits.sh LOGITS=reports/mobile_eval/server_logits.csv \
#        VALPRED=experiments/runs_newsplit_ddi/kd_.../fold_4/val_predictions.csv \
#        LABEL=server RUNTIME=pytorch-eager DEVICE=cpu \
#        OUTDIR=reports/mobile_eval/server
#
#   bash run/eval_from_logits.sh OUTDIR=reports/mobile_eval \
#        COMPARE="reports/mobile_eval/server/metrics.json reports/mobile_eval/mobile/metrics.json"
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "eval_from_logits"
activate_venv
export CUDA_VISIBLE_DEVICES=""          # metrics only, no model is loaded

BUNDLE="${BUNDLE:-data/mobile_eval_bundle}"
: "${OUTDIR:?OUTDIR env var required}"

if [ -n "${COMPARE:-}" ]; then
    # shellcheck disable=SC2086
    python scripts/eval_from_logits.py --compare ${COMPARE} --out-dir "${OUTDIR}"
    exit 0
fi

: "${LOGITS:?LOGITS env var required (or pass COMPARE)}"
ARGS=(--manifest "${BUNDLE}/manifest.csv" --logits "${LOGITS}" --out-dir "${OUTDIR}"
      --label "${LABEL:-arm}" --batch-size "${BATCH:-1}")
if [ -n "${VALPRED:-}" ]; then ARGS+=(--threshold-from "${VALPRED}"); fi
if [ -n "${THRESH:-}" ];  then ARGS+=(--threshold "${THRESH}"); fi
if [ -n "${RUNTIME:-}" ]; then ARGS+=(--runtime "${RUNTIME}"); fi
if [ -n "${DEVICE:-}" ];  then ARGS+=(--device "${DEVICE}"); fi

if [ -z "${VALPRED:-}" ] && [ -z "${THRESH:-}" ]; then
    echo "[run] ERROR: pass VALPRED (preferred) or THRESH." >&2; exit 2
fi

python scripts/eval_from_logits.py "${ARGS[@]}"
