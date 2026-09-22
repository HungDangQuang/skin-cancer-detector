# Kế hoạch: Arm tăng cường nhắm miền (`augmentation=domain`)

> Tài liệu này trả lời: *"mô hình sụp khi đổi miền ảnh — huấn luyện lại với tăng cường
> nhắm đúng nguyên nhân đã chẩn đoán thì thu hồi được bao nhiêu?"*
> **Trạng thái: Việc 1 XONG (21/09). Việc 2 CHƯA chạy — phạm vi đã ĐỔI, xem cảnh báo dưới.**
>
> ⚠️ **RÀNG BUỘC BẤT BIẾN CŨ ĐÃ VÔ HIỆU (22/09).** Tài liệu này ban đầu ghi *"không chạy lại
> `prepare` → splits không đổi → ma trận 140 fold-run vẫn so sánh được"*. Điều đó **không còn
> đúng**: `data/splits/` đã **mất** trên box, và khi dựng lại mới phát hiện splits gốc
> **không gom theo bệnh nhân** — dấu vân tay kích thước fold là bằng chứng (gom theo bệnh nhân
> cho độ lệch 24.270 dòng; splits gốc lệch **1 dòng**, tức phân hoạch theo từng dòng). Ma trận
> 140 fold-run vì thế có **rò rỉ bệnh nhân** giữa train và test.
>
> Quyết định của tác giả 2026-09-22: **sinh splits MỚI gom nhóm đúng** (`scripts/rebuild_splits.py`,
> đã verify tách biệt bệnh nhân 5/5 fold). Hệ quả bắt buộc phải chấp nhận:
> **arm này KHÔNG so sánh được với 140 fold-run cũ** ⇒ phải **tự chứa**: train lại cả nhánh
> `light` làm đối chứng trên splits mới. **Khối lượng 15 → 30 fold-run.**
> Chi tiết sự cố: memory `project_splits_lost_incident`.
> Mọi `file:line` dưới đây đã đối chiếu với code thực.

---

## TL;DR

- **Vấn đề đã đo:** cặp ship tụt từ in-domain AUPRC 0,6510 → HAM10000 **0,4572**; Sens@90%Spec
  0,9544 → **0,4624** (sập hơn một nửa). Teacher 453 MB tụt đúng bằng student 40 MB
  (0,6566 → 0,4856) ⇒ **sụp miền không phải hệ quả của việc nén mô hình**, mà của dữ liệu huấn luyện.
- **Nguyên nhân đã chẩn đoán được:** khung ảnh (field of view). Thí nghiệm crop70 cho **19/19 run dương**,
  **18/19 có ý nghĩa trên AUC-ROC** (nhưng chỉ 16/19 trên AUPRC, 7/19 trên Sens@90Spec), thu hồi
  **~6%** khoảng cách miền, **da tối hưởng lợi nhiều nhất**
  ([docs/PREPROCESSING.md:247-258](PREPROCESSING.md)).
- **Lỗ hổng:** crop70 sửa framing ở **thời điểm suy luận**. Chưa ai sửa ở **thời điểm huấn luyện** —
  `ShiftScaleRotate.scale_limit` đang là **0,2 ở CẢ `light` VÀ `heavy`**
  ([light.yaml:15](../configs/augmentation/light.yaml), [heavy.yaml:18](../configs/augmentation/heavy.yaml)),
  tức trục field-of-view **chưa từng được chạm vào**. `heavy` chỉ mạnh hơn về màu/nhiễu.
- **Giải pháp:** thêm `configs/augmentation/domain.yaml` nhắm hai trục — **field of view** và
  **ánh sáng/cân bằng trắng** — rồi train lại **15 fold-run** trên cặp nhanh nhất và so paired CI
  với nhánh `light` đã có.
- **Trần kỳ vọng: thấp.** Nếu framing chỉ chiếm ~6% vấn đề thì sửa ở train cũng có trần tương tự.
  Kết quả âm vẫn có giá trị: nó chuyển kết luận thành *"bài toán cần thêm dữ liệu, không cần thêm kỹ thuật"*.

---

## 1. Scope

| | |
|---|---|
| **Cặp chọn** | `efficientnetv2_m` → `mobilenetv4_conv_medium` |
| **Lý do** | Nhanh nhất cả hai vai: teacher **678 img/s** (vs convnextv2_base 238, maxvit_base 143); student **3.255 img/s** (vs repvit 2.151, fastvit 1.438). Nguồn: `reports/benchmark/*.json`, batch 32, RTX 3090 |
| **Cường độ** | **Một** arm, `scale_limit: 0.5` (phương án a) |
| **Khối lượng** | ~~15~~ → **30 fold-run** = (5 teacher + 5 baseline + 5 KD) × **2 nhánh aug** (`light` đối chứng + `domain`) |
| **Đối chứng** | ~~Đã có sẵn, không train lại~~ — **KHÔNG còn dùng được.** Các run cũ nằm trên splits đã rò rỉ bệnh nhân; nhánh `light` phải train LẠI trên splits mới thì cặp so sánh mới hợp lệ |

