# Bootstrap 95% confidence intervals — `experiments/runs`

B = 2000 replicates, seed 42, 62040 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_efficientformerv2_s2` | 5 | 0.9804 [0.9715, 0.9877] | 0.6283 [0.5665, 0.6838] | 0.1812 [0.1726, 0.1884] | 0.9452 [0.9183, 0.9682] |
| `baseline_efficientformerv2_s2__train_isic_only` | 5 | 0.9276 [0.9156, 0.9388] | 0.0803 [0.0652, 0.1034] | 0.1499 [0.1412, 0.1587] | 0.8116 [0.7768, 0.8456] |
| `baseline_fastvit_sa12` | 5 | 0.9817 [0.9731, 0.9885] | 0.6082 [0.5476, 0.6684] | 0.1825 [0.1743, 0.1893] | 0.9502 [0.9250, 0.9722] |
| `baseline_fastvit_sa12__train_isic_only` | 5 | 0.9448 [0.9335, 0.9554] | 0.1075 [0.0890, 0.1356] | 0.1589 [0.1494, 0.1682] | 0.8647 [0.8289, 0.8979] |
| `baseline_mobilenetv4_conv_medium` | 5 | 0.9790 [0.9695, 0.9868] | 0.6101 [0.5502, 0.6699] | 0.1798 [0.1706, 0.1874] | 0.9485 [0.9240, 0.9697] |
| `baseline_mobilenetv4_conv_medium__train_isic_only` | 5 | 0.9383 [0.9269, 0.9485] | 0.1014 [0.0834, 0.1267] | 0.1558 [0.1475, 0.1641] | 0.8249 [0.7885, 0.8600] |
| `baseline_repvit_m1_0` | 5 | 0.9709 [0.9579, 0.9822] | 0.5365 [0.4802, 0.6050] | 0.1718 [0.1591, 0.1829] | 0.9270 [0.8961, 0.9562] |
| `baseline_repvit_m1_0__train_isic_only` | 5 | 0.9074 [0.8910, 0.9228] | 0.0825 [0.0656, 0.1067] | 0.1347 [0.1226, 0.1468] | 0.7527 [0.7115, 0.7911] |
| `kd_convnextv2_base_to_efficientformerv2_s2` | 5 | 0.9833 [0.9759, 0.9894] | 0.6434 [0.5840, 0.7028] | 0.1839 [0.1770, 0.1899] | 0.9485 [0.9226, 0.9711] |
| `kd_convnextv2_base_to_fastvit_sa12` | 5 | 0.9836 [0.9759, 0.9899] | 0.6427 [0.5825, 0.7039] | 0.1842 [0.1767, 0.1904] | 0.9535 [0.9274, 0.9765] |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | 5 | 0.9828 [0.9750, 0.9891] | 0.6351 [0.5765, 0.6946] | 0.1835 [0.1759, 0.1897] | 0.9510 [0.9262, 0.9723] |
| `kd_convnextv2_base_to_repvit_m1_0` | 5 | 0.9797 [0.9700, 0.9879] | 0.5814 [0.5246, 0.6456] | 0.1806 [0.1710, 0.1886] | 0.9535 [0.9283, 0.9758] |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | 5 | 0.9841 [0.9771, 0.9900] | 0.6220 [0.5627, 0.6800] | 0.1849 [0.1780, 0.1907] | 0.9544 [0.9292, 0.9762] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | 5 | 0.9846 [0.9775, 0.9905] | 0.6209 [0.5613, 0.6805] | 0.1853 [0.1785, 0.1912] | 0.9577 [0.9357, 0.9787] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.9852 [0.9786, 0.9905] | 0.6056 [0.5453, 0.6681] | 0.1859 [0.1797, 0.1911] | 0.9568 [0.9333, 0.9770] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio10` | 5 | 0.9817 [0.9737, 0.9884] | 0.5486 [0.4926, 0.6103] | 0.1826 [0.1748, 0.1892] | 0.9510 [0.9261, 0.9732] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio3` | 5 | 0.9844 [0.9774, 0.9901] | 0.6152 [0.5549, 0.6753] | 0.1852 [0.1783, 0.1907] | 0.9577 [0.9339, 0.9776] |
| `kd_efficientnetv2_m_to_repvit_m1_0` | 5 | 0.9823 [0.9741, 0.9888] | 0.5537 [0.4914, 0.6180] | 0.1832 [0.1753, 0.1896] | 0.9477 [0.9212, 0.9699] |
| `kd_maxvit_base_to_efficientformerv2_s2` | 5 | 0.9837 [0.9755, 0.9902] | 0.6435 [0.5828, 0.7034] | 0.1843 [0.1763, 0.1908] | 0.9552 [0.9319, 0.9750] |
| `kd_maxvit_base_to_fastvit_sa12` | 5 | 0.9845 [0.9769, 0.9904] | 0.6510 [0.5880, 0.7104] | 0.1851 [0.1778, 0.1909] | 0.9544 [0.9305, 0.9741] |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | 5 | 0.9830 [0.9746, 0.9896] | 0.6254 [0.5679, 0.6870] | 0.1837 [0.1755, 0.1903] | 0.9510 [0.9254, 0.9731] |
| `kd_maxvit_base_to_repvit_m1_0` | 5 | 0.9824 [0.9741, 0.9890] | 0.6073 [0.5442, 0.6695] | 0.1832 [0.1752, 0.1897] | 0.9485 [0.9235, 0.9710] |
| `teacher/convnextv2_base` | 5 | 0.9816 [0.9736, 0.9887] | 0.6506 [0.5912, 0.7094] | 0.1822 [0.1744, 0.1892] | 0.9485 [0.9236, 0.9706] |
| `teacher/efficientnetv2_m` | 5 | 0.9820 [0.9744, 0.9885] | 0.6298 [0.5701, 0.6898] | 0.1826 [0.1753, 0.1890] | 0.9535 [0.9287, 0.9732] |
| `teacher/maxvit_base` | 5 | 0.9824 [0.9745, 0.9887] | 0.6566 [0.5950, 0.7152] | 0.1830 [0.1754, 0.1893] | 0.9502 [0.9261, 0.9712] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_convnextv2_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0029 [+0.0000, +0.0061] * | +0.0151 [-0.0049, +0.0398] | +0.0028 [-0.0001, +0.0059] | +0.0033 [-0.0092, +0.0178] |
| `kd_convnextv2_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0020 [-0.0008, +0.0047] | +0.0345 [+0.0140, +0.0558] * | +0.0017 [-0.0011, +0.0045] | +0.0033 [-0.0097, +0.0159] |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0038 [+0.0006, +0.0075] * | +0.0250 [+0.0049, +0.0446] * | +0.0037 [+0.0005, +0.0074] * | +0.0025 [-0.0091, +0.0154] |
| `kd_convnextv2_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0089 [+0.0036, +0.0149] * | +0.0449 [+0.0190, +0.0670] * | +0.0088 [+0.0035, +0.0148] * | +0.0266 [+0.0091, +0.0452] * |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0037 [+0.0004, +0.0072] * | -0.0062 [-0.0274, +0.0161] | +0.0037 [+0.0004, +0.0072] * | +0.0091 [-0.0000, +0.0211] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0029 [+0.0006, +0.0054] * | +0.0127 [-0.0083, +0.0351] | +0.0028 [+0.0005, +0.0053] * | +0.0075 [-0.0041, +0.0206] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0062 [+0.0020, +0.0110] * | -0.0045 [-0.0251, +0.0177] | +0.0061 [+0.0019, +0.0109] * | +0.0083 [-0.0039, +0.0229] |
| `kd_efficientnetv2_m_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0114 [+0.0047, +0.0187] * | +0.0172 [-0.0114, +0.0442] | +0.0115 [+0.0047, +0.0187] * | +0.0207 [+0.0017, +0.0400] * |
| `kd_maxvit_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0033 [-0.0003, +0.0073] | +0.0152 [-0.0066, +0.0393] | +0.0032 [-0.0004, +0.0071] | +0.0100 [-0.0026, +0.0243] |
| `kd_maxvit_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0028 [-0.0003, +0.0062] | +0.0428 [+0.0214, +0.0637] * | +0.0026 [-0.0004, +0.0060] | +0.0041 [-0.0094, +0.0180] |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0040 [+0.0008, +0.0075] * | +0.0152 [-0.0068, +0.0384] | +0.0039 [+0.0008, +0.0074] * | +0.0025 [-0.0078, +0.0137] |
| `kd_maxvit_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0116 [+0.0052, +0.0188] * | +0.0708 [+0.0429, +0.0917] * | +0.0114 [+0.0051, +0.0186] * | +0.0216 [+0.0053, +0.0394] * |

## 3. Ablation effect — paired bootstrap (main − ablated)

Pairs each `__<suffix>` fork against the same run without the suffix. The sign is **main − ablated**, so a positive delta means the main configuration wins (e.g. `__train_isic_only` → positive = mixing PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as section 2. `*` marks an interval excluding 0.

| Ablated run | vs main | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_efficientformerv2_s2__train_isic_only` | `baseline_efficientformerv2_s2` | +0.0528 [+0.0437, +0.0622] * | +0.5480 [+0.4911, +0.6008] * | +0.0313 [+0.0238, +0.0385] * | +0.1336 [+0.1019, +0.1650] * |
| `baseline_fastvit_sa12__train_isic_only` | `baseline_fastvit_sa12` | +0.0369 [+0.0288, +0.0467] * | +0.5007 [+0.4461, +0.5520] * | +0.0236 [+0.0166, +0.0316] * | +0.0855 [+0.0593, +0.1143] * |
| `baseline_mobilenetv4_conv_medium__train_isic_only` | `baseline_mobilenetv4_conv_medium` | +0.0407 [+0.0319, +0.0497] * | +0.5087 [+0.4508, +0.5645] * | +0.0240 [+0.0166, +0.0310] * | +0.1237 [+0.0946, +0.1525] * |
| `baseline_repvit_m1_0__train_isic_only` | `baseline_repvit_m1_0` | +0.0634 [+0.0534, +0.0755] * | +0.4540 [+0.3998, +0.5137] * | +0.0371 [+0.0287, +0.0455] * | +0.1743 [+0.1424, +0.2098] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio10` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0034 [+0.0012, +0.0062] * | +0.0570 [+0.0343, +0.0781] * | +0.0033 [+0.0010, +0.0061] * | +0.0058 [-0.0031, +0.0142] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio3` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | +0.0007 [-0.0005, +0.0020] | -0.0097 [-0.0222, +0.0044] | +0.0007 [-0.0005, +0.0021] | -0.0008 [-0.0085, +0.0077] |

