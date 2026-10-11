# Bootstrap 95% confidence intervals — `.tmp/ci_p3p0/fitzpatrick17k_headline`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_p0` | 5 | 0.7077 [0.6941, 0.7220] | 0.7022 [0.6843, 0.7213] | 0.0538 [0.0499, 0.0580] | 0.3415 [0.3162, 0.3661] | 0.4946 [0.4699, 0.5178] |
| `x_p3` | 5 | 0.7209 [0.7073, 0.7350] | 0.7205 [0.7026, 0.7393] | 0.0576 [0.0532, 0.0622] | 0.3444 [0.3163, 0.3694] | 0.5114 [0.4853, 0.5355] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_p3` | `x_p0` | +0.0132 [+0.0087, +0.0176] * | +0.0183 [+0.0119, +0.0244] * | +0.0038 [+0.0020, +0.0056] * | +0.0029 [-0.0112, +0.0153] | +0.0168 [+0.0042, +0.0292] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `x_p0`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| dark | 0.7242 [0.6796, 0.7654] | 0.7355 [0.6804, 0.7894] | 0.0601 [0.0484, 0.0743] | 0.3462 [0.2815, 0.4319] | 0.5000 [0.4248, 0.5837] |
| light | 0.7222 [0.7036, 0.7413] | 0.7319 [0.7071, 0.7564] | 0.0551 [0.0495, 0.0610] | 0.3654 [0.3292, 0.4042] | 0.5207 [0.4886, 0.5554] |
| medium | 0.6813 [0.6582, 0.7037] | 0.6494 [0.6165, 0.6844] | 0.0511 [0.0451, 0.0574] | 0.2951 [0.2554, 0.3376] | 0.4473 [0.4077, 0.4861] |
| **dark_minus_light** | +0.0019 [-0.0450, +0.0464] | +0.0036 [-0.0577, +0.0624] | +0.0050 [-0.0077, +0.0203] | -0.0192 [-0.0974, +0.0775] | -0.0207 [-0.1034, +0.0683] |
| **dark_minus_medium** | +0.0428 [-0.0068, +0.0885] | +0.0861 [+0.0206, +0.1496] * | +0.0090 [-0.0046, +0.0243] | +0.0510 [-0.0269, +0.1480] | +0.0527 [-0.0318, +0.1465] |
| **light_minus_medium** | +0.0409 [+0.0119, +0.0708] * | +0.0825 [+0.0402, +0.1230] * | +0.0041 [-0.0043, +0.0129] | +0.0702 [+0.0170, +0.1269] * | +0.0734 [+0.0247, +0.1258] * |

### `x_p3`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| dark | 0.7349 [0.6898, 0.7764] | 0.7388 [0.6823, 0.7948] | 0.0640 [0.0509, 0.0791] | 0.3625 [0.2906, 0.4457] | 0.5221 [0.4378, 0.6018] |
| light | 0.7339 [0.7149, 0.7533] | 0.7504 [0.7254, 0.7746] | 0.0584 [0.0522, 0.0648] | 0.3828 [0.3434, 0.4190] | 0.5404 [0.5069, 0.5749] |
| medium | 0.6979 [0.6743, 0.7210] | 0.6665 [0.6315, 0.7024] | 0.0558 [0.0496, 0.0630] | 0.2851 [0.2458, 0.3326] | 0.4589 [0.4126, 0.5025] |
| **dark_minus_light** | +0.0010 [-0.0470, +0.0451] | -0.0116 [-0.0750, +0.0496] | +0.0057 [-0.0088, +0.0212] | -0.0203 [-0.0995, +0.0692] | -0.0183 [-0.1099, +0.0671] |
| **dark_minus_medium** | +0.0371 [-0.0140, +0.0848] | +0.0723 [+0.0058, +0.1397] * | +0.0082 [-0.0067, +0.0244] | +0.0774 [-0.0091, +0.1727] | +0.0632 [-0.0319, +0.1590] |
| **light_minus_medium** | +0.0360 [+0.0064, +0.0668] * | +0.0839 [+0.0396, +0.1271] * | +0.0025 [-0.0066, +0.0120] | +0.0977 [+0.0378, +0.1501] * | +0.0815 [+0.0273, +0.1389] * |


## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|---|
| `x_p3` | `x_p0` | dark | +0.0108 [-0.0061, +0.0273] | +0.0033 [-0.0177, +0.0251] | +0.0039 [-0.0025, +0.0098] | +0.0163 [-0.0369, +0.0704] | +0.0221 [-0.0330, +0.0696] |
| `x_p3` | `x_p0` | light | +0.0117 [+0.0057, +0.0177] * | +0.0185 [+0.0103, +0.0258] * | +0.0032 [+0.0008, +0.0058] * | +0.0174 [-0.0042, +0.0335] | +0.0197 [+0.0012, +0.0346] * |
| `x_p3` | `x_p0` | medium | +0.0165 [+0.0088, +0.0248] * | +0.0171 [+0.0063, +0.0276] * | +0.0048 [+0.0017, +0.0079] * | -0.0100 [-0.0310, +0.0130] | +0.0116 [-0.0132, +0.0344] |
