# Slurm runbook — UIT cluster (`slurm.uit.edu.vn`)

Step-by-step to run the project on the UIT cluster. For deeper background see [`../docs/SLURM.md`](../docs/SLURM.md); for failure-mode diagnosis see the `diagnose-training` skill.

## File map

| File | Role | Where it runs |
|---|---|---|
| `setup_env.sh` | **First-time only** — create venv at `/datastore/keg/hungdang/venv` and install deps | login node |
| `preflight.sh` | Verify env + tiny CPU smoke test before submitting | login node |
| `submit.sh` | sbatch wrapper — does `mkdir -p logs` first, forwards `VAR=value` | login node |
| `_lib.sh` | Shared bash library sourced by every `*.slurm` (strict mode, tee log, helpers) | inside jobs |
| `_template.slurm` | Copy-and-customize starting point | reference |
| `01_prepare_poc.slurm` | Synthetic POC fixtures (CPU only) | sbatch |
| `02_poc_teacher.slurm` | POC teacher, 2 epochs | sbatch |
| `03_poc_student.slurm` | POC KD student, 2 epochs | sbatch |
| `10_prepare_data.slurm` | Real ISIC 2024 preprocessing + 5-fold splits | sbatch |
| `11_train_teacher.slurm` | Full B4 teacher (50 epochs) | sbatch |
| `12_train_student.slurm` | Full KD student | sbatch |
| `20_evaluate.slurm` | Evaluate any checkpoint | sbatch |

**Working dir on cluster:** `/datastore/keg/hungdang/skin-cancer-detector`. Override with `DATASTORE_USER_DIR=...` if your account is elsewhere.

---

## What to re-run when

| Situation | Re-run |
|---|---|
| **Reconnecting after a previous session** (most common) | Nothing in `slurm/`. Just SSH, `cd`, `git pull`, `bash slurm/submit.sh …`. |
| **First time ever on this cluster account** | §1 `setup_env.sh` (creates venv) → §2 `preflight.sh` (smoke test). |
| **After `git pull` brings new code** | Optional: `bash slurm/preflight.sh` to confirm Python imports still resolve (30 s). |
| **After `requirements.txt` changes** | `bash slurm/setup_env.sh` (re-runs `pip install -r requirements.txt` on the existing venv). |
| **`venv` got corrupted** (e.g. `ModuleNotFoundError` returns) | `rm -rf /datastore/keg/hungdang/venv && bash slurm/setup_env.sh`. |

The venv at `/datastore/keg/hungdang/venv` and the cloned repo live on persistent storage — they survive SSH disconnects, reboots, and weeks of you not logging in.

---

## 0. Connect

```bash
ssh keg@slurm.uit.edu.vn              # VPN first if off-campus
cd /datastore/keg/hungdang/skin-cancer-detector
git pull
```

If cloning fresh (first time):
```bash
mkdir -p /datastore/keg/hungdang && cd /datastore/keg/hungdang
git clone https://github.com/HungDangQuang/skin-cancer-detector.git
cd skin-cancer-detector && git checkout feature/poc
```

---

## Returning user — just submit

If §1 was done previously and the venv at `/datastore/keg/hungdang/venv` exists, skip to §3 (POC) or §4 (full pipeline). A typical reconnect session:

```bash
ssh keg@slurm.uit.edu.vn
cd /datastore/keg/hungdang/skin-cancer-detector
git pull
bash slurm/submit.sh slurm/<script>.slurm [VAR=value ...]
tail -f logs/<jobname>_<jobid>_runtime.log
```

That's it. No setup, no preflight, no venv-activation needed — the slurm scripts source `_lib.sh` which activates the venv inside each job automatically.

---

## 1. First-time environment setup (login node) — ONE TIME

Only on a fresh account, or after `rm -rf /datastore/keg/hungdang/venv`. Skip this section on reconnects.

```bash
bash slurm/setup_env.sh
```

Creates `/datastore/keg/hungdang/venv`, installs `requirements.txt`, and verifies CUDA. Expected last line:

```
torch: 2.x.x | cuda available: True
Setup complete.
```