## 4. Fairness gaps — paired bootstrap over `source`

### `baseline_efficientformerv2_s2`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9284 [0.8976, 0.9540] | 0.0517 [0.0297, 0.0948] | 0.1453 [0.1244, 0.1656] | 0.7836 [0.6909, 0.8642] |
| pad_ufes_20 | 0.8397 [0.8037, 0.8717] | 0.8104 [0.7551, 0.8573] | 0.1007 [0.0834, 0.1191] | 0.5611 [0.4599, 0.6487] |
| **isic2024_minus_pad_ufes_20** | +0.0887 [+0.0428, +0.1336] * | -0.7587 [-0.8075, -0.6871] * | +0.0446 [+0.0160, +0.0713] * | +0.2225 [+0.0972, +0.3511] * |

### `baseline_efficientformerv2_s2__train_isic_only`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.8896 [0.8563, 0.9168] | 0.0322 [0.0181, 0.0620] | 0.1289 [0.1123, 0.1463] | 0.6885 [0.6026, 0.7642] |
| pad_ufes_20 | 0.7134 [0.6700, 0.7538] | 0.6903 [0.6245, 0.7501] | 0.0566 [0.0449, 0.0704] | 0.3178 [0.2430, 0.3968] |
| **isic2024_minus_pad_ufes_20** | +0.1763 [+0.1247, +0.2259] * | -0.6581 [-0.7174, -0.5895] * | +0.0723 [+0.0514, +0.0927] * | +0.3707 [+0.2543, +0.4821] * |

