#!/bin/bash
# ============================================================================
# One-time environment setup — run on the LOGIN NODE (not as a Slurm job).
# Creates /datastore/${USER}/venv and installs project dependencies.
#
# Usage (on slurm.uit.edu.vn):
#     cd /datastore/${USER}/skin-cancer-detector
#     bash slurm/setup_env.sh
# ============================================================================
set -euo pipefail

DATASTORE_DIR=/datastore/${USER}
PROJECT_DIR=${DATASTORE_DIR}/skin-cancer-detector
VENV_DIR=${DATASTORE_DIR}/venv

echo "==> Loading modules"
module clear -f
module load shared python312

if [ ! -d "${VENV_DIR}" ]; then
    echo "==> Creating venv at ${VENV_DIR}"
    python -m venv "${VENV_DIR}"
else
    echo "==> Reusing existing venv at ${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

echo "==> Upgrading pip"
pip install --upgrade pip wheel

echo "==> Installing project + dev requirements"
cd "${PROJECT_DIR}"
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

echo "==> Verifying torch CUDA"
python -c "import torch; print('torch:', torch.__version__, '| cuda available:', torch.cuda.is_available())"

mkdir -p "${PROJECT_DIR}/logs"
echo
echo "Setup complete."
echo "  venv:        ${VENV_DIR}"
echo "  project:     ${PROJECT_DIR}"
echo "  next steps:  sbatch slurm/01_prepare_poc.slurm"
