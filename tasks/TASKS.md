# Project Task Log

Master checklist for the KD skin-cancer-detection thesis. Last updated: **2026-06-09**.

Legend: `[x]` done · `[~]` in progress / partially done · `[ ]` not started · `[!]` blocked

---

## ✅ Completed

### Data & pipeline
- [x] Environment setup on UIT cluster (venv, sync, verify) — Steps 0–4
- [x] Preprocessing pipeline (offline resize + quality filter, StratifiedGroupKFold, online Albumentations aug)
- [x] **Split-leak fix** (2026-06-06) — independent patient-disjoint held-out test split carved before CV
- [x] **Add PAD-UFES-20** dataset (2026-06-07) — staged + concatenated, lifts val-fold prevalence to 0.39%
- [x] PAD-UFES-20 `img_id` extension bug fixed (2026-06-07)

### Training
- [x] **Teacher EfficientNet-B4** re-trained on fixed splits (job 28250) — pAUC 0.1785, AUC 0.9777, sens 0.9087
- [x] **KD students** ×3 (jobs 28273/28276/28279) — efficientnet_b0, mobilenetv3_large, mobilevit_s
- [x] **Baseline students** ×3 (jobs 28281/28282/28283) — no-KD arm
- [x] Full 30-run matrix complete (3 arch × 2 conditions × 5 folds)

### Analysis (this session)
- [x] Extracted + aggregated all 30 student folds (5-fold mean±std)
- [x] KD-vs-baseline deltas + significance — robust for MobileNetV3, marginal B0, noise MobileViT
- [x] Identified best model: **KD MobileNetV3-Large** (sens 0.9552, AUC 0.9873)
- [x] Found students out-generalize teacher (not a KD artifact)
- [x] Consolidated analysis → `reports/2026-06-09_student_arm_analysis.md`

### Decisions / housekeeping
- [x] **Quantization de-scoped** (2026-06-08) — backbones run on mobile as-is; INT8/TFLite optional
- [x] Updated memory (`project_run_status.md`, `MEMORY.md`) to current state

---

## 🔜 To do now (storage-safe — NOT blocked)

### Mechanical / verification
- [ ] **Aggregate students** — `22_aggregate_folds.slurm RUN_DIR=...` for each kd_*/baseline_* dir
- [ ] **Re-pull canonical JSONs** — rsync `experiments/runs/*/fold_*/test_metrics.json` + `aggregated.{json,md}` to replace log-extracted numbers in the report
- [ ] **Re-aggregate teacher** — its on-disk `aggregated.json` is stale (job 28179); regenerate from fresh per-fold JSONs

### Pillar 4 — Mobile deployability
- [x] New `scripts/benchmark_mobile.py` — params + FP32 size + single-core CPU latency (median/p90); reviewed (review-training) + static-validated; cluster run pending
- [x] New `slurm/21_benchmark_mobile.slurm` (CPU-only job, no GPU) — reviewed (review-slurm) + docs propagated (slurm/README.md §5, docs/SLURM.md §4 + resource tables)
- [ ] Run benchmark across all 4 checkpoints (teacher + 3 KD students) — one fold each, weight-independent
- [ ] Pull `reports/mobile_benchmark/*.json` + add results table to `docs/`
- [ ] (Optional) INT8 quantization as a strengthening paragraph — not required

### Evaluation rigor (enabled by one patch)
- [ ] **Patch `src/evaluation/evaluator.py`** to save sibling `.npz` (`y_true`, `y_prob`)
- [ ] New `scripts/analyze_predictions.py` computing from the `.npz`:
  - [ ] **AUPRC / PR curve** (honest metric at 0.39% prevalence)
  - [ ] **Calibration** (ECE, Brier, reliability diagram)
  - [ ] Bootstrap confidence intervals on pAUC / AUC / sensitivity
  - [ ] Operating-point table (sens @ fixed 90% / 95% specificity)
- [ ] **Explainability** — Grad-CAM on test images (verify model attends to lesion, not rulers/ink/hair)

---

## ⛔ Blocked — server storage full (defer until disk frees)

### Pillar 5 — Cross-domain generalization
- [!] Stage HAM10000 on cluster
- [!] `process_ham10000()` in `src/data/` (needs benign/malignant label-mapping decision)
- [!] External-eval script + `slurm/23_evaluate_external.slurm`
- [!] Run + report cross-domain metrics

### Pillar 6 — Fairness across skin tones
- [!] Stage Fitzpatrick17k on cluster
- [!] `process_fitzpatrick17k()` + per-Fitzpatrick-group labels
- [!] Stratified eval (sens/pAUC per skin-tone group + max-min gap) + `slurm/24_evaluate_fairness.slurm`
- [!] Run + report fairness metrics

### Unblocker (optional, to free storage)
- [ ] Storage-cleanup audit — identify safe-to-delete cluster artifacts (e.g. OBSOLETE teacher job 28060 leaked-split run, superseded dirs)

---

## 📝 Decisions still needed (before pillars 5 & 6)
- [ ] HAM10000 malignant mapping — include `akiec` (actinic keratosis / in-situ SCC) as malignant? (standard: malignant = {mel, bcc, akiec})
- [ ] Fitzpatrick17k label source — `three_partition_label` vs `nine_partition_label`; confirm I–II / III–IV / V–VI grouping

---

## 📌 Open housekeeping
- [ ] Commit uncommitted tooling/docs (CLAUDE.md workflow section, review skills, PostToolUse hook, this report) as one "tooling/docs" commit
