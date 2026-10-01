# Item 2 (sampler theo nguồn) + item 3 (checkpoint theo AUPRC) — kết quả

> **Trạng thái:** đã qua một lượt kiểm chéo (2 verifier, 01/10/2026). Các dòng sửa SAU kiểm chéo — câu kết luận
> §2, ghi chú §3.1/§3.2, khối số theo nguồn ở §4, cột prevalence và ghi chú §6, mục 8 — chưa được agent nào kiểm lại.
>
> Brief và tiêu chí đăng ký trước: `docs/TASK_ITEM2_3_source_sampler_ship_ckpt.md` §3.
> Arm mới: `experiments/runs_newsplit_ddi/{kd_efficientnetv2_m_to_mobilenetv4_conv_medium,baseline_mobilenetv4_conv_medium}__srcsamp/`
> (train 30/09/2026, `data.sampler_stratify_by=source`, `training.callbacks.checkpoint.extra_monitors=[auprc]`).
> Đối chứng: cùng tên không hậu tố, cùng cây (arm DDI, 25/09), splits v2 có DDI; kết quả ngoài miền của đối chứng
> lấy từ `reports/external_newsplit_ddi/`, của arm mới từ `reports/external_newsplit_srcsamp{,_auprc}/`.
> Mọi Δ dưới đây là **mới − đối chứng** (dương = arm mới tốt hơn), paired bootstrap 2.000 lần, CI 95%,
> `*` = khoảng loại trừ 0. Nguồn: `reports/ci_srcsamp_*.md` (dựng bởi `run/srcsamp_eval.sh`) — bảng ở đây lấy từ
> **mục 3b** (cả tập) và **mục 6** (theo nhóm) của các file đó. **Mục 3 và mục 5 trong các file đó là ghép cặp tự
> động, dấu = đối chứng − mới — đừng trích** (ví dụ ô endpoint xuất hiện ở mục 5 dưới dạng −0,0563).

## 1. Sampler đã làm gì (fold 0)

Nguồn: dòng `Sampler stratify_by=source` trong `logs/train_student_20260930_154442.log` (chỉ có trên server).

| Nguồn | Ca ác | Ảnh lành trong pool | Ảnh lành/epoch: rút đều → theo nguồn |
|---|--:|--:|--:|
| ISIC 2024 | 237 | 251.712 | 5.357,5 → 4.091 (−23,6%) |
| PAD-UFES-20 | 669 | 809 | 17,2 → 809 |
| DDI | 171 | 485 | 10,3 → 485 |

Tổng ảnh lành/epoch giữ nguyên 5.385 (= 5 × 1.077 ca ác). 1.294 ảnh lành PAD + DDI lặp lại ở mọi epoch.

## 2. Item 2 — endpoint đăng ký trước (checkpoint pAUC ở cả hai phía)

Nguồn: `reports/ci_srcsamp_indomain.md` mục 6 (Δ theo `source`, dấu A − B).

| Cặp KD (đăng ký trước) | ΔAUPRC | ΔAUC-ROC |
|---|---|---|
| phần **PAD** | **+0,0563 [+0,0391, +0,0748] \*** | +0,0487 [+0,0356, +0,0638] \* |
| phần ISIC | −0,0043 [−0,0196, +0,0117] | −0,0013 [−0,0064, +0,0037] |

**Kết luận theo tiêu chí đăng ký trước:** ΔAUPRC trên phần PAD loại trừ 0 phía dương **và** phần ISIC không xấu
đi có ý nghĩa (cả 4 metric ISIC đều có CI chứa 0) ⇒ **item 2 đạt tiêu chí** cho student KD, **đo trên checkpoint
pAUC** (`best_model.pth`). Nhánh B (train lại cấu hình cũ) không cần. Đây là tiêu chí thí nghiệm, không phải cổng
chấp nhận triển khai; giới hạn bắt buộc của kết luận ở §8. "Không xấu đi có ý nghĩa" ≠ "không đổi": CI phần ISIC
vẫn cho phép ΔAUPRC tới −0,0196.

