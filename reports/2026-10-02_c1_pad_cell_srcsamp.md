# Ô PAD của C1 (KD − baseline) — ứng viên `__srcsamp`, checkpoint AUPRC (02/10/2026)

> Việc T7 trong `docs/NEXT_TASKS_2026-10-02.md`. C1 là **báo cáo**, không quyết định chọn model
> (`.claude/skills/eval-results/reference/acceptance-gates.md`, dòng C1). Mốc "> 0 trên PAD và Fitz" còn
> **ĐỀ XUẤT** (⚑).

**Lệnh** (server `vastnew`, CPU, 02/10/2026; cây symlink `.tmp/ci_srcsamp/auprc_indomain` = hai run-dir
`experiments/runs_newsplit_ddi/{kd_efficientnetv2_m_to_,baseline_}mobilenetv4_conv_medium__srcsamp`):

```bash
bash run/bootstrap_ci.sh RESULTS_DIR=.tmp/ci_srcsamp/auprc_indomain \
  PAIR=kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp:baseline_mobilenetv4_conv_medium__srcsamp \
  SUBGROUP=source PRED_NAME=predictions_auprc.csv \
  METRICS=auc_roc,auprc,pauc_at_tpr80,sens_at_90spec,sens_at_80spec \
  OUT_JSON=reports/ci_c1_pad_srcsamp_auprc_indomain.json OUT_MD=reports/ci_c1_pad_srcsamp_auprc_indomain.md
```

B = 2000, seed 42, 59.093 dòng test, 5 fold mỗi run, `predictions_auprc.csv`. Endpoint = **mục 6**
(`A − B` = KD − baseline, đúng dấu).

## Kết quả (`reports/ci_c1_pad_srcsamp_auprc_indomain.md` mục 6, dòng 61–62)

| Miền | ΔAUPRC | ΔAUC-ROC | ΔpAUC@TPR80 | ΔSens@80Spec |
|---|---|---|---|---|
| PAD-UFES-20 | −0,0008 [−0,0199, +0,0187] | −0,0002 [−0,0136, +0,0134] | −0,0012 [−0,0099, +0,0070] | +0,0138 [−0,0295, +0,0608] |
| ISIC 2024 | +0,0282 [+0,0039, +0,0598] * | +0,0331 [+0,0192, +0,0479] * | +0,0234 [+0,0120, +0,0340] * | +0,0579 [+0,0152, +0,1000] * |

`*` = CI loại trừ 0.

**Nhãn C1** (quy tắc "> 0": `lo > 0` ⇒ ĐẠT, `hi ≤ 0` ⇒ KHÔNG ĐẠT, còn lại CHƯA CHỨNG MINH):
- PAD: `lo = −0,0199`, `hi = +0,0187` ⇒ **CHƯA CHỨNG MINH** ⚑.
- Fitzpatrick17k (đã có, `reports/ci_srcsamp_auprc_fitzpatrick17k_headline.md:20`): +0,0395 [+0,0310, +0,0478] ⇒ ĐẠT ⚑.
- C1 cần **cả hai** miền ⇒ **C1 = CHƯA CHỨNG MINH** ⚑. Không đổi phán quyết tổng (C1 không phải tiêu chí chọn).

**Đọc kết quả.** Trong arm `__srcsamp`, lợi ích của KD trên tập test trong miền nằm **hoàn toàn ở miền ISIC**;
trên ảnh lâm sàng PAD, student KD và baseline **không phân biệt được** trên cả bốn metric. Con số gộp toàn
tập (mục 2: ΔAUPRC +0,1367 [+0,1083, +0,1653]) lớn hơn hẳn cả hai ô theo miền, vì AUPRC gộp còn phụ thuộc
cách hai miền xếp hạng lẫn nhau; ô theo miền mới là ô để trích (cùng khuyến cáo `run/bootstrap_ci.sh` ghi cho ablation PAD, dù lý do ở đó khác).

## Thay cho dòng C1 trong `reports/2026-10-02_acceptance_verdict_srcsamp.md`

File phán quyết nằm trên nhánh `docs/gates-signoff-and-guides` (chưa merge). Sau khi merge, thay dòng C1 bằng:

```
| C1 (báo cáo) | KD − baseline, ΔAUPRC | > 0 trên PAD và Fitz ⚑ | PAD −0,0008 [−0,0199, +0,0187] · Fitz +0,0395 [+0,0310, +0,0478] | `reports/ci_c1_pad_srcsamp_auprc_indomain.md:62`; `reports/ci_srcsamp_auprc_fitzpatrick17k_headline.md:20` | CCM ⚑ (PAD) |
```

và bỏ gạch đầu dòng "ô PAD của C1" khỏi mục "Lệnh còn thiếu để đo đủ".
