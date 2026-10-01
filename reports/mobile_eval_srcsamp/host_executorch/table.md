# Evaluation table — arm `host-executorch`

Runtime: **executorch-1.5.1** · batch **1** · device **cpu**
Frozen threshold: **0.227249** (source: `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp/fold_4/val_predictions_auprc.csv`)

Structure is fixed by `docs/MOBILE_EVAL_PIPELINE.md` §6 so this table can be laid beside the other arm's. Rank-free metrics are marked †: a delta there can only come from the runtime, never from a threshold crossing.

| dataset | n | prevalence | auprc† | pauc_at_tpr80† | auc_roc† | sens_at_90spec† | sens_at_95spec† | sensitivity | specificity | f1_score | brier | ece |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `indomain` | 59093 | 0.0045 | 0.6588 | 0.1837 | 0.9828 | 0.9585 | 0.9208 | 0.9283 | 0.9451 | 0.1315 | 0.0127 | 0.0721 |
| `ham10000_headline` | 7470 | 0.1565 | 0.5793 | 0.1276 | 0.8807 | 0.6133 | 0.4251 | 1.0000 | 0.0927 | 0.2903 | 0.2264 | 0.3550 |
| `fitzpatrick17k_headline` | 4320 | 0.5000 | 0.7246 | 0.0617 | 0.7315 | 0.3634 | 0.2384 | 1.0000 | 0.0014 | 0.6670 | 0.2207 | 0.0841 |

AUPRC is **not** comparable across datasets — its random baseline is the prevalence column, which differs by orders of magnitude here. Across datasets use `auc_roc` / `pauc_at_tpr80`; across arms within one dataset every column is fair.
