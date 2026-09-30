#!/usr/bin/env bash
# ============================================================================
# One-time setup of the ISOLATED ExecuTorch export venv.
#
# Creates ./.venv-export (SEPARATE from the training venv ./.venv-linux) and
# installs requirements-export.txt. ExecuTorch pins its own torch build; keeping
# it in its own venv means it can never change the torch>=2.2 that the
# training/eval runs depend on.
#
# Usage (on the server, from the repo root):
#     bash run/setup_export_env.sh
#
# Options (env vars):
#     EXPORT_VENV_DIR=/path/to/venv   # default ./.venv-export
#     PYTHON=python3.12               # interpreter to build the venv from
#
# Everything stays INSIDE the project folder — no sudo, no system python, no
# shell-rc edits.
# ============================================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

VENV_DIR="${EXPORT_VENV_DIR:-${PROJECT_DIR}/.venv-export}"
PYTHON="${PYTHON:-python3}"

echo "==> Python interpreter: ${PYTHON} ($(${PYTHON} --version 2>&1))"

if [ ! -d "${VENV_DIR}" ]; then
    echo "==> Creating export venv at ${VENV_DIR}"
    "${PYTHON}" -m venv "${VENV_DIR}"
else
    echo "==> Reusing existing export venv at ${VENV_DIR}"
fi
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "==> Upgrading pip / wheel"
pip install --upgrade pip wheel

echo "==> Installing export-only requirements (ExecuTorch brings its own torch)"
pip install -r requirements-export.txt
# --no-deps: make `src` importable without pulling the training stack
# (albumentations/mlflow/...) back into this isolated venv.
pip install -e . --no-deps

echo "==> Verifying ExecuTorch import"
python -c "import torch, executorch; print('torch:', torch.__version__, '| executorch OK')"

mkdir -p "${PROJECT_DIR}/logs" "${PROJECT_DIR}/exports/executorch"
echo
echo "Export venv ready."
echo "  venv:     ${VENV_DIR}  (separate from training venv ${PROJECT_DIR}/.venv-linux)"
echo "  next:     bash run/export_executorch.sh MODEL=mobilenetv4_conv_medium CKPT=..."
