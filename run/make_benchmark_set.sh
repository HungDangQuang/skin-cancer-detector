#!/usr/bin/env bash
# ============================================================================
# Build the FIXED benchmark input set from the internal held-out test split.
# CPU-only (~100 images). The output is reused for the PC + mobile latency
# benchmarks and the PC<->mobile numerical parity check, so both sides must see
# the SAME images in the SAME order.
#
# Args are KEY=VALUE OR env vars:
#   N       number of images                  (default 100)
#   OUTDIR  output directory                  (default data/benchmark_set)
#   MODEL   model name — optional, dumps reference logits
#   CKPT    checkpoint — optional, must be passed together with MODEL
#
# Usage:
#   bash run/make_benchmark_set.sh N=100
#   # also dump per-model reference logits for the parity check:
#   bash run/make_benchmark_set.sh N=100 MODEL=mobilenetv4_conv_medium \
#        CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
#
# Output: data/benchmark_set/  (copy to the Mac/phone; do NOT commit)
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "make_benchmark_set"
activate_venv
# Reference logits (if requested) run on CPU — ~100 images is trivial, and this
# keeps the job runnable while a training process owns the GPU.
export CUDA_VISIBLE_DEVICES=""

N="${N:-100}"
OUTDIR="${OUTDIR:-data/benchmark_set}"

ARGS=(--n "${N}" --output-dir "${OUTDIR}")
# MODEL + CKPT are optional; pass both or neither.
if [ -n "${MODEL:-}" ] && [ -n "${CKPT:-}" ]; then
    ARGS+=(--model-name "${MODEL}" --checkpoint "${CKPT}")
elif [ -n "${MODEL:-}" ] || [ -n "${CKPT:-}" ]; then
    echo "[run] ERROR: pass BOTH MODEL and CKPT (or neither) to dump reference logits." >&2
    exit 2
fi

echo "[run] Building benchmark set (N=${N}) -> ${OUTDIR}"
python scripts/make_benchmark_set.py "${ARGS[@]}"

echo "[run] DONE"
