# Bootstrap 95% confidence intervals — `/workspace/skin-cancer-detector/.tmp/ci_srcsamp/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.9744 [0.9653, 0.9825] | 0.6029 [0.5471, 0.6582] | 0.1755 [0.1669, 0.1833] | 0.9434 [0.9192, 0.9638] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.9695 [0.9592, 0.9784] | 0.4702 [0.4175, 0.5228] | 0.1730 [0.1635, 0.1812] | 0.9283 [0.9023, 0.9522] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.9816 [0.9746, 0.9879] | 0.6246 [0.5646, 0.6825] | 0.1826 [0.1760, 0.1886] | 0.9525 [0.9307, 0.9720] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.9815 [0.9739, 0.9879] | 0.6575 [0.6005, 0.7110] | 0.1824 [0.1751, 0.1887] | 0.9487 [0.9242, 0.9690] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0072 [+0.0030, +0.0117] * | +0.0217 [+0.0036, +0.0407] * | +0.0071 [+0.0028, +0.0115] * | +0.0091 [-0.0025, +0.0230] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0120 [+0.0076, +0.0169] * | +0.1873 [+0.1568, +0.2189] * | +0.0094 [+0.0053, +0.0138] * | +0.0204 [+0.0039, +0.0370] * |

## 3. Ablation effect — paired bootstrap (main − ablated)

Pairs each `__<suffix>` fork against the same run without the suffix. The sign is **main − ablated**, so a positive delta means the main configuration wins (e.g. `__train_isic_only` → positive = mixing PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as section 2. `*` marks an interval excluding 0.

| Ablated run | vs main | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | +0.0049 [-0.0003, +0.0100] | +0.1327 [+0.0973, +0.1699] * | +0.0025 [-0.0026, +0.0073] | +0.0151 [+0.0000, +0.0308] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0001 [-0.0013, +0.0015] | -0.0329 [-0.0470, -0.0178] * | +0.0001 [-0.0012, +0.0016] | +0.0038 [-0.0038, +0.0131] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | -0.0049 [-0.0100, +0.0003] | -0.1327 [-0.1699, -0.0973] * | -0.0025 [-0.0073, +0.0026] | -0.0151 [-0.0308, +0.0000] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | -0.0001 [-0.0015, +0.0013] | +0.0329 [+0.0178, +0.0470] * | -0.0001 [-0.0016, +0.0012] | -0.0038 [-0.0131, +0.0038] |

## 4. Fairness gaps — paired bootstrap over `source`

### `baseline_mobilenetv4_conv_medium`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9161 [0.8870, 0.9385] | 0.0652 [0.0359, 0.1140] | 0.1367 [0.1165, 0.1548] | 0.8053 [0.7375, 0.8656] |
| pad_ufes_20 | 0.7945 [0.7583, 0.8283] | 0.7800 [0.7305, 0.8274] | 0.0834 [0.0672, 0.1002] | 0.4614 [0.3938, 0.5513] |
| **isic2024_minus_pad_ufes_20** | +0.1216 [+0.0782, +0.1641] * | -0.7147 [-0.7672, -0.6486] * | +0.0533 [+0.0274, +0.0771] * | +0.3439 [+0.2315, +0.4272] * |

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9199 [0.8871, 0.9449] | 0.0351 [0.0236, 0.0596] | 0.1390 [0.1145, 0.1602] | 0.7974 [0.7253, 0.8622] |
| pad_ufes_20 | 0.8892 [0.8595, 0.9160] | 0.8674 [0.8229, 0.9067] | 0.1313 [0.1157, 0.1459] | 0.6455 [0.5550, 0.7570] |
| **isic2024_minus_pad_ufes_20** | +0.0307 [-0.0123, +0.0693] | -0.8322 [-0.8712, -0.7796] * | +0.0076 [-0.0210, +0.0339] | +0.1519 [+0.0167, +0.2603] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9418 [0.9200, 0.9593] | 0.0716 [0.0375, 0.1264] | 0.1570 [0.1405, 0.1713] | 0.8447 [0.7769, 0.9029] |
| pad_ufes_20 | 0.8245 [0.7875, 0.8596] | 0.7997 [0.7458, 0.8499] | 0.0993 [0.0816, 0.1166] | 0.4963 [0.4022, 0.5818] |
| **isic2024_minus_pad_ufes_20** | +0.1173 [+0.0751, +0.1577] * | -0.7281 [-0.7906, -0.6529] * | +0.0577 [+0.0332, +0.0805] * | +0.3484 [+0.2397, +0.4590] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9404 [0.9171, 0.9593] | 0.0674 [0.0393, 0.1168] | 0.1556 [0.1382, 0.1712] | 0.8237 [0.7493, 0.8872] |
| pad_ufes_20 | 0.8732 [0.8404, 0.9032] | 0.8561 [0.8095, 0.8976] | 0.1208 [0.1030, 0.1374] | 0.5968 [0.5078, 0.7223] |
| **isic2024_minus_pad_ufes_20** | +0.0672 [+0.0288, +0.1028] * | -0.7887 [-0.8387, -0.7216] * | +0.0348 [+0.0111, +0.0579] * | +0.2269 [+0.0815, +0.3276] * |


## 5. Ablation effect **within each `source`** — paired (main − ablated)

Section 3 gives the ablation delta on the whole test set. For the PAD-mixing arms that is the wrong cell — the ISIC-only arm collapses on the PAD rows, and those rows carry ~75% of all positives, so the whole-test delta is inflated. **Quote this table instead.** Still paired: every run draws the same rows for a given group, so the replicate vectors difference directly. `*` marks an interval excluding 0.

| Ablated run | vs main | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | isic2024 | -0.0039 [-0.0198, +0.0116] | +0.0301 [+0.0052, +0.0638] * | -0.0023 [-0.0158, +0.0108] | +0.0079 [-0.0313, +0.0500] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | pad_ufes_20 | -0.0948 [-0.1199, -0.0700] * | -0.0874 [-0.1190, -0.0581] * | -0.0479 [-0.0602, -0.0351] * | -0.1841 [-0.2624, -0.1026] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | isic2024 | +0.0013 [-0.0037, +0.0064] | +0.0043 [-0.0117, +0.0196] | +0.0014 [-0.0031, +0.0055] | +0.0211 [-0.0055, +0.0494] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | pad_ufes_20 | -0.0487 [-0.0638, -0.0356] * | -0.0563 [-0.0748, -0.0391] * | -0.0215 [-0.0293, -0.0140] * | -0.1005 [-0.1885, -0.0591] * |

## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | isic2024 | +0.0039 [-0.0116, +0.0198] | -0.0301 [-0.0638, -0.0052] * | +0.0023 [-0.0108, +0.0158] | -0.0079 [-0.0500, +0.0313] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | pad_ufes_20 | +0.0948 [+0.0700, +0.1199] * | +0.0874 [+0.0581, +0.1190] * | +0.0479 [+0.0351, +0.0602] * | +0.1841 [+0.1026, +0.2624] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | isic2024 | -0.0013 [-0.0064, +0.0037] | -0.0043 [-0.0196, +0.0117] | -0.0014 [-0.0055, +0.0031] | -0.0211 [-0.0494, +0.0055] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | pad_ufes_20 | +0.0487 [+0.0356, +0.0638] * | +0.0563 [+0.0391, +0.0748] * | +0.0215 [+0.0140, +0.0293] * | +0.1005 [+0.0591, +0.1885] * |
