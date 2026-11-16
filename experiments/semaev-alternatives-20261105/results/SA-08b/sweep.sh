#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
D=0.06,0.08,0.10,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.20,0.22
for cfg in "48 1" "48 2" "48 3" "48 4" "96 1" "96 2" "96 3" "96 4" "64 1" "64 2" "64 3" "64 4" "64 5" "48 5" "48 6" "64 6"; do
  set -- $cfg
  nice -n 10 timeout 1500 python3 -I lam.py $1 $2 box 2 20 $D raw/box_$1_$2.json > raw/box_$1_$2.log 2>&1
  echo done $cfg $(date +%T)
done
for cfg in "48 2" "48 3" "48 4" "48 5" "64 3" "64 4"; do
  set -- $cfg
  nice -n 10 timeout 1200 python3 -I lam.py $1 $2 simplex 2 20 $D raw/simplex_$1_$2.json > raw/simplex_$1_$2.log 2>&1
  echo done simplex $cfg $(date +%T)
done
