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

### 2. Recompute pAUC if predictions are saved

The `pauc_at_tpr80` field in every JSON is computed by [src/evaluation/metrics.py:37](../../../src/evaluation/metrics.py#L37) and lives on a stretched ~[0.9, 5.0] scale (see [project_pauc_metric_bug.md](../../../memory/project_pauc_metric_bug.md)).

**Recompute path (preferred).** If a `.npz` with `y_true` + `y_prob` sits next to the JSON (e.g. `reports/results/kd_b0.npz`), recompute the ISIC-correct pAUC:

```python
# Run with: python - <path-to-npz>
import sys, numpy as np
from pathlib import Path
from sklearn.metrics import roc_auc_score

def recompute_pauc(npz_path: Path, min_tpr: float = 0.80) -> float:
    """ISIC 2024 pAUC@TPR>=min_tpr in [0, 1-min_tpr]. Trick: invert
    labels+scores so 'max_fpr<=0.2' on sklearn becomes 'TPR>=0.8' on us.
    sklearn returns McClish-corrected pAUC in [0.5, 1.0]; convert back to raw."""
    d = np.load(npz_path)
    y_true, y_prob = d["y_true"], d["y_prob"]
    max_fpr = 1 - min_tpr
    a_c = roc_auc_score(1 - y_true, -y_prob, max_fpr=max_fpr)
    return float(max_fpr * (2 * a_c - 1))   # raw [0, 0.2]

print(f"{recompute_pauc(Path(sys.argv[1])):.4f}")
```

**Fallback path.** If no `.npz` is present (the default — [src/evaluation/evaluator.py:68](../../../src/evaluation/evaluator.py#L68) strips arrays before writing JSON and never stashes `_y_prob` at all):
- Quote `pauc_at_tpr80` verbatim in the metric table but tag it `(stretched scale — see caveats)`.
- Drive the verdict from `auc_roc` (correct) plus threshold-based `sensitivity`, `specificity`, `f1_score`, `accuracy`.
- In "Next steps", tell the user how to enable recomputation on future runs:
  > Patch `src/evaluation/evaluator.py` so `save_metrics` also writes a sibling `.npz` with `y_true` and `y_prob` arrays. That requires the evaluator to keep `_y_prob` in the metrics dict (it currently only keeps `_y_pred`). One-line change in `Evaluator.evaluate` + a `np.savez` in `save_metrics`.

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
| **Corrected pAUC@TPR80** (if §2 recompute succeeded) | ≥ 0.13 | 0.08–0.13 | < 0.08 |

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
- If a baseline file is requested but doesn't exist, stop and tell the user: the baseline arm is currently blocked by `KDTrainer` unconditionally reading `cfg.training.distillation` — see [project_baseline_kd_coupling.md](../../../memory/project_baseline_kd_coupling.md). Submitting `12_train_student.slurm STUDENT=... TRAINING=baseline` will crash until that's fixed. Don't invent baseline numbers.
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
| pauc_at_tpr80_corrected | … | … | … | … |   ← if §2 recompute succeeded
| pauc_at_tpr80 (raw, stretched) | … | … | … | … | ← always show for traceability
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
- Corrected pAUC: <or "(stretched-scale fallback — not scored)">

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

- **`pauc_at_tpr80` in the JSON is on a stretched [~0.9, 5.0] scale**, not the documented [0, 0.2]. See [project_pauc_metric_bug.md](../../../memory/project_pauc_metric_bug.md). Use it only for relative trend within a single source; never quote it as "the ISIC 2024 metric".
- **Predictions are not saved by default.** `Evaluator.save_metrics` strips arrays and never stores `_y_prob`. Without a sibling `.npz`, pAUC analysis is bounded by the broken metric. The fix is a one-line change to the evaluator — recommend it in "Next steps".
- **Baseline (no-KD) runs are currently broken.** Mode B's KD-vs-baseline cell has no real baseline numbers until `KDTrainer`'s coupling to `cfg.training.distillation` is fixed. See [project_baseline_kd_coupling.md](../../../memory/project_baseline_kd_coupling.md). Refuse to invent a baseline.
- **`20_evaluate.slurm` always evaluates fold 0.** It calls `scripts/evaluate.py` without forwarding `--fold`, so the default `--fold 0` applies regardless of what was trained. For a true 5-fold report, either rely on the training-time auto-eval JSONs at `experiments/runs/<run>/fold_*/test_metrics.json`, or extend `20_evaluate.slurm` to accept a `FOLD=` env var. Flag this when the user thinks they're getting a different fold.
- **Single-checkpoint variance is large.** Same architecture × different seed can move sens by 0.05+. Always recommend the 5-fold sweep before quoting numbers in the thesis.
- **`accuracy` is misleading at ISIC class imbalance.** Majority-class baseline ≈ 0.995. Never rank or verdict on raw accuracy — always anchor against the floor.
- **Don't quote `val_pauc`** — that's the training-log metric, biased by early stopping. This skill reads the *test* JSON. If only val numbers are available, use `assess-training` instead.
- **`config.yaml` saved in the run dir is authoritative**, not `configs/`. Hydra overrides at submit time can shift hyperparams.
- **Multi-checkpoint comparison requires matching data + augmentation.** If the saved `config.yaml` differs in augmentation or fold composition between inputs, the comparison is confounded — flag it and refuse to call a winner.
