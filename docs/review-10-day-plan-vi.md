# Lộ trình ôn 10 ngày — Nắm trọn dự án (song ngữ)

> **Cách dùng:** Đây là giáo trình tự học, biến [review-knowledge-checklist.md](review-knowledge-checklist.md)
> (danh sách phẳng, tiếng Anh) thành **10 ngày** có mục tiêu, giải thích dễ hiểu cho người
> **chưa vững ML/CV**, và câu tự kiểm tra kiểu giám khảo. Mỗi ngày: đọc phần "Kiến thức
> cần học" → mở file "Code ở đâu" xem thật → tự trả lời "Tự kiểm tra" **không nhìn tài liệu**.
> Muốn hỏi tương tác, gọi subagent **`knowledge-tutor`** (xem cuối file).
>
> **Nguồn chân lý = code + checklist + `report_phase_1/`. Nếu tài liệu này lệch với chúng,
> chúng đúng** — báo để cập nhật.

> **Đề tài một câu:** Phân loại nhị phân ung thư da (benign=0 / malignant=1); một **teacher**
> lớn "chưng cất tri thức" (**Knowledge Distillation, KD**) sang các **student** nhỏ chạy được
> trên điện thoại; đánh giá bằng metric chính thức ISIC 2024 **pAUC@TPR≥80** trên tập test độc
> lập (patient-disjoint), dùng **5-fold cross-validation**.

## Bảng lộ trình tổng

| Ngày | Chủ đề (Tier) | Độ khó | Bạn sẽ trả lời được |
|---|---|---|---|
| 1 | Tier 0 — Nền deep learning | Dễ | Vì sao 1 logit, sigmoid làm gì, transfer learning là gì |
| 2 | Tier 1 — Bài toán & dataset | Dễ | Vì sao ưu tiên độ nhạy, mỗi dataset dùng để làm gì |
| 3 | Tier 2 — Data pipeline & mất cân bằng | **Nặng** | Chống rò rỉ dữ liệu, xử lý mất cân bằng 3 tầng |
| 4 | Tier 3 — Kiến trúc model | Vừa | Teacher↔student, một wrapper cho mọi model |
| 5 | Tier 4+5 — Loss & cơ chế train | Vừa | Focal loss, LR phân tầng, vì sao quote test không quote val |
| 6 | Tier 6 — Knowledge Distillation (lõi) | **Nặng** | Loss KD, T², teacher đóng băng, 2 phát hiện chính |
| 7 | Tier 6b — Metadata & LUPI | Vừa | Vì sao metadata không phải input deploy, privileged teacher |
| 8 | Tier 7 — Đánh giá & metric | **Nặng** | AUPRC vs AUC-ROC, pAUC@TPR≥80, calibration≠ranking |
| 9 | Tier 8+9 — Thí nghiệm & hạ tầng | Vừa | 5-fold, mean±std, Hydra, tầng `run/` |
| 10 | Câu hỏi bảo vệ + tổng ôn | — | Nối tất cả thành một mạch kể chuyện luận văn |

---

## Ngày 1 — Nền deep learning (Tier 0)

*Hôm nay bạn sẽ trả lời được: model xuất ra cái gì, biến nó thành xác suất và nhãn ra sao,
và vì sao ta khởi tạo từ trọng số ImageNet thay vì con số ngẫu nhiên.*

**🎯 Mục tiêu ngày.** Nắm các "phản xạ" nền tảng: **logit → sigmoid → xác suất → ngưỡng → nhãn**,
hàm loss cơ bản, transfer learning, và khái niệm overfitting. Đây là nền cho mọi tầng sau.

**📚 Kiến thức cần học.**

- **Binary classification with a single logit (phân loại nhị phân bằng 1 logit).** Model xuất
  ra **một** số thực gọi là *logit* (chưa phải xác suất, có thể âm/dương). `sigmoid(logit)` ép
  về [0,1] = xác suất ác tính; so với **ngưỡng** → nhãn 0/1. *Ví von:* logit là "điểm số thô",
  sigmoid là "quy về thang phần trăm". Với bài 2 lớp, 1 logit đủ (tương đương softmax 2 lớp
  nhưng ít tham số hơn). 📁 [src/models/heads.py](../src/models/heads.py) — `build_head` =
  `Dropout → Linear(in, 1)`.
- **Logits vs probabilities (logit vs xác suất).** Ta huấn luyện trên **logit** vì
  `BCEWithLogitsLoss` gộp sigmoid + cross-entropy bằng thủ thuật log-sum-exp nên **ổn định số
  học** (không tràn số khi logit rất lớn/nhỏ). Chỉ áp `sigmoid` lúc **suy luận (inference)**,
  không nhét vào trong model.
- **Cross-entropy / BCE loss.** Công thức `-[y·log p + (1-y)·log(1-p)]`: phạt nặng khi model
  tự tin nhưng sai. *Ví von:* bạn cá cược 99% mà thua thì mất điểm rất nặng.
- **Gradient descent, backprop, epoch vs batch vs iteration.** *epoch* = duyệt hết dữ liệu 1
  lượt; *batch* = một nhúm ảnh xử lý cùng lúc; *iteration* = 1 lần cập nhật trọng số (1 batch).
  📁 [src/training/trainer.py](../src/training/trainer.py).
- **Overfitting / underfitting; vai trò train-val-test.** Overfit = học thuộc lòng dữ liệu
  train, kém trên dữ liệu mới. **Test là con số trung thực** vì model chưa từng thấy nó.
- **CNN basics.** Convolution (bộ lọc trượt tìm đặc trưng), pooling (thu nhỏ), feature map,
  receptive field (vùng ảnh mà 1 neuron "nhìn thấy").
- **Transfer learning & ImageNet pretraining.** Khởi tạo backbone từ trọng số đã học trên
  ImageNet (`pretrained=True`) thay vì ngẫu nhiên → đã biết "cạnh, góc, kết cấu" tổng quát →
  hội tụ nhanh, cần ít dữ liệu hơn. 📁 mọi model gọi `timm.create_model(..., pretrained=True)`.
- **Normalization ImageNet mean/std** `[0.485,0.456,0.406]`/`[0.229,0.224,0.225]`. Phải trùng
  thống kê lúc pretrain thì backbone mới "nhận đúng" phân phối đầu vào. 📁
  [src/data/transforms.py](../src/data/transforms.py).

