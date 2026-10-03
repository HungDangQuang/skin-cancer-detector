# Tóm tắt dự án để review (03/10/2026)

> Viết để một AI/người review độc lập đánh giá: **hướng đi và tiến trình hiện tại có hợp lý và hiệu quả không**.
> Mọi số lấy từ artifact trong repo; nguồn ghi trong ngoặc. Đây là bản tóm tắt, không phải nơi theo dõi việc
> (việc: `docs/PROGRESS.md`).
>
> **Kiểm chéo:** một lượt (FACTS + PATCH, 03/10/2026) — mọi số CI, benchmark, độ trễ khớp nguồn; 7 lỗi sự thật và các
> chỗ thiếu hạn chế đã sửa. Các đoạn viết **sau** lượt kiểm (chưa ai kiểm lại): định nghĩa nhãn ác tính (§1), câu
> metadata (§1), prevalence (§2), đoạn vòng 2 (§3), định nghĩa cổng A/B/C, phần "Chỉ báo cáo" + bảng hành vi tại ngưỡng
> (§4), giới hạn và dòng KD vs baseline (§5), §6, §7.

## 1. Bối cảnh

**Bài toán.** Phân loại nhị phân tổn thương da (lành = 0 / ác tính = 1) từ một ảnh. Nhãn ác tính theo từng nguồn:
PAD = melanoma, BCC, SCC; DDI dùng nhãn `malignant` gốc, rộng hơn (có cả mycosis fungoides, Kaposi sarcoma, ung thư di
căn…); HAM10000 tính cả `akiec` là ác tính. Model chạy **offline trên điện thoại Android** (app Kotlin, ExecuTorch `.pte`). App chỉ hiện quyết định nhị phân
("có dấu hiệu đáng ngờ — nên đi khám" / "không thấy dấu hiệu"), không hiện % rủi ro.

**Câu hỏi trung tâm** (tác giả, 30/09/2026, sau góp ý của GVHD 21/09):
> *Làm thế nào để tạo ra một mô hình hoạt động tốt trên điện thoại?*

Chưa có mô hình nào được chứng minh "tốt" theo định nghĩa đo được (mục 4) ⇒ dự án **chưa xong**.

Các bước trả lời (khung RQ đề xuất 30/09, **chưa được tác giả duyệt chính thức**):

| RQ | Câu hỏi |
|---|---|
| RQ1 | Mô hình có chạy được trên điện thoại không (độ trễ)? |
| RQ2 | Kết quả trên điện thoại có giống trên máy chủ không, và đã đủ dùng chưa? |
| RQ3 | Knowledge Distillation (KD) bù được bao nhiêu khi nén mô hình? |
| RQ4 | Khi đổi miền ảnh (dermoscopy, ảnh lâm sàng khác nguồn) thì sụt bao nhiêu — do nén hay do dữ liệu? |
| RQ5 | Sửa sụt miền bằng tăng cường ảnh hay bằng dữ liệu thật? |

Lưu ý cho reviewer: bản luận văn hiện có (`thesis/LUAN_VAN.md` §1.6) **vẫn dùng bộ Q1–Q6 cũ lấy KD làm trung tâm**;
GVHD đánh giá bộ đó "xa rời mục tiêu". Luận văn chỉ được sửa khi đã có kết quả ổn (quyết định của tác giả).

**Phạm vi:** một bài toán nhị phân; KD là *giải pháp* để có model nhỏ, không phải đối tượng nghiên cứu chính;
model chỉ nhận ảnh. Đã thử dùng 6 đặc trưng tổn thương `tbp_lv_*` của ISIC (đo từ ảnh 3D-TBP: đối xứng, viền, màu…)
làm thông tin đặc quyền khi train teacher — không có tác dụng đo được (thí nghiệm trên splits v1).

## 2. Dataset

