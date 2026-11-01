export ELAN_HOME=/dev/shm/j3/elan XDG_CACHE_HOME=/dev/shm/j3/xdg PATH=/dev/shm/j3/elan/bin:$PATH
cd /dev/shm/j3/ws; O=/dev/shm/j3/final-out; mkdir -p $O
echo "== final uniform pass $(date -u +%FT%TZ); lean: $(lean --version)"
for m in Lemma4Witness Lemma4Outside RecoveryRule Bridge BridgeB; do
  echo "== lake env lean CryptoResearch/Nagao/$m.lean -o $O/$m.olean"
  python3 -I /dev/shm/j3/timed.py lake env lean CryptoResearch/Nagao/$m.lean -o $O/$m.olean 2>&1 | grep -v "module system"
  echo "PASS_EXIT[$m]=${PIPESTATUS[0]}"
done
echo "== olean sha256 (final pass vs build tree)"; sha256sum $O/*.olean .lake/build/lib/lean/CryptoResearch/Nagao/*.olean