**❓ Tự kiểm tra.**
1. Vì sao xuất **1** logit thay vì softmax 2 lớp? *(Gợi ý: tương đương nhưng ít tham số, loss ổn định hơn.)*
2. Vì sao không đặt `sigmoid` bên trong model mà chỉ áp lúc inference? *(Ổn định số học của BCEWithLogitsLoss.)*
3. Ba con số epoch/batch/iteration khác nhau thế nào?
4. Vì sao con số trên tập **test** đáng tin hơn train/val?
5. Vì sao dùng đúng mean/std của ImageNet, không tự chọn số khác?

**⏱️ ~2–3 giờ · Dễ.** Nếu đã học ML cơ bản, lướt nhanh và tập trung câu 1–2.

---

## Ngày 2 — Bài toán & dataset (Tier 1)

*Hôm nay bạn sẽ trả lời được: vì sao "bỏ sót ung thư" định hình toàn bộ lựa chọn metric, và
mỗi bộ dữ liệu đóng vai gì.*

**🎯 Mục tiêu ngày.** Hiểu bối cảnh lâm sàng (vì sao **độ nhạy/sensitivity** quan trọng hơn
độ chính xác thô) và bản đồ 4 dataset: cái nào để train, cái nào chỉ để đánh giá.

**📚 Kiến thức cần học.**

- **Bất đối xứng chi phí lâm sàng (clinical cost asymmetry).** Bỏ sót một ca ung thư
  (**false negative**) nguy hiểm hơn nhiều một báo động nhầm (**false positive** — chỉ tốn công
  sinh thiết). → Đây là lý do ta dùng metric **tập trung vùng độ nhạy cao**, không phải accuracy.
- **Các dataset & vai trò:**
  - **ISIC 2024 SLICE-3D** — dữ liệu train chính; ~400k ảnh, gốc ~128×128, **~0.9% ác tính**
    (mất cân bằng cực đoan). 📁 `process_isic2024` trong
    [src/data/preprocessing.py](../src/data/preprocessing.py).
  - **PAD-UFES-20** — ảnh lâm sàng chụp **điện thoại**, thêm vào để có thêm mẫu ác tính; map
    6 lớp → nhị phân (BCC/SCC/MEL→1, ACK/NEV/SEK→0). 📁 `process_pad_ufes_20`.
  - **Prevalence test đo được ~0.39%** (ISIC + PAD, tập test held-out) — dùng **con số này**,
    không phải 0.9% của riêng ISIC, làm mốc ngẫu nhiên cho AUPRC (xem Ngày 8).
  - **HAM10000 / Fitzpatrick17k** — **không bao giờ train**; để đánh giá **cross-domain** và
    **công bằng theo tông da (fairness)**. 📁 configs trong [configs/data/](../configs/data/).
- **Domain shift (dịch chuyển miền).** Ảnh train khác ảnh lúc deploy (điện thoại). Vì thế
  augmentation kiểu "viền kính hiển vi" bị **bỏ** — nó sẽ rò đặc trưng giống HAM. *Doc:*
  [PREPROCESSING.md](PREPROCESSING.md) §4.
- **"128→224 là nội suy, không phải chi tiết mới".** Upsample chỉ giãn ảnh, **không** tạo
  thông tin mới → đừng gọi là "độ phân giải cao". *Doc:* PREPROCESSING.md §1.

**❓ Tự kiểm tra.**
1. Vì sao ta ưu tiên **sensitivity** thay vì accuracy trong sàng lọc ung thư?
2. PAD-UFES-20 được thêm vào để làm gì, và vì sao là ảnh điện thoại lại có ích?
3. Vì sao HAM10000 tuyệt đối không được đưa vào train?
4. Nên quote prevalence 0.39% hay 0.9%, và cho việc gì?
5. Vì sao không được gọi ảnh 224 là "high resolution"?

**⏱️ ~2 giờ · Dễ.**

---

## Ngày 3 — Data pipeline & mất cân bằng (Tier 2) — **NGÀY NẶNG**

*Hôm nay bạn sẽ trả lời được: dữ liệu rò rỉ (leakage) có thể chui vào ở đâu, và vì sao "xử lý
mất cân bằng" ở đây là MỘT hệ thống chỉnh được chứ không phải 3 bản vá chồng lên nhau.*

**🎯 Mục tiêu ngày.** Đây là ngày quan trọng nhất về dữ liệu. Nắm: offline vs online, lọc chất
lượng + khử trùng lặp, **chống rò rỉ theo bệnh nhân**, tách test độc lập, và bộ ba chống mất
cân bằng (undersampling + focal + α).

**📚 Kiến thức cần học.**

- **Offline vs online preprocessing.** *Offline* = resize + lọc sạch, lưu đĩa **một lần** (rẻ,
  tái lập được). *Online* = augment **mỗi batch** (đa dạng hoá). 📁
  [src/data/preprocessing.py](../src/data/preprocessing.py) (offline) +
  [src/data/transforms.py](../src/data/transforms.py) (online).
- **Quality filtering (mỗi bước phải biện minh được).** Bỏ ảnh giải mã lỗi; `is_uninformative`
  (grayscale std<8 hoặc >97% gần đen/trắng); bỏ `min_size<32`; **khử trùng lặp bằng md5 của
  pixel sau resize**. *Quy tắc an toàn:* không tự động bỏ một mẫu **ác tính** mà không có người
  xem (lớp hiếm). 📁 `preprocessing.py`.
- **Label unification.** Gộp nhãn của các dataset về **nhị phân** chung.
- **Leakage & patient grouping (rò rỉ & gom theo bệnh nhân).** Các nốt của **cùng một bệnh
  nhân** không được nằm cả train lẫn val — nếu không, model "nhận mặt bệnh nhân" thay vì học
  bệnh. 📁 `generate_group_kfold_splits` dùng `StratifiedGroupKFold(groups=patient_id)`.
- **StratifiedGroupKFold** = vừa **stratify** (giữ tỉ lệ benign:malignant mỗi fold) vừa **group**
  (mỗi bệnh nhân chỉ ở một phía) cùng lúc.
- **Patient-id namespacing** (`pad_...`) để id của 2 dataset không đụng nhau gây rò rỉ. *Gotcha:*
  CLAUDE.md "patient_id must be namespaced".
