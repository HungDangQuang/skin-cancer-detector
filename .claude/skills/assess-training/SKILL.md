---
name: assess-training
description: Read a finished training-run log, score the result (good/moderate/poor), and recommend high-level changes to improve the next run. Use when the user shares a log/job id and asks "is this any good", "how do I improve", "should I train longer / change LR / change aug", or wants a verdict on a *successful* run. NOT for failure triage — use `diagnose-training` if the job crashed, NaN'd, or never started learning.
---

# assess-training

Reads a finished training-run log, derives a verdict on the result, and produces a ranked list of high-level recommendations for the next run. Designed for the case where training *worked* but you want to know "is this good enough, and what should I change next?"

## When to use

- A training job completed (`[job] DONE`) and the user wants a verdict on the result.
- User shares a `logs/<jobname>_<jobid>.out` or `logs/<jobname>_<jobid>_runtime.log` path.
- User asks "should I train longer", "is this overfitting", "what should I tune next".
- User wants to know whether to push the current checkpoint to evaluation or iterate further.

## When NOT to use

- The job failed, crashed, or `val_pauc` is stuck at 0/random across all epochs → use `diagnose-training`.
- The user is asking about a checkpoint's performance on the *test* set → run `slurm/20_evaluate.slurm` first, then assess the resulting JSON, not the training log.
- Cross-run comparison (KD vs baseline, model A vs B) → use `kd-experiment`.

## How to use

### 0. Prefer the test-set JSON over the training log

Each training run now auto-evaluates the best checkpoint on the held-out test split and writes `experiments/<run>/fold_<N>/test_metrics.json`. **That JSON is the unbiased number** — the val-set metrics in the training log are optimistic because early-stopping/checkpoint-selection optimizes against val. Order of preference:

1. **`<run_dir>/aggregated.json` + `aggregated.md`** — if the full 5-fold sweep finished and `scripts/aggregate_folds.py` ran, this contains mean ± std and is the only thesis-grade signal.
2. **`<run_dir>/fold_<N>/test_metrics.json`** — single-fold unbiased number. Honest, but high variance (one fold).
3. **Per-epoch val log lines** — only as a fallback when the JSONs aren't there, or for "did training converge / overfit / plateau" trajectory analysis.

Always say in your report which tier of data you're judging from, because the confidence implied is different (aggregated >> single-fold test >> val-log only).

### 1. Locate the log

```bash
# By job id (most reliable):
ls logs/ | grep -E "_${JOBID}\."
# Returns one of:
#   logs/<jobname>_<JOBID>.out          ← SBATCH stdout
#   logs/<jobname>_<JOBID>_runtime.log  ← fallback tee log (always exists)
```

