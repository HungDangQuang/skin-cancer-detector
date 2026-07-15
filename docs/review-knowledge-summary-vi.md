# Tóm tắt kiến thức nền (tiếng Việt) — ôn phản biện

Bản giải thích ngắn gọn từng tầng khái niệm của đề tài, để **đọc nhanh lấy lại kiến thức**.
Dùng kèm checklist chi tiết [review-knowledge-checklist.md](review-knowledge-checklist.md) (có "code ở đâu")
và số liệu thật ở [report_phase_1/](../report_phase_1/).

> **Đề tài một câu:** Phân loại nhị phân ung thư da (benign=0 / malignant=1); một **teacher** lớn
> chưng cất tri thức (Knowledge Distillation) sang các **student** nhỏ chạy được trên điện thoại;
> đánh giá bằng metric chính thức ISIC 2024 **pAUC@TPR≥80** trên tập test độc lập
> (patient-disjoint), dùng 5-fold CV.
>
> **Bộ model hiện tại (SOTA):** teacher `convnextv2_base` / `maxvit_base` / `efficientnetv2_m`
> (mạnh) + `efficientnet_b4` (yếu, làm baseline); student `mobilenetv4_conv_medium` /
> `fastvit_sa12` / `efficientformerv2_s2`. Model deploy khuyến nghị:
> **mobilenetv4_conv_medium ← convnextv2_base**.

---

## Tier 0 — Nền deep learning

- **1 logit thay vì softmax 2 lớp:** model xuất **một** số thực (logit); `sigmoid(logit)` → xác suất
  ác tính; so với ngưỡng → nhãn. Với bài nhị phân, 1 logit tương đương softmax 2 lớp nhưng ít
  tham số hơn và loss ổn định số học hơn.
- **Logit vs xác suất:** train trên logit vì `BCEWithLogitsLoss` gộp sigmoid + BCE bằng log-sum-exp
  nên **ổn định số học** (không tràn số). Chỉ `sigmoid` ở lúc suy luận, không nhét vào trong model.
- **Transfer learning:** khởi tạo backbone từ trọng số ImageNet (`pretrained=True`) thay vì random —
  học đặc trưng ảnh tổng quát sẵn, hội tụ nhanh, cần ít dữ liệu hơn.
- **Chuẩn hoá ImageNet** mean `[0.485,0.456,0.406]` / std `[0.229,0.224,0.225]`: phải trùng thống kê
  lúc pretrain thì backbone mới nhận đúng phân phối đầu vào.

## Tier 1 — Bài toán

- **Bất đối xứng chi phí lâm sàng:** bỏ sót ung thư (false negative) **nguy hiểm hơn nhiều** báo
  động nhầm (false positive). → Ưu tiên **độ nhạy (sensitivity)**, và đó là lý do metric tập trung
  vào vùng độ nhạy cao.
- **Các dataset & vai trò:**
  - **ISIC 2024 SLICE-3D** — dữ liệu train chính, ~400k ảnh, ~128×128, **~0.9% ác tính** (mất cân
    bằng cực đoan).
  - **PAD-UFES-20** — ảnh lâm sàng chụp điện thoại, thêm vào để có thêm mẫu ác tính; map 6 lớp → nhị
    phân.
  - **HAM10000 / Fitzpatrick17k** — **không bao giờ train**, chỉ để đánh giá cross-domain và
    **công bằng theo tông da**.
- **128→224 là nội suy, không phải "độ phân giải cao":** upsample chỉ giãn ảnh, không tạo chi tiết
  mới — phải sẵn sàng bảo vệ điểm này, đừng gọi là "high resolution".

## Tier 2 — Dữ liệu & mất cân bằng

- **Offline vs online:** offline = resize + lọc sạch, lưu đĩa một lần (rẻ, tái lập); online = augment
  mỗi batch (đa dạng hoá).
