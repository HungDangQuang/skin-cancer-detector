# Hướng dẫn benchmark hiệu năng PC + Android (on-device)

Tài liệu này mô tả toàn bộ quy trình đo hiệu năng triển khai cho khóa luận:
**chạy sau khi các model đã train xong đầy đủ** (teacher + tất cả student, đã có
`best_model.pth` mỗi fold). Mọi số đều ở **FP32** (lượng tử hóa INT8 nằm ngoài
phạm vi đề tài). Runtime Android = **ExecuTorch** (PyTorch-native, không convert
sang TFLite).

> Bản chất hai loại số:
> - **Chuyển được giữa thiết bị:** params, FLOPs/MACs, model size → trục so sánh chính (kể cả trục x của Pareto).
> - **KHÔNG chuyển được:** latency/throughput tuyệt đối → device-specific, luôn ghi rõ phần cứng.

---

## 0. Tiền đề

- [ ] Các checkpoint tồn tại: teacher + student × 5 fold (`experiments/runs/.../fold_*/checkpoints/best_model.pth`).
- [ ] Một **điện thoại Android thật** (emulator cho số latency vô nghĩa).
- [ ] Latency là **weight-independent** → mỗi kiến trúc chỉ cần benchmark **1 checkpoint (fold bất kỳ)**.

---

## 1. Tạo bộ dữ liệu benchmark cố định (dùng chung PC + mobile + parity)

Một bộ test cố định, dùng chung cho cả ba mục đích. Proposal không pin dataset
benchmark → dùng **test nội bộ ISIC2024+PAD** (domain ảnh smartphone). Tiền xử lý
khớp tuyệt đối eval (`build_transforms(cfg,"val")`).

```bash
# Bộ input dùng chung:
bash slurm/submit.sh slurm/26_make_benchmark_set.slurm N=100
# Kèm logit tham chiếu cho parity — chạy cho TỪNG student định đo:
bash slurm/submit.sh slurm/26_make_benchmark_set.slurm N=100 \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
```

Kết quả `data/benchmark_set/` (rsync về Mac/điện thoại, **không commit**):

| File | Dùng cho |
|---|---|
| `inputs/<id>.bin` | latency + parity layer 1 (nạp thẳng, đã chuẩn hóa) |
| `inputs.npy` | PC (stacked `(N,3,224,224)`) |
| `images/<file>` | parity layer 2 (app tự tiền xử lý) |
| `ref_<model>.csv` | logit/prob tham chiếu (`id,label,source,logit,prob`) |
| `manifest.csv` | map `id ↔ file ↔ label ↔ source` |
| `meta.json` | hằng số tiền xử lý (224 / ImageNet mean-std / layout) |

**Format `.bin`:** `float32`, little-endian, C-order, shape `(3,224,224)` = CHW,
RGB, **đã chuẩn hóa hoàn chỉnh** (`/255` rồi `(x-mean)/std`). Inference chỉ cần
thêm batch → `(1,3,224,224)`.

---

## 2. Benchmark trên PC (server cluster)

```bash
bash slurm/submit.sh slurm/24_benchmark.slurm \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
```

Ra `reports/benchmark/<MODEL>.json`: params, FLOPs/MACs, FP32 size, latency
CPU/GPU (mean/median/p90/p95/p99), throughput, `device_info`.

> TODO (chưa làm): thêm `--input-file data/benchmark_set/inputs.npy` vào
> `scripts/benchmark.py` để PC dùng đúng bộ cố định thay vì `torch.randn`.

---

## 3. Export model sang ExecuTorch (.pte)

ExecuTorch pin torch riêng → **venv cô lập**, không đụng venv training.

```bash
# Một lần, trên login node:
bash slurm/setup_export_env.sh
# Mỗi student:
bash slurm/submit.sh slurm/25_export_executorch.slurm \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
# BACKEND=none nếu XNNPACK không partition được kiến trúc nào đó
```

Ra `exports/executorch/<MODEL>.pte`. Dùng `torch.export` → chạy được cả student
transformer (mobilevit/fastvit/efficientformerv2) mà `torch.jit.script` fail.

---

## 4. Benchmark trên Android (on-device)

### 4.1 Dependency
- Thêm **ExecuTorch Android AAR** (có **XNNPACK** — phải khớp vì `.pte` lower bằng XNNPACK).
- ⚠️ **Khớp version ExecuTorch** giữa lúc export (python venv-export) và AAR runtime — format `.pte` có versioning.
- Phần đo (timing/thống kê/JSON/bitmap) dùng **built-in Android/Java**, không cần lib ngoài.

