# `run/` — the project's execution layer (plain GPU server / VM over SSH)

Every job in this project is launched from here: `bash run/<script>.sh KEY=VALUE`.
The scripts are only an orchestration layer — the Python/Hydra code underneath is
the same one you edit locally.

| Concern | How `run/` does it |
|---|---|
| Deps / venv | `run/setup_env.sh` → `./.venv-linux` (export tooling: `./.venv-export`) |
| GPU | `CUDA_VISIBLE_DEVICES` via `GPU=` (`auto` picks the freest GPU) |
| 5-fold sweep | fold loop inside the `run/*.sh` script (`FOLDS="0 1 2"` to split) |
| Launch | `bash run/<script>.sh KEY=VALUE` |
| Logs | `logs/<name>_<timestamp>.log` (every script tees, survives SSH drops) |

All scripts source `run/common.sh`, which provides `set -euo pipefail`, repo-root
resolution, `activate_venv`, `select_gpu` and `start_log`. Three exceptions, all
deliberate: `setup_env.sh` / `setup_export_env.sh` / `setup_new_server.sh` must
run *before* a venv exists, `train_kd_parallel.sh` drops `-e` so one failed
student can't abort the batch, and the read-only monitors `progress.sh` /
`progress_all.sh` are standalone so they can be piped into a server over
`ssh 'bash -s'` (see §7).

> This is a **single-tenant** box: one training process at a time per GPU unless
> you pin different `GPU=` ids. Keep everything inside the project folder — no
> sudo, no system python, no shell-rc edits; env vars per session only.

## Script index

| Script | What it does |
|---|---|
| `setup_env.sh` | One-time: create `./.venv-linux`, install deps, verify CUDA |
| `setup_new_server.sh` | Bootstrap a brand-new server (clone + env + data layout) |
| `validate.sh` | Import sanity + Hydra dry-load of every registered model (CPU, ~1 min) |
| `poc.sh` | Synthetic-data smoke test: prepare → teacher → student |
| `prepare_data.sh` | ISIC 2024 (+ PAD-UFES-20) → processed images + fold splits |
| `download_external.sh` | Fetch the HAM10000 / Fitzpatrick17k raw bytes (network only) |
| `prepare_external.sh` | HAM10000 / Fitzpatrick17k eval-only sets + leakage check |
| `train_teacher.sh` | One teacher, all 5 folds sequentially |
| `train_student.sh` | One student (KD or baseline), all 5 folds |
| `train_kd_parallel.sh` | VRAM-gated parallel KD launcher (several students at once) |
| `progress.sh` | **Read-only** status of the training jobs on the current box (fold, %, ETA, RAM/VRAM) |
| `gpu_probe.sh` | **Read-only** GPU utilization / VRAM time-series into a CSV + p50/p90/p95/max summary — the measurement behind `MAX_JOBS` |
| `progress_all.sh` | Same report for **every** server at once, run from the Mac |
| `pull_results.sh` | **Mac-side**: diff the servers' run-dirs against this Mac, then rsync the missing results down |
| `ablation_sampler.sh` | Data-strategy ablation A — undersampling ratio |
| `ablation_pad.sh` | Data-strategy ablation B — PAD mixing (ISIC-only vs ISIC+PAD) |
| `aggregate.sh` | fold_*/test_metrics.json → mean ± std (`aggregated.{json,md}`) |
| `evaluate.sh` | Evaluate one checkpoint on the held-out test set |
| `evaluate_external.sh` | Cross-domain / fairness eval on HAM10000 / Fitzpatrick17k (frozen threshold) |
| `plot_pareto.sh` | Pareto figure: in-domain AUPRC (bootstrap CI) vs measured Pixel 6a latency — CPU-only, joins existing artifacts |
| `bootstrap_ci.sh` | Bootstrap CIs from `predictions.csv`: per-run, paired KD delta, paired ablation delta (`__suffix` forks), named A-vs-B pairs (`PAIR=`), paired fairness gap, per-subgroup variants (`SUBGROUP=`) |
| `attach_metadata.sh` | Add ISIC metadata columns to existing splits + `predictions.csv` (no GPU, no re-train) — unblocks subgroup calibration |
| `make_benchmark_set.sh` | Build the fixed 100-image benchmark input set |
| `benchmark.sh` | Params / FLOPs / size / latency profile (`MOBILE=1` for the light subset) |
| `export_model.sh` | Export to ONNX or TorchScript |
| `setup_export_env.sh` | One-time: isolated `./.venv-export` for ExecuTorch |
| `export_executorch.sh` | Export to `.pte` for Android on-device |
| `check_pte_parity.sh` | PyTorch ↔ `.pte` numerical parity gate (`max|Δlogit| < 1e-3`) |
| `export_all_students.sh` | All four mobile students → `.pte` + parity, one launch (ref/export/parity share one CKPT) |

