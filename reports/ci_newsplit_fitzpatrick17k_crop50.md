# Bootstrap 95% confidence intervals — `.tmp/ci_newsplit/fitzpatrick17k/crop50`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4` | 5 | 0.6469 [0.6313, 0.6619] | 0.6190 [0.5995, 0.6400] | 0.0439 [0.0399, 0.0480] | 0.2133 [0.1901, 0.2377] |
| `x_baseline_mobilenetv4__domain` | 5 | 0.6509 [0.6357, 0.6659] | 0.6279 [0.6086, 0.6488] | 0.0468 [0.0427, 0.0510] | 0.1807 [0.1606, 0.2345] |
| `x_kd_mobilenetv4` | 5 | 0.6597 [0.6461, 0.6734] | 0.6482 [0.6294, 0.6682] | 0.0476 [0.0437, 0.0516] | 0.2486 [0.2279, 0.2672] |
| `x_kd_mobilenetv4__domain` | 5 | 0.6249 [0.6107, 0.6389] | 0.5918 [0.5741, 0.6109] | 0.0443 [0.0403, 0.0483] | 0.1632 [0.1490, 0.1787] |
| `x_teacher_efficientnetv2_m` | 5 | 0.6975 [0.6833, 0.7114] | 0.6912 [0.6734, 0.7110] | 0.0530 [0.0489, 0.0572] | 0.3023 [0.2797, 0.3237] |
| `x_teacher_efficientnetv2_m__domain` | 5 | 0.6784 [0.6646, 0.6924] | 0.6678 [0.6501, 0.6874] | 0.0508 [0.0466, 0.0555] | 0.2736 [0.2496, 0.2945] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | +0.0040 [-0.0030, +0.0103] | +0.0089 [+0.0008, +0.0167] * | +0.0029 [+0.0006, +0.0051] * | -0.0326 [-0.0507, +0.0092] |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | -0.0348 [-0.0431, -0.0267] * | -0.0564 [-0.0658, -0.0466] * | -0.0033 [-0.0059, -0.0007] * | -0.0854 [-0.0996, -0.0686] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | -0.0191 [-0.0257, -0.0124] * | -0.0234 [-0.0315, -0.0155] * | -0.0021 [-0.0049, +0.0006] | -0.0287 [-0.0446, -0.0121] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `x_baseline_mobilenetv4`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6608 [0.6113, 0.7073] | 0.6554 [0.5910, 0.7198] | 0.0504 [0.0376, 0.0640] | 0.2625 [0.1991, 0.3321] |
| light | 0.6623 [0.6412, 0.6824] | 0.6452 [0.6179, 0.6755] | 0.0469 [0.0413, 0.0534] | 0.2099 [0.1753, 0.2497] |
| medium | 0.6242 [0.5985, 0.6492] | 0.5770 [0.5433, 0.6169] | 0.0384 [0.0326, 0.0448] | 0.2100 [0.1692, 0.2495] |
| **dark_minus_light** | -0.0014 [-0.0551, +0.0486] | +0.0103 [-0.0602, +0.0807] | +0.0035 [-0.0109, +0.0180] | +0.0526 [-0.0215, +0.1288] |
| **dark_minus_medium** | +0.0366 [-0.0181, +0.0921] | +0.0785 [+0.0026, +0.1519] * | +0.0119 [-0.0022, +0.0275] | +0.0525 [-0.0188, +0.1321] |
| **light_minus_medium** | +0.0380 [+0.0066, +0.0717] * | +0.0682 [+0.0214, +0.1138] * | +0.0085 [+0.0001, +0.0173] * | -0.0002 [-0.0499, +0.0584] |

