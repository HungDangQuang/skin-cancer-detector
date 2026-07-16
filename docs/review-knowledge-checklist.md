# Thesis Knowledge Review Checklist

A self-study checklist covering every concept and technique in this project, ordered **fundamental → advanced**. Each item has: what to know, where it lives in the code, and a "be able to explain" prompt (the kind of question a thesis examiner asks). Tick a box once you can explain it *without looking*.

> **Project in one sentence:** Binary skin-cancer classification (benign=0 / malignant=1) where a large **teacher** distills knowledge into small, mobile-deployable **students**, evaluated with the official **ISIC 2024 pAUC@TPR≥80** metric on a patient-disjoint held-out test set, using 5-fold CV.

> **⚠️ Model set — read this first.** This checklist was first written for the **baseline set** (teacher `efficientnet_b4` → students `efficientnet_b0 / mobilenetv3_large / mobilevit_s`). The project has since moved to a **SOTA set** which is now the primary story:
> - **Teachers:** `convnextv2_base`, `maxvit_base` (both strong, AUPRC ~0.68), `efficientnetv2_m`; `efficientnet_b4` is now the **weak baseline teacher** (AUPRC 0.60 — lower than its own students).
> - **Students (mobile-latency-optimized):** `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2`.
> - All SOTA models use one generic `TimmBackboneModel` wrapper (needs `timm>=1.0`); the baseline models keep their family wrappers.
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

- [ ] **Teacher vs student capacity trade-off.** Why B4 (big, accurate) teaches B0/MobileNetV3/MobileViT (small, deployable). Know rough param counts & the efficiency motivation (mobile inference).
- [ ] **EfficientNet** — compound scaling (depth/width/resolution), MBConv blocks. *Code:* [efficientnet.py](../src/models/efficientnet.py).
- [ ] **MobileNetV3-Large** — depthwise-separable conv, squeeze-excite, h-swish. *Code:* [mobilenet.py](../src/models/mobilenet.py).
- [ ] **MobileViT-S** — hybrid CNN + transformer blocks for mobile. *Code:* [mobilevit.py](../src/models/mobilevit.py).
- [ ] **SOTA student set (current primary)** — all via one generic wrapper [timm_backbone.py](../src/models/timm_backbone.py):
  - [ ] **MobileNetV4-Conv-Medium** — pure-conv, best mobile latency/accuracy balance (22 ms on Pixel 6a). *Config:* [configs/student/mobilenetv4_conv_medium.yaml](../configs/student/mobilenetv4_conv_medium.yaml).
  - [ ] **FastViT-SA12** — hybrid CNN+transformer, highest pAUC but transformer penalty on ARM (65 ms). *Config:* `configs/student/fastvit_sa12.yaml`.
  - [ ] **EfficientFormerV2-S2** — highest AUPRC (0.684) but largest `.pte` (47 MB). *Config:* `configs/student/efficientformerv2_s2.yaml`.
  - [ ] *Explain:* why **latency ranking flips on real hardware** — CPU-proxy says fastvit ≈ mobilenetv4, but on-device fastvit is ~7.8× slower than mobilenetv3 (transformers pay a 3.4× ARM penalty). *Doc:* report_phase_1/benchmark, [MOBILE.md](MOBILE.md).
