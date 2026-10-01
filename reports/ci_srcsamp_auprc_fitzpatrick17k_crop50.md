# Bootstrap 95% confidence intervals — `reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/crop50`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6683 [0.6547, 0.6822] | 0.6634 [0.6449, 0.6833] | 0.0438 [0.0403, 0.0474] | 0.2631 [0.2421, 0.2894] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.7051 [0.6910, 0.7191] | 0.7032 [0.6849, 0.7227] | 0.0523 [0.0481, 0.0569] | 0.3291 [0.3033, 0.3545] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0368 [+0.0306, +0.0428] * | +0.0399 [+0.0319, +0.0475] * | +0.0085 [+0.0057, +0.0114] * | +0.0660 [+0.0489, +0.0812] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6637 [0.6219, 0.7041] | 0.6843 [0.6304, 0.7409] | 0.0371 [0.0285, 0.0484] | 0.2942 [0.2290, 0.3771] |
| light | 0.6823 [0.6634, 0.7014] | 0.6884 [0.6623, 0.7161] | 0.0485 [0.0434, 0.0541] | 0.2741 [0.2453, 0.3095] |
| medium | 0.6487 [0.6274, 0.6709] | 0.6240 [0.5914, 0.6585] | 0.0393 [0.0348, 0.0445] | 0.2433 [0.2058, 0.2828] |
| **dark_minus_light** | -0.0186 [-0.0644, +0.0273] | -0.0041 [-0.0660, +0.0594] | -0.0114 [-0.0218, +0.0008] | +0.0201 [-0.0541, +0.1112] |
| **dark_minus_medium** | +0.0149 [-0.0325, +0.0619] | +0.0603 [-0.0069, +0.1245] | -0.0022 [-0.0120, +0.0101] | +0.0509 [-0.0282, +0.1449] |
| **light_minus_medium** | +0.0336 [+0.0059, +0.0630] * | +0.0644 [+0.0228, +0.1064] * | +0.0093 [+0.0024, +0.0165] * | +0.0308 [-0.0176, +0.0836] |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7297 [0.6856, 0.7726] | 0.7428 [0.6861, 0.7982] | 0.0590 [0.0458, 0.0743] | 0.3913 [0.3171, 0.4810] |
| light | 0.7146 [0.6957, 0.7336] | 0.7245 [0.6989, 0.7509] | 0.0545 [0.0487, 0.0612] | 0.3364 [0.3041, 0.3742] |
| medium | 0.6863 [0.6616, 0.7100] | 0.6655 [0.6322, 0.7004] | 0.0479 [0.0412, 0.0549] | 0.3057 [0.2667, 0.3451] |
| **dark_minus_light** | +0.0151 [-0.0324, +0.0649] | +0.0183 [-0.0421, +0.0800] | +0.0045 [-0.0096, +0.0206] | +0.0549 [-0.0295, +0.1473] |
| **dark_minus_medium** | +0.0434 [-0.0075, +0.0926] | +0.0773 [+0.0115, +0.1409] * | +0.0111 [-0.0039, +0.0280] | +0.0857 [-0.0007, +0.1809] |
| **light_minus_medium** | +0.0283 [-0.0001, +0.0589] | +0.0590 [+0.0175, +0.1023] * | +0.0066 [-0.0024, +0.0157] | +0.0307 [-0.0181, +0.0860] |

