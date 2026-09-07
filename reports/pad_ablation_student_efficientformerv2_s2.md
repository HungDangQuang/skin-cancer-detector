# PAD-mixing ablation — baseline_efficientformerv2_s2

Identical combined held-out test; only TRAIN+VAL differ (with-PAD = ISIC+PAD, no-PAD = ISIC-only).

- with-PAD folds: 5  |  no-PAD folds: 5


## Whole test (ISIC+PAD)

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0803 ± 0.0335 | 0.6283 ± 0.0131 | +0.5480 |
| pauc_at_tpr80 | 0.1499 ± 0.0121 | 0.1812 ± 0.0014 | +0.0313 |
| auc_roc | 0.9276 ± 0.0228 | 0.9804 ± 0.0015 | +0.0528 |
| sensitivity | 0.8639 ± 0.0401 | 0.9178 ± 0.0192 | +0.0539 |
| specificity | 0.8702 ± 0.0157 | 0.9592 ± 0.0151 | +0.0890 |
| sens_at_95spec | 0.6631 ± 0.0916 | 0.9178 ± 0.0080 | +0.2548 |
| prevalence | 0.0039 ± 0.0000 | 0.0039 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.5480, ΔSens=+0.0539; win iff both > 0)

## ISIC-source subset

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0322 ± 0.0211 | 0.0517 ± 0.0114 | +0.0194 |
| pauc_at_tpr80 | 0.1289 ± 0.0220 | 0.1453 ± 0.0061 | +0.0164 |
| auc_roc | 0.8896 ± 0.0523 | 0.9284 ± 0.0056 | +0.0387 |
| sensitivity | 0.8262 ± 0.0545 | 0.8787 ± 0.0471 | +0.0525 |
| specificity | 0.8151 ± 0.1150 | 0.8571 ± 0.0582 | +0.0420 |
| sens_at_95spec | 0.5475 ± 0.1494 | 0.6984 ± 0.0321 | +0.1508 |
| prevalence | 0.0010 ± 0.0000 | 0.0010 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.0194, ΔSens=+0.0525; win iff both > 0)

## PAD-source subset  ← decisive cell

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.6903 ± 0.0166 | 0.8104 ± 0.0160 | +0.1200 |
| pauc_at_tpr80 | 0.0566 ± 0.0045 | 0.1007 ± 0.0079 | +0.0441 |
| auc_roc | 0.7134 ± 0.0131 | 0.8397 ± 0.0111 | +0.1263 |
| sensitivity | 0.6833 ± 0.0618 | 0.7967 ± 0.0215 | +0.1133 |
| specificity | 0.6711 ± 0.0460 | 0.7746 ± 0.0224 | +0.1036 |
| sens_at_95spec | 0.2000 ± 0.0300 | 0.3056 ± 0.1574 | +0.1056 |
| prevalence | 0.4775 ± 0.0000 | 0.4775 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.1200, ΔSens=+0.1133; win iff both > 0)
