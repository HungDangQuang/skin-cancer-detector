# R10 — Các lần đã mở tập test PAD / HAM10000 / Fitzpatrick17k trên splits v2 (để khai trong luận văn)

Việc R10 trong `docs/PROGRESS.md`. Phạm vi: từ khi có splits v2 (22/09/2026) đến 04/10/2026. Splits v1 (ma trận 140
fold-run, rò rỉ bệnh nhân) không liệt kê; tập test v1 khác tập test v2.

**Nguồn và độ phân giải thời gian:**
- Từ 30/09: tên file log `start_log` trên server (`logs/evaluate_external_<ts>.log`, `logs/bootstrap_ci_<ts>.log`,
  giờ UTC; đồng hồ server = UTC, lệch Mac ≤ ~1 s khi kiểm 04/10). Log trước 30/09 không còn trên box hiện tại.
- Trước 30/09: ngày ghi trong `docs/domain_aug_plan.md` §5 (dòng 201–209) và §6 (dòng 238–250); không có giờ.
- "Mở" = có lệnh tính metric trên tập test mà kết quả được người hoặc assistant đọc. Trainer tự ghi
  `test_metrics*.json` khi train xong từng fold; các file đó chỉ tính là "mở" khi có người đọc.

| # | Ngày (UTC) | Ứng viên / arm | Tập test | Mục đích | Nguồn |
|---|---|---|---|---|---|
| 1 | 23/09 | arm `light` (đối chứng v2) và arm `domain`: teacher · baseline · KD `efficientnetv2_m → mobilenetv4` | in-domain (ISIC + PAD) | so sánh arm | `docs/domain_aug_plan.md:206` |
| 2 | 24/09 | như #1 | HAM headline; Fitz 4 biến thể; paired CI | so sánh arm (`domain` thất bại) | `docs/domain_aug_plan.md:207-209`; `reports/ci_newsplit_*.md` |
| 3 | 26/09 | arm DDI: teacher · baseline · KD | in-domain; HAM headline; Fitz 4 biến thể; paired CI | so sánh arm (DDI thành công) | `docs/domain_aug_plan.md:249-250`; `reports/ci_ddi_*.md` |
| 4 | 30/09 21:04–21:33 | arm `__srcsamp` (sẽ thành P0): KD + baseline, checkpoint chính **và** `_auprc` | in-domain (theo nguồn); HAM headline; Fitz 4 biến thể | item 2+3 (sampler theo nguồn, checkpoint AUPRC) | log `evaluate_external_20260930_2116…2122`, `bootstrap_ci_20260930_2104…2133`; `reports/ci_srcsamp_*` |
| 5 | 01/10 ~15:12 | P0 fold 4 vs `__mobile` fold 0 | in-domain; HAM; Fitz | so sánh bản Pixel cũ với bản ship | log `bootstrap_ci_20261001_1512…1513`; `reports/2026-10-01_pixel6a_srcsamp_vs_mobile.md` |
| 6 | 01/10 ~15:38–15:44 | P0 vs teacher `efficientnetv2_m` | in-domain (theo nguồn); HAM; Fitz theo tông | **cổng chấp nhận lần đầu** (B1–B4, C2, C4a) | log `bootstrap_ci_20261001_1538…1543`; `reports/ci_gates_srcsamp_*` |
| 7 | 01/10 | P0, 3 điểm vận hành trên val PAD | **test PAD** (5 fold, chú trọng fold 4); Fitz tại `pad_sens90` | chọn ngưỡng app | `reports/2026-10-01_pad_threshold/` (commit `2a732be`) |
| 8 | 02/10 ~00:21 | P0 KD vs baseline | in-domain theo nguồn (ô PAD) | C1 PAD | log `bootstrap_ci_20261002_002125`; `reports/2026-10-02_c1_pad_cell_srcsamp.md` |
| 9 | 02/10 | mọi run cây v2 (`light`, `domain`, `ddi`, `ddi_auprc`) | in-domain (sens/spec tại ngưỡng val) | tính bù `valthr_*` | `reports/valthr/` (commit `1272536`) |
| 10 | 02/10 | P0, 7 quy tắc ngưỡng × 5 fold | test PAD; Fitz headline; test ISIC | phương án ngưỡng app (`pad_sens90` được giữ 03/10) | `reports/2026-10-02_threshold_options/` (commit `deae77b`) |
| 11 | 03/10 01:36–01:43 | P0 checkpoint AUPRC vs checkpoint pAUC | in-domain theo nguồn; HAM; Fitz | R2 (item 3) | log `bootstrap_ci_20261003_0136…0143`; `reports/2026-10-03_item3_ckpt_paired.md` |
| 12 | 03/10 | P0 | in-domain (bootstrap theo bệnh nhân); Fitz theo tông tại ngưỡng app | kiểm theo review luận văn | `reports/2026-10-03_thesis_review_checks/` (commit `efc1a9c`) |
| 13 | 04/10 00:25 | **P1** (KD `convnextv2_base → mobilenetv4`) fold 4 | in-domain (dòng metric tổng, checkpoint `_auprc`) | **vô tình**: assistant `tail` log driver để kiểm job xong chưa; trước N1. Không chép số, không chuyển cho tác giả | `docs/PREREG_CANDIDATE2_2026-10-02.md` §10; `docs/PROGRESS.md` §6 |
| 14 | 04/10 00:33 → | P1, P2, baseline `repvit_m1_0`, teacher `convnextv2_base` | in-domain; HAM headline; Fitz 4 biến thể; paired CI | N2–N4 vòng 2, **chỉ báo cáo** — sau commit N1 `c61bab2` (00:32:51) | log `evaluate_external_20261004_0033…`; driver `.tmp/cand2_eval.sh` (server) |
| 15 | 04/10 00:35 → | P0-era: KD `__ddi` (không sampler theo nguồn) vs teacher; P0 B1/B3 với 6 seed | in-domain theo nguồn; Fitz | R7, R6 (bootstrap lại file dự đoán đã có, không có model mới) | log `bootstrap_ci_20261004_003508…`; driver `.tmp/r6r7.sh` (server) |

**Hệ quả cần khai trong luận văn:**
- **Test PAD** (397 ảnh, chung cho mọi fold) đã được nhìn ít nhất ở #1, #3, #4–#12. Ngưỡng app `pad_sens90` được chọn
  sau #7 ⇒ III-a của P0 là post-hoc.
- **Fitzpatrick** đã được nhìn ở #2–#7, #10–#12, trong đó có số tại ngưỡng app (#7, #10, #12) ⇒ III-b của P0 là post-hoc.
- **HAM** đã được nhìn ở #2–#6, #11; B4 chuyển sang báo cáo **sau** khi thấy kết quả (02/10).
- Vòng 2: luật chọn chỉ dùng val, commit trước #14. Có #13 (một dòng metric tổng in-domain của P1 fold 4, trước N1),
  đã khai. Hai cặp vòng 2 được chọn có tham khảo số HAM/Fitz của **splits v1** (prereg §7.4).
- Không tập test v2 nào còn "chưa ai chạm" ⇒ một kết luận xác nhận cần tập mới (`docs/PROGRESS.md` U8).

**Chưa verify được:** giờ chính xác của #1–#3 và #7, #9, #10, #12 (chỉ biết ngày); log trước 30/09 không còn trên box.
Bảng có thể sót các lượt mở ad-hoc không để lại log hay commit (ví dụ lệnh `python -c` đọc `test_metrics.json` trong
một phiên hội thoại).
