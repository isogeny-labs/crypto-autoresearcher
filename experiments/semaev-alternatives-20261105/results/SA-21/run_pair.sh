#!/bin/bash
cd /home/user/semaev-runs/SA-21
OUT=${1:-results/pair.jsonl}; rm -f $OUT
for k in 20 22 24 26 28 30 32 34 36 38 40; do
  echo "pair k=$k $(date +%T) $(uptime | sed 's/.*load/load/')" >> results/batches.log
  for idx in 0 1 2; do
    F=$(python3 -c "print(max(8,int(0.5*2**($k/3))))")
    Wb=256; if [ $k -le 24 ]; then Wb=64; fi
    nice -n 10 ./ic curves.txt W $k $idx pair 5 $((2000+k*10+idx)) -F $F -W $Wb -tmax 600 >> $OUT
  done
done