- **Tập test độc lập held-out.** Cắt **patient-disjoint TRƯỚC** khi chia 5-fold
  (`test_holdout_splits=6`, ~17%); mọi fold chấm trên **cùng** tập test chưa từng train →
  so sánh theo cặp được. *Vì sao:* thiết kế cũ "test = val của fold 0" làm phồng metric.
  *Doc:* PREPROCESSING.md §2.
- **Xử lý mất cân bằng như MỘT hệ thống chỉnh được** (không phải 3 fix rời):
  - **Dynamic undersampling 1:5** — mỗi epoch **bốc lại** pool benign qua `set_epoch` → thấy
    được nhiều benign đa dạng hơn so với undersample tĩnh. 📁
    [src/data/sampler.py](../src/data/sampler.py).
  - **Focal loss** — chỉnh ở tầng loss (chi tiết Ngày 5).
  - **Cảnh báo α/ratio:** α=0.25 vốn tinh chỉnh cho tỉ lệ thô ~1000:1; sau khi undersample về
    ~16.7% dương, nó có thể **đè** lớp dương quá tay → cần **ablate `ratio × α`**. *Doc:*
    PREPROCESSING.md §3. **Đây là câu "bạn có nghĩ tới không" hay bị hỏi nhất.**
- **Augmentation (Albumentations), chỉ train, đối xứng theo lớp.** Flip, xoay 0–360°,
  ShiftScaleRotate, ColorJitter, CLAHE xác suất thấp, GaussianBlur, rồi Normalize+ToTensorV2.
  **Thứ tự:** CLAHE/thao tác uint8 phải **trước** Normalize. 📁 `transforms.py`.
- **Augmentation cố ý KHÔNG dùng** (biện minh từng cái): aug mạnh riêng cho malignant (lệch
  train/test), crop tròn kính hiển vi (rò miền), CutOut (xoá mất nốt → nhiễu nhãn), MixUp (phá
  tính nhất quán của soft-target KD). *Doc:* PREPROCESSING.md §4.
- **DataModule / Dataset / DataLoader — phân vai.** 📁
  [src/data/datamodule.py](../src/data/datamodule.py); sampler cho train, `shuffle=False` cho val/test.

**❓ Tự kiểm tra.**
1. Nếu chia dữ liệu **theo ảnh** thay vì theo **bệnh nhân** thì hỏng chỗ nào?
2. Vì sao **khử trùng lặp TRƯỚC khi chia** mới đúng?
3. Tập test được cắt ra ở thời điểm nào và vì sao phải trước 5-fold?
4. Vì sao bốc lại pool benign **mỗi epoch** tốt hơn undersample tĩnh?
5. α=0.25 có thể sai ở đâu sau khi undersample, và bạn sẽ ablate cái gì?
6. Vì sao CLAHE phải chạy trước Normalize?

**⏱️ ~4 giờ · NẶNG.** Chia làm 2 buổi nếu cần: sáng leakage/splits, chiều imbalance/aug.

---

## Ngày 4 — Kiến trúc model (Tier 3)

*Hôm nay bạn sẽ trả lời được: vì sao một teacher lớn dạy được student nhỏ, và vì sao cả 7 model
dùng chung MỘT lớp wrapper.*

**🎯 Mục tiêu ngày.** Nắm trade-off teacher↔student, mẫu "backbone + head", registry, và các
model cụ thể (4 student SOTA, teacher set, PanDerm).

**📚 Kiến thức cần học.**

- **Teacher vs student capacity trade-off.** Teacher lớn, chính xác (`efficientnetv2_m` /
  `convnextv2_base`) dạy student nhỏ, deploy được (mobile). Nắm sơ số tham số & động cơ hiệu quả.
- **Một wrapper chung, không code riêng từng arch.** Mọi model timm chạy qua
  `TimmBackboneModel` 📁 [src/models/timm_backbone.py](../src/models/timm_backbone.py); các wrapper
  họ cũ (`efficientnet.py`...) đã bị **xoá**. Wrapper làm gì: backbone + `build_head` +
  `forward → (B,)` một logit.
- **Bộ student SOTA (đều qua `TimmBackboneModel`):**
  - **MobileNetV4-Conv-Medium** — thuần conv, cân bằng độ trễ/độ chính xác tốt nhất trên mobile
    (22 ms Pixel 6a). **Lựa chọn deploy.** 📁
    [configs/student/mobilenetv4_conv_medium.yaml](../configs/student/mobilenetv4_conv_medium.yaml).
  - **FastViT-SA12** — lai CNN+transformer, pAUC cao nhất nhưng chậm trên ARM (65 ms). 📁
    [configs/student/fastvit_sa12.yaml](../configs/student/fastvit_sa12.yaml).
  - **EfficientFormerV2-S2** — AUPRC cao nhất (0.684) nhưng `.pte` lớn nhất (47 MB). 📁
    [configs/student/efficientformerv2_s2.yaml](../configs/student/efficientformerv2_s2.yaml).
  - **RepViT-M1.0** — "reparameterizable": train dạng nhiều nhánh, **hợp nhất về conv phẳng lúc
    inference** → mobile-friendly. 📁
    [configs/student/repvit_m1_0.yaml](../configs/student/repvit_m1_0.yaml).
  - *Vì sao xếp hạng độ trễ **đảo** trên phần cứng thật:* proxy CPU nói fastvit ≈ mobilenetv4,
    nhưng on-device fastvit chậm ~7.8× (transformer trả "thuế ARM" ~3.4×). *Doc:*
    report_phase_1/benchmark, [MOBILE.md](MOBILE.md).
- **Bộ teacher SOTA** — `efficientnetv2_m` (chính), `convnextv2_base` (ConvNeXt V2, FCMAE-pretrain),
  `maxvit_base` (đã **rút khỏi run-plan** nhưng vẫn đăng ký). Teacher mạnh hơn → xem Ngày 6 (chất
  lượng teacher quyết định mức tăng AUPRC của KD).
