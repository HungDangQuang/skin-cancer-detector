---
name: update-report
description: >
  Write or refresh the project's Markdown deliverables once results exist — the report files
  under reports/ (incl. reports/BAO_CAO_TONG_HOP.md), the proposal (report_phase_1/DE_CUONG.md and
  its short form docs/DE_CUONG.md), narrative summaries of aggregated fold results, and the
  status tracker docs/PROGRESS.md. Use when the user says "update the report", "write up these
  results", "viết báo cáo kết quả arm X", "refresh the ablation report", "update the proposal /
  đề cương", "log this job / cập nhật tiến độ", or "turn aggregated.json into a report". It
  documents; it does not judge (use eval-results for the verdict), change code (use
  code-change), or edit the thesis LUAN_VAN.md (use review-thesis). Answering + storing a thesis
  Q&A is a separate skill (answer-qa).
---

# update-report

The entry-point for keeping the project's **Markdown deliverables** current after a run
finishes. This is the "Document" step of the modification workflow, made callable on its own.

## What this skill maintains

| Target | When to touch |
|---|---|
| `reports/<date>_<topic>.md` (new) | a result/analysis with no existing home — the usual case; one report per arm/question, dated |
| an existing `reports/*.md` | new results for an experiment already tracked there — update the number tables + conclusion, and say in the file what changed and when |
| `reports/BAO_CAO_TONG_HOP.md` | the single consolidated report — only when a headline finding changes |
| `report_phase_1/DE_CUONG.md` (full proposal) · `docs/DE_CUONG.md` (short form) | a headline result the proposal states has changed — check **both** for the same number and keep them consistent |
| `docs/PROGRESS.md` | **the only status tracker**: a job was launched / finished / a task changed state. Follow its own header ("Cách cập nhật"): edit the row's status + date, move finished rows to §7. Never open a second tracker |
| `CLAUDE.md` gotchas / `docs/*.md` / memory (`MEMORY.md` + file) | anything non-obvious the run revealed |

Out of scope: `thesis/LUAN_VAN.md` (the author reviews thesis edits through **review-thesis**, report
first, edit only on approval) and `QA/` (**answer-qa**).

## Procedure

1. **Get the verdict first if there isn't one.** This skill writes up a verdict you already have;
   if the user hasn't got one, run **eval-results** (and, for "đạt yêu cầu", its
   `reference/acceptance-gates.md`) before writing.
2. **Read the numbers from the artifacts** — `aggregated.json/md`, `fold_*/test_metrics.json`,
   `reports/external_newsplit_<arm>/<ds>/<variant>/` (v2 arms; plain `reports/external/` is the v1 matrix),
   `reports/{bootstrap_ci,ci}_*.md` (check which tree each CI file was computed on — run names repeat across trees). Note the path
   of every number as you go; you will cite it. If an artifact is only on the server, say so and
   give `bash run/pull_results.sh` — never fill the gap.
3. **Find the house format — and check the result isn't already written up.** Open the closest sibling
   `reports/*.md` (same arm family or same kind of question) and reuse its heading layout, table columns and
   tone. If an existing report already contains this comparison, cite it and add only what is new (a dated
   section there, or a short new report that links it) instead of duplicating its numbers.
   CI files name runs by alias (`x_kd`, `x_baseline__ddi`) — map them to run-dirs with the provenance rule in
   `eval-results/reference/analyze-evaluation.md`, and say how you mapped them.
4. **Draft into the session scratchpad**, not into `reports/` — a report with numbers is a claim
   the author will build on.
5. **Cross-check gate (mandatory, one pass).** Per `CLAUDE.md` → "Cross-check gate": spawn two
   `review-verifier` instances in parallel in one message — `REMIT=FACTS` and `REMIT=PATCH`, **kind B**
   — using the template in `.claude/skills/review-thesis/reference/cross-check.md` (its `report-template.md`
   and `thesis/REVIEW_LOG.md` parts apply to thesis reviews only). Fix proven
   `BỊA`/`SAI` before writing; keep `KHÔNG VERIFY ĐƯỢC` visible in the report.
6. **Write the file(s)**, then update `docs/PROGRESS.md` if a task changed state.
7. **Report back** with the file paths, the one-line finding, a `### Kiểm chéo` block (items
   checked, both verdicts, what was fixed, which lines were changed *after* the gate and so were
   checked by no agent).

### Logging a job that was just launched (no results yet)

This is a tracker update, not a report: add a row to `docs/PROGRESS.md` §1 (code **A**, 🏃, date) — and keep the
rest of the tracker consistent with it (the §0 summary line, the "Cập nhật lần cuối" stamp, and any line that
says no job is running — the header only says "edit the status, add the date", but a new running job makes those
lines false) — with the
command, host + tmux session, expected run-dir and log file, and what result it is waiting for. Before
writing the row, check and note in it: (a) the expected run-dir does not already exist in that tree (a
re-launch with the same `run_suffix` overwrites finished folds — relaunch only missing folds with `FOLDS=`);
(b) the matching control (baseline / teacher of the same tree) exists or is also queued; (c) whether the run
is inside a pre-registration (`docs/PREREG_*.md`) — if not, any selection from it is post-hoc; (d) that the
trainer will score the **test** set at the end of every fold, so opening those files later is a test-set
opening if a pre-registration logs them. Facts that only the server can confirm (is the job alive, start
time, `TMPDIR`) are marked unverified, never filled in. The row is a docs edit with claims (paths, run-dir
state, pre-registration scope), so it goes through the cross-check gate like any other edit here (`CLAUDE.md`
only exempts purely operational answers).

## Rules

- **Numbers come from the artifacts, never from memory.** Quote the **aggregated mean ± std**
  over folds, and lead with **AUPRC** (in-domain prevalence ~0.39%; HAM10000 / Fitzpatrick17k have
  their own, much higher prevalence — state it next to the AUPRC and never compare AUPRC across
  datasets); pAUC@TPR≥80 for ISIC-benchmark comparison. A KD/arm difference is quoted as its **paired CI**
  ("ΔAUPRC +0.030 [+0.011, +0.048]"), never as a win count.
- **State the split for every in-domain number** — splits v1 (`experiments/runs/`, leaked
  patients, inflated) or v2 (`experiments/runs_newsplit_*`). Never put v1 and v2 numbers in one
  comparison.
- **Never write "đạt yêu cầu / đủ tốt / sẵn sàng triển khai" on your own.** Such a sentence may
  only copy a verdict produced through `.claude/skills/eval-results/reference/acceptance-gates.md`,
  together with its `### Cổng chấp nhận` block. A comparison result ("KD tốt hơn baseline có ý
  nghĩa") must be written as a comparison, not upgraded to "model tốt".
- **Label post-hoc decisions as post-hoc** — a threshold, test subset or selection rule chosen
  after seeing the numbers it judges (see acceptance-gates §1 and its history file).
- **Don't overwrite a report whose framing contradicts the new data** without flagging it —
  surface the discrepancy instead of silently editing. `reports/<date>_*.md` are snapshots of
  that date: add a dated note rather than rewriting history.
- Keep edits scoped to `.md`; code/config changes go through **code-change**.

## Google Drive — deferred

Pushing reports to Google Drive is **out of scope for now** (author's decision, re-confirmed
05/10/2026): there is no agreed target Drive folder. Until a folder is agreed, this skill only
maintains repo-local `.md`.
