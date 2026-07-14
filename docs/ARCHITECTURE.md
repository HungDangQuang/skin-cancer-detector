# ARCHITECTURE — Bản đồ kiến trúc & pipeline dự án

> **Mục đích:** file "nạp nhanh" cho một chat session mới. Đọc file này là nắm được toàn bộ kiến trúc code + luồng pipeline mà không phải đọc rải rác nhiều nơi.
> **Nguồn chân lý chi tiết:** [CLAUDE.md](../CLAUDE.md) (§Architecture) + `docs/*.md`. File này là **bản đồ**, không thay thế các doc chuyên sâu.
> **Cập nhật lần cuối:** 2026-07-13.

---

## 0. Một câu tóm tắt

Phân loại nhị phân ung thư da (benign=0, malignant=1) trên ISIC 2024, dùng **Knowledge Distillation**: 1 teacher dung lượng lớn dạy ≥1 student nhẹ (mobile). Mọi model xuất **1 raw logit**; `sigmoid()` áp lúc inference. Metric có **hai vai trò (không mâu thuẫn)**: **pAUC@TPR≥80%** (ISIC 2024) = metric *đối chiếu benchmark/leaderboard*; **AUPRC** = *headline lâm sàng* ở prevalence **đo được ~0,39%** (ISIC 2024 + PAD-UFES-20, tập test độc lập — job 28250) — không dùng AUC-ROC (bị thổi phồng ở imbalance cực đoan).

---

## 1. Pipeline 2 giai đoạn (bức tranh lớn)

```
data/raw/ (ISIC2024 + PAD-UFES-20)
      │  scripts/prepare_data.py  (resize + quality filter + StratifiedGroupKFold theo patient_id)
      ▼
splits_dir/  test_split.csv (độc lập, patient-disjoint)  +  fold_{0..4}/{train,val}_split.csv
      │
      ├─ GIAI ĐOẠN 1 — TEACHER (standalone)
      │     scripts/train_teacher.py  → Trainer + BinaryFocalLoss
      │     teacher ∈ {efficientnetv2_m | convnextv2_base | maxvit_base}
      │     → experiments/runs/teacher/<name>/fold_N/checkpoints/best_model.pth
      │
      └─ GIAI ĐOẠN 2 — STUDENT (KD, teacher bị FREEZE)
            scripts/train_student.py  → KDTrainer + BinaryDistillationLoss
            student ∈ {mobilenetv4_conv_medium | fastvit_sa12 | efficientformerv2_s2}
            → experiments/runs/kd_<teacher>_to_<student>/fold_N/...
      ▼
Đánh giá tự động cuối train → test_metrics.json (+ val_metrics.json, predictions.csv)
      ▼
scripts/aggregate_folds.py → aggregated.{json,md}  (mean ± std trên 5 fold — số để trích dẫn)
      ▼
Benchmark hiệu năng (scripts/benchmark*.py) + export (ExecuTorch .pte) + cross-domain/fairness
```

**Công thức KD** (`src/training/distillation.py`, T=4.0, alpha=0.3):
```
L_total = 0.3 · L_focal(student, y_true) + 0.7 · T² · L_BCE(σ(s/T), σ(t/T))
```

**Thiết kế thực nghiệm:** mỗi student train 2 lần (có KD / không KD) cùng seed+split+hparam → `compute_kd_delta()`. 5-fold CV. Con số **"30 run" = 3 *student* × 2 điều kiện × 5 fold, ứng với MỘT teacher cố định** ("3 arch" ở đây là 3 *student*, KHÔNG phải teacher). Registry khai báo **3 SOTA teacher** và hiện đang train cả 3 → tổng số run thực tế lớn hơn 30. Báo cáo phải nêu rõ phạm vi teacher đang dùng (1 teacher chính + 2 teacher ablation-1-fold, hay cả 3 đầy đủ) thay vì trích mặc định "30".

---

## 2. Bản đồ thư mục `src/`

| Package | File chính | Vai trò |
|---|---|---|
| `src/data/` | `preprocessing.py` | `process_isic2024` / `process_pad_ufes_20`, `generate_group_kfold_splits` (nhớ `label_col="label"`, `patient_id` namespaced `pad_{id}`) |
| | `dataset.py` | `SkinLesionDataset` (đọc cột `image_path`, `label`) |
| | `datamodule.py` | `SkinLesionDataModule` — build DataLoader; `set_epoch()` reshuffle sampler |
| | `sampler.py` | `DynamicUndersampledSampler` — giữ tỉ lệ ~1:5 malignant:benign, reshuffle mỗi epoch |
| | `transforms.py` | `build_transforms` — Albumentations **từ config** `augmentation/{light,heavy}.yaml`; MixUp/CutMix/CutOut bị cấm (`_FORBIDDEN_OPS`) |
| `src/models/` | `registry.py` | `MODEL_REGISTRY` (string→class) + `build_model` / `build_model_from_name` |
| | `base_model.py` | `BaseModel` (ABC): `forward(x)->Tensor(B,)`, `freeze_backbone()`, `unfreeze()` |
| | `heads.py` | `build_head()` = `Dropout→Linear(in,1)`; dùng `infer_backbone_out_dim()`, **không** dùng `num_features` |
| | `efficientnet.py` / `mobilenet.py` / `mobilevit.py` | wrapper họ baseline |
| | `timm_backbone.py` | `TimmBackboneModel` — wrapper generic cho toàn bộ SOTA set (cần `timm>=1.0`) |
| `src/training/` | `trainer.py` | `Trainer` (teacher/baseline) |
| | `kd_trainer.py` | `KDTrainer` (student, teacher frozen) |
| | `losses.py` | `BinaryFocalLoss` (gamma=2.0, alpha=0.25) |
| | `distillation.py` | `BinaryDistillationLoss` (T=4.0, alpha=0.3) |
| | `callbacks.py` / `optimizers.py` / `schedulers.py` | early stopping/checkpoint, optimizer, LR schedule |
| `src/evaluation/` | `metrics.py` | `compute_metrics()` → `pauc_at_tpr80`, `auc_roc`, `auprc`(+`prevalence`), sensitivity/specificity, `sens_at_{90,95}spec`, TP/FP/TN/FN |
| | `evaluator.py` | `Evaluator.evaluate()`, `save_predictions()` (ghi `predictions.csv`) |
| | `confusion_matrix.py` / `grad_cam.py` | trực quan hoá |
| `src/inference/` | `predictor.py` / `ensemble.py` | inference đơn / ensemble |
| `src/utils/` | `config.py` | `load_config()` — **compose Hydra `defaults:`** (script standalone cần cái này) |
| | `checkpoint.py` / `seed.py` / `logger.py` / `visualization.py` | tiện ích |

