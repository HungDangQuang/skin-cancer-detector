# Hướng dẫn: đo L3 — từ ảnh camera đến tensor 224 (02/10/2026)

> Đối tượng: người làm app Android (thu ảnh) và người chạy pipeline ML (chấm điểm).
> Bối cảnh: `docs/MOBILE_EVAL_PLAN.md` §1 (ba tầng parity) và §1.2 (vì sao L3 chỉ đo được ở dạng proxy).

## 0. Đã đo gì, còn thiếu gì

| Tầng | Câu hỏi | Trạng thái (ứng viên `__srcsamp` fold 4) |
|---|---|---|
| L1: hạ graph | `.pte` có tính đúng như PyTorch trên cùng tensor đã chuẩn hoá? | ✅ host parity 6,311e-06; điện thoại 2,384e-06 (100 ảnh) |
| L2: giải mã + chuẩn hoá | app tự đọc JPEG 224×224 rồi tự chuẩn hoá có ra đúng tensor đó? | ✅ Pixel 6a (giải mã bằng `BitmapFactory`): 70.883 ảnh, mọi metric Δ = 0 (`reports/2026-10-01_pixel6a_srcsamp_vs_mobile.md`) |
| **L3: ảnh camera** | ảnh độ phân giải gốc → app cắt và thu về 224 → có ra input giống lúc huấn luyện? Model có còn đúng trên ảnh camera thật? | ❌ **chưa đo** |

L3 gồm ba nguồn sai lệch khác nhau, nên đo bằng ba tầng **T1 → T2 → T3**, mỗi tầng trả lời một câu riêng.
Đừng gộp tên: kết quả T1 là "độ nhạy với phép lấy mẫu lại", **không** phải "chạy tốt trên camera".

## 1. T1 — độ nhạy với phép lấy mẫu lại (phía ML, làm được ngay)

**Câu hỏi:** cùng một ảnh gốc, thu về 224 bằng thuật toán của app thay cho LANCZOS (thuật toán lúc huấn
luyện) thì logit và metric đổi bao nhiêu?

- **Dữ liệu:** ảnh ISIC 2024 ở độ phân giải gốc trong `train-image.hdf5`. Trên Mac nằm ở
  `data/raw/isic2024/train-image.hdf5`; **đã chép lên server 02/10/2026** tại `data/l3/isic2024_train-image.hdf5`
  (sha256 khớp) — cố ý **không** đặt ở `data/raw/isic2024/`, để `prepare` (có thể xoá ảnh processed) vẫn không chạy được. Chỉ lấy các ảnh thuộc **test v2**
  (khoá HDF5 là mã ISIC; khớp với cột `image_id` của `data/splits/isic2024/test_split.csv` để có nhãn, rồi
  ánh xạ sang `sample_id` của `data/mobile_eval_bundle/manifest.csv`, vì `scripts/eval_from_logits.py` bỏ các dòng
  không có trong manifest và chỉ cảnh báo).
- **Hạn chế đã biết:** 99,3% test là crop ISIC, nhiều ảnh nhỏ hơn 224 nên bị **phóng lên** chứ không thu nhỏ
  (`MOBILE_EVAL_PLAN.md` §1.2). T1 chủ yếu đo phép phóng. Ảnh PAD gốc đã mất, nên không đo được phép thu
  nhỏ ảnh điện thoại.
- **Cách làm:** với mỗi ảnh, tạo các biến thể 224×224 bằng LANCZOS (tham chiếu), bilinear (`Bitmap.createScaledBitmap`) và area (OpenCV `INTER_AREA`) (hai cách   app có thể dùng, theo `ANDROID_APP_SPEC.md` §4.3), rồi chạy cùng checkpoint, CPU, batch 1.
- **Đầu ra:** mỗi biến thể một file `sample_id,logit,error`. Chấm bằng `run/eval_from_logits.sh` với
  `VALPRED=…/fold_4/val_predictions_auprc.csv`, rồi `COMPARE=` từng biến thể với LANCZOS.
- **Tiêu chí — ĐỀ XUẤT, tác giả chốt ở bước 1 của §4 trước khi chạy:** |ΔAUPRC| < 0,0053, tức sàn nhiễu chạy
  lại của dự án. Báo cáo kèm
  max và p99 của |Δlogit|, và số quyết định bị lật ở cả hai điểm vận hành.
- **Việc code còn thiếu:** một script đọc HDF5 → biến thể resize → logit. Chưa có; viết qua skill `code-change`.

## 2. T2 — chụp lại ảnh đã biết nhãn qua app thật (Android + người chụp)