## 0. One-time setup

```bash
bash run/setup_env.sh                 # creates ./.venv-linux + installs deps + verifies CUDA
# If torch must match a specific CUDA/driver (see `nvidia-smi` top-right):
TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121 bash run/setup_env.sh
DEV=1 bash run/setup_env.sh           # also install test/lint deps

bash run/validate.sh                  # confirm every model builds in the real venv
```

## 1. Smoke-test the pipeline (no ISIC download)

Synthetic images carry a learnable color bias, so a 2-epoch run reaching AUC > 0.5
proves data → model → loss → gradients → metrics all wire up.

```bash
bash run/poc.sh                       # prepare + teacher + student
bash run/poc.sh STAGE=teacher TEACHER=convnextv2_base
```

## 2. Data

Raw data does **not** ship with the repo. Put it under `data/raw/` before
`run/prepare_data.sh`:

- **ISIC 2024** (required, primary training):
  <https://www.kaggle.com/competitions/isic-2024-challenge/data> → extract to
  ```
  data/raw/isic2024/train-image.hdf5
  data/raw/isic2024/train-metadata.csv
  ```
  (Kaggle CLI: `kaggle competitions download -c isic-2024-challenge -p data/raw/isic2024 && unzip …`)
- **PAD-UFES-20** (optional, extra malignants):
  <https://data.mendeley.com/datasets/zr7vgbcyr2/1> then stage with
  `bash scripts/setup_pad_ufes_20.sh <zr7vgbcyr2-1.zip>` → produces
  `data/raw/pad_ufes_20/{images/,metadata.csv}`. If absent, prepare runs ISIC-only.
- **HAM10000** (cross-domain evaluation only, never training):
  Harvard Dataverse, fetched by `run/download_external.sh` (~2.8 GB, md5-verified)
  → `data/raw/ham10000/HAM10000_metadata.csv` + `images/`.
- **Fitzpatrick17k** (fairness evaluation only, never training): the release ships
  **URLs, not images** — `run/download_external.sh` pulls the release CSV and then
  the pictures. Expect PARTIAL coverage (see the note below the commands).

```bash
bash run/prepare_data.sh              # → data/processed/… + data/splits/isic2024/fold_{0..4}/ + test_split.csv

# External EVAL-ONLY sets. Step 1 — fetch the raw bytes (CPU/network only):
bash run/download_external.sh DATASET=ham10000 RM_ZIP=1
bash run/download_external.sh DATASET=fitzpatrick17k SAMPLE=60   # trial first (random rows)
bash run/download_external.sh DATASET=fitzpatrick17k             # then the full ~16.5k URLs

# Step 2 — process + leakage check vs the internal splits (exits 2 on any overlap):
bash run/prepare_external.sh DATASET=ham10000
bash run/prepare_external.sh DATASET=fitzpatrick17k SKIP_DOWNLOAD=1   # + crop70 / crop50 framing variants
bash run/prepare_external.sh DATASET=fitzpatrick17k SKIP_DOWNLOAD=1 CROP_FRACS=none  # headline only
```

> **Fitzpatrick17k coverage: 99.98 % (16,574 / 16,577), md5-verified.** The release
> ships URLs and one of the two linked atlases (`www.dermaamin.com`) is gone, so
> fetching the published URLs directly recovers only ~24 %. This repo does not use
> that subset: the images come from a public mirror whose **filenames are the content
> md5**, checked against the release's own `md5hash` column. Only 3 rows remain
> missing. `data/raw/fitzpatrick17k/download_log.csv` records the per-row outcome —
> quote **99.98 %**, not the old 23.4 % figure.

## 3. Train

```bash
# Teacher first (one command trains all 5 folds sequentially):
bash run/train_teacher.sh                                  # default efficientnetv2_m
bash run/train_teacher.sh TEACHER=convnextv2_base

# Then students (KD distills from the matching trained teacher):
bash run/train_student.sh STUDENT=mobilenetv4_conv_medium            # default teacher efficientnetv2_m
bash run/train_student.sh STUDENT=fastvit_sa12 TEACHER=convnextv2_base
bash run/train_student.sh STUDENT=efficientformerv2_s2 TRAINING=baseline   # no-KD control

# Aggregate the 5 folds into mean ± std (cite THIS, not a single fold):
bash run/aggregate.sh RUN_DIR=experiments/runs/teacher/efficientnetv2_m
bash run/aggregate.sh RUN_DIR=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium
```

