# Benchmark & Kết quả tổng hợp (tài liệu luận văn)

*Cập nhật: 2026-07-04. Nguồn số liệu: `experiments/runs/**/test_metrics.json`,
`reports/benchmark/*.json` (full), `reports/mobile_benchmark/*.json` (proxy),
và benchmark on-device Pixel 6a (2026-07-03).*

Tài liệu gồm 4 phần: (1) giải thích từng độ đo, (2) bảng kết quả accuracy,
(3) bảng benchmark hiệu năng, (4) phần còn thiếu + lệnh slurm để hoàn thiện.

> **⚠️ Lưu ý scope (cập nhật 2026-07-15):** bộ **baseline** (`efficientnet_b4` teacher; `efficientnet_b0`,
> `mobilenetv3_large`, `mobilevit_s` students) đã được **gỡ khỏi codebase** — dự án giờ chỉ còn bộ SOTA
> (`efficientnetv2_m`/`convnextv2_base`/`maxvit_base` → `mobilenetv4_conv_medium`/`fastvit_sa12`/`efficientformerv2_s2`).
> Các số liệu baseline dưới đây là **kết quả đã đo (lịch sử), giữ nguyên** để so sánh/tham khảo, nhưng
> **không còn tái tạo được từ code hiện tại** (registry/config/wrapper đã xóa) và các lệnh `MODEL=<baseline>`
> ở Phần 4 không còn chạy. Xem `CLAUDE.md` §Architecture cho danh sách model hiện hành.

---

## PHẦN 1 — Giải thích các độ đo (vì sao dùng & mức quan trọng)

Ký hiệu: 🔴 Cốt lõi · 🟡 Hỗ trợ · ⚪ Bổ sung.

### 1.1 Độ chính xác (chất lượng model — device-independent)

| Độ đo | Là gì | Vì sao dùng | Mức |
|---|---|---|---|
| **pAUC@TPR≥80%** | Partial AUC vùng TPR≥0.8, chuẩn hoá ~[0.02, 0.20] | Metric **chính thức của ISIC 2024**; chỉ tính vùng độ nhạy cao — đúng nhu cầu sàng lọc ung thư | 🔴 |
| **AUPRC** | Diện tích dưới đường Precision-Recall | Ở prevalence ~0.4%, AUC-ROC lạc quan quá mức → **AUPRC là headline thực sự** | 🔴 |
| **AUC-ROC** | Diện tích dưới ROC | Chuẩn so sánh phổ biến, nhưng lạc quan ở lớp hiếm → dùng kèm, không đứng một mình | 🟡 |
| **Sensitivity (Recall)** | TP/(TP+FN) | Tỉ lệ bắt đúng ca ác tính — **chỉ số an toàn y tế quan trọng nhất** (bỏ sót = nguy hiểm) | 🔴 |
| **Specificity** | TN/(TN+FP) | Tỉ lệ loại đúng ca lành — liên quan số báo động giả | 🔴 |
| **F1 / Precision** | Cân bằng P-R | Ở prevalence thấp precision luôn nhỏ → tham khảo, không dùng làm chính | ⚪ |
| **Threshold (Youden J)** | Ngưỡng quyết định | KHÔNG phải 0.5; chọn để tối đa (Sens+Spec−1). Cần cho triển khai | 🔴 |

### 1.2 Hiệu năng tĩnh (kiến trúc — so chéo thiết bị được)

| Độ đo | Vì sao dùng | Mức |
|---|---|---|
| **Params (M)** | Dung lượng/độ nặng model; chuẩn học thuật. Nhưng **không dự đoán tốc độ** | 🔴 |
| **FLOPs / MACs (G)** | Chi phí tính toán độc lập phần cứng. **Không tỉ lệ latency thực** → luôn đi kèm latency đo | 🔴 |
| **Kích thước `.pte` (MB)** | Quyết định APK size, RAM nạp — rất thực tế cho mobile | 🔴 |

