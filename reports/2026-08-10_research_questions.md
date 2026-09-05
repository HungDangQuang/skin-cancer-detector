> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](BAO_CAO_TONG_HOP.md).
>
> Lý do: viết khi CHỈ có 1 teacher (`efficientnetv2_m`) có ma trận KD hợp lệ → kết luận "Q2 chưa trả lời được" nay đã lạc hậu (ma trận 3 teacher × 4 student đã đủ 60/60 fold).

---

# Bằng chứng cho 3 câu hỏi nghiên cứu (cập nhật 2026-08-10, **chỉ dữ liệu train từ 15/7**)

Tổng hợp đánh giá trả lời 3 câu hỏi cần chứng minh của đề tài, **chỉ dùng các run train từ 15/7/2026
trở đi** (đợt huấn luyện hợp lệ). Đây là tài liệu bằng chứng — mỗi số trích từ artifact, không lấy từ trí nhớ.

> ⚠️ **Phạm vi (quan trọng):** Các run **KD `convnextv2_base→*` và `maxvit_base→*` là bản tháng 6 (trước
> 15/7) → ĐÃ LOẠI** khỏi mọi bảng dưới đây. Hệ quả: **teacher duy nhất có ma trận KD hợp lệ là
> `efficientnetv2_m`**. Câu hỏi "teacher nào tạo student tốt nhất" vì thế **chưa trả lời được** (xem Q2).
> File `reports/comparison/kd_comparison.md` (dump thô của script) vẫn liệt kê các dòng tháng 6 — **không dùng**;
> báo cáo này mới là bản đúng phạm vi.

**Nguồn số:**
- Teacher / student: `experiments/runs/<run>/aggregated.json` (mean ± std qua 5 fold).
- Q1 PAD per-domain: `reports/pad_ablation_{efficientnetv2_m,convnextv2_base,maxvit_base}.md`
  (so with-PAD `runs/teacher/*` vs no-PAD `runs_isic_only/teacher/*` — cả hai đều là bản July 15+).

**Quy ước:** headline **AUPRC** (prevalence đo được **~0.39%**); **pAUC@TPR80** = metric chuẩn ISIC 2024.
Luôn trích **mean ± std qua 5 fold**; Δ nhỏ hơn ~1 std của baseline = "trong nhiễu", không tính là thắng.

**Dữ liệu in-scope (đã kiểm tra đủ):** 3 teacher with-PAD (5/5) + 3 teacher no-PAD (5/5); 4 baseline
student SOTA (5/5); **ma trận KD `efficientnetv2_m` × 4 student × 5 fold (đủ 4/4)**. Không có KD hợp lệ cho convnextv2/maxvit.

---

## Q1 — PAD dataset có làm teacher tốt hơn không? → ✅ **CÓ, cho cả 3 teacher**

**Thiết kế:** cùng một test set độc lập (ISIC+PAD), chỉ khác TRAIN+VAL (with-PAD vs ISIC-only). Ô quyết
định là **subset ảnh PAD** (miền lâm sàng mà nhánh no-PAD chưa từng thấy). Cả 3 teacher đều là bản July 15+.

| Teacher | ΔAUPRC (PAD subset) | ΔpAUC@80 | ΔSens | ΔSens@95Spec | Verdict |
|---|---|---|---|---|---|
| efficientnetv2_m | **+0.1241** | +0.0349 | +0.0756 | +0.1844 | ✅ PAD giúp |
| convnextv2_base | **+0.0920** | +0.0356 | +0.1256 | +0.1089 | ✅ PAD giúp |
| maxvit_base | **+0.1311** | +0.0352 | +0.1256 | +0.2322 | ✅ PAD giúp |

- **Miền PAD:** cả 3 teacher tốt hơn hẳn khi có PAD (ΔAUPRC +0.09…+0.13, Sens@95Spec tới +0.23).
- **Miền ISIC:** trung tính (Δ trong nhiễu) → thêm PAD **không hại** miền dermoscopy gốc.
- **Trung thực:** auto-verdict whole-test của convnextv2 ghi "❌ no clear win" chỉ vì ΔSens whole-test
  = −0.02 (artifact ngưỡng); trên subset PAD convnextv2 thắng rõ (ΔSens +0.1256).