| Dataset | Loại ảnh | Vai trò | Quy mô |
|---|---|---|---|
| **ISIC 2024** (SLICE-3D) | crop từ ảnh chụp toàn thân 3D (3D-TBP) | train / val / **test in-domain** | cùng PAD: 372.242 ảnh, 2.410 bệnh nhân, 1.448 ác tính (0,389%) |
| **PAD-UFES-20** | ảnh chụp bằng **điện thoại** | train / val / test — **miền gần app nhất** | test: **397 ảnh (189 ác tính)** |
| **DDI** (Stanford) | ảnh lâm sàng, tông da cân bằng, ác tính xác nhận bệnh học | **chỉ train** (thêm 25/09) | 656 ảnh, 171 ác tính; không bao giờ được chấm |
| **HAM10000** | dermoscopy | **chỉ đánh giá** — xuyên miền | 7.470 dòng ở biến thể chấm chính (headline) |
| **Fitzpatrick17k** | ảnh lâm sàng, có nhãn tông da | **chỉ đánh giá** — xuyên miền + công bằng theo tông da (sáng/trung bình/tối) | 4.320 dòng ở headline (tối 411 · sáng 2.310 · trung bình 1.599) |

**Chia dữ liệu (splits v2, 22/09/2026):** test độc lập 59.093 ảnh (265 ác tính: 189 PAD + 76 ISIC), tách theo bệnh
nhân **trước** khi chia 5 fold `StratifiedGroupKFold` theo `patient_id`. HAM/Fitz không bao giờ dùng để train hay chọn
ngưỡng (`CLAUDE.md` mục Evaluation).

Những điều reviewer cần biết:
- **Splits cũ (v1) bị rò rỉ bệnh nhân** (phát hiện 22/09): toàn bộ ma trận 140 fold-run cũ có số in-domain bị thổi phồng;
  mọi kết luận hiện hành dùng splits v2, trừ dòng metadata/RKD ở §5 (ghi rõ v1).
- **AUC in-domain gộp bị ảo**: chỉ cần đoán ảnh đến từ ISIC hay PAD đã cho AUC 0,872 (v1). Vì vậy mọi số in-domain phải
  **tách theo nguồn** (ISIC / PAD).
- Prevalence của test in-domain v2 = 265/59.093 ≈ 0,45% (cả population 0,389%) ⇒ AUPRC là thước đo xếp hạng chính,
  không phải AUC.
- Train có **0 ảnh dermoscopy** ⇒ HAM10000 là xuyên miền thật.

## 3. Model

Mọi model: backbone `timm` + đầu `Dropout → Linear(·, 1)`, xuất **một logit**; ảnh 224×224; 5-fold CV, seed 42.

| Vai | Model | Tham số (M) | GFLOPs | Độ trễ Pixel 6a, 4 luồng, sau 5 phút (ms) |
|---|---|---|---|---|
| Teacher | `efficientnetv2_m` | 52,9 | 10,7 | — |
| Teacher | `convnextv2_base` | 87,7 | 30,7 | — |
| Teacher | `maxvit_base` | 118,7 | 47,8 | — |
| Student | `mobilenetv4_conv_medium` | 8,4 | 1,65 | 39,5 |
| Student | `repvit_m1_0` | 6,4 | 2,21 | 57,2 |
| Student | `fastvit_sa12` | 10,6 | 2,96 | 113,9 |
| Student | `efficientformerv2_s2` | 12,1 | 2,49 | 3.908 (phải chạy portable: XNNPACK cho logit sai) |

(`reports/benchmark/*.json`; `reports/ondevice_latency.csv`, cột `sustained_ms`, đo theo kiến trúc.)

**Huấn luyện.** Teacher: Focal loss. Student: KD,
`L = 0,3·Focal(student, nhãn) + 0,7·T²·BCE(σ(s/T), σ(t/T))`, T = 4, teacher đông cứng. Mỗi student có một bản
**baseline** (không KD) cùng cấu hình để đo hiệu quả KD. Sampler giữ tỉ lệ ~1 ác : 5 lành mỗi epoch.

**Công thức hiện hành** (`experiments/runs_newsplit_ddi/`): splits v2 + DDI trong train + tăng cường `light` +
sampler phân tầng theo nguồn ảnh + checkpoint chọn theo val AUPRC.

**Ứng viên hiện tại (P0):** `efficientnetv2_m → mobilenetv4_conv_medium`, fold 4, `best_model_auprc.pth`.

