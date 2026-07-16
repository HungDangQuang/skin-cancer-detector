---
name: review-training
description: Review training-step code (src/training/, scripts/train_teacher.py, scripts/train_student.py) against this project's Trainer/KDTrainer contract and known gotchas. Use when the user changes a trainer, loss, optimizer/scheduler, callback, the KD loss, or a training script, and asks "review my training code", "did I break the trainer", "check the KD loss". NOT for judging a finished run's quality (use assess-training) or triaging a crash (use diagnose-training).
---

# review-training

Reviews the **training layer** — `Trainer`, `KDTrainer`, losses, the model
head/forward contract, and the two training scripts — against the invariants the
rest of the repo (and the 30-run experiment design) depends on. Catches wiring
bugs that crash a Slurm job halfway through or, worse, train silently on the
wrong objective.

Scope: `src/training/` (`trainer.py`, `kd_trainer.py`, `losses.py`,
`distillation.py`, `callbacks.py`, `optimizers.py`, `schedulers.py`),
`src/models/registry.py` + `heads.py` (forward/head contract),
`scripts/train_teacher.py`, `scripts/train_student.py`.

## How to run

1. Diff in scope: `git diff HEAD -- src/training/ src/models/ scripts/train_*.py`.
2. Walk the checklist in order. For each item read the hunk + enclosing
   function/caller; cite `file:line`.
3. Report most-severe first (a wrong-objective or crash-on-cluster bug outranks
   style). Recommend `validate-pipeline` (§1 imports, §2 Hydra dry-load, §4
   anti-patterns) and, for behavior, `poc-smoke-test`. State what can't be
   verified on the Mac (no torch/timm locally).

## The training contract (review against this)

- **Stage 1 Teacher**: one of the SOTA set `{efficientnetv2_m (default), convnextv2_base, maxvit_base}`
  + `Trainer` + `BinaryFocalLoss`.
- **Stage 2 Student**: one of the mobile-SOTA set `{mobilenetv4_conv_medium (default), fastvit_sa12, efficientformerv2_s2}`
  + `KDTrainer` + `BinaryDistillationLoss`, teacher **frozen**:
  `L = 0.3·L_focal(student, y) + 0.7·T²·L_BCE(σ(s/T), σ(t/T))`, **T=4.0**.
  (The old baseline set `efficientnet_b4`/`efficientnet_b0`/`mobilenetv3_large`/`mobilevit_s` was **deleted 2026-07-15** — project is SOTA-only now, all 6 via `TimmBackboneModel`, needs `timm>=1.0`.)
- **KD variants (opt-in, default OFF — must stay byte-for-byte back-compat):**
  `training.distillation.soft_loss_type` = `bce` (default) | `mse` (Kim 2021, MSE on raw logits, **no** T²);
  `training=distillation_rkd` adds `RKDLoss` (`src/training/feature_distillation.py`, Park 2019 — distance+angle,
  projector-free) on top of logit KD, tapping features via `BaseModel.forward_features(x)->(feat,logit)`.
- Every model `forward(x) -> Tensor (B,)` — a **single raw logit**, sigmoid at
  inference. Losses expect `(B,)`, not `(B,1)`.
- Run-dir is fold-scoped: `experiments/runs/<run>/fold_{0..4}/` with
  `checkpoints/best_model.pth`, `config.yaml`, `test_metrics.json`,
  `training_curves.png`.
- After training, the script reloads `best_model.pth` and runs `Evaluator` on the
  **test** dataloader, writing `test_metrics.json` (the unbiased number).

## Review checklist

### A. Hydra / config wiring (crash-on-job-start class)
- [ ] Any `OmegaConf.merge(cfg, {"model": ...})` is preceded by
  `OmegaConf.set_struct(cfg, False)` — struct mode rejects the new top-level key
  (`ConfigKeyError: Key 'model' is not in struct`).
- [ ] **Baseline coupling** (FIXED 2026-06-04 — verify it stays fixed):
  `train_student.py` branches on `use_kd = cfg.training.get("use_kd", True)` —
  `True` → `KDTrainer` + frozen teacher; `False` → plain `Trainer` +
  `BinaryFocalLoss`, no teacher. `KDTrainer` (which reads
  `cfg.training.distillation`) must only be constructed in the `use_kd` branch.
  Flag any student-training change that reintroduces an unconditional `KDTrainer`
  or an unconditional `cfg.training.distillation` read (would re-crash
  `training=baseline` with `ConfigAttributeError: Missing key distillation`).
- [ ] New config keys read by a trainer exist in the relevant `configs/training/*.yaml`.

