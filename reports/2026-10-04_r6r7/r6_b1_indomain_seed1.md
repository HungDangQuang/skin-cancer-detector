# Bootstrap 95% confidence intervals — `.tmp/ci_gates/indomain`

B = 2000 replicates, seed 1, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | pauc_at_tpr80 |
|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9715, 0.9863] | 0.1804 [0.1729, 0.1871] |
| `x_student` | 5 | 0.9825 [0.9757, 0.9885] | 0.1833 [0.1770, 0.1892] |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9330 [0.9073, 0.9544] | 0.1506 [0.1296, 0.1679] |
| pad_ufes_20 | 0.8189 [0.7846, 0.8539] | 0.0988 [0.0838, 0.1156] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0726, +0.1535] * | +0.0518 [+0.0251, +0.0752] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9437 [0.9225, 0.9620] | 0.1580 [0.1416, 0.1732] |
| pad_ufes_20 | 0.8779 [0.8475, 0.9083] | 0.1232 [0.1073, 0.1403] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0284, +0.1010] * | +0.0348 [+0.0109, +0.0570] * |

