#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/user/semaev-runs/SA-17
for st in "2 1" "3 1" "4 2" "5 2" "6 3"; do
 for n in 24 32 40 48 56 64; do
  for q in 3 5 7; do
   echo "$(date +%T) q=$q n=$n st=$st" >> grid.log
   nice -n 10 python3 -u run_cell.py $q $n $st 6 16 main >> grid.out 2>&1
  done
 done
done
echo ALLDONE >> grid.log
