# Bootstrap 95% confidence intervals — `reports/external/ham10000/full`

B = 2000 replicates, seed 42, 10015 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_efficientformerv2_s2` | 5 | 0.7935 [0.7848, 0.8028] | 0.4623 [0.4418, 0.4831] | 0.0889 [0.0849, 0.0932] | 0.4141 [0.3937, 0.4363] |
| `baseline_fastvit_sa12` | 5 | 0.7744 [0.7645, 0.7840] | 0.4495 [0.4301, 0.4695] | 0.0835 [0.0798, 0.0873] | 0.3823 [0.3634, 0.4019] |
| `baseline_mobilenetv4_conv_medium` | 5 | 0.7571 [0.7471, 0.7668] | 0.3969 [0.3786, 0.4159] | 0.0811 [0.0772, 0.0851] | 0.3208 [0.3024, 0.3414] |
| `baseline_repvit_m1_0` | 5 | 0.7185 [0.7077, 0.7292] | 0.3536 [0.3358, 0.3715] | 0.0692 [0.0653, 0.0731] | 0.2677 [0.2495, 0.2864] |
| `kd_convnextv2_base_to_efficientformerv2_s2` | 5 | 0.7971 [0.7874, 0.8068] | 0.4929 [0.4718, 0.5146] | 0.0868 [0.0825, 0.0914] | 0.4409 [0.4190, 0.4637] |
| `kd_convnextv2_base_to_fastvit_sa12` | 5 | 0.7966 [0.7874, 0.8060] | 0.4721 [0.4516, 0.4938] | 0.0961 [0.0923, 0.1002] | 0.4027 [0.3809, 0.4225] |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | 5 | 0.7769 [0.7674, 0.7868] | 0.4401 [0.4207, 0.4605] | 0.0853 [0.0812, 0.0896] | 0.3771 [0.3556, 0.3980] |
| `kd_convnextv2_base_to_repvit_m1_0` | 5 | 0.7362 [0.7253, 0.7466] | 0.3841 [0.3658, 0.4033] | 0.0729 [0.0689, 0.0769] | 0.3115 [0.2913, 0.3295] |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | 5 | 0.7899 [0.7805, 0.7990] | 0.4743 [0.4539, 0.4941] | 0.0872 [0.0833, 0.0914] | 0.4215 [0.4022, 0.4422] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | 5 | 0.8043 [0.7954, 0.8129] | 0.4937 [0.4743, 0.5134] | 0.0949 [0.0910, 0.0990] | 0.4351 [0.4118, 0.4566] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.7922 [0.7834, 0.8009] | 0.4623 [0.4432, 0.4816] | 0.0917 [0.0878, 0.0956] | 0.4049 [0.3861, 0.4235] |
| `kd_efficientnetv2_m_to_repvit_m1_0` | 5 | 0.7414 [0.7316, 0.7508] | 0.3823 [0.3660, 0.3996] | 0.0789 [0.0750, 0.0828] | 0.3038 [0.2856, 0.3188] |
| `kd_maxvit_base_to_efficientformerv2_s2` | 5 | 0.8019 [0.7922, 0.8116] | 0.4971 [0.4760, 0.5184] | 0.0912 [0.0868, 0.0957] | 0.4418 [0.4197, 0.4645] |
| `kd_maxvit_base_to_fastvit_sa12` | 5 | 0.8039 [0.7950, 0.8126] | 0.4735 [0.4542, 0.4933] | 0.1011 [0.0969, 0.1051] | 0.4071 [0.3862, 0.4270] |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | 5 | 0.7582 [0.7485, 0.7677] | 0.4215 [0.4034, 0.4402] | 0.0822 [0.0781, 0.0865] | 0.3421 [0.3230, 0.3621] |
| `kd_maxvit_base_to_repvit_m1_0` | 5 | 0.7330 [0.7220, 0.7432] | 0.3736 [0.3556, 0.3915] | 0.0750 [0.0709, 0.0791] | 0.2915 [0.2718, 0.3088] |
| `teacher/convnextv2_base` | 5 | 0.7743 [0.7641, 0.7845] | 0.4739 [0.4532, 0.4956] | 0.0742 [0.0701, 0.0785] | 0.4304 [0.4088, 0.4517] |
| `teacher/efficientnetv2_m` | 5 | 0.7962 [0.7875, 0.8052] | 0.4866 [0.4669, 0.5078] | 0.0882 [0.0843, 0.0922] | 0.4331 [0.4129, 0.4543] |
| `teacher/maxvit_base` | 5 | 0.8001 [0.7912, 0.8091] | 0.5026 [0.4825, 0.5225] | 0.0934 [0.0895, 0.0975] | 0.4429 [0.4234, 0.4633] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_convnextv2_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0036 [-0.0005, +0.0080] | +0.0306 [+0.0227, +0.0386] * | -0.0021 [-0.0046, +0.0005] | +0.0268 [+0.0139, +0.0390] * |
| `kd_convnextv2_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0222 [+0.0179, +0.0268] * | +0.0226 [+0.0144, +0.0313] * | +0.0126 [+0.0103, +0.0149] * | +0.0204 [+0.0058, +0.0330] * |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0198 [+0.0158, +0.0239] * | +0.0432 [+0.0355, +0.0511] * | +0.0041 [+0.0020, +0.0063] * | +0.0563 [+0.0421, +0.0667] * |
| `kd_convnextv2_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0177 [+0.0131, +0.0223] * | +0.0304 [+0.0224, +0.0381] * | +0.0037 [+0.0017, +0.0058] * | +0.0438 [+0.0299, +0.0554] * |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | -0.0036 [-0.0081, +0.0008] | +0.0120 [+0.0025, +0.0217] * | -0.0016 [-0.0039, +0.0005] | +0.0074 [-0.0076, +0.0210] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0299 [+0.0251, +0.0346] * | +0.0442 [+0.0339, +0.0541] * | +0.0114 [+0.0091, +0.0136] * | +0.0528 [+0.0374, +0.0682] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0351 [+0.0308, +0.0396] * | +0.0654 [+0.0563, +0.0739] * | +0.0106 [+0.0083, +0.0128] * | +0.0841 [+0.0695, +0.0967] * |
| `kd_efficientnetv2_m_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0228 [+0.0174, +0.0288] * | +0.0287 [+0.0190, +0.0387] * | +0.0098 [+0.0076, +0.0121] * | +0.0361 [+0.0200, +0.0499] * |
| `kd_maxvit_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0084 [+0.0046, +0.0121] * | +0.0348 [+0.0262, +0.0432] * | +0.0023 [+0.0001, +0.0046] * | +0.0276 [+0.0146, +0.0409] * |
| `kd_maxvit_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0295 [+0.0247, +0.0343] * | +0.0240 [+0.0149, +0.0328] * | +0.0176 [+0.0151, +0.0199] * | +0.0248 [+0.0110, +0.0382] * |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0010 [-0.0028, +0.0050] | +0.0246 [+0.0167, +0.0319] * | +0.0011 [-0.0009, +0.0031] | +0.0213 [+0.0081, +0.0342] * |
| `kd_maxvit_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0145 [+0.0093, +0.0195] * | +0.0200 [+0.0115, +0.0285] * | +0.0059 [+0.0036, +0.0082] * | +0.0238 [+0.0100, +0.0371] * |

## 3. Fairness gaps — paired bootstrap over `dx`

### `baseline_efficientformerv2_s2`

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

Group sizes (per fold): akiec n=327, bcc n=514, bkl n=1099, df n=115, mel n=1113, nv n=6705, vasc n=142

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| akiec | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bcc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| bkl | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| df | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| mel | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| nv | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| vasc | nan [undefined] | nan [undefined] | nan [undefined] | nan [undefined] |
| **akiec_minus_bcc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_bkl** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_df** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_mel** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_nv** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
| **akiec_minus_vasc** | +nan [undefined] | +nan [undefined] | +nan [undefined] | +nan [undefined] |
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