### `x_baseline_mobilenetv4__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6460 [0.5980, 0.6943] | 0.6268 [0.5652, 0.6913] | 0.0498 [0.0373, 0.0643] | 0.2106 [0.1239, 0.2800] |
| light | 0.6698 [0.6483, 0.6907] | 0.6619 [0.6345, 0.6916] | 0.0493 [0.0437, 0.0559] | 0.2052 [0.1773, 0.2750] |
| medium | 0.6305 [0.6051, 0.6561] | 0.5886 [0.5547, 0.6267] | 0.0437 [0.0377, 0.0507] | 0.1686 [0.1423, 0.2015] |
| **dark_minus_light** | -0.0238 [-0.0789, +0.0267] | -0.0352 [-0.1037, +0.0339] | +0.0005 [-0.0133, +0.0153] | +0.0054 [-0.1159, +0.0734] |
| **dark_minus_medium** | +0.0155 [-0.0416, +0.0693] | +0.0381 [-0.0337, +0.1110] | +0.0061 [-0.0079, +0.0216] | +0.0420 [-0.0516, +0.1170] |
| **light_minus_medium** | +0.0393 [+0.0073, +0.0722] * | +0.0733 [+0.0287, +0.1184] * | +0.0056 [-0.0032, +0.0143] | +0.0366 [-0.0040, +0.1153] |

### `x_kd_mobilenetv4`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6810 [0.6355, 0.7266] | 0.6827 [0.6241, 0.7398] | 0.0549 [0.0423, 0.0680] | 0.2731 [0.2057, 0.3406] |
| light | 0.6711 [0.6514, 0.6909] | 0.6735 [0.6478, 0.7009] | 0.0488 [0.0435, 0.0550] | 0.2611 [0.2321, 0.2897] |
| medium | 0.6389 [0.6156, 0.6623] | 0.6054 [0.5731, 0.6408] | 0.0447 [0.0390, 0.0508] | 0.2338 [0.1957, 0.2604] |
| **dark_minus_light** | +0.0099 [-0.0397, +0.0578] | +0.0092 [-0.0565, +0.0723] | +0.0061 [-0.0079, +0.0204] | +0.0120 [-0.0635, +0.0842] |
| **dark_minus_medium** | +0.0422 [-0.0078, +0.0930] | +0.0772 [+0.0086, +0.1412] * | +0.0102 [-0.0038, +0.0250] | +0.0393 [-0.0295, +0.1182] |
| **light_minus_medium** | +0.0323 [+0.0037, +0.0633] * | +0.0681 [+0.0254, +0.1106] * | +0.0042 [-0.0041, +0.0123] | +0.0273 [-0.0096, +0.0772] |

### `x_kd_mobilenetv4__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6198 [0.5751, 0.6630] | 0.5906 [0.5339, 0.6538] | 0.0485 [0.0372, 0.0614] | 0.1385 [0.1046, 0.1909] |
| light | 0.6375 [0.6179, 0.6570] | 0.6248 [0.5997, 0.6529] | 0.0462 [0.0408, 0.0519] | 0.1853 [0.1622, 0.2082] |
| medium | 0.6086 [0.5845, 0.6324] | 0.5502 [0.5203, 0.5847] | 0.0410 [0.0349, 0.0477] | 0.1517 [0.1274, 0.1758] |
| **dark_minus_light** | -0.0177 [-0.0650, +0.0300] | -0.0341 [-0.0958, +0.0329] | +0.0023 [-0.0100, +0.0160] | -0.0468 [-0.0875, +0.0121] |
| **dark_minus_medium** | +0.0113 [-0.0398, +0.0615] | +0.0404 [-0.0279, +0.1065] | +0.0075 [-0.0055, +0.0217] | -0.0132 [-0.0537, +0.0480] |
| **light_minus_medium** | +0.0290 [-0.0002, +0.0592] | +0.0746 [+0.0320, +0.1162] * | +0.0052 [-0.0029, +0.0138] | +0.0336 [+0.0013, +0.0679] * |

