# IMPLEMENTATION SPEC — thay đổi CODE còn tồn từ KD audit

> **Ngày:** 2026-07-15
> **Nguồn:** phát sinh từ `docs/KD_DESIGN_REVIEW_2026-07-13.md` (đợt audit KD 2026-07-14/15).
> **Mục đích:** đặc tả **chính xác, đủ để implement không lỗi** cho các thay đổi CODE còn tồn. File
> này dành cho một session sau: đọc → code theo từng bước → verify.
> **Trạng thái mỗi mục:** ✅ CODE đã ship (2026-07-15) — verify lại 2026-07-16 vs code thực tế. Phần còn
> tồn duy nhất = **chạy thật 5-fold trên server + điền kết quả** (chưa làm).
> **Đã đối chiếu code hiện tại** (file:line bên dưới đã verify tại thời điểm viết — nếu code đã đổi,
> kiểm lại trước khi sửa).

---

## 0. Nguyên tắc chung (đọc trước khi code)

- **Runtime = server SSH, không phải Mac.** Mac chỉ để sửa + `python -m py_compile` + `validate-pipeline`
  (static). Không `pip install`, không chạy training trên Mac. Xem `CLAUDE.md` §"Local environment ≠ runtime".
- **Modification-workflow (bắt buộc):** sau khi sửa `src/**` → chạy skill **review-training**
  (cho `src/training/**`, `src/models/**`) rồi **validate-pipeline**; nếu đổi cách job chạy/tiêu thụ/xuất →
  cập nhật `run/*.sh` + docs cùng lúc; correctness thật = **poc-smoke-test** trên server (Mac không train được).
- **Back-compat là ràng buộc cứng:** mọi thay đổi phải **mặc định giữ nguyên hành vi cũ** (các run KD/baseline
  chính không được đổi kết quả). Bật tính năng mới qua config opt-in.
- **Gotcha trainer (đã cắn repo này):** mọi key khai trong `self.history = {...}` PHẢI được `.append()` mỗi
  epoch, nếu không `plot_training_curves` shape-mismatch (`kd_trainer.py`).
- **2 alpha khác nhau — đừng nhầm:** `training.loss.alpha` (=0.25) = trọng số lớp dương của **focal loss**;
  `training.distillation.alpha` (=0.3) = tỉ lệ **hard vs soft** trong KD. Hai cái độc lập.

**Không thuộc file này (config-only, KHÔNG cần code):** ablation focal-α (`training.loss.alpha=0.75`),
DHKD KD-only (`training.distillation.alpha=0.0`), focal-only (= chạy `TRAINING=baseline` đã có), temperature
sweep (`training.distillation.temperature=...`). Tất cả chạy qua `run/train_student.sh` với
`EXTRA="<override> run_suffix=__<tag>"` → xem §4.

---

## 1. Change 1 — Calibration add-on  ✅ CODE DONE (chạy offline trên server: pending)

**Vì sao:** model học trên prior đã undersample (~16,7% malignant) chứ không phải prevalence thật ~0,39%
→ `sigmoid(logit)` hiển thị bị thổi phồng. Các metric ranking (pAUC/AUPRC/sens@spec) **miễn nhiễm**, nên
**không** ảnh hưởng số Chương 4; đây là bước cần **nếu** hiển thị "xác suất %" cho người dùng + là mục
Chương 4 rẻ mà ấn tượng (reliability curve + ECE/Brier). Rủi ro thấp (offline-first, không đụng trainer).

### 1a. Thêm ECE + Brier vào `src/evaluation/metrics.py`
Seam: `compute_metrics()` trả 1 dict, **chèn ngay trước `return`** (hiện dict điền tới ~dòng 180, các key
`tp/fp/tn/fn`). numpy + sklearn **đã import sẵn** ở đầu file.

