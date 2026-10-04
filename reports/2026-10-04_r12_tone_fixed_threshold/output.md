Fitzpatrick17k headline · fold 4 · threshold pad_sens90 = 0.5705 · B = 2000, seed 42 · reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp

| Tông | n ác / n lành | Độ nhạy tại ngưỡng [95%] | Độ đặc hiệu tại ngưỡng [95%] | sens@95spec [95%] |
|---|---|---|---|---|
| light | 1195 / 1115 | 0.604 [0.576, 0.631] | 0.755 [0.730, 0.778] | 0.249 [0.204, 0.295] |
| medium | 757 / 842 | 0.520 [0.484, 0.556] | 0.779 [0.751, 0.806] | 0.209 [0.156, 0.262] |
| dark | 208 / 203 | 0.524 [0.455, 0.593] | 0.808 [0.750, 0.860] | 0.288 [0.208, 0.380] |

| Chênh (A − B), cùng replicate | Độ nhạy tại ngưỡng [95%] | Độ đặc hiệu tại ngưỡng [95%] | sens@95spec [95%] |
|---|---|---|---|
| light − medium | +0.084 [+0.039, +0.127] * | -0.024 [-0.062, +0.010] | +0.040 [-0.027, +0.116] |
| light − dark | +0.080 [+0.004, +0.154] * | -0.053 [-0.110, +0.009] | -0.040 [-0.138, +0.059] |
| medium − dark | -0.004 [-0.082, +0.073] | -0.029 [-0.089, +0.030] | -0.080 [-0.191, +0.015] |

`*` = khoảng loại trừ 0.
