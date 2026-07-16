# QA — Thesis Q&A Knowledge Base

One **question + answer per file**, kept in sync with the actual state of this
project so the content can be lifted directly into the thesis report (Google
Drive).

## Conventions

- **One QA per file.** Filename: `NNN-short-kebab-slug.md` (zero-padded index for
  ordering), e.g. `001-do-i-need-multiple-teachers.md`.
- Each file uses the template below: a `Question` and an `Answer`, plus a short
  `Evidence` block citing the code / config / run artifact the answer rests on,
  and a `Status` line with the date it was last verified.
- **Cite, don't assert.** Every factual claim should point at a file
  (`src/...`, `configs/...`), a run artifact (`test_metrics.json`,
  `aggregated.md`), or `CLAUDE.md`. If a number comes from a live run, say which
  run and when it was read — numbers change as folds finish.
- When the underlying code or results change, **update the matching QA file** in
  the same task (same discipline as the modification workflow in `CLAUDE.md`).

## Template

```markdown
# QA NNN — <one-line question title>

**Status:** verified YYYY-MM-DD · <area tag>

## Question
<the question, as asked>

## Answer
<the answer, thesis-ready prose>

## Evidence
- <file:line or artifact> — <what it supports>

## For the thesis
<1–2 sentences phrased for the report, optional>
```

## Index

- [001 — Do I need to train more than one teacher?](001-do-i-need-multiple-teachers.md)
- [002 — Does the project have a training strategy for class imbalance?](002-class-imbalance-strategy.md)
- [003 — Why do the chosen datasets work for edge deployment (ISIC 2024 ≠ phone photos)?](003-datasets-edge-deployment-domain-fit.md)
- [004 — Knowledge Distillation vs Transfer Learning: phương pháp nào tốt hơn?](004-knowledge-distillation-vs-transfer-learning.md)
- [005 — Các student SOTA được chọn dựa theo tiêu chí nào?](005-sota-student-selection-criteria.md)
- [006 — Các metric đánh giá có được bài báo chính thống nào sử dụng không?](006-evaluation-metrics-published-references.md)
