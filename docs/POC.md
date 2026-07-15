# POC Guide — Knowledge-Distilled Skin Cancer Detection

This guide walks through a proof-of-concept run of the whole pipeline (teacher → KD student → evaluate) using the minimal `config_poc` configuration. Goal: confirm the solution works end-to-end in minutes before spending hours on the full 50-epoch training.

---

## 1. Models

All models inherit from `src/models/base_model.py` and output a **single raw logit** for binary classification (benign=0, malignant=1). Apply `torch.sigmoid()` at inference.

| Role | Name | Backbone (timm) | Params | Config |
|---|---|---|---|---|
| Teacher | `efficientnetv2_m` | `tf_efficientnetv2_m.in21k_ft_in1k` | ~54M | `configs/teacher/efficientnetv2_m.yaml` |
| Teacher | `convnextv2_base` | `convnextv2_base.fcmae_ft_in22k_in1k` | ~89M | `configs/teacher/convnextv2_base.yaml` |
| Teacher | `maxvit_base` | `maxvit_base_tf_224.in1k` | ~119M | `configs/teacher/maxvit_base.yaml` |
| Student | `mobilenetv4_conv_medium` | `mobilenetv4_conv_medium.e500_r224_in1k` | ~9M | `configs/student/mobilenetv4_conv_medium.yaml` |
| Student | `fastvit_sa12` | `fastvit_sa12.apple_in1k` | ~11M | `configs/student/fastvit_sa12.yaml` |
| Student | `efficientformerv2_s2` | `efficientformerv2_s2.snap_dist_in1k` | ~13M | `configs/student/efficientformerv2_s2.yaml` |

Registry: `src/models/registry.py` — `build_model(cfg)` dispatches on `cfg.model.name`. All 6 models share one generic wrapper `TimmBackboneModel` and require **`timm>=1.0`** (the earlier baseline set was removed).

---

## 2. Configs

### Root configs
| File | Purpose |
|---|---|
| `configs/config.yaml` | Full training (50 epochs, batch 32/64) |
| `configs/config_poc.yaml` | POC smoke test (2 epochs, batch 16) |

### Sub-config groups (selected via Hydra `defaults` list)
| Group | Options |
|---|---|
| `data/` | `isic2024` (primary), `pad_ufes_20` (augment), `ham10000` / `fitzpatrick17k` (external eval only) |
| `teacher/` | `efficientnetv2_m`, `convnextv2_base`, `maxvit_base` |
| `student/` | `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2` |
| `training/` | `default`, `baseline` (no KD), `distillation` (KD), `distillation_rkd` (KD + RKD), `ablation`, `poc` |
| `augmentation/` | `light`, `heavy` |

### Key hyperparameters in `training/poc.yaml`
- `epochs: 2`, `batch_size: 16`, `grad_clip: 1.0`
- Optimizer: AdamW (lr_backbone=1e-4, lr_head=1e-3)
- Scheduler: cosine, no warmup
- Loss: focal (γ=2.0, α=0.25)
- KD: T=4.0, α=0.3 (only used in student training)
- Early stopping: **disabled** (force both epochs to run)

---

## 3. Prerequisites

### 3.1 Python environment
```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
make install-dev
cp .env.example .env             # edit DATA_ROOT if needed
```

### 3.2 Data

The POC uses **synthetic fixtures** — no 30 GB download needed. Images are 224×224 RGB noise with a class-conditioned color bias so the model has something learnable.

```bash
make prepare-poc
```
Output:
```
data/processed/poc/{benign,malignant}/*.jpg   # 150 + 30 synthetic images
data/splits/poc/fold_0/train_split.csv        # 60% per class
data/splits/poc/fold_0/val_split.csv          # 20% per class
data/splits/poc/test_split.csv                # 20% per class
```
Tune size with: `python scripts/prepare_poc_data.py --n-benign 50 --n-malignant 10`.

