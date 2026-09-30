> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](../../reports/BAO_CAO_TONG_HOP.md).
>
> Lý do: cùng phạm vi "chỉ 1 teacher" (22/08); ΔKD nay có paired bootstrap CI, không còn chỉ mean ± std.

---

# Hiệu quả Knowledge Distillation (KD vs Baseline) — Phase 1

Câu hỏi cốt lõi của đề tài: **KD có làm student tốt hơn khi train KHÔNG có KD (baseline) không?**
So sánh trực tiếp `kd_<teacher>_to_<student>` với `baseline_<student>` (cùng kiến trúc, cùng
data/seed/siêu tham số — chỉ khác hàm mất mát). Δ = KD − Baseline (dương = KD giúp).

Cập nhật **2026-08-22**. Nguồn: `experiments/runs/<run>/aggregated.json`, 5 fold mỗi run.

---

## 0. ⚠️ Phạm vi

Chỉ dùng run từ **15/7/2026**. Vì thế bảng dưới **chỉ có một teacher — `efficientnetv2_m`** —
nhưng **đủ cả 4 student × 5 fold**, tức một ma trận KD *hoàn chỉnh* cho teacher đó.
KD của `convnextv2_base`/`maxvit_base` là bản tháng 6 (đang train lại, run-dir trộn fold) → **loại**.

---

## 1. Bảng Δ đầy đủ (KD − Baseline, teacher `efficientnetv2_m`)

| Student | n | Δ pAUC@80 | Δ AUPRC | Δ AUC | Δ Sens | Δ Sens@95Spec |
|---|---|---|---|---|---|---|
| **repvit_m1_0** | 5 | **+0.0115** | **+0.0172** | +0.0114 | +0.0124 | **+0.0324** |
| **fastvit_sa12** | 5 | +0.0028 | **+0.0127** | +0.0029 | +0.0066 | +0.0108 |
| mobilenetv4_conv_medium | 5 | +0.0061 | −0.0045 | +0.0062 | +0.0124 | +0.0141 |
| efficientformerv2_s2 | 5 | +0.0037 | −0.0062 | +0.0037 | +0.0108 | +0.0133 |

Baseline dùng để trừ: repvit 0.5365 · fastvit 0.6082 · mobilenetv4 0.6101 · efficientformerv2 0.6283 (AUPRC).

---

## 2. Kết luận (đây là luận điểm KD cho luận văn)

### 2.1 KD cải thiện NHẤT QUÁN pAUC@80, Sensitivity và Sens@95Spec
Trên **cả 4/4 student**: **ΔpAUC@80 luôn dương** (+0.0028 → +0.0115), **ΔSensitivity luôn dương**
(+0.0066 → +0.0124), **ΔSens@95Spec luôn dương** (+0.0108 → +0.0324), **ΔAUC luôn dương**.
Nghĩa là KD kéo model về **vùng độ nhạy cao** — chính là thứ quan trọng cho sàng lọc ung thư.
**Đây là bằng chứng chắc chắn nhất của đề tài.**

Đáng chú ý: mức cải thiện **lớn nhất rơi vào student yếu nhất** (`repvit_m1_0`, ΔpAUC +0.0115,
ΔSens@95Spec +0.0324) — gợi ý student càng thiếu năng lực thì càng hưởng lợi từ tín hiệu mềm của
teacher. Đây mới là *gợi ý*, chưa phải kết luận (1 teacher, 4 điểm dữ liệu).

### 2.2 AUPRC — HỖN HỢP, nằm trong nhiễu
- repvit **+0.0172** và fastvit **+0.0127** dương; mobilenetv4 −0.0045 và efficientformerv2 −0.0062 âm nhẹ.
- **Cả 4 Δ đều nhỏ hơn 1 std của baseline tương ứng** (std AUPRC 0.015–0.048) → mô tả đúng là
  **"trong nhiễu"**, KHÔNG phải "KD làm hại".
- → Với teacher `efficientnetv2_m`, **KD không nâng AUPRC một cách đáng tin**. Giá trị của KD nằm ở
  pAUC + độ nhạy.

> ⚠️ **Luận điểm cũ đã RÚT:** *"Hiệu quả trên AUPRC phụ thuộc chất lượng teacher — ConvNeXtV2 nâng
> AUPRC của MobileNetV4 +0.052"*. Nó dựa hoàn toàn trên KD `convnextv2_base` bản **tháng 6**, ngoài
> phạm vi. Đây hiện là **giả thuyết cần train thêm**, không phải phát hiện đã chứng minh.

### 2.3 Cặp KD tốt nhất
Tùy tiêu chí, và nên nói rõ cả hai:
- **Theo Δ (KD giúp nhiều nhất):** `repvit_m1_0 ← efficientnetv2_m` — dương ở **mọi** metric, mạnh nhất
  ở ΔpAUC (+0.0115) và ΔSens@95Spec (+0.0324).
- **Theo hiệu năng tuyệt đối (model để deploy):** `mobilenetv4_conv_medium ← efficientnetv2_m` —
  pAUC 0.1859 / AUC 0.9852 / Sens 0.933, dẫn đầu student, và nhanh/nhẹ nhất.

### 2.4 Cảnh báo độ tin
- **Chỉ kiểm chứng với 1 teacher.** Mọi phát biểu phải kèm mệnh đề *"với teacher EfficientNetV2-M"*.
- **ΔAUPRC có std lớn** (0.015–0.053) → ở phạm vi này **không có ΔAUPRC nào vượt ngưỡng khẳng định mạnh**.
- **Paired t-test chưa được cài đặt** (`scripts/compare_kd_results.py` chỉ tính mean±std + Δ, pure
  stdlib không import scipy). Hiện dùng heuristic "Δ < 1 std = trong nhiễu". Cần bổ sung trước khi
  viết chương kết quả.

---

## 3. Thông điệp một câu cho slide
> "Với teacher EfficientNetV2-M, Knowledge Distillation cải thiện **nhất quán trên cả 4/4 kiến trúc
> student** ở pAUC@TPR≥80%, AUC và độ nhạy (kể cả Sens@95Spec); thay đổi ở AUPRC nằm trong nhiễu."
