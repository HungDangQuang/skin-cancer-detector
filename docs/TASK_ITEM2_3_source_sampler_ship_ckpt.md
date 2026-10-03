# Task: item 2 (sampler theo nguồn) + item 3 (checkpoint ứng viên ship chọn đúng tiêu chí)

> 📋 **Theo dõi việc: `docs/PROGRESS.md`** — brief này đã thực hiện xong (item 2 đạt, 01/10); phần còn mở của item 3 là R2 trong PROGRESS. Không cập nhật trạng thái ở đây.

> Brief cho một session khác thực hiện. Đọc `CLAUDE.md` trước (quy tắc cứng + cổng kiểm chéo).
> Soạn 30/09/2026. Số giờ là **ước lượng từ log arm DDI**, không phải cam kết.

## 0. Bối cảnh

- Ứng viên ship hiện tại = student `mobilenetv4_conv_medium`, KD từ teacher `efficientnetv2_m` của
  arm DDI (`experiments/runs_newsplit_ddi/`, splits v2 gom theo bệnh nhân). *Chưa phải quyết định
  ship chính thức* — spec app cũ ghi cặp khác trên splits v1. Test Pixel 6a của checkpoint
  `__mobile` fold 0: phone = server (36/36 metric Δ=0), nhưng ảnh điện thoại (PAD-UFES-20) AUC chỉ
  0,819 và 205/208 ảnh PAD lành bị gắn cờ (số của MỘT checkpoint).
- **Giả thuyết item 2 (chưa đo):** `DynamicUndersampledSampler` rút ảnh lành ngẫu nhiên từ TOÀN pool,
  không phân biệt nguồn (`src/data/sampler.py:43`). Fold 0 (bản Mac, chưa có DDI): PAD 669 ác / 809
  lành trên 252.521 ảnh lành ⇒ ~14,5 ảnh PAD lành/epoch. Bằng chứng ngược: ablation 1:10 (gấp đôi
  ảnh PAD lành) lại xấu hơn trên miền PAD — đo trên splits v1, bị nhiễu vì ISIC cũng đổi
  (`reports/bootstrap_ci_ablation.md:337`); arm DDI thành công mà không cần sửa này.
- **Item 3:** checkpoint chọn theo pAUC **hard-code** (`src/training/kd_trainer.py:178`,
  `src/training/trainer.py:102`; key `monitor:` trong yaml bị bỏ qua); early stopping theo `val_loss`.
  `__mobile` fold 0 có best epoch 6 (theo memory; log trên server), trong khi 10 fold KD light+DDI có
  best epoch 15–46. Trên server chỉ còn checkpoint teacher + `__mobile` fold 0 ⇒ muốn có model ship
  phải **train lại**.

## 1. Quy tắc cứng

- Không chạy `prepare`; không động `data/splits` (bản server có +656 dòng DDI, KHÁC bản Mac).
- Không train lại teacher. Student fork bằng `run_suffix=`, và luôn kèm
  `output_dir=experiments/runs_newsplit_ddi` để tìm đúng teacher (`scripts/train_student.py:62`).
- Sửa code: skill `code-change` → review theo vùng → `run/*.sh` + `run/README.md` → validate-pipeline →
  docs + memory. Knob mới **mặc định TẮT** (run cũ tái lập byte-for-byte).
- `export TMPDIR="$(pwd)/.tmp"`, chạy trong `tmux`, một job một lúc.
- Python/`bootstrap_ci` chạy **trên server**; Mac chỉ `pull_results` và đọc kết quả.
- **HAM10000/Fitzpatrick không được dùng để CHỌN** (fold, checkpoint, cấu hình) — chỉ báo cáo.

## 2. Việc code (Mac)

**C1 — sampler theo nguồn.** Knob `data.sampler_stratify_by: null | source`, **khai báo trong
`configs/data/isic2024.yaml`** (Hydra struct từ chối override key chưa khai báo).
- Giữ TỔNG ảnh lành/epoch = `ratio × n_malignant`; mỗi nguồn `benign_s = min(ratio × n_mal_s, n_benign_s)`,
  phần còn lại lấy từ ISIC. Với fold 0 có DDI (1.077 ca dương ⇒ 5.385 ảnh lành/epoch): PAD 809 +
  DDI 485 lấy toàn bộ; ISIC còn ~4.091 (trước ~5.357, **giảm ~24%**) — ghi con số thật vào log.
