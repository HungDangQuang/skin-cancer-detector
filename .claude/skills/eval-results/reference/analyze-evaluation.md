---
name: analyze-evaluation
description: Render a verdict on finished evaluation artifacts — a run-dir's fold_*/test_metrics.json + aggregated.json, an external-eval tree under reports/external/, a bootstrap-CI report, or an on-demand run/evaluate.sh JSON. Two modes — single-result verdict, multi-result comparison (KD vs baseline / cross-student / teacher vs student). Use when the user says "is this checkpoint good", "did KD help", "compare students", or points at one of those artifacts. NOT for triaging a failed training run (use `diagnose-training`) and NOT for judging a still-running training log (use `assess-training`).
---

# analyze-evaluation

Reads finished evaluation artifacts and renders a verdict. Health/comparison only — the
"meets the requirement" verdict goes through [acceptance-gates.md](acceptance-gates.md) (see the
⛔ block in `../SKILL.md`).

## When to use

- User points at a run-dir (`experiments/runs*/<run>/`), a `fold_N/test_metrics.json`, an
  external-eval tree (`reports/external/<ds>/<variant>/`), or a `reports/bootstrap_ci*.md` / `reports/ci_*.md`.
- User asks "is this checkpoint good", "did KD help", "compare students", "which model wins".
- User just finished a `run/evaluate.sh` job (`OUT=reports/results/<name>.json`).

## When NOT to use

- Training crashed / NaN'd / never started learning → `diagnose-training`.
- Training is still running, or finished but the user only has the `logs/*.log` transcript (no JSON yet) → `assess-training`.
- User wants to *set up* the KD-vs-baseline comparison (submit jobs, design the experiment) → `code-change/reference/kd-experiment.md`. This file reads the result *afterwards*.
- The artifact isn't local yet — say so, give the fetch command (below) and stop. Do not invent numbers.

## Where results live (check which tree before quoting anything)

| Tree | What | Splits |
|---|---|---|
| `experiments/runs_newsplit_{light,ddi}/<run>/` (`runs_newsplit_domain` = the failed `augmentation=domain` arm, preset removed 2026-09-30 — history only) | current arms: `fold_{0..4}/test_metrics.json` (+ `_auprc` twins when `extra_monitors=[auprc]`), `predictions.csv`, `val_*`, `aggregated.{json,md}` | **v2** (patient-grouped) — the only tree that may back an in-domain verdict |
| `experiments/runs/`, `experiments/runs_isic_only/` | the 140-fold matrix + PAD ablation | **v1 — leaked patients**; in-domain numbers inflated (`CLAUDE.md` → Data integrity). Cross-domain AUC/AUPRC/pAUC still usable |
| `reports/external_newsplit_<arm>/<ds>/<variant>/<run_tag>/` (`<arm>` = light, ddi, srcsamp, srcsamp_auprc, …) | HAM10000 / Fitzpatrick17k cross-domain eval of the **v2** arms (`run/evaluate_external.sh`) | **v2** |
| `reports/external/<ds>/<variant>/<run_tag>/fold_N/` + `aggregated.{json,md}` | the same for the **v1** matrix (`experiments/runs/`) | v1 — cross-domain AUC/AUPRC/pAUC usable, threshold metrics optimistic |
| `reports/bootstrap_ci*.md`, `reports/ci_*.md` (+ `.json`) | paired / per-run 95% CIs (`run/bootstrap_ci.sh`) | per the tree it read |
| `reports/results/<name>.json` | on-demand single-checkpoint eval (`bash run/evaluate.sh MODEL=… CKPT=… OUT=…`) — rarely used | per the checkpoint |

`aggregated.json` (5-fold mean ± std) is the gold standard over a single fold. Metric keys come from
`compute_metrics()` in [src/evaluation/metrics.py](../../../../src/evaluation/metrics.py) (`pauc_at_tpr80`,
`auc_roc`, `auprc` + `prevalence`, `sensitivity`/`specificity`/`f1_score`/`threshold` — **Youden on the test set,
optimistic: prefer the `valthr_*` keys** when present — `sens_at_90spec`/`sens_at_80spec`, TP/FP/TN/FN, `brier`/`ece`).
Older JSONs may lack newer keys; say "missing" rather than guessing. Runs trained before the `valthr_*` change have them only in the offline back-fill `reports/valthr/<tree>{,_auprc}.{csv,md}` (`bash run/backfill_valthr.sh`) — use that instead of the test-Youden `sensitivity`/`specificity`; if only test-Youden numbers exist, flag them as optimistic wherever they are used (ranking rule below).

