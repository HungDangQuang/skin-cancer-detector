# NOTE PHÂN TÍCH KẾT QUẢ & BENCHMARK — dùng khi trình bày/bảo vệ

> **Mục đích:** ghi lại **bảng kết quả thật** (đã chạy 5-fold CV, tổng hợp mean ± std) kèm **cách đọc / cách đánh giá / lời phân tích** để bạn follow khi thuyết trình hoặc trả lời hội đồng.
>
> **Nguồn số liệu (đã kiểm chứng trong repo, không phải ước lượng):**
> - Accuracy: `report_phase_1/model/**/aggregated.json` (5-fold, mean ± std trên test set độc lập).
> - Benchmark hiệu năng: `report_phase_1/benchmark/cpu_benchmark/**` + `report_phase_1/benchmark/mobile_benchmark/pixel6a_ondevice.csv`.
> - Ngày cập nhật số liệu: **2026-07-04** (Pixel 6a đo 2026-07-04).
>
> ⚠️ **Giới hạn dữ liệu hiện có (nói thẳng khi trình bày):** mới hoàn thành **tier baseline** (teacher EfficientNet-B4 + 3 student cổ điển, đủ cả 2 nhánh KD/baseline) và **một phần tier SOTA** (teacher EfficientNetV2-M, ConvNeXtV2-Base đã có; 1 cặp KD SOTA `ConvNeXtV2-Base → FastViT-SA12`). Các cặp KD SOTA còn lại + baseline SOTA + MaxViT-Base + cross-domain/fairness **chưa xong** → xem Phần G.

---

## PHẦN A — BẢNG KẾT QUẢ ĐỘ CHÍNH XÁC (test set độc lập, 5-fold, mean ± std)

### A.1 — Teacher

| Teacher | Params | AUPRC 🔴 | pAUC@TPR80 🔴 | AUC-ROC | Sensitivity 🔴 | Specificity |
|---|---|---|---|---|---|---|
| EfficientNet-B4 (baseline) | ~17,6M | 0,600 ± 0,027 | 0,1785 ± 0,0034 | 0,978 ± 0,003 | 0,909 ± 0,013 | 0,955 ± 0,009 |
| EfficientNetV2-M (SOTA) | — | 0,649 ± 0,026 | 0,1875 ± 0,0022 | 0,987 ± 0,002 | 0,928 ± 0,010 | 0,956 ± 0,004 |
| **ConvNeXtV2-Base (SOTA)** | — | **0,683 ± 0,025** | **0,1893 ± 0,0011** | 0,989 ± 0,001 | 0,949 ± 0,016 | 0,947 ± 0,018 |

> **Đọc bảng:** teacher SOTA vượt rõ teacher baseline. ConvNeXtV2-Base là teacher mạnh nhất (AUPRC 0,683 vs 0,600 của B4 — **+0,083 tuyệt đối, ~+14% tương đối**). Đây là tiền đề để kiểm chứng giả thuyết "teacher mạnh → student tốt hơn".

### A.2 — Student: KD vs Baseline (cùng data/seed/hparam, chỉ khác hàm loss)

| Student (paradigm) | Điều kiện | AUPRC 🔴 | pAUC@TPR80 🔴 | AUC-ROC | Sensitivity 🔴 | Sens@95%Spec |
|---|---|---|---|---|---|---|
| **EfficientNet-B0** (Compound) | Baseline | 0,655 ± 0,029 | 0,1850 ± 0,0026 | 0,984 | 0,933 ± 0,021 | 0,910 |
| | **+ KD** | 0,651 ± 0,020 | 0,1877 ± 0,0006 | 0,987 | 0,940 ± 0,006 | 0,932 |
| **MobileNetV3-Large** (NAS-CNN) | Baseline | 0,661 ± 0,035 | 0,1858 ± 0,0008 | 0,985 | 0,934 ± 0,013 | 0,933 |
| | **+ KD** | 0,631 ± 0,016 | 0,1881 ± 0,0010 | 0,987 | 0,955 ± 0,005 | 0,927 |
| **MobileViT-S** (Hybrid) | Baseline | 0,627 ± 0,029 | 0,1866 ± 0,0020 | 0,986 | 0,940 ± 0,014 | 0,934 |
| | **+ KD** | 0,639 ± 0,039 | 0,1879 ± 0,0009 | 0,987 | 0,945 ± 0,013 | 0,932 |
| **FastViT-SA12** (CNN+Reparam) | **KD only¹** | 0,676 ± 0,034 | 0,1908 ± 0,0014 | 0,990 | 0,949 ± 0,021 | 0,944 |

