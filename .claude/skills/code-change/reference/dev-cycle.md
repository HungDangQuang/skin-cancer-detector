---
name: dev-cycle
description: Run the project's end-to-end change→server→thesis cycle as one process. (1) Review the edits against this project's rules, (2) commit + push them to the current feature branch WITHOUT asking approval, (3) emit the run/ launch command and log the job to tasks/daily/<date>.md for result tracking, (4) when results return, report objective metrics compared against SOTA/papers, (5) update docs/DE_CUONG.md (the proposal). Use when the user says "run the full cycle", "do the whole process end to end", "ship this change", or after a code change they want carried through to submission, evaluation, and the proposal. NOT a substitute for the area review skills — it CALLS them.
---

# dev-cycle

The master workflow that takes a change from code → reviewed → pushed → submitted →
evaluated-against-SOTA → written into the proposal. Run the phases in order. Do not
skip a phase; if a phase can't complete (e.g. results aren't back yet), stop cleanly
at that phase and tell the user exactly what you're waiting for.

**Standing authorizations for this workflow (already decided by the user):**
- **Commit + push without asking approval**, to the **current feature branch, no PR**
  (settings.json allows `git add/commit/push`; `push --force` stays denied).
- SOTA comparison uses **`docs/SOTA_BENCHMARKS.md` + WebSearch** to fill gaps.

**Always-on guardrails (never violated, even here):**
- Mac-only: never run training/eval/pip locally — that's the GPU server's job (the
  `local-python-guard` hook blocks it anyway).
- No hallucination: cite file paths / source URLs for every number; say "unknown" or
  "not yet computed" instead of guessing.
- Project-scoped server rules are absolute (no sudo/system-python, deps only in ./.venv-linux).

---

## Phase 1 — Review the change against the rules

1. `git diff --stat` + `git diff` to see exactly what changed.
2. Run the **area review skill(s)** routed by path (same map the PostToolUse hook uses):
   - `src/data/**`, `scripts/prepare_data.py` → `review-preprocessing`
   - `src/training/**`, `src/models/**`, `scripts/train_*.py` → `review-training`
   - `run/**`, `run/README.md` → `review-runner`
3. Run **`validate-pipeline`** (static checks: imports, Hydra compose, runner lint §3a–§3h).
4. Cross-check the principles the user cares about: the CLAUDE.md server rules,
   `docs/GOTCHAS.md`, and the feedback rules (no local python, project-scoped only,
   run-dir isolation, struct mode, augmentation-is-config-driven, …).
5. **Gate:** if anything violates a rule or a review finds a blocker → STOP, fix it,
   re-review. Do **not** proceed to Phase 2 until review + validate-pipeline are clean.
   Report the review outcome plainly (what passed, what was fixed).

## Phase 2 — Commit + push (no approval)

1. If on `main`, create a feature branch first (never commit straight to main).
2. `git add` the relevant files, commit with a clear message + the
   `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.
3. `git push` to `origin/<current-branch>`. No PR (user's choice). Never `--force`.
4. Report the commit hash + branch + that it's pushed.

## Phase 3 — Launch command + job tracking

You cannot run server jobs from the Mac — emit the command and track it.

1. Give the exact `bash run/<script>.sh VAR=value ...` command(s)
   for this change (pick the right script via the `run/README.md` script index). Quote
   `EXTRA="..."` as one arg when passing Hydra overrides.
2. **Log it to the daily ledger** `tasks/daily/<YYYY-MM-DD>.md` (create from
   `tasks/daily/_TEMPLATE.md` if today's file doesn't exist). Add a row under
   "⏳ Pending" with: the command, model/purpose, expected output path
   (e.g. `experiments/runs/.../test_metrics.json`), what result you need, and
   Status = `AWAITING-ID`.
3. **Remind the user to send the job id** after they submit. When they reply with it,
   fill the `Job ID` column and set Status = `RUNNING`. This ledger is the shared memory
   of "what jobs dev-cycle is waiting on" — both the user and you read it to resume.
4. Stop here until results come back. Tell the user you're waiting on job <id> for
   <output>.

## Phase 4 — Objective results vs SOTA

When the user says the job is done / shares results / logs are synced:

1. Read the metrics from disk — **quote `test_metrics.json`, never `val_pauc`**; cite the
   path. For a reportable claim use the **mean ± std from `aggregated.json`**, not one
   fold. (For many runs, fan out the `result-analyst` agent — but only if the user asks
   to use a subagent.)
2. **Headline = AUPRC vs its `prevalence` baseline** (prevalence ~0.4% → AUC-ROC is
   optimistic), plus **pAUC@TPR80** (ISIC 2024 official, range ~0.02–0.20).
3. **Compare against SOTA/papers BEFORE judging** — read `docs/SOTA_BENCHMARKS.md`;
   WebSearch to fill/refresh any missing reference number and record it there with its
   source URL + date. Put our number next to the published one in a table.
4. Give an **objective** verdict: where we beat / match / lag SOTA, and whether the KD
   pipeline is effective — no spin. State limitations (single fold, stale-scale logs,
   missing cross-domain) explicitly. Update the daily ledger row → Status = `DONE` with a
   one-line result summary; move it to "✅ Done".

## Phase 5 — Update the proposal

Once results are validated as OK:

1. Update **`docs/DE_CUONG.md`** (the proposal) — write the new results into the right
   sections (results tables, SOTA comparison, conclusions on KD effectiveness /
   cross-domain / fairness). Keep it factual and cite the run dirs + sources.
2. Keep it report-ready: the user takes `docs/DE_CUONG.md` to assemble the full thesis
   report on Google Drive. Don't leave TODOs in it — fill what the results support, and
   flag what still needs more runs.
3. Summarize what changed in the proposal and what's still pending.

---

## Resuming mid-cycle

If invoked when jobs are already pending, first read `tasks/daily/<date>.md` (and recent
days) for rows in `AWAITING-ID`/`RUNNING` — those are results you're waiting on. Ask the
user for any missing job id, or pick up at Phase 4 if results are now available.
