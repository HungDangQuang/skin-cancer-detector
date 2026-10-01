# Hướng dẫn: sinh `config.json` cho app Android

> Đối tượng: người phát hành model vào app. Công cụ: `run/make_app_config.sh` → `scripts/make_app_config.py`.
> Hợp đồng file: `docs/ANDROID_APP_SPEC.md` §3.2 (schema), §3.4 (công thức), §3.5–§3.5a (nguồn ngưỡng).

## 0. Script làm gì, và không làm gì

**Làm:** đọc artifact của một run đã train, sinh `config.json` đúng schema §3.2:
- kích thước ảnh, mean/std lấy từ `config.yaml` của run;
- hai điểm vận hành, ngưỡng **chỉ chọn trên val**, độ nhạy/độ đặc hiệu **đo trên test cùng miền**;
- hằng số hiệu chuẩn prior-shift;
- các dải rủi ro;
- metric 5 fold (từ `aggregated<tag>.json`) và kích thước/GFLOPs (từ `reports/benchmark/*.json`).

**Không làm:** export `.pte`, chép file vào app, quyết định tỉ lệ bệnh. Ba tỉ lệ bệnh là **quyết định của
tác giả** nên script bắt buộc truyền vào và dừng nếu thiếu.

| Điểm vận hành | Ngưỡng chọn trên | Độ nhạy/độ đặc hiệu đo trên |
|---|---|---|
| `phone_sens90` (**mặc định**) | hàng PAD-UFES-20 (ảnh điện thoại) của val, giữ độ nhạy ≥ 90% | hàng PAD của test |
| `global_youden` (tham chiếu) | Youden J trên toàn bộ val | toàn bộ test |

`val_predictions*.csv` không có cột nguồn. Script ghép nó với `<splits_dir>/fold_N/val_split.csv` theo
**thứ tự dòng**, kiểm số dòng và nhãn khớp từng dòng, lệch là dừng.

## 1. Trước khi chạy — 5 quyết định phải có

| # | Quyết định | Tham số | Ghi chú |
|---|---|---|---|
| 1 | Run, fold, checkpoint ship | `RUN_DIR`, `FOLD`, `CKPT_TAG` | Hiện tại: `runs_newsplit_ddi/kd_…__srcsamp`, fold 4 (trung vị val AUPRC), `CKPT_TAG=_auprc` |
| 2 | `.pte` đã qua parity | `PTE`, `EXECUTORCH_VERSION` | Phải là `.pte` export **từ đúng checkpoint đó** và đã PASS `run/check_pte_parity.sh`. Phiên bản lấy từ `.venv-export` (`pip show executorch`); hiện là 1.5.1, đã chạy được trên `executorch-android:1.4.0` |
| 3 | Tỉ lệ bệnh của ảnh camera trong thực tế | `PHONE_PREVALENCE` | Dùng cho PPV/NPV của điểm điện thoại. **Đừng** dùng 0,476 (tỉ lệ của test PAD — quần thể phòng khám chuyển tuyến, đã chọn lọc). Nếu chưa có số đáng tin, chọn một giá trị thận trọng và ghi nguồn |
| 4 | Tỉ lệ bệnh tham chiếu | `GLOBAL_PREVALENCE` | Dùng cho điểm toàn cục và `metrics.prevalence`; test in-domain đo được 0,0045 |
| 5 | Tỉ lệ đích để hiển thị "% rủi ro" | `PI_TARGET` | Prior-shift chỉ đổi con số hiển thị, **không** đổi quyết định (§3.4, I1–I2). Một prior chung làm hiệu chuẩn nhóm ảnh PAD xấu đi ở 17/19 lượt chạy (`reports/2026-09-09_calibration_findings.md`), nên nếu app chỉ nhận ảnh camera thì đặt bằng quyết định 3 |

## 2. Chạy (trên server)

```bash
export TMPDIR="$(pwd)/.tmp"
bash run/make_app_config.sh \
  RUN_DIR=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp \
  FOLD=4 CKPT_TAG=_auprc \
  PTE=exports/executorch_srcsamp/mobilenetv4_conv_medium__srcsamp_auprc_fold4.pte EXECUTORCH_VERSION=1.5.1 \
  MODEL_ID=<id> MODEL_VERSION=<vX.Y.Z> DISPLAY_NAME="<tên hiển thị>" \
  PHONE_PREVALENCE=<quyết định 3> GLOBAL_PREVALENCE=<quyết định 4> PI_TARGET=<quyết định 5> \
  OUT=exports/app_config/<id>/config.json
```

Script in một dòng cho mỗi điểm vận hành (ngưỡng, độ nhạy, độ đặc hiệu, PPV, tập đã đo). Nó từ chối ghi
đè `OUT`; muốn ghi đè thì truyền `FORCE=1`.

## 3. Kiểm trước khi đưa vào app — bắt buộc

| Kiểm | Cách | Kỳ vọng (ứng viên hiện tại, fold 4) |
|---|---|---|
| Ngưỡng điện thoại khớp báo cáo | so `operatingPoints[phone_sens90].threshold` với `reports/2026-10-01_pad_threshold/summary.csv` | 0,570523 |
| Ngưỡng toàn cục khớp val | so với `fold_4/val_metrics_auprc.json` → `threshold` | 0,227249 |
| Độ nhạy/độ đặc hiệu điện thoại | dòng in ra | 0,873 / 0,731 trên 189 ác + 208 lành |
| Bất biến I3 | script tự kiểm, lệch là dừng | — |
| `pteSha256` | trùng sha256 của file `.pte` sẽ chép vào app | — |
| Dải rủi ro tăng dần | script tự kiểm | `low < moderate < elevated < high = 1.0` |

Lượt chạy thử ngày 02/10/2026 ra đúng các giá trị trên (giá trị tỉ lệ bệnh minh hoạ, file ghi vào `.tmp/`,
không phát hành).

## 4. Đưa vào app (phía Android, theo §3.1)

1. `assets/models/<id>/model.pte` (đúng file có `pteSha256`) và `assets/models/<id>/config.json`.
2. Thêm một dòng vào `assets/models/catalog.json`, đặt `activeModelId`.
3. Sinh lại fixture parity cho model mới (MA9) rồi chạy §12.2.

## 5. Giới hạn phải ghi kèm khi phát hành

- **Ngưỡng `phone_sens90` là post-hoc**: mục tiêu 90% chọn sau khi đã xem kết quả test PAD của fold 4.
  Phép kiểm chưa bị đụng là Fitzpatrick17k, và ở đó độ nhạy chỉ còn 0,69 (fold 4: 0,57)
  (`reports/2026-10-01_pad_threshold/README.md`).
- Val đã được dùng để chọn checkpoint, chọn fold và chọn ngưỡng; val PAD nhỏ (351–403 ảnh/fold); không có CI.
- Ảnh camera thật qua app chưa đo: xem `docs/L3_CAMERA_EVAL_GUIDE.md`.
- `metrics` là trung bình 5 fold trên **toàn bộ** test in-domain (ISIC + PAD gộp), không phải số của ảnh
  điện thoại. Số theo miền nằm ở `reports/ci_gates_srcsamp_*.md`.
- Ứng viên hiện tại **KHÔNG ĐẠT YÊU CẦU** theo cổng chấp nhận: B4 (HAM10000) dưới mục tiêu đã chốt 0,81.
  Phát hành để thử nghiệm phải ghi rõ điều này.
