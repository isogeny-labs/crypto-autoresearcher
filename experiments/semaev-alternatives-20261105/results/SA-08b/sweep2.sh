#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
D=0.06,0.08,0.10,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.20,0.22
for cfg in "96 3" "96 4"; do set -- $cfg
  nice -n 10 timeout 900 python3 -I lam.py $1 $2 box 2 20 $D raw/box_$1_$2.json > raw/box_$1_$2.log 2>&1; echo done $cfg $(date +%T); done
for cfg in "48 2" "48 3" "48 4" "48 5"; do set -- $cfg
  nice -n 10 timeout 600 python3 -I lam.py $1 $2 simplex 2 20 $D raw/simplex_$1_$2.json > raw/simplex_$1_$2.log 2>&1; echo done simplex $cfg $(date +%T); done
nice -n 10 timeout 1500 python3 -I lam.py 64 6 box 1 20 0.12,0.13,0.14,0.15,0.16 raw/box_64_6.json > raw/box_64_6.log 2>&1; echo done 64 6 $(date +%T)
