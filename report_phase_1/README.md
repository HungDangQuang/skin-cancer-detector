> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](../reports/BAO_CAO_TONG_HOP.md).
>
> Lý do: phạm vi "chỉ 1 teacher hợp lệ" (22/08) đã hết đúng — nay có đủ 3 teacher × 4 student.

---

# Report Phase 1 — Skin Cancer Detection via Knowledge Distillation

Tổng hợp kết quả Phase 1 để chuẩn bị **proposal + slide**. Tất cả số liệu trích trực tiếp từ
`experiments/runs/*/aggregated.json` (5-fold CV, test độc lập patient-disjoint).

*Cập nhật: 2026-08-22.*

> ⚠️ **PHẠM VI SỐ LIỆU (đọc trước khi trích bất kỳ con số nào):** báo cáo này **chỉ dùng các run
> huấn luyện từ 15/7/2026 trở đi** — đợt hợp lệ, đồng bộ với bộ model hiện tại. Các run tháng 6
> (KD `convnextv2_base→*`, `maxvit_base→*`, và toàn bộ tier baseline cũ) **đã bị loại**. Hệ quả
> quan trọng: **teacher duy nhất có ma trận KD hợp lệ là `efficientnetv2_m`** → câu hỏi "teacher
> nào tạo student tốt nhất" **chưa trả lời được**. Xem `evaluation/02_model_comparison.md §0`.

---

## Cấu trúc thư mục

```
report_phase_1/
├── README.md                         ← file này (tóm tắt + điều hướng)
├── DE_CUONG.md                       ← đề cương luận văn (bản đầy đủ)
├── SLIDE_CONTENT.md                  ← nội dung 24 slide bảo vệ đề cương
├── SPEAKER_NOTES.md                  ← kịch bản thuyết trình theo từng slide
├── RESULTS_ANALYSIS.md               ← bảng kết quả + cách đọc/phân tích khi bảo vệ
├── model/                            ← checkpoint (symlink) + đánh giá từng model
│   ├── CHECKPOINTS_MANIFEST.md       ← đường dẫn thật mọi checkpoint
│   ├── teacher/  student_kd/  student_no_kd/
├── benchmark/
│   ├── cpu_benchmark/                ← FLOPs + GPU + CPU proxy (server)
│   └── mobile_benchmark/
│       └── pixel6a_ondevice.csv      ← đo thật trên Pixel 6a (2026-07-04)
└── evaluation/
    ├── 01_metrics_explained.md       ← giải thích từng độ đo (vì sao dùng)
    ├── 02_model_comparison.md        ← xếp hạng đầy đủ, model nào tốt hơn
    └── 03_kd_effectiveness.md        ← KD vs baseline, luận điểm KD
```

> Thư mục `model/` chứa **symlink fold_0** (tránh nhân bản checkpoint). Đường dẫn thật của mọi
> fold ở `model/CHECKPOINTS_MANIFEST.md` — lưu ý manifest đang liệt kê một số run **ngoài phạm vi**
> (xem cảnh báo trong file đó).

---

## Bộ model hiện tại (nguồn sự thật: `src/models/registry.py`)

| Vai trò | Model | Ghi chú |
|---|---|---|
| Teacher | `efficientnetv2_m`, `convnextv2_base`, `maxvit_base` | đã train đủ 5 fold |
| Teacher (chưa train) | `panderm` | foundation ViT-B/16 (Nature Medicine 2025), loader đã code |
| Teacher LUPI (chưa train) | `efficientnetv2_m_privileged`, `convnextv2_base_privileged` | metadata đặc quyền (hướng A) |
| Student | `mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2`, `repvit_m1_0` | đã train đủ 5 fold (KD + baseline) |

**Đã loại khỏi đề tài** (xoá khỏi registry 2026-07-15, không build lại được): `efficientnet_b4`,
`efficientnet_b0`, `mobilenetv3_large`, `mobilevit_s`. Mọi kết luận cũ dựa trên các model này
đã bị rút.

---

## Tóm tắt kết quả (headline cho slide)

### 1. PAD-UFES-20 giúp teacher tổng quát hóa — ✅ cả 3 teacher

Ablation có kiểm soát: cùng test set, chỉ khác TRAIN+VAL (`experiments/runs/teacher/*` vs
`experiments/runs_isic_only/teacher/*`). Ô quyết định = **subset ảnh PAD**:

| Teacher | ΔAUPRC | ΔpAUC@80 | ΔSens | ΔSens@95Spec |
|---|---|---|---|---|
| efficientnetv2_m | **+0,1241** | +0,0349 | +0,0756 | +0,1844 |
| convnextv2_base | **+0,0920** | +0,0356 | +0,1256 | +0,1089 |
| maxvit_base | **+0,1311** | +0,0352 | +0,1256 | +0,2322 |

Miền ISIC gốc **trung tính** (Δ trong nhiễu) → thêm PAD **không hại** miền dermoscopy.

### 2. Độ chính xác (mean ± std, 5-fold, test độc lập)

- **Teacher mạnh nhất (standalone):** `maxvit_base` AUPRC **0,6566 ± 0,0211** ≈ `convnextv2_base`
  **0,6506 ± 0,0306** — chênh **trong 1 std**, không tuyên bố tuyệt đối được.
