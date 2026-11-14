#!/bin/bash
cd /home/user/semaev-runs/SA-19
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nice -n 10 timeout 900 python3 coords3.py > results/coords3.log 2>&1
nice -n 10 timeout 1500 python3 search_c.py > results/search_c.log 2>&1
D="0.06,0.07,0.08,0.085,0.09,0.095,0.1,0.105,0.11,0.12"
nice -n 10 timeout 900 python3 lattice19.py multi box:2 64 20 $D 201 >> results/lattice_multi.log 2>&1
nice -n 10 timeout 900 python3 lattice19.py multi box:2 96 20 $D 202 >> results/lattice_multi.log 2>&1
nice -n 10 timeout 900 python3 lattice19.py multi tot:6 96 20 0.04,0.05,0.055,0.06,0.065,0.07,0.08 203 >> results/lattice_multi.log 2>&1
echo CHAIN2_DONE >> results/lattice_multi.log
