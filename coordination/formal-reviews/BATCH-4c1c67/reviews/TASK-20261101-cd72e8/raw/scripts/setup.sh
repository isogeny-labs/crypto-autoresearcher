set -x
export ELAN_HOME=/dev/shm/j3/elan MATHLIB_CACHE_DIR=/dev/shm/j3/cache XDG_CACHE_HOME=/dev/shm/j3/xdg
curl -sSf https://elan.lean-lang.org/elan-init.sh -o /dev/shm/j3/elan-init.sh
sh /dev/shm/j3/elan-init.sh -y --default-toolchain none --no-modify-path
export PATH=$ELAN_HOME/bin:$PATH
cd /dev/shm/j3/ws
elan show; lean --version; lake --version
lake exe cache get
echo SETUP_EXIT=$?
