# Bootstrap 95% confidence intervals — `reports/external_newsplit_srcsamp_auprc/ham10000/headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.7442 [0.7303, 0.7569] | 0.3882 [0.3634, 0.4127] | 0.0630 [0.0581, 0.0681] | 0.3979 [0.3730, 0.4232] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.8416 [0.8306, 0.8518] | 0.4997 [0.4728, 0.5267] | 0.1073 [0.1020, 0.1126] | 0.5321 [0.5035, 0.5604] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0974 [+0.0900, +0.1049] * | +0.1115 [+0.0985, +0.1257] * | +0.0442 [+0.0405, +0.0478] * | +0.1341 [+0.1152, +0.1518] * |
