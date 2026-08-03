# Recurring gotchas (full reference)

These have all bitten this repo at least once. `CLAUDE.md` keeps a short index of
these under "Recurring gotchas"; this file holds the **full detail** for each one.
Run the `code-change` skill's `validate-pipeline` checks after touching `src/`, `configs/`, or `slurm/`
to catch them before submitting cluster jobs.

Sections are grouped: **hard rules** (never violate) → **live coding traps**
(easy to re-trip when writing new code) → **operational / postmortems**
(context for why a helper behaves the way it does) → **resolved** (historical,
kept for the paper trail).

---

## Hard rules (never violate)

### Shared-cluster rule for `*.slurm` scripts

UIT's cluster is shared. **No `slurm/*.slurm` script we author may terminate, preempt, or reset other users' work.** If resources are exhausted, the job goes into `PD` (pending) state and waits — that is the only acceptable behavior. Forbidden in every script: `scancel`/`kill`/`pkill`/`killall`, `nvidia-smi --reset-gpu`, `fuser -k`, `#SBATCH --preempt`, priority-bumping `--nice`, and any write to `/tmp/nvidia-mps` without a job-unique suffix. `validate-pipeline §3f / §3g` lint enforces this — see `.claude/skills/code-change/reference/submit-slurm.md` "Authoring new `*.slurm` scripts" for the full table and the queue-don't-evict rationale.

### QOS caps `gres/gpu=0` — jobs MUST request `--gres=mps`, never `--gres=gpu` (added 2026-06-28)

A "fix" (commit 8229197) tried to stop the MPS-OOMs by switching every GPU script from `--gres=mps:l40:N` to `--gres=gpu:l40:1` (exclusive whole GPU). **It made every job unschedulable** — they sat `PD` forever with `Reason=QOSMaxGRESPerUser` even while the user held 0 GPUs. Root cause confirmed on-cluster: QOS `uit` sets `MaxTRESPerUser = cpu=32,gres/gpu=0,gres/mps=20`. **`gres/gpu=0` per user → any whole-GPU request is rejected outright.** Every running job on the cluster uses `gres/mps:*`; nobody is allowed a whole GPU. The node `AsusL40` has `gpu:l40:8,mps:l40:800` → **100 MPS units per GPU**, and the 20-unit per-user cap = 20% of one GPU, so you **cannot** reserve a whole GPU via MPS either. Commit 8229197 was reverted (2026-06-28); all GPU scripts are back on `--gres=mps:l40:N` + `setup_mps`, and `mps:l40:4` keeps the 5-concurrent-jobs model (20 budget ÷ 4).

The real OOM cause (jobs 32552/32558, efficientnetv2_m, 2026-06-23) was **not** the gres type — it was `_lib.sh::acquire_gpu` blindly honoring Slurm's pinned `CUDA_VISIBLE_DEVICES=0` without re-checking VRAM. The `gres/mps` plugin schedules by compute-% and ignores GPU memory, so Slurm pinned the job to a GPU another user's ~38 GiB job had filled (7 MiB free) while GPUs 2 & 6 sat empty. **Fixed:** `acquire_gpu` now queries free VRAM on the Slurm-pinned GPU; if it's `< required_vram`, it unsets `CUDA_VISIBLE_DEVICES` and falls through to the existing `nvidia-smi --query-gpu=memory.free` selection to **hop to a GPU with enough free memory** (picks the emptiest, so it never starves a neighbor). This re-enables the smart selection that was previously dead code under MPS. **Verified on-cluster (POC job 34349, 2026-06-28):** Slurm pinned GPU 0 (9128 MB free < 12288 needed) → the guard hopped to GPU 4 and training ran to `[job] DONE` with no OOM — confirming the CVD override routes correctly under this MPS setup. If a GPU with enough free VRAM genuinely doesn't exist, the job picks the emptiest and may still OOM → that's a "wait for the cluster to drain" situation, not a code bug.

### Always submit through `slurm/submit.sh`

