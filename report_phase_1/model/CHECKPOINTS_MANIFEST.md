# Checkpoint & artifact manifest (Phase 1)

Thư mục `model/` là **bản sao artifact** (không phải trọng số) của các run, để báo cáo tự đứng được:

```
model/
├── teacher/<name>/                         aggregated.json/md + fold_*/{test,val}_metrics.json, predictions.csv
├── student_kd/kd_<teacher>_to_<student>/    …
├── student_no_kd/baseline_<student>/        …
└── ablation_pad_isic_only/teacher/<name>/   nhánh ISIC-only của ablation PAD
```

Trọng số gốc nằm ở `experiments/runs/<run>/fold_<N>/checkpoints/best_model.pth` (một vài run cũ có
symlink `best_model_fold0.pth` trỏ về đó).

**Bản sao artifact đã được làm mới ngày 2026-08-22** cho toàn bộ run trong phạm vi July-15+ — số trong
`model/**/aggregated.*` khớp chính xác với các bảng ở `evaluation/` và `RESULTS_ANALYSIS.md`.
Mọi run dưới đây đều **đủ 5 fold**.

---

## Trong phạm vi (dùng được cho luận văn)

| Category | Run | Folds | Size / fold |
|---|---|---|---|
| teacher | `teacher/efficientnetv2_m` | 5 | 607 MB |
| teacher | `teacher/convnextv2_base` | 5 | 1,0 GB |
| teacher | `teacher/maxvit_base` | 5 | 1,3 GB |
| student_kd | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 97 MB |
| student_kd | `kd_efficientnetv2_m_to_fastvit_sa12` | 5 | 121 MB |
| student_kd | `kd_efficientnetv2_m_to_efficientformerv2_s2` | 5 | 140 MB |
| student_kd | `kd_efficientnetv2_m_to_repvit_m1_0` | 5 | 74 MB |
| student_no_kd | `baseline_mobilenetv4_conv_medium` | 5 | 97 MB |
| student_no_kd | `baseline_fastvit_sa12` | 5 | 121 MB |
| student_no_kd | `baseline_efficientformerv2_s2` | 5 | 140 MB |
| student_no_kd | `baseline_repvit_m1_0` | 5 | 74 MB |

**Ablation PAD (nhánh ISIC-only):** `experiments/runs_isic_only/teacher/{efficientnetv2_m,
convnextv2_base, maxvit_base}` — 5 fold mỗi teacher; bản sao artifact nằm ở
`model/ablation_pad_isic_only/teacher/<name>/`. **Không kéo `.pth` về Mac** (chỉ cần metrics +
predictions để phân tích, xem `reports/pad_ablation_*.md`).

> `.pth` teacher rất nặng (0,6–1,3 GB/fold). Nếu chỉ cần chạy lại eval/export thì kéo đúng fold cần
> bằng `bash run/pull_results.sh pull ckpt`.

---

## ⚠️ Có trên đĩa nhưng NGOÀI phạm vi — không trích số

| Run | Vì sao loại |
|---|---|
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` (5 fold) | toàn bộ là bản **tháng 6** |
| `kd_convnextv2_base_to_fastvit_sa12` (3 fold `.pth`) | **trộn**: fold_0 train lại 08-13, fold_1..4 vẫn tháng 6 |
| `kd_convnextv2_base_to_efficientformerv2_s2` (2 fold `.pth`) | đang train lại, chưa đủ 5 fold cùng đợt |
| `kd_maxvit_base_to_*` | mới 1–2 fold, bản tháng 6 |
| `kd_efficientnet_b4_to_*`, `baseline_efficientnet_b0`, `baseline_mobilenetv3_large`, `baseline_mobilevit_s`, `teacher/efficientnet_b4` | 4 kiến trúc đã bị **xoá khỏi `src/models/registry.py`** (2026-07-15) — không còn thuộc đề tài, không build lại được |

Các thư mục này được giữ lại làm **hồ sơ lịch sử**. Không chạy `aggregate_folds.py` trên nhóm
"trộn" cho tới khi đủ 5 fold cùng một đợt huấn luyện.

---

## Lấy checkpoint từ server

Training chạy trên box vast.ai `vastnew` (repo `/workspace/skin-cancer-detector`). Các checkpoint
tháng 6–8/2026 có một phần được train trên box `vast` (đã trả lại 2026-08-25) và đã được gộp hết về
`vastnew` trước khi trả.
Đối chiếu + tải về bằng:

```bash
bash run/pull_results.sh            # chỉ kiểm tra: NEW / STALE / SAME / RUNNING
bash run/pull_results.sh pull       # kéo fold mới về
bash run/pull_results.sh pull ckpt  # kèm best_model.pth (mặc định KHÔNG kéo .pth)
```

Script không bao giờ ghi lên server và không bao giờ xoá dưới máy Mac (`stale` sẽ chuyển bản cũ
sang `experiments/_replaced/<timestamp>/`). `last_model.pth` không bao giờ được truyền.
