# Bootstrap 95% confidence intervals — `.tmp/ci_gates/indomain`

B = 2000 replicates, seed 2, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | pauc_at_tpr80 |
|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9709, 0.9862] | 0.1804 [0.1722, 0.1870] |
| `x_student` | 5 | 0.9825 [0.9754, 0.9884] | 0.1833 [0.1768, 0.1891] |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9330 [0.9073, 0.9543] | 0.1506 [0.1301, 0.1676] |
| pad_ufes_20 | 0.8189 [0.7818, 0.8534] | 0.0988 [0.0821, 0.1144] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0697, +0.1557] * | +0.0518 [+0.0260, +0.0762] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9437 [0.9230, 0.9618] | 0.1580 [0.1424, 0.1728] |
| pad_ufes_20 | 0.8779 [0.8446, 0.9080] | 0.1232 [0.1053, 0.1394] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0286, +0.1034] * | +0.0348 [+0.0118, +0.0584] * |

