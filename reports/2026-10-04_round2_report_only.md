# Vòng chọn thứ hai — kết quả test của P1 / P2 (CHỈ BÁO CÁO, không phán quyết)

> N2 + N3 + N4 trong `docs/PROGRESS.md`, prereg `docs/PREREG_CANDIDATE2_2026-10-02.md` §5: "Chấm cả ba cặp trên các
> tập kiểm để báo cáo, nhưng **chỉ** ứng viên chọn ở §4 nhận phán quyết." Ứng viên được chọn là **P0**
> (`reports/2026-10-04_candidate2_selection/`, commit `c61bab2`); phán quyết của P0:
> `reports/2026-10-04_acceptance_verdict_P0_3pillar.md`.
>
> **Không được dùng bảng này để đổi ứng viên.** Các số dưới đây được mở **sau** khi chọn; chọn P1 hay P2 từ đây là
> chọn trên tập test (`acceptance-gates.md` §4 #9, #18). Nhãn trong ngoặc chỉ để đọc nhanh theo mốc chốt tạm 04/10.

- P1 = KD `convnextv2_base → mobilenetv4_conv_medium` `__srcsamp`; teacher `teacher/convnextv2_base`; baseline
  `baseline_mobilenetv4_conv_medium__srcsamp`.
- P2 = KD `efficientnetv2_m → repvit_m1_0` `__srcsamp`; teacher `teacher/efficientnetv2_m`; baseline
  `baseline_repvit_m1_0__srcsamp`.
- Student và baseline: checkpoint `best_model_auprc.pth`; teacher: checkpoint chính. Splits v2, `runs_newsplit_ddi`.
- CI: paired bootstrap, B = 2000, seed 42, trung bình 5 fold trên cùng replicate — `reports/ci_cand2_P{1,2}_*.md`
  (driver `.tmp/cand2_eval.sh` trên server, chạy 04/10 00:33–01:14 UTC). Eval ngoài miền: student/baseline trong
  `reports/external_newsplit_srcsamp_auprc/`, teacher `convnextv2_base` trong `reports/external_newsplit_ddi/`.

## 1. C2 — student không kém teacher quá δ (ΔAUPRC, cận dưới > −δ)

δ = 0,05 × AUPRC của chính teacher (trung bình 5 fold, checkpoint chính), không làm tròn.

| | Miền | AUPRC teacher | δ | Δ(student − teacher) [95%] | Nhãn (tạm) |
|---|---|---|---|---|---|
| P1 | PAD | 0,8514 | 0,0426 | +0,0105 [−0,0090; +0,0320] | ĐẠT |
| P1 | Fitzpatrick | 0,7078 | 0,0354 | −0,0054 [−0,0123; +0,0017] | ĐẠT |
| P1 | HAM10000 | 0,4505 | 0,0225 | −0,0064 [−0,0161; +0,0044] | ĐẠT |
| P2 | PAD | 0,7966 | 0,0398 | +0,0084 [−0,0207; +0,0390] | ĐẠT |
| P2 | Fitzpatrick | 0,6954 | 0,0348 | −0,0270 [−0,0362; −0,0173] | CCM |
| P2 | HAM10000 | 0,4938 | 0,0247 | −0,0277 [−0,0434; −0,0109] | CCM |

P1 C2 ĐẠT (tạm); P2 C2 CHƯA CHỨNG MINH (tạm) — student repvit **kém teacher có ý nghĩa** trên Fitz và HAM (cả khoảng
< 0), chỉ chưa rõ có kém quá δ không. Teacher của P1/P2 cũng train không có sampler theo nguồn (lệch công thức như P0,
xem `reports/2026-10-04_r6r7/README.md` R7).

## 2. C1 — KD có giúp không (KD − baseline cùng student, ΔAUPRC, > 0)

| | PAD | Fitzpatrick | HAM10000 |
|---|---|---|---|
| P1 (mobilenetv4) | +0,0026 [−0,0169; +0,0231] | **+0,0397 [+0,0322; +0,0466]** | **+0,0559 [+0,0445; +0,0678]** |
| P2 (repvit) | **+0,0349 [+0,0051; +0,0650]** | **+0,0403 [+0,0313; +0,0492]** | **+0,1296 [+0,1112; +0,1468]** |

In đậm = khoảng loại trừ 0. Trên PAD, KD với student mobilenetv4 không phân biệt được với baseline ở cả P0 (−0,0008,
`reports/2026-10-02_c1_pad_cell_srcsamp.md`) và P1; với student repvit thì dương.

## 3. III — tại ngưỡng app của chính ứng viên (fold ship, `pad_sens90`)

Fold ship theo luật của P0 (trung vị AUPRC toàn bộ val, `val_metrics_auprc.json`): **fold 4** cho cả P1 (0,6934) và P2
(0,6921). Ngưỡng `pad_sens90` của fold 4: P1 0,5517 · P2 0,5922. Tính bằng hai script R13
(`reports/2026-10-04_round2_app_threshold/P{1,2}/`). Wilson 95%, một fold. Wilson của III-a (PAD) tính từ số đếm ở dòng
`4,pad_sens90` của `P{1,2}/summary.csv` (P1: độ nhạy 169/189, độ đặc hiệu (208 − 61)/208 = 147/208; P2: 163/189,
140/208), chưa lưu thành file riêng. P2 đạt III-a với biên rất sát: cận dưới 0,806 và 0,607 so với mốc 0,80 và 0,60.

| | III-a PAD độ nhạy | III-a PAD độ đặc hiệu | III-b Fitz độ nhạy sáng · trung bình · tối | III-b Fitz độ đặc hiệu sáng · trung bình · tối |
|---|---|---|---|---|
| P0 (tham chiếu) | 0,873 [0,818; 0,913] | 0,731 [0,667; 0,786] | 0,604 [0,576; 0,632] · 0,520 [0,485; 0,556] · 0,524 [0,456; 0,591] | 0,755 [0,729; 0,779] · 0,779 [0,750; 0,806] · 0,808 [0,748; 0,856] |
| P1 | 0,894 [0,842; 0,930] | 0,707 [0,642; 0,764] | 0,711 [0,685; 0,736] · 0,670 [0,635; 0,702] · 0,736 [0,672; 0,791] | 0,644 [0,615; 0,672] · 0,662 [0,629; 0,693] · 0,591 [0,522; 0,656] |
| P2 | 0,862 [0,806; 0,904] | 0,673 [0,607; 0,733] | 0,695 [0,668; 0,720] · 0,561 [0,526; 0,596] · 0,572 [0,504; 0,637] | 0,612 [0,583; 0,640] · 0,673 [0,641; 0,704] · 0,734 [0,669; 0,790] |

Theo mốc tạm (S_min 0,80, Sp_min 0,60): **cả ba ứng viên đạt III-a và trượt III-b** (cận trên độ nhạy của mọi tông
< 0,80). P1 gần nhất (cận trên tông tối 0,791), đổi lại độ đặc hiệu thấp hơn (tông tối 0,591 [0,522; 0,656] — cắt qua
0,60). Không ứng viên nào của vòng 2 đóng được khoảng hụt III-b.

## 4. Báo cáo kèm — độ nhạy @ độ đặc hiệu 80% (trung bình 5 fold)

| | PAD (B2, tham chiếu 0,81 / 0,47) | Fitzpatrick (B3, sàn 0,47) | HAM10000 (B4, 0,81) |
|---|---|---|---|
| P0 | 0,8180 [0,7406; 0,8786] | 0,4946 [0,4699; 0,5178] | 0,7259 [0,7018; 0,7508] |
| P1 | 0,8571 [0,7811; 0,9101] | 0,4792 [0,4546; 0,5068] | 0,6395 [0,6121; 0,6652] |
| P2 | 0,7111 [0,6129; 0,7905] | 0,4325 [0,4037; 0,4581] | 0,6758 [0,6480; 0,7007] |

Nguồn P0: `reports/2026-10-02_acceptance_verdict_srcsamp.md:30-32`; P1/P2: `reports/ci_cand2_P{1,2}_*.json`
(`fairness_gaps.x_student.per_group.pad_ufes_20`; `per_run.x_student`).

## Khai báo

- Thứ tự: luật chọn chạy trên val và commit (`c61bab2`, 00:32:51 UTC) trước khi driver đọc file test (00:33:02 UTC, đồng
  hồ server; so hai đồng hồ lúc 00:34 UTC lệch ≤ ~2 s, gồm cả độ trễ ssh). Ngoại lệ: một dòng metric test tổng in-domain của P1 fold 4 đã bị assistant
  nhìn thấy qua `tail` lúc ~00:25 UTC (prereg §10; `reports/2026-10-04_test_set_openings.md` #13).
- Hai cặp P1/P2 được chọn có tham khảo số HAM/Fitz của splits v1 (prereg §7.4). Mốc S_min/Sp_min/δ được chốt tạm
  trước khi mở test vòng 2. Với P2, các nhãn ở đây là tiên nghiệm theo mốc tạm. Với P1, nhãn mang một phần nhỏ
  post-hoc, vì dòng test của P1 fold 4 đã bị assistant nhìn thấy trước khi chốt (prereg §10). Cả hai chỉ để báo cáo.
- Chưa báo cáo ở đây: B1, C4b (có trong `reports/ci_cand2_P{1,2}_*` → `fairness_gaps.x_student`), C3/A2 (theo kiến
  trúc, `reports/benchmark/`).
- Chưa có: `.pte`, parity, độ trễ cho P1/P2 (không cần vì không được chọn).
