# `run/` — non-Slurm runner (plain GPU server / VM over SSH)

This directory is the **local-server replacement for `slurm/`**. Use it when you
train on your own Linux box with an NVIDIA GPU (SSH), instead of the UIT Slurm
cluster. The Python/Hydra code is unchanged — these scripts only replace the
orchestration layer:

| Concern | Slurm (`slurm/`) | Here (`run/`) |
|---|---|---|
| Deps / venv | `module load` + `/datastore/keg/hungdang/venv` | `run/setup_env.sh` → `./.venv-linux` |
| GPU | `--gres=mps:l40:N` + `gpu_check.sh` | `CUDA_VISIBLE_DEVICES` via `GPU=` |
| 5-fold sweep | fold loop inside `*.slurm` | fold loop inside `run/*.sh` |
| Submit | `bash slurm/submit.sh <job> KEY=VAL` | `bash run/<script>.sh KEY=VAL` |
| Logs | `logs/<job>_<jobid>.out` | `logs/<name>_<timestamp>.log` |

Run-dir layout, config system, metrics, and aggregation are **identical**, so
results are directly comparable to any earlier cluster runs.

> The shared-cluster rules (no-kill / MPS / `/datastore`) do **not** apply here —
> it's your own machine. But this is single-tenant: one training process at a
> time per GPU unless you pin different `GPU=` ids.

## 0. One-time setup

```bash
bash run/setup_env.sh                 # creates ./.venv-linux + installs deps + verifies CUDA
# If torch must match a specific CUDA/driver (see `nvidia-smi` top-right):
TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121 bash run/setup_env.sh
DEV=1 bash run/setup_env.sh           # also install test/lint deps
```

## Data

Raw data does **not** ship with the repo. Put it under `data/raw/` before
`run/prepare_data.sh`:

- **ISIC 2024** (required, primary training):
  <https://www.kaggle.com/competitions/isic-2024-challenge/data> → extract to
  ```
  data/raw/isic2024/train-image.hdf5
  data/raw/isic2024/train-metadata.csv
  ```
  (Kaggle CLI: `kaggle competitions download -c isic-2024-challenge -p data/raw/isic2024 && unzip …`)
- **PAD-UFES-20** (optional, extra malignants):
  <https://data.mendeley.com/datasets/zr7vgbcyr2/1> then stage with
  `bash scripts/setup_pad_ufes_20.sh <zr7vgbcyr2-1.zip>` → produces
  `data/raw/pad_ufes_20/{images/,metadata.csv}`. If absent, prepare runs ISIC-only.
- **HAM10000 / Fitzpatrick17k** — evaluation only, never training.

```bash
bash run/prepare_data.sh              # → data/processed/… + data/splits/isic2024/fold_{0..4}/ + test_split.csv
```

## Train

```bash
# Teacher first (one command trains all 5 folds sequentially):
bash run/train_teacher.sh TEACHER=efficientnet_b4
bash run/train_teacher.sh TEACHER=efficientnetv2_m         # SOTA teacher

# Then students (KD distills from the matching trained teacher):
bash run/train_student.sh STUDENT=mobilenetv3_large
bash run/train_student.sh STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m
bash run/train_student.sh STUDENT=efficientnet_b0 TRAINING=baseline   # no-KD control

# Aggregate the 5 folds into mean ± std (cite THIS, not a single fold):
bash run/aggregate.sh RUN_DIR=experiments/runs/teacher/efficientnet_b4
bash run/aggregate.sh RUN_DIR=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large
```

Common knobs (all `KEY=VALUE`): `FOLDS="0 1 2"`, `GPU=1` (pin a specific GPU),
`GPU=auto` (default — picks the freest GPU), `GPU=cpu`, `AUG=heavy`,
`DROP_PATH=0.1`, `EXTRA="cudnn_deterministic=false training.batch_size=16"`.

## Evaluate one checkpoint

```bash
bash run/evaluate.sh MODEL=mobilenetv3_large \
     CKPT=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_0/checkpoints/best_model.pth
```

## Long runs survive SSH drops

Every script tees to `logs/<name>_<timestamp>.log`. For a full 5-fold run
(hours), detach it so closing the terminal doesn't kill it:

```bash
tmux new -s train
bash run/train_teacher.sh TEACHER=efficientnetv2_m
# Ctrl-b then d to detach;  tmux attach -t train  to return
# or:  nohup bash run/train_teacher.sh TEACHER=efficientnetv2_m &>/dev/null &
```

## Smoke-test the pipeline first (no ISIC download)

```bash
python scripts/prepare_poc_data.py
python scripts/train_teacher.py --config-name config_poc
python scripts/train_student.py --config-name config_poc student=efficientnet_b0
```