Common knobs (all `KEY=VALUE`): `FOLDS="0 1 2"`, `GPU=1` (pin a specific GPU),
`GPU=auto` (default — picks the freest GPU), `GPU=cpu`, `AUG=heavy`,
`DROP_PATH=0.1`, `EXTRA="cudnn_deterministic=false training.batch_size=16"`.

### 3b. Throughput knobs — use these on every long run

They cost nothing in result quality: the teacher-logit cache is *exact*, and the
rest only move data around. See `docs/GOTCHAS.md` "Training throughput".

```bash
bash run/train_student.sh STUDENT=fastvit_sa12 TEACHER=maxvit_base GPU=0 \
  EXTRA="num_workers=16 training.eval_batch_size=128 training.callbacks.checkpoint.save_last=false"
```

| knob | why |
|---|---|
| `num_workers=16` | the config default is a portable `4`; a 64-core box starves the GPU at that. Match it to the box, not the repo. |
| `training.eval_batch_size=128` | val/test run under `no_grad`, so a bigger batch fits and cuts per-batch overhead. `0` = same as `batch_size`. |
| `training.callbacks.checkpoint.save_last=false` | keep only `best_model.pth`. A `maxvit_base` fold is 1.4 GB, so this halves the checkpoint footprint — worth it when disk is tight. Costs you the ability to resume a job that dies mid-run. |
| `training.cache_val_teacher_logits` | already `true` by default for KD; only set it `false` to debug. |

## 4. Data-strategy ablations

Each arm forks into its own run-dir so the main runs are never overwritten.

```bash
# A — undersampling ratio (KD student; teacher is reused frozen, not retrained):
bash run/ablation_sampler.sh SAMP=off      # no resampling
bash run/ablation_sampler.sh SAMP=3        # 1:3   (SAMP=5 == the main run)
bash run/ablation_sampler.sh SAMP=10       # 1:10

# B — PAD mixing (baseline / no-KD by default, so soft labels can't leak PAD):
bash run/ablation_pad.sh ARM=isic_only
bash run/ablation_pad.sh ARM=isic_pad
bash run/ablation_pad.sh ARM=isic_only MODEL_KIND=teacher TEACHER=convnextv2_base
python scripts/analyze_pad_ablation.py --help   # per-domain (ISIC vs PAD) compare
```

> ⚠ The student arm isolates via `run_suffix=`, the teacher arm via `output_dir=`
> — `scripts/train_teacher.py` does **not** read `run_suffix`, so without the
> `output_dir` override a teacher ablation would overwrite the main teacher run.
> That is why the ISIC-only teachers live under `experiments/runs_isic_only/`.

## 5. Evaluate one checkpoint

```bash
bash run/evaluate.sh MODEL=mobilenetv4_conv_medium \
     CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
```

### 5b. External evaluation — cross-domain (HAM10000) & fairness (Fitzpatrick17k)

Needs the two steps in §2 first. One launch sweeps every fold of every run-dir
given (default: every run on the box that has a fold checkpoint), aggregates to
mean ± std, and writes a per-subgroup table (`dx` for HAM10000, `tone_group` for
Fitzpatrick17k).

```bash
bash run/evaluate_external.sh DATASET=ham10000                    # headline split
bash run/evaluate_external.sh DATASET=ham10000 VARIANTS=all GPU=0 # + full / no_akiec
bash run/evaluate_external.sh DATASET=fitzpatrick17k \
     VARIANTS=headline,crop70,crop50 GPU=0                       # framing experiment (§1.2)
bash run/evaluate_external.sh DATASET=fitzpatrick17k \
     RUNS="experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12 experiments/runs/baseline_fastvit_sa12"
```

Output (never inside `experiments/runs/` — training run-dirs stay untouched):

```
reports/external/<dataset>/<variant>/<run_tag>/fold_N/{test_metrics.json,predictions.csv,subgroup_metrics.json}
reports/external/<dataset>/<variant>/<run_tag>/aggregated.{json,md}
```

**Fitzpatrick17k framing variants (`crop70` / `crop50`).** Same rows, same
labels, same squash — only the field of view changes, so `headline` vs `crop70`
vs `crop50` measures what an on-device "crop to the lesion first" pipeline would
buy. Each fraction has its own `data/processed/fitzpatrick17k_<key>/` tree,
because the resize fast-path keys on the destination file existing and would
otherwise re-serve the uncropped pixels under a crop variant's name. Quote the
PAIRED bootstrap delta, not a win count. Full rationale + how to read each
outcome: [docs/PREPROCESSING.md §1.2](../docs/PREPROCESSING.md).

