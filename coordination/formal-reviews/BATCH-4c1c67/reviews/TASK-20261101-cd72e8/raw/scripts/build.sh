export ELAN_HOME=/dev/shm/j3/elan MATHLIB_CACHE_DIR=/dev/shm/j3/cache XDG_CACHE_HOME=/dev/shm/j3/xdg PATH=/dev/shm/j3/elan/bin:$PATH
cd /dev/shm/j3/ws
echo "== date: $(date -u +%FT%TZ)"; echo "== host: $(uname -a)"; echo "== nproc: $(nproc)"; free -m
echo "== toolchain"; cat lean-toolchain; elan show; lean --version; lake --version
echo "== manifest pins"; python3 -c "import json;[print(p['name'],p['rev']) for p in json.load(open('lake-manifest.json'))['packages']]"
echo "== mathlib checkout HEAD"; git -C .lake/packages/mathlib rev-parse HEAD
echo "== input sha256"; sha256sum lakefile.toml lake-manifest.json lean-toolchain CryptoResearch/Nagao/*.lean
echo "== stale oleans for Nagao before build (should be none)"; ls .lake/build/lib/lean/CryptoResearch/Nagao 2>&1
for m in Lemma4Witness Lemma4Outside RecoveryRule Bridge BridgeB; do
  echo "== lake build CryptoResearch.Nagao.$m"
  python3 -I /dev/shm/j3/timed.py lake build -v CryptoResearch.Nagao.$m 2>&1
  echo "BUILD_EXIT[$m]=$?"
done
echo "== olean sha256"; sha256sum .lake/build/lib/lean/CryptoResearch/Nagao/*.olean