**KHÔNG làm trong arm này:** MIDAS (đã loại vì phình scope) · arm thứ hai `scale_limit: 0.35` ·
mở rộng 4 student × 2 nhánh · chạy lại `prepare` · train lại ma trận 140 fold · thêm dataset mới
(việc riêng, xem §6).

---

## 2. Việc 1 — Mac, không GPU, không phụ thuộc ai

| # | File | Thay đổi | Xong |
|---|---|---|:--:|
| 1.1 | `configs/augmentation/domain.yaml` | **Tạo mới** — bảng op ở §3 | ☐ |
| 1.2 | `run/train_teacher.sh` | Docstring `AUG light \| heavy` → `light \| heavy \| domain` | ☐ |
| 1.3 | `run/train_student.sh` | Y như trên | ☐ |
| 1.4 | `run/README.md` | Ghi nhận biến thể thứ ba + lý do thiết kế | ☐ |
| 1.5 | `docs/PREPROCESSING.md §4.1–4.2` | Bổ sung `domain` vào mô tả aug config-driven | ☐ |
| 1.6 | — | Chạy **`validate-pipeline`** (AST + Hydra compose + runner lint) | ☐ |
| 1.7 | `MEMORY.md` + memory file | Ghi arm mới | ☐ |

Việc 1 **không** sửa `src/`. Không cần entry mới trong `MODEL_REGISTRY`, không cần config teacher mới
— xem §4 vì sao.

---

## 3. Thiết kế `domain.yaml`

