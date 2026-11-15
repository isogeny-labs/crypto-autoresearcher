#!/bin/bash
export OMP_NUM_THREADS=1 RED=1
cd /home/user/semaev-runs/SA-14b
python3 drv3.py 3 "[1,2,3,4,5,6]" "[1,2]" 1 0 1500 >> out/m3.txt 2>&1
python3 drv3.py 3 "[1,2,3,4,5,6]" "[1]" 1 1 1500 >> out/m3_null.txt 2>&1
