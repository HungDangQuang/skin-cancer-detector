---
name: eval-results
description: >
  Read the artifacts a run produced, judge them, and conclude whether the solution is
  effective — and, ONLY via reference/acceptance-gates.md, whether the model meets the
  deployment requirement ("đạt yêu cầu chưa / đủ tốt chưa / dùng được trên điện thoại chưa"). Use when the user asks "is this checkpoint good", "did KD help", "compare the
  students / teacher vs student", "rank my runs", "is this training run any good / how do I
  improve it", "why did it fail / NaN / not learn", or shares a reports/results/*.json, a
  training log, or an experiments/runs/ dir. It routes to the right detailed rubric in
  reference/ based on WHICH artifact you have. NOT for making a code change (use code-change)
  and NOT for writing the result up into a report (use update-report).
---

# eval-results

The single entry-point for the **"is this good / did it work?"** question. Pick the rubric by
**what artifact you have** — the detailed, project-specific criteria live **verbatim** in
`reference/` (moved here from the old eval skills). Open the matching file and follow it.

## ⛔ Before writing "đạt / good enough / usable / ready to ship" — open `reference/acceptance-gates.md`

Three different questions, three different kinds of evidence — never answer one with the other's:

| Question | Evidence | Allowed verdict words |
|---|---|---|
| (1) Did training run healthily? | log, val metrics, val − test gap | "healthy / has problems" (assess-training, diagnose-training) |
| (2) Is A better than B? (KD vs baseline, arm vs control, student vs teacher) | **paired bootstrap CI** (`run/bootstrap_ci.sh PAIR=…`) | "significantly better / indistinguishable / significantly worse" |
| (3) **Does the model MEET THE REQUIREMENT** (good enough on a phone)? | **every gate in `reference/acceptance-gates.md`**, on the model that will ship | only the labels in that file's §3 |

- A "better than baseline" result is **never** evidence for (3).
- While the gate thresholds are still `ĐỀ XUẤT` (not signed off by the author), the overall verdict
  for (3) **must** be `CHƯA CÓ TIÊU CHÍ CHỐT` — report each gate against the proposed threshold, but
  do not write "đạt yêu cầu".
- The Good/Moderate/Poor tables in `analyze-evaluation.md` / `assess-training.md` are **health
  heuristics for question (1)/(2)**, not acceptance criteria. Never promote a model to "ready" from them.
- Any report that gives a verdict on (3) must contain the `### Cổng chấp nhận` block (gates file §5).

## Route by artifact

| You have… | Question | Open |
|---|---|---|
| any question of the form "is it good enough / đạt chưa / can it ship / dùng được trên mobile chưa" | acceptance verdict | **`reference/acceptance-gates.md`** (then the rubric below for the numbers) |
| one/few `reports/results/*.json` (eval JSON) | "is this checkpoint good?", one KD-vs-baseline, cross-student compare | `reference/analyze-evaluation.md` |
| **all** of `experiments/runs/` | "did KD help across the board?", rank every teacher-student pair | `reference/compare-kd.md` |
| a **successful** training log | score the run (good/moderate/poor) + how to improve the next one | `reference/assess-training.md` |
| a **failed / misbehaving** run (crash, NaN, never learned) | triage the failure + recommend a fix | `reference/diagnose-training.md` |

## Grounding rules (this project)

- **Quote `test_metrics.json`, not val metrics**, for any verdict — val is biased by
  early-stopping. Cite the **aggregated mean ± std** (`aggregated.json/md`) over folds, not a
  single fold.
- Headline metric at the measured **~0.39% prevalence** is **AUPRC** (clinical); **pAUC@TPR≥80**
  is the ISIC-benchmark comparison metric; AUC-ROC is optimistic — don't lead with it.
- A large **val − test** gap (esp. AUPRC/pAUC) is the overfitting signal.
- Never invent numbers — read them from the JSON and cite `file:line`; say "missing" if an
  artifact isn't there rather than guessing.
- **Split per acquisition domain.** The in-domain test mixes ISIC + PAD; a "only guess the source"
  model already scores AUC 0.872 on the v1 test (~0.85 on v2, hand-computed, no artifact). Quote per-`source` numbers (`bootstrap_ci.sh SUBGROUP=source`),
  and lead the mobile story with the **PAD (phone-photo)** subset.
- **Splits v1 vs v2.** `experiments/runs/` (the 140-fold matrix) used splits **v1 that leaked
  patients** — its in-domain numbers are inflated and may not back an acceptance verdict.
  `experiments/runs_newsplit_*` use the patient-grouped v2. Never mix v1 and v2 in one comparison.
- **One fold is not an arm.** A single (or retrained, e.g. `__mobile`) checkpoint is at most
  `CHƯA CHỨNG MINH`; claims about an arm need the 5-fold CI.
- **Win counts are not evidence** ("KD won 12/12"); quote the paired CI of the delta.

## reference/ index

| File | Was skill | Use for |
|---|---|---|
| `reference/acceptance-gates.md` | — (new 2026-10-01) | **the only place that defines "meets the requirement"**: gates A/B/C, CI-based labelling rule (covers every case), verdict vocabulary, forbidden inferences |
| `reference/analyze-evaluation.md` | analyze-evaluation | verdict on one/few eval JSONs (single or comparison mode) |
| `reference/compare-kd.md` | compare-kd | whole-matrix KD-vs-baseline via `scripts/compare_kd_results.py` |
| `reference/assess-training.md` | assess-training | score a finished, successful training log |
| `reference/diagnose-training.md` | diagnose-training | triage a crashed / NaN / non-learning run |

For a single finished run you can also spawn the **result-analyst** agent (parallel triage of
many runs); this skill is the interactive, single-thread path.
