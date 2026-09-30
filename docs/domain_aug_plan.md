# Kế hoạch: Arm tăng cường nhắm miền (`augmentation=domain`)

> Tài liệu này trả lời: *"mô hình sụp khi đổi miền ảnh — huấn luyện lại với tăng cường
> nhắm đúng nguyên nhân đã chẩn đoán thì thu hồi được bao nhiêu?"*
>
> # 🔴 KẾT QUẢ: THẤT BẠI — KHÔNG DÙNG, KHÔNG ÁP DỤNG
>
> **Arm đã chạy xong đủ 30 fold-run + đánh giá 3 tầng (24/09). Câu trả lời: thu hồi được 0,
> và làm hại mô hình.** `augmentation=domain` **không được dùng cho bất kỳ run nào về sau**;
> **30/09/2026: preset `configs/augmentation/domain.yaml` và builder `RandomGamma` đã bị GỠ
> khỏi code** (chỉ giữ code cho kết quả tốt). Muốn tái lập kết quả âm này thì lấy lại từ
> commit `0c308b5`. Phần DDI (§6) giữ nguyên — đó là arm thành công.
>
> Bằng chứng quyết định — **student KD (mô hình sẽ đem triển khai) xấu đi có ý nghĩa ở 5/5 ô
> đánh giá**, paired CI loại trừ 0 ở cả năm (ΔAUPRC, domain − light):
> HAM10000 −0,0195 · Fitz headline −0,0436 · Fitz crop70 −0,0515 · Fitz crop50 −0,0564 ·
> Fitz with_non_neoplastic −0,0395. In-domain cũng âm (−0,0811 AUPRC, không có CI).
> Teacher và baseline thì lẫn lộn hai chiều tuỳ biến thể, chỉ riêng KD là nhất quán âm.
>
> Không quy được kết quả âm cho riêng trục nào: arm đổi **hai trục cùng lúc** (hình học là
> trục chính, màu là phụ) nên nó **không** phải phép thử cho giả thuyết "chỉnh màu ảnh train".
> Kết luận theo đúng điều đã đăng ký trước ở TL;DR: *bài toán cần thêm **dữ liệu** thật,
> không cần thêm kỹ thuật tăng cường* → xem §6 (DDI).
>
> Số liệu đầy đủ: `reports/ci_newsplit_{ham10000_headline,fitzpatrick17k_*}.md`,
> `reports/external_newsplit_{light,domain}/`, `experiments/runs_newsplit_{light,domain}/`.
>
> # ✅ VIỆC 4 (DDI) NGƯỢC LẠI: THÀNH CÔNG
>
> **Cũng chính kết luận "cần thêm DỮ LIỆU, không cần thêm kỹ thuật" đã được kiểm chứng và ĐÚNG.**
> Arm DDI xong 26/09 (15/15 fold-run + 3 tầng đánh giá + paired CI 6 ô): student KD **tốt lên
> có ý nghĩa ở 5/5 ô** trên AUPRC — đúng phản chiếu của arm `domain`. Chi tiết ở §6.
>
> **Trạng thái các việc: Việc 1 ✅ (21/09) · Việc 2 ✅ (23/09) · Việc 3 ✅ (24/09) · Việc 4 ✅ (26/09).**
> **Còn tồn:** 4 việc tài liệu/runner ở **§9** + 3 quyết định mở ở **§8** (chờ tác giả).
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
  **ánh sáng/cân bằng trắng** — rồi train lại ~~15~~ **30 fold-run** trên cặp nhanh nhất và so paired CI
  với nhánh `light` ~~đã có~~ **train lại trên splits mới** (xem ràng buộc 22/09 ở đầu tài liệu).
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

## 2. Việc 1 — Mac, không GPU, không phụ thuộc ai ✅ XONG 21/09

