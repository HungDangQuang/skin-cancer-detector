# Bootstrap 95% confidence intervals — `.tmp/ci_srcsamp/auprc_indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Predictions file:** `fold_*/predictions_auprc.csv` (not the main `predictions.csv`).

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.9654 [0.9556, 0.9744] | 0.5243 [0.4696, 0.5768] | 0.1685 [0.1597, 0.1770] | 0.9170 [0.8908, 0.9425] | 0.9562 [0.9367, 0.9741] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.9825 [0.9755, 0.9888] | 0.6609 [0.6034, 0.7145] | 0.1833 [0.1768, 0.1894] | 0.9562 [0.9342, 0.9756] | 0.9789 [0.9644, 0.9916] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0171 [+0.0119, +0.0227] * | +0.1367 [+0.1083, +0.1653] * | +0.0149 [+0.0100, +0.0198] * | +0.0392 [+0.0225, +0.0570] * | +0.0226 [+0.0105, +0.0360] * |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0171 [+0.0119, +0.0227] * | +0.1367 [+0.1083, +0.1653] * | +0.0149 [+0.0100, +0.0198] * | +0.0392 [+0.0225, +0.0570] * | +0.0226 [+0.0105, +0.0360] * |

## 4. Fairness gaps — paired bootstrap over `source`

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9107 [0.8801, 0.9357] | 0.0391 [0.0248, 0.0715] | 0.1346 [0.1128, 0.1544] | 0.7711 [0.6974, 0.8445] | 0.8711 [0.8074, 0.9238] |
| pad_ufes_20 | 0.8781 [0.8486, 0.9054] | 0.8592 [0.8147, 0.8985] | 0.1244 [0.1088, 0.1395] | 0.6317 [0.5528, 0.7155] | 0.8042 [0.7244, 0.8694] |
| **isic2024_minus_pad_ufes_20** | +0.0325 [-0.0090, +0.0707] | -0.8202 [-0.8605, -0.7656] * | +0.0102 [-0.0162, +0.0359] | +0.1393 [+0.0233, +0.2414] * | +0.0668 [-0.0258, +0.1622] |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

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
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | isic2024 | +0.0331 [+0.0192, +0.0479] * | +0.0282 [+0.0039, +0.0598] * | +0.0234 [+0.0120, +0.0340] * | +0.0842 [+0.0347, +0.1304] * | +0.0579 [+0.0152, +0.1000] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | pad_ufes_20 | -0.0002 [-0.0136, +0.0134] | -0.0008 [-0.0199, +0.0187] | -0.0012 [-0.0099, +0.0070] | -0.0243 [-0.0836, +0.0642] | +0.0138 [-0.0295, +0.0608] |
