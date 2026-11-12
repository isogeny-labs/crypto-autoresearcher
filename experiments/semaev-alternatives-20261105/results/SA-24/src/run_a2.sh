#!/bin/bash
# A2 splitting law, genus 2; sequential, resumable (a finished cell file is skipped)
cd /home/user/semaev-runs/SA-24
for k in 12 16 20 24; do for idx in 0 1 2; do
  out=results/a2_${k}_${idx}.jsonl; [ -s $out ] && continue
  L=$(grep "^A2 $k $idx " work/params.txt | cut -d' ' -f2-)
  echo "$(date +%T) A2 k=$k idx=$idx load=$(cut -d' ' -f1 /proc/loadavg)" >> logs/run_a2.log
  nice -n 10 ./src/split 2 sample 2000000000 $((24000+k*10+idx)) 100 0.3,0.4,0.5,0.6,0.7,0.8,0.9 A2 $L > $out.tmp 2>> logs/run_a2.log && echo "{\"done\":1,\"load_end\":\"$(cut -d' ' -f1-3 /proc/loadavg)\"}" >> $out.tmp && mv $out.tmp $out
done; done
echo "$(date +%T) A2 ALL DONE" >> logs/run_a2.log