- **Chống rò rỉ (leakage):** lesion của **cùng một bệnh nhân** không được nằm cả ở train lẫn val.
  Dùng `StratifiedGroupKFold` (group theo `patient_id`, đồng thời phân tầng theo nhãn). Nếu split
  theo ảnh thay vì bệnh nhân → model "nhớ" bệnh nhân → điểm ảo cao.
- **Test độc lập tách TRƯỚC CV:** khoảng 17% bệnh nhân được carve ra (patient-disjoint) trước khi
  chia 5 fold → mọi fold chấm trên **cùng một** test chưa từng train → so sánh cặp công bằng. Thiết
  kế cũ ("test = val của fold 0") làm điểm bị thổi phồng.
- **Chiến lược mất cân bằng = MỘT hệ thống, không phải 3 fix chồng nhau:**
  1. **Undersampling động 1:5** — mỗi epoch bốc lại pool benign qua `set_epoch` (thấy đa dạng benign
     hơn so với undersample tĩnh).
  2. **Focal loss** (Tier 4) — chỉnh ở mức loss.
  3. **Caveat α/ratio** (câu dễ bị hỏi nhất): `α=0.25` được chỉnh cho tỉ lệ gốc ~1000:1; sau khi
     undersample về ~16.7% dương, α có thể **đè quá tay** lớp dương → cần ablate `ratio × α`.
- **Augmentation cố tình KHÔNG dùng** (phải bảo vệ được từng cái): tăng-aug-riêng-cho-ác-tính (lệch
  train/test), crop tròn kính hiển vi (rò rỉ domain), CutOut (có thể xoá mất lesion → nhiễu nhãn),
  MixUp (phá tính nhất quán của soft-target trong KD).

## Tier 3 — Kiến trúc

- **Trade-off teacher–student:** teacher lớn, chính xác nhưng nặng; student nhỏ, deploy được trên
  điện thoại. KD chuyển "sự tinh tế" của teacher sang student.
- **Bộ SOTA (chính hiện nay):** dùng chung một wrapper `TimmBackboneModel` (cần `timm>=1.0`):
  - **MobileNetV4-Conv-Medium** — thuần conv, cân bằng tốc độ/độ chính xác tốt nhất trên phone (22 ms).
  - **FastViT-SA12** — lai CNN+transformer, pAUC cao nhất nhưng bị **phạt nặng trên ARM** (65 ms).
  - **EfficientFormerV2-S2** — AUPRC cao nhất (0.684) nhưng `.pte` lớn nhất (47 MB).
- **Xếp hạng latency ĐẢO trên phần cứng thật:** proxy CPU nói fastvit ≈ mobilenetv4, nhưng trên
  Pixel 6a fastvit chậm ~7.8× mobilenetv3 — transformer trả giá 3.4× trên ARM. → **Latency phải đo
  on-device, không suy từ FLOPs/proxy.**
- **Pitfall `num_features`:** timm báo `num_features` (vd MobileNetV3 = 960) ≠ chiều thật của forward
  (1280). Luôn dùng `infer_backbone_out_dim()` (chạy 1 forward giả) để lấy chiều đầu vào của head.

## Tier 4 — Hàm mất mát

- **Focal Loss** `α·(1−pt)^γ·CE`:
  - **γ (gamma)** — giảm trọng số mẫu **dễ** (pt cao), buộc model tập trung mẫu **khó**. γ càng lớn
    càng "quên" mẫu dễ.
  - **α (alpha)** — trọng số lớp, bù cho mất cân bằng.
  - Vì sao dùng focal thay BCE ở đây: cực mất cân bằng + rất nhiều benign dễ → BCE bị "chìm" bởi
    benign; focal kéo gradient về phía mẫu khó/hiếm.

## Tier 5 — Cơ chế train

- **AdamW** — weight decay tách rời (decoupled), chính quy hoá tốt hơn L2 gộp trong Adam.
- **Differential LR:** backbone pretrained dùng LR nhỏ (`1e-4`), head mới toanh dùng LR lớn (`1e-3`)
  — head chưa học gì nên cần bước lớn, backbone chỉ cần tinh chỉnh nhẹ.
