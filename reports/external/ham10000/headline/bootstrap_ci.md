# Bootstrap 95% confidence intervals — `reports/external/ham10000/headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `baseline_efficientformerv2_s2` | 5 | 0.8227 [0.8111, 0.8332] | 0.4533 [0.4267, 0.4793] | 0.0996 [0.0943, 0.1048] | 0.4854 [0.4511, 0.5142] |
| `baseline_fastvit_sa12` | 5 | 0.8027 [0.7910, 0.8133] | 0.4346 [0.4093, 0.4598] | 0.0933 [0.0884, 0.0983] | 0.4347 [0.4074, 0.4602] |
| `baseline_mobilenetv4_conv_medium` | 5 | 0.7856 [0.7737, 0.7969] | 0.3754 [0.3530, 0.3989] | 0.0915 [0.0863, 0.0969] | 0.3702 [0.3384, 0.3978] |
| `baseline_repvit_m1_0` | 5 | 0.7565 [0.7432, 0.7693] | 0.3347 [0.3134, 0.3566] | 0.0798 [0.0745, 0.0854] | 0.3237 [0.2983, 0.3472] |
| `kd_convnextv2_base_to_efficientformerv2_s2` | 5 | 0.8246 [0.8121, 0.8361] | 0.4833 [0.4544, 0.5106] | 0.0966 [0.0908, 0.1026] | 0.5098 [0.4787, 0.5398] |
| `kd_convnextv2_base_to_fastvit_sa12` | 5 | 0.8304 [0.8191, 0.8409] | 0.4625 [0.4346, 0.4892] | 0.1083 [0.1032, 0.1134] | 0.4708 [0.4415, 0.4996] |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | 5 | 0.8065 [0.7947, 0.8177] | 0.4198 [0.3942, 0.4459] | 0.0964 [0.0912, 0.1019] | 0.4286 [0.4012, 0.4547] |
| `kd_convnextv2_base_to_repvit_m1_0` | 5 | 0.7691 [0.7562, 0.7816] | 0.3669 [0.3428, 0.3906] | 0.0826 [0.0771, 0.0880] | 0.3618 [0.3367, 0.3856] |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | 5 | 0.8148 [0.8030, 0.8256] | 0.4593 [0.4338, 0.4839] | 0.0964 [0.0911, 0.1019] | 0.4778 [0.4524, 0.5040] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | 5 | 0.8333 [0.8232, 0.8433] | 0.4797 [0.4546, 0.5045] | 0.1069 [0.1019, 0.1120] | 0.5081 [0.4803, 0.5338] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.8211 [0.8108, 0.8311] | 0.4467 [0.4220, 0.4707] | 0.1028 [0.0978, 0.1080] | 0.4635 [0.4393, 0.4865] |
| `kd_efficientnetv2_m_to_repvit_m1_0` | 5 | 0.7763 [0.7646, 0.7875] | 0.3665 [0.3452, 0.3882] | 0.0903 [0.0851, 0.0958] | 0.3550 [0.3327, 0.3766] |
| `kd_maxvit_base_to_efficientformerv2_s2` | 5 | 0.8298 [0.8179, 0.8407] | 0.4841 [0.4567, 0.5108] | 0.1028 [0.0967, 0.1089] | 0.4989 [0.4687, 0.5281] |
| `kd_maxvit_base_to_fastvit_sa12` | 5 | 0.8333 [0.8235, 0.8426] | 0.4572 [0.4313, 0.4824] | 0.1148 [0.1097, 0.1196] | 0.4624 [0.4335, 0.4861] |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | 5 | 0.7820 [0.7703, 0.7934] | 0.3958 [0.3723, 0.4186] | 0.0920 [0.0867, 0.0978] | 0.3791 [0.3540, 0.4041] |
| `kd_maxvit_base_to_repvit_m1_0` | 5 | 0.7644 [0.7517, 0.7769] | 0.3493 [0.3268, 0.3727] | 0.0855 [0.0799, 0.0913] | 0.3285 [0.3022, 0.3515] |
| `teacher/convnextv2_base` | 5 | 0.7900 [0.7764, 0.8027] | 0.4547 [0.4267, 0.4818] | 0.0772 [0.0720, 0.0827] | 0.4806 [0.4512, 0.5080] |
| `teacher/efficientnetv2_m` | 5 | 0.8212 [0.8100, 0.8318] | 0.4761 [0.4506, 0.5026] | 0.0967 [0.0915, 0.1020] | 0.4977 [0.4704, 0.5236] |
| `teacher/maxvit_base` | 5 | 0.8233 [0.8129, 0.8329] | 0.4856 [0.4596, 0.5102] | 0.1036 [0.0991, 0.1085] | 0.4820 [0.4561, 0.5055] |