The output tree mirrors `experiments/runs/`, so the in-domain comparison script
runs on it unchanged — this is how you ask "did KD help *out of domain*?":

```bash
python scripts/compare_kd_results.py --runs-dir reports/external/ham10000/headline \
       --out-md reports/external/ham10000/headline/kd_comparison.md
```

> The decision threshold is **frozen** from each run's own internal validation
> fold (Youden's J over `val_predictions.csv`) — never refit on the external set,
> which would be selecting on the test data. A run whose folds have no
> `val_predictions.csv` is skipped with an error rather than silently re-tuned.
> The script also refuses to start unless `reports/external_overlap_check_<ds>.md`
> exists and is clean.

### 5c. Confidence intervals (`bootstrap_ci.sh`)

`aggregated.md` reports `mean ± std over 5 folds` — that is the spread between
the five *models*, not the sampling error of the test set, so it cannot settle
"is this gap real?". `bootstrap_ci.sh` resamples the test **rows** from the
`predictions.csv` files that already exist (no re-inference, nothing written
inside `experiments/runs/`):

```bash
bash run/bootstrap_ci.sh RESULTS_DIR=reports/external/ham10000/headline
bash run/bootstrap_ci.sh RESULTS_DIR=reports/external/fitzpatrick17k/headline SUBGROUP=tone_group
bash run/bootstrap_ci.sh RESULTS_DIR=experiments/runs N_BOOT=2000 SEED=42
# → <RESULTS_DIR>/bootstrap_ci.{json,md}

# Data-strategy ablations. Point OUT_JSON/OUT_MD outside experiments/runs/ so the
# cited experiments/runs/bootstrap_ci.{json,md} is not overwritten. SUBGROUP=source
# is REQUIRED for the PAD arms — see the warning below:
bash run/bootstrap_ci.sh RESULTS_DIR=experiments/runs SUBGROUP=source \
     OUT_JSON=reports/bootstrap_ci_ablation.json \
     OUT_MD=reports/bootstrap_ci_ablation.md
```

It emits a CI per run per metric, a **paired** CI on each KD delta
(`kd_<t>_to_<s>` vs `baseline_<s>`), a **paired** CI on each **ablation** delta,
a **paired** CI on each **named A-vs-B pair** (`PAIR=`), a **paired** CI on each
subgroup gap, and — when `SUBGROUP` is set — the per-subgroup versions of the
ablation and named-pair deltas. Pairing is the point: both models are resampled on
the *identical* rows, so the correlation between them is kept; an unpaired interval
discards it and overstates the uncertainty.

> **`PAIR="A:B"` compares two arbitrary run-dirs, signed A − B** (semicolon-separate
> several). The automatic sections only reach kd-vs-baseline and suffix-vs-main, so
> comparing **two KD runs to each other** — e.g. the two Pareto ship candidates —
> needs this. Reach for it whenever two per-run intervals in section 1 overlap:
> **overlapping unpaired intervals do not mean the models are equivalent**, and the
> paired delta can still exclude 0.

> **Ablation deltas** pair every `__<suffix>` fork against the same run *without*
> the suffix — the `run_suffix` convention, so `baseline_<s>__train_isic_only`
> (PAD mixing) and `kd_<t>_to_<s>__samp_off` (the sampler) are both covered. The
> sign is **main − ablated**: positive means the main configuration wins. The KD
> section cannot do this — there both sides parse to the same `kind`, so the
> kd-vs-baseline lookup never fires and the pair is silently absent.

> ⚠️ **For the PAD arms, quote section 5, not section 3.** The whole-test ablation
> delta is inflated: the ISIC-only arm collapses on the 377 PAD rows, and those
> rows carry ~75% of all positives in the test set. Run with `SUBGROUP=source` and
> read the `pad_ufes_20` row — that is the smartphone-domain generalization claim.

> **Fold convention:** one row-index draw per replicate, applied to **all five
> folds**, then averaged. Folds are five models scored on the *same* test set, so
> pooling their predictions would replicate every row 5× and shrink the interval
> into fiction. The script asserts the folds really share identical labels and
> row order before it starts.

### 5c-bis. Pareto figure (`plot_pareto.sh`)

Joins the two artifacts that already exist — no inference, no training:

```bash
bash run/plot_pareto.sh
# → reports/pareto_auprc_vs_latency.{png,svg}
bash run/plot_pareto.sh LATENCY_COL=best_ms OUT=reports/pareto_best.png
```

> **One x per ARCHITECTURE, not per run-dir.** The four KD variants of an
> architecture share a graph and a parameter count and differ only in weights;
> `reports/BENCHMARK_RESULTS.md` §5.4 shows the 24–149 % latency spread between
> variants tracks **temperature** (~14 % per °C), not the weights. A per-variant x
> would plot thermal noise. So each architecture is a vertical cluster: a better
> teacher moves a point **up for free**, a heavier architecture moves it **right**.

> **x defaults to `sustained_ms`, not the best case.** Throttling costs 45–49 % on
> this handset, and a screening app doing repeated inference sees the sustained
> figure. `LATENCY_COL=best_ms` is for an explicit best-case comparison only.

> `reports/ondevice_latency.csv` is **transcribed by hand** from
> `reports/BENCHMARK_RESULTS.md` (the 32 per-model JSONs are not in this repo). Its
> header carries the provenance — regenerate it from the JSONs if they land here.

### 5d. Subgroup calibration on finished runs (`attach_metadata.sh`)

Direction D (`docs/metadata_training_plan.md §D`) needs `anatom_site_general` /
`sex` beside each prediction. The model stays image-only — the columns ride the
`predictions.csv` side-channel — so **no re-training and no GPU inference** are
required. The documented path ("re-run `prepare` with `data.metadata_cols=[…]`,
then re-evaluate") needs `train-image.hdf5` *and* `data/raw/pad_ufes_20/`;
without the PAD raw dir `prepare_data.py` drops every PAD row and writes
**different splits** than the ones the finished runs were trained on. This
script only *adds columns*, so fold membership is provably untouched:

```bash
# needs data/raw/isic2024/train-metadata.csv on the box (246 MB; no images/HDF5)
bash run/attach_metadata.sh DRY_RUN=1                       # preview first
bash run/attach_metadata.sh                                 # splits + predictions
bash run/attach_metadata.sh STAGE=splits COLS=anatom_site_general,sex,age_approx

python scripts/compute_calibration.py --run-dir experiments/runs/<run> \
    --subgroup anatom_site_general
```

Positional back-fill is safe because `predictions.csv` is row-aligned to
`test_dataloader()` (`shuffle=False`) and `train_sources` filters train+val only.
It is **verified, not assumed** — every file must match the split's row count,
its `y_true` sequence must equal the split's `label` column, and its `source`
column must match row-for-row; a file failing any guard is skipped and the script
exits non-zero. Writes are additive, atomic and idempotent, and every file
touched is copied to `reports/_metadata_backup/<timestamp>/` first.

> This is the one script that writes **inside** an existing run-dir. It never
> touches `y_true/y_prob/y_pred` or any metric file — it appends columns that a
> re-evaluation would have written anyway. Run `DRY_RUN=1` first.

## 6. Benchmark & export (deployment)

```bash
bash run/make_benchmark_set.sh N=100          # fixed input set, reused by PC + phone

bash run/benchmark.sh MODEL=mobilenetv4_conv_medium CKPT=<…>/best_model.pth
bash run/benchmark.sh MODEL=… CKPT=… MOBILE=1   # light subset: params/size/CPU latency
bash run/benchmark.sh MODEL=… CKPT=… DEVICE=cpu # skip the GPU numbers

bash run/export_model.sh MODEL=… CKPT=…                 # → exports/<name>.onnx
bash run/setup_export_env.sh                            # one-time, ./.venv-export
bash run/export_executorch.sh MODEL=… CKPT=…            # → exports/executorch/<name>.pte
bash run/check_pte_parity.sh MODEL=…                    # gate: PyTorch ↔ .pte logits
```

> ⚠ The CPU latency here is a **proxy, not a phone number**. Only params, FLOPs
> and file size transfer across devices — the latency *ranking* can flip on a
> real phone, especially for the transformer students. See `docs/MOBILE.md`.

### 6b. Parity gate before any on-device number

A `.pte` that computes different logits is a different model, so
`check_pte_parity.sh` runs **before** latency is measured or reported. It feeds
the benchmark set's fully-preprocessed `inputs/*.bin` through the ExecuTorch
runtime and compares against the PyTorch `ref_<MODEL>.csv`; exit 1 = FAIL.

```bash
# The CKPT must be the SAME in both steps, or the check compares two models.
CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_4/checkpoints/best_model.pth
bash run/make_benchmark_set.sh N=100 MODEL=mobilenetv4_conv_medium CKPT="$CKPT"  # ref logits
bash run/export_executorch.sh       MODEL=mobilenetv4_conv_medium CKPT="$CKPT"  # the .pte
bash run/check_pte_parity.sh        MODEL=mobilenetv4_conv_medium               # TOL=1e-3
# → reports/mobile_benchmark/parity_<MODEL>.json
```

This is **parity layer 1** (graph lowering) only. Layer 2 — whether the Android
app's own decode + resize + normalize reproduces those tensors — is checked in
the app against `images/*` + `inputs/*.bin`; see `docs/ANDROID_APP_SPEC.md`.

### 6c. All four mobile students in one launch (`export_all_students.sh`)

`export_all_students.sh` drives the three steps above per student, so the
same-`CKPT` pairing that §6b warns about can't be got wrong by hand:

```bash
bash run/export_all_students.sh DRY=1     # print the plan, run nothing
bash run/export_all_students.sh           # ref logits → .pte → parity, ×4
```

The default `PAIRS` is one KD run per student — the run with the best 5-fold mean
**AUPRC**, at the fold closest to that run's own mean (the "median-behaving fold,
never the best one" rule of `docs/ANDROID_APP_SPEC.md` §2):

| Student | Run-dir | Fold | Mean AUPRC |
|---|---|---|---|
| `mobilenetv4_conv_medium` | `kd_convnextv2_base_to_mobilenetv4_conv_medium` | 0 | 0.6351 |
| `fastvit_sa12` | `kd_maxvit_base_to_fastvit_sa12` | 4 | 0.6510 |
| `efficientformerv2_s2` | `kd_convnextv2_base_to_efficientformerv2_s2` | 0 | 0.6521 |
| `repvit_m1_0` | `kd_maxvit_base_to_repvit_m1_0` | 1 | 0.6073 |

Override with `PAIRS="MODEL:RUN_DIR:FOLD …"` (RUN_DIR relative to
`experiments/runs/`). Every pair is resolved and its checkpoint existence-checked
**before** the first export, so a typo costs a second, not an hour.

Outputs carry a run tag so a second checkpoint of the same architecture never
clobbers an earlier `.pte`:

```
exports/executorch/<model>__<teacher>_fold<N>.pte
reports/mobile_benchmark/parity_<model>__<teacher>_fold<N>.json
```

`TAGGED=0` restores the bare `<model>.pte` / `parity_<model>.json` names. Other
knobs: `BACKEND=xnnpack|none`, `FALLBACK=1`, `SKIP_EXISTING=1`, `N=100`,
`TOL=1e-3`. Exit code 1 means at least one student failed export or parity — the
summary table says which.

`FALLBACK=1` retries on `BACKEND=none` (portable ops) when XNNPACK **either**
errors out **or** produces a `.pte` that fails parity. The second case is not
hypothetical: measured 2026-08-24, `efficientformerv2_s2` lowered through XNNPACK
without a single warning and then computed logits of ~−2.2e10 against PyTorch's
−3.15. Only the parity gate caught it. Note that the portable-ops build is far
slower (~70× on the 100-image sweep), so a student that needs it carries a real
deployment cost — measure its on-device latency, never inherit it.

Full sweep, 2026-08-24 on `vastnew` (executorch 1.4.1) — all 16 student arms
(4 architectures × 3 KD teachers + baseline), one median fold each, **16/16
parity PASS**. `max|Δlogit|` against the 1e-3 gate:

| Student | Backend | `.pte` | KD convnextv2 | KD efficientnetv2_m | KD maxvit | baseline |
|---|---|---|---|---|---|---|
| `mobilenetv4_conv_medium` | xnnpack | 32.1 MB | 4.13e-06 | 5.53e-06 | 3.54e-06 | 3.92e-06 |
| `fastvit_sa12` | xnnpack | 40.3 MB | 1.70e-05 | 2.52e-05 | 2.28e-05 | 6.30e-05 |
| `repvit_m1_0` | xnnpack | 24.5 MB | 6.67e-06 | 8.75e-06 | 1.16e-05 | 5.84e-06 |
| `efficientformerv2_s2` | **none** | 48.0 MB | 3.41e-05 | 6.53e-05 | 1.56e-05 | **5.57e-04** |

Two things to carry forward:

- **`efficientformerv2_s2__nokd_fold2` clears the gate by only 1.8×** where every
  other arm clears it by 15–280×. In probability terms it is still negligible
  (`max|Δprob|` 7.2e-06 — the divergence lands on a saturated logit), so it does
  not change a decision, but it is the one arm to re-check if the tolerance ever
  tightens.
- All four `efficientformerv2_s2` arms were exported with `BACKEND=none`
  **by assumption**, not by measurement: XNNPACK was only observed to mis-lower
  the `kd_convnextv2_base` fold_0 checkpoint, and the other three skipped the
  XNNPACK attempt to save ~8 minutes. The assumption is that mis-partitioning is
  a property of the architecture, not the weights — reasonable, but untested for
  those three.

One caveat inherited from `make_benchmark_set.sh`: the reference logits file is
named `ref_<MODEL>.csv` (per architecture, not per checkpoint), so re-exporting a
model from a different checkpoint replaces it. The driver copies the previous one
to `data/benchmark_set/_replaced/<timestamp>/` first rather than losing it.

## 7. Monitor running jobs (`progress.sh` / `progress_all.sh`)

There is no scheduler here — a run is just a process — so this is how you ask
"where is it up to?" without attaching to `tmux` or grepping a 5 MB log.

In Claude Code the shortcut is the project slash command **`/progress`**
(`.claude/commands/progress.md`) — it runs `progress_all.sh` and summarises the
result; `/progress vastnew` limits it to one host.

```bash
# On a server:
bash run/progress.sh                  # one-shot report
bash run/progress.sh WATCH=15         # live, refresh every 15s (Ctrl-C to stop)

# From the Mac, for every training box at once:
bash run/progress_all.sh
bash run/progress_all.sh WATCH=30
bash run/progress_all.sh HOSTS="vastnew"              # explicit single host
bash run/progress_all.sh HOSTS="vastnew mybox"        # add a box (ssh alias)
bash run/progress_all.sh HOSTS="mybox:/home/me/skin-cancer-detector"  # non-default repo path
```

Per running `scripts/train_{student,teacher}.py` process it prints: teacher /
student / training mode (KD, KD+RKD, baseline, privileged), the current fold and
its position in that launch's `FOLDS` list, `epoch N/M` with a **fold %** and a
**job %** bar, an ETA, RAM (trainer + dataloader workers) and VRAM, the last
epoch's `train_loss` / `val_loss` / `val_pauc`, and the live tqdm phase. It ends
with a run-dir table of how many folds already produced `test_metrics.json`.

Defaults: `HOSTS="vastnew"`, `REMOTE_DIR=/workspace/skin-cancer-detector`
(the vast.ai layout), `STALE_MIN=10` (log untouched that long ⇒ `STALLED`),
`RUNS=0` to drop the run-dir table.

Notes / limits:
- **Read-only by design.** It never writes, launches or kills anything; it only
  reads `ps`, `nvidia-smi`, `logs/` and `experiments/runs/`. Killing a job is
  still a manual, deliberate `kill <pid>` — and only for PIDs *you* started.
- `progress_all.sh` pipes `progress.sh` into each host over stdin, so the
  servers never need a `git pull` to get the newest monitor. That is why these
  two scripts don't source `common.sh` (piped over ssh there is no script path
  to resolve, and a `WATCH` loop must not write a log file per refresh).
- The **ETA assumes all `epochs`** actually run; early stopping (patience 10)
  usually ends a fold sooner, so read it as an upper bound.
- Fold % is time-based inside the current epoch (train and val phases differ
  wildly in length — val is ~10× the train phase here, so a batch-count average
  would lie).
- On a container whose PID namespace differs from what `nvidia-smi` reports
  (seen on vast.ai), per-process VRAM shows `n/a*` and the script says
  so — use the GPU total in the header.

### 7b. How many jobs fit at once (`gpu_probe.sh`)

`progress.sh` prints one nvidia-smi **snapshot** for a status display. Choosing
`MAX_JOBS` for `train_kd_parallel.sh` needs the *distribution* over a whole
fold: a job can average 45% utilization and still spike to 100%, and it is the
**peak** VRAM — not the mean — that decides whether a second job OOMs.

```bash
# window 1: start the job (note the save_last=false knob — see §3)
bash run/train_student.sh STUDENT=fastvit_sa12 TEACHER=maxvit_base FOLDS=0 GPU=0 \
     EXTRA="training.callbacks.checkpoint.save_last=false"

# window 2: watch it until it exits
bash run/gpu_probe.sh PID=auto INTERVAL=5 TAG=kd_fastvit_fold0
```

Args: `PID=<n>|auto`, `DURATION=<s>` (0 = unlimited), `INTERVAL=<s>` (default 5),
`GPU=<idx>|all` (**records** that index — it does *not* pin
`CUDA_VISIBLE_DEVICES`), `OUT=`, `TAG=`.

`PID=auto` picks the **trainer**, not a DataLoader worker. This matters: workers
are forks with a byte-identical cmdline, so a plain `pgrep -n -f` returns a
*worker*, and PyTorch recycles workers between epochs
(`persistent_workers=False`) — the probe would then stop after one epoch
reporting "watched job exited". `auto` therefore keeps only processes whose
parent is not itself a match. It also refuses a PID owned by another user.

Output:
```
reports/gpu_probe_<TAG>_<ts>.csv           ts,elapsed_s,index,util_pct,mem_used_mb,mem_total_mb,temp_c,power_w
reports/gpu_probe_<TAG>_<ts>_summary.txt   per-GPU p50/p90/p95/max + VRAM-fit estimate
logs/gpu_probe_<ts>.log
```

Reading the summary: **VRAM decides *if* a second job fits, utilization decides
if it *helps*.** A p50 already near 100% means the card is saturated, so a second
job buys no throughput and only adds OOM risk — which is exactly how the
`MAX_JOBS=2` cap in `train_kd_parallel.sh` was arrived at on the previous box.

Read-only: it never launches, signals or kills anything (`kill -0` is an
existence test), and writes only under `reports/` and `logs/`.

## 8. Bring finished results back to the Mac (`pull_results.sh`)

Training happens on the boxes; analysis (`eval-results`, `update-report`,
`scripts/analyze_pad_ablation.py`, `scripts/compute_calibration.py`) happens on
the Mac. `pull_results.sh` answers "which finished folds does the Mac not have
yet?" and then fetches exactly those. It is a **check by default** — nothing is
written until you add `pull`.

In Claude Code the shortcut is the slash command **`/pull-results`**
(`.claude/commands/pull-results.md`): it runs the check and summarises what is
missing, still training, or not yet trained anywhere.

```bash
bash run/pull_results.sh                    # check only: server vs Mac, per run-dir
bash run/pull_results.sh pull               # rsync the NEW folds down
bash run/pull_results.sh pull stale         # + folds whose remote copy is NEWER than the local one
bash run/pull_results.sh pull ckpt          # + checkpoints/best_model.pth (heavy)
bash run/pull_results.sh pull dry           # rsync --dry-run: show, don't write
bash run/pull_results.sh vastnew            # one host only
bash run/pull_results.sh 'kd_convnextv2*'   # one family of run-dirs
```

Every fold on every host is classified against the local copy:

| class | meaning | pulled by |
|---|---|---|
| `NEW` | finished on the server, no finished local copy | `pull` |
| `STALE` | same path exists locally but the server's `test_metrics.json` is **newer** (an old run re-trained) | `pull stale` |
| `SAME` | already on the Mac | — |
| `RUNNING` | no `test_metrics.json` yet — still training | — (come back later) |

A row is flagged **`MIXED: N fold cu con lai`** when some folds of that run-dir
are being replaced by a re-train while `N` folds of the *older* experiment are
still sitting there — pulling leaves one run-dir holding two different
experiments, and `aggregate.sh` would average across both. Either wait for the
new run to reach 5/5, or move the whole old run-dir aside first:
`mv experiments/runs/<run> experiments/_replaced/<date>_<run>`.

What it copies per fold (~4 MB): `test_metrics.json`, `val_metrics.json`,
`predictions.csv`, `val_predictions.csv`, `config.yaml`, `training_curves.png`,
`calibration_metrics.json`, `reliability_curve.png` — plus `aggregated.{json,md}`
at the run-dir level. Checkpoints only with `ckpt`, and `last_model.pth` is
**never** transferred (it is what filled the disk in the 2026-07-01 incident).

Args (`KEY=VALUE`, same style as the rest of `run/`): `HOSTS`, `REMOTE_DIR`,
`ROOTS` (default `experiments/runs experiments/runs_isic_only`), `MODE`, `ONLY`,
`STALE`, `CKPT`, `DRY`, `SSH_OPTS`. The bare words above are just shorthand for
those.

Notes / limits:
- **Never deletes.** `stale` *moves* the local fold to
  `experiments/_replaced/<timestamp>/<path>` before writing the new one, so an
  old run is always recoverable — this is the run-dir isolation rule applied to
  the download direction.
- Nothing is written on the servers: the inventory is piped in over
  `ssh 'bash -s'` (same trick as `progress_all.sh`, so no `git pull` needed) and
  the transfer is a one-way `rsync` pull.
- `STALE` is decided by the mtime of `test_metrics.json`. If you ever copy files
  by hand without preserving mtimes, a genuinely newer remote fold can look
  `SAME`; re-pull it explicitly with a glob + `stale`.
- The report's "chỉ có ở Mac" list is runs no server has any fold of — usually
  the retired baseline family and the June runs. It is informational; nothing
  touches them.

## Long runs survive SSH drops

Every script tees to `logs/<name>_<timestamp>.log`. For a full 5-fold run
(hours), detach it so closing the terminal doesn't kill it:

```bash
tmux new -s train
bash run/train_teacher.sh TEACHER=efficientnetv2_m
# Ctrl-b then d to detach;  tmux attach -t train  to return
# or:  nohup bash run/train_teacher.sh TEACHER=efficientnetv2_m &>/dev/null &
```
