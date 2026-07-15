# So sánh model — model nào tốt hơn (Phase 1)

Tất cả số là **mean qua các fold** trên **tập test độc lập** (patient-disjoint). Cột **n**
= số fold có kết quả; **n<5 = chưa đủ 5-fold → độ tin thấp hơn, đọc thận trọng**.

Cách đọc: xếp hạng chính theo **pAUC@80** (metric ISIC) và **AUPRC** (headline ở prevalence 0.4%).

---

## 1. Bảng xếp hạng đầy đủ (sắp theo pAUC@80 giảm dần)

| # | Model | Vai trò | n | pAUC@80 | AUPRC | AUC | Sens | Sens@95Spec |
|---|---|---|---|---|---|---|---|---|
| 1 | fastvit_sa12 ← convnextv2_base | KD | 5 | **0.1908** | 0.6756 | 0.9902 | 0.949 | 0.944 |
| 2 | mobilenetv4 ← maxvit_base | KD | ⚠️1 | 0.1905 | 0.6510 | 0.9899 | 0.959 | 0.959 |
| 3 | mobilenetv4 ← efficientnetv2_m | KD | 5 | 0.1905 | 0.6361 | 0.9897 | 0.949 | 0.947 |
| 4 | efficientformerv2_s2 ← efficientnetv2_m | KD | ⚠️2 | 0.1899 | 0.6211 | 0.9892 | 0.950 | 0.950 |
| 5 | mobilenetv4 ← convnextv2_base | KD | 5 | 0.1898 | 0.6614 | 0.9891 | **0.962** | 0.940 |
| 6 | efficientformerv2_s2 ← convnextv2_base | KD | ⚠️4 | 0.1897 | **0.6839** | 0.9892 | 0.960 | 0.947 |
| 7 | fastvit_sa12 ← efficientnetv2_m | KD | 5 | 0.1896 | 0.6517 | 0.9888 | 0.953 | 0.948 |
| — | **convnextv2_base** | *teacher* | 5 | 0.1893 | 0.6830 | 0.9888 | 0.949 | 0.936 |
| 8 | fastvit_sa12 ← maxvit_base | KD | ⚠️1 | 0.1888 | 0.6124 | 0.9880 | 0.934 | 0.934 |
| 9 | mobilenetv3_large ← efficientnet_b4 | KD | 5 | 0.1881 | 0.6313 | 0.9873 | 0.955 | 0.927 |
| 10 | mobilevit_s ← efficientnet_b4 | KD | 5 | 0.1879 | 0.6391 | 0.9872 | 0.945 | 0.932 |
| 11 | efficientnet_b0 ← efficientnet_b4 | KD | 5 | 0.1877 | 0.6511 | 0.9870 | 0.940 | 0.932 |
| — | efficientnetv2_m | *teacher* | 5 | 0.1875 | 0.6487 | 0.9869 | 0.928 | 0.928 |
| 12 | mobilenetv4 | baseline | 5 | 0.1870 | 0.6090 | 0.9862 | 0.956 | 0.933 |
| — | **maxvit_base** | *teacher* | 5 | 0.1869 | **0.6878** | 0.9863 | 0.944 | 0.934 |
| 13 | mobilevit_s | baseline | 5 | 0.1866 | 0.6273 | 0.9858 | 0.940 | 0.934 |
| 14 | mobilenetv3_large | baseline | 5 | 0.1858 | 0.6607 | 0.9852 | 0.934 | 0.933 |
| 15 | fastvit_sa12 | baseline | 5 | 0.1856 | 0.6679 | 0.9849 | 0.938 | 0.929 |
| 16 | efficientnet_b0 | baseline | 5 | 0.1850 | 0.6550 | 0.9844 | 0.933 | 0.910 |
| — | efficientnet_b4 | *teacher* | 5 | 0.1785 | 0.5998 | 0.9777 | 0.909 | 0.910 |

⚠️ = chưa đủ 5 fold (maxvit-KD mới 1 fold; efficientformerv2_s2 2–4 fold). Cần chạy nốt để chốt.

---

## 2. Kết luận rút ra

### 2.1 Model chính xác nhất (tổng thể)
- **KD fastvit_sa12 ← convnextv2_base** dẫn đầu pAUC (0.1908) + AUC (0.9902), AUPRC cao (0.6756).
- Về **AUPRC** (headline): cao nhất là **efficientformerv2_s2 ← convnextv2_base (0.6839)** nhưng
  mới 4 fold ⚠️; kế đến fastvit (0.6756) và mobilenetv4←convnextv2 (0.6614) đều đủ 5 fold.

### 2.2 Teacher tốt nhất
- **maxvit_base (AUPRC 0.6878)** và **convnextv2_base (0.6830)** là 2 teacher mạnh nhất.
- **efficientnet_b4 yếu nhất** (AUPRC 0.5998, pAUC 0.1785) — thấp hơn cả student của nó.
- → Teacher mạnh (convnextv2/maxvit) tạo ra student tốt hơn hẳn teacher yếu (efficientnet_b4).

### 2.3 Student vượt teacher
- Mọi student SOTA (0.63–0.68 AUPRC) **vượt teacher efficientnet_b4 (0.60)**. KD + kiến trúc
  mobile hiện đại cho kết quả tốt hơn teacher CNN cũ.

### 2.4 Ứng viên cho mobile (đã export `.pte`, đo on-device Pixel 6a)
| Model (bản deploy) | pAUC | AUPRC | Sens | Latency@t4 | Size .pte | Fold |
|---|---|---|---|---|---|---|
| fastvit ← convnextv2 (KD) | **0.1908** | 0.6756 | 0.949 | 65 ms | 40 MB | 5 |
| efficientformerv2_s2 ← convnextv2 (KD) | 0.1897 | **0.6839** | 0.960 | 43 ms | 47 MB | ⚠️4 |
| **mobilenetv4 ← convnextv2 (KD)** | 0.1898 | 0.6614 | **0.962** | 22 ms | 32 MB | 5 |
| mobilenetv3 ← b4 (KD) | 0.1881 | 0.6313 | 0.955 | **8.4 ms** | **16 MB** | 5 |

**Khuyến nghị Phase 1:** **mobilenetv4 ← convnextv2_base** là điểm cân bằng tốt nhất (đủ 5 fold,
AUPRC 0.6614, Sens cao nhất 0.962, 22 ms/32 MB). Chọn **mobilenetv3** nếu ưu tiên tốc độ/nhẹ
tuyệt đối (8.4 ms/16 MB, đổi lại AUPRC thấp hơn).

**Ứng viên mới nổi:** **efficientformerv2_s2** có **AUPRC cao nhất (0.6839)** và **nhanh hơn
fastvit** trên máy thật (43 vs 65 ms) — vượt fastvit ở cả accuracy lẫn tốc độ. Nhược: `.pte` lớn
nhất (47 MB) và **mới 4 fold** → cần chạy nốt fold 5 rồi mới đưa vào khẳng định chính thức.

*Chi tiết benchmark: xem [../benchmark/README.md](../benchmark/README.md). Hiệu quả KD: xem
[03_kd_effectiveness.md](03_kd_effectiveness.md).*