### 1.3 Độ trễ & bộ nhớ (device-specific — chỉ so trong cùng máy)

| Độ đo | Vì sao dùng | Mức |
|---|---|---|
| **Median / p50 (ms)** | Độ trễ điển hình, bền outlier → **headline latency** | 🔴 |
| **Mean ± Std (ms)** | Std = độ ổn định; thấp = UX mượt, đoán trước được | 🔴 |
| **p90 / p95 / p99 (ms)** | Tail latency — trường hợp xấu; cam kết "99% dưới X ms" | 🔴 |
| **Min / Max (ms)** | Min = trần phần cứng; Max = lần tệ (dễ nhiễu) | 🟡 |
| **Cold-start (ms)** | Độ trễ **lần đầu** — ấn tượng đầu của người dùng | 🟡 |
| **Load time (ms)** | Thời gian nạp model (1 lần) — ảnh hưởng khởi động app | 🟡 |
| **FPS** | 1000/latency; chỉ quan trọng nếu xử lý **camera real-time** | ⚪ |
| **Peak RAM (MB)** | RAM đỉnh; cao → Android kill app. **Quan trọng cho mobile** | 🔴 |
| **Throughput sweep (img/s)** | Kịch bản **server batch**, KHÔNG áp dụng app batch=1 | ⚪ |

### 1.4 Cấu hình đo — bắt buộc khai báo (nếu thiếu, phép đo mất giá trị)

**Warmup iters** (bỏ N lần đầu để làm nóng cache/JIT/XNNPACK) · **Measured iters**
(cỡ mẫu) · **Threads** (latency phụ thuộc mạnh) · **Batch size** (=1 cho mobile) ·
**Thiết bị/SoC/ABI/SDK** (latency chỉ có nghĩa khi gắn phần cứng cụ thể).

**3 nguyên tắc vàng:**
1. Params/FLOPs/size so chéo thiết bị được; **latency chỉ so trong cùng máy + cùng threads**.
2. Latency báo cáo **median + tail (p95/p99)**, không chỉ mean.
3. Luôn khai báo warmup + iters + threads + thiết bị.

---

## PHẦN 2 — Kết quả độ chính xác (mean ± std, 5-fold CV, test độc lập)

### 2.1 Teacher

| Teacher | pAUC@80 | AUC-ROC | AUPRC | Sens | Spec |
|---|---|---|---|---|---|
| maxvit_base | 0.1869 ± 0.0033 | 0.9863 | **0.6878 ± 0.0405** | 0.944 | 0.948 |
| convnextv2_base | 0.1893 ± 0.0010 | 0.9888 | 0.6830 ± 0.0225 | 0.949 | 0.947 |
| efficientnetv2_m | 0.1875 ± — | 0.9869 | 0.6487 ± — | 0.928 | 0.956 |
| efficientnet_b4 | 0.1785 ± 0.0031 | 0.9777 | 0.5998 ± 0.0241 | 0.909 | 0.955 |

### 2.2 Student — KD