If what the user names isn't on the Mac, don't hand-write rsync — use the project tool, which knows the live host
(default `vastnew`) and never transfers checkpoints by default:
```bash
bash run/pull_results.sh          # check: NEW / STALE / SAME / RUNNING per run-dir
bash run/pull_results.sh pull     # fetch NEW folds (metrics, predictions, configs — no .pth)
```
**Check a CI file's provenance before quoting it.** `reports/{bootstrap_ci,ci}_*.md` name runs by their run-dir
name only, and the same names (`kd_efficientnetv2_m_to_mobilenetv4_conv_medium`, `baseline_…`) exist in several
trees; CI trees built from symlinks use `x_` prefixes, which also disables auto-pairing (`kd_deltas` comes out
empty — use `PAIR=`). Read the report's header / `RESULTS_DIR` line or the `.json`'s source paths, and match a
couple of point estimates against that tree's `aggregated.md`, before attributing a delta to an arm. If no CI
exists for the pair asked about, say so and give the `bash run/bootstrap_ci.sh … PAIR="A:B"` command — do not
substitute a CI from another arm or a difference of fold means.

External-eval and CI reports under `reports/` are produced on the server; if one is missing locally, say which
command produces it (`run/evaluate_external.sh`, `run/bootstrap_ci.sh`) instead of estimating.

## How to use

### 1. Mode detection

| User input | Mode |
|---|---|
| One JSON path | **Mode A — single-result verdict** |
| Two or more JSON paths (or a directory of JSONs) | **Mode B — multi-result comparison** |
| A `<run_dir>` containing `aggregated.json` | **Mode A** but report mean ± std and call it the thesis-grade tier |
| A `<run_dir>` with `fold_*/test_metrics.json` but no `aggregated.json` | Recommend `bash run/aggregate.sh RUN_DIR=<run_dir>` first, OR aggregate inline (read all folds, compute mean/std) and label the report "ad-hoc aggregation" |

For Mode B, ask the user to **label** each file if the names don't clearly say what they are (`teacher.json`, `kd_fastvit_sa12.json`, `baseline_fastvit_sa12.json` are self-evident; `metrics_final.json` is not). The labels drive the comparison rows in the report.

### 2. pAUC is correct + predictions are saved (recompute is optional)

The `pauc_at_tpr80` field in every JSON is computed by [src/evaluation/metrics.py](../../../../src/evaluation/metrics.py)`::pauc_at_tpr` and (since 2026-06-04) is the **real ISIC 2024 metric** — McClish-corrected, range ≈ `[0.02, 0.20]`. Quote it verbatim. Only JSONs produced *before* 2026-06-04 are on the old stretched `[0.9, 5.0]` scale (see memory `project_pauc_metric_bug`); re-evaluate those checkpoints.

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

Read the JSON. Anchor on the prevalence floor — read `prevalence` from the JSON rather than assuming one (splits-v2 in-domain test: 265 / 59,093 ≈ 0.45%; the ~0.39% in `CLAUDE.md` is the whole population; HAM10000 / Fitzpatrick17k are far higher), so the majority-class accuracy floor in-domain is ~0.995. **`accuracy` alone means nothing at this imbalance**; always anchor it against the floor.

> **⛔ This rubric is a HEALTH HEURISTIC, not an acceptance verdict.** Its thresholds (AUC ≥ 0.92,
> sens ≥ 0.85, …) are not sourced, and they are applied to a **pooled** in-domain JSON where an
> "only guess ISIC-vs-PAD" model already reaches AUC 0.872 (v1 test; ~0.85 on v2) — so the v1 matrix
> runs score "Good" on AUC / sens / spec / pAUC here (F1 ≈ 0.12–0.14 is the one axis that reads "Poor").
> A "Good" from this table means *"the run is not broken and is worth comparing"*, **nothing more**.
> If the question is "is the model good enough / đạt chưa / can it ship", stop and use
> [acceptance-gates.md](acceptance-gates.md) — per-domain, CI-based labels, thresholds with a stated
> source and sign-off status.

Health rubric on the test set (slightly stricter than training-time val):

| Axis | Good | Moderate | Poor |
|---|---|---|---|
| **AUC-ROC** | ≥ 0.92 | 0.85–0.92 | < 0.85 |
| **Sensitivity** (catches malignants — domain-critical) | ≥ 0.85 | 0.70–0.85 | < 0.70 |
| **Specificity** | ≥ 0.85 | 0.70–0.85 | < 0.70 |
| **F1** (imbalance-aware) | ≥ 0.75 | 0.55–0.75 | < 0.55 |
| **Accuracy vs majority-class floor** | > floor + 5pp | within ±5pp | below floor |
| **pAUC@TPR80** (ISIC metric, ≈[0.02,0.20]) | ≥ 0.13 | 0.08–0.13 | < 0.08 |
| **AUPRC** (vs prevalence base) | clears base by a wide margin | modestly above base | ≈ base |

