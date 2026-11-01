export ELAN_HOME=/dev/shm/j3/elan XDG_CACHE_HOME=/dev/shm/j3/xdg PATH=/dev/shm/j3/elan/bin:$PATH
cd /dev/shm/j3/ws
O=.lake/build/lib/lean/CryptoResearch/Nagao; mkdir -p $O
echo "== date: $(date -u +%FT%TZ)"; lean --version; free -m | head -2
echo "== input sha256"; sha256sum lean-toolchain lake-manifest.json CryptoResearch/Nagao/*.lean
for m in "$@"; do
  echo "== lake env lean CryptoResearch/Nagao/$m.lean -o $O/$m.olean -i $O/$m.ilean"
  python3 -I /dev/shm/j3/timed.py lake env lean CryptoResearch/Nagao/$m.lean -o $O/$m.olean -i $O/$m.ilean 2>&1
  echo "BUILD_EXIT[$m]=$?"
done
echo "== olean sha256"; sha256sum $O/*.olean
