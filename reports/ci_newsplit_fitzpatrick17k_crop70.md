# Bootstrap 95% confidence intervals — `.tmp/ci_newsplit/fitzpatrick17k/crop70`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4` | 5 | 0.6485 [0.6336, 0.6639] | 0.6111 [0.5912, 0.6324] | 0.0461 [0.0423, 0.0502] | 0.1942 [0.1725, 0.2191] |
| `x_baseline_mobilenetv4__domain` | 5 | 0.6390 [0.6240, 0.6542] | 0.6071 [0.5883, 0.6274] | 0.0460 [0.0421, 0.0501] | 0.1553 [0.1367, 0.1727] |
| `x_kd_mobilenetv4` | 5 | 0.6586 [0.6452, 0.6723] | 0.6394 [0.6203, 0.6594] | 0.0475 [0.0439, 0.0515] | 0.2329 [0.2127, 0.2534] |
| `x_kd_mobilenetv4__domain` | 5 | 0.6176 [0.6040, 0.6311] | 0.5879 [0.5707, 0.6074] | 0.0411 [0.0374, 0.0450] | 0.1694 [0.1539, 0.1900] |
| `x_teacher_efficientnetv2_m` | 5 | 0.6986 [0.6848, 0.7121] | 0.6873 [0.6690, 0.7066] | 0.0560 [0.0518, 0.0603] | 0.2866 [0.2655, 0.3110] |
| `x_teacher_efficientnetv2_m__domain` | 5 | 0.6826 [0.6683, 0.6971] | 0.6760 [0.6584, 0.6946] | 0.0516 [0.0474, 0.0561] | 0.2858 [0.2654, 0.3057] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | -0.0096 [-0.0173, -0.0022] * | -0.0040 [-0.0123, +0.0046] | -0.0001 [-0.0026, +0.0023] | -0.0389 [-0.0591, -0.0215] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | -0.0410 [-0.0497, -0.0323] * | -0.0515 [-0.0618, -0.0416] * | -0.0064 [-0.0090, -0.0038] * | -0.0634 [-0.0806, -0.0445] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | -0.0160 [-0.0228, -0.0090] * | -0.0113 [-0.0200, -0.0030] * | -0.0044 [-0.0070, -0.0017] * | -0.0007 [-0.0194, +0.0130] |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `x_baseline_mobilenetv4`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6580 [0.6088, 0.7045] | 0.6339 [0.5694, 0.6998] | 0.0522 [0.0397, 0.0661] | 0.2404 [0.1522, 0.3096] |
| light | 0.6645 [0.6435, 0.6848] | 0.6397 [0.6116, 0.6693] | 0.0494 [0.0439, 0.0558] | 0.2018 [0.1672, 0.2343] |
| medium | 0.6227 [0.5968, 0.6474] | 0.5648 [0.5317, 0.6037] | 0.0404 [0.0346, 0.0467] | 0.1760 [0.1390, 0.2182] |
| **dark_minus_light** | -0.0066 [-0.0607, +0.0439] | -0.0058 [-0.0775, +0.0654] | +0.0028 [-0.0112, +0.0178] | +0.0385 [-0.0558, +0.1155] |
| **dark_minus_medium** | +0.0353 [-0.0191, +0.0864] | +0.0690 [-0.0035, +0.1423] | +0.0118 [-0.0021, +0.0275] | +0.0644 [-0.0298, +0.1435] |
| **light_minus_medium** | +0.0419 [+0.0104, +0.0744] * | +0.0748 [+0.0273, +0.1206] * | +0.0090 [+0.0009, +0.0173] * | +0.0259 [-0.0255, +0.0764] |

