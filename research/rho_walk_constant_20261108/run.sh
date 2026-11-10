#!/usr/bin/env bash
# Runs the registered grid of PROTOCOL.md (with Amendments 1 and 2).
# Usage: run.sh SIM_BINARY OUT_DIR [JOBS]
set -euo pipefail
SIM="$1"; OUT="$2"; JOBS="${3:-4}"
M=64
declare -A TRIALS=( [20]=4000 [24]=4000 [28]=3000 [32]=2000 [36]=1000 )
mkdir -p "$OUT"
{
for b in 20 24 28 32 36; do
  t=${TRIALS[$b]}
  for fam in 1 2; do
    echo "rm $b 0 $t $fam"
    echo "rm_plain $b 0 $t $fam"
    for r in 2 4 8 16 32 64 128 256 1024; do
      for arm in plain neg0 neg1 neg2; do echo "$arm $b $r $t $fam"; done
    done
  done
done
} | xargs -P "$JOBS" -L1 bash -c '
  arm=$0; b=$1; r=$2; t=$3; fam=$4
  f="'"$OUT"'/${arm}_b${b}_r${r}_f${fam}.txt"
  [ -s "$f" ] && exit 0
  "'"$SIM"'" "$arm" "$b" "$r" "$t" "$fam" '"$M"' > "$f.part" 2> "$f.err" && mv "$f.part" "$f"
'
