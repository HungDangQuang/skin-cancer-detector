# Phán quyết cổng chấp nhận — ứng viên ship `__srcsamp` (viết 02/10/2026)

> Hợp đồng: `.claude/skills/eval-results/reference/acceptance-gates.md`. Tối 01/10/2026 tác giả chốt
> **mục tiêu B2 = B4 = 0,81** và **metric C2 = ΔAUPRC**. Đây là quyết định **post-hoc**: chốt sau khi đã thấy
> kết quả bên dưới. Ký hiệu: CCM = CHƯA CHỨNG MINH; cờ `⚑` = mốc còn ĐỀ XUẤT, tức cổng mang thêm
> `CHƯA CÓ TIÊU CHÍ CHỐT` (§3 bước 3).

### Cổng chấp nhận (theo .claude/skills/eval-results/reference/acceptance-gates.md)
Model được chấm: `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` · fold 4 (cổng A) / CI 5 fold (cổng B, C) · `best_model_auprc.pth` · splits v2
Trạng thái mốc: B2, B4 (mục tiêu 0,81) và metric C2 **ĐÃ CHỐT tối 01/10/2026, post-hoc**; các mốc còn lại ĐỀ XUẤT

| Cổng | Metric | Mốc | Giá trị [CI 95%] | Nguồn | Nhãn |
|---|---|---|---|---|---|
| A1 | độ trễ sau 5 phút, Pixel 6a, 4 luồng, **trên `.pte` ship** | ≤ 80 ms ⚑ | chưa đo trên `.pte` ship. Số tham khảo theo kiến trúc (`.pte` khác, 27/08): 39,5 ms | `reports/ondevice_latency.csv:22` | **CHƯA ĐO** ⚑ |
| A3 | điện thoại ↔ máy chủ | max\|Δlogit\| < 1e-3 · \|ΔAUPRC\| < 0,005 ⚑ | 5,245e-06 · 0,0000 | `reports/2026-10-01_pixel6a_srcsamp_vs_mobile.md` §1 | ĐẠT so với mốc đề xuất ⚑ |
| A4 | parity + không lỗi + tất định | lỗi < 0,1% · trùng bit ⚑ | parity PASS 6,311e-06 · 0/70.883 lỗi · 500/500 trùng bit | như trên; `reports/mobile_benchmark/parity_mobilenetv4_conv_medium__srcsamp_auprc_fold4.json` | ĐẠT so với mốc đề xuất ⚑ |
| B1 | ISIC: AUC · pAUC | ≥ 0,922 · ≥ 0,142 ⚑ | 0,9437 [0,9227, 0,9616] · 0,1580 [0,1418, 0,1730] | `reports/ci_gates_srcsamp_indomain.md:40` | CCM so với mốc đề xuất ⚑ |
| B2 | PAD: sens@spec80 | **≥ 0,81 (đã chốt)** | 0,8180 [0,7406, 0,8786] | `reports/ci_gates_srcsamp_indomain.md:41` | **CCM** |
| B3 | Fitzpatrick17k: sens@spec80 | ≥ 0,47 ⚑ | 0,4946 [0,4699, 0,5178] | `reports/ci_gates_srcsamp_fitzpatrick17k_headline.md:11` | CCM so với mốc đề xuất ⚑ |
| B4 | HAM10000: sens@spec80 | **≥ 0,81 (đã chốt)** | 0,7259 [0,7018, **0,7508**] | `reports/ci_gates_srcsamp_ham10000_headline.md:11` | **KHÔNG ĐẠT** |
| C2 | student − teacher, **ΔAUPRC (đã chốt)**, `lo > 0` trên PAD·Fitz·HAM ⚑ | > 0 | PAD +0,0619 [+0,0396, +0,0852] · Fitz +0,0068 [−0,0008, +0,0146] · HAM +0,0059 [−0,0068, +0,0189] | `ci_gates_srcsamp_indomain.md:52`; `…_fitzpatrick17k_headline.md:20`; `…_ham10000_headline.md:20` | CCM ⚑ |
| C4a | từng nhóm tông da: sens@spec80 | ≥ 0,47 ⚑ | tối 0,5000 [0,4248, 0,5837] · sáng 0,5207 [0,4886, 0,5554] · trung bình 0,4473 [0,4077, 0,4861] | `…_fitzpatrick17k_headline.md:30-32` | CCM so với mốc đề xuất ⚑ |
| C1 (báo cáo) | KD − baseline, ΔAUPRC | > 0 trên PAD và Fitz ⚑ | PAD −0,0008 [−0,0199, +0,0187] · Fitz +0,0395 [+0,0310, +0,0478] | `reports/ci_c1_pad_srcsamp_auprc_indomain.md:62`; `reports/ci_srcsamp_auprc_fitzpatrick17k_headline.md:20` | CCM ⚑ (PAD) |
| C4b (báo cáo) | chênh AUC giữa các nhóm tông | ±0,02 ⚑ (tham khảo) | tối−sáng +0,0019 [−0,0450, +0,0464] · tối−trung bình +0,0428 [−0,0068, +0,0885] · sáng−trung bình +0,0409 [+0,0119, +0,0708] (khác 0 có ý nghĩa — hạn chế) | `…_fitzpatrick17k_headline.md:33-35` | CCM (tham khảo), cả 3 cặp |
| A2, C3 | bộ nhớ · nén | báo cáo | 208–257 MiB (16 model, theo kiến trúc) · 1,653 GFLOPs | `thesis/LUAN_VAN.md:2053`; `reports/benchmark/mobilenetv4_conv_medium.json:8` | báo cáo |

Hành vi tại ngưỡng val (theo miền):
- ngưỡng toàn cục 0,2272: PAD lành bị gắn cờ 207/208, PAD ác bắt 189/189; ISIC ác bắt 57/76;
  specificity HAM 0,0927, Fitzpatrick 0,0014;
- ngưỡng ảnh điện thoại `phone_sens90` 0,5705 (post-hoc): test PAD độ nhạy 0,873 / độ đặc hiệu 0,731
  (`reports/2026-10-01_pad_threshold/summary.csv`).

Sáu tiêu chí:
1. Evaluation (B1–B3) → CCM.
2. Vượt teacher (C2) → CCM.
3. Tốc độ (A1) → CHƯA ĐO trên `.pte` ship.
4. Chạy được trên mobile (A3 + A4) → ĐẠT so với mốc đề xuất; chưa phủ camera thật / app thật (L3).
5. Tông da (C4a) → CCM.
6. HAM10000 (B4) → **KHÔNG ĐẠT**.

Ứng viên định trước? Có: checkpoint AUPRC chốt trước, fold 4 chọn theo val AUPRC trung vị. Các mốc chốt post-hoc.

**Phán quyết tổng: KHÔNG ĐẠT YÊU CẦU.** Lý do: B4 là cổng bắt buộc, mốc đã chốt, và cả khoảng CI nằm dưới
0,81 (`acceptance-gates.md` §3 bước 4, mục 1). Các cổng ⚑ không đổi được kết luận này.

Lệnh còn thiếu để đo đủ:
- A1 và A2 trên chính `.pte` ship;
- L3: `docs/L3_CAMERA_EVAL_GUIDE.md`.

Hướng tiếp theo: `docs/NEXT_DIRECTION_2026-10-02.md`.
