# Skin Cancer Detector

Binary skin-lesion classification (**benign = 0 / malignant = 1**) on **ISIC 2024**
dermoscopy (+ **PAD-UFES-20** smartphone images), built around **Knowledge
Distillation (KD)**: a high-capacity teacher is compressed into lightweight,
mobile-deployable students.

> Earlier scoping was a 7-class HAM10000 problem; the project pivoted to binary
> ISIC 2024 + KD so the result is a deployable model with reportable ISIC-2024
> numbers. HAM10000 and Fitzpatrick17k are kept as **external test sets only**
> (cross-domain + fairness), never for training.

## Pipeline at a glance

Two stages, all models output a single raw logit (`torch.sigmoid()` at inference):

1. **Teacher** — trained standalone with `Trainer` + `BinaryFocalLoss`.
   - `efficientnetv2_m`, `convnextv2_base`, `maxvit_base`
2. **Student** — trained with `KDTrainer` + `BinaryDistillationLoss` against the
   frozen teacher:
   `L = 0.3·focal(student, y) + 0.7·T²·BCE(σ(s/T), σ(t/T))`, T = 4.0.
   - `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2`, `repvit_m1_0`

Each student is trained twice — **with KD** and **without KD (baseline)** — under
identical data/hyperparameters/seed, over **5-fold CV** (StratifiedGroupKFold by
`patient_id`). `compute_kd_delta()` reports the KD effect. Opt-in KD variants:
`training.distillation.soft_loss_type=mse` (MSE-on-logit, Kim et al. 2021) and
`training=distillation_rkd` (RKD feature-KD, Park et al. 2019); probability
calibration (ECE/Brier + reliability curve) via `scripts/compute_calibration.py`.

**Metrics — two distinct roles (not a contradiction):** **pAUC@TPR≥80** (ISIC 2024
official, range ≈ [0.02, 0.20]) is the **benchmark-comparison** metric — it lets the
result sit next to the ISIC 2024 leaderboard/literature. **AUPRC** is the **clinical
headline**: at the measured **~0.39 % prevalence** (ISIC 2024 + PAD-UFES-20 test set)
AUPRC, not AUC-ROC, reflects real performance (AUC-ROC is inflated at extreme
imbalance).

## Setup

```bash
make install-dev        # deps + pre-commit hooks
cp .env.example .env    # configure data paths
```

> The repo runs on the **Linux GPU server** (`bash run/<script>.sh`), not locally — see
> `CLAUDE.md` ("Local environment ≠ runtime environment"). The Mac is for editing only.

## Usage

```bash
# Data (raw ISIC 2024 HDF5 + PAD-UFES-20 in data/raw/ first)
make prepare

# Stage 1 — teacher (run before any student)
make train-teacher

# Stage 2 — students via KD
make train-student-mobilenetv4
make train-student-fastvit
make train-student-efficientformer
make train-all-students          # all three sequentially

# Evaluation / inference
make evaluate
python scripts/evaluate.py --model-name efficientnetv2_m --checkpoint path/to/best_model.pth
python scripts/predict.py  --model-name mobilenetv4_conv_medium --checkpoint path/to/best_model.pth \
    --image path/to/lesion.jpg --threshold 0.61   # use the Youden threshold from test_metrics.json

# Export for deployment (ONNX default; also torchscript). Export the STUDENT, not the teacher.
python scripts/export_model.py --model-name mobilenetv4_conv_medium \
    --checkpoint path/to/best_model.pth --format onnx --output exports/skin_mnv3

# Compare ALL runs: did KD help + best teacher→student pair (reads experiments/runs/*/fold_*/test_metrics.json)
python scripts/compare_kd_results.py     # → reports/comparison/kd_comparison.{md,json}

# Tests + code quality
make test
make lint     # flake8 + isort + black (check)
make format   # apply isort + black
```

Hydra overrides at the CLI, e.g.:
```bash
python scripts/train_student.py student=mobilenetv4_conv_medium training=baseline
python scripts/train_teacher.py teacher=efficientnetv2_m
```

### POC smoke test (synthetic data, no ISIC download)

```bash
make poc-all     # prepare-poc → poc-teacher → poc-student (2 epochs each)
```

### Cluster

```bash
bash run/train_teacher.sh TEACHER=efficientnetv2_m
bash run/train_student.sh STUDENT=mobilenetv4_conv_medium
bash run/export_model.sh \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
```
The model emits one raw logit → `sigmoid()` then the Youden threshold from that fold's `test_metrics.json` (not 0.5). Research/thesis model, not a validated medical device. See `run/README.md` and `run/README.md`.

## Project Structure

```
skin-cancer-detector/
├── configs/          # Hydra YAML configs (data, teacher, student, training, augmentation)
├── data/             # raw, processed data and split CSVs
├── src/
│   ├── data/         # Dataset, DataModule, transforms, sampler, preprocessing
│   ├── models/       # BaseModel + registry (single generic TimmBackboneModel)
│   ├── training/     # Trainer, KDTrainer, losses, distillation, optimizers, callbacks
│   ├── evaluation/   # metrics (pAUC/AUPRC), evaluator, confusion matrix, Grad-CAM
│   ├── inference/    # predictor and ensemble
│   └── utils/        # seed, logger, config, checkpoint helpers
├── scripts/          # CLI entry points (train_*, evaluate, prepare_data, benchmark_mobile, ...)
├── run/              # execution layer — launch everything via `bash run/<script>.sh`
├── docs/             # PREPROCESSING / POC / GOTCHAS guides
├── reports/ + QA/    # thesis figures, results, recorded Q&A
└── tests/            # unit tests
```

## Experiment Tracking

```bash
mlflow ui --backend-store-uri experiments/runs
```

## Citations

ISIC 2024 — SLICE-3D (primary). PAD-UFES-20 (Mendeley `zr7vgbcyr2`).
HAM10000 (external test only):
> Tschandl, P., Rosendahl, C. & Kittler, H. The HAM10000 dataset, a large
> collection of multi-source dermatoscopic images of common pigmented skin
> lesions. Sci. Data 5, 180161 (2018).
