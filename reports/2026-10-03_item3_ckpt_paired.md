# Item 3 — checkpoint theo val AUPRC vs checkpoint theo val pAUC: phép kiểm ghép cặp (03/10/2026)

> Việc R2 trong `docs/PROGRESS.md`. Lấp chỗ trống mà `reports/2026-10-01_srcsamp_item2_3.md` §4 tự khai:
> "không có CI ghép cặp, và báo cáo này không kết luận hai checkpoint khác hay bằng nhau". **Chỉ báo cáo**:
> checkpoint `best_model_auprc.pth` đã được cố định trước (item 3, rồi prereg `docs/PREREG_CANDIDATE2_2026-10-02.md`
> §4.2), nên kết quả ở đây không đổi lựa chọn nào — đổi checkpoint sau khi xem số là post-hoc.
> Số in-domain là **splits v2**.
>
> **Kiểm chéo:** một lượt (FACTS + PATCH, 03/10/2026) — 25/25 ô Δ khớp nguồn. Sửa **sau** lượt kiểm, chưa ai kiểm
> lại: khối lệnh `ln` và đoạn về `y_true` ngay dưới nó, hai gạch đầu dòng cuối của "Đọc kết quả", gạch đầu dòng thứ hai
> của "Giới hạn".

**Run:** `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` (P0, 5 fold).
Hai "run" trong cây symlink trỏ vào **cùng** run-dir, khác checkpoint: `p0_ckpt_auprc/fold_N/predictions.csv` là symlink tới
`predictions_auprc.csv` (và `test_metrics.json` tới `test_metrics_auprc.json`), `p0_ckpt_pauc/fold_N/` trỏ tới
`predictions.csv` + `test_metrics.json` gốc — lệnh vì thế không cần `PRED_NAME`. Ngoài miền: cùng
run trong `reports/external_newsplit_srcsamp_auprc/` vs `reports/external_newsplit_srcsamp/`. Cần symlink cả
`test_metrics.json` vì `bootstrap_ci.py` chỉ nhận thư mục có file đó là một run (`find_run_dirs`).
Symlink là **từng file, có đổi tên** (symlink nguyên thư mục sẽ cho Δ = 0 ở mọi ô), dựng bằng:

```bash
P=kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp; T=.tmp/ci_item3
for k in 0 1 2 3 4; do
  ln -sf "$PWD/experiments/runs_newsplit_ddi/$P/fold_$k/predictions_auprc.csv"   $T/indomain/p0_ckpt_auprc/fold_$k/predictions.csv
  ln -sf "$PWD/experiments/runs_newsplit_ddi/$P/fold_$k/test_metrics_auprc.json" $T/indomain/p0_ckpt_auprc/fold_$k/test_metrics.json
  ln -sf "$PWD/experiments/runs_newsplit_ddi/$P/fold_$k/predictions.csv"         $T/indomain/p0_ckpt_pauc/fold_$k/predictions.csv
  ln -sf "$PWD/experiments/runs_newsplit_ddi/$P/fold_$k/test_metrics.json"       $T/indomain/p0_ckpt_pauc/fold_$k/test_metrics.json
  # ngoài miền: cùng mẫu, nguồn reports/external_newsplit_srcsamp{_auprc,}/<ds>/headline/$P/fold_$k/{predictions.csv,test_metrics.json}
done
```

`bootstrap_ci.py` chỉ kiểm hai run có cùng **số dòng** (`scripts/bootstrap_ci.py:391`). Lượt kiểm chéo đã kiểm riêng
trên Mac: `y_true` của hai checkpoint trùng 5/5 fold (in-domain và ngoài miền), thứ tự `image_id` trùng ở các fold
đã đối chiếu, `y_prob` khác nhau — tức ghép cặp đúng hàng.

**Lệnh** (server `vastnew`, CPU, 03/10/2026; cây `.tmp/ci_item3/<tập>/`):

```bash
bash run/bootstrap_ci.sh RESULTS_DIR=.tmp/ci_item3/indomain SUBGROUP=source \
  PAIR=p0_ckpt_auprc:p0_ckpt_pauc METRICS=auc_roc,auprc,pauc_at_tpr80,sens_at_90spec,sens_at_80spec \
  OUT_JSON=reports/ci_item3_srcsamp_indomain.json OUT_MD=reports/ci_item3_srcsamp_indomain.md
# tương tự cho ham10000_headline và fitzpatrick17k_headline (không SUBGROUP)
```

