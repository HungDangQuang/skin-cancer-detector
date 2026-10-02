# Val-frozen vs test-Youden threshold metrics — `/workspace/skin-cancer-detector/experiments/runs_newsplit_ddi`

Predictions: `fold_*/predictions_auprc.csv`; threshold source: `fold_*/val_predictions_auprc.csv` (Youden's J on that fold's own val set).

`testthr_*` reproduces what `test_metrics*.json` reports (threshold fitted on the test set — optimistic). `valthr_*` is the honest counterpart (threshold frozen before seeing the test labels). Mean ± std over the folds of each run; the std is the spread between the fold models, not a confidence interval. Ranking metrics do not depend on a threshold and are not repeated here.

## Group `all`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2219 ± 0.0385 → 0.2076 ± 0.0450 | 0.9034 ± 0.0244 → 0.9064 ± 0.0344 | 0.9230 ± 0.0102 → 0.9053 ± 0.0257 | 0.0961 ± 0.0099 → 0.0833 ± 0.0213 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2024 ± 0.0424 → 0.1870 ± 0.0276 | 0.9291 ± 0.0147 → 0.9268 ± 0.0157 | 0.9482 ± 0.0102 → 0.9407 ± 0.0140 | 0.1413 ± 0.0212 → 0.1270 ± 0.0259 |

## Group `isic2024`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2219 ± 0.0385 → 0.2076 ± 0.0450 | 0.7395 ± 0.0729 → 0.7368 ± 0.0989 | 0.9249 ± 0.0103 → 0.9073 ± 0.0259 | 0.0249 ± 0.0022 → 0.0209 ± 0.0039 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2024 ± 0.0424 → 0.1870 ± 0.0276 | 0.7553 ± 0.0480 → 0.7500 ± 0.0483 | 0.9515 ± 0.0102 → 0.9439 ± 0.0140 | 0.0395 ± 0.0056 → 0.0347 ± 0.0074 |

## Group `pad_ufes_20`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2219 ± 0.0385 → 0.2076 ± 0.0450 | 0.9693 ± 0.0165 → 0.9746 ± 0.0147 | 0.4087 ± 0.1788 → 0.3635 ± 0.1711 | 0.7431 ± 0.0498 → 0.7315 ± 0.0491 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 5 | 0.2024 ± 0.0424 → 0.1870 ± 0.0276 | 0.9989 ± 0.0024 → 0.9979 ± 0.0047 | 0.0154 ± 0.0129 → 0.0163 ± 0.0139 | 0.6481 ± 0.0023 → 0.6479 ± 0.0023 |

## Coverage

Scored folds: 10. Skipped (no `val_predictions_auprc.csv`): 0.

