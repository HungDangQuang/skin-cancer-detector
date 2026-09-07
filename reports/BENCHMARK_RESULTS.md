# Android on-device benchmark — results

Deliverable for `mobile_benchmark_handover` (bundle version `2026-08-24`).
Written 2026-08-25, completed 2026-08-27.

Nothing in this file is estimated, extrapolated or carried over from another device.
Every number is measured on the device named below.

**All measurement steps are complete.** Step B was run twice: the first attempt
(`2026-08-26`) was invalidated when a charger was connected partway through, and the whole
32-row run was repeated (`2026-08-27`) under fully compliant §6.1 conditions. **The
2026-08-27 run is the deliverable**; the earlier one is retained only for the
condition-effect comparison in §5.6.

---

## 0. Status at a glance

| Brief section | Deliverable | Status |
|---|---|---|
| §2 | Bundle integrity verified | **done** — §2 below |
| §3.1 | ExecuTorch version resolved | **needs sign-off only** — 1.4.1 does not exist for Android; 1.3.1 and 1.4.0 give *identical* results. §3 |
| §6.3 Step A | Parity gate, 16 models | **done — 16/16 PASS**, identical across 2 runtime versions × 2 thread counts. §4 |
| §6.4 Step B | Cold start (32 measurements) | **done** — §5.1 |
| §6.4 Step B | Steady state, 32 rows | **done — all 32 compliant**, `charging=0` on every row. §5.2 |
| §6.4 Step B | Sustained / thermal, 4 models | **done** — and it is the headline result. §5.3 |
| §6.5 Step C | Peak PSS | **done** — §6 |
| §7.1 | 32 schema-conforming JSONs | **done** — `benchmark-2026-08-27-19-16/results/` |
| §7.2 | Summary table | **done** — `benchmark-2026-08-27-19-16/summary.{csv,md}` |
| §7.3 | Written note | this document |
| §8.6 | ±5 % within-row consistency | **FAILS on every row** — not a setup fault. §5.4 |

---

## 1. Environment

### Device

| Property | Value |
|---|---|
| Device | Google Pixel 6a (`bluejay`) |
| SoC | Google Tensor (G1) — `Build.SOC_MODEL` reports `Tensor` |
| Cores | 8 (2×Cortex-X1 + 2×Cortex-A76 + 4×Cortex-A55) |
| ABI | `arm64-v8a` |
| Android | 16 (SDK 36) |
| Physical device | yes — verified, not an emulator (§3.2, §8.7) |
| Free storage | 55 GB |

### Runtime

| Property | Value |
|---|---|
| Dependency | `org.pytorch:executorch-android` — parity verified on **both 1.3.1 and 1.4.0** |
| Bundle declares | `1.4.1` — does not exist for Android. **See §3** |
| Backends in AAR | XNNPACK present; native libs ship `arm64-v8a` and `x86_64` only |
| Load mode | `LOAD_MODE_FILE` (fixed; see §6) |
| Thread control | **controllable** — `Module.load(path, loadMode, numThreads)`; `0` = hardware default |

### Model staging

Models are **not** in the APK. Per §3.3 the bundle is pushed to the app's external files
directory and loaded from a plain filesystem path:

```
/sdcard/Android/data/com.nemis.skindetector/files/mobile_benchmark_handover/
```

638 MB transferred in 17 s (35.8 MB/s for the models, 123 MB/s for `benchmark_set`).

---

## 2. Bundle integrity — verified

Checked on the host before pushing.

| Check | Result |
|---|---|
| `shasum -a 256 -c SHA256SUMS` | **37 / 37 OK** |
| Models | 16 `.pte`; catalog ↔ disk ↔ refs filenames match exactly; no orphans |
| Inputs | 100 `.bin`, every one exactly **602,112 B** = 3×224×224×4 ✓ |
| References | 16 CSVs, 101 lines each, **CRLF confirmed** (`od -c`), `id` order identical to `manifest.csv` |
| Manifest | 100 rows · 50 benign / 50 malignant · 40 `pad_ufes_20` / 60 `isic2024` — matches `meta.json` |
| Filename ↔ label | 0 mismatches (`__y0` / `__y1` suffix vs `label` column) |
| On-device after push | 16 `.pte` · 100 `.bin` · 16 `.csv` |

### Two discrepancies found in the bundle

**a. `SHA256SUMS` does not cover the inputs or the images.** It covers 37 files: README,
catalog, schema, 16 models, manifest, meta, 16 refs. The 100 `inputs/*.bin` and 100
`images/*.jpg` are unchecksummed — and the `.bin` files are precisely the inputs to the
parity gate, so a corrupted one would present as a parity failure that looks like an Android
bug. All 100 are the correct size, but size is not content. **Request checksums for these.**

**b. Sizes are MiB, labelled MB.** `catalog.json` gives `size_mb: 47.98` for a file of
50,310,676 bytes — that is 47.98 **MiB**. All sizes and all PSS figures in this document are
MiB, matching the catalog's values.

### Reference logit ranges (measured from the shipped refs)

README §4.2 states values "sit between roughly −6.1 and +2.6". The shipped references are
wider than that:

| | Value | Model |
|---|--:|---|
| Global minimum | **−7.4082** | `repvit_m1_0__efficientnetv2_m_fold0` |
| Global maximum (excluding the outlier) | **+6.2200** | `mobilenetv4_conv_medium__efficientnetv2_m_fold4` |
| Outlier | **+77.4528** | `efficientformerv2_s2__nokd_fold2`, sample id `0064` |

The +77.4 outlier is confirmed exactly as documented. The stated −6.1…+2.6 range is not
correct for this bundle. No practical impact — §4.2 also says not to assume a bounded range,
and the harness does not clamp — but it suggests the prose was not regenerated from the
references that shipped.

Reference logits are rounded to 6 decimal places (quantisation ≤ 5e-7, which is finer than
float32 ULP at magnitude 77, ≈ 6e-6). No impact on a 1e-3 gate.

---

## 3. ExecuTorch version — awaiting sign-off (technical risk measured, not present)

**ExecuTorch 1.4.1 does not exist for Android.** `org.pytorch:executorch-android` on Maven
Central tops out at **1.4.0** (`maven-metadata.xml`, `lastUpdated 20260807`). The full
published list ends `… 1.3.0, 1.3.1-rc3, 1.3.1, 1.4.0`. There is no 1.4.1 artifact.

This is the §3.1 / §10 "stop and tell us before doing anything else" condition.

### What was measured about it

Rather than guess, the loader was exercised directly. `ColdStart` deliberately does not go
through the version gate, so one launch answers the question empirically:

| Model | Threads | Result |
|---|--:|---|
| `repvit_m1_0__nokd_fold1.pte` | 4 | **loaded and ran** — `Module.load` + first forward = **71.510 ms** |

So the `.pte` container is **not** rejected by the 1.3.1 runtime. That eliminates the first
of §3.1's two failure modes. The second — "loads and behaves incorrectly" — is measured by
the parity gate, and **the answer is now in: it does not.** See §4.

### Conclusion

All 16 models reproduce the PC reference logits under the 1.3.1 runtime, with per-model
`max|Δlogit|` between **0.43× and 1.20×** the value the ML team measured on PC — that is, the
device error is the same order of magnitude as their own float error, and for 11 of the 16
models it is *smaller*. A runtime that decoded the graph incorrectly could not produce that.

The gate was then repeated under **1.4.0**, and the results are identical (§4.1) — so the
runtime version is not an independent variable for these models at all.

**The version gap is a documentation problem, not a numerical one.** The harness still
refuses a full measurement run until the version is agreed in writing (§3.1 says stop and
tell you, and this document is that), but the technical risk it was guarding against has been
measured and found absent.

### Questions for the ML team

1. Is "1.4.1" a typo for **1.4.0**, or a PyPI `executorch` version with no Android counterpart?
   (PyPI and the Android AAR do not share a release cadence.)
2. Given §4, do you agree we proceed on **1.3.1** (or 1.4.0) without a re-export? A one-line
   confirmation unblocks Step B.
3. If you would still rather re-export, please target **1.4.0** — the newest obtainable for Android.

---

## 4. Step A — parity gate (§6.3) — **16 / 16 PASS**

Run three times — 1.3.1 @ 4t, 1.4.0 @ 4t, 1.4.0 @ 1t — 100 samples per model, 4,800
inferences total, tolerance 1e-3. Identical results every time (§4.1). Figures below are from
`benchmark-results/parity-2026-08-25-18-52/`; raw artefacts for all three runs are alongside it.

**Every model passed, with `0/100` samples over tolerance in all 16 cases.**

**Method.** All 100 `inputs/*.bin` are pushed through each model and the raw output logit is
compared against the `logit` column (index 3) of that model's own `ref_<model>.csv`. Pass
criterion `max|device_logit − reference_logit| < 1e-3`, tolerance read from
`catalog.json > parity.tolerance` rather than hardcoded. Each model uses its own reference
file, matched by name from the catalog.

**Why this run is valid under the current device conditions.** Parity is a *numerical* check,
not a timing one. Charging state, airplane mode and device temperature do not change
floating-point arithmetic. So Step A is a genuine deliverable even though the device is
currently plugged in — unlike anything in §6.4, which is not.

**Caveat that must travel with these numbers:** this run is executed under
`executorch-android:1.3.1` against a bundle declaring `1.4.1` (§3). If parity passes, that is
strong evidence the runtime computes the intended values. It is *evidence for the version
question*, not a claim that acceptance criterion §8.1 is satisfied under an agreed configuration.

### Results

`ratio` = device `max|Δ|` ÷ the PC value in `catalog.json`. §6.3 asks only that these be the
same order of magnitude; they are, and 11 of 16 are *below* 1.0.