Thêm 2 hàm module-level:
```python
def brier_score(y_true, y_prob) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    return float(np.mean((y_prob - y_true) ** 2))

def expected_calibration_error(y_true, y_prob, n_bins: int = 15) -> float:
    """Equal-width-bin ECE = sum_b (|B_b|/N) * |acc_b - conf_b|."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.digitize(y_prob, bins[1:-1])          # bin index per sample
    ece = 0.0
    n = len(y_prob)
    for b in range(n_bins):
        m = idx == b
        if not np.any(m):
            continue
        conf = float(np.mean(y_prob[m]))
        acc = float(np.mean(y_true[m]))
        ece += (np.sum(m) / n) * abs(acc - conf)
    return float(ece)
```
Trong `compute_metrics()`, ngay trước `return metrics` thêm:
```python
metrics["brier"] = brier_score(y_true, y_prob)
metrics["ece"] = expected_calibration_error(y_true, y_prob)
```
→ tự chảy vào `test_metrics.json` (qua `Evaluator.save_metrics`) và `val_metrics.json` (qua trainer).
Đây là ECE/Brier **RAW (chưa calibrate)** — đo mức miscalibration hiện có. **Không** thêm vào
`predictions.csv` (đó là CSV y_true/y_prob/y_pred/source).

### 1b. Script offline `scripts/compute_calibration.py` (MỚI) — prior-correction
Mô phỏng style discovery của `scripts/compare_kd_results.py` (quét cây `fold_*`). Đọc
`<run_dir>/fold_*/predictions.csv` (cột `y_true,y_prob`). Áp **prior-correction closed-form** (KHÔNG cần
fit set — đúng cho trường hợp chỉ đổi prior do undersampling):
```
π_train = 1/(1+ratio)          # undersampler 1:5 -> 1/6 ≈ 0.1667  (ratio mặc định 5)
π_target                       # prevalence muốn hiển thị; mặc định = mean(y_true) của test ≈ 0.0039
logit_model = log(p/(1-p))     # p = y_prob (clip vào [1e-6, 1-1e-6] trước khi log)
logit_cal   = logit_model + (logit(π_target) - logit(π_train))
p_cal       = sigmoid(logit_cal)
```
Xuất `<run_dir>/calibration_metrics.json`: `{brier_raw, ece_raw, brier_cal, ece_cal}` per-fold + mean±std,
và `<run_dir>/reliability_curve.png` (raw vs calibrated, dùng `sklearn.calibration.calibration_curve` hoặc
tự bin). CLI: `--run-dir <path> [--ratio 5] [--target-prevalence <float|auto>]`. Thuần numpy + sklearn +
matplotlib (đã dùng ở benchmark scripts).

> **Caveat ghi vào docstring:** focal-loss + `loss.alpha=0.25` cũng làm méo calibration ngoài prior;
> prior-correction chỉ sửa phần prior. Nếu ECE sau correction vẫn cao → dùng Platt/isotonic (§1c).

### 1c. (Tuỳ chọn mạnh hơn) Platt / isotonic — cần `val_predictions.csv`
Hiện `save_predictions` chỉ được gọi cho **test** (`train_student.py:108-112`, `train_teacher.py:65-69`).
Isotonic/Platt cần **fit trên VAL** (giữ prevalence thật ~0,39% — `datamodule.val_dataloader()` KHÔNG dùng
sampler, xác nhận `datamodule.py:114-121`; sampler chỉ ở train `datamodule.py:91-97`).
- Thêm trong `train_student.py`/`train_teacher.py`, ngay sau khối eval test: chạy
  `val_metrics = evaluator.evaluate(datamodule.val_dataloader())` rồi
  `evaluator.save_predictions(val_metrics, run_dir / "val_predictions.csv")`.
  **LƯU Ý (đã kiểm):** `datamodule.val_sources()` **KHÔNG tồn tại** (chỉ có `test_sources()` ở
  `datamodule.py:155`); `evaluate(loader, sources=None)` nên bỏ arg `sources` là hợp lệ. Nếu cần phân
  tích calibration theo domain trên val → thêm method `val_sources()` mirror `test_sources()` trước.
