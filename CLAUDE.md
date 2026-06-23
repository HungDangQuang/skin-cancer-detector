# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Local environment ≠ runtime environment

The local Mac is for editing only. **Do not install Python dependencies locally** (no `pip install`, no `make install-dev` on the Mac, no expectation that `pytest` / `torch` / `sklearn` will import here). The code runs on the UIT Slurm cluster (`slurm.uit.edu.vn`, venv at `${DATASTORE_USER_DIR:-/datastore/keg/hungdang}/venv` — created by `slurm/setup_env.sh`), and that is the only environment that has the full dependency set.

Consequences for verification:
- After editing `src/`, `configs/`, or `slurm/`, run the **`validate-pipeline`** skill (static checks — Python AST + Hydra config compose + slurm lint, no imports needed) instead of trying to import/run code.
- Real correctness verification (pytest, training smoke test) happens on the cluster — submit `slurm/01_prepare_poc.slurm` → `02_poc_teacher.slurm` → `03_poc_student.slurm` or invoke the `poc-smoke-test` skill.
- Do not propose `pip install <x>` to fix a `ModuleNotFoundError` you hit locally — it's expected; the import will resolve on the cluster.

## Modification workflow (mandatory after any code/config/slurm change)

Every edit to project source must be **reviewed, verified, and documented before the task is considered done** — not left for a follow-up. After modifying a file, run this loop automatically (don't wait to be asked). A `PostToolUse` hook in `.claude/settings.json` injects a `[modification-workflow]` reminder naming the right review skill for the edited path; treat that reminder as a required step, not a suggestion.

1. **Code** the change.
2. **Review** with the area-specific skill, routed by what you touched:
   - `src/data/**`, `scripts/prepare_data.py` → **`review-preprocessing`**
   - `src/training/**`, `src/models/**`, `scripts/train_{teacher,student}.py` → **`review-training`**
   - `slurm/**`, `slurm/README.md`, `docs/SLURM.md` → **`review-slurm`**
3. **Propagate to Slurm (if any).** If the change alters how a job is invoked, what it consumes, or what it produces, update the matching `slurm/*.slurm` script **and** its docs (`slurm/README.md`, `docs/SLURM.md`) in the same task. A code change that silently desyncs from its slurm wrapper is a defect.
4. **Verify.** Run **`validate-pipeline`** (static checks — the only verification possible on the Mac). Real correctness (pytest / `poc-smoke-test`) is a cluster step; state explicitly that it's deferred to the cluster rather than claiming it passed.
5. **Document.** Keep the docs and knowledge current: `CLAUDE.md` "Recurring gotchas" for anything non-obvious, the relevant `docs/*.md`, and auto-memory (`MEMORY.md` + the matching memory file). The end state of every task is up-to-date docs, not a TODO to update them later.

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

**Stage 1 — Teacher**: a high-capacity backbone trained standalone using `Trainer` + `BinaryFocalLoss`. Teachers: `efficientnet_b4` (baseline) and the SOTA set `{efficientnetv2_m, convnextv2_base, maxvit_base}`. Pick via `teacher=<name>` (Hydra) or `TEACHER=<name>` (slurm).

**Stage 2 — Student**: one of the baseline backbones `{efficientnet_b0, mobilenetv3_large, mobilevit_s}` or the SOTA mobile-/on-device-latency-optimized set `{mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2}`, trained with `KDTrainer` using `BinaryDistillationLoss`:
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

1. `scripts/prepare_data.py` creates fold CSVs via `StratifiedGroupKFold` (grouped by `patient_id` to prevent leakage) under `splits_dir/fold_{0..4}/train_split.csv` and `val_split.csv`, plus an **independent** `test_split.csv` — carved patient-disjoint + stratified *before* the CV (`test_holdout_splits`, default 6 ≈ 17%), so no fold trains on test patients. (Pre-2026-06-06 this was fold 0's val set → folds 1–4 leaked; see "Recurring gotchas".)
2. `SkinLesionDataModule` reads those CSVs and wraps them in `SkinLesionDataset` (expects columns `image_path`, `label`).
3. `DynamicUndersampledSampler` maintains a ~1:5 malignant:benign ratio, reshuffled each epoch via `datamodule.set_epoch(epoch)`.
4. `build_transforms` returns Albumentations pipelines built **from `configs/augmentation/{light,heavy}.yaml`** (not hard-coded); PIL images are converted to numpy internally before being passed to Albumentations. `light` (default) = the original pipeline; `heavy` = a stronger anti-overfit variant. MixUp/CutMix/CutOut are forbidden in-code (`_FORBIDDEN_OPS` → `raise`). Optional `drop_path_rate` (stochastic depth) per model config, default 0.0/off. See `docs/PREPROCESSING.md §4.1–4.2`.

### Model registry

`src/models/registry.py` maps string names → classes. All models inherit from `BaseModel` (ABC), expose `forward(x) -> Tensor (B,)` returning a single raw logit, and share `freeze_backbone()` / `unfreeze()` helpers. Backbones are loaded from `timm`; the classification head is always `Dropout → Linear(in_features, 1)` via `build_head()`. The SOTA set (efficientnetv2_m, convnextv2_base, maxvit_base, mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2) all use one generic wrapper `TimmBackboneModel` (`src/models/timm_backbone.py`) — there's no per-arch logic, so a single class covers them; the older family wrappers (`EfficientNetModel`/`MobileNetV3Model`/`MobileViTModel`) remain for the baseline backbones. The SOTA set requires `timm>=1.0` (mobilenetv4/fastvit/efficientformerv2 are not in 0.9.x).

To add a new architecture: register it against `TimmBackboneModel` (or a new class if it needs custom logic) in `MODEL_REGISTRY`, and create a matching config under `configs/student/` or `configs/teacher/`. Use `infer_backbone_out_dim(backbone)` for the head input dim, never `backbone.num_features`.

### Evaluation

Primary metric: **pAUC@TPR≥80%** (ISIC 2024 official metric), normalized to [0, 0.2]. Decision threshold is selected via Youden's J statistic. `compute_metrics()` in `src/evaluation/metrics.py` returns `pauc_at_tpr80`, `auc_roc`, `auprc` (+ `prevalence` = its random baseline), `sensitivity`, `specificity`, `f1_score`, fixed-specificity operating points `sens_at_90spec`/`sens_at_95spec`, and raw TP/FP/TN/FN counts. `Evaluator.save_predictions()` also writes `predictions.csv` (`y_true,y_prob,y_pred,source`) next to `test_metrics.json` so PR-curve / AUPRC / per-domain (ISIC-vs-PAD) / bootstrap CIs are recomputable offline without re-running inference. Use **AUPRC**, not AUC-ROC, as the headline at ~0.4% prevalence (AUC-ROC is optimistic).

External test sets (HAM10000, Fitzpatrick17k) are **never used for training** — only for post-hoc cross-domain and fairness evaluation.

### Experiment design

Each student is trained twice (with KD / without KD) using identical hyperparameters, data splits, and seed. `compute_kd_delta()` computes the effectiveness delta between the two runs. 5-fold CV is used; 30 total training runs (3 arch × 2 KD conditions × 5 folds).

### Run-dir convention (fold-aware)

Each training script writes results to a fold-scoped subdirectory so one job can populate all 5 folds without overwriting:

```
experiments/runs/
  teacher/efficientnet_b4/fold_{0..4}/
    checkpoints/best_model.pth
    config.yaml
    test_metrics.json          ← auto-eval on held-out test set, written at end of training
    val_metrics.json           ← best-epoch val metrics (for val-vs-test overfitting gap)
    training_curves.png
  kd_efficientnet_b4_to_efficientnet_b0/fold_{0..4}/...
  kd_efficientnet_b4_to_mobilenetv3_large/fold_{0..4}/...
  kd_efficientnet_b4_to_mobilevit_s/fold_{0..4}/...
```

`scripts/train_teacher.py` and `scripts/train_student.py` reload the best checkpoint from `checkpoints/best_model.pth` after training and run `Evaluator.evaluate(test_dataloader())`, saving the result alongside as `test_metrics.json`. The val-set metrics logged each epoch are *biased* (early-stopping optimizes against val); the `test_metrics.json` is the unbiased generalization number — quote that, not val_pauc, for verdicts. The trainers also write `val_metrics.json` (best-epoch val metrics, aligned to `best_model.pth`); a large **val − test** gap (esp. in AUPRC/pAUC) is the overfitting signal — `val_metrics.json` minus `test_metrics.json`.

### 5-fold CV — one job per model (folds loop sequentially)

`slurm/11_train_teacher.slurm` and `slurm/12_train_student.slurm` are **single** jobs (no Slurm array): each loops `for FOLD in ${FOLDS:-0 1 2 3 4}` internally and calls the training script once per fold, so **one model = one job = one of the 5 concurrency slots**. (This replaced the earlier `#SBATCH --array=0-4%2` design — that ran 2 folds at once but consumed 2 slots and produced 5 separate array tasks per model.) `--time=72:00:00` (the cluster cap) covers all 5 folds back-to-back. `FOLDS="0 1 2"` + `FOLDS="3 4"` splits a heavy run (e.g. `maxvit_base`) across two jobs if 5 sequential folds risk exceeding 72 h. Submit + log pattern:

```bash
# Submit (one command = one job that trains all 5 folds):
bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=efficientnetv2_m

# Logs (single job id, not array):
logs/train_teacher_<jobid>.out             # SBATCH-redirected
logs/train_teacher_<jobid>_runtime.log     # fallback tee log

# Aggregate after the job finishes all 5 folds:
bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
    RUN_DIR=experiments/runs/teacher/efficientnetv2_m
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

### `patient_id` must be namespaced when datasets are concatenated

`generate_group_kfold_splits()` groups by `patient_id` to keep all of a patient's lesions in one fold (no leakage). When ISIC 2024 and PAD-UFES-20 are concatenated, a PAD `patient_id` could numerically collide with an ISIC one, silently merging two unrelated patients into one group (or worse, splitting the same logical group). `process_pad_ufes_20()` therefore writes `patient_id` as `pad_{raw_id}`. Keep any new auxiliary dataset's group key namespaced the same way. Also note: the offline cleaner drops corrupt / too-small (`min_size`) / blank (`is_uninformative`) / exact-duplicate (md5 of resized pixels) images and logs them to `data/processed/<ds>/excluded_images.csv` — dedup is per-dataset and exact-pixel only. See `docs/PREPROCESSING.md` for the full spec and which proposal augmentations were intentionally NOT implemented.

### PAD-UFES-20 `img_id` already includes the file extension — FIXED 2026-06-07

PAD's `metadata.csv` stores `img_id` **with** the extension (e.g. `PAT_8_15_820.png`), and the image files on disk are named identically. The old `process_pad_ufes_20()` did `images_dir / f"{img_id}.png"` → looked for `PAT_8_15_820.png.png`, matched nothing, and `continue`d on **every** row → empty `records` → `KeyError: 'label'` on the summary line (job 28239, the first time PAD ever ran — the repo had been ISIC-only). Fixed: look up `images_dir / img_id` as-is first (then `stem+.png/.jpg` fallbacks for a bare-id mirror), derive processed names from `Path(img_id).stem` (so no `pad_….png.jpg`), and **raise a clear `RuntimeError`** ("0 of N rows produced an image…") instead of a cryptic `KeyError` when nothing matches. Lesson for any new auxiliary dataset: never assume the metadata id is extension-free — probe `head -3 metadata.csv` + `ls images/` first.

### `load_config()` must compose Hydra defaults for the root config

`@hydra.main(...)` composes the `defaults:` list automatically, but our standalone scripts (`prepare_data.py`, etc.) use `src/utils/config.py::load_config("configs/config.yaml")`. Plain `OmegaConf.load` doesn't expand the `defaults:` list, so `cfg.data` is missing → `ConfigKeyError: Missing key data`. `load_config` now detects a `defaults:` key and calls `hydra.compose` to merge the groups. Already-resolved configs (saved `experiments/<run>/config.yaml`) lack `defaults:` and load as-is, so `evaluate.py`/`export_model.py`/`predict.py` are unaffected.

### NumPy 2.0 removed `np.trapz`

`np.trapz(y, x)` is gone — replacement is `np.trapezoid(y, x)` (added in 2.0). The cluster venv has NumPy 2.x. Any new metric/integration code should use `np.trapezoid`.

### `Trainer.history` populates differently from `KDTrainer.history`

`Trainer.history` declares `train_loss`/`val_loss`/`train_pauc`/`val_pauc` but historically only appended to `train_loss` and `val_loss`, leaving `val_pauc` as an empty list. `plot_training_curves` then got `epochs=(N,)` and `val_paucs=()` → matplotlib shape mismatch. Always append `val_pauc` per epoch in any new trainer subclass; `KDTrainer` already does this at `kd_trainer.py:104`.

### `keg` is a shared lab account — `squeue -u keg` shows everyone

When tracking your own jobs, filter by job name: `squeue -u keg --name=poc_teacher`. For postmortems use `sacct -u keg --starttime=$(date -d "1 hour ago" '+%H:%M:%S')`. Per-user job IDs are unique, so any single `squeue -j <jobid>` / `sacct -j <jobid>` still works without a filter.

### `pauc_at_tpr()` — FIXED 2026-06-04, now the real ISIC 2024 metric

Historically [src/evaluation/metrics.py](src/evaluation/metrics.py) integrated raw TPR and divided by 0.2, so values ran ~[0.9, 5.0] instead of [0, 0.2] — they were **not** the official metric. `pauc_at_tpr()` now implements the competition's exact formulation: flip labels/scores (`v_gt = 1 - y_true`, `v_pred = -y_prob`), take `roc_auc_score(v_gt, v_pred, max_fpr=1-min_tpr)` (McClish-corrected), then invert the McClish scaling. Range is now **[0.5·max_fpr², max_fpr] ≈ [0.02, 0.20]** for min_tpr=0.80 (random ≈ 0.02, perfect = 0.20). `tests/test_metrics.py` asserts perfect ≈ 0.2. `val_pauc=…` logs, the `pauc_at_tpr80` JSON field, and `delta_pauc` are now quotable as the ISIC 2024 metric. (The threshold metrics `acc/sens/spec/f1` remain sklearn-direct and correct as before.)

### Baseline (no-KD) student training — FIXED 2026-06-04 via `use_kd` flag

Previously `KDTrainer.__init__` read `cfg.training.distillation` unconditionally and `train_student.py` always built a `KDTrainer`, so any `training=baseline` run crashed with `ConfigAttributeError: Missing key distillation` (jobs 26729/26730/26731, 2026-05-30). Now `scripts/train_student.py` reads `use_kd = cfg.training.get("use_kd", True)` and branches: **`use_kd: true`** (`distillation.yaml`) → `KDTrainer` + frozen teacher + `BinaryDistillationLoss`, run-dir `kd_<teacher>_to_<student>/`; **`use_kd: false`** (`baseline.yaml`) → plain `Trainer` + `BinaryFocalLoss`, no teacher load, run-dir `baseline_<student>/`. The baseline arm of the 30-run experiment is now runnable: `bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=<s> TRAINING=baseline`.

### Data-strategy ablations: `run_suffix` isolation + the two design traps (added 2026-06-21)

The data strategy (PAD mixing + undersampler) is ablated by `slurm/13_ablation_sampler.slurm` and `slurm/14_ablation_pad.slurm`. Three things that will silently invalidate a result if forgotten:

- **`run_suffix` (root `config.yaml`, default `""`)** is appended to the run-dir name (`kd_<teacher>_to_<student><suffix>/fold_N`) so an ablation arm never overwrites the main 30 runs. The ablation slurms set it (`__samp_off`, `__ratio3`, `__train_isic_only`, …). A new ablation that forgets `run_suffix` will clobber a real run.
- **`data.train_sources`** (in `configs/data/isic2024.yaml`, default `null`) filters **TRAIN+VAL only** — `SkinLesionDataModule._filter_to_sources` deliberately leaves the **test set whole** so both PAD-ablation arms share an identical held-out test (its PAD portion trained on by neither). Don't "helpfully" filter the test too; that breaks the comparison. It raises if a filter empties a split.
- **The PAD ablation must run baseline (no KD).** A teacher trained on ISIC+PAD leaks PAD via soft labels into the ISIC-only arm, confounding "does PAD data help". `14_ablation_pad.slurm` defaults `TRAINING=baseline` for this reason — only switch to KD if you also train a matched ISIC-only teacher.

Per-domain (ISIC vs PAD) verdicts read the `source` column in `predictions.csv` (written by `Evaluator.save_predictions`, derived via `source_from_path`). Quote **AUPRC** over AUC-ROC at this prevalence.

### Augmentation is config-driven; don't edit ops in `transforms.py` alone (added 2026-06-21)

`build_transforms` builds the pipeline **from `configs/augmentation/{light,heavy}.yaml`** via an internal `name → Albumentations` registry — it no longer hard-codes the op list (it used to, and silently ignored those YAMLs). Consequences:

- To change augmentation, edit the **YAML**, not `transforms.py`. Adding a new op also needs a builder entry in `_TRANSFORM_BUILDERS`; an unknown `name` raises.
- `augmentation=light` (default) reproduces the original hard-coded pipeline → the 30-run baseline is reproducible. `augmentation=heavy` is the stronger anti-overfit variant.
- **MixUp / CutMix / CoarseDropout(CutOut) are forbidden in code** (`_FORBIDDEN_OPS` → `ValueError`), enforcing the docs/PREPROCESSING.md decision. Don't add them to the YAML expecting them to run.
- `drop_path_rate` (stochastic depth) is a per-model-config knob (default 0.0/off) passed via `create_timm_backbone` only when `>0`. Some timm archs may not accept the kwarg — if a run sets `drop_path_rate>0` and errors with `TypeError`, that arch doesn't support it; verify per-arch on the cluster.
- `val_metrics.json` is a new per-fold output (best-epoch val metrics). `aggregate_folds.py` still reads only `test_metrics.json`; the val file is for the val−test overfitting gap, computed separately.

### `maxvit_base` cuDNN backward error + the `cudnn_deterministic` lever (added 2026-06-23)

POC smoke-test of the 3 SOTA teachers (jobs 32296/32297/32298): `convnextv2_base` and `efficientnetv2_m` PASS; **`maxvit_base` FAILS at `loss.backward()` with `RuntimeError: cuDNN error: CUDNN_STATUS_INTERNAL_ERROR`** (forward completes — not a tag/shape bug; timm tags + head dims of all 3 are confirmed correct). Two likely causes, in order: (1) **VRAM exhaustion** — maxvit_base (~119M + windowed/grid attention) has the largest backward activation footprint, and cuDNN masks workspace-alloc OOM as INTERNAL_ERROR; it failed even at POC batch 16, so batch 64 is worse. (2) deterministic-cuDNN incompatibility. Fixes available (combine both when retrying maxvit):
- **`cudnn_deterministic`** (root `config.yaml`/`config_poc.yaml`, default `true` = the bit-exact 30-run baseline behavior). `set_seed(seed, deterministic=...)` now honors it: `false` → `cudnn.deterministic=False` + `cudnn.benchmark=True` (lets cuDNN pick a working algo). Both training scripts pass `cfg.get("cudnn_deterministic", True)`. Override per-run: `cudnn_deterministic=false`. Only the convnextv2/efficientnetv2_m/maxvit teachers need consider this; the baseline 30 runs keep the default `true`.
- For the VRAM cause: lower `training.batch_size` and raise `acquire_gpu` for maxvit only (it's resolution-locked to 224, so batch is the only memory lever). If it still OOMs at small batch, maxvit_base is impractical on this MPS setup — drop it and keep convnextv2_base/efficientnetv2_m as the SOTA teachers.
- Both levers reach the training scripts via the `EXTRA=` passthrough on `11/12/02/03` (space-separated Hydra overrides, forwarded verbatim and word-split at the call site — quote it as one shell arg). Retry: `bash slurm/submit.sh slurm/02_poc_teacher.slurm TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=8"` (POC), then `slurm/11_train_teacher.slurm TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=16"` (real).
