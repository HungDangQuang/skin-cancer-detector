# Khai thác Metadata để "tăng độ tin cậy" cho mô hình KD phát hiện ung thư da trên edge — Phân tích chiến lược

## TL;DR
- Đường đi đúng đắn nhất về lý thuyết cho `tbp_lv_*` (chỉ có lúc train, không có trên phone) là **Learning Using Privileged Information (LUPI) / generalized distillation** (Lopez-Paz 2016) và **auxiliary multi-task** (dự đoán metadata làm target rồi vứt head lúc deploy) — cả hai giữ student **thuần image-only**, không phá vỡ ExecuTorch/XNNPACK/INT8.
- Nhưng "độ tin cậy" (reliability) mà Hưng thực sự cần **không phải discrimination mà là calibration**: với `DynamicUndersampledSampler` 1:5 từ prevalence thật ~0,39%, đầu ra sigmoid bị thổi phồng ~**40–50×**; **prior correction / logit adjustment (Menon 2021)** là can thiệp **rẻ nhất, an toàn nhất, tác động lớn nhất** và đúng trọng tâm yêu cầu — không cần train lại, không đụng 30-run matrix.
- Fusion metadata làm INPUT (MetaBlock) chỉ đáng làm cho subset deployable (age/sex/site + anamnesis kiểu PAD) và mang **rủi ro shortcut "đây là ảnh PAD → malignant"** rất nguy hiểm (PAD là nguồn augment malignant); phải xử lý bằng domain adversarial / per-dataset norm trước khi tin — và lợi ích kỳ vọng nhỏ.

## Key Findings
1. Với head **single-logit + sigmoid nhị phân** của Hưng, nhiều SOTA KD **degenerate về mặt toán học**: DKD, logit standardization, OFA-KD **không áp dụng được** (chi tiết §A4). Logit-level privileged distillation vẫn transfer được nhưng chỉ 1 chiều thông tin (confidence/ranking) → nên ưu tiên **feature-level**.
2. Metadata là nơi chứa phần lớn signal của ISIC 2024, nhưng phần mạnh nhất nằm ở `tbp_lv_*` — **thứ không thể lấy trên điện thoại** (cần phần cứng Vectra WB360 3D-TBP). Đây là nghịch lý cốt lõi: signal ở đúng chỗ không deploy được.
3. **Trần image-only thực tế ~0,142–0,16 pAUC@TPR80.** Mọi kỳ vọng "metadata sẽ kéo pAUC student lên gần mức full-model" đều **không khả thi** cho một mô hình image-only chạy trên phone.
4. Ứng viên tốt nhất, chi phí thấp, **không đụng experiment matrix 30-run**: **calibration + selective prediction**. Đây đúng nghĩa "tăng độ tin cậy" và viết được thành một chương/mục luận văn độc lập.

## Details

### Bối cảnh dữ liệu (neo theo tài liệu dự án của Hưng)
- **ISIC 2024 SLICE-3D**: 401.059 ảnh non-dermoscopic (TBP crop ~128×128) từ **5.349 bệnh nhân** tại 9 tổ chức y tế; tập test challenge bổ sung ~500.000 ảnh từ nhóm bệnh nhân độc lập. ISIC 2024 thô: **~393 ca ác tính / 401.059 ≈ 0,1% (~1:1000)**.
- **PAD-UFES-20** (Pacheco et al. 2020, Mendeley `zr7vgbcyr2`): **2.298 ảnh lâm sàng chụp smartphone** từ 1.641 tổn thương của 1.373 bệnh nhân; **58,4% mẫu có sinh thiết xác nhận** và 100% mẫu ung thư có sinh thiết đối chứng. Dùng làm nguồn augment malignant.
- **Prevalence sau gộp + làm sạch ≈ 0,39%** (đo thực tế: **241 dương tính / 61.831 âm tính** trên held-out test độc lập của dự án). Chính con số 0,39% này là lý do calibration trở nên tối quan trọng.

### (A) LUPI / Privileged Information Distillation — framing quan trọng nhất cho `tbp_lv_*`