> ¹ FastViT-SA12 mới có nhánh KD (teacher ConvNeXtV2-Base), **chưa có baseline** → chưa tính được Δ. Nhưng đây hiện là **student mạnh nhất toàn bảng** (AUPRC 0,676; pAUC 0,1908).

**Phát hiện quan trọng để nhấn mạnh:** các student (KD) **vượt cả teacher EfficientNet-B4** ở AUPRC (vd KD-B0 0,651 > B4 0,600) và pAUC (0,188 > 0,178). Student nhỏ ~5M param đánh bại teacher ~17,6M — bằng chứng KD + undersampling + Focal Loss hoạt động tốt trên bài toán mất cân bằng.

---

## PHẦN B — HIỆU QUẢ CỦA KD (Δ = KD − Baseline, tier baseline)

| Student | ΔAUPRC | ΔpAUC | ΔAUC-ROC | ΔSensitivity | ΔSens@95Spec |
|---|---|---|---|---|---|
| EfficientNet-B0 | **−0,004** | +0,0027 | +0,0026 | **+0,0075** | +0,0216 |
| MobileNetV3-Large | **−0,029** | +0,0023 | +0,0021 | **+0,0216** | −0,0058 |
| MobileViT-S | **+0,012** | +0,0013 | +0,0014 | +0,0050 | −0,0025 |

**Cách đánh giá (trung thực — đây là kết quả *có sắc thái*, không phải "KD thắng tuyệt đối"):**

1. **Trên pAUC@TPR80 (metric ISIC 2024) và AUC-ROC: KD cải thiện *nhất quán* cả 3 student** (Δ luôn dương). Đây là tín hiệu tích cực nhất — KD kéo đường ROC ở vùng độ nhạy cao lên.
2. **Trên Sensitivity: KD cũng cải thiện cả 3** (đặc biệt MobileNetV3 +2,16%) — đúng mục tiêu y tế "không bỏ sót ca ác tính".
3. **Trên AUPRC (headline metric): KD *mixed*** — chỉ MobileViT-S dương (+0,012), còn B0 (−0,004) và MobileNetV3 (−0,029) âm nhẹ→trung bình. **Không được che giấu điều này.** Cách diễn giải: ở prevalence ~0,39%, AUPRC dao động mạnh giữa các fold (std 0,02–0,04), nên các Δ nhỏ nằm trong khoảng nhiễu → **cần Paired t-test để kết luận** (xem Phần F).
4. **Kết luận sơ bộ:** KD giúp *ổn định độ nhạy và pAUC* nhưng *chưa chứng minh cải thiện AUPRC đồng đều* ở tier baseline. Paradigm hybrid (MobileViT) có vẻ hưởng lợi từ KD nhiều hơn CNN thuần — cần thêm tier SOTA để khẳng định.

> **Lưu ý phương pháp:** std giữa các fold (0,02–0,04 ở AUPRC) *lớn hơn* nhiều Δ → tuyệt đối phải báo cáo mean ± std và Paired t-test, **không** trích một con số điểm.

---

## PHẦN C — GIẢ THUYẾT "TEACHER MẠNH → STUDENT TỐT HƠN"

Bằng chứng hiện có (1 điểm dữ liệu SOTA, nên **mới là gợi ý, chưa phải kết luận**):

