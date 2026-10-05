---
name: kd-experiment
description: Set up and run a controlled KD-vs-baseline comparison for one student architecture on splits v2, then get the paired-CI delta. Use when the user asks to "compare KD effect", "run controlled experiment", "train with and without KD", or wants the KD effectiveness delta for a specific student. NOT for comparing results that already exist across all runs (eval-results → compare-kd) and NOT for judging one run (eval-results → analyze-evaluation).
---

# kd-experiment

Runs the proposal's controlled comparison: train one student architecture **twice** with identical seed/data/hyperparams — once with KD, once without — then compute the KD effectiveness delta.

## When to use

- "Train <student> with and without KD" / "What's the KD delta for <student>?"
- User wants to know whether KD actually helps for a specific student
- Adding a new KD/baseline pair to an existing splits-v2 arm

## DO NOT

- Change seed, batch size, learning rate, scheduler, sampler or augmentation between the KD and baseline runs — the comparison must be controlled.
- Skip the baseline run. Without it, there's no delta to report.
- Use a different teacher checkpoint between students — all students in one comparison distill from the *same* teacher run, **on the same splits**.
- Write into an existing run-dir. A new arm forks: students with `run_suffix=`, teachers with `output_dir=` (`train_teacher.py` ignores `run_suffix` — `CLAUDE.md` hard rule 2).
- Mix trees: `experiments/runs/` is splits v1 (leaked patients); new work lives under `experiments/runs_newsplit_<arm>/` and needs its **own** control in that tree.

## Workflow

All commands run **on the server** (`TMPDIR="$(pwd)/.tmp"`, pin `GPU=<id>` if another job is running, launch under `tmux`). Record the launch in `docs/PROGRESS.md`.

### Step 1 — Verify the teacher of this tree exists

```bash
ls experiments/runs_newsplit_<arm>/teacher/<teacher>/fold_*/checkpoints/best_model.pth
```
If missing, train it into the same tree: `bash run/train_teacher.sh TEACHER=<teacher> EXTRA="output_dir=experiments/runs_newsplit_<arm>"`.

### Step 2 — KD run

```bash
bash run/train_student.sh STUDENT=<student> TEACHER=<teacher> TRAINING=distillation \
     EXTRA="output_dir=experiments/runs_newsplit_<arm> [run_suffix=__<variant>] [other overrides]"
```
→ `experiments/runs_newsplit_<arm>/kd_<teacher>_to_<student>[__<variant>]/fold_{0..4}/`

### Step 3 — Baseline run (identical overrides, no KD)

```bash
bash run/train_student.sh STUDENT=<student> TRAINING=baseline \
     EXTRA="output_dir=experiments/runs_newsplit_<arm> [run_suffix=__<variant>] [other overrides]"
```
→ `experiments/runs_newsplit_<arm>/baseline_<student>[__<variant>]/fold_{0..4}/`. Verify the exact name with `ls` before pairing.

### Step 4 — Test metrics are already there

Both training scripts reload `best_model.pth` and write `test_metrics.json` + `predictions.csv` per fold — no separate eval step. `bash run/aggregate.sh RUN_DIR=<run>` gives the 5-fold mean ± std.

### Step 5 — The delta = a PAIRED bootstrap CI (not a subtraction of two means)

```bash
bash run/bootstrap_ci.sh RESULTS_DIR=experiments/runs_newsplit_<arm> \
     PAIR="kd_<teacher>_to_<student>[__v]:baseline_<student>[__v]" SUBGROUP=source
```
Quote it as "ΔAUPRC +x [lo, hi]" per source (PAD = the phone-photo subset). Never pool the five folds, never quote a win count. Cross-domain (HAM10000 / Fitzpatrick17k): `run/evaluate_external.sh`, with an `--out-root` under `reports/external_newsplit_<arm>/` (v2 trees never go into the v1 `reports/external/`), then the same `bootstrap_ci.sh` on that `<ds>/<variant>/` tree. Reading/judging the result → **eval-results** (`reference/compare-kd.md` for the whole matrix).

## Architectures available

Students (mobile-SOTA): `mobilenetv4_conv_medium` (default), `fastvit_sa12`, `efficientformerv2_s2`, `repvit_m1_0`.
Teachers (SOTA): `efficientnetv2_m` (default), `convnextv2_base`, `maxvit_base`. See `src/models/registry.py`.
(The old baseline set `efficientnet_b0`/`mobilenetv3_large`/`mobilevit_s`/`efficientnet_b4` was deleted 2026-07-15.)

## Key invariants

- Teacher (default **EfficientNetV2-M**) is **always frozen** (`KDTrainer` enforces this).
- KD loss: `L = 0.3 * focal(student, true) + 0.7 * T² * BCE(σ(s/T), σ(t/T))`, T=4.0 (`configs/training/distillation.yaml`).
- Baseline loss: `BinaryFocalLoss` only (`configs/training/baseline.yaml`).
- **KD variants** (opt-in, don't change the controlled default comparison unless that's the ablation you want):
  `EXTRA="training.distillation.soft_loss_type=mse run_suffix=__mselogit"` (MSE-logit KD) or
  `TRAINING=distillation_rkd EXTRA="run_suffix=__rkd"` (RKD feature-KD). Each writes an isolated `__suffix` run-dir.
- Headline metric: **AUPRC** at the ~0.39% prevalence, split by `source` (PAD first for the mobile story); **pAUC@TPR≥80%** (`src/evaluation/metrics.py::pauc_at_tpr`) for ISIC-benchmark comparison.
- 5 folds per run (`FOLDS="0 1 2 3 4"` default); per-fold differences below ~0.005 AUPRC are rerun noise (`experiments/_reproducibility/README.md`).
