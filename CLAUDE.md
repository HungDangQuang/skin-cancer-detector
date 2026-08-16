# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL — running jobs on the shared GPU server

Two rules that have cost real work before. Treat them as the highest-priority rule set, not gotchas. Both are linted by `validate-pipeline §3d/§3e`. Full detail: [docs/GOTCHAS.md](docs/GOTCHAS.md); review checklist in [code-change/reference/review-runner.md](.claude/skills/code-change/reference/review-runner.md).

1. **Everything stays inside the project folder.** The box (`islabworker2@islab-server2`, repo on the NAS at `/mnt/sharednas/binhnt/hungdang/skin-cancer-detector`) is shared with other people. No `sudo`, no `apt install`, no system python, no `~/.bashrc` edits, and never kill another person's process (`pkill`/`killall`/`nvidia-smi --reset-gpu`/`fuser -k`). Dependencies live only in `./.venv-linux` (export tooling in `./.venv-export`); env vars are set per session. The user audits this.
2. **Never overwrite an existing run-dir.** Ablations and variants fork: students with `run_suffix=`, **teachers with `output_dir=`** — `scripts/train_teacher.py:39` hard-wires `<output_dir>/teacher/<name>/fold_N` and does *not* read `run_suffix`, so a teacher variant launched with `run_suffix=` silently destroys the main teacher run. That is why the ISIC-only teacher arm lives under `experiments/runs_isic_only/`.

Also: the server root `/` has hit 100% full, so set a per-session `TMPDIR="$(pwd)/.tmp"` before long jobs; and pin `GPU=<id>` when running two jobs at once (`GPU=auto` picks the freest card, so two launches can collide).

## Local environment ≠ runtime environment

The local Mac is for editing only. **Do not install Python dependencies locally** (no `pip install`, no `make install-dev` on the Mac, no expectation that `pytest` / `torch` / `sklearn` will import here). The code runs on the Linux GPU server (venv at `./.venv-linux`, created by `run/setup_env.sh`), and that is the only environment that has the full dependency set.

Consequences for verification:
- After editing `src/`, `configs/`, or `run/`, run the **`code-change`** skill's **`validate-pipeline`** checks (static checks — Python AST + Hydra config compose + runner lint, no imports needed) instead of trying to import/run code.
- Real correctness verification happens on the server: `bash run/validate.sh` (imports + Hydra dry-load of every registered model, ~1 min) then `bash run/poc.sh` (synthetic end-to-end smoke test), or invoke the `code-change` skill's `poc-smoke-test`.
- Do not propose `pip install <x>` to fix a `ModuleNotFoundError` you hit locally — it's expected; the import will resolve on the server.

## Modification workflow (mandatory after any code/config/runner change)