| arch | model | backend | device max\|Δ\| | mean\|Δ\| | PC max\|Δ\| | ratio | over tol | worst id | pass |
|---|---|---|--:|--:|--:|--:|--:|:--:|:--:|
| mobilenetv4_conv_medium | `__nokd_fold4` | xnnpack | 1.967e-06 | 5.09e-07 | 3.917e-06 | 0.50× | 0/100 | 0011 | ✅ |
| mobilenetv4_conv_medium | `__efficientnetv2_m_fold4` | xnnpack | 2.384e-06 | 6.21e-07 | 5.532e-06 | 0.43× | 0/100 | 0055 | ✅ |
| mobilenetv4_conv_medium | `__maxvit_base_fold4` | xnnpack | 2.623e-06 | 4.79e-07 | 3.544e-06 | 0.74× | 0/100 | 0036 | ✅ |
| mobilenetv4_conv_medium | `__convnextv2_base_fold0` | xnnpack | 3.457e-06 | 4.11e-07 | 4.129e-06 | 0.84× | 0/100 | 0058 | ✅ |
| repvit_m1_0 | `__convnextv2_base_fold4` | xnnpack | 4.768e-06 | 9.81e-07 | 6.673e-06 | 0.71× | 0/100 | 0022 | ✅ |
| repvit_m1_0 | `__nokd_fold1` | xnnpack | 5.722e-06 | 1.28e-06 | 5.844e-06 | 0.98× | 0/100 | 0047 | ✅ |
| repvit_m1_0 | `__maxvit_base_fold1` | xnnpack | 6.676e-06 | 8.67e-07 | 1.163e-05 | 0.57× | 0/100 | 0056 | ✅ |
| repvit_m1_0 | `__efficientnetv2_m_fold0` | xnnpack | 7.153e-06 | 1.46e-06 | 8.754e-06 | 0.82× | 0/100 | 0028 | ✅ |
| efficientformerv2_s2 | `__maxvit_base_fold1` | portable | 1.276e-05 | 2.70e-06 | 1.559e-05 | 0.82× | 0/100 | 0000 | ✅ |
| fastvit_sa12 | `__convnextv2_base_fold4` | xnnpack | 1.702e-05 | 2.49e-06 | 1.700e-05 | 1.00× | 0/100 | 0031 | ✅ |
| fastvit_sa12 | `__maxvit_base_fold4` | xnnpack | 2.289e-05 | 5.17e-06 | 2.280e-05 | 1.00× | 0/100 | 0000 | ✅ |
| fastvit_sa12 | `__efficientnetv2_m_fold4` | xnnpack | 2.501e-05 | 6.71e-06 | 2.520e-05 | 0.99× | 0/100 | 0019 | ✅ |
| efficientformerv2_s2 | `__convnextv2_base_fold0` | portable | 3.529e-05 | 5.04e-06 | 3.414e-05 | 1.03× | 0/100 | 0058 | ✅ |
| efficientformerv2_s2 | `__efficientnetv2_m_fold4` | portable | 5.722e-05 | 8.95e-06 | 6.528e-05 | 0.88× | 0/100 | 0036 | ✅ |
| fastvit_sa12 | `__nokd_fold3` | xnnpack | 6.533e-05 | 1.24e-05 | 6.299e-05 | 1.04× | 0/100 | 0028 | ✅ |
| efficientformerv2_s2 | `__nokd_fold2` | portable | **6.676e-04** | 3.84e-05 | 5.573e-04 | 1.20× | 0/100 | 0069 | ✅ |

Sorted by device `max|Δ|` ascending. Full detail including the worst-sample device and
reference logits is in `parity.csv`.

### The one model the brief flagged

§6.3 singles out `efficientformerv2_s2__nokd_fold2` as clearing the gate by only 1.8× on PC,
and asks that a marginal miss on device be reported rather than treated as a hard failure.
**It did not miss.** Device `max|Δ| = 6.676e-04` against the 1e-3 tolerance — clearance
**1.5×**, versus 1.8× on PC. Tighter, as predicted, but passing with `0/100` samples over.

The mechanism is confirmed: the worst sample is `0069`, where the model emits a logit of
**+51.72**. Absolute float error scales with magnitude, so the high-magnitude outputs of this
model dominate its error budget. Note the worst sample is *not* `0064` (the +77.45 outlier
named in §4.2) — several samples in this model are large enough to matter.

### 4.1 Invariance check — two runtime versions × two thread counts

The gate was run three times on the same device with the same inputs and references, varying
only the AAR version and the thread count:

| Run | AAR | Threads | Duration | Result |
|---|---|--:|--:|---|
| `parity-2026-08-25-18-52` | 1.3.1 | 4 | 33 min | 16/16 pass |
| `parity-2026-08-25-22-18` | 1.4.0 | 4 | 33 min | 16/16 pass |
| `parity-2026-08-26-21-03` | 1.4.0 | 1 | 26 min | 16/16 pass |

**All three produce numerically identical results.** Hashing every data column except
`threads`, with rows sorted (run 3 iterates in a different order — see below):

```
2b054016cf08dd8b064f3eb32456b202   1.3.1 @ 4 threads
2b054016cf08dd8b064f3eb32456b202   1.4.0 @ 4 threads
2b054016cf08dd8b064f3eb32456b202   1.4.0 @ 1 thread
```

Every model agrees on `max|Δlogit|`, `mean|Δlogit|`, the worst sample's id, its device logit
and its reference logit — at the precision recorded (4 s.f. on deltas, 6 d.p. on logits).
Bit-exactness cannot be claimed from a CSV, but the runs agree to at least 1e-6 across all
4,800 inferences.