### `baseline_fastvit_sa12`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9337 [0.9059, 0.9571] | 0.0448 [0.0263, 0.0826] | 0.1487 [0.1286, 0.1673] | 0.8098 [0.7246, 0.8853] |
| pad_ufes_20 | 0.8022 [0.7658, 0.8389] | 0.7739 [0.7178, 0.8282] | 0.0873 [0.0701, 0.1048] | 0.4611 [0.3877, 0.5682] |
| **isic2024_minus_pad_ufes_20** | +0.1315 [+0.0865, +0.1754] * | -0.7291 [-0.7821, -0.6622] * | +0.0614 [+0.0354, +0.0888] * | +0.3487 [+0.2085, +0.4532] * |

### `baseline_fastvit_sa12__train_isic_only`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9147 [0.8817, 0.9428] | 0.0240 [0.0149, 0.0418] | 0.1378 [0.1154, 0.1583] | 0.7639 [0.6712, 0.8546] |
| pad_ufes_20 | 0.7004 [0.6537, 0.7448] | 0.6694 [0.6005, 0.7354] | 0.0546 [0.0420, 0.0696] | 0.3167 [0.2406, 0.3968] |
| **isic2024_minus_pad_ufes_20** | +0.2143 [+0.1588, +0.2708] * | -0.6454 [-0.7115, -0.5726] * | +0.0831 [+0.0576, +0.1080] * | +0.4473 [+0.3239, +0.5622] * |

