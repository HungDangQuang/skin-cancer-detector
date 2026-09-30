# PAD-mixing ablation — convnextv2_base

Identical combined held-out test; only TRAIN+VAL differ (with-PAD = ISIC+PAD, no-PAD = ISIC-only).

- with-PAD folds: 5  |  no-PAD folds: 5


## Whole test (ISIC+PAD)

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.3214 ± 0.0643 | 0.6506 ± 0.0274 | +0.3292 |
| pauc_at_tpr80 | 0.1787 ± 0.0028 | 0.1822 ± 0.0019 | +0.0035 |
| auc_roc | 0.9740 ± 0.0040 | 0.9816 ± 0.0019 | +0.0077 |
| sensitivity | 0.9402 ± 0.0201 | 0.9203 ± 0.0106 | -0.0199 |
| specificity | 0.9018 ± 0.0223 | 0.9540 ± 0.0137 | +0.0522 |
| sens_at_95spec | 0.8606 ± 0.0369 | 0.9154 ± 0.0163 | +0.0548 |
| prevalence | 0.0039 ± 0.0000 | 0.0039 ± 0.0000 | +0.0000 |

**Verdict:** ❌ no clear win (ΔAUPRC=+0.3292, ΔSens=-0.0199; win iff both > 0)

## ISIC-source subset

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0588 ± 0.0240 | 0.0689 ± 0.0221 | +0.0101 |
| pauc_at_tpr80 | 0.1542 ± 0.0049 | 0.1485 ± 0.0075 | -0.0057 |
| auc_roc | 0.9366 ± 0.0070 | 0.9328 ± 0.0075 | -0.0037 |
| sensitivity | 0.8951 ± 0.0266 | 0.8918 ± 0.0304 | -0.0033 |
| specificity | 0.8536 ± 0.0286 | 0.8552 ± 0.0362 | +0.0016 |
| sens_at_95spec | 0.6656 ± 0.0222 | 0.6820 ± 0.0482 | +0.0164 |
| prevalence | 0.0010 ± 0.0000 | 0.0010 ± 0.0000 | +0.0000 |

**Verdict:** ❌ no clear win (ΔAUPRC=+0.0101, ΔSens=-0.0033; win iff both > 0)

## PAD-source subset  ← decisive cell

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.7159 ± 0.0244 | 0.8079 ± 0.0357 | +0.0920 |
| pauc_at_tpr80 | 0.0793 ± 0.0071 | 0.1149 ± 0.0148 | +0.0356 |
| auc_roc | 0.7611 ± 0.0159 | 0.8453 ± 0.0286 | +0.0842 |
| sensitivity | 0.7167 ± 0.0865 | 0.8422 ± 0.0554 | +0.1256 |
| specificity | 0.6995 ± 0.1012 | 0.7442 ± 0.0302 | +0.0447 |
| sens_at_95spec | 0.2078 ± 0.0562 | 0.3167 ± 0.0896 | +0.1089 |
| prevalence | 0.4775 ± 0.0000 | 0.4775 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.0920, ΔSens=+0.1256; win iff both > 0)
