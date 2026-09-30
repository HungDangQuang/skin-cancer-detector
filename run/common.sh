#!/usr/bin/env bash
# ============================================================================
# Common library for the run/ execution layer (plain GPU server / VM over SSH).
# Source this from each run/*.sh script:   source "$(dirname "$0")/common.sh"
#
# This is the local-server analogue of run/common.sh. It intentionally drops
# every cluster-specific concern (no `module load`, no /datastore, no MPS, no
# scontrol/gpu_check.sh) — on your own box you own the GPU, so GPU selection is
# just CUDA_VISIBLE_DEVICES. Everything else (fold loop, run-dir convention,
# logging) is kept identical so results are directly comparable to cluster runs.
#
# Provides:
#   - set -euo pipefail
#   - PROJECT_DIR resolution + cd
#   - venv activation (VENV_DIR, default ./.venv-linux)
#   - select_gpu   — honor GPU env var, or auto-pick the freest GPU
#   - start_log    — tee stdout/stderr to logs/<name>_<ts>.log (survives SSH drop)
# ============================================================================
set -euo pipefail

# Resolve the repo root from this file's location (run/ lives at the repo root),
# so the scripts work regardless of the caller's cwd.
_RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${_RUN_DIR}/.." && pwd)"
cd "${PROJECT_DIR}"

mkdir -p logs

# ---------------------------------------------------------------------------
# Virtualenv. On the Linux server we build a fresh venv (the repo's ./.venv is
# a Mac-only artifact and must not be reused). Override with VENV_DIR=... .
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/.venv-linux}"

activate_venv() {
    if [ ! -d "${VENV_DIR}" ]; then
        echo "ERROR: venv missing at ${VENV_DIR}"
        echo "Run first:  bash run/setup_env.sh"
        exit 2
    fi
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
    echo "[run] python: $(command -v python) ($(python --version 2>&1))"
    if ! python -c "import numpy, pandas, PIL, torch, hydra, omegaconf" 2>/dev/null; then
        echo "ERROR: venv at ${VENV_DIR} is missing core dependencies."
        echo "       Re-run:  bash run/setup_env.sh"
        exit 2
    fi
}

# ---------------------------------------------------------------------------
# GPU selection is just CUDA_VISIBLE_DEVICES. Behavior:
#   GPU=0            -> pin to physical GPU 0 (the code then sees it as cuda:0)
#   GPU="0,1"        -> expose both (single-process still uses cuda:0)
#   GPU unset / auto -> auto-pick the GPU with the most free VRAM
#   GPU=cpu          -> force CPU (also set device=cpu below)
select_gpu() {
    local want="${GPU:-auto}"

    if [ "${want}" = "cpu" ]; then
        export CUDA_VISIBLE_DEVICES=""
        echo "[run] GPU: forced CPU (CUDA_VISIBLE_DEVICES='')"
        return 0
    fi

    if [ "${want}" != "auto" ]; then
        export CUDA_VISIBLE_DEVICES="${want}"
        echo "[run] GPU: pinned CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
        return 0
    fi

    # Auto: pick the GPU with the most free memory (falls back to 0).
    if command -v nvidia-smi >/dev/null 2>&1; then
        local best
        best="$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits \
                 | sort -t, -k2 -n -r | head -n1 | cut -d, -f1 | tr -d ' ')"
        export CUDA_VISIBLE_DEVICES="${best:-0}"
        echo "[run] GPU: auto-picked freest GPU -> CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
    else
        echo "[run] WARN: nvidia-smi not found — leaving CUDA_VISIBLE_DEVICES unset (will use CPU if no CUDA)."
    fi
}

# ---------------------------------------------------------------------------
# Tee all output to a timestamped log so a dropped SSH session doesn't lose it.
# (For a truly detached long run, launch the run/*.sh under tmux/nohup — see
# run/README.md.)
start_log() {
    local name="${1:-run}"
    local ts
    ts="$(date '+%Y%m%d_%H%M%S')"
    local log="${PROJECT_DIR}/logs/${name}_${ts}.log"
    echo "[run] logging to ${log}"
    exec > >(tee -a "${log}") 2>&1
    echo "================================================================"
    echo "Script:      ${name}"
    echo "Host:        $(hostname)"
    echo "Working dir: $(pwd)"
    echo "Date:        $(date '+%F %T')"
    echo "================================================================"
}