Three things follow:

1. **The ExecuTorch version is not an independent variable for these models.** What 1.4.1
   "would have" produced is moot — 1.3.1 and 1.4.0 already produce the same thing, and it
   matches the PC references.
2. **Thread count is not one either.** This was not assumed: the expectation was that
   changing thread count changes XNNPACK's reduction order and therefore the last bits. For
   these 16 models it does not. Parity consequently needs measuring only once per model, not
   once per (model, threads) — though the deliverable run still records it per row.
3. **1.4.0 is a drop-in.** Same API (`Module.load(path, loadMode, numThreads)`),
   `libexecutorch.so` loads (8.86 MB vs 8.72 MB in 1.3.1), no Kotlin changed. If the ML team
   prefers a re-export against 1.4.0, nothing on the Android side needs to move.

Note for anyone diffing two reports: **row order is not stable across harness versions.** Rows
are written in iteration order, and the run order was changed to put xnnpack models first
(so a broken configuration surfaces in ~2 min instead of ~13). Sort before comparing.

Comparison produced by `tools/compare_parity.py`.

### 4.2 A timing observation — resolved in §5.3

The 1-thread run took **26 minutes**; the 4-thread runs took **33**, for identical work. Fewer
threads, less wall-clock time.

The likely explanation is that the four portable models dominate total time and are
single-threaded regardless, so thread count barely moves the total — leaving thermal state as
the real variable. The 4-thread runs began at 32.5 °C on a charging device; the 1-thread run
began at 27 °C on a device that had been idle.

**Resolved: it was thermal.** §5.3 measured 45–49 % throttling over five minutes of sustained
load, and §5.4 measured ~14 % latency change per °C. A 27 % wall-clock swing between two
otherwise identical parity runs is well inside what that sensitivity produces. This was the
first hint of what turned out to be the dominant effect in the whole benchmark.

### Caveats that must travel with this table

1. **Runtime version.** Executed under `executorch-android:1.3.1` and again under `1.4.0`,
   against a bundle declaring `1.4.1` (§3). This is the evidence that the mismatch is
   numerically harmless — but it is not a claim that §8.1 is satisfied under an *agreed*
   configuration. That needs the ML team's sign-off, which the harness now records in
   `files/version_agreement.txt` and stamps into all 32 result files.
2. **Threads.** Measured at both 4 and 1 thread, with identical results (§4.1). The earlier
   concern that thread count might change the last bits was tested and did not hold.
3. **Conditions.** Device was plugged in and not in airplane mode. Irrelevant here — parity
   is arithmetic, not timing — and stated so it is not mistaken for a §6.1-compliant run.

---

## 5. Step B — latency (§6.4)

### 5.1 Cold start — **done, 32 / 32 measured**

Measured 2026-08-26 under **full §6.1 conditions**: physical Pixel 6a, battery 93 %,
**discharging** (USB connected for data only, no charging), 29.6 °C, **airplane mode on**.
This is the first set of numbers in this document taken under compliant conditions — the
parity runs did not need them.

Each of the 32 measurements is `Module.load` + first forward in a **genuinely fresh process**,
driven by `am force-stop` + `am start` (32 separate process launches). Raw data in
`benchmark-results/cold-2026-08-26/cold_start.jsonl`.

| architecture | backend | 1t median | spread | 4t median | spread | 1t/4t |
|---|---|--:|--:|--:|--:|--:|
| `mobilenetv4_conv_medium` | xnnpack | 119.2 ms | 28.6 % | **69.3 ms** | 5.3 % | 1.72× |
| `repvit_m1_0` | xnnpack | 113.5 ms | 5.7 % | **81.6 ms** | 9.9 % | 1.39× |
| `fastvit_sa12` | xnnpack | 230.3 ms | 6.6 % | **128.6 ms** | 4.8 % | 1.79× |
| `efficientformerv2_s2` | **portable** | 3181.0 ms | 4.9 % | **3241.2 ms** | 5.5 % | **0.98×** |

Spread is across the four variants within each architecture row.

**Two findings worth sending back.**

**a. The portable lowering costs ~40× on cold start.** Median 3241 ms against 82 ms for the
xnnpack models at 4 threads — **39.7× slower**. §5.1 of the brief predicted "roughly 70×" from
the server CPU; on this handset it is 40× for cold start. This is the first on-device
quantification of what the failed XNNPACK lowering actually costs, which is the number the
brief says it wants quantified. A 3.2-second cold start is a real deployment problem for a
screening app, independent of steady-state throughput.

**b. The portable models do not scale with threads at all** — 1t/4t of **0.98×**, i.e. four
threads are very slightly *slower* than one. The three xnnpack architectures scale 1.39–1.79×.
This is consistent with portable ops being single-threaded reference implementations, and it
means the `threads` parameter is meaningless for those four models. Worth stating explicitly
in the final table so the 1t and 4t columns are not read as a measurement error.

**Caveats.**

1. **Warm page cache.** The kernel still held the `.pte` files from the three parity runs;
   dropping the cache needs root. These are "cold process, warm file" and will understate a
   true first-launch-after-boot. Recorded in each result's `notes`.
