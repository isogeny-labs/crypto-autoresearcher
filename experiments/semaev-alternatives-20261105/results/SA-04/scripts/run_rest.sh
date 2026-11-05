#!/bin/bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/user/semaev-runs/SA-04/scripts
O=../out
# m=2 digit-coded: S_3 baseline to B=64, norm to B=16, null
nice -n 10 python3 sweep.py 2 S 2,4,8,16,32,64 3 real 16 400 $O/m2_S_real.jsonl
rm -f $O/m2_digit_real2.jsonl
nice -n 10 python3 sweep.py 2 digit 2,4,8,16 3 real 14 400 $O/m2_digit_real2.jsonl 
nice -n 10 python3 sweep.py 2 digit 2,4,8,16 3 null 14 400 $O/m2_digit_null.jsonl
# m=2 V baseline
nice -n 10 python3 sweep.py 2 SV 4,6,8,12,16,24,32,48,64 2 real 140 400 $O/m2_SV_real.jsonl
# m=3
nice -n 10 python3 sweep.py 3 S 4,8,16 3 real 16 400 $O/m3_S_real.jsonl
nice -n 10 python3 sweep.py 3 digit 4 3 real 14 600 $O/m3_digit_real.jsonl
nice -n 10 python3 sweep.py 3 digit 4 3 null 14 600 $O/m3_digit_null.jsonl
nice -n 10 python3 sweep.py 3 V 4,5,6,7,8 2 real 24 600 $O/m3_V_real.jsonl
nice -n 10 python3 sweep.py 3 SV 4,5,6,7,8,10,12 2 real 40 400 $O/m3_SV_real.jsonl
echo ALLDONE > $O/rest.done
