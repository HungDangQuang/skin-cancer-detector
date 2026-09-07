---
name: answer-qa
description: Answer a thesis/project question grounded in this repo's actual code and results, then store it as a new `QA/NNN-*.md` file and index it in `QA/README.md`. Use when the user asks a conceptual/methodology/results question about the project AND wants it saved for the thesis — phrasings like "answer and store this", "add this to the QA", "save this Q&A", "record this question for the thesis", or any question asked while the QA workflow is active. NOT for code edits (use the area review skills) and NOT for judging a checkpoint (use analyze-evaluation).
---

# answer-qa

Turns a question about this project into a **cited, thesis-ready answer** and
persists it as one Markdown file under `QA/`, kept in sync with the real state of
the code and runs so it can be lifted straight into the thesis report (Google
Drive).

This skill exists because the user is building a QA knowledge base
(`QA/README.md` defines the convention). Each invocation = one new QA file.

## When to use

- The user asks a methodology / design / results / "why did we do X" question about
  the project **and** wants it recorded (e.g. "answer and store this", "add to QA",
  "save this for the thesis").
- A question comes up mid-conversation that belongs in the thesis writeup.

## When NOT to use

- The user wants a code/config/runner change → use the matching area skill
  (`review-preprocessing` / `review-training` / `review-runner`) and the
  modification workflow in `CLAUDE.md`. (You *may* still record a QA *afterward* if
  asked.)
- The user wants a checkpoint/eval verdict → `analyze-evaluation`.
- The user just wants a throwaway answer with no file saved → answer inline; don't
  invoke this skill.

## Core rule: ground every claim, never invent

This is a thesis artifact. The `feedback_no_hallucination` memory applies in full:

- **Every factual claim cites its source** — a repo file (`src/...:NN`,
  `configs/...`, `CLAUDE.md` section), a run artifact (`test_metrics.json`,
  `aggregated.md`/`aggregated.json`), or a memory file. Use clickable
  `[file](path)` / `file:line` form.
- **Verify before asserting.** If the answer depends on what the code currently
  does, open the file and confirm — do not answer from memory or from a stale QA
  file. If it depends on a result number, read the artifact; if the artifact isn't
  local, say so and tell the user the rsync to fetch it (see `analyze-evaluation`
  §1) rather than guessing a number.
- **Numbers are timestamped and tiered.** A single fold's number is high-variance;
  prefer `aggregated.md` mean ± std and label the tier. Note the date the number
  was read — results change as folds finish.
- If something can't be verified, write "unknown / not yet measured" in the answer
  rather than filling the gap.

## Procedure

### 1. Capture the question
Use the user's question verbatim as the `Question`. If they paraphrased ("save
what we just discussed"), reconstruct the exact question from the conversation and
confirm it reads correctly in the file.

### 2. Research the answer
Gather evidence before writing:
- Identify which area the question touches (data / training / KD / eval / runner /
  experiment design) and open the authoritative files for it. Cross-check against
  `CLAUDE.md` ("Architecture", "Recurring gotchas") and the relevant `docs/*.md`.
- For results questions, read the run artifacts (`experiments/runs/.../test_metrics.json`,
  `aggregated.*`). If not present locally, stop and surface the rsync — don't
  fabricate.
- Reuse a related existing `QA/*.md` if one already covers part of the answer, and
  cross-link it.

### 3. Pick the file name
- Next zero-padded index: scan `QA/` for the highest `NNN-` prefix and add 1.
- Slug: short kebab-case from the question (e.g.
  `002-why-pauc-at-tpr80.md`). Keep it stable and descriptive.

### 4. Write the QA file
Use the template from [QA/README.md](../../../QA/README.md):

```markdown
# QA NNN — <one-line question title>

**Status:** verified YYYY-MM-DD · <area tag>

## Question
<verbatim question>

## Answer
<thesis-ready prose, every claim cited>

## Evidence
- <file:line / artifact> — <what it supports>

## For the thesis
<1–2 sentences phrased for the report — optional but encouraged>
```

Rules for the body:
- `Status` date = today (`currentDate` in context). Area tag is one of
  `data` / `training` / `kd` / `evaluation` / `runner` / `experiment-design` /
  `results`.
- The `Answer` is self-contained prose a reader can drop into the thesis. Lead with
  the direct answer (yes/no/the number), then the reasoning.
- The `Evidence` block is mandatory — at least one citation. Mark any live number
  with the date read and "re-confirm against `aggregated.md` before citing final".
- Phrase `For the thesis` in report register (third person, no "we just
  discussed").

### 5. Update the index
Add a bullet to the `## Index` section of [QA/README.md](../../../QA/README.md):
`- [NNN — <question title>](NNN-slug.md)`. Keep entries in index order.

### 6. Report back
Tell the user: the file created (clickable path), the one-line verdict from the
answer, and any caveat — especially if a cited number was unverifiable locally
(name the rsync) or is single-fold (recommend aggregating). Offer to draft the next
QA if the conversation suggests follow-ups.

## Keeping QA current

A QA file is a snapshot. If later work changes the underlying code or results,
**update the matching QA file in the same task** (re-verify its citations, bump the
`Status` date) — same discipline as the `CLAUDE.md` modification workflow. If a QA's
premise becomes false (e.g. a bug it cites gets fixed), correct the answer rather
than leaving a stale claim in a thesis source.

## Caveats

- This skill writes documentation only — it never edits `src/`, `configs/`, or
  `run/`. No `validate-pipeline` run is needed, but the *citations* inside the QA
  must reflect the code as it actually is at write time.
- Don't duplicate an existing QA — if the question overlaps one already in `QA/`,
  extend or cross-link that file instead of adding a near-duplicate.
- If the honest answer is "not yet known / not yet measured," record that as the
  answer. An accurate "unknown" is more useful to the thesis than a confident guess.
