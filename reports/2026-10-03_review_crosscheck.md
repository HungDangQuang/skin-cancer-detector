# Đối chiếu review ngoài 03/10 với code

> Review: `docs/REVIEW_DANH_GIA_2026-10-03.md` (reviewer chỉ đọc `docs/PROJECT_BRIEF_FOR_REVIEW.md`).
> File này trả lời từng ô "Đối chiếu trong code" ở mục 1.1–1.12 của review.
> Số dòng của `acceptance-gates.md` trong file này tính theo commit `3815e7c` (trước khi hợp đồng đổi sang khung 3 trụ
> cùng ngày); bản hiện hành: luật AND cũ ở `:228`, ghi chú teacher không có `_auprc` ở `:217`, CI 5 fold ở `:125`.
> **Kiểm chéo:** một lượt FACTS + PATCH ngày 03/10, đã sửa 1 lỗi SAI (mục 1.3) và 2 trích dẫn lệch.
> **Viết sau lượt kiểm, chưa ai kiểm lại:** mục 1.9 (config app thật, `Decision.kt`, đính chính `pad_spec80`), phần 1.10, khối "Ý nghĩa với kế hoạch".

## Tóm tắt

Reviewer đúng ở bốn điểm đã có code xác nhận:
- mốc B2 0,81 là mức bác sĩ đọc ảnh dermoscopy, không cùng loại với ảnh điện thoại (1.1);
- C2 so student với một teacher train theo công thức khác (1.5);
- checkpoint `_auprc` và fold ship được chọn theo AUPRC val gộp ISIC + PAD (1.12);
- B1 pAUC và B3 có thể đổi nhãn chỉ vì đổi seed bootstrap (1.3, mới là ước tính).

Reviewer sai ở hai chỗ:
- 1.9 so hai điểm vận hành khác nhau;
- 1.11 giả định dự án dùng `crop_pct` + center crop của timm.

## 1.1 Mốc B2: reviewer đúng

- **Nguồn Cochrane** (Dinnes 2018, PMC6517096; đọc qua web 03/10, agent kiểm chéo không có web nên chưa kiểm lại):
  - Đánh giá trên ảnh, độ đặc hiệu cố định 80%: đọc dermoscopy đạt 81%, nhìn ảnh lâm sàng đạt 47%. Hai số cùng một review, cùng điểm vận hành, chỉ tính melanoma.
  - Khám trực tiếp: nhìn bằng mắt đạt 76%, dermoscopy kèm nhìn đạt 92%.