- `compute_calibration.py` thêm chế độ `--method isotonic|platt`: fit `IsotonicRegression`
  (`sklearn.isotonic`) hoặc logistic (Platt) trên `val_predictions.csv`, áp lên `predictions.csv` (test),
  báo ECE/Brier before/after.

### 1d. Verify Change 1
- `python -m py_compile src/evaluation/metrics.py scripts/compute_calibration.py`; `validate-pipeline`.
- Chạy `scripts/compute_calibration.py --run-dir experiments/runs/kd_<t>_to_<s>` trên **server** (Mac
  thiếu sklearn) đọc predictions.csv có sẵn → sinh JSON + PNG. Không cần train lại.
- Nếu làm §1c: `poc-smoke-test` để chắc `val_predictions.csv` được ghi và không phá train loop.

---

## 2. Change 2 — MSE-on-logit KD [Kim et al. 2021]  ✅ CODE DONE (poc-smoke-test trên server: pending)

**Vì sao:** baseline KD thứ hai, gần như 0 chi phí. [13] chứng minh MSE trên raw logit ≈ KL ở T lớn — một
đối chứng hợp lệ ở K=1 cho soft-loss BCE hiện tại.

### 2a. `src/training/distillation.py` — thêm biến thể soft-loss
`BinaryDistillationLoss.__init__` (dòng 31-40) thêm param `soft_loss_type: str = "bce"`; lưu
`self.soft_loss_type`. Trong `forward` (dòng 42-79), thay khối tính `soft_loss` (dòng 67-71) bằng nhánh:
```python
if self.soft_loss_type == "mse":
    # Kim et al. 2021: MSE trên raw logit ~ KL ở T lớn; khớp trực tiếp, KHÔNG nhân T^2
    soft_loss = F.mse_loss(student_logits, teacher_logits)
else:  # "bce" — hành vi hiện tại, giữ nguyên
    with torch.no_grad():
        soft_targets = torch.sigmoid(teacher_logits / T)
    soft_loss = F.binary_cross_entropy_with_logits(student_logits / T, soft_targets) * (T ** 2)
```
`total_loss = alpha*hard + (1-alpha)*soft_loss` giữ nguyên. Cập nhật docstring đầu file cho biến thể mới.

### 2b. `src/training/kd_trainer.py:58-63` — truyền param
```python
self.criterion = BinaryDistillationLoss(
    temperature=kd_cfg.temperature,
    alpha=kd_cfg.alpha,
    soft_loss_type=kd_cfg.get("soft_loss_type", "bce"),   # <-- thêm
    hard_loss_fn=hard_loss_fn,
)
```

### 2c. `configs/training/distillation.yaml` — thêm key mặc định (không đổi hành vi)
Trong block `distillation:` thêm `soft_loss_type: bce`. Ablation:
`run/train_student.sh` với `EXTRA="training.distillation.soft_loss_type=mse run_suffix=__mselogit"`.

### 2d. Verify Change 2
- review-training + `validate-pipeline` (`python -c "import src.training"` phần này cần server/deps → chạy
  static AST bằng py_compile trên Mac; import đầy đủ verify trên server).
- `poc-smoke-test` trên server với `training.distillation.soft_loss_type=mse`. Default `bce` → back-compat.

---

## 3. Change 3 — Feature-based KD (RKD làm chính)  ✅ CODE DONE (poc-smoke-test trên server: pending)  ⚠️ LỚN NHẤT, RỦI RO CAO

**Vì sao:** đây là hướng nâng cấp KD **hợp lệ về mặt toán học** cho binary (KD_DESIGN_REVIEW §2.3): logit
ở binary chứa quá ít thông tin, nên chuyển sang distill **quan hệ giữa các mẫu** (relational) / feature.
**Chọn RKD [Park et al. 2019]** vì học quan hệ **distance + angle giữa các sample trong batch** → **KHÔNG
cần projector** (miễn nhiễm chênh dim teacher C_t vs student C_s), hợp lệ ở K=1. (SimKD/FitNet cần projector
khớp dim → xem §3e phụ lục.)