## 2. KD effect — paired bootstrap (KD − baseline)

Both models are resampled on the **identical** rows, so the correlation between them is kept; an unpaired interval would overstate the uncertainty. `*` marks an interval excluding 0.

| KD run | vs baseline | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `kd_convnextv2_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0019 [-0.0031, +0.0070] | +0.0300 [+0.0193, +0.0403] * | -0.0030 [-0.0063, +0.0004] | +0.0245 [+0.0102, +0.0437] * |
| `kd_convnextv2_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0277 [+0.0224, +0.0327] * | +0.0279 [+0.0167, +0.0382] * | +0.0151 [+0.0122, +0.0181] * | +0.0361 [+0.0192, +0.0551] * |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0209 [+0.0159, +0.0255] * | +0.0445 [+0.0350, +0.0547] * | +0.0049 [+0.0019, +0.0078] * | +0.0583 [+0.0428, +0.0768] * |
| `kd_convnextv2_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0126 [+0.0069, +0.0178] * | +0.0323 [+0.0219, +0.0429] * | +0.0027 [+0.0001, +0.0054] * | +0.0382 [+0.0221, +0.0553] * |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | -0.0079 [-0.0129, -0.0028] * | +0.0060 [-0.0054, +0.0177] | -0.0032 [-0.0062, -0.0002] * | -0.0075 [-0.0236, +0.0151] |
| `kd_efficientnetv2_m_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0306 [+0.0252, +0.0363] * | +0.0451 [+0.0325, +0.0575] * | +0.0137 [+0.0108, +0.0168] * | +0.0734 [+0.0543, +0.0921] * |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | +0.0355 [+0.0303, +0.0403] * | +0.0713 [+0.0598, +0.0819] * | +0.0113 [+0.0083, +0.0142] * | +0.0932 [+0.0758, +0.1139] * |
| `kd_efficientnetv2_m_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0198 [+0.0129, +0.0267] * | +0.0318 [+0.0196, +0.0440] * | +0.0105 [+0.0075, +0.0135] * | +0.0313 [+0.0122, +0.0513] * |
| `kd_maxvit_base_to_efficientformerv2_s2` | `baseline_efficientformerv2_s2` | +0.0071 [+0.0022, +0.0118] * | +0.0308 [+0.0201, +0.0419] * | +0.0032 [+0.0001, +0.0063] * | +0.0135 [-0.0019, +0.0325] |
| `kd_maxvit_base_to_fastvit_sa12` | `baseline_fastvit_sa12` | +0.0307 [+0.0248, +0.0364] * | +0.0226 [+0.0107, +0.0339] * | +0.0215 [+0.0184, +0.0248] * | +0.0277 [+0.0084, +0.0446] * |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | `baseline_mobilenetv4_conv_medium` | -0.0036 [-0.0081, +0.0009] | +0.0205 [+0.0108, +0.0300] * | +0.0006 [-0.0021, +0.0033] | +0.0089 [-0.0065, +0.0290] |
| `kd_maxvit_base_to_repvit_m1_0` | `baseline_repvit_m1_0` | +0.0079 [+0.0018, +0.0140] * | +0.0146 [+0.0044, +0.0256] * | +0.0057 [+0.0027, +0.0087] * | +0.0048 [-0.0120, +0.0227] |

## 3. Fairness gaps — paired bootstrap over `dx`

### `baseline_efficientformerv2_s2`

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

Group sizes (per fold): akiec n=228, bcc n=327, bkl n=727, df n=73, mel n=614, nv n=5403, vasc n=98

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

