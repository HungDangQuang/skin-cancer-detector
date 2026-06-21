# QA 001 — Do I need to train more than one teacher?

**Status:** verified 2026-06-09 · experiment-design

## Question
There is only one teacher model (EfficientNet-B4). Do I need to train more
teacher models to choose which is the best pipeline?

## Answer
No. A single strong teacher is the correct design for this study, and adding more
teachers would change the research question rather than strengthen it.

This project is a **knowledge-distillation effectiveness study**, not a
teacher-selection study. The controlled comparison is, for each student,
**KD vs. no-KD** under identical hyperparameters, data splits, and seed — the
delta is then attributed to distillation via `compute_kd_delta()`. The teacher is
the *fixed knowledge source*, deliberately held constant so that the measured
effect is caused by KD and not by which teacher was picked. The full run matrix
is `3 students × 2 KD conditions × 5 folds = 30 runs`; the teacher is upstream of
all of them equally and is not a variable being optimized.

The "best pipeline" you are actually choosing between is the **student deployment
model** — EfficientNet-B0 vs MobileNetV3-Large vs MobileViT-S, each under KD vs
baseline. That ranking is produced from the students' held-out
`test_metrics.json` aggregated across folds; the teacher does not enter it.

**When multiple teachers *would* be justified** — only if the thesis adds a
different claim, e.g. "KD benefit scales with teacher capacity" (B0/B4/B7 as
teachers) or "teacher architecture family matters" (CNN vs ViT teacher). Those
are separate ablation contributions, not requirements for a binary skin-cancer KD
thesis.

**What to do instead** — justify the single-teacher choice by confirming the
teacher is a *good* teacher (a weak teacher caps every student), then spend the
remaining compute on the parts still open: the FP32 mobile benchmark, HAM10000
cross-domain evaluation, and Fitzpatrick17k fairness evaluation.

## Evidence
- `CLAUDE.md` → "Two-stage training pipeline" — Stage 1 is a single EfficientNet-B4
  teacher; Stage 2 distils into 3 students with a frozen teacher.
- `CLAUDE.md` → "Experiment design" — each student trained twice (KD / no-KD) with
  identical settings; `compute_kd_delta()` measures the effect; 30 total runs.
- Teacher quality is read from its held-out `test_metrics.json`
  (`pauc_at_tpr80` / sensitivity / `auc_roc`), the unbiased generalization number
  written at end of training (`CLAUDE.md` → "Run-dir convention").
- Live run status (read 2026-06-09): best arm = KD MobileNetV3-Large,
  sensitivity 0.955 / AUC 0.987, students already exceed the teacher — evidence
  that one teacher was sufficient. *Re-confirm against `aggregated.md` before
  citing a final number.*

## For the thesis
A single high-capacity teacher (EfficientNet-B4) is used by design: holding the
teacher constant isolates the effect of knowledge distillation in the KD-vs-baseline
comparison across the three student architectures. Teacher-capacity and
teacher-family variation are out of scope for this work.
