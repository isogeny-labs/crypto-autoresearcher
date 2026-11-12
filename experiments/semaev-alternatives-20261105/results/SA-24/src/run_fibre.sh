#!/bin/bash
cd /home/user/semaev-runs/SA-24
for k in 12 16 20 24; do for idx in 0 1 2; do
  out=results/fibre_${k}_${idx}.jsonl; [ -s $out ] && continue
  L=$(grep "^A2 $k $idx " work/params.txt | cut -d' ' -f2-)
  nice -n 10 ./src/split 2 fibre 200000000 $((44000+k*10+idx)) 1 0.3,0.4,0.5,0.6,0.7,0.8,0.9 A2 $L > $out.tmp && mv $out.tmp $out
done; done
echo "$(date +%T) FIBRE DONE" >> logs/run_a3.log
