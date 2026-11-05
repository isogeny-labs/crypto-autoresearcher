#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/user/semaev-runs/SA-04/scripts; O=../out
nice -n 10 python3 sweep.py 3 S 4,8,16 3 real 16 400 $O/m3_S_real.jsonl
nice -n 10 python3 sweep.py 3 digit 4 3 real 14 600 $O/m3_digit_real.jsonl
nice -n 10 python3 sweep.py 3 digit 4 3 null 14 600 $O/m3_digit_null.jsonl
nice -n 10 python3 sweep.py 3 V 4,5,6 2 real 24 600 $O/m3_V_real.jsonl
nice -n 10 python3 sweep.py 3 SV 4,5,6,7,8,10,12 2 real 40 400 $O/m3_SV_real.jsonl
echo done > $O/m3.done