**Lý thuyết.** Vapnik & Vashist [1] đưa ra paradigm LUPI: lúc train có thêm "privileged information" x* (ở đây là `tbp_lv_*`, `iddx_*`, `mel_thick_mm`, `mel_mitotic_index`) chỉ có ở train, không có ở test. Vapnik & Izmailov [2] hình thức hoá qua SVM+ (similarity control). Lopez-Paz et al. [3] hợp nhất LUPI với distillation của Hinton [4] thành **generalized distillation**: privileged info không vào loss student trực tiếp mà đi qua một **teacher đặc quyền** (thấy x*), teacher này sinh soft targets dẫn dắt student image-only. Đây là fit trực tiếp cho pipeline 2-stage của Hưng.

**Recipe cụ thể (privileged teacher):**
1. *Stage 1′*: train teacher đa nhánh = (backbone ảnh hiện có, ví dụ `convnextv2_base`) ⊕ (MLP encode `tbp_lv_*` đã chuẩn hoá) → fusion → single logit. Teacher này mạnh hơn teacher image-only vì "biết" `tbp_lv_*`.
2. *Stage 2*: student image-only distill từ privileged teacher, **giữ nguyên** `L_total = 0.3·BinaryFocalLoss + 0.7·T²·BCE(sigmoid(s/T),sigmoid(t/T))`, chỉ đổi nguồn logit teacher. Student **không bao giờ** thấy `tbp_lv_*` → `.pte`/INT8 nguyên vẹn.
- Code changes: `src/models/` thêm privileged teacher (image+tabular); `src/data/dataset.py` trả thêm tensor `tbp_lv_*` (mask cho mẫu PAD); `src/training/kd_trainer.py` gần như không đổi.

**Y văn medical imaging.** Hoffman et al. [5] "Modality Hallucination" (CVPR 2016): train một nhánh "ảo hoá" modality thiếu để lúc test chỉ cần RGB — chính là privileged distillation ở **feature level**. Nhiều follow-up cross-modal / missing-modality distillation trong y ảnh theo cùng ý tưởng.

**A4 — Subtlety single-logit sigmoid (rất quan trọng, dễ hiểu sai) [well-supported]:**
- Trong KD đa lớp, "dark knowledge" là phân bố tương đối giữa các lớp non-target. Với **nhị phân single-logit**, teacher chỉ xuất **một** số p_t = sigmoid(t/T); thông tin transfer qua BCE chỉ **1 chiều** (mức tự tin / vị trí ranking). Vẫn hữu ích nhưng **nghèo hơn nhiều** dark knowledge đa lớp.
- **Degenerate cases phải flag rõ:** DKD [10] tách TCKD+NCKD — với 2 lớp, tập non-target chỉ 1 lớp ⇒ softmax phần non-target ≡ 1 ⇒ **NCKD ≡ 0**, DKD suy biến. Logit standardization [11] cần Z-score trên chiều lớp; với 1 logit, std trên 1 phần tử **không xác định**. OFA-KD [12] chiếu qua không gian logit đa lớp cũng vô nghĩa khi K≤2. ⇒ **KHÔNG dùng ba phương pháp này.**
- **Hệ quả:** privileged distillation ở **logit level** transfer rất ít trong chế độ nhị phân → chuyển sang **feature-level**: FitNet/hint [6], similarity-preserving SP [9], relational RKD [8], hoặc CRD [7]. Cho student học **cấu trúc quan hệ** của không gian đặc trưng mà privileged teacher hình thành — đây là chỗ `tbp_lv_*` thực sự rò rỉ tri thức vào student mà không cần logit.

### (B) Auxiliary / multi-task: dự đoán metadata làm TARGET rồi vứt head lúc deploy

