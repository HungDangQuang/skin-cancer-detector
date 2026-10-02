# Theo dõi tiến độ

> **Nơi duy nhất** theo dõi việc đang làm và việc cần làm. Thay cho `docs/NEXT_TASKS_2026-10-02.md` (bản cũ, không
> nằm trong git, mã việc T1–T9/D1–D4 của nó **không** dùng ở đây nữa).
>
> **Cách cập nhật:** khi một việc đổi trạng thái, sửa ô "Trạng thái", ghi ngày; việc xong thì chuyển xuống mục 7.
> Ký hiệu: 🏃 đang chạy · ⏳ chờ việc khác · 👤 chờ tác giả · 🔜 làm được ngay · ✅ xong · ⏸ hoãn.
> Mã việc: **A** đang chạy · **U** chờ tác giả · **N** làm sau khi train xong · **R** làm được ngay · **S** để sau.

**Cập nhật lần cuối:** 02/10/2026 23:00 (+0700). Trạng thái server là **ảnh chụp lúc đó** — xem lại bằng lệnh ở mục 1.

## 0. Tình trạng tổng quát

| Mục | Hiện tại |
|---|---|
| Ứng viên ship | `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`, `best_model_auprc.pth`, fold 4 |
| Phán quyết | **CHƯA CÓ TIÊU CHÍ CHỐT** (B4 chuyển sang báo cáo 02/10) — `reports/2026-10-02_acceptance_verdict_srcsamp.md` |
| Khoảng cách thật | **B2** (PAD): điểm ước lượng 0,8180 đã vượt 0,81, nhưng **cận dưới CI** 0,7406 còn thiếu ~0,07 · **C4a**: cận dưới tông trung bình 0,4077 và tông tối 0,4248 dưới 0,47 · **A1** chưa đo |
| Đang làm | Vòng chọn thứ hai: hai cặp teacher–student mới đang train (mục 1) |
| Hợp đồng chấm | `.claude/skills/eval-results/reference/acceptance-gates.md` |

## 1. Đang chạy 🏃 — vòng chọn thứ hai

Đăng ký trước: `docs/PREREG_CANDIDATE2_2026-10-02.md` (luật chọn §4, endpoint §5, phụ lục §7). Server `vastnew`,
tmux `cand2`, khởi chạy 02/10 15:34:41 UTC. Ước lượng thô ~1 ngày.

| Mã | Job | Run-dir (trong `experiments/runs_newsplit_ddi/`) | Ai / ở đâu | Trạng thái (02/10 15:56 UTC) |
|---|---|---|---|---|
| A1 | baseline `repvit_m1_0` (đối chứng C1 của P2) | `baseline_repvit_m1_0__srcsamp` | server | 🏃 1/5 fold xong |
| A2 | KD P2: `efficientnetv2_m → repvit_m1_0` | `kd_efficientnetv2_m_to_repvit_m1_0__srcsamp` | server | ⏳ sau A1 |
| A3 | teacher `convnextv2_base` | `teacher/convnextv2_base` | server | ⏳ sau A2 |
| A4 | KD P1: `convnextv2_base → mobilenetv4_conv_medium` | `kd_convnextv2_base_to_mobilenetv4_conv_medium__srcsamp` | server | ⏳ sau A3 |

**Xem tiến độ:**
```bash
bash run/progress_all.sh                                        # từ Mac
ssh vastnew 'cd /workspace/skin-cancer-detector && ls .tmp/cand2_status/ && tail -3 .tmp/cand2_driver.log'
```
`.tmp/cand2_status/<bước>.ok` = bước đã xong; `<bước>.failed` = hỏng, driver đã dừng. Driver `.tmp/cand2_driver.sh` chỉ
nằm trên server (không trong git); lệnh của từng bước ghi đủ ở prereg §3.

**Nếu một bước hỏng:** code không có resume. Chạy lại đúng bước đó với `FOLDS="<các fold còn thiếu>"`, nếu không sẽ
train lại từ fold 0 và ghi đè các fold vừa xong. Rủi ro đã biết: repvit từng OOM khi chung card; convnextv2 chưa
từng train trên `vastnew`.

## 2. Chờ tác giả 👤

