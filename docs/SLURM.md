# Slurm Training Guide — UIT DGX Cluster

Step-by-step instructions to train the KD pipeline on `slurm.uit.edu.vn`.
Based on the cluster usage rules in `HuongDanSuDungSlurm.pdf`:

- **Working dir**: `/datastore/${USER}` (NOT `/home/${USER}` — 30 GB hard limit there)
- **Limits per user**: 20 MPS slots, 5 concurrent jobs, 32 vCPU cores, 72 h max per job
- **vRAM**: must be declared via `REQUIRED_VRAM`; < 44000 MB on L40, < 80000 MB on A100
- **GPU dispatch**: `gpu_check.sh` returns the best free GPU; codes 10 (requeue) / 11 (fatal after 5 retries)

---

## 0. Connect

```bash
# From outside campus, connect VPN first (UIT credentials).
ssh ${USER}@slurm.uit.edu.vn

# Symlink /datastore → /home for convenience
ln -s /datastore/${USER} /home/${USER}/data

# Clone the repo into /datastore (NOT /home)
cd /datastore/${USER}
git clone <repo-url> skin-cancer-detector
cd skin-cancer-detector
```

---

## 1. One-time environment setup

Run on the **login node** (not a Slurm job):

```bash
bash slurm/setup_env.sh
```

This:
1. `module load shared python312`
2. Creates `/datastore/${USER}/venv`
3. Installs `requirements.txt`, `requirements-dev.txt`, and `pip install -e .`
4. Verifies `torch.cuda.is_available()`
5. Creates `logs/`

Verify:
```bash
source /datastore/${USER}/venv/bin/activate
python -c "import torch, timm, hydra; print('ok')"
```

---

## 2. POC pipeline — synthetic data (no ISIC download needed)

Use this to confirm the whole pipeline works end-to-end (~30 min total).

```bash
# 2.1 Generate synthetic fixtures
sbatch slurm/01_prepare_poc.slurm
# wait for job → check: ls data/splits/poc/fold_0/

# 2.2 Train teacher (2 epochs)
sbatch slurm/02_poc_teacher.slurm
# wait → check: experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth

# 2.3 KD-train student (2 epochs)
sbatch slurm/03_poc_student.slurm
# Or with a different student:
sbatch --export=ALL,STUDENT=mobilenetv3_large slurm/03_poc_student.slurm
sbatch --export=ALL,STUDENT=mobilevit_s       slurm/03_poc_student.slurm
```

Resource budget (per POC job):
- mps: 2 slots (mostly L40)
- mem: 8 GB
- vRAM: 8–10 GB
- time: 1 h

---

## 3. Full training pipeline — real ISIC 2024 data

### 3.1 Upload raw data to `/datastore`

```bash
# from your laptop:
rsync -avh --progress isic2024/ ${USER}@slurm.uit.edu.vn:/datastore/${USER}/skin-cancer-detector/data/raw/isic2024/
```
Required structure:
```
data/raw/isic2024/
├── train-image.hdf5
└── train-metadata.csv
```
(Optional augmentation: `data/raw/pad_ufes_20/{images,metadata.csv}`.)

### 3.2 Preprocess + 5-fold splits

```bash
sbatch slurm/10_prepare_data.slurm
# Output: data/processed/isic2024/{benign,malignant}/, data/splits/isic2024/fold_{0..4}/
```
Time: ~1–4 h depending on disk I/O.

### 3.3 Train teacher

```bash
sbatch slurm/11_train_teacher.slurm
# Output: experiments/runs/teacher/efficientnet_b4/checkpoints/best_model.pth
# Time: ~12–24 h for 50 epochs
```

### 3.4 KD-train all 3 students (parallel — uses 3 of your 5 job slots)

```bash
sbatch --export=ALL,STUDENT=efficientnet_b0    slurm/12_train_student.slurm
sbatch --export=ALL,STUDENT=mobilenetv3_large  slurm/12_train_student.slurm
sbatch --export=ALL,STUDENT=mobilevit_s        slurm/12_train_student.slurm
```

### 3.5 Controlled comparison — train each student WITHOUT KD

