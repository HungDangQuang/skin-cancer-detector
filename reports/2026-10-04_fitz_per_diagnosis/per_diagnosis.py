"""Diagnostic (report only): where does III-b lose sensitivity on Fitzpatrick17k-C? Stdlib only, from the repo root:
    python3 reports/2026-10-04_fitz_per_diagnosis/per_diagnosis.py <Fitzpatrick17k-C csv>

Fitzpatrick17k's `three_partition_label = malignant` covers 11 diagnoses. Two facts make that label differ from the
training label space:
  * actinic keratosis is "malignant" in Fitzpatrick17k but ACK is BENIGN in training (configs/data/pad_ufes_20.yaml:19);
  * mycosis fungoides and Kaposi sarcoma are absent from ISIC 2024 / PAD-UFES-20 and rare in DDI (32 + 6 malignant
    images, appended to the train side of runs_newsplit_ddi) — see README.
(1) sensitivity per diagnosis at the frozen app threshold (P0, `pad_sens90`), fold 4 and summed over 5 folds;
(2) per-diagnosis AUC vs all benign images (threshold-free), mean of 5 folds, P0 student vs its teacher
    `efficientnetv2_m` (checkpoint chính) — if the teacher is as weak, compression is not the cause;
(3) III-b of P0 (fold 4) recomputed with groups of diagnoses removed from the positives — DIAGNOSTIC ONLY, not a gate.
"""
import csv
import math
import sys
from collections import defaultdict

FITZC = sys.argv[1]
STU = ("reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline/"
       "kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp")
TEA = "reports/external_newsplit_ddi/fitzpatrick17k/headline/efficientnetv2_m"
TEA2 = "reports/external_newsplit_ddi/fitzpatrick17k/headline/convnextv2_base"  # P1's teacher, for comparison
SUMMARY = "reports/2026-10-02_threshold_options/summary.csv"
TONES = ["light", "medium", "dark"]
Z = 1.959964

dx = {r["md5hash"]: r["label"] for r in csv.DictReader(open(FITZC))}
thr = {int(r["fold"]): float(r["threshold"]) for r in csv.DictReader(open(SUMMARY)) if r["rule"] == "pad_sens90"}


def load(root, k):
    out = []
    for r in csv.DictReader(open(f"{root}/fold_{k}/predictions.csv")):
        m = r["image_id"].removeprefix("fitz_")
        if m in dx:  # Fitzpatrick17k-C subset only
            out.append((r["image_id"], r["tone_group"], int(float(r["y_true"])), float(r["y_prob"]), dx[m]))
    return out


def wilson(k, n):
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return c - h, c + h


def auc(pos, neg):
    """Mann-Whitney AUC with ties = 0.5, O((n+m) log(n+m))."""
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    rank, i, rsum = 0.0, 0, 0.0
    while i < len(allv):
        j = i
        while j < len(allv) and allv[j][0] == allv[i][0]:
            j += 1
        r = (i + 1 + j) / 2  # average rank of the tie block (1-based)
        rsum += r * sum(1 for t in allv[i:j] if t[1] == 1)
        i = j
    n1, n0 = len(pos), len(neg)
    return (rsum - n1 * (n1 + 1) / 2) / (n1 * n0)


stu = {k: load(STU, k) for k in range(5)}
tea = {k: load(TEA, k) for k in range(5)}
tea2 = {k: load(TEA2, k) for k in range(5)}
for k in range(5):
    assert [x[0] for x in stu[k]] == [x[0] for x in tea[k]] == [x[0] for x in tea2[k]], f"row order differs at fold {k}"

print("## (1) Độ nhạy theo chẩn đoán tại ngưỡng app — P0, Fitzpatrick17k-C\n")
print("| Chẩn đoán | n ác (fold 4) | sáng · trung bình · tối | Độ nhạy fold 4 [Wilson 95%] | Độ nhạy cộng 5 fold (mỗi fold ngưỡng pad_sens90 riêng — điểm vận hành khác nhau) |")
print("|---|---|---|---|---|")
by = defaultdict(lambda: [0, 0, defaultdict(int)])
pool = defaultdict(lambda: [0, 0])
for k in range(5):
    for _, t, y, p, d in stu[k]:
        if y == 1:
            pool[d][0] += p >= thr[k]
            pool[d][1] += 1
            if k == 4:
                by[d][0] += p >= thr[4]
                by[d][1] += 1
                by[d][2][t] += 1
for d, (tp, n, tc) in sorted(by.items(), key=lambda kv: -kv[1][1]):
    a = wilson(tp, n)
    print(f"| {d} | {n} | {tc['light']} · {tc['medium']} · {tc['dark']} | {tp / n:.3f} [{a[0]:.3f}; {a[1]:.3f}] "
          f"| {pool[d][0] / pool[d][1]:.3f} |")

print("\n## (2) AUC từng chẩn đoán so với toàn bộ ảnh lành (không phụ thuộc ngưỡng), trung bình 5 fold\n")
print("| Chẩn đoán | AUC student P0 | AUC teacher efficientnetv2_m | AUC teacher convnextv2_base |")
print("|---|---|---|---|")
for d in sorted(by, key=lambda d: -by[d][1]):
    s_auc = sum(auc([p for *_, y, p, dd in stu[k] if y == 1 and dd == d], [p for *_, y, p, dd in stu[k] if y == 0])
                for k in range(5)) / 5
    t_auc = sum(auc([p for *_, y, p, dd in tea[k] if y == 1 and dd == d], [p for *_, y, p, dd in tea[k] if y == 0])
                for k in range(5)) / 5
    t2_auc = sum(auc([p for *_, y, p, dd in tea2[k] if y == 1 and dd == d], [p for *_, y, p, dd in tea2[k] if y == 0])
                 for k in range(5)) / 5
    print(f"| {d} | {s_auc:.3f} | {t_auc:.3f} | {t2_auc:.3f} |")

print("\n## (3) III-b của P0 (fold 4) khi bỏ một số chẩn đoán khỏi nhóm ác — CHỈ CHẨN ĐOÁN, không phải cổng\n")
print("| Bỏ khỏi nhóm ác | Độ nhạy sáng · trung bình · tối [Wilson 95%] | n ác còn lại |")
print("|---|---|---|")
DROPS = {
    "không bỏ (III-b hiện hành)": set(),
    "actinic keratosis": {"actinic keratosis"},
    "mycosis fungoides + kaposi sarcoma": {"mycosis fungoides", "kaposi sarcoma"},
    "cả ba": {"actinic keratosis", "mycosis fungoides", "kaposi sarcoma"},
}
for name, drop in DROPS.items():
    cells, ns = [], []
    for g in TONES:
        pos = [p for _, t, y, p, d in stu[4] if t == g and y == 1 and d not in drop]
        tp = sum(p >= thr[4] for p in pos)
        a = wilson(tp, len(pos))
        cells.append(f"{tp / len(pos):.3f} [{a[0]:.3f}; {a[1]:.3f}]")
        ns.append(str(len(pos)))
    print(f"| {name} | " + " · ".join(cells) + f" | {' · '.join(ns)} |")