### `x_baseline_mobilenetv4__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6237 [0.5724, 0.6706] | 0.5961 [0.5334, 0.6616] | 0.0465 [0.0350, 0.0594] | 0.1356 [0.0928, 0.2350] |
| light | 0.6614 [0.6405, 0.6826] | 0.6462 [0.6193, 0.6762] | 0.0487 [0.0431, 0.0550] | 0.1774 [0.1547, 0.2396] |
| medium | 0.6149 [0.5900, 0.6399] | 0.5648 [0.5316, 0.6021] | 0.0428 [0.0371, 0.0491] | 0.1445 [0.1165, 0.1725] |
| **dark_minus_light** | -0.0377 [-0.0920, +0.0128] | -0.0501 [-0.1196, +0.0199] | -0.0022 [-0.0149, +0.0117] | -0.0418 [-0.1074, +0.0573] |
| **dark_minus_medium** | +0.0088 [-0.0499, +0.0627] | +0.0313 [-0.0414, +0.1050] | +0.0037 [-0.0093, +0.0183] | -0.0089 [-0.0595, +0.0957] |
| **light_minus_medium** | +0.0465 [+0.0153, +0.0795] * | +0.0815 [+0.0373, +0.1266] * | +0.0059 [-0.0024, +0.0146] | +0.0329 [-0.0043, +0.1001] |

### `x_kd_mobilenetv4`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6690 [0.6230, 0.7108] | 0.6663 [0.6070, 0.7244] | 0.0537 [0.0425, 0.0655] | 0.2644 [0.1989, 0.3290] |
| light | 0.6720 [0.6532, 0.6916] | 0.6700 [0.6437, 0.6975] | 0.0489 [0.0437, 0.0549] | 0.2514 [0.2210, 0.2812] |
| medium | 0.6354 [0.6124, 0.6585] | 0.5871 [0.5555, 0.6249] | 0.0445 [0.0389, 0.0505] | 0.1942 [0.1621, 0.2284] |
| **dark_minus_light** | -0.0030 [-0.0548, +0.0414] | -0.0036 [-0.0691, +0.0604] | +0.0048 [-0.0076, +0.0176] | +0.0130 [-0.0614, +0.0837] |
| **dark_minus_medium** | +0.0336 [-0.0174, +0.0820] | +0.0792 [+0.0088, +0.1455] * | +0.0092 [-0.0036, +0.0225] | +0.0702 [-0.0049, +0.1428] |
| **light_minus_medium** | +0.0366 [+0.0086, +0.0667] * | +0.0829 [+0.0398, +0.1254] * | +0.0044 [-0.0032, +0.0122] | +0.0572 [+0.0146, +0.1011] * |

### `x_kd_mobilenetv4__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6068 [0.5635, 0.6466] | 0.5786 [0.5238, 0.6402] | 0.0439 [0.0345, 0.0551] | 0.1413 [0.0995, 0.1969] |
| light | 0.6350 [0.6161, 0.6546] | 0.6257 [0.6007, 0.6532] | 0.0433 [0.0383, 0.0487] | 0.2007 [0.1772, 0.2262] |
| medium | 0.5948 [0.5716, 0.6177] | 0.5401 [0.5107, 0.5743] | 0.0376 [0.0321, 0.0438] | 0.1408 [0.1173, 0.1716] |
| **dark_minus_light** | -0.0282 [-0.0747, +0.0167] | -0.0472 [-0.1093, +0.0170] | +0.0005 [-0.0099, +0.0131] | -0.0593 [-0.1092, +0.0020] |
| **dark_minus_medium** | +0.0121 [-0.0359, +0.0586] | +0.0385 [-0.0291, +0.1043] | +0.0063 [-0.0048, +0.0189] | +0.0005 [-0.0502, +0.0613] |
| **light_minus_medium** | +0.0402 [+0.0107, +0.0696] * | +0.0856 [+0.0413, +0.1262] * | +0.0058 [-0.0021, +0.0133] | +0.0599 [+0.0235, +0.0943] * |

