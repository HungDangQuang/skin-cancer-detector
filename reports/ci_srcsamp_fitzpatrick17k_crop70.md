# Bootstrap 95% confidence intervals — `/workspace/skin-cancer-detector/.tmp/ci_srcsamp/fitzpatrick17k_crop70`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.6431 [0.6292, 0.6571] | 0.6217 [0.6039, 0.6415] | 0.0454 [0.0418, 0.0491] | 0.2167 [0.1976, 0.2359] |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.6874 [0.6734, 0.7019] | 0.6789 [0.6606, 0.6998] | 0.0494 [0.0455, 0.0536] | 0.2935 [0.2694, 0.3182] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.6808 [0.6666, 0.6952] | 0.6711 [0.6522, 0.6906] | 0.0492 [0.0452, 0.0534] | 0.2900 [0.2652, 0.3136] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.7109 [0.6975, 0.7251] | 0.7078 [0.6895, 0.7274] | 0.0543 [0.0501, 0.0589] | 0.3392 [0.3163, 0.3657] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0377 [+0.0303, +0.0451] * | +0.0493 [+0.0388, +0.0590] * | +0.0038 [+0.0014, +0.0061] * | +0.0733 [+0.0550, +0.0927] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium__srcsamp` | +0.0236 [+0.0178, +0.0293] * | +0.0289 [+0.0204, +0.0369] * | +0.0049 [+0.0024, +0.0073] * | +0.0456 [+0.0308, +0.0624] * |

## 3. Ablation effect — paired bootstrap (main − ablated)

