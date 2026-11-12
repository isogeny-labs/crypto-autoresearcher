#!/bin/bash
cd /home/user/semaev-runs/SA-25
for p in "$@"; do
  nice -n 10 python3 src/e2e.py $p 10 > logs/e2e_$p.log 2> logs/e2e_$p.err
done
echo E2EDONE
