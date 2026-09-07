# PAD-mixing ablation — efficientnetv2_m

Identical combined held-out test; only TRAIN+VAL differ (with-PAD = ISIC+PAD, no-PAD = ISIC-only).

- with-PAD folds: 5  |  no-PAD folds: 5


## Whole test (ISIC+PAD)

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.1462 ± 0.0170 | 0.6298 ± 0.0436 | +0.4837 |
| pauc_at_tpr80 | 0.1666 ± 0.0044 | 0.1826 ± 0.0022 | +0.0160 |
| auc_roc | 0.9554 ± 0.0048 | 0.9820 ± 0.0022 | +0.0265 |
| sensitivity | 0.9054 ± 0.0085 | 0.9270 ± 0.0175 | +0.0216 |
| specificity | 0.8885 ± 0.0175 | 0.9442 ± 0.0154 | +0.0557 |
| sens_at_95spec | 0.7917 ± 0.0194 | 0.9120 ± 0.0080 | +0.1203 |
| prevalence | 0.0039 ± 0.0000 | 0.0039 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.4837, ΔSens=+0.0216; win iff both > 0)

## ISIC-source subset

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0605 ± 0.0093 | 0.0640 ± 0.0181 | +0.0035 |
| pauc_at_tpr80 | 0.1472 ± 0.0101 | 0.1509 ± 0.0084 | +0.0037 |
| auc_roc | 0.9264 ± 0.0138 | 0.9340 ± 0.0085 | +0.0076 |
| sensitivity | 0.8492 ± 0.0445 | 0.8590 ± 0.0410 | +0.0098 |
| specificity | 0.8687 ± 0.0364 | 0.8920 ± 0.0241 | +0.0232 |
| sens_at_95spec | 0.6590 ± 0.0675 | 0.6656 ± 0.0396 | +0.0066 |
| prevalence | 0.0010 ± 0.0000 | 0.0010 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.0035, ΔSens=+0.0098; win iff both > 0)

## PAD-source subset  ← decisive cell

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.6616 ± 0.0279 | 0.7857 ± 0.0544 | +0.1241 |
| pauc_at_tpr80 | 0.0673 ± 0.0044 | 0.1023 ± 0.0116 | +0.0349 |
| auc_roc | 0.7113 ± 0.0154 | 0.8181 ± 0.0434 | +0.1068 |
| sensitivity | 0.7433 ± 0.0662 | 0.8189 ± 0.0591 | +0.0756 |
| specificity | 0.6081 ± 0.0439 | 0.6914 ± 0.0982 | +0.0832 |
| sens_at_95spec | 0.1522 ± 0.0490 | 0.3367 ± 0.1049 | +0.1844 |
| prevalence | 0.4775 ± 0.0000 | 0.4775 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.1241, ΔSens=+0.0756; win iff both > 0)
