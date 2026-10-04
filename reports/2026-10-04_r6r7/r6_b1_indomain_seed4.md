# Bootstrap 95% confidence intervals — `.tmp/ci_gates/indomain`

B = 2000 replicates, seed 4, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | pauc_at_tpr80 |
|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9708, 0.9865] | 0.1804 [0.1723, 0.1874] |
| `x_student` | 5 | 0.9825 [0.9747, 0.9886] | 0.1833 [0.1761, 0.1892] |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9330 [0.9061, 0.9548] | 0.1506 [0.1288, 0.1681] |
| pad_ufes_20 | 0.8189 [0.7813, 0.8534] | 0.0988 [0.0821, 0.1152] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0729, +0.1567] * | +0.0518 [+0.0252, +0.0758] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9437 [0.9214, 0.9625] | 0.1580 [0.1412, 0.1735] |
| pad_ufes_20 | 0.8779 [0.8444, 0.9082] | 0.1232 [0.1047, 0.1406] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0284, +0.1040] * | +0.0348 [+0.0114, +0.0597] * |

