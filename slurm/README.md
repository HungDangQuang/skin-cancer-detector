# Slurm runbook — UIT cluster (`slurm.uit.edu.vn`)

Step-by-step to run the project on the UIT cluster. For deeper background see [`../docs/SLURM.md`](../docs/SLURM.md); for failure-mode diagnosis see the `diagnose-training` skill.

## File map

| File | Role | Where it runs |
|---|---|---|
| `setup_env.sh` | One-time: create venv at `/datastore/keg/hungdang/venv` and install deps | login node |
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

## 0. Connect

```bash
ssh keg@slurm.uit.edu.vn              # VPN first if off-campus
cd /datastore/keg/hungdang/skin-cancer-detector
git checkout feature/poc
git pull
```

If cloning fresh:
```bash
mkdir -p /datastore/keg/hungdang && cd /datastore/keg/hungdang
git clone https://github.com/HungDangQuang/skin-cancer-detector.git
cd skin-cancer-detector && git checkout feature/poc
```

---

## 1. One-time environment setup (login node)

```bash
bash slurm/setup_env.sh
```

Creates `/datastore/keg/hungdang/venv`, installs `requirements.txt`, and verifies CUDA. Re-run only if the venv is missing or deps changed.

Expected last line:
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

## 2. Preflight (login node)

```bash
bash slurm/preflight.sh
```

Verifies working dir, venv, modules, Python imports, and runs a 5+2 synthetic-image smoke test. Expected last line:

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

### 4.1 Upload raw data (from laptop)
```bash
rsync -avh --progress isic2024/ keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024/
```

Required structure under `data/raw/isic2024/`: `train-image.hdf5`, `train-metadata.csv`.

### 4.2 Preprocess + 5-fold splits (~4 h, CPU)
```bash
bash slurm/submit.sh slurm/10_prepare_data.slurm
```

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

# Kill
scancel <jobid>
```

---

## 7. Common failures

| Symptom | Fix |
|---|---|
| `Submitted batch job <id>` but `logs/<job>_<id>.out` is empty | Submit via `bash slurm/submit.sh ...` not raw `sbatch`. Also check `logs/<job>_<id>_runtime.log` (fallback tee log written by `_lib.sh`). |
| `ERROR: venv missing at /datastore/keg/hungdang/venv` | Run `bash slurm/setup_env.sh` on the login node. |
| `ERROR: venv ... is missing core dependencies` | The venv was created but `pip install` didn't finish. `rm -rf /datastore/keg/hungdang/venv && bash slurm/setup_env.sh`. |
| `ImportError` / `ConfigKeyError` in the runtime log | Pull latest (`git pull`). If you changed code, run the `validate-pipeline` skill locally before re-submitting. |
| `Teacher checkpoint not found: ...` from student job | Re-run `02_poc_teacher.slurm` (or `11_train_teacher.slurm`) and wait for `[job] DONE` before submitting the student. |
| Job exits with code 10 | `gpu_check.sh` found no free GPU — Slurm requeues automatically. Wait. |
| Job exits with code 11 | 5× requeue exhausted. Lower the `acquire_gpu <vram_mb>` arg in the script, or wait for the cluster to free up. |
| `UserWarning: ... NVIDIA driver ... too old` + training falls back to CPU | Reinstall torch with the matching CUDA build (see §1 — `cu121` works for driver 12.8). |
| `squeue -u keg` doesn't show my job | `keg` is a shared lab account. Use `squeue -u keg --name=<jobname>` or `sacct -u keg --starttime=$(date -d "1 hour ago" '+%H:%M:%S')`. |

---

## 8. Resource budget per script

| Script | mps | mem | vRAM | time | Notes |
|---|---|---|---|---|---|
| `01_prepare_poc` | none | 4 G | — | 15 m | CPU only |
| `02_poc_teacher` | 2 | 8 G | 8 G | 1 h | 2 epochs B4 |
| `03_poc_student` | 2 | 8 G | 10 G | 1 h | Teacher + student in memory |
| `10_prepare_data` | none | 16 G | — | 4 h | HDF5 decode |
| `11_train_teacher` | 4 | 16 G | 14 G | 24 h | B4, batch 32 |
| `12_train_student` | 4 | 16 G | 18 G | 18 h | KD, batch 64 |
| `20_evaluate` | 1 | 8 G | 6 G | 1 h | Inference |

Cluster ceilings: 20 MPS, 5 concurrent jobs, 32 vCPU, 72 h max per job. vRAM ≤44 G on L40, ≤80 G on A100.

---

## 9. Before submitting after any code change

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
