# Đăng ký trước — vòng chọn ứng viên thứ hai: hai cặp teacher–student mới (02/10/2026)

> Ghi và commit **trước khi train**. Mọi thay đổi sau khi đã thấy kết quả phải ghi là post-hoc, kèm ngày.
> Hợp đồng chấm: `.claude/skills/eval-results/reference/acceptance-gates.md` (bản 02/10: B4 chỉ báo cáo).
> Quyết định của tác giả 02/10/2026: chọn hai cặp "đổi teacher một cặp, đổi student một cặp"; luật chọn ứng
> viên = AUPRC trên ảnh PAD của val.

## 1. Vì sao có vòng này, và nó là vòng thứ mấy

Ứng viên hiện tại (`kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`, fold 4, `best_model_auprc.pth`)
có phán quyết **CHƯA CÓ TIÊU CHÍ CHỐT** (`reports/2026-10-02_acceptance_verdict_srcsamp.md`); khoảng cách thật là
B2 (PAD) và C4a (tông trung bình, tông tối). Đây là **vòng chọn thứ hai**: mọi tập kiểm (test in-domain, HAM10000,
Fitzpatrick17k) **đã được nhìn** qua ứng viên thứ nhất. Không có tập xác nhận mới ⇒ kết quả vòng này vẫn mang
thành phần post-hoc và phải khai như vậy (acceptance-gates §2.0 bước 3, §4 #9/#18).

## 2. Ứng viên (theo thứ tự đăng ký)

| # | Cặp | Đổi gì so với đối chứng | Trạng thái |
|---|---|---|---|
| P0 | `efficientnetv2_m → mobilenetv4_conv_medium` (`__srcsamp`) | — (đối chứng, đã có) | đã train, đã chấm |
| P1 | `convnextv2_base → mobilenetv4_conv_medium` (`__srcsamp`) | teacher | mới |
| P2 | `efficientnetv2_m → repvit_m1_0` (`__srcsamp`) | student | mới |

Công thức giống hệt P0, chỉ khác đúng một biến: splits v2 + 656 ảnh DDI ở train
(`experiments/runs_newsplit_ddi`), `AUG=light`, seed 42, 50 epoch, batch 64. Teacher dùng sampler mặc định (như
teacher P0); student dùng `data.sampler_stratify_by=source` và `training.callbacks.checkpoint.extra_monitors=[auprc]`.

## 3. Việc train (một GPU, tuần tự)

| Bước | Job | Lệnh (server, `export TMPDIR="$(pwd)/.tmp"`) | Ghi vào (mới, không ghi đè) |
|---|---|---|---|
| 1 | baseline `repvit_m1_0` (cho C1) | `bash run/train_student.sh STUDENT=repvit_m1_0 TEACHER=efficientnetv2_m TRAINING=baseline GPU=0 EXTRA="$E"` | `baseline_repvit_m1_0__srcsamp` |
| 2 | KD P2 | `bash run/train_student.sh STUDENT=repvit_m1_0 TEACHER=efficientnetv2_m TRAINING=distillation GPU=0 EXTRA="$E"` | `kd_efficientnetv2_m_to_repvit_m1_0__srcsamp` |
| 3 | teacher `convnextv2_base` | `bash run/train_teacher.sh TEACHER=convnextv2_base GPU=0 EXTRA="output_dir=experiments/runs_newsplit_ddi"` | `teacher/convnextv2_base` |
| 4 | KD P1 | `bash run/train_student.sh STUDENT=mobilenetv4_conv_medium TEACHER=convnextv2_base TRAINING=distillation GPU=0 EXTRA="$E"` | `kd_convnextv2_base_to_mobilenetv4_conv_medium__srcsamp` |

`E="output_dir=experiments/runs_newsplit_ddi run_suffix=__srcsamp data.sampler_stratify_by=source training.callbacks.checkpoint.extra_monitors=[auprc]"`
(cùng chuỗi đã dùng cho P0 — `run/README.md` mục C). Teacher dùng `output_dir=` vì `train_teacher.py` bỏ qua
`run_suffix`; thư mục `teacher/convnextv2_base` chưa tồn tại nên không ghi đè gì.

## 4. Luật chọn ứng viên ship — CHỈ dùng val

1. **Chọn cặp:** cặp có **trung bình 5 fold của AUPRC trên các hàng PAD-UFES-20 của val** cao nhất, tính từ
   `fold_*/val_predictions_auprc.csv` ghép theo thứ tự dòng với `data/splits/isic2024/fold_N/val_split.csv`
   (kiểm số dòng và nhãn khớp từng dòng). So giữa P0, P1, P2. Hoà (chênh < 0,005, sàn nhiễu chạy lại) ⇒ giữ
   cặp đứng trước trong bảng §2.
2. **Checkpoint:** `best_model_auprc.pth` (như P0).
3. **Fold ship:** fold có val AUPRC (toàn bộ val) **trung vị** trong 5 fold của cặp được chọn (như P0).
4. **Không** dùng test in-domain, HAM10000 hay Fitzpatrick17k cho bất kỳ lựa chọn nào ở trên.

## 5. Endpoint — chấm một lần, trên đúng ứng viên đã chọn

- **Cổng bắt buộc** (luật gộp 02/10): A1 + A3 + A4 + B1 + B2 + B3 + C2 + C4a, theo mốc hiện hành (B2 = 0,81 đã
  chốt; còn lại là mốc đề xuất, tác giả giữ nguyên "thử xem"). Nhãn theo cả CI 95% (§3 của hợp đồng).
- **C2** so student với **chính teacher của nó trong cùng arm** (P1: `teacher/convnextv2_base`; P2:
  `teacher/efficientnetv2_m`), ΔAUPRC, tập miền PAD · Fitz · HAM.
- **Báo cáo bắt buộc:** B4, C1 (KD − baseline: P1 dùng `baseline_mobilenetv4_conv_medium__srcsamp` đã có; P2 dùng
  baseline ở bước 1), C3, C4b, A2. Chấm cả ba cặp trên các tập kiểm để báo cáo, nhưng **chỉ** ứng viên chọn ở §4
  nhận phán quyết.
- **A1/A3/A4** đo lại trên `.pte` mới của ứng viên được chọn: export với `OUT=` riêng, parity PASS trước
  (`CKPT` giống nhau ở `make_benchmark_set.sh` và `export_executorch.sh`); với `repvit_m1_0` phải kiểm parity
  XNNPACK, có lùi về portable nếu hỏng (gotcha `.pte`).

## 6. Rủi ro đã biết (ghi trước)

- Bằng chứng v1 cho hai đổi thay này **lẫn lộn** (điểm ước lượng, không ghép cặp, splits v1 khác công thức):
  với student mobilenetv4, teacher convnextv2 cho Fitz AUPRC 0,6172 so với 0,6037 (effnet) nhưng HAM 0,4198 so
  với 0,4467; student repvit (teacher effnet) kém mobilenetv4 trên cả Fitz (0,5901) lẫn HAM (0,3665)
  (`reports/external/{fitzpatrick17k,ham10000}/headline/bootstrap_ci.md`).
- C2 đòi student **vượt** teacher; teacher mạnh hơn làm C2 khó hơn.
- Không đòn bẩy nào ở đây có bằng chứng kéo B2 thêm ~+0,07. Kết quả "không đạt" vẫn là kết quả hợp lệ.

## 7. Phụ lục — thắt chặt luật, ghi 02/10/2026 15:43 UTC, TRƯỚC khi có bất kỳ số test nào

Lúc ghi: driver chạy từ 15:34:41 UTC (commit §1–§6 lúc 15:34:17 UTC, tức trước 24 giây — giả định đồng hồ Mac
và server khớp); job đầu (baseline repvit) đang ở fold 0, trong run-dir **chưa có** `test_metrics*.json` nào. Phụ
lục chỉ thêm ràng buộc, không đổi ứng viên hay luật chọn.

1. **Luật hoà (3 ứng viên):** lấy cặp có điểm cao nhất; nếu có cặp đứng trước nó trong bảng §2 mà kém nó dưới
   0,005, chọn cặp **đứng trước sớm nhất** trong số đó. Ngưỡng 0,005 là **quy ước**, mượn từ sàn nhiễu chạy lại
   của AUPRC toàn tập test một fold (`experiments/_reproducibility/README.md`); nó **không** phải nhiễu đo được
   của AUPRC trên ~350–400 hàng PAD của val.
2. **Thứ tự bắt buộc:** tính luật §4 (chỉ từ `val_predictions_auprc.csv` + `val_split.csv` và
   `val_metrics_auprc.json`) và **commit kết quả chọn** trước khi mở bất kỳ `test_metrics*.json`/`predictions*.csv`
   nào của P1/P2 để so sánh, và trước khi chạy eval ngoài miền. Các file test tự sinh khi train xong không được đọc
   trước mốc đó.
3. **Điểm vận hành ảnh điện thoại** của ứng viên được chọn: `phone_sens90` (độ nhạy 90% trên hàng PAD của val, như
   `scripts/make_app_config.py`), cố định từ bây giờ. Báo cáo bắt buộc "hành vi tại ngưỡng val" (acceptance-gates
   §2) gồm ngưỡng này và ngưỡng Youden toàn cục.
4. **Khai cách chọn hai cặp:** tác giả chọn khung "đổi teacher một cặp, đổi student một cặp" trong ba phương án do
   assistant đề xuất. Hai cặp cụ thể do assistant đề xuất, có tham khảo số HAM/Fitzpatrick **splits v1** (§6) và độ
   trễ: maxvit bị loại khỏi vai teacher vì trên v1 student mobilenetv4 học từ maxvit thua chính teacher đó nhiều hơn
   (rủi ro C2) và train chậm nhất; fastvit bị loại vì 113,9 ms > 80 ms. Đây là dùng thông tin HAM/Fitz (dù của v1)
   để chọn ⇒ một phần post-hoc (acceptance-gates §4 #9), phải khai khi báo cáo.
5. **Rủi ro vận hành:** repvit từng OOM khi chung card với 3 job khác (chạy một mình thì rủi ro thấp);
   convnextv2_base chưa từng train trên `vastnew`; code không có resume — nếu một bước hỏng giữa chừng, chạy lại
   phải truyền `FOLDS=` các fold còn thiếu, nếu không sẽ train lại từ fold 0 (ghi đè các fold vừa xong của chính
   bước đó). A1 của repvit (57,2 ms theo kiến trúc) sát mốc 80 ms hơn mobilenetv4 (39,5 ms).

## 8. Phụ lục — đổi định nghĩa C2, ghi 03/10/2026 (commit ~14:20 UTC), TRƯỚC khi mở test của P1/P2

Tác giả đổi tiêu chí 2 ngày 03/10/2026: C2 = student **không kém** teacher quá δ (cận dưới CI ghép cặp ΔAUPRC
> −δ trên từng miền), thay cho "vượt teacher" (`.claude/skills/eval-results/reference/acceptance-gates.md` §1).
Câu "C2 đòi student **vượt** teacher" ở §6 không còn đúng. Với P1/P2 (test chưa mở) đây là thay đổi tiên nghiệm;
với P0 là post-hoc. δ chưa có giá trị: nếu chốt δ trước khi mở test vòng 2 thì C2 của P1/P2 chấm được không
post-hoc; nếu không, C2 của vòng 2 mang cờ CHƯA CÓ TIÊU CHÍ CHỐT. Luật chọn §4 và các endpoint khác không đổi.

## 9. Phụ lục — đổi bộ cổng sang khung 3 trụ, ghi 03/10/2026 (commit ~14:20 UTC), TRƯỚC khi mở test của P1/P2

Tác giả chọn khung 3 trụ (`.claude/skills/eval-results/reference/acceptance-gates.md` §2.1) thay luật gộp cũ ở §5:
I-1 + II-1 + II-2 + II-3 + III-a + III-b + C2. III-a/III-b đo độ nhạy / độ đặc hiệu **tại ngưỡng app đóng băng**
(quy tắc `pad_sens90` trên val của fold ship) trên ảnh PAD và trên Fitzpatrick17k theo từng tông da. B1, B2, B3,
C4a cũ thành báo cáo. Luật chọn §4 không đổi (vẫn chỉ val). S_min, Sp_min, δ của C2 chưa có giá trị: chốt trước khi
mở test vòng 2 thì endpoint của P1/P2 không post-hoc; nếu không, phán quyết vòng 2 mang cờ CHƯA CÓ TIÊU CHÍ CHỐT.
