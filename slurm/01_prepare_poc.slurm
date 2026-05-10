#!/bin/bash
# ============================================================================
# Step 1 (POC) — generate synthetic fixtures. CPU-ONLY (no GPU/MPS).
# Submit:  bash slurm/submit.sh slurm/01_prepare_poc.slurm
# Output:  data/processed/poc/, data/splits/poc/
#          logs/prepare_poc_<jobid>.{out,err}
# ============================================================================
#SBATCH --job-name=prepare_poc
#SBATCH --output=logs/prepare_poc_%j.out
#SBATCH --error=logs/prepare_poc_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:15:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env

echo "[job] Generating synthetic POC data"
python scripts/prepare_poc_data.py

echo "[job] Verifying output"
ls -la data/processed/poc/benign | head -3
ls -la data/processed/poc/malignant | head -3
ls -la data/splits/poc/fold_0/
ls -la data/splits/poc/test_split.csv
echo "[job] DONE"
