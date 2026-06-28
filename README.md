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
   - Baseline: `efficientnet_b4`
   - SOTA set: `efficientnetv2_m`, `convnextv2_base`, `maxvit_base`
2. **Student** — trained with `KDTrainer` + `BinaryDistillationLoss` against the
   frozen teacher:
   `L = 0.3·focal(student, y) + 0.7·T²·BCE(σ(s/T), σ(t/T))`, T = 4.0.
   - Baseline: `efficientnet_b0`, `mobilenetv3_large`, `mobilevit_s`
   - SOTA set: `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2`

Each student is trained twice — **with KD** and **without KD (baseline)** — under
identical data/hyperparameters/seed, over **5-fold CV** (StratifiedGroupKFold by
`patient_id`). `compute_kd_delta()` reports the KD effect.

**Primary metric:** pAUC@TPR≥80 (ISIC 2024 official, range ≈ [0.02, 0.20]).
At ~0.4 % prevalence, quote **AUPRC** (not AUC-ROC) as the headline.

## Setup

```bash
make install-dev        # deps + pre-commit hooks
cp .env.example .env    # configure data paths
```

> The repo runs on the **UIT Slurm cluster**, not locally — see `CLAUDE.md`
> ("Local environment ≠ runtime environment"). The Mac is for editing only.

## Usage

```bash
# Data (raw ISIC 2024 HDF5 + PAD-UFES-20 in data/raw/ first)
make prepare

# Stage 1 — teacher (run before any student)
make train-teacher

# Stage 2 — students via KD
make train-student-b0
make train-student-mobilenet
make train-student-mobilevit
make train-all-students          # all three sequentially

# Evaluation / inference
make evaluate
python scripts/evaluate.py --model-name efficientnet_b4 --checkpoint path/to/best_model.pth
python scripts/predict.py  --model-name mobilenetv3_large --checkpoint path/to/best_model.pth \
    --image path/to/lesion.jpg --threshold 0.61   # use the Youden threshold from test_metrics.json

# Export for deployment (ONNX default; also torchscript). Export the STUDENT, not the teacher.
python scripts/export_model.py --model-name mobilenetv3_large \
    --checkpoint path/to/best_model.pth --format onnx --output exports/skin_mnv3

# Tests + code quality
make test
make lint     # flake8 + isort + black (check)
make format   # apply isort + black
```

Hydra overrides at the CLI, e.g.:
```bash
python scripts/train_student.py student=mobilenetv3_large training=baseline
python scripts/train_teacher.py teacher=efficientnetv2_m
```

### POC smoke test (synthetic data, no ISIC download)

```bash
make poc-all     # prepare-poc → poc-teacher → poc-student (2 epochs each)
```

### Cluster

```bash
bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=efficientnet_b4
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large
bash slurm/submit.sh slurm/23_export_model.slurm \
    MODEL=mobilenetv3_large \
    CKPT=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_0/checkpoints/best_model.pth
```
The model emits one raw logit → `sigmoid()` then the Youden threshold from that fold's `test_metrics.json` (not 0.5). Research/thesis model, not a validated medical device. See `docs/SLURM.md` and `slurm/README.md`.

## Project Structure

```
skin-cancer-detector/
├── configs/          # Hydra YAML configs (data, teacher, student, training, augmentation)
├── data/             # raw, processed data and split CSVs
├── src/
│   ├── data/         # Dataset, DataModule, transforms, sampler, preprocessing
│   ├── models/       # BaseModel + registry (family wrappers + TimmBackboneModel)
│   ├── training/     # Trainer, KDTrainer, losses, distillation, optimizers, callbacks
│   ├── evaluation/   # metrics (pAUC/AUPRC), evaluator, confusion matrix, Grad-CAM
│   ├── inference/    # predictor and ensemble
│   └── utils/        # seed, logger, config, checkpoint helpers
├── scripts/          # CLI entry points (train_*, evaluate, prepare_data, benchmark_mobile, ...)
├── slurm/            # cluster job scripts (submit via slurm/submit.sh)
├── docs/             # SLURM / PREPROCESSING / POC guides
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
