# `run/` — the project's execution layer (plain GPU server / VM over SSH)

Every job in this project is launched from here: `bash run/<script>.sh KEY=VALUE`.
The scripts are only an orchestration layer — the Python/Hydra code underneath is
the same one you edit locally.

| Concern | How `run/` does it |
|---|---|
| Deps / venv | `run/setup_env.sh` → `./.venv-linux` (export tooling: `./.venv-export`) |
| GPU | `CUDA_VISIBLE_DEVICES` via `GPU=` (`auto` picks the freest GPU) |
| 5-fold sweep | fold loop inside the `run/*.sh` script (`FOLDS="0 1 2"` to split) |
| Launch | `bash run/<script>.sh KEY=VALUE` |
| Logs | `logs/<name>_<timestamp>.log` (every script tees, survives SSH drops) |

All scripts source `run/common.sh`, which provides `set -euo pipefail`, repo-root
resolution, `activate_venv`, `select_gpu` and `start_log`.

> This is a **single-tenant** box: one training process at a time per GPU unless
> you pin different `GPU=` ids. Keep everything inside the project folder — no
> sudo, no system python, no shell-rc edits; env vars per session only.

## Script index

| Script | What it does |
|---|---|
| `setup_env.sh` | One-time: create `./.venv-linux`, install deps, verify CUDA |
| `setup_new_server.sh` | Bootstrap a brand-new server (clone + env + data layout) |
| `validate.sh` | Import sanity + Hydra dry-load of every registered model (CPU, ~1 min) |
| `poc.sh` | Synthetic-data smoke test: prepare → teacher → student |
| `prepare_data.sh` | ISIC 2024 (+ PAD-UFES-20) → processed images + fold splits |
| `prepare_external.sh` | HAM10000 / Fitzpatrick17k eval-only sets + leakage check |
| `train_teacher.sh` | One teacher, all 5 folds sequentially |
| `train_student.sh` | One student (KD or baseline), all 5 folds |
| `train_kd_parallel.sh` | VRAM-gated parallel KD launcher (several students at once) |
| `ablation_sampler.sh` | Data-strategy ablation A — undersampling ratio |
| `ablation_pad.sh` | Data-strategy ablation B — PAD mixing (ISIC-only vs ISIC+PAD) |
| `aggregate.sh` | fold_*/test_metrics.json → mean ± std (`aggregated.{json,md}`) |
| `evaluate.sh` | Evaluate one checkpoint on the held-out test set |
| `make_benchmark_set.sh` | Build the fixed 100-image benchmark input set |
| `benchmark.sh` | Params / FLOPs / size / latency profile (`MOBILE=1` for the light subset) |
| `export_model.sh` | Export to ONNX or TorchScript |
| `setup_export_env.sh` | One-time: isolated `./.venv-export` for ExecuTorch |
| `export_executorch.sh` | Export to `.pte` for Android on-device |

## 0. One-time setup

```bash
bash run/setup_env.sh                 # creates ./.venv-linux + installs deps + verifies CUDA
# If torch must match a specific CUDA/driver (see `nvidia-smi` top-right):
TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121 bash run/setup_env.sh
DEV=1 bash run/setup_env.sh           # also install test/lint deps

bash run/validate.sh                  # confirm every model builds in the real venv
```

## 1. Smoke-test the pipeline (no ISIC download)

Synthetic images carry a learnable color bias, so a 2-epoch run reaching AUC > 0.5
proves data → model → loss → gradients → metrics all wire up.

```bash
bash run/poc.sh                       # prepare + teacher + student
bash run/poc.sh STAGE=teacher TEACHER=convnextv2_base
```

## 2. Data

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
- **HAM10000** (cross-domain evaluation only, never training):
  Harvard Dataverse → `data/raw/ham10000/HAM10000_metadata.csv` + the extracted
  image zips (`images/` or `HAM10000_images_part_1/2`).
- **Fitzpatrick17k** (fairness evaluation only, never training): the release ships
  **URLs, not images** — put `fitzpatrick17k.csv` in `data/raw/fitzpatrick17k/`
  and `run/prepare_external.sh` fetches the pictures.

