#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/user/semaev-runs/SA-16
r() { nice -n 10 timeout 600 python3 run_sweep.py "$@"; }
r C3 128 20 6 22 2 raw/C3_128.json > raw/C3_128.log 2>&1
r G 96 12 6 18 2 raw/G_96.json > raw/G_96.log 2>&1
r Gp 96 12 6 18 2 raw/Gp_96.json > raw/Gp_96.log 2>&1
r C2 96 12 6 28 2 raw/C2_96.json > raw/C2_96.log 2>&1
r C1 96 12 6 36 2 raw/C1_96.json > raw/C1_96.log 2>&1
r C3 96 12 6 18 2 raw/C3_96.json > raw/C3_96.log 2>&1
r ENUM 128 5 6 16 1 raw/ENUM_128.json > raw/ENUM_128.log 2>&1
nice -n 10 timeout 900 python3 smart_oracle.py 128 6 12 10 10 raw/smart_128.json > raw/smart_128.log 2>&1
echo ALLDONE > raw/ALLDONE
