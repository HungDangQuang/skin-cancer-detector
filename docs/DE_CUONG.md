# ĐỀ CƯƠNG ĐỀ TÀI (RÚT GỌN)

**Tên đề tài:** Phát hiện ung thư da trên ảnh tổn thương da bằng học sâu kết hợp
Chưng cất tri thức (Knowledge Distillation) hướng tới triển khai trên thiết bị di động.

---

## 1. Nội dung

### a. Giới thiệu về đề tài

Ung thư da, đặc biệt là u hắc tố ác tính (melanoma), là một trong những loại ung thư
nguy hiểm nhưng có khả năng điều trị cao nếu được phát hiện sớm. Việc chẩn đoán hiện
nay phụ thuộc nhiều vào kinh nghiệm của bác sĩ da liễu qua quan sát ảnh dermoscopy,
dễ có sai khác giữa các chuyên gia và khó tiếp cận ở tuyến cơ sở.

Đề tài xây dựng một mô hình học sâu **phân loại nhị phân** tổn thương da
(lành tính = 0 / ác tính = 1) trên ảnh dermoscopy của bộ dữ liệu **ISIC 2024**,
kết hợp thêm ảnh chụp bằng điện thoại từ **PAD-UFES-20** để mô hình bền vững hơn với
ảnh thực tế ngoài phòng khám.

Một thách thức triển khai là mô hình chính xác thường rất lớn, khó chạy trên thiết bị
di động. Vì vậy đề tài sử dụng **Chưng cất tri thức (Knowledge Distillation - KD)**:
huấn luyện một mô hình "thầy" (teacher) dung lượng lớn, mạnh, rồi *chưng cất* tri thức
đó sang các mô hình "trò" (student) nhẹ, phù hợp để chạy trên điện thoại mà vẫn giữ
được độ chính xác cao.

### b. Mục tiêu đề tài

- Xây dựng **pipeline KD hai giai đoạn** (teacher → student) cho bài toán phân loại
  nhị phân ung thư da, có thể tái lập đầy đủ.
- Đạt chất lượng cao theo **metric chính thức của ISIC 2024 — pAUC@TPR≥80%**
  (miền giá trị ≈ [0.02, 0.20]) và **AUPRC** (chỉ số phù hợp khi tỉ lệ dương tính chỉ
  ~0.4%, thay cho AUC-ROC vốn lạc quan ở mức mất cân bằng cực đoan này).
- Tạo ra bộ **student nhẹ, triển khai được trên di động**, có báo cáo về số tham số,
  dung lượng mô hình và độ trễ suy luận trên CPU.
- Đánh giá **khả năng tổng quát hóa xuyên miền** (HAM10000) và **tính công bằng theo
  tông da** (Fitzpatrick17k).

### c. Nội dung nghiên cứu của đề tài

**+ Xây dựng bài toán**

- Đầu vào: ảnh tổn thương da (chuẩn hóa về 224×224). Đầu ra: một logit duy nhất, áp
  `sigmoid` ở suy luận để cho xác suất ác tính → phân loại nhị phân.
- Thách thức chính: **mất cân bằng lớp cực đoan** (~0.4% mẫu ác tính), đòi hỏi hàm mất
  mát và chiến lược lấy mẫu phù hợp; **chống rò rỉ dữ liệu** giữa các lần chia (mọi tổn
  thương của một bệnh nhân phải nằm cùng một fold — ràng buộc patient-disjoint); và yêu
  cầu mô hình **đủ nhẹ** cho thiết bị di động.

**+ Giải pháp đề xuất**

- **Chưng cất tri thức (KD):** hàm mất mát tổng hợp
  `L = 0.3·focal(student, y) + 0.7·T²·BCE(σ(s/T), σ(t/T))`, với nhiệt độ `T = 4.0`;
  teacher được **đóng băng** trong suốt quá trình huấn luyện student.
- **Bộ teacher:** baseline `efficientnet_b4`, cùng nhóm SOTA `efficientnetv2_m`,
  `convnextv2_base`, `maxvit_base`.
- **Bộ student (nhẹ, tối ưu cho di động):** baseline `efficientnet_b0`,
  `mobilenetv3_large`, `mobilevit_s`; nhóm SOTA `mobilenetv4_conv_medium`,
  `fastvit_sa12`, `efficientformerv2_s2`.
- **Xử lý mất cân bằng:** hàm `BinaryFocalLoss` + `DynamicUndersampledSampler` giữ tỉ
  lệ ác tính:lành tính ≈ 1:5 mỗi epoch + trộn thêm dữ liệu PAD-UFES-20 (nhiều ca ác
  tính hơn).
- **Thiết kế đối chứng:** mỗi student được huấn luyện hai lần — **có KD** và
  **không KD (baseline)** — với cùng dữ liệu/siêu tham số/seed, qua **5-fold CV**, rồi
  dùng `compute_kd_delta()` để định lượng tác động của KD.
- **Phân tích loại trừ (ablation) chiến lược dữ liệu:** bật/tắt undersampler và có/không
  trộn PAD-UFES-20 để chứng minh từng thành phần thực sự có ích.

### d. Phương pháp thực hiện

- **Dữ liệu:**
  - Tiền xử lý *offline* (chạy một lần): giải mã ảnh → resize 224×224 → lọc chất lượng
    (loại ảnh hỏng, quá nhỏ, không thông tin, trùng lặp) → chuẩn hóa nhãn nhị phân.
  - **Chia dữ liệu chống rò rỉ:** trước tiên tách một tập **test holdout độc lập**
    (patient-disjoint, có phân tầng theo nhãn), sau đó áp dụng
    `StratifiedGroupKFold(5)` (nhóm theo `patient_id`) trên phần còn lại → các
    fold train/val.
  - *Augmentation online* bằng Albumentations (lật, xoay, ColorJitter, CLAHE, blur,
    chuẩn hóa ImageNet); MixUp/CutMix/CutOut **không** dùng (có hại với lớp hiếm / lệch
    miền / phá tính nhất quán của KD).
