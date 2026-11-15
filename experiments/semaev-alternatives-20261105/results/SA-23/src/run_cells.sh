#!/bin/bash
# usage: run_cells.sh "d:p d:p ..." ; appends to results/cells.jsonl
cd /home/user/semaev-runs/SA-23
for cp in $1; do d=${cp%%:*}; p=${cp##*:}; chi=$((d/6))
  if grep -q "\"p\": $p, \"d\": $d," results/cells.jsonl 2>/dev/null; then continue; fi
  echo "$(date +%T) start d=$d p=$p load=$(cut -d' ' -f1 /proc/loadavg)" >> logs/driver.log
  out=$(nice -n 10 ./src/enum_c$chi $p $d work/s_${p}_${d}.txt 7200 2>>logs/enum.err); rc=$?
  echo "$out" >> logs/enum.log
  if [ $rc -ne 0 ]; then echo "$out" >> results/incomplete.jsonl; continue; fi
  sec=$(echo "$out" | python3 -c "import sys,json;print(json.load(sys.stdin)['enum_seconds'])")
  nice -n 10 python3 src/cell.py $p $d $sec "C exhaustive DFS (enum_c$chi)" >> results/cells.jsonl 2>>logs/cell.err
  echo "$(date +%T) done d=$d p=$p" >> logs/driver.log
done
