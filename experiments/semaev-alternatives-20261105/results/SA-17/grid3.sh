#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/user/semaev-runs/SA-17
while ! grep -q ALLDONE grid.log; do sleep 20; done
for nq in "3 32" "3 48" "3 64" "5 32" "5 48" "7 32" "7 48"; do
  echo "$(date +%T) m3 $nq" >> grid.log
  nice -n 10 python3 -u run3.py $nq 6 >> grid3.out 2>&1
done
echo ALLDONE3 >> grid.log