**Đang chạy tại 03/10 — vòng chọn thứ hai** (đăng ký trước, `docs/PREREG_CANDIDATE2_2026-10-02.md`):
P1 = `convnextv2_base → mobilenetv4_conv_medium` (đổi teacher), P2 = `efficientnetv2_m → repvit_m1_0` (đổi student).
Luật chọn: **một** ứng viên, chỉ bằng val (AUPRC trên ảnh PAD của val), commit trước khi mở số test của P1/P2; fold ship =
fold có val AUPRC trung vị (P0 ra fold 4 theo cùng luật). Phải khai: hai cặp P1/P2 được đề xuất **có tham khảo số
HAM/Fitzpatrick của splits v1** và độ trễ ⇒ một phần post-hoc; một lượt chạy thử luật chọn đã cho thấy P0 xếp trên P2
trên val PAD.

## 4. Evaluation

**Metric** (đều không phụ thuộc ngưỡng): AUC-ROC, AUPRC, pAUC@TPR≥80% (metric chính thức ISIC 2024, thang [0; 0,2]),
**độ nhạy tại độ đặc hiệu 80%** (sens@spec80). CI 95% bằng bootstrap **ghép cặp** trên hàng test, không gộp fold.

Ba nhóm cổng: **A** = chạy được trên điện thoại, **B** = đủ mạnh so với mốc bên ngoài (tách theo miền ảnh),
**C** = hiệu quả, chứng minh bằng so sánh ghép cặp.

**Quy tắc "đạt":** chỉ theo **cả khoảng CI 95%** — cổng "≥ mốc" đạt khi **cận dưới** ≥ mốc; điểm ước lượng không bao
giờ quyết định. Hợp đồng duy nhất: `.claude/skills/eval-results/reference/acceptance-gates.md`.

**Tám cổng bắt buộc** — model "đạt yêu cầu" chỉ khi **cả tám** đạt với mốc đã chốt:

| Cổng | Đo gì | Mốc | Trạng thái mốc | P0 hiện tại [CI 95%] | Nhãn |
|---|---|---|---|---|---|
| A1 | độ trễ sau 5 phút trên `.pte` ship | ≤ 80 ms | đề xuất | chưa đo trên `.pte` ship | CHƯA ĐO |
| A3 | điện thoại ↔ máy chủ | max\|Δlogit\| < 1e-3, \|ΔAUPRC\| < 0,005 | đề xuất | 5,2e-06 · 0,0000 | đạt so với mốc đề xuất |
| A4 | parity + không lỗi + tất định trên điện thoại | lỗi < 0,1%, chạy lại trùng bit | đề xuất | 0/70.883 lỗi, trùng bit | đạt so với mốc đề xuất |
| B1 | ISIC: AUC · pAUC | ≥ 0,922 · ≥ 0,142 (Kurtansky 2025, bản chỉ dùng ảnh; đo trên test của cuộc thi, không phải phần ISIC của splits v2) | đề xuất | 0,9437 [0,9227, 0,9616] · 0,1580 [0,1418, 0,1730] | chưa chứng minh |
| **B2** | **ảnh điện thoại (PAD): sens@spec80** | **≥ 0,81** (Cochrane 2018: mức bác sĩ đọc **dermoscopy**, **chỉ melanoma** — nhãn dương của dự án gồm cả BCC/SCC) | **đã chốt (post-hoc)** | **0,8180 [0,7406, 0,8786]** | **chưa chứng minh** |
| B3 | Fitzpatrick17k: sens@spec80 | ≥ 0,47 (Cochrane, nhìn bằng mắt) | đề xuất | 0,4946 [0,4699, 0,5178] | chưa chứng minh |
| C2 | student **vượt** teacher: ΔAUPRC từng miền PAD · Fitz · HAM | cận dưới > 0 | metric đã chốt; còn lại đề xuất | +0,0619 [+0,0396, +0,0852] · +0,0068 [−0,0008, +0,0146] · +0,0059 [−0,0068, +0,0189] | chưa chứng minh |
| C4a | **từng** tông da: sens@spec80 | ≥ 0,47 mỗi nhóm | chờ quyết | tối 0,5000 [0,4248, 0,5837] · sáng 0,5207 [0,4886, 0,5554] · trung bình 0,4473 [0,4077, 0,4861] | chưa chứng minh |