**Câu hỏi:** đường đi đầy đủ của app (CameraX → cắt → thu nhỏ → chuẩn hoá → model) cho ra logit lệch bao
nhiêu so với đường tham chiếu, trên ảnh đã biết nhãn?

T2 **không cần tập kiểm mới**, vì nó đo **độ đồng thuận** giữa hai đường đi trên cùng một ảnh. Nhãn chỉ
dùng thêm cho metric.

- **Ảnh:** một tập con cố định, chốt trước, lấy từ bundle hiện có (`data/mobile_eval_bundle`), ví dụ cả 397
  ảnh PAD của test, cộng một mẫu ngẫu nhiên có seed của ISIC và Fitzpatrick. Ghi danh sách `sample_id`
  vào một file trước khi chụp.
- **Hiển thị:** in ảnh, hoặc mở toàn màn hình trên một màn hình cố định. Chụp bằng app ở chế độ đánh giá,
  tức màn hình nhà phát triển (`ANDROID_APP_SPEC.md` §7.14). Ghi lại điều kiện: thiết bị, khoảng cách, ánh
  sáng, màn hình hay bản in.
- **Nhiễu do chính cách làm:** chụp lại từ màn hình hay bản in sẽ thêm moiré, độ chói và gam màu của
  màn hình hoặc máy in. T2 đo **cả đường đi của app cộng nhiễu tái chụp**, nên kết quả là **cận trên** của
  sai lệch L3. Phải ghi rõ điều này khi báo cáo.
- **Đầu ra từ app:** `sample_id,logit,error`, đúng định dạng của harness. Mỗi điều kiện chụp một file, kèm
  file mô tả điều kiện.
- **Chấm (phía ML):**
  - `run/eval_from_logits.sh` một lần cho mỗi điểm vận hành, truyền ngưỡng tường minh bằng `THRESH=<threshold>`
    lấy từ `config.json` (`VALPRED=` chỉ cho ngưỡng Youden, không ra `phone_sens90`);
  - so với logit tham chiếu của đúng các `sample_id` đó (file ref đầy đủ của model, ví dụ `~/Documents/materials_for_mobile/models/refs/ref_mobilenetv4_srcsamp_auprc_fold4_full.csv`; nằm ngoài repo): phân bố |Δlogit|,
    tỉ lệ quyết định bị lật ở từng điểm vận hành;
  - ΔAUC và ΔAUPRC ghép cặp trên tập con có nhãn (dựng cây như `.tmp/archived_root_drivers_20261002/.tmp_pixel_cmp.sh` (local, untracked), rồi `run/bootstrap_ci.sh PAIR=…`).
- **Tiêu chí:** chưa có mốc từ tài liệu. **Tác giả phải chốt trước khi chụp**, ví dụ tỉ lệ lật quyết định
  tối đa ở `phone_sens90`. Ví dụ này chỉ là gợi ý, không có nguồn.

## 3. T3 — thử nghiệm thực địa (ngoài phạm vi kỹ thuật)

Bằng chứng duy nhất cho câu "model đúng trên ảnh camera thật của bệnh nhân" là ảnh chụp bằng app trên bệnh
nhân thật, có kết quả sinh thiết. Việc này cần phê duyệt đạo đức, sự đồng ý của bệnh nhân và hợp tác lâm sàng,
nên **không làm được bằng code**. Luận văn chỉ nên nêu T3 là hướng mở và nói rõ T1/T2 không thay thế được nó.

## 4. Thứ tự đề xuất và ai làm gì

| Bước | Việc | Ai | Phụ thuộc |
|---|---|---|---|
| 1 | Chốt tiêu chí T1 và T2, danh sách `sample_id` của T2 | tác giả | — |
| 2 | ~~Chép HDF5 lên server~~ (xong 02/10); viết script T1 (`code-change`); chạy T1 | ML | bước 1 |
| 3 | Thêm chế độ "chụp để đánh giá" vào màn hình nhà phát triển, xuất `sample_id,logit,error` | Android | `config.json` từ `docs/APP_CONFIG_GUIDE.md` |
| 4 | Chụp T2 theo danh sách, ghi điều kiện | người chụp | bước 1, 3 |
| 5 | Chấm T2, viết báo cáo | ML | bước 4 |

## 5. Điều kiện dừng

Báo lại, không tự xoay xở, nếu:
- T1 cho |ΔAUPRC| ≥ 0,0053 với thuật toán resize mà app định dùng;
- T2 có hơn 0,1% ảnh lỗi;
- logit của cùng một ảnh chụp lặp lại không ổn định trong cùng một điều kiện;
- có ý định chỉnh ngưỡng hay model để số khớp.
