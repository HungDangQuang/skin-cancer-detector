# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Local environment ≠ runtime environment

The local Mac is for editing only. **Do not install Python dependencies locally** (no `pip install`, no `make install-dev` on the Mac, no expectation that `pytest` / `torch` / `sklearn` will import here). The code runs on the UIT Slurm cluster (`slurm.uit.edu.vn`, venv at `/datastore/keg/venv`), and that is the only environment that has the full dependency set.

Consequences for verification:
- After editing `src/`, `configs/`, or `slurm/`, run the **`validate-pipeline`** skill (static checks — Python AST + Hydra config compose + slurm lint, no imports needed) instead of trying to import/run code.
- Real correctness verification (pytest, training smoke test) happens on the cluster — submit `slurm/01_prepare_poc.slurm` → `02_poc_teacher.slurm` → `03_poc_student.slurm` or invoke the `poc-smoke-test` skill.
- Do not propose `pip install <x>` to fix a `ModuleNotFoundError` you hit locally — it's expected; the import will resolve on the cluster.

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

### Run-dir convention (fold-aware)

Each training script writes results to a fold-scoped subdirectory so a Slurm array can populate all 5 folds without overwriting:

```
experiments/runs/
  teacher/efficientnet_b4/fold_{0..4}/
    checkpoints/best_model.pth
    config.yaml
    test_metrics.json          ← auto-eval on held-out test set, written at end of training
    training_curves.png
  kd_efficientnet_b4_to_efficientnet_b0/fold_{0..4}/...
  kd_efficientnet_b4_to_mobilenetv3_large/fold_{0..4}/...
  kd_efficientnet_b4_to_mobilevit_s/fold_{0..4}/...
```

`scripts/train_teacher.py` and `scripts/train_student.py` reload the best checkpoint from `checkpoints/best_model.pth` after training and run `Evaluator.evaluate(test_dataloader())`, saving the result alongside as `test_metrics.json`. The val-set metrics logged each epoch are *biased* (early-stopping optimizes against val); the `test_metrics.json` is the unbiased generalization number — quote that, not val_pauc, for verdicts.

### 5-fold CV via Slurm array

`slurm/11_train_teacher.slurm` and `slurm/12_train_student.slurm` are declared as Slurm array jobs (`#SBATCH --array=0-4%2`) so submitting once trains all 5 folds, with at most 2 folds running concurrently to stay under the shared-account 5-job concurrency cap. Each task receives `SLURM_ARRAY_TASK_ID` and forwards it as `data.fold=${SLURM_ARRAY_TASK_ID}`. Submit + log pattern:

```bash
# Submit (one command, kicks off 5 jobs that share an array JOBID):
bash slurm/submit.sh slurm/11_train_teacher.slurm

# Logs:
logs/train_teacher_<arrayid>_<taskid>.out      # SBATCH-redirected per task
logs/train_teacher_<arrayid>_<taskid>_runtime.log   # fallback tee log

# Aggregate after all 5 finish:
bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
    RUN_DIR=experiments/runs/teacher/efficientnet_b4
```

`scripts/aggregate_folds.py` reads `fold_*/test_metrics.json`, computes mean ± std (+ min/max + per-fold) for every numeric metric, and writes `aggregated.json` (machine-readable) and `aggregated.md` (thesis-grade table). Cite the **aggregated mean ± std** for any reportable claim — a single fold's number has wide variance.

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

### Shared-cluster rule for `*.slurm` scripts

UIT's cluster is shared. **No `slurm/*.slurm` script we author may terminate, preempt, or reset other users' work.** If resources are exhausted, the job goes into `PD` (pending) state and waits — that is the only acceptable behavior. Forbidden in every script: `scancel`/`kill`/`pkill`/`killall`, `nvidia-smi --reset-gpu`, `fuser -k`, `#SBATCH --preempt`, priority-bumping `--nice`, and any write to `/tmp/nvidia-mps` without a job-unique suffix. `validate-pipeline §3f / §3g` lint enforces this — see `.claude/skills/submit-slurm/SKILL.md` "Authoring new `*.slurm` scripts" for the full table and the queue-don't-evict rationale.

### `/usr/local/bin/gpu_check.sh` is bypassed by default

The cluster's GPU dispatcher has a typo on line 31 (`nvidia-smi-i` instead of `nvidia-smi -i`) that makes it always false-negative AND it issues `scontrol requeue $SLURM_JOB_ID` internally before returning to us — so any fallback we run gets SIGTERM'd by Slurm seconds later. `_lib.sh::acquire_gpu` therefore picks a GPU itself via `nvidia-smi --query-gpu=memory.free` and skips the helper. Opt back in with `USE_CLUSTER_GPU_CHECK=1` only after UIT admin fixes the typo. **Do not** pass that env var to `submit.sh` in the meantime — it puts the job back into the requeue loop.

### timm `num_features` is unreliable as the head input dim

