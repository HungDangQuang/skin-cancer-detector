# Next tasks after the external evaluation (handoff)

**Written:** 2026-08-23 · **For:** a fresh session picking this up
**Context to read first:** [reports/2026-08-23_external_evaluation.md](../reports/2026-08-23_external_evaluation.md)
(what was run and what the numbers mean), then `CLAUDE.md` §"External test sets" and
[run/README.md](../run/README.md) §2 / §5b.

---

## 0. Where things stand

> **ALL FIVE TASKS COMPLETED on 2026-08-23 (session 2), all on `vastnew`** — except the parts of
> task 3 that physically require an Android handset. Each task section below keeps its original
> brief plus a **STATUS** block. Results write-up:
> [reports/2026-08-23_external_evaluation.md](../reports/2026-08-23_external_evaluation.md).

| Thing | State |
|---|---|
| HAM10000 | 10,015/10,015, **all three variants evaluated** (`headline` / `full` / `no_akiec`) × 19 runs × 5 folds, each with `kd_comparison.md`. ✅ |
| Fitzpatrick17k | **16,574 / 16,577 (99.98 %), md5-verified** from the Kaggle mirror; re-prepared and both variants re-evaluated. ✅ |
| Calibration on external results | ✅ 3 runs × 2 datasets, prior-shift **and** Platt (report §5) |
| Bootstrap CIs | ✅ `scripts/bootstrap_ci.py` + `run/bootstrap_ci.sh`, B=2000 over all 5 result trees (report §6) |
| `.pte` export + parity | ✅ layer 1 — `max\|Δlogit\|` **5.53e-06**. Layer 2 + latency + RAM need a physical device. |
| Checkpoints | all 19 runs on `vastnew` at `/workspace/skin-cancer-detector/experiments/runs/`. GPU idle. |

**Ordering rule that decided the sequence:** anything that **produces** `predictions.csv` runs
before anything that **analyses** it. That rule earned its keep — task 1's download landed *after*
the first Fitzpatrick calibration and CI pass, so both had to be redone on the full set. Doing task
1 first would have saved that work.

**Two conclusions changed once coverage was fixed** (both were wrong on the 23 % subset):
- The fairness gap is **light vs medium**, not light vs dark (report §4.2).
- `efficientnetv2_m` is the **best** KD teacher on HAM10000 and the **worst** on Fitzpatrick,
  where it significantly hurts 2/4 students (report §4.1).

---

## Task 1 — Check Kaggle for a complete Fitzpatrick17k, download only if verifiable

**Why first:** if a complete image set exists, the whole Fitzpatrick evaluation must be
regenerated, which would invalidate any calibration / CI work done on the current 23 % subset.

**Step 1a — search only (no download, ~10 min).** Look for a Kaggle dataset that ships the
Fitzpatrick17k **images**, not just the metadata CSV. Accept it only if all four hold:

1. It contains actual image files (the two HuggingFace mirrors checked on 2026-08-23 do not:
   `spycoder/fitzpatrick` is metadata-only, `ZYXue/Fitzpatrick_17k` is a 5k-row VQA derivative).
2. Filenames map to `md5hash` from the release CSV — otherwise `fitzpatrick_scale` cannot be
   attached and the set is useless for fairness.
3. **The bytes verify against the official `md5hash` column.** This is the acceptance test, and
   the repo already implements it: point `scripts/download_fitzpatrick17k.py`'s validation at the
   files, or md5 them directly against `data/raw/fitzpatrick17k/fitzpatrick17k.csv`.
   A mirror that fails md5 on most rows is re-encoded → it is a *different* dataset, say so.
4. License permits research use.

**Step 1b — credentials.** `vastnew` has no `~/.kaggle/kaggle.json` (checked
2026-08-23). Per the project's hard rule, keep it **inside the repo**, e.g.
`export KAGGLE_CONFIG_DIR="$(pwd)/.kaggle"` per session — never write to `$HOME`.

