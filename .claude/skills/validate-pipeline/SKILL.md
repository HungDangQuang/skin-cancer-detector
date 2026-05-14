---
name: validate-pipeline
description: Static-check the pipeline (Python imports, Hydra config composition, slurm scripts) before submitting any cluster job. Use after touching src/, configs/, or slurm/ — or whenever a remote job died with an import or config error and you want to catch the next one locally.
---

# validate-pipeline

Catches the bugs that have actually bitten this project on the cluster, **without** spending Slurm time. Runs in seconds locally / on the login node. Designed around real failures we saw on `slurm.uit.edu.vn`:

- `ImportError: cannot import name 'DistillationLoss' from 'src.training.distillation'` — caught by **§1** (import sanity).
- `ConfigKeyError: Key 'model' is not in struct` from `OmegaConf.merge(cfg, {"model": ...})` — caught by **§2** (Hydra dry-load) + **§4** (anti-pattern grep).
- `SLURM_JOB_ID: unbound variable` under `set -euo pipefail` — caught by **§3** (slurm script lint).
- `nvidia-smi: command not found` spam — caught by **§3**.
- Hardcoded `/datastore/${USER}/...` when `${USER}` is a shared lab account — caught by **§3**.

## When to use

- Right after any change in `src/`, `configs/`, `scripts/`, or `slurm/` and **before** `bash slurm/submit.sh ...`.
- When a remote job failed with `ImportError`, `ConfigKeyError`, or an unbound-var bash trace — run this locally to catch the next one before re-submitting.
- Before merging any branch that touches the training pipeline.

## DO NOT

- Treat this as a substitute for `poc-smoke-test`. Static checks confirm "the wiring is plausible"; the smoke test confirms "training actually runs end-to-end". Use both.
- Skip the slurm script lint just because the Python parts pass. Several incidents on this project came from shell-side issues that the Python side never sees.

## 1. Python import sanity

Catches mismatches between `__init__.py` re-exports and the actual class/function names in submodules — these only fail at import time on the cluster, halfway through a job.

```bash
python -c "
import src.data
import src.models
import src.training
import src.evaluation
import src.utils
from src.models.registry import MODEL_REGISTRY
from src.training import Trainer, KDTrainer, BinaryDistillationLoss
print('imports ok |', len(MODEL_REGISTRY), 'models registered')
"
```

If anything fails, fix the real symbol name in the failing `__init__.py` before doing anything else.

## 2. Hydra config dry-load

Catches struct-mode merge errors (the `OmegaConf.merge(cfg, {"model": ...})` bug we hit), missing default groups, and unresolved interpolations — without launching training.

```bash
python -c "
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf
import os
cfg_dir = os.path.abspath('configs')

for root in ['config', 'config_poc']:
    with initialize_config_dir(version_base=None, config_dir=cfg_dir):
        cfg = compose(config_name=root)
        # Reproduce what train_teacher / train_student do:
        OmegaConf.set_struct(cfg, False)
        merged = OmegaConf.merge(cfg, {'model': OmegaConf.to_container(cfg.teacher, resolve=True)})
        assert merged.model.name, f'{root}: merged model has no name'
        print(f'{root:12s} ok | teacher={cfg.teacher.name} student={cfg.student.name}')
"
```

## 3. Slurm script lint

Greps every `slurm/*.slurm` and `slurm/_lib.sh` for known fragile patterns. Each finding is a real cluster failure mode we've already paid for.