**For the real experiments (not POC)**, download **ISIC 2024** from Kaggle to `data/raw/isic2024/`:
```
data/raw/isic2024/
├── train-image.hdf5          # HDF5: keys=isic_id, values=JPEG bytes
└── train-metadata.csv        # cols: isic_id, patient_id, target, ...
```
Source: https://www.kaggle.com/competitions/isic-2024-challenge/data — then `make prepare` (uses `StratifiedGroupKFold` grouped by `patient_id`).

---

## 4. POC training pipeline

### 4.1 Train teacher (Step 1)
```bash
make poc-teacher
# equivalent to:
python scripts/train_teacher.py --config-name config_poc
```
Output:
```
experiments/poc/teacher/efficientnetv2_m/
├── checkpoints/best_model.pth
├── checkpoints/last.pth
├── config.yaml
└── training_curves.png
```

### 4.2 Train student via KD (Step 2)
```bash
make poc-student
# equivalent to:
python scripts/train_student.py --config-name config_poc student=mobilenetv4_conv_medium
```
The student script looks for the teacher checkpoint at:
```
experiments/poc/teacher/efficientnetv2_m/checkpoints/best_model.pth
```
Override with: `teacher_checkpoint=<path>` on the CLI.

Output:
```
experiments/poc/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/
├── checkpoints/best_model.pth
├── config.yaml
└── training_curves.png
```

### 4.3 Train other student architectures (optional)
```bash
python scripts/train_student.py --config-name config_poc student=mobilenetv4_conv_medium
python scripts/train_student.py --config-name config_poc student=efficientformerv2_s2
```

### 4.4 Run the full POC chain
```bash
make poc-all              # teacher + mobilenetv4_conv_medium student
```

---

## 5. Evaluation

`scripts/evaluate.py` runs inference on the held-out test split and computes all metrics.

```bash
# Evaluate teacher
python scripts/evaluate.py \
    --model-name efficientnetv2_m \
    --checkpoint experiments/poc/teacher/efficientnetv2_m/checkpoints/best_model.pth \
    --output reports/results/poc_teacher_metrics.json

# Evaluate KD student
python scripts/evaluate.py \
    --model-name mobilenetv4_conv_medium \
    --checkpoint experiments/poc/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/checkpoints/best_model.pth \
    --output reports/results/poc_kd_student_metrics.json
```

Metrics produced (`src/evaluation/metrics.py`):
- **`pauc_at_tpr80`** — primary metric (ISIC 2024 official, normalized)
- `auc_roc`
- `sensitivity`, `specificity`, `f1_score`
- Confusion-matrix entries (`tp`, `fp`, `tn`, `fn`)
- Decision `threshold` (Youden's J)

Confusion matrix PNG: `reports/figures/confusion_matrix.png`.

---

## 6. What the POC validates (checklist)

After `make poc-all` completes, verify:

- [ ] Teacher `best_model.pth` exists
- [ ] `training_curves.png` shows loss decreasing across 2 epochs
- [ ] Student `best_model.pth` exists
- [ ] Student training logs show both `hard_loss` and `soft_loss` printed each epoch
- [ ] `python scripts/evaluate.py --model-name mobilenetv4_conv_medium --checkpoint <path>` runs and writes metrics JSON
- [ ] Metric JSON contains `pauc_at_tpr80` (likely low — that's fine for POC)

If any step fails, the log at `experiments/prepare_data.log` and `stdout` from the Hydra run (in `outputs/`) are the first places to look.

---

## 7. Next steps after POC

1. Switch `--config-name config` (the full 50-epoch config).
2. Run all 3 students both with KD (`training=distillation`) and without (`training=baseline`) — the controlled comparison.
3. Across 5 folds → 30 training runs total.
4. Aggregate metrics via `src/evaluation/metrics.py::compute_kd_delta` to report the KD effectiveness delta.
5. External eval on HAM10000 and Fitzpatrick17k (never in training).