- **Student KD tốt nhất:** `mobilenetv4_conv_medium ← efficientnetv2_m` — pAUC@80 **0,1859**,
  AUC **0,9852**, Sens **0,933** (dẫn đầu cả 3 chỉ số trong nhóm student).
- **AUPRC cao nhất nhóm student KD:** `efficientformerv2_s2 ← efficientnetv2_m` **0,6220 ± 0,0531**.
- **Teacher vẫn hơn student ở AUPRC** (0,63–0,66 vs 0,55–0,62), nhưng **student KD đạt/vượt teacher
  ở pAUC@80 và Sensitivity** dù nhẹ hơn nhiều lần — đúng mục tiêu của KD.

### 3. Hiệu quả KD (KD − Baseline, teacher `efficientnetv2_m`, 4/4 student × 5 fold)

- **pAUC@80: cải thiện 4/4** (+0,0028 → +0,0115).
- **Sensitivity: cải thiện 4/4** (+0,0066 → +0,0124); **Sens@95Spec: 4/4** (+0,0108 → +0,0324).
- **AUPRC: hỗn hợp** — repvit +0,0172, fastvit +0,0127 (dương); mobilenetv4 −0,0045,
  efficientformerv2 −0,0062 (âm nhẹ). **Cả 4 đều nhỏ hơn 1 std → trong nhiễu.**
- → Bằng chứng KD nằm ở **pAUC + độ nhạy**, KHÔNG phải AUPRC. Phải nói đúng như vậy.

### 4. Benchmark on-device (Pixel 6a, `.pte` FP32, 4 threads, đo 2026-07-04)

Latency/size là **thuộc tính kiến trúc** (weight-independent) nên vẫn dùng được sau khi train lại:

| Model | AUPRC (KD ← effv2_m) | median@4t | Size .pte | FPS |
|---|---|---|---|---|
| **mobilenetv4_conv_medium** | 0,6056 | **22,6 ms** | **32,1 MB** | 44 |
| efficientformerv2_s2 | **0,6220** | 42,8 ms | 47,0 MB | 23 |
| fastvit_sa12 | 0,6209 | 65,5 ms | 40,3 MB | 15,3 |
| repvit_m1_0 | 0,5537 | *chưa đo* | *chưa đo* | — |

- **Latency ranking ĐẢO trên mobile:** fastvit chậm nhất (65,5 ms) dù **ít param hơn**
  efficientformerv2 (10,6M vs 12,1M) → phải đo on-device thật, không suy từ FLOPs.
- Model transformer/hybrid bị phạt nặng nhất trên ARM (fastvit 3,4× so với proxy server).

### Khuyến nghị model deploy Phase 1

**`mobilenetv4_conv_medium ← efficientnetv2_m`** — dẫn đầu pAUC@80 / AUC / Sensitivity trong
nhóm student, đồng thời **nhanh nhất và nhẹ nhất** trong 3 model đã đo (22,6 ms / 32,1 MB).
Nếu ưu tiên AUPRC thì `efficientformerv2_s2` cao hơn (0,6220) nhưng chậm gần **gấp đôi** và
`.pte` lớn hơn 15 MB.

---

## Việc còn thiếu (để hoàn thiện luận văn)

| GAP | Nội dung | Ưu tiên |
|---|---|---|
| **Khép Q2** | KD `convnextv2_base` × 4 student (và tùy chọn `maxvit_base`) — train lại **trong đợt mới** để so "teacher nào chưng cất tốt nhất" | 🔴 |
| **Run tháng 6 đang bị đè dở** | `kd_convnextv2_base_to_*` / `kd_maxvit_base_to_*` có fold cũ lẫn fold mới → **không được `aggregate`** cho tới khi đủ 5 fold cùng đợt | 🔴 |
| **Paired t-test** | Đã hứa trong đề cương nhưng **chưa có trong code** (`compare_kd_results.py` chỉ mean±std). Hiện dùng heuristic "Δ < 1 std = trong nhiễu" | 🔴 |
| Export `.pte` | `exports/` đang **rỗng** — chưa có `.pte` nào cho bộ model hiện tại; phải export lại từ checkpoint July-15+ | 🔴 |
| Parity check | `max\|Δlogit\| < 1e-3` giữa `.pte` và PyTorch — chưa xác nhận | 🟡 |
| Benchmark repvit | `repvit_m1_0` chưa có params/FLOPs/latency (không có JSON nào) | 🟡 |
| Cross-domain + fairness | HAM10000 / Fitzpatrick17k — data-layer đã code, **chưa chạy eval** | 🟡 |
| Calibration | `compute_calibration.py` đã có; chưa chạy cho model chốt (cần cho "% nguy cơ" hiển thị trong app) | 🟡 |
| Mobile metrics | Peak RAM + end-to-end latency (chỉ đo được trong app) | ⚪ |

Chi tiết đầy đủ + số ± std: xem `evaluation/` và `benchmark/`. Bản phân tích gốc theo phạm vi
July-15+: [`reports/2026-08-09_model_comparison.md`](../reports/2026-08-09_model_comparison.md) và
[`reports/2026-08-10_research_questions.md`](../reports/2026-08-10_research_questions.md).
