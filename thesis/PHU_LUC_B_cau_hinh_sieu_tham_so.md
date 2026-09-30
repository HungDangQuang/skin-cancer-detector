# PHỤ LỤC B — CẤU HÌNH SIÊU THAM SỐ ĐẦY ĐỦ

*Tài liệu đi kèm luận văn thạc sĩ **"Phát hiện ung thư da trên thiết bị biên sử dụng mô hình
học sâu kết hợp chưng cất tri thức"** (Đặng Quang Hưng, `thesis/LUAN_VAN.md`). Đây là toàn bộ
giá trị siêu tham số dùng cho mọi lượt huấn luyện, đánh giá và triển khai của luận văn. Hai
nhánh so sánh trong mỗi cặp chưng cất dùng chung tất cả các giá trị dưới đây và chỉ khác nhau
ở hàm mất mát — điều kiện của phép so sánh ceteris paribus mô tả ở Mục 3.7 của luận văn.*

---

## B.1 Dữ liệu và chia dữ liệu

| Tham số | Giá trị |
|---|---|
| Kích thước ảnh | 224 × 224 |
| Chiến lược chia | `stratified_group_kfold` |
| Số fold | 5 |
| Cột nhóm | `patient_id` (PAD gắn tiền tố `pad_`) |
| Tỉ lệ test giữ lại | 1/6 ≈ 17% |
| Seed ngẫu nhiên | 42 |
| Bộ lấy mẫu | `DynamicUndersampledSampler`, bật |
| Tỉ lệ undersampling | 5 (1 ác tính : 5 lành tính) |
| Lọc nguồn train | `null` (dùng cả ISIC + PAD) — đặt `[isic2024]` cho nhánh ablation |

## B.2 Kiến trúc

| Tham số | Giá trị |
|---|---|
| Nguồn backbone | `timm ≥ 1.0`, trọng số tiền huấn luyện ImageNet |
| Đầu phân loại | GAP → Dropout → Linear(in_features, 1) |
| Số chiều đầu vào của head | Suy ra bằng một lần chạy thử qua backbone |
| Đầu ra | 1 logit thô; `sigmoid` chỉ tại suy luận |
| `drop_path_rate` | 0,0 (tắt — Mục 4.2 cho thấy không cần) |

## B.3 Tối ưu hoá

| Tham số | Teacher | Student (KD và baseline) |
|---|---|---|
| Bộ tối ưu | AdamW | AdamW |
| Learning rate — backbone | 1e-4 | 1e-4 |
| Learning rate — head | 1e-3 | 1e-3 |
| Weight decay | 1e-4 | 1e-4 |
| Betas | (0,9 ; 0,999) | (0,9 ; 0,999) |
| Scheduler | Cosine annealing, `eta_min` = 1e-6 | như teacher |
| Warmup | 3 epoch | 3 epoch |
| Số epoch tối đa | 50 | 50 |
| Batch size | 32 | 64 |
| Gradient clipping | 1,0 | 1,0 |
| Seed | 42 | 42 |
| cuDNN deterministic | `true` (đặt `false` cho `maxvit_base` khi gặp lỗi backward) | `true` |

## B.4 Hàm mất mát

| Tham số | Giá trị |
|---|---|
| Focal Loss — γ | 2,0 |
| Focal Loss — α | 0,25 |
| KD — nhiệt độ T | 4,0 |
| KD — α (trọng số nhãn cứng) | 0,3 |
| KD — loại hàm mất mát mềm | BCE có hệ số $T^2$ (dạng Hinton gốc) |
| Teacher trong KD | Đóng băng hoàn toàn |

## B.5 Callback

| Tham số | Giá trị |
|---|---|
| Dừng sớm — theo dõi | `val_loss` (mode: min) |
| Dừng sớm — patience | 10 |
| Lưu checkpoint — theo dõi | `val_pauc_at_tpr80` (mode: max) |
| Lưu checkpoint cuối | có |

## B.6 Đánh giá và thống kê

| Tham số | Giá trị |
|---|---|
| Ngưỡng pAUC | TPR ≥ 0,80 (tương đương FPR ≤ 0,20 sau khi đảo) |
| Chọn ngưỡng nhị phân | Youden's J |
| Bootstrap — số lần lặp | 2.000 |
| Bootstrap — seed | 42 |
| Bootstrap — đơn vị lấy mẫu lại | **hàng của tập test** (không phải fold) |
| Ghép cặp | Bắt buộc — hai nhánh dùng chung bộ chỉ số mỗi lần lặp |

## B.7 Triển khai

| Tham số | Giá trị |
|---|---|
| Định dạng export | ExecuTorch `.pte`, FP32 |
| Backend ưu tiên | XNNPACK; chuyển `none` (portable) nếu **trượt kiểm tra tương đương** |
| Ngưỡng kiểm tra tương đương | sai lệch logit lớn nhất < 1e-3 |
| Số mẫu kiểm tương đương | 100 |
| Fold được export | Fold có hành vi **trung vị** (không bao giờ fold tốt nhất) |
| Thiết bị benchmark | Google Pixel 6a (Tensor G1) |
| Số luồng đo | 1 và 4 |
| Vòng khởi động / vòng đo | 30 / 200 |
| Điều kiện | Không cắm sạc, chế độ máy bay, độ sáng cố định, thứ tự xáo trộn có seed |
| Runtime đã kiểm chứng | `executorch-android` 1.3.1 và 1.4.0 (kết quả trùng khớp) |
