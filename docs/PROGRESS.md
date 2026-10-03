# Theo dõi tiến độ

> **Nơi duy nhất** theo dõi việc đang làm và việc cần làm. Tracker cũ `docs/NEXT_TASKS_2026-10-02.md` đã xoá
> (03/10); mã việc T1–T9/D1–D4 của nó không dùng nữa.
>
> **Các file khác KHÔNG theo dõi trạng thái.** `docs/*_plan.md`, `docs/TASK_*.md`, `docs/PREREG_*.md`,
> `docs/NEXT_DIRECTION_*.md`, `docs/external_eval_next_tasks.md`, `docs/REVIEW_*.md` là kế hoạch / review / brief / đăng ký trước; ô ☐ hay
> "còn tồn" trong đó là bản gốc lúc viết. `reports/<ngày>_*.md` là kết quả chụp tại ngày đó. Việc nào trong
> các file ấy còn mở thì đã được chép vào đây (mục 2–5) — thêm việc mới thì thêm vào **file này**, không mở
> file theo dõi mới.
>
> **Cách cập nhật:** khi một việc đổi trạng thái, sửa ô "Trạng thái", ghi ngày; việc xong thì chuyển xuống mục 7.
> Ký hiệu: 🏃 đang chạy · ⏳ chờ việc khác · 👤 chờ tác giả · 🔜 làm được ngay · ✅ xong · ⏸ hoãn.
> Mã việc: **A** đang chạy · **U** chờ tác giả · **N** làm sau khi train xong · **R** làm được ngay · **S** để sau.

**Cập nhật lần cuối:** 03/10/2026 21:20 (+0700). Trạng thái server là **ảnh chụp lúc đó** — xem lại bằng lệnh ở mục 1.

## 0. Tình trạng tổng quát

| Mục | Hiện tại |
|---|---|
| Ứng viên ship | `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`, `best_model_auprc.pth`, fold 4 |
| Phán quyết | **CHƯA CÓ TIÊU CHÍ CHỐT** (B4 chuyển sang báo cáo 02/10) — `reports/2026-10-02_acceptance_verdict_srcsamp.md` |
| Khoảng cách thật | Theo **khung 3 trụ** (03/10; khám phá — ngưỡng post-hoc, fold 4): III-a ảnh điện thoại độ nhạy 0,873 / độ đặc hiệu 0,731; **III-b ảnh lâm sàng khác nguồn độ nhạy chỉ 0,604 / 0,520 / 0,524 theo tông** — đây là chỗ hụt; S_min/Sp_min/δ chưa chốt; I-1, II-3 chưa đo. (Khung cũ: B2 cận dưới 0,7406 < 0,81; C4a dưới 0,47) |
| **Review ngoài 03/10** | `docs/REVIEW_DANH_GIA_2026-10-03.md`: theo reviewer, vấn đề chính nằm ở **thiết kế đánh giá**. Đối chiếu code 03/10 (`reports/2026-10-03_review_crosscheck.md`) xác nhận: mốc B2 0,81 là bác sĩ đọc **dermoscopy** (mốc cùng loại ảnh lâm sàng là 0,47) · teacher của C2 **không** train cùng công thức với student (thiếu sampler theo nguồn; chỉ có checkpoint pAUC) · checkpoint `_auprc` và fold ship chọn theo AUPRC val **gộp** ISIC+PAD. Chưa đo: B1 pAUC và B3 (nhãn CCM) có cận dưới hụt mốc 0,0002 / 0,0001, nhỏ hơn sai số Monte Carlo **ước tính** ⇒ nhãn có thể lật theo seed (R6). Việc phát sinh (review 03/10 + review luận văn 20/09): U10, U11, R6–R12, S9–S16; ghi chú sửa luận văn `thesis/CAN_SUA_SAU.md` #8–#23 |
| Quyết định lớn đang treo | **U10 đã quyết 03/10: khung 3 trụ** (`acceptance-gates.md` §2.1). Còn treo: **S_min / Sp_min** và **δ của C2** (U7) — nên chốt **trước khi mở test vòng 2** |
| Đang làm | Vòng chọn thứ hai: teacher của P1 gần xong, KD P1 chạy tiếp theo (mục 1) |
| Hợp đồng chấm | `.claude/skills/eval-results/reference/acceptance-gates.md` — 03/10: C2 = không kém teacher quá δ; **khung 3 trụ §2.1** (III-a ảnh điện thoại + III-b ảnh lâm sàng khác nguồn theo tông, tại ngưỡng app); B2 0,81 thôi làm cổng; S_min/Sp_min/δ chờ quyết |

## 1. Đang chạy 🏃 — vòng chọn thứ hai

