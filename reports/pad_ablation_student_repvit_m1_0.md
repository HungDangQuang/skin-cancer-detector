# PAD-mixing ablation — baseline_repvit_m1_0

Identical combined held-out test; only TRAIN+VAL differ (with-PAD = ISIC+PAD, no-PAD = ISIC-only).

- with-PAD folds: 5  |  no-PAD folds: 5


## Whole test (ISIC+PAD)

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0825 ± 0.0322 | 0.5365 ± 0.0324 | +0.4540 |
| pauc_at_tpr80 | 0.1347 ± 0.0190 | 0.1718 ± 0.0021 | +0.0371 |
| auc_roc | 0.9074 ± 0.0329 | 0.9709 ± 0.0022 | +0.0634 |
| sensitivity | 0.8506 ± 0.0480 | 0.9120 ± 0.0188 | +0.0614 |
| specificity | 0.8431 ± 0.0299 | 0.9388 ± 0.0168 | +0.0957 |
| sens_at_95spec | 0.6058 ± 0.1234 | 0.8905 ± 0.0116 | +0.2846 |
| prevalence | 0.0039 ± 0.0000 | 0.0039 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.4540, ΔSens=+0.0614; win iff both > 0)

## ISIC-source subset

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.0224 ± 0.0068 | 0.0489 ± 0.0144 | +0.0265 |
| pauc_at_tpr80 | 0.1035 ± 0.0101 | 0.1199 ± 0.0059 | +0.0163 |
| auc_roc | 0.8574 ± 0.0189 | 0.8906 ± 0.0086 | +0.0332 |
| sensitivity | 0.7607 ± 0.0471 | 0.8033 ± 0.0232 | +0.0426 |
| specificity | 0.8407 ± 0.0333 | 0.8544 ± 0.0260 | +0.0137 |
| sens_at_95spec | 0.4623 ± 0.0642 | 0.5738 ± 0.0427 | +0.1115 |
| prevalence | 0.0010 ± 0.0000 | 0.0010 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.0265, ΔSens=+0.0426; win iff both > 0)

## PAD-source subset  ← decisive cell

| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |
|---|---|---|---|
| auprc | 0.6409 ± 0.0327 | 0.6812 ± 0.0224 | +0.0404 |
| pauc_at_tpr80 | 0.0487 ± 0.0089 | 0.0764 ± 0.0054 | +0.0277 |
| auc_roc | 0.6776 ± 0.0237 | 0.7420 ± 0.0230 | +0.0644 |
| sensitivity | 0.6567 ± 0.0729 | 0.7367 ± 0.0652 | +0.0800 |
| specificity | 0.6416 ± 0.0764 | 0.6660 ± 0.0681 | +0.0244 |
| sens_at_95spec | 0.1022 ± 0.0609 | 0.1733 ± 0.0636 | +0.0711 |
| prevalence | 0.4775 ± 0.0000 | 0.4775 ± 0.0000 | +0.0000 |

**Verdict:** ✅ PAD HELPS (ΔAUPRC=+0.0404, ΔSens=+0.0800; win iff both > 0)