If the SBATCH `.out` is empty (Slurm 23 silently drops output when `logs/` doesn't exist at parse time), fall back to the `_runtime.log` — it is always written via `tee` inside `slurm/_lib.sh`.

### 2. Extract per-epoch metrics

The training scripts log one line per epoch. Format depends on the trainer:

**Teacher (`src/training/trainer.py`):**
```
Epoch N/E | train_loss=X | val_loss=Y val_pauc=P acc=A sens=S spec=Sp f1=F
```

**KD student (`src/training/kd_trainer.py`):**
```
Epoch N/E | train_loss=X (hard=H, soft=Z) | val_loss=Y val_pauc=P acc=A sens=S spec=Sp f1=F
```

Extract them cleanly (tqdm progress bars in the log can blow up `cat`/`head` — filter them out):

```bash
LOG="logs/<jobname>_<jobid>.out"

# Per-epoch summary lines (drop tqdm and INFO/DEBUG noise):
grep -aE "Epoch [0-9]+/[0-9]+" "$LOG" | grep -v "it/s" | sort -u

# Best-saved-checkpoint markers (each one is a new "best" epoch):
grep -aE "Saved best model \(epoch [0-9]+" "$LOG" | sort -u

# Did training stop early or run to completion?
grep -aE "Early stopping triggered|\[job\] DONE" "$LOG"
```

### 3. Apply the verdict rubric

Score the run on three axes — **convergence**, **discrimination**, **stability** — using the *threshold-based* metrics (`acc`, `sens`, `spec`, `f1`) and the train/val loss trajectory. **Do NOT use `val_pauc` for absolute judgment** until the metric bug is fixed (see Caveats below); use it only for relative trend within the same run.

**Always anchor discrimination numbers to the prevalence baseline.** The trainer logs `Val set: N benign + N malignant (X% positive) | majority-class baseline acc=...` at the start of every run. If reported `acc=0.95` and the majority-class baseline is `0.99`, the model is *worse than predict-all-benign*. Don't let a high acc deceive you — always compare against the floor logged for that run.

| Axis | Good | Moderate | Poor |
|---|---|---|---|
| **Convergence** (train_loss trajectory) | Monotonic decrease, plateaus by last 20% of epochs | Decreases but still falling at the end | Flat after epoch 3, or increases |
| **Discrimination** (val `f1`, `acc`) | f1 ≥ 0.80, acc ≥ 0.90 with class-imbalance-aware reading | f1 0.60–0.80 | f1 < 0.60 |
| **Sensitivity** (val `sens`) — domain-critical for skin cancer | sens ≥ 0.85 (catches most malignants) | sens 0.70–0.85 | sens < 0.70 (misses too many positives) |
| **Specificity** (val `spec`) | spec ≥ 0.85 with sens still high | spec 0.70–0.85 | spec < 0.70 (too many false alarms) |
| **Generalization gap** (`val_loss − train_loss` in last 5 epochs) | gap small, val_loss flat or decreasing with train_loss | gap growing slowly | val_loss rising while train_loss drops → overfitting |
| **Stability** (val_pauc / val_loss epoch-over-epoch variance) | smooth or near-monotonic | small oscillations | wild swings between adjacent epochs |
| **Early stopping** | did not trigger (model still had room) OR triggered well after best epoch | triggered shortly after best epoch | triggered very early (training didn't get to use the schedule) |

For KD runs, also check:
- `soft_loss` and `hard_loss` should both be > 0 and trending down. If `soft_loss` is flat from epoch 1, the teacher's signal isn't helping — teacher may be miscalibrated or `temperature` too high.
- `hard_loss` ≪ `soft_loss` is normal when `alpha=0.3` (hard weight 0.3 vs soft 0.7) — that's the configured weighting in `configs/training/distillation.yaml`, not a bug.

Aggregate verdict:
- **Good** — promote to test evaluation (`slurm/20_evaluate.slurm`). Don't keep tuning.
- **Moderate** — try one targeted change from §4 and re-train.
- **Poor** — multiple axes failing; usually a setup issue. Re-check `experiments/<run>/config.yaml` first, then consult `diagnose-training`.

### 4. Recommendations — match symptoms to high-level levers

For each symptom that's failing, suggest ONE direction at a time (changing many things at once makes it impossible to attribute the effect).

| Symptom in the log | High-level direction |
|---|---|
| `val_loss` diverges from `train_loss` (overfitting) | Stronger augmentation; more regularization (dropout / weight decay); shorter schedule or earlier stopping; smaller effective LR |
| Both losses plateau early and stay flat (underfitting) | Train longer; unfreeze more of the backbone; raise the head LR; reconsider whether the backbone is being initialized correctly |
| Loss drops but `val_pauc` / `f1` does not improve | Decision threshold is mis-set — re-check `youden_threshold` selection; or class collapse — inspect prediction distribution; or evaluation set too tiny to be representative |
| Low **sensitivity** (misses malignants) | Increase focal-loss `alpha` toward the minority class; raise the malignant ratio in `DynamicUndersampledSampler`; lower the decision threshold; consider class-weighted loss |
| Low **specificity** (too many false alarms) | Inverse of above — reduce minority oversampling; raise threshold; try heavier augmentation on benign class to discourage overfitting to benign features |
| `val_pauc` swings wildly epoch-to-epoch | Lower LR; larger batch; less aggressive scheduler; for POC this is expected (small val set) |
| Early stopping triggers at epoch 1–5 | Patience too tight, OR optimizer state bad, OR LR way too high; check the warmup_epochs setting |
| Training ran the full schedule with metric still improving at the end | Increase epochs; or extend the cosine `T_max` so the LR doesn't decay to zero mid-improvement |
| KD `soft_loss` flat from epoch 1 | Teacher signal not informative — verify teacher checkpoint path; try lower distillation `temperature`; consider re-training a stronger teacher |
| KD-student worse than baseline-student | Distillation weight wrong (try shifting `alpha` toward 0.5); temperature too high; teacher itself is weak |

For each suggestion, name the **configs/** file(s) that control the relevant lever so the user knows where to look:
- LR / weight decay / optimizer → `configs/training/{distillation,baseline,default}.yaml`
- Augmentation strength → `configs/augmentation/{light,heavy}.yaml` (and the `augmentation=heavy` Hydra override)
- KD `temperature` / `alpha` → `configs/training/distillation.yaml`'s `distillation:` block
- Early stopping `patience` / monitor → `configs/training/*.yaml`'s `callbacks.early_stopping`

### 5. Report format

Give the user a structured response. **Every metric value present in the source must appear verbatim in the report** — never quote only the axes you scored on, never round away precision the source had, never drop fields because you didn't use them in the verdict. The user (and their thesis reader) needs to see what was actually recorded.

```
Verdict: <Good | Moderate | Poor>
Data tier: <Aggregated 5-fold | Single-fold test JSON | Val-log only>
Source: <path/to/aggregated.md or test_metrics.json or logs/…>

## All recorded metrics (verbatim from source)
| metric | value (or mean ± std for aggregated) |
|---|---|
| pauc_at_tpr80 | … |
| auc_roc | … |
| accuracy | … |
| precision | … |
| recall | … |
| sensitivity | … |
| specificity | … |
| f1_score | … |
| threshold | … |
| tp / fp / tn / fn | … / … / … / … |
| <any other key the source has> | … |

Class-prevalence floor (for anchoring accuracy claims):
- Val set: <N_negative> benign + <N_positive> malignant (<positive_rate>% positive)
- Majority-class baseline acc: <X.XXXX>
- Random-classifier AUC: 0.5000

## Per-axis scoring
- Convergence: <good/mod/poor> — <one-line reason from data>
- Discrimination (anchored vs floor): <…>
- Sensitivity / Recall (skin-cancer critical): <…>
- Specificity / Precision (false-alarm rate): <…>
- Generalization gap: <…>
- Stability: <…>

## Recommendations (priority order)
1. <highest-impact lever> — touches <config file>
2. <second> — touches <config file>
3. <optional third>

Next step: <concrete cluster command or follow-up action>

## Caveats applied
- <pauc bug? POC noise? single-fold variance? missing fields?>
```

**Rules:**
- For aggregated reports, the metric column shows `mean ± std`.
- For single-fold reports, the metric column shows the bare value.
- If a metric is in the source JSON but you don't recognize it (custom additions like calibration/ECE later), still list it — say "(no rubric — listed for completeness)" in the verdict if you can't score it.
- Always cite the **epoch where the peak was reached**, **final values**, **gap size in last 5 epochs** in the per-axis section so the user can verify the reasoning against the log without re-reading it.
- If the source doesn't have a metric (e.g. legacy run from before today's instrumentation) write `(not recorded)` in that row — never silently omit.

## Caveats

- **`val_pauc` is currently mis-scaled.** [src/evaluation/metrics.py:37](../../src/evaluation/metrics.py#L37) integrates raw TPR instead of `(TPR − min_tpr)` and divides by 0.2, so the value lives in roughly `[0.9, 5.0]` instead of the documented `[0, 0.2]`. Until that's fixed, use `val_pauc` only for *relative trend within a single run*; for cross-run comparison and absolute verdict, lean on `acc`, `sens`, `spec`, `f1`. Flag this caveat in the report.
- **POC runs are noisy.** The synthetic POC dataset has ~36 val samples; `val_pauc` and `val_loss` swing a lot from epoch to epoch. Convergence is the only signal worth trusting on POC.
- **POC `acc` near 1.0 is not real-world good.** Synthetic POC images have a learnable color bias — saturating on POC just confirms gradients flow.
- **One bad epoch ≠ broken training.** Early stopping has `patience` for a reason. Look at the trend across the last 5–10 epochs, not single-epoch dips.
- **Always check `experiments/<run>/config.yaml`**, not `configs/`. Hydra overrides at submit time can shift hyperparams; the run's saved config is the authoritative record.
- **Don't recommend changes you can't tie to a symptom in the log.** "Try a bigger model" is not a recommendation — "discrimination axis is poor (f1=0.55), backbone may be under-capacity for this dataset, consider trying the next size up" is.