Thêm các head phụ (chỉ tồn tại lúc train) buộc backbone **regress `tbp_lv_*`** — vốn là ABCDE đã lượng hoá: Asymmetry↔`tbp_lv_symm_2axis`, Border↔`tbp_lv_norm_border`, Color↔`tbp_lv_norm_color`/`tbp_lv_color_std_mean`, Diameter↔`clin_size_long_diam_mm`. Deploy: bỏ head phụ → student vẫn image-only, `.pte`/INT8 không đổi.
- **Y văn ủng hộ:** ISIC 2018 Task 2 (phát hiện dermoscopic attributes: pigment network, globules, streaks, milia-like cysts, negative network); nhiều nghiên cứu "attribute-guided" cho thấy giám sát thuộc tính lâm sàng cải thiện tính giải thích và đôi khi hiệu năng phân loại chính ("clinically-criteria-supervised").
- **Cân bằng loss:** focal + KD + nhiều auxiliary loss → dùng **uncertainty weighting (Kendall & Gal 2018)** [16] hoặc **GradNorm (Chen 2018)** [17] thay vì chỉnh tay.
- **Honest caveat [extrapolation]:** dưới prevalence 0,39%, auxiliary regression `tbp_lv_*` chủ yếu là **representation regularizer**; lợi ích lên AUPRC/pAUC thường **nhỏ và không chắc chắn** — chưa có bằng chứng mạnh cho binary + extreme imbalance. Giá trị lớn nhất là **giải thích được** (head ABCDE cho biết "vì sao nghi ngờ"), hỗ trợ narrative "độ tin cậy". `tbp_lv_*` chỉ có cho mẫu ISIC ⇒ auxiliary loss phải **mask theo dataset** (PAD không có → không backprop head đó).

### (C) Metadata làm INPUT (multimodal fusion) — chỉ subset deployable

Subset phone lấy được: age, sex, `anatom_site_general` + anamnesis kiểu PAD (itch/grew/hurt/changed/bleed/elevation, tiền sử ung thư da bản thân/gia đình, Fitzpatrick tự khai).
- **Papers:** Pacheco & Krohling **MetaBlock** [13] (IEEE JBHI; dùng PAD-UFES-20 + ISIC — trực tiếp liên quan) và bản trước [14]; PAD-UFES-20 dataset [15]. Fusion: late vs early vs attention — **FiLM** (Perez 2018) [26], cross-attention. MetaBlock/MetaNet cải thiện balanced accuracy vài điểm phần trăm so với image-only trên PAD (*số BACC cụ thể và DOI: Hưng cần xác minh — xem Caveats*).
- **Định lượng lợi ích demographic-only:** theo brief từ bài kết quả ISIC 2024, thêm demographic cơ bản chỉ nâng pAUC từ ~0,142 → ~0,154 (**~+0,012**) ⇒ **nhỏ**.
- **Engineering trên XNNPACK/PT2E:** nhánh MLP tabular về nguyên tắc export ExecuTorch được và PT2E lượng tử hoá được (toàn Linear/ReLU), nhưng: (i) **làm hỏng narrative** "thuần image lightweight backbone"; (ii) app phải thu thập input tin cậy; (iii) op concat/fusion cần kiểm tra hỗ trợ XNNPACK delegate. Chi phí kỹ thuật **trung bình–cao**.
- **Rủi ro đạo đức + shortcut:** điều kiện hoá risk score trên anamnesis tự khai ⇒ người dùng khai sai; model có thể **over-rely metadata, bỏ qua ảnh** (metadata shortcut). Bắt buộc ablation "drop metadata lúc test" + modality dropout khi train.

### (D) Harmonization — ISIC 2024 vs PAD-UFES-20 gần như không giao nhau

- **Intersection-only** (age, sex, site): mất toàn bộ `tbp_lv_*` (signal mạnh nhất) và toàn bộ anamnesis PAD. An toàn nhưng gần như vô ích.
- **Missing-modality training:** learnable "missing" embedding, **modality dropout**, per-dataset encoder chia sẻ backbone ảnh; kỹ thuật missing-modality (ví dụ SMIL — Ma et al., AAAI 2021 [29]). Cho phép dùng `tbp_lv_*` chỉ cho ISIC, anamnesis chỉ cho PAD.
- **RỦI RO NGHIÊM TRỌNG NHẤT — dataset-bias shortcut:** ISIC = TBP crop, PAD = ảnh smartphone; PAD lại là nguồn augment malignant ⇒ "trông giống ảnh PAD" ≈ "malignant". Nếu metadata schema cũng khác theo dataset, model học "tôi ở dataset nào" thay vì học tổn thương → **catastrophic**. Mitigation: **domain adversarial (DANN — Ganin et al. 2016** [25]) với gradient reversal để backbone không phân biệt được dataset; **per-dataset normalization**; sampling cân đối; và **bắt buộc report cross-domain HAM10000** để lộ shortcut.

