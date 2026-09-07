# Kế hoạch: Cổng phát hiện ảnh không hợp lệ (OOD gate) cho student deploy

> Tài liệu này trả lời: "khi đưa một ảnh **không phải tổn thương da** (con mèo, phong cảnh,
> ảnh mờ, ngón tay…) vào model thì làm sao để nó **từ chối** thay vì ép ra benign/malignant?".
> Mọi đường dẫn/def dưới đây đã **đối chiếu với code thực** (file:line) — không bịa API.
> **Trạng thái: PLANNED (chưa code).** Đây là doc thiết kế, viết trước khi implement.
> Ràng buộc bất biến: **post-hoc, opt-in, mặc định tắt** → không đụng một con số nào của Chapter 4.
> Doc hợp nhất **thiết kế + checklist review** (§4 bất biến-phải-soi, §8 quyết định mở, §9 checklist code) —
> đủ để nạp nhanh trong một session review độc lập, không cần đọc lại hội thoại.

---

## TL;DR

- **Vấn đề:** mọi model trong repo xuất **1 raw logit** → `sigmoid()` luôn cho ra một số trong `[0,1]`
  cho **bất kỳ** ảnh nào ([src/models/timm_backbone.py:37-39](../src/models/timm_backbone.py),
  [src/inference/predictor.py:50-53](../src/inference/predictor.py)). Không có lớp "unknown", không có
  phát hiện out-of-distribution (OOD). Đưa ảnh rác → model vẫn "tự tin" trả benign/malignant một cách vô nghĩa.
- **Không thể** dựa vào chính `prob` để biết ảnh lạ (kết quả kinh điển: mạng phân loại trả xác suất
  rất cao một cách sai lầm cho ảnh OOD — Nguyen 2015, Hendrycks & Gimpel 2017). Cần cơ chế **riêng**.