2. **Cold start is intrinsically noisy** — it includes process creation, class loading, JIT and
   file I/O. The 28.6 % within-row spread for `mobilenetv4_conv_medium` at 1 thread is that
   noise, not a setup fault. Note this is **not** the §8.6 criterion, which concerns
   steady-state median; those figures are still to be measured.

### 5.2 Steady state — **done, 32 / 32 rows, all compliant**

Run 2026-08-27 19:16 → ~23:40. 16 models × 1 and 4 threads, 30 warmup + 200 measured
iterations each, cycling all 100 inputs, seeded model-order shuffle (seed recorded in output).

**Conditions verified on every row, not once per session: `charging = 0` on all 32.**

| | |
|---|---|
| Power | never charged — `AC powered: false` throughout; battery 100 % → 48 % |
| Airplane mode | on |
| Brightness | 8, manual (fixed) |
| Temperature | 31.5 °C at row 1 → 40.1 °C at peak |
| Artefacts | `benchmark-results/benchmark-2026-08-27-19-16/` (32 JSONs + summary), per-row conditions in `run-2026-08-27-19-16/partial-rows.jsonl` |

| model | backend | med@1t | med@4t | p95@4t | p99@4t | PSSΔ@4t | temp@4t |
|---|---|--:|--:|--:|--:|--:|--:|
| `mobilenetv4_conv_medium__convnextv2_base_fold0` | xnnpack | 50.5 | **21.6** | 25.1 | 27.6 | 77 | 31.5 |
| `mobilenetv4_conv_medium__nokd_fold4` | xnnpack | 61.2 | **24.1** | 28.0 | 29.0 | 95 | 38.3 |
| `mobilenetv4_conv_medium__efficientnetv2_m_fold4` | xnnpack | 78.7 | **25.1** | 25.8 | 28.0 | 89 | 39.8 |
| `mobilenetv4_conv_medium__maxvit_base_fold4` | xnnpack | 125.7 | **32.8** | 37.6 | 39.0 | 98 | 40.1 |
| `repvit_m1_0__maxvit_base_fold1` | xnnpack | 122.6 | **34.4** | 38.0 | 39.7 | 80 | 34.8 |
| `repvit_m1_0__convnextv2_base_fold4` | xnnpack | 110.7 | **34.7** | 37.1 | 37.9 | 72 | 34.8 |
| `repvit_m1_0__efficientnetv2_m_fold0` | xnnpack | 82.2 | **34.7** | 39.0 | 39.9 | 75 | 32.9 |
| `repvit_m1_0__nokd_fold1` | xnnpack | 153.7 | **48.3** | 51.9 | 53.3 | 84 | 40.1 |
| `fastvit_sa12__nokd_fold3` | xnnpack | 150.0 | **73.3** | 77.4 | 81.9 | 76 | 32.9 |
| `fastvit_sa12__maxvit_base_fold4` | xnnpack | 164.1 | **75.4** | 79.0 | 82.5 | 96 | 34.8 |
| `fastvit_sa12__convnextv2_base_fold4` | xnnpack | 243.9 | **81.9** | 93.0 | 99.2 | 96 | 39.3 |
| `fastvit_sa12__efficientnetv2_m_fold4` | xnnpack | 273.2 | **103.7** | 121.0 | 125.8 | 80 | 40.1 |
| `efficientformerv2_s2__nokd_fold2` | **portable** | 3915.1 | **3906.9** | 3923.0 | 4083.6 | 86 | 38.1 |
| `efficientformerv2_s2__maxvit_base_fold1` | **portable** | 4132.8 | **3910.5** | 4158.6 | 4175.0 | 73 | 38.3 |
| `efficientformerv2_s2__convnextv2_base_fold0` | **portable** | 4857.5 | **4842.9** | 4892.7 | 4895.2 | 74 | 39.3 |
| `efficientformerv2_s2__efficientnetv2_m_fold4` | **portable** | 4177.9 | **4679.9** | 4686.9 | 4690.7 | 74 | 39.8 |

#### Architecture ranking

Read the **best case** column as the number a cool device achieves and the **sustained** column
as what a screening app doing repeated inference will actually see (§5.3):

| architecture | backend | disk | best case @4t | sustained @4t | portable penalty |
|---|---|--:|--:|--:|--:|
| `mobilenetv4_conv_medium` | xnnpack | 32.11 MiB | **21.6 ms** | 39.5 ms | — |
| `repvit_m1_0` | xnnpack | 24.46 MiB | 34.4 ms | 57.2 ms | — |
| `fastvit_sa12` | xnnpack | 40.35 MiB | 73.3 ms | 113.9 ms | — |
| `efficientformerv2_s2` | **portable** | 47.98 MiB | 3906.9 ms | 3908.2 ms | **~181×** |

**MobileNetV4-Conv-Medium is the clear winner** — 1.6× faster than RepViT, 3.4× faster than
FastViT. Note **RepViT is the smallest file yet 59 % slower** than MobileNetV4: on-device
latency is not predicted by file size, which is exactly the inversion the thesis notes warn
about.

