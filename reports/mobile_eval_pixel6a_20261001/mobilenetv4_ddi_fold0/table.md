# Evaluation table — arm `mobile`

Runtime: **executorch-android-1.4.0(threads=4)** · batch **1** · device **Pixel 6a (Tensor G1)**
Frozen threshold: **0.158256** (source: `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__mobile/fold_0/val_predictions.csv`)

Structure is fixed by `docs/MOBILE_EVAL_PIPELINE.md` §6 so this table can be laid beside the other arm's. Rank-free metrics are marked †: a delta there can only come from the runtime, never from a threshold crossing.

| dataset | n | prevalence | auprc† | pauc_at_tpr80† | auc_roc† | sens_at_90spec† | sens_at_95spec† | sensitivity | specificity | f1_score | brier | ece |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `indomain` | 59093 | 0.0045 | 0.6182 | 0.1843 | 0.9834 | 0.9585 | 0.9283 | 0.9509 | 0.9366 | 0.1186 | 0.0095 | 0.0436 |
| `ham10000_headline` | 7470 | 0.1565 | 0.4044 | 0.0956 | 0.8049 | 0.4192 | 0.2335 | 0.9957 | 0.0621 | 0.2824 | 0.3270 | 0.4470 |
| `fitzpatrick17k_headline` | 4320 | 0.5000 | 0.5963 | 0.0407 | 0.6176 | 0.1778 | 0.1042 | 1.0000 | 0.0009 | 0.6669 | 0.3214 | 0.2862 |

AUPRC is **not** comparable across datasets — its random baseline is the prevalence column, which differs by orders of magnitude here. Across datasets use `auc_roc` / `pauc_at_tpr80`; across arms within one dataset every column is fair.
