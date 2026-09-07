# Recurring gotchas (full reference)

These have all bitten this repo at least once. `CLAUDE.md` keeps a short index of
these under "Recurring gotchas"; this file holds the **full detail** for each one.
Run the `code-change` skill's `validate-pipeline` checks after touching `src/`, `configs/`, or `run/`
to catch them before launching jobs on the GPU server.

Sections are grouped: **hard rules** (never violate) → **live coding traps**
(easy to re-trip when writing new code) → **operational / postmortems**
(context for why a helper behaves the way it does) → **resolved** (historical,
kept for the paper trail).

---

## Hard rules (never violate)

### Everything stays inside the project folder (shared server)

The GPU box (`islabworker2@islab-server2`) is shared with other people and the repo lives on a NAS mount at `/mnt/sharednas/binhnt/hungdang/skin-cancer-detector`. **No `run/*.sh` may touch anything outside the project directory.** Forbidden everywhere: `sudo`, `apt`/`apt-get install`, the system python, edits to `~/.bashrc`/`~/.zshrc`, and killing other people's processes (`pkill`/`killall`/`nvidia-smi --reset-gpu`/`fuser -k`). Dependencies go in `./.venv-linux` (export tooling in `./.venv-export`); env vars are set per session, preferably from inside the repo. `validate-pipeline §3e / §3f` lint enforces this. The user audits it.

### The server root `/` has been 100% full — set `TMPDIR` inside the project

Anything that spills to `/tmp` can fail with `OSError: [Errno 28] No space left on device` even though the NAS has terabytes free. Per session, before a long job: `export TMPDIR="$(pwd)/.tmp"` (and `mkdir -p "$TMPDIR"`). NFS also produces harmless `Device or resource busy` tracebacks on file deletion — those are noise, not failures.

### Never overwrite an existing run-dir — and teachers isolate differently from students

