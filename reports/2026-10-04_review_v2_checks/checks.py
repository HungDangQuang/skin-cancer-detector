"""Checks for review/REVIEW_DANH_GIA_V2_2026-10-04.md (report only). Stdlib only; run from the repo root:
    python3 reports/2026-10-04_review_v2_checks/checks.py reports/2026-10-04_review_v2_checks/fitz17kC_headline_image_ids.txt
or, from the original Fitzpatrick17k-C CSV (column md5hash), which also regenerates the id list:
    python3 reports/2026-10-04_review_v2_checks/checks.py <fitzpatrick17k-C csv> --write-ids

(1) III-b at the frozen app threshold on Fitzpatrick17k headline: full set vs the subset that survives the
    Fitzpatrick17k-C cleaning (Abhishek, Jain & Hamarneh, Sci Data 12:196, 2025 — near-duplicates and erroneous images
    removed). Matched on md5 (our image_id = "fitz_<md5>"). P0, P1, P2 at their own fold-4 `pad_sens90` threshold.
(2) D4: the ROC operating point at specificity >= 0.60 per tone (best sensitivity, same rule as
    src/evaluation/metrics.py::sensitivity_at_specificity), fold 4, with a row bootstrap (B = 1000, seed 42).
(3) D6: exact power of the gate "Wilson 95% lower bound >= m" for n cases at true rate p (binomial sum, no
    simulation noise); smallest n with power >= 0.80.
"""
import csv
import math
import random
import sys

SRC = sys.argv[1]
EXT = "reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline"
CANDS = {
    "P0": ("kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp", "reports/2026-10-02_threshold_options/summary.csv"),
    "P1": ("kd_convnextv2_base_to_mobilenetv4_conv_medium__srcsamp", "reports/2026-10-04_round2_app_threshold/P1/summary.csv"),
    "P2": ("kd_efficientnetv2_m_to_repvit_m1_0__srcsamp", "reports/2026-10-04_round2_app_threshold/P2/summary.csv"),
}
TONES = ["light", "medium", "dark"]
FOLD = 4
Z = 1.959964


def wilson(k, n):
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return c - h, c + h


def sens_at_spec(pos, neg, s):
    if not pos or not neg:
        return float("nan")
    n = len(neg)
    desc = sorted(neg, reverse=True)
    kmax = max(fp for fp in range(n + 1) if 1.0 - fp / n >= s)
    if kmax >= n:
        return 1.0
    return sum(p > desc[kmax] for p in pos) / len(pos)


