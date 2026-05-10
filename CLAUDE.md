# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
make install-dev        # Install all deps + pre-commit hooks
cp .env.example .env    # Configure data paths

# Data
make prepare            # Run scripts/prepare_data.py (requires raw data in data/raw/)

# Training (must run teacher before students)
make train-teacher                  # Step 1: Train EfficientNet-B4 teacher
make train-student-b0               # Step 2: KD → EfficientNet-B0
make train-student-mobilenet        # Step 2: KD → MobileNetV3-Large
make train-student-mobilevit        # Step 2: KD → MobileViT-S
make train-all-students             # Run all three students sequentially

# Evaluation
python scripts/evaluate.py --model-name efficientnet_b4 --checkpoint path/to/best_model.pth

# Tests
make test                           # All tests with coverage
pytest tests/test_models.py -v      # Single test file
pytest tests/test_losses.py::TestBinaryFocalLoss -v  # Single test class

# Code quality
make lint       # flake8 + isort check + black check
make format     # Apply isort + black

# Experiment tracking
mlflow ui --backend-store-uri experiments/runs
```

## POC pipeline (synthetic data, no ISIC download)

For end-to-end smoke testing of the whole pipeline in minutes:

```bash
make prepare-poc                    # Generate ~180 synthetic images + split CSVs
make poc-teacher                    # 2-epoch teacher with config_poc
make poc-student                    # 2-epoch KD student
make poc-all                        # All three sequentially
```

The POC config (`configs/config_poc.yaml` + `configs/training/poc.yaml`) uses 2 epochs, batch 16, no warmup, no early stopping. Synthetic images have a learnable color bias (benign=greenish, malignant=reddish) so the model achieves AUC>0.5, confirming gradients flow. See `docs/POC.md` for full details.

## Slurm execution (UIT cluster)

Cluster scripts live in `slurm/`. **Always submit via the wrapper**:
```bash
bash slurm/submit.sh slurm/01_prepare_poc.slurm
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv3_large
```

The wrapper does `mkdir -p logs` before `sbatch` (Slurm 23 silently drops output if `logs/` doesn't exist). Every `*.slurm` script sources `slurm/_lib.sh` which provides `set -euo pipefail`, a fallback `tee` log at `logs/<job>_<jobid>_runtime.log`, a diagnostic header, and helpers `load_python_env` / `acquire_gpu` / `setup_mps`. See `docs/SLURM.md` for the full guide.

## Architecture

This is a **binary skin cancer classification** project (benign=0, malignant=1) using **Knowledge Distillation (KD)**. All models output a single raw logit; `torch.sigmoid()` is applied at inference time.

### Two-stage training pipeline

**Stage 1 — Teacher**: `EfficientNet-B4` trained standalone using `Trainer` + `BinaryFocalLoss`.

**Stage 2 — Student**: One of `{EfficientNet-B0, MobileNetV3-Large, MobileViT-S}` trained with `KDTrainer` using `BinaryDistillationLoss`:
```
L_total = 0.3 * L_focal(student, true_labels) + 0.7 * T² * L_BCE(sigmoid(s/T), sigmoid(t/T))
```
where T=4.0. The teacher is always frozen during student training.

### Config system (Hydra)

All scripts use `@hydra.main(config_path="../configs", config_name="config")`. The root `configs/config.yaml` composes defaults from sub-configs:
- `configs/data/` — dataset paths and split settings
- `configs/teacher/` and `configs/student/` — model name, backbone, head dropout
- `configs/training/` — `distillation.yaml` (KD), `baseline.yaml` (no KD), `default.yaml`
- `configs/augmentation/` — `light.yaml` or `heavy.yaml`

Override at the CLI: `python scripts/train_student.py student=mobilenetv3_large training=baseline`

### Data flow

1. `scripts/prepare_data.py` creates fold CSVs via `StratifiedGroupKFold` (grouped by `patient_id` to prevent leakage) under `splits_dir/fold_{0..4}/train_split.csv` and `val_split.csv`, plus a held-out `test_split.csv`.
2. `SkinLesionDataModule` reads those CSVs and wraps them in `SkinLesionDataset` (expects columns `image_path`, `label`).
3. `DynamicUndersampledSampler` maintains a ~1:5 malignant:benign ratio, reshuffled each epoch via `datamodule.set_epoch(epoch)`.
4. `build_transforms` returns Albumentations pipelines; PIL images are converted to numpy internally before being passed to Albumentations.

### Model registry

`src/models/registry.py` maps string names → classes. All models inherit from `BaseModel` (ABC), expose `forward(x) -> Tensor (B,)` returning a single raw logit, and share `freeze_backbone()` / `unfreeze()` helpers. Backbones are loaded from `timm`; the classification head is always `Dropout → Linear(in_features, 1)` via `build_head()`.

To add a new architecture: create a class in `src/models/`, add it to `MODEL_REGISTRY` in `registry.py`, and create a matching config under `configs/student/` or `configs/teacher/`.

### Evaluation

Primary metric: **pAUC@TPR≥80%** (ISIC 2024 official metric), normalized to [0, 0.2]. Decision threshold is selected via Youden's J statistic. `compute_metrics()` in `src/evaluation/metrics.py` returns `pauc_at_tpr80`, `auc_roc`, `sensitivity`, `specificity`, `f1_score`, and raw TP/FP/TN/FN counts.

External test sets (HAM10000, Fitzpatrick17k) are **never used for training** — only for post-hoc cross-domain and fairness evaluation.

### Experiment design

Each student is trained twice (with KD / without KD) using identical hyperparameters, data splits, and seed. `compute_kd_delta()` computes the effectiveness delta between the two runs. 5-fold CV is used; 30 total training runs (3 arch × 2 KD conditions × 5 folds).

## Recurring gotchas

These have all bitten this repo at least once. Run the `validate-pipeline` skill after touching `src/`, `configs/`, or `slurm/` to catch them before submitting cluster jobs.

### Hydra struct mode

`@hydra.main(...)` returns `cfg` with `struct=True`. Adding a top-level key via merge raises `ConfigKeyError: Key '<X>' is not in struct`. Both training scripts inject `cfg.teacher` / `cfg.student` under a unified `cfg.model` key — that requires disabling struct first:

```python
OmegaConf.set_struct(cfg, False)
teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})
```

### Package re-exports

If `src/<pkg>/__init__.py` re-exports a symbol, the name has to match the actual `class`/`def` in the submodule. Renaming a class without updating `__init__.py` is the easy way to break the whole import graph from a Slurm job (`ImportError: cannot import name 'X' from 'src.<pkg>.<mod>'`). Static check: `python -c "import src.training, src.models, src.data, src.evaluation"`.

### Slurm scripts run under `set -euo pipefail`

`slurm/_lib.sh` enables strict mode for every job. Two consequences:

- Any reference to a Slurm-provided variable must use a `:-default` form, e.g. `${SLURM_JOB_ID:-$$}`. A bare `${SLURM_JOB_ID}` will kill the job with `unbound variable` if Slurm hasn't set it (running outside `sbatch`, or some MPS configurations).
- Cluster CLI tools that aren't on every node (`nvidia-smi`, `gpu_check.sh`) must be gated with `command -v` or `[ -x ... ]` and have a fallback path. The `acquire_gpu` helper in `_lib.sh` already implements the gpu_check.sh / nvidia-smi / default fallback chain.

### `/datastore/${USER}` is wrong on shared lab accounts

On `slurm.uit.edu.vn`, multiple people share the `keg` account, so `${USER}` resolves to `keg` and the per-person subdir lives at `/datastore/keg/<name>/`. Scripts default to `/datastore/keg/hungdang/...` and accept a `DATASTORE_USER_DIR=...` env override. Don't reintroduce raw `/datastore/${USER}/...` — `validate-pipeline §3c` will flag it.

### Always submit through `slurm/submit.sh`

Raw `sbatch` parses `--output=logs/...` before the script runs. If `logs/` doesn't exist at submit time (Slurm 23 silently drops stdout/stderr), you get a job that "ran" with no log. `submit.sh` does `mkdir -p logs` first and forwards env vars via `--export=ALL,VAR=value`. Even if it does fall through, `_lib.sh` writes a fallback `tee` log at `logs/<job>_<jobid>_runtime.log` — always check that file when the SBATCH log is empty.
