# Kế hoạch chi tiết: Sử dụng Metadata cho Training (3 hướng)

> Tài liệu này trả lời câu hỏi "nếu đưa metadata vào training thì làm gì, từ code tới report".
> Nó **đi kèm và cụ thể hoá** phần phân tích chiến lược ở [docs/metadata_appication.md](metadata_appication.md).
> Mọi đường dẫn/def dưới đây đã được **đối chiếu với code thực** (file:line) — không bịa API.
> Các con số định lượng chưa kiểm chứng verbatim đều gắn nhãn **[cần verify]**.
> **Đã đồng bộ với quyết định bộ model** [docs/SOTA_MODEL_DECISION_2026-07.md](SOTA_MODEL_DECISION_2026-07.md) (2026-07-16).

---

## TL;DR

- Hiện tại **toàn bộ metadata bị loại ở bước preprocessing** — `process_isic2024()`/`process_pad_ufes_20()`
  trong [src/data/preprocessing.py](../src/data/preprocessing.py) chỉ giữ 6 cột
  (`image_id, patient_id, image_path, label, class_name, source`). `SkinLesionDataset.__getitem__`
  ([src/data/dataset.py:33-41](../src/data/dataset.py)) trả đúng `(image, label)`. Model là
  `TimmBackboneModel` thuần ảnh `forward(x)->logit` ([src/models/timm_backbone.py:37-39](../src/models/timm_backbone.py)).
- **Nghịch lý cốt lõi:** signal metadata mạnh nhất (`tbp_lv_*`, 39 cột) đến từ phần cứng Vectra WB360 3D-TBP,
  **không lấy được trên điện thoại** → không thể là input cho model deploy image-only. Vì vậy metadata **không nên
  được bán như "đòn bẩy pAUC cho model deploy"**; đóng góp chắc chắn nhất là **calibration/reliability** + một
  **ablation KD-privileged trung thực**.
- Ba hướng train, xếp theo mức khuyến nghị:

| # | Hướng | Impl cost | Đổi model deploy? | Kỳ vọng headline | Rủi ro | Khuyến nghị |
|---|-------|-----------|-------------------|------------------|--------|-------------|
| A | **Privileged Teacher** (LUPI, feature-level KD) | TB–Cao | **Không** (student image-only) | ΔpAUC/ΔAUPRC +nhỏ, chưa chắc | Overfit, scope creep, leakage nếu chọn sai cột | ✅ nếu còn compute |
| B | **Auxiliary head** (regress `tbp_lv_*`, vứt lúc deploy) | TB | **Không** | +nhỏ/không chắc; **mạnh về giải thích** | Cân bằng loss | 🟡 nếu muốn tính giải thích |
| C | **Fusion-input** (MetaBlock, metadata là INPUT student) | Cao | **CÓ — phá narrative image-only** | ~+0.012 pAUC (demographic) **[cần verify]** | Shortcut, ethics, `.pte` phức tạp | ❌ không khuyến nghị |
| D | *(companion)* **Calibration + eval subgroup** (không train lại) | Thấp | Không | Ranking không đổi; calibration cải thiện lớn | Rất thấp | ✅ làm ngay |

**Bộ model hiện tại** (đồng bộ [docs/SOTA_MODEL_DECISION_2026-07.md](SOTA_MODEL_DECISION_2026-07.md), 2026-07-16):
teacher `{efficientnetv2_m (chính), convnextv2_base (phụ), panderm (foundation ViT-B/16 — loader
`PanDermModel(TimmBackboneModel)` đã code, chờ verify weights/arch/normalize trên server)}` — `maxvit_base` giữ
registry nhưng **retired khỏi run-plan**; student **4 con** `{mobilenetv4_conv_medium, fastvit_sa12,
efficientformerv2_s2, repvit_m1_0}`, **tất cả thuần ảnh** → mọi hướng dưới đây áp dụng đồng nhất cho cả 4 student.

**Ràng buộc bất biến:** mọi thay đổi phải **gate sau cờ config** để **ma trận image-only hiện có (~62 fold-run mới
sau quyết định 2026-07-16)** byte-for-byte không đổi (mặc định tắt = hành vi cũ). Student deploy phải **image-only**
cho hướng A/B.