> **Điểm đúng-sai then chốt:** distance/angle của teacher tính TRONG không gian feature của teacher; của
> student tính TRONG không gian student; RKD khớp **cấu trúc quan hệ** (ma trận distance đã chuẩn hoá) giữa
> hai bên. **TUYỆT ĐỐI KHÔNG** so trực tiếp `feat_s` với `feat_t` (khác chiều) — đó là lỗi phổ biến nhất.

### 3a. Model feature API — `src/models/base_model.py` (bản mặc định)
> **ĐÃ SHIP khác spec gốc (đúng, không phải lỗi):** `forward_features` được đặt **1 chỗ duy nhất** là bản
> mặc định ở `BaseModel` (`base_model.py:15-27`), KHÔNG phải 4 wrapper như dự tính bên dưới — vì bộ baseline
> (`efficientnet.py`/`mobilenet.py`/`mobilevit.py`) đã bị xoá, dự án giờ SOTA-only với `TimmBackboneModel`
> làm wrapper duy nhất (theo đúng pattern `head(backbone(x)).squeeze(1)` nên default ở base là đủ). Phần dưới
> giữ nguyên làm tham chiếu lịch sử.

Hiện `forward(x)` (vd `timm_backbone.py:37-39`) = `self.head(self.backbone(x)).squeeze(1)`. Backbone (timm
`num_classes=0`) đã trả vector `(B, C)`. Thêm method **mới**, **giữ `forward` nguyên** (back-compat):
```python
def forward_features(self, x):
    """Trả (feat (B,C), logit (B,)). Dùng cho feature-based KD."""
    f = self.backbone(x)
    return f, self.head(f).squeeze(1)
```
- Thêm signature abstract (không bắt buộc @abstractmethod để khỏi vỡ model cũ — thêm bản mặc định ở
  `BaseModel` gọi `self.backbone`/`self.head` nếu có, hoặc implement ở từng wrapper).
- Implement giống nhau ở: `timm_backbone.py`, `efficientnet.py`, `mobilenet.py`, `mobilevit.py` (cả bốn đều
  có `self.backbone` + `self.head`, cùng pattern `head(backbone(x)).squeeze(1)`).
- **Không** đổi `MODEL_REGISTRY` / `build_head` / `infer_backbone_out_dim`.

### 3b. `src/training/feature_distillation.py` (MỚI) — `RKDLoss`
Theo Park et al. 2019. Sketch (kiểm numeric kỹ):
```python
import torch, torch.nn as nn, torch.nn.functional as F

def _pdist(feat, eps=1e-12):
    # ma trận khoảng cách Euclid (B,B)
    prod = feat @ feat.t()
    sq = prod.diag().unsqueeze(1)
    dist = (sq + sq.t() - 2 * prod).clamp_min(0.0).sqrt()
    return dist

class RKDLoss(nn.Module):
    def __init__(self, weight_dist=25.0, weight_angle=50.0):
        super().__init__(); self.wd, self.wa = weight_dist, weight_angle
    def forward(self, feat_s, feat_t):
        # --- distance-wise ---
        with torch.no_grad():
            dt = _pdist(feat_t)
            mean_dt = dt[dt > 0].mean(); dt = dt / (mean_dt + 1e-12)
        ds = _pdist(feat_s)
        mean_ds = ds[ds > 0].mean(); ds = ds / (mean_ds + 1e-12)
        loss_d = F.smooth_l1_loss(ds, dt)
        # --- angle-wise (triplets) ---
        with torch.no_grad():
            td = feat_t.unsqueeze(0) - feat_t.unsqueeze(1)      # (B,B,C)
            tn = F.normalize(td, dim=2)
            t_ang = torch.bmm(tn, tn.transpose(1, 2))           # (B,B,B) cos-góc
        sd = feat_s.unsqueeze(0) - feat_s.unsqueeze(1)
        sn = F.normalize(sd, dim=2)
        s_ang = torch.bmm(sn, sn.transpose(1, 2))
        loss_a = F.smooth_l1_loss(s_ang, t_ang)
        return self.wd * loss_d + self.wa * loss_a
```
> **Bộ nhớ:** angle là O(B²·C) và O(B³) phần tử — với `batch_size=64` (distillation.yaml) là ~262k, chấp
> nhận được. Nếu OOM → giảm batch hoặc sample subset sample cho nhánh angle (ghi TODO). `feat` phải là 2D
> `(B,C)`; nếu backbone nào trả 4D thì `flatten`/`adaptive_avg_pool` trước (verify bằng
> `infer_backbone_out_dim` đã dùng — nó giả định `(B,C)`).