- [ ] **SOTA teacher set** — `convnextv2_base` (ConvNeXt V2, FCMAE-pretrained), `maxvit_base` (multi-axis attention), `efficientnetv2_m`. *Explain:* why a stronger teacher matters — see Tier 6 (teacher quality gates KD's AUPRC gain).
- [ ] **timm** as backbone source; `num_classes=0` returns features only. *Explain:* what `num_classes=0` does.
- [ ] **Backbone + head pattern & the registry.** `BaseModel` ABC, `forward → (B,)` raw logit, `freeze_backbone()`/`unfreeze()`. *Code:* [base_model.py](../src/models/base_model.py), [registry.py](../src/models/registry.py).
- [ ] **The `num_features` pitfall** — `infer_backbone_out_dim()` runs a dummy forward because `timm`'s reported `num_features` (e.g. MobileNetV3 says 960) ≠ true forward output (1280). *Code:* [heads.py](../src/models/heads.py). *Gotcha:* CLAUDE.md.

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
- [ ] **The two headline KD findings (know these cold — they ARE the thesis result):** *Doc:* [report_phase_1/evaluation/03_kd_effectiveness.md](../report_phase_1/evaluation/03_kd_effectiveness.md).
  - [ ] **(1) KD improves pAUC@80 and Sensitivity *consistently*** — Δ pAUC > 0 on **every** student×teacher pair (+0.001→+0.005); the high-sensitivity region (what matters for screening) always improves. This is the strongest, safest claim.
  - [ ] **(2) The AUPRC gain is *gated by teacher quality*** — a **strong** teacher (`convnextv2_base`) lifts MobileNetV4 AUPRC **+0.052** (0.609→0.661); a **weak** teacher (`efficientnet_b4`) gives Δ AUPRC in the noise or negative. *Explain:* distilling from a weak teacher only helps the high-sensitivity tail, not overall ranking. **Best case study = `mobilenetv4_conv_medium ← convnextv2_base`.**

---

## Tier 7 — Evaluation & metrics

- [ ] **ROC curve, AUC, TPR/FPR.** Foundation for everything below.
- [ ] **pAUC@TPR≥80 — the ISIC 2024 official metric.** Partial AUC over the high-sensitivity region only (TPR ∈ [0.8,1.0]), because below 80% sensitivity a cancer screener is clinically useless. *Code:* `pauc_at_tpr` in [metrics.py](../src/evaluation/metrics.py).
  - [ ] **Implementation trick:** flip labels/scores (`v_gt=1−y`, `v_pred=−p`) so "TPR≥0.8" becomes "FPR≤0.2", use sklearn `roc_auc_score(max_fpr=0.2)`, then **invert the McClish correction**. *Explain:* range is ~[0.02 random, 0.20 perfect].
  - [ ] **McClish correction** — what `max_fpr` rescaling does and why you must undo it to report the true partial area.
- [ ] **Sensitivity (recall/TPR), specificity (TNR), precision (PPV), F1.** *Code:* `compute_metrics`. *Explain:* why sensitivity dominates in cancer screening.
- [ ] **Youden's J threshold** `J = TPR − FPR`, maximize to pick the decision threshold. *Code:* `youden_threshold`. *Explain:* why a tuned threshold beats default 0.5 under imbalance.
- [ ] **Confusion matrix & TP/FP/TN/FN.** *Code:* [confusion_matrix.py](../src/evaluation/confusion_matrix.py).
- [ ] **Majority-class / random baselines** a model must beat. *Code:* `class_prevalence_baselines`.
- [ ] **Grad-CAM interpretability** — gradient-weighted class activation maps; finding the last conv layer. *Code:* [grad_cam.py](../src/evaluation/grad_cam.py). *Explain:* what a Grad-CAM heatmap shows and its limits.
- [ ] **Ensemble (probability averaging).** *Code:* [ensemble.py](../src/inference/ensemble.py).
- [ ] **Cross-domain & fairness evaluation** on HAM10000 / Fitzpatrick17k (never trained on). *Explain:* why per-skin-tone metrics matter ethically and what disparity would look like.

---

## Tier 8 — Experimental design & rigor

- [ ] **5-fold cross-validation** and why a single split is unreliable. *Explain:* what the 5 folds vary.
- [ ] **The paired-run design:** each student trained twice (KD / baseline) on identical folds+seed, per teacher. The baseline set was 3 arch × 2 × 5 = 30 runs; the SOTA matrix adds more student×teacher pairings (see the full ranking in [report_phase_1/evaluation/02_model_comparison.md](../report_phase_1/evaluation/02_model_comparison.md)). *Doc:* CLAUDE.md "Experiment design."
- [ ] **Fold-completeness caveat** — some SOTA pairs are not yet at 5 folds (maxvit-KD 1 fold, efficientformerv2_s2 2–4 folds); a claim from n<5 folds carries lower confidence. *Explain:* why you must say "n=4 folds, preliminary" rather than quote it as final.
- [ ] **Aggregation: report mean ± std** (not a single fold) — `aggregate_folds.py` → `aggregated.{json,md}`. *Explain:* why a lone fold's number is misleading.
- [ ] **Paired comparison** (KD vs baseline on identical folds/seed) and why pairing reduces variance.
- [ ] **Ablations** — `ratio × α` ablation (still TODO in the plan), augmentation choices. *Doc:* PREPROCESSING.md §3/§6.
- [ ] **Experiment tracking with MLflow.** *Cmd:* `mlflow ui --backend-store-uri experiments/runs`.
- [ ] **Hyperparameter tuning** entry point. *Code:* `scripts/tune_hyperparams.py`, `configs/training/ablation.yaml`.

---

## Tier 9 — Engineering & infrastructure (defend if asked)

- [ ] **Hydra config composition** — `defaults:` list composes data/teacher/student/training/augmentation groups; CLI overrides (`student=mobilenetv3_large training=baseline`). *Code:* [configs/config.yaml](../configs/config.yaml).
  - [ ] **Struct mode gotcha** — adding a top-level key needs `OmegaConf.set_struct(cfg, False)`; the `cfg.model` unification. *Gotcha:* CLAUDE.md.
  - [ ] **`load_config` must compose defaults** for standalone scripts (not just `@hydra.main`). *Gotcha:* CLAUDE.md.
- [ ] **Fold-aware run-dir convention** — `experiments/runs/<arch>/fold_{0..4}/...` so a Slurm array fills all folds without clobbering; `test_metrics.json` auto-written at end of training. *Doc:* CLAUDE.md.
- [ ] **Slurm on the UIT shared cluster** — array jobs (`--array=0-4%2`), `submit.sh` wrapper (`mkdir -p logs` first), `_lib.sh` strict mode, GPU acquisition, MPS. *Doc:* [SLURM.md](SLURM.md).
  - [ ] **Shared-cluster rule:** never kill/preempt/reset others' jobs — exhausted resources → job *queues* (PD). *Memory:* feedback_slurm_no_kill.
- [ ] **NumPy 2.0 note:** `np.trapz` → `np.trapezoid`. *Gotcha:* CLAUDE.md.
- [ ] **Local Mac ≠ cluster runtime** — no local pip/torch; verify with `validate-pipeline` (static) then cluster jobs. *Doc:* CLAUDE.md.

---

## Likely thesis-defense questions (rapid-fire self-test)

- [ ] Why pAUC@TPR≥80 instead of plain accuracy or AUC? (imbalance + clinical sensitivity floor)
- [ ] How do you *prove* a gain comes from KD and not luck? (paired baseline, same seed/folds, mean±std, delta)
- [ ] Where could data leakage sneak in, and how is each path closed? (patient grouping, dedup, namespacing, held-out test before CV)
- [ ] Why distill instead of just training a small model directly? (soft targets / dark knowledge → better small-model generalization; show the delta)
- [ ] What does T=4 and the T² factor do, concretely?
- [ ] Why α=0.25 in focal loss is questioned here, and what you'd ablate.
- [ ] Why quote test metrics over val metrics?
- [ ] What are the failure modes / limitations? (per-dataset exact-only dedup, untuned filter thresholds, 128→224 interpolation, single teacher, ablation still pending)

---

*Generated 2026-06-06 as a study aid; updated 2026-07-08 for the SOTA model set + headline KD findings. Source of truth remains the code, [CLAUDE.md](../CLAUDE.md), and `report_phase_1/`; if an item here ever disagrees with them, they win — update this file. Companion: [review-knowledge-summary-vi.md](review-knowledge-summary-vi.md) (Vietnamese tier-by-tier summary).*
