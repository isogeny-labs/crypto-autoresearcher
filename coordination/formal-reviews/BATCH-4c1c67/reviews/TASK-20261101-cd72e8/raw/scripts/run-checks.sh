export ELAN_HOME=/dev/shm/j3/elan XDG_CACHE_HOME=/dev/shm/j3/xdg PATH=/dev/shm/j3/elan/bin:$PATH
cd /dev/shm/j3/ws
for f in "$@"; do
  echo "== $(date -u +%FT%TZ) lake env lean J3/$f.lean  (sha256 $(sha256sum J3/$f.lean | cut -c1-64))"
  python3 -I /dev/shm/j3/timed.py lake env lean J3/$f.lean 2>&1
  echo "EXIT[$f]=$?"
done