### `baseline_mobilenetv4_conv_medium`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9233 [0.8912, 0.9496] | 0.0541 [0.0307, 0.1043] | 0.1409 [0.1191, 0.1614] | 0.7967 [0.7105, 0.8725] |
| pad_ufes_20 | 0.7947 [0.7555, 0.8310] | 0.7633 [0.7072, 0.8185] | 0.0843 [0.0659, 0.1032] | 0.4422 [0.3610, 0.5437] |
| **isic2024_minus_pad_ufes_20** | +0.1285 [+0.0805, +0.1758] * | -0.7091 [-0.7654, -0.6325] * | +0.0566 [+0.0279, +0.0846] * | +0.3545 [+0.2218, +0.4599] * |

### `baseline_mobilenetv4_conv_medium__train_isic_only`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9080 [0.8740, 0.9365] | 0.0370 [0.0178, 0.0747] | 0.1366 [0.1160, 0.1560] | 0.7213 [0.6185, 0.8086] |
| pad_ufes_20 | 0.6920 [0.6491, 0.7325] | 0.6501 [0.5878, 0.7147] | 0.0555 [0.0431, 0.0691] | 0.2611 [0.2000, 0.3362] |
| **isic2024_minus_pad_ufes_20** | +0.2160 [+0.1618, +0.2694] * | -0.6131 [-0.6797, -0.5403] * | +0.0811 [+0.0572, +0.1038] * | +0.4602 [+0.3315, +0.5717] * |

### `baseline_repvit_m1_0`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.8906 [0.8443, 0.9286] | 0.0489 [0.0233, 0.1014] | 0.1199 [0.0908, 0.1494] | 0.7246 [0.6164, 0.8170] |
| pad_ufes_20 | 0.7420 [0.6976, 0.7851] | 0.6812 [0.6171, 0.7485] | 0.0764 [0.0602, 0.0931] | 0.2867 [0.2213, 0.3830] |
| **isic2024_minus_pad_ufes_20** | +0.1486 [+0.0825, +0.2082] * | -0.6323 [-0.7028, -0.5524] * | +0.0435 [+0.0093, +0.0781] * | +0.4379 [+0.2896, +0.5537] * |

### `baseline_repvit_m1_0__train_isic_only`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.8574 [0.8088, 0.8994] | 0.0224 [0.0108, 0.0543] | 0.1035 [0.0776, 0.1324] | 0.6393 [0.5321, 0.7334] |
| pad_ufes_20 | 0.6776 [0.6308, 0.7213] | 0.6409 [0.5791, 0.7042] | 0.0487 [0.0365, 0.0627] | 0.2411 [0.1710, 0.3326] |
| **isic2024_minus_pad_ufes_20** | +0.1798 [+0.1115, +0.2440] * | -0.6185 [-0.6819, -0.5457] * | +0.0548 [+0.0243, +0.0858] * | +0.3982 [+0.2574, +0.5177] * |

