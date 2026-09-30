> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](../reports/BAO_CAO_TONG_HOP.md).
>
> Lý do: cùng phạm vi "chỉ 1 teacher" (22/08).

---

# NOTE PHÂN TÍCH KẾT QUẢ & BENCHMARK — dùng khi trình bày/bảo vệ

> **Mục đích:** ghi lại **bảng kết quả thật** (5-fold CV, mean ± std trên test độc lập) kèm **cách đọc / cách đánh giá / lời phân tích** để follow khi thuyết trình hoặc trả lời hội đồng.
>
> **Nguồn số liệu (kiểm chứng trong repo, không phải ước lượng):**
> - Độ chính xác: `experiments/runs/<run>/aggregated.json` (5-fold, mean ± std, test set độc lập).
> - Ablation PAD: `reports/pad_ablation_{efficientnetv2_m,convnextv2_base,maxvit_base}.md`.
> - Benchmark: `report_phase_1/benchmark/cpu_benchmark/**` + `benchmark/mobile_benchmark/pixel6a_ondevice.csv`.
> - Ngày cập nhật: **2026-08-22** (Pixel 6a đo 2026-07-04).
>
> ⚠️ **PHẠM VI — nói thẳng khi trình bày:** chỉ dùng run huấn luyện **từ 15/7/2026**. Các run tháng 6 (KD `convnextv2_base→*`, `maxvit_base→*`) và toàn bộ tier baseline cũ (EfficientNet-B4 / B0 / MobileNetV3 / MobileViT-S) **đã bị loại** — 4 kiến trúc đó đã bị xoá khỏi `src/models/registry.py`. Hệ quả: **teacher duy nhất có ma trận KD hợp lệ là `efficientnetv2_m`** → không kết luận được "teacher nào chưng cất tốt nhất" (xem Phần C và G).

---

## PHẦN A — BẢNG KẾT QUẢ ĐỘ CHÍNH XÁC (test độc lập, 5-fold, mean ± std)

### A.1 — Teacher (standalone)

| Teacher | AUPRC 🔴 | pAUC@TPR80 🔴 | AUC-ROC | Sensitivity 🔴 | Sens@95Spec | Specificity |
|---|---|---|---|---|---|---|
| **MaxViT-Base** | **0,6566 ± 0,0211** | **0,1830 ± 0,0025** | 0,9824 ± 0,0024 | 0,924 ± 0,007 | **0,917 ± 0,004** | 0,949 |
| ConvNeXtV2-Base | 0,6506 ± 0,0306 | 0,1822 ± 0,0021 | 0,9816 ± 0,0021 | 0,920 ± 0,012 | 0,915 ± 0,018 | 0,954 |
| EfficientNetV2-M | 0,6298 ± 0,0488 | 0,1826 ± 0,0025 | 0,9820 ± 0,0025 | **0,927 ± 0,020** | 0,912 ± 0,009 | 0,944 |

> **Đọc bảng:** `maxvit_base` cao nhất ở AUPRC/pAUC/AUC/Sens@95Spec, nhưng **chồng lấn trong 1 std** với `convnextv2_base` → **không** tuyên bố "teacher mạnh nhất" một cách tuyệt đối. `efficientnetv2_m` thấp nhất ở AUPRC (std lớn nhất, 0,0488) dù Sensitivity cao nhất và pAUC ngang nhau.

### A.2 — Student: KD vs Baseline (cùng data/seed/hparam, chỉ khác hàm mất mát)

Teacher chưng cất = `efficientnetv2_m` (teacher duy nhất có ma trận KD hợp lệ).

| Student (paradigm) | Điều kiện | AUPRC 🔴 | pAUC@TPR80 🔴 | AUC-ROC | Sensitivity 🔴 | Sens@95Spec |
|---|---|---|---|---|---|---|
| **MobileNetV4-Conv-M** (Depthwise-sep CNN) | Baseline | 0,6101 ± 0,0476 | 0,1798 ± 0,0052 | 0,9790 | 0,920 ± 0,009 | 0,916 |
| | **+ KD** | 0,6056 ± 0,0341 | **0,1859 ± 0,0016** | **0,9852** | **0,933 ± 0,009** | 0,930 |
| **FastViT-SA12** (CNN + Reparam) | Baseline | 0,6082 ± 0,0417 | 0,1825 ± 0,0032 | 0,9817 | 0,923 ± 0,012 | 0,923 |
| | **+ KD** | 0,6209 ± 0,0225 | 0,1853 ± 0,0023 | 0,9846 | 0,929 ± 0,013 | **0,934** |
| **EfficientFormerV2-S2** (Attention-CNN hybrid) | Baseline | 0,6283 ± 0,0147 | 0,1812 ± 0,0016 | 0,9804 | 0,918 ± 0,021 | 0,918 |
| | **+ KD** | **0,6220 ± 0,0531** | 0,1849 ± 0,0017 | 0,9841 | 0,929 ± 0,007 | 0,931 |
| **RepViT-M1.0** (ViT-style CNN) | Baseline | 0,5365 ± 0,0362 | 0,1718 ± 0,0024 | 0,9709 | 0,912 ± 0,021 | 0,890 |
| | **+ KD** | 0,5537 ± 0,0292 | 0,1832 ± 0,0008 | 0,9823 | 0,924 ± 0,011 | 0,923 |

**Phát hiện quan trọng để nhấn mạnh:** **cả 4 student KD** đều có pAUC@80 (0,1832–0,1859) **cao hơn hoặc ngang cả 3 teacher** (0,1822–0,1830), và Sensitivity ngang/hơn teacher — trong khi nhẹ hơn nhiều lần. Đó **đúng là mục tiêu của KD**: nén về mobile mà giữ vùng độ nhạy cao.

⚠️ **Đừng nói "student vượt teacher".** Ở **AUPRC**, teacher vẫn cao hơn (0,63–0,66 vs 0,55–0,62). Phát biểu đúng là: *"student KD đạt/vượt teacher ở pAUC@TPR≥80% và độ nhạy, nhưng chưa bằng ở AUPRC"*. (Luận điểm "student vượt teacher" ở bản cũ dựa trên teacher yếu EfficientNet-B4 — model đã bị loại khỏi đề tài.)

---

## PHẦN B — HIỆU QUẢ CỦA KD (Δ = KD − Baseline, teacher `efficientnetv2_m`, 4/4 student × 5 fold)

| Student | ΔAUPRC | ΔpAUC | ΔAUC-ROC | ΔSensitivity | ΔSens@95Spec |
|---|---|---|---|---|---|
| RepViT-M1.0 | **+0,0172** | **+0,0115** | +0,0114 | +0,0124 | **+0,0324** |
| FastViT-SA12 | **+0,0127** | +0,0028 | +0,0029 | +0,0066 | +0,0108 |
| MobileNetV4-Conv-M | −0,0045 | +0,0061 | +0,0062 | +0,0124 | +0,0141 |
| EfficientFormerV2-S2 | −0,0062 | +0,0037 | +0,0037 | +0,0108 | +0,0133 |

**Cách đánh giá (trung thực — đây là kết quả *có sắc thái*, không phải "KD thắng tuyệt đối"):**

1. **pAUC@TPR80 (metric ISIC 2024) và AUC-ROC: KD cải thiện *nhất quán* cả 4/4 student** (Δ luôn dương, +0,003 → +0,012). Đây là tín hiệu tích cực nhất — KD kéo đường ROC ở vùng độ nhạy cao lên.
2. **Sensitivity: KD cải thiện 4/4** (+0,007 → +0,012), và **Sens@95Spec cũng 4/4** (+0,011 → +0,032) — đúng mục tiêu y tế "không bỏ sót ca ác tính". **Đây là bằng chứng chắc chắn nhất.**
3. **AUPRC (headline metric): *hỗn hợp*** — RepViT (+0,0172) và FastViT (+0,0127) dương; MobileNetV4 (−0,0045) và EfficientFormerV2 (−0,0062) âm nhẹ. **Cả 4 Δ đều nhỏ hơn 1 std của baseline tương ứng → nằm trong nhiễu**, không phải "KD làm hại". **Không được che giấu điều này.**
4. **Kết luận:** với teacher `efficientnetv2_m`, KD *cải thiện chắc chắn pAUC và độ nhạy* nhưng *không nâng AUPRC một cách đáng tin*. Giá trị của KD trong đề tài này nằm ở **vùng độ nhạy cao**, đúng thứ mà bài toán sàng lọc cần.

> **Lưu ý phương pháp:** std giữa các fold ở AUPRC (0,015–0,053) *lớn hơn* mọi Δ quan sát được → tuyệt đối phải báo cáo mean ± std, **không** trích một con số điểm. Kiểm định thống kê chính thức (Paired t-test) **chưa được cài đặt** — xem Phần G.

⚠️ **Đã RÚT luận điểm cũ "ΔAUPRC phụ thuộc chất lượng teacher" (ConvNeXtV2 → MobileNetV4 +0,052).** Nó dựa trên KD `convnextv2_base` bản **tháng 6**, ngoài phạm vi. Muốn khẳng định lại phải train lại ma trận KD của `convnextv2_base`/`maxvit_base`.

---

## PHẦN C — GIẢ THUYẾT "TEACHER MẠNH → STUDENT TỐT HƠN" → ⏳ CHƯA TRẢ LỜI ĐƯỢC

Trong phạm vi July-15+, **chỉ `efficientnetv2_m` có ma trận KD hợp lệ**. Không có điểm dữ liệu thứ hai để so → **không thể** vẽ scatter `AUPRC_teacher ↔ ΔAUPRC_student` hay tính hệ số tương quan.

| Teacher (AUPRC standalone) | Ma trận KD hợp lệ? | Student đã có |
|---|---|---|
| maxvit_base (0,6566) | ❌ chỉ có bản tháng 6 (1–2 fold) | — |
| convnextv2_base (0,6506) | ❌ chỉ có bản tháng 6, **đang train lại dở** | — |
| **efficientnetv2_m (0,6298)** | ✅ **4/4 student × 5 fold** | mobilenetv4, fastvit, efficientformerv2, repvit |

**Cách nói trước hội đồng:** *"Về chất lượng teacher standalone, MaxViT ≈ ConvNeXtV2 mạnh hơn EfficientNetV2-M nhưng chênh trong 1 std. Còn câu hỏi teacher nào chưng cất tốt nhất thì em chưa có đủ dữ liệu hợp lệ để trả lời — đó là công việc còn lại của luận văn, và em đã ghi rõ trong kế hoạch."* Sự trung thực này an toàn hơn nhiều so với việc trích số tháng 6.

---

## PHẦN C-bis — ABLATION DỮ LIỆU: PAD-UFES-20 CÓ GIÚP KHÔNG? → ✅ CÓ, cả 3 teacher

Đây là **kết quả mới**, chứng minh một quyết định thiết kế dữ liệu thay vì chỉ khẳng định.

**Thiết kế:** cùng một test set độc lập (ISIC+PAD), chỉ khác TRAIN+VAL — with-PAD (`experiments/runs/teacher/*`) vs ISIC-only (`experiments/runs_isic_only/teacher/*`). Ô quyết định là **subset ảnh PAD** (miền lâm sàng mà nhánh no-PAD chưa từng thấy). Cả 3 teacher đều là bản July-15+, 5/5 fold.

| Teacher | ΔAUPRC (PAD subset) | ΔpAUC@80 | ΔSens | ΔSens@95Spec | Verdict |
|---|---|---|---|---|---|
| efficientnetv2_m | **+0,1241** | +0,0349 | +0,0756 | +0,1844 | ✅ PAD giúp |
| convnextv2_base | **+0,0920** | +0,0356 | +0,1256 | +0,1089 | ✅ PAD giúp |
| maxvit_base | **+0,1311** | +0,0352 | +0,1256 | +0,2322 | ✅ PAD giúp |

- **Miền PAD:** cả 3 teacher tốt hơn hẳn khi có PAD (Sens@95Spec tăng tới +0,23).
- **Miền ISIC:** Δ trong nhiễu → thêm PAD **không hại** miền dermoscopy gốc.
- **Kết luận:** trộn PAD-UFES-20 giúp teacher tổng quát hóa **rõ rệt trên ảnh lâm sàng/smartphone** mà không hy sinh miền gốc — đúng với cả 3 teacher. Đây là bằng chứng định lượng cho lựa chọn dữ liệu của đề tài.

---

## PHẦN D — BENCHMARK HIỆU NĂNG

### D.1 — Hiệu năng tĩnh (device-independent, SO CHÉO ĐƯỢC)

| Model | Params (M) | GFLOPs | Size FP32 (MB) |
|---|---|---|---|
| MobileNetV4-Conv-M | 8,436 | 1,653 | 32,44 |
| FastViT-SA12 | 10,557 | 2,962 | 40,41 |
| EfficientFormerV2-S2 | 12,132 | 2,493 | 46,75 |
| RepViT-M1.0 | *chưa đo* | *chưa đo* | *chưa đo* |
| 3 teacher (effv2_m / convnextv2 / maxvit) | *chưa đo* | *chưa đo* | *chưa đo* |

