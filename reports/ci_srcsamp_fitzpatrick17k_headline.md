# Bootstrap 95% confidence intervals — `/workspace/skin-cancer-detector/.tmp/ci_srcsamp/fitzpatrick17k_headline`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.6401 [0.6263, 0.6536] | 0.6188 [0.6004, 0.6384] | 0.0437 [0.0403, 0.0475] | 0.2108 [0.1928, 0.2285] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6791 [0.6652, 0.6931] | 0.6752 [0.6565, 0.6956] | 0.0469 [0.0433, 0.0510] | 0.2904 [0.2654, 0.3151] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.6690 [0.6551, 0.6833] | 0.6624 [0.6436, 0.6822] | 0.0454 [0.0416, 0.0492] | 0.2741 [0.2493, 0.2960] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6999 [0.6861, 0.7145] | 0.6951 [0.6767, 0.7148] | 0.0515 [0.0475, 0.0558] | 0.3265 [0.3009, 0.3513] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0289 [+0.0212, +0.0362] * | +0.0436 [+0.0338, +0.0527] * | +0.0016 [-0.0008, +0.0041] | +0.0632 [+0.0452, +0.0799] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0208 [+0.0147, +0.0269] * | +0.0199 [+0.0119, +0.0279] * | +0.0045 [+0.0021, +0.0069] * | +0.0361 [+0.0206, +0.0521] * |

## 3. Ablation effect — paired bootstrap (main − ablated)

