#!/bin/bash
# ============================================================================
# Export a checkpoint to ExecuTorch (.pte) for Android on-device. CPU-only.
#
# Uses the ISOLATED export venv (${DATASTORE_USER_DIR}/venv-export) — deliberately
# NOT load_python_env (that activates the training venv). ExecuTorch lives in its
# own venv so it can't perturb the training torch>=2.2. Run the one-time setup
# first on the LOGIN NODE:  bash slurm/setup_export_env.sh
#
# Submit:
#   bash slurm/submit.sh slurm/25_export_executorch.slurm \
#       MODEL=mobilenetv4_conv_medium \
#       CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
#   # BACKEND=none for a portable-ops fallback if XNNPACK can't partition an arch
#
# Output (default): exports/executorch/<MODEL>.pte
# ============================================================================
#SBATCH --job-name=export_executorch
#SBATCH --output=logs/export_executorch_%j.out
#SBATCH --error=logs/export_executorch_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"

# Activate the ISOLATED export venv directly (NOT load_python_env / training venv).
module clear -f
module load shared python312
EXPORT_VENV="${DATASTORE_USER_DIR:-/datastore/keg/hungdang}/venv-export"
if [ ! -d "${EXPORT_VENV}" ]; then
    echo "ERROR: export venv missing at ${EXPORT_VENV}"
    echo "Run on the LOGIN NODE first:  bash slurm/setup_export_env.sh"
    exit 2
fi
# shellcheck disable=SC1091
source "${EXPORT_VENV}/bin/activate"
echo "[job] Export venv: $(which python) ($(python --version 2>&1))"

: "${MODEL:?MODEL env var required (e.g. mobilenetv4_conv_medium)}"
: "${CKPT:?CKPT env var required (path to best_model.pth)}"
BACKEND="${BACKEND:-xnnpack}"
OUT="${OUT:-exports/executorch/${MODEL}.pte}"

echo "[job] ExecuTorch export ${MODEL} (backend=${BACKEND}) from ${CKPT} -> ${OUT}"
python scripts/export_executorch.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --backend "${BACKEND}" \
    --output "${OUT}"

echo "[job] DONE"