Aggregate health verdict (never write it as "đạt yêu cầu" / "ready"):
- **Good** — the run is healthy and worth carrying into comparisons/gates; if not yet thesis-reported, run the 5-fold sweep next to get mean ± std before quoting externally. It is **not** a promotion to "ship" — that needs every gate in `acceptance-gates.md`.
- **Moderate** — usable, but identify the weakest axis and recommend the lever (see §3a).
- **Poor** — re-check `experiments/<run>/config.yaml` first (the run's authoritative config), then consult `diagnose-training` if the training itself looks wrong.

**A single result is high-variance.** A different seed/fold can move sens by 0.05+. Close every Mode A verdict with: "this is one checkpoint; run the 5-fold sweep + `run/aggregate.sh` before quoting in the thesis."

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
| **KD vs baseline (same student)** | e.g. `kd_<t>_to_<s>` + `baseline_<s>` run-dirs |
| **Cross-student** | `kd_<t>_to_mobilenetv4_conv_medium` + `kd_<t>_to_fastvit_sa12` + … (same teacher, same tree) |
| **Teacher vs student** | `teacher.json` + `kd_<student>.json` |

**Gating check first.**
- If a baseline file is requested but doesn't exist, don't invent numbers — tell the user to produce it: `bash run/train_student.sh STUDENT=... TRAINING=baseline` (the baseline arm works via the `use_kd` flag, fixed 2026-06-04; run-dir `baseline_<student>/`). See memory `project_baseline_kd_coupling`.
- If the inputs are clearly different splits / data / augmentation (read each run's saved `config.yaml` if present), flag it and refuse to call a winner — the comparison is confounded.
- **No paired CI for this exact pair?** Say so plainly, report the point estimates as descriptive only, and give the server command (`TMPDIR="$(pwd)/.tmp" bash run/bootstrap_ci.sh RESULTS_DIR=<tree> PAIR="<A>:<B>" SUBGROUP=source OUT_JSON=reports/ci_<name>.json OUT_MD=reports/ci_<name>.md` — without `OUT_*` the runner writes into the results tree itself). Don't hand-roll a bootstrap on the Mac and don't borrow a CI computed on another tree — neither is citable (see "Check a CI file's provenance" above). If the user needs a thesis sentence now, give one that states what is and isn't established ("chưa có kiểm định ghép cặp; điểm ước lượng …") plus the sentence to use once the CI exists.

**If the user asked for a verdict or one sentence, lead with it** — the sentence (with its CI or its "not yet tested" caveat) first, then the supporting table. The full table below is the evidence, not the answer.

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

**Preferred: paired bootstrap CI.** When `predictions.csv` exists for both arms (it does for every run since 2026-06-21), the real test is `bash run/bootstrap_ci.sh RESULTS_DIR=… PAIR="<A>:<B>" OUT_JSON=reports/ci_<name>.json OUT_MD=reports/ci_<name>.md` (add `SUBGROUP=source` for the ISIC/PAD split). Quote "Δ [lo, hi]" and call it significant only if the interval excludes 0. The pooled-std heuristic below is the fallback when no predictions exist. Overlapping *unpaired* intervals do **not** mean "no difference".

**Significance heuristic (for KD-vs-baseline only, fallback).** Without 5-fold std we can't bound noise. Quote the delta and warn: "single-checkpoint delta — run 5 folds via the array jobs before drawing a conclusion." Do not call it "robust" or "significant" on n=1.

**If the user has 5 folds for each run** (fed as multiple JSONs labeled `<label>_fold<i>.json`, or auto-detected from `<tree>/<run>/fold_*/test_metrics.json` — say which tree, v1 or v2), aggregate them into mean ± std per label *before* comparing. A pooled-std overlap check is then a rough **model-to-model spread** hint only — it is not the test set's sampling error (`CLAUDE.md` → Uncertainty) and can never replace the paired CI above:
```
pooled_std = sqrt((std_kd**2 + std_baseline**2) / 2)
significance = "robust"   if abs(delta) > 2 * pooled_std
             = "marginal" if abs(delta) > 1 * pooled_std
             = "noise"    otherwise
```
This is a heuristic, not a t-test — language is "robust", "marginal", "noise", never "p<0.05".

**Ranking + verdict rules:**
- For KD-vs-baseline: with `predictions.csv` for both arms, KD wins **only if the paired CI of ΔAUPRC (and of the operating-point metric, e.g. Δsens_at_90spec) excludes 0 on the positive side**; a CI containing 0 is "indistinguishable", never "KD won". Point-estimate rule (fallback only, label it "point estimate, not tested"): `delta_auc > 0` AND `delta_sens > 0`; if sens worsens, KD did not win regardless of accuracy/specificity gains. (Domain priority: missing a malignant > false alarm.)
- For cross-student: rank by **sensitivity first, then auc_roc**. Don't rank on accuracy — misleading at imbalance. `sensitivity` in `test_metrics*.json` uses Youden's J fitted on the test set (optimistic) — prefer `valthr_sensitivity` when the run has it, otherwise flag the number as test-threshold (`docs/GOTCHAS.md`).
- For teacher vs student: a Good student is one whose `sens` and `auc_roc` are within ~0.02 of the teacher's. Bigger gap → KD didn't transfer well. (For model selection the author requires the student to **keep** the teacher's performance — acceptance gate C2, non-inferiority since 2026-10-03 (post-hoc; before that it was "beat the teacher, lower bound > 0"): paired CI lower bound of Δ(student − teacher) **> −δ** on each gated domain, same splits and arm; δ = 5% of the arm's own teacher AUPRC per domain (provisionally locked 2026-10-04 — current value in `acceptance-gates.md` §1). "Within ~0.02" is only a health hint, never a pass. C2 passing says nothing about whether KD helped — that is C1.)
- **None of these rankings is an acceptance verdict.** "KD wins" / "best pair" answers *which is better*; whether the winner is *good enough* is `acceptance-gates.md`.
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
Health verdict: <Good | Moderate | Poor>   (Mode A only — run health, NOT acceptance)
Acceptance: <not assessed — see acceptance-gates.md | the `### Cổng chấp nhận` block from that file>
Data tier: <Aggregated 5-fold | Single-checkpoint test JSON>
Splits: <v1 (leaked, experiments/runs/) | v2 (patient-grouped, runs_newsplit_*)>
Files read:
- <path 1>
- <path 2>   (if comparing)

## All recorded metrics
<table — every key from every input JSON, verbatim, 4 dp>

Class-prevalence floor:
- Test set positive rate: <`prevalence` from the JSON; never assume one>
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
- <"Run 5-fold sweep" / "Aggregate the existing folds via run/aggregate.sh" / "Patch evaluator to save predictions" / "Fix baseline arm before re-attempting comparison">

## Caveats applied
- <pauc bug? single-checkpoint variance? missing baseline? confounded augmentation? unknown class prevalence?>
```

## Caveats

- **`pauc_at_tpr80` is the real ISIC 2024 metric (fixed 2026-06-04)**, range ≈ [0.02, 0.20] — quotable as an absolute number. Only JSONs produced *before* 2026-06-04 are on the old stretched [0.9, 5.0] scale. See memory `project_pauc_metric_bug`.
- **Predictions ARE saved (since 2026-06-21).** `Evaluator.save_predictions` writes `predictions.csv` (`y_true,y_prob,y_pred[,source]`) next to each `test_metrics.json` — recompute AUPRC / PR-curve / per-domain / bootstrap CIs from it. The scalar `test_metrics.json` already carries `auprc`, `prevalence`, `sens_at_90spec`, `sens_at_95spec`.
- **Baseline (no-KD) runs work (fixed 2026-06-04).** Mode B's KD-vs-baseline cell has real baseline numbers via the `use_kd` flag (`training=baseline` → plain `Trainer`, run-dir `baseline_<student>/`). See memory `project_baseline_kd_coupling`.
- **`run/evaluate.sh` always evaluates fold 0.** It calls `scripts/evaluate.py` without forwarding `--fold`, so the default `--fold 0` applies regardless of what was trained. For a true 5-fold report, either rely on the training-time auto-eval JSONs at `experiments/runs/<run>/fold_*/test_metrics.json`, or extend `run/evaluate.sh` to accept a `FOLD=` env var. Flag this when the user thinks they're getting a different fold.
- **Single-checkpoint variance is large.** Same architecture × different seed can move sens by 0.05+. Always recommend the 5-fold sweep before quoting numbers in the thesis.
- **`accuracy` is misleading at ISIC class imbalance.** Majority-class baseline ≈ 0.995. Never rank or verdict on raw accuracy — always anchor against the floor.
- **Don't quote `val_pauc`** — that's the training-log metric, biased by early stopping. This skill reads the *test* JSON. If only val numbers are available, use `assess-training` instead.
- **`config.yaml` saved in the run dir is authoritative**, not `configs/`. Hydra overrides at submit time can shift hyperparams.
- **Multi-checkpoint comparison requires matching data + augmentation.** If the saved `config.yaml` differs in augmentation or fold composition between inputs, the comparison is confounded — flag it and refuse to call a winner.
