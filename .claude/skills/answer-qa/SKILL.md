---
name: answer-qa
description: Answer a thesis/project question grounded in this repo's actual code and results, then store it as a new `QA/NNN-*.md` file and index it in `QA/README.md`. Use when the user asks a conceptual/methodology/results question about the project AND wants it saved for the thesis — phrasings like "answer and store this", "add this to the QA", "save this Q&A", "record this question for the thesis", or any question asked while the QA workflow is active. Every answer goes through ONE mandatory cross-check pass — two `review-verifier` sub-agents in parallel (facts/fabrication, and completeness + transparency) — BEFORE the file is written into `QA/`. NOT for code edits (use the area review skills) and NOT for judging a checkpoint (use analyze-evaluation).
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
- **"Is the model good enough / đạt chưa / usable on a phone" is an acceptance question.**
  Answer it only through `.claude/skills/eval-results/reference/acceptance-gates.md` (per-domain,
  CI lower bound, signed-off thresholds, verdict labels in its §3). "KD beat the baseline" or
  "phone = server" never answers it, and while the thresholds are `ĐỀ XUẤT` the answer must say
  `CHƯA CÓ TIÊU CHÍ CHỐT`, not "đạt".

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

### 4. Draft the QA file — into the scratchpad, NOT into `QA/`
Write the draft to `<scratchpad>/qa_draft_NNN-slug.md` first. **Nothing lands in `QA/`
until the cross-check gate in step 5 has run** — a QA file is a thesis source, and an
unverified claim stored there outlives the session that wrote it.

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

### 5. Cross-check gate (mandatory) — one pass, two sub-agents, kind B

Spawn **two** [`review-verifier`](../../agents/review-verifier.md) instances **in parallel, in
one message**, pointed at the scratchpad draft. Use the **kind-B** prompt template in
[review-thesis/reference/cross-check.md](../review-thesis/reference/cross-check.md) step B and
fill its fields *for a QA draft* — three of them do not map one-to-one:

| Field of the kind-B template | For an `answer-qa` draft |
|---|---|
| `Yêu cầu gốc của user` | the QA **question, verbatim** — that is what "complete" is measured against |
| `File đã tạo/sửa` | `chưa có — bản nháp ở <scratchpad>/qa_draft_NNN-slug.md, chưa ghi vào QA/` |
| the read-only-git line | not applicable — nothing has been written yet, and `git status` would only show unrelated work already in the tree. Replace it with `Đối chiếu trùng lặp với QA/ hiện có: <liệt kê file>` |

| Instance | What it checks in the QA draft |
|---|---|
| `REMIT=FACTS` | every citation opens **and** actually supports the claim pinned on it; every number matches the artifact quoted (`test_metrics.json` / `aggregated.json` — never val); every *negative* claim ("the project does not do X") is re-grepped; a number that exists only on the GPU server is `KHÔNG VERIFY ĐƯỢC`, never filled in |
| `REMIT=PATCH` | the answer answers **the question that was asked**, not a nearby one; the `QA/README.md` template holds (`Status` + area tag + `Evidence` ≥ 1 citation; `For the thesis` is optional); live numbers carry the date they were read; no **duplication** of an existing `QA/NNN`; and the draft says plainly what it could not verify instead of going quiet — transparency (item 5 of that remit) applies to kind B too |

Reconcile as in `cross-check.md` step C: a proven `BỊA`/`SAI` is fixed **before** the file is
written; a `KHÔNG VERIFY ĐƯỢC` must stay visible in the QA itself — in `Evidence`, or as
"unknown / not yet measured" per the Core rule above — rather than being dropped; if the
verifier is wrong, push back **with `file:line`** and tell the user there was a disagreement.
**Exactly one pass**: whatever you fix after the gate has been checked by no agent, and step 7
must say so.

### 6. Write the file + update the index
Only a draft that has been through the gate — and corrected per the gate — is written to
`QA/NNN-slug.md`. Then add a bullet to the `## Index` section of
[QA/README.md](../../../QA/README.md):
`- [NNN — <question title>](NNN-slug.md)`. Keep entries in index order.

### 7. Report back
Tell the user: the file created (clickable path), the one-line verdict from the
answer, and any caveat — especially if a cited number was unverifiable locally
(name the rsync) or is single-fold (recommend aggregating). Offer to draft the next
QA if the conversation suggests follow-ups.

Include a `### Kiểm chéo` block: how many items were checked out of how many, the two
verdicts, what the verifiers caught, what you fixed afterwards, and **which lines were
fixed after the gate and therefore checked by no agent**. Mandatory even when both
verifiers return `ĐẠT`.

## Keeping QA current

A QA file is a snapshot. If later work changes the underlying code or results,
**update the matching QA file in the same task** (re-verify its citations, bump the
`Status` date) — same discipline as the `CLAUDE.md` modification workflow. If a QA's
premise becomes false (e.g. a bug it cites gets fixed), correct the answer rather
than leaving a stale claim in a thesis source. **An updated QA goes through the same gate**
(step 5) on the revised body — same reason: it is still a thesis source.

## Caveats

- This skill writes documentation only — it never edits `src/`, `configs/`, or
  `run/`. No `validate-pipeline` run is needed — but the **cross-check gate (step 5) is
  not optional**, and the *citations* inside the QA must reflect the code as it actually
  is at write time.
- Don't duplicate an existing QA — if the question overlaps one already in `QA/`,
  extend or cross-link that file instead of adding a near-duplicate.
- If the honest answer is "not yet known / not yet measured," record that as the
  answer. An accurate "unknown" is more useful to the thesis than a confident guess.
