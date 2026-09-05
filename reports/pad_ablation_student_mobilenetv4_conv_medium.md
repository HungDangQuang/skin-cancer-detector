# PAD-mixing ablation — baseline_mobilenetv4_conv_medium

Identical combined held-out test; only TRAIN+VAL differ (with-PAD = ISIC+PAD, no-PAD = ISIC-only).

- with-PAD folds: 5  |  no-PAD folds: 5


## Whole test (ISIC+PAD)

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.1014 ± 0.0360 | 0.6101 ± 0.0426 | +0.5087 |
| pauc_at_tpr80 | 0.1558 ± 0.0067 | 0.1798 ± 0.0047 | +0.0240 |
| auc_roc | 0.9383 ± 0.0119 | 0.9790 ± 0.0048 | +0.0407 |
| sensitivity | 0.8739 ± 0.0327 | 0.9203 ± 0.0080 | +0.0465 |
| specificity | 0.8808 ± 0.0232 | 0.9508 ± 0.0047 | +0.0699 |
| sens_at_95spec | 0.7071 ± 0.0863 | 0.9162 ± 0.0132 | +0.2091 |
| prevalence | 0.0039 ± 0.0000 | 0.0039 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.5087, ΔSens=+0.0465; win iff both > 0)

## ISIC-source subset

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0370 ± 0.0151 | 0.0541 ± 0.0166 | +0.0171 |
| pauc_at_tpr80 | 0.1366 ± 0.0067 | 0.1409 ± 0.0145 | +0.0043 |
| auc_roc | 0.9080 ± 0.0088 | 0.9233 ± 0.0185 | +0.0152 |
| sensitivity | 0.8852 ± 0.0232 | 0.8623 ± 0.0482 | -0.0230 |
| specificity | 0.8010 ± 0.0355 | 0.8725 ± 0.0240 | +0.0715 |
| sens_at_95spec | 0.5934 ± 0.0300 | 0.6852 ± 0.0407 | +0.0918 |
| prevalence | 0.0010 ± 0.0000 | 0.0010 ± 0.0000 | +0.0000 |

**Verdict:** ❌ no clear win (ΔAUPRC=+0.0171, ΔSens=-0.0230; win iff both > 0)

## PAD-source subset  ← decisive cell

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.6501 ± 0.0384 | 0.7633 ± 0.0513 | +0.1132 |
| pauc_at_tpr80 | 0.0555 ± 0.0067 | 0.0843 ± 0.0084 | +0.0288 |
| auc_roc | 0.6920 ± 0.0226 | 0.7947 ± 0.0350 | +0.1028 |
| sensitivity | 0.6711 ± 0.0935 | 0.7800 ± 0.0411 | +0.1089 |
| specificity | 0.6609 ± 0.0963 | 0.7157 ± 0.0703 | +0.0548 |
| sens_at_95spec | 0.1333 ± 0.0542 | 0.2911 ± 0.0926 | +0.1578 |
| prevalence | 0.4775 ± 0.0000 | 0.4775 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.1132, ΔSens=+0.1089; win iff both > 0)