- **PanDerm foundation teacher** (`panderm`) — model **nền theo miền da** (ViT-B/16, pretrain
  ~2.1M ảnh da, Nature Medicine 2025). Trọng số ship **ngoài timm** (BEiT-style, Google Drive,
  CC-BY-NC-4.0) → `PanDermModel` 📁 [src/models/panderm.py](../src/models/panderm.py) dựng ViT-B/16
  tương thích rồi nạp trọng số với **loader "ồn ào" báo lỗi nếu quá ít tensor khớp** (arch sai
  thì fail to, không âm thầm train net gần-ngẫu-nhiên). *Doc:*
  [SOTA_MODEL_DECISION_2026-07.md](SOTA_MODEL_DECISION_2026-07.md) §5.
- **timm; `num_classes=0`** → trả về **feature**, không có head phân loại.
- **Backbone + head & registry.** `BaseModel` (ABC), `forward → (B,)` một logit,
  `freeze_backbone()`/`unfreeze()`. 📁 [src/models/base_model.py](../src/models/base_model.py),
  [src/models/registry.py](../src/models/registry.py). Thêm arch mới = đăng ký vào registry +
  thêm 1 config.
- **`forward_features(x) → (feat, logit)`** — cửa thứ 2 mọi model có, chỉ dùng khi bật RKD
  feature-KD (Ngày 6). Đường logit **giữ nguyên** dù có đọc feature hay không.
- **Bẫy `num_features`.** `infer_backbone_out_dim()` chạy một forward giả để lấy đúng chiều
  head input, vì `num_features` của timm **không đáng tin**. 📁 [src/models/heads.py](../src/models/heads.py).

**❓ Tự kiểm tra.**
1. Một "wrapper" thực chất làm gì, và vì sao một lớp là đủ cho cả 7 model?
2. RepViT "reparameterization" mang lại lợi gì lúc deploy?
3. Vì sao xếp hạng độ trễ CPU có thể **đảo** trên điện thoại?
4. `num_classes=0` trong timm làm gì?
5. Vì sao loader của PanDerm phải "báo lỗi to" khi ít tensor khớp?
6. Vì sao không tin `num_features` mà phải chạy forward giả?

**⏱️ ~3 giờ · Vừa.**

---

## Ngày 5 — Loss & cơ chế huấn luyện (Tier 4 + Tier 5)

*Hôm nay bạn sẽ trả lời được: focal loss "hạ trọng số" ví dụ dễ ra sao, và vì sao con số dùng
để phán xét phải là test chứ không phải val.*

**🎯 Mục tiêu ngày.** Gộp 2 tầng liên quan chặt: hàm loss (BCE → focal) và cơ chế train (optimizer,
scheduler, early stopping, checkpoint).

**📚 Kiến thức cần học — Loss (Tier 4).**

- **BCEWithLogitsLoss** — loss nền.
- **Binary Focal Loss** `α·(1-pt)^γ·CE`. **γ (gamma)** = tập trung vào ví dụ **khó** (down-weight
  ví dụ dễ); **α (alpha)** = trọng số theo tỉ lệ lớp. 📁
  [src/training/losses.py](../src/training/losses.py). *Ref:* Lin et al. 2017. *Ví von:* ví dụ dễ
  (benign rõ ràng) bị nhân với số rất nhỏ nên gần như "biến mất" khỏi loss, model dồn sức vào ca khó.
- **Vì sao focal thay vì BCE thuần ở đây:** mất cân bằng cực đoan + rất nhiều benign dễ.
- **Tương tác với undersampling** — nối lại cảnh báo α/ratio ở Ngày 3.

**📚 Kiến thức cần học — Training mechanics (Tier 5).**

- **AdamW & weight decay** (decoupled, khác L2 thường). 📁
  [src/training/optimizers.py](../src/training/optimizers.py).
- **Differential/discriminative learning rates** — LR **thấp** cho backbone đã pretrain
  (`lr_backbone=1e-4`), LR **cao** cho head mới (`lr_head=1e-3`). *Vì sao:* head khởi tạo ngẫu
  nhiên nên cần học nhanh; backbone đã tốt, chỉ tinh chỉnh nhẹ.
- **Cosine annealing + linear warmup** (`SequentialLR`, `warmup_epochs=3`). 📁
  [src/training/schedulers.py](../src/training/schedulers.py). Warmup ngăn "sốc" gradient lúc đầu.
- **Gradient clipping** (`clip_grad_norm_`, `grad_clip=1.0`) — chặn gradient nổ.
- **Early stopping** (patience trên `val_loss`). 📁
  [src/training/callbacks.py](../src/training/callbacks.py).
- **Checkpoint theo `val_pauc` tốt nhất** (`mode=max`) trong khi early-stopping theo dõi
  `val_loss` — **hai tín hiệu khác nhau**, biết vì sao.
- **Reproducibility / seeding.** 📁 [src/utils/seed.py](../src/utils/seed.py), `seed=42` khắp nơi.
- **Val có thiên lệch vs test không thiên lệch.** Val bị "tối ưu vào" (early stop + chọn
  checkpoint) → **phán xét bằng `test_metrics.json`, không phải `val_pauc`.** Đây là phân biệt
  **sống còn khi bảo vệ**. *Doc:* CLAUDE.md.

**❓ Tự kiểm tra.**
1. Suy ra vì sao thừa số `(1-pt)^γ` làm ví dụ **dễ** đóng góp ít vào loss.
2. `pt = p nếu y=1, 1-p nếu y=0` — vì sao định nghĩa vậy?
3. Vì sao head cần LR lớn hơn backbone?
4. Warmup ngăn điều gì ở những epoch đầu?
5. Checkpoint và early-stopping theo dõi **2 tín hiệu khác nhau** nào, vì sao?
6. Vì sao khi kết luận phải trích test chứ không phải val?

**⏱️ ~3 giờ · Vừa.**

---

## Ngày 6 — Knowledge Distillation (Tier 6) — **NGÀY NẶNG, LÕI LUẬN VĂN**

*Hôm nay bạn sẽ trả lời được: "dark knowledge" là gì, T² để làm gì, và 2 phát hiện chính của
luận văn — thuộc nằm lòng.*

**🎯 Mục tiêu ngày.** Đây là trái tim đề tài. Nắm loss KD nhị phân, vai trò T và T², teacher
đóng băng, cặp baseline↔KD, 2 biến thể, và **2 kết quả headline**.

**📚 Kiến thức cần học.**