- Nguồn lấy từ `self._train_dataset.df["source"]` (`src/data/datamodule.py:117-123`; DDI mang `"ddi"`).
- Log mỗi epoch số ảnh theo (source × label). Rủi ro: 1.294 ảnh lành PAD+DDI lặp lại mọi epoch.
- Review: `code-change/reference/review-preprocessing.md`.

**C2 — thêm checkpoint theo AUPRC.** `best_model.pth` giữ nguyên (pAUC). Knob
`training.callbacks.checkpoint.extra_monitors: []` (khai báo trong `configs/training/distillation.yaml`
**và** `baseline.yaml`); với `[auprc]` lưu thêm `checkpoints/best_model_auprc.pth` và
`scripts/train_student.py` ghi đủ bộ cho checkpoint đó: `val_metrics_auprc.json`,
**`val_predictions_auprc.csv`** (nguồn ngưỡng Youden), `test_metrics_auprc.json`, `predictions_auprc.csv`.
Review: `code-change/reference/review-training.md`.

**C3 — công cụ đọc checkpoint thứ hai:**
- `scripts/evaluate_external.py` hiện nạp cứng `checkpoints/best_model.pth` (:216) và lấy ngưỡng từ
  `val_predictions.csv` (:116); `run_tag = run_dir.name` (:330). Thêm cờ `--ckpt-name` +
  `--val-pred-name` (mặc định giữ nguyên) và chấm hai checkpoint vào **hai `--out-root` khác nhau**,
  nếu không sẽ ghi đè nhau im lặng.
- `scripts/bootstrap_ci.py` nạp cứng `predictions.csv` (:213) → thêm cờ tên file (mặc định giữ nguyên).
- `scripts/aggregate_folds.py` chỉ đọc `test_metrics.json` → cho phép chọn tên file.
- `run/*.sh` + `run/README.md` tương ứng.

## 3. Đăng ký trước tiêu chí (chốt TRƯỚC khi chạy)

- **Item 2 — so cùng tiêu chí checkpoint (pAUC, `predictions.csv`) ở cả hai phía:**
  `PAIR="kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp:kd_efficientnetv2_m_to_mobilenetv4_conv_medium"`
  (dấu = mới − đối chứng; **dương = arm mới tốt hơn**) + `--subgroup-col source`.
  ⚠️ Đừng dùng auto-pair `__<suffix>`: dấu của nó là đối chứng − `__srcsamp` (`scripts/bootstrap_ci.py:444-446`).
  - Endpoint chính: ΔAUC và ΔAUPRC trên **phần PAD** của test in-domain. Thành công = CI của ΔAUPRC
    (chọn một metric chính để khỏi đa kiểm định) loại trừ 0 phía dương **và** phần ISIC không xấu đi có ý nghĩa.
  - Endpoint phụ (chỉ báo cáo): ΔAUC-PAD, HAM, Fitzpatrick 4 biến thể.
  - Giới hạn phải ghi khi kết luận: CI bootstrap chỉ phủ sai số lấy mẫu test, không phủ nhiễu train lại
    (~0,005 AUPRC/fold, `experiments/_reproducibility/README.md`).
- **Item 3:** checkpoint ship = `best_model_auprc.pth` (chốt trước; AUPRC là headline lâm sàng). So với
  checkpoint pAUC chỉ để minh bạch, không dùng test để chọn lại. Kết quả item 2 (đo trên checkpoint pAUC)
  **không tự động** áp cho checkpoint AUPRC — báo cáo riêng.
- **Fold ship:** fold trung vị theo **val** AUPRC (`val_metrics_auprc.json`).

## 4. Các bước trên server + ước lượng giờ

