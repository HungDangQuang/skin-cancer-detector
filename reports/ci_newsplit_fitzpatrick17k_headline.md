# Bootstrap 95% confidence intervals — `.tmp/ci_newsplit/fitzpatrick17k/headline`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4` | 5 | 0.6335 [0.6185, 0.6488] | 0.5947 [0.5757, 0.6160] | 0.0437 [0.0401, 0.0478] | 0.1695 [0.1507, 0.1929] |
| `x_baseline_mobilenetv4__domain` | 5 | 0.6168 [0.6019, 0.6316] | 0.5849 [0.5663, 0.6049] | 0.0400 [0.0363, 0.0438] | 0.1341 [0.1193, 0.1548] |
| `x_kd_mobilenetv4` | 5 | 0.6432 [0.6298, 0.6574] | 0.6223 [0.6033, 0.6427] | 0.0437 [0.0402, 0.0474] | 0.2160 [0.1964, 0.2357] |
| `x_kd_mobilenetv4__domain` | 5 | 0.6065 [0.5936, 0.6197] | 0.5788 [0.5616, 0.5978] | 0.0373 [0.0339, 0.0408] | 0.1666 [0.1502, 0.1813] |
| `x_teacher_efficientnetv2_m` | 5 | 0.6848 [0.6714, 0.6982] | 0.6721 [0.6530, 0.6917] | 0.0514 [0.0476, 0.0554] | 0.2737 [0.2523, 0.2917] |
| `x_teacher_efficientnetv2_m__domain` | 5 | 0.6738 [0.6594, 0.6876] | 0.6669 [0.6490, 0.6859] | 0.0487 [0.0446, 0.0530] | 0.2707 [0.2500, 0.2921] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | -0.0167 [-0.0249, -0.0087] * | -0.0098 [-0.0185, -0.0005] * | -0.0037 [-0.0064, -0.0013] * | -0.0355 [-0.0522, -0.0158] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | -0.0367 [-0.0456, -0.0279] * | -0.0436 [-0.0538, -0.0332] * | -0.0064 [-0.0089, -0.0040] * | -0.0494 [-0.0680, -0.0336] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | -0.0111 [-0.0183, -0.0035] * | -0.0053 [-0.0145, +0.0035] | -0.0027 [-0.0052, -0.0003] * | -0.0030 [-0.0182, +0.0154] |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `x_baseline_mobilenetv4`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6355 [0.5878, 0.6804] | 0.6076 [0.5463, 0.6738] | 0.0495 [0.0384, 0.0619] | 0.1769 [0.1155, 0.2550] |
| light | 0.6537 [0.6335, 0.6742] | 0.6279 [0.6001, 0.6569] | 0.0473 [0.0421, 0.0534] | 0.1859 [0.1526, 0.2238] |
| medium | 0.6024 [0.5764, 0.6271] | 0.5441 [0.5126, 0.5824] | 0.0373 [0.0314, 0.0434] | 0.1493 [0.1220, 0.1823] |
| **dark_minus_light** | -0.0183 [-0.0704, +0.0294] | -0.0203 [-0.0911, +0.0514] | +0.0022 [-0.0103, +0.0155] | -0.0090 [-0.0838, +0.0759] |
| **dark_minus_medium** | +0.0330 [-0.0205, +0.0847] | +0.0634 [-0.0088, +0.1372] | +0.0122 [-0.0002, +0.0263] | +0.0276 [-0.0409, +0.1097] |
| **light_minus_medium** | +0.0513 [+0.0199, +0.0837] * | +0.0838 [+0.0357, +0.1286] * | +0.0100 [+0.0022, +0.0182] * | +0.0367 [-0.0082, +0.0834] |