`build_transforms` **luôn prepend `Resize(image_size)`** ([src/data/transforms.py:86](../src/data/transforms.py))
⇒ **không dùng `RandomResizedCrop`**: nó sẽ crop từ ảnh đã bị squash, đúng cái
[PREPROCESSING.md:192](PREPROCESSING.md) cảnh báo (*"cropping the already squashed 224 square would
discard the very detail the crop is meant to zoom into"*). Trục field-of-view đi qua
`ShiftScaleRotate.scale_limit` thay thế: `scale < 1` làm nội dung ảnh nhỏ lại giữa khung —
đúng nghĩa "chụp xa hơn".

| Op | `light` (hiện tại) | **`domain` (mới)** | Mô phỏng |
|---|---|---|---|
| `HorizontalFlip` / `VerticalFlip` / `RandomRotate90` | p 0,5 | p 0,5 (giữ nguyên) | Tổn thương không có hướng chuẩn |
| `ShiftScaleRotate` | shift 0,1 / **scale 0,2** / rot 180 / p 0,5 | shift **0,3** / **scale 0,5** / rot 180 / p **0,9** | **Field of view + lệch tâm** — trục chính của arm này |
| `ColorJitter` | 0,2/0,2/0,2/0,1 · p 0,5 | **0,4/0,4/0,4/0,2** · p **0,8** | Cân bằng trắng + ánh sáng khác nhau giữa các máy |
| `CLAHE` | clip 2,0 · p 0,2 | clip **4,0** · p **0,5** | Biến thiên tương phản |
| `RandomGamma` | — | **mới** · p 0,3 | Sai phơi sáng |
| `GaussianBlur` | blur [3,7] · p 0,2 | blur [3,7] · p **0,3** | Lấy nét trượt |
| `GaussNoise` | — | **mới** · var [10,50] · p 0,3 | Nhiễu cảm biến điện thoại |
| `Normalize` | ImageNet | ImageNet (giữ nguyên) | — |
| **khối `val`** | `Normalize` | **`Normalize` — Y NGUYÊN** | **Không được chạm vào đường đánh giá** |

**Cấm, có lý do:**
- **MixUp / CutMix / CutOut** — `_FORBIDDEN_OPS` raise ngay ([src/data/transforms.py:37](../src/data/transforms.py)).
- **Vignette kiểu ống kính soi da** — dữ liệu duy nhất có vignette là **HAM10000, tập test xuyên miền**;
  train cho nó là trộn tổng quát hoá với rò rỉ ([PREPROCESSING.md:392](PREPROCESSING.md)).

**ĐÍNH CHÍNH (2026-09-21, khi thi công):** câu trước đây ở đây — *"ops được resolve theo tên từ
albumentations, chỉ `_FORBIDDEN_OPS` bị chặn"* — **SAI**. `_TRANSFORM_BUILDERS`
([src/data/transforms.py:11](../src/data/transforms.py)) là một **allowlist**: `_build_op` raise
`Unknown augmentation` với bất kỳ tên nào không có builder ([transforms.py:54-58](../src/data/transforms.py)).
`GaussNoise` đã có sẵn; **`RandomGamma` thì không** — đã phải thêm builder cho nó.
⇒ Kéo theo: câu "Việc 1 **không** sửa `src/`" ở §2 cũng sai; arm này BẮT BUỘC đụng `src/`.

---

## 4. Việc 2 — Server, 15 fold-run

Cả arm ghi vào **`experiments/runs_aug_domain/`**, theo tiền lệ `experiments/runs_isic_only/`.

**Vì sao `output_dir` chứ không phải `run_suffix`** — một quyết định giải đúng hai bẫy cùng lúc:
1. `scripts/train_teacher.py:39` hardwire `Path(cfg.output_dir)/"teacher"/cfg.teacher.name/f"fold_{fold}"`
   và **không đọc `run_suffix`** ⇒ teacher variant chạy bằng `run_suffix=` sẽ **ghi đè** teacher chính.
2. `scripts/train_student.py:62` tìm teacher checkpoint tại
   `{cfg.output_dir}/teacher/{cfg.teacher.name}/fold_{fold}/checkpoints/best_model.pth`
   ⇒ đổi `output_dir` là student tự tìm đúng teacher mới, **không cần** config teacher mới
   (mà nếu tạo config teacher tên khác thì lại phải thêm entry vào `MODEL_REGISTRY`, vì
   `build_model` raise khi `cfg.model.name` không có trong registry — `src/models/registry.py:37-38`).

```bash
export TMPDIR="$(pwd)/.tmp"          # / trên server đã từng đầy 100%

# (1) Teacher — phải xong đủ 5 fold TRƯỚC khi chạy (3)
bash run/train_teacher.sh TEACHER=efficientnetv2_m AUG=domain GPU=0 \
     EXTRA="output_dir=experiments/runs_aug_domain"

# (2) Baseline student (không KD) — độc lập với (1), chạy song song được nếu pin GPU khác
bash run/train_student.sh STUDENT=mobilenetv4_conv_medium TRAINING=baseline AUG=domain GPU=1 \
     EXTRA="output_dir=experiments/runs_aug_domain"

# (3) KD student — sau (1)
bash run/train_student.sh STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m \
     TRAINING=distillation AUG=domain GPU=0 \
     EXTRA="output_dir=experiments/runs_aug_domain"

# Sau mỗi run-dir xong đủ 5 fold:
bash run/aggregate.sh RUN_DIR=experiments/runs_aug_domain/<run>
```

Launch dưới `tmux`/`nohup`. **Pin `GPU=<id>`** khi chạy hai job — `GPU=auto` chọn card rảnh nhất nên
hai lệnh phóng cùng lúc có thể đâm nhau. Kéo về Mac: `bash run/pull_results.sh pull`.

| ☐ | Bước |
|:--:|---|
| ☐ | 2.1 Teacher, 5 fold |
| ☐ | 2.2 Baseline student, 5 fold |
| ☐ | 2.3 KD student, 5 fold (sau 2.1) |
| ☐ | 2.4 `aggregate.sh` × 3 |
| ☐ | 2.5 `pull_results.sh pull` |

---

## 5. Việc 3 — Đánh giá

| ☐ | Tầng | Cách |
|:--:|---|---|
| ☐ | In-domain | `test_metrics.json` tự sinh khi train xong |
| ☐ | Cross-domain | `bash run/evaluate_external.sh DATASET=ham10000 RUNS="<3 run-dir mới>"` |
| ☐ | Công bằng theo tông da | `bash run/evaluate_external.sh DATASET=fitzpatrick17k VARIANTS=all` |
| ☐ | **Paired CI** | `run/bootstrap_ci.sh` — **phải dựng tree tạm trước**, xem dưới |

⚠️ **Bẫy phải xử lý:** `bootstrap_ci.sh` §3 chỉ tự ghép cặp `__<suffix>` với run cùng tên không suffix
**trong cùng một `RESULTS_DIR`**. Arm mới nằm ở tree khác và **trùng tên** ⇒ auto-pairing **không kích hoạt**.
Cách đúng đã có tiền lệ: `reports/framing_crop_ci19.md` được sinh từ `.tmp/framing_ci19` với run-dir
**đổi tên** (`x_baseline_..._crop70`). Làm y vậy — symlink hai nhánh vào một tree tạm, đặt tên
`..._light` / `..._aug_domain`, rồi chạy CI trên tree đó. Script chỉ đọc `fold_*/predictions.csv`.

**Ô quyết định:** ΔAUPRC và ΔSens@90Spec **trên HAM10000 và Fitzpatrick17k**, **paired**.
In-domain chỉ dùng để kiểm *"aug mới có làm hại miền gốc không"* — với 241 ca dương trên 62.040 ảnh,
in-domain vốn thiếu lực (chỉ 5/12 cặp KD đạt ý nghĩa ở đó).

---

## 6. Việc 4 — Song song, khởi động ngay

| ☐ | Bước |
|:--:|---|
| ☐ | Xin Research Use Agreement cho **DDI** (Diverse Dermatology Images, Stanford) |

**Vì sao DDI:** 656 ảnh / 570 bệnh nhân, **171 ác tính / 485 lành**, FST **cân bằng có chủ đích**
(I-II 208 · III-IV 241 · V-VI 207), non-commercial research use — **cho phép huấn luyện**. Là bộ duy nhất
có ác tính đã xác nhận bệnh học **trên da tối**, và chính bài báo gốc báo cáo *fine-tune trên DDI thu hẹp
khoảng cách sáng–tối*. Với `DynamicUndersampledSampler` 1:5 thì **số ca dương** mới là yếu tố quyết định,
không phải tổng số ảnh — nên 171 ca dương nằm cùng bậc độ lớn với đóng góp của PAD (377 ảnh / 180 ác tính
phía test, đã tạo ΔAUPRC +0,092…+0,131).

Đây là đường găng **thời gian**, không phải kỹ thuật. Việc thêm DDI vào train là **quyết định riêng, lớn hơn**:
nó buộc chạy lại `prepare` ⇒ chia lại splits ⇒ ma trận 140 fold cũ **không còn so sánh được**. Chỉ khởi động
khi (a) DUA về và (b) arm §2–§5 đã có kết luận. Khi làm: namespace `patient_id` thành `ddi_{id}`, nếu không
group trùng và rò rỉ qua fold.

**MIDAS — đã LOẠI** (2026-09-21, quyết định của tác giả): làm phình scope luận văn. Ghi lại giá trị đã mất
để khỏi phải tìm lại: MIDAS có ảnh lâm sàng của **cùng một tổn thương ở 15 cm và 30 cm**, tức một thí nghiệm
field-of-view **có đối chứng** — sạch hơn crop70. Nếu sau này mở scope thì đây là tập đánh giá đáng lấy,
**không phải** tập huấn luyện.

---

## 7. Rủi ro đã biết — phải nêu trong báo cáo, không giấu

1. **`efficientnetv2_m` là teacher yếu nhất xuyên miền** — mọi trận thua trên Fitzpatrick17k đều thuộc về nó.
   So sánh là paired **trong cùng teacher** nên Δ vẫn đọc được, nhưng trần thấp. Nếu arm ra null,
   **không tách được** "aug không giúp" khỏi "teacher này vốn yếu xuyên miền".
2. **`mobilenetv4_conv_medium` là student dung lượng thấp nhất** ⇒ nhạy nhất với thay đổi (RKD hại nó nặng nhất).
   Ở đây là điểm cộng: nếu có hiệu ứng, nó lộ ra ở đây trước. Nhưng fold-to-fold std của nó cũng lớn hơn.
3. **Trần kỳ vọng thấp** — crop70 chỉ thu hồi ~6% khoảng cách miền.
4. **`scale_limit: 0.5` chọn theo lập luận, không theo số đo.** Nếu arm âm thì phương án (b) — hai cường độ
   0,35 và 0,5, 30 fold-run — mới phân định được "hướng sai" khỏi "cường độ sai".
5. **Sàn nhiễu run-to-run ~0,005 AUPRC/fold** (`cudnn_deterministic=true` **không** bit-exact).
   Δ per-fold nhỏ hơn mức này **không** đọc là tín hiệu.

---

## 8. Quyết định mở

| # | Câu hỏi | Chờ ai |
|---|---|---|
| 1 | Nếu arm dương có ý nghĩa: mở rộng sang cặp ship (`maxvit_base → fastvit_sa12`) không? | Tác giả, sau khi có số |
| 2 | Nếu arm âm: chuyển sang phương án (b) hai cường độ, hay dừng và kết luận "cần thêm dữ liệu"? | Tác giả, sau khi có số |
| 3 | Arm này gắn vào câu hỏi nghiên cứu nào của luận văn? | Phụ thuộc việc chốt khung Q_A/Q_B/Q_C/Q_D (feedback GVHD 2026-09-21) |
| 4 | Calibration có đưa lại vào luận văn không? Nó bị gỡ 09/09 với lý do *"không Q nào trong Q1–Q6 hỏi về hiệu chuẩn"* — lý do đó mất hiệu lực nếu có một câu hỏi về "đòn bẩy tăng độ chính xác" | Tác giả |
