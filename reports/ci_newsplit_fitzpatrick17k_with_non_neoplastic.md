# Bootstrap 95% confidence intervals — `.tmp/ci_newsplit/fitzpatrick17k/with_non_neoplastic`

B = 2000 replicates, seed 42, 16012 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4` | 5 | 0.6469 [0.6353, 0.6585] | 0.2050 [0.1946, 0.2174] | 0.0438 [0.0405, 0.0472] | 0.2061 [0.1919, 0.2211] |
| `x_baseline_mobilenetv4__domain` | 5 | 0.6223 [0.6109, 0.6340] | 0.1872 [0.1779, 0.1979] | 0.0398 [0.0368, 0.0431] | 0.1429 [0.1312, 0.1645] |
| `x_kd_mobilenetv4` | 5 | 0.6459 [0.6357, 0.6565] | 0.2180 [0.2069, 0.2311] | 0.0429 [0.0402, 0.0460] | 0.2267 [0.2118, 0.2411] |
| `x_kd_mobilenetv4__domain` | 5 | 0.6064 [0.5965, 0.6170] | 0.1786 [0.1704, 0.1882] | 0.0379 [0.0353, 0.0407] | 0.1598 [0.1507, 0.1706] |
| `x_teacher_efficientnetv2_m` | 5 | 0.6956 [0.6845, 0.7065] | 0.2870 [0.2722, 0.3037] | 0.0502 [0.0468, 0.0539] | 0.3094 [0.2938, 0.3256] |
| `x_teacher_efficientnetv2_m__domain` | 5 | 0.6960 [0.6849, 0.7070] | 0.2919 [0.2767, 0.3082] | 0.0509 [0.0474, 0.0547] | 0.3147 [0.2986, 0.3314] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | -0.0246 [-0.0305, -0.0182] * | -0.0178 [-0.0222, -0.0131] * | -0.0039 [-0.0062, -0.0019] * | -0.0632 [-0.0743, -0.0418] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | -0.0395 [-0.0462, -0.0328] * | -0.0395 [-0.0464, -0.0333] * | -0.0050 [-0.0071, -0.0030] * | -0.0669 [-0.0777, -0.0550] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | +0.0004 [-0.0052, +0.0060] | +0.0049 [-0.0032, +0.0128] | +0.0007 [-0.0016, +0.0028] | +0.0054 [-0.0067, +0.0167] |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `x_baseline_mobilenetv4`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6493 [0.6164, 0.6828] | 0.1512 [0.1273, 0.1856] | 0.0507 [0.0430, 0.0601] | 0.1817 [0.1401, 0.2289] |
| light | 0.6634 [0.6484, 0.6781] | 0.2449 [0.2288, 0.2629] | 0.0461 [0.0417, 0.0510] | 0.2346 [0.2120, 0.2571] |
| medium | 0.6241 [0.6056, 0.6438] | 0.1761 [0.1609, 0.1938] | 0.0399 [0.0355, 0.0449] | 0.1815 [0.1579, 0.2046] |
| **dark_minus_light** | -0.0141 [-0.0503, +0.0231] | -0.0937 [-0.1225, -0.0571] * | +0.0046 [-0.0043, +0.0152] | -0.0529 [-0.0988, +0.0010] |
| **dark_minus_medium** | +0.0252 [-0.0131, +0.0651] | -0.0249 [-0.0535, +0.0114] | +0.0108 [+0.0014, +0.0211] * | +0.0002 [-0.0469, +0.0542] |
| **light_minus_medium** | +0.0392 [+0.0140, +0.0638] * | +0.0688 [+0.0447, +0.0927] * | +0.0062 [-0.0006, +0.0129] | +0.0531 [+0.0211, +0.0865] * |

### `x_baseline_mobilenetv4__domain`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6045 [0.5709, 0.6383] | 0.1251 [0.1073, 0.1509] | 0.0404 [0.0315, 0.0508] | 0.1096 [0.0773, 0.1411] |
| light | 0.6511 [0.6361, 0.6667] | 0.2392 [0.2239, 0.2569] | 0.0433 [0.0390, 0.0482] | 0.2186 [0.1981, 0.2389] |
| medium | 0.6054 [0.5870, 0.6245] | 0.1649 [0.1511, 0.1803] | 0.0386 [0.0342, 0.0435] | 0.1313 [0.1146, 0.1564] |
| **dark_minus_light** | -0.0466 [-0.0838, -0.0091] * | -0.1141 [-0.1388, -0.0848] * | -0.0029 [-0.0127, +0.0084] | -0.1090 [-0.1463, -0.0714] * |
| **dark_minus_medium** | -0.0010 [-0.0410, +0.0380] | -0.0398 [-0.0636, -0.0111] * | +0.0018 [-0.0084, +0.0131] | -0.0217 [-0.0639, +0.0135] |
| **light_minus_medium** | +0.0456 [+0.0212, +0.0703] * | +0.0742 [+0.0530, +0.0972] * | +0.0047 [-0.0020, +0.0116] | +0.0873 [+0.0532, +0.1146] * |

### `x_kd_mobilenetv4`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6545 [0.6239, 0.6856] | 0.1619 [0.1369, 0.1953] | 0.0486 [0.0409, 0.0582] | 0.2231 [0.1796, 0.2692] |
| light | 0.6548 [0.6410, 0.6690] | 0.2568 [0.2403, 0.2750] | 0.0432 [0.0392, 0.0476] | 0.2447 [0.2245, 0.2643] |
| medium | 0.6263 [0.6092, 0.6445] | 0.1839 [0.1688, 0.2025] | 0.0424 [0.0384, 0.0468] | 0.1915 [0.1684, 0.2139] |
| **dark_minus_light** | -0.0003 [-0.0338, +0.0337] | -0.0949 [-0.1255, -0.0577] * | +0.0055 [-0.0034, +0.0158] | -0.0216 [-0.0685, +0.0279] |
| **dark_minus_medium** | +0.0282 [-0.0083, +0.0649] | -0.0220 [-0.0527, +0.0153] | +0.0062 [-0.0030, +0.0168] | +0.0315 [-0.0190, +0.0821] |
| **light_minus_medium** | +0.0285 [+0.0050, +0.0508] * | +0.0729 [+0.0481, +0.0968] * | +0.0008 [-0.0052, +0.0068] | +0.0531 [+0.0233, +0.0844] * |

### `x_kd_mobilenetv4__domain`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6025 [0.5748, 0.6307] | 0.1249 [0.1086, 0.1469] | 0.0406 [0.0338, 0.0487] | 0.1375 [0.1082, 0.1678] |
| light | 0.6148 [0.6015, 0.6286] | 0.2116 [0.1996, 0.2255] | 0.0385 [0.0350, 0.0426] | 0.1774 [0.1623, 0.1923] |
| medium | 0.5948 [0.5780, 0.6125] | 0.1580 [0.1460, 0.1721] | 0.0373 [0.0331, 0.0420] | 0.1464 [0.1310, 0.1636] |
| **dark_minus_light** | -0.0123 [-0.0434, +0.0196] | -0.0867 [-0.1078, -0.0621] * | +0.0021 [-0.0057, +0.0110] | -0.0399 [-0.0727, -0.0061] * |
| **dark_minus_medium** | +0.0077 [-0.0246, +0.0405] | -0.0331 [-0.0539, -0.0089] * | +0.0033 [-0.0048, +0.0127] | -0.0089 [-0.0426, +0.0239] |
| **light_minus_medium** | +0.0200 [-0.0015, +0.0422] | +0.0536 [+0.0354, +0.0724] * | +0.0012 [-0.0044, +0.0072] | +0.0310 [+0.0083, +0.0532] * |

### `x_teacher_efficientnetv2_m`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6909 [0.6592, 0.7243] | 0.2001 [0.1684, 0.2426] | 0.0505 [0.0417, 0.0614] | 0.2875 [0.2402, 0.3446] |
| light | 0.7049 [0.6904, 0.7191] | 0.3395 [0.3179, 0.3633] | 0.0506 [0.0461, 0.0557] | 0.3377 [0.3172, 0.3608] |
| medium | 0.6791 [0.6616, 0.6979] | 0.2393 [0.2189, 0.2651] | 0.0500 [0.0453, 0.0554] | 0.2658 [0.2396, 0.2934] |
| **dark_minus_light** | -0.0140 [-0.0481, +0.0212] | -0.1394 [-0.1787, -0.0945] * | -0.0000 [-0.0099, +0.0120] | -0.0502 [-0.1017, +0.0111] |
| **dark_minus_medium** | +0.0118 [-0.0258, +0.0496] | -0.0392 [-0.0788, +0.0082] | +0.0005 [-0.0099, +0.0126] | +0.0217 [-0.0321, +0.0848] |
| **light_minus_medium** | +0.0258 [+0.0024, +0.0491] * | +0.1002 [+0.0678, +0.1316] * | +0.0006 [-0.0068, +0.0076] | +0.0720 [+0.0379, +0.1072] * |

### `x_teacher_efficientnetv2_m__domain`

Group sizes (per fold): dark n=2168, light n=7755, medium n=6089

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6916 [0.6598, 0.7236] | 0.2033 [0.1731, 0.2444] | 0.0546 [0.0464, 0.0657] | 0.2625 [0.2206, 0.3135] |
| light | 0.7099 [0.6949, 0.7246] | 0.3453 [0.3242, 0.3682] | 0.0522 [0.0473, 0.0577] | 0.3411 [0.3183, 0.3621] |
| medium | 0.6710 [0.6523, 0.6894] | 0.2371 [0.2169, 0.2603] | 0.0483 [0.0429, 0.0543] | 0.2761 [0.2500, 0.3028] |
| **dark_minus_light** | -0.0183 [-0.0526, +0.0174] | -0.1419 [-0.1799, -0.0981] * | +0.0025 [-0.0072, +0.0142] | -0.0786 [-0.1263, -0.0240] * |
| **dark_minus_medium** | +0.0205 [-0.0165, +0.0592] | -0.0338 [-0.0721, +0.0114] | +0.0063 [-0.0041, +0.0188] | -0.0136 [-0.0653, +0.0459] |
| **light_minus_medium** | +0.0389 [+0.0145, +0.0628] * | +0.1081 [+0.0749, +0.1398] * | +0.0038 [-0.0041, +0.0115] | +0.0650 [+0.0290, +0.1008] * |


## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | dark | -0.0448 [-0.0642, -0.0258] * | -0.0261 [-0.0411, -0.0154] * | -0.0103 [-0.0178, -0.0026] * | -0.0721 [-0.1060, -0.0454] * |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | light | -0.0123 [-0.0204, -0.0037] * | -0.0057 [-0.0132, +0.0026] | -0.0028 [-0.0060, +0.0003] | -0.0161 [-0.0322, +0.0003] |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | medium | -0.0187 [-0.0283, -0.0095] * | -0.0111 [-0.0172, -0.0057] * | -0.0013 [-0.0045, +0.0018] | -0.0502 [-0.0642, -0.0288] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | dark | -0.0520 [-0.0741, -0.0302] * | -0.0370 [-0.0564, -0.0219] * | -0.0081 [-0.0151, -0.0013] * | -0.0856 [-0.1237, -0.0504] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | light | -0.0400 [-0.0491, -0.0307] * | -0.0452 [-0.0547, -0.0354] * | -0.0047 [-0.0078, -0.0018] * | -0.0673 [-0.0841, -0.0510] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | medium | -0.0315 [-0.0420, -0.0214] * | -0.0259 [-0.0350, -0.0182] * | -0.0051 [-0.0081, -0.0021] * | -0.0452 [-0.0619, -0.0265] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | dark | +0.0006 [-0.0185, +0.0193] | +0.0032 [-0.0176, +0.0230] | +0.0041 [-0.0028, +0.0107] | -0.0250 [-0.0646, +0.0135] |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | light | +0.0050 [-0.0024, +0.0124] | +0.0057 [-0.0061, +0.0164] | +0.0016 [-0.0014, +0.0047] | +0.0033 [-0.0133, +0.0176] |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | medium | -0.0081 [-0.0174, +0.0009] | -0.0022 [-0.0130, +0.0086] | -0.0017 [-0.0052, +0.0016] | +0.0103 [-0.0073, +0.0276] |