Pairs each `__<suffix>` fork against the same run without the suffix. The sign is **main − ablated**, so a positive delta means the main configuration wins (e.g. `__train_isic_only` → positive = mixing PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as section 2. `*` marks an interval excluding 0.

| Ablated run | vs main | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | -0.0443 [-0.0524, -0.0357] * | -0.0571 [-0.0665, -0.0469] * | -0.0040 [-0.0071, -0.0010] * | -0.0769 [-0.0949, -0.0597] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | -0.0302 [-0.0349, -0.0257] * | -0.0367 [-0.0432, -0.0304] * | -0.0051 [-0.0071, -0.0033] * | -0.0492 [-0.0642, -0.0359] * |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | +0.0443 [+0.0357, +0.0524] * | +0.0571 [+0.0469, +0.0665] * | +0.0040 [+0.0010, +0.0071] * | +0.0769 [+0.0597, +0.0949] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0302 [+0.0257, +0.0349] * | +0.0367 [+0.0304, +0.0432] * | +0.0051 [+0.0033, +0.0071] * | +0.0492 [+0.0359, +0.0642] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `baseline_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6368 [0.5915, 0.6802] | 0.6273 [0.5690, 0.6894] | 0.0517 [0.0403, 0.0633] | 0.2077 [0.1475, 0.2597] |
| light | 0.6642 [0.6445, 0.6843] | 0.6567 [0.6309, 0.6844] | 0.0488 [0.0434, 0.0548] | 0.2378 [0.2088, 0.2645] |
| medium | 0.6164 [0.5935, 0.6403] | 0.5750 [0.5437, 0.6110] | 0.0396 [0.0344, 0.0454] | 0.1958 [0.1663, 0.2293] |
| **dark_minus_light** | -0.0273 [-0.0756, +0.0196] | -0.0293 [-0.0944, +0.0381] | +0.0029 [-0.0099, +0.0157] | -0.0301 [-0.0976, +0.0285] |
| **dark_minus_medium** | +0.0205 [-0.0301, +0.0712] | +0.0524 [-0.0180, +0.1198] | +0.0121 [-0.0007, +0.0254] | +0.0119 [-0.0585, +0.0701] |
| **light_minus_medium** | +0.0478 [+0.0198, +0.0761] * | +0.0817 [+0.0400, +0.1238] * | +0.0091 [+0.0016, +0.0170] * | +0.0421 [-0.0021, +0.0801] |

### `baseline_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7041 [0.6578, 0.7476] | 0.7158 [0.6621, 0.7728] | 0.0474 [0.0343, 0.0616] | 0.3615 [0.2689, 0.4524] |
| light | 0.6994 [0.6796, 0.7194] | 0.7044 [0.6774, 0.7326] | 0.0516 [0.0463, 0.0578] | 0.3090 [0.2742, 0.3452] |
| medium | 0.6662 [0.6428, 0.6899] | 0.6345 [0.6012, 0.6705] | 0.0474 [0.0413, 0.0539] | 0.2605 [0.2243, 0.3015] |
| **dark_minus_light** | +0.0047 [-0.0450, +0.0514] | +0.0114 [-0.0528, +0.0738] | -0.0043 [-0.0186, +0.0111] | +0.0526 [-0.0472, +0.1484] |
| **dark_minus_medium** | +0.0380 [-0.0148, +0.0874] | +0.0814 [+0.0143, +0.1470] * | -0.0000 [-0.0146, +0.0165] | +0.1010 [-0.0014, +0.1996] |
| **light_minus_medium** | +0.0333 [+0.0042, +0.0642] * | +0.0699 [+0.0273, +0.1152] * | +0.0042 [-0.0039, +0.0129] | +0.0485 [-0.0027, +0.0998] |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6997 [0.6543, 0.7419] | 0.7053 [0.6467, 0.7627] | 0.0553 [0.0431, 0.0696] | 0.3260 [0.2546, 0.3990] |
| light | 0.6942 [0.6748, 0.7140] | 0.6979 [0.6712, 0.7250] | 0.0521 [0.0464, 0.0585] | 0.3054 [0.2708, 0.3406] |
| medium | 0.6550 [0.6323, 0.6781] | 0.6215 [0.5891, 0.6577] | 0.0442 [0.0383, 0.0506] | 0.2528 [0.2161, 0.2911] |
| **dark_minus_light** | +0.0055 [-0.0457, +0.0512] | +0.0074 [-0.0568, +0.0681] | +0.0032 [-0.0111, +0.0185] | +0.0205 [-0.0568, +0.0984] |
| **dark_minus_medium** | +0.0447 [-0.0056, +0.0939] | +0.0838 [+0.0145, +0.1476] * | +0.0111 [-0.0030, +0.0270] | +0.0731 [-0.0078, +0.1560] |
| **light_minus_medium** | +0.0392 [+0.0106, +0.0697] * | +0.0764 [+0.0317, +0.1193] * | +0.0079 [-0.0002, +0.0164] | +0.0526 [+0.0039, +0.1025] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7353 [0.6893, 0.7769] | 0.7516 [0.6969, 0.8037] | 0.0623 [0.0493, 0.0765] | 0.3837 [0.3077, 0.4663] |
| light | 0.7218 [0.7027, 0.7415] | 0.7316 [0.7066, 0.7583] | 0.0554 [0.0494, 0.0619] | 0.3613 [0.3261, 0.3978] |
| medium | 0.6890 [0.6660, 0.7126] | 0.6615 [0.6284, 0.6979] | 0.0516 [0.0451, 0.0584] | 0.3022 [0.2598, 0.3449] |
| **dark_minus_light** | +0.0136 [-0.0349, +0.0593] | +0.0200 [-0.0412, +0.0787] | +0.0069 [-0.0074, +0.0221] | +0.0223 [-0.0638, +0.1108] |
| **dark_minus_medium** | +0.0463 [-0.0039, +0.0937] | +0.0901 [+0.0240, +0.1517] * | +0.0108 [-0.0039, +0.0270] | +0.0814 [-0.0060, +0.1731] |
| **light_minus_medium** | +0.0327 [+0.0043, +0.0642] * | +0.0701 [+0.0269, +0.1133] * | +0.0039 [-0.0048, +0.0131] | +0.0591 [+0.0048, +0.1172] * |


## 5. Ablation effect **within each `tone_group`** — paired (main − ablated)

Section 3 gives the ablation delta on the whole test set. For the PAD-mixing arms that is the wrong cell — the ISIC-only arm collapses on the PAD rows, and those rows carry ~75% of all positives, so the whole-test delta is inflated. **Quote this table instead.** Still paired: every run draws the same rows for a given group, so the replicate vectors difference directly. `*` marks an interval excluding 0.

| Ablated run | vs main | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | -0.0673 [-0.1007, -0.0357] * | -0.0885 [-0.1204, -0.0570] * | +0.0043 [-0.0071, +0.0154] | -0.1538 [-0.2279, -0.0899] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | -0.0353 [-0.0461, -0.0244] * | -0.0477 [-0.0606, -0.0353] * | -0.0029 [-0.0070, +0.0013] | -0.0711 [-0.0986, -0.0487] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | -0.0498 [-0.0636, -0.0354] * | -0.0595 [-0.0754, -0.0431] * | -0.0078 [-0.0125, -0.0028] * | -0.0647 [-0.0937, -0.0376] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | -0.0356 [-0.0519, -0.0199] * | -0.0464 [-0.0660, -0.0257] * | -0.0070 [-0.0131, -0.0012] * | -0.0577 [-0.1096, -0.0129] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | -0.0276 [-0.0337, -0.0212] * | -0.0337 [-0.0423, -0.0251] * | -0.0033 [-0.0059, -0.0007] * | -0.0559 [-0.0769, -0.0378] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | -0.0340 [-0.0421, -0.0259] * | -0.0401 [-0.0511, -0.0283] * | -0.0074 [-0.0106, -0.0042] * | -0.0494 [-0.0724, -0.0246] * |

## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | dark | +0.0673 [+0.0357, +0.1007] * | +0.0885 [+0.0570, +0.1204] * | -0.0043 [-0.0154, +0.0071] | +0.1538 [+0.0899, +0.2279] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | light | +0.0353 [+0.0244, +0.0461] * | +0.0477 [+0.0353, +0.0606] * | +0.0029 [-0.0013, +0.0070] | +0.0711 [+0.0487, +0.0986] * |
| `baseline_mobilenetv4_conv_medium__srcsamp` | `baseline_mobilenetv4_conv_medium` | medium | +0.0498 [+0.0354, +0.0636] * | +0.0595 [+0.0431, +0.0754] * | +0.0078 [+0.0028, +0.0125] * | +0.0647 [+0.0376, +0.0937] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | dark | +0.0356 [+0.0199, +0.0519] * | +0.0464 [+0.0257, +0.0660] * | +0.0070 [+0.0012, +0.0131] * | +0.0577 [+0.0129, +0.1096] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | light | +0.0276 [+0.0212, +0.0337] * | +0.0337 [+0.0251, +0.0423] * | +0.0033 [+0.0007, +0.0059] * | +0.0559 [+0.0378, +0.0769] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | medium | +0.0340 [+0.0259, +0.0421] * | +0.0401 [+0.0283, +0.0511] * | +0.0074 [+0.0042, +0.0106] * | +0.0494 [+0.0246, +0.0724] * |