### (E) CALIBRATION & reliability — đây mới đúng "tăng độ tin cậy" [ưu tiên #1]

- **Prior correction / logit adjustment (Menon et al. 2021** [18]): undersampling 1:5 ⇒ prevalence train ≈ 1/6 ≈ 0,167, prevalence thật ≈ 0,0039. Odds ratio ≈ (0,167/0,833)/(0,0039/0,9961) ≈ 0,2/0,0039 ≈ **~51×**. Sửa hậu xử lý: `logit_hiệu_chỉnh = logit_train − log[ π_train(1−π_test) / ((1−π_train)π_test) ]` ≈ trừ ~3,9 trên logit. **Không cần train lại**, chỉ hậu xử lý → app hiển thị "risk probability" đúng thang. Đây là fix quan trọng nhất về "độ tin cậy".
- **Temperature scaling (Guo et al. 2017** [19]) sau prior correction; hoặc isotonic/Platt trên validation. Nên **calibrate riêng theo anatomical site / Fitzpatrick** (metadata-conditioned calibration) — cách metadata cải thiện reliability mà **không cần vào model**, không đụng `.pte`.
- **Selective prediction / abstention:** app nói "không đánh giá được, hãy đi khám" khi bất định — hợp với screening tool. Công cụ: MC dropout (Gal & Ghahramani 2016) [21], deep ensembles (Lakshminarayanan 2017) [20], evidential DL (Sensoy 2018) [22], conformal prediction [23] (bảo đảm coverage). Rẻ nhất cho edge: threshold trên xác suất đã calibrate + entropy.
- **Metrics bổ sung:** ECE, Brier score, reliability diagram, risk–coverage curve. Thêm vào eval hiện có mà **không đổi model** — thuần `src/eval`.

### (F) ISIC 2024 winners đã làm gì với metadata

- Công thức thắng cuộc chủ đạo (theo hiểu biết chung về challenge — *Hưng cần trích dẫn writeup Kaggle cụ thể, xem Caveats*): **GBDT (LightGBM/CatBoost/XGBoost) trên tabular `tbp_lv_*`**, cộng **out-of-fold prediction của CNN ảnh làm một feature** (stacking). Feature engineering nặng: ratio và **patient-normalized "ugly duckling"** — z-score đặc trưng của một lesion so với các lesion khác **trên cùng bệnh nhân**.
- **Ugly duckling:** melanoma thường là nốt "lạc loài" so với các nốt của chính bệnh nhân. Cần **nhiều lesion/bệnh nhân** — một app chụp 1 ảnh **không có**. Về lý thuyết app có thể yêu cầu chụp 2–3 nốt để so sánh; Soenksen et al. [24] (Science Translational Medicine 2021) phát hiện tự động ugly-duckling từ ảnh wide-field gần mức chuyên gia — nhưng cần ảnh diện rộng, không phải mô hình 1-crop.
- **Định lượng:** phần lớn điểm số thắng cuộc đến từ nhánh tabular/GBDT + `tbp_lv_*`; image branch đóng góp tương đối nhỏ (image-only ~0,142 vs full ~0,1726). ⇒ **Bài học cay đắng:** signal nằm ở đúng thứ Hưng không có trên phone → củng cố kết luận rằng đóng góp luận văn nên là **reliability/calibration + KD trên image-only**, không phải chạy đua pAUC tuyệt đối.

## Recommendations (xếp hạng, cho người ĐANG train, seed=42, patient-level 5-fold, 30-run matrix)

**Nguyên tắc:** ưu tiên (i) không phá student image-only / ExecuTorch / INT8, (ii) không làm hỏng 30-run matrix (thêm như **trục ablation mới**, không redesign), (iii) đúng trọng tâm "độ tin cậy".