| Student (teacher) | pAUC@80 | AUC-ROC | AUPRC | Sens | Spec |
|---|---|---|---|---|---|
| **fastvit_sa12** (convnextv2_base) | **0.1908 ± 0.0013** | **0.9902** | **0.6756 ± 0.0306** | 0.949 | 0.953 |
| mobilenetv4_conv_medium (efficientnetv2_m) | 0.1905 ± 0.0011 | 0.9897 | 0.6361 ± 0.0593 | 0.949 | 0.954 |
| mobilenetv4_conv_medium (convnextv2_base) | 0.1898 ± 0.0020 | 0.9891 | 0.6614 ± 0.0284 | 0.962 | 0.941 |
| fastvit_sa12 (efficientnetv2_m) | 0.1896 ± 0.0014 | 0.9888 | 0.6517 ± 0.0319 | 0.953 | 0.953 |
| mobilenetv3_large (efficientnet_b4) | 0.1881 ± 0.0009 | 0.9873 | 0.6313 ± 0.0138 | 0.955 | 0.936 |
| mobilevit_s (efficientnet_b4) | 0.1879 ± 0.0008 | 0.9872 | 0.6391 ± 0.0347 | 0.945 | 0.944 |
| efficientnet_b0 (efficientnet_b4) | 0.1877 ± 0.0005 | 0.9870 | 0.6511 ± 0.0179 | 0.940 | 0.949 |
| ⚠️ efficientformerv2_s2 (convnextv2_base) *(4 fold)* | 0.1897 | 0.9892 | **0.6839** | 0.960 | 0.946 |
| ⚠️ efficientformerv2_s2 (efficientnetv2_m) *(2 fold)* | 0.1899 | 0.9892 | 0.6211 | 0.950 | 0.958 |
| ⚠️ mobilenetv4 (maxvit_base) *(1 fold)* | 0.1905 | 0.9899 | 0.6510 | 0.959 | 0.953 |
| ⚠️ fastvit_sa12 (maxvit_base) *(1 fold)* | 0.1888 | 0.9880 | 0.6124 | 0.934 | 0.953 |

⚠️ = **chưa đủ 5 fold** → độ tin thấp, cần chạy nốt trước khi trích dẫn. Bảng xếp hạng đầy đủ
20 run: [`report_phase_1/evaluation/02_model_comparison.md`](../report_phase_1/evaluation/02_model_comparison.md).

### 2.3 Student — Baseline (không KD)

| Student | pAUC@80 | AUC-ROC | AUPRC | Sens | Spec |
|---|---|---|---|---|---|
| mobilenetv4_conv_medium | 0.1870 ± — | 0.9862 | 0.6090 | 0.956 | 0.934 |
| mobilevit_s | 0.1866 ± 0.0018 | 0.9858 | 0.6273 ± 0.0261 | 0.940 | 0.952 |
| mobilenetv3_large | 0.1858 ± 0.0007 | 0.9852 | 0.6607 ± 0.0317 | 0.934 | 0.956 |
| fastvit_sa12 | 0.1856 ± — | 0.9849 | 0.6679 | 0.938 | 0.951 |
| efficientnet_b0 | 0.1850 ± 0.0023 | 0.9844 | 0.6550 ± 0.0257 | 0.933 | 0.938 |

### 2.4 Hiệu quả KD (KD − Baseline) — GAP-1 đã lấp (2026-07-04)

| Student | Teacher | n(KD) | Δ pAUC@80 | Δ AUPRC | Δ Sens |
|---|---|---|---|---|---|
| **mobilenetv4_conv_medium** | **convnextv2_base** | 5 | +0.0027 | **+0.0524** | +0.0058 |
| mobilenetv4_conv_medium | maxvit_base | ⚠️1 | +0.0035 | +0.0421 | +0.0025 |
| mobilenetv4_conv_medium | efficientnetv2_m | 5 | +0.0035 | +0.0271 | −0.0066 |
| **fastvit_sa12** | **convnextv2_base** | 5 | +0.0052 | +0.0077 | +0.0116 |
| fastvit_sa12 | efficientnetv2_m | 5 | +0.0040 | −0.0162 | +0.0149 |
| fastvit_sa12 | maxvit_base | ⚠️1 | +0.0032 | −0.0555 | −0.0041 |
| efficientnet_b0 | efficientnet_b4 | 5 | +0.0027 | −0.0040 | +0.0075 |
| mobilenetv3_large | efficientnet_b4 | 5 | +0.0023 | −0.0294 | **+0.0216** |
| mobilevit_s | efficientnet_b4 | 5 | +0.0013 | +0.0118 | +0.0050 |

