#!/bin/bash
# A1 + rho + bench, resumable per (k,idx). usage: run_a1.sh "k list" deltas
cd /home/user/semaev-runs/SA-24
KS="$1"; D="$2"
for k in $KS; do for idx in 0 1 2; do
  out=results/a1_${k}_${idx}.jsonl; [ -s $out ] && continue
  { ./src/a1 bench $k $idx 1 24; nice -n 10 ./src/a1 rho $k $idx 5 24; nice -n 10 ./src/a1 a1 $k $idx 3 24 $D; ./src/a1 bench $k $idx 1 24; } > $out.tmp 2>> logs/run_a1.log && echo "{\"done\":1}" >> $out.tmp && mv $out.tmp $out
  echo "$(date +%T) a1 k=$k idx=$idx done load=$(cut -d' ' -f1 /proc/loadavg)" >> logs/run_a1.log
done; done