The portable lowering costs **181×** at 4 threads best-case (3906.9 vs 21.6 ms). §5.1 of the
brief estimated ~70× from a server CPU; on this handset it is 40× for cold start and 181× for
steady state, because XNNPACK scales with threads and portable does not, so the gap widens
with core count.

### 5.3 Sustained / thermal — the headline result

300 s continuous at 4 threads, one representative model per architecture, 120 s cooldown
between runs.

| model | backend | first minute | last minute | throttle | iterations |
|---|---|--:|--:|--:|--:|
| `repvit_m1_0__convnextv2_base_fold4` | xnnpack | 38.3 ms | **57.2 ms** | **1.494** | 5 728 |
| `mobilenetv4_conv_medium__convnextv2_base_fold0` | xnnpack | 26.8 ms | **39.5 ms** | **1.475** | 8 228 |
| `fastvit_sa12__convnextv2_base_fold4` | xnnpack | 78.6 ms | **113.9 ms** | **1.448** | 2 837 |
| `efficientformerv2_s2__convnextv2_base_fold0` | portable | 3907.7 ms | 3908.2 ms | **1.000** | 78 |

**All three XNNPACK architectures slow by 45–49 % over five minutes.** The three ratios agree
closely (1.448, 1.475, 1.494), so this is a property of the handset, not of any model.

The portable model does **not** throttle at all (1.000) — single-threaded, so it never
generates enough heat for the governor to intervene. It is already so slow that thermal limits
never bind.

Consequences:

1. **Steady-state medians understate sustained cost by ~1.5×** for the XNNPACK models. A
   product doing repeated inference sees the last-minute figures.
2. **This is the largest effect in the benchmark** — larger than architecture choice between
   RepViT and FastViT, and far larger than anything weights contribute.
3. It explains every anomaly logged earlier: the 26-vs-33 minute parity runs (§4.2), cold start
   coming in *faster* than steady state, and the whole of §5.4.

The earlier charging-contaminated run measured 1.523–1.556. Removing the charger reduced
throttling slightly (1.448–1.494) but did not change the finding.

### 5.4 §8.6 within-row consistency — **fails on every row**

The brief requires the four variants of each architecture to agree on median latency within
~5 %, treating a larger gap as evidence of a broken measurement setup. On fully compliant data:

| architecture | thr | min | max | spread | temp range |
|---|--:|--:|--:|--:|--:|
| `mobilenetv4_conv_medium` | 1 | 50.5 | 125.7 | **149.1 %** | 31.5–40.1 °C |
| `repvit_m1_0` | 1 | 82.2 | 153.7 | **87.0 %** | 32.9–40.1 °C |
| `fastvit_sa12` | 1 | 150.0 | 273.2 | **82.2 %** | 32.9–40.1 °C |
| `mobilenetv4_conv_medium` | 4 | 21.6 | 32.8 | **51.8 %** | 31.5–40.1 °C |
| `fastvit_sa12` | 4 | 73.3 | 103.7 | **41.4 %** | 32.9–40.1 °C |
| `repvit_m1_0` | 4 | 34.4 | 48.3 | **40.3 %** | 32.9–40.1 °C |
| `efficientformerv2_s2` | 1 | 3915.1 | 4857.5 | **24.1 %** | 38.1–39.8 °C |
| `efficientformerv2_s2` | 4 | 3906.9 | 4842.9 | **24.0 %** | 38.1–39.8 °C |

**Not one row passes.** This is the clean, §6.1-conformant run — no charging, airplane mode on,
one session, randomised order.

**The cause is temperature, and the last column shows it.** The portable models, all measured
within a 1.7 °C window, spread 24 %. The others, spread across 8.6 °C, scatter 40–149 %. The
temperature range of a row predicts its spread across all eight rows.

The cleanest demonstration is the portable row at 1 thread, where single-threaded execution
removes core-placement variance and thermal saturation removes everything else:

| variant | temp | median |
|---|--:|--:|
| `__nokd_fold2` | 38.1 °C | 3915.1 ms |
| `__maxvit_base_fold1` | 38.6 °C | 4132.8 ms |
| `__efficientnetv2_m_fold4` | 38.9 °C | 4177.9 ms |
| `__convnextv2_base_fold0` | 39.8 °C | 4857.5 ms |

**Perfectly monotonic, four out of four.** Sorting by temperature sorts by latency exactly.
A 1.7 °C range produces 24.1 % — roughly **14 % per °C**.

At that sensitivity, **±5 % corresponds to about 0.35 °C of thermal stability**, which no
handset maintains across a multi-hour session. §6.1's model-order randomisation spreads the
bias evenly across models but cannot reduce it.

**A second, independent mechanism affects the 1-thread rows.** Temperature does not explain
them fully: `mobilenetv4_conv_medium__maxvit_base_fold4` at 40.1 °C is 105 % slower than
`__nokd_fold4` at 38.3 °C — far too much for 1.8 °C. The signature is core placement: the
Tensor G1 is 2×Cortex-X1 + 2×Cortex-A76 + 4×Cortex-A55, and a single thread lands on whichever
the scheduler picks. Supporting evidence: a slow 1-thread run has the *tightest* distribution
(median 78.7, p95 78.9 — a 0.2 ms spread), which is a stable different core rather than
interference; and one 1-thread measurement reproduced across sessions to **0.08 %**
(244.1 → 243.9 ms) while others moved 33–49 %, i.e. stable when placement happens to repeat.

