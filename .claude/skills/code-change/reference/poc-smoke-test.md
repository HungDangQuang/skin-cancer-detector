---
name: poc-smoke-test
description: Run the POC pipeline end-to-end as a smoke test (synthetic data, no ISIC download). Use when the user asks to "smoke test", "verify the pipeline works", "run POC", "test end-to-end", or wants a quick check before committing to long training.
---

# poc-smoke-test

Runs the whole training pipeline (data → teacher → KD student) on synthetic fixtures in minutes, before committing to expensive real-data runs.

## When to use

- "Make sure the code works before I run on real data"
- "Smoke test the changes"
- "Run a quick end-to-end"
- After any non-trivial refactor in `src/models/`, `src/training/`, `src/data/`, or any of the configs

## DO NOT

- Use the POC `pauc_at_tpr80` to make scientific claims — synthetic data with 30 malignant samples gives noisy metrics. The signal is "did training run without errors?", not "did it learn?".
- Run `make poc-teacher` before `make prepare-poc`. The teacher needs the synthetic CSVs to exist.
- Call `scripts/prepare_poc_data.py` / `scripts/train_*.py` directly on the server. Use `bash run/poc.sh …` so the venv, GPU selection and `logs/` transcript are set up for you.

## Local execution (Mac/Linux without GPU)

```bash
# 1. Verify environment
python -c "import torch, hydra, timm, omegaconf; print('imports ok')"

# 2. Generate synthetic fixtures
make prepare-poc
# → data/processed/poc/{benign,malignant}/*.jpg + data/splits/poc/...

# 3. Teacher (2 epochs)
make poc-teacher
# → experiments/poc/teacher/efficientnetv2_m/checkpoints/best_model.pth

# 4. KD student (2 epochs)
make poc-student
# → experiments/poc/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/checkpoints/best_model.pth

# Or all at once:
make poc-all
```

For CPU-only laptops, override device:
```bash
python scripts/train_teacher.py --config-name config_poc device=cpu
```

## Server execution

```bash
bash run/poc.sh STAGE=prepare
# → tail -f logs/poc_<timestamp>.log

bash run/poc.sh STAGE=teacher
# wait → check experiments/poc/teacher/.../best_model.pth

bash run/poc.sh STAGE=student
# Or with a different student:
bash run/poc.sh STAGE=student STUDENT=fastvit_sa12
```

## Success criteria

After all 3 stages, all of these must be true:

- [ ] `data/splits/poc/fold_0/{train,val}_split.csv` exist
- [ ] `experiments/poc/teacher/efficientnetv2_m/checkpoints/best_model.pth` exists
- [ ] `experiments/poc/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/checkpoints/best_model.pth` exists
- [ ] Teacher log shows 2 epochs ran (search for `Epoch 2/2`)
- [ ] Student log shows both `hard_loss=` and `soft_loss=` per epoch
- [ ] `train_loss` decreased from epoch 1 to epoch 2 (any decrease is fine — synthetic data, 2 epochs)

If all pass → the full pipeline (data loading, model build, both trainers, both losses, KD soft-target flow, checkpoint save) is working.

## What POC validates / what it doesn't

✓ `SkinLesionDataModule` + `DynamicUndersampledSampler` data flow
✓ Model build via `MODEL_REGISTRY`
✓ Teacher's `Trainer` + `BinaryFocalLoss`
✓ Teacher checkpoint save + KD load
✓ Student's `KDTrainer` + `BinaryDistillationLoss` with both hard/soft components
✓ pAUC + Youden's J metric pipeline
✓ Albumentations transforms + PIL → numpy conversion
✓ Hydra config composition with `--config-name config_poc`

✗ Whether the model actually learns dermoscopy features — needs real data
✗ Real-data hyperparameter quality
✗ Cross-domain generalization (HAM10000, Fitzpatrick17k — full pipeline only)
✗ 5-fold CV stability (POC uses fold 0 only)