Raw `sbatch` parses `--output=logs/...` before the script runs. If `logs/` doesn't exist at submit time (Slurm 23 silently drops stdout/stderr), you get a job that "ran" with no log. `submit.sh` does `mkdir -p logs` first and forwards env vars via `--export=ALL,VAR=value`. Even if it does fall through, `_lib.sh` writes a fallback `tee` log at `logs/<job>_<jobid>_runtime.log` — always check that file when the SBATCH log is empty.

### `/datastore/${USER}` is wrong on shared lab accounts

On `slurm.uit.edu.vn`, multiple people share the `keg` account, so `${USER}` resolves to `keg` and the per-person subdir lives at `/datastore/keg/<name>/`. Scripts default to `/datastore/keg/hungdang/...` and accept a `DATASTORE_USER_DIR=...` env override. Don't reintroduce raw `/datastore/${USER}/...` — `validate-pipeline §3c` will flag it.

---

## Live coding traps

### Hydra struct mode

`@hydra.main(...)` returns `cfg` with `struct=True`. Adding a top-level key via merge raises `ConfigKeyError: Key '<X>' is not in struct`. Both training scripts inject `cfg.teacher` / `cfg.student` under a unified `cfg.model` key — that requires disabling struct first:

```python
OmegaConf.set_struct(cfg, False)
teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})
```

### Package re-exports

If `src/<pkg>/__init__.py` re-exports a symbol, the name has to match the actual `class`/`def` in the submodule. Renaming a class without updating `__init__.py` is the easy way to break the whole import graph from a Slurm job (`ImportError: cannot import name 'X' from 'src.<pkg>.<mod>'`). Static check: `python -c "import src.training, src.models, src.data, src.evaluation"`.

### Slurm scripts run under `set -euo pipefail`

`slurm/_lib.sh` enables strict mode for every job. Two consequences:

- Any reference to a Slurm-provided variable must use a `:-default` form, e.g. `${SLURM_JOB_ID:-$$}`. A bare `${SLURM_JOB_ID}` will kill the job with `unbound variable` if Slurm hasn't set it (running outside `sbatch`, or some MPS configurations).
- Cluster CLI tools that aren't on every node (`nvidia-smi`, `gpu_check.sh`) must be gated with `command -v` or `[ -x ... ]` and have a fallback path. The `acquire_gpu` helper in `_lib.sh` already implements the gpu_check.sh / nvidia-smi / default fallback chain.

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
- `drop_path_rate` (stochastic depth) is a per-model-config knob (default 0.0/off) passed via `create_timm_backbone` only when `>0`. Some timm archs may not accept the kwarg — if a run sets `drop_path_rate>0` and errors with `TypeError`, that arch doesn't support it; verify per-arch on the cluster.
- `val_metrics.json` is a new per-fold output (best-epoch val metrics). `aggregate_folds.py` still reads only `test_metrics.json`; the val file is for the val−test overfitting gap, computed separately.

### `load_config()` must compose Hydra defaults for the root config

`@hydra.main(...)` composes the `defaults:` list automatically, but our standalone scripts (`prepare_data.py`, etc.) use `src/utils/config.py::load_config("configs/config.yaml")`. Plain `OmegaConf.load` doesn't expand the `defaults:` list, so `cfg.data` is missing → `ConfigKeyError: Missing key data`. `load_config` now detects a `defaults:` key and calls `hydra.compose` to merge the groups. Already-resolved configs (saved `experiments/<run>/config.yaml`) lack `defaults:` and load as-is, so `evaluate.py`/`export_model.py`/`predict.py` are unaffected.

### NumPy 2.0 removed `np.trapz`

`np.trapz(y, x)` is gone — replacement is `np.trapezoid(y, x)` (added in 2.0). The cluster venv has NumPy 2.x. Any new metric/integration code should use `np.trapezoid`.

### `Trainer.history` populates differently from `KDTrainer.history`

`Trainer.history` declares `train_loss`/`val_loss`/`train_pauc`/`val_pauc` but historically only appended to `train_loss` and `val_loss`, leaving `val_pauc` as an empty list. `plot_training_curves` then got `epochs=(N,)` and `val_paucs=()` → matplotlib shape mismatch. Always append `val_pauc` per epoch in any new trainer subclass; `KDTrainer` already does this at `kd_trainer.py:104`.

