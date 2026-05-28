#!/bin/bash
# ============================================================================
# Common bash library for all *.slurm jobs.
# Source this from each script:    source "${SLURM_SUBMIT_DIR}/slurm/_lib.sh"
#
# Provides:
#   - set -euo pipefail (fail loudly)
#   - Defensive logs/ creation + fallback tee log (so output survives even if
#     SBATCH's --output redirect fails)
#   - Diagnostic header (jobid, hostname, pwd, user)
#   - load_python_env       — module load + venv activation, with checks
#   - acquire_gpu <vram_mb> — calls gpu_check.sh; handles exit codes 10 / 11
#   - setup_mps             — per-job CUDA MPS pipe directory
# ============================================================================
set -euo pipefail

# Resolve project dir from where sbatch was invoked.
PROJECT_DIR="${SLURM_SUBMIT_DIR:-$(pwd)}"
cd "${PROJECT_DIR}"

# Defensive: ensure logs/ exists even if user forgot to run setup_env.sh.
mkdir -p logs

# Fallback runtime log — survives even if SBATCH --output redirect failed
# (e.g. parent dir missing at submit time on older Slurm versions).
JOBID="${SLURM_JOB_ID:-$$}"
JOBNAME="${SLURM_JOB_NAME:-job}"
RUNLOG="${PROJECT_DIR}/logs/${JOBNAME}_${JOBID}_runtime.log"
exec > >(tee -a "${RUNLOG}") 2>&1

echo "================================================================"
echo "Job ID:      ${SLURM_JOB_ID:-N/A}"
echo "Job name:    ${SLURM_JOB_NAME:-N/A}"
echo "Hostname:    $(hostname)"
echo "Working dir: $(pwd)"
echo "Submit dir:  ${SLURM_SUBMIT_DIR:-N/A}"
echo "Runtime log: ${RUNLOG}"
echo "User:        ${USER}"
echo "Date:        $(date '+%F %T')"
echo "================================================================"

# ------------------------------------------------------------------
load_python_env() {
    echo "[lib] Loading modules + venv"
    module clear -f
    module load shared python312

    local datastore_dir="${DATASTORE_USER_DIR:-/datastore/keg/hungdang}"
    local venv_path="${datastore_dir}/venv"
    if [ ! -d "${venv_path}" ]; then
        echo "ERROR: venv missing at ${venv_path}"
        echo "Run on the LOGIN NODE first:  bash slurm/setup_env.sh"
        exit 2
    fi
    # shellcheck disable=SC1091
    source "${venv_path}/bin/activate"
    echo "[lib] Python: $(which python) ($(python --version 2>&1))"

    # Sanity-check that the venv was actually populated by setup_env.sh.
    # Without this, scripts crash mid-run with "ModuleNotFoundError: numpy"
    # and the cause (incomplete pip install) is not obvious.
    if ! python -c "import numpy, pandas, PIL, torch, hydra, omegaconf" 2>/dev/null; then
        echo "ERROR: venv at ${venv_path} is missing core dependencies."
        echo "       (failed: import numpy, pandas, PIL, torch, hydra, omegaconf)"
        echo
        echo "Fix on the LOGIN NODE:"
        echo "    cd ${datastore_dir}/skin-cancer-detector"
        echo "    bash slurm/setup_env.sh"
        echo
        echo "Then re-submit:"
        echo "    bash slurm/submit.sh slurm/01_prepare_poc.slurm"
        exit 2
    fi
    echo "[lib] Core imports OK (numpy, pandas, PIL, torch, hydra, omegaconf)"
}

