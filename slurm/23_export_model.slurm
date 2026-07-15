#!/bin/bash
# ============================================================================
# Export a trained checkpoint to ONNX or TorchScript for deployment.
# CPU-ONLY — torch.onnx.export / torch.jit.script trace on a dummy CPU forward,
# no CUDA needed. So this requests NO --gres: it never touches the 20-MPS budget
# and schedules immediately (doesn't queue behind GPU jobs).
# Submit:
#   bash slurm/submit.sh slurm/23_export_model.slurm \
#       MODEL=mobilenetv4_conv_medium \
#       CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
# Optional env:
#   FORMAT=onnx|torchscript   (default onnx)
#   OUT=exports/<name>        (default exports/${MODEL}; extension added by the script)
#   CONFIG=<path/to/config>   (default: the run's saved config.yaml next to the
#                              checkpoint, so the ONNX dummy uses the exact
#                              image_size the model trained at)
# Output: exports/<name>.onnx (or .pt). Download it and run with onnxruntime
#         anywhere — no torch required at inference time for ONNX.
# ============================================================================
#SBATCH --job-name=export_model
#SBATCH --output=logs/export_model_%j.out
#SBATCH --error=logs/export_model_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
# CPU-only: no acquire_gpu / setup_mps. Force CPU so a stray CUDA_VISIBLE_DEVICES
# from the environment can't make torch try (and fail) to grab a GPU.
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
    echo "[job] ERROR: checkpoint not found or empty: ${CKPT}" >&2
    echo "[job] Train the model first (slurm 11/12) and use the fold-scoped path" >&2
    echo "[job]   experiments/runs/<run>/fold_N/checkpoints/best_model.pth" >&2
    exit 1
fi

echo "[job] Exporting ${MODEL} | ckpt=${CKPT} | format=${FORMAT} | config=${CONFIG} -> ${OUT}.*"
python scripts/export_model.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --format "${FORMAT}" \
    --output "${OUT}" \
    --config "${CONFIG}"

echo "[job] DONE"
