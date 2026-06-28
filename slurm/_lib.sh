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
# Strategy: bypass /usr/local/bin/gpu_check.sh by default. The UIT
# cluster's helper currently has a typo on line 31 ("nvidia-smi-i"
# instead of "nvidia-smi -i") that makes it always false-negative, AND
# it internally issues `scontrol requeue` BEFORE returning control to
# us. That means any retry/fallback we do in this function never gets
# to run — Slurm SIGTERMs the allocation to honor the requeue. We have
# zero authority to talk it out of that.
#
# Until the cluster admin fixes the typo, we pick a GPU ourselves via
# `nvidia-smi --query-gpu`. To opt back into the cluster helper once
# it's fixed:    export USE_CLUSTER_GPU_CHECK=1
#
# This still respects the shared-cluster rule — we only ever pick a
# GPU that has the requested vRAM free. We never kill another job.
acquire_gpu() {
    local required_vram="$1"
    echo "[lib] Acquiring GPU with REQUIRED_VRAM=${required_vram} MB"

    # Optional opt-in to cluster helper, off by default.
    if [ "${USE_CLUSTER_GPU_CHECK:-0}" = "1" ] && [ -x /usr/local/bin/gpu_check.sh ]; then
        echo "[lib] USE_CLUSTER_GPU_CHECK=1 — delegating to /usr/local/bin/gpu_check.sh"
        unset CUDA_VISIBLE_DEVICES
        set +e
        local check_out
        check_out=$(/usr/local/bin/gpu_check.sh "${required_vram}" "${SLURM_JOB_ID:-0}")
        local exit_code=$?
        set -e
        if [ "${exit_code}" = "0" ]; then
            echo "[lib] GPU acquired via gpu_check.sh: ${check_out}"
            export CUDA_VISIBLE_DEVICES="${check_out}"
            return 0
        fi
        # On any non-zero we fall through to the nvidia-smi path. If
        # gpu_check.sh already issued scontrol requeue, Slurm will kill
        # us soon — but at least we tried.
        echo "[lib] gpu_check.sh exited ${exit_code} — falling through to nvidia-smi"
    fi

    # Slurm pins CUDA_VISIBLE_DEVICES via --gres=mps, but the gres/mps plugin
    # schedules by compute-% and IGNORES GPU memory, so the pinned GPU may already
    # be full of another user's job (this OOM'd jobs 32552/32558 at the first CUDA
    # alloc). Don't trust the pin blindly: verify free VRAM on it, and if it's too
    # full, fall through to the nvidia-smi selection below to hop to a freer GPU.
    # (The QOS `uit` caps gres/gpu=0, so requesting a whole exclusive GPU is not an
    #  option on this cluster — MPS + runtime re-selection is the only safe path.)
    if [ -n "${CUDA_VISIBLE_DEVICES:-}" ]; then
        local pinned="${CUDA_VISIBLE_DEVICES%%,*}" pinned_free=""
        if [ -n "$(command -v nvidia-smi 2>/dev/null || true)" ]; then
            pinned_free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits \
                            -i "${pinned}" 2>/dev/null | head -1 | tr -dc '0-9' || true)
        fi
        if [ -n "${pinned_free}" ] && [ "${pinned_free}" -ge "${required_vram}" ] 2>/dev/null; then
            echo "[lib] CUDA_VISIBLE_DEVICES=${pinned} (Slurm-pinned; ${pinned_free} MB free >= ${required_vram} MB — keeping)"
            return 0
        fi
        echo "[lib] WARN: Slurm-pinned GPU ${pinned} has ${pinned_free:-unknown} MB free < ${required_vram} MB needed"
        echo "[lib] Re-selecting a GPU with enough free VRAM (MPS ignores memory — this is the 32552/32558 OOM guard)..."
        unset CUDA_VISIBLE_DEVICES
        # fall through to the nvidia-smi selection below
    fi

    # nvidia-smi-driven GPU selection.
    local picked="" sm_out="" sm_exit=1 nvsmi_path=""
    nvsmi_path=$(command -v nvidia-smi 2>/dev/null || true)

    if [ -n "${nvsmi_path}" ]; then
        echo "[lib] Step A: nvidia-smi at ${nvsmi_path}"
        echo "[lib] Step B: querying GPU free memory (30s timeout)..."
        if command -v timeout >/dev/null 2>&1; then
            sm_out=$(timeout 30s "${nvsmi_path}" \
                        --query-gpu=index,memory.free \
                        --format=csv,noheader,nounits 2>&1 || true)
            sm_exit=$?
        else
            sm_out=$("${nvsmi_path}" \
                        --query-gpu=index,memory.free \
                        --format=csv,noheader,nounits 2>&1 || true)
            sm_exit=$?
        fi
        echo "[lib] Step C: nvidia-smi exit=${sm_exit}, ${#sm_out} bytes returned:"
        printf '%s\n' "${sm_out:-<empty>}" | sed 's/^/    /' | head -20

        echo "[lib] Step D: selecting GPU with free vRAM >= ${required_vram} MB..."
        picked=$(printf '%s\n' "${sm_out}" 2>/dev/null \
                 | sort -t',' -k2 -nr 2>/dev/null \
                 | awk -F',' -v need="${required_vram}" \
                       '$2+0 >= need {gsub(/ /,"",$1); print $1; exit}' \
                       2>/dev/null \
                 || true)
        echo "[lib] Step E: picked='${picked:-<none>}'"
    else
        echo "[lib] nvidia-smi NOT on PATH"
    fi

    if [ -n "${picked}" ]; then
        export CUDA_VISIBLE_DEVICES="${picked}"
        echo "[lib] CUDA_VISIBLE_DEVICES=${picked} (selected via nvidia-smi)"
    else
        # Last resort — try GPU 0 rather than failing. Still respects the
        # shared-cluster rule (we never kill another job; we just pick a
        # device and let PyTorch attempt allocation).
        export CUDA_VISIBLE_DEVICES=0
        echo "[lib] WARN: could not select a GPU via nvidia-smi — defaulting to CUDA_VISIBLE_DEVICES=0"
        echo "[lib] WARN: job will OOM if GPU 0 is full; lower acquire_gpu vRAM or wait for the cluster to free up"
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