> **Kết luận Q1:** Trộn PAD-UFES-20 vào train giúp teacher **tổng quát hóa tốt hơn rõ rệt trên ảnh lâm sàng**
> mà **không hy sinh** miền ISIC — đúng với cả 3 teacher. (Không đổi so với trước; dữ liệu Q1 đều in-scope.)

---

## Q2 — Teacher nào tốt nhất? → ⚠️ **Chỉ so được STANDALONE; câu "teacher-KD tốt nhất" chưa trả lời**

Chỉ có 3 teacher tự đánh giá trên test (`runs/teacher/*/aggregated.json`, đều là bản July 15+):

| Teacher | AUPRC | pAUC@80 | AUC | Sens | Sens@95Spec |
|---|---|---|---|---|---|
| **maxvit_base** | **0.6566 ± 0.0211** | **0.1830 ± 0.0025** | **0.9824 ± 0.0024** | 0.9245 ± 0.0074 | **0.9170 ± 0.0041** |
| convnextv2_base | 0.6506 ± 0.0306 | 0.1822 ± 0.0021 | 0.9816 ± 0.0021 | 0.9203 ± 0.0119 | 0.9154 ± 0.0182 |
| efficientnetv2_m | 0.6298 ± 0.0488 | 0.1826 ± 0.0025 | 0.9820 ± 0.0025 | **0.9270 ± 0.0196** | 0.9120 ± 0.0090 |

- **Standalone:** `maxvit_base` cao nhất ở AUPRC/pAUC/AUC/Sens@95Spec, nhưng **chồng lấn trong 1 std** với
  `convnextv2_base`. `efficientnetv2_m` thấp nhất về AUPRC (dù Sens cao nhất, pAUC ngang nhau).
- **Là teacher KD:** ⚠️ **KHÔNG so được trong phạm vi July-15+** — chỉ `efficientnetv2_m` có ma trận KD hợp lệ;
  KD của convnextv2/maxvit đều là bản tháng 6 đã loại. Vì thế **chưa thể kết luận teacher nào tạo student tốt nhất**.

> **Kết luận Q2 (thận trọng):** Về **chất lượng teacher standalone**, `maxvit_base` ≈ `convnextv2_base` là hai
> teacher mạnh nhất (hơn `efficientnetv2_m`, nhưng trong 1 std). **Để trả lời dứt điểm "teacher nào tốt nhất cho
> chưng cất", cần train lại ma trận KD của `convnextv2_base` và `maxvit_base` trong đợt mới** (xem [§Việc còn lại](#việc-còn-lại-để-khép-q2)).

### ⏳ Bức tranh TẠM THỜI cho Q2 (dữ liệu tháng 6 — CHƯA hợp lệ, chờ train lại)

> ⚠️ **KHÔNG dùng để kết luận.** Bảng dưới điền tạm bằng KD convnextv2/maxvit **bản tháng 6** (distill từ
> teacher **cũ**, config train giống hệt nhưng teacher đã train lại 19–21/7). Chỉ để **hình dung** Q2 trong
> lúc server train lại. Số thật sẽ thay khi có bản July-15+.

Mỗi ô = **AUPRC / pAUC@80** (n fold). Cùng student, so 3 teacher:

| Student (KD) | efficientnetv2_m (Jul ✅) | convnextv2_base (Jun ⏳) | maxvit_base (Jun ⏳) |
|---|---|---|---|
| mobilenetv4_conv_medium | 0.6056 / 0.1859 (n5) | **0.6614 / 0.1898** (n5) | 0.6510 / 0.1905 (n1) |
| fastvit_sa12 | 0.6209 / 0.1853 (n5) | **0.6756 / 0.1908** (n5) | 0.6124 / 0.1888 (n1) |
| efficientformerv2_s2 | 0.6220 / 0.1849 (n5) | **0.6839 / 0.1897** (n4) | — (0 fold) |
| repvit_m1_0 | 0.5537 / 0.1832 (n5) | — (chưa có) | — (chưa có) |

