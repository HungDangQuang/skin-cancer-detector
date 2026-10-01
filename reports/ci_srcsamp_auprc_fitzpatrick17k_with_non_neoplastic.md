# Bootstrap 95% confidence intervals — `reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/with_non_neoplastic`

B = 2000 replicates, seed 42, 16012 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6583 [0.6476, 0.6704] | 0.2719 [0.2565, 0.2891] | 0.0357 [0.0331, 0.0387] | 0.2972 [0.2806, 0.3140] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6976 [0.6861, 0.7097] | 0.3062 [0.2899, 0.3246] | 0.0459 [0.0426, 0.0496] | 0.3456 [0.3281, 0.3633] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0393 [+0.0343, +0.0442] * | +0.0343 [+0.0271, +0.0416] * | +0.0101 [+0.0080, +0.0123] * | +0.0483 [+0.0381, +0.0585] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6476 [0.6159, 0.6790] | 0.1799 [0.1513, 0.2198] | 0.0377 [0.0297, 0.0476] | 0.2462 [0.2049, 0.2929] |
| light | 0.6771 [0.6618, 0.6922] | 0.3306 [0.3083, 0.3556] | 0.0372 [0.0336, 0.0415] | 0.3337 [0.3104, 0.3576] |
| medium | 0.6358 [0.6177, 0.6540] | 0.2265 [0.2050, 0.2513] | 0.0350 [0.0312, 0.0393] | 0.2613 [0.2344, 0.2871] |
| **dark_minus_light** | -0.0295 [-0.0647, +0.0059] | -0.1507 [-0.1897, -0.1058] * | +0.0004 [-0.0082, +0.0113] | -0.0876 [-0.1366, -0.0384] * |
| **dark_minus_medium** | +0.0118 [-0.0242, +0.0494] | -0.0466 [-0.0846, +0.0006] | +0.0027 [-0.0065, +0.0132] | -0.0151 [-0.0627, +0.0398] |
| **light_minus_medium** | +0.0413 [+0.0172, +0.0661] * | +0.1041 [+0.0702, +0.1384] * | +0.0022 [-0.0036, +0.0083] | +0.0724 [+0.0371, +0.1106] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7116 [0.6779, 0.7444] | 0.2257 [0.1868, 0.2741] | 0.0567 [0.0476, 0.0680] | 0.3202 [0.2602, 0.3728] |
| light | 0.7087 [0.6936, 0.7244] | 0.3558 [0.3327, 0.3814] | 0.0462 [0.0419, 0.0511] | 0.3724 [0.3460, 0.3979] |
| medium | 0.6757 [0.6564, 0.6956] | 0.2605 [0.2364, 0.2892] | 0.0441 [0.0393, 0.0496] | 0.3073 [0.2787, 0.3371] |
| **dark_minus_light** | +0.0029 [-0.0340, +0.0398] | -0.1301 [-0.1757, -0.0789] * | +0.0105 [-0.0000, +0.0225] | -0.0522 [-0.1177, +0.0076] |
| **dark_minus_medium** | +0.0360 [-0.0022, +0.0749] | -0.0348 [-0.0809, +0.0172] | +0.0126 [+0.0019, +0.0250] * | +0.0129 [-0.0509, +0.0729] |
| **light_minus_medium** | +0.0331 [+0.0085, +0.0576] * | +0.0953 [+0.0597, +0.1304] * | +0.0021 [-0.0048, +0.0091] | +0.0651 [+0.0246, +0.1046] * |