---

## Trạng thái thực thi (cập nhật 2026-07-18)

Phạm vi user chốt: **D trước, rồi A** (bỏ B, C).

- **Hướng D — ĐÃ CODE (chờ verify cluster).** Tất cả gate sau `data.metadata_cols: null` (mặc định = ma trận
  image-only byte-for-byte không đổi). Đã ship:
  - Data-layer `metadata_cols` **dùng chung cho cả D và A**: `process_isic2024`/`process_pad_ufes_20`
    ([src/data/preprocessing.py](../src/data/preprocessing.py)) nhận `metadata_cols` (ISIC giữ verbatim, missing→NaN;
    PAD set NaN). `_validate_metadata_cols` **raise** nếu chứa cột leakage (`iddx_`/`mel_`) **hoặc** trùng cột base
    schema (`patient_id/label/...` — tránh ghi đè thành NaN gây leak/mất nhãn). `prepare_data.py` thread cấu hình;
    knob thêm ở [configs/data/isic2024.yaml](../configs/data/isic2024.yaml).
  - `SkinLesionDataModule.test_metadata(cols)` (song song `test_sources()`) — **side-channel**, KHÔNG qua
    `__getitem__` nên D không đụng dataset/trainer.
  - `Evaluator.evaluate(..., metadata=)` + `save_predictions` ghi thêm cột vào `predictions.csv`
    (`test_metrics.json` không đổi; val_predictions vẫn image-only). Wired ở train_teacher/train_student/evaluate.
  - `scripts/compute_calibration.py --subgroup <col> [--min-subgroup-n]` — ECE/Brier raw-vs-cal theo nhóm, cùng
    một hiệu chỉnh global (không fit calibrator per-group vì quá ít dương ở 0.39%).
  - **Chạy D trên checkpoint cũ — ĐÃ CHẠY 2026-08-24 trên `vastnew` bằng `run/attach_metadata.sh`.**
    Đường thiết kế ban đầu (re-run `prepare` với `metadata_cols: [...]` rồi re-eval) **KHÔNG dùng được** ở
    đây: `process_isic2024` mở `train-image.hdf5` vô điều kiện, và quan trọng hơn — nếu thiếu
    `data/raw/pad_ufes_20/` thì `prepare_data.py` **âm thầm bỏ toàn bộ hàng PAD** (nhánh "PAD-UFES-20 not
    found") → splits mới KHÁC splits mà 95 fold-run đã train/test. Thay vào đó `scripts/attach_metadata.py`
    chỉ **thêm cột** vào split CSV + `predictions.csv`/`val_predictions.csv` sẵn có (back-fill theo vị trí,
    hợp lệ vì `test_dataloader()` là `shuffle=False` và `train_sources` chỉ lọc train+val). Không kiểm chứng
    bằng niềm tin: mỗi file phải khớp row count, khớp chuỗi `y_true` với cột `label`, và khớp chuỗi `source`
    — sai một guard là bỏ qua file đó và exit ≠ 0. Kết quả: **11 split + 95 test + 95 val, 0 failure**,
    ~99,4% hàng khớp (phần còn lại là PAD → NaN, đúng như thiết kế). Không tốn GPU-giờ nào.
- **Hướng A — ĐÃ CODE (chờ verify cluster).** Gate kép: `data.metadata_cols` (cột nào) **+** `data.metadata_as_input`
  (đưa vào batch hay không). D chỉ set `metadata_cols` (side-channel, model image-only); A set **cả hai** → dataset
  trả 4-tuple. Đã ship:
  - `SkinLesionDataset(metadata_cols=)` → `(image, meta, mask, label)` khi bật (mask=0 cho NaN/PAD), `(image, label)`
    khi tắt. Scaler **fit chỉ trên train-fold** (`SkinLesionDataModule._fit_meta_scaler`, NaN-aware) rồi push sang
    val/test → không leak. `_build_meta()` giữ `_meta_raw` đồng bộ sau `train_sources` filter. `default_collate` xử lý
    4-tuple (không cần custom collate).
  - `PrivilegedTimmBackboneModel(TimmBackboneModel)` ([src/models/privileged.py](../src/models/privileged.py)):
    backbone timm ⊕ MLP tabular (`Linear→ReLU→Linear→ReLU`) → concat → `build_head(image_dim+tab_out)`. **Override**
    `forward(x,meta,mask)` và `forward_features(x,meta,mask)->(fused,logit)` (logit bit-identical). `accepts_metadata=True`.
    PAD (mask toàn 0) bị zero ở nhánh tabular → không backprop. Registry: `efficientnetv2_m_privileged`,
    `convnextv2_base_privileged`.
  - `Trainer`/`KDTrainer`/`Evaluator` unpack 2-tuple **hoặc** 4-tuple qua `src/utils/batch.py::unpack_batch`; teacher
    privileged nhận `(images,meta,mask)` (kể cả nhánh RKD `forward_features`), **student luôn image-only**. Plain
    KD/baseline (meta=None) gọi y hệt code cũ → back-compat byte-for-byte.
  - Configs: `configs/teacher/{efficientnetv2_m,convnextv2_base}_privileged.yaml` (thêm `tab_hidden/tab_out`),
    `configs/training/distillation_privileged.yaml` (= distillation_rkd, RKD là cơ chế leak). Runner `PRIVILEGED=1` +
    `META_COLS=` trên `10/11/12`; `prepare_data.py --metadata-cols`. Guard: train scripts raise nếu teacher privileged
    mà `metadata_as_input=false`.
  - **Chạy A:** prepare `META_COLS=tbp_lv_...` → `11 TEACHER=..._privileged PRIVILEGED=1` → `12 STUDENT=... TEACHER=..._privileged
    TRAINING=distillation_privileged PRIVILEGED=1`. Run-dir `kd_<teacher>_privileged_to_<student>` so với `kd_<teacher>_to_<student>` = ablation.
  - **Verified static:** review-preprocessing/training/runner + compileall + runner-lint. **Chờ server:** Hydra dry-load
    (§2, cần hydra/omegaconf) + poc-smoke-test (mask PAD, scaler train-fold, 4-tuple collate không NaN-vỡ).

---

## §0 — Taxonomy 53 cột metadata ISIC 2024 (vì sao đa số không dùng)

Đây là mục "giải thích các field không tận dụng" — nên đưa **nguyên bảng này vào report** để chứng minh việc loại bỏ
là có chủ đích, không phải bỏ sót.

| Nhóm cột | Số lượng | Phân loại | Có dùng được không? |
|----------|----------|-----------|----------------------|
| `tbp_lv_A/Aext/B/Bext/C/Cext/H/Hext/L/Lext, tbp_lv_areaMM2, tbp_lv_area_perim_ratio, tbp_lv_color_std_mean, tbp_lv_deltaA/B/L/LB/LBnorm, tbp_lv_eccentricity, tbp_lv_minorAxisMM, tbp_lv_nevi_confidence, tbp_lv_norm_border, tbp_lv_norm_color, tbp_lv_perimeterMM, tbp_lv_radial_color_std_max, tbp_lv_stdL/stdLExt, tbp_lv_symm_2axis/_angle, tbp_lv_x/y/z, tbp_lv_dnn_lesion_confidence` | 39 | **Privileged-only** | Chỉ train-time (hướng A/B). **Không có trên phone** (cần Vectra WB360 3D-TBP) → không bao giờ là input deploy |
| `iddx_full, iddx_1..5, mel_mitotic_index, mel_thick_mm` | 8 | **LEAKAGE (nhãn hậu sinh thiết)** | ❌ **Cấm dùng kể cả privileged**. Đây là chẩn đoán/mô bệnh học sau sinh thiết; trong ISIC 2024 gần như **chỉ có giá trị ở ca dương tính** → chính sự có/NaN đã lộ nhãn. Dùng làm feature = teacher biến thành "máy copy nhãn", soft target ≈ hard label → **mất sạch dark knowledge** |
| `lesion_id, attribution, copyright_license, image_type, tbp_tile_type, tbp_lv_location, tbp_lv_location_simple` | 7 | **Hành chính/định danh** | ❌ Không tổng quát hoá; còn tạo shortcut theo nguồn/thiết bị → loại |
| `age_approx, sex, anatom_site_general, clin_size_long_diam_mm` | 4 | **Deployable subset** | 🟡 *Có thể* lấy trên phone. Nhưng PAD-UFES-20 dùng schema khác (không có `tbp_lv_*`, có anamnesis) → giao ISIC∩PAD gần rỗng → lợi ích demographic-only nhỏ |
| `isic_id, target, patient_id` | 3 | **Đang dùng** | image_id / label / group-key (đã có trong pipeline) |

**Lưu ý pha loãng (quan trọng cho hướng A/B):** `tbp_lv_*` **chỉ có ở ISIC**. PAD-UFES-20 — nguồn augment malignant
chính — **không có** các cột này. Nên nhánh tabular của teacher/aux-head chỉ nhận signal trên subset ISIC; các mẫu
malignant từ PAD phải **mask** (không backprop nhánh tabular) → lợi ích privileged bị pha loãng thêm.

---

## §A — Hướng 1: Privileged Teacher (LUPI, feature-level KD) — *khuyến nghị*

### Ý tưởng
Stage-1 huấn luyện một **teacher đặc quyền** = (image backbone của một teacher **timm** — `efficientnetv2_m` chính
hoặc `convnextv2_base`; **KHÔNG** dùng `panderm`, xem *Định vị* cuối §A) ⊕ (MLP mã hoá `tbp_lv_*` đã chuẩn hoá) →
fusion → 1 logit.
Stage-2 student **thuần ảnh** distill từ teacher này. Vì §A4 của tài liệu gốc (nhị phân single-logit làm DKD /
logit-standardization / OFA-KD **suy biến** ở K≤2), phần tri thức `tbp_lv_*` rò rỉ vào student **qua feature-level KD**,
không qua logit. Dùng lại **đúng đường RKD sẵn có** — không phải viết loss mới.

Đường RKD hiện tại đã đúng dạng cần: `RKDLoss.forward(feat_s, feat_t)` không cần projector, **miễn nhiễm với
chênh lệch chiều đặc trưng** teacher/student ([src/training/feature_distillation.py:42-85](../src/training/feature_distillation.py)),
và KDTrainer đã có nhánh `if self.rkd is not None: teacher.forward_features(images)`
([src/training/kd_trainer.py:196-212](../src/training/kd_trainer.py)). Nhánh RKD (`training=distillation_rkd`) nay
là hạng mục **đang chạy thật** trong run-plan 2026-07 → privileged teacher cắm vào một path đã được exercised,
không phải code loss mới.

### Code surface (đường dẫn + việc cần làm — tất cả gate sau cờ config)

1. **`configs/data/isic2024.yaml`** — thêm knob (mặc định null → hành vi cũ):
   ```yaml
   metadata_cols: null   # vd: [tbp_lv_symm_2axis, tbp_lv_norm_border, tbp_lv_norm_color, ...]
   ```
2. **[src/data/preprocessing.py](../src/data/preprocessing.py)** `process_isic2024()`:
   giữ thêm các cột trong `metadata_cols` vào records ISIC (đọc từ `train-metadata.csv`). `process_pad_ufes_20()`:
   set các cột đó = `NaN`. Vì `generate_group_kfold_splits()` ghi DataFrame nguyên trạng ra CSV, các cột này
   **tự chảy** vào `train/val/test_split.csv` không cần sửa hàm split.
3. **[src/data/dataset.py](../src/data/dataset.py)** `SkinLesionDataset`:
   thêm tham số `metadata_cols=None`. Khi bật, `__getitem__` trả `(image, meta_tensor, meta_mask, label)`
   (mask = 0 nếu NaN, tức mẫu PAD); khi tắt vẫn trả `(image, label)` **y nguyên** để mọi run cũ không đổi.
4. **[src/data/datamodule.py](../src/data/datamodule.py)**:
   - Fit **StandardScaler chỉ trên `train_split` của fold** (không dùng val/test → tránh leak), lưu mean/std vào
     run-dir để tái lập / để export nếu cần.
   - Thread metadata qua collate; thêm `test_metadata()` song song `test_sources()`.
5. **[src/models/](../src/models/)** — model mới `PrivilegedTimmBackboneModel(BaseModel)`:
   - `__init__`: image backbone của **teacher timm** (dựng như `TimmBackboneModel`: `create_timm_backbone` +
     `infer_backbone_out_dim`) + `nn.Sequential(Linear→ReLU→Linear)` cho tabular + fusion (concat rồi `Linear`) → `build_head`.
   - `forward(self, x, meta=None, mask=None) -> logit`.
   - **BẮT BUỘC override `forward_features(self, x, meta, mask) -> (fused_feat, logit)`** — vì docstring của
     `BaseModel.forward_features` ([src/models/base_model.py:15-27](../src/models/base_model.py)) cảnh báo:
     *"A subclass whose forward deviates from this layout MUST override this too, keeping the returned logit
     bit-identical to forward(x)."* Nếu quên, RKD sẽ lấy nhầm feature thuần ảnh.
   - Đăng ký trong `registry.py`; tạo `configs/teacher/<name>_privileged.yaml`.
   - *Tiền lệ khuôn subclass trong repo:* `PanDermModel(TimmBackboneModel)` ([src/models/panderm.py](../src/models/panderm.py))
     cho thấy pattern "subclass `TimmBackboneModel` → gọi `super().__init__(cfg)` → mở rộng `__init__`" — privileged
     model dùng đúng khuôn này (thêm nhánh tabular + **override** `forward`/`forward_features`). **Khác biệt:** PanDerm
     chỉ nạp weights nên **giữ nguyên** `forward_features` kế thừa (ViT-B/16 768-d, layout timm chuẩn); privileged model
     **buộc override** vì forward có fusion. PanDerm là **trục đóng góp riêng** — đừng gộp với privileged.
6. **[src/training/trainer.py](../src/training/trainer.py)** (dùng để train Stage-1 teacher đặc quyền):
   `_train_epoch`/`_val_epoch` đang unpack `for images, labels in loader` — thêm nhánh back-compat nhận
   `(images, meta, mask, labels)` khi `metadata_cols` bật, gọi `model(images, meta, mask)`.
7. **[src/training/kd_trainer.py](../src/training/kd_trainer.py)** (Stage-2):
   - `_train_epoch` ([:189](../src/training/kd_trainer.py)) unpack thêm metadata **back-compat**.
   - Nhánh RKD: đổi `teacher.forward_features(images)` → `teacher.forward_features(images, meta, mask)`
     **chỉ cho teacher privileged**; `student.forward_features(images)` **giữ thuần ảnh**.
   - `_val_epoch` ([:246-251](../src/training/kd_trainer.py)): teacher cần meta để cho logit nhất quán → truyền vào teacher, student vẫn `student(images)`.
8. **configs/training**: variant `distillation_privileged.yaml` (kế thừa `distillation_rkd.yaml`, thêm cờ chọn teacher privileged).
9. **runner** ([run/train_teacher.sh](../run/train_teacher.sh), [run/train_student.sh](../run/train_student.sh)):
   thêm biến `PRIVILEGED=1` truyền qua `${VAR:-default}`; cập nhật [run/README.md](../run/README.md) + [run/README.md](../run/README.md).

### Guards bắt buộc
- **Loại `iddx_*` / `mel_*`** khỏi mọi `metadata_cols` (leakage — §0).
- **Mask PAD** ở nhánh tabular (PAD không có `tbp_lv_*`).
- Student **không bao giờ** nhận metadata → `.pte`/INT8/benchmark **không đổi một dòng**.
- Scaler fit **chỉ trên train-fold**.

### Report
- So **privileged-vs-non-privileged teacher** trên cùng student, cùng seed=42, cùng 5-fold.
- Trích **mean ± std** từ `aggregated.json` (không trích 1 fold).
- **Ngưỡng giữ:** ΔpAUC (hoặc ΔAUPRC) ≥ ~+0.01 **nhất quán ≥4/5 fold**; nếu không → dừng, giữ image-only + calibration.

### Định vị vs PanDerm (tránh trùng đóng góp)
Privileged teacher (LUPI) và **PanDerm** (teacher domain-foundation,
[docs/SOTA_MODEL_DECISION_2026-07.md §7](SOTA_MODEL_DECISION_2026-07.md)) cùng chiếm "slot teacher mới lạ" và
**cạnh tranh compute**. Đây là **2 trục riêng, trả lời 2 câu khác nhau**:
- **LUPI** = *"metadata privileged ở teacher (image + `tbp_lv_*`) có giúp student image-only không?"* → trục **thông tin đầu vào teacher**.
- **PanDerm** = *"teacher pretrain domain da liễu có distill hơn teacher supervised-CNN không?"* → trục **kiến trúc/pretrain teacher**.

→ **Chốt định vị & ngân sách compute TRƯỚC khi train.** **Không** dựng privileged teacher trên nền `panderm`
(gộp 2 trục = thừa + rối narrative). Bổ trợ nhau nếu tách bạch; thừa nếu bán như "một đóng góp duy nhất".

---

## §B — Hướng 2: Auxiliary multi-task head (ABCDE, train-only)

### Ý tưởng
Thêm **head phụ chỉ tồn tại lúc train** buộc backbone regress các đặc trưng ABCDE đã lượng hoá trong `tbp_lv_*`:
Asymmetry↔`tbp_lv_symm_2axis`, Border↔`tbp_lv_norm_border`, Color↔`tbp_lv_norm_color`/`tbp_lv_color_std_mean`,
Diameter↔`clin_size_long_diam_mm`. **Deploy: bỏ head phụ** → student vẫn image-only, `.pte` không đổi
(áp dụng cho cả **4 student**, gồm `repvit_m1_0`).

### Code surface
- Data layer: giống §A (giữ cột `tbp_lv_*` + mask PAD).
- Model: thêm `aux_head = Linear(in_features, n_aux)` song song head chính; `forward` trả cả logit chính + aux khi train.
- Trainer: thêm `L_aux = masked_MSE(aux_pred, aux_target)` vào tổng loss; **mask theo dataset** (PAD → không backprop head aux).
- Cân bằng nhiều loss (focal + KD + nhiều aux): dùng **uncertainty weighting (Kendall & Gal 2018)** hoặc
  **GradNorm (Chen 2018)** thay vì chỉnh tay các trọng số.

### Honest caveat (đưa vào report)
Dưới prevalence 0.39%, auxiliary regression `tbp_lv_*` chủ yếu là **representation regularizer**; lợi ích lên
AUPRC/pAUC thường **nhỏ và không chắc** cho binary + imbalance cực đoan. **Giá trị lớn nhất là khả năng giải thích**
(head ABCDE cho biết "vì sao nghi ngờ") — hỗ trợ narrative "độ tin cậy", không phải chạy đua pAUC.

---

## §C — Hướng 3: Fusion-input MetaBlock — ❌ KHÔNG khuyến nghị (kèm cảnh báo)

### Ý tưởng
Metadata (chỉ subset deployable: age/sex/`anatom_site_general` + anamnesis kiểu PAD) là **INPUT của student** qua
cơ chế fusion (MetaBlock/FiLM/cross-attention). Student **không còn image-only**.

### Cảnh báo bắt buộc (ghi rõ trong report nếu chọn)
1. **Phá narrative** "image-only lightweight backbone" — trục chính của khoá luận.
2. **Rủi ro shortcut nghiêm trọng nhất:** ISIC = TBP crop, PAD = ảnh smartphone, **PAD là nguồn augment malignant**
   → model có thể học "trông giống ảnh PAD ≈ malignant" thay vì học tổn thương. Bắt buộc **domain adversarial (DANN)**
   / per-dataset normalization + **report cross-domain HAM10000** để lộ shortcut + ablation "drop metadata lúc test".
3. **`tbp_lv_*` bất khả dụng trên phone** → model deploy chỉ dùng subset demographic yếu → là **một model KHÁC, yếu hơn**
   bất kỳ phiên bản dùng `tbp_lv_*` nào.
4. Lợi ích kỳ vọng nhỏ: theo brief ISIC 2024, thêm demographic cơ bản chỉ nâng pAUC ~0.142 → ~0.154 (**~+0.012**) **[cần verify verbatim — Kurtansky et al.]**.

### Tác động mobile chi tiết (trả lời trực tiếp cho câu 5) — xem §"Mobile" bên dưới.

---

## §D — Companion low-risk: Calibration + eval theo subgroup (không train lại)

Đây là "quick win" đúng nghĩa reliability, **không đụng model/matrix/deploy**, làm ngay trên checkpoint đã có.

- **Cột metadata vào predictions:** thêm `test_metadata()` (như `test_sources()`), rồi ghi thêm cột vào
  `predictions.csv` qua `Evaluator.save_predictions` ([src/evaluation/evaluator.py:93-120](../src/evaluation/evaluator.py)) —
  đúng khuôn mẫu cột `source` đã có sẵn (`metrics["_source"]`).
- **Calibration theo nhóm:** mở rộng [scripts/compute_calibration.py](../scripts/compute_calibration.py) thêm
  `--subgroup <col>` để tính **ECE/Brier + prior-shift theo từng nhóm** (anatomical site / sex). Prior-shift closed-form
  (`--method none`) không cần fit; isotonic/platt fit trên `val_predictions.csv`.
- **Bất biến quan trọng:** ranking metrics (pAUC@TPR80 / AUPRC / AUC-ROC) **không đổi** dưới re-scaling đơn điệu →
  **không đụng bất kỳ số Chương-4 nào**; chỉ làm "% risk" hiển thị trung thực.

---

## §E — Ảnh hưởng tới pipeline & mục tiêu khoá luận (câu 4)

| Khía cạnh | Hướng A (privileged) | Hướng B (auxiliary) | Hướng C (fusion-input) | Hướng D (calibration) |
|-----------|----------------------|---------------------|------------------------|------------------------|
| Student deploy image-only | ✅ giữ | ✅ giữ | ❌ mất | ✅ giữ |
| `.pte`/XNNPACK/benchmark | không đổi | không đổi | phải sửa (nhánh tabular, op concat) | không đổi |
| Ma trận image-only (~62 fold-run) | +1 trục ablation sạch (gate) | +1 trục (gate) | gần như redesign | 0 (hậu xử lý) |
| Rủi ro leakage/shortcut | có (nếu chọn sai cột) | có (mask) | **cao** | không |
| Effort | TB–Cao | TB | Cao | Thấp |

**Định vị đóng góp (khuyến nghị):** vì signal mạnh nhất không deploy được, **không bán metadata như tăng accuracy
deploy**. Đóng góp defensible = **reliability (calibration/selective prediction) + một ablation KD-privileged trung thực**.
Điều này *củng cố* câu chuyện khoá luận thay vì làm loãng. **Phối hợp với trục PanDerm:** giữ **LUPI và PanDerm
tách bạch** (§A *Định vị*) để mỗi hạng mục là một đóng góp riêng, không trùng slot "teacher mới lạ".

---

## §"Mobile" — Xử lý trên điện thoại sau khi train có metadata (câu 5)

- **Hướng A / B (privileged / auxiliary):** student deploy **100% image-only** → export `.pte`
  ([scripts/export_executorch.py](../scripts/export_executorch.py)), XNNPACK, `benchmark.py`, `make_benchmark_set.py`
  **KHÔNG đổi**. Trên phone **không cần thu thập gì thêm**. *Đây chính là lý do LUPI/auxiliary là lựa chọn đúng.*
- **Hướng C (fusion-input):** phía mobile đổi đáng kể:
  1. App cần UI thu `age/sex/site` (+ anamnesis) → phụ thuộc người dùng khai đúng.
  2. Graph `.pte` thêm nhánh tabular (Linear/ReLU export được, nhưng **op concat/fusion phải verify hỗ trợ
     XNNPACK delegate**).
  3. Ship **thống kê scaler** (mean/std tabular) trong app + xử lý **thiếu field** on-device.
  4. `tbp_lv_*` bất khả dụng → model deploy chỉ dùng subset demographic yếu.
  5. `make_benchmark_set.py` phải phát thêm vector metadata; parity check phải kiểm cả nhánh tabular.

---

## §F — Các bước làm REPORT / thesis

1. **Bảng taxonomy §0** — chứng minh việc loại 47/53 cột là có chủ đích (leakage / privileged-only / hành chính / deployable-yếu).
2. **Bảng ablation A** — privileged vs non-privileged teacher, mean ± std qua 5 fold (pAUC@TPR80 + AUPRC).
3. **Cross-domain HAM10000** — bắt buộc, để lộ shortcut (nhất là nếu thử hướng C).
4. **Reliability** — reliability diagram + ECE/Brier trước/sau calibration (từ hướng D), theo subgroup nếu có.
5. **Ngưỡng ra quyết định** — nêu rõ tiêu chí giữ/bỏ (ΔpAUC ≥ +0.01 nhất quán ≥4/5 fold; nếu "drop metadata lúc test"
   làm điểm sụt mạnh ở hướng C → bằng chứng shortcut → bỏ).
6. **Câu chữ trung thực** — không gọi metadata là "tăng accuracy deploy"; định vị đúng là reliability + ablation KD.

---

## §G — Checklist thực thi (theo modification-workflow bắt buộc)

Cho **mỗi** hướng nếu code hoá:

1. **Code** thay đổi (gate sau cờ config, mặc định tắt = hành vi cũ).
2. **Review** bằng skill đúng area:
   - `src/data/**`, `scripts/prepare_data.py` → **`review-preprocessing`**
   - `src/training/**`, `src/models/**`, `scripts/train_{teacher,student}.py` → **`review-training`**
   - `run/**` + docs → **`review-runner`**
3. **Propagate to the runner** — cập nhật `run/train_{teacher,student}.sh` + `run/README.md` cùng lúc.
4. **Verify** — chạy **`validate-pipeline`** (static, Mac); rồi **`poc-smoke-test`** trên cluster
   (đảm bảo path metadata không NaN-vỡ, mask PAD đúng, scaler chỉ fit train-fold). **Không** verify trên Mac.
5. **Document** — cập nhật `CLAUDE.md` "Recurring gotchas" (nếu có bẫy mới, vd NaN mask), docs area, và auto-memory.

**Kiểm thử back-compat quan trọng:** với `metadata_cols: null`, một run KD/baseline phải cho kết quả
**byte-for-byte** như trước (dataset trả `(image, label)`, trainer unpack 2-tuple, student thuần ảnh).

---

## Caveats & References

- Kế thừa toàn bộ caveats của [docs/metadata_appication.md](metadata_appication.md). Các số **0.142 / 0.154 / 0.1726 /
  0.939 / 0.922** lấy theo brief dẫn từ Kurtansky et al. (*npj Digital Medicine*, PMC12639164) — **cần đối chiếu
  verbatim + DOI** trước khi ghi cứng vào luận văn.
- Số **BACC MetaBlock/MetaNet** (Pacheco & Krohling, IEEE JBHI) và **DOI/số liệu Soenksen et al. 2021**
  (Science Translational Medicine) **chưa xác minh offline** — phải tra cứu lại.
- **Claim well-supported:** degeneracy DKD/logit-standardization/OFA-KD ở K≤2; khung LUPI/generalized distillation;
  công thức prior correction/logit adjustment; rủi ro dataset-bias shortcut (ISIC-crop vs PAD-smartphone).
- **Claim extrapolation (đừng oversell):** mức lợi ích cụ thể của auxiliary/privileged cho binary + prevalence 0.39%
  **chưa được chứng minh mạnh** trong y văn; kỳ vọng nên khiêm tốn. Đóng góp chắc chắn nhất của "khai thác metadata"
  ở bối cảnh này là **calibration/reliability**, không phải nâng pAUC tuyệt đối.

**Tham chiếu chính** (chuẩn hoá DOI/venue theo [docs/metadata_appication.md](metadata_appication.md)):
Lopez-Paz 2016 (generalized distillation) · Vapnik & Vashist 2009 / Vapnik & Izmailov 2015 (LUPI) ·
Park 2019 (RKD) · Tung & Mori 2019 (SP) · Romero 2015 (FitNet) · Pacheco & Krohling 2021 (MetaBlock) ·
Kendall & Gal 2018 (uncertainty weighting) · Chen 2018 (GradNorm) · Menon 2021 (logit adjustment) ·
Guo 2017 (temperature scaling) · Ganin 2016 (DANN) · Perez 2018 (FiLM).
