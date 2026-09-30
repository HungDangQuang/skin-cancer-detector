#!/usr/bin/env bash
# ============================================================================
# Export a trained checkpoint to ONNX or TorchScript. CPU-ONLY —
# torch.onnx.export / torch.jit.script trace a dummy CPU forward, no CUDA
# needed, so this stays runnable while a training process owns the GPU.
#
# Args are KEY=VALUE OR env vars:
#   MODEL   model name (must match MODEL_REGISTRY)   [required]
#   CKPT    path to best_model.pth                   [required]
#   FORMAT  onnx | torchscript        (default onnx)
#   OUT     output path w/o extension (default exports/${MODEL})
#   CONFIG  config to size the dummy input
#           (default: the run's saved config.yaml next to the checkpoint, so the
#            ONNX dummy uses the exact image_size the model trained at)
#
# Usage:
#   bash run/export_model.sh MODEL=mobilenetv4_conv_medium \
#        CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
#   bash run/export_model.sh MODEL=... CKPT=... FORMAT=torchscript
#
# Output: exports/<name>.onnx (or .pt). ONNX runs anywhere with onnxruntime —
#         no torch needed at inference time. For Android use run/export_executorch.sh.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "export_model"
activate_venv
# Force CPU so a stray CUDA_VISIBLE_DEVICES can't make torch try (and fail) to
# grab a GPU that a training run is using.
export CUDA_VISIBLE_DEVICES=""

: "${MODEL:?MODEL env var required (e.g. mobilenetv4_conv_medium) — must match MODEL_REGISTRY}"
: "${CKPT:?CKPT env var required (path to best_model.pth)}"
FORMAT="${FORMAT:-onnx}"
OUT="${OUT:-exports/${MODEL}}"

# Prefer the run's saved config.yaml (two levels up from .../checkpoints/best_model.pth)
# so the dummy input image_size matches how the model was trained; else repo default.
RUN_CFG="$(dirname "$(dirname "${CKPT}")")/config.yaml"
if [ -n "${CONFIG:-}" ]; then
    :
elif [ -s "${RUN_CFG}" ]; then
    CONFIG="${RUN_CFG}"
else
    CONFIG="configs/config.yaml"
fi

if [ ! -s "${CKPT}" ]; then
    echo "[run] ERROR: checkpoint not found or empty: ${CKPT}" >&2
    echo "[run] Train the model first (run/train_teacher.sh | run/train_student.sh)" >&2
    echo "[run] and use the fold-scoped path experiments/runs/<run>/fold_N/checkpoints/best_model.pth" >&2
    exit 2
fi

mkdir -p "$(dirname "${OUT}")"
echo "[run] Exporting ${MODEL} | ckpt=${CKPT} | format=${FORMAT} | config=${CONFIG} -> ${OUT}.*"
python scripts/export_model.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --format "${FORMAT}" \
    --output "${OUT}" \
    --config "${CONFIG}"

echo "[run] DONE"
