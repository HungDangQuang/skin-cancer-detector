# Chọn ngưỡng cho app nhị phân — các lựa chọn và ý nghĩa (02/10/2026)

Ứng viên ship: `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`,
`best_model_auprc.pth`. Sinh bằng `threshold_options.sh` (bash + awk, chạy trên Mac) → `summary.csv`
(một dòng mỗi fold × quy tắc, số đếm thô).

## Cách app dùng ngưỡng

Model trả một logit → `rawProb = sigmoid(logit)` (một điểm số 0–1, **không** phải "% khả năng ác tính":
model học trên dữ liệu đã lấy mẫu lại 1 ác : 5 lành nên điểm số bị phóng đại). App so `rawProb` với ngưỡng:
`rawProb ≥ ngưỡng` → **"Phát hiện dấu hiệu đáng ngờ — nên đi khám bác sĩ da liễu"**, ngược lại → **"Không thấy
dấu hiệu đáng ngờ — tiếp tục theo dõi"**. App không được in chữ "ác tính/lành tính" (spec P1) và ở chế độ nhị
phân không hiện con số nào (spec §3.4a).

Ngưỡng càng **thấp** → bắt được nhiều ca ác hơn (độ nhạy ↑) nhưng báo nhầm nhiều người lành hơn (độ đặc hiệu ↓).

## Các quy tắc (đều chọn trên **val**, không chọn trên test)

| Quy tắc | Chọn ngưỡng sao cho (trên các ảnh PAD/điện thoại của val, trừ dòng đầu) |
|---|---|
| `global_youden` | Youden J trên **toàn bộ** val (hầu hết là crop ISIC) — ngưỡng hiện có trong `val_metrics_auprc.json` |
| `pad_youden` | Youden J trên ảnh PAD của val (cân bằng độ nhạy và độ đặc hiệu) |
| `pad_sens95` / `pad_sens90` / `pad_sens85` | giữ độ nhạy ≥ 95 / 90 / 85% |
| `pad_spec80` / `pad_spec90` | đạt độ đặc hiệu ≥ 80 / 90% |

## Kết quả — fold 4 (fold được ship)

Test PAD = 189 ảnh ác + 208 ảnh lành (ảnh điện thoại). "Bỏ sót" và "báo nhầm" tính trên 100 ca.

| Quy tắc | Ngưỡng | PAD độ nhạy | PAD độ đặc hiệu | Bỏ sót / 100 ca ác | Báo nhầm / 100 người lành | Fitzpatrick độ nhạy / độ đặc hiệu | ISIC độ nhạy |
|---|---|---|---|---|---|---|---|
| `global_youden` | 0,2272 | 1,000 | 0,005 | 0 | 99,5 | 1,000 / 0,001 | 0,750 |
| `pad_sens95` | 0,5247 | 0,931 | 0,562 | 6,9 | 43,8 | 0,703 / 0,622 | 0,092 |
| **`pad_sens90`** (mặc định hiện tại) | 0,5705 | 0,873 | 0,731 | 12,7 | 26,9 | 0,567 / 0,769 | 0,066 |
| `pad_sens85` | 0,6116 | 0,799 | 0,812 | 20,1 | 18,8 | 0,452 / 0,856 | 0,026 |
| `pad_spec80` | 0,6358 | 0,762 | 0,837 | 23,8 | 16,3 | 0,401 / 0,885 | 0,013 |
| `pad_youden` | 0,6602 | 0,704 | 0,870 | 29,6 | 13,0 | 0,355 / 0,903 | 0,000 |
| `pad_spec90` | 0,7073 | 0,603 | 0,909 | 39,7 | 9,1 | 0,266 / 0,941 | 0,000 |

## Gộp 5 fold (mỗi fold một ngưỡng riêng; cộng số đếm của 5 fold trên cùng các ảnh test)

