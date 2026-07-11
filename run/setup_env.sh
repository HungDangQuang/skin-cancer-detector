#!/usr/bin/env bash
# ============================================================================
# One-time environment setup for a plain Linux GPU server / VM (no Slurm).
# Creates a fresh venv (./.venv-linux by default) and installs the project.
#
# Usage (on the server, from the repo root):
#     bash run/setup_env.sh
#
# Options (env vars):
#     VENV_DIR=/path/to/venv           # where to create the venv (default ./.venv-linux)
#     PYTHON=python3.12                # interpreter to build the venv from
#     TORCH_INDEX_URL=<pytorch wheel>  # force a specific CUDA build of torch, e.g.
#                                        https://download.pytorch.org/whl/cu121
#     DEV=1                            # also install requirements-dev.txt (tests/lint)
#
# NOTE: on Linux, `pip install torch>=2.2` from PyPI already pulls a CUDA build
# by default, so TORCH_INDEX_URL is only needed if you must match a specific
# driver/CUDA version. Check your driver with `nvidia-smi` (top-right CUDA X.Y).
# ============================================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/.venv-linux}"
PYTHON="${PYTHON:-python3}"

echo "==> Python interpreter: ${PYTHON} ($(${PYTHON} --version 2>&1))"

if [ ! -d "${VENV_DIR}" ]; then
    echo "==> Creating venv at ${VENV_DIR}"
    "${PYTHON}" -m venv "${VENV_DIR}"
else
    echo "==> Reusing existing venv at ${VENV_DIR}"
fi
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "==> Upgrading pip / wheel"
pip install --upgrade pip wheel

if [ -n "${TORCH_INDEX_URL:-}" ]; then
    echo "==> Installing torch/torchvision from ${TORCH_INDEX_URL}"
    pip install torch torchvision --index-url "${TORCH_INDEX_URL}"
fi

echo "==> Installing project requirements"
pip install -r requirements.txt
if [ "${DEV:-0}" = "1" ]; then
    echo "==> Installing dev requirements (tests + lint)"
    pip install -r requirements-dev.txt
fi
pip install -e .

echo "==> Verifying torch + CUDA"
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device count:", torch.cuda.device_count())
    for i in range(torch.cuda.device_count()):
        print(f"  [{i}] {torch.cuda.get_device_name(i)}")
else:
    print("WARNING: CUDA not available — training will run on CPU (very slow).")
PY

mkdir -p logs data/raw data/processed data/splits experiments/runs
echo
echo "Setup complete."
echo "  venv:        ${VENV_DIR}"
echo "  project:     ${PROJECT_DIR}"
echo
echo "Next steps:"
echo "  1. Put raw data under data/raw/ (see run/README.md § Data)"
echo "  2. bash run/prepare_data.sh"
echo "  3. bash run/train_teacher.sh TEACHER=efficientnet_b4"
