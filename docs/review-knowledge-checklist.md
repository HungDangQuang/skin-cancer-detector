# Thesis Knowledge Review Checklist

A self-study checklist covering every concept and technique in this project, ordered **fundamental → advanced**. Each item has: what to know, where it lives in the code, and a "be able to explain" prompt (the kind of question a thesis examiner asks). Tick a box once you can explain it *without looking*.

> **Project in one sentence:** Binary skin-cancer classification (benign=0 / malignant=1) where a large **teacher** distills knowledge into small, mobile-deployable **students**, evaluated with the official **ISIC 2024 pAUC@TPR≥80** metric on a patient-disjoint held-out test set, using 5-fold CV.

> **⚠️ Model set — read this first (the project is now SOTA-only).** This checklist was first written for a **baseline set** (teacher `efficientnet_b4` → students `efficientnet_b0 / mobilenetv3_large / mobilevit_s`). That entire set — and its family-specific wrapper files (`efficientnet.py`, `mobilenet.py`, `mobilevit.py`) — was **deleted** (2026-07-15). Old runs stay on disk but can no longer be rebuilt; `efficientnet_b4` is history, not a code path. The current registry ([registry.py](../src/models/registry.py)) is:
> - **Teachers (high-capacity, frozen during KD):** `efficientnetv2_m` (main), `convnextv2_base`, `maxvit_base` (retired from the run-plan but still registered), and the **domain-foundation** teacher `panderm` (PanDerm ViT-B/16, Nature Medicine 2025 — weights ship *out of timm*).
> - **Privileged (LUPI) teachers:** `efficientnetv2_m_privileged`, `convnextv2_base_privileged` — image ⊕ tabular-metadata fusion (see the new **Tier 6b — Metadata / privileged learning**).
> - **Students (mobile-/on-device-latency-optimized):** `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2`, `repvit_m1_0`.
> - **Every** timm model uses one generic `TimmBackboneModel` wrapper (needs `timm>=1.0`) — there are **no** per-arch family wrappers anymore. The two exceptions subclass it: `PanDermModel` (out-of-timm checkpoint loader) and `PrivilegedTimmBackboneModel` (metadata fusion).
> Use this file for **concepts**; use `report_phase_1/` for **current numbers, rankings, and the deploy recommendation** (best-balanced = `mobilenetv4_conv_medium ← convnextv2_base`).

---

## Tier 0 — Deep-learning fundamentals (must be automatic)

- [ ] **Binary classification with a single logit.** Model outputs one raw score; `sigmoid(logit)` → probability; threshold → class. *Code:* [heads.py](../src/models/heads.py) `build_head` = `Dropout → Linear(in,1)`. *Explain:* why output 1 logit instead of 2-class softmax?
- [ ] **Logits vs probabilities.** Why we train on logits (`BCEWithLogitsLoss` is numerically stable via log-sum-exp) and only apply `sigmoid` at inference. *Explain:* why not apply sigmoid inside the model?
- [ ] **Cross-entropy / BCE loss.** Definition of `-[y·log p + (1-y)·log(1-p)]`.
- [ ] **Gradient descent, backprop, epoch vs batch vs iteration.** *Code:* training loops in [trainer.py](../src/training/trainer.py).
- [ ] **Overfitting / underfitting, train-val-test roles.** Why the *test* number is the honest one.
- [ ] **CNN basics:** convolution, pooling, feature maps, receptive field.
- [ ] **Transfer learning & ImageNet pretraining.** Why we start from `pretrained=True` backbones instead of random init. *Code:* every model file calls `timm.create_model(..., pretrained=True)`.
- [ ] **Normalization with ImageNet mean/std** `[0.485,0.456,0.406]/[0.229,0.224,0.225]`. *Code:* [transforms.py](../src/data/transforms.py). *Explain:* why these exact numbers?

---

## Tier 1 — Problem domain