### `x_baseline_mobilenetv4__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.5956 [0.5448, 0.6434] | 0.5679 [0.5057, 0.6349] | 0.0409 [0.0300, 0.0534] | 0.0971 [0.0613, 0.1628] |
| light | 0.6405 [0.6204, 0.6615] | 0.6281 [0.6013, 0.6577] | 0.0429 [0.0378, 0.0486] | 0.1670 [0.1414, 0.2261] |
| medium | 0.5914 [0.5662, 0.6161] | 0.5376 [0.5054, 0.5736] | 0.0365 [0.0312, 0.0425] | 0.1184 [0.0974, 0.1469] |
| **dark_minus_light** | -0.0449 [-0.1005, +0.0068] | -0.0603 [-0.1268, +0.0102] | -0.0020 [-0.0141, +0.0109] | -0.0699 [-0.1429, -0.0034] * |
| **dark_minus_medium** | +0.0043 [-0.0560, +0.0601] | +0.0303 [-0.0423, +0.1047] | +0.0044 [-0.0079, +0.0190] | -0.0212 [-0.0676, +0.0482] |
| **light_minus_medium** | +0.0491 [+0.0172, +0.0819] * | +0.0905 [+0.0458, +0.1368] * | +0.0064 [-0.0012, +0.0143] | +0.0487 [+0.0115, +0.1134] * |

### `x_kd_mobilenetv4`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6479 [0.6040, 0.6889] | 0.6464 [0.5867, 0.7038] | 0.0471 [0.0370, 0.0583] | 0.2250 [0.1683, 0.2951] |
| light | 0.6573 [0.6389, 0.6768] | 0.6536 [0.6272, 0.6808] | 0.0453 [0.0404, 0.0509] | 0.2333 [0.2033, 0.2597] |
| medium | 0.6202 [0.5973, 0.6431] | 0.5692 [0.5375, 0.6048] | 0.0413 [0.0358, 0.0470] | 0.1807 [0.1526, 0.2124] |
| **dark_minus_light** | -0.0094 [-0.0593, +0.0343] | -0.0073 [-0.0729, +0.0545] | +0.0018 [-0.0099, +0.0140] | -0.0083 [-0.0714, +0.0711] |
| **dark_minus_medium** | +0.0277 [-0.0225, +0.0755] | +0.0771 [+0.0061, +0.1426] * | +0.0059 [-0.0060, +0.0185] | +0.0443 [-0.0218, +0.1202] |
| **light_minus_medium** | +0.0371 [+0.0088, +0.0668] * | +0.0844 [+0.0404, +0.1259] * | +0.0041 [-0.0034, +0.0117] | +0.0526 [+0.0106, +0.0921] * |

### `x_kd_mobilenetv4__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.5774 [0.5356, 0.6174] | 0.5493 [0.4964, 0.6110] | 0.0395 [0.0298, 0.0504] | 0.1173 [0.0832, 0.1575] |
| light | 0.6256 [0.6071, 0.6444] | 0.6182 [0.5931, 0.6457] | 0.0386 [0.0341, 0.0435] | 0.1901 [0.1658, 0.2200] |
| medium | 0.5851 [0.5610, 0.6079] | 0.5329 [0.5034, 0.5670] | 0.0351 [0.0298, 0.0410] | 0.1477 [0.1221, 0.1720] |
| **dark_minus_light** | -0.0481 [-0.0947, -0.0030] * | -0.0690 [-0.1290, -0.0034] * | +0.0009 [-0.0096, +0.0127] | -0.0728 [-0.1191, -0.0261] * |
| **dark_minus_medium** | -0.0077 [-0.0557, +0.0399] | +0.0164 [-0.0483, +0.0832] | +0.0044 [-0.0068, +0.0170] | -0.0304 [-0.0725, +0.0184] |
| **light_minus_medium** | +0.0404 [+0.0109, +0.0700] * | +0.0853 [+0.0424, +0.1264] * | +0.0035 [-0.0038, +0.0104] | +0.0424 [+0.0106, +0.0819] * |

