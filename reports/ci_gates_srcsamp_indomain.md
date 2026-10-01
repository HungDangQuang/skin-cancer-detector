# Bootstrap 95% confidence intervals — `.tmp/ci_gates/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9713, 0.9863] | 0.6161 [0.5582, 0.6731] | 0.1804 [0.1726, 0.1872] | 0.9517 [0.9304, 0.9711] | 0.9758 [0.9600, 0.9893] |
| `x_student` | 5 | 0.9825 [0.9755, 0.9888] | 0.6609 [0.6034, 0.7145] | 0.1833 [0.1768, 0.1894] | 0.9562 [0.9342, 0.9756] | 0.9789 [0.9644, 0.9916] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `teacher/efficientnetv2_m` | +0.0032 [+0.0001, +0.0063] * | +0.0448 [+0.0262, +0.0633] * | +0.0030 [-0.0001, +0.0061] | +0.0045 [-0.0032, +0.0125] | +0.0030 [-0.0053, +0.0123] |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9330 [0.9073, 0.9528] | 0.0533 [0.0310, 0.0954] | 0.1506 [0.1314, 0.1668] | 0.8368 [0.7735, 0.8950] | 0.9158 [0.8635, 0.9595] |
| pad_ufes_20 | 0.8189 [0.7832, 0.8543] | 0.7966 [0.7453, 0.8444] | 0.0988 [0.0831, 0.1152] | 0.4529 [0.3696, 0.5598] | 0.6751 [0.5822, 0.7542] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0708, +0.1542] * | -0.7433 [-0.7953, -0.6745] * | +0.0518 [+0.0254, +0.0744] * | +0.3839 [+0.2574, +0.4842] * | +0.2407 [+0.1446, +0.3462] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9437 [0.9227, 0.9616] | 0.0673 [0.0394, 0.1165] | 0.1580 [0.1418, 0.1730] | 0.8553 [0.7855, 0.9116] | 0.9289 [0.8771, 0.9694] |
| pad_ufes_20 | 0.8779 [0.8453, 0.9083] | 0.8584 [0.8099, 0.9015] | 0.1232 [0.1055, 0.1403] | 0.6074 [0.5173, 0.7381] | 0.8180 [0.7406, 0.8786] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0282, +0.1011] * | -0.7911 [-0.8421, -0.7232] * | +0.0348 [+0.0114, +0.0571] * | +0.2479 [+0.0913, +0.3495] * | +0.1110 [+0.0289, +0.1982] * |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|---|
| `x_student` | `teacher/efficientnetv2_m` | isic2024 | +0.0107 [+0.0004, +0.0209] * | +0.0140 [-0.0037, +0.0348] | +0.0074 [-0.0025, +0.0171] | +0.0184 [-0.0111, +0.0424] | +0.0132 [-0.0184, +0.0408] |
| `x_student` | `teacher/efficientnetv2_m` | pad_ufes_20 | +0.0590 [+0.0430, +0.0751] * | +0.0619 [+0.0396, +0.0852] * | +0.0244 [+0.0155, +0.0337] * | +0.1545 [+0.0995, +0.2305] * | +0.1429 [+0.0917, +0.2000] * |
