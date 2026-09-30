# Kế hoạch: đánh giá CHẤT LƯỢNG trên điện thoại (on-device evaluation)

> Tài liệu này trả lời: *"mô hình chạy trên điện thoại có còn đúng bằng mô hình chạy trên server
> không — đo bằng pAUC/AUPRC, không phải bằng ms?"*
>
> Viết 2026-09-26. Phân biệt rõ với `docs/MOBILE_BENCHMARK_TASK.md` (lượt 08/2026) — lượt đó đo
> **tốc độ**, **bộ nhớ** (peak PSS 208–257 MiB, `BENCHMARK_RESULTS.md` §6) và **parity số học trên
> 100 ảnh**, và brief của nó nói thẳng *"Not measuring accuracy… Do not compute or report accuracy,
> AUC, or any quality metric"* ([MOBILE_BENCHMARK_TASK.md §1](MOBILE_BENCHMARK_TASK.md)). Chỗ trống
> mà luận văn đang có là thật.
>
> **Trạng thái: chưa bắt đầu, và hiện đang BỊ CHẶN** — xem §0.

---

## 0. ⛔ Điều kiện chặn: không còn checkpoint student nào trên splits sạch

**Cả 16 `.pte` hiện có đều export từ checkpoint của ma trận 140 fold CŨ**, tức huấn luyện trên
`data/splits/` **đã rò rỉ bệnh nhân**. Bằng chứng: `run/export_all_students.sh:123` hard-wire
`ckpt="experiments/runs/${run}/fold_${fold}/checkpoints/best_model.pth"`, và
`reports/mobile_benchmark/EXPORT_MANIFEST.md:17-32` liệt kê cả 16 checkpoint nguồn — tất cả thuộc
`experiments/runs/`.

**Và checkpoint của các arm sạch đã bị xoá.** Bản ghi dọn đĩa 26/09
(memory `project_vast_servers`, bảng dòng 248–258) ghi rõ: trong 90 file `best_model.pth` bị xoá
có *"3 arm `runs_newsplit_*` **student/baseline**"*; phần **CÒN GIỮ** chỉ là *"30 checkpoint
teacher"*, trong đó `runs_newsplit_{light,domain,ddi}/teacher/efficientnetv2_m`. Mac cũng có **0**
file `.pth` trong cả ba cây đó.

⇒ **Mô hình đem triển khai (student KD) hiện không tồn tại ở dạng checkpoint trên splits sạch, ở
bất cứ đâu.** Đây không phải nhánh dự phòng mà là tình trạng thực.