```bash
bash run/prepare_data.sh              # → data/processed/… + data/splits/isic2024/fold_{0..4}/ + test_split.csv

# External EVAL-ONLY sets (CPU-only; writes one test CSV + variants per dataset,
# then a leakage check vs the internal splits — exits 2 on any overlap):
bash run/prepare_external.sh DATASET=ham10000
bash run/prepare_external.sh DATASET=fitzpatrick17k DOWNLOAD_LIMIT=50   # trial run first
```

## 3. Train

```bash
# Teacher first (one command trains all 5 folds sequentially):
bash run/train_teacher.sh                                  # default efficientnetv2_m
bash run/train_teacher.sh TEACHER=convnextv2_base

# Then students (KD distills from the matching trained teacher):
bash run/train_student.sh STUDENT=mobilenetv4_conv_medium            # default teacher efficientnetv2_m
bash run/train_student.sh STUDENT=fastvit_sa12 TEACHER=convnextv2_base
bash run/train_student.sh STUDENT=efficientformerv2_s2 TRAINING=baseline   # no-KD control

# Aggregate the 5 folds into mean ± std (cite THIS, not a single fold):
bash run/aggregate.sh RUN_DIR=experiments/runs/teacher/efficientnetv2_m
bash run/aggregate.sh RUN_DIR=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium
```

Common knobs (all `KEY=VALUE`): `FOLDS="0 1 2"`, `GPU=1` (pin a specific GPU),
`GPU=auto` (default — picks the freest GPU), `GPU=cpu`, `AUG=heavy`,
`DROP_PATH=0.1`, `EXTRA="cudnn_deterministic=false training.batch_size=16"`.

## 4. Data-strategy ablations

Each arm forks into its own run-dir so the main runs are never overwritten.

```bash
# A — undersampling ratio (KD student; teacher is reused frozen, not retrained):
bash run/ablation_sampler.sh SAMP=off      # no resampling
bash run/ablation_sampler.sh SAMP=3        # 1:3   (SAMP=5 == the main run)
bash run/ablation_sampler.sh SAMP=10       # 1:10

# B — PAD mixing (baseline / no-KD by default, so soft labels can't leak PAD):
bash run/ablation_pad.sh ARM=isic_only
bash run/ablation_pad.sh ARM=isic_pad
bash run/ablation_pad.sh ARM=isic_only MODEL_KIND=teacher TEACHER=convnextv2_base
python scripts/analyze_pad_ablation.py --help   # per-domain (ISIC vs PAD) compare
```

> ⚠ The student arm isolates via `run_suffix=`, the teacher arm via `output_dir=`
> — `scripts/train_teacher.py` does **not** read `run_suffix`, so without the
> `output_dir` override a teacher ablation would overwrite the main teacher run.
> That is why the ISIC-only teachers live under `experiments/runs_isic_only/`.

## 5. Evaluate one checkpoint

```bash
bash run/evaluate.sh MODEL=mobilenetv4_conv_medium \
     CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
```

## 6. Benchmark & export (deployment)

```bash
bash run/make_benchmark_set.sh N=100          # fixed input set, reused by PC + phone

bash run/benchmark.sh MODEL=mobilenetv4_conv_medium CKPT=<…>/best_model.pth
bash run/benchmark.sh MODEL=… CKPT=… MOBILE=1   # light subset: params/size/CPU latency
bash run/benchmark.sh MODEL=… CKPT=… DEVICE=cpu # skip the GPU numbers

bash run/export_model.sh MODEL=… CKPT=…                 # → exports/<name>.onnx
bash run/setup_export_env.sh                            # one-time, ./.venv-export
bash run/export_executorch.sh MODEL=… CKPT=…            # → exports/executorch/<name>.pte
```

> ⚠ The CPU latency here is a **proxy, not a phone number**. Only params, FLOPs
> and file size transfer across devices — the latency *ranking* can flip on a
> real phone, especially for the transformer students. See `docs/MOBILE.md`.

## Long runs survive SSH drops

Every script tees to `logs/<name>_<timestamp>.log`. For a full 5-fold run
(hours), detach it so closing the terminal doesn't kill it:

```bash
tmux new -s train
bash run/train_teacher.sh TEACHER=efficientnetv2_m
# Ctrl-b then d to detach;  tmux attach -t train  to return
# or:  nohup bash run/train_teacher.sh TEACHER=efficientnetv2_m &>/dev/null &
```