- **Nhãn PAD:** BCC/SCC/MEL → 1, ACK/NEV/SEK → 0 (`scripts/rebuild_splits.py:86`, `src/data/preprocessing.py:263-264`).
- ⚠️ B2 = 0,81 **đã chốt**. Đổi xuống 0,47 hay 0,76 lúc này là post-hoc (`acceptance-gates.md` §4 #13), không được dùng để ghi "đạt".

## 1.2 Độ rộng CI

- Ngưỡng spec80 được tính lại trong mỗi lần resample (`scripts/bootstrap_ci.py:165-166`), nên CI không bị hẹp giả.
- Không nội suy: lấy độ nhạy cao nhất trong các ngưỡng có độ đặc hiệu ≥ 0,80 (`src/evaluation/metrics.py:96-99`).
- Bootstrap không phân tầng theo lớp. Khi tách theo nguồn ảnh thì phân tầng theo nguồn: giữ nguyên 397 dòng PAD, nhưng số ca dương trong đó thay đổi (`bootstrap_ci.py:268-272, 532`).
- Bảng cỡ mẫu của reviewer tính lại theo đúng giả định của họ cho ~11.100 / 2.660 / 600 / 236 / 115, khớp.

## 1.3 Phán quyết sát mép

- B = 2.000, seed 42 (`bootstrap_ci.py:340-341`), CI percentile, không dùng BCa (`:306-311`).
- Sai số Monte Carlo của cận dưới (ước tính: σ = độ rộng CI / 3,92, nhân 0,06):

| Cổng | Sai số MC | Khoảng cách tới mốc | Đổi seed có thể đổi nhãn? |
|---|---|---|---|
| B1 pAUC | ~0,0005 | 0,0002 | có |
| B3 | ~0,0007 | 0,0001 | có |
| B1 AUC | ~0,0006 | 0,0007 | ít khả năng hơn |

- Chưa đo. Việc kiểm là R6 trong `docs/PROGRESS.md`.

## 1.4 Luật AND tám cổng

- `acceptance-gates.md:155` gộp các cổng bằng AND phẳng, không có cổng chính/phụ.
- "Power chung = tích power từng cổng" chỉ đúng khi các cổng độc lập. Ở đây các cổng tương quan dương nên power chung cao hơn tích, nhưng vẫn thấp. Đây là lập luận, chưa đo.

## 1.5 C2: nghi ngờ của reviewer đúng

- **So config fold_4:**
  - Teacher không có `sampler_stratify_by: source` và chỉ có checkpoint theo val pAUC.
  - Augmentation giống hệt nhau (light); teacher có DDI.
  - Bất đối xứng này đã ghi sẵn ở `acceptance-gates.md:143` (teacher không có bản `_auprc`, brief cấm train lại teacher), nhưng brief gửi reviewer không nhắc.
- **AUPRC trên PAD:**
  - Student KD **không** dùng sampler theo nguồn: 0,7997.
  - Teacher: 0,7966 (`reports/ci_ddi_indomain.md:67, :87`).
  - Đây là CI từng run, chưa ghép cặp (R7). Nó gợi ý phần lớn khoảng "vượt teacher" +0,0619 trên PAD đến từ sampler và cách chọn checkpoint.
  - Lưu ý: hiệu ứng sampler +0,0563 đo trên checkpoint pAUC ở cả hai phía.
- **Teacher trong KD:** `.eval()` và `requires_grad=False` (`src/training/kd_trainer.py:49-51`), chạy trong `no_grad` (`:233`), nhận đúng ảnh đã augment mà student nhận (`:223-237`).

## 1.6 Loss KD và C1

- Hệ số T² có nhân. Loss dùng `binary_cross_entropy_with_logits(s/T, sigmoid(t/T))`, target nằm trong `no_grad` (`src/training/distillation.py:80-84`).
- Config baseline và KD `__srcsamp` chỉ khác `use_kd`, khối `distillation` và `cache_val_teacher_logits`. Vì vậy C1 là so sánh công bằng.

## 1.7 C4a theo từng tông da

- Fitzpatrick headline: tối 411 ảnh / 208 ác tính; sáng 2.310 / 1.195; trung bình 1.599 / 757.
- Gộp nhóm I–II / III–IV / V–VI (`configs/data/fitzpatrick17k.yaml:41-44`). Ảnh có tông da −1 bị loại.

## 1.8 pAUC

- Cài theo cách của cuộc thi: lật nhãn và điểm, tính pAUC McClish bằng sklearn, rồi đảo phép chuẩn hoá (`src/evaluation/metrics.py:11-45`).
- Chưa chạy song song với hàm chấm chính thức (R8).

## 1.9 Ngưỡng app

- Ngưỡng 0,5705 chọn trên 373 ảnh PAD của val fold 4 (198 ác / 175 lành; `reports/2026-10-02_threshold_options/summary.csv:33`).
- Val fold 4 và test có 0 bệnh nhân chung.
- **Config app thật:** `phone_sens90` = 0,570523, `displayMode: binary`. App quyết định `rawProb ≥ ngưỡng` với `rawProb = sigmoid(logit)` (`SkinDetector` develop, `core/ml/.../decision/Decision.kt:17-20`). Logit tương ứng ≈ 0,284.
- **Reviewer so lệch:** họ đặt sens@spec80 (độ đặc hiệu 0,80) cạnh ngưỡng `pad_sens90` (độ đặc hiệu 0,731). Điểm vận hành tương đương là ngưỡng đóng băng `pad_spec80`, chọn trên val:

| Phạm vi | Độ nhạy | Độ đặc hiệu |
|---|---|---|
| fold 4 (model ship) | 0,762 | 0,837 |
| cộng số đếm 5 fold | 0,815 | 0,799 |

  So với sens@spec80 = 0,818 (trung bình 5 fold, ngưỡng tính lại trên test): model ship thấp hơn, còn tính trên cả 5 fold thì gần như bằng.

## 1.10 Những lần đã mở tập test (danh sách một phần)

- **Splits v1:** cả ma trận 140 fold-run.
- **Splits v2:** arm `light`, `domain` (24/09), `ddi` (26/09), `srcsamp` (01/10).
- **01/10:** mốc các cổng được ghi nhận sau khi đã thấy mọi kết quả B/C của P0.
- **01–02/10:** ngưỡng app chọn sau khi xem 3 điểm vận hành trên test PAD fold 4.
- **02/10:** B4 chuyển sang chỉ báo cáo.
- **Vòng 2:** hai cặp P1/P2 được đề xuất có tham khảo số v1.

Danh sách đầy đủ là việc R10.

## 1.11 Pipeline camera (L3)

- **Phía Python (lúc train):**
  - Resize offline bằng PIL LANCZOS về 224×224, kéo méo không giữ tỉ lệ, không center crop (`src/data/preprocessing.py:158` cho ISIC, `:306` cho PAD).
  - Sau đó chia 255, chuẩn hoá mean/std ImageNet, thứ tự kênh RGB.
- **Spec app:** `resize: "squash"`, RGB, CHW (`docs/ANDROID_APP_SPEC.md:336-346`); Coil decode có xử lý EXIF và không gian màu (`:62, :98`).
- **Đã đo:** decode JPEG trên Pixel cho logit trùng bit với host 100/100 ảnh (`mobile/testing_result/README.md:34-36`). Lần đo đó dùng checkpoint khác, không qua bước resize.
- **Chưa đo:** bilinear (mặc định của app) so với LANCZOS (lúc train) — việc S11 và U5.

## 1.12 Chọn checkpoint lẫn yếu tố nguồn ảnh: reviewer đúng

- `best_model_auprc.pth` chọn theo AUPRC trên toàn bộ val (`src/training/kd_trainer.py:335`). Ở val fold 4, 198/267 ca dương (74%) nằm trong 373 dòng PAD.
- Fold ship chọn theo trung vị AUPRC val gộp (`reports/2026-10-01_srcsamp_item2_3.md:111-112`). Chỉ bước chọn *cặp* ở vòng 2 mới dùng AUPRC trên ảnh PAD của val.
- **Chọn lại theo PAD:**
  - Chọn lại *fold*: làm offline được (R9).
  - Chọn lại *checkpoint*: phải sửa code rồi train lại (S9), vì không lưu checkpoint từng epoch.

## Điểm brief không nêu

Số của các cổng B/C là CI của **trung bình 5 fold**, không phải của checkpoint fold 4 sẽ ship. Đây là thiết kế đã ghi ở `acceptance-gates.md:93`.

## Ý nghĩa với kế hoạch

Các việc phát sinh đã ghi vào `docs/PROGRESS.md`: U10, R6–R10, S9–S11.