> Số của 3 student đầu lấy từ `benchmark/cpu_benchmark/full_profile_cpu_gpu/*.json`. **RepViT-M1.0 và 3 teacher hiện tại chưa có job benchmark nào** → cần chạy `bash run/benchmark.sh` bổ sung (GAP).

### D.2 — Latency ON-DEVICE THẬT trên Pixel 6a (ExecuTorch `.pte`, FP32, batch=1, median ms)

| Model | Size .pte (MB) | 1 thread | 2 threads | **4 threads** | FPS (4t) |
|---|---|---|---|---|---|
| MobileNetV4-Conv-M | 32,11 | 53,3 | 29,8 | **22,6** | 44,2 |
| EfficientFormerV2-S2 | 46,98 | 88,6 | 51,5 | **42,8** | 23,3 |
| FastViT-SA12 | 40,35 | 142,3 | 85,0 | **65,5** | 15,3 |
| RepViT-M1.0 | — | — | — | *chưa đo* | — |

> Đo 2026-07-04 (Pixel 6a, Google Tensor, arm64-v8a, SDK 36, warmup 10 / 50 iters). Latency là **weight-independent** (`docs/MOBILE.md §0`) nên các số này **vẫn hợp lệ** sau khi model được train lại — chỉ cần đổi cột AUPRC đi kèm.
>
> Phiên đo gốc còn có `mobilenetv3_large` (8,4 ms / 16 MB) nhưng kiến trúc đó **đã bị loại khỏi đề tài** → không đưa vào bảng Pareto/khuyến nghị nữa.

**Cách đánh giá benchmark:**
1. **Chỉ params/FLOPs/size là so chéo thiết bị được.** Latency cluster-CPU là *proxy*, không phải số điện thoại — **luôn ưu tiên trích số Pixel 6a thật**.
2. **Đa luồng scale tốt:** từ 1→4 thread, MobileNetV4 giảm 53,3→22,6 ms (~2,4×), FastViT 142→66 ms.
3. **Ranking latency KHÁC ranking params:** FastViT (10,6M) chạy *chậm hơn* EfficientFormerV2 (12,1M) trên Pixel 6a (65,5 vs 42,8 ms) dù ít param hơn — **đây là lý do phải đo on-device thật, không suy từ FLOPs**.
4. **MobileNetV4 là model nhanh nhất & nhẹ nhất** trong 3 model đã đo (22,6 ms / 32,1 MB).

---

## PHẦN E — PHÂN TÍCH PARETO & KHUYẾN NGHỊ TRIỂN KHAI

Ghép độ chính xác (bản July-15+, KD ← `efficientnetv2_m`) với latency Pixel 6a (4 threads):

| Model | AUPRC | pAUC@80 | Sens | Latency 4t | Size .pte | Nhận định Pareto |
|---|---|---|---|---|---|---|
| **MobileNetV4-Conv-M (KD)** | 0,6056 | **0,1859** | **0,933** | **22,6 ms** | **32,1 MB** | **Điểm cân bằng** — nhanh nhất, nhẹ nhất, dẫn đầu pAUC/AUC/Sens |
| EfficientFormerV2-S2 (KD) | **0,6220** | 0,1849 | 0,929 | 42,8 ms | 47,0 MB | **Điểm "AUPRC tối đa"** — đổi lại chậm gần 2× và nặng hơn 15 MB |
| FastViT-SA12 (KD) | 0,6209 | 0,1853 | 0,929 | 65,5 ms | 40,3 MB | **Bị lấn át** — AUPRC ≈ EfficientFormerV2 nhưng chậm hơn 1,5× |
| RepViT-M1.0 (KD) | 0,5537 | 0,1832 | 0,924 | *chưa đo* | *chưa đo* | Chưa xếp được — thiếu benchmark |

**Khuyến nghị (nói khi trình bày):**
- **Model chốt: MobileNetV4-Conv-Medium ← EfficientNetV2-M.** Nó thắng ở *hai* trục cùng lúc — vừa nhanh/nhẹ nhất, vừa dẫn đầu pAUC@80 (0,1859), AUC (0,9852) và Sensitivity (0,933) trong toàn bộ student.
- Nếu bắt buộc tối đa hóa AUPRC → EfficientFormerV2-S2, chấp nhận 42,8 ms và `.pte` 47 MB.
- **FastViT bị lấn át** trên máy thật (chậm hơn mà không chính xác hơn) — một kết luận chỉ có được nhờ đo on-device.

---

## PHẦN F — TALKING POINTS & CÁCH TRÌNH BÀY KẾT QUẢ (trung thực)