### `x_teacher_efficientnetv2_m`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6968 [0.6534, 0.7393] | 0.6994 [0.6397, 0.7568] | 0.0560 [0.0442, 0.0694] | 0.3250 [0.2402, 0.3953] |
| light | 0.7103 [0.6918, 0.7297] | 0.7154 [0.6902, 0.7420] | 0.0572 [0.0512, 0.0636] | 0.3151 [0.2796, 0.3451] |
| medium | 0.6804 [0.6575, 0.7030] | 0.6398 [0.6072, 0.6740] | 0.0548 [0.0485, 0.0616] | 0.2531 [0.2167, 0.2906] |
| **dark_minus_light** | -0.0135 [-0.0632, +0.0320] | -0.0160 [-0.0814, +0.0470] | -0.0012 [-0.0149, +0.0138] | +0.0099 [-0.0784, +0.0899] |
| **dark_minus_medium** | +0.0164 [-0.0335, +0.0647] | +0.0596 [-0.0103, +0.1244] | +0.0012 [-0.0122, +0.0170] | +0.0719 [-0.0196, +0.1505] |
| **light_minus_medium** | +0.0299 [+0.0012, +0.0604] * | +0.0756 [+0.0338, +0.1179] * | +0.0024 [-0.0064, +0.0116] | +0.0620 [+0.0128, +0.1081] * |

### `x_teacher_efficientnetv2_m__domain`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| dark | 0.6790 [0.6326, 0.7252] | 0.6760 [0.6175, 0.7342] | 0.0583 [0.0456, 0.0727] | 0.2692 [0.2047, 0.3491] |
| light | 0.6963 [0.6776, 0.7153] | 0.7033 [0.6784, 0.7291] | 0.0522 [0.0465, 0.0586] | 0.3006 [0.2724, 0.3349] |
| medium | 0.6613 [0.6381, 0.6845] | 0.6327 [0.6009, 0.6666] | 0.0493 [0.0427, 0.0562] | 0.2552 [0.2241, 0.2871] |
| **dark_minus_light** | -0.0172 [-0.0686, +0.0321] | -0.0274 [-0.0914, +0.0343] | +0.0060 [-0.0078, +0.0211] | -0.0314 [-0.1036, +0.0536] |
| **dark_minus_medium** | +0.0178 [-0.0331, +0.0716] | +0.0433 [-0.0225, +0.1092] | +0.0090 [-0.0060, +0.0255] | +0.0140 [-0.0593, +0.1018] |
| **light_minus_medium** | +0.0350 [+0.0056, +0.0651] * | +0.0707 [+0.0306, +0.1127] * | +0.0030 [-0.0060, +0.0120] | +0.0454 [+0.0036, +0.0902] * |


## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | dark | -0.0343 [-0.0608, -0.0089] * | -0.0378 [-0.0660, -0.0114] * | -0.0057 [-0.0147, +0.0026] | -0.1048 [-0.1427, -0.0154] * |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | light | -0.0031 [-0.0131, +0.0065] | +0.0066 [-0.0044, +0.0175] | -0.0007 [-0.0045, +0.0028] | -0.0244 [-0.0450, +0.0164] |
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | medium | -0.0077 [-0.0199, +0.0046] | -0.0001 [-0.0132, +0.0132] | +0.0023 [-0.0014, +0.0063] | -0.0314 [-0.0604, -0.0034] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | dark | -0.0622 [-0.0933, -0.0323] * | -0.0877 [-0.1200, -0.0536] * | -0.0099 [-0.0195, -0.0008] * | -0.1231 [-0.1746, -0.0660] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | light | -0.0370 [-0.0489, -0.0249] * | -0.0442 [-0.0578, -0.0305] * | -0.0056 [-0.0095, -0.0019] * | -0.0507 [-0.0753, -0.0256] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | medium | -0.0406 [-0.0542, -0.0272] * | -0.0470 [-0.0634, -0.0304] * | -0.0070 [-0.0109, -0.0031] * | -0.0534 [-0.0820, -0.0222] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | dark | -0.0177 [-0.0396, +0.0034] | -0.0235 [-0.0479, +0.0018] | +0.0023 [-0.0054, +0.0097] | -0.0558 [-0.0984, +0.0101] |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | light | -0.0141 [-0.0238, -0.0041] * | -0.0121 [-0.0233, -0.0011] * | -0.0050 [-0.0087, -0.0012] * | -0.0146 [-0.0338, +0.0152] |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | medium | -0.0192 [-0.0304, -0.0086] * | -0.0072 [-0.0207, +0.0068] | -0.0055 [-0.0099, -0.0014] * | +0.0021 [-0.0216, +0.0301] |