⚠️ **Và không có đường tắt bằng cách dùng `.pte` v1**: phân hoạch v1 **không tái tạo được**
(memory `project_splits_lost_incident`: *"population khớp TUYỆT ĐỐI (372.242) nhưng PHÂN HOẠCH thì
không"*), nên không có tập test hợp lệ cho chúng — chấm `.pte` v1 lên 59.093 hàng v2 là cho mô hình
gặp lại bệnh nhân nó đã học.

### Ba đường đi, phải chọn một trước khi bỏ công vào §2–§4

| | Đường | Chi phí | Nói được gì |
|---|---|---|---|
| **A** (khuyến nghị) | **Train lại 1 fold student KD trên splits v2** rồi export. Arm DDI 15 fold-run chạy 25/09 12:03 → 26/09 04:23 ≈ **16 h wall-clock cho cả 15 fold** ⇒ một fold student ở bậc **một giờ** (ước bậc độ lớn, không phải số đo một fold) | 1 fold GPU + export | Trả lời đúng câu của luận văn, trên mô hình đúng là mô hình sẽ ship |
| **B** | Dùng **teacher `efficientnetv2_m` của arm sạch** (checkpoint còn) cho nghiên cứu *tương đương số học* | 0 GPU | Chứng minh được `.pte` + tiền xử lý app không làm mất chất lượng — nhưng trên mô hình **không** đem ship (453 MB). Là một mục phương pháp, không phải mục triển khai |
| **C** | Dùng `.pte` v1 và nói rõ | 0 GPU | **Không khuyến nghị**: không có tập test hợp lệ (xem cảnh báo trên) |

**Bước 0.x:**

| ☐ | Bước | Ghi chú |
|:--:|---|---|
| ☐ | 0.1 Xác nhận trên box rằng `runs_newsplit_*/{kd,baseline}` thật sự không còn `best_model.pth` | Tôi chỉ đọc được **bản ghi** dọn đĩa trên Mac, không ssh được vào box training (`~/.ssh/config` không có alias `islab-server2`; alias `vastnew` hiện trỏ tới một instance **không có project**). Xác nhận cuối phải làm trên box |
| ☐ | 0.2 Chọn đường A / B / C | Quyết định của bạn |
| ☐ | 0.3 Dựng lại `.venv-export` trên box | `bash run/setup_export_env.sh` — bản cũ đã bị xoá đợt 26/09 (5,20 GB) |
| ☐ | 0.4 Export + **cổng parity L1** | ⚠️ **Truyền `OUT=` tường minh.** `run/export_executorch.sh:46` mặc định ghi `exports/executorch/${MODEL}.pte`, mà file đó **đã tồn tại** (bản v1) ⇒ sẽ ghi đè. Đường `run/export_all_students.sh` thì tên tag (`<model>__<teacher>_fold<N>.pte`) **trùng** bản v1 và `SKIP_EXISTING=1` sẽ **bỏ qua trong im lặng**. Đặt cây riêng, ví dụ `exports/executorch_v2/` |

`CLAUDE.md`: export thành công **không** chứng minh gì cho tới khi parity pass — XNNPACK từng lower
sai `efficientformerv2_s2` ra logit −2,2e10 mà không báo lỗi.

---

## 1. Ba tầng parity — tầng nào chưa ai đo, và tầng nào đo được

| Tầng | Câu hỏi | Trạng thái |
|---|---|---|
| **L1 — hạ graph** | `.pte` có tính đúng hàm PyTorch tính, khi hai bên nhận **cùng tensor đã chuẩn hoá**? | ✅ **XONG.** 16/16 PASS trên PC và 16/16 trên chính Pixel 6a. Dải PC **3,92e-06 … 5,57e-04**; device ca xấu nhất **6,676e-04** so với ngưỡng 1e-3 — tức chỉ cách ngưỡng ~1,5× ở `efficientformerv2_s2__nokd_fold2`, không phải "~1e-5 thoải mái" (`EXPORT_MANIFEST.md` caveat 3) |
| **L2 — giải mã + chuẩn hoá** | App tự đọc JPEG 224×224 rồi tự chuẩn hoá thì có ra **đúng tensor đó**? | ❌ **CHƯA AI ĐO.** Bundle 08/2026 có sẵn `images/` cho việc này nhưng brief để là *"Step D — preprocessing check (optional, only if asked)"* (`MOBILE_BENCHMARK_TASK.md:323`) và báo cáo trả về không có mục nào. `reports/2026-08-23_external_evaluation.md:532` cũng liệt kê "preprocessing parity (layer 2)" là việc chưa làm |
| **L3 — lấy mẫu lại ảnh** | Ảnh ở **độ phân giải gốc** → app thu nhỏ/phóng to về 224 → có ra pixel giống lúc huấn luyện? | ❌ **CHƯA ĐO, và chỉ đo được ở dạng proxy** — xem §1.2 |

### 1.1 Vì sao L2 hẹp

`data/processed/**.jpg` **đã là 224×224 sẵn trên đĩa** — `prepare` lấy mẫu lại bằng
`Image.LANCZOS` rồi lưu JPEG ([src/data/preprocessing.py:53](../src/data/preprocessing.py),
`:158`, `:306`, `:454`). Cho nên lúc đánh giá, `A.Resize(224,224)`
([src/data/transforms.py:86](../src/data/transforms.py)) là một **no-op**, và khối `val` của
`configs/augmentation/light.yaml` chỉ có `Normalize` ⇒ toàn bộ đường val/test rút về:

```
x = jpeg_decode(file) / 255.0                  # RGB, HWC, float
x = (x - [0.485,0.456,0.406]) / [0.229,0.224,0.225]
x = transpose(x, CHW)                          # -> (3,224,224) float32
```

⇒ L2 chỉ còn rủi ro ở **bộ giải mã JPEG** (libjpeg-turbo trên Android vs PIL ở phía ML) và **thứ
tự kênh**. Hẹp, đo một lần là xong. *Mức lệch cụ thể là ẩn số — chưa ai đo, nên đừng viết trước
một con số kỳ vọng vào luận văn.*

### 1.2 Vì sao L3 chỉ đo được ở dạng proxy — đính chính một lập luận sai

Bản đầu của tài liệu này lập luận: *"app thu nhỏ ảnh camera 3000×2000 về 224 bằng bilinear sẽ
aliasing, còn LANCZOS lọc trước"*. Lập luận đó **chỉ đúng cho một phần rất nhỏ của tập test**:

- **ISIC 2024 là ảnh *crop* tổn thương**, kích thước gốc thay đổi và **nhiều ảnh nhỏ hơn 224 nên bị
  PHÓNG LÊN**, không phải thu nhỏ — `src/data/preprocessing.py:152-155` có comment
  *"Native crop too small to carry detail once **upscaled** to image_size"*, `docs/PREPROCESSING.md:38`
  *"a tiny crop upscaled to 224 is pure blur"*, và luận văn `:1170` *"Một ảnh gốc 20×20 nếu được
  phóng lên 224×224…"*. ISIC là **58.696 / 59.093 = 99,3%** tập test.
- Phần thật sự bị thu nhỏ là **397 dòng PAD-UFES-20** — và `data/raw/pad_ufes_20/` **đã mất khỏi
  box** (`CLAUDE.md` mục "Data integrity").

⇒ **Không có bộ dữ liệu nào trong tay đại diện cho "ảnh camera ở độ phân giải đầy đủ" mà lại hợp lệ
để chấm điểm**: PAD raw đã mất; DDI có ảnh lâm sàng ở độ phân giải gốc (`data/raw/DDI`, 226 MB trên
Mac) nhưng DDI giờ là **nguồn huấn luyện** nên chấm trên nó là vô hiệu.

**Việc L3 vẫn làm được, ở dạng proxy:** lấy ảnh ISIC ở độ phân giải gốc từ
`data/raw/isic2024/train-image.hdf5` (1,3 GB, **có trên Mac**) và đo *"đổi thuật toán lấy mẫu lại
thì logit lệch bao nhiêu"* — LANCZOS (chuẩn huấn luyện) vs bilinear (Android) vs nearest. Đó là một
câu hỏi hợp lệ và đo được. Nhưng phải gọi đúng tên nó: **độ nhạy với phép lấy mẫu lại**, không phải
"mô phỏng camera".

⚠️ Và đừng dùng câu *"khung ảnh là nguyên nhân sụp miền"* để biện minh cho L3 — nguồn nói ngược:
`docs/PREPROCESSING.md:254-258` viết *"Framing mismatch is a genuine, addressable — and **minor** —
component of the cross-domain drop. **The bulk is image content plus the missing benign classes**"*.
Con số ~6% là đúng, nhưng nó là **một phần nhỏ**, không phải nguyên nhân chính.

---

## 2. Ngân sách — khả thi, trừ một kiến trúc

Từ `reports/ondevice_latency.csv` (cột `sustained_ms` = đã tính điều tiết nhiệt, 4 luồng) và tập
test nội miền **59.093 ảnh**:

| Kiến trúc | sustained/ảnh | × 59.093 | Khả thi? |
|---|--:|--:|---|
| `mobilenetv4_conv_medium` | 39,5 ms | **≈ 39 phút** | ✅ |
| `repvit_m1_0` | 57,2 ms | ≈ 56 phút | ✅ |
| `fastvit_sa12` | 113,9 ms | ≈ 1 giờ 52 phút | ✅ |
| `efficientformerv2_s2` (portable) | 3.908,2 ms | **≈ 64 giờ** | ❌ **loại** (~99× chậm hơn) |

**Dung lượng đẩy sang máy:** byte thật của ảnh processed là **5,83 KB/ảnh** (597.239 B cho 100 ảnh
của bundle cũ — `du` báo 824 KB vì đếm theo block, đừng dùng số đó), và tập test 99,3% là ISIC
(5,00 KB/ảnh) ⇒ **≈ 300–345 MB**. Đẩy được qua `adb push`.

⚠️ **KHÔNG đẩy `inputs/*.bin` cho tập đầy đủ.** Mỗi `.bin` là đúng **602.112 B** (3×224×224×4)
⇒ 59.093 ảnh là **~35,6 GB**, và `make_benchmark_set.py` còn ghi thêm `inputs.npy` cùng cỡ. `inputs/`
chỉ dùng cho tập 100 ảnh của cổng L1; nhánh đánh giá đọc **JPEG**.

**Thành phần tập test (cần biết khi đọc kết quả):** 59.093 dòng / **265 ca dương** / 399 bệnh nhân,
chia **PAD 397 dòng – 189 dương** · **ISIC 58.696 dòng – 76 dương**. Tức **71,3% ca dương nằm trên
0,67% số dòng**. Hệ quả: AUPRC bị chi phối bởi vài trăm ảnh PAD và **CI sẽ rộng**; sàn nhiễu
run-to-run của dự án là **0,0053 AUPRC** (`experiments/_reproducibility/README.md`).

---

## 3. Việc phía ML (bạn chạy) — 4 việc code phải làm trước

| ☐ | Bước | Chi tiết |
|:--:|---|---|
| ☐ | 3.1 Giải §0 xong | Không có checkpoint sạch thì mọi số ở dưới không dùng được cho luận văn |
| ☐ | 3.2 **`make_benchmark_set.py`: thêm `--no-inputs`** | Hiện `:136`/`:145` ghi `inputs/*.bin` **và** `inputs.npy` vô điều kiện |
| ☐ | 3.3 **`make_benchmark_set.py`: sinh reference THEO LÔ** | Đây là lỗi chặn, không chỉ là tối ưu: `:143` `np.stack(tensors)` giữ cả stack trong RAM (35,6 GB ở N=59093) và `:183-186` gọi `model(torch.from_numpy(inputs))` — **một forward duy nhất trên toàn bộ N**. Phải viết lại thành vòng lặp theo lô. *Hoặc* bỏ hẳn đường này và dùng `y_prob` trong `predictions.csv` sẵn có làm reference (nhưng `predictions.csv` **không có cột id** nên phải dựa vào thứ tự dòng — kiểm kỹ trước khi tin) |
| ☐ | 3.4 **Truyền cờ mới qua runner + cập nhật README** | `run/make_benchmark_set.sh:34-40` không có pass-through; `run/README.md:65` còn ghi *"the fixed **100-image** benchmark input set"*. CLAUDE.md bước 3 bắt buộc sửa cùng task |
| ☐ | 3.5 **Viết `scripts/metrics_from_logits.py` + `run/metrics_from_logits.sh` + 1 dòng README** | Chưa tồn tại. Nhận CSV `id,logit` từ máy + nhãn từ `manifest.csv` → `sigmoid` → áp ngưỡng Youden đông cứng từ `val_predictions.csv` → gọi `compute_metrics()` (`src/evaluation/metrics.py:168`) → ghi `test_metrics.json` + `predictions.csv` **theo đúng layout run-dir**. **Đừng để app tự tính metric** |
| ☐ | 3.6 Sinh bundle | `bash run/make_benchmark_set.sh N=59093 OUTDIR=data/eval_set_v2 MODEL=<m> CKPT=<ckpt>` — ⚠️ **phải đặt `OUTDIR`**: mặc định là `data/benchmark_set`, nơi đang có bundle 100 ảnh + các `ref_*.csv` cũ (kể cả của model đã xoá khỏi registry); ghi lẫn vào đó sẽ trộn hai bundle có **cùng id nhưng khác ảnh** và phá luôn cổng L1 (`run/check_pte_parity.sh` đọc `BENCH_DIR=data/benchmark_set`) |
| ☐ | 3.7 **Sinh `l1_gate/` từ CÙNG lượt chọn** | ⚠️ Xem §3a — id **không** so sánh được giữa hai lần gọi `make_benchmark_set` |
| ☐ | 3.8 Đóng bundle giao cho dev | `catalog.json`, `SHA256SUMS`, `README.md`, `schema/`. **Không script nào sinh các file này** — bundle 08/2026 làm bằng tay. Đây là một việc, không phải một lệnh |
| ☐ | 3.9 Cổng L1 trên PC | `bash run/check_pte_parity.sh MODEL=<m> BENCH_DIR=<bundle> PTE=<pte v2>` |
| ☐ | 3.10 Đẩy bundle + chạy harness | `docs/MOBILE_EVAL_TASK.md` |
| ☐ | 3.11 So sánh có CI | Xem §3b |

### 3a. ⚠️ Bẫy: `id` không phải định danh ảnh bền

`scripts/make_benchmark_set.py:63-78` chọn mẫu bằng `rng.shuffle` rồi lấy `n//2` ca dương, và
`:100-118` cấp `sample_id = f"{i:04d}"` **theo thứ tự của lượt chọn đó**. Nên với `n=100` và
`n=59093`, id `0042` là **hai ảnh khác nhau**; tên tệp cũng mã hoá nhãn
(`<id>__<source>__y<label>.<ext>`). ⇒ Bộ 100 ảnh của cổng L1 phải được **trích ra từ chính bundle
đánh giá** (lấy 100 dòng đầu của `manifest.csv` của nó), chứ không phải sinh bằng một lần gọi thứ
hai. Nếu làm sai, dev sẽ thấy Δ bậc 1 và đi tìm một bug CHW/RGB không tồn tại.

### 3b. Cách dàn thư mục cho `bootstrap_ci`

`scripts/bootstrap_ci.py:323` nhận **một** `--results-dir`, và `--pair A:B` ghép hai run-dir
**trong cùng cây đó**. Nên tạo một cây tạm rồi symlink hai nhánh vào, đúng tiền lệ của arm DDI
(`.tmp/ci_ddi/...`):

```
.tmp/ci_mobile/
  server/fold_N/predictions.csv     -> nhánh PyTorch
  mobile/fold_N/predictions.csv     -> nhánh .pte trên máy
```
rồi `bash run/bootstrap_ci.sh RESULTS_DIR=.tmp/ci_mobile PAIR="mobile:server"`. Không cần sửa code.
Đây là trường hợp **paired** mạnh nhất có thể có: cùng tập ảnh, hai runtime.

**Ngưỡng quyết định:** giữ quy ước dự án — Youden's J **đông cứng từ `val_predictions.csv`** của
chính fold đó, không fit lại trên test. App dump logit thô; ngưỡng áp ngoài máy.

---

## 4. Điện thoại nói được gì, và không nói được gì

**Nói được:** logit do phần cứng thật tính, trên đúng những ảnh server đã chấm ⇒ Δ metric giữa hai
runtime, tách được thành L2 và (proxy) L3.

**Không nói được:**
- **Không** phải bằng chứng tốc độ mới — tốc độ + bộ nhớ đã đo xong 27/08, và lượt đánh giá này
  **được phép cắm sạc, chạy ở xung nào cũng được**: logit là tất định, điều tiết nhiệt làm chậm chứ
  không làm lệch số. Khác hẳn lượt benchmark (bắt buộc rút sạc + máy bay). **Đừng trộn hai bảng số.**
- **Không** trả lời được câu về ảnh ngoài miền (HAM10000 / Fitzpatrick17k) trừ khi đẩy thêm các tập
  đó — việc riêng, và đáng làm **sau**, vì đó mới là phân phối app ngoài đời gặp.

---

## 5. Kết quả mong đợi — đăng ký trước

1. **L2 dự kiến vô hại**, nhưng **mức lệch là ẩn số chưa đo**. Nếu L2 lệch lớn thì khả năng cao là
   **bug trong harness** (sai thứ tự kênh, sai CHW, sai `/255`), không phải phát hiện khoa học.
2. **L3 (proxy) là ẩn số thật.** Nếu đổi thuật toán lấy mẫu lại mà ΔAUPRC vượt sàn nhiễu 0,0053 thì
   kết luận là: *app phải tái lập đúng phép lấy mẫu lại của lúc huấn luyện*.
3. **Nếu cả hai null** thì cũng là kết quả cần cho chương triển khai: *mô hình 32 MB
   (`mobilenetv4`, 32,11 MiB) chạy trên điện thoại cho đúng chất lượng đã báo cáo*.

---

## 6. Rủi ro đã biết

1. **Không còn checkpoint student trên splits sạch** (§0) — rủi ro lớn nhất; và xác nhận cuối phải
   làm trên box, không kiểm được từ Mac.
2. **`efficientformerv2_s2` không đánh giá được ở quy mô đầy đủ** (64 giờ) ⇒ nếu cần cả 4 kiến trúc
   thì phải rút xuống tập con và nói rõ là tập con.
3. **265 ca dương** ⇒ CI rộng; một Δ nhỏ sẽ không phân định được. Đừng hứa trước là sẽ phân định.
4. **App cũ không tái dùng được** — nhưng **lý do không phải "không lái được bằng adb"**: báo cáo
   27/08 nói lượt cold-start được lái bằng `am force-stop` + `am start`
   (`BENCHMARK_RESULTS.md:311`), tức adb **lái được** một app chỉ có LAUNCHER. Lý do thật là: không
   có source Kotlin trong repo (`find . -name "*.kt"` = 0), app tính **max\|Δ\| + latency** chứ
   không dump logit từng ảnh, và không có cách trỏ nó vào bộ ảnh mới. Ghi chú: APK đang cài trên
   máy có `lastUpdateTime = 2026-09-26 22:11`, cài qua `com.android.shell` — tức bản trên máy **mới
   hôm nay**, nên đừng mặc định nó giống bản đã dùng tháng 8.
5. **Đừng sửa `.pte` để "cho khớp"** — một `.pte` tính ra logit khác là **một model khác**.

---

## 7. Điều tài liệu này KHÔNG verify được

- Trạng thái thật trên box: checkpoint `runs_newsplit_*/{kd,baseline}` còn hay mất; `.venv-export`
  đã xoá hay chưa. Chỉ đọc được **bản ghi** dọn đĩa 26/09 trên Mac.
- Mức lệch pixel/logit của L2 và L3 — **chưa ai đo**; tài liệu này không đưa con số kỳ vọng nào.
- Lượt 08/2026 được lái bằng công cụ UI nào (chuỗi "uiautomator" không có trong bất kỳ artifact
  nào; dữ kiện duy nhất là app dùng Compose — `BENCHMARK_RESULTS.md:551`).
- Tỉ lệ chính xác ảnh ISIC bị phóng lên vs thu nhỏ (§1.2) — cần đọc kích thước gốc trong HDF5.
- Một lượt nạp `.pte` thử trên Mac trong phiên soạn tài liệu này đã chạy được, nhưng **không ghi
  artifact nào**, nên không trích được. Artifact parity duy nhất sinh trên Mac là
  `reports/mobile_benchmark/parity_mobilenetv3_large.json` (25/09): `max_abs_logit_delta`
  **4,34e-06**.
