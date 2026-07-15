# Report Phase 1 — Skin Cancer Detection via Knowledge Distillation

Tổng hợp toàn bộ kết quả Phase 1 để chuẩn bị **proposal + slide**. Tất cả số liệu trích trực
tiếp từ `experiments/runs/` và `reports/` (5-fold CV, test độc lập patient-disjoint).

*Cập nhật: 2026-07-04.*

---

## Cấu trúc thư mục

```
report_phase_1/
├── README.md                         ← file này (tóm tắt + điều hướng)
├── model/                            ← checkpoint (symlink) + đánh giá từng model
│   ├── CHECKPOINTS_MANIFEST.md       ← đường dẫn + dung lượng thật mọi checkpoint (9.1 GB gốc)
│   ├── teacher/                      ← 4 teacher: convnextv2_base, maxvit_base, efficientnetv2_m, efficientnet_b4
│   ├── student_kd/                   ← student có KD (kd_<teacher>_to_<student>)
│   └── student_no_kd/                ← student baseline (không KD)
│        └── <run>/fold_*/test_metrics.json, val_metrics.json, predictions.csv
│            aggregated.json/md, best_model_fold0.pth (symlink)
├── benchmark/
│   ├── cpu_benchmark/
│   │   ├── full_profile_cpu_gpu/     ← FLOPs + GPU + CPU percentile
│   │   └── cpu_proxy_singlethread/   ← CPU 1-luồng (proxy mobile)
│   └── mobile_benchmark/
│       └── pixel6a_ondevice.csv      ← đo thật trên Pixel 6a
└── evaluation/
    ├── 01_metrics_explained.md       ← giải thích từng độ đo (vì sao dùng)
    ├── 02_model_comparison.md        ← xếp hạng đầy đủ, model nào tốt hơn
    └── 03_kd_effectiveness.md        ← KD vs baseline, luận điểm KD
```

> Checkpoint trong `model/` là **symlink fold_0** (tránh nhân bản 9.1 GB). Đường dẫn thật của
> mọi fold ở `model/CHECKPOINTS_MANIFEST.md`. Cần bản copy vật lý cho model nào thì báo.

---

## Tóm tắt kết quả (headline cho slide)

### Độ chính xác (mean 5-fold, test độc lập)
- **Student KD tốt nhất:** `fastvit_sa12 ← convnextv2_base` — pAUC@80 **0.1908**, AUC **0.9902**, AUPRC **0.6756**, Sens 0.949.
- **AUPRC cao nhất:** `efficientformerv2_s2 ← convnextv2_base` 0.6839 (⚠️ mới 4 fold); đủ 5-fold cao nhất là fastvit (0.6756).
- **Teacher mạnh nhất:** maxvit_base / convnextv2_base (AUPRC ~0.68); **efficientnet_b4 yếu nhất (0.60)**.
- **Mọi student SOTA vượt teacher efficientnet_b4** → KD + kiến trúc mobile hiện đại thắng CNN cũ.

### Hiệu quả KD (KD − Baseline)
- **pAUC@80 và Sensitivity: KD cải thiện NHẤT QUÁN** trên mọi cặp student×teacher.
- **AUPRC: phụ thuộc chất lượng teacher** — teacher mạnh (convnextv2) → KD nâng AUPRC MobileNetV4 **+0.052** (0.609→0.661); teacher yếu (efficientnet_b4) → Δ trong nhiễu.

### Benchmark on-device (Pixel 6a, threads=4) — đo 4 model cùng phiên 2026-07-04
| Model | AUPRC | median | Size .pte | FPS |
|---|---|---|---|---|
| mobilenetv3_large (KD) | 0.6313 | **8.4 ms** | **16 MB** | 119 |
| **mobilenetv4 ← convnextv2 (KD)** | **0.6614** | 22.6 ms | 32 MB | 44 |
| efficientformerv2_s2 ← convnextv2 (KD) | **0.6839** ⚠️4fold | 42.8 ms | 47 MB | 23 |
| fastvit ← convnextv2 (KD) | 0.6756 | 65.5 ms | 40 MB | 15.3 |

- **Latency ranking ĐẢO trên mobile:** proxy server nói fastvit ~ mobilenetv4, nhưng trên phone
  fastvit chậm gấp ~7.8× mobilenetv3. Transformer/hybrid bị phạt nặng nhất trên ARM (3.4×).
- **efficientformerv2_s2 vượt fastvit trên máy thật:** nhanh hơn (43 vs 65 ms) VÀ AUPRC cao hơn
  (0.684 vs 0.676) — ứng viên mới đáng chú ý, chỉ vướng `.pte` lớn (47 MB) + mới 4 fold.

### Khuyến nghị model deploy Phase 1
**mobilenetv4_conv_medium ← convnextv2_base** — cân bằng tốt nhất (AUPRC 0.661, Sens 0.962,
22 ms, 32 MB) và đồng thời là **case chứng minh KD mạnh nhất** (+0.052 AUPRC). Dùng mobilenetv3
nếu cần nhẹ/nhanh tối đa.

---

## Việc còn thiếu (để hoàn thiện luận văn)
| GAP | Nội dung | Ưu tiên |
|---|---|---|
| Fold chưa đủ | maxvit-KD (1 fold), efficientformerv2_s2 (4 fold) → chạy nốt fold còn lại | 🔴 |
| Parity check | `max|Δlogit|<1e-3` giữa `.pte` và PyTorch chưa xác nhận | 🟡 |
| Mobile metrics | Peak RAM + end-to-end latency (đo trong app) | 🟡 |
| FLOPs | mobilenetv3/b0/mobilevit_s — job đã chạy, JSON chưa rsync về | ⚪ |
| On-device (tùy chọn) | efficientnet_b0 / mobilevit_s (đã bị mobilenetv3 lấn át) | ⚪ |

Chi tiết đầy đủ + số ± std: xem `evaluation/` và `benchmark/`.
