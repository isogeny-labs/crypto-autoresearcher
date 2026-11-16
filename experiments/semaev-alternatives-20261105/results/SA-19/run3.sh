#!/bin/bash
cd /home/user/semaev-runs/SA-19
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
D="0.04,0.05,0.055,0.06,0.065,0.07,0.075,0.08,0.09,0.1"
nice -n 10 timeout 900 python3 lattice19.py multi sym:8 64 20 $D 301 >> results/lattice_multi.log 2>&1
nice -n 10 timeout 900 python3 lattice19.py multi sym:8 96 20 $D 302 >> results/lattice_multi.log 2>&1
nice -n 10 timeout 900 python3 lattice19.py multi sym:6 96 20 $D 303 >> results/lattice_multi.log 2>&1
echo CHAIN3_DONE >> results/lattice_multi.log