### `kd_convnextv2_base_to_efficientformerv2_s2`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9397 [0.9142, 0.9612] | 0.0646 [0.0343, 0.1172] | 0.1535 [0.1379, 0.1697] | 0.8033 [0.7072, 0.8814] |
| pad_ufes_20 | 0.8370 [0.7985, 0.8736] | 0.8038 [0.7478, 0.8590] | 0.1029 [0.0821, 0.1233] | 0.5244 [0.4012, 0.6409] |
| **isic2024_minus_pad_ufes_20** | +0.1027 [+0.0590, +0.1482] * | -0.7392 [-0.7990, -0.6601] * | +0.0506 [+0.0256, +0.0779] * | +0.2788 [+0.1285, +0.4350] * |

### `kd_convnextv2_base_to_fastvit_sa12`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9412 [0.9141, 0.9626] | 0.0644 [0.0375, 0.1138] | 0.1542 [0.1347, 0.1719] | 0.8262 [0.7304, 0.9075] |
| pad_ufes_20 | 0.8317 [0.7938, 0.8697] | 0.7954 [0.7358, 0.8518] | 0.1040 [0.0850, 0.1231] | 0.4867 [0.3667, 0.6299] |
| **isic2024_minus_pad_ufes_20** | +0.1094 [+0.0637, +0.1539] * | -0.7310 [-0.7909, -0.6505] * | +0.0502 [+0.0234, +0.0774] * | +0.3396 [+0.1626, +0.4871] * |

### `kd_convnextv2_base_to_mobilenetv4_conv_medium`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9379 [0.9100, 0.9594] | 0.0618 [0.0365, 0.1096] | 0.1532 [0.1348, 0.1697] | 0.8131 [0.7245, 0.8862] |
| pad_ufes_20 | 0.8217 [0.7848, 0.8579] | 0.7910 [0.7349, 0.8433] | 0.0981 [0.0794, 0.1169] | 0.4689 [0.3494, 0.5836] |
| **isic2024_minus_pad_ufes_20** | +0.1163 [+0.0712, +0.1611] * | -0.7291 [-0.7845, -0.6547] * | +0.0551 [+0.0292, +0.0811] * | +0.3442 [+0.1923, +0.4896] * |

### `kd_convnextv2_base_to_repvit_m1_0`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9257 [0.8904, 0.9529] | 0.0476 [0.0258, 0.0885] | 0.1431 [0.1174, 0.1659] | 0.8197 [0.7254, 0.8968] |
| pad_ufes_20 | 0.7820 [0.7379, 0.8235] | 0.7420 [0.6792, 0.8043] | 0.0792 [0.0625, 0.0981] | 0.4033 [0.3094, 0.5288] |
| **isic2024_minus_pad_ufes_20** | +0.1437 [+0.0907, +0.1960] * | -0.6944 [-0.7587, -0.6191] * | +0.0639 [+0.0319, +0.0931] * | +0.4163 [+0.2618, +0.5351] * |

### `kd_efficientnetv2_m_to_efficientformerv2_s2`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9429 [0.9180, 0.9636] | 0.0688 [0.0359, 0.1215] | 0.1562 [0.1409, 0.1725] | 0.8230 [0.7344, 0.9015] |
| pad_ufes_20 | 0.8060 [0.7678, 0.8427] | 0.7765 [0.7213, 0.8302] | 0.0923 [0.0739, 0.1111] | 0.4489 [0.3732, 0.5425] |
| **isic2024_minus_pad_ufes_20** | +0.1369 [+0.0933, +0.1800] * | -0.7077 [-0.7688, -0.6304] * | +0.0640 [+0.0399, +0.0887] * | +0.3741 [+0.2405, +0.4815] * |