---

## Operational / postmortems

### `keg` is a shared lab account — `squeue -u keg` shows everyone

When tracking your own jobs, filter by job name: `squeue -u keg --name=poc_teacher`. For postmortems use `sacct -u keg --starttime=$(date -d "1 hour ago" '+%H:%M:%S')`. Per-user job IDs are unique, so any single `squeue -j <jobid>` / `sacct -j <jobid>` still works without a filter.

### `/usr/local/bin/gpu_check.sh` is bypassed by default

The cluster's GPU dispatcher has a typo on line 31 (`nvidia-smi-i` instead of `nvidia-smi -i`) that makes it always false-negative AND it issues `scontrol requeue $SLURM_JOB_ID` internally before returning to us — so any fallback we run gets SIGTERM'd by Slurm seconds later. `_lib.sh::acquire_gpu` therefore picks a GPU itself via `nvidia-smi --query-gpu=memory.free` and skips the helper. Opt back in with `USE_CLUSTER_GPU_CHECK=1` only after UIT admin fixes the typo. **Do not** pass that env var to `submit.sh` in the meantime — it puts the job back into the requeue loop.

### Data-strategy ablations: `run_suffix` isolation + the two design traps (added 2026-06-21)

The data strategy (PAD mixing + undersampler) is ablated by `slurm/13_ablation_sampler.slurm` and `slurm/14_ablation_pad.slurm`. Three things that will silently invalidate a result if forgotten:

- **`run_suffix` (root `config.yaml`, default `""`)** is appended to the run-dir name (`kd_<teacher>_to_<student><suffix>/fold_N`) so an ablation arm never overwrites the main 30 runs. The ablation slurms set it (`__samp_off`, `__ratio3`, `__train_isic_only`, …). A new ablation that forgets `run_suffix` will clobber a real run.
- **`data.train_sources`** (in `configs/data/isic2024.yaml`, default `null`) filters **TRAIN+VAL only** — `SkinLesionDataModule._filter_to_sources` deliberately leaves the **test set whole** so both PAD-ablation arms share an identical held-out test (its PAD portion trained on by neither). Don't "helpfully" filter the test too; that breaks the comparison. It raises if a filter empties a split.
- **The PAD ablation must run baseline (no KD).** A teacher trained on ISIC+PAD leaks PAD via soft labels into the ISIC-only arm, confounding "does PAD data help". `14_ablation_pad.slurm` defaults `TRAINING=baseline` for this reason — only switch to KD if you also train a matched ISIC-only teacher.

Per-domain (ISIC vs PAD) verdicts read the `source` column in `predictions.csv` (written by `Evaluator.save_predictions`, derived via `source_from_path`). Quote **AUPRC** over AUC-ROC at this prevalence.

### `maxvit_base` cuDNN backward error + the `cudnn_deterministic` lever (added 2026-06-23)

