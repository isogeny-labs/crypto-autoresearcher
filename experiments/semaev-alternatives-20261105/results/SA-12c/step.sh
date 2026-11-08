#!/bin/bash
# usage: step.sh mode seed secs ; resumes, exits 0 when finished
cd /home/user/semaev-runs/SA-12c; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
[ -f out_$1_s$2.json ] && { echo done; exit 0; }
nice -n 10 timeout 590 python3 search3.py $1 $2 3000 $3 >> log_search.txt 2>&1
tail -1 log_search.txt