### `kd_efficientnetv2_m_to_fastvit_sa12`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9444 [0.9199, 0.9652] | 0.0552 [0.0299, 0.0992] | 0.1562 [0.1394, 0.1735] | 0.8426 [0.7593, 0.9164] |
| pad_ufes_20 | 0.8064 [0.7699, 0.8446] | 0.7732 [0.7146, 0.8304] | 0.0901 [0.0730, 0.1090] | 0.4489 [0.3605, 0.5704] |
| **isic2024_minus_pad_ufes_20** | +0.1380 [+0.0929, +0.1799] * | -0.7180 [-0.7772, -0.6463] * | +0.0661 [+0.0414, +0.0907] * | +0.3937 [+0.2459, +0.5062] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9480 [0.9262, 0.9664] | 0.0646 [0.0358, 0.1185] | 0.1610 [0.1466, 0.1753] | 0.8328 [0.7507, 0.9065] |
| pad_ufes_20 | 0.7902 [0.7522, 0.8265] | 0.7511 [0.6918, 0.8078] | 0.0871 [0.0702, 0.1059] | 0.3856 [0.3026, 0.4965] |
| **isic2024_minus_pad_ufes_20** | +0.1578 [+0.1144, +0.2001] * | -0.6865 [-0.7477, -0.6078] * | +0.0739 [+0.0502, +0.0966] * | +0.4472 [+0.3113, +0.5574] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio10`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9356 [0.9061, 0.9594] | 0.0508 [0.0298, 0.0949] | 0.1503 [0.1296, 0.1697] | 0.8197 [0.7311, 0.8968] |
| pad_ufes_20 | 0.7552 [0.7174, 0.7937] | 0.7144 [0.6568, 0.7717] | 0.0746 [0.0590, 0.0911] | 0.3522 [0.2838, 0.4506] |
| **isic2024_minus_pad_ufes_20** | +0.1805 [+0.1318, +0.2254] * | -0.6636 [-0.7232, -0.5892] * | +0.0756 [+0.0504, +0.1009] * | +0.4674 [+0.3346, +0.5682] * |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio3`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9443 [0.9198, 0.9634] | 0.0645 [0.0351, 0.1187] | 0.1575 [0.1418, 0.1733] | 0.8393 [0.7562, 0.9088] |
| pad_ufes_20 | 0.7979 [0.7589, 0.8344] | 0.7625 [0.7040, 0.8177] | 0.0910 [0.0735, 0.1087] | 0.4322 [0.3278, 0.5265] |
| **isic2024_minus_pad_ufes_20** | +0.1464 [+0.1015, +0.1895] * | -0.6980 [-0.7569, -0.6194] * | +0.0665 [+0.0428, +0.0911] * | +0.4071 [+0.2826, +0.5353] * |

### `kd_efficientnetv2_m_to_repvit_m1_0`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9363 [0.9092, 0.9582] | 0.0462 [0.0259, 0.0886] | 0.1529 [0.1356, 0.1697] | 0.7967 [0.7000, 0.8750] |
| pad_ufes_20 | 0.7452 [0.7038, 0.7860] | 0.6943 [0.6285, 0.7626] | 0.0702 [0.0535, 0.0872] | 0.3089 [0.2262, 0.4133] |
| **isic2024_minus_pad_ufes_20** | +0.1911 [+0.1429, +0.2387] * | -0.6481 [-0.7152, -0.5714] * | +0.0826 [+0.0581, +0.1068] * | +0.4878 [+0.3438, +0.6020] * |

### `kd_maxvit_base_to_efficientformerv2_s2`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9408 [0.9110, 0.9637] | 0.0625 [0.0363, 0.1136] | 0.1536 [0.1325, 0.1721] | 0.8262 [0.7414, 0.9000] |
| pad_ufes_20 | 0.8430 [0.8059, 0.8785] | 0.8184 [0.7600, 0.8723] | 0.1018 [0.0818, 0.1221] | 0.5556 [0.4562, 0.6656] |
| **isic2024_minus_pad_ufes_20** | +0.0978 [+0.0524, +0.1415] * | -0.7559 [-0.8132, -0.6773] * | +0.0518 [+0.0238, +0.0802] * | +0.2707 [+0.1392, +0.3972] * |