## 3. Endpoint phụ (chỉ báo cáo)

### 3.1 Cặp KD

| Tập | ΔAUC-ROC | ΔAUPRC | ΔpAUC@TPR80 | ΔSens@90Spec |
|---|---|---|---|---|
| In-domain, toàn tập test ⁽¹⁾ | −0,0001 [−0,0015, +0,0013] | +0,0329 [+0,0178, +0,0470] \* | −0,0001 [−0,0016, +0,0012] | −0,0038 [−0,0131, +0,0038] |
| HAM10000 headline | +0,0070 [+0,0027, +0,0112] \* | +0,0140 [+0,0049, +0,0233] \* | +0,0019 [−0,0006, +0,0044] | +0,0330 [+0,0196, +0,0477] \* |
| Fitzpatrick17k headline | +0,0309 [+0,0257, +0,0360] \* | +0,0328 [+0,0262, +0,0391] \* | +0,0061 [+0,0041, +0,0080] \* | +0,0524 [+0,0395, +0,0682] \* |
| Fitzpatrick17k crop70 | +0,0302 [+0,0257, +0,0349] \* | +0,0367 [+0,0304, +0,0432] \* | +0,0051 [+0,0033, +0,0071] \* | +0,0492 [+0,0359, +0,0642] \* |
| Fitzpatrick17k crop50 | +0,0297 [+0,0255, +0,0341] \* | +0,0360 [+0,0300, +0,0419] \* | +0,0060 [+0,0043, +0,0078] \* | +0,0431 [+0,0301, +0,0570] \* |
| Fitzpatrick17k with_non_neoplastic | +0,0219 [+0,0178, +0,0259] \* | +0,0395 [+0,0335, +0,0454] \* | +0,0001 [−0,0016, +0,0017] | +0,0528 [+0,0440, +0,0623] \* |

Fitzpatrick17k headline theo tông da (mục 6), ΔAUPRC: dark +0,0317 [+0,0115, +0,0544] \*,
medium +0,0348 [+0,0238, +0,0461] \*, light +0,0311 [+0,0223, +0,0395] \*.

⁽¹⁾ Số gộp, không phải endpoint đăng ký trước: AUPRC toàn tập còn chứa thứ hạng chéo giữa ảnh PAD và ảnh ISIC,
nên không phải trung bình của hai phần (xem dòng baseline ở §3.2, nơi Δ toàn tập nằm ngoài khoảng giữa hai Δ thành phần).

### 3.2 Cặp baseline (không KD) — KHÔNG đăng ký trước, chỉ để tham khảo

| Tập | ΔAUC-ROC | ΔAUPRC | ΔpAUC@TPR80 |
|---|---|---|---|
| In-domain, phần PAD | +0,0948 [+0,0700, +0,1199] \* | +0,0874 [+0,0581, +0,1190] \* | +0,0479 [+0,0351, +0,0602] \* |
| In-domain, phần ISIC | +0,0039 [−0,0116, +0,0198] | **−0,0301 [−0,0638, −0,0052] \*** | +0,0023 [−0,0108, +0,0158] |
| In-domain, toàn tập test ⁽¹⁾ | −0,0049 [−0,0100, +0,0003] | **−0,1327 [−0,1699, −0,0973] \*** | −0,0025 [−0,0073, +0,0026] |
| HAM10000 headline | **−0,0477 [−0,0580, −0,0376] \*** | −0,0028 [−0,0162, +0,0113] | **−0,0303 [−0,0350, −0,0258] \*** |
| Fitzpatrick17k headline | +0,0390 [+0,0307, +0,0471] \* | +0,0565 [+0,0468, +0,0654] \* | +0,0032 [+0,0002, +0,0061] \* |