### B. Loss & objective (silent wrong-training class)
- [ ] Model `forward` returns `(B,)`; if a new head emits `(B,1)`, it must
  `.squeeze(1)` before the loss — shape mismatch or broadcast-silent-wrong.
- [ ] KD loss keeps weights **0.3 focal / 0.7 distill** and **T=4.0** (or reads
  them from config); the `T²` scaling on the distill term is present.
- [ ] Teacher is `freeze_backbone()`/`eval()` and under `torch.no_grad()` during
  student steps — an unfrozen teacher leaks gradients and invalidates the KD comparison.
- [ ] Teacher checkpoint is actually loaded before student training (not random weights).
- [ ] Focal/BCE applied to **logits** with the right reduction; no double sigmoid.
- [ ] **KD variants stay opt-in / back-compat:** `soft_loss_type` defaults to `bce` (constructed via
  `kd_cfg.get("soft_loss_type", "bce")`); the `mse` branch uses `F.mse_loss(student_logits, teacher_logits)`
  with **no** T² scaling. RKD is gated on `kd_cfg.get("feature_kd", None)` being present — no `feature_kd`
  block ⇒ `self.rkd is None` ⇒ zero behavior change to the main KD/baseline runs.
- [ ] **RKD correctness:** `RKDLoss` matches teacher-space distance/angle to student-space distance/angle
  (never compares `feat_s` vs `feat_t` directly — different dims). Teacher features come from
  `forward_features` under `torch.no_grad()`. `_pdist` clamps to ≥0 before `sqrt` and normalizes by the
  mean of **nonzero** distances (NaN guard). `forward_features` returns `(feat (B,C), logit (B,))` and must
  not perturb the plain `forward` path.

### C. Trainer mechanics (curve/metric class)
- [ ] Every key declared in `self.history = {...}` is `.append()`ed each epoch —
  `Trainer` historically declared `val_pauc` but never appended it →
  `plot_training_curves` shape mismatch. `KDTrainer` appends at
  [kd_trainer.py:104](src/training/kd_trainer.py#L104); a new subclass must too.
  (Same trap if RKD logging adds a `train_rkd_loss` history key — declare it only if you also `.append()`
  it every epoch; if not logging RKD, don't declare an empty key.)
- [ ] Early stopping reads `cfg.training.callbacks.early_stopping`; mode/patience
  match the monitored metric direction.
- [ ] Optimizer/scheduler step order correct; scheduler stepped per-epoch vs
  per-batch as intended; warmup honored.
- [ ] `set_epoch(epoch)` is called on the datamodule each epoch so the
  undersampler reshuffles (otherwise the same benign subset repeats).
- [ ] Checkpoint saved is the **best** (by the monitored metric), and reloaded
  for the final test-set eval — not the last-epoch weights.

### D. Metric reporting (don't mis-quote)
- [ ] `pauc_at_tpr()` is the real ISIC 2024 metric as of 2026-06-04 (range
  ~[0.02, 0.20]: random ≈ 0.02, perfect = 0.20). `val_pauc` / `pauc_at_tpr80`
  ARE now quotable as the ISIC metric. Any new metric code must keep the
  competition formulation (flip labels/scores → `roc_auc_score(max_fpr=1-min_tpr)`
  → invert McClish), NOT revert to raw-TPR integration. Logs/JSON produced
  **before** that date are still on the old stretched scale.
- [ ] `test_metrics.json` is written from the reloaded best checkpoint on the
  test dataloader. Since 2026-06-06 `test_split.csv` is an independent
  patient-disjoint holdout (carved before CV), so this is genuinely unbiased —
  a new change must not revert to the old `test = fold0-val` design.

### E. Registry / import graph (cluster ImportError class)
- [ ] New model class added to `MODEL_REGISTRY` AND re-exported names in
  `src/<pkg>/__init__.py` match the real `class`/`def` (a mismatch breaks the
  whole import graph from a Slurm job).
- [ ] Head input dim uses `infer_backbone_out_dim(backbone)`, NOT
  `backbone.num_features` (MobileNetV3 reports 960 but forwards 1280).
- [ ] `np.trapezoid` (not removed `np.trapz`) in any new metric/integration code.

## Don't
- Don't run/import on the Mac to confirm — verify via `validate-pipeline` then a
  `poc-smoke-test` (02_poc_teacher → 03_poc_student) on the cluster.
- Don't sign off a baseline/KD-flag change without confirming both arms compose
  (`config` and `config_poc`, `training=distillation` and `training=baseline`).