| # | Approach | Impl cost | Đổi model deploy? | Kỳ vọng (headline) | Thêm vào matrix? | Rủi ro |
|---|----------|-----------|-------------------|--------------------|------------------|--------|
| 1 | **Prior correction + metadata-conditioned calibration + ECE/Brier** | Thấp | Không | AUPRC/pAUC ~không đổi; calibration cải thiện lớn (đúng "độ tin cậy") | Có (post-hoc trên checkpoint đã có) | Rất thấp |
| 2 | **Selective prediction / abstention** (conformal / threshold+entropy) | Thấp–TB | Không (hậu xử lý) | Tăng safety screening; báo cáo risk–coverage | Có | Thấp |
| 3 | **Privileged teacher (feature-level distill từ image+`tbp_lv_*`)** | TB–Cao | Không (student image-only) | pAUC/AUPRC có thể +nhỏ; bằng chứng vừa phải | Có — trục KD mới | Overfit, scope creep |
| 4 | **Auxiliary ABCDE (`tbp_lv_*` làm target, mask theo dataset)** | TB | Không | Lợi ích nhỏ/không chắc; mạnh về giải thích | Có | Cân bằng loss |
| 5 | **Fusion input (MetaBlock, subset deployable)** | Cao | **CÓ — phá narrative image-only** | pAUC ~+0,012 (demographic) | Không — gần redesign | Shortcut, ethics |

**Kế hoạch theo giai đoạn:**
- **Làm NGAY (không đụng training):** #1 và #2 trên các checkpoint đang có. "Quick win" đúng nghĩa reliability, thành một mục luận văn độc lập, không rủi ro với 30-run matrix.
- **Nếu còn compute:** #3 như một teacher variant bổ sung (privileged vs non-privileged) — trục ablation sạch, student không đổi. Dùng **feature-level**, KHÔNG logit-level (vì lý do §A4).
- **Chỉ nếu dư thời gian & muốn tính giải thích:** #4 (kèm uncertainty weighting/GradNorm, mask dataset).
- **Cân nhắc rất kỹ / có thể bỏ:** #5 — lợi ích nhỏ, phá deployment story, rủi ro shortcut cao.
- **Ngưỡng đổi quyết định:** nếu #3 không cho **ΔpAUC ≥ ~+0,01 nhất quán qua ≥4/5 fold** → dừng, giữ image-only + calibration. Nếu ablation "drop metadata lúc test" (#5) làm điểm sụt mạnh → đó là bằng chứng shortcut, phải bỏ.

## Caveats
- **Môi trường thực thi này KHÔNG có web tool trực tiếp** (đã xác nhận qua subagent và enricher). Các số **0,939 / 0,922 / 0,1726 / 0,142 / 0,154** lấy theo brief của Hưng dẫn từ bài kết quả ISIC 2024 (Kurtansky et al., *npj Digital Medicine*, PMC12639164) — **cần Hưng đối chiếu verbatim + DOI** trước khi ghi cứng vào luận văn.
- Số **BACC cụ thể của MetaBlock/MetaNet** (Pacheco & Krohling, IEEE JBHI) và **DOI + số hiệu năng của Soenksen et al. 2021** (Science Translational Medicine) **chưa xác minh được offline** — phải tra cứu lại.
- **Claim well-supported:** degeneracy của DKD / logit standardization / OFA-KD ở K≤2; công thức prior correction / logit adjustment; khung LUPI / generalized distillation; rủi ro dataset-bias shortcut (ISIC-crop vs PAD-smartphone, PAD là nguồn malignant).
- **Claim extrapolation (flag rõ, đừng oversell):** mức lợi ích cụ thể của auxiliary supervision và privileged distillation cho **binary + prevalence 0,39%** là **chưa được chứng minh mạnh** trong y văn; kỳ vọng nên khiêm tốn. Đóng góp chắc chắn và defensible nhất của việc "khai thác metadata" trong bối cảnh này là **calibration/reliability**, không phải nâng pAUC tuyệt đối.

