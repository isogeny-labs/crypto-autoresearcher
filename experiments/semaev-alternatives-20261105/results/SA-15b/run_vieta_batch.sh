#!/bin/bash
# usage: run_vieta_batch.sh log2p start end   (each instance under a 60 s wall cap)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
for i in $(seq $2 $(($3-1))); do
  out=$(timeout 60 nice -n 10 python3 vieta_lattice.py $1 $i 2>&1 | grep POST)
  if [ -z "$out" ]; then echo "{\"log2p\": $1, \"idx\": $i, \"timeout_or_error\": true}"; else echo "${out#POST }"; fi
done >> vieta_lattice_$1.jsonl
