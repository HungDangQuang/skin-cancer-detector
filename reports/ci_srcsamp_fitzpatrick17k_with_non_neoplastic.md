# Bootstrap 95% confidence intervals — `/workspace/skin-cancer-detector/.tmp/ci_srcsamp/fitzpatrick17k_with_non_neoplastic`

B = 2000 replicates, seed 42, 16012 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.6479 [0.6377, 0.6589] | 0.2302 [0.2188, 0.2435] | 0.0426 [0.0397, 0.0458] | 0.2376 [0.2240, 0.2528] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6683 [0.6566, 0.6810] | 0.2881 [0.2711, 0.3067] | 0.0383 [0.0354, 0.0417] | 0.3143 [0.2972, 0.3330] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.6681 [0.6568, 0.6799] | 0.2614 [0.2476, 0.2772] | 0.0431 [0.0401, 0.0465] | 0.2832 [0.2667, 0.3000] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6900 [0.6781, 0.7024] | 0.3009 [0.2847, 0.3189] | 0.0432 [0.0399, 0.0469] | 0.3360 [0.3176, 0.3541] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0202 [+0.0145, +0.0258] * | +0.0312 [+0.0239, +0.0388] * | +0.0005 [-0.0014, +0.0024] | +0.0456 [+0.0335, +0.0558] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0217 [+0.0167, +0.0268] * | +0.0128 [+0.0053, +0.0202] * | +0.0048 [+0.0030, +0.0069] * | +0.0218 [+0.0104, +0.0313] * |

## 3. Ablation effect — paired bootstrap (main − ablated)