**Xu hướng tạm thời:** `convnextv2_base` tạo student **tốt hơn** `efficientnetv2_m` ở **mọi** student có dữ liệu
(AUPRC +0.05…+0.06, pAUC +0.003…+0.005). Nếu bản train lại giữ xu hướng này → **`convnextv2_base` sẽ là teacher-KD tốt nhất**.
`maxvit_base` mới n=1 → không đọc được.

**Các model đang là PLACEHOLDER (tháng 6) — sẽ update sau khi server train lại:**
- `kd_convnextv2_base_to_mobilenetv4_conv_medium` (n5, Jun) · `kd_convnextv2_base_to_fastvit_sa12` (n5, Jun) · `kd_convnextv2_base_to_efficientformerv2_s2` (n4, Jun)
- `kd_maxvit_base_to_mobilenetv4_conv_medium` (n1, Jun) · `kd_maxvit_base_to_fastvit_sa12` (n1, Jun)
- **Chưa có cả placeholder** (cần train mới hoàn toàn): `kd_convnextv2_base_to_repvit_m1_0`, `kd_maxvit_base_to_efficientformerv2_s2`, `kd_maxvit_base_to_repvit_m1_0`

---

## Q3 — KD có giá trị nghiên cứu không? → ✅ **CÓ** (bằng chứng: ma trận `efficientnetv2_m`, đủ 4/4 × 5 fold)

Thí nghiệm có kiểm soát, **một teacher** `efficientnetv2_m`, so `kd_efficientnetv2_m_to_<student>` với
`baseline_<student>` (cùng seed/data/HP). Tất cả 5 fold, đều bản July 15+.

| Student | AUPRC(KD) | ΔAUPRC | ΔpAUC@80 | ΔSens | ΔSens@95Spec |
|---|---|---|---|---|---|
| repvit_m1_0 | 0.5537 | **+0.0172** | +0.0115 | +0.0124 | +0.0323 |
| fastvit_sa12 | 0.6209 | +0.0127 | +0.0028 | +0.0066 | +0.0108 |
| mobilenetv4_conv_medium | 0.6056 | −0.0045 | +0.0061 | +0.0124 | +0.0141 |
| efficientformerv2_s2 | 0.6220 | −0.0062 | +0.0037 | +0.0108 | +0.0133 |

- **pAUC@TPR80: KD cải thiện 4/4** (+0.003…+0.012). Nhất quán — đúng metric ISIC.
- **Sensitivity & Sens@95Spec: KD cải thiện 4/4** (Sens +0.007…+0.012; Sens@95Spec +0.011…+0.032). KD kéo
  model về **vùng độ nhạy cao** — thứ quan trọng nhất cho tầm soát ung thư. **Đây là bằng chứng chắc chắn nhất.**
- **AUPRC: hỗn hợp** — repvit +0.0172 và fastvit +0.0127 dương; mnv4 −0.0045, efv2 −0.0062 âm nhẹ
  (**đều < 1 std → trong nhiễu**, không phải "KD làm hại").

**Phát hiện phụ:**
- **Không overfit:** gap val−test AUPRC của mọi run in-scope nhỏ (+0.02…+0.04), pAUC ~0.
- **Student tiệm cận teacher ở pAUC/Sens:** student KD đạt pAUC ~0.185 (teacher ~0.183) và Sens ≥ teacher,
  dù nhẹ hơn nhiều lần — đúng mục tiêu KD.

> **Kết luận Q3:** KD (từ `efficientnetv2_m`) **có giá trị rõ ràng**: cải thiện **nhất quán** pAUC@TPR80 và độ
> nhạy (kể cả Sens@95Spec) trên **cả 4** student. Mức thay đổi **AUPRC là biên/nhỏ trong nhiễu** với teacher này
> (2 dương, 2 âm nhẹ). *Bằng chứng KD mạnh nằm ở pAUC + Sensitivity, không phải AUPRC — cần nêu đúng như vậy.*

---

