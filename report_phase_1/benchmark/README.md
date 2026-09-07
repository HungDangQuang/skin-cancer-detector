# Benchmark — Phase 1

Ba lớp đo, KHÔNG so chéo latency với nhau (khác phần cứng). Chỉ params/FLOPs/size là so chéo được.

```
benchmark/
├── cpu_benchmark/
│   ├── full_profile_cpu_gpu/     ← FLOPs + GPU + CPU percentile (fastvit, mobilenetv4, efficientformerv2)
│   └── cpu_proxy_singlethread/   ← CPU 1-luồng server, proxy cho mobile
└── mobile_benchmark/
    └── pixel6a_ondevice.csv      ← đo THẬT trên Pixel 6a (.pte, ExecuTorch/XNNPACK)
```

> ⚠️ **Phạm vi model:** đề tài hiện dùng 4 student `{mobilenetv4_conv_medium, fastvit_sa12,
> efficientformerv2_s2, repvit_m1_0}` + 3 teacher `{efficientnetv2_m, convnextv2_base, maxvit_base}`.
> Các file JSON của `efficientnet_b0` / `mobilenetv3_large` / `mobilevit_s` / `efficientnet_b4` trong
> thư mục này là **số lịch sử** — 4 kiến trúc đó đã bị xoá khỏi `src/models/registry.py` và không còn
> thuộc đề tài, nên **không đưa vào bảng Pareto hay khuyến nghị** nữa.

---

## 1. Hiệu năng tĩnh (so chéo thiết bị được)

| Model | Params (M) | GFLOPs | GMACs | Size FP32 (MB) |
|---|---|---|---|---|
| mobilenetv4_conv_medium | 8.436 | 1.653 | 0.826 | 32.44 |
| fastvit_sa12 | 10.557 | 2.962 | 1.481 | 40.41 |
| efficientformerv2_s2 | 12.132 | 2.493 | 1.246 | 46.75 |
| **repvit_m1_0** | *chưa đo* | *chưa đo* | *chưa đo* | *chưa đo* |
| 3 teacher hiện tại | *chưa đo* | *chưa đo* | *chưa đo* | *chưa đo* |

*Nguồn: `full_profile_cpu_gpu/*.json`. **GAP:** `repvit_m1_0` (student thứ 4) và 3 teacher hiện tại
chưa có job benchmark nào → chạy `bash run/benchmark.sh MODEL=<name> CKPT=<path>` bổ sung.*

## 2. Latency proxy trên CPU server (x86, 1 luồng, batch=1, median ms)

| Model | CPU proxy | GPU (cuda) |
|---|---|---|
| mobilenetv4_conv_medium | 17.36 | 0.75 |
| efficientformerv2_s2 | 37.64 | 7.17 |
| fastvit_sa12 | 41.73 | 3.57 |

⚠️ **Đây KHÔNG phải số điện thoại** — chỉ để so tương đối trên cùng CPU server. Cột GPU đo trên card
của cụm cũ (L40); training hiện chạy trên box vast.ai `vastnew` (1×RTX 3090) nên số GPU chỉ có giá trị
tham khảo lịch sử.

## 3. Latency ON-DEVICE thật — Pixel 6a (Google Tensor, arm64-v8a, SDK 36)

`.pte` FP32 · ExecuTorch/XNNPACK · warmup 10 · 50 iters · batch=1 · đo **2026-07-04**.

| Model | Size .pte | median@t1 | median@t4 | p90@t4 | Cold@t4 | FPS@t4 |
|---|---|---|---|---|---|---|
| **mobilenetv4_conv_medium** | 32.11 MB | 53.32 | **22.64** | 23.98 | 34.94 | **44** |
| efficientformerv2_s2 | 46.98 MB | 88.60 | 42.83 | 44.36 | 61.52 | 23 |
| fastvit_sa12 | 40.35 MB | 142.32 | 65.48 | 68.29 | 91.56 | 15.3 |
| repvit_m1_0 | — | — | *chưa đo* | — | — | — |

> **Vì sao số 2026-07-04 vẫn dùng được sau khi model train lại:** latency và kích thước là
> **weight-independent** — chỉ phụ thuộc kiến trúc, không phụ thuộc giá trị trọng số
> (`docs/MOBILE.md §0`). Chỉ cột độ chính xác đi kèm là phải thay bằng bản July-15+.

## 4. Proxy vs thực tế — hệ số phạt trên ARM (single-thread)

| Model | CPU server | Pixel 6a t1 | Hệ số phạt |
|---|---|---|---|
| efficientformerv2_s2 | 37.64 | 88.60 | 2.4× |
| mobilenetv4_conv_medium | 17.36 | 53.32 | 3.1× |
| fastvit_sa12 | 41.73 | 142.32 | **3.4×** |

---

## Phát hiện chính (đáng đưa vào slide)

Thứ hạng latency on-device (t4 median): **mobilenetv4 22.6 < efficientformerv2 42.8 < fastvit 65.5 ms.**

1. **Latency ranking KHÔNG theo params/FLOPs.** `fastvit_sa12` (10.6M param, 2.96 GFLOPs) chạy **chậm
   hơn** `efficientformerv2_s2` (12.1M param, 2.49 GFLOPs) trên Pixel 6a — 65.5 vs 42.8 ms — dù ít
   param hơn. → **Phải đo on-device, không suy từ FLOPs.**
2. **FastViT bị lấn át trên máy thật:** AUPRC ≈ EfficientFormerV2 (0.6209 vs 0.6220) nhưng chậm hơn
   1,5×. Kết luận này chỉ có được nhờ benchmark thật.
3. **Model transformer/hybrid bị phạt nặng trên ARM** (fastvit 3.4×, mobilenetv4 3.1×) → proxy server
   không dự đoán được latency thật.
4. **Đa luồng quan trọng:** t4 nhanh gấp ~2,4× t1. Khuyến nghị app dùng `threads=0` (auto) hoặc 4.
5. **Kích thước `.pte` ≈ size FP32** (chưa lượng tử hóa — INT8 nằm ngoài phạm vi đề tài):
   mobilenetv4 32 MB, fastvit 40 MB, efficientformerv2 47 MB.
6. **Model chốt = `mobilenetv4_conv_medium`** — nhanh nhất, nhẹ nhất, *và* dẫn đầu pAUC@80/AUC/Sens
   trong nhóm student sau KD.

## Còn thiếu (GAP)
- **`exports/` đang RỖNG** → chưa có `.pte` nào cho checkpoint July-15+. Phải export lại
  (`bash run/export_executorch.sh`) trước khi trích số on-device cho bộ model hiện tại.
- **Parity check** `max|Δlogit| < 1e-3` giữa `.pte` và PyTorch — **bắt buộc** trước khi tin số on-device.
- **`repvit_m1_0`**: params / FLOPs / size / latency — chưa có số nào.
- **Params/FLOPs cho 3 teacher hiện tại** (`efficientnetv2_m`, `convnextv2_base`, `maxvit_base`).
- **Peak RAM** + **end-to-end latency** (resize + normalize + forward + sigmoid) — chỉ đo được trong app.
