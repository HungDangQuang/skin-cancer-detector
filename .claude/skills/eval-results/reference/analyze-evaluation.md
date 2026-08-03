---
name: analyze-evaluation
description: Analyze evaluation JSON files produced by `slurm/20_evaluate.slurm` (Section 5 of slurm/README.md) and rendered to a verdict. Two modes — single-result verdict, multi-result comparison (KD vs baseline / cross-student / teacher vs student). Use when the user shares a `reports/results/*.json` path, says "is this checkpoint good", "did KD help", "compare students", or downloads eval JSONs from the cluster. NOT for triaging a failed training run (use `diagnose-training`) and NOT for judging a still-running training log (use `assess-training`).
---

# analyze-evaluation

Reads the JSON files that `slurm/20_evaluate.slurm` writes to `reports/results/` and renders a verdict. The user's workflow is:

1. Train a checkpoint (auto-eval already wrote `experiments/runs/<run>/fold_N/test_metrics.json` on the cluster).
2. Optionally re-evaluate explicitly via `bash slurm/submit.sh slurm/20_evaluate.slurm MODEL=... CKPT=... OUT=reports/results/<name>.json`.
3. `rsync` the JSON(s) back to the laptop.
4. This skill reads them and produces the verdict.

## When to use

- User shares a path under `reports/results/` (or `experiments/runs/.../test_metrics.json`).
- User asks "is this checkpoint good", "did KD help", "compare students", "which model wins".
- User just finished a `20_evaluate.slurm` job and downloaded the JSON.

## When NOT to use

- Training crashed / NaN'd / never started learning → `diagnose-training`.
- Training is still running, or finished but the user only has the SBATCH `.out` log (no JSON yet) → `assess-training`.
- User wants to *set up* the KD-vs-baseline comparison (submit jobs, design the experiment) → `kd-experiment`. This skill reads the result *afterwards*.
- The JSON isn't local yet — print the rsync command (see §1) and stop. Do not invent numbers.

## Input layout the skill expects

