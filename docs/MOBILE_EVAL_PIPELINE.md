# Evaluation pipeline specification — server and mobile

Normative spec. Both implementations MUST follow it exactly; any deviation makes the two result
tables incomparable. Written 2026-09-26.

Scope: scoring one **fixed image bundle** with one **fixed checkpoint**, on two runtimes, and
producing two tables of identical structure. Anything not listed here is out of scope.

---

## 1. Unit of comparison

One checkpoint — a single fold, not a 5-fold mean. A 5-fold mean has no weight file and cannot be
installed on a phone. Pick the **median fold** (closest to the fold-mean on AUPRC and pAUC jointly),
never the best fold: choosing on the test set is selection bias.

The same checkpoint supplies both arms:

| Arm | Runtime | Weights |
|---|---|---|
| `server` | PyTorch eager | `fold_N/checkpoints/best_model.pth` |
| `mobile` | ExecuTorch `.pte` on the phone | the `.pte` exported **from that same file** |

If the two arms use different checkpoints, the comparison measures nothing. This has bitten the
project before (see `docs/GOTCHAS.md`, `.pte` parity needs the same `CKPT`).

---

## 2. The bundle

Produced by `scripts/make_mobile_eval_bundle.py`; the zip is the single source of truth for which
rows are scored.

```
mobile_eval_bundle/
├── manifest.csv        sample_id,dataset,image_file,image_id,label,source
├── meta.json           preprocessing constants + per-dataset row counts
├── images/<sample_id>.jpg
└── SHA256SUMS
```

Rules:

- `manifest.csv` row order **is** the scoring order. It is the concatenation of each dataset's
  `test_split.csv` **in file order** — no shuffling, no class balancing, no subsampling.
- `sample_id` is a zero-padded global index, unique across datasets, and is the join key for every
  downstream file.
- Images are copied **byte-for-byte** from `data/processed/`. They are already 224×224 (resized at
  `prepare` time with `Image.LANCZOS`). The bundle never re-encodes them.
- One bundle may hold several datasets. The `dataset` column splits them at scoring time, so one
  phone run covers all of them.

---

## 3. Per-image pipeline — the normative part

Identical on both arms. `meta.json` carries every constant; read it, do not hardcode.

```
1. READ      bundle bytes of images/<sample_id>.jpg          (no re-encode, no EXIF transform)
2. DECODE    JPEG -> 8-bit RGB, HWC, shape (224,224,3)
             - RGB, not BGR, not ARGB
             - no alpha premultiplication
             - no density/DPI scaling, no subsampling (inSampleSize = 1)
3. RESIZE    NONE. Assert width == 224 and height == 224; error the row if not.
4. SCALE     x = pixel / 255.0                                -> float32 in [0,1]
5. NORMALISE x = (x - mean) / std
             mean = [0.485, 0.456, 0.406]   std = [0.229, 0.224, 0.225]   (per channel, RGB order)
6. LAYOUT    transpose HWC -> CHW, then add batch dim -> (1, 3, 224, 224) float32, C-contiguous
7. FORWARD   one raw logit, shape (1,) or scalar. BATCH SIZE = 1.
8. EMIT      sample_id, logit
```

Step order matters: divide by 255 **before** subtracting the mean. Step 3 is the one most often got
wrong — scaling an already-224 image through a scaler introduces error that cannot be attributed
afterwards.

### What the model does NOT contain

No preprocessing, no `sigmoid`, no threshold, no probability calibration. The `.pte` ends at the raw
logit. Steps 9–11 happen **off-device**, once, from the emitted logits — never on the phone, so that
both arms share one implementation.

```
 9. PROB      p = sigmoid(logit)
10. THRESHOLD frozen Youden's J from the run's own internal val_predictions.csv.
              NEVER refit on the evaluation set.
11. METRICS   src/evaluation/metrics.py::compute_metrics(y_true, p, threshold)
```

---

## 4. Numeric contract

| Property | Value |
|---|---|
| Input shape | `(1, 3, 224, 224)` |
| Input dtype | `float32`, little-endian, C-contiguous |
| Channel order | RGB |
| Batch size | **1**, both arms |
| Device | server: **CPU**; mobile: phone CPU |
| CPU threads (server arm) | **pin it, and record it.** 8 is the measured sweet spot; see §4.1 |
| Output | one raw logit, unbounded. Observed across shipped references: **−7.41 … +6.22**, with one known model reaching **+77.45**. Do not clamp |
| Logit precision in output files | ≥ 7 significant digits (`%.7g`) |

### 4.1 Pin the server arm's thread count — it is neither free nor neutral

Measured on a 64-core host, batch-1 inference over this graph:

| Threads | ms/image | 70,883 images |
|--:|--:|--:|
| 64 (PyTorch default = all cores) | **723** | **~14 h** |
| 8 | **29.3** | 35 min |
| 1 | 43.5 | 51 min |

Letting PyTorch use every core is **25× slower** than 8 threads: synchronisation dominates a
tiny batch-1 graph. `scripts/infer_bundle.py` therefore defaults to `--threads 8`, not to the
library default.

Thread count also **changes the logits slightly**: 8 threads vs 1 thread gave
`max|Δlogit| = 2.0e-06`, mean 2.4e-07, with 100/600 rows differing by more than 1e-6. That is
~280× smaller than the export effect in §5 and ~500× below the 1e-3 parity tolerance, so it is
negligible — but it is not zero, so **pin the value and record it** rather than comparing two
runs that happened to use different thread counts. Note this contradicts what the on-device work
found (1 vs 4 threads gave identical logits on the phone); do not generalise either result across
platforms.