| # | File | Thay đổi | Xong |
|---|---|---|:--:|
| 1.1 | `configs/augmentation/domain.yaml` | **Tạo mới** — bảng op ở §3 | ✅ |
| 1.2 | `run/train_teacher.sh` | Docstring `AUG light \| heavy` → `light \| heavy \| domain` | ✅ |
| 1.3 | `run/train_student.sh` | Y như trên | ✅ |
| 1.4 | `run/README.md` | Ghi nhận biến thể thứ ba + lý do thiết kế | ✅ |
| 1.5 | `docs/PREPROCESSING.md §4.1–4.2` | Bổ sung `domain` vào mô tả aug config-driven | ✅ |
| 1.6 | — | Chạy **`validate-pipeline`** (AST + Hydra compose + runner lint) | ✅ |
| 1.7 | `MEMORY.md` + memory file | Ghi arm mới | ✅ |

**XONG 2026-09-21** (commit `0c308b5`). Đính chính: Việc 1 **CÓ** phải sửa `src/` — xem đính chính ở §3
(`_TRANSFORM_BUILDERS` là allowlist, `RandomGamma` phải thêm builder). Không cần entry mới trong
`MODEL_REGISTRY`, không cần config teacher mới — xem §4 vì sao.

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

## 4. Việc 2 — Server, ~~15~~ 30 fold-run ✅ XONG 23/09

