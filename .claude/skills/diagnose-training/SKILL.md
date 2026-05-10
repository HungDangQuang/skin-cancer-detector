---
name: diagnose-training
description: Diagnose a training run that finished, failed, or is misbehaving. Use when the user asks "why isn't training improving", "training looks weird", "diagnose this run", "is this checkpoint any good", or shares a log/checkpoint path and wants analysis.
---

# diagnose-training

Systematic diagnosis of a training run: check whether the loss is dropping, the metric is improving, gradients are flowing, and whether known failure modes (class collapse, NaN, leakage) are present.

## When to use

- User shares a `logs/<job>_<jobid>.out` or `experiments/<run>/training_curves.png` and asks what's wrong.
- A POC or full training run completed but `val_pauc` is stuck at 0 or near random.
- KD soft loss is suspiciously high relative to hard loss (or vice versa).
- A re-run produces different results than expected.

## Where to look (in order)

### 1. The fallback runtime log
```bash
cat logs/<jobname>_<jobid>_runtime.log
```
This is the most reliable log — written by `slurm/_lib.sh` via `tee`. Even if SBATCH redirect failed, this exists. The diagnostic header at the top tells you: jobid, hostname, working dir, GPU acquired.

### 2. The SBATCH stdout/stderr
```bash
tail -200 logs/<jobname>_<jobid>.out
tail -50  logs/<jobname>_<jobid>.err
```

### 3. The training curves PNG
`experiments/<run>/training_curves.png` — quick visual check. If `val_loss` is flat or rising while `train_loss` drops → overfitting or leakage.

### 4. The saved config
```bash
cat experiments/<run>/config.yaml
```
Confirm the hyperparams that actually ran (Hydra resolves overrides at runtime).

### 5. The Slurm postmortem
```bash
sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode,WorkDir
```

## Common failure modes

| Symptom | Likely cause | Where to confirm |
|---|---|---|
| `val_pauc` stuck at 0 across all epochs | All predictions same class — head bias collapsed | Check `pauc_at_tpr` returns 0 because `mask.sum() < 2` in `src/evaluation/metrics.py:30`; print prob distribution |
| `train_loss` drops, `val_loss` flat/rising | Data leakage OR severe overfitting | Confirm `StratifiedGroupKFold` grouped by `patient_id` in `scripts/prepare_data.py`; check val set has malignant samples |
| `loss=nan` on first iter | LR too high, or label dtype mismatch | Check `cfg.training.optimizer.lr_*` against `configs/training/distillation.yaml` defaults; ensure labels cast to float in the dataset |
| KD `soft_loss` ≈ 0 from epoch 1 | Teacher logits collapsed (always negative or positive) | `python -c "import torch; ckpt = torch.load('teacher.pth'); print(ckpt['model_state_dict'].keys())"` then run inference on val |
| `val_pauc` jumps wildly between epochs | Validation set too small (POC has only 36) | Expected for POC; only meaningful with full data |
| `Job exited code 10` in log | gpu_check.sh requeued — Slurm will retry | Wait; not a failure |
| `Job exited code 11` in log | 5× requeue exhausted | Lower `REQUIRED_VRAM` arg in `acquire_gpu` call |
| `import` errors at start | venv outdated | Re-run `bash slurm/setup_env.sh` on login node |

## Quick checks

### Is the checkpoint actually trained?
```python
import torch
ckpt = torch.load("path/to/best_model.pth", map_location="cpu", weights_only=False)
print(list(ckpt.keys()))                              # expect 'model_state_dict' + meta
print(ckpt.get("epoch"), ckpt.get("metrics"))         # which epoch saved + val metrics
state = ckpt["model_state_dict"]
total_params = sum(v.numel() for v in state.values())
print(f"Params loaded: {total_params:,}")
```

### Loss components for a KD run (read from log)
```bash
grep -E "Epoch [0-9]+/[0-9]+" logs/<run>_runtime.log
```
Expected pattern:
```
Epoch 1/2 | train_loss=X (hard=Y, soft=Z) | val_loss=W val_pauc=V
```
Both `hard` and `soft` should be > 0 and decreasing.

## Don't conclude prematurely

- **POC val_pauc may be low even when working** — synthetic data with 30 malignant samples gives noisy val metrics. The signal: `train_loss` should drop epoch-over-epoch.
- **One bad epoch ≠ broken training** — early stopping uses `patience` for a reason.
- **Always check the config that ran** (`experiments/<run>/config.yaml`), not what's currently in `configs/`. Hydra overrides may have shifted things.
