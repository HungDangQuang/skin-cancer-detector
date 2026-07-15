#!/bin/bash
# ============================================================================
# Submit wrapper — guarantees logs/ exists before sbatch and forwards env vars.
#
# Usage:
#     bash slurm/submit.sh <script.slurm> [VAR1=value1 VAR2=value2 ...]
#
# Examples:
#     bash slurm/submit.sh slurm/01_prepare_poc.slurm
#     bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv4_conv_medium
#     bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2 TRAINING=baseline
# ============================================================================
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <script.slurm> [VAR=value ...]"
    exit 1
fi

SCRIPT="$1"
shift

if [ ! -f "${SCRIPT}" ]; then
    echo "ERROR: script not found: ${SCRIPT}"
    exit 1
fi

# Defensive: SBATCH --output paths are relative to the submit dir; if logs/
# doesn't exist when sbatch runs, Slurm silently drops the job's stdout.
mkdir -p logs

# Build --export string from VAR=value pairs.
EXPORT_VARS="ALL"
for arg in "$@"; do
    if [[ ! "${arg}" =~ ^[A-Za-z_][A-Za-z0-9_]*=.* ]]; then
        echo "ERROR: arg '${arg}' is not VAR=value form"
        exit 1
    fi
    EXPORT_VARS="${EXPORT_VARS},${arg}"
done

echo "Submitting:  ${SCRIPT}"
echo "Exports:     ${EXPORT_VARS}"
echo "Logs dir:    $(pwd)/logs"

sbatch --export="${EXPORT_VARS}" "${SCRIPT}"
