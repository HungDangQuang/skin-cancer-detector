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
acquire_gpu() {
    local required_vram="$1"
    echo "[lib] Acquiring GPU with REQUIRED_VRAM=${required_vram} MB"

    if [ ! -x /usr/local/bin/gpu_check.sh ]; then
        echo "ERROR: /usr/local/bin/gpu_check.sh not found or not executable"
        echo "       (are you running on a Slurm compute node?)"
        exit 2
    fi

    unset CUDA_VISIBLE_DEVICES
    set +e
    local check_out
    check_out=$(/usr/local/bin/gpu_check.sh "${required_vram}" "${SLURM_JOB_ID}")
    local exit_code=$?
    set -e

    case "${exit_code}" in
        0)
            echo "[lib] GPU acquired: ${check_out}"
            export CUDA_VISIBLE_DEVICES="${check_out}"
            ;;
        10)
            echo "[lib] No suitable GPU — Slurm will requeue"
            echo "${check_out}"
            exit 0
            ;;
        11)
            echo "[lib] GPU dispatch exhausted retries — fatal"
            echo "${check_out}"
            exit 1
            ;;
        *)
            echo "[lib] gpu_check.sh returned unexpected code ${exit_code}"
            echo "${check_out}"
            exit 1
            ;;
    esac
}

# ------------------------------------------------------------------
setup_mps() {
    echo "[lib] Initializing private MPS pipe"
    export CUDA_MPS_PIPE_DIRECTORY="/tmp/nvidia-mps-job${SLURM_JOB_ID}"
    export CUDA_MPS_LOG_DIRECTORY="/tmp/nvidia-mps-log-job${SLURM_JOB_ID}"
    rm -rf "${CUDA_MPS_PIPE_DIRECTORY}" "${CUDA_MPS_LOG_DIRECTORY}"
    mkdir -p "${CUDA_MPS_PIPE_DIRECTORY}" "${CUDA_MPS_LOG_DIRECTORY}"
}
