# Pixel 6a, 01/10/2026 — ứng viên ship mới so với model điện thoại trước đó

> **Trạng thái:** đã qua một lượt kiểm chéo (2 verifier). Viết lại sau kiểm chéo: tóm tắt, §2.2 (hiệu ứng quy được),
> §3 (tách theo miền, calibration), §5 — các dòng này chưa được agent nào kiểm lại.

## Tóm tắt

1. **Điện thoại chạy đúng model:** mọi metric trên Pixel 6a trùng host/server (Δ = 0 tới 4 chữ số); `.pte` export bằng
   ExecuTorch 1.5.1 chạy được trên runtime Android 1.4.0.
2. **Hiệu quả quy được cho task (item 2, 5 fold, có đối chứng):** ảnh PAD (chụp bằng điện thoại) được xếp hạng tốt hơn —
   ΔAUPRC +0,0563 [+0,0391, +0,0748]; ngoài miền HAM +0,0140, Fitzpatrick +0,0328 (đều có ý nghĩa). Trên điện thoại,
   phần PAD đổi cùng chiều, cùng cỡ: +0,0695 [+0,0260, +0,1147].
3. **Item 3 (checkpoint theo AUPRC) chưa có bằng chứng** — không có phép kiểm ghép cặp nào.
4. **Triệu chứng người dùng gặp KHÔNG đổi:** ở ngưỡng đóng băng, ảnh PAD lành bị gắn cờ 205/208 → **207/208**; model
   mới bắt ít hơn 6 ca ác ISIC (63/76 → 57/76) dù gắn cờ ít hơn 503 ảnh ISIC lành. Vấn đề nằm ở ngưỡng, không ở thứ hạng,
   và sửa ngưỡng nằm ngoài brief.

## Thiết lập

- Mới: `mobilenetv4_srcsamp_auprc_fold4` =
  `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp/fold_4/checkpoints/best_model_auprc.pth`.
- Cũ: `mobilenetv4_ddi_fold0` = `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__mobile/fold_0`.
  **Logit của model cũ là lượt chạy ngày 29/09**, dùng lại nguyên (trùng byte với
  `eval-results/2026-09-29-pixel6a/processed224/mobilenetv4_ddi_fold0.csv`); chỉ model mới chạy ngày 01/10.
- Cùng Pixel 6a (Tensor G1), `executorch-android-1.4.0`, 4 luồng, batch 1, cùng bundle 70.883 ảnh (manifest `2128e9ac…`).
- Chấm lại trên server bằng `run/eval_from_logits.sh` + `run/bootstrap_ci.sh` qua driver `.tmp_pixel_cmp.sh`
  (**untracked**); kết quả `reports/mobile_eval_pixel6a_20261001/`. Trong `comparison.md` ở đó, cả hai cột đều có nhãn
  `mobile`: **cột 1 = model cũ, cột 2 = model mới, Δ = mới − cũ**.

## 1. Điện thoại có chạy đúng model không? — Có

| Kiểm tra (model mới) | Kết quả | Nguồn |
|---|---|---|
| Nạp `.pte` (ExecuTorch 1.5.1) trên runtime Android 1.4.0 | được | nạp + cổng PASS: `run_log.txt` 01/10 18:51:05; "1.5.1": `scored/vs_host_executorch/comparison.md`; "1.4.0": `processed224/*.json` `runtime` |
| Cổng parity 100 ảnh, đường `.bin` và đường ảnh | max\|Δlogit\| 2,384e-06 (PASS) | `processed224/mobilenetv4_srcsamp_auprc_fold4.json` `gate` |
| So với ref đủ 70.883 ảnh | max\|Δlogit\| 5,245e-06, 0 dòng vượt 1e-3 | cùng file, `vs_reference` |
| Chạy lại 500 ảnh | trùng bit | `determinism` |
| 4 luồng so với 1 luồng (100 ảnh cổng) | trùng bit | `gate.thread_check` |
| Dòng lỗi | 0/70.883 | `n_errored` |
| Metric điện thoại − host ExecuTorch / − server PyTorch | Δ = 0 tới 4 chữ số, cả 3 tập | `scored/vs_host_executorch/comparison.md`, `scored/vs_server/comparison.md` |

