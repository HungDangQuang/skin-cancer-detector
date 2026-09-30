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
| `kd_efficientnetv2_m_privileged_to_fastvit_sa12` | 5 | 0.9834 [0.9755, 0.9896] | 0.5990 [0.5424, 0.6582] | 0.1844 [0.1767, 0.1905] | 0.9568 [0.9328, 0.9775] |
| `kd_efficientnetv2_m_privileged_to_mobilenetv4_conv_medium` | 5 | 0.9782 [0.9693, 0.9858] | 0.5718 [0.5158, 0.6303] | 0.1792 [0.1707, 0.1865] | 0.9419 [0.9175, 0.9643] |
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
| `teacher/efficientnetv2_m_privileged` | 5 | 0.9818 [0.9744, 0.9882] | 0.6239 [0.5669, 0.6821] | 0.1826 [0.1755, 0.1888] | 0.9444 [0.9183, 0.9674] |
| `teacher/maxvit_base` | 5 | 0.9824 [0.9745, 0.9887] | 0.6566 [0.5950, 0.7152] | 0.1830 [0.1754, 0.1893] | 0.9502 [0.9261, 0.9712] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_convnextv2_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0029 [+0.0000, +0.0061] * | +0.0151 [-0.0049, +0.0398] | +0.0028 [-0.0001, +0.0059] | +0.0033 [-0.0092, +0.0178] |
| `kd_convnextv2_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0020 [-0.0008, +0.0047] | +0.0345 [+0.0140, +0.0558] * | +0.0017 [-0.0011, +0.0045] | +0.0033 [-0.0097, +0.0159] |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0038 [+0.0006, +0.0075] * | +0.0250 [+0.0049, +0.0446] * | +0.0037 [+0.0005, +0.0074] * | +0.0025 [-0.0091, +0.0154] |
| `kd_convnextv2_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0089 [+0.0036, +0.0149] * | +0.0449 [+0.0190, +0.0670] * | +0.0088 [+0.0035, +0.0148] * | +0.0266 [+0.0091, +0.0452] * |
| `kd_efficientnetv2_m_privileged_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0018 [-0.0005, +0.0041] | -0.0092 [-0.0303, +0.0133] | +0.0018 [-0.0004, +0.0042] | +0.0066 [-0.0043, +0.0181] |
| `kd_efficientnetv2_m_privileged_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | -0.0008 [-0.0048, +0.0033] | -0.0384 [-0.0616, -0.0133] * | -0.0006 [-0.0045, +0.0036] | -0.0066 [-0.0183, +0.0062] |
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

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_efficientnetv2_m_privileged_to_fastvit_sa12` | `kd_efficientnetv2_m_to_fastvit_sa12` | -0.0011 [-0.0038, +0.0016] | -0.0219 [-0.0423, -0.0001] * | -0.0010 [-0.0035, +0.0018] | -0.0008 [-0.0120, +0.0104] |
| `kd_efficientnetv2_m_privileged_to_mobilenetv4_conv_medium` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | -0.0070 [-0.0112, -0.0031] * | -0.0338 [-0.0578, -0.0076] * | -0.0067 [-0.0107, -0.0029] * | -0.0149 [-0.0273, -0.0024] * |