- [ ] **Skin-cancer screening task:** dermoscopy/clinical images, benign vs malignant; clinical cost asymmetry (a missed melanoma = false negative is far worse than a false alarm). *Explain:* why this drives a **sensitivity-focused** metric.
- [ ] **The datasets and their roles:**
  - [ ] **ISIC 2024 SLICE-3D** — primary training data; ~400k images, native ~128×128, **~0.9% malignant** (extreme imbalance). *Code:* `process_isic2024` in [preprocessing.py](../src/data/preprocessing.py).
  - [ ] **PAD-UFES-20** — smartphone clinical images, added for extra malignant positives; 6-class → binary mapping (BCC/SCC/MEL→1, ACK/NEV/SEK→0). *Code:* `process_pad_ufes_20`.
  - [ ] **The measured test prevalence is ~0.39%** (ISIC 2024 + PAD-UFES-20 held-out test set) — *this*, not the 0.9% ISIC-only figure, is the number to quote for the AUPRC random baseline. *Explain:* why AUPRC (not AUC-ROC) is the headline at this prevalence (Tier 7).
  - [ ] **HAM10000 / Fitzpatrick17k** — **never trained on**; held for cross-domain generalization & **fairness** (skin-tone) evaluation. *Code:* configs in [configs/data/](../configs/data/).
- [ ] **Domain shift:** training images vs the smartphone deployment domain; why dermatoscope-vignette augmentation was *dropped* (it would leak HAM-like features). *Doc:* [PREPROCESSING.md](PREPROCESSING.md) §4.
- [ ] **Why "128→224 upsampling is interpolation, not new detail"** — be ready to defend not calling it "high resolution." *Doc:* PREPROCESSING.md §1.

---

## Tier 2 — Data pipeline & class imbalance

- [ ] **Offline vs online preprocessing.** Offline = resize+clean to disk once; online = per-batch augmentation. *Explain:* why split it this way (cost, reproducibility).
- [ ] **Quality filtering** (each must be justifiable): corrupt-decode drop, `is_uninformative` (grayscale std<8 or >97% near-black/white), `min_size<32` drop, **exact md5 dedup of resized pixels**. *Code:* [preprocessing.py](../src/data/preprocessing.py). *Explain:* why dedup *before* splitting matters, and the rare-class safety rule (never auto-drop a malignant without a human look).
- [ ] **Label unification** to binary across datasets.
- [ ] **Leakage & patient grouping.** Same patient's lesions must not span train+val. *Code:* `generate_group_kfold_splits` uses `StratifiedGroupKFold(groups=patient_id)`. *Explain:* what goes wrong if you split by image instead of patient.
- [ ] **StratifiedGroupKFold** = stratify by label (keep benign:malignant ratio) **and** group by patient simultaneously.
- [ ] **Patient-id namespacing** (`pad_…`) to stop cross-dataset id collisions. *Gotcha:* CLAUDE.md "patient_id must be namespaced."
- [ ] **Independent held-out test set.** Carved patient-disjoint *before* the 5-fold CV (`test_holdout_splits=6`, ~17%); every fold is scored on the *same* untrained test set → paired-comparable. *Explain:* why the old "test = fold 0's val" design inflated metrics. *Doc:* PREPROCESSING.md §2.
- [ ] **Class-imbalance strategy as ONE tunable system** (not 3 stacked fixes):
  - [ ] **Dynamic undersampling 1:5**, benign pool re-drawn every epoch via `set_epoch`. *Code:* [sampler.py](../src/data/sampler.py). *Explain:* why re-draw each epoch (sees more benign diversity) vs static undersample.
  - [ ] **Focal loss** as the loss-level correction (Tier 4).
  - [ ] **The α/ratio interaction caveat:** α=0.25 was tuned for raw ~1000:1; after undersampling to ~16.7% positive it may over-suppress positives → ablate `ratio × α`. *Doc:* PREPROCESSING.md §3. *Explain:* this is the single most likely "did you think about it" question.
- [ ] **Augmentation pipeline (Albumentations), train-only, class-symmetric.** Flips, full 0–360° rotation, ShiftScaleRotate, ColorJitter, low-p CLAHE, GaussianBlur, then Normalize+ToTensorV2. *Code:* [transforms.py](../src/data/transforms.py). *Explain ordering:* why CLAHE/uint8 ops come **before** Normalize.
- [ ] **Augmentations deliberately NOT used** and why: stronger-aug-on-malignant (train/test skew), microscope circular crop (domain leak), CutOut (can erase the lesion → label noise), MixUp (breaks KD soft-target consistency). *Doc:* PREPROCESSING.md §4. *Explain:* be able to defend each rejection.
- [ ] **DataModule / Dataset / DataLoader split of responsibilities.** *Code:* [datamodule.py](../src/data/datamodule.py); sampler used for train, `shuffle=False` for val/test.