- **Khái niệm KD (Hinton et al. 2015).** Student nhỏ **bắt chước output mềm** của teacher lớn —
  soft output mang "**dark knowledge**" (mức tự tin tương đối giữa các lớp) vượt xa nhãn cứng
  0/1. *Ví von:* nhãn cứng nói "đây là ác tính"; teacher mềm nói "80% ác, nhưng khá giống một
  loại lành tính X" — thông tin phụ đó giúp student học tốt hơn.
- **Loss KD nhị phân dùng ở đây:**
  `L = α·L_focal(student, true) + (1−α)·T²·BCE(sigmoid(s/T), sigmoid(t/T))`, với **T=4.0, α=0.3**
  (30% nhãn cứng / 70% mềm). 📁 [src/training/distillation.py](../src/training/distillation.py).
- **Temperature T (nhiệt độ).** Làm "mềm" cả hai phân phối; T cao → mềm hơn. T→1: về gần
  sigmoid thường; T→∞: gần như phẳng (mọi thứ ~0.5).
- **Thừa số T².** Gradient của số hạng mềm bị chia cho T² (vì `s/T`), nên nhân lại **T²** để độ
  lớn gradient cứng/mềm **cân nhau**. *Đây là câu hỏi kinh điển khi bảo vệ.*
- **Teacher đóng băng (frozen).** `requires_grad=False`, `eval()`, `torch.no_grad()` cho forward
  của teacher. 📁 [src/training/kd_trainer.py](../src/training/kd_trainer.py). *Vì sao:* teacher
  là "mục tiêu cố định"; nếu nó cũng học thì student đuổi theo một mục tiêu di chuyển.
- **Cặp baseline vs KD.** Cùng student, cùng data/seed/hparam, train **có** KD (`KDTrainer`) và
  **không** KD (`Trainer`) qua cờ `use_kd`. 📁 `scripts/train_student.py`. *Vì sao:* chỉ khi mọi
  thứ giống hệt trừ KD, ta mới quy được mức tăng là **do KD**.
- **KD effectiveness delta** `delta_pauc = pauc_KD − pauc_baseline`. 📁 `compute_kd_delta` trong
  [src/evaluation/metrics.py](../src/evaluation/metrics.py).
- **Biến thể 1 — MSE trên logit** (`training.distillation.soft_loss_type=mse`, Kim et al. 2021):
  thay số hạng mềm bằng `MSE(student_logit, teacher_logit)` trên logit **thô** — **không T, không
  T²** (≈ KL khi T lớn). Mặc định vẫn `bce`. *Đánh đổi:* mất "núm vặn" T.
- **Biến thể 2 — Relational KD (RKD) feature distillation** (`training=distillation_rkd`, Park et
  al. 2019): thêm số hạng **mức đặc trưng**. *Động cơ:* ở K=1 (nhị phân) một logit mang rất ít để
  chưng cất, nên RKD khớp **khoảng cách (distance) + góc (angle) theo cặp/bộ-ba trong batch** của
  feature áp chót. 📁 `RKDLoss` trong
  [src/training/feature_distillation.py](../src/training/feature_distillation.py). Điểm cần giải
  thích: **projector-free/dim-agnostic** (tính ma trận quan hệ trong **không gian riêng** mỗi bên
  rồi chuẩn hoá → teacher-dim ≠ student-dim vẫn được); trainer chỉ **tap `forward_features`** khi
  có block `feature_kd`; chi tiết an toàn số học: `_pdist` clamp khoảng cách bình phương tới `eps`
  **trước** `sqrt` (tránh NaN gradient ở đường chéo khoảng-cách-0).
- **HAI phát hiện headline (thuộc lòng — CHÍNH LÀ kết quả luận văn).** *Doc:*
  [report_phase_1/evaluation/03_kd_effectiveness.md](../report_phase_1/evaluation/03_kd_effectiveness.md).
  1. **KD cải thiện pAUC@80 và Sensitivity một cách NHẤT QUÁN** — Δ pAUC > 0 trên **mọi** cặp
     student×teacher (+0.001→+0.005); vùng độ nhạy cao (quan trọng cho sàng lọc) luôn tốt lên. Đây
     là tuyên bố **mạnh & an toàn nhất**.
  2. **Mức tăng AUPRC bị QUY ĐỊNH bởi chất lượng teacher** — teacher **mạnh** (`convnextv2_base`)
     nâng AUPRC của MobileNetV4 **+0.052** (0.609→0.661); teacher **yếu** (`efficientnet_b4`, run
     baseline cũ giữ lại để đối chứng) cho Δ AUPRC ~nhiễu hoặc âm. **Case study tốt nhất =
     `mobilenetv4_conv_medium ← convnextv2_base`.**

**❓ Tự kiểm tra.**
1. "Dark knowledge" là gì, vì sao soft target dạy được nhiều hơn nhãn cứng?
2. Điều gì xảy ra khi T→1 và T→∞?
3. T² để làm gì — giải thích bằng độ lớn gradient.
4. Vì sao teacher **bắt buộc** đóng băng?
5. Vì sao phải ghép cặp "giống hệt trừ KD" mới quy được công cho KD?
6. Vì sao ở bài nhị phân người ta thêm RKD (feature-KD) thay vì chỉ chưng cất logit?
7. Phát biểu 2 kết quả headline và cặp case study tốt nhất.

**⏱️ ~4 giờ · NẶNG.** Ưu tiên tuyệt đối; đọc kèm `03_kd_effectiveness.md`.

---

## Ngày 7 — Metadata & Privileged Learning / LUPI (Tier 6b)

*Hôm nay bạn sẽ trả lời được: nghịch lý "thêm metadata nhưng vẫn là model deploy chỉ-ảnh" — bằng
cách nào.*

**🎯 Mục tiêu ngày.** Nắm phần opt-in (mặc định TẮT, nên ma trận chỉ-ảnh **không đổi byte nào**):
2 gate cấu hình, hướng D (calibration/subgroup) và hướng A (privileged teacher). *Doc:*
[metadata_training_plan.md](metadata_training_plan.md).

**📚 Kiến thức cần học.**