### 3c. `src/training/kd_trainer.py` — tap features + cộng loss (gate opt-in)
- `_setup_training` (~dòng 58-63): sau khi tạo `self.criterion`, đọc `fk = kd_cfg.get("feature_kd", None)`;
  nếu có → `self.rkd = RKDLoss(fk.weight_dist, fk.weight_angle)` else `self.rkd = None`.
- `_train_epoch` (dòng 168-193): thay 2 dòng forward:
  ```python
  with torch.no_grad():
      t_feat, teacher_logits = self.teacher.forward_features(images)  # teacher frozen (đã eval+no_grad)
  s_feat, student_logits = self.student.forward_features(images)
  loss, components = self.criterion(student_logits, teacher_logits, labels)
  if self.rkd is not None:
      rkd_loss = self.rkd(s_feat, t_feat)
      loss = loss + rkd_loss
      # tích luỹ để log
  ```
- `_val_epoch` (dòng 201-222): teacher/student vẫn có thể dùng `forward_features` hoặc `forward` (val chỉ
  cần logit → dùng `forward` cho gọn cũng được; nếu muốn log val rkd thì `forward_features`).
- **GOTCHA lịch sử — history keys:** nếu log rkd, thêm `"train_rkd_loss"` vào `self.history` (dòng ~81-85)
  **và** `.append()` mỗi epoch (dòng ~116-120). Nếu KHÔNG log thì không thêm key (đừng khai key trống).
- Gate `self.rkd is not None` đảm bảo: không có block `feature_kd` trong config → hành vi y hệt hiện tại.

### 3d. Config — `configs/training/distillation_rkd.yaml` (MỚI)
Copy `distillation.yaml`, thêm vào block `distillation:`:
```yaml
distillation:
  temperature: 4.0
  alpha: 0.3
  soft_loss_type: bce
  feature_kd:
    type: rkd
    weight_dist: 25.0     # λ_dist (Park 2019) — tune lại cho binary
    weight_angle: 50.0    # λ_angle (Park 2019)
```
Chạy: `run/train_student.sh` với `TRAINING=distillation_rkd`. **Giữ `distillation.yaml` nguyên** → các run
KD chính không đổi. Ablation weight qua `EXTRA="training.distillation.feature_kd.weight_dist=... run_suffix=__rkd"`.

### 3e. (Phụ lục) SimKD nếu muốn thử — nhiều code hơn
SimKD [Chen 2022] tái dùng classifier của teacher + cần **projector** `Conv/Linear(C_s → C_t)`; student học
sao cho `projector(feat_s)` khớp `feat_t` (MSE) rồi đưa qua classifier teacher. Cần: module projector (lưu
state riêng), thay đường logit của student lúc distill. Rủi ro cao hơn RKD → chỉ làm nếu RKD không đủ.

### 3f. Verify Change 3
- review-training + `validate-pipeline` (AST + import trên server: `python -c "import src.training, src.models"`).
- **BẮT BUỘC** `poc-smoke-test` trên server với `TRAINING=distillation_rkd`: xác nhận (i) `forward_features`
  trả đúng `(feat, logit)`; (ii) RKDLoss không NaN với batch nhỏ của POC; (iii) training_curves vẽ được
  (history keys khớp); (iv) run KD thường (`TRAINING=distillation`) vẫn chạy y như trước (gate off).
- So kết quả: `run/aggregate.sh RUN_DIR=experiments/runs/kd_<t>_to_<s>__rkd` rồi
  `compare_kd_results.py --include-ablations`.

---