**Kết luận (luận điểm KD — nay có bằng chứng đầy đủ hơn):**
- **Δ pAUC@80 luôn DƯƠNG** trên mọi cặp (student × teacher), Δ Sensitivity dương ở hầu hết →
  KD cải thiện nhất quán **vùng độ nhạy cao**, đúng thứ quan trọng cho sàng lọc.
- **Δ AUPRC phụ thuộc CHẤT LƯỢNG TEACHER:** teacher mạnh **convnextv2_base** cho Δ AUPRC dương rõ
  (mobilenetv4 **+0.0524**: 0.609→0.661; fastvit +0.0077); teacher yếu **efficientnet_b4** cho Δ
  lẫn lộn/âm. → *KD chỉ nâng AUPRC khi teacher đủ mạnh.*
- **Case KD thuyết phục nhất:** `mobilenetv4 ← convnextv2_base` (dương cả pAUC/AUPRC/Sens) — nên
  làm ví dụ chính trong proposal.

⚠️ Các cặp `teacher=maxvit_base` mới 1 fold → Δ chưa đáng tin, cần chạy nốt 5 fold.

**Phát hiện phụ:** teacher efficientnet_b4 AUPRC chỉ **0.5998** — thấp hơn cả student của nó, và
thấp hơn hẳn teacher SOTA (maxvit 0.688 / convnextv2 0.683). efficientnet_b4 là teacher yếu.

---

## PHẦN 3 — Kết quả benchmark hiệu năng

### 3.1 Hiệu năng tĩnh (so chéo thiết bị được)

| Model | Params (M) | GFLOPs | GMACs | Size FP32 (MB) |
|---|---|---|---|---|
| efficientnet_b0 | 4.009 | *(thiếu)* | | 15.45 |
| mobilenetv3_large | 4.203 | *(thiếu)* | | 16.13 |
| mobilevit_s | 4.938 | *(thiếu)* | | 18.89 |
| mobilenetv4_conv_medium | 8.436 | 1.653 | 0.826 | 32.44 |
| fastvit_sa12 | 10.557 | 2.962 | 1.481 | 40.41 |
| efficientformerv2_s2 | 12.132 | 2.493 | 1.246 | 46.75 |
| efficientnet_b4 (teacher) | 17.55 | *(thiếu)* | | 67.43 |

### 3.2 Latency proxy trên cluster (single-thread, batch=1, median ms)

| Model | CPU proxy (server) | GPU L40 (cuda) |
|---|---|---|
| mobilenetv3_large | 8.64 | *(thiếu)* |
| mobilenetv4_conv_medium | 17.36 | 0.75 |
| efficientnet_b0 | 22.22 | *(thiếu)* |
| mobilevit_s | 35.73 | *(thiếu)* |
| efficientformerv2_s2 | 37.64 | 7.17 |
| fastvit_sa12 | 41.73 | 3.57 |
| efficientnet_b4 (teacher) | 46.23 | *(thiếu)* |

⚠️ CPU proxy đo trên CPU x86 server — **KHÔNG phải số điện thoại**, chỉ để so tương đối.

### 3.3 Latency ON-DEVICE thật — Pixel 6a (Google Tensor, arm64-v8a, SDK 36)

`.pte` FP32 · warmup 10 · 50 iters · batch=1 · run 2026-07-04 (4 model cùng phiên).

| Model | Size .pte | median@t1 | median@t4 | p90@t4 | Cold@t4 | FPS@t4 |
|---|---|---|---|---|---|---|
| **mobilenetv3_large** | 16.05 MB | 18.20 | **8.40** | 9.23 | 12.01 | **119** |
| mobilenetv4_conv_medium | 32.11 MB | 53.32 | 22.64 | 23.98 | 34.94 | 44 |
| efficientformerv2_s2 | 46.98 MB | 88.60 | 42.83 | 44.36 | 61.52 | 23 |
| fastvit_sa12 | 40.35 MB | 142.32 | 65.48 | 68.29 | 91.56 | 15.3 |