```bash
sbatch --export=ALL,STUDENT=efficientnet_b0,TRAINING=baseline    slurm/12_train_student.slurm
sbatch --export=ALL,STUDENT=mobilenetv3_large,TRAINING=baseline  slurm/12_train_student.slurm
sbatch --export=ALL,STUDENT=mobilevit_s,TRAINING=baseline        slurm/12_train_student.slurm
```

This produces 6 student runs (3 archs × {KD, baseline}) for the KD-effectiveness delta.

---

## 4. Evaluation

```bash
# Teacher
sbatch --export=ALL,MODEL=efficientnet_b4,CKPT=experiments/runs/teacher/efficientnet_b4/checkpoints/best_model.pth,OUT=reports/results/teacher.json \
    slurm/20_evaluate.slurm

# KD student
sbatch --export=ALL,MODEL=efficientnet_b0,CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/checkpoints/best_model.pth,OUT=reports/results/kd_b0.json \
    slurm/20_evaluate.slurm
```

Metrics JSON contains: `pauc_at_tpr80` (primary), `auc_roc`, `sensitivity`, `specificity`, `f1_score`, threshold (Youden's J), and TP/FP/TN/FN counts.

---

## 5. Resource budget per script

| Script | mps | mem | vRAM | time | Notes |
|---|---|---|---|---|---|
| `01_prepare_poc` | 1 | 4 G | 2 G | 15 m | CPU-bound |
| `02_poc_teacher` | 2 | 8 G | 8 G | 1 h | 2 epochs B4 |
| `03_poc_student` | 2 | 8 G | 10 G | 1 h | T+S in memory |
| `10_prepare_data` | 1 | 16 G | 2 G | 4 h | HDF5 decode |
| `11_train_teacher` | 4 | 16 G | 14 G | 24 h | B4, batch 32 |
| `12_train_student` | 4 | 16 G | 18 G | 18 h | KD, batch 64 |
| `20_evaluate` | 1 | 8 G | 6 G | 1 h | inference only |

Total MPS at peak (3 students in parallel): 12 of 20 limit. Remaining 8 MPS available for evaluations.

---

## 6. Useful Slurm commands

```bash
squeue -u ${USER}                    # your jobs (PD = pending, R = running)
scancel <jobid>                      # cancel a job
scontrol show job <jobid>            # full info
scontrol show nodes                  # node status
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS,ExitCode  # postmortem

tail -f logs/train_teacher_<jobid>.out    # live log
tail -f logs/train_teacher_<jobid>.err    # live errors

# Quick interactive GPU check
srun --gres=mps:l40:1 --time=00:05:00 --pty nvidia-smi
srun --gres=mps:a100:1 --time=00:05:00 --pty nvidia-smi
```

---

## 7. Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Job stuck PD for hours | Cluster busy; or your `REQUIRED_VRAM` > any free slot. Lower it. |
| Job exits with code 10 in log | `gpu_check.sh` requeued — normal; Slurm will retry up to 5×. |
| Job exits with code 11 in log | 5× requeue exhausted. Free a slot or reduce `REQUIRED_VRAM`. |
| `CUDA out of memory` | Lower `batch_size` in the corresponding `configs/training/*.yaml`, OR raise `REQUIRED_VRAM` and resubmit. |
| `module: command not found` | You're not on the login node / compute node didn't load `shared`. Check `module clear -f && module load shared python312`. |
| Disk quota exceeded on `/home` | Move data out of `/home/${USER}` (30 GB cap). Keep everything under `/datastore/${USER}`. |
| `gpu_check.sh: command not found` | You're on a node where the helper isn't installed — confirm you submitted via `sbatch`, not running locally. |

---

## 8. End-to-end checklist

- [ ] Connected to `slurm.uit.edu.vn` (VPN if off-campus)
- [ ] Repo cloned under `/datastore/${USER}/skin-cancer-detector`
- [ ] `bash slurm/setup_env.sh` succeeded
- [ ] POC: `01 → 02 → 03` finished, `experiments/poc/.../best_model.pth` exists
- [ ] Real data uploaded to `data/raw/isic2024/`
- [ ] `10_prepare_data` finished, splits exist
- [ ] `11_train_teacher` finished, teacher checkpoint exists
- [ ] `12_train_student` finished for all 3 students × {KD, baseline}
- [ ] `20_evaluate` produced metric JSONs in `reports/results/`
- [ ] `compute_kd_delta` aggregated → KD-effectiveness deltas reported