## 4. Phụ lục — cách chạy mọi thứ (non-slurm, server SSH)

Đường chạy hiện tại = `run/*.sh` (KHÔNG slurm). `run/train_student.sh` đọc env: `STUDENT TEACHER TRAINING
FOLDS AUG DROP_PATH GPU EXTRA`; forward `EXTRA` verbatim thành Hydra override; loop 5 fold.

```bash
# Ablation config-only (KHÔNG thuộc spec code, để đây cho tiện):
STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m \
  EXTRA="training.loss.alpha=0.75 run_suffix=__focal_a075" bash run/train_student.sh   # focal-α
STUDENT=... TEACHER=... EXTRA="training.distillation.alpha=0.0 run_suffix=__kdonly" bash run/train_student.sh  # DHKD KD-only

# Change 2 (MSE-logit):
STUDENT=... TEACHER=... EXTRA="training.distillation.soft_loss_type=mse run_suffix=__mselogit" bash run/train_student.sh

# Change 3 (RKD):
STUDENT=... TEACHER=... TRAINING=distillation_rkd EXTRA="run_suffix=__rkd" bash run/train_student.sh

# Aggregate + compare (mọi ablation dùng run_suffix nên có run-dir riêng, không đè run chính):
RUN_DIR=experiments/runs/kd_<teacher>_to_<student>__rkd bash run/aggregate.sh
python scripts/compare_kd_results.py --include-ablations
```
Run-dir: KD = `experiments/runs/kd_<teacher>_to_<student><run_suffix>/fold_<N>/`, baseline =
`baseline_<student><run_suffix>/fold_<N>/` (`train_student.py:71,85`). `compare_kd_results.py` tách
`__suffix` để phân loại (`split_suffix`).

---

## 5. Thứ tự đề xuất + Status checklist

Làm theo rủi ro tăng dần (mỗi mục verify xong mới sang mục sau):

- [x] **Change 1** Calibration (1a metrics.py `brier`/`ece` → 1b `compute_calibration.py` → 1c `val_predictions.csv`) — CODE DONE
- [x] **Change 2** MSE-logit (2a `distillation.py` `soft_loss_type` → 2b kd_trainer → 2c config `bce` default) — CODE DONE
- [x] **Change 3** Feature-KD RKD (3a `forward_features` ở BaseModel → 3b `RKDLoss` → 3c kd_trainer gate → 3d `distillation_rkd.yaml`) — CODE DONE
- [x] Sau mỗi change: review-training/validate-pipeline (static, Mac); ARCHITECTURE.md + memory đã cập nhật.
- [ ] **CÒN TỒN:** `poc-smoke-test` trên server (đặc biệt RKD — bắt buộc), rồi chạy thật 5 fold, aggregate,
      so bằng `compare_kd_results.py --include-ablations`, điền kết quả. **Chưa làm** (Mac không train được).

## 6. File đụng tới (tóm tắt)
| Change | Sửa | Tạo mới |
|---|---|---|
| 1 Calibration | `src/evaluation/metrics.py`; (1c) `scripts/train_student.py`,`scripts/train_teacher.py` | `scripts/compute_calibration.py` |
| 2 MSE-logit | `src/training/distillation.py`, `src/training/kd_trainer.py`, `configs/training/distillation.yaml` | — |
| 3 Feature-KD | `src/models/{base_model,timm_backbone,efficientnet,mobilenet,mobilevit}.py`, `src/training/kd_trainer.py` | `src/training/feature_distillation.py`, `configs/training/distillation_rkd.yaml` |

---

> **Tài liệu liên quan:** `docs/KD_DESIGN_REVIEW_2026-07-13.md` (§2 feature/relational KD, §6.1 calibration,
> §3 DHKD/α), `docs/ARCHITECTURE.md`, `reports/2026-06-21_data_strategy_ablation_plan.md` (house-style +
> tiền lệ ablation). Con số prevalence chuẩn: **0,39%** (ISIC 2024 + PAD-UFES-20 test) — xem `docs/PREPROCESSING.md`.