| Mã | Việc | Vì sao cần | Link / file | Trạng thái |
|---|---|---|---|---|
| U1 | Mở PR và merge nhánh ML `feat/binary-app-config` | Chế độ hiển thị nhị phân (`make_app_config`, spec §3.4a), bảng chọn ngưỡng, `thesis/CAN_SUA_SAU.md`. **Chưa vào develop**; đã kiểm merge sạch với develop 02/10 | https://github.com/HungDangQuang/skin-cancer-detector/compare/develop...feat/binary-app-config?expand=1 | 👤 |
| U2 | Mở PR và merge nhánh Android `support-binary-config` (repo `android-skin-detector`) | Lõi `:core:ml` đọc config nhị phân. **Chưa vào develop** | https://github.com/HungDangQuang/android-skin-detector/pull/new/support-binary-config | 👤 |
| U3 | Báo session Android đang làm màn hình kết quả | Repo `SkinDetector`, nhánh `implement-result-screen`, file **chưa commit** `app/src/main/java/com/nemis/skindetector/ui/result/ResultViewModel.kt:108` (`riskBand ?: return InvalidInput`): sau U2, mọi kết quả nhị phân sẽ thành "ảnh không hợp lệ" mà không báo lỗi biên dịch | spec §3.4a (trên nhánh U1) | 👤 |
| U4 | Chọn ngưỡng cho app | Đang dùng `phone_sens90` (quy tắc `pad_sens90` trong bảng; 0,5705; post-hoc). Xác nhận hoặc chọn khác | `reports/2026-10-02_threshold_options/README.md` (trên nhánh U1) | 👤 |
| U5 | Đặt mốc cho đo L3: **T1** (độ nhạy với thuật toán thu nhỏ ảnh) và **T2** (chụp lại qua app) + danh sách `sample_id` cho T2 | Phải chốt trước khi chạy, nếu không thành post-hoc (tên T1/T2/T3 theo đúng guide) | `docs/L3_CAMERA_EVAL_GUIDE.md` §1, §2, §4 | 👤 |
| U6 | Đo A1 trên đúng `.pte` ship | A1 là cổng bắt buộc, đang CHƯA ĐO — phán quyết không thể "đạt" khi chưa đo. Pixel 6a **rút sạc**, chế độ máy bay | repo `SkinDetector-eval`: `tools/run_benchmark.sh` | 👤 ⏸ (tác giả 02/10: chưa cần) |
| U7 | Chốt các mốc còn ĐỀ XUẤT | B1, B3, C4a, cách hiểu + tập miền C2, δ C4b, A1/A3/A4. Tác giả 02/10: "giữ các mốc đề xuất thử xem" | `acceptance-gates.md` §1 | 👤 ⏸ |
| U8 | Có tìm nguồn ảnh điện thoại/lâm sàng mới không | Ứng viên đòn bẩy cho B2/C4a (cần cả hai lớp, đa dạng tông da, không trùng HAM/Fitz/PAD/DDI). Là mở rộng scope — MIDAS từng bị loại vì lý do đó | — | 👤 |
| U9 | Các quyết định còn treo của arm augmentation | `docs/domain_aug_plan.md` §8: #3 (gắn vào câu hỏi nghiên cứu nào), #4 (calibration có đưa lại luận văn không — app giờ nhị phân); #5 coi như **đã thay** bằng vòng chọn thứ hai | `docs/domain_aug_plan.md` §8 | 👤 |

## 3. Làm khi vòng chọn thứ hai train xong ⏳ — đúng thứ tự (prereg §4, §5, §7)

