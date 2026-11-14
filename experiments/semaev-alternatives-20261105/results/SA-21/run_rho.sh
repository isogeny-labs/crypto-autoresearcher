#!/bin/bash
cd /home/user/semaev-runs/SA-21
rm -f results/rho.jsonl
for k in 20 22 24 26 28 30 32 34 36 38 40; do
  echo "rho k=$k $(date +%T) $(uptime | sed 's/.*load/load/')" >> results/batches.log
  for idx in 0 1 2; do for fam in W E; do
      nice -n 10 ./ic curves.txt $fam $k $idx rho 5 $((1000+k*10+idx)) -tmax 300 >> results/rho.jsonl
  done; done
done