**Step 1c — if accepted:** stage images into `data/raw/fitzpatrick17k/images/<md5hash>.jpg`,
regenerate `metadata_downloaded.csv`, then:
```bash
bash run/prepare_external.sh  DATASET=fitzpatrick17k SKIP_DOWNLOAD=1
bash run/evaluate_external.sh DATASET=fitzpatrick17k VARIANTS=all GPU=0
```
Then re-run `scripts/compare_kd_results.py` per variant and update the report's §2 coverage
caveat and §4 fairness tables — the current tone counts (light 310 / medium 596 / dark 137)
would all change.

**Acceptance:** either a verified dataset staged and re-evaluated, or a one-paragraph note in the
report saying the search found nothing usable and *why* (that note is itself thesis material).

### STATUS 2026-08-23 — ✅ DONE: coverage 23.4 % → **99.98 %**

Downloaded and **fully md5-verified**: `md5sum *.jpg` matched the filename (which *is* the official
`md5hash`) on **16,574 / 16,574** files, zero mismatches, 0 files not in the release. Only 3 rows
remain missing, all `dermaamin.com` — that is the practical ceiling.

Re-prepared and both variants re-evaluated (19 runs × 5 folds), then `compare_kd_results`,
calibration and bootstrap CIs re-run on the new predictions. **Payoff:**

| | 23 % subset | Full set |
|---|---|---|
| Headline split | 1,043 | **4,320** |
| Prevalence | 64.6 % | **50.0 %** |
| dark / light / medium | 137 / 310 / 596 | **411 / 2,310 / 1,599** |

The 64.6 % prevalence was an artefact of *which atlas survived*, not a property of the dataset.
Superseded results archived at `reports/_archive/fitzpatrick17k_subset23pct_20260823/`; old
manifests as `data/raw/fitzpatrick17k/*_subset23pct.csv.bak`.

**Credentials (reusable):** token at `.kaggle/kaggle.json` inside the repo, `chmod 600` —
`.gitignore` already covers `.kaggle/` and `kaggle.json` (check with `git check-ignore`). **No
`kaggle` pip package needed**: write `.kaggle/curlrc` containing `user = "<username>:<key>"` and use
`curl -L -K .kaggle/curlrc <download-url>`, which also keeps the key out of `ps` output. ~22 MB/s.

<details><summary>The pre-download vetting that justified spending the bandwidth (kept — reusable)</summary>

**`mobaswiralfarabi/fitzpatrick17k-original`** (Kaggle, 1.46 GB, uploader-declared CC0) passes all
four criteria as far as they can be tested without downloading:

| Criterion | Result |
|---|---|
| 1. actual image files | ✅ 16,574 `.jpg` under `finalfitz17k/` |
| 2. filenames map to `md5hash` | ✅ all `<32-hex>.jpg`; **16,574 / 16,577** official hashes, **0 extras**; the 3 missing are all `dermaamin.com` |
| 3. bytes verify | ⏳ **strong proxy passed** — all **3,887 / 3,887** images we already md5-verified have **byte-identical file sizes** in the mirror (3,887 independent re-encodings cannot collide on exact byte counts). Real md5 still to run on the downloaded bytes. |
| 4. license | ⚠️ Kaggle says CC0, but the uploader's tag is **not** authoritative for the atlas images — cite the original Fitzpatrick17k terms. |

**How the pre-verification was done (reusable trick, no credentials needed):** Kaggle's public API
answers unauthenticated for *metadata*, including per-file byte sizes.

```bash
# paginate with .nextPageTokenNullable (83 pages at pageSize=200)
curl -s "https://www.kaggle.com/api/v1/datasets/list/<owner>/<slug>?pageSize=200&pageToken=$TOK" \
  | jq -r '.datasetFiles[] | [.name, (.totalBytes|tostring)] | @tsv'
# then `join` those sizes against the images already on disk and compare
```
(`/datasets/view/<owner>/<slug>` gives totalBytes + license. The `/datasets/list/files/...` path in
older docs 404s.)

Kaggle 404s unauthenticated *downloads*, so this pre-check is what let the mirror be judged before
asking the user for a token at all.

</details>

---

## Task 2 — HAM10000 remaining variants (`full`, `no_akiec`)

Produces artifacts, so it comes before the analyses.

```bash
# on vastnew, under tmux — ~2 h for 19 runs × 5 folds × 2 variants
cd /workspace/skin-cancer-detector
tmux new-session -d -s eval_ham_all \
  "bash run/evaluate_external.sh DATASET=ham10000 VARIANTS=full,no_akiec GPU=0 BATCH=64"
```