---

## Tier 3 — Model architectures

- [ ] **Teacher vs student capacity trade-off.** Why a big, accurate teacher (`efficientnetv2_m` / `convnextv2_base`) teaches a small, deployable student. Know rough param counts & the efficiency motivation (mobile inference).
- [ ] **One generic wrapper, no per-arch code.** Every timm model runs through `TimmBackboneModel` ([timm_backbone.py](../src/models/timm_backbone.py)); the old family wrappers (`efficientnet.py`/`mobilenet.py`/`mobilevit.py`) were deleted. *Explain:* what a wrapper actually does (backbone + `build_head` + `forward → (B,)` logit) and why one class suffices.
- [ ] **SOTA student set (current, all via `TimmBackboneModel`):**
  - [ ] **MobileNetV4-Conv-Medium** — pure-conv, best mobile latency/accuracy balance (22 ms on Pixel 6a). **The deploy pick.** *Config:* [configs/student/mobilenetv4_conv_medium.yaml](../configs/student/mobilenetv4_conv_medium.yaml).
  - [ ] **FastViT-SA12** — hybrid CNN+transformer, highest pAUC but transformer penalty on ARM (65 ms). *Config:* `configs/student/fastvit_sa12.yaml`.
  - [ ] **EfficientFormerV2-S2** — highest AUPRC (0.684) but largest `.pte` (47 MB). *Config:* `configs/student/efficientformerv2_s2.yaml`.
  - [ ] **RepViT-M1.0** — reparameterizable ViT-flavored conv net (train multi-branch, fuse to a plain conv net at inference → mobile-friendly). Added 2026-07. *Config:* `configs/student/repvit_m1_0.yaml`. *Explain:* what structural reparameterization buys at deploy.
  - [ ] *Explain:* why **latency ranking flips on real hardware** — CPU-proxy says fastvit ≈ mobilenetv4, but on-device fastvit is ~7.8× slower than a conv student (transformers pay a ~3.4× ARM penalty). *Doc:* report_phase_1/benchmark, [MOBILE.md](MOBILE.md).
