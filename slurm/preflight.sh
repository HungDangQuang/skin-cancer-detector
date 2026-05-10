#!/bin/bash
# ============================================================================
# Login-node preflight check. Run BEFORE submitting any sbatch jobs.
#
#     cd /datastore/${USER}/skin-cancer-detector
#     bash slurm/preflight.sh
#
# Verifies: working dir, venv, logs/, modules, python imports, gpu_check.sh,
# and runs a tiny synthetic-data smoke test (CPU only) to exercise the data
# pipeline end-to-end without a Slurm allocation.
# ============================================================================
set -euo pipefail

PROJECT_DIR="/datastore/${USER}/skin-cancer-detector"
VENV_DIR="/datastore/${USER}/venv"

red()   { printf "\033[31m%s\033[0m\n" "$*"; }
green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m%s\033[0m\n" "$*"; }

ok()   { green   "  [OK]   $*"; }
warn() { yellow  "  [WARN] $*"; }
fail() { red     "  [FAIL] $*"; FAILED=1; }

FAILED=0

echo "=== Preflight ==="
echo "User:      ${USER}"
echo "Hostname:  $(hostname)"
echo "Date:      $(date '+%F %T')"
echo

echo "1. Working directory"
if [ "$(pwd)" = "${PROJECT_DIR}" ]; then
    ok "in ${PROJECT_DIR}"
else
    warn "not in ${PROJECT_DIR} (currently $(pwd))"
fi
[ -f Makefile ] && [ -d slurm ] && ok "Makefile and slurm/ found" || fail "not in project root"

echo
echo "2. logs/ directory"
mkdir -p logs && ok "logs/ exists ($(pwd)/logs)"

echo
echo "3. venv at ${VENV_DIR}"
if [ -d "${VENV_DIR}" ]; then
    ok "venv exists"
else
    fail "venv missing — run:  bash slurm/setup_env.sh"
fi

echo
echo "4. Modules"
if module avail 2>&1 | grep -q "shared\|python312"; then
    ok "modules 'shared' and 'python312' visible"
else
    warn "couldn't confirm modules with 'module avail' — try anyway"
fi
module clear -f
module load shared python312
ok "modules loaded"

if [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
    echo
    echo "5. Python imports"
    if python -c "import torch, hydra, timm, omegaconf, albumentations, sklearn" 2>/dev/null; then
        ok "torch, hydra, timm, omegaconf, albumentations, sklearn"
    else
        fail "import error — re-run setup_env.sh"
    fi
fi

echo
echo "6. gpu_check.sh helper"
if [ -x /usr/local/bin/gpu_check.sh ]; then
    ok "/usr/local/bin/gpu_check.sh executable"
else
    warn "gpu_check.sh missing on this node (only matters on compute nodes)"
fi

echo
echo "7. Smoke test — generate 5 + 2 synthetic images (CPU)"
if [ -d "${VENV_DIR}" ] && [ -f scripts/prepare_poc_data.py ]; then
    rm -rf /tmp/poc_smoke /tmp/poc_smoke_splits
    if python scripts/prepare_poc_data.py \
            --n-benign 5 --n-malignant 2 \
            --processed-dir /tmp/poc_smoke \
            --splits-dir /tmp/poc_smoke_splits >/dev/null 2>&1; then
        ok "synthetic data pipeline works"
        rm -rf /tmp/poc_smoke /tmp/poc_smoke_splits
    else
        fail "smoke test failed — re-run manually:  python scripts/prepare_poc_data.py --n-benign 5 --n-malignant 2 --processed-dir /tmp/x --splits-dir /tmp/y"
    fi
fi

echo
if [ "${FAILED}" -eq 0 ]; then
    green "=== All checks passed. Ready to submit jobs. ==="
    echo "Next: bash slurm/submit.sh slurm/01_prepare_poc.slurm"
else
    red   "=== Some checks failed. Fix the issues above before submitting. ==="
    exit 1
fi
