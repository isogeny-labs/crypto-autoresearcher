#!/usr/bin/env bash
set -euo pipefail
# Run from the repository root after publishing this exact source and protocol.
python -m orchestration.eval.capability_campaign run \
  --spec examples/capability-campaign/qualification.json \
  --protocol examples/capability-campaign/protocol.json \
  --model gpt-6-astra --effort xhigh --max-sessions 15 \
  --out examples/capability-campaign/records/native-qualification