`timm.create_model(name, num_classes=0).num_features` reports the *pre-classifier* channel count, which is NOT always what `forward(x)` emits. MobileNetV3-Large reports 960 but the `conv_head` expansion runs anyway and the forward output is 1280. Building the head with 960 channels then feeding it 1280 → `RuntimeError: mat1 and mat2 shapes cannot be multiplied (BxC1 and C2x1)`. Always use `infer_backbone_out_dim(backbone)` from `src/models/heads.py` — it runs a one-sample dummy forward and returns the true output dim. EfficientNet and MobileViT happen to be self-consistent, but use the helper for new architectures too as a safety net.

### `cfg.data.label_col` is the *raw* column name, not the in-memory one

`configs/data/isic2024.yaml` sets `label_col: target` because ISIC's `train-metadata.csv` uses that column name. `process_isic2024()` reads `target` from the raw CSV but writes the same value into the processed dataframe under the column name `"label"` (matching `SkinLesionDataset`'s schema). When calling `generate_group_kfold_splits()` on the processed dataframe, pass `label_col="label"` — passing `cfg.data.label_col` ("target") gives `KeyError: 'target'`.

### `load_config()` must compose Hydra defaults for the root config

`@hydra.main(...)` composes the `defaults:` list automatically, but our standalone scripts (`prepare_data.py`, etc.) use `src/utils/config.py::load_config("configs/config.yaml")`. Plain `OmegaConf.load` doesn't expand the `defaults:` list, so `cfg.data` is missing → `ConfigKeyError: Missing key data`. `load_config` now detects a `defaults:` key and calls `hydra.compose` to merge the groups. Already-resolved configs (saved `experiments/<run>/config.yaml`) lack `defaults:` and load as-is, so `evaluate.py`/`export_model.py`/`predict.py` are unaffected.

### NumPy 2.0 removed `np.trapz`

`np.trapz(y, x)` is gone — replacement is `np.trapezoid(y, x)` (added in 2.0). The cluster venv has NumPy 2.x. Any new metric/integration code should use `np.trapezoid`.

### `Trainer.history` populates differently from `KDTrainer.history`

`Trainer.history` declares `train_loss`/`val_loss`/`train_pauc`/`val_pauc` but historically only appended to `train_loss` and `val_loss`, leaving `val_pauc` as an empty list. `plot_training_curves` then got `epochs=(N,)` and `val_paucs=()` → matplotlib shape mismatch. Always append `val_pauc` per epoch in any new trainer subclass; `KDTrainer` already does this at `kd_trainer.py:104`.

### `keg` is a shared lab account — `squeue -u keg` shows everyone

When tracking your own jobs, filter by job name: `squeue -u keg --name=poc_teacher`. For postmortems use `sacct -u keg --starttime=$(date -d "1 hour ago" '+%H:%M:%S')`. Per-user job IDs are unique, so any single `squeue -j <jobid>` / `sacct -j <jobid>` still works without a filter.

### `pauc_at_tpr()` is mis-scaled — values run ~[0.9, 5.0] not [0, 0.2]

[src/evaluation/metrics.py:37](src/evaluation/metrics.py#L37) integrates raw TPR instead of `(TPR − min_tpr)` and divides by `0.2`, so the value lives roughly in `[0.9, 5.0]` instead of the documented `[0, 0.2]`. Random ≈ 0.9, perfect ≈ 5.0. The ranking is monotonic so within-run trends are still meaningful, but every `val_pauc=…` line in the trainer logs, the `pauc_at_tpr80` field in `scripts/evaluate.py` JSON output, and the `delta_pauc` from `compute_kd_delta()` are on this stretched scale — **don't quote them as the ISIC 2024 official metric**. For absolute verdicts and cross-run comparison, lean on the threshold-based metrics (`acc`, `sens`, `spec`, `f1`) which are computed from sklearn directly and are correct. Fix: replace the integrand with the standard sklearn-based formulation (`roc_auc_score(1 - y_true, -y_prob, max_fpr=0.2)`); also update `tests/test_metrics.py` which currently asserts `pauc > 0.9` for a perfect classifier (would become `pauc ≈ 0.2`).

### Baseline (no-KD) student training is broken — KDTrainer is unconditionally coupled to KD config

`KDTrainer.__init__` reads `cfg.training.distillation` at [src/training/kd_trainer.py:57](src/training/kd_trainer.py#L57), but `configs/training/baseline.yaml` intentionally has no `distillation:` block. Any `training=baseline` override therefore crashes immediately with `ConfigAttributeError: Missing key distillation` — confirmed by jobs 26729 / 26730 / 26731 on 2026-05-30. **This blocks the entire baseline arm of the KD-vs-baseline experiment** (the experiment design wants 3 archs × 2 conditions × 5 folds = 30 runs; the baseline column is currently unrunnable). Fix: add `use_kd: true/false` flags to the two training configs and gate the distillation-config read + `BinaryDistillationLoss` construction behind it, falling through to `Trainer` + `BinaryFocalLoss` when off. Do **not** submit baseline jobs to the cluster until this is fixed — guaranteed crash, wastes the queue slot.
