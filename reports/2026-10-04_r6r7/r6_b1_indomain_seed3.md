# Bootstrap 95% confidence intervals — `.tmp/ci_gates/indomain`

B = 2000 replicates, seed 3, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | pauc_at_tpr80 |
|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9712, 0.9861] | 0.1804 [0.1726, 0.1870] |
| `x_student` | 5 | 0.9825 [0.9759, 0.9884] | 0.1833 [0.1771, 0.1891] |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9330 [0.9076, 0.9535] | 0.1506 [0.1312, 0.1674] |
| pad_ufes_20 | 0.8189 [0.7828, 0.8521] | 0.0988 [0.0830, 0.1154] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0706, +0.1562] * | +0.0518 [+0.0252, +0.0752] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9437 [0.9221, 0.9623] | 0.1580 [0.1416, 0.1734] |
| pad_ufes_20 | 0.8779 [0.8467, 0.9076] | 0.1232 [0.1066, 0.1403] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0292, +0.1011] * | +0.0348 [+0.0108, +0.0575] * |