### 4.2 Đẩy bộ dữ liệu
Copy `data/benchmark_set/` (+ file `.pte`) vào device. Trên Android dùng các
`inputs/<id>.bin` (bỏ qua `inputs.npy`).

### 4.3 Đọc `.bin` → tensor (Kotlin)
```kotlin
fun loadBin(file: File, numEl: Int = 3*224*224): FloatArray {
    val buf = ByteBuffer.wrap(file.readBytes())
        .order(ByteOrder.LITTLE_ENDIAN).asFloatBuffer()
    return FloatArray(numEl).also { buf.get(it) }
}
val input = loadBin(File(inputsDir, "0001.bin"))
val t = Tensor.fromBlob(input, longArrayOf(1, 3, 224, 224))
val logit = module.forward(EValue.from(t))[0].toTensor().dataAsFloatArray[0]
val prob = 1f / (1f + kotlin.math.exp(-logit))
// quyết định: prob >= youden_threshold (từ test_metrics.json), KHÔNG dùng 0.5
```

### 4.4 (a) Đo latency
Lặp `forward` trên các `.bin` (warmup ~30, đo ~100–200 lần) → ghi
mean/median/p90/p95/p99, **cold start** (`Module.load` + forward đầu), **sustained**
(chạy ~5 phút xem thermal throttle), model/app size. Điều kiện: airplane mode,
màn hình bật, không app nền, pin ổn định. Chốt **single/multi-thread** và ghi rõ.

### 4.5 (b) Parity layer 1 — độ trung thực model (chặt, `< 1e-3`)
Vì input `.bin` **giống hệt** PC, lớp này cô lập lỗi *model/convert*:
```kotlin
// đọc ref_<model>.csv theo id
val diff = kotlin.math.abs(onDeviceLogit - refLogit)   // yêu cầu < 1e-3
```

### 4.6 (c) Parity layer 2 — sanity tiền xử lý (tolerance lỏng)
App đọc `images/<file>` → tự resize 224 + `/255` + chuẩn hóa ImageNet (theo
`meta.json`) → so với `inputs/<id>.bin`.
```kotlin
val bmp = BitmapFactory.decodeFile(File(imagesDir, imgFile).path)
val resized = Bitmap.createScaledBitmap(bmp, 224, 224, true)
// getPixels -> tách R,G,B -> /255 -> (x-mean)/std từng kênh -> CHW float[]
```
⚠️ Android `Bitmap.createScaledBitmap` (bilinear) **khác** `cv2.INTER_LINEAR` của
Albumentations → mảng lệch nhẹ, **đừng** đòi `<1e-3` ở lớp này. Dùng tolerance
lỏng (logit cuối lệch nhỏ / dự đoán không đổi). Lớp 1 = chứng minh model; lớp 2 =
sanity tiền xử lý.

### 4.7 Xuất kết quả khớp schema PC
Ghi JSON giống `reports/benchmark/<model>.json`, thêm:
```json
{ "device": "android-<phone>", "soc": "<chipset>", "android": "<ver>",
  "backend": "xnnpack", "threads": 1,
  "latency_batch1": { "mean":.., "median":.., "p90":.., "p95":.., "p99":.. },
  "cold_start_ms": .., "model_size_mb": .. }
```

---

## 5. Tổng hợp + biểu đồ Pareto

> TODO (chưa làm): script gộp `reports/benchmark/*.json` (PC) + JSON Android +
> AUPRC từ `aggregated.json` của mỗi run → bảng + **Pareto: AUPRC (y) vs
> FLOPs/params (x)**, nhãn phụ latency theo thiết bị. Đây là hình "đắt" nhất cho
> chương đánh giá triển khai.

---

## 6. Lưu ý báo cáo
- Trục so sánh chính = **AUPRC vs FLOPs/params** (transferable). Latency là nhãn phụ, ghi rõ thiết bị.
- **Đừng** gọi CPU latency proxy bên PC là "tốc độ điện thoại" — gọi đúng tên + nêu caveat.
- Khoảng cách **FLOPs (lý thuyết) vs latency đo thật** là một insight: student transformer có thể chậm trên mobile hơn FLOPs gợi ý.
- `.pte` đang lower **XNNPACK = CPU** → số là mobile CPU. NPU/GPU (QNN/Vulkan) là scope khác.

Xem thêm: `slurm/README.md` (mục Section 5 — benchmark/export) và
`docs/SLURM.md`.