If `cuda available: False`, install a torch wheel that matches the cluster's CUDA driver (currently 12.8):
```bash
source /datastore/keg/hungdang/venv/bin/activate
pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## 2. Preflight (login node) — optional but recommended after pulls

```bash
bash slurm/preflight.sh
```

Verifies working dir, venv, modules, Python imports, and runs a 5+2 synthetic-image smoke test (~30 seconds total). Expected last line:

```
=== All checks passed. Ready to submit jobs. ===
```

Fix any `[FAIL]` line before continuing. `[WARN]` lines are informational (e.g. `gpu_check.sh` is correctly absent on the login node).

---

## 3. POC pipeline (synthetic data — ~30 min total)

Run in order. Each step depends on the previous one's output.

### 3.1 Generate synthetic data (~1 min, CPU)

```bash
bash slurm/submit.sh slurm/01_prepare_poc.slurm
```

Wait for completion, then verify:
```bash
ls data/processed/poc/{benign,malignant} | head
ls data/splits/poc/fold_0/
```

### 3.2 POC teacher (~5–15 min, GPU)

```bash
bash slurm/submit.sh slurm/02_poc_teacher.slurm
# note the "Submitted batch job <jobid>" line, then:
tail -f logs/poc_teacher_<jobid>_runtime.log
```

Done when the log ends with:
```
[INFO] Teacher training complete. Checkpoint: experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth
[job] DONE
```

Verify before moving on:
```bash
ls -lh experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth
```

### 3.3 POC KD student (~5–10 min, GPU)

```bash
bash slurm/submit.sh slurm/03_poc_student.slurm
# Different student arch:
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv3_large
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilevit_s
```

Verify:
```bash
ls -lh experiments/poc/kd_efficientnet_b4_to_efficientnet_b0/checkpoints/best_model.pth
```

---

## 4. Full pipeline (real ISIC 2024)

### 4.1 Get raw data onto the server

**Option A — Kaggle CLI on the server** (recommended; no local download/upload):
```bash
# One-time: drop your kaggle.json at ~/.kaggle/kaggle.json (chmod 600)
# Then accept the competition rules in the browser, and:
source /datastore/keg/hungdang/venv/bin/activate
pip install kaggle
cd /datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024
kaggle competitions download -c isic-2024-challenge
unzip -q isic-2024-challenge.zip
rm isic-2024-challenge.zip
rm -rf train-image/ test-image/ test-image.hdf5  # keep only the HDF5 + CSV
```

**Option B — rsync from laptop**:
```bash
ssh keg@slurm.uit.edu.vn "mkdir -p /datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024"
rsync -avh --progress --partial \
    ~/Downloads/isic-2024-challenge.zip \
    keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024/
# Then SSH in, unzip as in Option A.
```

Required structure under `data/raw/isic2024/`: `train-image.hdf5`, `train-metadata.csv`.

### 4.2 Preprocess + 5-fold splits (~45 min cold, ~2 min warm — idempotent)
```bash
bash slurm/submit.sh slurm/10_prepare_data.slurm
```
The script skips re-extracting images whose JPG already exists on disk, so retries after a downstream bug fix are fast.

### 4.3 Teacher (~24 h, GPU)
```bash
bash slurm/submit.sh slurm/11_train_teacher.slurm
```

### 4.4 Students × {KD, baseline} (~18 h each)
```bash
# KD
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s
# Baseline (no KD)
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0    TRAINING=baseline
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large  TRAINING=baseline
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s        TRAINING=baseline
```

---

## 5. Evaluate a checkpoint

```bash
bash slurm/submit.sh slurm/20_evaluate.slurm \
    MODEL=efficientnet_b0 \
    CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/checkpoints/best_model.pth \
    OUT=reports/results/kd_b0.json
```

Metrics JSON contains `pauc_at_tpr80`, `auc_roc`, `sensitivity`, `specificity`, `f1_score`, threshold, TP/FP/TN/FN.

---

## 6. Tracking a job

```bash
# squeue -u keg shows EVERYONE on the shared account; filter by name:
squeue -u keg --name=poc_teacher

# Live logs
tail -f logs/poc_teacher_<jobid>_runtime.log     # always-written tee log (preferred)
tail -f logs/poc_teacher_<jobid>.out             # SBATCH-redirected stdout
tail -f logs/poc_teacher_<jobid>.err             # SBATCH-redirected stderr

# Postmortem after a job ends
sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode,WorkDir

# Kill your own job (never anyone else's)
scancel <jobid>
```

### Pulling logs back to your laptop

Logs are written to `/datastore/keg/hungdang/skin-cancer-detector/logs/` on the cluster. To read them in your editor / share with Claude on the Mac, rsync them back after the job finishes:

```bash
# From your laptop. Pull only the new log files for this jobid:
rsync -avh --progress \
    "keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/logs/*_<jobid>*" \
    logs/

# Or sync the whole logs/ dir (cheap — they're small text files):
rsync -avh --progress --delete-excluded --include='*.out' --include='*.err' --include='*.log' \
    keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/logs/ \
    logs/