| Mã | Việc | Ai / ở đâu | Lệnh / ghi chú | Trạng thái |
|---|---|---|---|---|
| N1 | **Tính luật chọn từ val và COMMIT kết quả** — trước mọi bước đọc số test | server (Python) | Chưa có script: viết qua skill `code-change`. Trung bình 5 fold AUPRC trên hàng PAD của `fold_*/val_predictions_auprc.csv` ghép theo thứ tự dòng với `data/splits/isic2024/fold_N/val_split.csv` (**kiểm số dòng và nhãn khớp từng dòng**), cho P0/P1/P2; luật hoà §7.1; fold ship = trung vị `val_metrics_auprc.json` | ⏳ |
| N2 | Kéo kết quả về Mac + `aggregate` (cả checkpoint chính và `_auprc`) | Mac + server | `bash run/pull_results.sh pull`; `bash run/aggregate.sh RUN_DIR=<run>` và `… METRICS_NAME=test_metrics_auprc.json` (teacher: chỉ bản chính). `aggregated*.md` chứa số test — chỉ chạy sau N1 | ⏳ |
| N3 | Eval ngoài miền: HAM headline + Fitzpatrick 4 biến thể | server | `bash run/evaluate_external.sh DATASET=… RUNS="<run-dir>" OUT_ROOT=<riêng>`. Student/baseline (P1, P2, baseline repvit): thêm `CKPT_NAME=best_model_auprc.pth VAL_PRED_NAME=val_predictions_auprc.csv`. **Teacher `convnextv2_base` cần lượt riêng với checkpoint mặc định** (teacher không có `best_model_auprc.pth`) — thiếu nó thì không tính được C2 của P1 trên Fitz/HAM | ⏳ |
| N4 | CI các cổng | server | `bash run/bootstrap_ci.sh RESULTS_DIR=<cây symlink> PAIR="<student>:<teacher>" SUBGROUP=source\|tone_group METRICS=auc_roc,auprc,pauc_at_tpr80,sens_at_90spec,sens_at_80spec`. Dựng cây symlink như P0 (`.tmp/ci_gates/` trên server: student = file `_auprc`, teacher = file chính). C2 = student vs **teacher của chính cặp**; C1 = KD vs baseline cùng student | ⏳ |
| N5 | Export `.pte` + parity cho ứng viên được chọn | server | `OUT=` riêng; **cùng `CKPT`** ở `make_benchmark_set.sh` và `export_executorch.sh`; repvit: kiểm XNNPACK, lùi portable nếu hỏng. Nếu chọn lại P0: `.pte` và A3/A4 đã có | ⏳ |
| N6 | Đo A1/A3/A4 trên điện thoại cho `.pte` mới | Android / Pixel 6a | như U6 | ⏳ |
| N7 | Phán quyết mới | Mac | `reports/<ngày>_acceptance_verdict_<ứng viên>.md`; luật gộp A1+A3+A4+B1+B2+B3+C2+C4a; báo cáo B4, C1, C3, C4b, A2, hành vi tại ngưỡng val (`phone_sens90` + Youden toàn cục). **Khai post-hoc**: vòng thứ hai, mọi tập kiểm đã nhìn, hai cặp chọn có tham khảo số v1 (prereg §1, §7.4). Viết sau N6, hoặc ghi A1/A3/A4 = CHƯA ĐO rồi viết lại sau N6 | ⏳ |
| N8 | Config app + bundle | server + Mac | `run/make_app_config.sh … SKIP_GLOBAL_OP=1` (cần U1); cập nhật `catalog.json` + sinh lại `SHA256SUMS` trong **cả hai** bản `materials_for_mobile/` (`~/Documents/` và `~/Documents/android-projects/SkinDetector-eval/`) | ⏳ |
| N9 | Cập nhật file này, memory, `thesis/CAN_SUA_SAU.md` (chỉ ghi chú) | Mac | — | ⏳ |

## 4. Làm được ngay 🔜

| Mã | Việc | Ai / ở đâu | Ghi chú | Trạng thái |
|---|---|---|---|---|
| R1 | sens@spec80 theo tông da trên Fitzpatrick crop70 cho ứng viên hiện tại | server, CPU | Đề xuất của assistant 02/10. Chỉ để chẩn đoán, **không** dùng để chọn | 🔜 |
| R2 | Phép kiểm ghép cặp cho item 3 (checkpoint AUPRC vs checkpoint pAUC) | server, CPU | Chưa có (`reports/2026-10-01_srcsamp_item2_3.md` §4). Chỉ báo cáo; đổi checkpoint sau khi xem là post-hoc | 🔜 |
| R3 | Ghi vào `CLAUDE.md` mục "Data integrity": mỗi `fold_*/train_split.csv` có thêm 656 dòng DDI | Mac | Còn tồn từ `docs/domain_aug_plan.md` §9.2 | 🔜 |
| R4 | Báo cáo arm DDI thành `reports/*.md` | Mac | Còn tồn từ `docs/domain_aug_plan.md` §9.4 (hiện chỉ có `reports/ci_ddi_*`) | 🔜 |

## 5. Để sau / hoãn ⏸