Then per variant:
```bash
python scripts/compare_kd_results.py --runs-dir reports/external/ham10000/<variant> \
       --out-md reports/external/ham10000/<variant>/kd_comparison.md \
       --out-json reports/external/ham10000/<variant>/kd_comparison.json
```

**What each variant answers:**
- `full` (10,015 images) — every photograph, including repeat shots of the same lesion. Only for
  literature comparison; samples are **not independent**, so CIs from it are optimistic.
- `no_akiec` (7,242) — drops actinic keratosis. Tests whether the "akiec = malignant" convention
  is carrying the headline result. If the KD verdict flips here, that must be reported.

**Acceptance:** both variants have `aggregated.md` + `kd_comparison.md` for all 19 runs, and a
paragraph in the report comparing the KD verdict across the three variants.

### STATUS 2026-08-23 — ✅ DONE

Both variants evaluated (19/19 runs each) and compared; write-up is report **§3.4**.

| Variant | Images | Prevalence | KD on AUPRC | KD on pAUC |
|---|---|---|---|---|
| `headline` | 7,470 | 15.6 % | **12/12**, +0.0297 | 10/12, +0.0071 |
| `full` | 10,015 | 19.5 % | **12/12**, +0.0298 | 10/12, +0.0063 |
| `no_akiec` | 7,242 | 13.0 % | **12/12**, +0.0267 | 11/12, +0.0074 |

**The verdict does not flip** — so neither "akiec counted as malignant" nor "de-duplicated split"
is carrying the headline result. Two traps found while writing it up:

- **Do not rank variants by raw AUPRC.** Its random baseline *is* the prevalence, which differs by
  construction. Lift over baseline: `full` 2.5× < `headline` 3.1× < `no_akiec` **3.3×** — the exact
  reverse of the raw-number ordering.
- `full` contains repeat photographs of the same lesion, so its rows are **not independent** and any
  CI from it is optimistic. Literature comparison only; never the headline.

---

## Task 3 — Mobile: export `.pte` + parity check (independent — interleave with tasks 1–2)

Needs CPU + `./.venv-export` only, so run it **while** a GPU sweep is going. It is currently the
blocker on every mobile claim in the thesis.

```bash
bash run/setup_export_env.sh                                   # once, creates ./.venv-export
bash run/export_executorch.sh MODEL=mobilenetv4_conv_medium \
     CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_4/checkpoints/best_model.pth
```

Five steps, in order — **benchmarking is meaningless before steps 2 and 3 pass**:

1. Export `.pte` (above). `exports/` is empty today, so no current student has ever been exported.
2. **Numerical parity** PyTorch vs `.pte` on the fixed benchmark set: `max|Δlogit| < 1e-3`.
   `docs/BENCHMARK_AND_RESULTS.md:269` records this as never confirmed.
3. **Preprocessing parity on Android** — squash-resize to 224, interpolation, normalization must
   match training. See `docs/ANDROID_APP_SPEC.md` (bilinear vs LANCZOS is a known trap; the
   `.bin` parity fixtures must be regenerated if the resize path changes).
4. Push benchmark set + `.pte` via adb, measure latency / memory.
5. Verify the Android ExecuTorch AAR version matches the version inside `.venv-export`.

**Which checkpoint:** `docs/ANDROID_APP_SPEC.md` decided **fold_4** (the fold closest to the mean,
deliberately not the best fold). Keep that decision unless the app spec is revised.

**Acceptance:** `exports/executorch/<model>.pte` exists, parity max|Δlogit| recorded in the
benchmark report, and on-device latency measured for the *current* SOTA student (the existing
Pixel 6a numbers in `docs/BENCHMARK_AND_RESULTS.md` are from the retired mobilenetv3 family).

### STATUS 2026-08-23 — steps 1–2 ✅ DONE; steps 3–5 need a physical Android device

- **Step 1 ✅** `exports/executorch/mobilenetv4_conv_medium.pte`, 32.11 MB, from `fold_4` as the
  app spec decided. `./.venv-export` built: **executorch 1.4.1**, torch 2.13.0.
