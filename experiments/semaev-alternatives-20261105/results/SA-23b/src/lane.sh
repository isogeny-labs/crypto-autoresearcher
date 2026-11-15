#!/bin/bash
# lane worker: take undone chunks from queue (mkdir lock), stop starting new ones after 85 min
cd /home/user/semaev-runs/SA-23b; t0=$(date +%s); lane=$1
while read p alo ahi fb; do
  [ $(( $(date +%s)-t0 )) -gt 5100 ] && break
  k=${p}_${alo}_${ahi}_fb${fb}; [ -f work/c_$k.txt.done ] && continue
  mkdir work/lock_$k 2>/dev/null || continue
  echo "$(date +%T) lane$lane start $k load=$(cut -d' ' -f1 /proc/loadavg)" >> logs/lanes.log
  src/chunk.sh $p $alo $ahi $fb
  [ -f work/c_$k.txt.done ] || rmdir work/lock_$k   # failed: release
  echo "$(date +%T) lane$lane end $k" >> logs/lanes.log
done < src/queue.txt