| Quy tắc | PAD độ nhạy / độ đặc hiệu | Fitzpatrick độ nhạy / độ đặc hiệu |
|---|---|---|
| `global_youden` | 0,998 / 0,016 | 1,000 / 0,002 |
| `pad_sens95` | 0,939 / 0,547 | 0,830 / 0,396 |
| `pad_sens90` | 0,891 / 0,713 | 0,692 / 0,590 |
| `pad_sens85` | 0,804 / 0,800 | 0,562 / 0,725 |
| `pad_spec80` | 0,815 / 0,799 | 0,578 / 0,705 |
| `pad_youden` | 0,753 / 0,834 | 0,504 / 0,775 |
| `pad_spec90` | 0,666 / 0,884 | 0,390 / 0,861 |

## Đọc bảng để quyết định

- **`global_youden` không dùng được cho ảnh điện thoại**: báo nhầm 207/208 người lành. Config đã bỏ nó
  (`SKIP_GLOBAL_OP=1`).
- **App sàng lọc ưu tiên không bỏ sót** → vùng hợp lý là `pad_sens90` (cân đối: bỏ sót ~13, báo nhầm ~27 trên
  100) hoặc `pad_sens95` (bỏ sót ~7 nhưng báo nhầm ~44 trên 100 — gần một nửa người lành bị gửi đi khám).
  Các quy tắc ở nửa dưới bảng giảm báo nhầm nhưng bỏ sót 20–40 ca ác trên 100.
- **Ra ngoài miền thì tụt**: trên Fitzpatrick (ảnh lâm sàng chưa dùng để chọn gì), cùng ngưỡng `pad_sens90` chỉ
  bắt 57% (fold 4) / 69% (gộp 5 fold) ca ác.
- **Ảnh kiểu ISIC (crop 3D-TBP) phần lớn bị bỏ sót** ở mọi ngưỡng chọn trên PAD: độ nhạy ≤ 0,092 ở fold 4,
  gộp 5 fold cao nhất 0,139 (`pad_sens95`), một fold riêng lẻ cao nhất 0,21 — model chấm hai loại ảnh trên
  hai thang khác nhau. Khớp phạm vi app (chỉ ảnh camera), nhưng là giới hạn phải ghi.

## Giới hạn — phải khai khi trích

- Bản đầu của script (02/10, trước khi kiểm chéo) in ngưỡng với 10 chữ số và đặt ngưỡng `pad_spec*` bằng đúng
  điểm của ca lành ở biên, nên vài fold hụt mục tiêu trên val một ca. Đã sửa cho khớp `scripts/make_app_config.py`;
  giờ mọi quy tắc theo độ nhạy/độ đặc hiệu đạt mục tiêu trên val ở cả 5 fold, và `global` + `pad_sens90` trùng
  `../2026-10-01_pad_threshold/summary.csv` ở cả 5 fold. Bảng trên là số sau khi sửa.
- **Post-hoc**: test PAD của fold 4 đã được xem ở 3 điểm vận hành ngày 01/10 (`reports/2026-10-01_pad_threshold/`);
  mọi lựa chọn từ bảng này là chọn sau khi thấy kết quả test. Kể cả `pad_sens90`: mục tiêu 90% được chọn sau khi
  đã chấm 3 điểm trên test PAD của fold 4 (`../2026-10-01_pad_threshold/README.md`, mục "Giới hạn"); thứ được
  đăng ký trước chỉ là phép kiểm 5 fold của nó (`pad_threshold_5fold.sh`, dòng đầu). Các dòng khác là mới.
- Val PAD nhỏ (351–403 ảnh/fold); số của một fold không có CI; val đã được dùng để chọn checkpoint và fold.
- Fitzpatrick: dòng `pad_sens90` đã được xem ngày 01/10; các dòng khác chưa.

Config hiện tại (`exports/app_config/mobilenetv4_srcsamp_auprc_fold4/config.json` trên server; bản sao trong
`materials_for_mobile/models_srcsamp_auprc_fold4/config.json`) dùng `pad_sens90`. Đổi sang mức độ nhạy khác:
chạy lại `run/make_app_config.sh … PHONE_SENS_TARGET=0.95 FORCE=1` (các quy tắc theo độ đặc hiệu / Youden chưa
có trong script).
