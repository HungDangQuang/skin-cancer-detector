# Tasks — 2026-06-28

Mục tiêu tổng: **train teacher + student SOTA (KD và baseline) trên dataset đã merge (ISIC 2024 + PAD-UFES-20) → so sánh để chứng minh KD có tác dụng + tìm cặp teacher–student tốt nhất → export model để dùng.**

> Quy ước trong file này: `<T>` = teacher dùng để KD. **Khuyến nghị `<T> = convnextv2_base`** (đã train xong, dùng được ngay). Mọi lệnh submit chạy trên cluster `slurm.uit.edu.vn`, trong thư mục `/datastore/keg/hungdang/skin-cancer-detector`.

---

## ✅ Đã xong (KHÔNG làm lại)
- [x] Sửa lỗi GPU: revert `--gres=gpu` → `--gres=mps:l40:N` + `acquire_gpu` tự nhảy GPU đầy. Smoke-test job 34349 PASS (hop GPU 0→4, không OOM).
- [x] Dataset merged (ISIC + PAD) + prepare + 5-fold splits — **không cần prepare lại**.
- [x] Teacher `convnextv2_base`: train xong 5 fold (job 32551).
- [x] Tooling so sánh KD (`scripts/compare_kd_results.py` + skill `/compare-kd`).
- [x] Tooling export (`slurm/23_export_model.slurm` + `scripts/export_model.py`).
- [x] Bộ baseline cũ (efficientnet_b4 → b0/mobilenetv3/mobilevit) đã train xong (tháng 6).

## 🔧 Quyết định cần chốt trước khi bắt đầu
- [ ] **Teacher KD:** `convnextv2_base` (sẵn sàng) hay `efficientnetv2_m` (nhẹ hơn, phải train lại). → Mặc định lấy `convnextv2_base`.
- [ ] **Có làm `maxvit_base` không?** (từng lỗi cuDNN/OOM) → optional, để cuối.

---

## Phase 1 — Hoàn tất teacher SOTA

> Chỉ cần nếu chọn thêm teacher ngoài `convnextv2_base`.

- [ ] (Tùy chọn) Train `efficientnetv2_m`:
  ```bash
  bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=efficientnetv2_m
  ```
- [ ] Aggregate teacher đã xong (tạo `aggregated.md` cho luận văn):
  ```bash
  bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
      RUN_DIR=experiments/runs/teacher/convnextv2_base
  ```
- [ ] (Tùy chọn, để cuối) Test `maxvit_base`:
  ```bash
  bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base \
      EXTRA="cudnn_deterministic=false training.batch_size=16"
  ```

---

## Phase 2 — Train ma trận student SOTA ⭐ (CỐT LÕI để chứng minh KD)

3 student SOTA × 2 điều kiện (KD / baseline) × 5 fold = **6 job**. Đây chính là 2 nội dung cần so sánh.

**Student SOTA:** `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2`.

- [ ] mobilenetv4_conv_medium — **KD**:
  ```bash
  bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=<T>
  ```
- [ ] mobilenetv4_conv_medium — **baseline (no-KD)**:
  ```bash
  bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium TRAINING=baseline
  ```
- [ ] fastvit_sa12 — **KD**:
  ```bash
  bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TEACHER=<T>
  ```
- [ ] fastvit_sa12 — **baseline**:
  ```bash
  bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TRAINING=baseline
  ```
- [ ] efficientformerv2_s2 — **KD**:
  ```bash
  bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2 TEACHER=<T>
  ```
- [ ] efficientformerv2_s2 — **baseline**:
  ```bash
  bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2 TRAINING=baseline
  ```

**Guideline Phase 2:**
- KD là mặc định (`TRAINING=distillation`) → chỉ cần `STUDENT=` + `TEACHER=`. Baseline → thêm `TRAINING=baseline`, **không** cần `TEACHER`.
- KD **bắt buộc teacher đã train xong** (best_model.pth tồn tại) — submit KD sau khi Phase 1 báo `[job] DONE`.
- Run-dir tự tạo: KD → `experiments/runs/kd_<T>_to_<student>/fold_{0..4}/`, baseline → `experiments/runs/baseline_<student>/fold_{0..4}/`.
- Mỗi job chiếm 4/20 MPS → **tối đa 5 job song song**; job thứ 6 sẽ `PD` chờ (bình thường).
- Mỗi job tự loop 5 fold tuần tự (`--time=72h`).

---

## Phase 3 — So sánh & kết luận KD ⭐

