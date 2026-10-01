# Bootstrap 95% confidence intervals — `/workspace/skin-cancer-detector/.tmp/ci_srcsamp/fitzpatrick17k_crop50`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.6383 [0.6244, 0.6526] | 0.6260 [0.6074, 0.6458] | 0.0425 [0.0389, 0.0463] | 0.2190 [0.2023, 0.2403] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6853 [0.6707, 0.6997] | 0.6730 [0.6542, 0.6936] | 0.0513 [0.0474, 0.0556] | 0.2778 [0.2527, 0.3028] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.6746 [0.6601, 0.6891] | 0.6661 [0.6473, 0.6863] | 0.0461 [0.0423, 0.0501] | 0.2809 [0.2554, 0.3063] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.7043 [0.6906, 0.7185] | 0.7021 [0.6838, 0.7216] | 0.0521 [0.0479, 0.0566] | 0.3240 [0.2993, 0.3492] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0363 [+0.0288, +0.0436] * | +0.0402 [+0.0302, +0.0496] * | +0.0036 [+0.0014, +0.0058] * | +0.0619 [+0.0421, +0.0785] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0190 [+0.0130, +0.0249] * | +0.0292 [+0.0214, +0.0370] * | +0.0008 [-0.0019, +0.0034] | +0.0462 [+0.0307, +0.0618] * |

## 3. Ablation effect — paired bootstrap (main − ablated)

