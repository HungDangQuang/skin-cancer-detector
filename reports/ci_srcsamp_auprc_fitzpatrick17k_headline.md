# Bootstrap 95% confidence intervals — `reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6651 [0.6518, 0.6785] | 0.6627 [0.6441, 0.6832] | 0.0415 [0.0383, 0.0451] | 0.2783 [0.2522, 0.3003] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.7077 [0.6941, 0.7220] | 0.7022 [0.6843, 0.7213] | 0.0538 [0.0499, 0.0580] | 0.3415 [0.3162, 0.3661] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0425 [+0.0361, +0.0491] * | +0.0395 [+0.0310, +0.0478] * | +0.0123 [+0.0096, +0.0147] * | +0.0631 [+0.0478, +0.0806] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6688 [0.6287, 0.7074] | 0.6729 [0.6154, 0.7309] | 0.0408 [0.0316, 0.0521] | 0.2760 [0.2226, 0.3435] |
| light | 0.6769 [0.6583, 0.6967] | 0.6899 [0.6635, 0.7166] | 0.0430 [0.0386, 0.0481] | 0.2982 [0.2661, 0.3307] |
| medium | 0.6467 [0.6246, 0.6683] | 0.6184 [0.5865, 0.6535] | 0.0405 [0.0355, 0.0458] | 0.2380 [0.2059, 0.2813] |
| **dark_minus_light** | -0.0081 [-0.0517, +0.0330] | -0.0170 [-0.0813, +0.0487] | -0.0022 [-0.0128, +0.0105] | -0.0223 [-0.0836, +0.0527] |
| **dark_minus_medium** | +0.0221 [-0.0237, +0.0671] | +0.0545 [-0.0122, +0.1226] | +0.0003 [-0.0105, +0.0131] | +0.0379 [-0.0304, +0.1146] |
| **light_minus_medium** | +0.0302 [+0.0035, +0.0581] * | +0.0715 [+0.0288, +0.1138] * | +0.0025 [-0.0043, +0.0095] | +0.0602 [+0.0094, +0.1042] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7242 [0.6796, 0.7654] | 0.7355 [0.6804, 0.7894] | 0.0601 [0.0484, 0.0743] | 0.3462 [0.2815, 0.4319] |
| light | 0.7222 [0.7036, 0.7413] | 0.7319 [0.7071, 0.7564] | 0.0551 [0.0495, 0.0610] | 0.3654 [0.3292, 0.4042] |
| medium | 0.6813 [0.6582, 0.7037] | 0.6494 [0.6165, 0.6844] | 0.0511 [0.0451, 0.0574] | 0.2951 [0.2554, 0.3376] |
| **dark_minus_light** | +0.0019 [-0.0450, +0.0464] | +0.0036 [-0.0577, +0.0624] | +0.0050 [-0.0077, +0.0203] | -0.0192 [-0.0974, +0.0775] |
| **dark_minus_medium** | +0.0428 [-0.0068, +0.0885] | +0.0861 [+0.0206, +0.1496] * | +0.0090 [-0.0046, +0.0243] | +0.0510 [-0.0269, +0.1480] |
| **light_minus_medium** | +0.0409 [+0.0119, +0.0708] * | +0.0825 [+0.0402, +0.1230] * | +0.0041 [-0.0043, +0.0129] | +0.0702 [+0.0170, +0.1269] * |

