# Bootstrap 95% confidence intervals — `reports/external/ham10000/no_akiec`

B = 2000 replicates, seed 42, 7242 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_efficientformerv2_s2` | 5 | 0.8213 [0.8097, 0.8336] | 0.4029 [0.3754, 0.4306] | 0.0986 [0.0929, 0.1048] | 0.4846 [0.4507, 0.5144] |
| `baseline_fastvit_sa12` | 5 | 0.8082 [0.7958, 0.8201] | 0.3985 [0.3727, 0.4267] | 0.0942 [0.0887, 0.1001] | 0.4510 [0.4223, 0.4789] |
| `baseline_mobilenetv4_conv_medium` | 5 | 0.7906 [0.7781, 0.8036] | 0.3398 [0.3156, 0.3645] | 0.0919 [0.0862, 0.0979] | 0.3860 [0.3534, 0.4150] |
| `baseline_repvit_m1_0` | 5 | 0.7636 [0.7494, 0.7777] | 0.2997 [0.2780, 0.3232] | 0.0812 [0.0749, 0.0876] | 0.3401 [0.3119, 0.3671] |
| `kd_convnextv2_base_to_efficientformerv2_s2` | 5 | 0.8255 [0.8130, 0.8387] | 0.4369 [0.4068, 0.4665] | 0.0972 [0.0910, 0.1042] | 0.5116 [0.4798, 0.5432] |
| `kd_convnextv2_base_to_fastvit_sa12` | 5 | 0.8350 [0.8237, 0.8468] | 0.4270 [0.3977, 0.4568] | 0.1088 [0.1032, 0.1149] | 0.4905 [0.4595, 0.5215] |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | 5 | 0.8152 [0.8038, 0.8275] | 0.3860 [0.3592, 0.4134] | 0.1002 [0.0946, 0.1063] | 0.4444 [0.4161, 0.4740] |
| `kd_convnextv2_base_to_repvit_m1_0` | 5 | 0.7773 [0.7641, 0.7912] | 0.3333 [0.3099, 0.3591] | 0.0847 [0.0785, 0.0912] | 0.3753 [0.3475, 0.4029] |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | 5 | 0.8163 [0.8048, 0.8283] | 0.4094 [0.3837, 0.4358] | 0.0971 [0.0916, 0.1028] | 0.4750 [0.4491, 0.5054] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | 5 | 0.8365 [0.8259, 0.8470] | 0.4323 [0.4062, 0.4594] | 0.1081 [0.1028, 0.1134] | 0.5143 [0.4866, 0.5426] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.8249 [0.8147, 0.8357] | 0.4034 [0.3776, 0.4298] | 0.1045 [0.0991, 0.1103] | 0.4652 [0.4390, 0.4893] |
| `kd_efficientnetv2_m_to_repvit_m1_0` | 5 | 0.7826 [0.7706, 0.7947] | 0.3301 [0.3085, 0.3529] | 0.0913 [0.0854, 0.0974] | 0.3722 [0.3479, 0.3959] |
| `kd_maxvit_base_to_efficientformerv2_s2` | 5 | 0.8259 [0.8141, 0.8380] | 0.4285 [0.4000, 0.4565] | 0.1011 [0.0952, 0.1076] | 0.4901 [0.4599, 0.5215] |
| `kd_maxvit_base_to_fastvit_sa12` | 5 | 0.8329 [0.8225, 0.8436] | 0.4059 [0.3802, 0.4331] | 0.1131 [0.1074, 0.1188] | 0.4646 [0.4348, 0.4926] |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | 5 | 0.7864 [0.7751, 0.7987] | 0.3576 [0.3341, 0.3814] | 0.0932 [0.0874, 0.0991] | 0.3872 [0.3626, 0.4157] |
| `kd_maxvit_base_to_repvit_m1_0` | 5 | 0.7671 [0.7536, 0.7807] | 0.3085 [0.2856, 0.3329] | 0.0849 [0.0787, 0.0913] | 0.3358 [0.3091, 0.3631] |
| `teacher/convnextv2_base` | 5 | 0.7951 [0.7817, 0.8092] | 0.4165 [0.3870, 0.4473] | 0.0791 [0.0738, 0.0851] | 0.4865 [0.4576, 0.5194] |
| `teacher/efficientnetv2_m` | 5 | 0.8207 [0.8088, 0.8323] | 0.4283 [0.4002, 0.4561] | 0.0957 [0.0902, 0.1016] | 0.5016 [0.4731, 0.5281] |
| `teacher/maxvit_base` | 5 | 0.8222 [0.8118, 0.8333] | 0.4311 [0.4040, 0.4584] | 0.1027 [0.0975, 0.1080] | 0.4825 [0.4562, 0.5104] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_convnextv2_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0043 [-0.0014, +0.0100] | +0.0340 [+0.0235, +0.0452] * | -0.0014 [-0.0051, +0.0025] | +0.0270 [+0.0114, +0.0458] * |
| `kd_convnextv2_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0269 [+0.0212, +0.0327] * | +0.0285 [+0.0164, +0.0406] * | +0.0145 [+0.0110, +0.0182] * | +0.0395 [+0.0208, +0.0596] * |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0247 [+0.0195, +0.0300] * | +0.0462 [+0.0361, +0.0578] * | +0.0082 [+0.0048, +0.0115] * | +0.0584 [+0.0426, +0.0775] * |
| `kd_convnextv2_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0137 [+0.0078, +0.0198] * | +0.0336 [+0.0224, +0.0445] * | +0.0035 [+0.0002, +0.0066] * | +0.0353 [+0.0161, +0.0542] * |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | -0.0050 [-0.0108, +0.0004] | +0.0065 [-0.0061, +0.0189] | -0.0015 [-0.0049, +0.0017] | -0.0096 [-0.0266, +0.0126] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0283 [+0.0221, +0.0341] * | +0.0338 [+0.0191, +0.0476] * | +0.0138 [+0.0104, +0.0171] * | +0.0633 [+0.0436, +0.0856] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0344 [+0.0286, +0.0399] * | +0.0636 [+0.0514, +0.0751] * | +0.0126 [+0.0090, +0.0159] * | +0.0793 [+0.0607, +0.1010] * |
| `kd_efficientnetv2_m_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0191 [+0.0116, +0.0267] * | +0.0304 [+0.0169, +0.0442] * | +0.0101 [+0.0065, +0.0138] * | +0.0321 [+0.0103, +0.0548] * |
| `kd_maxvit_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0047 [-0.0005, +0.0094] | +0.0256 [+0.0144, +0.0378] * | +0.0025 [-0.0008, +0.0057] | +0.0055 [-0.0103, +0.0242] |
| `kd_maxvit_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0248 [+0.0184, +0.0311] * | +0.0074 [-0.0054, +0.0205] | +0.0189 [+0.0149, +0.0228] * | +0.0136 [-0.0064, +0.0332] |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | -0.0042 [-0.0093, +0.0013] | +0.0178 [+0.0064, +0.0277] * | +0.0012 [-0.0019, +0.0046] | +0.0013 [-0.0150, +0.0226] |
| `kd_maxvit_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0036 [-0.0036, +0.0102] | +0.0088 [-0.0026, +0.0203] | +0.0037 [+0.0000, +0.0075] * | -0.0043 [-0.0223, +0.0161] |

## 3. Fairness gaps — paired bootstrap over `dx`

### `baseline_efficientformerv2_s2`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `baseline_fastvit_sa12`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `baseline_mobilenetv4_conv_medium`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `baseline_repvit_m1_0`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_convnextv2_base_to_efficientformerv2_s2`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_convnextv2_base_to_fastvit_sa12`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_convnextv2_base_to_mobilenetv4_conv_medium`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_convnextv2_base_to_repvit_m1_0`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_efficientnetv2_m_to_efficientformerv2_s2`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_efficientnetv2_m_to_fastvit_sa12`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_efficientnetv2_m_to_mobilenetv4_conv_medium`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_efficientnetv2_m_to_repvit_m1_0`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_maxvit_base_to_efficientformerv2_s2`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_maxvit_base_to_fastvit_sa12`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_maxvit_base_to_mobilenetv4_conv_medium`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `kd_maxvit_base_to_repvit_m1_0`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `teacher/convnextv2_base`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `teacher/efficientnetv2_m`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

### `teacher/maxvit_base`

Group sizes (per fold): bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **bcc_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bcc_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **bkl_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **df_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **mel_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **nv_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |

