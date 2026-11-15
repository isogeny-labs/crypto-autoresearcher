#!/bin/bash
export OMP_NUM_THREADS=1
cd /home/user/semaev-runs/SA-14b
for s in 2 3; do python3 drv.py 12289 2 10 $s 1 3000 >> out/t10_seeds.txt 2>&1; done
RED=0 python3 drv3.py 2 "[10]" "[1]" 1 1 3000 >> out/null_m2.txt 2>&1