Ở baseline, sampler theo nguồn làm **xấu đi có ý nghĩa** AUPRC in-domain toàn tập (−0,1327; AUPRC trung bình 5 fold
0,6029 → 0,4702), AUPRC phần ISIC, và AUC-ROC / pAUC trên HAM10000. Ở cặp KD, các ô tương ứng **không xấu đi có ý
nghĩa**. Khác biệt về mức ý nghĩa giữa hai cặp **không phải** một phép kiểm tương tác (KD × sampler) — tương tác đó
chưa được kiểm, và báo cáo này không kiểm cơ chế nào. Mỗi arm chỉ train một lượt.

## 4. Item 3 — checkpoint theo val AUPRC (student KD `__srcsamp`)

Checkpoint của ứng viên ship đã chốt trước = `best_model_auprc.pth`. **Checkpoint này không có phép kiểm item 2
nào**: run đối chứng không có checkpoint AUPRC, nên mọi Δ ở §2–§3 là của checkpoint pAUC. Báo cáo riêng (mô tả, CI
per-run, không ghép cặp), `reports/ci_srcsamp_auprc_indomain.md` mục 4:

| Checkpoint AUPRC, in-domain | AUPRC | AUC-ROC | pAUC@TPR80 | Sens@90Spec |
|---|---|---|---|---|
| phần PAD (397 dòng) | 0,8584 [0,8099, 0,9015] | 0,8779 [0,8453, 0,9083] | 0,1232 [0,1055, 0,1403] | 0,6074 [0,5173, 0,7381] |
| phần ISIC (58.696 dòng) | 0,0673 [0,0394, 0,1165] | 0,9437 [0,9227, 0,9616] | 0,1580 [0,1418, 0,1730] | 0,8553 [0,7855, 0,9116] |

Không so AUPRC giữa hai phần: prevalence khác nhau hàng trăm lần (189/397 so với 76/58.696).

So với checkpoint pAUC của cùng run — chỉ để minh bạch; `bootstrap_ci.py --pred-name` không ghép được hai
checkpoint của cùng một run nên **không có CI ghép cặp, và báo cáo này không kết luận hai checkpoint khác hay bằng
nhau**:

| Tập test | Checkpoint pAUC (`best_model.pth`) | Checkpoint AUPRC (`best_model_auprc.pth`) |
|---|---|---|
| In-domain, AUPRC (mean ± std 5 fold) | 0,6575 ± 0,0193 | 0,6609 ± 0,0140 |
| In-domain, pAUC@TPR80 | 0,1824 ± 0,0028 | 0,1833 ± 0,0029 |
| In-domain, Sens@90Spec | 0,9487 ± 0,0043 | 0,9562 ± 0,0051 |
| HAM10000 headline, AUPRC [CI per-run] | 0,4969 [0,4687, 0,5255] | 0,4997 [0,4728, 0,5267] |
| Fitzpatrick17k headline, AUPRC [CI per-run] | 0,6951 [0,6767, 0,7148] | 0,7022 [0,6843, 0,7213] |

Chênh AUPRC in-domain theo từng fold (AUPRC − pAUC checkpoint): fold_0 +0,0061, fold_1 −0,0105, fold_2 −0,0080,
fold_3 −0,0003, **fold_4 +0,0299** (0,6289 → 0,6588). Best epoch (pAUC / AUPRC): fold_0 45/50, fold_1 23/49,
fold_2 31/29, fold_3 42/34, **fold_4 12/36**.

## 5. Chọn fold + export (S5)

- Fold trung vị theo **val** AUPRC của checkpoint AUPRC (`val_metrics_auprc.json`): fold_2 0,6296 · fold_1 0,6616 ·
  **fold_4 0,7018** · fold_0 0,7688 · fold_3 0,7691 ⇒ **fold_4**, best epoch 36.
- `.pte`: `exports/executorch_srcsamp/mobilenetv4_conv_medium__srcsamp_auprc_fold4.pte` (server), export từ
  `fold_4/checkpoints/best_model_auprc.pth`; benchmark set + logit tham chiếu dựng bằng **cùng** checkpoint
  (`data/benchmark_set_srcsamp`, server; driver `.tmp_s5s6_srcsamp.sh`).
