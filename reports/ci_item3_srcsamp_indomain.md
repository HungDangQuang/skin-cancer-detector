# Bootstrap 95% confidence intervals — `.tmp/ci_item3/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `p0_ckpt_auprc` | 5 | 0.9825 [0.9755, 0.9888] | 0.6609 [0.6034, 0.7145] | 0.1833 [0.1768, 0.1894] | 0.9562 [0.9342, 0.9756] | 0.9789 [0.9644, 0.9916] |
| `p0_ckpt_pauc` | 5 | 0.9815 [0.9739, 0.9879] | 0.6575 [0.6005, 0.7110] | 0.1824 [0.1751, 0.1887] | 0.9487 [0.9242, 0.9690] | 0.9796 [0.9651, 0.9916] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `p0_ckpt_auprc` | `p0_ckpt_pauc` | +0.0010 [-0.0002, +0.0024] | +0.0034 [-0.0039, +0.0106] | +0.0009 [-0.0003, +0.0024] | +0.0075 [+0.0022, +0.0148] * | -0.0008 [-0.0042, +0.0024] |

## 4. Fairness gaps — paired bootstrap over `source`

### `p0_ckpt_auprc`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9437 [0.9227, 0.9616] | 0.0673 [0.0394, 0.1165] | 0.1580 [0.1418, 0.1730] | 0.8553 [0.7855, 0.9116] | 0.9289 [0.8771, 0.9694] |
| pad_ufes_20 | 0.8779 [0.8453, 0.9083] | 0.8584 [0.8099, 0.9015] | 0.1232 [0.1055, 0.1403] | 0.6074 [0.5173, 0.7381] | 0.8180 [0.7406, 0.8786] |
| **isic2024_minus_pad_ufes_20** | +0.0658 [+0.0282, +0.1011] * | -0.7911 [-0.8421, -0.7232] * | +0.0348 [+0.0114, +0.0571] * | +0.2479 [+0.0913, +0.3495] * | +0.1110 [+0.0289, +0.1982] * |

### `p0_ckpt_pauc`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9404 [0.9171, 0.9593] | 0.0674 [0.0393, 0.1168] | 0.1556 [0.1382, 0.1712] | 0.8237 [0.7493, 0.8872] | 0.9289 [0.8790, 0.9694] |
| pad_ufes_20 | 0.8732 [0.8404, 0.9032] | 0.8561 [0.8095, 0.8976] | 0.1208 [0.1030, 0.1374] | 0.5968 [0.5078, 0.7223] | 0.8000 [0.7177, 0.8656] |
| **isic2024_minus_pad_ufes_20** | +0.0672 [+0.0288, +0.1028] * | -0.7887 [-0.8387, -0.7216] * | +0.0348 [+0.0111, +0.0579] * | +0.2269 [+0.0815, +0.3276] * | +0.1289 [+0.0445, +0.2192] * |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|---|
| `p0_ckpt_auprc` | `p0_ckpt_pauc` | isic2024 | +0.0033 [-0.0010, +0.0081] | -0.0001 [-0.0082, +0.0076] | +0.0024 [-0.0013, +0.0065] | +0.0316 [+0.0056, +0.0585] * | +0.0000 [-0.0135, +0.0103] |
| `p0_ckpt_auprc` | `p0_ckpt_pauc` | pad_ufes_20 | +0.0047 [-0.0010, +0.0105] | +0.0023 [-0.0062, +0.0106] | +0.0024 [-0.0009, +0.0057] | +0.0106 [-0.0272, +0.0471] | +0.0180 [-0.0086, +0.0444] |
