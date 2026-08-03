---
name: review-slurm
description: Review Slurm scripts (slurm/*.slurm, _lib.sh, submit.sh) AND their documentation (slurm/README.md, docs/SLURM.md) for the UIT shared-cluster rules and known failure modes. Use when the user adds/edits a *.slurm script or its docs and asks "review my slurm script", "is this safe to submit", "check the cluster job/docs", "did I follow the shared-cluster rules". Enforces the no-kill/queue-don't-evict rule. NOT for actually submitting (use submit-slurm) and NOT for Python-side bugs (use review-training).
---

# review-slurm

Reviews `slurm/` scripts **and** the docs that describe them against the
hard-won rules of the UIT shared cluster (`slurm.uit.edu.vn`, shared `keg`
account). The cluster is shared and the account is shared — a script that kills
or preempts wins you nothing and breaks other people's runs. This skill catches
both the safety violations and the strict-mode/logging bugs that make a job
"run" with no output.

Scope: `slurm/*.slurm`, `slurm/_lib.sh`, `slurm/submit.sh`, `slurm/preflight.sh`,
`slurm/_template.slurm`, and the docs `slurm/README.md` + `docs/SLURM.md`.

## How to run

1. Diff in scope: `git diff HEAD -- slurm/ docs/SLURM.md`.
2. Run the **§3 + §4 lint from `validate-pipeline`** first (the grep-based slurm
   checks) — it mechanically catches most of section A/B below. Then walk this
   checklist for what grep can't see (logic, docs drift).
3. Report most-severe first. **Any** finding in section A (shared-cluster
   safety) is a blocker — call it out explicitly, never soft-pedal it.
4. Finish by cross-checking the docs (section E): the README/SLURM.md must match
   what the scripts actually do.

## A. Shared-cluster safety — BLOCKERS (the rule that overrides everything)

No `slurm/*.slurm` script we author may terminate, preempt, or reset another
user's work. If resources are exhausted the job goes `PD` (pending) and **waits**
— that is the only acceptable behavior.

- [ ] **No** `scancel`, `kill`, `pkill`, `killall`.
- [ ] **No** `nvidia-smi --reset-gpu` / `-r` / `--gpu-reset`.
- [ ] **No** `fuser -k`.
- [ ] **No** `#SBATCH --preempt`, **no** priority-bumping `#SBATCH --nice=-…`.
- [ ] **No** `scontrol requeue` / re-enabling `USE_CLUSTER_GPU_CHECK` (the
  cluster `gpu_check.sh` issues `scontrol requeue $SLURM_JOB_ID` internally and
  SIGTERMs our fallback — `_lib.sh::acquire_gpu` deliberately bypasses it).
- [ ] **MPS pipe dir is per-job-unique**: any `CUDA_MPS_PIPE_DIRECTORY=` includes
  `${SLURM_JOB_ID:-…}`/`$$` — never a bare shared `/tmp/nvidia-mps` (would
  collide with the system MPS daemon / other jobs).
- [ ] **GPU scripts request `--gres=mps:l40:N`, never `--gres=gpu`** — QOS `uit`
  caps `gres/gpu=0` per user, so a whole-GPU request sits `PD` forever
  (`QOSMaxGRESPerUser`). `validate-pipeline §3h` greps for this.

(These mirror `validate-pipeline §3f/§3g` and `submit-slurm`'s authoring table —
if any are present, stop and flag before any other comment.)

## B. Strict-mode & logging (the "ran with no output" class)

Every script sources `slurm/_lib.sh`, which sets `set -euo pipefail`.

- [ ] Script `source`s `slurm/_lib.sh` (else it loses strict mode AND the
  fallback `tee` log at `logs/<job>_<jobid>_runtime.log`).
- [ ] Every Slurm-provided var uses a `:-default`: `${SLURM_JOB_ID:-$$}`,
  `${SLURM_ARRAY_TASK_ID:-0}`, etc. A bare `${SLURM_JOB_ID}` dies with
  `unbound variable` when run outside `sbatch` or under some MPS configs.
- [ ] Cluster CLI tools not on every node (`nvidia-smi`, `gpu_check.sh`) are
  gated with `command -v` / `[ -x … ]` and have a fallback (use the
  `acquire_gpu` helper rather than re-implementing).
- [ ] `#SBATCH --output`, `--error`, and `--job-name` are all present (a missing
  `--job-name` makes `squeue -u keg --name=…` unable to find the job on the
  shared account).
- [ ] Output paths point at `logs/…`; the script is only ever submitted via
  `slurm/submit.sh` (which `mkdir -p logs` first — raw `sbatch` parses
  `--output=logs/…` before the script runs and Slurm 23 silently drops output
  if `logs/` is absent).

## C. Paths & portability
- [ ] No hardcoded `/datastore/${USER}/…` — `${USER}` is `keg` (shared). Use the
  `/datastore/keg/hungdang/…` default with a `DATASTORE_USER_DIR=` override.
- [ ] venv path `/datastore/keg/venv` activated via the `_lib.sh` helper
  (`load_python_env`), not re-hardcoded.
- [ ] Relative paths assume `$SLURM_SUBMIT_DIR` (`:-` guarded) or an explicit cd
  to the repo root, not the node's cwd.

## D. Fold loop & dependency logic
- [ ] **5-fold CV is ONE job that loops folds internally** (`for FOLD in
  ${FOLDS:-0 1 2 3 4}`), NOT a Slurm array — so one model = one job = one of the 5
  concurrency slots (see `11/12_train_*.slurm`). A heavy model is split across two
  jobs with `FOLDS="0 1 2"` + `FOLDS="3 4"`, not with `--array`. (Legacy
  `#SBATCH --array=0-4%2` is no longer used here; if you ever reintroduce an array,
  forward `SLURM_ARRAY_TASK_ID` to `data.fold` and keep `%N` ≤ the 5-job cap.)
- [ ] Student job doesn't assume the teacher checkpoint exists without checking
  (`test -s …/best_model.pth`) — order dependency, not a silent random-weight run.
- [ ] Aggregation/eval jobs read the fold-scoped run-dir convention
  (`experiments/runs/<run>/fold_{0..4}/`).

## E. Documentation consistency (the half that's easy to forget)
The user explicitly wants the **docs reviewed alongside the scripts**. Drift here
sends the next person down the wrong path.
- [ ] `slurm/README.md` and `docs/SLURM.md` describe the script as it now
  behaves — submit command, env-var overrides (`STUDENT=`, `RUN_DIR=`,
  `DATASTORE_USER_DIR=`), array layout, and produced log paths all match.
- [ ] Any new `*.slurm` script is listed/numbered consistently with the existing
  `NN_name.slurm` scheme and referenced from the README's workflow section.
- [ ] Example commands in the docs go through `bash slurm/submit.sh …`, never
  raw `sbatch`.
- [ ] The one-time-setup vs per-session distinction stays accurate if the change
  touches `setup_env.sh` / `preflight.sh`.
- [ ] If the change alters the shared-cluster rules or GPU-acquisition behavior,
  the corresponding note in `CLAUDE.md`'s "Recurring gotchas" / the `submit-slurm`
  skill is still correct (flag if it now contradicts the script).

## Don't
- Don't approve a script that newly introduces any section-A pattern, even
  "temporarily" or behind a flag — there is no acceptable use on this cluster.
- Don't review the script and skip the docs (or vice-versa) — the user asked for
  both, and doc drift is a real defect here.
