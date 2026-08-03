---
name: code-change
description: >
  Implement any code/config/slurm change and carry it through the project's mandatory
  modification workflow — edit → area-specific review → propagate to slurm+docs → static
  validate → run on the cluster. Use when the user asks to "change/add/remove code", "fix
  the trainer / loss / sampler / split", "add a new model architecture", "run POC / smoke
  test", "submit a job", "validate the pipeline", "author a new slurm script", or "run the
  full cycle / ship this end to end". It routes to the right detailed checklist in
  reference/ based on WHICH files you touched. NOT for judging a finished run's results
  (use eval-results) and NOT for teaching project concepts (use tutor-knowledge).
---

# code-change

The single entry-point for **making a code/config/slurm change and getting it safely to the
cluster**. This project forbids running Python/pytest/training on the Mac (local ≠ runtime),
so the loop here is: edit → review against the area contract → propagate to the slurm wrapper
+ docs → static-validate → submit. Real correctness (pytest, training) is a **cluster** step.

The detailed, battle-tested checklists live **verbatim** in `reference/` (moved here from the
old per-area skills). This file is just the router — open the matching reference file and
follow it.

## The mandatory workflow (CLAUDE.md §"Modification workflow")

1. **Code** the change.
2. **Review** — route by the path you edited to the matching `reference/` checklist:

   | You touched… | Open |
   |---|---|
   | `src/data/**`, `scripts/prepare_data.py` | `reference/review-preprocessing.md` |
   | `src/training/**`, `src/models/**`, `scripts/train_{teacher,student}.py` | `reference/review-training.md` |
   | `slurm/**`, `slurm/README.md`, `docs/SLURM*` | `reference/review-slurm.md` |
   | adding a brand-new architecture | `reference/add-model.md` (then `review-training.md`) |

   The PostToolUse `modification-workflow` hook injects a `[modification-workflow]` reminder
   naming the area right after you edit — treat it as a required step, not a suggestion.

3. **Propagate to Slurm (if any).** If the change alters how a job is invoked, what it
   consumes, or what it produces, update the matching `slurm/*.slurm` **and** its docs
   (`slurm/README.md`, `docs/SLURM.md`) in the *same* task. A code change that silently
   desyncs from its slurm wrapper is a defect.

4. **Verify (static, Mac-only).** Follow `reference/validate-pipeline.md` — Python import
   sanity, Hydra config compose, slurm lint. This is the only verification possible locally;
   state explicitly that pytest / smoke-test is deferred to the cluster rather than claiming
   it passed.

5. **Run.**
   - Cluster job → `reference/submit-slurm.md` (wraps `bash slurm/submit.sh ...`; enforces the
     shared-cluster no-kill / `--gres=mps:l40:N` rules).
   - Quick end-to-end check on synthetic data → `reference/poc-smoke-test.md`.
   - Controlled KD-vs-baseline for one student → `reference/kd-experiment.md`.
   - Full change→commit→submit→proposal cycle → `reference/dev-cycle.md`.

6. **Document.** End state = up-to-date docs, not a TODO to update them later: `CLAUDE.md`
   gotchas, relevant `docs/*.md`, and memory (`MEMORY.md` + the matching file). To write up
   the *results* of the run afterwards, use the **update-report** skill.

## Hard rules (never violate — also hook-enforced)

- GPU slurm jobs MUST request `--gres=mps:l40:N`, **never** `--gres=gpu` (QOS caps
  `gres/gpu=0` → `PD` forever with `QOSMaxGRESPerUser`).
- No `slurm/*.slurm` may kill/preempt/reset another user's job — out of resources = queue and
  wait. No `scancel`/`kill`/`pkill`, `--reset-gpu`, `fuser -k`, `--preempt`, `--nice`.
- Always submit via `bash slurm/submit.sh` (raw `sbatch` drops logs on Slurm 23).
- Never use raw `/datastore/${USER}/...` — default to `/datastore/keg/hungdang` or
  `DATASTORE_USER_DIR`.

See `reference/review-slurm.md` and `docs/GOTCHAS.md` for the full rationale.

## reference/ index

| File | Was skill | Use for |
|---|---|---|
| `reference/review-preprocessing.md` | review-preprocessing | splits / augmentation / sampler / dataset processing contract |
| `reference/review-training.md` | review-training | Trainer/KDTrainer contract, loss, optimizer/scheduler, KD loss |
| `reference/review-slurm.md` | review-slurm | shared-cluster no-kill rule + known cluster failure modes |
| `reference/add-model.md` | add-model | register in `MODEL_REGISTRY` + matching config |
| `reference/validate-pipeline.md` | validate-pipeline | static checks (imports, Hydra compose, slurm lint) |
| `reference/submit-slurm.md` | submit-slurm | submit a job / author a new `*.slurm` script safely |
| `reference/poc-smoke-test.md` | poc-smoke-test | synthetic-data POC end-to-end smoke test |
| `reference/kd-experiment.md` | kd-experiment | controlled KD-vs-baseline for one student |
| `reference/dev-cycle.md` | dev-cycle | end-to-end change→commit→submit→proposal orchestration |