**Primary path — what Section 5 produces:**
```
reports/results/
  teacher.json              ← e.g. OUT=reports/results/teacher.json
  kd_b0.json                ← OUT=reports/results/kd_b0.json
  kd_mobilenet.json
  kd_mobilevit.json
  baseline_b0.json          ← (once baseline arm is fixed — see Caveats)
```
Each JSON is a flat dict from [src/evaluation/evaluator.py:65](../../../src/evaluation/evaluator.py#L65) with keys: `pauc_at_tpr80`, `auc_roc`, `threshold`, `sensitivity`, `specificity`, `precision`, `recall`, `f1_score`, `accuracy`, `tp`, `fp`, `tn`, `fn`. **No fold scoping** — `20_evaluate.slurm` always evaluates a single checkpoint (fold 0 by default; see [scripts/evaluate.py:32](../../../scripts/evaluate.py#L32)).

**Fallback path — auto-eval at the end of training:**
```
experiments/runs/<run_name>/
  fold_{0..4}/test_metrics.json     ← per-fold, same schema as above
  aggregated.json                   ← if scripts/aggregate_folds.py ran
  aggregated.md                     ← thesis-grade markdown table
```
Same schema, fold-scoped. If the user happens to have these (e.g. they rsync'd the whole `experiments/runs/` dir), use them — `aggregated.json` is the gold standard because it carries 5-fold mean ± std.

If the path the user names doesn't exist locally, stop and print:
```bash
# From the laptop. Pull just the eval JSON(s) — small, no checkpoints, no logs:
rsync -avh keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/reports/results/ \
    reports/results/

# Or for auto-eval/aggregated artifacts under experiments/:
rsync -av --include='*/' --include='test_metrics.json' --include='aggregated.*' \
    --include='config.yaml' --exclude='*' \
    keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/experiments/runs/<run_name>/ \
    experiments/runs/<run_name>/
```

**Do not download these — you don't need them for evaluation analysis:**
- `checkpoints/best_model.pth` — multi-GB, useless locally (no Python on the Mac per `CLAUDE.md`)
- `logs/*.out` / `*_runtime.log` — those drive `assess-training` / `diagnose-training`, not this skill

## How to use

### 1. Mode detection

| User input | Mode |
|---|---|
| One JSON path | **Mode A — single-result verdict** |
| Two or more JSON paths (or a directory of JSONs) | **Mode B — multi-result comparison** |
| A `<run_dir>` containing `aggregated.json` | **Mode A** but report mean ± std and call it the thesis-grade tier |
| A `<run_dir>` with `fold_*/test_metrics.json` but no `aggregated.json` | Recommend `bash slurm/submit.sh slurm/22_aggregate_folds.slurm RUN_DIR=<run_dir>` first, OR aggregate inline (read all folds, compute mean/std) and label the report "ad-hoc aggregation" |

For Mode B, ask the user to **label** each file if the names don't clearly say what they are (`teacher.json`, `kd_b0.json`, `baseline_b0.json` are self-evident; `metrics_final.json` is not). The labels drive the comparison rows in the report.

### 2. pAUC is correct + predictions are saved (recompute is optional)

The `pauc_at_tpr80` field in every JSON is computed by [src/evaluation/metrics.py](../../../src/evaluation/metrics.py)`::pauc_at_tpr` and (since 2026-06-04) is the **real ISIC 2024 metric** — McClish-corrected, range ≈ `[0.02, 0.20]`. Quote it verbatim. Only JSONs produced *before* 2026-06-04 are on the old stretched `[0.9, 5.0]` scale (see [project_pauc_metric_bug.md](../../../memory/project_pauc_metric_bug.md)); re-evaluate those checkpoints.

`Evaluator.save_predictions` now writes a sibling **`predictions.csv`** (`y_true, y_prob, y_pred[, source]`) next to every `test_metrics.json`. Use it for anything the scalar JSON can't give you — PR-curve / **AUPRC** / per-domain (ISIC vs PAD) breakdowns / bootstrap CIs — recomputed offline without re-running inference:

```python
import pandas as pd, numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

df = pd.read_csv("experiments/runs/<run>/fold_0/predictions.csv")
y, p = df["y_true"].values, df["y_prob"].values
print("AUPRC", average_precision_score(y, p), "(base", y.mean(), ")")
# per-domain (PAD = smartphone-domain generalization, the decisive ablation cell):
for src, g in df.groupby("source"):
    print(src, "AUPRC", average_precision_score(g.y_true, g.y_prob))
```

At ~0.4 % prevalence, **AUPRC is the honest headline** (AUC-ROC is optimistic); `prevalence` in the JSON is its random baseline.

### 3. Mode A — single-result verdict

Read the JSON. Anchor on the prevalence floor — ISIC 2024's test split is ~0.5% malignant, so majority-class accuracy floor is ~0.995. **`accuracy` alone means nothing at this imbalance**; always anchor it against the floor.

Scoring rubric on the test set (slightly stricter than training-time val):

| Axis | Good | Moderate | Poor |
|---|---|---|---|
| **AUC-ROC** | ≥ 0.92 | 0.85–0.92 | < 0.85 |
| **Sensitivity** (catches malignants — domain-critical) | ≥ 0.85 | 0.70–0.85 | < 0.70 |
| **Specificity** | ≥ 0.85 | 0.70–0.85 | < 0.70 |
| **F1** (imbalance-aware) | ≥ 0.75 | 0.55–0.75 | < 0.55 |
| **Accuracy vs majority-class floor** | > floor + 5pp | within ±5pp | below floor |
| **pAUC@TPR80** (ISIC metric, ≈[0.02,0.20]) | ≥ 0.13 | 0.08–0.13 | < 0.08 |
| **AUPRC** (vs prevalence base) | clears base by a wide margin | modestly above base | ≈ base |

Aggregate verdict:
- **Good** — promote; if not yet thesis-reported, run the 5-fold sweep next to get mean ± std before quoting externally.
- **Moderate** — usable, but identify the weakest axis and recommend the lever (see §3a).
- **Poor** — re-check `experiments/<run>/config.yaml` first (the run's authoritative config), then consult `diagnose-training` if the training itself looks wrong.

**A single result is high-variance.** A different seed/fold can move sens by 0.05+. Close every Mode A verdict with: "this is one checkpoint; run the 5-fold sweep + `22_aggregate_folds.slurm` before quoting in the thesis."

#### 3a. Suggesting levers (Mode A)

If the verdict is Moderate or Poor, point to ONE config file per recommendation so the user can locate the lever:
- Low sensitivity → focal-loss `alpha` toward minority / lower threshold / raise malignant ratio in `DynamicUndersampledSampler` → `configs/training/*.yaml`
- Low specificity → opposite; raise threshold / heavier augmentation on benign → `configs/augmentation/heavy.yaml`
- Low AUC-ROC despite OK sens/spec → backbone may be under-capacity or training stopped early → `configs/training/*.yaml` (epochs / patience)
- KD-specific: weak signal from teacher → `configs/training/distillation.yaml` (`temperature`, `alpha`)

### 4. Mode B — multi-result comparison

Inputs: 2+ JSONs the user wants compared. Cover three sub-cases:

| Sub-case | Files |
|---|---|
| **KD vs baseline (same student)** | e.g. `kd_b0.json` + `baseline_b0.json` |
| **Cross-student** | `kd_b0.json` + `kd_mobilenet.json` + `kd_mobilevit.json` |
| **Teacher vs student** | `teacher.json` + `kd_<student>.json` |

**Gating check first.**
- If a baseline file is requested but doesn't exist, don't invent numbers — tell the user to produce it: `bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=... TRAINING=baseline` (the baseline arm works via the `use_kd` flag, fixed 2026-06-04; run-dir `baseline_<student>/`). See [project_baseline_kd_coupling.md](../../../memory/project_baseline_kd_coupling.md).
- If the inputs are clearly different splits / data / augmentation (read each run's saved `config.yaml` if present), flag it and refuse to call a winner — the comparison is confounded.

**Build a unified table.** Always include every numeric field in the source JSON — never drop a column because the rubric doesn't use it.

```
## Comparison
Files compared:
- <label A>: <path A>
- <label B>: <path B>
- ...

| metric | <label A> | <label B> | … | Δ (vs <baseline label>) |
|---|---|---|---|---|
| auc_roc | … | … | … | … |
| sensitivity | … | … | … | … |
| specificity | … | … | … | … |
| f1_score | … | … | … | … |
| accuracy | … | … | … | … |
| precision | … | … | … | … |
| recall | … | … | … | … |
| pauc_at_tpr80 | … | … | … | … |   ← real ISIC metric, ≈[0.02,0.20] (tag "(pre-2026-06-04 stretched scale)" only for old JSONs)
| auprc (base=prevalence) | … | … | … | … | ← headline at ~0.4% prevalence
| threshold | … | … | … | — |
| tp / fp / tn / fn | … | … | … | — |
```

Pick a baseline column for the Δ:
- KD-vs-baseline → baseline is the no-KD run.
- Cross-student → no implicit baseline; rank instead (see below) and omit the Δ column or compute Δ vs the leader.
- Teacher vs student → baseline is the teacher (judges KD efficacy: a student close to the teacher is doing well).

**Significance heuristic (for KD-vs-baseline only).** Without 5-fold std we can't bound noise. Quote the delta and warn: "single-checkpoint delta — run 5 folds via the array jobs before drawing a conclusion." Do not call it "robust" or "significant" on n=1.

**If the user has 5 folds for each run** (fed as multiple JSONs labeled `<label>_fold<i>.json`, or auto-detected from `experiments/runs/<run>/fold_*/test_metrics.json`), aggregate them into mean ± std per label *before* comparing. Then a pooled-std overlap check is meaningful:
```
pooled_std = sqrt((std_kd**2 + std_baseline**2) / 2)
significance = "robust"   if abs(delta) > 2 * pooled_std
             = "marginal" if abs(delta) > 1 * pooled_std
             = "noise"    otherwise
```
This is a heuristic, not a t-test — language is "robust", "marginal", "noise", never "p<0.05".

**Ranking + verdict rules:**
- For KD-vs-baseline: KD wins if `delta_auc > 0` AND `delta_sens > 0`. If sens worsens, KD did not win regardless of accuracy/specificity gains. (Domain priority: missing a malignant > false alarm.)
- For cross-student: rank by **sensitivity first, then auc_roc**. Don't rank on accuracy — misleading at imbalance.
- For teacher vs student: a Good student is one whose `sens` and `auc_roc` are within ~0.02 of the teacher's. Bigger gap → KD didn't transfer well.
- Note any Pareto-dominated entry (worse on every metric than another) — those are clean losers.

### 5. Common output rules (all modes)

- **Every metric in the source JSON must appear verbatim in the report.** Don't drop columns the rubric doesn't use.
- **Always state which file(s) you read** in the report header so the user can reopen them.
- **Always state the data tier:** aggregated 5-fold > single-checkpoint test JSON. A single Section-5 JSON is the lower tier — say so.
- **Round to 4 decimal places** to match `aggregate_folds.py`'s markdown convention. Don't synthesize precision the source didn't have.
- **Unknown metrics get listed too** (if a calibration metric like ECE gets added later, list it with `(no rubric — listed for completeness)`).
- **Cite the saved `config.yaml`**, not `configs/`, for any "which hyperparams produced this" claim — Hydra overrides at submit time can shift hyperparams; the saved per-run config is authoritative.

### 6. Report template

```
Verdict: <Good | Moderate | Poor>   (Mode A only)
Data tier: <Aggregated 5-fold | Single-checkpoint test JSON>
Files read:
- <path 1>
- <path 2>   (if comparing)

## All recorded metrics
<table — every key from every input JSON, verbatim, 4 dp>

Class-prevalence floor:
- Test set positive rate: <if known, else "ISIC 2024 default ≈ 0.5%">
- Majority-class baseline accuracy: <approx 0.995 for ISIC 2024>
- Random-classifier AUC: 0.5000

## Per-axis scoring   (Mode A — for each axis in the rubric)
- AUC-ROC: <good/mod/poor> — <one-line cite from data>
- Sensitivity (skin-cancer critical): …
- Specificity: …
- F1: …
- Accuracy vs floor: …
- pAUC@TPR80 (≈[0.02,0.20]): …
- AUPRC (vs prevalence base): …

## Ranking + delta   (Mode B)
- Ranking by sensitivity → auc_roc: <ordered list>
- KD effect (if applicable): <delta values + heuristic significance or "single-checkpoint — re-run 5 folds">
- Pareto winners / losers: <…>

## Recommendations
1. <highest-impact lever> — touches <configs/path/file.yaml>
2. <second> — touches <…>
3. <optional third>

Next steps:
- <"Run 5-fold sweep" / "Aggregate the existing folds via 22_aggregate_folds.slurm" / "Patch evaluator to save predictions" / "Fix baseline arm before re-attempting comparison">

## Caveats applied
- <pauc bug? single-checkpoint variance? missing baseline? confounded augmentation? unknown class prevalence?>
```

## Caveats

- **`pauc_at_tpr80` is the real ISIC 2024 metric (fixed 2026-06-04)**, range ≈ [0.02, 0.20] — quotable as an absolute number. Only JSONs produced *before* 2026-06-04 are on the old stretched [0.9, 5.0] scale. See [project_pauc_metric_bug.md](../../../memory/project_pauc_metric_bug.md).
- **Predictions ARE saved (since 2026-06-21).** `Evaluator.save_predictions` writes `predictions.csv` (`y_true,y_prob,y_pred[,source]`) next to each `test_metrics.json` — recompute AUPRC / PR-curve / per-domain / bootstrap CIs from it. The scalar `test_metrics.json` already carries `auprc`, `prevalence`, `sens_at_90spec`, `sens_at_95spec`.
- **Baseline (no-KD) runs work (fixed 2026-06-04).** Mode B's KD-vs-baseline cell has real baseline numbers via the `use_kd` flag (`training=baseline` → plain `Trainer`, run-dir `baseline_<student>/`). See [project_baseline_kd_coupling.md](../../../memory/project_baseline_kd_coupling.md).
- **`20_evaluate.slurm` always evaluates fold 0.** It calls `scripts/evaluate.py` without forwarding `--fold`, so the default `--fold 0` applies regardless of what was trained. For a true 5-fold report, either rely on the training-time auto-eval JSONs at `experiments/runs/<run>/fold_*/test_metrics.json`, or extend `20_evaluate.slurm` to accept a `FOLD=` env var. Flag this when the user thinks they're getting a different fold.
- **Single-checkpoint variance is large.** Same architecture × different seed can move sens by 0.05+. Always recommend the 5-fold sweep before quoting numbers in the thesis.
- **`accuracy` is misleading at ISIC class imbalance.** Majority-class baseline ≈ 0.995. Never rank or verdict on raw accuracy — always anchor against the floor.
- **Don't quote `val_pauc`** — that's the training-log metric, biased by early stopping. This skill reads the *test* JSON. If only val numbers are available, use `assess-training` instead.
- **`config.yaml` saved in the run dir is authoritative**, not `configs/`. Hydra overrides at submit time can shift hyperparams.
- **Multi-checkpoint comparison requires matching data + augmentation.** If the saved `config.yaml` differs in augmentation or fold composition between inputs, the comparison is confounded — flag it and refuse to call a winner.
