#!/bin/bash
# small regime: n<=90 ; 3 seeds
cd /home/user/semaev-runs/SA-12
for m in ea sa random; do for md in convex full; do
 echo "NCAP=90 TAG=s nice -n 10 timeout 1700 python3 search.py $m $md 90 3 >> log_s_${m}_${md}.txt"
done; done > jobs_s.txt