### 3.4 Proxy vs thực tế — hệ số phạt trên ARM (single-thread)

| Model | Cluster CPU | Pixel 6a t1 | Hệ số phạt |
|---|---|---|---|
| mobilenetv3_large | 8.64 | 18.20 | 2.1× |
| efficientformerv2_s2 | 37.64 | 88.60 | 2.4× |
| mobilenetv4_conv_medium | 17.36 | 53.32 | 3.1× |
| fastvit_sa12 | 41.73 | 142.32 | **3.4×** |

→ **Phát hiện chính:** latency ranking ĐẢO trên mobile; model transformer (fastvit)
bị phạt nặng nhất. FLOPs/proxy **không** dự đoán được latency thật trên ARM.

### 3.5 Bảng đánh đổi cho 3 ứng viên mobile (accuracy vs on-device)

| Model (bản) | AUPRC | pAUC | median@t4 | Size | Vai trò |
|---|---|---|---|---|---|
| mobilenetv3_large (KD, đã deploy) | 0.6313 | 0.1881 | **8.4 ms** | **16 MB** | Nhanh/nhẹ nhất |
| mobilenetv3_large (baseline) | **0.6607** | 0.1858 | (≈KD) | (≈16 MB) | AUPRC cao nhất trong nhóm nhẹ |
| **mobilenetv4_conv_medium** (convnextv2) | **0.6614** | 0.1898 | 22 ms | 32 MB | **Cân bằng, bằng chứng đủ** |
| fastvit_sa12 (convnextv2) | 0.6756 | 0.1908 | 64 ms | 40 MB | Accuracy cao nhất, quá chậm |

*Lưu ý bất ngờ:* bản **baseline mobilenetv3 (AUPRC 0.6607) ≈ mobilenetv4 (0.6614)** nhưng
nhanh gấp 2.6× và nhẹ nửa. Bản KD mobilenetv3 (đang deploy trên phone) lại thấp hơn (0.6313)
— nên nếu AUPRC là tiêu chí chính, đáng cân nhắc export & benchmark **baseline mobilenetv3**.

---

## PHẦN 4 — Phần còn thiếu & lệnh slurm để hoàn thiện

Chạy trên cluster (VPN → `ssh keg@slurm.uit.edu.vn` → `cd /datastore/keg/hungdang/skin-cancer-detector`).

### GAP-1 ✅ ĐÃ XONG (2026-07-04) — baseline fastvit + mobilenetv4 đã có
`baseline_fastvit_sa12` và `baseline_mobilenetv4_conv_medium` đã train đủ 5 fold → Δ KD đã tính
(xem 2.4). Kết quả: KD từ teacher mạnh convnextv2_base nâng AUPRC mobilenetv4 +0.052.

**GAP-1b 🔴 còn lại — chạy nốt fold cho các run KD dở dang:**
```bash
# maxvit-KD mới 1 fold, efficientformerv2_s2 mới 2–4 fold → chạy nốt các fold còn thiếu
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=maxvit_base FOLDS="1 2 3 4"
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TEACHER=maxvit_base FOLDS="1 2 3 4"
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2 TEACHER=convnextv2_base FOLDS="4"
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2 TEACHER=efficientnetv2_m FOLDS="2 3 4"
# (tham chiếu: lệnh train baseline gốc, nếu cần train lại)
# bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12 TRAINING=baseline
bash slurm/submit.sh slurm/22_aggregate_folds.slurm RUN_DIR=experiments/runs/baseline_fastvit_sa12
bash slurm/submit.sh slurm/22_aggregate_folds.slurm RUN_DIR=experiments/runs/baseline_mobilenetv4_conv_medium
```