def pct(v, q):
    v = sorted(x for x in v if x == x)
    i = q * (len(v) - 1)
    lo, hi = int(i), min(int(i) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


if SRC.endswith(".csv"):
    keep = {r["md5hash"] for r in csv.DictReader(open(SRC))}
else:  # fitz17kC_headline_image_ids.txt — image_id = "fitz_<md5>"
    keep = {l.strip().removeprefix("fitz_") for l in open(SRC) if l.strip()}
if "--write-ids" in sys.argv:
    ids = sorted(r["image_id"] for r in csv.DictReader(open(f"{EXT}/{CANDS['P0'][0]}/fold_0/predictions.csv"))
                 if r["image_id"].removeprefix("fitz_") in keep)
    open("reports/2026-10-04_review_v2_checks/fitz17kC_headline_image_ids.txt", "w").write("\n".join(ids) + "\n")

print("## (1) III-b tại ngưỡng app, fold 4: toàn bộ headline vs tập còn lại sau Fitzpatrick17k-C\n")
print("| Ứng viên | Tập | Tông | n ác / n lành | Độ nhạy [Wilson 95%] | Độ đặc hiệu [Wilson 95%] |")
print("|---|---|---|---|---|---|")
for name, (run, summary) in CANDS.items():
    thr = next(float(r["threshold"]) for r in csv.DictReader(open(summary))
               if r["rule"] == "pad_sens90" and int(r["fold"]) == FOLD)
    rows = [(r["tone_group"], int(float(r["y_true"])), float(r["y_prob"]), r["image_id"].replace("fitz_", "") in keep)
            for r in csv.DictReader(open(f"{EXT}/{run}/fold_{FOLD}/predictions.csv"))]
    for subset, sel in (("toàn bộ", lambda r: True), ("Fitz17k-C", lambda r: r[3])):
        for g in TONES:
            pos = [p for t, y, p, k in rows if t == g and y == 1 and sel((t, y, p, k))]
            neg = [p for t, y, p, k in rows if t == g and y == 0 and sel((t, y, p, k))]
            tp, tn = sum(p >= thr for p in pos), sum(p < thr for p in neg)
            a, b = wilson(tp, len(pos)), wilson(tn, len(neg))
            print(f"| {name} | {subset} | {g} | {len(pos)} / {len(neg)} | {tp / len(pos):.3f} [{a[0]:.3f}; {a[1]:.3f}] "
                  f"| {tn / len(neg):.3f} [{b[0]:.3f}; {b[1]:.3f}] |")

print("\n## (2) D4 — độ nhạy tốt nhất tại độ đặc hiệu ≥ 0,60, P0 fold 4 (bootstrap theo dòng, B = 1000)\n")
print("| Tập | Tông | sens@60spec [95%] | sens@80spec [95%] |")
print("|---|---|---|---|")
run = CANDS["P0"][0]
rows = [(r["tone_group"], int(float(r["y_true"])), float(r["y_prob"]), r["image_id"].replace("fitz_", "") in keep)
        for r in csv.DictReader(open(f"{EXT}/{run}/fold_{FOLD}/predictions.csv"))]
for subset, data in (("toàn bộ", rows), ("Fitz17k-C", [r for r in rows if r[3]])):
    rng = random.Random(42)
    reps = [[data[rng.randrange(len(data))] for _ in range(len(data))] for _ in range(1000)]
    for g in TONES:
        out = []
        for s in (0.60, 0.80):
            f = lambda d: sens_at_spec([p for t, y, p, _ in d if t == g and y == 1],
                                       [p for t, y, p, _ in d if t == g and y == 0], s)
            v = [f(d) for d in reps]
            out.append(f"{f(data):.3f} [{pct(v, .025):.3f}; {pct(v, .975):.3f}]")
        print(f"| {subset} | {g} | " + " | ".join(out) + " |")


def power(n, p, m):
    """P(Wilson lower bound of Binomial(n, p) >= m), exact."""
    lg = math.lgamma
    return sum(math.exp(lg(n + 1) - lg(k + 1) - lg(n - k + 1) + k * math.log(p) + (n - k) * math.log(1 - p))
               for k in range(n + 1) if wilson(k, n)[0] >= m) if n else 0.0


def min_n(p, m, target=0.80, start=10, stop=6000):
    for n in range(start, stop):
        if power(n, p, m) >= target:
            return n
    return None


print("\n## (3) D6 — cỡ mẫu cho cổng \"cận dưới Wilson 95% ≥ mốc\", power chính xác (tổng nhị thức)\n")
print("| Mốc | Tỉ lệ thật | n nhỏ nhất có power ≥ 0,80 | power tại n reviewer ước tính |")
print("|---|---|---|---|")
for m, p, n_rev in ((0.80, 0.87, 180), (0.80, 0.85, 400), (0.80, 0.83, 1200), (0.60, 0.73, 90)):
    n = min_n(p, m)
    print(f"| {m:.2f} | {p:.2f} | {n} | {power(n_rev, p, m):.3f} (n = {n_rev}) |")
print("\nGhi chú: power theo n có dạng răng cưa (rời rạc) — n lớn hơn một chút đôi khi power thấp hơn.")

# III-a needs BOTH cells (sensitivity AND specificity); the two samples are disjoint, so joint power = product.
pa, pb = power(218, 0.87, 0.80), power(99, 0.73, 0.60)
print(f"\nPower chung III-a với 218 ca ác + 99 ca lành: {pa:.4f} × {pb:.4f} = {pa * pb:.4f}")
t = math.sqrt(0.80)
na, nb = min_n(0.87, 0.80, t, start=200), min_n(0.73, 0.60, t, start=90)
print(f"Power chung 0,80 cần mỗi ô ≥ {t:.4f}: {na} ca ác (power {power(na, 0.87, 0.80):.4f}) + {nb} ca lành "
      f"(power {power(nb, 0.73, 0.60):.4f}) ⇒ chung {power(na, 0.87, 0.80) * power(nb, 0.73, 0.60):.4f}")


def stable(p, m, target, n0, window=60):
    while any(power(n, p, m) < target for n in range(n0, n0 + window)):
        n0 += 1
    return n0


print(f"Răng cưa: n nhỏ nhất mà 60 giá trị n liền sau đều có power ≥ 0,80 — độ nhạy (0,87 vs 0,80): "
      f"{stable(0.87, 0.80, 0.80, 218)}; độ đặc hiệu (0,73 vs 0,60): {stable(0.73, 0.60, 0.80, 99)}")


# (4) D2 as REPORT ONLY: sens@spec80 per tone, mean of the 5 folds of P0 (row bootstrap B = 1000, one index set per
# replicate scored on every fold, as scripts/bootstrap_ci.py does), vs the clinician reference on clinical photos 0.47.
print("\n## (4) D2 (chỉ báo cáo) — sens@spec80 theo tông, trung bình 5 fold P0, so với mốc bác sĩ 0,47\n")
print("| Tập | Tông | sens@80spec TB 5 fold [95%] | so với 0,47 |")
print("|---|---|---|---|")
run = CANDS["P0"][0]
folds = []
for k in range(5):
    folds.append([(r["tone_group"], int(float(r["y_true"])), float(r["y_prob"]), r["image_id"].replace("fitz_", "") in keep)
                  for r in csv.DictReader(open(f"{EXT}/{run}/fold_{k}/predictions.csv"))])
ids0 = [r["image_id"] for r in csv.DictReader(open(f"{EXT}/{run}/fold_0/predictions.csv"))]
for k in range(1, 5):  # rows must be aligned across folds for a shared bootstrap index
    assert [r["image_id"] for r in csv.DictReader(open(f"{EXT}/{run}/fold_{k}/predictions.csv"))] == ids0
for subset in ("toàn bộ", "Fitz17k-C"):
    idx_all = [i for i in range(len(ids0)) if subset == "toàn bộ" or folds[0][i][3]]
    rng = random.Random(42)
    reps = [[idx_all[rng.randrange(len(idx_all))] for _ in range(len(idx_all))] for _ in range(1000)]
    for g in TONES:
        def stat(ix):
            return sum(sens_at_spec([folds[k][i][2] for i in ix if folds[k][i][0] == g and folds[k][i][1] == 1],
                                    [folds[k][i][2] for i in ix if folds[k][i][0] == g and folds[k][i][1] == 0], 0.80)
                       for k in range(5)) / 5
        v = [stat(ix) for ix in reps]
        pt, lo, hi = stat(idx_all), pct(v, .025), pct(v, .975)
        rel = "trên (cả khoảng > 0,47)" if lo > 0.47 else ("dưới (cả khoảng < 0,47)" if hi < 0.47 else "cắt qua 0,47")
        print(f"| {subset} | {g} | {pt:.4f} [{lo:.4f}; {hi:.4f}] | {rel} |")
