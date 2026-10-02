# Val-frozen vs test-Youden threshold metrics — `/workspace/skin-cancer-detector/experiments/runs_newsplit_ddi`

Predictions: `fold_*/predictions.csv`; threshold source: `fold_*/val_predictions.csv` (Youden's J on that fold's own val set).

`testthr_*` reproduces what `test_metrics*.json` reports (threshold fitted on the test set — optimistic). `valthr_*` is the honest counterpart (threshold frozen before seeing the test labels). Mean ± std over the folds of each run; the std is the spread between the fold models, not a confidence interval. Ranking metrics do not depend on a threshold and are not repeated here.

## Group `all`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2546 ± 0.0192 → 0.2729 ± 0.0241 | 0.9170 ± 0.0113 → 0.8921 ± 0.0211 | 0.9392 ± 0.0129 → 0.9488 ± 0.0118 | 0.1223 ± 0.0215 → 0.1384 ± 0.0240 |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2298 ± 0.0317 → 0.2114 ± 0.0228 | 0.9162 ± 0.0167 → 0.9185 ± 0.0197 | 0.9282 ± 0.0172 → 0.9125 ± 0.0175 | 0.1074 ± 0.0276 → 0.0883 ± 0.0150 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.1927 ± 0.0294 → 0.1751 ± 0.0202 | 0.9291 ± 0.0098 → 0.9313 ± 0.0114 | 0.9439 ± 0.0103 → 0.9345 ± 0.0131 | 0.1316 ± 0.0193 → 0.1161 ± 0.0213 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__mobile` | 1 | 0.1623 ± 0.0000 → 0.1583 ± 0.0000 | 0.9509 ± 0.0000 → 0.9509 ± 0.0000 | 0.9385 ± 0.0000 → 0.9365 ± 0.0000 | 0.1219 ± 0.0000 → 0.1185 ± 0.0000 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.1917 ± 0.0433 → 0.1721 ± 0.0606 | 0.9313 ± 0.0167 → 0.9268 ± 0.0251 | 0.9431 ± 0.0126 → 0.9273 ± 0.0381 | 0.1322 ± 0.0271 → 0.1245 ± 0.0652 |
| `teacher/efficientnetv2_m` | 5 | 0.2238 ± 0.0336 → 0.2174 ± 0.0151 | 0.9260 ± 0.0232 → 0.9200 ± 0.0132 | 0.9402 ± 0.0286 → 0.9391 ± 0.0199 | 0.1383 ± 0.0535 → 0.1266 ± 0.0337 |

## Group `isic2024`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2546 ± 0.0192 → 0.2729 ± 0.0241 | 0.7105 ± 0.0395 → 0.6237 ± 0.0736 | 0.9425 ± 0.0130 → 0.9521 ± 0.0119 | 0.0318 ± 0.0056 → 0.0333 ± 0.0055 |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2298 ± 0.0317 → 0.2114 ± 0.0228 | 0.7711 ± 0.0563 → 0.7684 ± 0.0700 | 0.9299 ± 0.0171 → 0.9144 ± 0.0174 | 0.0290 ± 0.0073 → 0.0231 ± 0.0030 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.1927 ± 0.0294 → 0.1751 ± 0.0202 | 0.7605 ± 0.0377 → 0.7684 ± 0.0390 | 0.9471 ± 0.0104 → 0.9378 ± 0.0131 | 0.0365 ± 0.0050 → 0.0318 ± 0.0055 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__mobile` | 1 | 0.1623 ± 0.0000 → 0.1583 ± 0.0000 | 0.8289 ± 0.0000 → 0.8289 ± 0.0000 | 0.9418 ± 0.0000 → 0.9398 ± 0.0000 | 0.0355 ± 0.0000 → 0.0343 ± 0.0000 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.1917 ± 0.0433 → 0.1721 ± 0.0606 | 0.7605 ± 0.0584 → 0.7447 ± 0.0876 | 0.9464 ± 0.0127 → 0.9305 ± 0.0382 | 0.0366 ± 0.0070 → 0.0339 ± 0.0186 |
| `teacher/efficientnetv2_m` | 5 | 0.2238 ± 0.0336 → 0.2174 ± 0.0151 | 0.7421 ± 0.0809 → 0.7211 ± 0.0460 | 0.9434 ± 0.0286 → 0.9423 ± 0.0200 | 0.0380 ± 0.0152 → 0.0335 ± 0.0090 |

## Group `pad_ufes_20`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2546 ± 0.0192 → 0.2729 ± 0.0241 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0250 ± 0.0146 → 0.0279 ± 0.0221 | 0.6508 ± 0.0034 → 0.6515 ± 0.0052 |
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2298 ± 0.0317 → 0.2114 ± 0.0228 | 0.9746 ± 0.0147 → 0.9788 ± 0.0112 | 0.4567 ± 0.0915 → 0.3827 ± 0.0722 | 0.7585 ± 0.0244 → 0.7369 ± 0.0181 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.1927 ± 0.0294 → 0.1751 ± 0.0202 | 0.9968 ± 0.0047 → 0.9968 ± 0.0047 | 0.0279 ± 0.0133 → 0.0269 ± 0.0139 | 0.6501 ± 0.0033 → 0.6499 ± 0.0033 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__mobile` | 1 | 0.1623 ± 0.0000 → 0.1583 ± 0.0000 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0144 ± 0.0000 → 0.0144 ± 0.0000 | 0.6484 ± 0.0000 → 0.6484 ± 0.0000 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.1917 ± 0.0433 → 0.1721 ± 0.0606 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0163 ± 0.0100 → 0.0154 ± 0.0224 | 0.6488 ± 0.0023 → 0.6486 ± 0.0052 |
| `teacher/efficientnetv2_m` | 5 | 0.2238 ± 0.0336 → 0.2174 ± 0.0151 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0356 ± 0.0269 → 0.0337 ± 0.0290 | 0.6534 ± 0.0064 → 0.6529 ± 0.0069 |

## Coverage

Scored folds: 26. Skipped (no `val_predictions.csv`): 0.

