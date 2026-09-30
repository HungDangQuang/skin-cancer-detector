#!/usr/bin/env bash
# ============================================================================
# Benchmark a trained checkpoint. Two modes in one script:
#
#   MOBILE=0 (default) -> scripts/benchmark.py       — FULL computational profile:
#       params, FLOPs, FP32 size, CPU @ batch=1 latency (single-thread,
#       phone-comparable proxy), GPU latency, batch-throughput sweep, percentiles.
#   MOBILE=1           -> scripts/benchmark_mobile.py — the light mobile subset:
#       params + FP32 size + single-core CPU latency only (~1 min, no GPU).
#
# ⚠ CPU latency is a PROXY, not a phone number. Only params / FLOPs / file size
#   transfer across devices; the latency RANKING can flip on a real phone,
#   especially for the transformer students. See docs/MOBILE.md.
#
# Args are KEY=VALUE OR env vars:
#   MODEL        model name (must match MODEL_REGISTRY)   [required]
#   CKPT         path to best_model.pth                   [required]
#   MOBILE       0 | 1                        (default 0 = full profile)
#   DEVICE       auto | cpu | cuda            (default auto; full mode only)
#   BATCH_SIZES  space-separated              (default "1 8 32"; full mode only)
#   OUT          output json  (default reports/{benchmark,mobile_benchmark}/<MODEL>.json)
#   GPU          physical GPU id / "auto" / "cpu"  (default auto)
#
# Usage:
#   bash run/benchmark.sh MODEL=mobilenetv4_conv_medium \
#        CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
#   bash run/benchmark.sh MODEL=... CKPT=... DEVICE=cpu       # skip GPU numbers
#   bash run/benchmark.sh MODEL=... CKPT=... MOBILE=1         # mobile subset only
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "benchmark"
activate_venv

: "${MODEL:?MODEL env var required (e.g. mobilenetv4_conv_medium)}"
: "${CKPT:?CKPT env var required (path to best_model.pth)}"
MOBILE="${MOBILE:-0}"
DEVICE="${DEVICE:-auto}"
BATCH_SIZES="${BATCH_SIZES:-1 8 32}"

if [ ! -s "${CKPT}" ]; then
    echo "[run] ERROR: checkpoint not found or empty: ${CKPT}" >&2
    exit 2
fi

if [ "${MOBILE}" = "1" ]; then
    # Mobile subset is single-core CPU by definition — never touch the GPU.
    export CUDA_VISIBLE_DEVICES=""
    OUT="${OUT:-reports/mobile_benchmark/${MODEL}.json}"
    mkdir -p "$(dirname "${OUT}")"
    echo "[run] Mobile benchmark ${MODEL} from ${CKPT} -> ${OUT}"
    python scripts/benchmark_mobile.py \
        --model-name "${MODEL}" \
        --checkpoint "${CKPT}" \
        --output "${OUT}"
else
    if [ "${DEVICE}" = "cpu" ]; then
        export CUDA_VISIBLE_DEVICES=""
    else
        select_gpu
    fi
    OUT="${OUT:-reports/benchmark/${MODEL}.json}"
    mkdir -p "$(dirname "${OUT}")"
    echo "[run] Full benchmark ${MODEL} from ${CKPT} (device=${DEVICE}) -> ${OUT}"
    # ${BATCH_SIZES} intentionally unquoted: argparse nargs="+" needs separate args.
    python scripts/benchmark.py \
        --model-name "${MODEL}" \
        --checkpoint "${CKPT}" \
        --device "${DEVICE}" \
        --batch-sizes ${BATCH_SIZES} \
        --output "${OUT}"
fi

echo "[run] DONE"
