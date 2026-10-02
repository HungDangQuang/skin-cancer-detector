#!/usr/bin/env bash
# Threshold options for the binary app (D2), 02/10/2026. Mac-side, bash + awk only.
#
# Ship candidate: __srcsamp, best_model_auprc.pth. Every threshold is chosen on the VAL rows
# (never on test); each rule is then applied unchanged to
#   (a) TEST PAD-UFES-20 rows (in-domain phone photos) — already SEEN at 3 operating points on
#       2026-10-01 (reports/2026-10-01_pad_threshold/), so any choice made from this table is post-hoc;
#   (b) Fitzpatrick17k headline (clinical photos, never used to choose anything — but the
#       pad_sens90 row was seen on 2026-10-01 as well);
#   (c) TEST ISIC rows (3D-TBP crops — not what the app's camera sees; for reference).
# Rules (all on val):
#   global_youden  Youden's J on ALL val rows (what val_metrics_auprc.json stores)
#   pad_youden     Youden's J on the val PAD rows only
#   pad_sensXX     highest threshold keeping val-PAD sensitivity >= XX%
#   pad_specXX     lowest threshold giving val-PAD specificity >= XX%
# Output: summary.csv (one row per fold x rule) next to this script.
set -euo pipefail
cd "$(dirname "$0")/../.."
OUT=reports/2026-10-02_threshold_options
W=${W:-$(pwd)/.tmp/thropt}
mkdir -p "$W"
RUN=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp
FITZ=reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp

count() {  # $1 file (y_true,prob), $2 threshold -> "tp m fp b"
    awk -F, -v t="$2" '{ if ($1==1) { m++; if ($2>=t) tp++ } else { b++; if ($2>=t) fp++ } }
        END { printf "%d %d %d %d", tp+0, m+0, fp+0, b+0 }' "$1"
}
sens_thr() {  # $1 file, $2 target sensitivity -> highest t with sens >= target
    awk -F, '$1==1{print $2}' "$1" | sort -g \
      | awk -v s="$2" '{a[NR]=$1} END{k=int(NR*(1-s))+1; if (k<1) k=1; printf "%.10g", a[k]}'
}
spec_thr() {  # $1 file, $2 target specificity -> lowest t with spec >= target
    awk -F, '$1==0{print $2}' "$1" | sort -g \
      | awk -v s="$2" '{a[NR]=$1} END{k=int(NR*s); if (k*1.0 < NR*s) k++; if (k>=NR) {printf "%.10g", a[NR]+1e-9} else {printf "%.10g", a[k+1]}}'
}
youden_thr() {  # $1 file -> t maximising sens+spec-1 over the observed scores
    sort -t, -k2,2g "$1" | awk -F, '{y[NR]=$1; p[NR]=$2; if ($1==1) M++; else B++}
        END { tp=M; fp=B; best=-1;
              for (i=1;i<=NR;i++) { j=(tp/M)+(1-fp/B)-1; if (j>best) {best=j; bt=p[i]}
                                    if (y[i]==1) tp--; else fp-- }
              printf "%.10g", bt }'
}

echo "fold,rule,threshold,val_tp,val_pos,val_fp,val_neg,pad_tp,pad_pos,pad_fp,pad_neg,fitz_tp,fitz_pos,fitz_fp,fitz_neg,isic_tp,isic_pos,isic_fp,isic_neg" > $W/summary.csv
for k in 0 1 2 3 4; do
    R=$RUN/fold_$k
    paste -d, <(tr -d '\r' < $R/val_predictions_auprc.csv) <(tr -d '\r' < data/splits/isic2024/fold_$k/val_split.csv | cut -d, -f4,6) \
      | awk -F, 'NR>1 { if ($1!=$4) bad++; if ($5=="pad_ufes_20") print $1","$2 }
                 END { if (bad) { print "LABEL MISMATCH " bad > "/dev/stderr"; exit 3 } }' > $W/val_$k.csv
    tr -d '\r' < $R/predictions_auprc.csv | awk -F, 'NR>1 && $4=="pad_ufes_20" {print $1","$2}' > $W/pad_$k.csv
    tr -d '\r' < $R/predictions_auprc.csv | awk -F, 'NR>1 && $4=="isic2024" {print $1","$2}' > $W/isic_$k.csv
    tr -d '\r' < $FITZ/fold_$k/predictions.csv | awk -F, 'NR>1 {print $1","$2}' > $W/fitz_$k.csv
    rules="global_youden:$(jq -r .threshold $R/val_metrics_auprc.json)"
    rules="$rules pad_youden:$(youden_thr $W/val_$k.csv)"
    for s in 0.95 0.90 0.85; do rules="$rules pad_sens${s#0.}:$(sens_thr $W/val_$k.csv $s)"; done
    for s in 0.80 0.90; do rules="$rules pad_spec${s#0.}:$(spec_thr $W/val_$k.csv $s)"; done
    for rule in $rules; do
        n=${rule%%:*}; t=${rule#*:}
        line="$k,$n,$t"
        for f in val pad fitz isic; do line="$line,$(count $W/${f}_$k.csv $t | tr ' ' ',')"; done
        echo "$line" >> $W/summary.csv
    done
done
cp $W/summary.csv $OUT/summary.csv
echo "wrote $OUT/summary.csv ($(($(wc -l < $OUT/summary.csv)-1)) rows)"