Thời gian chấm 70.883 ảnh: model mới 18:51:19 → 19:56:02 (~65 phút); model cũ 20:09:56 → 21:10:41 ngày 29/09 (~61 phút).

## 2. So sánh trên điện thoại

### 2.1 Mới − cũ, paired bootstrap trên CÙNG các ảnh

2.000 lần lặp, CI 95%, `*` = loại trừ 0. Mỗi bên là **một** checkpoint; CI chỉ phủ sai số lấy mẫu ảnh test.

| Tập | ΔAUC-ROC | ΔAUPRC | ΔpAUC@TPR80 | ΔSens@90Spec |
|---|---|---|---|---|
| In-domain — phần **PAD** (397 ảnh) | +0,0561 [+0,0251, +0,0874] \* | +0,0695 [+0,0260, +0,1147] \* | +0,0235 [+0,0063, +0,0390] \* | +0,1852 [+0,0358, +0,3557] \* |
| In-domain — phần ISIC (58.696 ảnh) | −0,0021 [−0,0216, +0,0146] | −0,0132 [−0,0435, +0,0161] | −0,0020 [−0,0181, +0,0123] | +0,0132 [−0,0597, +0,0824] |
| In-domain — toàn tập ⁽¹⁾ | −0,0005 [−0,0059, +0,0041] | +0,0406 [+0,0079, +0,0753] \* | −0,0006 [−0,0059, +0,0040] | +0,0000 [−0,0217, +0,0217] |
| HAM10000 headline | +0,0757 [+0,0643, +0,0871] \* | +0,1749 [+0,1493, +0,2013] \* | +0,0319 [+0,0240, +0,0398] \* | +0,1942 [+0,1599, +0,2324] \* |
| Fitzpatrick17k headline | +0,1138 [+0,1014, +0,1262] \* | +0,1284 [+0,1123, +0,1436] \* | +0,0210 [+0,0165, +0,0257] \* | +0,1856 [+0,1537, +0,2222] \* |

Nguồn: `ci_indomain.md` (mục 3b; mục 6 theo `source`), `ci_ham10000_headline.md`, `ci_fitzpatrick17k_headline.md` (mục 3b).
⁽¹⁾ Số gộp ISIC + PAD, không phải trung bình hai phần.

Ứng viên ship mới tốt hơn có ý nghĩa trên phần PAD, HAM10000 và Fitzpatrick17k; trên phần ISIC (~83% bundle) không
phân biệt được; trên toàn tập in-domain chỉ AUPRC có ý nghĩa.

Giá trị tuyệt đối trên phần PAD (`ci_indomain.md` mục 4):

| Phần PAD | AUC-ROC | AUPRC | Sens@90Spec |
|---|---|---|---|
| Model cũ | 0,8190 [0,7774, 0,8601] | 0,7847 [0,7223, 0,8442] | 0,4286 [0,2827, 0,5845] |
| Model mới | 0,8751 [0,8395, 0,9080] | 0,8542 [0,8018, 0,8998] | 0,6138 [0,4593, 0,7564] |

### 2.2 Phần nào là hiệu quả của task? — đừng đọc §2.1 là hiệu ứng của task

Hai checkpoint khác nhau ở ít nhất bốn thứ cùng lúc: sampler (item 2), tiêu chí chọn checkpoint (item 3), fold (4 so
với 0), lượt train. Hiệu ứng quy được cho item 2 lấy từ phép so 5 fold có đối chứng
(`reports/2026-10-01_srcsamp_item2_3.md`, cặp KD, checkpoint pAUC):

| ΔAUPRC | Điện thoại, 1 checkpoint mỗi bên (§2.1) | Quy được cho item 2 (5 fold, paired) |
|---|---|---|
| In-domain phần PAD | +0,0695 [+0,0260, +0,1147] | **+0,0563 [+0,0391, +0,0748]** |
| HAM10000 headline | +0,1749 [+0,1493, +0,2013] | **+0,0140 [+0,0049, +0,0233]** |
| Fitzpatrick17k headline | +0,1284 [+0,1123, +0,1436] | **+0,0328 [+0,0262, +0,0391]** |

