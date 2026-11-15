#!/bin/bash
for k in 28 32 36 40; do
 N13=$(python3 -c "print(int(2**($k/3)))")
 for kap in 0.125 0.25 0.35 0.5 0.7; do
  F=$(python3 -c "print(int($kap*$N13))")
  nice -n 10 ./ic curves.txt W $k 1 pair 4 9 -F $F -W 256 -tmax 300 | python3 -c "
import sys,json
rs=[json.loads(l) for l in sys.stdin]
import statistics as st
print($k,$kap,$F,'mean wall ms',round(1000*st.mean(r['wall'] for r in rs),2),'mean adds',int(st.mean(r['adds'] for r in rs)),'ok',sum(r['ok'] for r in rs),'rels',st.mean(r['relations_added'] for r in rs),'setup ms',round(1000*st.mean(r['t_setup'] for r in rs),1))
"
 done
done