- **Step 2 ✅ PARITY PASS.** `max|Δlogit|` **5.53e-06** vs the 1e-3 gate (180× margin), mean
  1.12e-06, `max|Δprob|` 4.76e-07, 0/100 samples over tolerance.
  `docs/BENCHMARK_AND_RESULTS.md` GAP-6 flipped from "never confirmed" to confirmed.
- **Steps 3, 4, 5 ⛔ not doable from here** — preprocessing parity inside the app, `adb` latency /
  memory, and the AAR version check all require a real handset. Step 5 is *half* answered: the
  version to match is **1.4.1**.

New tooling (both went through the mandatory review + validate-pipeline loop):
`scripts/check_pte_parity.py`, `run/check_pte_parity.sh` → `reports/mobile_benchmark/parity_<model>.json`.

```bash
bash run/setup_export_env.sh                                    # once
CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_4/checkpoints/best_model.pth
bash run/make_benchmark_set.sh N=100 MODEL=mobilenetv4_conv_medium CKPT="$CKPT"
bash run/export_executorch.sh       MODEL=mobilenetv4_conv_medium CKPT="$CKPT"
bash run/check_pte_parity.sh        MODEL=mobilenetv4_conv_medium   # exit 1 on FAIL
```

⚠️ **Pass the same `CKPT` to `make_benchmark_set.sh` and `export_executorch.sh`** — different folds
are different models, so a mismatch fails parity for a reason unrelated to the lowering.
⚠️ `run/setup_export_env.sh`, `export_executorch.sh`, `make_benchmark_set.sh`, `benchmark.sh` were
**missing on `vastnew`** (its git remote is behind the Mac) — `rsync` them, don't `git pull`.

---

## Task 4 — Calibration on the external results

Post-hoc only — **no retraining, no re-inference**, and it does not change any ranking metric
(pAUC / AUPRC / AUC are invariant to monotone rescaling).

The external output tree already has the layout the script wants (`fold_*/predictions.csv`):

```bash
# on the server (needs numpy + sklearn + matplotlib), prior-shift closed form:
python scripts/compute_calibration.py \
    --run-dir reports/external/ham10000/headline/kd_efficientnetv2_m_to_mobilenetv4_conv_medium
```

