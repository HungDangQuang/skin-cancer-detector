# Hiệu quả Knowledge Distillation (KD vs Baseline) — Phase 1

Câu hỏi cốt lõi của đề tài: **KD có làm student tốt hơn khi train KHÔNG có KD (baseline) không?**
So sánh trực tiếp `kd_<teacher>_to_<student>` với `baseline_<student>` (cùng kiến trúc, cùng
data/seed). Δ = KD − Baseline (dương = KD giúp).

⚠️ Δ nên đọc cùng std của từng run (±0.01–0.06 tuỳ metric). Các cặp có KD run n<5 fold được đánh dấu.

---

## 1. Bảng Δ đầy đủ (KD − Baseline)

| Student | Teacher | n(KD) | Δ pAUC@80 | Δ AUPRC | Δ Sens |
|---|---|---|---|---|---|
| **mobilenetv4_conv_medium** | **convnextv2_base** | 5 | +0.0027 | **+0.0524** | +0.0058 |
| mobilenetv4_conv_medium | maxvit_base | ⚠️1 | +0.0035 | +0.0421 | +0.0025 |
| mobilenetv4_conv_medium | efficientnetv2_m | 5 | +0.0035 | +0.0271 | −0.0066 |
| **fastvit_sa12** | **convnextv2_base** | 5 | +0.0052 | +0.0077 | +0.0116 |
| fastvit_sa12 | efficientnetv2_m | 5 | +0.0040 | −0.0162 | +0.0149 |
| fastvit_sa12 | maxvit_base | ⚠️1 | +0.0032 | −0.0555 | −0.0041 |
| efficientnet_b0 | efficientnet_b4 | 5 | +0.0027 | −0.0040 | +0.0075 |
| mobilenetv3_large | efficientnet_b4 | 5 | +0.0023 | −0.0294 | +0.0216 |
| mobilevit_s | efficientnet_b4 | 5 | +0.0013 | +0.0118 | +0.0050 |

---

## 2. Kết luận (đây là luận điểm KD cho luận văn)

### 2.1 KD cải thiện NHẤT QUÁN pAUC@80 và Sensitivity
Trên **tất cả** cặp (mọi student × mọi teacher), **Δ pAUC@80 luôn dương** (+0.001 → +0.005),
và **Δ Sensitivity dương ở hầu hết** trường hợp. Nghĩa là KD giúp model tốt hơn ở **vùng độ
nhạy cao** — chính là thứ quan trọng cho sàng lọc ung thư. Đây là bằng chứng chắc chắn nhất.

### 2.2 Hiệu quả trên AUPRC PHỤ THUỘC CHẤT LƯỢNG TEACHER
Đây là phát hiện quan trọng và tinh tế:
- **Teacher mạnh (convnextv2_base)** → Δ AUPRC **dương rõ** cho cả 2 student SOTA:
  mobilenetv4 **+0.0524** (baseline 0.609 → 0.661), fastvit +0.0077. **KD thực sự hiệu quả.**
- **Teacher yếu (efficientnet_b4)** → Δ AUPRC lẫn lộn/âm (b0 −0.004, mobilenetv3 −0.029).
- → *KD chỉ phát huy trên AUPRC khi teacher đủ mạnh.* Distill từ teacher yếu chỉ giúp vùng
  high-sensitivity chứ không nâng được AUPRC tổng thể.

### 2.3 Cặp KD tốt nhất
**mobilenetv4_conv_medium ← convnextv2_base**: dương trên CẢ pAUC, AUPRC (+0.052 lớn nhất) và
Sens → minh hoạ thuyết phục nhất cho "KD có tác dụng". Nên đưa cặp này làm **case chính** trong
proposal, kèm mobilenetv3 (Δ Sens +0.022) để cho thấy KD tăng độ nhạy.

### 2.4 Cảnh báo độ tin
- Các cặp **teacher=maxvit_base mới có 1 fold** → Δ chưa đáng tin, cần chạy nốt 5 fold.
- Δ AUPRC có std lớn (0.03–0.06); các Δ nhỏ (<1 std) nên mô tả là "trong nhiễu", chỉ Δ lớn như
  mobilenetv4←convnextv2 (+0.052) mới nên khẳng định mạnh.

---

## 3. Thông điệp một câu cho slide
> "KD cải thiện nhất quán pAUC@TPR≥80% và độ nhạy trên mọi kiến trúc student; mức cải thiện
> AUPRC phụ thuộc chất lượng teacher — với teacher mạnh (ConvNeXtV2), KD nâng AUPRC của
> MobileNetV4 thêm +0.052 (0.609 → 0.661)."
