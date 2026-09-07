---
name: tutor-knowledge
description: >
  Teach, review, or quiz the student on this project's concepts — deep-learning fundamentals,
  the data pipeline, model architectures, Knowledge Distillation, metadata/LUPI, evaluation
  metrics, experiment rigor, infra — grounded in the repo's ACTUAL code and docs. Use when the
  user says "explain concept X", "quiz me", "review Tier N / Day N", "play examiner and grill
  me", "where does the code for X live", or is self-studying with the review checklist / 10-day
  plan. This is the /tutor entry-point; it delegates to the read-only knowledge-tutor agent.
  NOT for judging experiment RESULTS (use eval-results) and NOT for reviewing code you just
  changed (use code-change).
---

# tutor-knowledge

The `/tutor` entry-point for **self-study of this project's knowledge**. It does not teach in
the main thread — it delegates to the dedicated **`knowledge-tutor` agent** (a read-only,
Mac-only Computer-Vision professor that cites `file:line` from the real code).

## How to use it

1. **Spawn the tutor.** Launch the `knowledge-tutor` agent (Agent tool,
   `subagent_type: "knowledge-tutor"`) with the concrete ask — e.g. "explain the KD loss and
   where it lives", "quiz me on Tier 0", "play examiner on the evaluation metrics". Relay the
   agent's answer back to the user.
2. **Continue a session in-context.** If a tutor instance is already running for this study
   session, use `SendMessage` to that instance instead of spawning a fresh (cold) one, so it
   keeps the thread of what's already been taught.

## Study materials it works from

- `docs/review-knowledge-checklist.md` — the concept checklist (Tiers / KN items).
- `docs/review-10-day-plan-vi.md` — the bilingual 10-day self-study plan.
- Progress tracker: memory `project_study_progress.md` (current Tier/Day, which KN done).

## Guardrails

- Read-only & Mac-only — the tutor never trains, evaluates, edits files, or submits cluster
  jobs. It explains and quizzes.
- NOT for judging a checkpoint's quality or an experiment's results → that's **eval-results**.
- NOT for reviewing code you just changed → that's **code-change**.
