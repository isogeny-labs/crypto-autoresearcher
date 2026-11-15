#!/bin/bash
# usage: fin.sh p  -> verifies all chunks present (done files), counts sections, runs Gram
cd /home/user/semaev-runs/SA-23c; p=$1
n=$(ls work/c_${p}_*.done | wc -l); echo "chunks done: $n"
cat work/c_${p}_*.txt > work/s_${p}_12_all.txt
echo "dup lines: $(sort work/s_${p}_12_all.txt | uniq -d | wc -l)  lines: $(wc -l < work/s_${p}_12_all.txt)"
python3 - <<P
import json
rs=[json.loads(l) for l in open('results/chunks_$p.jsonl')]
print("rc all 0:",all(r['rc']==0 for r in rs),"n",len(rs),"sum_sections",sum(r['out']['num_integral_sections'] for r in rs),"enum_seconds",round(sum(r['out']['enum_seconds'] for r in rs)),"loads",min(r['load_at_start'] for r in rs),max(r['load_at_start'] for r in rs))
P
nice -n 10 python3 src/cellb.py $p 12 work/s_${p}_12_all.txt | tee -a results/gram_new.jsonl