Đăng ký trước: `docs/PREREG_CANDIDATE2_2026-10-02.md` (luật chọn §4, endpoint §5, phụ lục §7). Review 03/10 §2: chạy cho xong vì đã đăng ký, nhưng **giới hạn thời gian** — vòng này không chạm khoảng cách B2, và chênh giữa các ứng viên có thể nhỏ hơn nhiễu train ~0,005. Server `vastnew`,
tmux `cand2`, khởi chạy 02/10 15:34:41 UTC. Ước lượng (03/10 10:31 UTC, suy từ mốc thời gian log, không phải cam kết): job bắt đầu 21:47 UTC 02/10; fold 0 ~2 giờ, fold 1 ~4,5 giờ, fold 2 + fold 3 ~5,8 giờ cộng lại; fold 4 bắt đầu ~10:09 UTC ⇒ A3 xong khoảng 19:00–23:10 03/10; A4 ước 5–8 giờ (A2 mất 4 giờ 46 phút; teacher P1 nặng 30,7 so với 10,7 GFLOPs, `reports/benchmark/*.json`, nhưng chỉ chạy forward trên tập train vì logits val được cache) ⇒ xong khoảng 00:00–07:00 04/10 (giờ VN). Early stopping theo `val_loss`, patience 10 (`src/training/trainer.py:121`).

| Mã | Job | Run-dir (trong `experiments/runs_newsplit_ddi/`) | Ai / ở đâu | Trạng thái (03/10 10:31 UTC) |
|---|---|---|---|---|
| A1, A2 | ✅ xong — xem mục 7 | | | |
| A3 | teacher `convnextv2_base` | `teacher/convnextv2_base` | server | 🏃 **4/5 fold** xong; fold 4 ở epoch 2/50, ~7 phút/epoch (`run/progress_all.sh`) |
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
từng train trên instance `vastnew` hiện tại trước vòng này (fold 0 đã xong 02/10).

## 2. Chờ tác giả 👤