### `kd_maxvit_base_to_fastvit_sa12`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9439 [0.9173, 0.9650] | 0.0592 [0.0340, 0.1056] | 0.1569 [0.1377, 0.1742] | 0.8230 [0.7424, 0.8968] |
| pad_ufes_20 | 0.8362 [0.7992, 0.8717] | 0.8111 [0.7541, 0.8644] | 0.1013 [0.0812, 0.1210] | 0.5356 [0.4187, 0.6373] |
| **isic2024_minus_pad_ufes_20** | +0.1078 [+0.0636, +0.1507] * | -0.7519 [-0.8093, -0.6786] * | +0.0557 [+0.0294, +0.0840] * | +0.2874 [+0.1565, +0.4291] * |

### `kd_maxvit_base_to_mobilenetv4_conv_medium`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9393 [0.9083, 0.9626] | 0.0579 [0.0337, 0.1067] | 0.1538 [0.1302, 0.1735] | 0.8164 [0.7260, 0.8972] |
| pad_ufes_20 | 0.8216 [0.7840, 0.8571] | 0.7899 [0.7357, 0.8408] | 0.0959 [0.0773, 0.1147] | 0.5033 [0.4032, 0.5990] |
| **isic2024_minus_pad_ufes_20** | +0.1178 [+0.0717, +0.1633] * | -0.7320 [-0.7865, -0.6563] * | +0.0579 [+0.0284, +0.0857] * | +0.3131 [+0.1793, +0.4452] * |

### `kd_maxvit_base_to_repvit_m1_0`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9359 [0.9058, 0.9585] | 0.0531 [0.0284, 0.1012] | 0.1534 [0.1340, 0.1706] | 0.7967 [0.7031, 0.8750] |
| pad_ufes_20 | 0.7879 [0.7456, 0.8275] | 0.7613 [0.6981, 0.8207] | 0.0806 [0.0619, 0.0990] | 0.4311 [0.3509, 0.5360] |
| **isic2024_minus_pad_ufes_20** | +0.1480 [+0.1002, +0.1962] * | -0.7081 [-0.7699, -0.6280] * | +0.0728 [+0.0463, +0.0987] * | +0.3656 [+0.2231, +0.4718] * |

### `teacher/convnextv2_base`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9328 [0.9042, 0.9562] | 0.0689 [0.0395, 0.1229] | 0.1485 [0.1287, 0.1672] | 0.8098 [0.7224, 0.8842] |
| pad_ufes_20 | 0.8453 [0.8085, 0.8785] | 0.8079 [0.7515, 0.8619] | 0.1149 [0.0981, 0.1306] | 0.4678 [0.3707, 0.6179] |
| **isic2024_minus_pad_ufes_20** | +0.0875 [+0.0433, +0.1314] * | -0.7390 [-0.7977, -0.6601] * | +0.0336 [+0.0087, +0.0596] * | +0.3421 [+0.1645, +0.4636] * |

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9340 [0.9079, 0.9568] | 0.0640 [0.0353, 0.1166] | 0.1509 [0.1347, 0.1677] | 0.8197 [0.7344, 0.8915] |
| pad_ufes_20 | 0.8181 [0.7817, 0.8524] | 0.7857 [0.7281, 0.8389] | 0.1023 [0.0864, 0.1182] | 0.4822 [0.3847, 0.5688] |
| **isic2024_minus_pad_ufes_20** | +0.1159 [+0.0713, +0.1589] * | -0.7217 [-0.7805, -0.6437] * | +0.0486 [+0.0241, +0.0736] * | +0.3374 [+0.2162, +0.4534] * |

### `teacher/maxvit_base`

Group sizes (per fold): isic2024 n=61663, pad_ufes_20 n=377

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9366 [0.9082, 0.9593] | 0.0592 [0.0353, 0.1052] | 0.1515 [0.1313, 0.1690] | 0.8066 [0.7231, 0.8800] |
| pad_ufes_20 | 0.8552 [0.8213, 0.8877] | 0.8345 [0.7805, 0.8826] | 0.1102 [0.0917, 0.1285] | 0.5856 [0.4787, 0.6714] |
| **isic2024_minus_pad_ufes_20** | +0.0814 [+0.0384, +0.1221] * | -0.7754 [-0.8296, -0.7051] * | +0.0413 [+0.0148, +0.0677] * | +0.2210 [+0.1030, +0.3518] * |


