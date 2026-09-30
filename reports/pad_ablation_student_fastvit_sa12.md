# PAD-mixing ablation — baseline_fastvit_sa12

Identical combined held-out test; only TRAIN+VAL differ (with-PAD = ISIC+PAD, no-PAD = ISIC-only).

- with-PAD folds: 5  |  no-PAD folds: 5


## Whole test (ISIC+PAD)

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.1075 ± 0.0267 | 0.6082 ± 0.0373 | +0.5007 |
| pauc_at_tpr80 | 0.1589 ± 0.0054 | 0.1825 ± 0.0028 | +0.0236 |
| auc_roc | 0.9448 ± 0.0090 | 0.9817 ± 0.0029 | +0.0369 |
| sensitivity | 0.8805 ± 0.0206 | 0.9228 ± 0.0107 | +0.0423 |
| specificity | 0.8945 ± 0.0139 | 0.9597 ± 0.0121 | +0.0653 |
| sens_at_95spec | 0.7344 ± 0.0493 | 0.9228 ± 0.0100 | +0.1884 |
| prevalence | 0.0039 ± 0.0000 | 0.0039 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.5007, ΔSens=+0.0423; win iff both > 0)

## ISIC-source subset

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0240 ± 0.0047 | 0.0448 ± 0.0063 | +0.0208 |
| pauc_at_tpr80 | 0.1378 ± 0.0095 | 0.1487 ± 0.0103 | +0.0109 |
| auc_roc | 0.9147 ± 0.0135 | 0.9337 ± 0.0116 | +0.0190 |
| sensitivity | 0.8590 ± 0.0321 | 0.8984 ± 0.0407 | +0.0393 |
| specificity | 0.8363 ± 0.0281 | 0.8531 ± 0.0216 | +0.0168 |
| sens_at_95spec | 0.6197 ± 0.0432 | 0.7148 ± 0.0353 | +0.0951 |
| prevalence | 0.0010 ± 0.0000 | 0.0010 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.0208, ΔSens=+0.0393; win iff both > 0)

## PAD-source subset  ← decisive cell

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.6694 ± 0.0133 | 0.7739 ± 0.0360 | +0.1045 |
| pauc_at_tpr80 | 0.0546 ± 0.0014 | 0.0873 ± 0.0081 | +0.0327 |
| auc_roc | 0.7004 ± 0.0071 | 0.8022 ± 0.0269 | +0.1019 |
| sensitivity | 0.6422 ± 0.0781 | 0.7533 ± 0.0692 | +0.1111 |
| specificity | 0.6802 ± 0.0758 | 0.7350 ± 0.0482 | +0.0548 |
| sens_at_95spec | 0.1822 ± 0.0151 | 0.2833 ± 0.0685 | +0.1011 |
| prevalence | 0.4775 ± 0.0000 | 0.4775 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.1045, ΔSens=+0.1111; win iff both > 0)