### Tài liệu tham khảo (cần Hưng chuẩn hoá DOI/venue)
- [1] Vapnik, V. & Vashist, A. (2009). "A new learning paradigm: Learning using privileged information." *Neural Networks* 22(5–6).
- [2] Vapnik, V. & Izmailov, R. (2015). "Learning using privileged information: similarity control and knowledge transfer." *JMLR* 16.
- [3] Lopez-Paz, D., Bottou, L., Schölkopf, B., Vapnik, V. (2016). "Unifying distillation and privileged information." *ICLR*. arXiv:1511.03643.
- [4] Hinton, G., Vinyals, O., Dean, J. (2015). "Distilling the Knowledge in a Neural Network." arXiv:1503.02531.
- [5] Hoffman, J., Gupta, S., Darrell, T. (2016). "Learning with Side Information through Modality Hallucination." *CVPR*.
- [6] Romero, A. et al. (2015). "FitNets: Hints for Thin Deep Nets." *ICLR*. arXiv:1412.6550.
- [7] Tian, Y., Krishnan, D., Isola, P. (2020). "Contrastive Representation Distillation (CRD)." *ICLR*. arXiv:1910.10699.
- [8] Park, W. et al. (2019). "Relational Knowledge Distillation (RKD)." *CVPR*. arXiv:1904.05068.
- [9] Tung, F. & Mori, G. (2019). "Similarity-Preserving Knowledge Distillation." *ICCV*. arXiv:1907.09682.
- [10] Zhao, B. et al. (2022). "Decoupled Knowledge Distillation (DKD)." *CVPR*. arXiv:2203.08679.
- [11] Sun, S. et al. (2024). "Logit Standardization in Knowledge Distillation." *CVPR*. arXiv:2403.01427.
- [12] Hao, Z. et al. (2023). "One-for-All KD (OFA-KD)." *NeurIPS*. arXiv:2310.19444.
- [13] Pacheco, A.G.C. & Krohling, R.A. (2021). "An attention-based mechanism to combine images and metadata in deep learning models applied to skin cancer classification (MetaBlock)." *IEEE JBHI*. (DOI cần xác minh.)
- [14] Pacheco, A.G.C. & Krohling, R.A. (2020). "The impact of patient clinical information on automated skin cancer detection." *Computers in Biology and Medicine* 116:103545.
- [15] Pacheco, A.G.C. et al. (2020). "PAD-UFES-20: A skin lesion dataset composed of patient data and clinical images collected from smartphones." *Data in Brief*. Mendeley zr7vgbcyr2.
- [16] Kendall, A., Gal, Y., Cipolla, R. (2018). "Multi-task learning using uncertainty to weigh losses." *CVPR*. arXiv:1705.07115.
- [17] Chen, Z. et al. (2018). "GradNorm." *ICML*. arXiv:1711.02257.
- [18] Menon, A.K. et al. (2021). "Long-tail learning via logit adjustment." *ICLR*. arXiv:2007.07314.
- [19] Guo, C. et al. (2017). "On Calibration of Modern Neural Networks." *ICML*. arXiv:1706.04599.
- [20] Lakshminarayanan, B. et al. (2017). "Deep Ensembles." *NeurIPS*. arXiv:1612.01474.
- [21] Gal, Y. & Ghahramani, Z. (2016). "Dropout as a Bayesian Approximation (MC dropout)." *ICML*. arXiv:1506.02142.
- [22] Sensoy, M. et al. (2018). "Evidential Deep Learning." *NeurIPS*. arXiv:1806.01768.
- [23] Angelopoulos, A. & Bates, S. (2021). "A Gentle Introduction to Conformal Prediction." arXiv:2107.07511.
- [24] Soenksen, L.R. et al. (2021). "Using deep learning and wide-field photography to detect suspicious pigmented lesions." *Science Translational Medicine*. (DOI/số liệu cần xác minh.)
- [25] Ganin, Y. et al. (2016). "Domain-Adversarial Training of Neural Networks (DANN)." *JMLR*. arXiv:1505.07818.
- [26] Perez, E. et al. (2018). "FiLM: Feature-wise Linear Modulation." *AAAI*. arXiv:1709.07871.
- [29] Ma, M. et al. (2021). "SMIL: Multimodal Learning with Severely Missing Modality." *AAAI*. arXiv:2103.05677.
- Kurtansky, N. et al. (ISIC 2024 results). *npj Digital Medicine*, PMC12639164. (Số ablation cần đối chiếu verbatim.)