### `x_teacher_efficientnetv2_m`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.7068 [0.6634, 0.7517] | 0.7118 [0.6542, 0.7666] | 0.0585 [0.0456, 0.0733] | 0.3202 [0.2542, 0.3980] |
| light | 0.7071 [0.6880, 0.7264] | 0.7146 [0.6893, 0.7415] | 0.0540 [0.0480, 0.0605] | 0.3172 [0.2854, 0.3529] |
| medium | 0.6810 [0.6577, 0.7047] | 0.6522 [0.6199, 0.6862] | 0.0506 [0.0443, 0.0575] | 0.2737 [0.2387, 0.3114] |
| **dark_minus_light** | -0.0002 [-0.0505, +0.0473] | -0.0027 [-0.0662, +0.0573] | +0.0045 [-0.0100, +0.0199] | +0.0030 [-0.0749, +0.0859] |
| **dark_minus_medium** | +0.0258 [-0.0263, +0.0764] | +0.0596 [-0.0080, +0.1243] | +0.0079 [-0.0068, +0.0243] | +0.0465 [-0.0320, +0.1303] |
| **light_minus_medium** | +0.0260 [-0.0035, +0.0565] | +0.0623 [+0.0206, +0.1063] * | +0.0034 [-0.0058, +0.0123] | +0.0434 [-0.0049, +0.0947] |

### `x_teacher_efficientnetv2_m__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6893 [0.6428, 0.7359] | 0.6843 [0.6272, 0.7431] | 0.0605 [0.0471, 0.0756] | 0.2817 [0.2219, 0.3470] |
| light | 0.6874 [0.6681, 0.7077] | 0.6896 [0.6642, 0.7166] | 0.0515 [0.0454, 0.0580] | 0.2812 [0.2507, 0.3150] |
| medium | 0.6614 [0.6368, 0.6844] | 0.6324 [0.6012, 0.6662] | 0.0479 [0.0415, 0.0550] | 0.2539 [0.2202, 0.2884] |
| **dark_minus_light** | +0.0019 [-0.0476, +0.0504] | -0.0053 [-0.0669, +0.0559] | +0.0090 [-0.0056, +0.0251] | +0.0006 [-0.0692, +0.0697] |
| **dark_minus_medium** | +0.0279 [-0.0238, +0.0799] | +0.0519 [-0.0126, +0.1172] | +0.0126 [-0.0031, +0.0291] | +0.0278 [-0.0428, +0.1039] |
| **light_minus_medium** | +0.0260 [-0.0025, +0.0569] | +0.0572 [+0.0165, +0.1002] * | +0.0036 [-0.0059, +0.0127] | +0.0273 [-0.0186, +0.0760] |


## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | dark | -0.0148 [-0.0382, +0.0081] | -0.0287 [-0.0546, -0.0024] * | -0.0006 [-0.0082, +0.0071] | -0.0519 [-0.1228, -0.0038] * |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | light | +0.0076 [-0.0010, +0.0158] | +0.0167 [+0.0063, +0.0267] * | +0.0024 [-0.0007, +0.0056] | -0.0047 [-0.0240, +0.0484] |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | medium | +0.0063 [-0.0050, +0.0176] | +0.0117 [-0.0017, +0.0255] | +0.0053 [+0.0017, +0.0088] * | -0.0415 [-0.0678, -0.0086] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | dark | -0.0612 [-0.0916, -0.0309] * | -0.0921 [-0.1228, -0.0572] * | -0.0064 [-0.0156, +0.0027] | -0.1346 [-0.1812, -0.0750] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | light | -0.0336 [-0.0446, -0.0224] * | -0.0487 [-0.0613, -0.0356] * | -0.0026 [-0.0061, +0.0008] | -0.0758 [-0.0979, -0.0554] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | medium | -0.0303 [-0.0439, -0.0175] * | -0.0552 [-0.0710, -0.0383] * | -0.0037 [-0.0075, +0.0002] | -0.0822 [-0.1056, -0.0497] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | dark | -0.0175 [-0.0394, +0.0036] | -0.0275 [-0.0499, -0.0051] * | +0.0020 [-0.0066, +0.0103] | -0.0385 [-0.0899, +0.0057] |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | light | -0.0196 [-0.0294, -0.0095] * | -0.0250 [-0.0362, -0.0144] * | -0.0025 [-0.0065, +0.0012] | -0.0360 [-0.0580, -0.0121] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | medium | -0.0196 [-0.0315, -0.0083] * | -0.0198 [-0.0336, -0.0059] * | -0.0027 [-0.0074, +0.0018] | -0.0198 [-0.0442, +0.0060] |
