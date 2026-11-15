#!/bin/bash
cd /home/user/semaev-runs/SA-25
for p in "$@"; do
  if [ -f logs/done_$p ]; then continue; fi
  nice -n 10 python3 src/sa25.py stage1 $p > logs/stage1_$p.log 2> logs/stage1_$p.err && touch logs/done_$p
done
echo LISTDONE