```

Pull *after* you see `[job] DONE` (or the job failed) — tailing a remote log in real-time is faster done with `ssh keg@slurm.uit.edu.vn "tail -f /datastore/keg/hungdang/skin-cancer-detector/logs/<jobname>_<jobid>_runtime.log"`. The Mac copy is for post-hoc analysis only.

---

## 7. GPU dispatch — current state

`_lib.sh::acquire_gpu` **bypasses `/usr/local/bin/gpu_check.sh` by default** and picks a GPU itself via `nvidia-smi --query-gpu=index,memory.free`. The cluster helper currently has a typo on line 31 (`nvidia-smi-i` instead of `nvidia-smi -i`) that makes it false-negative *and* it issues `scontrol requeue` internally — so once it runs against us, Slurm requeues no matter what our fallback says.

Until UIT admin fixes that typo, every job's log starts with:
```
[lib] Step A: nvidia-smi at /usr/bin/nvidia-smi
[lib] Step B: querying GPU free memory (30s timeout)...
[lib] Step C: nvidia-smi exit=0, ~X bytes returned:
    0, 45921
    1, 45262
    ...
[lib] Step D: selecting GPU with free vRAM >= 14336 MB...
[lib] Step E: picked='N'
[lib] CUDA_VISIBLE_DEVICES=N (selected via nvidia-smi)
```

**Do not** pass `USE_CLUSTER_GPU_CHECK=1` to `submit.sh` — that re-enables the broken helper. The env var is only for after the cluster admin patches the typo.

---

## 8. Common failures

| Symptom | Fix |
|---|---|
| `Submitted batch job <id>` but `logs/<job>_<id>.out` is empty | Submit via `bash slurm/submit.sh ...` not raw `sbatch`. Also check `logs/<job>_<id>_runtime.log` (fallback tee log written by `_lib.sh`). |
| Log shows endless `gpu_check.sh exited 10 — falling through to nvidia-smi` followed by requeue | You passed `USE_CLUSTER_GPU_CHECK=1`. Remove it and re-submit — see §7. |
| `ERROR: venv missing at /datastore/keg/hungdang/venv` | Run `bash slurm/setup_env.sh` on the login node (§1). |
| `ERROR: venv ... is missing core dependencies` | The venv was created but `pip install` didn't finish. `rm -rf /datastore/keg/hungdang/venv && bash slurm/setup_env.sh`. |
| `ImportError` / `ConfigKeyError` in the runtime log | `git pull` for the latest fixes. If you changed code yourself, run the `validate-pipeline` skill locally before re-submitting. |
| `Teacher checkpoint not found: ...` from student job | Re-run `02_poc_teacher.slurm` (or `11_train_teacher.slurm`) and wait for `[job] DONE` before submitting the student. |
| `UserWarning: ... NVIDIA driver ... too old` + training falls back to CPU | Reinstall torch with the matching CUDA build (see §1 — `cu121` works for driver 12.8). |
| `squeue -u keg` doesn't show my job | `keg` is a shared lab account. Use `squeue -u keg --name=<jobname>` or `sacct -u keg --starttime=$(date -d "1 hour ago" '+%H:%M:%S')`. |
| `CUDA_OUT_OF_MEMORY` early in training | GPU 0 was the fallback default and is full. Re-submit — `acquire_gpu` will pick a freer GPU on the next attempt; or wait for cluster to drain. |
| `No space left on device` during preprocessing | `df -h /datastore/keg/hungdang/`. Remove the raw zip (`isic-2024-challenge.zip`) and the redundant `train-image/` JPG folder (HDF5 is what we read). |

---

## 9. Resource budget per script

| Script | mps | mem | vRAM | time | Notes |
|---|---|---|---|---|---|
| `01_prepare_poc` | none | 4 G | — | 15 m | CPU only |
| `02_poc_teacher` | 2 | 8 G | 8 G | 1 h | 2 epochs B4 |
| `03_poc_student` | 2 | 8 G | 10 G | 1 h | Teacher + student in memory |
| `10_prepare_data` | none | 16 G | — | 4 h | HDF5 decode (idempotent across re-runs) |
| `11_train_teacher` | 4 | 16 G | 14 G | 24 h | B4, batch 32 |
| `12_train_student` | 4 | 16 G | 18 G | 18 h | KD, batch 64 |
| `20_evaluate` | 1 | 8 G | 6 G | 1 h | Inference |

Cluster ceilings: 20 MPS, 5 concurrent jobs, 32 vCPU, 72 h max per job. vRAM ≤44 G on L40, ≤80 G on A100.

---

## 10. Before submitting after any code change

Run the `validate-pipeline` skill (`.claude/skills/validate-pipeline/`):

```bash
# Python imports — catches __init__ re-export mismatches
python -c "from src.training import Trainer, KDTrainer, BinaryDistillationLoss; print('ok')"

# Hydra dry-load — catches struct-mode merge errors before training starts
python -c "
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf
import os
with initialize_config_dir(version_base=None, config_dir=os.path.abspath('configs')):
    cfg = compose(config_name='config_poc')
    OmegaConf.set_struct(cfg, False)
    OmegaConf.merge(cfg, {'model': OmegaConf.to_container(cfg.teacher, resolve=True)})
print('ok')
"
```

Both should print `ok`. Anything else means the cluster job will fail at the same point — fix locally.