Every edit to project source must be **reviewed, verified, and documented before the task is considered done** — not left for a follow-up. After modifying a file, run this loop automatically (don't wait to be asked). A `PostToolUse` hook in `.claude/settings.json` injects a `[modification-workflow]` reminder naming the **`code-change`** skill and the review area for the edited path; treat that reminder as a required step, not a suggestion.

1. **Code** the change.
2. **Review** with the **`code-change`** skill, which routes by what you touched to the matching checklist in its `reference/`:
   - `src/data/**`, `scripts/prepare_data.py` → `reference/review-preprocessing.md`
   - `src/training/**`, `src/models/**`, `scripts/train_{teacher,student}.py` → `reference/review-training.md`
   - `run/**`, `run/README.md` → `reference/review-runner.md`
3. **Propagate to the runner (if any).** If the change alters how a job is invoked, what it consumes, or what it produces, update the matching `run/*.sh` script **and** `run/README.md` in the same task. A code change that silently desyncs from its runner script is a defect.
4. **Verify.** Run the **`code-change`** skill's **validate-pipeline** checks (`reference/validate-pipeline.md` — static checks, the only verification possible on the Mac). Real correctness (`bash run/validate.sh`, pytest, the `reference/poc-smoke-test.md` smoke test) is a server step; state explicitly that it's deferred to the server rather than claiming it passed.
5. **Document.** Keep the docs and knowledge current: `CLAUDE.md` "Recurring gotchas" for anything non-obvious, the relevant `docs/*.md`, and auto-memory (`MEMORY.md` + the matching memory file). The end state of every task is up-to-date docs, not a TODO to update them later.

## Commands

```bash
# Setup
make install-dev        # Install all deps + pre-commit hooks
cp .env.example .env    # Configure data paths

# Data
make prepare            # Run scripts/prepare_data.py (requires raw data in data/raw/)

# Training (must run teacher before students)
make train-teacher                  # Step 1: Train EfficientNetV2-M teacher (default)
make train-student-mobilenetv4      # Step 2: KD → MobileNetV4-Conv-Medium
make train-student-fastvit          # Step 2: KD → FastViT-SA12
make train-student-efficientformer  # Step 2: KD → EfficientFormerV2-S2
make train-all-students             # Run all three students sequentially

# Evaluation
python scripts/evaluate.py --model-name efficientnetv2_m --checkpoint path/to/best_model.pth

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

## Server execution (`run/`)

Every job is launched from `run/` with `KEY=VALUE` args:
```bash
bash run/poc.sh                                                   # synthetic smoke test
bash run/train_teacher.sh TEACHER=efficientnetv2_m                # all 5 folds, sequential
bash run/train_student.sh STUDENT=mobilenetv4_conv_medium GPU=1
```

Every `run/*.sh` sources `run/common.sh`, which provides `set -euo pipefail`, repo-root resolution, `activate_venv` (`./.venv-linux`), `select_gpu` (`GPU=auto|<id>|cpu` → `CUDA_VISIBLE_DEVICES`; `auto` picks the freest card) and `start_log` (tees everything to `logs/<name>_<timestamp>.log`, so a dropped SSH session doesn't lose the run). Launch long runs under `tmux`/`nohup`. See [run/README.md](run/README.md) for the full script index and guide.

## Architecture

> **Quick-load map:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) is the one-file architecture + pipeline map (dir tree, model registry, config groups, run-dirs, execution backends) for getting a new session up to speed fast. Keep it in sync when the pipeline changes.

This is a **binary skin cancer classification** project (benign=0, malignant=1) using **Knowledge Distillation (KD)**. All models output a single raw logit; `torch.sigmoid()` is applied at inference time.

### Two-stage training pipeline

**Stage 1 — Teacher**: a high-capacity backbone trained standalone using `Trainer` + `BinaryFocalLoss`. Teachers: the SOTA set `{efficientnetv2_m, convnextv2_base, maxvit_base}`. Pick via `teacher=<name>` (Hydra) or `TEACHER=<name>` (`run/*.sh`).

**Stage 2 — Student**: one of the SOTA mobile-/on-device-latency-optimized backbones `{mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2, repvit_m1_0}`, trained with `KDTrainer` using `BinaryDistillationLoss`:
```
L_total = 0.3 * L_focal(student, true_labels) + 0.7 * T² * L_BCE(sigmoid(s/T), sigmoid(t/T))
```
where T=4.0. The teacher is always frozen during student training.

Two opt-in KD variants leave this default untouched: `training.distillation.soft_loss_type=mse` swaps the soft term for MSE on the raw logits (Kim et al. 2021 — no temperature, no T²), and `training=distillation_rkd` adds a Relational-KD feature term (`RKDLoss` in `src/training/feature_distillation.py`, Park et al. 2019 — matches within-batch distance+angle, projector-free so teacher/student dims may differ) on top of the logit KD loss. Both default off (`soft_loss_type: bce`, no `feature_kd` block), so the main KD/baseline runs are byte-for-byte unchanged; the trainer taps features via `BaseModel.forward_features(x) -> (feat, logit)` only when RKD is enabled.

### Config system (Hydra)

All scripts use `@hydra.main(config_path="../configs", config_name="config")`. The root `configs/config.yaml` composes defaults from sub-configs:
- `configs/data/` — dataset paths and split settings
- `configs/teacher/` and `configs/student/` — model name, backbone, head dropout
- `configs/training/` — `distillation.yaml` (KD), `distillation_rkd.yaml` (KD + RKD feature-KD), `baseline.yaml` (no KD), `default.yaml`
- `configs/augmentation/` — `light.yaml` or `heavy.yaml`

Override at the CLI: `python scripts/train_student.py student=fastvit_sa12 training=baseline`

### Data flow

1. `scripts/prepare_data.py` creates fold CSVs via `StratifiedGroupKFold` (grouped by `patient_id` to prevent leakage) under `splits_dir/fold_{0..4}/train_split.csv` and `val_split.csv`, plus an **independent** `test_split.csv` — carved patient-disjoint + stratified *before* the CV (`test_holdout_splits`, default 6 ≈ 17%), so no fold trains on test patients. (Pre-2026-06-06 this was fold 0's val set → folds 1–4 leaked; see "Recurring gotchas".)
2. `SkinLesionDataModule` reads those CSVs and wraps them in `SkinLesionDataset` (expects columns `image_path`, `label`).
3. `DynamicUndersampledSampler` maintains a ~1:5 malignant:benign ratio, reshuffled each epoch via `datamodule.set_epoch(epoch)`.
4. `build_transforms` returns Albumentations pipelines built **from `configs/augmentation/{light,heavy}.yaml`** (not hard-coded); PIL images are converted to numpy internally before being passed to Albumentations. `light` (default) = the original pipeline; `heavy` = a stronger anti-overfit variant. MixUp/CutMix/CutOut are forbidden in-code (`_FORBIDDEN_OPS` → `raise`). Optional `drop_path_rate` (stochastic depth) per model config, default 0.0/off. See `docs/PREPROCESSING.md §4.1–4.2`.

### Model registry

`src/models/registry.py` maps string names → classes. All models inherit from `BaseModel` (ABC), expose `forward(x) -> Tensor (B,)` returning a single raw logit, and share `freeze_backbone()` / `unfreeze()` helpers. Backbones are loaded from `timm`; the classification head is always `Dropout → Linear(in_features, 1)` via `build_head()`. All seven timm models (teachers: efficientnetv2_m, convnextv2_base, maxvit_base; students: mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2, repvit_m1_0) use one generic wrapper `TimmBackboneModel` (`src/models/timm_backbone.py`) — there's no per-arch logic, so a single class covers them (the older baseline family wrappers were removed). They require `timm>=1.0` (mobilenetv4/fastvit/efficientformerv2/repvit are not in 0.9.x). The one exception is the domain-foundation teacher `panderm` (PanDerm ViT-B/16, Nature Medicine 2025), whose weights ship **out of timm** as a BEiT-style checkpoint (Google Drive, CC-BY-NC-4.0): `PanDermModel` (`src/models/panderm.py`) subclasses `TimmBackboneModel` — it builds a structurally-compatible timm ViT-B/16 and loads the PanDerm foundation weights over the backbone with a **loud remapping loader** that raises if fewer than `min_weight_match` of the backbone tensors match (so a wrong arch fails instead of silently training a near-random net). Set `teacher.weights_path=<abs path>` on the server for the teacher-training run; the timm arch (`vit_base_patch16_224` vs `beit_base_patch16_224`), feature dim 768, and input normalize must be verified there — see `docs/SOTA_MODEL_DECISION_2026-07.md §5`.

To add a new architecture: register it against `TimmBackboneModel` (or a new class if it needs custom logic) in `MODEL_REGISTRY`, and create a matching config under `configs/student/` or `configs/teacher/`. Use `infer_backbone_out_dim(backbone)` for the head input dim, never `backbone.num_features`.

### Evaluation

Primary metric: **pAUC@TPR≥80%** (ISIC 2024 official metric), normalized to [0, 0.2]. Decision threshold is selected via Youden's J statistic. `compute_metrics()` in `src/evaluation/metrics.py` returns `pauc_at_tpr80`, `auc_roc`, `auprc` (+ `prevalence` = its random baseline), `sensitivity`, `specificity`, `f1_score`, fixed-specificity operating points `sens_at_90spec`/`sens_at_95spec`, raw TP/FP/TN/FN counts, and RAW calibration diagnostics `brier`/`ece`. `Evaluator.save_predictions()` also writes `predictions.csv` (`y_true,y_prob,y_pred,source`) next to `test_metrics.json` so PR-curve / AUPRC / per-domain (ISIC-vs-PAD) / bootstrap CIs are recomputable offline without re-running inference. Use **AUPRC**, not AUC-ROC, as the headline at the measured **~0.39% prevalence** (ISIC 2024 + PAD-UFES-20 test set, job 28250; AUC-ROC is optimistic). pAUC is the ISIC-benchmark-comparison metric; AUPRC is the clinical headline — two roles, not a contradiction.

**Calibration** (distinct from ranking): `brier`/`ece` in `test_metrics.json` are the RAW miscalibration — the undersampled ~16.7% training prior inflates `sigmoid(logit)` vs the true ~0.39% prevalence. `scripts/compute_calibration.py --run-dir <run>` corrects the *displayed* probabilities offline (prior-shift closed-form by default; Platt/isotonic with `--method`, fit on the `val_predictions.csv` the training scripts now emit) and writes `calibration_metrics.json` + `reliability_curve.png`. Ranking metrics (pAUC/AUPRC/AUC) are invariant to any monotone re-scaling, so this changes **no** Chapter-4 number — it only makes shown "% risk" honest.

External test sets (HAM10000, Fitzpatrick17k) are **never used for training** — only for post-hoc cross-domain and fairness evaluation. They are prepared by a **separate** script, `scripts/prepare_external_data.py` (`bash run/prepare_external.sh DATASET=…`) — *not* `prepare_data.py`, which owns the training path — and they produce **one `test_split.csv` per dataset plus sensitivity variants**, no folds. Because they are test sets, cleaning is **two-tier**: only integrity failures are dropped, while `is_uninformative`/duplicate merely *flag* (`docs/PREPROCESSING.md §1.1`). Fitzpatrick17k ships **URLs, not images** — fetch with `scripts/download_fitzpatrick17k.py` first. Preparation ends in a leakage check (`reports/external_overlap_check_<ds>.md`) that **exits 2** on any overlap with the internal splits.

### Experiment design

Each student is trained twice (with KD / without KD) using identical hyperparameters, data splits, and seed. `compute_kd_delta()` computes the effectiveness delta between the two runs. 5-fold CV is used. The **"30 runs"** figure = **3 *students* × 2 KD conditions × 5 folds for ONE fixed teacher** ("3 arch" = students, not teachers). The registry declares **3 SOTA teachers** and all three are being trained, so the real total exceeds 30 — reports must state the actual teacher scope (one main teacher + 1-fold ablation of the others, or all three in full) rather than quoting "30".

### Run-dir convention (fold-aware)

Each training script writes results to a fold-scoped subdirectory so one job can populate all 5 folds without overwriting:

```
experiments/runs/
  teacher/efficientnetv2_m/fold_{0..4}/
    checkpoints/best_model.pth
    config.yaml
    test_metrics.json          ← auto-eval on held-out test set, written at end of training
    val_metrics.json           ← best-epoch val metrics (for val-vs-test overfitting gap)
    predictions.csv            ← test y_true,y_prob,y_pred[,source] (offline PR/AUPRC/per-domain)
    val_predictions.csv        ← val fit-set for calibration (no sampler → true ~0.39% prevalence)
    training_curves.png
  kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_{0..4}/...
  kd_efficientnetv2_m_to_fastvit_sa12/fold_{0..4}/...
  kd_efficientnetv2_m_to_efficientformerv2_s2/fold_{0..4}/...
```

`scripts/train_teacher.py` and `scripts/train_student.py` reload the best checkpoint from `checkpoints/best_model.pth` after training and run `Evaluator.evaluate(test_dataloader())`, saving the result alongside as `test_metrics.json`. The val-set metrics logged each epoch are *biased* (early-stopping optimizes against val); the `test_metrics.json` is the unbiased generalization number — quote that, not val_pauc, for verdicts. The trainers also write `val_metrics.json` (best-epoch val metrics, aligned to `best_model.pth`); a large **val − test** gap (esp. in AUPRC/pAUC) is the overfitting signal — `val_metrics.json` minus `test_metrics.json`.

### 5-fold CV — one process per model (folds loop sequentially)

`run/train_teacher.sh` and `run/train_student.sh` are **single** processes: each loops `for FOLD in ${FOLDS:-0 1 2 3 4}` internally and calls the training script once per fold, so **one model = one launch = all 5 folds**. `FOLDS="0 1 2"` + `FOLDS="3 4"` splits a heavy run (e.g. `maxvit_base`) across two launches. Launch + log pattern:

```bash
# One command = one process that trains all 5 folds:
bash run/train_teacher.sh TEACHER=efficientnetv2_m

# Log (tee'd by start_log; survives an SSH drop):
logs/train_teacher_<timestamp>.log

# Aggregate after all 5 folds finish:
bash run/aggregate.sh RUN_DIR=experiments/runs/teacher/efficientnetv2_m
```

To train several KD students concurrently on one GPU, use the VRAM-gated launcher `run/train_kd_parallel.sh` (`MAX_JOBS=2` is the measured safe cap) rather than backgrounding `run/train_student.sh` by hand.

`scripts/aggregate_folds.py` reads `fold_*/test_metrics.json`, computes mean ± std (+ min/max + per-fold) for every numeric metric, and writes `aggregated.json` (machine-readable) and `aggregated.md` (thesis-grade table). Cite the **aggregated mean ± std** for any reportable claim — a single fold's number has wide variance.

## Recurring gotchas

These have all bitten this repo at least once. Run the `code-change` skill's `validate-pipeline` checks after touching `src/`, `configs/`, or `run/` to catch them before launching jobs on the server. **Full detail for every item below lives in [docs/GOTCHAS.md](docs/GOTCHAS.md)** — this is just the index; read the matching section there before acting on one.

**Hard rules (never violate):**
- **Everything stays inside the project folder** — the server is shared. No `sudo`/`apt`/system-python/`~/.bashrc` edits, no killing other people's processes; deps only in `./.venv-linux` (`./.venv-export` for ExecuTorch), env vars per session.
- **Never overwrite an existing run-dir** — students fork with `run_suffix=`, **teachers with `output_dir=`** (`train_teacher.py` ignores `run_suffix`).
- **Set `TMPDIR="$(pwd)/.tmp"` per session** — the server root `/` has hit 100% full; `/tmp` spill causes `Errno 28`.
- **Pin `GPU=<id>` when running two jobs at once** — `GPU=auto` picks the freest card, so simultaneous launches can collide and OOM.

**Live coding traps:**
- **Hydra struct mode** — `OmegaConf.set_struct(cfg, False)` before merging any new top-level key, else `ConfigKeyError`.
- **Package re-exports** — names in `src/<pkg>/__init__.py` must match the real `class`/`def`; verify with `python -c "import src.training, src.models, src.data, src.evaluation"`.
- **Runner strict mode (`set -euo pipefail`, via `run/common.sh`)** — use `${VAR:-default}` for every knob; gate non-universal CLIs (`nvidia-smi`) with `command -v`.
- **timm `num_features` is unreliable** as the head input dim — always use `infer_backbone_out_dim(backbone)`.
- **`cfg.data.label_col` is the raw name (`target`)** — the processed dataframe uses `label`; pass `label_col="label"` to `generate_group_kfold_splits()`.
- **`patient_id` must be namespaced** (`pad_{id}`) when concatenating datasets, or groups collide and leak across folds.
- **Augmentation is config-driven** — edit `configs/augmentation/{light,heavy}.yaml`, not `transforms.py`; MixUp/CutMix/CutOut are forbidden in code.
- **External test sets filter in TWO tiers** — on HAM10000/Fitzpatrick17k, only integrity failures may be dropped; `is_uninformative`/duplicates just flag. Dropping changes the benchmark, and `is_uninformative`'s ISIC-tuned `std<8` can fire on flat clinical photos — which is not independent of skin tone. Don't "fix" this by reusing the ISIC/PAD drop logic (`docs/PREPROCESSING.md §1.1`).
- **`load_config()` composes Hydra `defaults:`** for the root config — standalone scripts break without it.
- **NumPy 2.0 removed `np.trapz`** — use `np.trapezoid`.
- **New trainer subclass must append `val_pauc`** per epoch, or `plot_training_curves` shape-mismatches.
- **Metadata has TWO independent gates** (`docs/metadata_training_plan.md`, default off = image-only unchanged): `data.metadata_cols` = *which* raw cols to carry into the split CSVs (direction D subgroup calibration + the privileged inputs); `data.metadata_as_input` = whether the dataset feeds them into the batch as a 4-tuple `(image, meta, mask, label)` (direction A privileged/LUPI teacher). D sets only `metadata_cols` (model stays image-only, cols ride the `predictions.csv` side-channel via `test_metadata()`); A sets **both**. Any new DataLoader consumer must unpack via `src/utils/batch.py::unpack_batch` (2- or 4-tuple). `iddx_*`/`mel_*` are rejected as leakage; the metadata scaler is fit on the **train fold only**.

**Operational / postmortems (context for helper behavior):**
- **No scheduler** — a run is just a process. Launch under `tmux`/`nohup`; find it again via `ps -ef | grep train_`, `nvidia-smi`, or `logs/<name>_<timestamp>.log`. Only kill PIDs you started.
- **`run/train_kd_parallel.sh` is VRAM-gated** — launches only when running-jobs < `MAX_JOBS` **and** free VRAM ≥ `MIN_FREE_MB`. Measured 2026-08-13: one KD job already saturates the GPU, so more concurrency adds no speedup, only OOM risk (`MAX_JOBS=2` cap).
- **Data-strategy ablations** — `run_suffix` isolates student run-dirs (`output_dir` for teachers), `data.train_sources` filters train+val only (test stays whole), the PAD ablation must run baseline (no KD).
- **`maxvit_base` cuDNN backward error** + the `cudnn_deterministic` lever — likely VRAM; retry with lower batch + `cudnn_deterministic=false`.

**Resolved (historical):**
- `pauc_at_tpr()` — FIXED 2026-06-04, now the real ISIC 2024 metric (~[0.02, 0.20]).
- Baseline (no-KD) student training — FIXED 2026-06-04 via the `use_kd` flag.
- PAD-UFES-20 `img_id` includes the extension — FIXED 2026-06-07.
