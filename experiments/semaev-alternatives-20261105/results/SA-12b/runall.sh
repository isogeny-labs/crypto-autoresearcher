#!/bin/bash
cd /home/user/semaev-runs/SA-12b
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for s in 0 1 2; do for m in convex full; do
 nice -n 10 timeout 1500 python3 search2.py $m $s 1200 >> log_search.txt 2>&1
done; done
nice -n 10 timeout 600 python3 grid_convex.py 300 >> log_grid.txt 2>&1
touch done.flag
