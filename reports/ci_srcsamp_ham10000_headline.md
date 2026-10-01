# Bootstrap 95% confidence intervals — `/workspace/skin-cancer-detector/.tmp/ci_srcsamp/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.7738 [0.7613, 0.7857] | 0.3779 [0.3551, 0.4016] | 0.0815 [0.0762, 0.0870] | 0.3759 [0.3494, 0.4020] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.7262 [0.7106, 0.7407] | 0.3752 [0.3508, 0.4007] | 0.0512 [0.0461, 0.0567] | 0.3892 [0.3630, 0.4151] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.8267 [0.8153, 0.8375] | 0.4829 [0.4556, 0.5100] | 0.1002 [0.0949, 0.1057] | 0.5004 [0.4720, 0.5254] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.8337 [0.8223, 0.8446] | 0.4969 [0.4687, 0.5255] | 0.1022 [0.0965, 0.1078] | 0.5334 [0.5050, 0.5618] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0529 [+0.0467, +0.0588] * | +0.1050 [+0.0902, +0.1190] * | +0.0187 [+0.0157, +0.0216] * | +0.1246 [+0.1048, +0.1424] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.1076 [+0.0987, +0.1164] * | +0.1217 [+0.1086, +0.1353] * | +0.0509 [+0.0466, +0.0553] * | +0.1442 [+0.1249, +0.1619] * |

## 3. Ablation effect — paired bootstrap (main − ablated)

Pairs each `__<suffix>` fork against the same run without the suffix. The sign is **main − ablated**, so a positive delta means the main configuration wins (e.g. `__train_isic_only` → positive = mixing PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as section 2. `*` marks an interval excluding 0.

| Ablated run | vs main | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | +0.0477 [+0.0376, +0.0580] * | +0.0028 [-0.0113, +0.0162] | +0.0303 [+0.0258, +0.0350] * | -0.0133 [-0.0335, +0.0078] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | -0.0070 [-0.0112, -0.0027] * | -0.0140 [-0.0233, -0.0049] * | -0.0019 [-0.0044, +0.0006] | -0.0330 [-0.0477, -0.0196] * |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | -0.0477 [-0.0580, -0.0376] * | -0.0028 [-0.0162, +0.0113] | -0.0303 [-0.0350, -0.0258] * | +0.0133 [-0.0078, +0.0335] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0070 [+0.0027, +0.0112] * | +0.0140 [+0.0049, +0.0233] * | +0.0019 [-0.0006, +0.0044] | +0.0330 [+0.0196, +0.0477] * |