## 5. Ablation effect **within each `source`** — paired (main − ablated)

Section 3 gives the ablation delta on the whole test set. For the PAD-mixing arms that is the wrong cell — the ISIC-only arm collapses on the PAD rows, and those rows carry ~75% of all positives, so the whole-test delta is inflated. **Quote this table instead.** Still paired: every run draws the same rows for a given group, so the replicate vectors difference directly. `*` marks an interval excluding 0.

| Ablated run | vs main | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `baseline_efficientformerv2_s2__train_isic_only` | `baseline_efficientformerv2_s2` | isic2024 | +0.0387 [+0.0226, +0.0552] * | +0.0194 [+0.0012, +0.0473] * | +0.0164 [+0.0035, +0.0272] * | +0.0951 [+0.0357, +0.1500] * |
| `baseline_efficientformerv2_s2__train_isic_only` | `baseline_efficientformerv2_s2` | pad_ufes_20 | +0.1263 [+0.0875, +0.1641] * | +0.1200 [+0.0747, +0.1630] * | +0.0441 [+0.0276, +0.0608] * | +0.2433 [+0.1423, +0.3307] * |
| `baseline_fastvit_sa12__train_isic_only` | `baseline_fastvit_sa12` | isic2024 | +0.0190 [+0.0069, +0.0320] * | +0.0208 [+0.0075, +0.0467] * | +0.0109 [+0.0001, +0.0207] * | +0.0459 [+0.0061, +0.0852] * |
| `baseline_fastvit_sa12__train_isic_only` | `baseline_fastvit_sa12` | pad_ufes_20 | +0.1019 [+0.0668, +0.1390] * | +0.1045 [+0.0589, +0.1493] * | +0.0327 [+0.0177, +0.0466] * | +0.1444 [+0.0703, +0.2482] * |
| `baseline_mobilenetv4_conv_medium__train_isic_only` | `baseline_mobilenetv4_conv_medium` | isic2024 | +0.0152 [-0.0058, +0.0347] | +0.0171 [-0.0081, +0.0497] | +0.0043 [-0.0135, +0.0206] | +0.0754 [+0.0237, +0.1300] * |
| `baseline_mobilenetv4_conv_medium__train_isic_only` | `baseline_mobilenetv4_conv_medium` | pad_ufes_20 | +0.1028 [+0.0661, +0.1410] * | +0.1132 [+0.0707, +0.1549] * | +0.0288 [+0.0117, +0.0463] * | +0.1811 [+0.1017, +0.2715] * |
| `baseline_repvit_m1_0__train_isic_only` | `baseline_repvit_m1_0` | isic2024 | +0.0332 [+0.0163, +0.0510] * | +0.0265 [+0.0046, +0.0589] * | +0.0163 [+0.0038, +0.0270] * | +0.0852 [+0.0214, +0.1491] * |
| `baseline_repvit_m1_0__train_isic_only` | `baseline_repvit_m1_0` | pad_ufes_20 | +0.0644 [+0.0216, +0.1046] * | +0.0404 [-0.0092, +0.0908] | +0.0277 [+0.0128, +0.0410] * | +0.0456 [-0.0400, +0.1432] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio10` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | isic2024 | +0.0123 [+0.0038, +0.0237] * | +0.0138 [+0.0004, +0.0319] * | +0.0108 [+0.0032, +0.0205] * | +0.0131 [-0.0182, +0.0516] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio10` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | pad_ufes_20 | +0.0350 [+0.0168, +0.0526] * | +0.0367 [+0.0117, +0.0611] * | +0.0125 [+0.0047, +0.0205] * | +0.0333 [-0.0293, +0.0979] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio3` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | isic2024 | +0.0037 [-0.0010, +0.0090] | +0.0001 [-0.0124, +0.0115] | +0.0035 [-0.0010, +0.0079] | -0.0066 [-0.0361, +0.0226] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__ratio3` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | pad_ufes_20 | -0.0077 [-0.0195, +0.0047] | -0.0114 [-0.0273, +0.0062] | -0.0039 [-0.0100, +0.0024] | -0.0467 [-0.0893, +0.0263] |
