#!/bin/bash
cd /home/user/semaev-runs/SA-19
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
D="0.09,0.095,0.1,0.105,0.11,0.115,0.12,0.125,0.13,0.135,0.14,0.145,0.15,0.16"
for bits in 64 96 128; do
  for name in edwards_y weierstrass_x; do
    nice -n 10 timeout 900 python3 lattice19.py coord $name $bits 40 $D $((bits+7)) >> results/lattice.log 2>&1
  done
done
nice -n 10 timeout 1500 python3 search_c.py > results/search_c.log 2>&1
nice -n 10 timeout 900 python3 m3.py > results/m3.log 2>&1
nice -n 10 timeout 900 python3 coords3.py > results/coords3.log 2>&1
echo CHAIN_DONE >> results/lattice.log