POC smoke-test of the 3 SOTA teachers (jobs 32296/32297/32298): `convnextv2_base` and `efficientnetv2_m` PASS; **`maxvit_base` FAILS at `loss.backward()` with `RuntimeError: cuDNN error: CUDNN_STATUS_INTERNAL_ERROR`** (forward completes — not a tag/shape bug; timm tags + head dims of all 3 are confirmed correct). Two likely causes, in order: (1) **VRAM exhaustion** — maxvit_base (~119M + windowed/grid attention) has the largest backward activation footprint, and cuDNN masks workspace-alloc OOM as INTERNAL_ERROR; it failed even at POC batch 16, so batch 64 is worse. (2) deterministic-cuDNN incompatibility. Fixes available (combine both when retrying maxvit):
- **`cudnn_deterministic`** (root `config.yaml`/`config_poc.yaml`, default `true` = the bit-exact 30-run baseline behavior). `set_seed(seed, deterministic=...)` now honors it: `false` → `cudnn.deterministic=False` + `cudnn.benchmark=True` (lets cuDNN pick a working algo). Both training scripts pass `cfg.get("cudnn_deterministic", True)`. Override per-run: `cudnn_deterministic=false`. Only the convnextv2/efficientnetv2_m/maxvit teachers need consider this; the baseline 30 runs keep the default `true`.
- For the VRAM cause: lower `training.batch_size` and raise `acquire_gpu` for maxvit only (it's resolution-locked to 224, so batch is the only memory lever). If it still OOMs at small batch, maxvit_base is impractical on this MPS setup — drop it and keep convnextv2_base/efficientnetv2_m as the SOTA teachers.
- Both levers reach the training scripts via the `EXTRA=` passthrough on `11/12/02/03` (space-separated Hydra overrides, forwarded verbatim and word-split at the call site — quote it as one shell arg). Retry: `bash slurm/submit.sh slurm/02_poc_teacher.slurm TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=8"` (POC), then `slurm/11_train_teacher.slurm TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=16"` (real).

---

## Resolved (historical — kept for the paper trail)

### `pauc_at_tpr()` — FIXED 2026-06-04, now the real ISIC 2024 metric

Historically [src/evaluation/metrics.py](../src/evaluation/metrics.py) integrated raw TPR and divided by 0.2, so values ran ~[0.9, 5.0] instead of [0, 0.2] — they were **not** the official metric. `pauc_at_tpr()` now implements the competition's exact formulation: flip labels/scores (`v_gt = 1 - y_true`, `v_pred = -y_prob`), take `roc_auc_score(v_gt, v_pred, max_fpr=1-min_tpr)` (McClish-corrected), then invert the McClish scaling. Range is now **[0.5·max_fpr², max_fpr] ≈ [0.02, 0.20]** for min_tpr=0.80 (random ≈ 0.02, perfect = 0.20). `tests/test_metrics.py` asserts perfect ≈ 0.2. `val_pauc=…` logs, the `pauc_at_tpr80` JSON field, and `delta_pauc` are now quotable as the ISIC 2024 metric. (The threshold metrics `acc/sens/spec/f1` remain sklearn-direct and correct as before.)

### Baseline (no-KD) student training — FIXED 2026-06-04 via `use_kd` flag

Previously `KDTrainer.__init__` read `cfg.training.distillation` unconditionally and `train_student.py` always built a `KDTrainer`, so any `training=baseline` run crashed with `ConfigAttributeError: Missing key distillation` (jobs 26729/26730/26731, 2026-05-30). Now `scripts/train_student.py` reads `use_kd = cfg.training.get("use_kd", True)` and branches: **`use_kd: true`** (`distillation.yaml`) → `KDTrainer` + frozen teacher + `BinaryDistillationLoss`, run-dir `kd_<teacher>_to_<student>/`; **`use_kd: false`** (`baseline.yaml`) → plain `Trainer` + `BinaryFocalLoss`, no teacher load, run-dir `baseline_<student>/`. The baseline arm of the 30-run experiment is now runnable: `bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=<s> TRAINING=baseline`.

### PAD-UFES-20 `img_id` already includes the file extension — FIXED 2026-06-07

PAD's `metadata.csv` stores `img_id` **with** the extension (e.g. `PAT_8_15_820.png`), and the image files on disk are named identically. The old `process_pad_ufes_20()` did `images_dir / f"{img_id}.png"` → looked for `PAT_8_15_820.png.png`, matched nothing, and `continue`d on **every** row → empty `records` → `KeyError: 'label'` on the summary line (job 28239, the first time PAD ever ran — the repo had been ISIC-only). Fixed: look up `images_dir / img_id` as-is first (then `stem+.png/.jpg` fallbacks for a bare-id mirror), derive processed names from `Path(img_id).stem` (so no `pad_….png.jpg`), and **raise a clear `RuntimeError`** ("0 of N rows produced an image…") instead of a cryptic `KeyError` when nothing matches. Lesson for any new auxiliary dataset: never assume the metadata id is extension-free — probe `head -3 metadata.csv` + `ls images/` first.
