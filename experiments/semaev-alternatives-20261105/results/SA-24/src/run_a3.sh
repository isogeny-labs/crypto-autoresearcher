#!/bin/bash
cd /home/user/semaev-runs/SA-24
for k in 12 16 20; do for idx in 0 1 2; do
  out=results/a3_${k}_${idx}.jsonl; [ -s $out ] && continue
  L=$(grep "^A3 $k $idx " work/params.txt | cut -d' ' -f2-)
  echo "$(date +%T) A3 k=$k idx=$idx load=$(cut -d' ' -f1 /proc/loadavg)" >> logs/run_a3.log
  nice -n 10 ./src/split 3 sample 100000000 $((34000+k*10+idx)) 100 0.5,0.6,0.7,0.8,0.9 A3 $L > $out.tmp 2>> logs/run_a3.log && echo "{\"done\":1,\"load_end\":\"$(cut -d' ' -f1-3 /proc/loadavg)\"}" >> $out.tmp && mv $out.tmp $out
done; done
echo "$(date +%T) A3 ALL DONE" >> logs/run_a3.log