- [ ] **SOTA teacher set** — `efficientnetv2_m` (main), `convnextv2_base` (ConvNeXt V2, FCMAE-pretrained), `maxvit_base` (multi-axis attention, *retired from the run-plan but still registered*). *Explain:* why a stronger teacher matters — see Tier 6 (teacher quality gates KD's AUPRC gain).
- [ ] **PanDerm foundation teacher** (`panderm`) — a **domain-specific** foundation model (ViT-B/16, pretrained on ~2.1M skin images, Nature Medicine 2025). Ships as a **BEiT-style checkpoint out of timm** (Google Drive, CC-BY-NC-4.0), so `PanDermModel` ([panderm.py](../src/models/panderm.py)) builds a structurally-compatible timm ViT-B/16 and loads the weights over the backbone with a **loud remapping loader that raises if too few tensors match** (so a wrong arch fails loudly instead of training a near-random net). *Explain:* general-ImageNet vs domain-foundation pretraining, and why the loud loader matters. *Doc:* [SOTA_MODEL_DECISION_2026-07.md](SOTA_MODEL_DECISION_2026-07.md) §5.
- [ ] **timm** as backbone source; `num_classes=0` returns features only. *Explain:* what `num_classes=0` does.
- [ ] **Backbone + head pattern & the registry.** `BaseModel` ABC, `forward → (B,)` raw logit, `freeze_backbone()`/`unfreeze()`. *Code:* [base_model.py](../src/models/base_model.py), [registry.py](../src/models/registry.py). *Explain:* how you'd add a new arch (register against `TimmBackboneModel` + add a `configs/{student,teacher}/*.yaml`).
- [ ] **`forward_features(x) → (feat, logit)`** — the second entry point every model exposes, tapped only when RKD feature-KD is on (Tier 6). *Explain:* why the logit path stays bit-identical whether or not features are read.
- [ ] **The `num_features` pitfall** — `infer_backbone_out_dim()` runs a dummy forward because `timm`'s reported `num_features` is unreliable as the head input dim. *Code:* [heads.py](../src/models/heads.py). *Gotcha:* CLAUDE.md.

---

## Tier 4 — Loss functions

- [ ] **BCEWithLogitsLoss** baseline.
- [ ] **Binary Focal Loss** `α·(1-pt)^γ·CE`. Role of **γ** (focus on hard examples) and **α** (class prior weight). *Code:* [losses.py](../src/training/losses.py). *Reference:* Lin et al. 2017. *Explain:* derive how γ down-weights easy examples; why `pt = p if y=1 else 1-p`.
- [ ] **Why focal over plain BCE here** (extreme imbalance + many easy benign).
- [ ] **Interaction with undersampling** (links back to Tier 2 α/ratio ablation).

---

## Tier 5 — Training mechanics

- [ ] **AdamW** and weight decay (decoupled vs L2). *Code:* [optimizers.py](../src/training/optimizers.py).
- [ ] **Differential / discriminative learning rates** — lower LR for pretrained backbone, higher for fresh head (`lr_backbone=1e-4`, `lr_head=1e-3`). *Explain:* why the head needs a bigger LR.
- [ ] **Cosine annealing + linear warmup** (`SequentialLR`, `warmup_epochs=3`). *Code:* [schedulers.py](../src/training/schedulers.py). *Explain:* what warmup prevents early in training.
- [ ] **Gradient clipping** (`clip_grad_norm_`, `grad_clip=1.0`) — exploding-gradient guard.
- [ ] **Early stopping** (patience on `val_loss`). *Code:* [callbacks.py](../src/training/callbacks.py).
- [ ] **Model checkpointing on best `val_pauc`** (`mode=max`) while early-stopping watches `val_loss` — know that these monitor *different* signals and why. *Code:* callbacks + `*_trainer.py` `checkpoint.step`.
- [ ] **Reproducibility / seeding.** *Code:* [seed.py](../src/utils/seed.py), `seed=42` everywhere.
- [ ] **Biased val vs unbiased test.** Val metrics are optimized against (early stopping/checkpoint selection) → **quote `test_metrics.json`, not `val_pauc`, for verdicts.** *Doc:* CLAUDE.md run-dir convention. *Explain:* this is a defense-critical distinction.

---

## Tier 6 — Knowledge Distillation (the thesis core)

- [ ] **KD concept (Hinton et al. 2015):** a small student mimics a large teacher's *soft* outputs, which carry "dark knowledge" (relative confidences) beyond hard labels.
- [ ] **The binary KD loss** implemented here:
  `L = α·L_focal(student, true) + (1−α)·T²·BCE(sigmoid(s/T), sigmoid(t/T))`, with **T=4.0, α=0.3** (30% hard / 70% soft). *Code:* [distillation.py](../src/training/distillation.py).
- [ ] **Temperature T** — softens both distributions; higher T = softer. *Explain:* what happens as T→1 and T→∞.
- [ ] **The T² factor** — why soft-loss gradients are rescaled by T² so hard/soft gradient magnitudes stay comparable. *Explain:* a classic exam question.
- [ ] **Frozen teacher** — `requires_grad=False`, `eval()`, `torch.no_grad()` for teacher forward. *Code:* [kd_trainer.py](../src/training/kd_trainer.py) `__init__` + `_train_epoch`. *Explain:* why the teacher must not update.
- [ ] **Baseline vs KD arm** — same student, same data/seed/hparams, trained with (`KDTrainer`) and without (`Trainer`) KD via the `use_kd` flag. *Code:* `train_student.py`; *Gotcha:* CLAUDE.md "use_kd flag." *Explain:* why an identical-everything-but-KD pairing is required to attribute the gain to KD.
- [ ] **KD effectiveness delta** `delta_pauc = pauc_KD − pauc_baseline`. *Code:* `compute_kd_delta` in [metrics.py](../src/evaluation/metrics.py).
- [ ] **KD variant 1 — MSE-on-logits soft loss** (`training.distillation.soft_loss_type=mse`, Kim et al. 2021): replaces the T²-scaled soft BCE with `MSE(student_logit, teacher_logit)` on the *raw* logits — **no temperature, no T²** (≈ KL at large T). Default stays `bce`. *Code:* [distillation.py](../src/training/distillation.py). *Explain:* why matching raw logits directly is an alternative to temperature-softened BCE, and what you give up (no T knob).
- [ ] **KD variant 2 — Relational KD (RKD) feature distillation** (`training=distillation_rkd`, Park et al. 2019): adds a **feature-level** term on top of the logit KD loss. Motivation: at K=1 (binary) a single logit carries little to distill, so RKD instead matches the **within-batch pairwise DISTANCE + triplet ANGLE** of the penultimate features. *Code:* `RKDLoss` in [feature_distillation.py](../src/training/feature_distillation.py). Key properties to be able to explain:
  - [ ] **Projector-free / dim-agnostic** — each side's relational matrix is computed *within its own* feature space then normalized, so teacher-dim ≠ student-dim is fine (never compare features element-wise across spaces).
  - [ ] **Trainer taps `forward_features(x) → (feat, logit)`** only when the `feature_kd` block is present; remove the block → plain logit KD, byte-for-byte.
  - [ ] **Numerical-safety detail:** `_pdist` clamps squared distances to a small `eps` *before* `sqrt` (else NaN gradient on the zero-distance diagonal).
- [ ] **The two headline KD findings (know these cold — they ARE the thesis result):** *Doc:* [report_phase_1/evaluation/03_kd_effectiveness.md](../report_phase_1/evaluation/03_kd_effectiveness.md).
  - [ ] **(1) KD improves pAUC@80 and Sensitivity *consistently*** — Δ pAUC > 0 on **every** student×teacher pair (+0.001→+0.005); the high-sensitivity region (what matters for screening) always improves. This is the strongest, safest claim.
  - [ ] **(2) The AUPRC gain is *gated by teacher quality*** — a **strong** teacher (`convnextv2_base`) lifts MobileNetV4 AUPRC **+0.052** (0.609→0.661); a **weak** teacher (`efficientnet_b4`, from a now-retired baseline run kept on disk for this contrast) gives Δ AUPRC in the noise or negative. *Explain:* distilling from a weak teacher only helps the high-sensitivity tail, not overall ranking. **Best case study = `mobilenetv4_conv_medium ← convnextv2_base`.**

---

## Tier 6b — Metadata & privileged learning (LUPI)  *(opt-in; default off)*

> Everything here is **gated behind config flags and defaults OFF**, so the image-only matrix is byte-for-byte unchanged. *Doc:* [metadata_training_plan.md](metadata_training_plan.md).

- [ ] **The core paradox — why metadata is *not* sold as a deploy-time pAUC lever.** The strongest metadata signal is the ISIC `tbp_lv_*` columns (39 features) produced by **Vectra WB360 3D-TBP hardware** — unavailable on a phone. So it cannot be an input to an image-only deployable model; its honest contributions are **calibration** and a truthful **privileged-teacher ablation**.
- [ ] **Two independent gates (know which turns on what):**
  - [ ] `data.metadata_cols` — *which* raw columns are carried into the split CSVs. Enables **direction D** alone (model stays image-only; cols ride a `predictions.csv` side-channel via `DataModule.test_metadata()`).
  - [ ] `data.metadata_as_input` — whether the dataset feeds metadata into the batch as a **4-tuple `(image, meta, mask, label)`**. Enables **direction A** (needs *both* gates).
- [ ] **Direction D — calibration + subgroup evaluation** (safest, no retraining). Re-run `prepare` with `metadata_cols=[anatom_site_general, sex]` (split is seed-deterministic → same rows, just extra cols → old checkpoints still valid), then re-eval; `compute_calibration.py --subgroup <col>` reports per-group ECE/Brier. *Explain:* why a single **global** correction is used (too few positives per group at 0.39% to fit a per-group calibrator).
- [ ] **Direction A — privileged (LUPI) teacher.** `PrivilegedTimmBackboneModel` ([privileged.py](../src/models/privileged.py)) = timm image backbone ⊕ a small tabular MLP over standardized `tbp_lv_*`, fused → head. **Only the teacher sees metadata**; the image-only student distills the *fused feature structure* via **RKD** (projector-free, so teacher-fused-dim > student-image-dim is fine). *Config:* `configs/teacher/*_privileged.yaml` + `training=distillation_privileged`. *Explain:* the LUPI idea — privileged info present at train time, absent at test time, leaks only as relational structure, never as a student input → nothing on the `.pte`/benchmark path changes.
  - [ ] **`accepts_metadata=True`** tells `Trainer`/`KDTrainer` to feed `(images, meta, mask)`; the `mask` zeros the tabular branch for rows with no metadata (e.g. all PAD rows) so they don't backprop through it.
- [ ] **Leakage discipline** — `iddx_*` / `mel_*` columns are **rejected** (`_validate_metadata_cols` raises); the metadata scaler is fit on the **train fold only** (then pushed to val/test) so nothing leaks. *Explain:* why post-hoc diagnosis columns are leakage.
- [ ] **`unpack_batch`** ([src/utils/batch.py](../src/utils/batch.py)) — the single choke-point every DataLoader consumer uses to accept a 2- **or** 4-tuple; the plain image-only path returns `meta=mask=None` and runs the old code unchanged.

---

## Tier 7 — Evaluation & metrics

- [ ] **ROC curve, AUC, TPR/FPR.** Foundation for everything below.
- [ ] **AUPRC is the *clinical headline*, not AUC-ROC.** At the measured ~0.39% prevalence AUC-ROC is optimistic (huge TN pool); AUPRC (area under precision–recall, random baseline = prevalence) is the honest imbalance metric. **pAUC = ISIC-benchmark-comparison metric; AUPRC = clinical headline** — two roles, not a contradiction. *Code:* `compute_metrics` in [metrics.py](../src/evaluation/metrics.py) returns `auprc` + `prevalence`. *Explain:* why the same model can look great on AUC-ROC and mediocre on AUPRC.
- [ ] **pAUC@TPR≥80 — the ISIC 2024 official metric.** Partial AUC over the high-sensitivity region only (TPR ∈ [0.8,1.0]), because below 80% sensitivity a cancer screener is clinically useless. *Code:* `pauc_at_tpr` in [metrics.py](../src/evaluation/metrics.py).
  - [ ] **Implementation trick:** flip labels/scores (`v_gt=1−y`, `v_pred=−p`) so "TPR≥0.8" becomes "FPR≤0.2", use sklearn `roc_auc_score(max_fpr=0.2)`, then **invert the McClish correction**. *Explain:* range is ~[0.02 random, 0.20 perfect].
  - [ ] **McClish correction** — what `max_fpr` rescaling does and why you must undo it to report the true partial area.
- [ ] **Sensitivity (recall/TPR), specificity (TNR), precision (PPV), F1.** *Code:* `compute_metrics`. *Explain:* why sensitivity dominates in cancer screening.
- [ ] **Youden's J threshold** `J = TPR − FPR`, maximize to pick the decision threshold. *Code:* `youden_threshold`. *Explain:* why a tuned threshold beats default 0.5 under imbalance.
- [ ] **Confusion matrix & TP/FP/TN/FN.** *Code:* [confusion_matrix.py](../src/evaluation/confusion_matrix.py).
- [ ] **Majority-class / random baselines** a model must beat. *Code:* `class_prevalence_baselines`.
- [ ] **Grad-CAM interpretability** — gradient-weighted class activation maps; finding the last conv layer. *Code:* [grad_cam.py](../src/evaluation/grad_cam.py). *Explain:* what a Grad-CAM heatmap shows and its limits.
- [ ] **Ensemble (probability averaging).** *Code:* [ensemble.py](../src/inference/ensemble.py).
- [ ] **Calibration ≠ ranking.** `brier` / `ece` in `test_metrics.json` are the **RAW** miscalibration: the 1:5 undersampler trains on a ~16.7% prior, so `sigmoid(logit)` is over-confident vs the true ~0.39% prevalence. *Explain:* the difference between *ranking* quality and *probability* honesty.
  - [ ] **`compute_calibration.py --run-dir <run>`** fixes only the *displayed* probability offline: **prior-shift** closed form by default (`logit_cal = logit(p) + logit(π_target) − logit(π_train)`), or Platt/isotonic (`--method`) fit on `val_predictions.csv` (the val loader has **no sampler** → keeps the true prevalence). *Explain:* why ranking metrics (pAUC/AUPRC/AUC) are invariant to any monotone re-scaling → **this changes no Chapter-4 number**, only the shown "% risk". *Code:* [compute_calibration.py](../scripts/compute_calibration.py).
  - [ ] **Caveat:** focal `α=0.25` distorts calibration *beyond* the prior term, so prior-shift alone may leave ECE high → then use isotonic/Platt.
- [ ] **Recomputable prediction side-files.** `Evaluator.save_predictions()` writes `predictions.csv` (`y_true,y_prob,y_pred[,source]`) next to `test_metrics.json`, plus `val_predictions.csv` — so PR-curve / AUPRC / **per-domain (ISIC-vs-PAD via `source`)** / bootstrap CIs are recomputable offline **without re-running inference**. *Explain:* why per-domain breakdown matters (smartphone PAD vs dermoscopy ISIC are different operating regimes).
- [ ] **Cross-domain & fairness evaluation** on HAM10000 / Fitzpatrick17k (never trained on). *Explain:* why per-skin-tone metrics matter ethically and what disparity would look like.

---

## Tier 8 — Experimental design & rigor

- [ ] **5-fold cross-validation** and why a single split is unreliable. *Explain:* what the 5 folds vary.
- [ ] **The paired-run design:** each student trained twice (KD / baseline) on identical folds+seed, per teacher. **The canonical "30 runs" = 3 *students* × 2 KD conditions × 5 folds for ONE fixed teacher** ("3 arch" means students, not teachers). *Explain:* don't quote "30" as the project total — the registry has 3 (+privileged) teachers and 4 students, so the real matrix is larger (~62 new fold-runs after the 2026-07-16 model-set decision, plus opt-in KD-variant / privileged branches). Report the *actual* teacher scope. Full ranking: [report_phase_1/evaluation/02_model_comparison.md](../report_phase_1/evaluation/02_model_comparison.md). *Doc:* CLAUDE.md "Experiment design."
- [ ] **Fold-completeness caveat** — some SOTA pairs are not yet at 5 folds (maxvit-KD 1 fold, efficientformerv2_s2 2–4 folds); a claim from n<5 folds carries lower confidence. *Explain:* why you must say "n=4 folds, preliminary" rather than quote it as final.
- [ ] **Aggregation: report mean ± std** (not a single fold) — `aggregate_folds.py` → `aggregated.{json,md}`. *Explain:* why a lone fold's number is misleading.
- [ ] **Paired comparison** (KD vs baseline on identical folds/seed) and why pairing reduces variance.
- [ ] **Ablations** — `ratio × α` ablation (still TODO in the plan), augmentation choices. *Doc:* PREPROCESSING.md §3/§6.
- [ ] **Experiment tracking with MLflow.** *Cmd:* `mlflow ui --backend-store-uri experiments/runs`.
- [ ] **Hyperparameter tuning** entry point. *Code:* `scripts/tune_hyperparams.py`, `configs/training/ablation.yaml`.

---

## Tier 9 — Engineering & infrastructure (defend if asked)

- [ ] **Hydra config composition** — `defaults:` list composes data/teacher/student/training/augmentation groups; CLI overrides (e.g. `student=fastvit_sa12 training=baseline`, or `teacher=convnextv2_base`). *Code:* [configs/config.yaml](../configs/config.yaml).
  - [ ] **Struct mode gotcha** — adding a top-level key needs `OmegaConf.set_struct(cfg, False)`; the `cfg.model` unification. *Gotcha:* CLAUDE.md.
  - [ ] **`load_config` must compose defaults** for standalone scripts (not just `@hydra.main`). *Gotcha:* CLAUDE.md.
- [ ] **Fold-aware run-dir convention** — `experiments/runs/<arch>/fold_{0..4}/...` so one job fills all 5 folds without clobbering; `test_metrics.json` + `val_metrics.json` + `predictions.csv` + `val_predictions.csv` auto-written at end of training. *Doc:* CLAUDE.md.
- [ ] **One process per model, folds loop *sequentially*** — `run/train_teacher.sh` / `run/train_student.sh` are **single** processes that loop `for FOLD in ${FOLDS:-0 1 2 3 4}` internally. Split a heavy run with `FOLDS="0 1 2"` + `FOLDS="3 4"`. *Doc:* [run/README.md](../run/README.md), CLAUDE.md.
- [ ] **The `run/` execution layer** — `run/common.sh` gives every script `set -euo pipefail`, `activate_venv` (`./.venv-linux`), `select_gpu` (`GPU=auto|<id>|cpu` → `CUDA_VISIBLE_DEVICES`) and `start_log` (tees to `logs/<name>_<timestamp>.log`, survives an SSH drop). *Doc:* [run/README.md](../run/README.md).
  - [ ] **Run-dir isolation rule:** students fork with `run_suffix=`, teachers with `output_dir=` — `train_teacher.py` ignores `run_suffix` and would overwrite the main run. *Gotcha:* [GOTCHAS.md](GOTCHAS.md).
  - [ ] **Shared-server rule:** everything stays inside the project folder — no sudo/apt/system-python, deps only in `./.venv-linux`, env vars per session. *Memory:* feedback_project_scoped_only.
- [ ] **NumPy 2.0 note:** `np.trapz` → `np.trapezoid`. *Gotcha:* CLAUDE.md.
- [ ] **Local Mac ≠ server runtime** — no local pip/torch; verify with `validate-pipeline` (static) then run on the server. *Doc:* CLAUDE.md.

---

## Likely thesis-defense questions (rapid-fire self-test)

- [ ] Why pAUC@TPR≥80 instead of plain accuracy or AUC? (imbalance + clinical sensitivity floor)
- [ ] How do you *prove* a gain comes from KD and not luck? (paired baseline, same seed/folds, mean±std, delta)
- [ ] Where could data leakage sneak in, and how is each path closed? (patient grouping, dedup, namespacing, held-out test before CV)
- [ ] Why distill instead of just training a small model directly? (soft targets / dark knowledge → better small-model generalization; show the delta)
- [ ] What does T=4 and the T² factor do, concretely?
- [ ] Why α=0.25 in focal loss is questioned here, and what you'd ablate.
- [ ] Why quote test metrics over val metrics?
- [ ] Why is AUPRC the headline instead of AUC-ROC at 0.39% prevalence? (huge TN pool makes AUC-ROC optimistic; AUPRC's baseline = prevalence)
- [ ] Your probabilities are over-confident — does that hurt your results? (No: ranking metrics are scale-invariant; calibration is a separate, offline prior-shift fix that changes no Chapter-4 number)
- [ ] You added metadata but claim an image-only deploy model — how? (LUPI: only the teacher sees `tbp_lv_*`; the student distills the fused *structure* via RKD, never takes metadata as input; `tbp_lv_*` is undeployable 3D-TBP hardware output)
- [ ] Which metadata columns are forbidden and why? (`iddx_*`/`mel_*` are post-hoc diagnosis → leakage; scaler fit on train fold only)
- [ ] Why two KD soft-loss variants (BCE vs MSE) and why add RKD? (MSE = temperature-free logit matching; RKD adds feature-structure signal because a single binary logit distills little)
- [ ] What are the failure modes / limitations? (per-dataset exact-only dedup, untuned filter thresholds, 128→224 interpolation, some SOTA pairs at n<5 folds, α×ratio ablation still pending, PanDerm weights/arch pending server verification)

---

*Generated 2026-06-06 as a study aid; updated 2026-07-08 for the SOTA model set + headline KD findings; updated 2026-07-19 for the SOTA-only registry (baseline set deleted; +repvit, +panderm, +privileged teachers), the two KD variants (MSE-logit, RKD feature-KD), the new Tier 6b metadata/LUPI material, calibration + AUPRC/per-domain evaluation, and the one-process-per-model run/ design. Source of truth remains the code, [CLAUDE.md](../CLAUDE.md), and `report_phase_1/`; if an item here ever disagrees with them, they win — update this file. Companions: [review-knowledge-summary-vi.md](review-knowledge-summary-vi.md) (Vietnamese tier-by-tier summary) and [review-10-day-plan-vi.md](review-10-day-plan-vi.md) (bilingual 10-day self-study schedule; also drivable interactively via the `knowledge-tutor` sub-agent).*