- **Nghịch lý cốt lõi.** Tín hiệu metadata mạnh nhất là các cột ISIC `tbp_lv_*` (39 đặc trưng) do
  **phần cứng Vectra WB360 3D-TBP** tạo ra — **không có trên điện thoại**. Nên nó **không thể** là
  input của model deploy chỉ-ảnh; đóng góp trung thực của nó là **calibration** và một **ablation
  privileged-teacher** trung thực.
- **Hai gate độc lập (biết cái nào bật cái gì):**
  - `data.metadata_cols` — **cột nào** được mang vào split CSV. Bật **hướng D** (model vẫn chỉ-ảnh;
    cột đi theo "side-channel" `predictions.csv` qua `DataModule.test_metadata()`).
  - `data.metadata_as_input` — có nạp metadata vào batch thành **4-tuple `(image, meta, mask,
    label)`** không. Bật **hướng A** (cần **cả hai** gate).
- **Hướng D — calibration + đánh giá subgroup** (an toàn nhất, không cần train lại). Chạy lại
  `prepare` với `metadata_cols=[anatom_site_general, sex]` (split seed-deterministic → **cùng
  hàng**, chỉ thêm cột → checkpoint cũ vẫn dùng được), rồi eval lại; `compute_calibration.py
  --subgroup <col>` báo ECE/Brier theo nhóm. *Vì sao dùng một hiệu chỉnh **toàn cục**:* ở 0.39%,
  mỗi nhóm quá ít dương để khớp calibrator riêng.
- **Hướng A — privileged (LUPI) teacher.** `PrivilegedTimmBackboneModel` 📁
  [src/models/privileged.py](../src/models/privileged.py) = backbone ảnh timm ⊕ một MLP bảng nhỏ
  trên `tbp_lv_*` chuẩn hoá, fuse → head. **Chỉ teacher thấy metadata**; student chỉ-ảnh chưng cất
  **cấu trúc feature đã fuse** qua **RKD** (projector-free nên teacher-dim > student-dim vẫn ổn).
  *Config:* `configs/teacher/*_privileged.yaml` + `training=distillation_privileged`. *Ý tưởng
  LUPI:* thông tin đặc quyền có lúc **train**, vắng lúc **test**, chỉ rò dưới dạng **cấu trúc quan
  hệ**, không bao giờ là input của student → **không gì trên đường `.pte`/benchmark đổi**.
  - **`accepts_metadata=True`** báo `Trainer`/`KDTrainer` nạp `(images, meta, mask)`; **`mask`**
    làm-0 nhánh bảng cho các hàng không có metadata (vd toàn bộ PAD) để chúng không backprop qua đó.
- **Kỷ luật chống rò rỉ.** Cột `iddx_*` / `mel_*` bị **từ chối** (`_validate_metadata_cols` raise)
  — đây là **chẩn đoán hậu kỳ** = leakage; scaler metadata **chỉ fit trên train fold** rồi mới áp
  cho val/test.
- **`unpack_batch`** 📁 [src/utils/batch.py](../src/utils/batch.py) — **một cửa duy nhất** mọi
  consumer DataLoader dùng để nhận 2- **hoặc** 4-tuple; đường chỉ-ảnh trả `meta=mask=None`, chạy
  code cũ y nguyên.

**❓ Tự kiểm tra.**
1. Vì sao `tbp_lv_*` **không thể** là input của model deploy?
2. Hai gate `metadata_cols` vs `metadata_as_input` bật hướng nào?
3. Ý tưởng LUPI: thông tin đặc quyền "rò" sang student dưới dạng gì, không dưới dạng gì?
4. `mask` trong 4-tuple để làm gì?
5. Vì sao `iddx_*`/`mel_*` là leakage và scaler chỉ fit trên train fold?

**⏱️ ~2.5 giờ · Vừa.**

---

## Ngày 8 — Đánh giá & metric (Tier 7) — **NGÀY NẶNG**

*Hôm nay bạn sẽ trả lời được: vì sao AUPRC (không phải AUC-ROC) là headline, pAUC@TPR≥80 được
tính thế nào, và vì sao "xác suất quá tự tin" KHÔNG làm hỏng kết quả.*

**🎯 Mục tiêu ngày.** Nắm hệ metric: ROC/AUC nền, AUPRC headline, pAUC@TPR≥80 + McClish, ngưỡng
Youden, và phân biệt **calibration ≠ ranking**.

**📚 Kiến thức cần học.**

- **ROC, AUC, TPR/FPR** — nền cho mọi thứ dưới.
- **AUPRC là headline lâm sàng, KHÔNG phải AUC-ROC.** Ở prevalence ~0.39%, AUC-ROC **lạc quan**
  (pool TN khổng lồ); AUPRC (diện tích dưới precision–recall, mốc ngẫu nhiên = prevalence) mới
  trung thực với mất cân bằng. **pAUC = metric để so với benchmark ISIC; AUPRC = headline lâm
  sàng** — hai vai, không mâu thuẫn. 📁 `compute_metrics` trong
  [src/evaluation/metrics.py](../src/evaluation/metrics.py) trả `auprc` + `prevalence`.
- **pAUC@TPR≥80 — metric chính thức ISIC 2024.** AUC **một phần** trên vùng độ nhạy cao (TPR ∈
  [0.8,1.0]), vì dưới 80% sensitivity thì một máy sàng lọc ung thư **vô dụng lâm sàng**. 📁
  `pauc_at_tpr`. *Thủ thuật cài đặt:* lật nhãn/điểm (`v_gt=1−y`, `v_pred=−p`) để "TPR≥0.8" thành
  "FPR≤0.2", dùng sklearn `roc_auc_score(max_fpr=0.2)`, rồi **đảo ngược hiệu chỉnh McClish**. Dải
  ~[0.02 ngẫu nhiên, 0.20 hoàn hảo].
- **Sensitivity (recall/TPR), specificity (TNR), precision (PPV), F1.** Vì sao sensitivity thống
  trị trong sàng lọc ung thư.
- **Ngưỡng Youden's J** `J = TPR − FPR`, cực đại hoá để chọn ngưỡng quyết định. 📁
  `youden_threshold`. *Vì sao:* ngưỡng tinh chỉnh đánh bại 0.5 mặc định khi mất cân bằng.
- **Confusion matrix & TP/FP/TN/FN.** 📁
  [src/evaluation/confusion_matrix.py](../src/evaluation/confusion_matrix.py).
