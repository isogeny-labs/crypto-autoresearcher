#!/usr/bin/env bash
# Runner for EXP-PKM-RADIX-001 (PROTOCOL.md). Every cell and flag here is frozen
# by the protocol; change them only by a dated amendment.
#
#   run_cells.sh G0      regression against research/prime_fall_degree_t14_20261101 R-t9-t10
#   run_cells.sh L2      m=2 ladder, tower + null, radix 2/4/8
#   run_cells.sh L3      m=3 ladder, tower, radix 2/4/8
#   run_cells.sh X2      replication on p = 786433
#   run_cells.sh A1      determinism rerun of L2 radix-4 t=8 tower
#   run_cells.sh smoke   tiny cells for a build check (not study rows)
set -u
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../.." && pwd)
bin=${BIN:-$repo/target/release/examples/pkm_tower_pilot}
mkdir -p "$here/runs"
cd "$here/runs"
P1=2013265921
P0=786433
VMEM_KB=${VMEM_KB:-6500000}
THREADS=${THREADS:-2}
f4=(--budget 1800 --max-nnz 2000000000)
base=(--ladder-t none --random 2 --engine tower --kinds kummer)

if [ ! -f ../binary.sha256 ] || [ "${1:-}" = "G0" ]; then
  sha256sum "$bin" | awk '{print $1}' > ../binary.sha256
  git -C "$repo" rev-parse HEAD > ../commit.txt 2>/dev/null || true
  rustc -Vv > ../rustc.txt 2>/dev/null || true
fi

run() {
  name=$1
  shift
  echo "$(date -u +%FT%TZ) start $name: $*" >> ../progress.txt
  ( ulimit -v "$VMEM_KB"; RAYON_NUM_THREADS=$THREADS "$bin" "$@" --out "$name.jsonl" 2> "$name.log" )
  rc=$?
  echo "$(date -u +%FT%TZ) end $name exit $rc" >> ../progress.txt
}

# Arms in the frozen rotation: t even -> 2 4 8, t odd -> 8 4 2.
arms_for() { if [ $(( $1 % 2 )) -eq 0 ]; then echo "2 4 8"; else echo "8 4 2"; fi; }

case "${1:-}" in
  G0)
    run G0-t9-t10 --p $P1 "${base[@]}" --planted 0 --m 2 --controls tower "${f4[@]}" --t-min 9 --max-t 10
    ;;
  L2)
    for t in 4 5 6 7 8 9 10; do
      for r in $(arms_for $t); do
        run L2-t$t-r$r --p $P1 "${base[@]}" --planted 1 --planted-max-t 8 --m 2 --controls tower,null \
          "${f4[@]}" --t-min $t --max-t $t --radix $r
      done
    done
    ;;
  L3)
    for t in 3 4 5; do
      for r in $(arms_for $t); do
        run L3-t$t-r$r --p $P1 "${base[@]}" --planted 1 --planted-max-t 4 --m 3 --controls tower \
          "${f4[@]}" --t-min $t --max-t-m3 $t --radix $r
      done
    done
    ;;
  X2)
    for t in 6 8 10; do
      for r in $(arms_for $t); do
        run X2-t$t-r$r --p $P0 "${base[@]}" --planted 0 --m 2 --controls tower \
          "${f4[@]}" --t-min $t --max-t $t --radix $r
      done
    done
    ;;
  A1)
    run A1-t8-r4 --p $P1 "${base[@]}" --planted 1 --planted-max-t 8 --m 2 --controls tower,null \
      "${f4[@]}" --t-min 8 --max-t 8 --radix 4
    ;;
  smoke)
    mkdir -p ../smoke && cd ../smoke
    for r in 2 4 8; do
      ( ulimit -v "$VMEM_KB"; RAYON_NUM_THREADS=$THREADS "$bin" --p $P1 "${base[@]}" --planted 1 --m 2 \
          --controls tower,null --budget 120 --t-min 3 --max-t 4 --radix $r --out smoke-r$r.jsonl 2> smoke-r$r.log )
      echo "smoke radix $r exit $?"
    done
    ;;
  *)
    echo "usage: $0 G0|L2|L3|X2|A1|smoke" >&2
    exit 2
    ;;
esac
