# Kết quả đánh giá ngày 04/10/2026 — bảng số liệu (để kiểm chứng độc lập)

Chỉ gồm bảng metric và kết quả tính hoặc chấm trong ngày 04/10/2026. Mỗi bảng ghi file nguồn trong repo; mọi đường dẫn
tính từ gốc repo. Quy ước: `[a; b]` = khoảng tin cậy 95%; "TB 5 fold" = trung bình 5 model trên cùng tập test; "(tạm)" =
mốc chốt tạm 04/10; CCM = CHƯA CHỨNG MINH. Splits v2 (chia theo bệnh nhân, 22/09/2026).

**Model:**

| Mã | Run-dir (`experiments/runs_newsplit_ddi/`) | Checkpoint | Teacher |
|---|---|---|---|
| P0 (ứng viên ship) | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` | `best_model_auprc.pth` | `teacher/efficientnetv2_m` |
| P1 | `kd_convnextv2_base_to_mobilenetv4_conv_medium__srcsamp` | `best_model_auprc.pth` | `teacher/convnextv2_base` |
| P2 | `kd_efficientnetv2_m_to_repvit_m1_0__srcsamp` | `best_model_auprc.pth` | `teacher/efficientnetv2_m` |

**Mốc (`.claude/skills/eval-results/reference/acceptance-gates.md` §1, §2.1):** S_min 0,80 · Sp_min 0,60 (III-a và
III-b) · δ của C2 = 0,05 × AUPRC của chính teacher, từng miền. Ngưỡng app = `pad_sens90` của fold ship (P0 fold 4:
0,5705).

---

## 1. Chọn ứng viên vòng 2 (chỉ dùng val)

Nguồn: `reports/2026-10-04_candidate2_selection/selection.{md,json}`

| Ứng viên | AUPRC val PAD, TB 5 fold | fold 0 | fold 1 | fold 2 | fold 3 | fold 4 |
|---|---|---|---|---|---|---|
| P0 | 0,8831 | 0,9146 | 0,8593 | 0,8326 | 0,9144 | 0,8946 |
| P1 | 0,8840 | 0,9161 | 0,8771 | 0,8069 | 0,9256 | 0,8944 |
| P2 | 0,8536 | 0,8685 | 0,8458 | 0,7654 | 0,8922 | 0,8962 |

| Kết quả | Giá trị |
|---|---|
| Chênh P1 − P0 | 0,0009 (< biên hoà 0,005) |
| Ứng viên được chọn | P0 |
| Fold ship P0 (trung vị AUPRC toàn bộ val) | fold 4: 0,6296 · 0,6616 · **0,7018** · 0,7688 · 0,7691 |
| Fold ship theo trung vị AUPRC val PAD (R9) | fold 4 |
| Fold ship P1 / P2 (cùng luật) | fold 4 (0,6934) / fold 4 (0,6921) |

## 2. Phán quyết P0 — khung 3 trụ

Nguồn: `reports/2026-10-04_acceptance_verdict_P0_3pillar.md`

| Cổng | Metric | Mốc | Giá trị [95%] | Nhãn |
|---|---|---|---|---|
| I-1 | độ trễ p95 trên `.pte` ship | ≤ 80 ms (đề xuất) | chưa đo | CHƯA ĐO |
| II-1 | max\|Δlogit\| · \|ΔAUPRC\| điện thoại ↔ máy chủ | < 1e-3 · < 0,005 (đề xuất) | 5,245e-06 · 0,0000 | ĐẠT (mốc đề xuất) |
| II-2 | parity · lỗi · trùng bit | PASS · < 0,1% · trùng (đề xuất) | 6,311e-06 · 0/70.883 · 500/500 | ĐẠT (mốc đề xuất) |
| II-3 | tỉ lệ đổi quyết định qua pipeline app | < 0,5% (đề xuất) | chưa đo | CHƯA ĐO |
| III-a | độ nhạy PAD tại ngưỡng app | cận dưới ≥ 0,80 | 165/189 = 0,873 [0,818; 0,913] | ĐẠT (tạm) |
| III-a | độ đặc hiệu PAD tại ngưỡng app | cận dưới ≥ 0,60 | 152/208 = 0,731 [0,667; 0,786] | ĐẠT (tạm) |
| III-b | độ nhạy theo tông, Fitzpatrick17k-C | cận dưới ≥ 0,80 mỗi tông | xem bảng 3 | **KHÔNG ĐẠT (tạm)** |
| III-b | độ đặc hiệu theo tông, Fitzpatrick17k-C | cận dưới ≥ 0,60 mỗi tông | xem bảng 3 | ĐẠT (tạm) |
| C2 | Δ AUPRC student − teacher | cận dưới > −δ mỗi miền | xem bảng 5 | ĐẠT (tạm) |
| **Tổng** | | | | **KHÔNG ĐẠT YÊU CẦU (tạm, khám phá)** |

## 3. III-b theo tông da tại ngưỡng app (fold 4, Wilson 95%)

Nguồn: `reports/2026-10-04_review_v2_checks/output.md` (1); P0 trên Fitzpatrick17k-C còn ở
`reports/2026-10-04_review_v2_checks/tone_at_app_threshold_P0_fitz17kC.txt`. Tập con Fitzpatrick17k-C:
`reports/2026-10-04_review_v2_checks/fitz17kC_headline_image_ids.txt` (3.086 / 4.320 ảnh headline).

| Ứng viên | Tập | Tông | n ác / n lành | Độ nhạy [95%] | Độ đặc hiệu [95%] |
|---|---|---|---|---|---|
| P0 | headline | sáng | 1195 / 1115 | 0,604 [0,576; 0,632] | 0,755 [0,729; 0,779] |
| P0 | headline | trung bình | 757 / 842 | 0,520 [0,485; 0,556] | 0,779 [0,750; 0,806] |
| P0 | headline | tối | 208 / 203 | 0,524 [0,456; 0,591] | 0,808 [0,748; 0,856] |
| P0 | Fitz17k-C | sáng | 934 / 824 | 0,603 [0,571; 0,634] | 0,742 [0,711; 0,770] |
| P0 | Fitz17k-C | trung bình | 559 / 514 | 0,503 [0,461; 0,544] | 0,813 [0,777; 0,845] |
| P0 | Fitz17k-C | tối | 130 / 125 | 0,508 [0,423; 0,592] | 0,824 [0,748; 0,881] |
| P1 | headline | sáng | 1195 / 1115 | 0,711 [0,685; 0,736] | 0,644 [0,615; 0,672] |
| P1 | headline | trung bình | 757 / 842 | 0,670 [0,635; 0,702] | 0,662 [0,629; 0,693] |
| P1 | headline | tối | 208 / 203 | 0,736 [0,672; 0,791] | 0,591 [0,522; 0,656] |
| P1 | Fitz17k-C | sáng | 934 / 824 | 0,706 [0,676; 0,734] | 0,655 [0,622; 0,687] |
| P1 | Fitz17k-C | trung bình | 559 / 514 | 0,646 [0,605; 0,684] | 0,720 [0,680; 0,757] |
| P1 | Fitz17k-C | tối | 130 / 125 | 0,723 [0,641; 0,793] | 0,624 [0,537; 0,704] |
| P2 | headline | sáng | 1195 / 1115 | 0,695 [0,668; 0,720] | 0,612 [0,583; 0,640] |
| P2 | headline | trung bình | 757 / 842 | 0,561 [0,526; 0,596] | 0,673 [0,641; 0,704] |
| P2 | headline | tối | 208 / 203 | 0,572 [0,504; 0,637] | 0,734 [0,669; 0,790] |
| P2 | Fitz17k-C | sáng | 934 / 824 | 0,696 [0,666; 0,725] | 0,609 [0,575; 0,642] |
| P2 | Fitz17k-C | trung bình | 559 / 514 | 0,530 [0,488; 0,571] | 0,714 [0,673; 0,751] |
| P2 | Fitz17k-C | tối | 130 / 125 | 0,546 [0,460; 0,629] | 0,768 [0,687; 0,833] |

Ngưỡng `pad_sens90` fold 4: P0 0,5705 · P1 0,5517 · P2 0,5922 (`reports/2026-10-02_threshold_options/summary.csv`,
`reports/2026-10-04_round2_app_threshold/P{1,2}/summary.csv`).

## 4. III-a tại ngưỡng app (PAD test, fold 4, Wilson 95%)

Nguồn: `reports/2026-10-02_threshold_options/summary.csv`, `reports/2026-10-04_round2_app_threshold/P{1,2}/summary.csv`
(dòng `4,pad_sens90`)

| Ứng viên | Độ nhạy | Độ đặc hiệu | Nhãn |
|---|---|---|---|
| P0 | 165/189 = 0,873 [0,818; 0,913] | 152/208 = 0,731 [0,667; 0,786] | ĐẠT (tạm) |
| P1 | 169/189 = 0,894 [0,842; 0,930] | 147/208 = 0,707 [0,642; 0,764] | ĐẠT (tạm) |
| P2 | 163/189 = 0,862 [0,806; 0,904] | 140/208 = 0,673 [0,607; 0,733] | ĐẠT (tạm) |

## 5. C2 — student không kém teacher quá δ (Δ AUPRC, TB 5 fold, bootstrap ghép cặp B = 2000)

Nguồn: P0 `reports/ci_gates_srcsamp_{indomain,fitzpatrick17k_headline,ham10000_headline}.json`; P1/P2
`reports/ci_cand2_P{1,2}_{indomain,fitzpatrick17k_headline,ham10000_headline}.json` (PAD = hàng `pad_ufes_20`
của `explicit_pairs_by_subgroup`)

| Ứng viên | Miền | AUPRC teacher | δ | Δ (student − teacher) [95%] | Nhãn (tạm) |
|---|---|---|---|---|---|
| P0 | PAD | 0,7966 | 0,0398 | +0,0619 [+0,0396; +0,0852] | ĐẠT |
| P0 | Fitz headline | 0,6954 | 0,0348 | +0,0068 [−0,0008; +0,0146] | ĐẠT |
| P0 | HAM headline | 0,4938 | 0,0247 | +0,0059 [−0,0068; +0,0189] | ĐẠT |
| P1 | PAD | 0,8514 | 0,0426 | +0,0105 [−0,0090; +0,0320] | ĐẠT |
| P1 | Fitz headline | 0,7078 | 0,0354 | −0,0054 [−0,0123; +0,0017] | ĐẠT |
| P1 | HAM headline | 0,4505 | 0,0225 | −0,0064 [−0,0161; +0,0044] | ĐẠT |
| P2 | PAD | 0,7966 | 0,0398 | +0,0084 [−0,0207; +0,0390] | ĐẠT |
| P2 | Fitz headline | 0,6954 | 0,0348 | −0,0270 [−0,0362; −0,0173] | CCM |
| P2 | HAM headline | 0,4938 | 0,0247 | −0,0277 [−0,0434; −0,0109] | CCM |

## 6. C1 — KD − baseline cùng student (Δ AUPRC, TB 5 fold) — chỉ báo cáo

Nguồn: P0 `reports/ci_c1_pad_srcsamp_auprc_indomain.md:62`, `reports/ci_srcsamp_auprc_fitzpatrick17k_headline.md:20`;
P1/P2 `reports/ci_cand2_P{1,2}_*.json`

| Ứng viên | PAD | Fitz headline | HAM headline |
|---|---|---|---|
| P0 | −0,0008 [−0,0199; +0,0187] | +0,0395 [+0,0310; +0,0478] | — |
| P1 | +0,0026 [−0,0169; +0,0231] | +0,0397 [+0,0322; +0,0466] | +0,0559 [+0,0445; +0,0678] |
| P2 | +0,0349 [+0,0051; +0,0650] | +0,0403 [+0,0313; +0,0492] | +0,1296 [+0,1112; +0,1468] |

## 7. Metric báo cáo theo miền (TB 5 fold) — chỉ báo cáo

Nguồn: P0 `reports/2026-10-02_acceptance_verdict_srcsamp.md:29-32`; P1/P2 `reports/ci_cand2_P{1,2}_*.json`
(`fairness_gaps.x_student.per_group`, `per_run.x_student`)

| Ứng viên | ISIC AUC | ISIC pAUC@TPR80 | PAD AUC | PAD AUPRC | PAD sens@spec80 | Fitz sens@spec80 | HAM sens@spec80 |
|---|---|---|---|---|---|---|---|
| P0 | 0,9437 [0,9227; 0,9616] | 0,1580 [0,1418; 0,1730] | — | — | 0,8180 [0,7406; 0,8786] | 0,4946 [0,4699; 0,5178] | 0,7259 [0,7018; 0,7508] |
| P1 | 0,9404 [0,9161; 0,9599] | 0,1542 [0,1346; 0,1707] | 0,8891 [0,8579; 0,9193] | 0,8619 [0,8157; 0,9065] | 0,8571 [0,7811; 0,9101] | 0,4792 [0,4546; 0,5068] | 0,6395 [0,6121; 0,6652] |
| P2 | 0,9412 [0,9181; 0,9603] | 0,1553 [0,1388; 0,1710] | 0,8314 [0,7938; 0,8683] | 0,8049 [0,7491; 0,8583] | 0,7111 [0,6129; 0,7905] | 0,4325 [0,4037; 0,4581] | 0,6758 [0,6480; 0,7007] |

Tham chiếu ngoài: ISIC (Kurtansky 2025) AUC 0,922 · pAUC 0,142; sens@spec80 bác sĩ (Cochrane, chỉ melanoma) 0,81
dermoscopy / 0,47 ảnh lâm sàng.

## 8. R6 — cận dưới B1/B3 của P0 theo seed bootstrap (B = 2000)

Nguồn: `reports/2026-10-04_r6r7/r6_b1_indomain_seed*.json` (`fairness_gaps.x_student.per_group.isic2024`),
`reports/2026-10-04_r6r7/r6_b3_fitz_seed*.json` (`per_run.x_student.sens_at_80spec`)

| Seed | B1 AUC lo (mốc 0,922) | B1 pAUC lo (mốc 0,142) | Nhãn B1 | B3 lo (mốc 0,47) | Nhãn B3 |
|---|---|---|---|---|---|
| 42 | 0,922679 | 0,141796 | CCM | 0,469931 | CCM |
| 1 | 0,922521 | 0,141567 | CCM | 0,469167 | CCM |
| 2 | 0,922965 | 0,142375 | ĐẠT | 0,468964 | CCM |
| 3 | 0,922143 | 0,141606 | CCM | 0,469999 | CCM |
| 4 | 0,921359 | 0,141234 | CCM | 0,469334 | CCM |
| 5 | 0,922333 | 0,141947 | CCM | 0,468103 | CCM |

## 9. R7 — KD cùng công thức với teacher (không sampler theo nguồn, checkpoint chính) − teacher, trên PAD

Nguồn: `reports/2026-10-04_r6r7/r7_kd_ddi_vs_teacher_ddi.md:31,41,52`; `reports/ci_srcsamp_indomain.json`

| So sánh (PAD) | AUC | AUPRC | pAUC@TPR80 | sens@spec80 |
|---|---|---|---|---|
| KD (không sampler) − teacher | +0,0056 [−0,0110; +0,0222] | +0,0032 [−0,0169; +0,0251] | +0,0005 [−0,0103; +0,0105] | +0,0127 [−0,0345; +0,0774] |
| KD có sampler − KD không sampler (đo 30/09) | — | +0,0563 [+0,0391; +0,0748] | — | — |

| Phân rã điểm ước lượng Δ AUPRC PAD của P0 so với teacher (+0,0619) | Giá trị |
|---|---|
| checkpoint AUPRC − checkpoint chính | +0,0023 |
| sampler theo nguồn | +0,0563 |
| KD − teacher (cùng công thức) | +0,0032 |

## 10. R8 — pAUC của dự án so với hàm chấm chính thức ISIC 2024

Nguồn: `reports/2026-10-04_r8_pauc_official/output.csv`

| Phạm vi | Chênh tuyệt đối lớn nhất |
|---|---|
| 19 dòng (17 tập khác nhau) dự đoán của P0: in-domain 5 fold (toàn bộ, ISIC, PAD), HAM và Fitz headline fold 4 | 2,776e-17 |

## 11. R11 — PPV / NPV tại ngưỡng app, P0 fold 4, ảnh PAD, prevalence giả định

Nguồn: `reports/2026-10-04_ppv_npv_app_threshold/output.txt`

| Prevalence | PPV [khoảng bảo thủ] | NPV [khoảng bảo thủ] | Số ảnh bị gắn cờ / 1000 | Trong đó ác |
|---|---|---|---|---|
| 1% | 0,032 [0,024; 0,041] | 0,9982 [0,9973; 0,9989] | 275 | 8,7 |
| 5% | 0,146 [0,114; 0,184] | 0,9909 [0,9858; 0,9942] | 299 | 43,7 |

## 12. R12 — chênh theo tông tại ngưỡng app, P0 fold 4, Fitzpatrick headline (bootstrap theo dòng B = 2000)

Nguồn: `reports/2026-10-04_r12_tone_fixed_threshold/output.md`

| Tông | n ác / n lành | Độ nhạy | Độ đặc hiệu | sens@spec95 |
|---|---|---|---|---|
| sáng | 1195 / 1115 | 0,604 [0,576; 0,631] | 0,755 [0,730; 0,778] | 0,249 [0,204; 0,295] |
| trung bình | 757 / 842 | 0,520 [0,484; 0,556] | 0,779 [0,751; 0,806] | 0,209 [0,156; 0,262] |
| tối | 208 / 203 | 0,524 [0,455; 0,593] | 0,808 [0,750; 0,860] | 0,288 [0,208; 0,380] |

| Chênh (A − B) | Độ nhạy | Độ đặc hiệu | sens@spec95 |
|---|---|---|---|
| sáng − trung bình | +0,084 [+0,039; +0,127] | −0,024 [−0,062; +0,010] | +0,040 [−0,027; +0,116] |
| sáng − tối | +0,080 [+0,004; +0,154] | −0,053 [−0,110; +0,009] | −0,040 [−0,138; +0,059] |
| trung bình − tối | −0,004 [−0,082; +0,073] | −0,029 [−0,089; +0,030] | −0,080 [−0,191; +0,015] |

## 13. Review v2 — D2, D4, D6 (chỉ báo cáo)

Nguồn: `reports/2026-10-04_review_v2_checks/output.md` (2), (3), (4)

**D2 — sens@spec80 theo tông, P0, TB 5 fold (bootstrap B = 1000), so với 0,47:**

| Tập | Sáng | Trung bình | Tối |
|---|---|---|---|
| headline | 0,5207 [0,4865; 0,5528] | 0,4473 [0,4084; 0,4888] | 0,5000 [0,4231; 0,5798] |
| Fitz17k-C | 0,5143 [0,4764; 0,5529] | 0,4723 [0,4228; 0,5264] | 0,5092 [0,3985; 0,5928] |

**D4 — độ nhạy tốt nhất ở độ đặc hiệu ≥ 0,60 và ≥ 0,80, P0 fold 4, ngưỡng chọn trên chính test (bootstrap B = 1000):**

| Tập | Tông | sens@spec60 | sens@spec80 |
|---|---|---|---|
| headline | sáng | 0,742 [0,708; 0,769] | 0,555 [0,514; 0,595] |
| headline | trung bình | 0,696 [0,640; 0,731] | 0,503 [0,448; 0,545] |
| headline | tối | 0,726 [0,657; 0,812] | 0,548 [0,446; 0,651] |
| Fitz17k-C | sáng | 0,743 [0,705; 0,774] | 0,542 [0,485; 0,586] |
| Fitz17k-C | trung bình | 0,691 [0,648; 0,739] | 0,503 [0,452; 0,557] |
| Fitz17k-C | tối | 0,731 [0,644; 0,820] | 0,592 [0,419; 0,688] |

**D6 — cỡ mẫu cho cổng "cận dưới Wilson 95% ≥ mốc", power chính xác:**

| Mốc | Tỉ lệ thật | n nhỏ nhất có power ≥ 0,80 | Power tại n reviewer ước tính |
|---|---|---|---|
| 0,80 | 0,87 | 218 | 0,687 (n = 180) |
| 0,80 | 0,85 | 454 | 0,739 (n = 400) |
| 0,80 | 0,83 | 1312 | 0,745 (n = 1200) |
| 0,60 | 0,73 | 99 | 0,704 (n = 90) |

| Power chung III-a (cả hai ô) | Giá trị |
|---|---|
| 218 ác + 99 lành | 0,8011 × 0,8046 = 0,6446 |
| Cần cho power chung 0,80 | 287 ác + 130 lành (0,8011) |
| n mà 60 giá trị liền sau đều ≥ 0,80 | độ nhạy 241; độ đặc hiệu 111 |

## 14. III-b theo chẩn đoán — P0, Fitzpatrick17k-C (chỉ chẩn đoán)

Nguồn: `reports/2026-10-04_fitz_per_diagnosis/output.md`

| Chẩn đoán | n ác fold 4 | Độ nhạy fold 4 tại ngưỡng app [95%] | Cộng 5 fold (ngưỡng riêng từng fold) | AUC student | AUC teacher effnet | AUC teacher convnext |
|---|---|---|---|---|---|---|
| basal cell carcinoma | 404 | 0,678 [0,631; 0,722] | 0,801 | 0,792 | 0,761 | 0,783 |
| squamous cell carcinoma | 348 | 0,664 [0,613; 0,711] | 0,796 | 0,784 | 0,767 | 0,779 |
| melanoma | 167 | 0,539 [0,463; 0,613] | 0,630 | 0,665 | 0,641 | 0,697 |
| mycosis fungoides | 137 | 0,299 [0,229; 0,381] | 0,491 | 0,581 | 0,541 | 0,602 |
| actinic keratosis | 136 | 0,360 [0,284; 0,444] | 0,546 | 0,611 | 0,624 | 0,623 |
| superficial spreading melanoma | 104 | 0,500 [0,406; 0,594] | 0,525 | 0,602 | 0,569 | 0,667 |
| kaposi sarcoma | 96 | 0,323 [0,238; 0,422] | 0,479 | 0,586 | 0,590 | 0,590 |
| malignant melanoma | 87 | 0,586 [0,481; 0,684] | 0,577 | 0,653 | 0,633 | 0,653 |
| lentigo maligna | 58 | 0,466 [0,343; 0,592] | 0,555 | 0,603 | 0,616 | 0,657 |
| BCC morpheiform | 46 | 0,717 [0,575; 0,827] | 0,852 | 0,832 | 0,824 | 0,868 |
| solid cystic BCC | 40 | 0,775 [0,625; 0,877] | 0,875 | 0,839 | 0,833 | 0,864 |

| Bỏ khỏi nhóm ác (chỉ chẩn đoán) | Độ nhạy sáng · trung bình · tối [95%] | n ác còn lại |
|---|---|---|
| không bỏ | 0,603 [0,571; 0,634] · 0,503 [0,461; 0,544] · 0,508 [0,423; 0,592] | 934 · 559 · 130 |
| actinic keratosis | 0,624 [0,591; 0,656] · 0,521 [0,478; 0,564] · 0,516 [0,429; 0,603] | 845 · 520 · 122 |
| mycosis fungoides + kaposi sarcoma | 0,633 [0,599; 0,665] · 0,557 [0,511; 0,602] · 0,566 [0,467; 0,659] | 833 · 458 · 99 |
| cả ba | 0,660 [0,625; 0,693] · 0,585 [0,537; 0,631] · 0,582 [0,480; 0,678] | 744 · 419 · 91 |

| Nhãn train | Giá trị | Nguồn |
|---|---|---|
| ACK (PAD) | lành (0) | `configs/data/pad_ufes_20.yaml:19` |
| actinic keratosis (DDI) | lành (4 ảnh) | `data/raw/DDI/ddidiversedermatologyimages.zip` → `ddi_metadata.csv` |
| mycosis fungoides / kaposi sarcoma (DDI) | ác (32 / 6 ảnh) | như trên |
| Tông da Fitzpatrick | sáng I–II · trung bình III–IV · tối V–VI | `configs/data/fitzpatrick17k.yaml:41-44` |