| Mã | Việc | Ghi chú |
|---|---|---|
| S1 | Thêm ảnh dermoscopy vào train (hướng H3 trong `docs/NEXT_DIRECTION_2026-10-02.md`) | Tác giả: tạm không làm. B4 đã thành báo cáo |
| S2 | Đo L3-T1 (thu nhỏ ảnh) | Chờ U5. HDF5 ISIC đã chép lên server ở `data/l3/isic2024_train-image.hdf5` (02/10; sha256 khớp bản Mac), cố ý **không** đặt ở `data/raw/isic2024/` để `prepare` vẫn không chạy được |
| S3 | Đo L3-T2 (chụp lại ảnh đã biết nhãn qua app) | Chờ U5, N8 và chế độ "chụp để đánh giá" trên app |
| S4 | Sửa luận văn | **Chỉ ghi chú, chưa sửa** (tác giả). Danh sách `thesis/CAN_SUA_SAU.md` (trên nhánh U1) |
| S5 | Tính bù `valthr_*` cho ma trận v1 (cho luận văn) | 165 fold; ~913 MB `predictions*.csv` + `val_predictions*.csv` trên Mac, phải đẩy lên server trước. `run/backfill_valthr.sh` |
| S6 | Spec app: các mục chưa cập nhật cho chế độ nhị phân | §3.3, §3.7, §9.1 `ScanEntity`, MA7, R-RES-07, R-HOME-02/03, R-HIS-01 — liệt kê trong spec §3.4a (trên nhánh U1) |

**Đồ tồn đọng cần dọn khi tiện:** stash `apply-metadata-for-training` trên server; `.tmp/untracked_before_develop_20261002/`
(server); `.tmp/archived_root_drivers_20261002/` (Mac); `docs/NEXT_TASKS_2026-10-02.md` (Mac, đã được file này thay).

## 6. Chưa verify được / chỉ có trên server

- Trạng thái train ở mục 1 là ảnh chụp lúc 15:56 UTC; job có hoàn thành hay không, mất bao lâu: xem lại bằng lệnh ở mục 1.
- HDF5 ở `data/l3/` và sha256 của nó: chỉ kiểm được trên server.
- Nhánh Android `support-binary-config`: 185/185 unit test theo lần chạy 02/10 trên Mac (ghi trong commit message 8cadf8f); instrumented test và giao diện **chưa** chạy.
- Câu "chưa cần" (U6) và "giữ các mốc đề xuất thử xem" (U7) là lời tác giả trong hội thoại 02/10.

## 7. Đã xong ✅

| Ngày | Việc | Nơi ghi |
|---|---|---|
| 02/10 | Ô PAD của C1: ΔAUPRC −0,0008 [−0,0199, +0,0187] ⇒ C1 CHƯA CHỨNG MINH | `reports/2026-10-02_c1_pad_cell_srcsamp.md` (PR #13) |
| 02/10 | `valthr_*`: độ nhạy/độ đặc hiệu ở ngưỡng chọn trên val, trong trainer + `evaluate.py` + tính bù cho cây v2 | PR #13, #16; `reports/valthr/` |
| 02/10 | Công cụ báo cáo dùng ngưỡng val (`compare_kd_results`, `analyze_pad_ablation`) | PR #16 |
| 02/10 | Merge app-config + gates/guides | PR #14, #15 |
| 02/10 | B4 chuyển sang báo cáo; phán quyết thành CHƯA CÓ TIÊU CHÍ CHỐT | PR #17 |
| 02/10 | Đăng ký trước vòng chọn thứ hai (+ phụ lục §7) | PR #18 |
| 02/10 | Config app thật (chế độ nhị phân, `phone_sens90`) + `catalog.json` + `SHA256SUMS` | ngoài git: `exports/app_config/mobilenetv4_srcsamp_auprc_fold4/` (server), `materials_for_mobile/models_srcsamp_auprc_fold4/` (bản trong `SkinDetector-eval`) |
| 02/10 | `pull_results.sh` đã có `runs_newsplit_ddi` trong `ROOTS` (`domain_aug_plan.md` §9.1) | `run/pull_results.sh` |

**Code xong nhưng CHƯA merge:** chế độ app nhị phân — xem U1, U2.

## 8. Tham chiếu nhanh

| Chủ đề | File |
|---|---|
| Hợp đồng "đạt yêu cầu" | `.claude/skills/eval-results/reference/acceptance-gates.md` |
| Phán quyết hiện hành | `reports/2026-10-02_acceptance_verdict_srcsamp.md` |
| Đăng ký trước vòng 2 | `docs/PREREG_CANDIDATE2_2026-10-02.md` |
| Các hướng H1–H4 (NEXT_DIRECTION) | `docs/NEXT_DIRECTION_2026-10-02.md` |
| Config app | `docs/APP_CONFIG_GUIDE.md`; chế độ nhị phân: `docs/ANDROID_APP_SPEC.md` §3.4a (trên nhánh U1) |
| Đo L3 | `docs/L3_CAMERA_EVAL_GUIDE.md` |
| Bẫy hay gặp | `CLAUDE.md`, `docs/GOTCHAS.md` |
