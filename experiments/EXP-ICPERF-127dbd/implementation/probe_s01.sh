#!/usr/bin/env bash
# S01 probe: thin, read-only. Makes NO AWS write call (sts get-caller-identity is a read). No study logic.
#
# usage: probe_s01.sh --protocol PROTOCOL.json --inputs INPUTS_DIR --ecbench ECBENCH --aws-cli TOKEN --request NAME [--request NAME ...]
#
# In order, exiting nonzero at the first mismatch:
#   0. aws --version (no AWS call): its first token must equal --aws-cli TOKEN (e.g. aws-cli/1.46.2), the CLI whose memory use was measured;
#      a mismatch stops the session before any AWS call
#   1. aws sts get-caller-identity (prints Account, UserId, Arn; no credential is read or printed)
#   2. sha256 of ECBENCH equals the pinned 73362eed...
#   3. every request the runbook binds (each --request NAME, a file name in INPUTS_DIR) must be present and its sha256 must equal
#      protocol.json extensions.requests["launch/NAME"]; a missing bound request, an unknown name or an empty --request list is
#      an error: nothing is skipped because it is absent (a -r2 session binds and passes its -r2 requests)
#   4. the four launcher scripts under $CRYPTO_CHECKOUT/taskq/deploy/eks-karpenter/remote match remote-pins.sha256
#   5. prints git -C $CRYPTO_CHECKOUT rev-parse HEAD (recorded, not compared)
# Environment: CRYPTO_CHECKOUT (required), AWS settings (ambient).
set -euo pipefail
set +x
PIN_ECBENCH=73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01
protocol=""; inputs=""; ecb=""; awscli=""; reqs=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --protocol) protocol=${2:?}; shift 2 ;;
    --inputs) inputs=${2:?}; shift 2 ;;
    --ecbench) ecb=${2:?}; shift 2 ;;
    --aws-cli) awscli=${2:?}; shift 2 ;;
    --request) reqs+=("${2:?}"); shift 2 ;;
    *) echo "unknown argument $1" >&2; exit 2 ;;
  esac
done
[[ -n $protocol && -n $inputs && -n $ecb && -n $awscli ]] || { echo "usage: probe_s01.sh --protocol P --inputs DIR --ecbench PATH --aws-cli TOKEN --request NAME [--request NAME ...]" >&2; exit 2; }
[[ ${#reqs[@]} -ge 1 ]] || { echo "at least one --request is required: the bound requests are never inferred" >&2; exit 2; }
[[ -n ${CRYPTO_CHECKOUT:-} ]] || { echo "CRYPTO_CHECKOUT is required" >&2; exit 2; }
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

echo "== 0. aws cli version"
vers=$(aws --version 2>&1 | head -n 1) || true
echo "aws_version=$vers"
tok=${vers%% *}
[[ $tok == "$awscli" ]] || { echo "AWS CLI MISMATCH: first token '$tok' != pinned '$awscli'; re-measure under the recorded procedure, do not edit the runbook" >&2; exit 1; }

echo "== 1. caller identity"
aws sts get-caller-identity --output json

echo "== 2. local pinned ecbench"
got=$(sha256sum "$ecb" | cut -d ' ' -f1)
echo "ecbench_sha256=$got"
[[ $got == "$PIN_ECBENCH" ]] || { echo "ECBENCH MISMATCH: $ecb is not $PIN_ECBENCH" >&2; exit 1; }

echo "== 3. bound requests"
for name in "${reqs[@]}"; do
  base=$(basename "$name")
  want=$(jq -r --arg k "launch/$base" '.extensions.requests[$k] // empty' "$protocol")
  [[ -n $want ]] || { echo "REQUEST UNKNOWN: $base is not in protocol.json extensions.requests" >&2; exit 1; }
  f="$inputs/$base"
  [[ -f $f ]] || { echo "REQUEST ABSENT: $f (a bound request must be present)" >&2; exit 1; }
  have=$(sha256sum "$f" | cut -d ' ' -f1)
  [[ $have == "$want" ]] || { echo "REQUEST MISMATCH: $f sha256 $have != protocol.json $want" >&2; exit 1; }
  echo "request_ok $base $have"
done

echo "== 4. launcher script pins"
remote="$CRYPTO_CHECKOUT/taskq/deploy/eks-karpenter/remote"
npins=0
while read -r want name; do
  [[ -n $want ]] || continue
  have=$(sha256sum "$remote/$name" 2>/dev/null | cut -d ' ' -f1)
  [[ $have == "$want" ]] || { echo "PIN MISMATCH: $remote/$name sha256 ${have:-absent} != pinned $want" >&2; exit 1; }
  echo "pin_ok $name"; npins=$((npins + 1))
done < "$here/remote-pins.sha256"
[[ $npins == 4 ]] || { echo "remote-pins.sha256 must pin exactly 4 scripts" >&2; exit 1; }

echo "== 5. crypto checkout HEAD (recorded)"
echo "CRYPTO_CHECKOUT_HEAD=$(git -C "$CRYPTO_CHECKOUT" rev-parse HEAD)"
echo S01_PROBE_OK
