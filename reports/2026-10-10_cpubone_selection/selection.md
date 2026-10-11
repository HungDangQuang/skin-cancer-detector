# Kết quả chọn ứng viên — chỉ dùng val

Luật: docs/PREREG_CANDIDATE2_2026-10-02.md §4 + §7.1 (validation only). Checkpoint tag `_auprc`. Sinh lúc 2026-10-10T19:16:49+00:00.
Script chỉ đọc `val_predictions*.csv`, `val_split.csv`, `val_metrics*.json`.

| Ứng viên | Run-dir | AUPRC val PAD (TB 5 fold) | fold_0 | fold_1 | fold_2 | fold_3 | fold_4 |
|---|---|---|---|---|---|---|---|
| P0 | `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 0.8831 | 0.9146 (219/403) | 0.8593 (168/351) | 0.8326 (137/359) | 0.9144 (166/395) | 0.8946 (198/373) |
| P3 | `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_cpubone_b1__srcsamp` | 0.8766 | 0.9136 (219/403) | 0.8538 (168/351) | 0.7919 (137/359) | 0.9186 (166/395) | 0.9052 (198/373) |

Ô fold: AUPRC (số ca ác / số hàng PAD của val).

**Chọn: P0** — highest score (0.8831).

**Fold ship: fold_4** — trung vị AUPRC toàn bộ val (`val_metrics_auprc.json`) của P0: fold_2 0.6296 · fold_1 0.6616 · fold_4 0.7018 · fold_0 0.7688 · fold_3 0.7691.