- **Cosine annealing + warmup 3 epoch:** warmup tránh gradient sốc lúc đầu (LR tăng dần từ 0);
  cosine giảm mượt về cuối để hội tụ ổn.
- **Val lệch, test khách quan:** early stopping + chọn checkpoint đều tối ưu **theo val** → val bị
  thiên vị. **Chỉ trích `test_metrics.json` khi kết luận**, không dùng `val_pauc`.

## Tier 6 — Knowledge Distillation (lõi luận văn)

- **Ý tưởng (Hinton 2015):** student nhỏ bắt chước **soft output** của teacher — chứa "dark
  knowledge" (mức tự tin tương đối giữa các lớp) mà nhãn cứng không có.
- **Loss KD nhị phân của đề tài:**
  `L = 0.3·L_focal(student, nhãn thật) + 0.7·T²·BCE(sigmoid(s/T), sigmoid(t/T))`, với **T=4.0**
  (30% học nhãn cứng / 70% học teacher).
- **Nhiệt độ T:** làm "mềm" cả hai phân phối; T càng lớn càng mềm (T→∞ về gần đồng đều; T→1 về
  xác suất gốc). Mềm hơn → lộ nhiều thông tin tương đối hơn để student học.
- **Hệ số T²:** gradient của soft-loss bị co lại theo 1/T²; nhân T² để **độ lớn gradient hard/soft
  cân nhau** (câu hỏi kinh điển của examiner).
- **Teacher đóng băng:** `requires_grad=False` + `eval()` + `torch.no_grad()` — teacher là mục tiêu
  cố định, không được cập nhật.
- **Cặp baseline vs KD:** cùng student, cùng data/seed/hparam, chỉ khác bật/tắt KD (cờ `use_kd`) →
  mới quy được phần cải thiện là **do KD**, không phải may rủi.

### ⭐ Hai phát hiện KD phải thuộc lòng (đây LÀ kết quả luận văn)
1. **KD cải thiện NHẤT QUÁN pAUC@80 và Sensitivity** — Δ pAUC > 0 trên **mọi** cặp student×teacher
   (+0.001→+0.005). Vùng độ nhạy cao (thứ quan trọng cho sàng lọc) luôn tốt lên. Đây là khẳng định
   chắc và an toàn nhất.
2. **Mức tăng AUPRC PHỤ THUỘC chất lượng teacher** — teacher **mạnh** (`convnextv2_base`) nâng AUPRC
   của MobileNetV4 **+0.052** (0.609→0.661); teacher **yếu** (`efficientnet_b4`) → Δ AUPRC trong
   nhiễu hoặc âm. → Chưng cất từ teacher yếu chỉ giúp phần đuôi độ nhạy, không nâng xếp hạng tổng.
   **Case chứng minh mạnh nhất: `mobilenetv4_conv_medium ← convnextv2_base`.**

## Tier 7 — Đánh giá & metric

- **pAUC@TPR≥80 (metric chính thức ISIC 2024):** chỉ tính diện tích dưới ROC ở **vùng độ nhạy cao**
  (TPR ∈ [0.8, 1.0]) — dưới 80% độ nhạy thì máy sàng lọc ung thư **vô dụng lâm sàng** nên không tính.
  - Mẹo cài đặt: lật nhãn/điểm (`v_gt=1−y`, `v_pred=−p`) để "TPR≥0.8" thành "FPR≤0.2", dùng sklearn
    `roc_auc_score(max_fpr=0.2)`, rồi **đảo ngược hiệu chỉnh McClish**. Thang giá trị ≈ [0.02 ngẫu
    nhiên, 0.20 hoàn hảo].
- **AUPRC là headline, KHÔNG phải AUC-ROC:** ở prevalence ~0.4%, AUC-ROC lạc quan giả tạo; AUPRC
  phản ánh đúng độ khó khi lớp dương cực hiếm. Baseline ngẫu nhiên của AUPRC = prevalence.