- **Baseline đa số/ngẫu nhiên** model phải vượt. 📁 `class_prevalence_baselines`.
- **Grad-CAM interpretability** — bản đồ kích hoạt trọng-số-theo-gradient; tìm conv cuối. 📁
  [src/evaluation/grad_cam.py](../src/evaluation/grad_cam.py). Cho biết model "nhìn" vào đâu, và
  giới hạn của nó.
- **Ensemble (trung bình xác suất).** 📁 [src/inference/ensemble.py](../src/inference/ensemble.py).
- **Calibration ≠ ranking.** `brier`/`ece` trong `test_metrics.json` là **miscalibration THÔ**:
  undersampler 1:5 train trên prior ~16.7%, nên `sigmoid(logit)` **quá tự tin** so với prevalence
  thật ~0.39%. Phân biệt **chất lượng xếp hạng** vs **độ trung thực của xác suất**.
  - **`compute_calibration.py --run-dir <run>`** chỉ sửa **xác suất hiển thị** offline:
    **prior-shift** dạng đóng mặc định (`logit_cal = logit(p) + logit(π_target) − logit(π_train)`),
    hoặc Platt/isotonic (`--method`) fit trên `val_predictions.csv` (val loader **không sampler** →
    giữ prevalence thật). Metric xếp hạng (pAUC/AUPRC/AUC) **bất biến với mọi phép co giãn đơn
    điệu** → **không đổi con số Chương 4 nào**, chỉ đổi "% nguy cơ" hiển thị. 📁
    [scripts/compute_calibration.py](../scripts/compute_calibration.py). *Lưu ý:* focal α=0.25 làm
    méo calibration **ngoài** phần prior → prior-shift đơn lẻ có thể vẫn để ECE cao → dùng
    isotonic/Platt.
- **File dự đoán tái tính được.** `Evaluator.save_predictions()` ghi `predictions.csv`
  (`y_true,y_prob,y_pred[,source]`) + `val_predictions.csv` → PR-curve / AUPRC / **per-domain
  (ISIC vs PAD qua `source`)** / bootstrap CI **tái tính offline** không cần chạy lại inference.
- **Cross-domain & fairness** trên HAM10000 / Fitzpatrick17k (không train). Vì sao metric theo
  **tông da** quan trọng về mặt đạo đức, và chênh lệch (disparity) trông thế nào.

**❓ Tự kiểm tra.**
1. Vì sao cùng model có thể **đẹp trên AUC-ROC nhưng tầm thường trên AUPRC** ở 0.39%?
2. pAUC@TPR≥80 tính qua mấy bước (lật nhãn → max_fpr → đảo McClish)? Dải giá trị?
3. Vì sao ngưỡng Youden đánh bại 0.5 khi mất cân bằng?
4. Giám khảo hỏi "xác suất của bạn quá tự tin, có hại kết quả không?" — trả lời sao?
5. Vì sao breakdown per-domain (ISIC vs PAD) đáng quan tâm?

**⏱️ ~4 giờ · NẶNG.**

---

## Ngày 9 — Thiết kế thí nghiệm & hạ tầng (Tier 8 + Tier 9)

*Hôm nay bạn sẽ trả lời được: vì sao báo cáo mean±std chứ không phải một fold, và các luật cứng
của cluster chia sẻ.*

**🎯 Mục tiêu ngày.** Gộp phần rigor thí nghiệm (5-fold, paired-run, aggregation) và phần kỹ thuật
(Hydra, run-dir, tầng `run/`). Phần cần "bảo vệ được nếu bị hỏi".

**📚 Kiến thức cần học — Rigor (Tier 8).**

- **5-fold cross-validation** — vì sao một split đơn không đáng tin (phương sai lớn).
- **Thiết kế paired-run.** Mỗi student train **hai lần** (KD/baseline) trên **cùng fold+seed**,
  theo từng teacher. **"30 runs" chuẩn = 3 *student* × 2 điều kiện KD × 5 fold cho MỘT teacher cố
  định** ("3 arch" = student, không phải teacher). *Đừng* quote "30" là tổng dự án — registry có 3
  (+privileged) teacher và 4 student → ma trận thật lớn hơn (~62 fold-run mới sau quyết định
  2026-07-16). *Doc:* CLAUDE.md.
- **Cảnh báo fold-completeness** — vài cặp SOTA chưa đủ 5 fold (maxvit-KD 1 fold, efficientformerv2
  2–4 fold); claim từ n<5 fold **độ tin thấp** → phải nói "n=4 fold, sơ bộ".
- **Aggregation: báo mean ± std** (không phải một fold) — `aggregate_folds.py` →
  `aggregated.{json,md}`.
- **Paired comparison** (KD vs baseline trên cùng fold/seed) — ghép cặp **giảm phương sai**.
- **Ablations** — `ratio × α` (còn TODO), lựa chọn augmentation. *Doc:* PREPROCESSING.md §3/§6.
- **MLflow tracking.** *Cmd:* `mlflow ui --backend-store-uri experiments/runs`.
- **Hyperparameter tuning.** 📁 `scripts/tune_hyperparams.py`, `configs/training/ablation.yaml`.

**📚 Kiến thức cần học — Engineering (Tier 9).**

- **Hydra config composition** — `defaults:` gộp nhóm data/teacher/student/training/augmentation;
  override CLI (vd `student=fastvit_sa12 training=baseline`). 📁
  [configs/config.yaml](../configs/config.yaml). *Gotcha:* thêm key top-level cần
  `OmegaConf.set_struct(cfg, False)`; `load_config` phải compose defaults cho script standalone.
- **Run-dir fold-aware** — `experiments/runs/<arch>/fold_{0..4}/...` để một job lấp đủ 5 fold không
  đè nhau; `test_metrics.json` + `val_metrics.json` + `predictions.csv` + `val_predictions.csv`
  tự ghi cuối train.
- **Một process một model, fold lặp *tuần tự*** — `run/train_teacher.sh` / `run/train_student.sh`
  là **một** process lặp `for FOLD in ${FOLDS:-0 1 2 3 4}`. Tách job nặng bằng `FOLDS="0 1 2"` +
  `FOLDS="3 4"`. *Doc:* [run/README.md](../run/README.md).
