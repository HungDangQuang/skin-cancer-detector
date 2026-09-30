---
name: kd-experiment
description: Set up and run a controlled KD-vs-baseline comparison for one student architecture. Use when the user asks to "compare KD effect", "run controlled experiment", "train with and without KD", or wants to compute KD effectiveness delta for a specific student. NOT for comparing results that already exist across all runs (use compare-kd) and NOT for a single eval JSON (use analyze-evaluation).
---

# kd-experiment

Runs the proposal's controlled comparison: train one student architecture **twice** with identical seed/data/hyperparams — once with KD, once without — then compute the KD effectiveness delta.

## When to use

- "Train MobileNetV3 with and without KD" / "Run KD comparison for B0"
- "What's the KD delta for <model>?"
- User wants to evaluate whether KD actually helps for a specific arch
- Setting up the 30-run experiment matrix (3 archs × {KD, baseline} × 5 folds)

## DO NOT

- Change seed, batch size, learning rate, scheduler, or augmentation between the KD and baseline runs — the comparison must be controlled.
- Skip the baseline run. Without it, there's no delta to report.
- Use a different teacher checkpoint between archs — all students should distill from the *same* teacher run.

## Workflow

### Step 1 — Verify teacher exists

The teacher must be trained first. Check:
```bash
ls experiments/runs/teacher/efficientnetv2_m/checkpoints/best_model.pth
```
If missing, train it first via `run/README.md` script index (`run/train_teacher.sh`), passing `TEACHER=<name>`.

### Step 2 — Submit the KD run

```bash
bash run/train_student.sh STUDENT=<arch> TEACHER=<teacher> TRAINING=distillation
```
Output dir: `experiments/runs/kd_<teacher>_to_<arch>/` (default teacher `efficientnetv2_m`)

### Step 3 — Submit the baseline run

```bash
bash run/train_student.sh STUDENT=<arch> TRAINING=baseline
```
Output dir: `experiments/runs/baseline_<arch>/` (per `train_student.py` naming — verify with `ls experiments/runs/`)

### Step 4 — Evaluate both checkpoints on the test split

```bash
bash run/evaluate.sh \
    MODEL=<arch> CKPT=<kd_checkpoint_path> OUT=reports/results/<arch>_kd.json

bash run/evaluate.sh \
    MODEL=<arch> CKPT=<baseline_checkpoint_path> OUT=reports/results/<arch>_baseline.json
```

### Step 5 — Compute the delta

```python
import json
from src.evaluation.metrics import compute_kd_delta

with open("reports/results/<arch>_baseline.json") as f:
    no_kd = json.load(f)
with open("reports/results/<arch>_kd.json") as f:
    with_kd = json.load(f)

delta = compute_kd_delta(no_kd, with_kd)
print(delta)   # {'delta_pauc': ..., 'delta_auc': ..., 'delta_sensitivity': ..., 'delta_specificity': ...}
```

## Architectures available

Students (mobile-SOTA): `mobilenetv4_conv_medium` (default), `fastvit_sa12`, `efficientformerv2_s2`.
Teachers (SOTA): `efficientnetv2_m` (default), `convnextv2_base`, `maxvit_base`. See `src/models/registry.py`.
(The old baseline set `efficientnet_b0`/`mobilenetv3_large`/`mobilevit_s`/`efficientnet_b4` was deleted 2026-07-15.)

## Key invariants

- Teacher (default **EfficientNetV2-M**) is **always frozen** (`KDTrainer` enforces this).
- KD loss: `L = 0.3 * focal(student, true) + 0.7 * T² * BCE(σ(s/T), σ(t/T))`, T=4.0 (`configs/training/distillation.yaml`).
- Baseline loss: `BinaryFocalLoss` only (`configs/training/baseline.yaml`).
- **KD variants** (opt-in, don't change the controlled default comparison unless that's the ablation you want):
  `EXTRA="training.distillation.soft_loss_type=mse run_suffix=__mselogit"` (MSE-logit KD) or
  `TRAINING=distillation_rkd EXTRA="run_suffix=__rkd"` (RKD feature-KD). Each writes an isolated `__suffix` run-dir.
- Primary metric: **pAUC@TPR≥80%** (`src/evaluation/metrics.py::pauc_at_tpr`). Higher is better.
- 5-fold CV planned — POC uses fold 0 only.