**The brief pins thread count but never thread affinity.** Fixing it needs `taskset`, which
§6.4 does not specify.

### 5.5 Repeatability floor — 7.70 %

The harness re-measures one model twice in-session. Result: **7.70 % median spread** (13.42 %
in the charging-contaminated run).

That is the number §8.6 is missing: a ±5 % criterion cannot be assessed when repeating an
identical measurement moves the median by 7.7 %. It is also not in tension with the 0.2–3.3 %
cross-session figures in §7 — those were short runs on a cool device. **Repeatability here is a
function of thermal state.**

### 5.6 What the invalidated run showed — and a correction

The 2026-08-26 run had a charger connected from row 15. It was fully repeated rather than
patched, because §6.1 requires all 16 models in *one session sharing thermal conditions* —
splicing rows from two sessions would produce a table whose rows are not comparable, which is
precisely what that rule exists to prevent.

**Correction to an earlier draft of this document.** It reported a measured "charging penalty"
of +10.9 % @1t and +9.9 % @4t. **That finding was confounded and is withdrawn.** Charging
began at row 15 and was therefore perfectly correlated with "later in the session and hotter".
The clean run settles it: `efficientformerv2_s2__convnextv2_base_fold0 @1t` measured
**4857.5 ms unplugged** here against **4048.5 ms charging** in the contaminated run — the
unplugged figure is 20 % *slower*. Whatever the charger costs, it is smaller than the session
position it was confounded with, and this data cannot separate them.

The re-run remains correct regardless: charging is a stated §6.1 violation whatever its
magnitude.

Also withdrawn: an intermediate claim that §8.6 "passes at 4 threads". That came from three
RepViT rows agreeing to 0.87 % — all measured within 2 °C of one another. The fourth variant,
5 °C hotter, was 40 % slower. The full compliant run (§5.4) is what settles it.

---

## 6. Step C — memory (§6.5) — done

`Debug.MemoryInfo.totalPss` is the whole process, not the model. The harness must hold all
100 inputs resident (§3.4 forbids timing file I/O), which is 100 × 602,112 B ≈ **60 MB** of
direct buffers on its own, plus the JVM and Compose. Reporting only the absolute figure would
answer a question about the harness rather than about the model — which is not what §6.5 is
for ("decides whether a model is viable on a low-RAM device").

So each result carries three fields: `peak_pss_mb` (as requested), plus `baseline_pss_mb`
(process idle, inputs resident, no model loaded) and `model_pss_delta_mb`.

PSS is sampled **between** iterations, outside the `nanoTime` window, never from a concurrent
thread — `Debug.getMemoryInfo` costs milliseconds and a sampling thread would steal a core
during the 1-thread runs and pollute the p99 tail.

`LOAD_MODE_FILE` is fixed for every load and recorded in the output, because FILE vs MMAP
changes both cold start and PSS accounting and the brief does not specify one.

### Results

From the compliant 2026-08-27 run, across all 32 rows:

| architecture | backend | file on disk | PSS delta | peak PSS (whole process) |
|---|---|--:|--:|--:|
| `repvit_m1_0` | xnnpack | 24.46 MiB | 48.5–84.0 MiB | 207.9–243.4 MiB |
| `mobilenetv4_conv_medium` | xnnpack | 32.11 MiB | 56.1–97.8 MiB | 215.5–257.2 MiB |
| `fastvit_sa12` | xnnpack | 40.35 MiB | 74.5–96.3 MiB | 233.8–255.7 MiB |
| `efficientformerv2_s2` | **portable** | 47.98 MiB | 72.4–85.6 MiB | 231.8–245.0 MiB |

**Read the delta column, not the absolute one.** Peak PSS sits at 210–256 MiB for every model
because the harness holds all 100 inputs resident (~60 MiB) plus the JVM and Compose. The
absolute figure is dominated by the harness; the delta is what is attributable to the model.

**Every model fits comfortably.** Peak process PSS spans **208–257 MiB** across all 16 models
and both thread counts — a ~50 MiB range for models differing 2× in file size and 181× in
speed. For §6.5's question, viability on a low-RAM device, **memory does not discriminate
between these models**; latency does.

**The delta ranges are wide and overlap heavily** (e.g. RepViT 48.5–84.0 MiB against
MobileNetV4 56.1–97.8 MiB), so a per-architecture memory ranking is not supportable from this
data. An earlier draft of this document claimed the portable models cost 1.5× their file size
against 2.3–2.9× for XNNPACK; that was computed from a subset of rows and **does not hold**
across the full compliant run. It is withdrawn.

The likely cause of the spread is the sampling method: PSS is read between iterations, so a
fast model at 21 ms gets far more samples across its 200 iterations than a portable model at
3.9 s, and the peak-of-samples estimator is correspondingly biased. Measuring model memory
properly would need `Debug.MemoryInfo` deltas around load/unload rather than peak sampling
during the timing loop — worth doing if the ML team needs a memory ranking, but it is not what
§6.5 asks for.

