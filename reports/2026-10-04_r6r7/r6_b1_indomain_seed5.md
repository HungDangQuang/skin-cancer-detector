# Bootstrap 95% confidence intervals — `.tmp/ci_gates/indomain`

B = 2000 replicates, seed 5, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | pauc_at_tpr80 |
|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9710, 0.9860] | 0.1804 [0.1722, 0.1869] |
| `x_student` | 5 | 0.9825 [0.9753, 0.9882] | 0.1833 [0.1765, 0.1889] |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9330 [0.9078, 0.9545] | 0.1506 [0.1307, 0.1682] |
| pad_ufes_20 | 0.8189 [0.7850, 0.8544] | 0.0988 [0.0836, 0.1155] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0715, +0.1523] * | +0.0518 [+0.0257, +0.0745] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | pauc_at_tpr80 |
|---|---|---|
| isic2024 | 0.9437 [0.9223, 0.9617] | 0.1580 [0.1419, 0.1728] |
| pad_ufes_20 | 0.8779 [0.8480, 0.9082] | 0.1232 [0.1072, 0.1399] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0285, +0.1006] * | +0.0348 [+0.0111, +0.0563] * |