- **Tầng thực thi `run/`** — `run/common.sh` cấp cho mọi script: `set -euo pipefail`,
  `activate_venv` (`./.venv-linux`), `select_gpu` (`GPU=auto|<id>|cpu` → `CUDA_VISIBLE_DEVICES`),
  `start_log` (tee ra `logs/<name>_<timestamp>.log`, sống sót khi rớt SSH).
  - **Luật tách run-dir:** student tách bằng `run_suffix=`, teacher bằng `output_dir=` —
    `train_teacher.py` KHÔNG đọc `run_suffix` nên sẽ ghi đè run chính. *Gotcha:* [GOTCHAS.md](GOTCHAS.md).
  - **Luật server chia sẻ:** mọi thứ nằm trong thư mục project — không sudo/apt/system-python,
    dependency chỉ trong `./.venv-linux`, env var theo từng session. *Memory:* feedback_project_scoped_only.
- **NumPy 2.0:** `np.trapz` → `np.trapezoid`.
- **Mac ≠ server** — không pip/torch cục bộ; kiểm bằng `validate-pipeline` (static) rồi chạy trên server.

**❓ Tự kiểm tra.**
1. "30 runs" đếm những gì, và vì sao **không** phải tổng dự án?
2. Vì sao claim từ n=4 fold phải kèm chữ "sơ bộ"?
3. Vì sao ghép cặp KD/baseline trên cùng fold+seed **giảm phương sai**?
4. Vì sao ablation của teacher phải tách bằng `output_dir=` chứ không phải `run_suffix=`?
5. Luật cứng khi làm việc trên máy chủ dùng chung là gì?

**⏱️ ~3 giờ · Vừa.**

---

## Ngày 10 — Câu hỏi bảo vệ & tổng ôn

*Hôm nay bạn sẽ trả lời được: mọi câu rapid-fire, và kể được câu chuyện luận văn liền mạch từ dữ
liệu → model → KD → đánh giá.*

**🎯 Mục tiêu ngày.** Không học mới; **luyện trả lời** và **nối các tầng** thành một mạch. Tự bấm
giờ trả lời, không nhìn tài liệu.

**📚 Tự trả lời rapid-fire (rút từ checklist "Likely thesis-defense questions").**

1. Vì sao **pAUC@TPR≥80** thay vì accuracy hay AUC thường? *(mất cân bằng + sàn độ nhạy lâm sàng.)*
2. Làm sao *chứng minh* mức tăng đến từ KD chứ không phải may? *(paired baseline, cùng seed/fold,
   mean±std, delta.)*
3. Rò rỉ dữ liệu có thể chui vào đâu, mỗi đường bịt ra sao? *(gom bệnh nhân, dedup, namespacing,
   test cắt trước CV.)*
4. Vì sao chưng cất thay vì train thẳng model nhỏ? *(soft target/dark knowledge → student
   generalize tốt hơn; đưa ra delta.)*
5. T=4 và T² làm gì, cụ thể?
6. Vì sao α=0.25 focal bị nghi ngờ ở đây, sẽ ablate gì?
7. Vì sao trích test thay vì val?
8. Vì sao AUPRC là headline thay vì AUC-ROC ở 0.39%? *(pool TN lớn → AUC-ROC lạc quan; mốc AUPRC =
   prevalence.)*
9. "Xác suất của bạn quá tự tin — có hại kết quả không?" *(Không: metric xếp hạng bất biến co giãn;
   calibration là fix prior-shift offline riêng, không đổi con số Chương 4.)*
10. Thêm metadata nhưng vẫn deploy chỉ-ảnh — bằng cách nào? *(LUPI: chỉ teacher thấy `tbp_lv_*`;
    student chưng cất **cấu trúc** fuse qua RKD, không bao giờ nhận metadata làm input.)*
11. Cột metadata nào bị cấm và vì sao? *(`iddx_*`/`mel_*` = chẩn đoán hậu kỳ → leakage; scaler chỉ
    fit train fold.)*
12. Vì sao hai biến thể soft-loss (BCE vs MSE) và vì sao thêm RKD?
13. Các failure mode / giới hạn là gì? *(dedup chỉ exact per-dataset, ngưỡng lọc chưa tinh chỉnh,
    128→224 nội suy, vài cặp SOTA n<5 fold, ablation α×ratio còn treo, trọng số/arch PanDerm chờ
    verify trên server.)*

**📚 Bài tập nối mạch (kể trong 5 phút, không nhìn).** "Tôi có ~400k ảnh ISIC mất cân bằng 0.9% →
[lọc + dedup + tách test patient-disjoint + 5-fold] → [undersample 1:5 + focal loss chống mất cân
bằng] → [teacher SOTA train chuẩn] → [KD sang 4 student mobile, cặp có/không KD] → [đánh giá bằng
pAUC@TPR≥80 để so ISIC, AUPRC làm headline lâm sàng ở 0.39%] → [mean±std qua 5 fold] → kết quả:
KD tăng pAUC/sensitivity nhất quán, tăng AUPRC khi teacher đủ mạnh."

**❓ Tự chấm.** Câu nào ngập ngừng → quay lại đúng Ngày/Tier tương ứng ôn lại. Dùng subagent
`knowledge-tutor` để nó **đóng vai giám khảo hỏi vặn**.

**⏱️ ~3 giờ · Ôn tập.**

---

## Ôn tương tác với subagent `knowledge-tutor`

Sau khi **restart session** (agent mới chỉ nạp ở đầu phiên), bạn có thể gọi:

- *"Dùng knowledge-tutor giải thích lại Tier 6 (KD) cho tôi."*
- *"Dùng knowledge-tutor đóng vai giám khảo, hỏi vặn tôi phần đánh giá (Ngày 8)."*
- *"knowledge-tutor: code tính pAUC nằm ở đâu, giải thích từng bước."*

Agent bám sát code thật + checklist, **cite `file:line`**, và nói "chưa rõ" thay vì đoán.

---

*Tạo 2026-07-20 làm giáo trình 10 ngày, chuyển thể từ [review-knowledge-checklist.md](review-knowledge-checklist.md)
(nguồn chân lý, cùng với code và `report_phase_1/`). Companion: [review-knowledge-summary-vi.md](review-knowledge-summary-vi.md)
(bản tóm tắt từng tầng). Nếu file này lệch với code/checklist, chúng đúng — hãy cập nhật.*