```bash
echo "--- a) Slurm vars without :- default (set -u will kill the job) ---"
grep -nE '\$\{?SLURM_(JOB_ID|JOB_NAME|SUBMIT_DIR|NODELIST)\}?' slurm/*.slurm slurm/_lib.sh \
    | grep -vE ':-' \
    | grep -vE '^[^:]+:[0-9]+:#' \
    || echo "  (clean)"

echo "--- b) nvidia-smi without 'command -v' guard ---"
grep -nE '^[[:space:]]*nvidia-smi' slurm/*.slurm \
    | grep -vE 'command -v' \
    || echo "  (clean — all calls gated)"

echo "--- c) Hardcoded /datastore/\${USER}/ (shared lab accounts!) ---"
grep -nE '/datastore/\$\{?USER\}?' slurm/ docs/ -r 2>/dev/null \
    || echo "  (clean — using DATASTORE_USER_DIR pattern)"

echo "--- d) Raw sbatch instead of submit.sh ---"
grep -nE '^[^#]*\bsbatch\b' slurm/*.sh slurm/*.slurm 2>/dev/null \
    | grep -v 'slurm/submit.sh' \
    || echo "  (clean — only submit.sh runs sbatch)"

echo "--- e) Missing --output / --error / --job-name SBATCH directives ---"
for f in slurm/*.slurm; do
    for d in '#SBATCH --output' '#SBATCH --error' '#SBATCH --job-name'; do
        grep -q "${d}" "$f" || echo "  $f missing: ${d}"
    done
done

echo "--- f) Forbidden disruptive commands (kill other users' work) ---"
# Hard rule: no script may terminate, preempt, or reset shared resources.
# See .claude/skills/submit-slurm/SKILL.md "Authoring new *.slurm scripts".
# Skip bash-comment lines (start with #) but KEEP #SBATCH directives.
FOUND=$(grep -nE '\bscancel\b|\bpkill\b|\bkillall\b|^[[:space:]]*kill[[:space:]]|nvidia-smi[[:space:]]+(--reset-gpu|-r\b|--gpu-reset)|fuser[[:space:]]+-k|#SBATCH[[:space:]]+--preempt|#SBATCH[[:space:]]+--nice=-' slurm/*.slurm slurm/*.sh 2>/dev/null \
        | grep -vE ':[0-9]+:[[:space:]]*#[^S]')
if [ -n "${FOUND}" ]; then
    echo "  FAIL: forbidden patterns detected:"
    echo "${FOUND}"
else
    echo "  (clean — no scancel/kill/reset/preempt)"
fi

echo "--- g) MPS pipe dir must be per-job (no shared /tmp/nvidia-mps) ---"
# CUDA_MPS_PIPE_DIRECTORY must include ${SLURM_JOB_ID:-...} so jobs don't
# collide with the system-wide MPS daemon at /tmp/nvidia-mps.
BAD=$(grep -nE 'CUDA_MPS_PIPE_DIRECTORY[[:space:]]*=' slurm/*.slurm slurm/*.sh 2>/dev/null \
      | grep -vE 'SLURM_JOB_ID|job_tag|\$\$')
if [ -n "${BAD}" ]; then
    echo "  FAIL: MPS pipe dir not per-job-unique:"
    echo "${BAD}"
else
    echo "  (clean — MPS pipe dirs are per-job)"
fi
```

A clean run is silent except for the `(clean)` markers. Anything else is a finding to fix.

## 4. Code anti-patterns to look for (manual, in diffs)

These don't show up in greps but are easy to spot in `git diff`:

- `OmegaConf.merge(cfg, {"new_top_level_key": ...})` **without** a preceding `OmegaConf.set_struct(cfg, False)` — Hydra emits cfg in struct mode, struct-merge rejects new keys.
- `from .X import Y` in any `__init__.py` where `Y` doesn't appear as `class Y` or `def Y` in `X.py`. Easiest check: `grep -n "^class \|^def " src/<module>/X.py` and compare.
- `forward(x)` returning `(B, 1)` shape — `BinaryFocalLoss` and `BinaryDistillationLoss` expect `(B,)`. Always `.squeeze(1)`.
- A new `*.slurm` script that doesn't `source slurm/_lib.sh` — loses the fallback runtime log.

## 5. Pipeline prerequisite check

Catches "submitted student before teacher finished" — the student script will refuse to run, but you'd rather not waste a Slurm allocation finding out.

```bash
# Run this on the cluster before submitting 03_poc_student.slurm:
test -s experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth \
    && echo "teacher checkpoint OK" \
    || echo "MISSING — run 02_poc_teacher.slurm first and wait for [job] DONE"
```

## What "clean" looks like

```
imports ok | 3 models registered
config       ok | teacher=efficientnet_b4 student=efficientnet_b0
config_poc   ok | teacher=efficientnet_b4 student=efficientnet_b0
--- a) Slurm vars without :- default ---
  (clean)
--- b) nvidia-smi without 'command -v' guard ---
  (clean — all calls gated)
--- c) Hardcoded /datastore/${USER}/ ---
  (clean — using DATASTORE_USER_DIR pattern)
--- d) Raw sbatch instead of submit.sh ---
  (clean — only submit.sh runs sbatch)
--- e) Missing SBATCH directives ---
  (no output)
--- f) Forbidden disruptive commands ---
  (clean — no scancel/kill/reset/preempt)
--- g) MPS pipe dir per-job ---
  (clean — MPS pipe dirs are per-job)
```

If all seven sections pass, submit with confidence. If any fail, fix locally and re-run — don't rely on the cluster to surface the bug. Sections **(f)** and **(g)** are especially important: they enforce the shared-cluster rule that no script may kill or preempt other users' work.