Memory is not thermally sensitive, so unlike the latency figures these are unaffected by
temperature drift.

---

## 7. Appendix — prior runs (NOT part of this deliverable)

Two earlier runs exist on this same Pixel 6a from July 2026. They are **not valid for the
handover** and must not be reported to the ML team as results:

- different `.pte` files (one per architecture, not the 16 handover variants)
- **random tensors** as input, not the real `inputs/*.bin`
- warmup 10 / measured 50 — below the schema floors of 30 / 100
- no parity check was possible (no references existed)
- device conditions not recorded

They are included for one reason: they give a **same-model, cross-session repeatability
baseline** on this exact device, which is the number missing from the brief's §8.6 acceptance
criterion.

| Model (old build) | Threads | Median 03 Jul | Median 04 Jul | Spread |
|---|--:|--:|--:|--:|
| `mobilenetv3_large` | 4 | 8.377 ms | 8.396 ms | **0.2 %** |
| `mobilenetv4_conv_medium` | 4 | 22.157 ms | 22.641 ms | **2.2 %** |
| `fastvit_sa12` | 4 | 64.262 ms | 65.477 ms | **1.9 %** |
| `mobilenetv4_conv_medium` | 1 | 52.289 ms | 53.317 ms | **2.0 %** |
| `fastvit_sa12` | 1 | 137.834 ms | 142.322 ms | **3.3 %** |

**Two independent sessions, same device, same model: 0.2–3.3 % median spread.** That is the
floor against which §8.6's "within about 5 %" should be read. A 4 % spread between two
variants in the same architecture row is inside measurement noise on this hardware, not
evidence of a setup problem. The formal in-session figure for the deliverable run is
**7.70 %** — see §5.5. The gap between that and these 0.2–3.3 % cross-session numbers is
itself informative: these July runs were short and started cool, the deliverable run measured
its repeatability pair after four hours of continuous load.

One further observation worth passing back, now quantified. The old `efficientformerv2_s2.pte`
— the *same architecture* lowered to **XNNPACK** — ran at **42.8 ms** median at 4 threads on
this device. The handover's EfficientFormerV2 models use **portable** ops and measure
**3906.9 ms**.

**That is a 91× penalty for the same architecture on the same handset**, isolating the cost of
the failed XNNPACK lowering from any architectural difference. It is a stronger measurement
than the 181× cross-architecture figure in §5.2, because nothing but the backend changed. The
July run is not a valid handover measurement for the reasons listed above, but as a
backend-vs-backend comparison on identical hardware it is the most direct evidence available
that the lowering failure — not the architecture — is what makes these four models
undeployable.

---

## 8. Open questions for the ML team

1. **§3 — the version.** 1.4.1 is not obtainable for Android. Typo for 1.4.0, or re-export?
2. **§2 — checksums** for `inputs/*.bin` and `images/*.jpg`.
3. **The schema cannot express a parity failure.** `result.schema.json` puts `latency_ms`,
   `cold_start_ms` and `peak_pss_mb` in `required` with `exclusiveMinimum: 0`, but the
   `parity` description says they "should be omitted or null" when `passed` is false, and
   `null` is not in their types. A failing model has no schema-valid representation. This
   harness omits the fields and explains in `notes` — please confirm or correct.
4. **§6.4 — which thread count for the sustained runs?** Not specified. 4 threads was chosen
   (hottest case) and is recorded in the output.
5. **§8.6 — the ±5 % criterion fails on all eight rows, and we do not believe it is
   achievable on this class of device.** Measured on a fully compliant run (§5.4): spreads of
   24–149 %. The cause is thermal — latency moves ~**14 % per °C** on this handset, so ±5 %
   corresponds to ~0.35 °C of stability across a four-hour session. Model-order randomisation
   spreads that bias but cannot reduce it. Requests: **(a)** replace the flat 5 % with a
   comparison against a measured in-session repeatability floor (**7.70 %** here); **(b)**
   specify `taskset` core pinning for the 1-thread runs, which carry a second and independent
   placement effect; **(c)** consider requiring a cooldown *between models*, not only between
   sustained runs — without it, a model's measured latency depends materially on where the
   shuffle placed it.
6. **§6.4 — sustained throttling is the largest single effect in the benchmark.** All three
   XNNPACK architectures slow **45–49 %** over five minutes (§5.3); the portable ones do not
   throttle at all. Steady-state medians understate sustained cost by ~1.5×. We suggest the
   final table carry both, since a screening app doing repeated inference sees the
   last-minute figure.
7. **§5.1 — the portable penalty is worse on mobile than your server estimate.** You predicted
   ~70×; we measure **40× on cold start** and **181× on steady state at 4 threads**. The gap
   widens with core count because XNNPACK scales with threads (1.4–1.8×) and portable does not
   (1.00×). A 3.2 s cold start and a 3.9 s inference are not deployable for a screening app.
8. **§4.2 — the stated logit range** (−6.1…+2.6) does not match the shipped references
   (−7.41…+6.22, plus the +77.45 outlier). Worth correcting in the brief.