---

## 3. Model registry (arch nào ↔ class nào)

`src/models/registry.py`:

| Vai trò | Tên (key) | Class wrapper |
|---|---|---|
| Teacher | `efficientnetv2_m` (EfficientNetV2-M) | `TimmBackboneModel` |
| | `convnextv2_base` (ConvNeXtV2-Base) | `TimmBackboneModel` |
| | `maxvit_base` | `TimmBackboneModel` |
| Student (mobile) | `mobilenetv4_conv_medium` | `TimmBackboneModel` |
| | `fastvit_sa12` | `TimmBackboneModel` |
| | `efficientformerv2_s2` | `TimmBackboneModel` |

**Thêm arch mới:** đăng ký key → `TimmBackboneModel` (hoặc class mới nếu cần logic riêng) + tạo config `configs/{student,teacher}/<name>.yaml`. Dùng skill `add-model`.

---

## 4. Config system (Hydra)

Root `configs/config.yaml` compose các group; `teacher`/`student` chọn qua override CLI:
```
defaults: data=isic2024 · training=distillation · augmentation=light · _self_
          teacher=<...> · student=<...>   (chọn từ SOTA set bên dưới)
```
| Group | Lựa chọn |
|---|---|
| `data/` | `isic2024`, `pad_ufes_20`, `ham10000`, `fitzpatrick17k`, `poc` |
| `teacher/` | `efficientnetv2_m`, `convnextv2_base`, `maxvit_base` |
| `student/` | `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2` |
| `training/` | `distillation` (KD), `baseline` (no-KD), `default`, `finetuning`, `ablation`, `poc` |
| `augmentation/` | `light` (mặc định), `heavy` (anti-overfit) |

Override CLI: `python scripts/train_student.py teacher=convnextv2_base student=fastvit_sa12 training=baseline`
Cờ toàn cục: `seed=42`, `run_suffix` (tách run-dir cho ablation), `cudnn_deterministic` (**mặc định `true`** = bit-exact; **chỉ** override `false` cho maxvit_base như workaround lỗi cuDNN-backward, không nằm trong config), `device`, `num_workers`.
POC: `configs/config_poc.yaml` (2 epoch, batch 16, data tổng hợp).

> **Reproducibility (đính chính):** `seed=42` kiểm soát data order / init / augmentation ở **mọi** run. Riêng maxvit_base chạy `cudnn_deterministic=false` nên **không bit-exact** (chỉ khác lựa chọn kernel cuDNN) — KHÔNG ảnh hưởng kết luận vì teacher bị **freeze** khi dạy student và mọi số liệu báo cáo là **mean±std trên 5 fold**. Đây không phải "vi phạm mandate seed=42"; cân nhắc bỏ maxvit_base (nếu có) nên dựa vào **accuracy thấp hơn dù nặng ~2×**, không phải lý do reproducibility.

---

## 5. Run-dir convention (fold-aware)

```
experiments/runs/
  teacher/<name>/fold_{0..4}/
    checkpoints/best_model.pth
    config.yaml
    test_metrics.json    ← số generalization KHÔNG bias → trích dẫn cái này
    val_metrics.json     ← best-epoch val (val−test = tín hiệu overfit)
    training_curves.png
  kd_<teacher>_to_<student>/fold_{0..4}/...
  <...>__<run_suffix>/    ← ablation (samp_off, ratio3, …)
```
Sau aggregate: `aggregated.{json,md}` = **mean ± std** — con số để báo cáo (1 fold đơn lẻ variance rất rộng).

---

## 6. Đánh giá & benchmark

- **Accuracy** (device-independent): `test_metrics.json` → aggregate → so KD vs baseline (skill `compare-kd`, `scripts/compare_kd_results.py`).
- **Hiệu năng tĩnh** (so chéo thiết bị được): params / FLOPs / model size — `scripts/benchmark.py`.
- **Latency** (device-specific): cluster CPU latency chỉ là **proxy**, KHÔNG phải số điện thoại; ranking có thể lật trên mobile (nhất là student transformer). On-device thật: export ExecuTorch `.pte` (`scripts/export_executorch.py`) → `scripts/benchmark_mobile.py` (Pixel 6a).
- **Cross-domain / fairness:** HAM10000 (cross-domain), Fitzpatrick17k (fairness) — **chỉ post-hoc, không bao giờ train**.
- Tổng hợp kết quả luận văn: [docs/BENCHMARK_AND_RESULTS.md](BENCHMARK_AND_RESULTS.md).

---

> **Bảo trì file này:** khi thêm arch/config/script hoặc đổi luồng pipeline, cập nhật bảng tương ứng ở §2–§6. Giữ nó ở mức **bản đồ** — chi tiết để trong doc chuyên sâu, tránh trùng lặp gây lệch.
