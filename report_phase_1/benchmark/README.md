# Benchmark — Phase 1

Ba lớp đo, KHÔNG so chéo latency với nhau (khác phần cứng). Chỉ params/FLOPs/size là so chéo được.

```
benchmark/
├── cpu_benchmark/
│   ├── full_profile_cpu_gpu/     ← reports/benchmark: FLOPs + GPU L40 + CPU percentile (fastvit, mobilenetv4)
│   └── cpu_proxy_singlethread/   ← reports/mobile_benchmark: CPU 1-luồng server, proxy cho mobile (6 model)
└── mobile_benchmark/
    └── pixel6a_ondevice.csv      ← đo THẬT trên Pixel 6a (.pte, ExecuTorch/XNNPACK)
```

---

## 1. Hiệu năng tĩnh (so chéo thiết bị được)

| Model | Params (M) | GFLOPs | GMACs | Size FP32 (MB) |
|---|---|---|---|---|
| efficientnet_b0 | 4.009 | — | — | 15.45 |
| mobilenetv3_large | 4.203 | — | — | 16.13 |
| mobilevit_s | 4.938 | — | — | 18.89 |
| mobilenetv4_conv_medium | 8.436 | 1.653 | 0.826 | 32.44 |
| fastvit_sa12 | 10.557 | 2.962 | 1.481 | 40.41 |
| efficientformerv2_s2 | 12.132 | 2.493 | 1.246 | 46.75 |
| efficientnet_b4 (teacher) | 17.55 | — | — | 67.43 |

*FLOPs đã đo cho fastvit, mobilenetv4, efficientformerv2 (full_profile). Còn thiếu FLOPs cho
mobilenetv3/b0/mobilevit_s — job 24_benchmark DEVICE=cpu đã submit nhưng JSON chưa rsync về
(kiểm tra logs/benchmark_357xx trên cluster). Xem GAP-3.*

## 2. Latency proxy trên cluster (CPU x86 server, 1 luồng, batch=1, median ms)

| Model | CPU proxy | GPU L40 (cuda) |
|---|---|---|
| mobilenetv3_large | 8.64 | — |
| mobilenetv4_conv_medium | 17.36 | 0.75 |
| efficientnet_b0 | 22.22 | — |
| mobilevit_s | 35.73 | — |
| efficientformerv2_s2 | 37.64 | 7.17 |
| fastvit_sa12 | 41.73 | 3.57 |
| efficientnet_b4 (teacher) | 46.23 | — |

⚠️ **Đây KHÔNG phải số điện thoại** — chỉ để so tương đối trên cùng CPU server.

## 3. Latency ON-DEVICE thật — Pixel 6a (Google Tensor, arm64-v8a, SDK 36)

`.pte` FP32 · ExecuTorch/XNNPACK · warmup 10 · 50 iters · batch=1 · run 2026-07-04 (đo 4 model cùng phiên).

| Model | Size .pte | median@t1 | median@t4 | p90@t4 | Cold@t4 | FPS@t4 |
|---|---|---|---|---|---|---|
| **mobilenetv3_large** | 16.05 MB | 18.20 | **8.40** | 9.23 | 12.01 | **119** |
| mobilenetv4_conv_medium | 32.11 MB | 53.32 | 22.64 | 23.98 | 34.94 | 44 |
| efficientformerv2_s2 | 46.98 MB | 88.60 | 42.83 | 44.36 | 61.52 | 23 |
| fastvit_sa12 | 40.35 MB | 142.32 | 65.48 | 68.29 | 91.56 | 15.3 |

## 4. Proxy vs thực tế — hệ số phạt trên ARM (single-thread)

| Model | Cluster CPU | Pixel 6a t1 | Hệ số phạt |
|---|---|---|---|
| mobilenetv3_large | 8.64 | 18.20 | 2.1× |
| efficientformerv2_s2 | 37.64 | 88.60 | 2.4× |
| mobilenetv4_conv_medium | 17.36 | 53.32 | 3.1× |
| fastvit_sa12 | 41.73 | 142.32 | **3.4×** |

---

## Phát hiện chính (đáng đưa vào slide)

Thứ hạng latency on-device (t4 median): **mobilenetv3 8.4 < mobilenetv4 22.6 < efficientformerv2 42.8 < fastvit 65.5 ms.**

1. **Latency ranking ĐẢO trên mobile.** Trên proxy server fastvit 41.7 ms; trên Pixel 6a t4
   fastvit chậm nhất (65 ms) còn mobilenetv3 nhanh nhất (8.4 ms — gấp ~7.8× fastvit).
2. **efficientformerv2_s2 "thống trị" fastvit trên máy thật:** nhanh hơn (43 ms vs 65 ms @t4)
   VÀ AUPRC cao hơn (0.684 vs 0.676) — dù nhiều params hơn (12.1M vs 10.6M). Thêm một bằng chứng
   **latency không tỉ lệ params/FLOPs**; đổi lại `.pte` lớn nhất (47 MB) và AUPRC mới 4-fold ⚠️.
3. **Model transformer/hybrid bị phạt nặng trên ARM** (fastvit 3.4×, mobilenetv4 3.1× vs
   mobilenetv3 conv 2.1×). → FLOPs/proxy KHÔNG dự đoán latency thật; **phải đo on-device**.
4. **Đa luồng quan trọng:** t4 nhanh gấp ~2× t1. Khuyến nghị app dùng `threads=0` (auto) hoặc 4.
5. **Kích thước `.pte` ≈ size FP32** (chưa lượng tử hoá) — mobilenetv3 16, mobilenetv4 32,
   fastvit 40, efficientformerv2 47 MB.

## Còn thiếu (GAP)
- **Peak RAM** + **end-to-end latency** (resize+normalize+forward+sigmoid) — chỉ đo được trong app.
- **FLOPs cho mobilenetv3/b0/mobilevit_s** — job đã chạy nhưng JSON chưa rsync về (GAP-3).
- **On-device cho efficientnet_b0 / mobilevit_s** — tùy chọn (đã bị mobilenetv3 lấn át).
- **Parity check** `max|Δlogit|<1e-3` giữa `.pte` và PyTorch — bắt buộc trước khi tin số on-device.
- FLOPs cho các model nhẹ (mobilenetv3, b0, mobilevit_s).
