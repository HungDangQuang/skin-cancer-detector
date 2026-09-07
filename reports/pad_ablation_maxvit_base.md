# PAD-mixing ablation — maxvit_base

Identical combined held-out test; only TRAIN+VAL differ (with-PAD = ISIC+PAD, no-PAD = ISIC-only).

- with-PAD folds: 5  |  no-PAD folds: 5


## Whole test (ISIC+PAD)

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.1863 ± 0.0361 | 0.6566 ± 0.0188 | +0.4703 |
| pauc_at_tpr80 | 0.1756 ± 0.0043 | 0.1830 ± 0.0022 | +0.0074 |
| auc_roc | 0.9673 ± 0.0067 | 0.9824 ± 0.0022 | +0.0150 |
| sensitivity | 0.9195 ± 0.0163 | 0.9245 ± 0.0066 | +0.0050 |
| specificity | 0.9038 ± 0.0319 | 0.9490 ± 0.0098 | +0.0452 |
| sens_at_95spec | 0.8324 ± 0.0452 | 0.9170 ± 0.0037 | +0.0846 |
| prevalence | 0.0039 ± 0.0000 | 0.0039 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.4703, ΔSens=+0.0050; win iff both > 0)

## ISIC-source subset

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0416 ± 0.0100 | 0.0592 ± 0.0137 | +0.0175 |
| pauc_at_tpr80 | 0.1568 ± 0.0069 | 0.1515 ± 0.0079 | -0.0053 |
| auc_roc | 0.9390 ± 0.0098 | 0.9366 ± 0.0085 | -0.0024 |
| sensitivity | 0.8984 ± 0.0350 | 0.9082 ± 0.0422 | +0.0098 |
| specificity | 0.8529 ± 0.0300 | 0.8440 ± 0.0279 | -0.0089 |
| sens_at_95spec | 0.6951 ± 0.0245 | 0.7082 ± 0.0123 | +0.0131 |
| prevalence | 0.0010 ± 0.0000 | 0.0010 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.0175, ΔSens=+0.0098; win iff both > 0)

## PAD-source subset  ← decisive cell

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.7034 ± 0.0152 | 0.8345 ± 0.0188 | +0.1311 |
| pauc_at_tpr80 | 0.0750 ± 0.0119 | 0.1102 ± 0.0062 | +0.0352 |
| auc_roc | 0.7551 ± 0.0147 | 0.8552 ± 0.0133 | +0.1001 |
| sensitivity | 0.7133 ± 0.0987 | 0.8389 ± 0.0261 | +0.1256 |
| specificity | 0.7066 ± 0.0818 | 0.7452 ± 0.0507 | +0.0386 |
| sens_at_95spec | 0.1711 ± 0.0373 | 0.4033 ± 0.0556 | +0.2322 |
| prevalence | 0.4775 ± 0.0000 | 0.4775 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.1311, ΔSens=+0.1256; win iff both > 0)
