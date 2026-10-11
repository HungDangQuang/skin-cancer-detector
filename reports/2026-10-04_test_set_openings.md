# R10 — Các lần đã mở tập test PAD / HAM10000 / Fitzpatrick17k trên splits v2 (để khai trong luận văn)

Việc R10 trong `docs/PROGRESS.md`. Phạm vi: từ khi có splits v2 (22/09/2026) đến 04/10/2026. Splits v1 (ma trận 140
fold-run, rò rỉ bệnh nhân) không liệt kê; tập test v1 khác tập test v2.

**Nguồn và độ phân giải thời gian:**
- Từ 30/09: tên file log `start_log` trên server (`logs/evaluate_external_<ts>.log`, `logs/bootstrap_ci_<ts>.log`,
  giờ UTC; đồng hồ server = UTC, lệch Mac ≤ ~2 s khi so lúc 00:34 UTC 04/10, gồm cả độ trễ ssh). Log trước 30/09 không còn trên box hiện tại.
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
| 14 | 04/10 00:33 → | P1, P2, baseline `repvit_m1_0`, teacher `convnextv2_base` | in-domain; HAM headline; Fitz 4 biến thể; paired CI | N2–N4 vòng 2, **chỉ báo cáo** (kèm III-a/III-b tại ngưỡng app cho P1/P2, `reports/2026-10-04_round2_app_threshold/`) — sau commit N1 `c61bab2` (00:32:51) | log `evaluate_external_20261004_0033…`; driver `.tmp/cand2_eval.sh` (server) |
| 15 | 04/10 00:35 → | P0-era: KD `__ddi` (không sampler theo nguồn) vs teacher; P0 B1/B3 với 6 seed | in-domain theo nguồn; Fitz | R7, R6 (bootstrap lại file dự đoán đã có, không có model mới) | log `bootstrap_ci_20261004_003508…`; driver `.tmp/r6r7.sh` (server) |
| 16 | 04/10 (sau #14; giờ chưa ghi) | P0 `_auprc` 5 fold; HAM, Fitz headline fold 4 | in-domain (toàn bộ, ISIC, PAD); HAM; Fitz | R8 — so hàm pAUC với hàm chấm chính thức (chỉ so định nghĩa) | `reports/2026-10-04_r8_pauc_official/output.csv` |
| 17 | 04/10 (sau #14; giờ chưa ghi) | P0 fold 4 | Fitz headline theo tông, tại ngưỡng app | R12 — chênh giữa tông, bootstrap | `reports/2026-10-04_r12_tone_fixed_threshold/` |
| 18 | 04/10 (~13:20 giờ VN; giờ chính xác chưa ghi) | P0, P1, P2 fold 4; P0 5 fold | Fitz headline + tập con Fitzpatrick17k-C theo tông, tại ngưỡng app; sens@spec60/80 | review v2 (D2, D4, 🔍 2.4) — sau đó tác giả đổi tập chấm III-b sang Fitzpatrick17k-C | `reports/2026-10-04_review_v2_checks/` |

**Hệ quả cần khai trong luận văn:**
- **Test PAD** (397 ảnh, chung cho mọi fold) đã được nhìn ít nhất ở #1, #3, #4–#12, #16. Ngưỡng app `pad_sens90` được chọn
  sau #7 ⇒ III-a của P0 là post-hoc.
- **Fitzpatrick** đã được nhìn ở #2–#7, #10–#12, #16–#18, trong đó có số tại ngưỡng app (#7, #10, #12) ⇒ III-b của P0 là post-hoc.
- **HAM** đã được nhìn ở #2–#6, #11; B4 chuyển sang báo cáo **sau** khi thấy kết quả (02/10).
- Vòng 2: luật chọn chỉ dùng val, commit trước #14. Có #13 (một dòng metric tổng in-domain của P1 fold 4, trước N1),
  đã khai. Hai cặp vòng 2 được chọn có tham khảo số HAM/Fitz của **splits v1** (prereg §7.4).
- Không tập test v2 nào còn "chưa ai chạm" ⇒ một kết luận xác nhận cần tập mới (`docs/PROGRESS.md` U8).

**Chưa verify được:** giờ chính xác của #1–#3 và #7, #9, #10, #12, #16, #17, #18 (chỉ biết ngày); log trước 30/09 không còn trên box.
Bảng có thể sót các lượt mở ad-hoc không để lại log hay commit (ví dụ lệnh `python -c` đọc `test_metrics.json` trong
một phiên hội thoại).

## Bổ sung 11/10/2026 — thử CPUBone-B1 (P3, `docs/PREREG_CPUBONE_2026-10-10.md`)

Luật chọn chỉ dùng val, commit `6475d76` lúc 03:26:19 UTC 11/10, trước mọi lượt dưới đây. Giờ theo tên log `start_log` trên
server (UTC); #21 chạy trên Mac (giờ mtime file, +0700).

| # | Ngày giờ (UTC) | Ứng viên / arm | Tập test | Mục đích | Nguồn |
|---|---|---|---|---|---|
| 19 | 11/10 03:26–03:38 | P3 + `baseline_cpubone_b1__srcsamp` (`_auprc`), teacher `efficientnetv2_m` | in-domain (theo nguồn); HAM headline; Fitz 4 biến thể (theo tông) | prereg §5: aggregate, eval ngoài miền, CI C1/C2 | `logs/{aggregate,evaluate_external,bootstrap_ci}_20261011_03*.log`; `reports/ci_cpubone_P3_*` |
| 20 | 11/10 04:38–04:39 | P3, P0 | HAM headline; Fitz headline (theo tông) | khám phá, post-hoc: P3 − P0 ngoài miền | `logs/bootstrap_ci_20261011_0438*.log`; `reports/ci_cpubone_P3vsP0_*` |
| 21 | 11/10 05:07 (12:07 +0700, Mac) | P3 fold 4 | PAD, Fitz headline + Fitzpatrick17k-C theo tông, ISIC, tại ngưỡng app | khám phá: III-a/III-b như vòng 2 | `reports/2026-10-11_cpubone_app_threshold/P3/` |
| 22 | 11/10 05:08–05:21 | P0, P1, P2, P3 | in-domain (theo nguồn); HAM headline; Fitz 4 biến thể (theo tông) | khám phá: P3 so với P0/P1/P2 | `logs/bootstrap_ci_20261011_05*.log`; `reports/ci_cpubone_P3vsAll_*` |

Không có lượt nào đổi lựa chọn P0. Trước #19 assistant chỉ đọc `selection.md` (val) và `run/progress.sh` (val pAUC); log
train (in số test cuối mỗi fold) không được `tail`.