- [ ] (Tùy chọn) Aggregate từng run để có `aggregated.md`:
  ```bash
  bash slurm/submit.sh slurm/22_aggregate_folds.slurm RUN_DIR=experiments/runs/kd_<T>_to_mobilenetv4_conv_medium
  bash slurm/submit.sh slurm/22_aggregate_folds.slurm RUN_DIR=experiments/runs/baseline_mobilenetv4_conv_medium
  # ... lặp cho fastvit_sa12 và efficientformerv2_s2 (KD + baseline)
  ```
- [ ] rsync kết quả về Mac:
  ```bash
  rsync -avz slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/experiments/runs/ ./experiments/runs/
  ```
- [ ] Chạy so sánh (trên Mac, không cần cluster — chỉ đọc JSON):
  ```bash
  python scripts/compare_kd_results.py
  # → reports/comparison/kd_comparison.{md,json}
  ```
  hoặc trong Claude Code gõ: `/compare-kd`
- [ ] Đọc verdict: KD HELPS/MIXED/không (theo AUPRC + pAUC) + **best pair** theo 2 tiêu chí (hiệu năng cao nhất / KD cải thiện nhiều nhất).

**Guideline Phase 3:**
- `compare_kd_results.py` tự gộp 5 fold (mean±std), không bắt buộc chạy `22_aggregate` trước (aggregate chỉ để có bảng `.md` đẹp cho luận văn).
- Verdict đầy đủ cần **cả KD và baseline** của cùng một student → đó là lý do Phase 2 phải chạy đủ 6 job.
- Ưu tiên đọc **AUPRC** (prevalence ~0.4% → AUC-ROC lạc quan giả), rồi **pAUC@TPR80** (metric ISIC chính thức).
- Delta nhỏ hơn std giữa các fold = **nhiễu**, không phải KD có tác dụng.

---

## Phase 4 — Export & dùng model tốt nhất

- [ ] Export student tốt nhất (thay `<best_student>` + fold tốt nhất):
  ```bash
  bash slurm/submit.sh slurm/23_export_model.slurm \
      MODEL=<best_student> \
      CKPT=experiments/runs/kd_<T>_to_<best_student>/fold_<N>/checkpoints/best_model.pth
  # FORMAT=torchscript nếu cần; OUT=exports/<tên>
  ```
- [ ] Download file `.onnx` về Mac, chạy bằng `onnxruntime`.

**Guideline Phase 4:**
- Export **student** (đích deploy), KHÔNG export teacher.
- Inference: model xuất **1 logit thô** → `sigmoid()` → so với **threshold Youden trong `test_metrics.json`** của fold đó (KHÔNG dùng 0.5).
- `.onnx` chạy được mọi nơi có onnxruntime, không cần torch.

---

## 🛠 Mẹo theo dõi & xử lý sự cố

| Tình huống | Cách xử lý |
|---|---|
| Xem job của mình (account `keg` dùng chung) | `squeue -u keg --name=train_student` (lọc theo tên, vì `keg` là account chung) |
| Job ở `PD` lý do `(Resources)` / hết MPS | Bình thường — chờ tới lượt, **không** sửa gì |
| Job ở `PD` lý do `(QOSMaxGRESPerUser)` | Đã chiếm hết 20 MPS budget của user → chờ job khác xong; **đừng** đổi sang `--gres=gpu` (QOS chặn `gpu=0`) |
| Log job | `logs/<job>_<jobid>.out` và `logs/<job>_<jobid>_runtime.log` (trên cluster; rsync về nếu cần) |
| Xác nhận GPU-hop hoạt động | Trong log có `[lib] Re-selecting a GPU...` hoặc `CUDA_VISIBLE_DEVICES=N (Slurm-pinned; ... free >= ...)`, và **không** `OutOfMemoryError` |
| `Teacher checkpoint not found` khi chạy KD | Teacher chưa xong → đợi Phase 1 `[job] DONE` rồi mới submit KD |
| Trước khi đọc log trên Mac | `ls logs/` — nếu thiếu thì rsync từ cluster |

## 📊 Tóm tắt khối lượng

| Phase | Việc | Số job slurm |
|---|---|---|
| 1 | Teacher SOTA (+ aggregate) | 0–2 |
| 2 | **Student SOTA KD + baseline** | **6** ⭐ |
| 3 | Aggregate + so sánh (compare chạy local) | ~12 aggregate (tùy chọn) |
| 4 | Export best student | 1 |

**Đường tới câu trả lời "KD có tác dụng không":** Phase 2 (6 job) → Phase 3 (`/compare-kd`). Phase 1 chỉ cần nếu đổi teacher; Phase 4 là bước dùng model cuối cùng.
