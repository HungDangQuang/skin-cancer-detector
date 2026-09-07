# `.pte` export manifest — 2026-08-24

Provenance for every ExecuTorch program in `exports/executorch/`. Produced by
`bash run/export_all_students.sh` on `vastnew` (executorch **1.4.1**, CPU-only).

`exports/` and `data/benchmark_set*/` are gitignored — this file is the tracked
record of what was built, so the binaries can be regenerated exactly.

## The 16 student arms

Each run-dir contributes its **median-behaving fold** — the fold closest to that
run's own 5-fold mean on AUPRC + pAUC, per `docs/ANDROID_APP_SPEC.md` §2 ("pick
the median fold, never the best one"). The fold therefore differs per arm.

| `.pte` | Source checkpoint | Backend | `max|Δlogit|` | `max|Δprob|` | Parity |
|---|---|---|---|---|---|
| `mobilenetv4_conv_medium__convnextv2_base_fold0.pte` | `kd_convnextv2_base_to_mobilenetv4_conv_medium/fold_0` | xnnpack | 4.13e-06 | 8.93e-07 | PASS |
| `mobilenetv4_conv_medium__efficientnetv2_m_fold4.pte` | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_4` | xnnpack | 5.53e-06 | 4.76e-07 | PASS |
| `mobilenetv4_conv_medium__maxvit_base_fold4.pte` | `kd_maxvit_base_to_mobilenetv4_conv_medium/fold_4` | xnnpack | 3.54e-06 | 3.44e-07 | PASS |
| `mobilenetv4_conv_medium__nokd_fold4.pte` | `baseline_mobilenetv4_conv_medium/fold_4` | xnnpack | 3.92e-06 | 5.80e-07 | PASS |
| `fastvit_sa12__convnextv2_base_fold4.pte` | `kd_convnextv2_base_to_fastvit_sa12/fold_4` | xnnpack | 1.70e-05 | 4.25e-06 | PASS |
| `fastvit_sa12__efficientnetv2_m_fold4.pte` | `kd_efficientnetv2_m_to_fastvit_sa12/fold_4` | xnnpack | 2.52e-05 | 6.28e-06 | PASS |
| `fastvit_sa12__maxvit_base_fold4.pte` | `kd_maxvit_base_to_fastvit_sa12/fold_4` | xnnpack | 2.28e-05 | 5.67e-06 | PASS |
| `fastvit_sa12__nokd_fold3.pte` | `baseline_fastvit_sa12/fold_3` | xnnpack | 6.30e-05 | 5.50e-06 | PASS |
| `repvit_m1_0__convnextv2_base_fold4.pte` | `kd_convnextv2_base_to_repvit_m1_0/fold_4` | xnnpack | 6.67e-06 | 1.01e-06 | PASS |
| `repvit_m1_0__efficientnetv2_m_fold0.pte` | `kd_efficientnetv2_m_to_repvit_m1_0/fold_0` | xnnpack | 8.75e-06 | 8.88e-07 | PASS |
| `repvit_m1_0__maxvit_base_fold1.pte` | `kd_maxvit_base_to_repvit_m1_0/fold_1` | xnnpack | 1.16e-05 | 1.15e-06 | PASS |
| `repvit_m1_0__nokd_fold1.pte` | `baseline_repvit_m1_0/fold_1` | xnnpack | 5.84e-06 | 6.86e-07 | PASS |
| `efficientformerv2_s2__convnextv2_base_fold0.pte` | `kd_convnextv2_base_to_efficientformerv2_s2/fold_0` | **none** | 3.41e-05 | 5.53e-06 | PASS |
| `efficientformerv2_s2__efficientnetv2_m_fold4.pte` | `kd_efficientnetv2_m_to_efficientformerv2_s2/fold_4` | **none** | 6.53e-05 | 6.51e-06 | PASS |
| `efficientformerv2_s2__maxvit_base_fold1.pte` | `kd_maxvit_base_to_efficientformerv2_s2/fold_1` | **none** | 1.56e-05 | 1.97e-06 | PASS |
| `efficientformerv2_s2__nokd_fold2.pte` | `baseline_efficientformerv2_s2/fold_2` | **none** | **5.57e-04** | 7.25e-06 | PASS |

Tolerance 1e-3, 100 samples, 0/100 over tolerance for every arm. Sizes: 32.1 MB
(mobilenetv4), 40.3 MB (fastvit), 24.5 MB (repvit), 48.0 MB (efficientformer).

Not listed: `exports/executorch/mobilenetv4_conv_medium.pte` (untagged) — the
first export ever made, 2026-08-23, from
`kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_4`. Same weights as the
`__efficientnetv2_m_fold4` file above; kept only for continuity with
`parity_mobilenetv4_conv_medium.json`.

## Three caveats to carry into the mobile benchmark

1. **`efficientformerv2_s2` needs `BACKEND=none`.** XNNPACK lowers it without any
   error and then computes logits of ~−2.2e10 against PyTorch's −3.15. Only the
   parity gate catches this. See `docs/GOTCHAS.md`. The portable-ops build is far
   slower (~70× on the 100-image sweep, server CPU) — so this architecture's
   on-device latency **must be measured**, never interpolated from the other
   three.
2. **Only one of the four efficientformer arms was observed to fail on XNNPACK**
   (`kd_convnextv2_base/fold_0`). The other three were exported straight to
   `BACKEND=none` on the assumption that mis-partitioning is a property of the
   architecture, not the weights. Reasonable, but untested.
3. **`efficientformerv2_s2__nokd_fold2` clears the gate by only 1.8×**, where the
   other arms clear it by 15–280×. In probability terms it is still negligible
   (7.25e-06 — the divergence lands on a saturated logit), so no decision
   changes; it is simply the arm to re-check first if the tolerance tightens.

## Reference logits (`ref_<arch>.csv`) — read before comparing

`run/make_benchmark_set.sh` names the reference **per architecture**, not per
checkpoint, so each `ref_*.csv` reflects whichever checkpoint was exported *last*
for that architecture:

| File in `data/benchmark_set/` | Corresponds to |
|---|---|
| `ref_mobilenetv4_conv_medium.csv` | `baseline_mobilenetv4_conv_medium/fold_4` |
| `ref_fastvit_sa12.csv` | `baseline_fastvit_sa12/fold_3` |
| `ref_repvit_m1_0.csv` | `baseline_repvit_m1_0/fold_1` |
| `ref_efficientformerv2_s2.csv` | `kd_convnextv2_base_to_efficientformerv2_s2/fold_0` |
| `ref_efficientformerv2_s2__nokd_fold2.csv` | `baseline_efficientformerv2_s2/fold_2` (pulled from the second batch's `benchmark_set_ef/`) |

**Comparing a `.pte` against the wrong `ref_*.csv` fails parity for a reason that
has nothing to do with the export.** To check any other arm, regenerate the
reference for that exact checkpoint first:

```bash
bash run/make_benchmark_set.sh N=100 MODEL=<arch> CKPT=experiments/runs/<run>/fold_<N>/checkpoints/best_model.pth
```

The per-arm numbers in the table above are already recorded in
`parity_<arch>__<tag>.json` next to this file, so nothing needs re-running to
quote them.

## Benchmark set

`data/benchmark_set/` — 100 images from the internal held-out test split
(50 malignant; isic2024 60 / pad_ufes_20 40), selected deterministically from
`cfg.seed`, so regenerating reproduces the identical set. Verified 2026-08-24:
the second batch's independently-built `data/benchmark_set_ef/` was byte-identical
(`manifest.csv` and `inputs.npy` md5s matched).

- `inputs/*.bin`, `inputs.npy` — fully preprocessed float32 CHW tensors. Feed
  these directly for **parity layer 1** (the model/lowering path).
- `images/*` — the original files. Preprocess these *in the app* and compare
  against `inputs/*.bin` for **parity layer 2** (the app's own decode + resize +
  normalize). Layer 2 is where the bilinear-vs-LANCZOS resize trap lives; see
  `docs/ANDROID_APP_SPEC.md`.
- `meta.json` — normalization constants, channel order, layout.
