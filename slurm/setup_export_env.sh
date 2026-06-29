#!/bin/bash
# ============================================================================
# One-time setup of the ISOLATED ExecuTorch export venv — run on the LOGIN NODE.
#
# Creates ${DATASTORE_USER_DIR}/venv-export (SEPARATE from the training venv at
# ${DATASTORE_USER_DIR}/venv) and installs requirements-export.txt. ExecuTorch
# pins its own torch build; keeping it here means it can never change the
# torch>=2.2 the training/eval jobs rely on.
#
# Usage (on slurm.uit.edu.vn):
#     cd /datastore/keg/hungdang/skin-cancer-detector
#     bash slurm/setup_export_env.sh
#
# Override base dir if your account/path differs:
#     DATASTORE_USER_DIR=/datastore/<acct>/<sub> bash slurm/setup_export_env.sh
# ============================================================================
set -euo pipefail

DATASTORE_DIR="${DATASTORE_USER_DIR:-/datastore/keg/hungdang}"
PROJECT_DIR=${DATASTORE_DIR}/skin-cancer-detector
VENV_DIR=${DATASTORE_DIR}/venv-export

echo "==> Loading modules"
module clear -f
module load shared python312

if [ ! -d "${VENV_DIR}" ]; then
    echo "==> Creating export venv at ${VENV_DIR}"
    python -m venv "${VENV_DIR}"
else
    echo "==> Reusing existing export venv at ${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

echo "==> Upgrading pip"
pip install --upgrade pip wheel

echo "==> Installing export-only requirements (ExecuTorch brings its own torch)"
cd "${PROJECT_DIR}"
pip install -r requirements-export.txt
# --no-deps: make `src` importable without pulling the training stack
# (albumentations/mlflow/...) back into this isolated venv.
pip install -e . --no-deps

echo "==> Verifying ExecuTorch import"
python -c "import torch, executorch; print('torch:', torch.__version__, '| executorch OK')"

mkdir -p "${PROJECT_DIR}/logs" "${PROJECT_DIR}/exports/executorch"
echo
echo "Export venv ready."
echo "  venv:     ${VENV_DIR}  (separate from training venv ${DATASTORE_DIR}/venv)"
echo "  next:     bash slurm/submit.sh slurm/25_export_executorch.slurm MODEL=efficientnet_b0 CKPT=..."