- **Huấn luyện:** cấu hình bằng **Hydra**; lớp `Trainer` (teacher / baseline) và
  `KDTrainer` (student có KD); chạy trên **cụm UIT Slurm** (GPU L40, chiếm trọn GPU để
  tránh tranh chấp bộ nhớ).
- **Đánh giá:** `compute_metrics` xuất pAUC@TPR≥80, AUC-ROC, **AUPRC** (+ prevalence),
  độ nhạy/đặc hiệu, các điểm vận hành sens@90/95spec; ngưỡng quyết định chọn theo
  **chỉ số Youden's J**; tổng hợp 5-fold theo **mean ± std**.
- **Triển khai di động:** export ONNX/TorchScript, đo **số tham số + dung lượng + độ trễ
  CPU** của các student.
- **Đánh giá xuyên miền & công bằng:** HAM10000 và Fitzpatrick17k chỉ dùng làm **tập
  test ngoài** (không bao giờ huấn luyện) — đo độ tổng quát hóa và khoảng cách hiệu năng
  lớn nhất–nhỏ nhất giữa các nhóm tông da Fitzpatrick.

### e. Kết quả, sản phẩm dự kiến

- **Pipeline KD hoàn chỉnh, tái lập được**: mã nguồn + cấu hình + script chạy cụm.
- **Bộ student nhẹ** đạt pAUC kỳ vọng tiệm cận trần 0.20 và AUPRC cao ở mức prevalence
  ~0.4%, kèm **bảng so sánh KD vs baseline** và đo tác động KD (`compute_kd_delta`).
- **Báo cáo triển khai di động** (params / dung lượng / độ trễ) cho từng student.
- **Báo cáo xuyên miền (HAM10000)** và **báo cáo công bằng (Fitzpatrick17k)**.
- **Khóa luận** + các artifact định lượng (`aggregated.md`, `predictions.csv`,
  `test_metrics.json`).

### f. Tài liệu tham khảo

1. ISIC 2024 Challenge — *Skin Cancer Detection with 3D-TBP* (bộ dữ liệu & metric
   pAUC@TPR≥80%).
2. Tschandl P. et al. (2018). *The HAM10000 dataset.* Scientific Data.
3. Pacheco A. G. C. et al. (2020). *PAD-UFES-20: a skin lesion dataset of smartphone
   images.* Data in Brief.
4. Groh M. et al. (2021). *Evaluating Deep Neural Networks Trained on Clinical Images in
   Dermatology with the Fitzpatrick 17k Dataset.* CVPR Workshops.
5. Hinton G., Vinyals O., Dean J. (2015). *Distilling the Knowledge in a Neural Network.*
6. Lin T.-Y. et al. (2017). *Focal Loss for Dense Object Detection.* (RetinaNet).
7. Tan M., Le Q. (2019). *EfficientNet*; (2021). *EfficientNetV2.*
8. Howard A. et al. (2019). *Searching for MobileNetV3*; Qin D. et al. (2024).
   *MobileNetV4.*
9. Mehta S., Rastegari M. (2022). *MobileViT.*
10. Woo S. et al. (2023). *ConvNeXt V2.*
11. Tu Z. et al. (2022). *MaxViT: Multi-Axis Vision Transformer.*
12. Vasu P. K. A. et al. (2023). *FastViT*; Li Y. et al. (2022). *EfficientFormerV2.*
13. Wightman R. *PyTorch Image Models (`timm`).*

---

## 2. Kế hoạch thực hiện

| Giai đoạn | Công việc | Sản phẩm / cột mốc |
|-----------|-----------|--------------------|
| **GĐ 1** (Tuần 1–2) | Khảo sát tài liệu, chốt bài toán & phạm vi; thu thập ISIC 2024 + PAD-UFES-20 | Đề cương, dữ liệu thô được staging trên cụm |
| **GĐ 2** (Tuần 3–4) | Tiền xử lý offline (resize, lọc chất lượng, dedup) + chia fold patient-disjoint | `data/processed/`, các file split CSV; tập test holdout độc lập |
| **GĐ 3** (Tuần 5–6) | Huấn luyện **teacher** (baseline `efficientnet_b4` + nhóm SOTA) | Checkpoint teacher + `test_metrics.json` per-fold |
| **GĐ 4** (Tuần 7–9) | Huấn luyện **student** có/không KD × 5-fold; tính `compute_kd_delta` | Bảng so sánh KD vs baseline, `aggregated.md` |
| **GĐ 5** (Tuần 10) | **Ablation** chiến lược dữ liệu (undersampler bật/tắt; có/không PAD) | Bằng chứng định lượng từng thành phần |
| **GĐ 6** (Tuần 11) | **Mobile benchmark**: export ONNX/TorchScript, đo params/size/latency | `reports/mobile/*.json` |
| **GĐ 7** (Tuần 12) | **Cross-domain (HAM10000)** + **fairness (Fitzpatrick17k)** | Báo cáo tổng quát hóa & công bằng |
| **GĐ 8** (Tuần 13–14) | Tổng hợp kết quả, viết & hoàn thiện khóa luận | Khóa luận hoàn chỉnh + slide bảo vệ |

> *Ghi chú:* timeline mang tính dự kiến; các giai đoạn huấn luyện (GĐ 3–7) phụ thuộc
> hàng đợi và tài nguyên GPU của cụm UIT Slurm (chia sẻ), có thể chạy gối nhau khi tài
> nguyên cho phép.