### `x_teacher_efficientnetv2_m`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6671 [0.6208, 0.7109] | 0.6727 [0.6099, 0.7353] | 0.0436 [0.0331, 0.0562] | 0.2904 [0.2091, 0.3567] |
| light | 0.7009 [0.6830, 0.7201] | 0.7055 [0.6795, 0.7311] | 0.0538 [0.0482, 0.0599] | 0.3054 [0.2738, 0.3362] |
| medium | 0.6642 [0.6413, 0.6865] | 0.6183 [0.5841, 0.6528] | 0.0507 [0.0447, 0.0571] | 0.2248 [0.1916, 0.2549] |
| **dark_minus_light** | -0.0338 [-0.0850, +0.0117] | -0.0328 [-0.1028, +0.0327] | -0.0102 [-0.0223, +0.0037] | -0.0151 [-0.1035, +0.0578] |
| **dark_minus_medium** | +0.0029 [-0.0471, +0.0534] | +0.0544 [-0.0171, +0.1256] | -0.0071 [-0.0194, +0.0067] | +0.0655 [-0.0204, +0.1391] |
| **light_minus_medium** | +0.0367 [+0.0082, +0.0677] * | +0.0872 [+0.0433, +0.1309] * | +0.0031 [-0.0050, +0.0115] | +0.0806 [+0.0395, +0.1257] * |

### `x_teacher_efficientnetv2_m__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6566 [0.6074, 0.7036] | 0.6442 [0.5841, 0.7066] | 0.0542 [0.0426, 0.0670] | 0.2163 [0.1707, 0.2793] |
| light | 0.6929 [0.6738, 0.7121] | 0.7008 [0.6757, 0.7259] | 0.0508 [0.0451, 0.0570] | 0.2917 [0.2603, 0.3230] |
| medium | 0.6479 [0.6233, 0.6728] | 0.6152 [0.5835, 0.6500] | 0.0454 [0.0393, 0.0522] | 0.2425 [0.2099, 0.2747] |
| **dark_minus_light** | -0.0363 [-0.0892, +0.0124] | -0.0566 [-0.1228, +0.0089] | +0.0034 [-0.0094, +0.0177] | -0.0754 [-0.1297, -0.0070] * |
| **dark_minus_medium** | +0.0087 [-0.0446, +0.0625] | +0.0290 [-0.0393, +0.1019] | +0.0088 [-0.0048, +0.0238] | -0.0262 [-0.0842, +0.0447] |
| **light_minus_medium** | +0.0450 [+0.0147, +0.0769] * | +0.0856 [+0.0440, +0.1282] * | +0.0053 [-0.0032, +0.0140] | +0.0492 [+0.0042, +0.0952] * |


## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | dark | -0.0398 [-0.0689, -0.0100] * | -0.0397 [-0.0708, -0.0075] * | -0.0086 [-0.0170, -0.0001] * | -0.0798 [-0.1327, -0.0214] * |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | light | -0.0132 [-0.0243, -0.0024] * | +0.0002 [-0.0120, +0.0120] | -0.0044 [-0.0081, -0.0009] * | -0.0189 [-0.0397, +0.0270] |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | medium | -0.0111 [-0.0236, +0.0019] | -0.0065 [-0.0195, +0.0062] | -0.0008 [-0.0043, +0.0029] | -0.0309 [-0.0523, -0.0090] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | dark | -0.0705 [-0.1018, -0.0407] * | -0.0971 [-0.1242, -0.0642] * | -0.0076 [-0.0161, +0.0003] | -0.1077 [-0.1640, -0.0610] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | light | -0.0317 [-0.0447, -0.0196] * | -0.0354 [-0.0500, -0.0213] * | -0.0067 [-0.0107, -0.0032] * | -0.0432 [-0.0642, -0.0130] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | medium | -0.0350 [-0.0488, -0.0216] * | -0.0363 [-0.0524, -0.0203] * | -0.0062 [-0.0099, -0.0023] * | -0.0330 [-0.0593, -0.0081] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | dark | -0.0106 [-0.0366, +0.0134] | -0.0285 [-0.0570, -0.0007] * | +0.0106 [+0.0030, +0.0179] * | -0.0740 [-0.1194, -0.0062] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | light | -0.0080 [-0.0177, +0.0016] | -0.0047 [-0.0160, +0.0069] | -0.0030 [-0.0065, +0.0007] | -0.0137 [-0.0372, +0.0117] |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | medium | -0.0163 [-0.0275, -0.0049] * | -0.0031 [-0.0163, +0.0107] | -0.0053 [-0.0091, -0.0015] * | +0.0177 [-0.0044, +0.0430] |
