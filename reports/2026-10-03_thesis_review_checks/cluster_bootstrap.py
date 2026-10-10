# Ước lượng THÔ, chỉ thư viện chuẩn: so CI bootstrap theo DÒNG (như bootstrap_ci.py) với theo BỆNH NHÂN.
# Thống kê = trung bình 5 fold (cùng quy ước repo). Không dùng hàm metric của repo.
import csv, random, sys, collections
D="experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp"
split=list(csv.DictReader(open("data/splits/isic2024/test_split.csv")))
probs=[]
for f in range(5):
    rows=list(csv.DictReader(open(f"{D}/fold_{f}/predictions_auprc.csv")))
    assert len(rows)==len(split)
    for r,s in zip(rows,split):
        assert int(float(r['y_true']))==int(s['label']) and r['source']==s['source']
    probs.append([float(r['y_prob']) for r in rows])
print("căn hàng predictions↔test_split: OK (59.093 dòng, nhãn + nguồn khớp 5/5 fold)")

def stats(idx_w, y, order_list):
    # idx_w: dict row->weight ; trả (auc, sens@spec80) trung bình fold
    aucs=[];sens=[]
    P=sum(w for i,w in idx_w.items() if y[i]);N=sum(w for i,w in idx_w.items() if not y[i])
    if P==0 or N==0: return None
    for order,score in order_list:
        tp=fp=0;auc=0.0;prev_tpr=prev_fpr=0.0;best=0.0;k=0;n=len(order)
        while k<n:
            s=score[order[k]];
            while k<n and score[order[k]]==s:
                i=order[k];w=idx_w.get(i,0)
                if w:
                    if y[i]: tp+=w
                    else: fp+=w
                k+=1
            tpr=tp/P;fpr=fp/N
            auc+=(fpr-prev_fpr)*(tpr+prev_tpr)/2
            if 1-fpr>=0.8: best=max(best,tpr)
            prev_tpr,prev_fpr=tpr,fpr
        aucs.append(auc);sens.append(best)
    return sum(aucs)/5, sum(sens)/5

def run(source,B,seed=42):
    rows=[i for i,s in enumerate(split) if s['source']==source]
    y={i:int(split[i]['label']) for i in rows}
    order_list=[]
    for p in probs:
        o=sorted(rows,key=lambda i:-p[i]); order_list.append((o,p))
    pts=stats({i:1 for i in rows},y,order_list)
    pat=collections.defaultdict(list)
    for i in rows: pat[split[i]['patient_id']].append(i)
    pids=list(pat)
    rng=random.Random(seed)
    res={'dòng':[], 'bệnh nhân':[]}
    for b in range(B):
        w=collections.Counter(rng.choice(rows) for _ in rows)
        r=stats(w,y,order_list); res['dòng'].append(r) if r else None
        w=collections.Counter()
        for _ in pids:
            for i in pat[rng.choice(pids)]: w[i]+=1
        r=stats(w,y,order_list); res['bệnh nhân'].append(r) if r else None
    def pct(v,q): v=sorted(v); return v[int(q*(len(v)-1))]
    print(f"\n{source}: {len(rows)} ảnh, {len(pids)} bệnh nhân, B={B}. Điểm: AUC {pts[0]:.4f}, sens@spec80 {pts[1]:.4f}")
    for k,v in res.items():
        a=[x[0] for x in v];s=[x[1] for x in v]
        print(f"  theo {k:9s}: AUC [{pct(a,.025):.4f}, {pct(a,.975):.4f}] rộng {pct(a,.975)-pct(a,.025):.4f} | sens@spec80 [{pct(s,.025):.4f}, {pct(s,.975):.4f}] rộng {pct(s,.975)-pct(s,.025):.4f}")
if int(sys.argv[1]): run('pad_ufes_20', int(sys.argv[1]))
run('isic2024', int(sys.argv[2]))
