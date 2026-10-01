# Bootstrap 95% confidence intervals — `reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/crop70`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6669 [0.6538, 0.6807] | 0.6646 [0.6467, 0.6850] | 0.0415 [0.0383, 0.0449] | 0.2756 [0.2503, 0.2978] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.7146 [0.7014, 0.7285] | 0.7087 [0.6904, 0.7277] | 0.0551 [0.0508, 0.0596] | 0.3454 [0.3203, 0.3731] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0477 [+0.0415, +0.0539] * | +0.0440 [+0.0351, +0.0528] * | +0.0136 [+0.0108, +0.0162] * | +0.0698 [+0.0553, +0.0918] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6731 [0.6319, 0.7114] | 0.6892 [0.6349, 0.7441] | 0.0387 [0.0297, 0.0504] | 0.2952 [0.2284, 0.3687] |
| light | 0.6788 [0.6600, 0.6981] | 0.6899 [0.6634, 0.7181] | 0.0445 [0.0399, 0.0497] | 0.2882 [0.2537, 0.3248] |
| medium | 0.6476 [0.6270, 0.6708] | 0.6227 [0.5906, 0.6581] | 0.0388 [0.0342, 0.0439] | 0.2460 [0.2117, 0.2844] |
| **dark_minus_light** | -0.0056 [-0.0500, +0.0372] | -0.0008 [-0.0598, +0.0626] | -0.0058 [-0.0159, +0.0066] | +0.0070 [-0.0724, +0.0867] |
| **dark_minus_medium** | +0.0255 [-0.0211, +0.0710] | +0.0665 [+0.0012, +0.1300] * | -0.0001 [-0.0107, +0.0125] | +0.0492 [-0.0310, +0.1298] |
| **light_minus_medium** | +0.0312 [+0.0033, +0.0603] * | +0.0673 [+0.0251, +0.1091] * | +0.0057 [-0.0010, +0.0126] | +0.0422 [-0.0070, +0.0921] |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7403 [0.6949, 0.7815] | 0.7545 [0.6999, 0.8060] | 0.0629 [0.0501, 0.0779] | 0.4019 [0.3228, 0.4928] |
| light | 0.7244 [0.7059, 0.7437] | 0.7318 [0.7074, 0.7577] | 0.0564 [0.0505, 0.0629] | 0.3592 [0.3226, 0.3972] |
| medium | 0.6935 [0.6706, 0.7172] | 0.6648 [0.6331, 0.7011] | 0.0520 [0.0454, 0.0590] | 0.3070 [0.2689, 0.3557] |
| **dark_minus_light** | +0.0159 [-0.0309, +0.0618] | +0.0228 [-0.0375, +0.0794] | +0.0065 [-0.0079, +0.0223] | +0.0428 [-0.0424, +0.1422] |
| **dark_minus_medium** | +0.0468 [-0.0033, +0.0949] | +0.0898 [+0.0249, +0.1508] * | +0.0109 [-0.0037, +0.0275] | +0.0949 [+0.0032, +0.1935] * |
| **light_minus_medium** | +0.0308 [+0.0028, +0.0619] * | +0.0670 [+0.0251, +0.1092] * | +0.0044 [-0.0043, +0.0136] | +0.0522 [-0.0116, +0.1052] |