Pairs each `__<suffix>` fork against the same run without the suffix. The sign is **main − ablated**, so a positive delta means the main configuration wins (e.g. `__train_isic_only` → positive = mixing PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as section 2. `*` marks an interval excluding 0.

| Ablated run | vs main | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | -0.0470 [-0.0557, -0.0384] * | -0.0470 [-0.0564, -0.0371] * | -0.0088 [-0.0122, -0.0055] * | -0.0588 [-0.0750, -0.0387] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | -0.0297 [-0.0341, -0.0255] * | -0.0360 [-0.0419, -0.0300] * | -0.0060 [-0.0078, -0.0043] * | -0.0431 [-0.0570, -0.0301] * |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | +0.0470 [+0.0384, +0.0557] * | +0.0470 [+0.0371, +0.0564] * | +0.0088 [+0.0055, +0.0122] * | +0.0588 [+0.0387, +0.0750] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0297 [+0.0255, +0.0341] * | +0.0360 [+0.0300, +0.0419] * | +0.0060 [+0.0043, +0.0078] * | +0.0431 [+0.0301, +0.0570] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6455 [0.5998, 0.6895] | 0.6420 [0.5841, 0.7042] | 0.0525 [0.0409, 0.0647] | 0.2106 [0.1674, 0.2758] |
| light | 0.6550 [0.6347, 0.6753] | 0.6526 [0.6258, 0.6802] | 0.0454 [0.0401, 0.0514] | 0.2244 [0.1998, 0.2585] |
| medium | 0.6186 [0.5948, 0.6422] | 0.5915 [0.5595, 0.6265] | 0.0368 [0.0311, 0.0431] | 0.2217 [0.1881, 0.2498] |
| **dark_minus_light** | -0.0095 [-0.0606, +0.0392] | -0.0106 [-0.0735, +0.0551] | +0.0071 [-0.0064, +0.0208] | -0.0139 [-0.0712, +0.0518] |
| **dark_minus_medium** | +0.0269 [-0.0250, +0.0770] | +0.0505 [-0.0187, +0.1181] | +0.0157 [+0.0029, +0.0292] * | -0.0111 [-0.0617, +0.0629] |
| **light_minus_medium** | +0.0364 [+0.0064, +0.0668] * | +0.0611 [+0.0179, +0.1039] * | +0.0087 [+0.0006, +0.0169] * | +0.0028 [-0.0332, +0.0524] |

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6919 [0.6466, 0.7353] | 0.7056 [0.6504, 0.7625] | 0.0480 [0.0362, 0.0622] | 0.3212 [0.2491, 0.4073] |
| light | 0.6956 [0.6766, 0.7155] | 0.6932 [0.6663, 0.7212] | 0.0541 [0.0488, 0.0606] | 0.2837 [0.2488, 0.3197] |
| medium | 0.6687 [0.6454, 0.6923] | 0.6372 [0.6029, 0.6728] | 0.0484 [0.0422, 0.0552] | 0.2605 [0.2242, 0.3003] |
| **dark_minus_light** | -0.0037 [-0.0541, +0.0461] | +0.0124 [-0.0507, +0.0770] | -0.0061 [-0.0193, +0.0093] | +0.0375 [-0.0405, +0.1363] |
| **dark_minus_medium** | +0.0232 [-0.0296, +0.0757] | +0.0684 [+0.0018, +0.1359] * | -0.0004 [-0.0141, +0.0150] | +0.0607 [-0.0196, +0.1557] |
| **light_minus_medium** | +0.0269 [-0.0022, +0.0584] | +0.0560 [+0.0131, +0.1004] * | +0.0057 [-0.0026, +0.0153] | +0.0232 [-0.0297, +0.0723] |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6951 [0.6508, 0.7396] | 0.7059 [0.6491, 0.7631] | 0.0533 [0.0416, 0.0667] | 0.3240 [0.2502, 0.4061] |
| light | 0.6882 [0.6687, 0.7078] | 0.6917 [0.6646, 0.7206] | 0.0488 [0.0434, 0.0551] | 0.2934 [0.2606, 0.3311] |
| medium | 0.6505 [0.6267, 0.6747] | 0.6209 [0.5879, 0.6569] | 0.0406 [0.0346, 0.0470] | 0.2520 [0.2190, 0.2897] |
| **dark_minus_light** | +0.0069 [-0.0407, +0.0553] | +0.0142 [-0.0493, +0.0773] | +0.0044 [-0.0084, +0.0192] | +0.0306 [-0.0522, +0.1230] |
| **dark_minus_medium** | +0.0446 [-0.0061, +0.0940] | +0.0850 [+0.0171, +0.1491] * | +0.0127 [-0.0004, +0.0279] | +0.0720 [-0.0108, +0.1582] |
| **light_minus_medium** | +0.0377 [+0.0087, +0.0685] * | +0.0708 [+0.0265, +0.1158] * | +0.0083 [-0.0002, +0.0167] | +0.0413 [-0.0128, +0.0921] |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7282 [0.6840, 0.7722] | 0.7363 [0.6796, 0.7956] | 0.0592 [0.0460, 0.0744] | 0.4029 [0.3173, 0.4804] |
| light | 0.7152 [0.6962, 0.7345] | 0.7252 [0.6993, 0.7527] | 0.0543 [0.0485, 0.0610] | 0.3431 [0.3080, 0.3780] |
| medium | 0.6840 [0.6593, 0.7081] | 0.6639 [0.6298, 0.6997] | 0.0478 [0.0413, 0.0550] | 0.2914 [0.2575, 0.3320] |
| **dark_minus_light** | +0.0131 [-0.0350, +0.0625] | +0.0112 [-0.0503, +0.0745] | +0.0050 [-0.0092, +0.0208] | +0.0598 [-0.0318, +0.1458] |
| **dark_minus_medium** | +0.0442 [-0.0079, +0.0953] | +0.0724 [+0.0039, +0.1392] * | +0.0114 [-0.0034, +0.0280] | +0.1115 [+0.0165, +0.1951] * |
| **light_minus_medium** | +0.0311 [+0.0024, +0.0620] * | +0.0613 [+0.0188, +0.1048] * | +0.0064 [-0.0024, +0.0155] | +0.0517 [-0.0035, +0.1001] |


## 5. Ablation effect **within each `tone_group`** — paired (main − ablated)

Section 3 gives the ablation delta on the whole test set. For the PAD-mixing arms that is the wrong cell — the ISIC-only arm collapses on the PAD rows, and those rows carry ~75% of all positives, so the whole-test delta is inflated. **Quote this table instead.** Still paired: every run draws the same rows for a given group, so the replicate vectors difference directly. `*` marks an interval excluding 0.

| Ablated run | vs main | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | -0.0464 [-0.0775, -0.0147] * | -0.0636 [-0.0925, -0.0322] * | +0.0045 [-0.0071, +0.0149] | -0.1106 [-0.1762, -0.0483] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | -0.0406 [-0.0520, -0.0297] * | -0.0406 [-0.0534, -0.0282] * | -0.0087 [-0.0132, -0.0044] * | -0.0592 [-0.0804, -0.0307] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | -0.0501 [-0.0648, -0.0347] * | -0.0457 [-0.0615, -0.0285] * | -0.0116 [-0.0170, -0.0057] * | -0.0388 [-0.0715, -0.0143] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | -0.0332 [-0.0479, -0.0187] * | -0.0304 [-0.0507, -0.0114] * | -0.0060 [-0.0128, +0.0007] | -0.0788 [-0.1215, -0.0333] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | -0.0270 [-0.0326, -0.0214] * | -0.0334 [-0.0407, -0.0256] * | -0.0054 [-0.0080, -0.0030] * | -0.0497 [-0.0659, -0.0300] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | -0.0336 [-0.0407, -0.0259] * | -0.0430 [-0.0531, -0.0315] * | -0.0073 [-0.0100, -0.0045] * | -0.0394 [-0.0592, -0.0192] * |

## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | +0.0464 [+0.0147, +0.0775] * | +0.0636 [+0.0322, +0.0925] * | -0.0045 [-0.0149, +0.0071] | +0.1106 [+0.0483, +0.1762] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | +0.0406 [+0.0297, +0.0520] * | +0.0406 [+0.0282, +0.0534] * | +0.0087 [+0.0044, +0.0132] * | +0.0592 [+0.0307, +0.0804] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | +0.0501 [+0.0347, +0.0648] * | +0.0457 [+0.0285, +0.0615] * | +0.0116 [+0.0057, +0.0170] * | +0.0388 [+0.0143, +0.0715] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | +0.0332 [+0.0187, +0.0479] * | +0.0304 [+0.0114, +0.0507] * | +0.0060 [-0.0007, +0.0128] | +0.0788 [+0.0333, +0.1215] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | +0.0270 [+0.0214, +0.0326] * | +0.0334 [+0.0256, +0.0407] * | +0.0054 [+0.0030, +0.0080] * | +0.0497 [+0.0300, +0.0659] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | +0.0336 [+0.0259, +0.0407] * | +0.0430 [+0.0315, +0.0531] * | +0.0073 [+0.0045, +0.0100] * | +0.0394 [+0.0192, +0.0592] * |
