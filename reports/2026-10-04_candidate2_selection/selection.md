# Kết quả chọn ứng viên — chỉ dùng val

Luật: docs/PREREG_CANDIDATE2_2026-10-02.md §4 + §7.1 (validation only). Checkpoint tag `_auprc`. Sinh lúc 2026-10-04T00:28:21+00:00.
Script chỉ đọc `val_predictions*.csv`, `val_split.csv`, `val_metrics*.json`.

| Ứng viên | Run-dir | AUPRC val PAD (TB 5 fold) | fold_0 | fold_1 | fold_2 | fold_3 | fold_4 |
|---|---|---|---|---|---|---|---|
| P0 | `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | 0.8831 | 0.9146 (219/403) | 0.8593 (168/351) | 0.8326 (137/359) | 0.9144 (166/395) | 0.8946 (198/373) |
| P1 | `experiments/runs_newsplit_ddi/kd_convnextv2_base_to_mobilenetv4_conv_medium__srcsamp` | 0.8840 | 0.9161 (219/403) | 0.8771 (168/351) | 0.8069 (137/359) | 0.9256 (166/395) | 0.8944 (198/373) |
| P2 | `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_repvit_m1_0__srcsamp` | 0.8536 | 0.8685 (219/403) | 0.8458 (168/351) | 0.7654 (137/359) | 0.8922 (166/395) | 0.8962 (198/373) |

Ô fold: AUPRC (số ca ác / số hàng PAD của val).

**Chọn: P0** — tie rule §7.1: P0 (0.8831) is listed before P1 (0.8840) and trails it by 0.0009 < 0.005.

**Fold ship: fold_4** — trung vị AUPRC toàn bộ val (`val_metrics_auprc.json`) của P0: fold_2 0.6296 · fold_1 0.6616 · fold_4 0.7018 · fold_0 0.7688 · fold_3 0.7691.