### GAP-2 ✅ ĐÃ XONG (2026-07-04) — AUPRC đã re-eval cho 7 run cũ
Đã chạy `slurm/20_evaluate.slurm` (35 job) để sinh lại `test_metrics.json` + `predictions.csv`
có AUPRC cho `baseline_{efficientnet_b0,mobilenetv3_large,mobilevit_s}`,
`kd_efficientnet_b4_to_{efficientnet_b0,mobilenetv3_large,mobilevit_s}`, `teacher/efficientnet_b4`.
Lệnh tham chiếu (nếu cần lặp lại cho run khác):

```bash
for F in 0 1 2 3 4; do
  bash slurm/submit.sh slurm/20_evaluate.slurm \
    MODEL=<arch> \
    CKPT=experiments/runs/<run>/fold_${F}/checkpoints/best_model.pth \
    OUT=experiments/runs/<run>/fold_${F}/test_metrics.json
done
```

### GAP-3 🟡 — Benchmark full (FLOPs + GPU) còn thiếu
*Vì sao:* `reports/benchmark/` mới có fastvit + mobilenetv4 → thiếu FLOPs của các model nhẹ.

```bash
bash slurm/submit.sh slurm/24_benchmark.slurm MODEL=mobilenetv3_large \
    CKPT=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_0/checkpoints/best_model.pth
bash slurm/submit.sh slurm/24_benchmark.slurm MODEL=efficientnet_b0 \
    CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth
bash slurm/submit.sh slurm/24_benchmark.slurm MODEL=mobilevit_s \
    CKPT=experiments/runs/kd_efficientnet_b4_to_mobilevit_s/fold_0/checkpoints/best_model.pth
```

### GAP-4 🟡 — Đo trên mobile: Peak RAM + end-to-end latency
*Vì sao:* hai thứ này chỉ đo được **trong app Android**, không có trên cluster.
- Peak RAM: `Debug.getMemoryInfo()` / `Runtime` quanh vòng inference.
- End-to-end: bọc thời gian cả `resize + normalize + forward + sigmoid`, không chỉ `forward`.
(Không có lệnh slurm — làm trong app; xem `SkinDetector/docs/MODEL_HANDOFF.md`.)

### GAP-5 ⚪ — efficientformerv2_s2 (student mobile-SOTA thứ 3) chưa train
*Vì sao:* để bộ mobile-SOTA đủ 3 kiến trúc. Tốn 1 lượt train KD đầy đủ (tùy chọn).

```bash
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2 TEACHER=convnextv2_base
```

### GAP-6 ⚪ — On-device cho model khác + parity check
- Nếu muốn số on-device của efficientnet_b0 / mobilevit_s: export `.pte` (slurm 25) → đo trên phone.
- **Parity check** (`max|Δlogit|<1e-3`) chưa xác nhận — bắt buộc trước khi tin số on-device.

---

## Trạng thái sẵn sàng cho luận văn

| Hạng mục | Trạng thái |
|---|---|
| Accuracy 16 student-run + 4 teacher (5-fold) | ✅ Đủ (một số run KD SOTA n<5) |
| AUPRC toàn bộ run | ✅ Có (GAP-2 xong 2026-07-04) |
| Hiệu quả KD (mọi student, gồm fastvit + mobilenetv4) | ✅ Có (GAP-1 xong) — pAUC/Sens dương nhất quán; AUPRC tùy teacher |
| Benchmark on-device 3 ứng viên mobile | ✅ Có (Pixel 6a) |
| Fold đủ 5 cho maxvit-KD + efficientformerv2_s2 | ❌ GAP-1b |
| FLOPs cho model nhẹ | ❌ GAP-3 |
| Peak RAM / end-to-end mobile + parity check | ❌ GAP-4 |

**Đủ để làm đề cương/proposal ngay** — luận điểm KD đã có bằng chứng đầy đủ (case chính
mobilenetv4←convnextv2, +0.052 AUPRC). Còn lại là hoàn thiện: GAP-1b (chạy nốt fold dở dang)
rồi GAP-3/4 bổ sung. Bản tổng hợp đầy đủ & mới nhất: [`report_phase_1/`](../report_phase_1/).