## Model tốt nhất (trong phạm vi July-15+)
Đối tượng triển khai là **student** (mobile). Trong 4 student, nhóm **KD `efficientnetv2_m`** dẫn đầu ở
pAUC@TPR80 / AUC / Sensitivity:

| Student (KD) | AUPRC | pAUC@80 | AUC | Sens | Sens@95Spec |
|---|---|---|---|---|---|
| **mobilenetv4_conv_medium ← efficientnetv2_m** | 0.6056 | **0.1859** | **0.9852** | **0.933** | 0.930 |
| fastvit_sa12 ← efficientnetv2_m | 0.6209 | 0.1853 | 0.9846 | 0.929 | 0.934 |
| efficientformerv2_s2 ← efficientnetv2_m | **0.6220** | 0.1849 | 0.9841 | 0.929 | 0.931 |

- **Ứng viên triển khai tốt nhất:** **`mobilenetv4_conv_medium ← efficientnetv2_m`** — dẫn đầu **pAUC@80
  (0.1859)** + **AUC (0.9852)** + **Sens (0.933)**, và nhẹ/nhanh nhất (benchmark trước ~22 ms, ~32 MB `.pte`).
- **AUPRC cao nhất trong nhóm KD student:** `efficientformerv2_s2 ← efficientnetv2_m` (0.6220).
- Lưu ý: teacher (maxvit/convnextv2 ~0.65 AUPRC) cao hơn student, nhưng nặng → không phải đích triển khai.

## Giới hạn (nêu trong luận văn)
- **Q2 chưa khép:** chỉ có KD của 1 teacher (`efficientnetv2_m`) trong phạm vi → không so được "teacher-KD tốt nhất".
- **KD chỉ được kiểm chứng với 1 teacher** → luận điểm "hiệu quả AUPRC phụ thuộc teacher" (từng nêu ở bản trước)
  **không còn dữ liệu in-scope để khẳng định**; xem như giả thuyết cần train thêm.
- `val_predictions.csv` nhóm KD in-scope đủ 5/5 (calibration được cho ma trận `efficientnetv2_m`).

## Việc còn lại (để khép Q2)
Train **trong đợt mới** (đồng bộ với teacher hiện tại) rồi cập nhật báo cáo:
```bash
# KD convnextv2_base × 4 student (baseline student đã có sẵn)
for S in mobilenetv4_conv_medium fastvit_sa12 efficientformerv2_s2 repvit_m1_0; do
  bash run/train_student.sh STUDENT=$S TEACHER=convnextv2_base TRAINING=distillation
done
# (tùy chọn) tương tự cho maxvit_base
```
Sau đó: `aggregate_folds.py` → `compare_kd_results.py` → cập nhật báo cáo này + `2026-08-09_model_comparison.md`.

---

## Kết luận tổng (một đoạn cho luận văn, đúng phạm vi July-15+)
> Trộn **PAD-UFES-20** vào tập huấn luyện làm **cả 3 teacher tốt hơn rõ rệt trên ảnh lâm sàng** (ΔAUPRC
> +0.09…+0.13 trên miền PAD) mà không hại miền dermoscopy (**Q1 ✅**). Về teacher, `maxvit_base` và
> `convnextv2_base` mạnh hơn `efficientnetv2_m` khi đánh giá standalone (trong 1 std), nhưng do chỉ
> `efficientnetv2_m` có ma trận chưng cất hợp lệ nên **chưa kết luận được teacher nào tạo student tốt nhất**
> (**Q2 ⚠️ — cần train thêm**). **Knowledge Distillation có giá trị**: với teacher `efficientnetv2_m`, KD cải
> thiện **nhất quán** pAUC@TPR≥80% và độ nhạy (kể cả Sens@95Spec) trên **cả 4** student, dù thay đổi AUPRC chỉ
> ở mức nhiễu (**Q3 ✅**). Model triển khai tốt nhất hiện có là **MobileNetV4 chưng cất từ EfficientNetV2-M**
> (pAUC 0.1859, AUC 0.9852, Sens 0.933, nhẹ/nhanh nhất).
