#!/bin/bash
# ============================================================================
# UIT Slurm template — copy and customize.
# Submit with: bash slurm/submit.sh slurm/<your_script>.slurm [VAR=value ...]
# Logs land in: logs/<job-name>_<jobid>.{out,err,_runtime.log}
#
# SHARED-CLUSTER RULE — non-negotiable when authoring new scripts:
#   This job MUST NOT terminate, preempt, or reset other users' work.
#   If the cluster is full, let Slurm queue this job (PD state) and wait.
#   FORBIDDEN: scancel/kill/pkill/killall, nvidia-smi --reset-gpu,
#              fuser -k, #SBATCH --preempt or priority-bumping --nice,
#              anything touching /tmp/nvidia-mps (system daemon path).
#   See .claude/skills/submit-slurm/SKILL.md "Authoring new *.slurm scripts".
# ============================================================================
#SBATCH --job-name=skin_template
#SBATCH --output=logs/template_%j.out
#SBATCH --error=logs/template_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:2          # mps:2 generic, mps:l40:2 / mps:a100:2 specific
#SBATCH --mem=4G
#SBATCH --time=00:30:00       # HH:MM:SS — max 72:00:00

# All boilerplate (logs/, fallback tee, env load, GPU dispatch) is in _lib.sh.
source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 4096              # required vRAM in MB; < 44000 (L40) / < 80000 (A100)
setup_mps

echo "[job] Sanity check"
nvidia-smi || true
python -c "import torch; print('cuda:', torch.cuda.is_available(), '| device:', torch.cuda.get_device_name(0))"

# REPLACE THIS with your actual command:
# python scripts/your_script.py --arg ...

echo "[job] DONE"
