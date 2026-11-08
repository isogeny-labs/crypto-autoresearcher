#!/bin/bash
# rho (W and E curves) and IC-pair (W curves), all sizes, 3 curves x 5 targets. Sequential, nice 10, single thread.
cd /home/user/semaev-runs/SA-21
for k in 20 22 24 26 28 30 32 34 36 38 40; do
  echo "== k=$k $(date +%T) $(uptime | sed 's/.*load/load/')" >> results/batches.log
  for idx in 0 1 2; do
    for fam in W E; do
      nice -n 10 ./ic curves.txt $fam $k $idx rho 5 $((1000+k*10+idx)) -tmax 300 >> results/rho.jsonl
    done
    F=$(python3 -c "print(max(8,int(0.5*2**($k/3))))")
    Wb=256; if [ $k -le 24 ]; then Wb=64; fi
    nice -n 10 ./ic curves.txt W $k $idx pair 5 $((2000+k*10+idx)) -F $F -W $Wb -tmax 600 >> results/pair.jsonl
  done
done
echo "done $(date +%T)" >> results/batches.log