1. **Mở bằng phát hiện chắc chắn nhất:** *"Cả 4 student sau KD đều đạt pAUC@TPR≥80% và độ nhạy ngang hoặc hơn teacher, dù nhẹ hơn nhiều lần"* — đúng số liệu, và đúng mục tiêu của KD.
2. **KD giúp cái gì, không giúp cái gì (nói thẳng):** cải thiện *nhất quán 4/4* ở pAUC + độ nhạy + Sens@95Spec; còn AUPRC thì Δ nằm **trong nhiễu** (2 dương / 2 âm nhẹ). Sự trung thực này *tăng* độ tin cậy trước hội đồng.
3. **Chứng minh được quyết định dữ liệu:** ablation PAD cho thấy trộn PAD-UFES-20 nâng AUPRC trên miền lâm sàng +0,09…+0,13 cho **cả 3** teacher mà không hại miền ISIC — đây là bằng chứng, không phải giả định.
4. **Nhấn tầm quan trọng của on-device thật:** thứ hạng latency đảo so với params/FLOPs (FastViT chậm hơn EfficientFormerV2) → chứng minh vì sao đề tài *phải* benchmark trên Pixel 6a thật.
5. **Khung Pareto = đóng góp thực tiễn:** không có "một model tốt nhất" tuyệt đối, mà là *frontier* để chọn theo ràng buộc thiết bị.
6. **Nếu bị hỏi "Δ nhỏ thế có ý nghĩa không?":** trả lời thẳng — std giữa fold lớn hơn Δ ở AUPRC nên em **không** kết luận từ AUPRC; kết luận KD của em dựa trên pAUC/Sens vốn dương nhất quán 4/4. Kiểm định Paired t-test là bước còn lại (Phần G).
7. **Nếu bị hỏi về teacher nào tốt nhất:** nói rõ chưa trả lời được, và giải thích vì sao (chỉ 1 teacher có ma trận KD hợp lệ trong đợt huấn luyện hiện tại).

---

## PHẦN G — CÒN THIẾU (cập nhật note này sau mỗi đợt chạy)

- [ ] **Ma trận KD của `convnextv2_base`** (× 4 student × 5 fold) — bắt buộc để khép câu hỏi "teacher nào chưng cất tốt nhất" (Phần C). Tùy chọn: `maxvit_base`.
      *Cảnh báo:* các run-dir `kd_convnextv2_base_to_*` / `kd_maxvit_base_to_*` hiện **trộn fold tháng 6 và fold mới** → **không chạy `aggregate_folds.py`** trên chúng cho tới khi đủ 5 fold cùng đợt.
- [ ] **Paired t-test** cho từng ΔAUPRC / ΔpAUC — **chưa có trong code**: `scripts/compare_kd_results.py` chỉ tính mean±std + Δ (pure stdlib, không import scipy). Phải bổ sung, hoặc mô tả đúng là "kế hoạch" trong đề cương.
- [ ] **Export `.pte`** cho bộ model July-15+ (`exports/` đang rỗng) + **parity check** `max|Δlogit| < 1e-3`.
- [ ] **Benchmark `repvit_m1_0`** (params/FLOPs/size/latency) + params/FLOPs cho 3 teacher.
- [ ] **Cross-domain HAM10000** + **Fairness Fitzpatrick17k** — data-layer đã code (`scripts/prepare_external_data.py`, kiểm tra rò rỉ exit 2), **chưa chạy eval**. Lưu ý: Fitzpatrick17k ship **URL chứ không ship ảnh** (phải tải bằng `scripts/download_fitzpatrick17k.py`), và bộ lọc phải theo **two-tier** (chỉ drop lỗi integrity) vì ngưỡng `is_uninformative` tuned cho dermoscopy sẽ tương quan với tông da — đúng ngay chỗ đang đo fairness.
- [ ] **Calibration** cho model chốt (`scripts/compute_calibration.py`): sigmoid thô bị lệch vì prior undersample ~16,7% ≠ prevalence thật 0,39%. Không đổi bất kỳ số ranking nào (pAUC/AUPRC/AUC bất biến với biến đổi đơn điệu), nhưng cần cho "% nguy cơ" hiển thị trong app.

> **Quy trình cập nhật:** `aggregate_folds.py` → `compare_kd_results.py` → thay số trong các bảng trên → tick checkbox. Giữ nguyên format mean ± std và **giữ nguyên nguyên tắc phạm vi July-15+**.