| # | Bước | Lệnh chính | Giờ | Căn cứ |
|---|---|---|--:|---|
| S0 | `git pull`, validate, POC | `bash run/validate.sh && bash run/poc.sh` | 0,3 | validate ~1 phút (CLAUDE.md); POC 2 epoch |
| S1 | KD student 5 fold, sampler=source + 2 checkpoint | `bash run/train_student.sh STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m TRAINING=distillation GPU=0 EXTRA="output_dir=experiments/runs_newsplit_ddi run_suffix=__srcsamp data.sampler_stratify_by=source training.callbacks.checkpoint.extra_monitors=[auprc]"` | 4,0 | KD DDI 5 fold 17:32:06→21:23:54 = 3,86 h (`logs/train_student_20260925_173206.log`); số epoch có thể đổi khi đổi sampler |
| S2 | *(tuỳ chọn)* baseline 5 fold cùng sampler | như S1 với `TRAINING=baseline` | 1,2 | 16:18→17:32 (`logs/train_student_20260925_161810.log`) |
| S3 | `aggregate.sh` + eval ngoài miền HAM + Fitz (4 biến thể), 2 checkpoint × 2 out-root | mẫu: `.tmp/archived_root_drivers_20261002/.tmp_eval_ddi.sh` (local, untracked) (Mac, untracked) + cờ C3 | 0,7 | HAM 9 phút / 3 run-dir (`logs/evaluate_external_20260923_163413.log`); Fitz ≥12 phút, log dừng giữa chừng |
| S4 | Paired CI (in-domain + ngoài miền) | `bash run/bootstrap_ci.sh RESULTS_DIR=... PAIR="..."` | 0,1 | ~1,5 phút/lượt (`logs/bootstrap_ci_20260926_*.log`) |
| S5 | Ship: chọn fold theo val → export `.pte` + parity, **CÙNG `CKPT=.../best_model_auprc.pth`** cho `make_benchmark_set.sh` và `export_executorch.sh` | `run/make_benchmark_set.sh`, `run/export_executorch.sh`, `run/check_pte_parity.sh` | 0,2 | export ~34 s (log 27/09, chỉ trên server); parity: **chưa có số đo server** |
| S6 | Chấm bundle trên host (ExecuTorch + eager, tuần tự, ghim luồng), `VALPRED=val_predictions_auprc.csv` | `run/infer_bundle.sh` → `run/eval_from_logits.sh` | 1,0 | 16:42→17:44 ngày 27/09 (log chỉ trên server) |
| B | **Nếu item 2 KHÔNG đạt:** train lại cấu hình cũ + 2 checkpoint để có model ship | như S1, bỏ `data.sampler_stratify_by`, `run_suffix=__ship` | +4,0 | như S1 |

**Tổng giờ server:**

| Kịch bản | Giờ |
|---|--:|
| Tối thiểu (S0+S1+S3+S4+S5+S6) | **6,3 h** |
| + baseline tuỳ chọn (S2) | **7,5 h** |
| + nhánh B (item 2 thất bại) | **10,3 – 11,5 h** |
| Khuyến nghị lên lịch (tối thiểu + 20% dự phòng) | **~7,6 h** |

Ngoài server: code C1–C3 (Mac), `bash run/pull_results.sh pull` (Mac), chấm lại trên Pixel 6a ~1 h
(70.883 ảnh × ~51 ms).

## 5. Sản phẩm bàn giao

1. Code C1–C3 đã review + validate; knob mặc định tắt; `run/README.md`, `docs/PREPROCESSING.md` cập nhật.
2. `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp/` 5 fold + aggregated, pull về Mac.
3. `reports/ci_srcsamp_*.md` (in-domain theo `source`, HAM, Fitz) — kết luận đúng tiêu chí mục 3, kèm dấu.
4. `.pte` của fold ship (checkpoint AUPRC) + parity PASS + bảng chấm bundle trên host.
5. Memory: `project_ondevice_eval_gap.md` + file mới cho kết quả sampler.

## 6. Ngoài phạm vi

PanDerm (đã audit: không train), cặp `maxvit→fastvit` (~20 fold-run), thêm dataset mới, đổi
ngưỡng/calibration, train lại teacher với sampler mới.

## 7. Chưa verify được (khi soạn brief)

- `__mobile` best epoch 6; "chỉ còn checkpoint teacher + `__mobile`" — trạng thái/log trên server.
- Thời gian export 34 s và chấm bundle 1,0 h — log 27/09 chỉ có trên server.
- Thời gian parity trên server — chưa từng đo.