- **Sensitivity/Specificity/PPV/F1** — sensitivity thống trị vì bỏ sót ung thư là tệ nhất.
- **Ngưỡng Youden** `J = TPR − FPR` (chọn ngưỡng cực đại J): dưới mất cân bằng, ngưỡng tinh chỉnh
  tốt hơn hẳn mặc định 0.5.
- **Grad-CAM:** bản đồ nhiệt cho biết vùng ảnh nào chi phối dự đoán — kiểm tra model có nhìn vào
  lesion không (giải thích được), nhưng chỉ là gợi ý định tính, không phải bằng chứng nhân quả.
- **Cross-domain & fairness:** chấm trên HAM10000 / Fitzpatrick17k (chưa từng train) để đo tổng quát
  hoá và chênh lệch hiệu năng theo tông da (khía cạnh đạo đức).

## Tier 8 — Thiết kế thực nghiệm & tính chặt

- **5-fold CV:** một split đơn dễ may rủi; 5 fold cho **mean ± std** đáng tin. Luôn trích mean±std,
  đừng trích một fold.
- **So sánh cặp (paired):** KD vs baseline trên **cùng fold/seed** → giảm phương sai, quy đúng phần
  cải thiện cho KD.
- **Cảnh báo fold chưa đủ:** vài cặp SOTA chưa đủ 5 fold (maxvit-KD 1 fold; efficientformerv2_s2 2–4
  fold) → phải ghi "n=4 fold, sơ bộ", không chốt như số cuối.

## Tier 9 — Kỹ thuật & hạ tầng (bảo vệ nếu bị hỏi)

- **Hydra** — compose config từ nhóm data/teacher/student/training/augmentation; override ở CLI.
- **Run-dir theo fold** — `experiments/runs/<arch>/fold_{0..4}/...`; `test_metrics.json` tự ghi cuối
  train.
- **Slurm cluster UIT** — luôn submit qua `slurm/submit.sh`; GPU phải xin `--gres=mps:l40:N` (không
  phải `gpu`); **không bao giờ kill/preempt job người khác** — hết tài nguyên thì xếp hàng (PD).
- **Mac ≠ runtime cluster** — không pip/torch trên Mac; kiểm bằng `validate-pipeline` (tĩnh) rồi mới
  chạy cluster.

---

## Câu hỏi phản biện hay gặp (tự test nhanh)

1. Vì sao pAUC@TPR≥80 chứ không phải accuracy hay AUC thường? *(mất cân bằng + sàn độ nhạy lâm sàng)*
2. Làm sao **chứng minh** cải thiện là do KD chứ không phải may? *(cặp baseline cùng seed/fold,
   mean±std, delta)*
3. Rò rỉ dữ liệu có thể lọt ở đâu, chặn thế nào? *(group theo bệnh nhân, dedup, namespace id, test
   tách trước CV)*
4. Vì sao chưng cất thay vì train thẳng model nhỏ? *(soft target/dark knowledge → student tổng quát
   tốt hơn; đưa ra delta)*
5. T=4 và hệ số T² làm gì cụ thể? *(mềm phân phối; cân độ lớn gradient hard/soft)*
6. Vì sao nghi ngờ α=0.25 của focal, sẽ ablate gì? *(α tuned cho 1000:1, sau undersample có thể đè
   lớp dương → ablate ratio×α)*
7. Vì sao trích test thay vì val? *(val bị early-stopping/chọn checkpoint tối ưu → thiên vị)*
8. Hạn chế / điểm yếu của đề tài? *(dedup exact-only, ngưỡng lọc chưa tune, nội suy 128→224, vài
   cặp chưa đủ 5 fold, một teacher/cặp)*

---

*Sinh 2026-07-08 làm tài liệu ôn tập. Nguồn chuẩn vẫn là code + [CLAUDE.md](../CLAUDE.md) +
`report_phase_1/`; nếu file này lệch với chúng thì lấy chúng làm chuẩn và cập nhật lại file này.
Chi tiết "code ở đâu" xem [review-knowledge-checklist.md](review-knowledge-checklist.md).*
