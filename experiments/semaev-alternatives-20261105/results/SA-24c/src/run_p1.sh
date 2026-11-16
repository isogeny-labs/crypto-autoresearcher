#!/bin/bash
# Part 1 production, sequential and resumable (finished cell file skipped)
cd /home/user/semaev-runs/SA-24c
run() { # name mode args...
  out=results/$1.jsonl; shift; [ -s $out ] && return
  echo "$(date +%T) $out load=$(cut -d' ' -f1 /proc/loadavg)" >> logs/run_p1.log
  nice -n 10 "$@" > $out.tmp 2>> logs/run_p1.log && echo "{\"done\":1,\"load_end\":\"$(cut -d' ' -f1-3 /proc/loadavg)\"}" >> $out.tmp && mv $out.tmp $out
}
for cell in "20 0.3 67" "24 0.4 67" "24 0.5 340" "24 0.3 67"; do set -- $cell; for idx in 0 1 2; do
  L=$(grep "^A2 $1 $idx " work/params.txt)
  run f2_$1_$2_$idx ./src/filt filt2 2 $((52000+$1*10+idx)) $2 $3 100 -- $L
done; done
for cell in "16 0.5 67" "20 0.6 67" "20 0.5 67"; do set -- $cell; for idx in 0 1 2; do
  L=$(grep "^A3 $1 $idx " work/params.txt)
  run f3_$1_$2_$idx ./src/filt filt3 3 $((53000+$1*10+idx)) $2 $3 100 20000000 -- $L
done; done
for k in 20 24; do for idx in 0 1 2; do L=$(grep "^A2 $k $idx " work/params.txt); run den2_${k}_$idx ./src/filt den 2 $((54000+k*10+idx)) 1000000000 100 -- $L; done; done
for k in 16 20; do for idx in 0 1 2; do L=$(grep "^A3 $k $idx " work/params.txt); run den3_${k}_$idx ./src/filt den 3 $((55000+k*10+idx)) 300000000 100 -- $L; done; done
echo "$(date +%T) P1 ALL DONE" >> logs/run_p1.log
