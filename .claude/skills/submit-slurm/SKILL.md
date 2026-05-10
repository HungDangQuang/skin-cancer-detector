---
name: submit-slurm
description: Submit a Slurm job on the UIT cluster (slurm.uit.edu.vn). Use when the user asks to run training/eval/data-prep on the cluster, mentions sbatch, says "submit job", "queue job", or asks about Slurm. Wraps slurm/submit.sh and forwards env vars.
---

# submit-slurm

Submits a Slurm job through the project's `slurm/submit.sh` wrapper, which guarantees `logs/` exists before sbatch and forwards `VAR=value` overrides.

## When to use

- User asks to "submit", "run on cluster", "sbatch ...", "queue a job"
- User mentions Slurm, UIT, the DGX cluster, training jobs
- User wants to check on a running job (use `squeue`, `sacct`, log paths)

## DO NOT

- Run `sbatch` directly — always go through `bash slurm/submit.sh ...`. Raw sbatch loses logs if `logs/` doesn't exist.
- Submit without confirming the venv exists. If unsure, run `bash slurm/preflight.sh` first.
- Submit a job that depends on prior outputs (e.g. `03_poc_student` needs the teacher checkpoint) without first verifying those outputs exist on disk — the cluster allocation will be wasted.
- Edit `--time`, `--mem`, `--gres` ad-hoc — those defaults are tuned in `docs/SLURM.md §5`. Bump them only if a job actually OOM'd or timed out.

## Before submitting after any code change

Run the `validate-pipeline` skill (`.claude/skills/validate-pipeline/`) — it does Python imports + Hydra config dry-load + slurm script lint in seconds. Catches `ImportError`, `ConfigKeyError` (struct mode), unbound Slurm vars, ungated `nvidia-smi`, and hardcoded `/datastore/${USER}/...` — all of which we've actually shipped to the cluster on this project.

## How to use

### 1. Pick the right script

| Goal | Script |
|---|---|
| Generate POC fixtures | `slurm/01_prepare_poc.slurm` (CPU only) |
| POC teacher (2 epochs) | `slurm/02_poc_teacher.slurm` |
| POC student (2 epochs, KD) | `slurm/03_poc_student.slurm` |
| Real ISIC preprocessing | `slurm/10_prepare_data.slurm` |
| Full B4 teacher (50 epochs) | `slurm/11_train_teacher.slurm` |
| Full KD student | `slurm/12_train_student.slurm` |
| Evaluate a checkpoint | `slurm/20_evaluate.slurm` |

### 2. Submit

```bash
bash slurm/submit.sh slurm/<script>.slurm [VAR=value ...]
```

Examples:
```bash
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv3_large
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s TRAINING=baseline
bash slurm/submit.sh slurm/20_evaluate.slurm \
    MODEL=efficientnet_b0 \
    CKPT=experiments/poc/kd_efficientnet_b4_to_efficientnet_b0/checkpoints/best_model.pth \
    OUT=reports/results/poc_kd_b0.json
```

### 3. Track the job

```bash
squeue -u ${USER}                # all your jobs
squeue -j <jobid>                # specific
sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode
tail -f logs/<jobname>_<jobid>.out
tail -f logs/<jobname>_<jobid>_runtime.log    # fallback tee log (always written)
```

## Important context

- **Workflow:** preflight → submit → monitor. Skip preflight only if it's been run successfully recently.
- **Working dir:** must be `/datastore/${USER}/skin-cancer-detector`. Never put data or runs under `/home/${USER}` (30 GB cap).
- **Resource limits:** 20 MPS, 5 concurrent jobs, 32 vCPU cores, 72 h max per job. vRAM ≤44 GB on L40, ≤80 GB on A100.
- **Two log paths per job:** SBATCH-redirected `logs/<job>_<id>.out` AND the script's own `logs/<job>_<id>_runtime.log` written via `tee` in `slurm/_lib.sh`. Always check both if output looks missing.
