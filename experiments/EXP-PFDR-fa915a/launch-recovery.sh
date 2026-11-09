#!/usr/bin/env bash
# Existing-host execution only. Approval, published claim and checkpoint gate
# must pass before invoking this launcher; the supervisor checks authority again.
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo 'usage: launch-recovery.sh CLAIM_OWNER CLAIM_EPOCH' >&2
  exit 2
fi
cd "$(dirname "$0")/../.."
exec systemd-run --user --scope --unit=pfdr-recovery-fa915a-20261109 \
  -p MemoryMax=4G -p CPUQuota=400% \
  -p RuntimeMaxSec=107570 -p TimeoutStopSec=30 -p KillSignal=SIGINT \
  /home/ec2-user/.local/bin/uv run --no-project --python 3.12 --with pyyaml \
  python tools/experiment_execution.py run \
  --plan experiments/EXP-PFDR-fa915a/trial-plan.json \
  --owner "$1" --epoch "$2"
