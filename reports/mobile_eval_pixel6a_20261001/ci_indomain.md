# Bootstrap 95% confidence intervals — `.tmp/pixel_cmp/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_mobilenetv4_ddi_fold0` | 1 ⚠ | 0.9834 [0.9755, 0.9901] | 0.6182 [0.5576, 0.6800] | 0.1843 [0.1765, 0.1909] | 0.9585 [0.9328, 0.9807] |
| `x_mobilenetv4_srcsamp_auprc_fold4` | 1 ⚠ | 0.9828 [0.9746, 0.9898] | 0.6588 [0.5983, 0.7167] | 0.1837 [0.1757, 0.1905] | 0.9585 [0.9321, 0.9811] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_mobilenetv4_srcsamp_auprc_fold4` | `x_mobilenetv4_ddi_fold0` | -0.0005 [-0.0059, +0.0041] | +0.0406 [+0.0079, +0.0753] * | -0.0006 [-0.0059, +0.0040] | +0.0000 [-0.0217, +0.0217] |

## 4. Fairness gaps — paired bootstrap over `source`

### `x_mobilenetv4_ddi_fold0`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9468 [0.9200, 0.9675] | 0.0673 [0.0344, 0.1220] | 0.1597 [0.1364, 0.1783] | 0.8553 [0.7727, 0.9268] |
| pad_ufes_20 | 0.8190 [0.7774, 0.8601] | 0.7847 [0.7223, 0.8442] | 0.0993 [0.0792, 0.1208] | 0.4286 [0.2827, 0.5845] |
| **isic2024_minus_pad_ufes_20** | +0.1278 [+0.0792, +0.1739] * | -0.7174 [-0.7827, -0.6317] * | +0.0604 [+0.0301, +0.0874] * | +0.4267 [+0.2523, +0.5871] * |

### `x_mobilenetv4_srcsamp_auprc_fold4`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9446 [0.9200, 0.9656] | 0.0541 [0.0327, 0.1008] | 0.1577 [0.1374, 0.1759] | 0.8684 [0.7857, 0.9390] |
| pad_ufes_20 | 0.8751 [0.8395, 0.9080] | 0.8542 [0.8018, 0.8998] | 0.1228 [0.1047, 0.1419] | 0.6138 [0.4593, 0.7564] |
| **isic2024_minus_pad_ufes_20** | +0.0696 [+0.0275, +0.1100] * | -0.8001 [-0.8510, -0.7303] * | +0.0349 [+0.0074, +0.0605] * | +0.2547 [+0.0829, +0.4155] * |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `x_mobilenetv4_srcsamp_auprc_fold4` | `x_mobilenetv4_ddi_fold0` | isic2024 | -0.0021 [-0.0216, +0.0146] | -0.0132 [-0.0435, +0.0161] | -0.0020 [-0.0181, +0.0123] | +0.0132 [-0.0597, +0.0824] |
| `x_mobilenetv4_srcsamp_auprc_fold4` | `x_mobilenetv4_ddi_fold0` | pad_ufes_20 | +0.0561 [+0.0251, +0.0874] * | +0.0695 [+0.0260, +0.1147] * | +0.0235 [+0.0063, +0.0390] * | +0.1852 [+0.0358, +0.3557] * |