**Chỉ báo cáo** (không quyết định chọn):
- **B4** HAM10000 sens@spec80, mốc 0,81 → 0,7259 [0,7018, 0,7508], cả khoảng dưới mốc. B4 vốn là cổng bắt buộc và đã
  làm phán quyết thành `KHÔNG ĐẠT YÊU CẦU`; tác giả chuyển B4 sang chỉ báo cáo ngày 02/10 (lý do: app nhận ảnh camera,
  không phải dermoscopy) **sau khi đã thấy kết quả này**, và việc đó đổi phán quyết thành `CHƯA CÓ TIÊU CHÍ CHỐT`.
- **C1** KD − baseline, ΔAUPRC: PAD −0,0008 [−0,0199, +0,0187] (không phân định) · Fitz +0,0395 [+0,0310, +0,0478].
- **C4b** chênh AUC giữa các tông da: sáng − trung bình +0,0409 [+0,0119, +0,0708], khác 0 có ý nghĩa — chênh này có
  ở cả 6 arm splits v2, kể cả teacher; tối − sáng và tối − trung bình không phân định (nhóm tối n = 411).
- **C3** tỉ lệ nén, **A2** bộ nhớ (208–257 MiB, đo theo kiến trúc).

**Hành vi app tại ngưỡng** (bắt buộc báo cáo; ngưỡng chọn trên val, đo trên test, fold 4):

| Ngưỡng | PAD (điện thoại) | Fitzpatrick17k | ISIC | HAM10000 |
|---|---|---|---|---|
| Ngưỡng app `pad_sens90` = 0,5705 (độ nhạy 90% trên ảnh PAD của val; số của một fold, không có CI) | nhạy 0,873 · đặc hiệu 0,731 | nhạy 0,567 · đặc hiệu 0,769 | nhạy 0,066 | — |
| Youden J trên toàn bộ val = 0,2272 | bắt 189/189 ác, **gắn cờ 207/208 ảnh lành** | đặc hiệu 0,0014 | bắt 57/76 ác | đặc hiệu 0,0927 |

Ngưỡng app là **post-hoc**: mục tiêu 90% được chọn sau khi đã xem 3 điểm vận hành trên test PAD của fold 4. Ngưỡng toàn
cục bị ảnh ISIC áp đảo nên vô dụng cho ảnh điện thoại. Nguồn: `reports/2026-10-02_threshold_options/README.md`,
`reports/2026-10-02_acceptance_verdict_srcsamp.md`.

**Mọi mốc số của cổng A/B/C đều được ghi nhận post-hoc** (01/10, sau khi đã thấy mọi kết quả B/C của P0); B2, B4 và
metric của C2 được chốt ở lượt đó.

**Phán quyết hiện hành của P0: `CHƯA CÓ TIÊU CHÍ CHỐT`** (còn mốc đề xuất). Nếu coi mọi mốc đề xuất như đã chốt:
`CHƯA KẾT LUẬN ĐƯỢC`. Không kịch bản nào cho `ĐẠT YÊU CẦU`. Nguồn: `reports/2026-10-02_acceptance_verdict_srcsamp.md`.

**Khoảng cách lớn nhất: B2.** Test PAD chỉ có 189 ca ác tính nên CI rộng; với P0, cận dưới thấp hơn điểm ước lượng ~0,077,
nên điểm ước lượng phải khoảng ≥ 0,89 thì cận dưới mới chạm 0,81 (ước tính thô). Đăng ký trước của vòng 2 tự ghi: không
đòn bẩy nào **ở vòng này** (đổi teacher, đổi student) có bằng chứng kéo B2 thêm ~+0,07.

## 5. Kết quả đã có (để reviewer đánh giá hiệu quả các bước đã làm)