# ------------------------------------------------------------------
# acquire_gpu <required_vram_mb>
#
# Two paths:
#   1. If /usr/local/bin/gpu_check.sh exists (UIT's preferred dispatcher),
#      use it and honor exit codes 0 / 10 / 11.
#   2. Otherwise, trust Slurm's native --gres allocation: Slurm sets
#      CUDA_VISIBLE_DEVICES for the job, so we just log it and proceed.
#      The required_vram arg is informational in this branch.
acquire_gpu() {
    local required_vram="$1"
    echo "[lib] Acquiring GPU with REQUIRED_VRAM=${required_vram} MB"

    if [ -x /usr/local/bin/gpu_check.sh ]; then
        unset CUDA_VISIBLE_DEVICES
        set +e
        local check_out
        check_out=$(/usr/local/bin/gpu_check.sh "${required_vram}" "${SLURM_JOB_ID:-0}")
        local exit_code=$?
        set -e

        case "${exit_code}" in
            0)
                echo "[lib] GPU acquired via gpu_check.sh: ${check_out}"
                export CUDA_VISIBLE_DEVICES="${check_out}"
                ;;
            10)
                # gpu_check.sh said no GPU is free, but the cluster helper has
                # been seen to false-negative (e.g. internal "nvidia-smi-i:
                # command not found" typo bug — line 31). Before trusting it
                # and requeuing, ask nvidia-smi ourselves: if any GPU genuinely
                # has >= required_vram free, use it. This still respects the
                # shared-cluster rule — we only pick a GPU that has the room.
                echo "[lib] gpu_check.sh reported no GPU — verifying with nvidia-smi"
                echo "${check_out}"
                if command -v nvidia-smi >/dev/null 2>&1; then
                    local picked
                    picked=$(nvidia-smi --query-gpu=index,memory.free \
                                --format=csv,noheader,nounits 2>/dev/null \
                             | sort -t',' -k2 -nr \
                             | awk -F',' -v need="${required_vram}" '$2+0 >= need {gsub(/ /,"",$1); print $1; exit}')
                    if [ -n "${picked}" ]; then
                        export CUDA_VISIBLE_DEVICES="${picked}"
                        echo "[lib] nvidia-smi found GPU ${picked} with sufficient free vRAM — overriding gpu_check.sh"
                    else
                        echo "[lib] nvidia-smi confirms no GPU has ${required_vram} MB free — Slurm will requeue"
                        exit 0
                    fi
                else
                    echo "[lib] nvidia-smi unavailable — accepting gpu_check.sh decision, Slurm will requeue"
                    exit 0
                fi
                ;;
            11)
                # gpu_check.sh has exhausted its own internal retries. Same
                # fallback as code 10: verify with nvidia-smi before giving up,
                # because the same typo bug also surfaces here after 5 requeues.
                echo "[lib] gpu_check.sh exhausted retries — verifying with nvidia-smi"
                echo "${check_out}"
                if command -v nvidia-smi >/dev/null 2>&1; then
                    local picked
                    picked=$(nvidia-smi --query-gpu=index,memory.free \
                                --format=csv,noheader,nounits 2>/dev/null \
                             | sort -t',' -k2 -nr \
                             | awk -F',' -v need="${required_vram}" '$2+0 >= need {gsub(/ /,"",$1); print $1; exit}')
                    if [ -n "${picked}" ]; then
                        export CUDA_VISIBLE_DEVICES="${picked}"
                        echo "[lib] nvidia-smi found GPU ${picked} — overriding gpu_check.sh fatal exit"
                    else
                        echo "[lib] nvidia-smi confirms no GPU has ${required_vram} MB free — fatal"
                        exit 1
                    fi
                else
                    echo "[lib] nvidia-smi unavailable — accepting gpu_check.sh fatal exit"
                    exit 1
                fi
                ;;
            *)
                echo "[lib] gpu_check.sh returned unexpected code ${exit_code}"
                echo "${check_out}"
                exit 1
                ;;
        esac
    else
        # Fallback: no gpu_check.sh helper. Prefer Slurm's CUDA_VISIBLE_DEVICES
        # if it was set by --gres; otherwise auto-pick the GPU with the most
        # free vRAM via nvidia-smi.
        echo "[lib] gpu_check.sh not present — using Slurm's allocation directly"
        if [ -n "${CUDA_VISIBLE_DEVICES:-}" ]; then
            echo "[lib] CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES} (set by Slurm)"
        else
            echo "[lib] CUDA_VISIBLE_DEVICES unset — picking GPU with most free vRAM"
            if command -v nvidia-smi >/dev/null 2>&1; then
                local picked
                picked=$(nvidia-smi --query-gpu=index,memory.free \
                            --format=csv,noheader,nounits 2>/dev/null \
                         | sort -t',' -k2 -nr \
                         | head -1 \
                         | awk -F',' '{print $1}' \
                         | tr -d ' ')
                if [ -n "${picked}" ]; then
                    export CUDA_VISIBLE_DEVICES="${picked}"
                    echo "[lib] CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES} (picked via nvidia-smi)"
                else
                    echo "[lib] WARN: nvidia-smi found no GPUs — defaulting to 0"
                    export CUDA_VISIBLE_DEVICES=0
                fi
            else
                echo "[lib] WARN: nvidia-smi unavailable — defaulting to CUDA_VISIBLE_DEVICES=0"
                export CUDA_VISIBLE_DEVICES=0
            fi
        fi
    fi
}

# ------------------------------------------------------------------
setup_mps() {
    echo "[lib] Initializing private MPS pipe"
    local job_tag="${SLURM_JOB_ID:-$$}"
    export CUDA_MPS_PIPE_DIRECTORY="/tmp/nvidia-mps-job${job_tag}"
    export CUDA_MPS_LOG_DIRECTORY="/tmp/nvidia-mps-log-job${job_tag}"
    rm -rf "${CUDA_MPS_PIPE_DIRECTORY}" "${CUDA_MPS_LOG_DIRECTORY}"
    mkdir -p "${CUDA_MPS_PIPE_DIRECTORY}" "${CUDA_MPS_LOG_DIRECTORY}"
}