Pairs each `__<suffix>` fork against the same run without the suffix. The sign is **main − ablated**, so a positive delta means the main configuration wins (e.g. `__train_isic_only` → positive = mixing PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as section 2. `*` marks an interval excluding 0.

| Ablated run | vs main | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | -0.0204 [-0.0268, -0.0140] * | -0.0578 [-0.0671, -0.0492] * | +0.0043 [+0.0020, +0.0066] * | -0.0767 [-0.0887, -0.0652] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | -0.0219 [-0.0259, -0.0178] * | -0.0395 [-0.0454, -0.0335] * | -0.0001 [-0.0017, +0.0016] | -0.0528 [-0.0623, -0.0440] * |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | +0.0204 [+0.0140, +0.0268] * | +0.0578 [+0.0492, +0.0671] * | -0.0043 [-0.0066, -0.0020] * | +0.0767 [+0.0652, +0.0887] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0219 [+0.0178, +0.0259] * | +0.0395 [+0.0335, +0.0454] * | +0.0001 [-0.0016, +0.0017] | +0.0528 [+0.0440, +0.0623] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6363 [0.6053, 0.6675] | 0.1600 [0.1354, 0.1932] | 0.0448 [0.0381, 0.0533] | 0.2154 [0.1736, 0.2544] |
| light | 0.6645 [0.6503, 0.6790] | 0.2826 [0.2648, 0.3024] | 0.0446 [0.0405, 0.0489] | 0.2664 [0.2466, 0.2868] |
| medium | 0.6342 [0.6175, 0.6520] | 0.1953 [0.1794, 0.2146] | 0.0414 [0.0372, 0.0464] | 0.2127 [0.1915, 0.2361] |
| **dark_minus_light** | -0.0283 [-0.0620, +0.0053] | -0.1226 [-0.1542, -0.0854] * | +0.0002 [-0.0081, +0.0096] | -0.0511 [-0.0965, -0.0092] * |
| **dark_minus_medium** | +0.0020 [-0.0337, +0.0381] | -0.0353 [-0.0670, +0.0030] | +0.0034 [-0.0052, +0.0130] | +0.0027 [-0.0450, +0.0449] |
| **light_minus_medium** | +0.0303 [+0.0079, +0.0528] * | +0.0873 [+0.0614, +0.1130] * | +0.0031 [-0.0033, +0.0094] | +0.0538 [+0.0233, +0.0846] * |

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6627 [0.6275, 0.6975] | 0.1952 [0.1634, 0.2403] | 0.0411 [0.0329, 0.0517] | 0.2721 [0.2240, 0.3255] |
| light | 0.6899 [0.6742, 0.7060] | 0.3494 [0.3256, 0.3758] | 0.0408 [0.0369, 0.0455] | 0.3528 [0.3281, 0.3763] |
| medium | 0.6401 [0.6196, 0.6603] | 0.2354 [0.2118, 0.2628] | 0.0359 [0.0318, 0.0406] | 0.2729 [0.2448, 0.2996] |
| **dark_minus_light** | -0.0272 [-0.0664, +0.0101] | -0.1542 [-0.1966, -0.1049] * | +0.0004 [-0.0087, +0.0116] | -0.0807 [-0.1359, -0.0209] * |
| **dark_minus_medium** | +0.0226 [-0.0176, +0.0636] | -0.0402 [-0.0821, +0.0114] | +0.0053 [-0.0047, +0.0168] | -0.0008 [-0.0560, +0.0601] |
| **light_minus_medium** | +0.0498 [+0.0238, +0.0765] * | +0.1140 [+0.0786, +0.1503] * | +0.0049 [-0.0011, +0.0111] | +0.0799 [+0.0432, +0.1189] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6812 [0.6479, 0.7140] | 0.2018 [0.1678, 0.2447] | 0.0495 [0.0410, 0.0596] | 0.2779 [0.2255, 0.3290] |
| light | 0.6743 [0.6592, 0.6896] | 0.2995 [0.2795, 0.3221] | 0.0438 [0.0396, 0.0484] | 0.2929 [0.2697, 0.3165] |
| medium | 0.6495 [0.6309, 0.6683] | 0.2234 [0.2032, 0.2480] | 0.0412 [0.0369, 0.0461] | 0.2515 [0.2267, 0.2791] |
| **dark_minus_light** | +0.0069 [-0.0295, +0.0432] | -0.0977 [-0.1384, -0.0510] * | +0.0057 [-0.0038, +0.0166] | -0.0150 [-0.0718, +0.0420] |
| **dark_minus_medium** | +0.0317 [-0.0059, +0.0698] | -0.0216 [-0.0634, +0.0257] | +0.0083 [-0.0014, +0.0192] | +0.0264 [-0.0318, +0.0856] |
| **light_minus_medium** | +0.0249 [+0.0003, +0.0489] * | +0.0761 [+0.0453, +0.1071] * | +0.0026 [-0.0039, +0.0089] | +0.0414 [+0.0063, +0.0748] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7053 [0.6713, 0.7390] | 0.2194 [0.1820, 0.2680] | 0.0528 [0.0438, 0.0646] | 0.3250 [0.2673, 0.3846] |
| light | 0.7007 [0.6848, 0.7169] | 0.3504 [0.3273, 0.3765] | 0.0434 [0.0389, 0.0485] | 0.3583 [0.3331, 0.3833] |
| medium | 0.6681 [0.6488, 0.6878] | 0.2553 [0.2309, 0.2844] | 0.0420 [0.0373, 0.0472] | 0.2993 [0.2687, 0.3314] |
| **dark_minus_light** | +0.0046 [-0.0333, +0.0421] | -0.1310 [-0.1772, -0.0791] * | +0.0094 [-0.0015, +0.0221] | -0.0333 [-0.0941, +0.0313] |
| **dark_minus_medium** | +0.0372 [-0.0016, +0.0775] | -0.0359 [-0.0823, +0.0172] | +0.0108 [+0.0005, +0.0237] * | +0.0257 [-0.0392, +0.0927] |
| **light_minus_medium** | +0.0326 [+0.0068, +0.0576] * | +0.0951 [+0.0596, +0.1318] * | +0.0014 [-0.0054, +0.0082] | +0.0590 [+0.0182, +0.0988] * |


## 5. Ablation effect **within each `tone_group`** — paired (main − ablated)

Section 3 gives the ablation delta on the whole test set. For the PAD-mixing arms that is the wrong cell — the ISIC-only arm collapses on the PAD rows, and those rows carry ~75% of all positives, so the whole-test delta is inflated. **Quote this table instead.** Still paired: every run draws the same rows for a given group, so the replicate vectors difference directly. `*` marks an interval excluding 0.

| Ablated run | vs main | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | -0.0264 [-0.0504, -0.0015] * | -0.0352 [-0.0564, -0.0171] * | +0.0037 [-0.0055, +0.0124] | -0.0567 [-0.0945, -0.0271] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | -0.0254 [-0.0338, -0.0167] * | -0.0668 [-0.0792, -0.0543] * | +0.0038 [+0.0006, +0.0070] * | -0.0864 [-0.1018, -0.0696] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | -0.0059 [-0.0169, +0.0054] | -0.0401 [-0.0541, -0.0277] * | +0.0056 [+0.0019, +0.0094] * | -0.0602 [-0.0772, -0.0412] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | -0.0241 [-0.0369, -0.0122] * | -0.0176 [-0.0353, +0.0006] | -0.0033 [-0.0097, +0.0023] | -0.0471 [-0.0833, -0.0144] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | -0.0263 [-0.0314, -0.0209] * | -0.0509 [-0.0600, -0.0424] * | +0.0004 [-0.0019, +0.0028] | -0.0654 [-0.0788, -0.0513] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | -0.0186 [-0.0254, -0.0122] * | -0.0319 [-0.0413, -0.0232] * | -0.0008 [-0.0032, +0.0016] | -0.0478 [-0.0625, -0.0326] * |

## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | +0.0264 [+0.0015, +0.0504] * | +0.0352 [+0.0171, +0.0564] * | -0.0037 [-0.0124, +0.0055] | +0.0567 [+0.0271, +0.0945] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | +0.0254 [+0.0167, +0.0338] * | +0.0668 [+0.0543, +0.0792] * | -0.0038 [-0.0070, -0.0006] * | +0.0864 [+0.0696, +0.1018] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | +0.0059 [-0.0054, +0.0169] | +0.0401 [+0.0277, +0.0541] * | -0.0056 [-0.0094, -0.0019] * | +0.0602 [+0.0412, +0.0772] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | +0.0241 [+0.0122, +0.0369] * | +0.0176 [-0.0006, +0.0353] | +0.0033 [-0.0023, +0.0097] | +0.0471 [+0.0144, +0.0833] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | +0.0263 [+0.0209, +0.0314] * | +0.0509 [+0.0424, +0.0600] * | -0.0004 [-0.0028, +0.0019] | +0.0654 [+0.0513, +0.0788] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | +0.0186 [+0.0122, +0.0254] * | +0.0319 [+0.0232, +0.0413] * | +0.0008 [-0.0016, +0.0032] | +0.0478 [+0.0326, +0.0625] * |
