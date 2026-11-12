#!/bin/bash
# Part 2 A1-full, resumable per (k,idx). usage: run_p2.sh "k list"
cd /home/user/semaev-runs/SA-24c
CAP=150000000
for k in $1; do
  case $k in
    10|12|14|16|18) D=0.4,0.5,0.6,0.7,0.8,0.9;;
    20) D=0.55,0.65,0.75,0.85,0.9;;
    22) D=0.55,0.65,0.75,0.85,0.9;;
  esac
  for idx in 0 1 2; do
    out=results/p2_${k}_${idx}.jsonl; [ -s $out ] && continue
    { ./src/a1full bench $k $idx 1 24; nice -n 10 ./src/a1full full $k $idx 3 24 $D $CAP; ./src/a1full bench $k $idx 1 24; } > $out.tmp 2>> logs/run_p2.log && echo "{\"done\":1}" >> $out.tmp && mv $out.tmp $out
    echo "$(date +%T) p2 k=$k idx=$idx done load=$(cut -d' ' -f1 /proc/loadavg)" >> logs/run_p2.log
  done
done
echo "$(date +%T) P2 batch $1 DONE" >> logs/run_p2.log
