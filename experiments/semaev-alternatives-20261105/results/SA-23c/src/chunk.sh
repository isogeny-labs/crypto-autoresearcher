#!/bin/bash
# usage: chunk.sh p alo ahi dofb   (idempotent; writes work/c_p_alo_ahi.txt and appends results/chunks.jsonl)
cd /home/user/semaev-runs/SA-23c
p=$1; alo=$2; ahi=$3; fb=$4; f=work/c_${p}_${alo}_${ahi}_fb${fb}.txt
[ -f $f.done ] && exit 0
ld=$(cut -d' ' -f1 /proc/loadavg)
out=$(nice -n 10 ./src/enum_r2 $p 12 $f 6600 $alo $ahi $fb 2>>logs/enum.err); rc=$?
echo "{\"alo\":$alo,\"ahi\":$ahi,\"fb\":$fb,\"rc\":$rc,\"load_at_start\":$ld,\"out\":$out}" >> results/chunks_$p.jsonl
[ $rc -eq 0 ] && touch $f.done