| Thí nghiệm | Kết quả (CI ghép cặp) | Nguồn |
|---|---|---|
| Thêm DDI vào train (vs không) | student KD: ΔAUPRC dương có ý nghĩa 6/6 tập đánh giá và 12/12 ô (3 tông da × 4 biến thể cắt ảnh của Fitzpatrick); teacher/baseline lẫn lộn. **Giới hạn:** chỉ thử một cặp `efficientnetv2_m → mobilenetv4` (teacher này yếu nhất trên Fitzpatrick ở splits v1); không tách được cơ chế (DDI thêm cả tông da tối lẫn +17–19% ca dương); trên riêng ảnh PAD, ΔAUPRC +0,0254 [−0,0010, +0,0495] không phân định | `reports/2026-10-03_ddi_arm.md` |
| Tăng cường ảnh nhắm miền (`augmentation=domain`) | student KD **xấu đi** có ý nghĩa 5/5 ô ngoài miền ⇒ đã gỡ khỏi code | `docs/domain_aug_plan.md` |
| Sampler phân tầng theo nguồn | endpoint đăng ký trước đạt: PAD ΔAUPRC +0,0563 [+0,0391, +0,0748] (đo trên checkpoint chọn theo val pAUC ở cả hai phía) | `reports/2026-10-01_srcsamp_item2_3.md` |
| KD vs baseline (cùng student, công thức hiện hành) | PAD ΔAUPRC −0,0008 [−0,0199, +0,0187] không phân định; Fitz +0,0395 [+0,0310, +0,0478] | `reports/2026-10-02_c1_pad_cell_srcsamp.md` |
| (splits v1) Metadata làm thông tin đặc quyền + RKD (Relational KD — chưng cất quan hệ khoảng cách/góc giữa các mẫu) | metadata không tác dụng (0/8 phép kiểm); RKD làm hại student nhỏ | `CLAUDE.md` mục Direction A |
| Điện thoại vs máy chủ (Pixel 6a, ứng viên P0) | mọi metric trùng host/server (Δ = 0 tới 4 chữ số), max\|Δlogit\| 5,2e-06 trên 70.883 ảnh | `reports/2026-10-01_pixel6a_srcsamp_vs_mobile.md` |

CI bootstrap chỉ đo sai số lấy mẫu của tập test, **không** gồm độ ngẫu nhiên khi train: chạy lại cùng seed đã lệch ~0,005
AUPRC/fold, nên các Δ có cận sát 0 vẫn có thể là nhiễu.

**Chưa đo / còn hở:** A1 trên `.pte` ship; ảnh camera thật qua app (bước đổi kích thước ảnh, "L3"); test in-domain,
HAM và Fitz đã được nhìn qua ứng viên thứ nhất nên vòng 2 mang thành phần post-hoc, và chưa có tập xác nhận mới; mọi mốc
số được ghi nhận sau khi đã thấy kết quả.

## 6. Chưa kiểm được độc lập

- Hai mốc ngoài (Kurtansky 2025 cho B1, Cochrane 2018 cho B2/B3) do assistant đối chiếu qua Europe PMC ngày 01/10;
  các lượt kiểm chéo không có web nên chưa kiểm lại được.
- Số chỉ có trên máy chủ train (656 dòng DDI mỗi fold, các run của vòng 2) không kiểm được từ máy tác giả.
- Khung RQ1–RQ5 là đề xuất, chưa được tác giả duyệt chính thức.

## 7. Câu hỏi gợi ý cho reviewer

1. Bộ cổng A/B/C và các mốc số có phù hợp với một app sàng lọc trên điện thoại không? Lưu ý: mọi mốc đã được ghi
   nhận sau khi thấy kết quả, nên đổi mốc lúc này cũng là post-hoc.
2. Quy trình có đủ chặt không: mốc chốt sau khi xem kết quả, tập kiểm dùng lại qua nhiều vòng, chưa có tập xác nhận
   mới. Cần gì để một kết luận "đạt" (hoặc "chưa đạt") đứng được?
3. Với test PAD chỉ 189 ca ác tính, cổng B2 theo cận dưới CI đòi hỏi gì? Có những cách nào hợp lệ để có kết luận rõ hơn?
4. Với bằng chứng hiện có (mục 5), bước tiếp theo nào có khả năng thu hẹp khoảng cách B2 / C4a nhất — và vòng chọn thứ
   hai (đổi teacher / đổi student) có phải lựa chọn hợp lý không?
5. Khung RQ1–RQ5 có trả lời được câu trung tâm "làm thế nào để có model tốt trên điện thoại" không?
