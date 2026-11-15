#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/user/semaev-runs/SA-17
while ! grep -q "q=7 n=64 st=4 2" grid.log; do sleep 10; done
# wait for that last cell to finish (next cell start or process end), then stop the original grid
while pgrep -f "run_cell.py 7 64 4 2" > /dev/null; do sleep 5; done
pkill -f grid.sh; sleep 1; pkill -f run_cell.py
echo "$(date +%T) grid.sh stopped after s=4; starting reduced s=5,6 grid" >> grid.log
for st in "6 3" "5 2"; do
 for n in 32 48 64; do
  for q in 3 7; do
   echo "$(date +%T) q=$q n=$n st=$st" >> grid.log
   nice -n 10 python3 -u run_cell.py $q $n $st 5 12 main >> grid.out 2>&1
  done
 done
done
echo ALLDONE >> grid.log