~~Cả arm ghi vào `experiments/runs_aug_domain/`~~ — **tên cây đã ĐỔI khi thi công.** Hai nhánh thực tế
là `experiments/runs_newsplit_light/` và `experiments/runs_newsplit_domain/` (xem khối cây ở dưới):
tiền tố `newsplit_` để nói rõ chúng nằm trên splits gom-theo-bệnh-nhân sinh lại 22/09, **không**
so sánh được với ma trận 140 fold cũ. Theo tiền lệ `experiments/runs_isic_only/`.

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
```

⚠️ **HAI nhánh ⇒ HAI `output_dir`, bắt buộc.** `train_teacher.py` hardwire
`<output_dir>/teacher/<name>/fold_N` và **không đọc `AUG`** — để chung một `output_dir` thì
teacher `domain` **ghi đè** teacher `light`, mất luôn đối chứng.

```
experiments/runs_newsplit_light/     ← AUG=light   (đối chứng, phải train lại)
experiments/runs_newsplit_domain/    ← AUG=domain
```

Driver chạy tuần tự cả 6 bước: `.tmp/arm_driver.sh` (tmux `newsplit_arm`). Thứ tự được xếp để
**sau hai baseline đã có một so sánh light-vs-domain hợp lệ**, không phải đợi hết 30 fold:

| # | Job | Cây |
|---|---|---|
| 1 | teacher `light` | `runs_newsplit_light` |
| 2 | teacher `domain` | `runs_newsplit_domain` |
| 3 | baseline student `light` | `runs_newsplit_light` |
| 4 | baseline student `domain` | `runs_newsplit_domain` |
| 5 | KD student `light` (sau 1) | `runs_newsplit_light` |
| 6 | KD student `domain` (sau 2) | `runs_newsplit_domain` |

**Một GPU ⇒ chạy tuần tự.** CLAUDE.md đã đo: một job KD đã bão hoà card, thêm job chỉ thêm rủi ro OOM.
Theo dõi: `OUTPUT_DIR_DEFAULT=experiments/runs_newsplit_light bash run/progress.sh`.
Kéo về Mac: `bash run/pull_results.sh pull` — ~~hai cây mới chưa nằm trong `ROOTS` mặc định~~ **đã
thêm** từ commit `e7d6486` ([run/pull_results.sh:95](../run/pull_results.sh)); nhưng cây thứ ba
`runs_newsplit_ddi` thì **vẫn chưa** — xem §9.1.

| ☑ | Bước (30 fold-run) — **TẤT CẢ XONG 23/09** |
|:--:|---|
| ✅ | 2.1 Teacher × 2 nhánh (light + domain), 5 fold mỗi nhánh |
| ✅ | 2.2 Baseline student × 2 nhánh, 5 fold mỗi nhánh |
| ✅ | 2.3 KD student × 2 nhánh, 5 fold mỗi nhánh |
| ✅ | 2.4 `aggregate.sh` × **6** run-dir |
| ✅ | 2.5 `pull_results.sh pull` — 30 fold về Mac. `ROOTS` **đã** có hai cây mới từ commit `e7d6486`, không phải sửa |

---

## 5. Việc 3 — Đánh giá ✅ XONG 24/09

| ☑ | Tầng | Cách | Xong |
|:--:|---|---|:--:|
| ✅ | In-domain | `test_metrics.json` tự sinh khi train xong | 23/09 |
| ✅ | Cross-domain | `run/evaluate_external.sh DATASET=ham10000` | 24/09 |
| ✅ | Công bằng theo tông da | `run/evaluate_external.sh DATASET=fitzpatrick17k VARIANTS=all` | 24/09 |
| ✅ | **Paired CI** | `run/bootstrap_ci.sh`, đủ **5/5 ô** (HAM headline + Fitz × 4 biến thể) | 24/09 |

⚠️ **HAI bẫy đã bật ra khi thi công, phải nhớ nếu làm arm tương tự:**
1. **`evaluate_external.py:319` khoá cứng `runs_root = Path("experiments/runs")`.** Run-dir nằm ngoài
   cây đó rơi về `run_tag = run_dir.name` ⇒ hai nhánh `runs_newsplit_{light,domain}` **và** cả run cũ
   cùng tên **ghi đè nhau trong im lặng**. Bắt buộc truyền `--out-root` riêng cho từng nhánh
   (`reports/external_newsplit_{light,domain}/`).
2. **Auto-pairing `__<suffix>` ở §3 của `bootstrap_ci.py` KHÔNG kích hoạt** với tên có tiền tố `x_`:
   nó còn đòi khớp "kind" đã parse (`scripts/bootstrap_ci.py:452`). Dùng cờ **`PAIR="A:B"`** tường minh
   (quy ước ở đây: `domain − light`, dương = aug giúp).

⚠️ **Đối chứng đã ĐỔI (22/09):** so sánh giờ là `runs_newsplit_light` vs `runs_newsplit_domain` —
**không** còn so với ma trận 140 fold cũ (splits khác, và splits cũ rò rỉ bệnh nhân).

⚠️ **Bẫy phải xử lý:** `bootstrap_ci.sh` §3 chỉ tự ghép cặp `__<suffix>` với run cùng tên không suffix
**trong cùng một `RESULTS_DIR`**. Hai nhánh nằm ở hai tree khác và **trùng tên** ⇒ auto-pairing **không kích hoạt**.
Cách đúng đã có tiền lệ: `reports/framing_crop_ci19.md` được sinh từ `.tmp/framing_ci19` với run-dir
**đổi tên** (`x_baseline_..._crop70`). Làm y vậy — symlink hai nhánh vào một tree tạm, đặt tên
`..._light` / `..._aug_domain`, rồi chạy CI trên tree đó. Script chỉ đọc `fold_*/predictions.csv`.

**Ô quyết định:** ΔAUPRC và ΔSens@90Spec **trên HAM10000 và Fitzpatrick17k**, **paired**.
In-domain chỉ dùng để kiểm *"aug mới có làm hại miền gốc không"* — tập test mới có **265 ca dương
trên 59.093 ảnh** (`CLAUDE.md:258`), vốn thiếu lực. *(Bản trước ghi "241 ca dương / 62.040 ảnh" —
đó là số của splits CŨ đã rò rỉ bệnh nhân, đã sửa 24/09.)*

**Một cảnh báo khi đọc kết quả:** phát hiện *"da tối bị hại nặng nhất"* **không vững qua các biến thể**
— đúng rõ ở `headline` (cả 3 model) và `crop50` (baseline, KD), nhưng ở `with_non_neoplastic` thì
nhóm light của KD còn bị hại nặng hơn dark, và ở `crop70` nhóm dark của teacher không phân định được.
Chỉ phát biểu kèm tên biến thể, không tổng quát hoá.

---

## 6. Việc 4 — DDI ✅ XONG 26/09 — và **THÀNH CÔNG**

| ☑ | Bước | Xong |
|:--:|---|:--:|
| ✅ | Lấy **DDI** (Diverse Dermatology Images, Stanford) — 656 ảnh | 25/09 |
| ✅ | Nạp vào TRAIN side: `bash run/prepare_ddi.sh` | 25/09 |
| ✅ | Train arm DDI — **15/15 fold-run** (tmux `ddiarm`, khởi động 25/09 12:03, fold cuối ghi 26/09 04:23) | 26/09 |
| ✅ | `aggregate.sh` × 3 run-dir (`teacher` · `baseline` · `kd`) | 26/09 |
| ✅ | Eval ngoài đủ **5 ô** — `reports/external_newsplit_ddi/{ham10000/headline, fitzpatrick17k/{headline,crop70,crop50,with_non_neoplastic}}`, mỗi ô 3 model | 26/09 |
| ✅ | Paired CI **6 file** `reports/ci_ddi_*.md` (5 ô ngoài + in-domain) | 26/09 |
| ☐ | Viết kết quả thành **báo cáo** + cập nhật `CLAUDE.md`/`PREPROCESSING.md` + `pull_results.sh` (memory ✅ 26/09) | **xem §9** |

### 6a. Kết quả (26/09) — ngược hẳn arm `domain`

Quy ước: Δ = `x_*__ddi − x_*`, đối chứng là nhánh **`light`** (`runs_newsplit_light`), dương = DDI giúp.
`*` = CI 95% loại trừ 0. Nguồn: mục **3b** của 6 file `reports/ci_ddi_*.md`.

| Ô đánh giá | ΔAUPRC student KD | ΔAUPRC teacher | ΔAUPRC baseline |
|---|---|---|---|
| HAM10000 headline | **+0,0863 [+0,0737, +0,0979]** \* | +0,0391 \* | +0,0154 \* |
| Fitzpatrick17k headline | **+0,0400 [+0,0332, +0,0467]** \* | +0,0233 \* | +0,0241 \* |
| Fitz crop70 | **+0,0317** \* | +0,0206 \* | +0,0106 \* |
| Fitz crop50 | **+0,0179** \* | +0,0098 \* | +0,0070 |
| Fitz with_non_neoplastic | **+0,0434** \* | +0,0175 \* | +0,0253 \* |
| In-domain | **+0,0246 [+0,0060, +0,0425]** \* | +0,0024 | +0,0041 |

- **Student KD dương có ý nghĩa 5/5 ô ngoài** — **phản chiếu chính xác** arm `domain` (âm 5/5 ô).
  Trên HAM10000 KD dương có ý nghĩa **cả 4 metric**, Sens@90%Spec **+0,1038 [+0,0875, +0,1190]** \*.
- **Nhóm da tối** (Fitz headline, per-`tone_group`): KD ΔAUPRC **+0,0473 [+0,0276, +0,0672]** \*,
  ΔAUC +0,0360 \* — tức 656 ảnh (171 ca dương) làm được cái mà tăng cường không làm được.
- **Phải nêu, không giấu:** pAUC của **teacher** âm có ý nghĩa ở nhiều biến thể
  (crop70 −0,0027 \* · crop50 −0,0032 \* · with_non_neoplastic −0,0087 \* · in-domain −0,0029 \*),
  và baseline ở crop50 nhóm dark Sens@90%Spec −0,0519 \*. Kết luận dương thuộc **student KD**,
  không phải "mọi model đều tốt lên".
- In-domain: ΔAUC của KD là −0,0000 (không phân định) nhưng **ΔAUPRC dương có ý nghĩa** — và AUPRC
  mới là headline ở prevalence 0,39% (`CLAUDE.md`, mục Evaluation). Không đọc ô này qua AUC.

⚠️ **Chưa verify được trên Mac:** các số liệu nạp ở §6b (656 dòng append vào mỗi `train_split.csv`,
test/val giữ byte-for-byte) chỉ kiểm được trên server — Mac không có `data/splits/fold_*` lẫn
`data/processed/ddi/`, chỉ có backup `reports/_ddi_backup/20260925_120233/` (bản **trước** khi append).

### 6b. Cách thi công

**ĐÃ THỰC HIỆN 2026-09-25 — và KHÁC kế hoạch ban đầu ở một điểm quan trọng.**
Kế hoạch viết *"thêm DDI buộc chạy lại `prepare` ⇒ chia lại splits ⇒ ma trận cũ không còn so
sánh được"*. Cách đó **không dùng được**: CLAUDE.md cấm re-run `prepare` (ISIC HDF5 + PAD raw đã
mất, fast-path `dst.exists()` sẽ `unlink()` vĩnh viễn ảnh processed), và nó còn vô hiệu hoá luôn
30 fold-run vừa train xong.

Cách đã làm thay thế — `scripts/prepare_ddi.py` + `run/prepare_ddi.sh`:
- Xử lý DDI vào cây RIÊNG `data/processed/ddi/` (không đọc/ghi gì của ISIC/PAD ⇒ không thể phá).
- **APPEND** 656 dòng vào mỗi `fold_*/train_split.csv`. `test_split.csv` và cả 5 `val_split.csv`
  **giữ nguyên byte-for-byte** (đã kiểm: test 59.093 dòng / 0 DDI; mỗi val 0 DDI; mỗi train đúng 656 DDI).
- ⇒ `experiments/runs_newsplit_light` **vẫn là đối chứng ghép cặp hợp lệ** ⇒ chi phí **15 fold-run
  thay vì 30**. Arm DDI ghi vào `experiments/runs_newsplit_ddi/` (dùng `output_dir=`, `AUG=light`
  để khác biệt duy nhất là 656 dòng DDI).

Số liệu nạp: 656 ảnh · 171 ác tính / 485 lành · FST 12/34/56 = 208/241/207 · **0 ảnh bị loại**
(0 integrity failure, 0 flagged uninformative) · positives mỗi fold **+17,3% đến +18,9%**
(fold_0: 906 → 1.077). Backup CSV gốc: `reports/_ddi_backup/<ts>/`.

**Hai hệ quả phải nêu khi báo cáo:** (a) DDI **không bao giờ được chấm điểm** — đóng góp của nó đo
gián tiếp trên tập test in-domain không đổi và trên nhóm tông da của Fitzpatrick17k; (b) `patient_id`
của DDI là **một nhóm mỗi ảnh** (release không có cột bệnh nhân), chấp nhận được **chỉ vì** DDI
không bao giờ vào val/test. Muốn đưa DDI vào tập đánh giá thì phải sinh lại splits + train lại
đối chứng — một việc khác.

**Vì sao DDI:** 656 ảnh / 570 bệnh nhân, **171 ác tính / 485 lành**, FST **cân bằng có chủ đích**
(I-II 208 · III-IV 241 · V-VI 207), non-commercial research use — **cho phép huấn luyện**. Là bộ duy nhất
có ác tính đã xác nhận bệnh học **trên da tối**, và chính bài báo gốc báo cáo *fine-tune trên DDI thu hẹp
khoảng cách sáng–tối*. Với `DynamicUndersampledSampler` 1:5 thì **số ca dương** mới là yếu tố quyết định,
không phải tổng số ảnh — nên 171 ca dương nằm cùng bậc độ lớn với đóng góp của PAD (377 ảnh / 180 ác tính
phía test, đã tạo ΔAUPRC +0,092…+0,131).

~~Đây là đường găng **thời gian**, không phải kỹ thuật. Việc thêm DDI vào train là **quyết định riêng,
lớn hơn**: nó buộc chạy lại `prepare` ⇒ chia lại splits ⇒ ma trận 140 fold cũ **không còn so sánh được**.
Chỉ khởi động khi (a) DUA về và (b) arm §2–§5 đã có kết luận.~~
→ **ĐOẠN NÀY ĐÃ VÔ HIỆU (25/09), giữ lại để thấy kế hoạch đã sai ở đâu.** Nó nói ngược hẳn §6b ngay
phía trên: `prepare` **không** phải chạy lại, splits **không** bị chia lại, `runs_newsplit_light` **vẫn**
là đối chứng hợp lệ, và chi phí là 15 chứ không phải 30 fold-run. Phần duy nhất còn hiệu lực:
**namespace `patient_id` thành `ddi_{id}`**, nếu không group trùng và rò rỉ qua fold — đã làm.

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
| ~~1~~ | ~~Nếu arm dương: mở rộng sang cặp ship?~~ — **ĐÓNG (24/09): arm âm, không mở rộng** | — |
| **2** | **Arm âm rồi: chạy phương án (b) hai cường độ (thêm 30 fold-run), hay dừng hẳn?** ⇒ khuyến nghị **dừng**, và kết quả DDI ở §6a **củng cố thêm**: cùng một câu hỏi ("thu hẹp khoảng cách miền") đã có lời đáp dương bằng **dữ liệu**, nên 30 fold-run tăng cường nữa là chi phí đặt sai chỗ | **Tác giả — đang chờ** |
| 3 | Arm này gắn vào câu hỏi nghiên cứu nào của luận văn? Giờ là **một cặp đối chứng**: `domain` (âm) vs DDI (dương) trả lời cùng một câu hỏi bằng hai đường — đáng vào luận văn như một mục chung | Phụ thuộc việc chốt khung Q_A/Q_B/Q_C/Q_D (feedback GVHD 2026-09-21) |
| 4 | Calibration có đưa lại vào luận văn không? Nó bị gỡ 09/09 với lý do *"không Q nào trong Q1–Q6 hỏi về hiệu chuẩn"* — lý do đó mất hiệu lực nếu có một câu hỏi về "đòn bẩy tăng độ chính xác" | Tác giả |
| **5** | **MỚI (26/09) — DDI dương rồi: có mở rộng sang cặp ship (`maxvit_base → fastvit_sa12`) và/hoặc 4 student không?** Hiện chỉ đo trên một cặp `efficientnetv2_m → mobilenetv4_conv_medium`, tức **teacher yếu nhất xuyên miền** (§7.1) — trần có thể còn cao hơn. Chi phí: 10 fold-run/cặp (đối chứng `light` đã có) | **Tác giả** |

---

## 9. Việc còn tồn (26/09) — không phải GPU, là tài liệu + runner

Bốn việc dưới đây là lý do tài liệu này **chưa** đóng được, dù cả 4 Việc đã xong phần thí nghiệm.
Bằng chứng đều kiểm được trên Mac.

| # | Việc | Bằng chứng còn thiếu |
|:--:|---|---|
| 9.1 | Thêm `experiments/runs_newsplit_ddi` vào `ROOTS` của `pull_results.sh` | [run/pull_results.sh:95](../run/pull_results.sh) chỉ có `runs`, `runs_isic_only`, `runs_newsplit_light`, `runs_newsplit_domain` ⇒ `/pull-results` **vô hình** với arm DDI. Đúng loại desync runner↔code mà bước 3 quy trình CLAUDE.md nhắm tới |
| 9.2 | `CLAUDE.md` — khối "Data integrity" chưa nói mỗi `fold_*/train_split.csv` giờ có thêm 656 dòng DDI | `grep -c DDI CLAUDE.md` = **0**. Người đọc sau sẽ trích sai population/positive count của tập train |
| 9.3 | `docs/PREPROCESSING.md` — chưa có mục nào về nguồn train **thứ ba** | `grep -c DDI docs/PREPROCESSING.md` = **0** |
| 9.4 | Viết kết quả DDI thành **báo cáo** (`reports/`) — memory ✅ đã ghi 26/09 (`project_ddi_arm_result`) | Ngoài 6 file `reports/ci_ddi_*.md` (artifact thô) thì **không** file `reports/*.md` nào báo cáo arm DDI |

**Đã xong, không cần làm lại:** [run/README.md:44](../run/README.md) và [:131-143](../run/README.md)
đã tài liệu hoá `prepare_ddi.sh` đầy đủ (kèm hai hệ quả "DDI never scored on" + `patient_id` một
nhóm mỗi ảnh) ⇒ runner↔README **không** desync.

**Một nghĩa khác của "xong" mà tài liệu này không quyết:** `scripts/prepare_ddi.py` và
`run/prepare_ddi.sh` hiện còn **untracked** trong git (`??`). Theo CLAUDE.md chỉ commit khi tác giả
yêu cầu, nên đây **không** phải lỗi — chỉ ghi ra để không ai tưởng arm DDI đã vào lịch sử repo.