| Teacher (AUPRC) | Student | Student AUPRC | Student pAUC |
|---|---|---|---|
| EfficientNet-B4 (0,600) | → EfficientNet-B0 | 0,651 | 0,1877 |
| EfficientNet-B4 (0,600) | → MobileNetV3-L | 0,631 | 0,1881 |
| EfficientNet-B4 (0,600) | → MobileViT-S | 0,639 | 0,1879 |
| **ConvNeXtV2-Base (0,683)** | **→ FastViT-SA12** | **0,676** | **0,1908** |

**Phân tích:** teacher mạnh nhất (ConvNeXtV2-Base) đi với student tốt nhất (FastViT, AUPRC 0,676 — cao nhất bảng, sát teacher 0,683). Xu hướng *thuận chiều* với giả thuyết, **nhưng** FastViT cũng là kiến trúc student mạnh hơn bản chất → chưa tách được "teacher tốt" khỏi "student tốt". Cần hoàn thành ma trận (cùng student, đổi teacher) để vẽ được **scatter AUPRC_teacher ↔ ΔAUPRC_student** và tính hệ số tương quan — đây là câu hỏi nghiên cứu bổ sung, sẽ trả lời ở Phần 2 của luận văn.

---

## PHẦN D — BENCHMARK HIỆU NĂNG

### D.1 — Hiệu năng tĩnh (device-independent, SO CHÉO ĐƯỢC)

| Model | Params (M) | GFLOPs | Size FP32 (MB) |
|---|---|---|---|
| EfficientNet-B0 | 4,01 | — | 15,45 |
| MobileNetV3-Large | 4,20 | — | 16,13 |
| MobileViT-S | 4,94 | — | 18,89 |
| MobileNetV4-Conv-M | 8,44 | 1,653 | 32,44 |
| FastViT-SA12 | 10,56 | 2,962 | 40,41 |
| EfficientFormerV2-S2 | 12,13 | 2,493 | 46,75 |
| EfficientNet-B4 (teacher) | 17,55 | — | 67,43 |

### D.2 — Latency ON-DEVICE THẬT trên Pixel 6a (ExecuTorch .pte, batch=1, median ms)

| Model | Size .pte (MB) | 1 thread | 2 threads | **4 threads** | FPS (4t) |
|---|---|---|---|---|---|
| **MobileNetV3-Large** | 16,05 | 18,2 | 10,1 | **8,4** | **119,1** |
| MobileNetV4-Conv-M | 32,11 | 53,3 | 29,8 | **22,6** | 44,2 |
| EfficientFormerV2-S2 | 46,98 | 88,6 | 51,5 | **42,8** | 23,3 |
| FastViT-SA12 | 40,35 | 142,3 | 85,0 | **65,5** | 15,3 |

> EfficientNet-B0 / MobileViT-S **chưa export .pte** → chưa có số on-device (xem Phần G).

**Cách đánh giá benchmark:**
1. **Chỉ params/FLOPs/size là so chéo thiết bị được.** Latency cluster-CPU là *proxy*, không phải số điện thoại — **luôn ưu tiên trích số Pixel 6a thật** khi nói về "chạy trên điện thoại".
2. **Đa luồng scale tốt:** từ 1→4 thread, MobileNetV3 giảm 18,2→8,4 ms (~2,2×), FastViT 142→66 ms.
3. **Ranking latency KHÁC ranking params:** FastViT (10,6M) chạy *chậm hơn* EfficientFormerV2 (12,1M) trên Pixel 6a (65,5 vs 42,8 ms) dù ít param hơn — đúng như cảnh báo "latency transformer có thể đảo thứ hạng trên ARM". **Đây là lý do phải đo on-device thật, không suy từ FLOPs.**
4. **MobileNetV3-Large là nhà vô địch tốc độ:** 8,4 ms (119 FPS) — nhanh gấp ~5× so với EfficientFormerV2, gấp ~8× FastViT.

---

## PHẦN E — PHÂN TÍCH PARETO & KHUYẾN NGHỊ TRIỂN KHAI

Ghép accuracy (AUPRC) với latency Pixel 6a (4 threads):