**The server arm MUST run on CPU with batch 1.** This is not a performance choice. The project's
routine evaluation runs on CUDA with batch 64 (`run/evaluate_external.sh` defaults `BATCH=64`,
`GPU=auto`; a driver log confirms `CUDA_VISIBLE_DEVICES=0`). Comparing a CUDA/batch-64 number against
a phone number mixes four divergence sources into one delta. Fixing the server arm to CPU/batch-1
leaves only two, and both are then attributable.

---

## 5. Divergence accounting

After §4 is honoured, three things still differ between arms — but only #2 is both unmeasured
and potentially material:

| # | Divergence | Status |
|---|---|---|
| 1 | PyTorch eager → ExecuTorch (XNNPACK or portable) | **Measured, and metric-neutral.** 2026-09-27, `mobilenetv4_conv_medium` over **70,883 images** on one host CPU at batch 1: `max|Δlogit| = 1.2e-05`, mean 1.4e-06, p99 6.0e-06, **0 rows above 1e-3** — and **every** metric in §6's table identical to 4 dp on all three datasets. Earlier evidence (100 images, 16 models): PC 3.92e-06 … 5.57e-04, Pixel 6a worst case 6.676e-04 |
| 2 | Host JPEG decoder (PIL / libjpeg) → Android decoder (libjpeg-turbo) | **Never measured.** Chroma upsampling may differ by a few LSB |
| 3 | CPU thread count, if the two arms differ | **Measured, negligible:** `max|Δlogit| = 2.0e-06` between 8 and 1 thread on the host (§4.1). Eliminate it by pinning the value |

Eliminated by §4, and therefore *not* part of the reported delta: CUDA↔CPU, and batch 64↔1.

**Attribution procedure.** Score 100 bundle rows twice on the phone: once from
`images/*.jpg` through steps 1–8, and once from pre-normalised `.bin` tensors (steps 7–8 only,
tensors supplied in the bundle's `l1_gate/`). The `.bin` delta isolates #1; the difference between
the two deltas is #2.

---

## 6. Output format — identical on both arms

Each arm writes one CSV. Same columns, same order, same row count as `manifest.csv`:

```csv
sample_id,logit,error
000000,-0.5613037,
000001,2.1068820,
000002,,decode_returned_null
```

- One row per manifest row. **Never omit a row**: a failure gets an empty `logit` and a non-empty
  `error`. A missing row is indistinguishable from a bug; an error row is data.
- `error` empty on success.

Both CSVs are then scored by the **same** program, `scripts/eval_from_logits.py`, which is what makes
the two tables structurally identical:

```
scripts/eval_from_logits.py --manifest manifest.csv --logits <arm>.csv \
    --threshold-from <run>/fold_N/val_predictions.csv --label server|mobile
```

It emits `metrics.json` and `table.md` with rows = dataset and a fixed metric set: `n`, `prevalence`,
`auprc`, `pauc_at_tpr80`, `auc_roc`, `sens_at_90spec`, `sens_at_95spec`, `sensitivity`,
`specificity`, `f1_score`, `brier`, `ece`. Running it twice with the same `--manifest` and the same
`--threshold-from` guarantees two tables that differ only in the numbers.

`--compare server_metrics.json mobile_metrics.json` then emits `comparison.md`: one row per dataset ×
metric with `server`, `mobile`, and `Δ = mobile − server`.

---

## 7. Reading the delta

- **Rank metrics** (`auprc`, `auc_roc`, `pauc_at_tpr80`, `sens_at_*spec`) are threshold-free, so a
  non-zero Δ can only come from §5.
- **Threshold-dependent metrics** (`sensitivity`, `specificity`, `f1_score`) additionally move if a
  logit crosses the frozen threshold. A handful of crossings out of tens of thousands of rows is
  expected and is not a defect.
- **Noise floor.** The project's single-fold rerun noise floor is **0.0053 AUPRC**
  (`experiments/_reproducibility/README.md`). A |Δ| below that is not evidence of anything. Note this
  floor comes from retraining, not from re-running inference; inference on a fixed checkpoint is
  deterministic, so a genuine runtime Δ should be far smaller.
- **Do not compare AUPRC across datasets.** Prevalence differs by ~100× between the in-domain set
  (~0.45%) and Fitzpatrick17k (50%), and AUPRC's random baseline is the prevalence. Across datasets,
  compare `auc_roc` and `pauc_at_tpr80` only. Within one dataset, across arms, every metric is fair.

---

## 7a. Run the two host arms SEQUENTIALLY, not in parallel

Measured 2026-09-27 on a 64-core host: running the PyTorch and ExecuTorch arms at the same time
(8 threads each) slowed the PyTorch arm from **29 ms/image to 91 ms** — 3.1× — while total CPU use
stayed near 830%, i.e. ~8 of 64 cores. The two processes contend rather than share, so

    sequential: 35 min + 12 min = ~47 min
    parallel:   max(95 min, 28 min) = ~95 min

Sequential is twice as fast. The ExecuTorch arm is roughly **2.7× faster than PyTorch eager** on the
same CPU (33 ms vs 91 ms under contention; 12 min vs 35 min solo), which is expected — XNNPACK is an
inference runtime, eager PyTorch pays per-op dispatch overhead.

## 8. Stop conditions

Report rather than work around:

- The `.bin` gate exceeds `max|Δlogit| ≥ 1e-3` on any model.
- Logits are not bit-identical when the first 500 rows are re-run.
- Logits change with thread count.
- More than 0.1% of rows error.
- Any urge to modify the `.pte`, re-export, or adjust a number so it matches.