`scripts/train_student.py` honours `run_suffix=` ([train_student.py:71](../scripts/train_student.py#L71)/[:93](../scripts/train_student.py#L93)), but **`scripts/train_teacher.py` does not** — its run-dir is hard-wired to `<output_dir>/teacher/<name>/fold_N` ([train_teacher.py:39](../scripts/train_teacher.py#L39)). A teacher ablation launched with `run_suffix=` therefore silently writes straight into the main teacher run and destroys it. Isolate teacher variants with `output_dir=` instead — that is why the ISIC-only teacher arm lives under `experiments/runs_isic_only/`. `validate-pipeline §3d` greps for this.

### One process per GPU unless you pin different ids

`run/common.sh::select_gpu` auto-picks the freest GPU (`GPU=auto`), so two jobs launched at once can land on the same card and OOM each other. Pin explicitly (`GPU=0` / `GPU=1`) when running concurrently, or use `run/train_kd_parallel.sh`, which is VRAM-gated (starts a job only when running-jobs < `MAX_JOBS` **and** free VRAM ≥ `MIN_FREE_MB`). Measured 2026-08-13 on the 3090: a single KD job already saturates the GPU, so extra concurrency does **not** finish sooner — it only adds OOM risk. `MAX_JOBS=2` is the safe cap.

---

## Live coding traps

### Hydra struct mode

`@hydra.main(...)` returns `cfg` with `struct=True`. Adding a top-level key via merge raises `ConfigKeyError: Key '<X>' is not in struct`. Both training scripts inject `cfg.teacher` / `cfg.student` under a unified `cfg.model` key — that requires disabling struct first:

```python
OmegaConf.set_struct(cfg, False)
teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})
```

### Package re-exports

If `src/<pkg>/__init__.py` re-exports a symbol, the name has to match the actual `class`/`def` in the submodule. Renaming a class without updating `__init__.py` is the easy way to break the whole import graph at job start (`ImportError: cannot import name 'X' from 'src.<pkg>.<mod>'`). Static check: `python -c "import src.training, src.models, src.data, src.evaluation"`.

### Runner scripts run under `set -euo pipefail`

`run/common.sh` enables strict mode for every job. Two consequences:

- Every `KEY=VALUE` knob must be read as `${KEY:-default}` (or `${KEY:?message}` when required). A bare `${FOLDS}` kills the job with `unbound variable` the moment the caller omits it.
- CLI tools that aren't on every box (`nvidia-smi`, `tmux`) must be gated with `command -v` or made non-fatal (`2>/dev/null` + a default). `select_gpu` in `run/common.sh` already implements the nvidia-smi / fallback chain.

### timm `num_features` is unreliable as the head input dim

`timm.create_model(name, num_classes=0).num_features` reports the *pre-classifier* channel count, which is NOT always what `forward(x)` emits. MobileNetV3-Large reports 960 but the `conv_head` expansion runs anyway and the forward output is 1280. Building the head with 960 channels then feeding it 1280 → `RuntimeError: mat1 and mat2 shapes cannot be multiplied (BxC1 and C2x1)`. Always use `infer_backbone_out_dim(backbone)` from `src/models/heads.py` — it runs a one-sample dummy forward and returns the true output dim. EfficientNet and MobileViT happen to be self-consistent, but use the helper for new architectures too as a safety net.

### `cfg.data.label_col` is the *raw* column name, not the in-memory one

`configs/data/isic2024.yaml` sets `label_col: target` because ISIC's `train-metadata.csv` uses that column name. `process_isic2024()` reads `target` from the raw CSV but writes the same value into the processed dataframe under the column name `"label"` (matching `SkinLesionDataset`'s schema). When calling `generate_group_kfold_splits()` on the processed dataframe, pass `label_col="label"` — passing `cfg.data.label_col` ("target") gives `KeyError: 'target'`.

### `patient_id` must be namespaced when datasets are concatenated

`generate_group_kfold_splits()` groups by `patient_id` to keep all of a patient's lesions in one fold (no leakage). When ISIC 2024 and PAD-UFES-20 are concatenated, a PAD `patient_id` could numerically collide with an ISIC one, silently merging two unrelated patients into one group (or worse, splitting the same logical group). `process_pad_ufes_20()` therefore writes `patient_id` as `pad_{raw_id}`. Keep any new auxiliary dataset's group key namespaced the same way. Also note: the offline cleaner drops corrupt / too-small (`min_size`) / blank (`is_uninformative`) / exact-duplicate (md5 of resized pixels) images and logs them to `data/processed/<ds>/excluded_images.csv` — dedup is per-dataset and exact-pixel only. See `docs/PREPROCESSING.md` for the full spec and which proposal augmentations were intentionally NOT implemented.

### Augmentation is config-driven; don't edit ops in `transforms.py` alone (added 2026-06-21)

`build_transforms` builds the pipeline **from `configs/augmentation/{light,heavy}.yaml`** via an internal `name → Albumentations` registry — it no longer hard-codes the op list (it used to, and silently ignored those YAMLs). Consequences:

- To change augmentation, edit the **YAML**, not `transforms.py`. Adding a new op also needs a builder entry in `_TRANSFORM_BUILDERS`; an unknown `name` raises.
- `augmentation=light` (default) reproduces the original hard-coded pipeline → the 30-run baseline is reproducible. `augmentation=heavy` is the stronger anti-overfit variant.
- **MixUp / CutMix / CoarseDropout(CutOut) are forbidden in code** (`_FORBIDDEN_OPS` → `ValueError`), enforcing the docs/PREPROCESSING.md decision. Don't add them to the YAML expecting them to run.
- `drop_path_rate` (stochastic depth) is a per-model-config knob (default 0.0/off) passed via `create_timm_backbone` only when `>0`. Some timm archs may not accept the kwarg — if a run sets `drop_path_rate>0` and errors with `TypeError`, that arch doesn't support it; verify per-arch on the server.
- `val_metrics.json` is a new per-fold output (best-epoch val metrics). `aggregate_folds.py` still reads only `test_metrics.json`; the val file is for the val−test overfitting gap, computed separately.

### `load_config()` must compose Hydra defaults for the root config

`@hydra.main(...)` composes the `defaults:` list automatically, but our standalone scripts (`prepare_data.py`, etc.) use `src/utils/config.py::load_config("configs/config.yaml")`. Plain `OmegaConf.load` doesn't expand the `defaults:` list, so `cfg.data` is missing → `ConfigKeyError: Missing key data`. `load_config` now detects a `defaults:` key and calls `hydra.compose` to merge the groups. Already-resolved configs (saved `experiments/<run>/config.yaml`) lack `defaults:` and load as-is, so `evaluate.py`/`export_model.py`/`predict.py` are unaffected.

### NumPy 2.0 removed `np.trapz`

`np.trapz(y, x)` is gone — replacement is `np.trapezoid(y, x)` (added in 2.0). The server venv has NumPy 2.x. Any new metric/integration code should use `np.trapezoid`.

### `Trainer.history` populates differently from `KDTrainer.history`

`Trainer.history` declares `train_loss`/`val_loss`/`train_pauc`/`val_pauc` but historically only appended to `train_loss` and `val_loss`, leaving `val_pauc` as an empty list. `plot_training_curves` then got `epochs=(N,)` and `val_paucs=()` → matplotlib shape mismatch. Always append `val_pauc` per epoch in any new trainer subclass; `KDTrainer` already does this at `kd_trainer.py:104`.

### Bootstrap CIs: never pool the 5 folds' `predictions.csv` (added 2026-08-23)

The 5 folds are **5 different models scored on the same test rows**, not 5 disjoint samples. Concatenating `fold_*/predictions.csv` therefore replicates every test row 5×, and a bootstrap over that pool reports an interval ~√5 too narrow — a fabricated result, not a conservative one. `scripts/bootstrap_ci.py` instead draws **one** row-index set per replicate, scores **every** fold on those same rows, and averages → a replicate of exactly the "mean ± std over 5 folds" quantity the tables already quote. It asserts the folds share identical labels *and row order* before starting, and refuses to run rather than guess.

Two more things that are easy to get wrong here:

- **Pair the KD delta.** KD and baseline are scored on identical rows, so resample them with the *same* index draw and bootstrap `Δ` directly. An unpaired interval discards that correlation and badly overstates uncertainty: on HAM10000 the per-run AUPRC intervals for `kd_convnextv2_base_to_mobilenetv4` (0.4198 [0.3959, 0.4440]) and its baseline (0.3754 [0.3578, 0.3996]) **overlap**, yet the paired delta is +0.0445 [+0.0353, +0.0527] — unambiguously non-zero. Same for a fairness gap: bootstrap `light − dark` itself, don't eyeball two intervals.
- **A single-class resample is undefined, not zero.** `pauc_at_tpr()` and `sensitivity_at_specificity()` both *return 0.0* when only one class is present — a sentinel, not a measurement. Averaging those into the replicate vector drags the interval down. Map them to `NaN` and drop them from the percentiles (`bootstrap_ci.py::_metric` does, and reports `n_dropped`). This bites hardest exactly where CIs matter most: small subgroups like Fitzpatrick's 137-image dark-tone group.

### `.pte` parity: the checkpoint must be identical on both sides (added 2026-08-23)

`run/check_pte_parity.sh` compares the ExecuTorch program against `data/benchmark_set/ref_<model>.csv`. That reference is written by `run/make_benchmark_set.sh MODEL=… CKPT=…`, and the `.pte` by `run/export_executorch.sh MODEL=… CKPT=…` — **pass the same `CKPT` to both**. Different folds of the same architecture are different models, so a mismatch fails parity for a reason that has nothing to do with the lowering, and the failure message will point you at the exporter. Confirmed working 2026-08-23: `mobilenetv4_conv_medium` fold_4 gives `max|Δlogit|` 5.53e-06 against a 1e-3 tolerance.

This only covers **layer 1** (`torch.export` → edge → XNNPACK). Layer 2 — whether the Android app's own decode/resize/normalize reproduces `inputs/*.bin` — is a separate in-app check, and the bilinear-vs-LANCZOS resize trap lives there (`docs/ANDROID_APP_SPEC.md`). Passing layer 1 is what makes an app-side discrepancy *diagnosable*: the model is exonerated, so the bug is in the app.

### A `.pte` can export "successfully" and still compute garbage (added 2026-08-24)

Exporting `efficientformerv2_s2` with the default `BACKEND=xnnpack` **succeeded** — no error, no warning, a plausible 47 MB `.pte` — and the program then returned logits around **−2.24e10** where PyTorch gives −3.15 (`max|Δprob|` 0.956, 100/100 samples over tolerance). XNNPACK mis-partitioned the architecture and nothing on the export path noticed. Re-exported with `BACKEND=none` (portable ops), the same checkpoint passes at `max|Δlogit|` 3.41e-05.

Two consequences:

- **A successful export is not evidence of a correct model.** Only `check_pte_parity.sh` distinguishes the two, which is why it is a *gate*, not a report. Treat "export exited 0" as meaning nothing until parity passes. `run/export_all_students.sh` therefore falls back to `BACKEND=none` on a **parity** failure, not just on an export failure.
- **The portable-ops backend is dramatically slower.** The same 100-image parity sweep took ~11 s on the XNNPACK builds and ~12.5 min on the portable-ops `efficientformerv2_s2` — roughly 70×. That is a CPU-on-server number, not a phone number, but a student that can only be lowered without XNNPACK carries a real deployment cost, and the on-device latency claim for it must be measured, never inherited from the other students.

Measured 2026-08-24 on `vastnew`, executorch 1.4.1. The other three students (`mobilenetv4_conv_medium`, `fastvit_sa12`, `repvit_m1_0`) all pass on XNNPACK.

### Re-running `prepare` to add metadata columns silently drops PAD → different splits (added 2026-08-24)

The documented way to enable direction D on finished checkpoints was "re-run `prepare` with `data.metadata_cols=[…]`, splits are seed-deterministic so only columns change". That reasoning holds **only if the inputs are identical**, and on a box that has `data/processed/` but not `data/raw/`, they are not:

- `scripts/prepare_data.py` guards PAD with `if pad_raw.exists():` — no `data/raw/pad_ufes_20/` means the "PAD-UFES-20 not found — using ISIC 2024 only" branch runs, every PAD row disappears from the dataframe, and `StratifiedGroupKFold` re-partitions **a different population**. The new `test_split.csv` would not be the test set the 95 finished fold-runs were scored on, and nothing would warn you — the job exits 0.
- `process_isic2024` also opens `train-image.hdf5` unconditionally (existence check + `h5py.File`), so 1.3 GB of images must be present even though every already-resized JPG is skipped.

Use `run/attach_metadata.sh` instead: it only **appends columns** to the existing split CSVs and prediction CSVs, so membership cannot change, and it needs `train-metadata.csv` alone (246 MB, no images, no PAD raw, no GPU). Positional back-fill is legitimate because `predictions.csv` is written row-aligned to `test_dataloader()` (`shuffle=False`) and `train_sources` filters train+val only — but the script *verifies* it per file (row count, `y_true` vs the split's `label` sequence, `source` sequence) and skips + exits non-zero rather than trusting it. Every file touched is copied to `reports/_metadata_backup/<timestamp>/` first.

Note the asymmetry this creates: a run trained with `data.train_sources=[isic2024]` has a **filtered** val set, so its `val_predictions.csv` will (correctly) fail the row-count guard against the unfiltered `val_split.csv`. That is the guard working, not a bug — those runs live in `experiments/runs_isic_only/` and are not part of the default `RUNS_DIR`.

---

### A framing/crop variant of an external set needs its own `data/processed/` tree

`_clean_external_image` (`src/data/preprocessing.py`) opens with a fast-path:

```python
if dst.exists():
    return Image.open(dst).convert("RGB"), None
```

That is what makes re-running `prepare_external.sh` cheap — but it keys on the
**destination path only**. It has no idea what `image_size`, `min_size` or
`center_crop_frac` produced the file already sitting there. Point two different
`center_crop_frac` values at one `processed_dir` and the second one reloads the
first one's pixels, writes a split CSV that *looks* like a crop variant, and
exits 0. You then get a full 19-run × 5-fold sweep whose `crop70` numbers are
byte-identical to `headline` — and the natural reading of that ("cropping makes
no difference") is exactly the wrong conclusion.

`prepare_external_data.py` therefore derives the directory from the variant key
(`data/processed/fitzpatrick17k_crop70/`) rather than letting a caller pass one.
If you add a variant that changes **pixels** in any other way, do the same.

Two companion checks in the same code path:

- **Row count must match the headline.** `min_size` is checked on the RAW frame
  *before* the crop, so cropping cannot drop rows the headline kept — that
  ordering is what keeps the framing delta paired. Prepare still warns on a
  count mismatch, which then means a missing/unreadable source file, not a
  selective crop.
- **`is_uninformative` (tier 2) fires more often on crops** — a close-up of
  uniform skin is flatter than a whole-limb photo. It still only flags, never
  drops (`docs/PREPROCESSING.md §1.1`), but compare `quality_flags` counts
  across variants before attributing a metric change to framing.

Full design + how to read each outcome: `docs/PREPROCESSING.md §1.2`.

---

## Operational / postmortems

### Track your own jobs — the box is shared

There's no scheduler, so a long run is just a process. Launch under `tmux` (or `nohup`) so an SSH drop doesn't kill it, and find it again with `ps -ef | grep train_`, `nvidia-smi` (which PIDs hold VRAM), or the transcript at `logs/<name>_<timestamp>.log`. Only kill PIDs you started.

### Data-strategy ablations: `run_suffix` isolation + the two design traps (added 2026-06-21)

The data strategy (PAD mixing + undersampler) is ablated by `run/ablation_sampler.sh` and `run/ablation_pad.sh`. Three things that will silently invalidate a result if forgotten:

- **`run_suffix` (root `config.yaml`, default `""`)** is appended to the run-dir name (`kd_<teacher>_to_<student><suffix>/fold_N`) so an ablation arm never overwrites the main 30 runs. `run/ablation_sampler.sh` / `run/ablation_pad.sh` set it (`__samp_off`, `__ratio3`, `__train_isic_only`, …). A new ablation that forgets `run_suffix` will clobber a real run.
- **`data.train_sources`** (in `configs/data/isic2024.yaml`, default `null`) filters **TRAIN+VAL only** — `SkinLesionDataModule._filter_to_sources` deliberately leaves the **test set whole** so both PAD-ablation arms share an identical held-out test (its PAD portion trained on by neither). Don't "helpfully" filter the test too; that breaks the comparison. It raises if a filter empties a split.
- **The PAD ablation must run baseline (no KD).** A teacher trained on ISIC+PAD leaks PAD via soft labels into the ISIC-only arm, confounding "does PAD data help". `run/ablation_pad.sh` defaults `TRAINING=baseline` for this reason — only switch to KD if you also train a matched ISIC-only teacher.

Per-domain (ISIC vs PAD) verdicts read the `source` column in `predictions.csv` (written by `Evaluator.save_predictions`, derived via `source_from_path`). Quote **AUPRC** over AUC-ROC at this prevalence.

### `maxvit_base` cuDNN backward error + the `cudnn_deterministic` lever (added 2026-06-23)

POC smoke-test of the 3 SOTA teachers (jobs 32296/32297/32298): `convnextv2_base` and `efficientnetv2_m` PASS; **`maxvit_base` FAILS at `loss.backward()` with `RuntimeError: cuDNN error: CUDNN_STATUS_INTERNAL_ERROR`** (forward completes — not a tag/shape bug; timm tags + head dims of all 3 are confirmed correct). Two likely causes, in order: (1) **VRAM exhaustion** — maxvit_base (~119M + windowed/grid attention) has the largest backward activation footprint, and cuDNN masks workspace-alloc OOM as INTERNAL_ERROR; it failed even at POC batch 16, so batch 64 is worse. (2) deterministic-cuDNN incompatibility. Fixes available (combine both when retrying maxvit):
- **`cudnn_deterministic`** (root `config.yaml`/`config_poc.yaml`, default `true` = the 30-run baseline behavior; NOT bit-exact — see below). `set_seed(seed, deterministic=...)` now honors it: `false` → `cudnn.deterministic=False` + `cudnn.benchmark=True` (lets cuDNN pick a working algo). Both training scripts pass `cfg.get("cudnn_deterministic", True)`. Override per-run: `cudnn_deterministic=false`. Only the convnextv2/efficientnetv2_m/maxvit teachers need consider this; the baseline 30 runs keep the default `true`.
- For the VRAM cause: lower `training.batch_size` and raise `acquire_gpu` for maxvit only (it's resolution-locked to 224, so batch is the only memory lever). If it still OOMs at small batch, maxvit_base is impractical on this MPS setup — drop it and keep convnextv2_base/efficientnetv2_m as the SOTA teachers.
- Both levers reach the training scripts via the `EXTRA=` passthrough on `11/12/02/03` (space-separated Hydra overrides, forwarded verbatim and word-split at the call site — quote it as one shell arg). Retry: `bash run/poc.sh STAGE=teacher TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=8"` (POC), then `run/train_teacher.sh TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=16"` (real).

---

## Resolved (historical — kept for the paper trail)

### `pauc_at_tpr()` — FIXED 2026-06-04, now the real ISIC 2024 metric

Historically [src/evaluation/metrics.py](../src/evaluation/metrics.py) integrated raw TPR and divided by 0.2, so values ran ~[0.9, 5.0] instead of [0, 0.2] — they were **not** the official metric. `pauc_at_tpr()` now implements the competition's exact formulation: flip labels/scores (`v_gt = 1 - y_true`, `v_pred = -y_prob`), take `roc_auc_score(v_gt, v_pred, max_fpr=1-min_tpr)` (McClish-corrected), then invert the McClish scaling. Range is now **[0.5·max_fpr², max_fpr] ≈ [0.02, 0.20]** for min_tpr=0.80 (random ≈ 0.02, perfect = 0.20). `tests/test_metrics.py` asserts perfect ≈ 0.2. `val_pauc=…` logs, the `pauc_at_tpr80` JSON field, and `delta_pauc` are now quotable as the ISIC 2024 metric. (The threshold metrics `acc/sens/spec/f1` remain sklearn-direct and correct as before.)

### Baseline (no-KD) student training — FIXED 2026-06-04 via `use_kd` flag

Previously `KDTrainer.__init__` read `cfg.training.distillation` unconditionally and `train_student.py` always built a `KDTrainer`, so any `training=baseline` run crashed with `ConfigAttributeError: Missing key distillation` (jobs 26729/26730/26731, 2026-05-30). Now `scripts/train_student.py` reads `use_kd = cfg.training.get("use_kd", True)` and branches: **`use_kd: true`** (`distillation.yaml`) → `KDTrainer` + frozen teacher + `BinaryDistillationLoss`, run-dir `kd_<teacher>_to_<student>/`; **`use_kd: false`** (`baseline.yaml`) → plain `Trainer` + `BinaryFocalLoss`, no teacher load, run-dir `baseline_<student>/`. The baseline arm of the 30-run experiment is now runnable: `bash run/train_student.sh STUDENT=<s> TRAINING=baseline`.

### PAD-UFES-20 `img_id` already includes the file extension — FIXED 2026-06-07

PAD's `metadata.csv` stores `img_id` **with** the extension (e.g. `PAT_8_15_820.png`), and the image files on disk are named identically. The old `process_pad_ufes_20()` did `images_dir / f"{img_id}.png"` → looked for `PAT_8_15_820.png.png`, matched nothing, and `continue`d on **every** row → empty `records` → `KeyError: 'label'` on the summary line (job 28239, the first time PAD ever ran — the repo had been ISIC-only). Fixed: look up `images_dir / img_id` as-is first (then `stem+.png/.jpg` fallbacks for a bare-id mirror), derive processed names from `Path(img_id).stem` (so no `pad_….png.jpg`), and **raise a clear `RuntimeError`** ("0 of N rows produced an image…") instead of a cryptic `KeyError` when nothing matches. Lesson for any new auxiliary dataset: never assume the metadata id is extension-free — probe `head -3 metadata.csv` + `ls images/` first.

### Training throughput: validation was ~90% of every KD epoch (added 2026-09-03)

Measured on `vastnew` (RTX 3090), `kd_maxvit_base_to_fastvit_sa12` fold 0: the
**train** phase is 91 batches in **3 min 21 s**, but the whole epoch took
**32 min 19 s**. The other ~29 minutes were validation, and inside it the
*teacher* dominated — `maxvit_base` is **47.8 GFLOPs** against
`fastvit_sa12`'s **3.0** (`reports/benchmark/*.json`), i.e. **~94%** of the val
forward. `KDTrainer._val_epoch` was re-running that teacher forward over all
62,041 val rows once per epoch, 50 times.

**It never had to.** The val pipeline is `Resize + Normalize + ToTensorV2`
(`configs/augmentation/*.yaml` `val:` has no random op), `val_dataloader()` is
`shuffle=False`, `set_epoch()` only touches the *train* sampler, and the teacher
is frozen. So the teacher's val logits are constant across epochs. Verified
empirically, three passes over the val loader: `max|delta| = 0.000e+00`,
`torch.equal == True`.

Levers now available (all default-on where exact, all off where they change math):

| knob | where | effect |
|---|---|---|
| `training.cache_val_teacher_logits` | KD configs, default `true` | compute the teacher's val logits once, replay them. **Exact** — `val_loss`, early stopping and checkpoint selection are unchanged. |
| `training.eval_batch_size` | all training configs, default `0` = same as `batch_size` | bigger val/test batch. Eval-mode BatchNorm uses running stats, so per-sample outputs don't change. |
| `persistent_workers`, `prefetch_factor` | root `config.yaml`, default `true` / `4` | stop re-forking the worker pool every epoch; queue batches ahead. Ignored when `num_workers=0`. |
| `num_workers` | root `config.yaml`, default `4` | **raise it at launch on a big box** (`EXTRA="num_workers=16"`). The vast box has 64 cores and a 3.1 GB dataset that fits entirely in page cache; 4 workers were starving the GPU. |

Two traps hit while adding these:
- **Hydra struct mode**: the code reads the new keys with `.get(key, default)`, so a
  run *works* without declaring them — but `training.cache_val_teacher_logits=false`
  on the CLI dies with `Key ... is not in struct`. A knob you intend to override
  must be declared in the config file, `configs/training/poc.yaml` included.
- **Don't A/B this by re-running and diffing losses.** Two runs of the identical
  config diverge at epoch 1 anyway (see the noise floor in
  `experiments/_reproducibility/README.md`), so the comparison proves nothing.
  Test the *premise* (are the teacher's logits constant?) instead.