| Model | AUPRC | Latency 4t (ms) | Nhận định Pareto |
|---|---|---|---|
| MobileNetV3-Large (KD) | 0,631 | **8,4** | **Điểm "latency tối thiểu"** — nhanh nhất, accuracy chấp nhận được |
| EfficientFormerV2-S2 | *(chưa có KD-agg)* | 42,8 | Trung gian |
| FastViT-SA12 (KD) | **0,676** | 65,5 | **Điểm "accuracy tối đa"** — tốt nhất nhưng chậm nhất |

**Khuyến nghị (nói khi trình bày):** Pareto frontier có **hai đầu rõ rệt**:
- Nếu ưu tiên **tốc độ / máy yếu** → **MobileNetV3-Large + KD** (8,4 ms, 119 FPS, AUPRC 0,63, sens KD cao nhất 0,955).
- Nếu ưu tiên **độ chính xác lâm sàng** → **FastViT-SA12 + KD** (AUPRC 0,676, pAUC 0,191 — cao nhất, nhưng 65 ms).
- **MobileNetV3 + KD là lựa chọn cân bằng nhất** cho kịch bản Edge AI cộng đồng: nhanh nhất *và* có độ nhạy KD cao nhất — hiếm khi một model thắng cả hai tiêu chí.

---

## PHẦN F — TALKING POINTS & CÁCH TRÌNH BÀY KẾT QUẢ (trung thực)

1. **Mở bằng phát hiện mạnh nhất:** "Student ~5M param sau KD *vượt teacher* 17,6M ở AUPRC và pAUC" — gây ấn tượng, đúng số liệu.
2. **KD giúp cái gì, không giúp cái gì (nói thẳng):** cải thiện *nhất quán* pAUC + độ nhạy (đúng mục tiêu y tế), nhưng AUPRC còn *mixed* ở tier baseline → cần Paired t-test + tier SOTA để kết luận. Sự trung thực này *tăng* độ tin cậy trước hội đồng.
3. **Nhấn tầm quan trọng của on-device thật:** thứ hạng latency đảo so với FLOPs (FastViT chậm hơn EfficientFormerV2) → chứng minh vì sao đề tài *phải* benchmark trên Pixel 6a thật, không suy đoán.
4. **Khung Pareto = đóng góp thực tiễn:** không có "một model tốt nhất" tuyệt đối, mà là *frontier* để người dùng chọn theo ràng buộc thiết bị.
5. **Nếu bị hỏi "Δ nhỏ thế có ý nghĩa không?":** trả lời — std giữa fold lớn hơn Δ, nên em *không* kết luận từ con số điểm mà dùng **Paired t-test 5-fold (p<0,05)**; đó chính là lý do thiết kế đối chứng ceteris paribus.

---

## PHẦN G — CÒN THIẾU (điền vào note này sau khi chạy xong đánh giá)

Khi các job cluster hoàn tất + rsync về, cập nhật các bảng trên và điền tiếp:

- [ ] **Baseline SOTA students** (mobilenetv4 / fastvit / efficientformerv2 no-KD) → mới tính được ΔAUPRC/ΔpAUC tier SOTA.
- [ ] **Các cặp KD SOTA còn lại** (EffNetV2-M / MaxViT-Base × 3 student) → hoàn tất ma trận Phần C, vẽ scatter teacher↔Δ + hệ số tương quan.
- [ ] **Teacher MaxViT-Base** aggregated (đang thiếu trong bảng A.1).
- [ ] **Paired t-test** cho từng ΔAUPRC / ΔpAUC (p-value) → thay cụm "mixed/nhất quán" bằng kết luận thống kê.
- [ ] **Export .pte** cho EfficientNet-B0 + MobileViT-S → hoàn tất bảng latency Pixel 6a (D.2) và Pareto (E).
- [ ] **Cross-domain HAM10000** + **Fairness Fitzpatrick17k** (nhóm da I–VI, gap max−min) → chưa có số nào.

> **Quy trình cập nhật:** sau khi có `aggregated.json` mới → chạy lại các lệnh trích số (xem git log của file này) → thay số trong bảng → tick checkbox. Giữ nguyên format mean ± std.
