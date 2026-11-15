#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/user/semaev-runs/SA-17
for st in "2 1" "4 2" "6 3" "3 1"; do
 for n in 24 32 40 48 64; do
  for q in 3 5 7; do
   if [ "$st" = "6 3" ]; then
     if [ $n = 24 ] || [ $n = 40 ] || [ $q = 5 ]; then continue; fi
   fi
   echo "$(date +%T) q=$q n=$n st=$st" >> grid.log
   nice -n 10 python3 -u run_cell.py $q $n $st 5 12 v2 >> grid.out 2>&1
  done
 done
done
echo ALLDONE >> grid.log
for nq in "3 32" "3 48" "3 64" "7 32" "7 48"; do
  echo "$(date +%T) m3 $nq" >> grid.log
  nice -n 10 python3 -u run3.py $nq 5 >> grid3.out 2>&1
done
echo ALLDONE3 >> grid.log