Pairs each `__<suffix>` fork against the same run without the suffix. The sign is **main − ablated**, so a positive delta means the main configuration wins (e.g. `__train_isic_only` → positive = mixing PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as section 2. `*` marks an interval excluding 0.

| Ablated run | vs main | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | -0.0390 [-0.0471, -0.0307] * | -0.0565 [-0.0654, -0.0468] * | -0.0032 [-0.0061, -0.0002] * | -0.0795 [-0.0964, -0.0633] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | -0.0309 [-0.0360, -0.0257] * | -0.0328 [-0.0391, -0.0262] * | -0.0061 [-0.0080, -0.0041] * | -0.0524 [-0.0682, -0.0395] * |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | +0.0390 [+0.0307, +0.0471] * | +0.0565 [+0.0468, +0.0654] * | +0.0032 [+0.0002, +0.0061] * | +0.0795 [+0.0633, +0.0964] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0309 [+0.0257, +0.0360] * | +0.0328 [+0.0262, +0.0391] * | +0.0061 [+0.0041, +0.0080] * | +0.0524 [+0.0395, +0.0682] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6270 [0.5835, 0.6687] | 0.6217 [0.5613, 0.6841] | 0.0452 [0.0356, 0.0561] | 0.2221 [0.1664, 0.2734] |
| light | 0.6609 [0.6420, 0.6803] | 0.6549 [0.6282, 0.6816] | 0.0472 [0.0419, 0.0531] | 0.2269 [0.2024, 0.2569] |
| medium | 0.6146 [0.5918, 0.6377] | 0.5687 [0.5380, 0.6036] | 0.0386 [0.0333, 0.0442] | 0.1844 [0.1565, 0.2113] |
| **dark_minus_light** | -0.0339 [-0.0839, +0.0127] | -0.0332 [-0.0993, +0.0347] | -0.0020 [-0.0138, +0.0104] | -0.0048 [-0.0701, +0.0503] |
| **dark_minus_medium** | +0.0124 [-0.0368, +0.0619] | +0.0530 [-0.0168, +0.1231] | +0.0066 [-0.0050, +0.0193] | +0.0377 [-0.0246, +0.0956] |
| **light_minus_medium** | +0.0463 [+0.0174, +0.0759] * | +0.0862 [+0.0430, +0.1271] * | +0.0086 [+0.0011, +0.0164] * | +0.0425 [+0.0071, +0.0823] * |

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6917 [0.6454, 0.7337] | 0.7017 [0.6429, 0.7573] | 0.0470 [0.0359, 0.0604] | 0.3212 [0.2505, 0.3990] |
| light | 0.6928 [0.6735, 0.7129] | 0.7041 [0.6773, 0.7318] | 0.0485 [0.0435, 0.0542] | 0.3215 [0.2878, 0.3566] |
| medium | 0.6561 [0.6328, 0.6802] | 0.6246 [0.5914, 0.6606] | 0.0452 [0.0396, 0.0511] | 0.2431 [0.2115, 0.2801] |
| **dark_minus_light** | -0.0011 [-0.0492, +0.0445] | -0.0024 [-0.0693, +0.0611] | -0.0015 [-0.0139, +0.0128] | -0.0004 [-0.0805, +0.0855] |
| **dark_minus_medium** | +0.0356 [-0.0159, +0.0835] | +0.0771 [+0.0076, +0.1433] * | +0.0018 [-0.0106, +0.0162] | +0.0781 [-0.0036, +0.1606] |
| **light_minus_medium** | +0.0367 [+0.0072, +0.0680] * | +0.0795 [+0.0351, +0.1240] * | +0.0033 [-0.0044, +0.0115] | +0.0784 [+0.0319, +0.1271] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6839 [0.6383, 0.7264] | 0.6937 [0.6361, 0.7504] | 0.0489 [0.0385, 0.0621] | 0.3096 [0.2202, 0.3768] |
| light | 0.6854 [0.6663, 0.7055] | 0.6936 [0.6673, 0.7203] | 0.0484 [0.0432, 0.0542] | 0.2951 [0.2640, 0.3372] |
| medium | 0.6402 [0.6156, 0.6634] | 0.6073 [0.5747, 0.6420] | 0.0409 [0.0354, 0.0467] | 0.2251 [0.1942, 0.2579] |
| **dark_minus_light** | -0.0015 [-0.0542, +0.0450] | +0.0001 [-0.0668, +0.0640] | +0.0005 [-0.0116, +0.0144] | +0.0146 [-0.0890, +0.0886] |
| **dark_minus_medium** | +0.0437 [-0.0079, +0.0936] | +0.0864 [+0.0169, +0.1508] * | +0.0081 [-0.0038, +0.0220] | +0.0845 [-0.0108, +0.1594] |
| **light_minus_medium** | +0.0452 [+0.0152, +0.0762] * | +0.0863 [+0.0422, +0.1279] * | +0.0076 [-0.0001, +0.0153] | +0.0700 [+0.0264, +0.1223] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7158 [0.6694, 0.7584] | 0.7254 [0.6698, 0.7819] | 0.0562 [0.0445, 0.0702] | 0.3558 [0.2838, 0.4480] |
| light | 0.7148 [0.6960, 0.7342] | 0.7246 [0.6987, 0.7504] | 0.0533 [0.0474, 0.0593] | 0.3528 [0.3173, 0.3907] |
| medium | 0.6727 [0.6490, 0.6955] | 0.6421 [0.6085, 0.6797] | 0.0485 [0.0429, 0.0547] | 0.2830 [0.2459, 0.3248] |
| **dark_minus_light** | +0.0010 [-0.0485, +0.0455] | +0.0007 [-0.0627, +0.0626] | +0.0029 [-0.0100, +0.0179] | +0.0030 [-0.0785, +0.1033] |
| **dark_minus_medium** | +0.0431 [-0.0070, +0.0912] | +0.0833 [+0.0153, +0.1479] * | +0.0077 [-0.0058, +0.0228] | +0.0728 [-0.0102, +0.1748] |
| **light_minus_medium** | +0.0421 [+0.0119, +0.0736] * | +0.0825 [+0.0376, +0.1250] * | +0.0048 [-0.0034, +0.0135] | +0.0698 [+0.0175, +0.1251] * |


## 5. Ablation effect **within each `tone_group`** — paired (main − ablated)

Section 3 gives the ablation delta on the whole test set. For the PAD-mixing arms that is the wrong cell — the ISIC-only arm collapses on the PAD rows, and those rows carry ~75% of all positives, so the whole-test delta is inflated. **Quote this table instead.** Still paired: every run draws the same rows for a given group, so the replicate vectors difference directly. `*` marks an interval excluding 0.

| Ablated run | vs main | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | -0.0647 [-0.0986, -0.0315] * | -0.0800 [-0.1098, -0.0479] * | -0.0018 [-0.0137, +0.0094] | -0.0990 [-0.1581, -0.0486] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | -0.0319 [-0.0431, -0.0213] * | -0.0492 [-0.0612, -0.0368] * | -0.0013 [-0.0054, +0.0024] | -0.0946 [-0.1192, -0.0711] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | -0.0415 [-0.0557, -0.0273] * | -0.0559 [-0.0714, -0.0400] * | -0.0066 [-0.0115, -0.0016] * | -0.0587 [-0.0839, -0.0371] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | -0.0319 [-0.0500, -0.0145] * | -0.0317 [-0.0544, -0.0115] * | -0.0073 [-0.0143, -0.0001] * | -0.0462 [-0.1280, -0.0069] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | -0.0295 [-0.0363, -0.0226] * | -0.0311 [-0.0395, -0.0223] * | -0.0048 [-0.0077, -0.0019] * | -0.0577 [-0.0746, -0.0335] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | -0.0326 [-0.0411, -0.0239] * | -0.0348 [-0.0461, -0.0238] * | -0.0076 [-0.0106, -0.0044] * | -0.0579 [-0.0808, -0.0352] * |

## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | +0.0647 [+0.0315, +0.0986] * | +0.0800 [+0.0479, +0.1098] * | +0.0018 [-0.0094, +0.0137] | +0.0990 [+0.0486, +0.1581] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | +0.0319 [+0.0213, +0.0431] * | +0.0492 [+0.0368, +0.0612] * | +0.0013 [-0.0024, +0.0054] | +0.0946 [+0.0711, +0.1192] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | +0.0415 [+0.0273, +0.0557] * | +0.0559 [+0.0400, +0.0714] * | +0.0066 [+0.0016, +0.0115] * | +0.0587 [+0.0371, +0.0839] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | +0.0319 [+0.0145, +0.0500] * | +0.0317 [+0.0115, +0.0544] * | +0.0073 [+0.0001, +0.0143] * | +0.0462 [+0.0069, +0.1280] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | +0.0295 [+0.0226, +0.0363] * | +0.0311 [+0.0223, +0.0395] * | +0.0048 [+0.0019, +0.0077] * | +0.0577 [+0.0335, +0.0746] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | +0.0326 [+0.0239, +0.0411] * | +0.0348 [+0.0238, +0.0461] * | +0.0076 [+0.0044, +0.0106] * | +0.0579 [+0.0352, +0.0808] * |