- Parity lớp 1: **PASS**, max|Δlogit| = 6,311e-06, 0/100 vượt 1e-3
  (`reports/mobile_benchmark/parity_mobilenetv4_conv_medium__srcsamp_auprc_fold4.json`).

## 6. Chấm bundle trên host (S6)

Bundle `data/mobile_eval_bundle` (70.883 ảnh), CPU, batch 1, hai runtime (PyTorch eager rồi ExecuTorch 1.5.1) chạy
tuần tự; ngưỡng Youden đóng băng = 0,2272 từ `fold_4/val_predictions_auprc.csv`.
Nguồn: `reports/mobile_eval_srcsamp/{comparison.md,server/,host_executorch/,*_logits.csv}`.

- 0 dòng lỗi ở cả hai runtime; sample id khớp 70.883/70.883.
- max|Δlogit| = 9,0e-06, trung bình 1,08e-06, 0 dòng vượt 1e-3 — tính bằng `paste` + `awk` trên hai file
  `*_logits.csv` (logit làm tròn 6 chữ số thập phân), không có artifact riêng.
- **Mọi metric trong `comparison.md` có Δ = 0 tới 4 chữ số** trên cả ba tập.

| Tập (fold_4, checkpoint AUPRC) | n | prevalence | AUPRC† | AUC-ROC† | pAUC@TPR80† | Sens@90Spec† | Sensitivity | Specificity |
|---|--:|--:|---|---|---|---|---|---|
| In-domain | 59.093 | 0,0045 | 0,6588 | 0,9828 | 0,1837 | 0,9585 | 0,9283 | 0,9451 |
| HAM10000 headline | 7.470 | 0,1565 | 0,5793 | 0,8807 | 0,1276 | 0,6133 | 1,0000 | 0,0927 |
| Fitzpatrick17k headline | 4.320 | 0,5000 | 0,7246 | 0,7315 | 0,0617 | 0,3634 | 1,0000 | 0,0014 |

† = không phụ thuộc ngưỡng. **Không so AUPRC giữa các tập** (prevalence chênh ~100×); giữa các tập chỉ so AUC-ROC và
pAUC. AUC-ROC in-domain là số gộp ISIC + PAD (xem ⁽¹⁾).

Ngưỡng đóng băng từ val in-domain gắn cờ gần như mọi ảnh ngoài miền là ác tính (specificity HAM 0,0927, Fitzpatrick
0,0014). Hiện tượng này **cũng có ở đối chứng** (checkpoint pAUC của KD đối chứng, 5 fold: specificity HAM
0,0833–0,2282, Fitzpatrick 0,0009–0,0231), nên không quy cho sampler. Đổi ngưỡng/calibration nằm ngoài phạm vi brief (§6).
Đây là số của **một** checkpoint, chấm trên host — chưa phải số Pixel 6a.

## 7. Chưa verify được trên Mac

- Bảng §1: chỉ có trong log khởi động trên server.
- `.pte` và `data/benchmark_set_srcsamp`: chỉ có trên server; việc hai thứ dựng từ cùng checkpoint dựa trên driver
  `.tmp_s5s6_srcsamp.sh` và bằng chứng gián tiếp (AUPRC in-domain của bundle 0,6588 = `test_metrics_auprc.json`
  fold_4; parity 6e-06).
- Thứ tự chạy tuần tự hai runtime ở S6: log trên server (`.tmp/s5s6_srcsamp.log`).

## 8. Giới hạn

- CI bootstrap chỉ phủ sai số lấy mẫu của tập test, **không** phủ nhiễu train lại (~0,005 AUPRC/fold,
  `experiments/_reproducibility/README.md`). Mỗi arm chỉ train một lượt.
- Test in-domain: phần PAD 397 dòng / 189 ca dương, phần ISIC 58.696 dòng / 76 ca dương
  (`predictions.csv`, cột `source`) — 189/265 ca dương nằm ở phần PAD.
- Kết quả item 2 đo trên checkpoint pAUC; **không** áp cho checkpoint AUPRC (brief §3) — xem §4.
- Chưa đo trên Pixel 6a; camera thật / app thật vẫn chưa đo.
