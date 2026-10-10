# Bootstrap 95% confidence intervals — `.tmp/ci_gates/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | pauc_at_tpr80 |
|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9713, 0.9863] | 0.1804 [0.1726, 0.1872] |
| `x_student` | 5 | 0.9825 [0.9755, 0.9888] | 0.1833 [0.1768, 0.1894] |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9330 [0.9073, 0.9528] | 0.1506 [0.1314, 0.1668] |
| pad_ufes_20 | 0.8189 [0.7832, 0.8543] | 0.0988 [0.0831, 0.1152] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0708, +0.1542] * | +0.0518 [+0.0254, +0.0744] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9437 [0.9227, 0.9616] | 0.1580 [0.1418, 0.1730] |
| pad_ufes_20 | 0.8779 [0.8453, 0.9083] | 0.1232 [0.1055, 0.1403] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0282, +0.1011] * | +0.0348 [+0.0114, +0.0571] * |

