# QA 002 — Does the project have a training strategy for the highly imbalanced dataset?

**Status:** verified 2026-06-10 · training

## Question
The dataset is highly imbalanced, does the current project have the training strategy to resolve this problem?

## Answer
Yes. Class imbalance is addressed at **four** independent layers of the pipeline rather than a single fix, which matters because the malignant prevalence in ISIC 2024 is well under 1% — no one mechanism is sufficient on its own.

1. **Imbalance-aware loss — Binary Focal Loss.** Both the teacher and the hard-label term of the student's KD loss use `BinaryFocalLoss` (γ=2.0, α=0.25), which down-weights the easy, abundant benign examples via the `(1−pₜ)^γ` modulating factor and up-weights the rare malignant class via α ([src/training/losses.py:6-41](../src/training/losses.py#L6-L41), configured in [configs/training/default.yaml:20-22](../configs/training/default.yaml#L20-L22) and [configs/training/distillation.yaml:22-24](../configs/training/distillation.yaml#L22-L24)). For the distilled students the focal term is the `L_hard` component of `BinaryDistillationLoss` ([src/training/distillation.py:8](../src/training/distillation.py#L8)).

2. **Dynamic undersampling at the batch level.** `DynamicUndersampledSampler` keeps **all** malignant samples every epoch and randomly draws a 1:5 (malignant:benign) subset of benign samples, re-shuffling the benign pool each epoch so the model still sees the full benign distribution over training while each epoch is far more balanced ([src/data/sampler.py:6-51](../src/data/sampler.py#L6-L51)). It is wired into the train dataloader only (val/test stay unsampled) and is on by default with `undersample_ratio: 5` ([src/data/datamodule.py:56-74](../src/data/datamodule.py#L56-L74), [configs/data/isic2024.yaml:39-40](../configs/data/isic2024.yaml#L39-L40)).

3. **Stratified, leakage-free splits.** Both the held-out test carve and the 5-fold CV use `StratifiedGroupKFold` — stratified by label so the rare class is proportionally represented in every fold, and grouped by `patient_id` so no patient leaks across folds ([src/data/preprocessing.py:307-381](../src/data/preprocessing.py#L307-L381)). This keeps the minority count stable across all splits.

4. **Imbalance-robust evaluation, not accuracy.** The headline metric is **pAUC@TPR≥80** (the ISIC 2024 official metric), a threshold-region-restricted AUC that is insensitive to prevalence, and the decision threshold is chosen by **Youden's J** (max TPR−FPR) rather than the default 0.5, so the operating point is set for sensitivity rather than overall accuracy ([src/evaluation/metrics.py:47-105](../src/evaluation/metrics.py#L47-L105)). Accuracy alone would be misleading here — a model predicting "benign" always would score ~99%.

**Evidence it works:** on the best student (KD MobileNetV3-Large, 5-fold aggregate, read 2026-06-10) sensitivity/recall is **0.955 ± 0.005** at specificity 0.936 ± 0.008 and pAUC 0.1881 ± 0.0010 — i.e. the strategy recovers the minority malignant class (≈230 of 241 caught per fold) despite the extreme skew ([experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/aggregated.md](../experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/aggregated.md)). The trade-off is low precision (≈0.056) — high false-positive count — which is the expected and clinically acceptable bias for a screening model tuned toward sensitivity. Re-confirm against `aggregated.md` before citing as final.

## Evidence
- [src/training/losses.py:6-41](../src/training/losses.py#L6-L41) — `BinaryFocalLoss` (γ, α) down-weights easy/majority examples.
- [src/data/sampler.py:6-51](../src/data/sampler.py#L6-L51) — `DynamicUndersampledSampler` keeps all malignants + 1:5 benign, reshuffled per epoch.
- [src/data/datamodule.py:56-74](../src/data/datamodule.py#L56-L74) + [configs/data/isic2024.yaml:39-40](../configs/data/isic2024.yaml#L39-L40) — sampler on by default, `undersample_ratio: 5`, train-only.
- [src/training/distillation.py:8](../src/training/distillation.py#L8) — focal loss is the hard-label term of the student KD loss.
- [src/data/preprocessing.py:307-381](../src/data/preprocessing.py#L307-L381) — `StratifiedGroupKFold` keeps minority class proportional and patient-disjoint across folds.
- [src/evaluation/metrics.py:47-105](../src/evaluation/metrics.py#L47-L105) — pAUC@TPR≥80 + Youden-J threshold = prevalence-robust evaluation.
- [experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/aggregated.md](../experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/aggregated.md) — sensitivity 0.955 ± 0.005 (5-fold), read 2026-06-10; re-confirm before final citation.

## For the thesis
The project mitigates the extreme class imbalance of ISIC 2024 through a combined strategy operating at four levels — a focal-loss objective, dynamic 1:5 per-epoch undersampling, label-stratified patient-grouped cross-validation splits, and a prevalence-robust evaluation protocol (pAUC@TPR≥80 with a Youden-J-selected threshold) — which together yield 95.5% ± 0.5% sensitivity to the minority malignant class on the held-out test set.