Trên PAD hai cột khớp cỡ. Ngoài miền, phần lớn khoảng chênh trên điện thoại **không** đến từ task mà từ việc chọn
fold/checkpoint: HAM AUPRC của model cũ 0,4044 thấp hơn hẳn trung bình 5 fold của arm đối chứng 0,4829
(`reports/ci_srcsamp_ham10000_headline.md` mục 1), còn model mới 0,5793 cao hơn trung bình 5 fold của arm mới với
checkpoint AUPRC 0,4997 (`reports/ci_srcsamp_auprc_ham10000_headline.md` mục 1).

**Item 3** không có phép kiểm ghép cặp: trung bình 5 fold AUPRC in-domain chỉ đổi 0,6575 → 0,6609, và fold_4 là fold mà
checkpoint AUPRC hơn checkpoint pAUC nhiều nhất (+0,0299) — model ship nằm ở phía thuận lợi của item 3, nên §2.1 bị đội
lên một phần vì đó.

## 3. Điều CHƯA cải thiện

Mỗi model dùng ngưỡng Youden đóng băng từ val in-domain của chính nó (cũ 0,1583, mới 0,2272). Đếm trên
`.tmp/pixel_cmp/indomain/*/fold_0/predictions.csv` (server) và `pad_flags.txt`:

| Ở ngưỡng đóng băng | Model cũ | Model mới |
|---|---|---|
| PAD lành bị gắn cờ ác tính | 205/208 | **207/208** |
| PAD ác tính bắt được | 189/189 | 189/189 |
| ISIC ác tính bắt được | 63/76 | **57/76** |
| ISIC lành bị gắn cờ | 3.527/58.620 | 3.024/58.620 |
| Specificity HAM10000 / Fitzpatrick17k | 0,0621 / 0,0009 | 0,0927 / 0,0014 |

- Model mới xếp hạng ảnh PAD tốt hơn (§2), nhưng ngưỡng đóng băng vẫn nằm dưới gần như mọi ảnh PAD lành, nên app dùng
  ngưỡng này vẫn gắn cờ hầu hết ảnh lành chụp bằng điện thoại. Ví dụ về khác biệt thứ hạng: ở mức chỉ gắn cờ 10% ảnh PAD
  lành (Sens@90Spec), model mới bắt 61% ca ác PAD so với 43% — nhưng đó là ngưỡng riêng cho PAD, không phải ngưỡng app dùng.
- Ngưỡng của model mới cao hơn nên bắt ít hơn 6/76 ca ác ISIC, đổi lại gắn cờ ít hơn 503 ảnh ISIC lành.
- Calibration in-domain xấu đi (Brier 0,0095 → 0,0127, ECE 0,0436 → 0,0721), ngoài miền tốt lên (HAM ECE 0,4470 → 0,3550;
  Fitzpatrick 0,2862 → 0,0841) — `comparison.md`.
- Sửa ngưỡng / calibration theo miền nằm ngoài brief item 2+3.

## 4. Đọc kết quả cho đúng

- Một checkpoint mỗi bên: không phải bằng chứng cho một arm (`acceptance-gates.md`), và báo cáo này **không** đưa ra
  phán quyết "đạt yêu cầu triển khai".
- Vẫn chưa đo: ảnh chụp bằng camera thật qua app (resample/camera, L3).

## 5. Chưa verify được trên Mac

- Run-dir `__mobile/fold_0` (config, tiêu chí checkpoint, best epoch, `val_predictions.csv` cho ngưỡng 0,1583) chỉ có
  trên server; danh sách "bốn khác biệt" có thể chưa đủ.
- `data/mobile_eval_bundle/manifest.csv`, `.tmp/pixel_in/`, `.tmp/pixel_cmp/` chỉ có trên server; phép join của driver được
  xác nhận gián tiếp (n, prevalence khớp; model cũ ra lại đúng 0,6182 / 0,4044 / 0,5963; checksum hai file logit khớp).
