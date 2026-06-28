---
name: submit-slurm
description: Submit a Slurm job on the UIT cluster (slurm.uit.edu.vn) AND author new slurm/*.slurm scripts safely. Use when the user asks to run training/eval/data-prep on the cluster, mentions sbatch, says "submit job", "queue job", "create a slurm file/script", "add a new slurm job", or asks about Slurm in general. Wraps slurm/submit.sh and forwards env vars. Enforces the shared-cluster rule that no slurm script may terminate, preempt, or reset other users' running jobs — if resources are exhausted, the job waits in queue.
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
- Pass `USE_CLUSTER_GPU_CHECK=1` to `submit.sh`. The cluster's `/usr/local/bin/gpu_check.sh` is currently broken (typo on line 31) and issues `scontrol requeue` internally — passing that env var puts the job into an infinite requeue loop. `_lib.sh::acquire_gpu` bypasses the helper by default. Only re-enable once UIT admin patches the typo.

## Before submitting after any code change

Run the `validate-pipeline` skill (`.claude/skills/validate-pipeline/`) — it does Python imports + Hydra config dry-load + slurm script lint in seconds. Catches `ImportError`, `ConfigKeyError` (struct mode), unbound Slurm vars, ungated `nvidia-smi`, and hardcoded `/datastore/${USER}/...` — all of which we've actually shipped to the cluster on this project.

## Authoring new `*.slurm` scripts — non-negotiable rules

The UIT cluster is shared across many users. **Any new `slurm/*.slurm` script you write MUST NOT terminate, preempt, or reset other people's work.** If our job can't get the resources it needs, Slurm queues it (`PD` state) and waits — that is the only acceptable behavior.

### NEVER include any of these in a slurm script

| Forbidden | Why |
|---|---|
| `scancel <jobid>` for any job we don't own | Cancels someone else's work. |
| `kill`, `pkill`, `killall` targeting GPU/python processes | Kills other users' training. |
| `nvidia-smi --reset-gpu`, `nvidia-smi -r`, `nvidia-smi --gpu-reset` | Resets the device for *every* user on it. |
| `fuser -k`, `lsof | xargs kill`, or anything that signals by file/port | Same blast-radius problem. |
| `#SBATCH --preempt` flags, `#SBATCH --requeue` combined with priority bumps, `#SBATCH --nice=-N` | Tries to evict lower-priority jobs. Just queue normally. |
| Manipulating the system-wide MPS daemon (anything that touches `/tmp/nvidia-mps` without a job-specific suffix) | All jobs on the node share that daemon. |
| Custom `trap` handlers that `kill -- -$$` or `kill -9` parent processes | Risk of broader signal propagation than intended. |

### Required for any GPU-using script

- **Request `--gres=mps:l40:N` (e.g. `mps:l40:4`), NEVER `--gres=gpu`.** QOS `uit` caps `gres/gpu=0` per user, so any whole-GPU request sits in `PD` forever with `Reason=QOSMaxGRESPerUser` even while you hold 0 GPUs. `mps:l40:4` keeps the 5-concurrent-job model (20-unit MPS budget ÷ 4). Always pair it with `setup_mps` from `_lib.sh`. (See `docs/GOTCHAS.md` "QOS caps gres/gpu=0".)

### What to do instead when resources are scarce

- Just submit normally via `bash slurm/submit.sh slurm/<script>.slurm`. Slurm puts the job in **`PD` (pending)** state and runs it as soon as resources are free.
- If `_lib.sh::acquire_gpu` returns exit code **10** (no GPU available), the script exits with code 0 and Slurm **automatically requeues**. No special handling needed.
- If you need to bound how long a job waits in queue, use `#SBATCH --time-min=...` (lets the scheduler start it earlier with less time) — never priority/preemption flags.
- For your own old jobs you want to clean up, use `scancel <jobid>` interactively from the shell — **never** baked into a `*.slurm` file.

Every new slurm script gets its private MPS pipe directory via `setup_mps` (`/tmp/nvidia-mps-job<JOBID>`) — that path is per-job-unique, so the `rm -rf` in there cannot collide with another user's MPS state.

Run `validate-pipeline §3` after writing a new slurm script — its lint catches `scancel`, `--preempt`, `nvidia-smi --reset`, and other forbidden patterns.

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
- **Working dir:** the repo on the cluster, e.g. `/datastore/keg/hungdang/skin-cancer-detector` (the `DATASTORE_USER_DIR` default). **Not** `/datastore/${USER}/...` — `${USER}` is the shared `keg` account, so that resolves to a shared path rather than your per-person dir. Never put data or runs under `/home/${USER}` (30 GB cap).
- **Resource limits:** 20 MPS, 5 concurrent jobs, 32 vCPU cores, 72 h max per job. vRAM ≤44 GB on L40, ≤80 GB on A100.
- **Two log paths per job:** SBATCH-redirected `logs/<job>_<id>.out` AND the script's own `logs/<job>_<id>_runtime.log` written via `tee` in `slurm/_lib.sh`. Always check both if output looks missing.