B = 2000, seed 42, không gộp fold. Δ = **checkpoint AUPRC − checkpoint pAUC** (mục 3b; theo miền: mục 6), dương =
checkpoint AUPRC tốt hơn. `*` = CI 95% loại trừ 0.

**Kiểm tính đúng của cây symlink:** giá trị từng run ở mục 1 khớp bảng `reports/2026-10-01_srcsamp_item2_3.md` §4
(in-domain AUPRC 0,6609 vs 0,6575; HAM 0,4997 vs 0,4969; Fitzpatrick 0,7022 vs 0,6951).

## Kết quả

| Tập | ΔAUC-ROC | ΔAUPRC | ΔpAUC@TPR80 | ΔSens@90Spec | ΔSens@80Spec | Nguồn |
|---|---|---|---|---|---|---|
| In-domain (cả tập) | +0,0010 [−0,0002, +0,0024] | +0,0034 [−0,0039, +0,0106] | +0,0009 [−0,0003, +0,0024] | **+0,0075 [+0,0022, +0,0148]** * | −0,0008 [−0,0042, +0,0024] | `reports/ci_item3_srcsamp_indomain.md:20` |
| — phần ISIC 2024 | +0,0033 [−0,0010, +0,0081] | −0,0001 [−0,0082, +0,0076] | +0,0024 [−0,0013, +0,0065] | **+0,0316 [+0,0056, +0,0585]** * | +0,0000 [−0,0135, +0,0103] | `…_indomain.md:51` |
| — phần PAD-UFES-20 | +0,0047 [−0,0010, +0,0105] | +0,0023 [−0,0062, +0,0106] | +0,0024 [−0,0009, +0,0057] | +0,0106 [−0,0272, +0,0471] | +0,0180 [−0,0086, +0,0444] | `…_indomain.md:52` |
| HAM10000 headline | **+0,0079 [+0,0055, +0,0104]** * | +0,0028 [−0,0032, +0,0091] | **+0,0051 [+0,0035, +0,0067]** * | −0,0014 [−0,0121, +0,0087] | +0,0060 [−0,0036, +0,0133] | `reports/ci_item3_srcsamp_ham10000_headline.md:20` |
| Fitzpatrick17k headline | **+0,0078 [+0,0050, +0,0104]** * | **+0,0071 [+0,0034, +0,0111]** * | **+0,0023 [+0,0011, +0,0036]** * | **+0,0150 [+0,0051, +0,0238]** * | **+0,0178 [+0,0081, +0,0249]** * | `reports/ci_item3_srcsamp_fitzpatrick17k_headline.md:20` |

## Đọc kết quả

- **Không ô nào checkpoint AUPRC kém hơn có ý nghĩa** (0/25 ô có cận trên < 0).
- **Fitzpatrick17k:** checkpoint AUPRC tốt hơn có ý nghĩa trên **cả 5** metric.
- **HAM10000:** tốt hơn có ý nghĩa trên AUC-ROC và pAUC; AUPRC, Sens@90Spec, Sens@80Spec không phân định.
- **In-domain:** chỉ Sens@90Spec phân định (+0,0075), và phần đó nằm ở miền ISIC (+0,0316). Trên ảnh **PAD**
  (miền của endpoint B2 và của app) không metric nào phân định. Đây là *không phân định được*, không phải tương
  đương: CI trên PAD vẫn chứa mức kém tới −0,0062 AUPRC, −0,0086 Sens@80Spec (metric của B2) và −0,0272 Sens@90Spec.
- Ý nghĩa cho dự án: với `best_model_auprc.pth` đã cố định (item 3, prereg §4.2), không ô nào cho thấy nó kém
  checkpoint pAUC có ý nghĩa (0/25), nhưng trên PAD chưa loại trừ được một mức kém nhỏ. Ngoài miền nó tốt hơn có ý
  nghĩa nhưng mức nhỏ (≤ +0,0079 AUC-ROC); ΔAUPRC chỉ phân định trên Fitzpatrick17k (+0,0071), trên HAM10000 thì
  không. Đây là mô tả, không phải lý do để chọn lại — lựa chọn đã khoá trước khi có các số này.

## Giới hạn

- Một run (P0), một cặp checkpoint; không nói gì về P1/P2 của vòng chọn thứ hai.
- Test in-domain, HAM10000 và Fitzpatrick17k đều đã được nhìn qua ứng viên thứ nhất (prereg §1); kết quả này chỉ để
  báo cáo. 25 ô không hiệu chỉnh đa so sánh, và ba dòng in-domain không độc lập với nhau.
- Chạy trên server; Mac chỉ có các file kết quả `reports/ci_item3_srcsamp_*` kéo về, không có cây symlink.