- **Giải pháp chọn (phương án 2):** cổng **khoảng cách Mahalanobis** trong không gian đặc trưng của
  backbone **đã train** (phương pháp gốc: **Lee et al. 2018, NeurIPS — "A Simple Unified Framework for
  Detecting Out-of-Distribution Samples and Adversarial Attacks"**). Tận dụng
  `BaseModel.forward_features(x) -> (feat, logit)` **đã có sẵn**
  ([src/models/base_model.py:15-27](../src/models/base_model.py)) — không sửa mô hình, không train lại.
- **Không cần dataset ảnh-lạ để build:** ngưỡng OOD calibrate trên tập **val** (in-distribution) theo
  tiêu chí "giữ lại `id_keep`% ảnh hợp lệ" (mặc định 95%). Chỉ cần ảnh-lạ khi muốn **đo AUROC** của cổng.
- **Chi phí *số* Chapter-4 = 0:** cổng chạy sau khi train xong, không đổi trọng số, không đổi
  loss/KD/metric. Ranking (pAUC/AUPRC/AUC) **bất biến**. Áp cho **student image-only** (cái sẽ deploy).
- **Vai trò scope (đã chốt): tính năng an toàn cho app (app-safety), KHÔNG phải đóng góp có số liệu.**
  → **§5 (mobile export 2-output) và §7 (đo AUROC cổng) là DEFERRED** — chỉ build lõi (§3.1–3.4) khi rảnh.
  "Cost = 0" chỉ nói về *số Chapter-4*, **không** nói về công sức code/viết. Con số "cổng bắt ảnh lạ tốt
  cỡ nào" (AUROC) **bắt buộc cần một tập ảnh-lạ**; chưa có tập đó thì vẫn build được cổng nhưng **không có
  số để viết vào luận văn**.

---

## 1. Vì sao phương án này (so với các hướng khác)

| # | Hướng | Cần train lại? | Cần ảnh-lạ để build? | Nặng deploy? | Đụng số Chapter 4? | Kết luận |
|---|-------|:--:|:--:|:--:|:--:|---|
| 1 | Chặn ở tầng app/UX (khung chụp, blur/brightness check) | Không | Không | Nhẹ | Không | 🟡 bổ sung, yếu — không chặn được "ảnh da nhưng không phải tổn thương" |
| 2 | **Mahalanobis / k-NN trên feature (post-hoc)** | **Không** | **Không** (chỉ cần để đo) | TB | **Không** | ✅ **chọn** |
| 3 | Classifier "lesion vs non-lesion" riêng đứng trước | Có (model mới) | **Có** | Nặng (2 model) | Không | 🟡 mạnh nhất nhưng scope creep + cần data |
| 4 | Thêm lớp "other/invalid" vào chính model | Có (toàn bộ) | Có | — | **CÓ — phá tính so sánh KD** | ❌ không |

**Mahalanobis (mặc định) vs k-NN:** Mahalanobis chỉ lưu `μ (C,)` + `Σ⁻¹ (C,C)` → gọn, hợp deploy;
k-NN phải lưu cả ngân hàng feature → nặng cho `.pte`. Có thể để k-NN làm option thứ 2 trong cùng lớp.

---

## 2. Cơ chế — quyết định 2 cửa nối tiếp

```
Ảnh ──► backbone ──► feature (B,C) ──► [Cửa 1: OOD gate]
                                            │
                          ood_score > threshold?  ──YES──► "invalid_input"  (DỪNG, không kết luận)
                                            │ NO
                              logit ──► sigmoid ──► prob ──► [Cửa 2: ngưỡng Youden như cũ]
                                                                 ├─ prob ≥ thr ─► "malignant"
                                                                 └─ prob < thr ─► "benign"
```

- **Cửa 1 chạy trước.** Ảnh bị coi là lạ → dừng, `prob` bên trong bỏ qua.
- `ood_score` = khoảng cách Mahalanobis, **KHÔNG** phải xác suất, không nằm trong `[0,1]`; chỉ so với `threshold`.
- Với ảnh **hợp lệ**, cửa 1 luôn "cho qua" → quyết định benign/malignant vẫn 100% do ngưỡng Youden như cũ
  → **mọi số liệu benign-vs-malignant không đổi.**

Ví dụ dict trả về (mở rộng của `Predictor.predict`):
```python
{"class": "benign",        "probability": 0.08, "ood_score": 12.3, "threshold": 0.31}  # lành tính
{"class": "malignant",     "probability": 0.91, "ood_score": 15.7, "threshold": 0.31}  # ác tính
{"class": "invalid_input", "probability": 0.63, "ood_score": 88.4, "threshold": 0.31}  # ảnh lạ
```

**Đánh đổi:** `id_keep=0.95` → ~5% ảnh da thật bị từ chối nhầm thành `invalid_input`. Tăng `id_keep=0.99`
→ ít từ chối nhầm hơn nhưng bắt ảnh lạ kém đi. Đây là núm người dùng tự chọn.

---

## 3. Thay đổi code (tất cả mới hoặc opt-in, mặc định tắt)

### 3.1 Mới — `src/inference/ood_gate.py` (lõi)
```python
class OODGate:
    """Cổng Mahalanobis hậu-xử-lý trên feature backbone. Fit CHỈ trên train fold."""
    def fit(self, feats, labels=None):        # feats (N,C) từ forward_features
        # labels=None -> 1 μ TOÀN CỤC: biến thể class-agnostic (đơn giản hoá bản
        # class-conditional per-lớp của Lee et al. 2018). Đủ cho "ID vs OOD" (2 lớp,
        # gọn, hợp deploy); per-class μ_c là option DEFERRED nếu cần bắt lạ tinh hơn.
        self.mu = feats.mean(0)
        self.prec = LedoitWolf().fit(feats).precision_    # Σ⁻¹ có shrinkage (khả nghịch khi C lớn)
    def score(self, feats):                   # -> khoảng cách Mahalanobis (N,)
        d = feats - self.mu
        return np.sqrt(np.einsum('ni,ij,nj->n', d, self.prec, d))
    def calibrate_threshold(self, val_feats, id_keep=0.95):
        self.threshold = np.quantile(self.score(val_feats), id_keep)
    def is_ood(self, feats): return self.score(feats) > self.threshold
    def save(self, path) / load(path)         # -> <run_dir>/ood_gate.npz (mu, prec, threshold, meta)
```

### 3.2 Mới — `scripts/fit_ood_gate.py` (chạy **1 lần / checkpoint**, trên server/GPU)
- Nạp `best_model.pth`, chạy `forward_features` qua **train fold** (transform `val`, **không augment**) → `fit`.
- Chạy qua **val fold** → `calibrate_threshold(id_keep)`. Ghi `<run_dir>/ood_gate.npz`.
- **Không backward, không sửa trọng số.** Dùng đúng CSV split đã có → chạy được trên checkpoint đã train xong.

### 3.3 Sửa opt-in — `src/inference/predictor.py`
Thêm tham số `ood_gate=None` cho `Predictor`. Trong `predict()`
([src/inference/predictor.py:38-59](../src/inference/predictor.py)): nếu có gate → lấy
`feat, _ = self.model.forward_features(tensor)`, tính `ood_score`, nếu `is_ood` thì `class="invalid_input"`.
**Mặc định `ood_gate=None` → hành vi cũ byte-for-byte không đổi.**

### 3.4 Sửa opt-in — `scripts/predict.py`
Thêm cờ `--ood-gate path/to/ood_gate.npz` (mặc định tắt) → nạp gate, truyền vào `Predictor`.

### 3.5 (Giai đoạn sau) Sửa opt-in — `scripts/export_executorch.py` → `.pte` 2-output
Xem §5 (triển khai biên). Chỉ làm khi thật sự chuẩn bị lên mobile.

**KHÔNG đụng:** `Evaluator`, `metrics.py`, `test_metrics.json`, loss/KD/trainer, `train_teacher.py`/`train_student.py`
(cố ý **không** nhét fit vào cuối train — giữ script rời để không coupling với job đang chạy), config mặc định.

---

## 4. Ràng buộc bất biến & gotcha — PHẢI soi khi review (từ luật repo)

- [ ] **Fit CHỈ trên train fold** — giống hệt luật của metadata scaler ("fit on train fold only",
  xem [docs/metadata_training_plan.md](metadata_training_plan.md)). Fit lẫn val/test = rò rỉ.
- [ ] Feature lấy bằng **transform `val`** (không aug), khớp lúc inference.
- [ ] **Chỉ gắn cho student image-only.** `forward_features` của privileged teacher
  ([src/models/privileged.py](../src/models/privileged.py)) có layout khác (nhận thêm meta/mask) → tránh.
- [ ] `Σ` cần **shrinkage (Ledoit-Wolf)** để khả nghịch khi `C` lớn (vd `C≈1280`). `sklearn` có sẵn trên cluster.
- [ ] **Chạy trên server/GPU**, không phải Mac (cần `forward_features` qua cả train fold). Verify tĩnh bằng
  `validate-pipeline`; đúng-sai thật sự kiểm trên cluster.
- [ ] `μ/Σ⁻¹` **riêng cho từng checkpoint** (đặc trưng của đúng không gian feature model đó) — không dùng
  chung giữa các student khác nhau.
- [ ] **Mặc định TẮT** (`ood_gate=None`) → hành vi cũ **byte-for-byte không đổi**; không config mặc định nào bật.
- [ ] **KHÔNG** nhét fit vào `train_student.py`/`train_teacher.py` — giữ script rời (job train có thể đang chạy).
- [ ] Không đụng `Evaluator`, `metrics.py`, `test_metrics.json`, loss/KD/trainer.

---

## 5. Triển khai lên thiết bị biên (ExecuTorch `.pte`) — DEFERRED

> **Giai đoạn sau, CHƯA làm** (quyết định scope: app-safety, defer mobile). Phần này là thiết kế
> tham khảo cho lúc thật sự lên mobile — không nằm trong đợt build lõi (§3.1–3.4).
> Phía app: [docs/ANDROID_APP_SPEC.md §5.2](ANDROID_APP_SPEC.md) đã đặc tả sẵn `OodGate` +
> trạng thái `INVALID_INPUT` sau một feature-flag (`ood.enabled=false`), nên khi có `.pte`
> 2-output thì chỉ cần đổi asset + config, không phải sửa luồng UI.

**Vấn đề:** `.pte` hiện chỉ xuất **1 output = logit** ([scripts/export_executorch.py:95-108](../scripts/export_executorch.py)).
Nhưng cổng cần **feature** nằm *bên trong* model. Trên Android không có Python/NumPy → phải quyết định cổng sống ở đâu.

**Cách A — nướng cổng vào graph (khuyến nghị).** Bọc model bằng wrapper mỏng, nhét `μ/Σ⁻¹` làm **buffer**,
export **wrapper** này:
```python
class GatedModel(nn.Module):
    def __init__(self, base, mu, precision):
        self.base = base
        self.register_buffer("mu", mu)              # -> đông cứng vào .pte
        self.register_buffer("precision", precision)
    def forward(self, x):
        feat, logit = self.base.forward_features(x)
        d = feat - self.mu
        ood = torch.sqrt((d @ self.precision * d).sum(-1))   # Mahalanobis
        return logit, ood                            # .pte 2-output
```
→ `.pte` xuất `(logit, ood_score)`, `μ/Σ⁻¹` đông cứng trong file. **App không làm toán ma trận**, chỉ so 2 ngưỡng.

**Luồng trên điện thoại** (đọc `.bin`→tensor: [docs/MOBILE.md §4.3](MOBILE.md); parity: [§4.5](MOBILE.md)):
```
Camera ─► resize/normalize (khớp transform 'val') ─► .pte ─► (logit, ood_score)
   ood_score > OOD_THRESHOLD?  → "Ảnh không hợp lệ"
   else sigmoid(logit) ≥ YOUDEN_THRESHOLD? → "Ác tính" | "Lành tính"
```
- **2 ngưỡng chỉ là 2 số float** ship trong app config → chỉnh được **không cần export lại** `.pte`.
- **Chi phí:** `Σ⁻¹` là `C×C` → với `C≈1280` thêm ~**6.5 MB** float32 vào `.pte`. Núm giảm: hiệp phương sai
  **đường chéo** (chỉ `C` phương sai, vài KB, yếu hơn) hoặc PCA giảm chiều. Tính toán thêm = 1 matvec `C×C` → không đáng kể.
- **⚠️ Rủi ro parity float32 (đáng lưu ý nhất của nhánh này):** threshold được calibrate ở **float64**
  (numpy/`LedoitWolf` trên server), nhưng `ood_score` chạy ở **float32** trong `.pte`. Dạng toàn phương
  **~1280 chiều** (`d·Σ⁻¹·dᵀ`) dễ tích luỹ sai số → giá trị `ood_score` trôi nhẹ → **ranh giới invalid/valid
  có thể lệch** dù `logit` khớp. Giảm thiểu: **mặc định cov đường chéo cho bản mobile** (vừa cắt 6.5 MB→vài KB,
  vừa ổn định số hơn) hoặc cộng một **margin** vào threshold; và **bắt buộc** đo parity `|Δood|` (dưới) trước
  khi tin bất kỳ quyết định "invalid" nào.
- **Parity:** [scripts/export_executorch.py:120-124](../scripts/export_executorch.py) **không phải assert
  tự động** — đó là `logger.info` *hướng dẫn dev tự parity trong app Android* (`max|Δlogit| < 1e-3`, tương ứng
  [docs/MOBILE.md §4.5](MOBILE.md)). Mở rộng **hướng dẫn** đó sang cả `ood_score`. Cách A dùng chung graph nên
  `logit` parity gần như tự nhiên đạt; nhưng `ood_score` vẫn phải đo riêng vì rủi ro float32 ở trên.

**Cách B — sidecar** (export feature thô + tính Mahalanobis bằng Kotlin): dễ lệch số, nhiều code app → **không khuyến nghị** cho luận văn.

---

## 6. Áp dụng vào student đang/đã train

Vì cổng là **post-hoc**, việc student đang train **không cản trở**:
- Code mới (§3.1–3.4) là file mới/opt-in → job train **không import** → thêm vào lúc này không đụng job đang chạy.
- Chỉ cần **1 `best_model.pth` đã xong** để chạy `fit_ood_gate.py` (fold nào xong trước thử fold đó, không đợi đủ 5 fold).
- **Không dừng job, không train lại, không sửa** `train_student.py`/config đang chạy.

| Bước | Ở đâu | Sửa trọng số? |
|---|---|:--:|
| Viết code gate (§3.1–3.4) + `validate-pipeline` | Mac (chỉ sửa code) | — |
| `fit_ood_gate.py` → `μ/Σ⁻¹` + ngưỡng | server/GPU, **1 lần/checkpoint**, vài phút | **Không** |
| (giai đoạn sau) export `GatedModel` → `.pte` 2-output | server | **Không** |
| Chạy `.pte` + so 2 ngưỡng | mobile (không có wrapper, chỉ đọc output) | **Không** |

---

## 7. Kiểm chứng

- **Tĩnh (Mac):** `validate-pipeline` sau khi thêm code; `review-training` cho phần inference nếu chạm trainer path (không nên chạm).
- **Server:** log `fit_ood_gate.py` phải báo `ID-retention ≈ id_keep` trên val + `threshold`.
- **Nếu có ảnh-lạ:** đo **AUROC (ID vs OOD)** của cổng — con số để viết vào luận văn ("cổng bắt ảnh lạ tốt cỡ nào").
  Chưa có ảnh-lạ vẫn chạy được, chỉ thiếu con số này.
- **Biên:** parity `|Δood|` nhỏ giữa server và `.pte` trước khi tin bất kỳ quyết định "invalid" nào.

---

## 8. Tham số mở (chốt trước khi code)

| # | Câu hỏi | Mặc định đề xuất | Ghi chú |
|---|---------|------------------|---------|
| Q1 | Checkpoint đầu tiên nhắm tới? | `mobilenetv4_conv_medium` (bản KD tốt nhất) | Gate là **per-checkpoint** (μ/Σ⁻¹ riêng từng feature space). Mobile đã defer + thường chỉ **1 student** lên máy → chỉ checkpoint đó cần cổng, không fit cả 4 student |
| Q2 | `id_keep` (tỉ lệ giữ ảnh hợp lệ)? | `0.95` (từ chối nhầm ~5% ảnh thật) | `0.99` → ít từ chối nhầm hơn, bắt ảnh lạ kém hơn |
| Q3 | Distance? | Mahalanobis | Có thêm k-NN làm option thứ 2 không? (k-NN nặng hơn cho `.pte`) |
| Q4 | Có ảnh-lạ để đo AUROC cổng không? | **DEFERRED** (scope app-safety) | Đo AUROC = hạng mục để sau; build cổng KHÔNG phụ thuộc nó |

---

## 9. Checklist review (tick khi soi code sau này)

- [ ] `OODGate.fit` chỉ nhận feature từ **train fold**, transform `val`?
- [ ] `calibrate_threshold` dùng **val fold**, đúng `id_keep`?
- [ ] `Predictor` mặc định `ood_gate=None` → path cũ không đổi?
- [ ] Không import/đụng trainer, evaluator, metrics?
- [ ] `fit_ood_gate.py` không có backward, không sửa/ghi đè checkpoint?
- [ ] (export, DEFERRED) `.pte` 2-output; parity `|Δlogit|` **và** `|Δood|` đều nhỏ?
- [ ] `validate-pipeline` pass; đúng-sai thật kiểm trên cluster (Mac chỉ static-check)?