- `--method none` (default, prior-shift) needs no fit set → works directly.
- `--method platt|isotonic` reads `fold_dir/val_predictions.csv` ([compute_calibration.py:223](../scripts/compute_calibration.py#L223)),
  which the external dirs do **not** have. Copy it in from
  `experiments/runs/<run>/fold_N/val_predictions.csv` first (same fold, same model).
- `--target-prevalence auto` uses the test set's own prevalence (HAM 15.7 %, Fitz headline 64.6 %).
- `--subgroup tone_group` works on the Fitzpatrick predictions (the column is already in the CSV).

**Set expectations correctly — this is a presentation fix, not a performance fix.** §3.2 of the
report shows sensitivity at 90 % specificity is ~0.46–0.51 on HAM and ~0.24 on Fitzpatrick;
no threshold or calibration change lifts that ceiling. Deliverable is honest displayed
probabilities + a before/after ECE/Brier + reliability curve, nothing more.

**Acceptance:** `calibration_metrics.json` + `reliability_curve.png` for at least the deployable
student and one teacher per dataset, and a short §"Calibration" in the report stating raw vs
corrected ECE — with an explicit sentence that ranking metrics are unchanged.

### STATUS 2026-08-23 — ✅ DONE (report §5)

Ran on 3 runs (KD student / its baseline / `teacher/efficientnetv2_m`) × 2 datasets, in **both**
modes. Platt outputs are kept beside the prior-shift ones as
`calibration_metrics_platt.json` + `reliability_curve_platt.png`.

| Dataset | Run | ECE raw | prior-shift | Platt |
|---|---|---|---|---|
| HAM | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 0.3019 | 0.2884 | **0.0594** |
| HAM | `teacher/efficientnetv2_m` | 0.2887 | 0.2744 | **0.0588** |
| Fitz | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | **0.0956** | 0.3104 | 0.2508 |
| Fitz | `teacher/efficientnetv2_m` | **0.0661** | 0.2822 | 0.3050 |

Three findings the next person should not have to re-derive:

1. **Prior-shift is ≈ a no-op on HAM by arithmetic, not by failure.** The shift is
   `logit(π_target) − logit(π_train)` with π_target = 0.1565 (HAM's own prevalence) and
   π_train = 1/(1+5) = 0.1667 — nearly equal. Prior-shift is the right tool for the *internal*
   0.39 %-prevalence test set and the wrong tool for HAM. Use Platt there (ECE ÷5).
2. **On Fitzpatrick the RAW probabilities are the best-calibrated and both corrections make it
   worse** — that set is 64.6 % malignant, so the model's over-confidence happens to match it.
   **A calibrator is only valid for the prevalence it was fitted against.**
3. Bonus: the **KD student is better calibrated than its baseline** before any correction
   (0.302 vs 0.369 on HAM; 0.096 vs 0.179 on Fitz).

**Re-run on the full set after task 1 landed** — and the story changed. At 50 % prevalence
prior-shift roughly *doubles* ECE on all three runs (0.205→0.408, 0.286→0.437, 0.136→0.369), while
Platt helps the two students (0.205→0.182, 0.286→0.203) but **hurts the teacher** (0.136→0.209).
Each of the three domains (internal 0.39 %, HAM 15.6 %, Fitz 50.0 %) needs a *different* correction,
so the app must state the prevalence it assumes rather than hard-code one logit shift.

Mechanics: `--method platt` needs `fold_dir/val_predictions.csv`, which the external tree lacks —
copy it from `experiments/runs/<run>/fold_N/` first (same run, same fold). Both modes write to the
same fixed filenames, so run Platt first and rename, then prior-shift.

---

## Task 5 — Bootstrap confidence intervals (needs a NEW script)

**Why:** everything is currently reported as `mean ± std over 5 folds`, which measures spread
*between models*, not sampling error of the test set. The dark-tone group is 137 images
(93 malignant) — at that size the 5-fold std cannot decide whether a light−dark gap is real.

**No script exists for this.** Writing one means following the mandatory modification workflow in
`CLAUDE.md` (code → `code-change` skill review → propagate to `run/` + docs → validate-pipeline →
run on the server). Suggested shape: `scripts/bootstrap_ci.py`, pure numpy/sklearn, reading the
`predictions.csv` files that are already on the Mac.

It must produce three things:

1. **CI per run per metric.** Resample rows with replacement (B = 2000, seeded), recompute
   AUC / AUPRC / pAUC, report the 2.5–97.5 percentile → `AUPRC 0.480 [0.44–0.52]`.
2. **Paired bootstrap for the KD delta.** Resample the *same row indices* for the KD run and its
   baseline, recompute Δ each time. This turns the current "KD improved 12/12" into
   "ΔAUPRC +0.030 [CI]", which is a far stronger statistical claim than a win count.
   Pairing matters: the two models are scored on the identical test set, so an unpaired CI
   throws away that correlation and overstates the uncertainty.
3. **Paired bootstrap for the fairness gap.** Bootstrap the *difference* (light AUC − dark AUC)
   directly, not two separate CIs compared by eye. Report per run and per tone pair.

Folds: bootstrap **within** each fold and then combine, or pool the fold predictions — pick one,
state which, and keep it consistent (they answer slightly different questions).

**Acceptance:** CI columns added to the report's HAM ranking table and the §4.1 fairness table,
and the §4.1 conclusion re-stated in terms of the CI on the gap rather than "inside the fold
spread".

### STATUS 2026-08-23 — ✅ script written and run

`scripts/bootstrap_ci.py` + `run/bootstrap_ci.sh` (through the mandatory review + validate-pipeline
loop; `run/README.md` §5c documents it). B = 2000, seed 42, over all five result trees →
`<tree>/bootstrap_ci.{json,md}`. All three required outputs are produced, plus `n_folds` per run so
the one 3-fold run can't be quoted as a 5-fold interval.

**Fold convention chosen (and stated in every output):** one row-index draw per replicate applied
to **all** folds, then averaged. The folds are five *models* on the *same* rows, so pooling their
`predictions.csv` would replicate each row 5× and shrink the interval by ~√5 — a fabricated result.
The script asserts identical labels *and row order* across folds and refuses to run otherwise.

**Why pairing was worth the effort — a concrete case.** On HAM10000, `kd_convnextv2_base_to_
mobilenetv4` AUPRC 0.4198 [0.3959, 0.4440] and `baseline_mobilenetv4` 0.3754 [0.3578, 0.3996]
**overlap**, so read separately they look inconclusive. The paired delta is **+0.0445
[+0.0353, +0.0527]** — decisively non-zero. Report the paired delta, never a win count.

**Two implementation notes for whoever touches this next:**

1. **Performance.** Four sklearn calls per (replicate, fold) was ~2 h *per tree* (≈10 h for five).
   A bootstrap resample is just integer **weights** over the original rows, so the script sorts once
   per fold and gets each replicate's ROC/PR curve from an O(n) cumsum — exact, not approximate, and
   ~50× faster (whole job ≈15 min). Tie-groups are collapsed the way sklearn does, or the trapezoid
   area shifts. `_verify_fast_path()` checks the fast path against `src.evaluation.metrics` on unit
   weights for every fold and **aborts** on any disagreement > 1e-9 — do not remove that gate.
2. **A single-class resample is undefined, not zero.** `pauc_at_tpr()` and
   `sensitivity_at_specificity()` both *return 0.0* there; averaging that into the replicate vector
   drags the interval down. They are mapped to NaN and dropped from the percentiles (`n_dropped` is
   reported). This matters most in small subgroups — exactly where CIs are the point.

**Result on the fairness question (re-run on the full set):** across all 19 runs,
**light − medium is significant in 19/19** (mean +0.047 AUC, +0.089 AUPRC) while **dark − light is
significant in only 4/19** (mean −0.029). So the reproducible disparity is on **medium** skin
(Fitzpatrick III–IV), not the darkest group — a "worse as skin gets darker" narrative is not
supported. The light−dark gap is consistently signed but individually unresolved: quote the
interval, claim neither a gap nor a clearance.

---

## Recurring traps (all of these already bit this project)

- **Never run Python / `pip install` on the Mac** — a `PreToolUse` hook blocks it. Analysis that
  needs numpy/sklearn/matplotlib runs on `vastnew`. Reading JSON with stdlib `python3` is fine.
- **Everything stays inside the project folder** on the shared/rented boxes: no `sudo`, no `apt`,
  no `~/.bashrc` edits, deps only in `./.venv-linux` (`./.venv-export` for ExecuTorch). Set
  `export TMPDIR="$(pwd)/.tmp"` before long jobs.
- **Pin `GPU=<id>`** when two jobs could run at once; `GPU=auto` picks the freest card and two
  launches can collide.
- **Never write inside `experiments/runs/`** from the external-eval path. Results belong in
  `reports/external/`. Training run-dirs are the record of finished jobs.
- **Keep the external output tree shaped like `experiments/runs/`** — teacher runs stay nested as
  `teacher/<name>`. That is the only reason `scripts/compare_kd_results.py` works on it unchanged;
  flattening to `teacher__<name>` makes the script silently skip them.
- **The frozen-threshold rule is load-bearing.** `scripts/evaluate_external.py` takes the decision
  threshold from each run's internal `val_predictions.csv`. Do not "improve" results by refitting
  a threshold on HAM/Fitzpatrick — those configs list `threshold_selection` under `do_not_use_for`.
  If an oracle threshold is ever reported, label it as an upper bound.
- **Long jobs go under `tmux`**; every `run/*.sh` tees to `logs/<name>_<timestamp>.log`.
- **rsync on the Mac is openrsync** — only `-az[n] -v --include/--exclude` work (`--info=progress2`
  fails). The vast.ai MOTD prints on stderr, so filter it when parsing command output.
- `vastnew`'s git remote is behind the Mac; new scripts get there by `rsync`, not `git pull`.

## When the tasks are done

Update, in the same session that produced the numbers: the report above, `CLAUDE.md` if a rule
changed, the matching `docs/*.md`, and auto-memory (`MEMORY.md` + `project_external_eval_run.md`).
An end state with stale docs counts as unfinished work.