| Mã | Việc | Vì sao cần | Link / file | Trạng thái |
|---|---|---|---|---|
| U5 | Đặt mốc cho đo L3: **T1** (độ nhạy với thuật toán thu nhỏ ảnh) và **T2** (chụp lại qua app) + danh sách `sample_id` cho T2 | Phải chốt trước khi chạy, nếu không thành post-hoc (tên T1/T2/T3 theo đúng guide). Review xếp L3 vào trụ II và gọi là "nguồn lỗi thực tế phổ biến nhất"; rủi ro cụ thể còn lại: app thu nhỏ bằng bilinear, train dùng PIL LANCZOS (`docs/ANDROID_APP_SPEC.md` L2) | `docs/L3_CAMERA_EVAL_GUIDE.md` §1, §2, §4; review §1.11 | 👤 ⏸ (tác giả 03/10: đo phía mobile, làm sau) |
| U6 | Đo A1 trên đúng `.pte` ship | A1 là cổng bắt buộc, đang CHƯA ĐO — phán quyết không thể "đạt" khi chưa đo. Pixel 6a **rút sạc**, chế độ máy bay. Review (trụ I) đề xuất thêm: p95 chứ không chỉ trung vị, độ trễ end-to-end (decode → EXIF → resize → normalize → model), cold start, bộ nhớ đỉnh trên app thật | repo `SkinDetector-eval`: `tools/run_benchmark.sh`; review §3 trụ I | 👤 ⏸ (tác giả 02/10: chưa cần; **03/10: sẽ đo phía mobile, làm sau**) — review xếp đây vào phần lõi của "chạy tốt trên điện thoại" |
| U7 | Chốt các mốc còn mở của khung 3 trụ (`acceptance-gates.md` §2.1) — **S_min, Sp_min, δ của C2**; mốc đề xuất I-1 (p95 ≤ 80 ms), II-3 (< 0,5%), II-1/II-2 | Chốt **trước khi mở test vòng 2** thì không post-hoc với P1/P2 (với P0 luôn là post-hoc). S_min/Sp_min lập luận từ use case sàng lọc, nên có GVHD; δ theo nguyên tắc, không theo cận dưới C2 hiện có (mọi δ > 0,0068 làm P0 qua) | `acceptance-gates.md` §1, §2.1 | 👤 |
| U11 | Có thêm so sánh với kỹ thuật nén / điều chuẩn khác không (review luận văn ThesisForge Issue 4) | Câu trung tâm 1 là "thu gọn và triển khai" ⇒ khả năng bị hỏi. Hai ứng viên: (a) **label smoothing không teacher** — **chưa từng chạy** (đối chiếu 03/10: chỉ có trong template 7 lớp tháng 4; 21/06 tác giả từ chối như đòn bẩy chống overfit); kiểm giả thuyết "KD nhị phân ≈ label smoothing thích ứng" mà luận văn đang viết như cơ chế; cần sửa code nhỏ + train 5 fold một student; (b) **PTQ INT8** cho model ship — mở lại quyết định de-scope 14/07 (`docs/KD_DESIGN_REVIEW_2026-07-13.md:10`); rủi ro lowering. Review còn nêu: QAT (ngoài PTQ), baseline class-balanced / biến thể focal (baseline hiện đã dùng focal loss — luận văn nói được điều này), pruning và kiến trúc mobile cổ điển (MobileNetV3 — đã có rồi bị xoá khỏi registry 15/07); phần không làm thì ghi thành hạn chế (`thesis/CAN_SUA_SAU.md` #15). Lưu ý: run mới trên splits v2 chỉ so được với KD/baseline v2 cùng student, không với số v1 của luận văn | `reports/2026-10-03_thesis_review_checks/README.md` §3 | 👤 |
| U8 | Có tìm nguồn ảnh điện thoại/lâm sàng mới không — **cũng chính là tập xác nhận** | Ứng viên đòn bẩy cho B2/C4a (cần cả hai lớp, đa dạng tông da, không trùng HAM/Fitz/PAD/DDI). Review §3: test PAD đã mở nhiều lần và ngưỡng app chọn sau khi xem nó ⇒ muốn kết luận "đạt" đứng được cần một tập **chưa ai chạm**, chạy **một lần**; phương án: tập ngoài (review nêu Derm7pt phần clinical và MIDAS — chưa kiểm license/nhãn; **MIDAS tác giả đã loại 21/09 ở cả vai tập đánh giá**, chỉ xét lại nếu mở lại quyết định đó), tự thu qua app, hoặc chấp nhận kết luận "exploratory". Một phương án review nêu (kèm cảnh báo): **ước lượng out-of-fold trên toàn bộ ảnh PAD** (dựng từ `val_predictions` sẵn có: 888 ca ác PAD trong 5 val fold + 189 ở test ≈ 1.077, thay vì 189) — thu hẹp CI nhưng là hiệu năng của *quy trình train*, không của một checkpoint ship, và có optimism vì val PAD đã dùng để chọn checkpoint. Nếu dùng tập xác nhận: tính cỡ mẫu **trước** khi mở (review §3 có bảng thô: sens thật 0,87, S_min 0,80 cần ~180 ca ác cho power 80%), chạy **một lần**. **03/10: tác giả chọn thu bộ ảnh mới** (hướng: hợp tác bệnh viện qua GVHD, thu qua app, nhãn sinh thiết, duyệt đạo đức; ~180 ca ác cho power 80% theo ước tính thô của review); **đánh giá của assistant** (03/10, nguồn web chưa kiểm chéo) về tool crawl ảnh trên mạng: không hợp làm **tập xác nhận** — ảnh web thường không có xác nhận sinh thiết, vướng bản quyền (vd trang giấy phép DermNet), dễ trùng nguồn với Fitzpatrick17k (vốn lấy từ hai atlas), không rõ thiết bị chụp, và là dữ liệu sức khoẻ (Nghị định 13/2023; Luật BVDLCN 91/2025/QH15 hiệu lực 01/01/2026 — áp dụng cụ thể nên hỏi trường/GVHD). Dùng được: tool **tải + xử lý** các bộ có giấy phép và nhãn rõ (theo khuôn `download_external` → `prepare_external` → kiểm trùng đã có); ảnh không phải tổn thương làm mẫu âm cho cổng OOD (S7); ảnh người dùng tự chụp để đo độ bền chất lượng ảnh (S14). Là mở rộng scope — MIDAS từng bị loại vì lý do đó | review §3 "Tập xác nhận" | 👤 |
| U9 | Các quyết định còn treo của arm augmentation | `docs/domain_aug_plan.md` §8: #2 (chạy thêm phương án (b) hai cường độ hay dừng hẳn — tài liệu khuyến nghị **dừng**), #3 (gắn vào câu hỏi nghiên cứu nào), #4 (calibration có đưa lại luận văn không — app giờ nhị phân; review luận văn ThesisForge Issue 2 cũng hỏi ECE/Brier — nếu không đưa lại thì phải nói lý do trong luận văn); #5 coi như **đã thay** bằng vòng chọn thứ hai | `docs/domain_aug_plan.md` §8 | 👤 |

## 3. Làm khi vòng chọn thứ hai train xong ⏳ — đúng thứ tự (prereg §4, §5, §7)

| Mã | Việc | Ai / ở đâu | Lệnh / ghi chú | Trạng thái |
|---|---|---|---|---|
| N1 | **Tính luật chọn từ val và COMMIT kết quả** — trước mọi bước đọc số test | server (Python) | **Script sẵn (03/10):** `bash run/select_candidate.sh OUT_DIR=reports/<ngày>_candidate2_selection CANDIDATES="P0=… P1=… P2=…"` (thứ tự P0, P1, P2; đường dẫn đầy đủ trong header `run/select_candidate.sh`). Chỉ đọc file `val_*`, từ chối mọi file khác; chạy thử 03/10 trên val P0+P2 ra fold ship P0 = fold_4, khớp `reports/2026-10-01_srcsamp_item2_3.md` §5 — **lượt thử này đã cho thấy thứ hạng P0 vs P2 trên val PAD** (P0 xếp trên; chỉ val, không vi phạm §7.2; thư mục thử `.tmp/n1_test/` đã xoá). Việc còn lại: Trung bình 5 fold AUPRC trên hàng PAD của `fold_*/val_predictions_auprc.csv` ghép theo thứ tự dòng với `data/splits/isic2024/fold_N/val_split.csv` (**kiểm số dòng và nhãn khớp từng dòng**), cho P0/P1/P2; luật hoà §7.1; fold ship = trung vị `val_metrics_auprc.json` | ⏳ |
| N2 | Kéo kết quả về Mac + `aggregate` (cả checkpoint chính và `_auprc`) | Mac + server | `bash run/pull_results.sh pull`; `bash run/aggregate.sh RUN_DIR=<run>` và `… METRICS_NAME=test_metrics_auprc.json` (teacher: chỉ bản chính). `aggregated*.md` chứa số test — chỉ chạy sau N1 | ⏳ |
| N3 | Eval ngoài miền: HAM headline + Fitzpatrick 4 biến thể | server | `bash run/evaluate_external.sh DATASET=… RUNS="<run-dir>" OUT_ROOT=<riêng>`. Student/baseline (P1, P2, baseline repvit): thêm `CKPT_NAME=best_model_auprc.pth VAL_PRED_NAME=val_predictions_auprc.csv`. **Teacher `convnextv2_base` cần lượt riêng với checkpoint mặc định** (teacher không có `best_model_auprc.pth`) — thiếu nó thì không tính được C2 của P1 trên Fitz/HAM | ⏳ |
| N4 | CI các cổng | server | `bash run/bootstrap_ci.sh RESULTS_DIR=<cây symlink> PAIR="<student>:<teacher>" SUBGROUP=source\|tone_group METRICS=auc_roc,auprc,pauc_at_tpr80,sens_at_90spec,sens_at_80spec`. Dựng cây symlink như P0 (`.tmp/ci_gates/` trên server: student = file `_auprc`, teacher = file chính). C2 = student vs **teacher của chính cặp**; C1 = KD vs baseline cùng student. **Khai trong báo cáo** (review §1.5, đối chiếu 03/10): teacher không dùng sampler theo nguồn và chỉ có checkpoint pAUC, student có cả hai ⇒ C2 không phải so sánh cùng công thức (P0: student KD **không** sampler theo nguồn có AUPRC PAD 0,7997 vs teacher 0,7966, `reports/ci_ddi_indomain.md:67,87`, CI từng run, chưa ghép cặp — xem R7) | ⏳ |
| N5 | Export `.pte` + parity cho ứng viên được chọn | server | `OUT=` riêng; **cùng `CKPT`** ở `make_benchmark_set.sh` và `export_executorch.sh`; repvit: kiểm XNNPACK, lùi portable nếu hỏng. Nếu chọn lại P0: `.pte` và A3/A4 đã có | ⏳ |
| N6 | Đo A1/A3/A4 trên điện thoại cho `.pte` mới | Android / Pixel 6a | như U6 | ⏳ |
| N7 | Phán quyết mới | Mac | `reports/<ngày>_acceptance_verdict_<ứng viên>.md`; luật gộp **khung 3 trụ** I-1+II-1+II-2+II-3+III-a+III-b+C2 (`acceptance-gates.md` §2.1); báo cáo B1, B3, B4, C1, C3, C4b, A2, hành vi tại ngưỡng app (`phone_sens90` + Youden toàn cục). **Khai post-hoc**: vòng thứ hai, mọi tập kiểm đã nhìn, hai cặp chọn có tham khảo số v1 (prereg §1, §7.4). Viết sau N6, hoặc ghi A1/A3/A4 = CHƯA ĐO rồi viết lại sau N6. **Ghi thêm** (review): C2 là CI của trung bình 5 fold, III-a/III-b là Wilson CI trên fold ship (`acceptance-gates.md` §2.1); III-a/III-b tính bằng script đã tham số hoá (R13) | ⏳ |
| N8 | Config app + bundle | server + Mac | `run/make_app_config.sh … SKIP_GLOBAL_OP=1` (U1 đã merge); cập nhật `catalog.json` + sinh lại `SHA256SUMS` trong **cả hai** bản `materials_for_mobile/` (`~/Documents/` và `~/Documents/android-projects/SkinDetector-eval/`) | ⏳ |
| N9 | Cập nhật file này, memory, `thesis/CAN_SUA_SAU.md` (chỉ ghi chú) | Mac | — | ⏳ |

## 4. Làm được ngay 🔜

Việc rẻ phát sinh từ review 03/10 — kiểm tra, **không** đổi model hay mốc. Tất cả chỉ đọc file đã có; không cần GPU (chạy được song song với A3/A4). Đề xuất của assistant (chưa phải quyết định của tác giả): giới hạn nửa ngày cho cả nhóm.

| Mã | Việc | Ai / ở đâu | Ghi chú | Trạng thái |
|---|---|---|---|---|
| R6 | Độ nhạy của phán quyết với seed bootstrap: chạy lại CI của B1 (pAUC, AUC) và B3 với 5 seed | server | `bash run/bootstrap_ci.sh RESULTS_DIR=<cây .tmp/ci_gates/…> SUBGROUP=source SEED=<s> METRICS=…,sens_at_80spec OUT_JSON=… OUT_MD=…` (B1 là hàng `isic2024` của bảng theo nguồn ⇒ bắt buộc `SUBGROUP=source`; B3 chạy trên cây Fitzpatrick headline) (ra file riêng, đừng ghi đè `reports/ci_gates_*`). Ước tính (chưa đo) sai số Monte Carlo của cận dưới (B = 2000): B1 pAUC ~0,0005, B3 ~0,0007 > khoảng cách tới mốc 0,0002 / 0,0001 ⇒ dự đoán nhãn CCM có thể lật (review §1.3) | 🔜 |
| R7 | Tách hiệu ứng sampler khỏi C2: CI ghép cặp `x_kd__ddi` vs `x_teacher__ddi` trên PAD | server | `bash run/bootstrap_ci.sh RESULTS_DIR=.tmp/ci_ddi_indomain PAIR="x_kd__ddi:x_teacher__ddi" SUBGROUP=source OUT_JSON=… OUT_MD=…` (cây symlink trên server, ghi trong `reports/ci_ddi_indomain.json`; nếu đã xoá thì phải dựng lại — tên `x_*` xem `reports/ci_ddi_indomain.md`, cách dựng chưa được ghi ở đâu). Nếu Δ PAD chứa 0 ⇒ không phân định được student KD (không sampler theo nguồn) với teacher trên PAD, tức khoảng "vượt teacher" +0,0619 của P0 nhiều khả năng đến từ sampler/checkpoint (review §1.5) | 🔜 |
| R8 | So hàm `pauc_at_tpr` với hàm chấm chính thức ISIC 2024 trên cùng mảng dự đoán | server | `src/evaluation/metrics.py:11-45`; lấy code chấm chính thức từ trang cuộc thi. Chỉ để khẳng định B1 so được với Kurtansky (review §1.8) | 🔜 |
| R9 | Fold ship của P0 nếu chọn theo AUPRC val **PAD** thay vì val gộp — chỉ chẩn đoán | server | `scripts/select_candidate.py` đã có `pad_val_auprc`. **Không** đổi fold ship: luật đã đăng ký là trung vị AUPRC val gộp (`docs/PREREG_CANDIDATE2_2026-10-02.md` §4); đổi là lệch prereg, phải khai (review §1.12) | 🔜 |
| R10 | Liệt kê mọi lần đã mở test PAD / HAM / Fitz (ngày, ứng viên, mục đích) để khai trong luận văn | Mac | từ `git log -- reports/` + mục 7 của file này (review §1.10) | 🔜 |
| R11 | PPV / NPV tại ngưỡng app ở prevalence giả định 1% và 5% (ảnh điện thoại) — chỉ báo cáo | Mac | Tính từ độ nhạy/độ đặc hiệu đã có trong `reports/2026-10-02_threshold_options/summary.csv`; PAD có ~48% ca dương nên PPV đo thẳng trên test là ảo (review 03/10 §3 "báo cáo kèm") | 🔜 |
| R12 | Công bằng tại ngưỡng cố định, có CI: chênh độ nhạy (tỉ lệ bỏ sót) và chênh độ đặc hiệu giữa các tông, **CI ghép cặp**, tại ngưỡng app; thêm sens@95spec theo tông | server | Review luận văn ThesisForge Issue 6 Fix 1–2. Đã có: sens@80/90spec theo tông + Wilson CI từng nhóm tại ngưỡng app (`reports/2026-10-03_thesis_review_checks/` §2). `bootstrap_ci.py` chưa có metric tại ngưỡng cố định và chưa có sens@95spec ⇒ sửa nhỏ (code-change). Fitz đã nhìn ⇒ chỉ báo cáo | 🔜 |
| R13 | Tham số hoá `reports/2026-10-03_thesis_review_checks/tone_at_app_threshold.py` và `reports/2026-10-02_threshold_options/threshold_options.sh` (đang hard-code đường dẫn P0) để tính III-a/III-b cho P1/P2 | Mac (bash/stdlib) | Cần cho N7 vòng 2 theo `acceptance-gates.md` §2.1 | 🔜 |

## 5. Để sau / hoãn ⏸

| Mã | Việc | Ghi chú |
|---|---|---|
| S1 | Thêm ảnh dermoscopy vào train (hướng H3 trong `docs/NEXT_DIRECTION_2026-10-02.md`) | Tác giả: tạm không làm. B4 đã thành báo cáo |
| S2 | Đo L3-T1 (thu nhỏ ảnh) | Chờ U5. HDF5 ISIC đã chép lên server ở `data/l3/isic2024_train-image.hdf5` (02/10; sha256 khớp bản Mac), cố ý **không** đặt ở `data/raw/isic2024/` để `prepare` vẫn không chạy được |
| S3 | Đo L3-T2 (chụp lại ảnh đã biết nhãn qua app) | Chờ U5, N8 và chế độ "chụp để đánh giá" trên app |
| S4 | Sửa luận văn | **Chỉ ghi chú, chưa sửa** (tác giả). Danh sách `thesis/CAN_SUA_SAU.md`. **03/10: tác giả chọn phương án A cho splits v1/v2** (công khai rò rỉ, giữ Chương 4 v1 kèm nhãn lạm phát, thêm mục v2 tự chứa — `docs/thesis_ddi_section_checklist.md`; CAN_SUA_SAU #8) |
| S5 | Tính bù `valthr_*` cho ma trận v1 (cho luận văn) | 165 fold; ~913 MB `predictions*.csv` + `val_predictions*.csv` trên Mac, phải đẩy lên server trước. `run/backfill_valthr.sh` |
| S6 | Spec app: các mục chưa cập nhật cho chế độ nhị phân | §3.3, §3.7, §9.1 `ScanEntity`, MA7, R-RES-07, R-HOME-02/03, R-HIS-01 — liệt kê trong spec §3.4a |
| S7 | Cổng OOD (từ chối ảnh không phải tổn thương da) | Mới là thiết kế, **chưa code**: `docs/ood_gate_plan.md` (checklist §4, §9). Phạm vi an toàn app, không thuộc Chương 4 |
| S8 | sens@spec80 theo tông da trên Fitzpatrick crop70 cho ứng viên hiện tại (trước là R1) | Tác giả 03/10: không làm lúc này. C4a chính thức chấm trên biến thể headline; crop70 không phải cổng. Nếu làm thì chỉ chẩn đoán, và dùng nó để quyết thay đổi (vd. app cắt khung) là post-hoc (`acceptance-gates.md` "Chọn ≠ phát triển") |
| S9 | Chọn checkpoint theo AUPRC val **PAD** (hoặc trung bình theo nguồn) thay vì val gộp | Review §1.12. Phải sửa code (thêm khoá monitor theo nguồn: `EXTRA_MONITOR_KEYS` ở `src/training/callbacks.py:75` chỉ có metric trên toàn val; không lưu checkpoint từng epoch nên không chọn lại offline được) **và train lại**. Chờ kết quả R9 |
| S10 | Đo trên ≥ 2 máy, trong đó có một máy cấp thấp | Review §3 trụ I: mốc độ trễ phải đạt trên máy yếu nhất. Hiện chỉ có Pixel 6a. Chờ U7 (mốc I-1) và việc đo phía mobile (U6) |
| S11 | Parity tầng 2 của app: cùng ~200 ảnh PAD qua pipeline Kotlin thật (decode → resize → normalize) và pipeline Python, so \|Δlogit\| và **tỉ lệ đổi quyết định** tại ngưỡng app | Review §1.11; spec `docs/ANDROID_APP_SPEC.md` R-DEV-04 / §12.2. Khác L3-T1/T2 (U5). Rủi ro chính: app thu nhỏ bằng bilinear (mặc định trong spec), train dùng PIL LANCZOS. Cần công việc phía app (test instrumented) |
| S12 | Phân tích lỗi: xem từng ca ác bị bỏ sót và ca lành bị báo nhầm (PAD, Fitzpatrick) + bản đồ chú ý Grad-CAM — model nhìn tổn thương hay nhìn tín hiệu miền | Review luận văn Issue 5. `src/evaluation/grad_cam.py` có sẵn nhưng chưa script/runner nào gọi ⇒ cần script mới (code-change) + chạy trên server. Đã có: phân tích theo nguồn, theo tông, theo loại tổn thương trên HAM (ad-hoc) |
| S13 | Phụ lục tái lập cho luận văn: commit, môi trường (phiên bản Python/PyTorch/timm/ExecuTorch), lệnh chạy từng pha, checksum splits/predictions | Review luận văn Issue 7. Làm lúc viết luận văn |
| S14 | Độ bền theo chất lượng ảnh: mờ, thiếu sáng / dư sáng, chụp xa — trên ảnh PAD test, đo độ nhạy / độ đặc hiệu tại ngưỡng app khi ảnh bị làm xấu có kiểm soát | Review 03/10 §3 "báo cáo kèm"; trực tiếp phục vụ câu trung tâm 2 (ảnh camera thực tế). L3-T1 chỉ phủ khâu thu nhỏ ảnh. Cần script mới (code-change) + chạy server |
| S15 | Độ nhạy theo loại ung thư (BCC / SCC / MEL) trên ảnh điện thoại | Review 03/10 §3. Split CSV chỉ còn nhãn nhị phân; cần cột `diagnostic` của PAD — `data/raw/pad_ufes_20/` không còn trên box, nhưng **trên Mac còn bản metadata đầy đủ** `logs/_server_tmp_20260926/pad_metadata_dl` (CSV 2.298 dòng, có `diagnostic`, `img_id`) ⇒ ghép theo `image_id`, kiểm khớp nhãn nhị phân; MEL rất ít ca ⇒ CI rộng |
| S16 | Train lại teacher **cùng công thức** với student (sampler theo nguồn, checkpoint AUPRC) | Review 03/10 §1.5(a)(b): teacher hiện thiếu sampler theo nguồn ⇒ (a) C2 không công bằng; (b) teacher đúng công thức có thể làm KD hữu ích hơn trên PAD. Teacher `efficientnetv2_m` công thức hiện hành mất ~4 giờ 15 phút cho 5 fold (`logs/train_teacher_20260925_120331.log`: 12:03 → 16:18 ngày 25/09), số epoch có thể khác khi đổi sampler; dùng `output_dir=` (không ghi đè). Chờ kết quả R7 |

**Đồ tồn đọng cần dọn khi tiện:** stash `apply-metadata-for-training` trên server; `.tmp/untracked_before_develop_20261002/`
(server); `.tmp/archived_root_drivers_20261002/` (Mac). (`docs/NEXT_TASKS_2026-10-02.md` đã xoá 03/10.)

## 6. Chưa verify được / chỉ có trên server

- Trạng thái train ở mục 1 là ảnh chụp lúc 03/10 10:31 UTC; job có hoàn thành hay không, mất bao lâu: xem lại bằng lệnh ở mục 1.
- HDF5 ở `data/l3/` và sha256 của nó: chỉ kiểm được trên server.
- Nhánh Android `support-binary-config`: 185/185 unit test theo lần chạy 02/10 trên Mac (ghi trong commit message 8cadf8f); instrumented test và giao diện **chưa** chạy.
- Lượt chạy thử `select_candidate.py` trên server (03/10, val P0+P2) và mọi số của R2 trước khi kéo về: chỉ có trên server.
- Câu "chưa cần" (U6) và "giữ các mốc đề xuất thử xem" (U7) là lời tác giả trong hội thoại 02/10.
- Đối chiếu review 03/10: số Cochrane (đọc dermoscopy 81% vs nhìn ảnh lâm sàng 47% ở độ đặc hiệu 80%, chỉ melanoma) kiểm qua web (PMC6517096), sub-agent kiểm chéo không kiểm lại được. Ngưỡng app: config thật (`SkinDetector-eval/materials_for_mobile/models_srcsamp_auprc_fold4/config.json`) có `phone_sens90` = 0,570523, `displayMode: binary`; app quyết định `rawProb ≥ ngưỡng` (`SkinDetector` develop, `core/ml/.../decision/Decision.kt:17-20`) — đọc code, chưa chạy trên máy. Sai số Monte Carlo ở R6 là ước tính, chưa đo.
- Ước lượng giờ xong A3/A4 ở mục 1 suy từ mốc thời gian log, không phải đo.
- Nguồn web chưa kiểm chéo (chỉ assistant đọc, 03/10): văn liệu KD (Hinton 2015, Mirzadeh 2020, Cho & Hariharan 2019, Furlanello 2018); Cochrane Dinnes 2018; SCIN (nhãn bác sĩ, 89,0% không ác tính); trang giấy phép DermNet; Fitzpatrick17k chia theo atlas (12.672 / 3.905); Nghị định 13/2023 và Luật 91/2025/QH15.

## 7. Đã xong ✅

| Ngày | Việc | Nơi ghi |
|---|---|---|
| 03/10 | Kiểm theo review luận văn ThesisForge: (1) bootstrap theo bệnh nhân (một run v2, AUC + sens@spec80, script tự viết, B = 1000): PAD gần như không đổi ⇒ không cần cho B2; ISIC AUC rộng thêm ~17% (ô AUC của B1 lật, cổng vốn đã CCM); AUPRC/pAUC/hiệu ghép cặp chưa đo; (2) độ nhạy theo tông tại ngưỡng app, Fitzpatrick fold 4: sáng 0,604 · trung bình 0,520 · tối 0,524; cộng 5 fold 0,712 · 0,657 · 0,699 (chỉ báo cáo, một fold, ngưỡng post-hoc, Fitz đã nhìn); (3) label smoothing chưa từng chạy | `reports/2026-10-03_thesis_review_checks/` (README + 2 script thư viện chuẩn) |
| 03/10 | **U10: tác giả chọn khung 3 trụ** ("phương án A — khung đánh giá"; khác "phương án A — splits v1" ở S4): I chạy được · II giữ chất lượng · III tại ngưỡng app — III-a ảnh điện thoại (PAD) **và** III-b ảnh lâm sàng khác nguồn (Fitzpatrick) theo từng tông da; C2 giữ. B2 0,81 thôi làm cổng (tham chiếu); B1, B3 báo cáo; C4a gộp vào III-b. Post-hoc. Kèm: crawl ảnh web không làm tập xác nhận (hướng: hợp tác bệnh viện qua GVHD); luận văn chỉ trình bày tiêu chí cuối + đoạn khai báo (CAN_SUA #23) | `acceptance-gates.md` §1, §2.1; `CLAUDE.md`; `thesis/CAN_SUA_SAU.md` #23 |
| 03/10 | U4: tác giả **giữ quy tắc ngưỡng app `pad_sens90`** (độ nhạy 90% trên ảnh PAD của val; fold 4 = 0,5705). Quy tắc vẫn **post-hoc** với test PAD fold 4 ⇒ xác nhận trên dữ liệu mới (U8) | `reports/2026-10-02_threshold_options/README.md`; `acceptance-gates.md` "Báo cáo bắt buộc" |
| 03/10 | Tác giả xác nhận C2: vẫn bắt buộc, tập miền PAD·Fitz·HAM, câu chữ "giữ được hiệu năng của teacher" | `acceptance-gates.md` §1 |
| 03/10 | Tác giả đổi tiêu chí 2: C2 = **không kém teacher quá δ** thay cho "vượt teacher" (post-hoc; δ chờ quyết) — căn cứ văn liệu đã kiểm qua web | `.claude/skills/eval-results/reference/acceptance-gates.md` §1; `CLAUDE.md`; `thesis/CAN_SUA_SAU.md` #22 |
| 03/10 | Tác giả chọn **phương án A** cho luận văn (splits v1 rò rỉ) | `thesis/CAN_SUA_SAU.md` #8–#13 |
| 03/10 | U3: màn hình kết quả Android xử lý chế độ nhị phân — rẽ nhánh theo quyết định, không theo `riskBand` (`ResultViewModel.kt` `contentFor`); kèm màn hình ảnh không hợp lệ (PR #23) và phần chi tiết kỹ thuật (PR #24). **Chưa** chạy instrumented test / trên máy | repo `SkinDetector`, develop: PR #22 (08:50), #23 (09:46), #24 (11:13); sau đó #25 (18:39, rà câu chữ) và #26 (18:52, Room entities/DAO) |
| 03/10 | Nhận review ngoài và đối chiếu từng mục "Đối chiếu trong code" (1.1–1.12) với code, có kiểm chéo FACTS + PATCH; sinh U10, R6–R10, S9–S11 | `docs/REVIEW_DANH_GIA_2026-10-03.md`; `reports/2026-10-03_review_crosscheck.md` |
| 03/10 | Brief một trang gửi reviewer | `docs/PROJECT_BRIEF_FOR_REVIEW.md` (commit 3815e7c) |
| 03/10 | R2: CI ghép cặp item 3 (checkpoint AUPRC − checkpoint pAUC của P0), chỉ báo cáo: 0/25 ô kém có ý nghĩa; trên PAD không phân định (chưa loại trừ mức kém nhỏ) | `reports/2026-10-03_item3_ckpt_paired.md` |
| 03/10 | R4: báo cáo arm DDI (đóng `domain_aug_plan.md` §9.4) | `reports/2026-10-03_ddi_arm.md` |
| 03/10 | R3: CLAUDE.md "Data integrity" ghi 656 dòng DDI ở train phía server; bản splits trên Mac là bản trước DDI | `CLAUDE.md` |
| 03/10 | R5: mục 1.3 "DDI — nguồn train thứ ba" | `docs/PREPROCESSING.md` §1.3 |
| 03/10 | Script luật chọn val-only cho N1 | `scripts/select_candidate.py`, `run/select_candidate.sh` |
| 02/10 | A2: KD `efficientnetv2_m → repvit_m1_0` 5/5 fold, xong 21:46 UTC (~4 giờ 46 phút) | `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_repvit_m1_0__srcsamp` (server) |
| 02/10 | A1: baseline `repvit_m1_0` 5/5 fold, xong 16:59 UTC (~1 giờ 25 phút) | `experiments/runs_newsplit_ddi/baseline_repvit_m1_0__srcsamp` (server) |
| 02/10 | Ô PAD của C1: ΔAUPRC −0,0008 [−0,0199, +0,0187] ⇒ C1 CHƯA CHỨNG MINH | `reports/2026-10-02_c1_pad_cell_srcsamp.md` (PR #13) |
| 02/10 | `valthr_*`: độ nhạy/độ đặc hiệu ở ngưỡng chọn trên val, trong trainer + `evaluate.py` + tính bù cho cây v2 | PR #13, #16; `reports/valthr/` |
| 02/10 | Công cụ báo cáo dùng ngưỡng val (`compare_kd_results`, `analyze_pad_ablation`) | PR #16 |
| 02/10 | Merge app-config + gates/guides | PR #14, #15 |
| 02/10 | Merge chế độ app nhị phân: nhánh ML `feat/binary-app-config` (PR #20, repo skin-cancer-detector) + nhánh Android `support-binary-config` (PR #21, repo android-skin-detector) | develop của hai repo |
| 02/10 | B4 chuyển sang báo cáo; phán quyết thành CHƯA CÓ TIÊU CHÍ CHỐT | PR #17 |
| 02/10 | Đăng ký trước vòng chọn thứ hai (+ phụ lục §7) | PR #18 |
| 02/10 | Config app thật (chế độ nhị phân, `phone_sens90`) + `catalog.json` + `SHA256SUMS` | ngoài git: `exports/app_config/mobilenetv4_srcsamp_auprc_fold4/` (server), `materials_for_mobile/models_srcsamp_auprc_fold4/` (bản trong `SkinDetector-eval`) |
| 02/10 | `pull_results.sh` đã có `runs_newsplit_ddi` trong `ROOTS` (`domain_aug_plan.md` §9.1) | `run/pull_results.sh` |

**Code xong nhưng CHƯA merge:** không còn (U1, U2 đã merge 02/10; màn hình kết quả Android merge 03/10, PR #22–#24).

## 8. Tham chiếu nhanh

| Chủ đề | File |
|---|---|
| Hợp đồng "đạt yêu cầu" | `.claude/skills/eval-results/reference/acceptance-gates.md` |
| Phán quyết hiện hành | `reports/2026-10-02_acceptance_verdict_srcsamp.md` |
| Đăng ký trước vòng 2 | `docs/PREREG_CANDIDATE2_2026-10-02.md` |
| Các hướng H1–H4 (NEXT_DIRECTION) | `docs/NEXT_DIRECTION_2026-10-02.md` |
| Review ngoài + khung 3 trụ đề xuất | `docs/REVIEW_DANH_GIA_2026-10-03.md` (brief đã gửi: `docs/PROJECT_BRIEF_FOR_REVIEW.md`) |
| Review luận văn bản 20/09 (ThesisForge: kỹ thuật; ThesisPolisher: trình bày) | `docs/review_luan_van_grad_thesisforge.pdf`, `docs/danh_gia_luan_van_thesispolisher.pdf`; kiểm tra: `reports/2026-10-03_thesis_review_checks/` |
| Config app | `docs/APP_CONFIG_GUIDE.md`; chế độ nhị phân: `docs/ANDROID_APP_SPEC.md` §3.4a |
| Đo L3 | `docs/L3_CAMERA_EVAL_GUIDE.md` |
| Bẫy hay gặp | `CLAUDE.md`, `docs/GOTCHAS.md` |
