#!/usr/bin/env bash
# Permanent regression suite for the C1 results locator, launch wrapper and reconciler (EXP-ICPERF-127dbd).
# TASK-20261107-d07e94 E-4. Offline only.
#
# PORTED FROM the red-team harness of TASK-20261107-9d2b6a: experiments/EXP-ICPERF-127dbd/reviews/redteam-9d2b6a/fixtures/rt_harness.sh,
# sha256 980abbd1cc35498bf65c2dc4f17677b3dd79805e3db679a5b50a19a9f13a9547 (its isobin-wrap/aws helper, sha256 bbaf62de63ae62214d7fa015c40d46a60d8e636ee82698dfb7285c5ce2d1a127,
# is tests/fixtures/isobin-wrap/aws here). Every case id and every attack of that harness is kept; the cases are re-targeted at v3c
# (K-1 to K-7 of DEC-20261107-a83c51). New cases carry the suffixes b, c, d or the ids K4-*, K5-*, K7-*, P-*.
#
# usage: env -i HOME="$HOME" TMPDIR=<tmp> PATH=<dir holding only the fake aws>:/usr/bin:/bin bash rt_regression.sh OUTDIR [IMPL_DIR [MODE [CASE_REGEX]]]
#   IMPL_DIR    the directory holding launch_eks.sh, locate_results.sh, reconcile_run.sh, check_job.py (default: this suite's implementation/);
#               tests/mutation_check.sh points it at a mutated scratch copy.
#   MODE        v3c (default): each case must give the v3c result. legacy: IMPL_DIR is ignored and the three v3b scripts of
#               tests/fixtures/ run instead; each case must reproduce the 9d2b6a verdict (a check that this port detects the same breaks).
#   CASE_REGEX  run only the cases whose id matches (extended regex); the exit status then covers only those.
# Exit status: the number of cases whose observed outcome differs from the expected one (0 = all as expected).
#
# It refuses to start unless `aws` resolves to the committed offline fake and no AWS_* variable is set. Every run of a C1 script goes
# through that fake (directly, or through fixtures/isobin-wrap/aws, which delegates every call to the same fake by path). The job
# outputs are synthetic. The launcher receipt shape is tests/fixtures/receipt/{result,status}.json. No real pod-uid prefix is read.
set -u
FXD=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
TESTS=$FXD
IMPL_OWN=$(cd "$TESTS/.." && pwd)
EXP=$(cd "$IMPL_OWN/.." && pwd)
WT=$(cd "$EXP/../.." && pwd)
RCPT=$TESTS/fixtures/receipt
REQ1=$EXP/inputs/request-s1.json; REQ2=$EXP/inputs/request-s2.json; PROTO=$EXP/inputs/protocol.json
OUT=${1:?usage: rt_regression.sh OUTDIR [IMPL_DIR [MODE [CASE_REGEX]]]}
IMPL=${2:-$IMPL_OWN}; MODE=${3:-v3c}; ONLY=${4:-.}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
CHECKJOB=$IMPL_OWN/check_job.py
RUNBOOK=$EXP/runbook.yaml
if [[ $MODE == legacy ]]; then
  IMPL=$OUT/legacy-impl; mkdir -p "$IMPL"
  cp "$TESTS/fixtures/launch_eks.v3b.sh" "$IMPL/launch_eks.sh"; cp "$TESTS/fixtures/locate_results.v3b.sh" "$IMPL/locate_results.sh"
  cp "$TESTS/fixtures/reconcile_run.v3b.sh" "$IMPL/reconcile_run.sh"; chmod +x "$IMPL"/*.sh
fi
[[ -f $IMPL/launch_eks.sh && -f $IMPL/locate_results.sh && -f $IMPL/reconcile_run.sh ]] || { echo "REFUSED: $IMPL does not hold the three scripts" >&2; exit 99; }

BUCKET=isolab-results-104186811093-us-east-2
JOB1=ic-c1-dg-s1-20261106; JOB2=ic-c1-dg-s2-20261106
POD=5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7          # the pod uid string as it appears in the launcher receipt fixture
LID=47cf1e4f-10a7-4ee3-862d-9e9700e122e3
JUID=8a20d036-efc2-45d2-ada6-6442b93c5a52
OTHER=0bbbbbbb-1111-2222-3333-555555555555         # an attacker-chosen pod uid
LID2=0ccccccc-1111-2222-3333-666666666666          # a second launcher receipt id
PIN_ECBENCH=73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01
PIN_COMMIT=ea8e9ef71c3c82027dd9e01535302725519c3fca
PIN_NA=2026-11-07T02:14:41Z; SNAP='2026-11-07T02:14:21Z'

# ---------------------------------------------------------------- isolation preconditions (RT-2 of 9d2b6a, E-1 of d07e94)
fake_real=$(readlink -f "$TESTS/fake-aws")
[[ $(readlink -f "$(command -v aws)") == "$fake_real" ]] || { echo "REFUSED: aws is not the offline fake" >&2; exit 99; }
[[ $(env | grep -c '^AWS_') == 0 ]] || { echo "REFUSED: AWS_* variables present" >&2; exit 99; }
[[ ! -e /usr/bin/aws && ! -e /bin/aws ]] || { echo "REFUSED: an aws binary exists in /usr/bin or /bin" >&2; exit 99; }
[[ -z $(env | grep '^BASH_FUNC_') ]] || { echo "REFUSED: an exported shell function is in the environment (it would reach the scripts under test)" >&2; exit 99; }

TABLE="$OUT/rt-results.tsv"
printf 'case\tquestion\tsound_result\tobserved\toutcome\texpected\tverdict\tv3b_9d2b6a_verdict\n' > "$TABLE"
NFAIL=0; NROW=0
want_case() { [[ $1 =~ $ONLY ]]; }
# WANT_LRC: for a case that goes through launch_eks.sh, the exact exit status of `locate_results.sh locate` the refusal must come from. A refusal
# by a later check (a download that then differs, a class veto) is not enough, so removing one check cannot hide behind the next (DEC-20261107-a83c51 E-4 mutation cases).
declare -A WANT_LRC=(
  [A01-ruleA-sibling-prefix]=13 [A01b-ruleA-sibling-prefix-with-receipt]=24 [A01d-ruleA-uri-located-poduid-differs]=24 [A02-ruleA-cross-job]=13 [A02b-ruleA-cross-job-with-receipt]=24
  [A03-ruleA-other-bucket]=13 [A03b-ruleA-other-bucket-with-receipt]=24 [A04-ruleA-verification-failed-genuine]=13 [A05-uid-prefix-sibling]=16
  [A06a-receipt-other-job]=12 [A06b-receipt-dotdot]=12 [A06c-receipt-other-bucket]=12 [A06d-receipt-deeper]=12 [A06e-receipt-second-launcher-id]=12 [A06f-receipt-id-all-dashes]=12
  [A07a-poduid-dotdot]=15 [A07b-poduid-slash]=15 [A07c-poduid-35]=15 [A07d-poduid-upper]=15 [A07e-poduid-trailing-newline]=15
  [A12a-status-job-uid]=14 [A12b-status-job-name]=14 [A12c-two-pods]=15 [A12d-zero-pods]=15
  [A08-restart-count]=15 [A08b-restart-count-only]=15 [A08c-laststate-only]=15
  [A09a-added-object]=22 [A09b-replaced-object]=22 [A09c-objects-json-vacuous]=21 [A09c2-objects-json-empty-array]=21 [A09d-objects-json-truncated]=21 [A09d2-objects-json-next-token-only]=21 [A09e-objects-json-key-outside]=21
  [A09f-objects-json-missing-etag]=21 [A09g-objects-json-extra-entry]=22 [A09i-multipart-size-changed]=22 [A09j-objects-json-no-pod-entries]=21 [A10-toctou-after-listing]=22
  [B12a-ruleA-exit-string-0]=13 [B12b-ruleA-exit-string-42]=13 [B14b-partial-unlisted-lost]=22 [B15e-status-not-json]=13 [B15f-objects-not-json]=20
)
# WANT_RLRC: the same for a case that runs reconcile_run.sh only (the receipt pins exist only there): the locate exit status printed in its stdout.
declare -A WANT_RLRC=( [A13a-pin-status-wrong]=23 [A13b-pin-objects-wrong]=23 [A13c-receipt-object-too-new]=23 [A13d-pod-object-too-new]=23 [A13e-receipt-lastmodified-missing]=23 )
# WANT_VRC: for the K-4 cases, the refusal must come from `locate_results.sh verify` (exit 18) AND the wrapper must record no job_exit_code (its own K-4 check).
declare -A WANT_VRC=(
  [B05-exit-string-42]=18 [B06-exit-true]=18 [B07-exit-false]=18 [B08-exit-null]=18 [B09-exit-42.5]=18 [B10-exit-42.0]=18 [B11-exit-array]=18 [B11b-exit-exponent]=18 [B11c-exit-negative-zero]=18
  [K4-a-string-0]=18 [K4-b-string-42]=18 [K4-c-true]=18 [K4-d-float-42.0]=18 [K4-e-exponent]=18 [K4-f-float-0.0]=18
)
row() { # row ID QUESTION SOUND OBSERVED OUTCOME EXPECTED_V3C EXPECTED_V3B
  local exp=$6 obs=$5; [[ $MODE == legacy ]] && exp=$7
  if [[ $MODE == v3c && -n ${WANT_LRC[$1]:-} && ( $obs == holds* || $obs == refused ) && $W_LRC != "${WANT_LRC[$1]}" ]]; then obs="refused-by-locate-exit-$W_LRC-not-${WANT_LRC[$1]}"; fi
  if [[ $MODE == v3c && -n ${WANT_RLRC[$1]:-} && ( $obs == holds* || $obs == refused ) && $R_LRC != "${WANT_RLRC[$1]}" ]]; then obs="refused-by-reconcile-locate-exit-$R_LRC-not-${WANT_RLRC[$1]}"; fi
  if [[ $MODE == v3c && -n ${WANT_VRC[$1]:-} && ( $obs == holds* || $obs == refused ) && ( $W_VRC != "${WANT_VRC[$1]}" || -n $W_JEC ) ]]; then obs="refused-by-verify-exit-$W_VRC-jec-[$W_JEC]-not-${WANT_VRC[$1]}-empty"; fi
  local v=PASS; [[ $obs == "$exp" ]] || { v=FAIL; NFAIL=$((NFAIL + 1)); }
  NROW=$((NROW + 1))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$obs" "$exp" "$v" "$7" | tee -a "$TABLE"
}

planned() { jq -r '(.job.spec.workloads.curves | length) * .job.spec.workloads.targets_per_curve
  * (.job.spec.measurement.warmup + .job.spec.measurement.rounds) * (.job.spec.arms | length)' "$1"; }
regen_sums() { (cd "$1" && find . -type f ! -name SHA256SUMS | sed 's|^\./||' | LC_ALL=C sort | xargs -d '\n' sha256sum) > "$1/SHA256SUMS"; }

# mk_jobset DIR JOB POD EXIT_JSON REQ : a synthetic job output set that check_job.py accepts against REQ
mk_jobset() {
  local d=$1 job=$2 pod=$3 ex=$4 req=$5
  mkdir -p "$d/session"
  printf '%s  ecbench\n' "$PIN_ECBENCH" > "$d/binary.sha256"
  jq -n --arg b "$PIN_ECBENCH" --arg c "$PIN_COMMIT" '{ecbench_sha256:$b, source_revision:$c}' > "$d/build-info.json"
  echo '{"accepted":true}' > "$d/l2-gate.json"
  jq '.job.spec' "$req" > "$d/input-spec.json"; cp "$d/input-spec.json" "$d/session/spec.json"
  yes '{}' 2>/dev/null | head -n "$(planned "$req")" > "$d/session/records.jsonl"
  echo '{"fixture":true}' > "$d/session/plan.json"
  echo fixture > "$d/audit.stderr"
  : > "$d/run-summary.json"
  printf '{"exit_code":%s,"job_name":"%s","pod_uid":"%s","node_name":"fixture"}\n' "$ex" "$job" "$pod" > "$d/job-exit.json"
  regen_sums "$d"
}
# objects_json PODDIR JOB POD > objects.json : launcher-style listing (Key, Size, ETag = md5 of the bytes) of a pod prefix
objects_json() {
  (cd "$1" && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while read -r f; do
     printf '%s %s %s\n' "$(stat -c %s "$f")" "$(md5sum "$f" | cut -d ' ' -f1)" "$f"; done) \
  | jq -Rn --arg b "$BUCKET" --arg j "$2" --arg p "$3" '{next_token:null, results_uri:("s3://"+$b+"/runs/"+$j+"/"),
      objects:[inputs | split(" ") | {Key:("runs/"+$j+"/"+$p+"/"+.[2]), Size:(.[0]|tonumber), ETag:("\""+.[1]+"\"")}]}'
}
age() { find "$1" -exec touch -h -d "$SNAP" {} +; }   # every object is as old as the launcher's snapshot
# mk_case_b ID JOB REQ [je_exit=42] [cexit=42] [launch_rc=26] [bstatus=FAILED] [status_mut=.] [result_mut=.] [je_job=] [je_pod=]
#   [ruri=URI] [rpod=UID] [jstate=failed] [objects_mut=.]
#   T1 receipt shape (rule b): failed Job, empty results_uri, receipt at runs/JOB/launcher/LID/, one pod POD.
#   ruri= gives result.json a results_uri (LOCATED means the located prefix s3://BUCKET/runs/JOB/POD/); rpod= sets result.json pod_uid.
mk_case_b() {
  local id=$1 job=$2 req=$3; shift 3
  local -A P=(); local kv; for kv in "$@"; do P[${kv%%=*}]=${kv#*=}; done
  local fx="$OUT/cases/$id/fx"; rm -rf "$OUT/cases/$id"; mkdir -p "$fx/launcher"
  local pd="$fx/s3/runs/$job/$POD" rc="$fx/s3/runs/$job/launcher/$LID"; mkdir -p "$rc"
  mk_jobset "$pd" "${P[je_job]:-$job}" "${P[je_pod]:-$POD}" "${P[je_exit]:-42}" "$req"   # je_job/je_pod only change job-exit.json
  local ruri=${P[ruri]:-}; [[ $ruri == LOCATED ]] && ruri="s3://$BUCKET/runs/$job/$POD/"
  jq --arg j "$job" --arg u "$JUID" --arg r "s3://$BUCKET/runs/$job/launcher/$LID/" --arg ru "$ruri" --arg rp "${P[rpod]:-}" \
    '.job_name=$j | .job_uid=$u | .receipt_uri=$r | .results_uri=$ru | .pod_uid=$rp' "$RCPT/result.json" | jq "${P[result_mut]:-.}" > "$rc/result.json"
  jq --arg j "$job" --arg u "$JUID" --arg p "$POD" --argjson cx "${P[cexit]:-42}" --arg js "${P[jstate]:-failed}" \
    '.job.job_name=$j | .job.uid=$u | .job.state=$js | .pods[0].uid=$p | .pods[0].status.containerStatuses[0].state.terminated.exitCode=$cx' \
    "$RCPT/status.json" | jq "${P[status_mut]:-.}" > "$rc/status.json"
  objects_json "$pd" "$job" "$POD" | jq "${P[objects_mut]:-.}" > "$rc/objects.json"
  cp "$rc/result.json" "$fx/launcher/result.json"
  echo "${P[launch_rc]:-26}" > "$fx/launch_rc"
  if [[ ${P[bstatus]-FAILED} == NONE ]]; then echo '{}' > "$fx/launcher/build.json"
  else jq -n --arg s "${P[bstatus]:-FAILED}" '{builds:[{buildStatus:$s}]}' > "$fx/launcher/build.json"; fi
  age "$fx/s3"
}
# mk_case_a ID JOB REQ RESULTS_URI POD_UID [launch_rc=26] [bstatus=FAILED] [state=failed] : rule (a) as v3b saw it: non-empty results_uri
# and a receipt directory that holds result.json only (no status.json, no objects.json)
mk_case_a() {
  local id=$1 job=$2 req=$3 uri=$4 puid=$5 lrc=${6:-26} bs=${7:-FAILED} st=${8:-failed}
  local fx="$OUT/cases/$id/fx"; rm -rf "$OUT/cases/$id"; mkdir -p "$fx/launcher" "$fx/s3/runs/$job/launcher/$LID"
  jq --arg j "$job" --arg u "$JUID" --arg r "s3://$BUCKET/runs/$job/launcher/$LID/" --arg uri "$uri" --arg p "$puid" --arg st "$st" \
    '.job_name=$j | .job_uid=$u | .receipt_uri=$r | .results_uri=$uri | .pod_uid=$p | .state=$st' "$RCPT/result.json" > "$fx/launcher/result.json"
  cp "$fx/launcher/result.json" "$fx/s3/runs/$job/launcher/$LID/result.json"
  echo "$lrc" > "$fx/launch_rc"; jq -n --arg s "$bs" '{builds:[{buildStatus:$s}]}' > "$fx/launcher/build.json"
  age "$fx/s3"
}

# mk_bin DIR S3ROOT LOG [wrap] [conf lines...] : a directory holding only `aws` (the fake, or the delegating wrapper) and its conf file
mk_bin() {
  local d=$1 root=$2 log=$3 kind=${4:-plain}; shift 4 2>/dev/null || shift $#
  mkdir -p "$d"; rm -f "$d/aws"
  if [[ $kind == wrap ]]; then cp "$TESTS/fixtures/isobin-wrap/aws" "$d/aws"; chmod +x "$d/aws"; else ln -s "$TESTS/fake-aws" "$d/aws"; fi
  { printf 'FAKE_AWS_LOG=%q\nFAKE_S3_ROOT=%q\nRT_FAKE_AWS=%q\n' "$log" "$root" "$TESTS/fake-aws"; printf '%s\n' "$@"; } > "$d/fake-aws.conf"
}

# run_wrapper ID REQ [wrap] [envprefix...] : launch_eks.sh (copies) against the fake aws + fake-launch-remote, with trial T2 of the real plan
run_wrapper() {
  local id=$1 req=$2 kind=${3:-plain}; shift 3 2>/dev/null || shift $#
  local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/wrap"
  rm -rf "$w"; mkdir -p "$w/impl" "$w/checkout/taskq/deploy/eks-karpenter/remote" "$w/rec" "$w/s3root" "$w/state" "$w/home"
  cp "$IMPL/launch_eks.sh" "$IMPL/locate_results.sh" "$w/impl/"; chmod +x "$w/impl/"*.sh
  local r="$w/checkout/taskq/deploy/eks-karpenter/remote" f
  cp "$TESTS/fake-launch-remote" "$r/launch-remote"
  printf 'FAKE_CASE_DIR=%q\nFAKE_S3_ROOT=%q\n' "$fx" "$w/s3root" > "$r/fake-launch-remote.conf"
  printf '#!/usr/bin/env bash\ncat "$1"\n' > "$r/validate-request"
  echo '#!/usr/bin/env bash' > "$r/run-request"; echo 'version: 0.2' > "$r/current-run-request-buildspec.yml"
  chmod +x "$r/launch-remote" "$r/validate-request" "$r/run-request"
  : > "$w/impl/remote-pins.sha256"
  for f in launch-remote validate-request run-request current-run-request-buildspec.yml; do
    printf '%s  %s\n' "$(sha256sum "$r/$f" | cut -d ' ' -f1)" "$f" >> "$w/impl/remote-pins.sha256"; done
  printf '{"run_id":"RUN-ICPERF-efb7ef","trial_id":"T2"}\n' > "$w/rec/launch.json"
  : > "$w/aws.log"
  mk_bin "$w/bin" "$w/s3root" "$w/aws.log" "$kind" "RT_STATE=$w/state" "${RT_CONF[@]}"
  [[ -n ${RT_PRE_REC:-} ]] && eval "$RT_PRE_REC"   # test hook: prepare the record directory (K5b makes manifest.yaml a directory)
  W_RC=0
  env PATH="$w/bin:/usr/bin:/bin" HOME="${RT_HOME:-$w/home}" TMPDIR="$w" AWS_REGION=us-east-2 AWS_DEFAULT_REGION=us-east-2 \
    ISOLAB_BUCKET="$BUCKET" ISOLAB_CODEBUILD_PROJECT=isolab-experiment-launcher CRYPTO_CHECKOUT="$w/checkout" "$@" \
    bash "$w/impl/launch_eks.sh" --protocol "$PROTO" --experiment-id EXP-ICPERF-127dbd --hypothesis-id H-ICPERF-4cb536 \
    --task-id TASK-20261107-f14df8 --approved-by DEC-20261107-7802ec --trial-id T2 --run-id RUN-ICPERF-efb7ef --out "$w/rec/job" --record-dir "$w/rec" "$req" \
    > "$w/stdout" 2> "$w/stderr" || W_RC=$?
  W_CLASS=$(jq -r '.outcome_class // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_LOC=$(jq -r '.results_locator // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_URI=$(jq -r '.results_uri // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_DL=$(jq -r '.download_exit // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_OM=$(jq -r '.objects_match // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_SUB=$(jq -r '.submitted // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_LRC=$(grep -o 'locate_results exit [0-9]*' "$w/stdout" | head -1 | sed 's/locate_results exit //'); W_LRC=${W_LRC:-none}
  W_RAW=$([[ -f $w/rec/raw-result.json ]] && echo present || echo absent)
  W_VRC=$(grep -o 'locate_results verify exit [0-9]*' "$w/stdout" | head -1 | sed 's/locate_results verify exit //'); W_VRC=${W_VRC:-none}
  W_JEC=$(jq -r '.job_exit_code // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_WRITES=$(grep -c -E 'REFUSED|^aws s3 cp [^ ]+ s3://|^aws (s3 (rm|mv|sync)|s3api (put|delete|copy)|codebuild (start|batch))' "$w/aws.log" "$w/stderr" 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
  W_DIR=$w
  # S03-trial-s2 validity: the committed runbook.yaml assertions (steps S03-trial-s2 validity.files and by_trial.T2.files), evaluated by tools/runbook.py
  W_VALID=$(python3 "$TESTS/rt_validity.py" "$RUNBOOK" "$w/rec" 2>/dev/null | head -1); W_VALID=${W_VALID:-error}
}
# check_job on the wrapper download
run_cj() { # run_cj ID REQ
  local w="$OUT/cases/$1/wrap"
  if [[ -d $w/rec/job/artifacts ]]; then
    python3 -I "$CHECKJOB" "$w/rec/job/artifacts" --request "$2" --launcher-result "$w/rec/job/launcher/result.json" > "$w/check_job.stdout" 2>&1
    CJ_RC=$?; CJ_LAST=$(tail -n 1 "$w/check_job.stdout")
  else CJ_RC=none; CJ_LAST=no-artifacts; fi
}
# run_reconcile ID [SHA] [kind] [envprefix...] ; reconcile_run.sh runs in place (IMPL), the pins are those of the case's own receipt objects
RC_PIN_STATUS=""; RC_PIN_OBJECTS=""; RC_PIN_NA=$PIN_NA; RC_JOB=$JOB1; RC_OUTSUB=out; RC_OUTROOT=""; RC_OUTARG=""
run_reconcile() {
  local id=$1 sha=${2:-} kind=${3:-plain}; shift 3 2>/dev/null || shift $#
  local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/rec"
  [[ -n $sha ]] || sha=$(sha256sum "$fx/launcher/result.json" | cut -d ' ' -f1)
  local rcd="$fx/s3/runs/$RC_JOB/launcher/$LID"
  local ps=${RC_PIN_STATUS:-$(sha256sum "$rcd/status.json" 2>/dev/null | cut -d ' ' -f1)} po=${RC_PIN_OBJECTS:-$(sha256sum "$rcd/objects.json" 2>/dev/null | cut -d ' ' -f1)}
  [[ -n $ps ]] || ps=0000000000000000000000000000000000000000000000000000000000000000
  [[ -n $po ]] || po=0000000000000000000000000000000000000000000000000000000000000000
  rm -rf "$w"; mkdir -p "$w/s3root" "$w/state" "$w/home"; cp -a "$fx/s3/." "$w/s3root/"; : > "$w/aws.log"
  mk_bin "$w/bin" "$w/s3root" "$w/aws.log" "$kind" "RT_STATE=$w/state" "${RT_CONF[@]}"
  local outarg=${RC_OUTARG:-$w/$RC_OUTSUB}; mkdir -p "$w/$RC_OUTSUB"
  local -a newargs=(--out-root "${RC_OUTROOT:-$w}" --pin-status-sha256 "$ps" --pin-objects-sha256 "$po" --pin-not-after "$RC_PIN_NA")
  [[ $MODE == legacy ]] && newargs=()
  R_RC=0
  env PATH="$w/bin:/usr/bin:/bin" HOME="${RT_HOME:-$w/home}" TMPDIR="$w" AWS_REGION=us-east-2 AWS_DEFAULT_REGION=us-east-2 ISOLAB_BUCKET="${RC_BUCKET:-$BUCKET}" "$@" \
    bash "$IMPL/reconcile_run.sh" --launcher-result "$fx/launcher/result.json" --launcher-result-sha256 "$sha" --request "${RC_REQ:-$REQ1}" \
    --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$outarg" "${newargs[@]}" > "$w/stdout" 2> "$w/stderr" || R_RC=$?
  R_DIR=$w
  R_PASS=$(jq -r '.reconcile_pass | tostring' "$w/$RC_OUTSUB/reconcile-result.json" 2>/dev/null || echo absent)
  R_OM=$(jq -r '.objects_match | tostring' "$w/$RC_OUTSUB/reconcile-result.json" 2>/dev/null || echo absent)
  R_LRC=$(grep -o 'locate_results exit [0-9]*' "$w/stdout" | head -1 | sed 's/locate_results exit //'); R_LRC=${R_LRC:-none}
  R_WRITES=$(grep -c -E 'REFUSED|^aws s3 cp [^ ]+ s3://|^aws (s3 (rm|mv|sync)|s3api (put|delete|copy)|codebuild)' "$w/aws.log" "$w/stderr" 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
  R_CALLS=$(grep -v -E '^aws --version$|^ENVNAMES ' "$w/aws.log" | grep -c . || true)
}
RT_CONF=()
rc_reset() { RC_PIN_STATUS=""; RC_PIN_OBJECTS=""; RC_PIN_NA=$PIN_NA; RC_JOB=$JOB1; RC_OUTSUB=out; RC_OUTROOT=""; RC_OUTARG=""; RC_BUCKET=""; RC_REQ=""; RT_CONF=(); RT_HOME=""; }
# prune ID : keep logs and records, drop bulky synthetic trees, keep a sha256 listing of what was dropped
prune() {
  local c="$OUT/cases/$1"
  (cd "$c" && find . -type f \( -path '*/s3/*' -o -path '*/s3root/*' -o -path '*/artifacts/*' -o -path '*/checkout/*' -o -path '*/impl/*' \) \
     -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum) > "$c/pruned-files.sha256" 2>/dev/null
  rm -rf "$c"/fx/s3 "$c"/wrap/s3root "$c"/wrap/rec/job/artifacts "$c"/wrap/checkout "$c"/wrap/impl "$c"/rec/s3root "$c"/rec/out/artifacts "$c"/rec/out/locator/objects.json
}
# objctl : the independent control (downloaded size and md5 versus objects.json, zero AWS calls). Prints same | DIFFERS.
objctl() {
  local o="$R_DIR/out/locator/objects.json" a="$R_DIR/out/artifacts" want have
  [[ -f $o && -d $a ]] || { echo n/a; return; }
  want=$(jq -r --arg p "runs/$JOB1/$POD/" '.objects[] | "\(.Size) \(.ETag|gsub("\"";"")) \(.Key|ltrimstr($p))"' "$o" | LC_ALL=C sort -k3)
  have=$(cd "$a" && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while read -r f; do printf '%s %s %s\n' "$(stat -c %s "$f")" "$(md5sum "$f" | cut -d ' ' -f1)" "$f"; done | LC_ALL=C sort -k3)
  [[ $want == "$have" ]] && echo same || echo DIFFERS
}
W() { echo "rc=$W_RC class=$W_CLASS locator=$W_LOC raw=$W_RAW sub=$W_SUB dl=$W_DL objects_match=$W_OM locate_exit=$W_LRC s03_validity=$W_VALID s3_write_attempts=$W_WRITES"; }
refused_w() { [[ $W_CLASS != job_completed ]] && echo holds || echo BREAK; }

echo "== rt_regression $(date -u +%FT%TZ) mode=$MODE impl=$IMPL jq=$(jq --version) bash=$BASH_VERSION" | tee "$OUT/rt-header.txt"
echo "aws=$(command -v aws) -> $(readlink -f "$(command -v aws)"); AWS_ vars=$(env | grep -c '^AWS_')" | tee -a "$OUT/rt-header.txt"

# ================================================================ (a) binding of the results prefix
id=A00-control-T1-shape
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"
  run_wrapper $id "$REQ1"; run_cj $id "$REQ1"; w_summary=$(W)
  rc_reset; run_reconcile $id
  row $id a "job_completed rc0; reconcile pass" "$w_summary; check_job=$CJ_LAST; reconcile rc=$R_RC pass=$R_PASS writes=$R_WRITES; control(object-list vs objects.json)=$(objctl)" \
    "$([[ $W_CLASS == job_completed && $W_RC == 0 && $R_PASS == true ]] && echo control || echo BROKEN)" control control
  prune $id
fi

id=A01-ruleA-sibling-prefix   # rule (a) as v3b saw it: result.json names an attacker-placed sibling prefix runs/JOB/OTHER/
if want_case $id; then
  mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB2/$OTHER/" "$OTHER"
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$POD" "$JOB2" "$POD" 42 "$REQ2"          # the genuine pod's output
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$OTHER" "$JOB2" "$OTHER" 42 "$REQ2"      # attacker-placed, self-consistent
  age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id a,b "not job_completed (two pod prefixes; not this pod)" "$(W) uri=$W_URI; check_job=$CJ_LAST" "$(refused_w)" holds BREAK
  prune $id
fi
id=A01b-ruleA-sibling-prefix-with-receipt   # the same attack against a genuine receipt: status.json names POD, result.json names OTHER (K-1: exit 24)
if want_case $id; then
  mk_case_b $id "$JOB2" "$REQ2" "ruri=s3://$BUCKET/runs/$JOB2/$OTHER/" "rpod=$OTHER"
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$OTHER" "$JOB2" "$OTHER" 42 "$REQ2"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id a,b "class other, rc 5, locate exit 24, nothing downloaded" "$(W) uri=$W_URI" \
    "$([[ $W_CLASS == other && $W_RC == 5 && $W_LRC == 24 && ! -d $W_DIR/rec/job/artifacts ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo BREAK || echo differs; })" holds BREAK
  prune $id
fi
id=A01c-ruleA-uri-equals-located   # rule (a) with a results_uri that equals the located prefix stays accepted
if want_case $id; then
  mk_case_b $id "$JOB2" "$REQ2" "ruri=LOCATED" "rpod=$POD"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id a "job_completed rc0 (results_uri equals the located prefix), validity VALID" "$(W); check_job=$CJ_LAST" \
    "$([[ $W_CLASS == job_completed && $W_RC == 0 && $W_VALID == VALID ]] && echo control || echo BROKEN)" control control
  prune $id
fi

id=A01d-ruleA-uri-located-poduid-differs   # K-1: result.json results_uri equals the located prefix but its pod_uid names another pod
if want_case $id; then
  mk_case_b $id "$JOB2" "$REQ2" "ruri=LOCATED" "rpod=$OTHER"
  run_wrapper $id "$REQ2"
  row $id a,b "class other, rc 5, locate exit 24 (result.json pod_uid differs from the located pod)" "$(W) uri=$W_URI" \
    "$([[ $W_CLASS == other && $W_RC == 5 && $W_LRC == 24 ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo differs; })" holds BREAK-wrapper
  prune $id
fi

id=A02-ruleA-cross-job   # the S2 job's result.json names the S1 job's pod prefix
if want_case $id; then
  mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB1/$POD/" "$POD"
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB1/$POD" "$JOB1" "$POD" 42 "$REQ1"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id a,b "not job_completed (another job's prefix)" "$(W) uri=$W_URI; check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo holds)" holds BREAK-wrapper
  prune $id
fi
id=A02b-ruleA-cross-job-with-receipt   # the same with a genuine S2 receipt: result.json names S1's prefix and pod
if want_case $id; then
  mk_case_b $id "$JOB2" "$REQ2" "ruri=s3://$BUCKET/runs/$JOB1/$POD/" "rpod=$POD"
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB1/$POD" "$JOB1" "$POD" 42 "$REQ1"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ2"
  row $id a,b "class other, rc 5, locate exit 24, validity INVALID" "$(W) uri=$W_URI" \
    "$([[ $W_CLASS == other && $W_RC == 5 && $W_LRC == 24 && $W_VALID != VALID ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo differs; })" holds BREAK-wrapper
  prune $id
fi

id=A03-ruleA-other-bucket
if want_case $id; then
  mk_case_a $id "$JOB2" "$REQ2" "s3://rt-9d2b6a-elsewhere/x/$OTHER/" "$OTHER"
  mk_jobset "$OUT/cases/$id/fx/s3/x/$OTHER" "$JOB2" "$OTHER" 42 "$REQ2"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id a,b "not job_completed (outside s3://BUCKET/runs/JOB/)" "$(W) uri=$W_URI; check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo holds)" holds BREAK-wrapper
  prune $id
fi
id=A03b-ruleA-other-bucket-with-receipt
if want_case $id; then
  mk_case_b $id "$JOB2" "$REQ2" "ruri=s3://rt-9d2b6a-elsewhere/x/$POD/" "rpod=$POD"
  run_wrapper $id "$REQ2"
  row $id a,b "class other, rc 5, locate exit 24" "$(W) uri=$W_URI" \
    "$([[ $W_CLASS == other && $W_RC == 5 && $W_LRC == 24 ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo differs; })" holds BREAK-wrapper
  prune $id
fi

id=A04-ruleA-verification-failed-genuine   # the pinned launcher's own rule-(a)-with-exit-26 shape: state verification_failed, results_uri = the exit-0 pod
if want_case $id; then
  mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB2/$POD/" "$POD" 26 FAILED verification_failed
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$POD" "$JOB2" "$POD" 0 "$REQ2"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id a,b "not job_completed (launcher rejected the output)" "$(W); check_job=$CJ_LAST" "$(refused_w)" holds holds
  prune $id
fi
id=A04b-ruleA-verification-failed-with-receipt   # the same shape with a full receipt (job state succeeded, exit 0): the pairing (26, FAILED, 0) is class other
if want_case $id; then
  mk_case_b $id "$JOB2" "$REQ2" "ruri=LOCATED" "rpod=$POD" "je_exit=0" "cexit=0" "jstate=succeeded" 'result_mut=.state="verification_failed"'
  run_wrapper $id "$REQ2"
  row $id a,b "not job_completed (launcher exit 26 with job exit 0)" "$(W)" "$(refused_w)" holds holds
  prune $id
fi

id=A05-uid-prefix-sibling   # a pod prefix that extends the located uid (same 36-char uid + suffix) also exists
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"; mkdir -p "$OUT/cases/$id/fx/s3/runs/$JOB1/${POD}0"; echo x > "$OUT/cases/$id/fx/s3/runs/$JOB1/${POD}0/job-exit.json"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "refused (listing holds a third entry)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS != job_completed && $R_PASS != true ]] && echo holds || echo BREAK)" holds holds
  prune $id
fi

# A06 receipt_uri variants (rule b)
for v in "A06a-receipt-other-job|s3://$BUCKET/runs/$JOB2/launcher/$LID/" "A06b-receipt-dotdot|s3://$BUCKET/runs/$JOB1/launcher/$LID/../" \
         "A06c-receipt-other-bucket|s3://rt-9d2b6a-elsewhere/runs/$JOB1/launcher/$LID/" "A06d-receipt-deeper|s3://$BUCKET/runs/$JOB1/launcher/$LID/x/"; do
  id=${v%%|*}; ru=${v#*|}
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1" "result_mut=.receipt_uri=\"$ru\""
  run_wrapper $id "$REQ1"
  row $id a "refused, locator exit 12" "$(W)" "$([[ $W_CLASS != job_completed && $W_LRC == 12 ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo BREAK || echo differs; })" holds holds
  prune $id
done
id=A06e-receipt-second-launcher-id   # a second launcher receipt id named by result.json (not the build that ran, K-6), self-consistent
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" "result_mut=.receipt_uri=\"s3://$BUCKET/runs/$JOB1/launcher/$LID2/\""
  mv "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID" "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID2"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-6: refused (locator exit 12): the receipt id is not result.json .launcher / the build id" "$(W); reconcile rc=$R_RC pass=$R_PASS; result.launcher=$(jq -r .launcher "$OUT/cases/$id/fx/launcher/result.json" | sed 's/.*://')" \
    "$([[ $W_LOC == receipt_status_pod_uid ]] && echo NOTE-accepted || echo refused)" refused NOTE-accepted
  prune $id
fi
id=A06f-receipt-id-all-dashes   # a receipt id of 36 dashes passes the [a-f0-9-]{36} shape, not the UUID shape
if want_case $id; then
  D36=------------------------------------
  mk_case_b $id "$JOB1" "$REQ1" "result_mut=.receipt_uri=\"s3://$BUCKET/runs/$JOB1/launcher/$D36/\" | .launcher=\"isolab-experiment-launcher:$D36\""
  mv "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID" "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$D36"
  run_wrapper $id "$REQ1"
  row $id a "K-6: refused (locator exit 12): the id is not a canonical UUID" "$(W)" "$([[ $W_LOC == receipt_status_pod_uid ]] && echo NOTE-accepted || echo refused)" refused NOTE-accepted
  prune $id
fi

# A07 pod uid with path characters / odd shapes in status.json
for v in "A07a-poduid-dotdot|../../$JOB2/x" "A07b-poduid-slash|$POD/../x" "A07c-poduid-35|${POD:0:35}" "A07d-poduid-upper|${POD^^}"; do
  id=${v%%|*}; pu=${v#*|}
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1" "status_mut=.pods[0].uid=\"$pu\""
  run_wrapper $id "$REQ1"
  row $id a "refused, locator exit 15" "$(W)" "$([[ $W_CLASS != job_completed && $W_LRC == 15 ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo BREAK || echo differs; })" holds holds
  prune $id
done
id=A07e-poduid-trailing-newline
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" "status_mut=.pods[0].uid=\"$POD\\n\""
  run_wrapper $id "$REQ1"
  row $id a "K-6: refused, locator exit 15 (no silent strip of the newline)" "$(W) pod=$(jq -r .pod_uid "$W_DIR/rec/raw-result.json" 2>/dev/null)" "$([[ $W_CLASS == job_completed ]] && echo NOTE-accepted || echo refused)" refused NOTE-accepted
  prune $id
fi

# A12 status.json identity mismatches
for v in 'A12a-status-job-uid|.job.uid="00000000-0000-0000-0000-000000000000"' 'A12b-status-job-name|.job.job_name="ic-c1-dg-s2-20261106"' \
         'A12c-two-pods|.pods+=[(.pods[0]|.uid="0bbbbbbb-1111-2222-3333-555555555555")]' 'A12d-zero-pods|.pods=[]'; do
  id=${v%%|*}
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1" "status_mut=${v#*|}"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "refused (14/15)" "$(W) reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS != job_completed && $R_PASS != true ]] && echo holds || echo BREAK)" holds holds
  prune $id
done

# A08 restarted container (restartCount 2, lastState terminated 1) and its two halves (K-6)
for v in 'A08-restart-count|.pods[0].status.containerStatuses[0].restartCount=2 | .pods[0].status.containerStatuses[0].lastState={terminated:{exitCode:1,reason:"Error"}}' \
         'A08b-restart-count-only|.pods[0].status.containerStatuses[0].restartCount=1' \
         'A08c-laststate-only|.pods[0].status.containerStatuses[0].lastState={terminated:{exitCode:1,reason:"Error"}}'; do
  id=${v%%|*}
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1" "status_mut=${v#*|}"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-6: refused (locator exit 15) the restarted container" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS == job_completed || $R_PASS == true ]] && echo NOTE-accepted || echo refused)" refused NOTE-accepted
  prune $id
done

# A09 content under the correct prefix changed after the launcher's objects.json snapshot, SHA256SUMS regenerated
for v in A09a-added-object A09b-replaced-object; do
  id=$v
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1"; pd="$OUT/cases/$id/fx/s3/runs/$JOB1/$POD"
  if [[ $v == A09a-added-object ]]; then echo '{"placed":"after the launcher snapshot"}' > "$pd/session/extra.json"
  else echo "replaced after the launcher snapshot" > "$pd/audit.stderr"; fi
  regen_sums "$pd"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  ctl=$(objctl)
  row $id a "K-2: refuse (reconcile exit 5 from the pod listing; wrapper not job_completed)" "wrapper: $(W); reconcile rc=$R_RC pass=$R_PASS locate_exit=$R_LRC; control(object-list vs objects.json)=$ctl" \
    "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds BREAK
  prune $id
done
# A09c objects.json without an .objects array; A09d a truncated listing (next_token set); A09e a key outside launcher/ and the pod prefix
id=A09c-objects-json-vacuous
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"; echo '{}' > "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-2: refused (locator exit 21 -> reconcile 5) a document with no objects" "$(W); reconcile rc=$R_RC pass=$R_PASS r3=$(jq -r .r3_outcome "$R_DIR/out/reconcile-result.json" 2>/dev/null)" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo NOTE-vacuous || echo holds)" holds NOTE-vacuous
  prune $id
fi
id=A09c2-objects-json-empty-array   # K-2: .objects is an empty array (the live pod listing then differs from the empty set: exit 22 if the entries check is also gone)
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" 'objects_mut=.objects = []'
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-2: refused (locator exit 21 -> reconcile 5) an empty objects.json listing" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds BREAK
  prune $id
fi
id=A09d-objects-json-truncated
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" 'objects_mut=.next_token="tok" | .objects=.objects[0:2]'
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-2: refused (locator exit 21 -> reconcile 5) a truncated launcher listing" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo NOTE-truncated-accepted || echo holds)" holds NOTE-truncated-accepted
  prune $id
fi
id=A09e-objects-json-key-outside
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" "objects_mut=.objects += [{Key:\"runs/$JOB1/$OTHER/job-exit.json\", Size:1, ETag:\"\\\"00000000000000000000000000000000\\\"\"}]"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "R-3 refuses (exit 5)" "$(W); reconcile rc=$R_RC pass=$R_PASS r3=$(jq -r .r3_outcome "$R_DIR/out/reconcile-result.json" 2>/dev/null)" "$([[ $R_RC == 5 && $R_PASS == false && $W_CLASS != job_completed ]] && echo holds || echo BREAK)" holds BREAK
  # legacy (v3b) expectation BREAK: the v3b wrapper ignores objects.json (job_completed); the 9d2b6a row judged reconcile only (R-3), which held
  prune $id
fi
id=A09d2-objects-json-next-token-only   # K-2: a complete objects.json whose only defect is next_token set (the launcher listing was cut short)
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" 'objects_mut=.next_token="tok"'
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-2: refused (locator exit 21 -> reconcile 5)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds BREAK
  prune $id
fi
id=A09j-objects-json-no-pod-entries   # K-2: a non-empty .objects array that lists no object of the pod prefix
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" "objects_mut=.objects = [{Key:\"runs/$JOB1/launcher/$LID/status.json\", Size:1, ETag:\"\\\"00000000000000000000000000000000\\\"\"}]"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-2: refused (locator exit 21 -> reconcile 5)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds BREAK
  prune $id
fi
id=A09f-objects-json-missing-etag   # K-2: an entry of the pod prefix without an ETag
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" 'objects_mut=.objects[0] |= del(.ETag)'
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-2: refused (locator exit 21 -> reconcile 5)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds BREAK
  prune $id
fi
id=A09g-objects-json-extra-entry   # K-2: objects.json lists an object the prefix does not hold
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1" "objects_mut=.objects += [{Key:\"runs/$JOB1/$POD/ghost.bin\", Size:3, ETag:\"\\\"00000000000000000000000000000000\\\"\"}]"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id a "K-2: refused (locator exit 22 -> reconcile 5)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds BREAK
  prune $id
fi
# A09h multipart ETag: records.jsonl listed with a multipart-style ETag; compared by size only, so the genuine shape still passes
id=A09h-multipart-etag-size-only
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"
  mkdir -p "$OUT/cases/$id/fx/etag"
  key="runs/$JOB1/$POD/session/records.jsonl"; mkdir -p "$OUT/cases/$id/fx/etag/$(dirname "$key")"; printf '"055dafade8c8ac0319c2b3a2b63d032e-11"' > "$OUT/cases/$id/fx/etag/$key"
  f="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json"
  jq --arg k "$key" '(.objects[] | select(.Key == $k) | .ETag) = "\"055dafade8c8ac0319c2b3a2b63d032e-11\""' "$f" > "$f.t" && mv "$f.t" "$f"; age "$OUT/cases/$id/fx/s3"
  RT_CONF=("FAKE_ETAG_DIR=$OUT/cases/$id/fx/etag")
  run_wrapper $id "$REQ1"; rc_reset; RT_CONF=("FAKE_ETAG_DIR=$OUT/cases/$id/fx/etag"); run_reconcile $id; rc_reset
  row $id a "multipart ETag is compared by size only: the genuine shape passes (wrapper job_completed, reconcile pass)" "$(W); reconcile rc=$R_RC pass=$R_PASS" \
    "$([[ $W_CLASS == job_completed && $R_PASS == true ]] && echo control || echo BROKEN)" control control
  prune $id
fi
id=A09i-multipart-size-changed   # the multipart object changes size: refused
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"
  key="runs/$JOB1/$POD/session/records.jsonl"; mkdir -p "$OUT/cases/$id/fx/etag/$(dirname "$key")"; printf '"055dafade8c8ac0319c2b3a2b63d032e-11"' > "$OUT/cases/$id/fx/etag/$key"
  f="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json"
  jq --arg k "$key" '(.objects[] | select(.Key == $k) | .ETag) = "\"055dafade8c8ac0319c2b3a2b63d032e-11\""' "$f" > "$f.t" && mv "$f.t" "$f"
  echo '{}' >> "$OUT/cases/$id/fx/s3/runs/$JOB1/$POD/session/records.jsonl"; age "$OUT/cases/$id/fx/s3"
  RT_CONF=("FAKE_ETAG_DIR=$OUT/cases/$id/fx/etag")
  run_wrapper $id "$REQ1"; RT_CONF=("FAKE_ETAG_DIR=$OUT/cases/$id/fx/etag"); rc_reset; RT_CONF=("FAKE_ETAG_DIR=$OUT/cases/$id/fx/etag"); run_reconcile $id; rc_reset
  row $id a "refused (pod listing differs: the Size changed)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true || $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds BREAK
  prune $id
fi

# A10 TOCTOU: right after the locator's job listing a third party adds a late pod prefix AND a file under the located prefix
HOOK_TXT() { cat <<HOOK
set -e
: "\${FAKE_S3_ROOT:?the hook needs FAKE_S3_ROOT}"
mkdir -p "\$FAKE_S3_ROOT/runs/$JOB1/$OTHER"; echo late > "\$FAKE_S3_ROOT/runs/$JOB1/$OTHER/job-exit.json"
pd="\$FAKE_S3_ROOT/runs/$JOB1/$POD"; echo '{"placed":"between listing and download"}' > "\$pd/session/late.json"
(cd "\$pd" && find . -type f ! -name SHA256SUMS | sed 's|^\./||' | LC_ALL=C sort | xargs -d '\n' sha256sum) > "\$pd/SHA256SUMS"
HOOK
}
id=A10-toctou-after-listing
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"; HOOK_TXT > "$OUT/cases/$id/toctou-hook.sh"
  RT_CONF=(RT_MODE=toctou RT_TOCTOU_AT=2 "RT_TOCTOU_HOOK=$OUT/cases/$id/toctou-hook.sh")
  run_wrapper $id "$REQ1" wrap; run_cj $id "$REQ1"
  late_dl=$([[ -f $W_DIR/rec/job/artifacts/session/late.json ]] && echo downloaded || echo absent)
  other_dl=$(find "$W_DIR/rec/job/artifacts" -path "*$OTHER*" 2>/dev/null | wc -l)
  rc_reset; RT_CONF=(RT_MODE=toctou RT_TOCTOU_AT=1 "RT_TOCTOU_HOOK=$OUT/cases/$id/toctou-hook.sh")
  run_reconcile $id "" wrap; rc_reset
  row $id a "late prefix not bound; late bytes are not this job's output; both refused" "$(W); check_job=$CJ_LAST; late.json=$late_dl; other-prefix files downloaded=$other_dl; reconcile rc=$R_RC pass=$R_PASS" \
    "$([[ $other_dl == 0 ]] && echo 'holds(prefix)' || echo BREAK)/$([[ $late_dl == downloaded && $W_CLASS == job_completed ]] && echo 'content-not-bound' || echo ok)" 'holds(prefix)/ok' 'holds(prefix)/content-not-bound'
  prune $id
fi
id=A10b-toctou-after-pod-listing   # the third-party write lands after the pod-prefix listing, before the download (K-2 post-download check)
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"; HOOK_TXT > "$OUT/cases/$id/toctou-hook.sh"
  RT_CONF=(RT_MODE=toctou2 RT_TOCTOU_AT=1 "RT_TOCTOU_HOOK=$OUT/cases/$id/toctou-hook.sh")
  run_wrapper $id "$REQ1" wrap; run_cj $id "$REQ1"
  rc_reset; RT_CONF=(RT_MODE=toctou2 RT_TOCTOU_AT=1 "RT_TOCTOU_HOOK=$OUT/cases/$id/toctou-hook.sh")
  run_reconcile $id "" wrap; rc_reset
  row $id a "the late file is downloaded but the downloaded set differs from objects.json: wrapper not job_completed, reconcile exit 6" "$(W); check_job=$CJ_LAST; reconcile rc=$R_RC pass=$R_PASS objects_match=$R_OM" \
    "$([[ $W_CLASS != job_completed && $R_PASS != true && $R_RC == 6 ]] && echo holds || echo BREAK)" holds BREAK
  prune $id
fi

# A13 receipt pins of K-2 (reconcile only; T1 specific)
for v in A13a-pin-status-wrong A13b-pin-objects-wrong A13c-receipt-object-too-new A13d-pod-object-too-new A13e-receipt-lastmodified-missing; do
  id=$v
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1"; rc_reset
  case $v in
    A13a*) RC_PIN_STATUS=0000000000000000000000000000000000000000000000000000000000000000 ;;
    A13b*) RC_PIN_OBJECTS=0000000000000000000000000000000000000000000000000000000000000000 ;;
    A13c*) touch -d '2026-11-07T03:00:00Z' "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json" ;;
    A13d*) touch -d '2026-11-07T03:00:00Z' "$OUT/cases/$id/fx/s3/runs/$JOB1/$POD/session/plan.json" ;;
    A13e*) RT_CONF=("FAKE_LIST_FAIL=launcher/") ;;
  esac
  run_reconcile $id
  row $id a "K-2: refused, reconcile exit 10, receipt_pins_outcome fail" "reconcile rc=$R_RC pass=$R_PASS locate_exit=$R_LRC pins=$(jq -r .receipt_pins_outcome "$R_DIR/out/reconcile-result.json" 2>/dev/null)" \
    "$([[ $R_RC == 10 && $R_PASS == false ]] && echo holds || { [[ $R_PASS == true ]] && echo BREAK || echo differs; })" holds BREAK
  rc_reset; prune $id
done

# ================================================================ (b) job_completed / exit 0 without this pod's accepted job-exit.json
crash_state() { # exit status 5, a raw-result.json that says submitted true, never 2/3/4 after a submission
  [[ $W_RAW == present && $W_RC == 5 && $W_SUB == true ]] && echo ok || echo crash
}
for v in "B01-jobexit-missing|rm" "B02-jobexit-empty|empty" "B03-jobexit-not-json|notjson" "B04-jobexit-is-directory|dir" \
         'B05-exit-string-42|"42"' "B06-exit-true|true" "B07-exit-false|false" "B08-exit-null|null" "B09-exit-42.5|42.5" "B10-exit-42.0|42.0" "B11-exit-array|[42]" \
         "B11b-exit-exponent|4.2e1" "B11c-exit-negative-zero|-0"; do
  id=${v%%|*}; m=${v#*|}
  want_case $id || continue
  case $m in rm|empty|notjson|dir) mk_case_b $id "$JOB1" "$REQ1" ;; *) mk_case_b $id "$JOB1" "$REQ1" "je_exit=$m" ;; esac
  pd="$OUT/cases/$id/fx/s3/runs/$JOB1/$POD"
  case $m in
    rm) rm -f "$pd/job-exit.json"; regen_sums "$pd" ;;
    empty) : > "$pd/job-exit.json"; regen_sums "$pd" ;;
    notjson) printf 'exit 42\n' > "$pd/job-exit.json"; regen_sums "$pd" ;;
    dir) rm -f "$pd/job-exit.json"; mkdir -p "$pd/job-exit.json"; echo '{"exit_code":42}' > "$pd/job-exit.json/part"; regen_sums "$pd" ;;
  esac
  case $m in rm|empty|notjson|dir) objects_json "$pd" "$JOB1" "$POD" > "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json" ;; esac
  age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ1"
  row $id b "not job_completed, rc 5; raw-result.json written with submitted true; rc never 2/3/4 after a submission" "$(W)" \
    "$([[ $W_CLASS == job_completed || $W_RC == 0 ]] && echo BREAK || { [[ $(crash_state) == crash ]] && echo NOTE-crash || echo holds; })" holds "$(case $id in B03*|B04*) echo NOTE-crash ;; *) echo holds ;; esac)"
  prune $id
done
# B16 rule (b): job-exit.json of another pod / job / exit
for v in "B16a-jobexit-other-pod|je_pod=$OTHER" "B16b-jobexit-other-job|je_job=$JOB2" "B16c-jobexit-ne-container|cexit=43"; do
  id=${v%%|*}
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1" "${v#*|}"
  run_wrapper $id "$REQ1"; rc_reset; run_reconcile $id
  row $id b "not job_completed; reconcile refused (7)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS != job_completed && $R_PASS != true && $R_RC == 7 ]] && echo holds || echo BREAK)" holds holds
  prune $id
done
# B12 rule (a): exit_code as a string passes the wrapper's string comparison (v3b); with a genuine receipt, results_uri equal to the located prefix
for v in 'B12a-ruleA-exit-string-0|0|SUCCEEDED|"0"|succeeded|0' 'B12b-ruleA-exit-string-42|26|FAILED|"42"|failed|42'; do
  IFS='|' read -r id lrc bs ex jst cx <<<"$v"
  want_case $id || continue
  mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB2/$POD/" "$POD" "$lrc" "$bs" "$([[ $lrc == 0 ]] && echo succeeded || echo failed)"
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$POD" "$JOB2" "$POD" "$ex" "$REQ2"; age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id b "not job_completed (exit_code is not an integer)" "$(W); check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo holds)" holds BREAK-wrapper
  prune $id
done
# K4 strict job exit under rule (a) with a genuine receipt (results_uri equal to the located prefix): string, boolean, float and exponent spellings
for v in 'K4-a-string-0|0|SUCCEEDED|"0"|succeeded|0' 'K4-b-string-42|26|FAILED|"42"|failed|42' 'K4-c-true|26|FAILED|true|failed|42' 'K4-d-float-42.0|26|FAILED|42.0|failed|42' \
         'K4-e-exponent|26|FAILED|4.2e1|failed|42' 'K4-f-float-0.0|0|SUCCEEDED|0.0|succeeded|0'; do
  IFS='|' read -r id lrc bs ex jst cx <<<"$v"
  want_case $id || continue
  mk_case_b $id "$JOB2" "$REQ2" "ruri=LOCATED" "rpod=$POD" "je_exit=$ex" "cexit=$cx" "launch_rc=$lrc" "bstatus=$bs" "jstate=$jst"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id b "K-4: not job_completed (the exit code is not a JSON number spelled 0, 42 or 43)" "$(W); check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK || echo holds)" holds holds
  prune $id
done
# B13 pairing matrix on rule (b) (job-exit = container exit = E)
for v in 26:FAILED:42 26:FAILED:43 26:FAILED:0 0:SUCCEEDED:42 0:FAILED:42 26:SUCCEEDED:42 26:NONE:42 25:FAILED:42 1:FAILED:42 26:TIMED_OUT:42 0:SUCCEEDED:0 26:STOPPED:42; do
  IFS=: read -r lrc bs e <<<"$v"; id="B13-pair-${lrc}-${bs}-${e}"
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1" "je_exit=$e" "cexit=$e" "launch_rc=$lrc" "bstatus=$bs"
  run_wrapper $id "$REQ1"
  want=other; [[ $v == 26:FAILED:42 || $v == 26:FAILED:43 ]] && want=job_completed; [[ $bs == TIMED_OUT ]] && want=deadline_hit
  oddv=holds; [[ $v == 0:SUCCEEDED:0 ]] && oddv=NOTE-odd-pairing-accepted   # unchanged by DEC-20261107-a83c51: the 42/43 accept pairing and the class block stay byte-identical (E-2)
  row $id b "class $want" "$(W)" "$([[ $W_CLASS == "$want" ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo NOTE-odd-pairing-accepted || echo differs; })" "$oddv" "$oddv"
  prune $id
done
# B14 partial download (aws exit 1): (i) a listed file lost; (ii) an unlisted object lost; (iii) nothing lost but the exit is 1
for v in "B14a-partial-listed-lost|session/records.jsonl|0" "B14b-partial-unlisted-lost|stray.bin|1" "B14c-partial-nothing-lost||0"; do
  IFS='|' read -r id drop extra <<<"$v"
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1"; pd="$OUT/cases/$id/fx/s3/runs/$JOB1/$POD"
  [[ $extra == 1 ]] && { head -c 64 /dev/zero > "$pd/stray.bin"; age "$OUT/cases/$id/fx/s3"; }   # an object in the prefix that SHA256SUMS and objects.json do not list
  RT_CONF=(RT_MODE=partial "RT_DROP=$drop")
  run_wrapper $id "$REQ1" wrap; run_cj $id "$REQ1"
  rc_reset; RT_CONF=(RT_MODE=partial "RT_DROP=$drop"); run_reconcile $id "" wrap; rc_reset
  row $id b "not job_completed when the download exit is nonzero; reconcile refused" "$(W); check_job=$CJ_LAST; reconcile rc=$R_RC pass=$R_PASS" \
    "$([[ $W_CLASS == job_completed ]] && { [[ $CJ_LAST == CHECK_JOB_OK ]] && echo BREAK-wrapper+check_job || echo BREAK-wrapper-only; } || { [[ $R_PASS == true ]] && echo BREAK-reconcile || echo holds; })" holds \
    "$(case $id in B14a*) echo BREAK-wrapper-only ;; B14b*) echo BREAK-wrapper+check_job ;; *) echo BREAK-wrapper+check_job ;; esac)"
  prune $id
done
# B15 non-JSON launcher files after the submission (K-5)
for v in "B15a-result-not-json|result" "B15b-build-not-json|build" "B15c-result-array|resultarray" "B15d-result-empty|resultempty" "B15e-status-not-json|statusbad" "B15f-objects-not-json|objectsbad"; do
  id=${v%%|*}; m=${v#*|}
  want_case $id || continue
  mk_case_b $id "$JOB1" "$REQ1"
  case $m in result) echo 'not json' > "$OUT/cases/$id/fx/launcher/result.json" ;; build) echo 'not json' > "$OUT/cases/$id/fx/launcher/build.json" ;;
             resultarray) echo '[1]' > "$OUT/cases/$id/fx/launcher/result.json" ;; resultempty) : > "$OUT/cases/$id/fx/launcher/result.json" ;;
             statusbad) echo 'not json' > "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/status.json" ;;
             objectsbad) echo 'not json' > "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json" ;; esac
  age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ1"
  row $id b "K-5: not job_completed; rc 5; a raw-result.json with submitted:true" "$(W)" "$([[ $W_CLASS == job_completed ]] && echo BREAK || { [[ $(crash_state) == crash ]] && echo NOTE-crash || echo holds; })" holds "$(case $id in B15a*|B15b*|B15c*) echo NOTE-crash ;; *) echo holds ;; esac)"
  prune $id
done
# K5 the safety net: a failure no parse guard anticipates (a downloaded file name with a newline makes the job_files inventory fail)
id=K5-newline-file-name
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"
  odd="$(printf 'odd\nname.txt')"; printf 'x' > "$OUT/cases/$id/fx/s3/runs/$JOB1/$POD/$odd"
  f="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json"   # objects.json lists it too (built by hand, so the key keeps its newline)
  jq --arg k "runs/$JOB1/$POD/$odd" --arg e "\"$(printf x | md5sum | cut -d ' ' -f1)\"" '.objects += [{Key:$k, Size:1, ETag:$e}]' "$f" > "$f.t" && mv "$f.t" "$f"
  age "$OUT/cases/$id/fx/s3"
  run_wrapper $id "$REQ1"
  row $id b "not job_completed (the file set differs from objects.json), rc 5, raw-result.json with submitted true" "$(W)" \
    "$([[ $W_RAW == present && $W_RC == 5 && $W_SUB == true && $W_CLASS == other ]] && echo holds || echo NOTE-crash)" holds NOTE-crash
  prune $id
fi
id=K5b-record-write-fails   # a failure no parse guard anticipates: manifest.yaml cannot be written (it is a directory). The ERR handler must still leave raw-result.json
if want_case $id; then
  mk_case_b $id "$JOB1" "$REQ1"
  RT_PRE_REC='mkdir "$w/rec/manifest.yaml"'
  run_wrapper $id "$REQ1"; RT_PRE_REC=""
  row $id b "K-5: the ERR handler rewrites raw-result.json (submitted true, class other, never job_completed) and the exit status is 5" "$(W); handler lines=$(grep -c 'post-submission failure' "$W_DIR/stderr")" \
    "$([[ $W_RAW == present && $W_RC == 5 && $W_SUB == true && $W_CLASS == other && $(grep -c 'post-submission failure' "$W_DIR/stderr") -ge 1 ]] && echo holds || echo NOTE-crash)" holds NOTE-crash
  prune $id
fi

# ================================================================ (c) can reconcile_run.sh / launch_eks.sh submit or write
ATT="$OUT/attacker"; mkdir -p "$ATT"
cat > "$ATT/payload.sh" <<'PAY'
# attacker payload (sourced). It acts only when the PATH aws is the offline fake, and at most once per process tree.
# Its two calls are an S3 write and a CodeBuild start-build; the fake refuses the first (exit 99), rejects the second as
# unsupported (exit 97), and logs both. No real AWS endpoint can be reached from here.
if [[ -z ${RT_IN_PAYLOAD:-} ]]; then
  case "$(readlink -f "$(type -P aws)")" in
    */implementation/tests/fake-aws|*/fixtures/isobin-wrap/aws|*/tests/fake-aws)
      export RT_IN_PAYLOAD=1
      echo "RT-PAYLOAD ran via ${RT_VECTOR:-?} phase=${C1_ENV_PHASE:-none} in pid $$" >> "${RT_MARK:?}"
      command aws s3 cp /etc/hostname "s3://rt-9d2b6a-no-such-bucket/payload-${RT_VECTOR:-x}" >/dev/null 2>&1
      command aws codebuild start-build --project-name rt-9d2b6a-no-such-project >/dev/null 2>&1 ;;
  esac
fi
PAY
mk_case_b C00-base "$JOB1" "$REQ1"
cvec() { # cvec ID VECTOR : report one environment vector
  local id=$1 vec=$2 marks p2 wr
  marks=$(grep -c RT-PAYLOAD "$OUT/cases/$id/mark.txt" 2>/dev/null); marks=${marks:-0}
  p2=$(grep -c 'phase=2' "$OUT/cases/$id/mark.txt" 2>/dev/null); p2=${p2:-0}
  wr=$(grep -c -E '^aws s3 cp [^ ]+ s3://|^aws codebuild start-build' "$R_DIR/aws.log" 2>/dev/null); wr=${wr:-0}
  CV_MARKS=$marks; CV_P2=$p2; CV_WR=$wr
  CV_OBS="vector=$vec payload_runs=$marks payload_runs_in_the_clean_phase=$p2 write_or_submit_calls_reaching_aws=$wr reconcile rc=$R_RC pass=$R_PASS"
}
newcase() { rm -rf "$OUT/cases/$1"; mkdir -p "$OUT/cases/$1"; cp -a "$OUT/cases/C00-base/fx" "$OUT/cases/$1/fx"; : > "$OUT/cases/$1/mark.txt"; }
for vec in BASH_ENV EXPORTED_FUNCTION PATH_SHIM; do
  id="C01-$vec"
  want_case $id || continue
  newcase $id; rc_reset
  case $vec in
    BASH_ENV) run_reconcile $id "" plain BASH_ENV="$ATT/payload.sh" RT_VECTOR=BASH_ENV RT_MARK="$OUT/cases/$id/mark.txt" ;;
    EXPORTED_FUNCTION) run_reconcile $id "" plain "BASH_FUNC_aws%%=() { RT_VECTOR=exported-function; . $ATT/payload.sh; command aws \"\$@\"; }" RT_MARK="$OUT/cases/$id/mark.txt" ;;
    PATH_SHIM) mkdir -p "$ATT/shim"; printf '#!/bin/bash\nRT_VECTOR=PATH-python3 . %s\nexec /usr/bin/python3 "$@"\n' "$ATT/payload.sh" > "$ATT/shim/python3"; chmod +x "$ATT/shim/python3"
               # the shim directory (a python3 shim, no aws) is ahead of the case's aws directory on PATH, as in 9d2b6a; a later PATH= assignment
               # overrides the one run_reconcile sets. In v3c the prologue keeps only the directory of the first aws, so the shim never runs.
               run_reconcile $id "" plain "PATH=$ATT/shim:$OUT/cases/$id/rec/bin:/usr/bin:/bin" RT_MARK="$OUT/cases/$id/mark.txt" ;;
  esac
  cvec $id $vec
  case $vec in
    BASH_ENV) # the payload runs once in the caller's bash before the first line of the script (no script can prevent that); K-7 must keep it out of the clean phase
      row $id c "K-7: BASH_ENV is cleared (listed as dropped) and the payload never runs in the clean phase; pre-script runs are residual" "$CV_OBS; k7 line: $(grep -o 'dropped=\[[^]]*\]' "$R_DIR/stdout" | head -1)" \
        "$([[ $CV_P2 == 0 && $R_PASS == true && $(grep -c 'dropped=\[.*BASH_ENV' "$R_DIR/stdout") == 1 ]] && echo holds || { [[ $CV_P2 -gt 0 || ( $MODE == legacy && $CV_WR -gt 0 ) ]] && echo BREAK-env || echo differs; })" holds BREAK-env ;;
    *) row $id c "K-7: no payload run, no write or submit call reaching aws" "$CV_OBS" "$([[ $CV_WR -gt 0 || $CV_MARKS -gt 0 ]] && echo BREAK-env || { [[ $R_PASS == true ]] && echo holds || echo differs; })" holds BREAK-env ;;
  esac
  prune $id
done
# C01w the same vectors against launch_eks.sh (the wrapper)
for vec in BASH_ENV EXPORTED_FUNCTION; do
  id="C01w-$vec"
  want_case $id || continue
  newcase $id; rc_reset
  case $vec in
    BASH_ENV) run_wrapper $id "$REQ1" plain BASH_ENV="$ATT/payload.sh" RT_VECTOR=BASH_ENV RT_MARK="$OUT/cases/$id/mark.txt" ;;
    EXPORTED_FUNCTION) run_wrapper $id "$REQ1" plain "BASH_FUNC_aws%%=() { RT_VECTOR=exported-function; . $ATT/payload.sh; command aws \"\$@\"; }" RT_MARK="$OUT/cases/$id/mark.txt" ;;
  esac
  marks=$(grep -c RT-PAYLOAD "$OUT/cases/$id/mark.txt" 2>/dev/null); p2=$(grep -c 'phase=2' "$OUT/cases/$id/mark.txt" 2>/dev/null)
  row $id c "K-7 on launch_eks.sh: the payload never runs in the clean phase" "vector=$vec payload_runs=${marks:-0} in_clean_phase=${p2:-0}; $(W)" \
    "$([[ ${p2:-0} -gt 0 || ( $vec == EXPORTED_FUNCTION && ${marks:-0} -gt 0 ) ]] && echo BREAK-env || { [[ $W_CLASS == job_completed ]] && echo holds || echo differs; })" holds BREAK-env
  prune $id
done
# C02 CDPATH + the runbook's relative argv path: `here=$(cd "$(dirname ...)" && pwd)` resolved to an attacker directory in v3b
id=C02-CDPATH-relative-argv
if want_case $id; then
  newcase $id; rc_reset
  CDA=$(mktemp -d "${TMPDIR:-/tmp}/rt-d07e94-cdpath.XXXXXX")
  rel=experiments/EXP-ICPERF-127dbd/implementation
  REPO="$OUT/cases/$id/repo"; mkdir -p "$REPO/$rel" "$REPO/experiments/EXP-ICPERF-127dbd/inputs"
  cp "$IMPL/reconcile_run.sh" "$IMPL/locate_results.sh" "$CHECKJOB" "$REPO/$rel/"; chmod +x "$REPO/$rel/"*.sh
  cp "$REQ1" "$REPO/experiments/EXP-ICPERF-127dbd/inputs/"
  mkdir -p "$CDA/$rel"
  hij="$CDA/$rel"$'\n'"$CDA/$rel"                          # the value `here` took in v3b: two lines, both the attacker path
  mkdir -p "$hij"
  printf '#!/bin/bash\nRT_VECTOR=CDPATH . %s\nexec bash %s "$@"\n' "$ATT/payload.sh" "$IMPL/locate_results.sh" > "$hij/locate_results.sh"; chmod +x "$hij/locate_results.sh"
  w="$OUT/cases/$id/rec"; mkdir -p "$w/s3root" "$w/home" "$w/out"; cp -a "$OUT/cases/$id/fx/s3/." "$w/s3root/"; : > "$w/aws.log"
  mk_bin "$w/bin" "$w/s3root" "$w/aws.log" plain
  rcd="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID"
  newargs=(--out-root "$w" --pin-status-sha256 "$(sha256sum "$rcd/status.json" | cut -d ' ' -f1)" --pin-objects-sha256 "$(sha256sum "$rcd/objects.json" | cut -d ' ' -f1)" --pin-not-after "$PIN_NA"); [[ $MODE == legacy ]] && newargs=()
  ( cd "$REPO" && env PATH="$w/bin:/usr/bin:/bin" HOME="$w/home" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" CDPATH="$CDA" RT_MARK="$OUT/cases/$id/mark.txt" \
    bash "$rel/reconcile_run.sh" --launcher-result "$OUT/cases/$id/fx/launcher/result.json" \
    --launcher-result-sha256 "$(sha256sum "$OUT/cases/$id/fx/launcher/result.json" | cut -d ' ' -f1)" --request "experiments/EXP-ICPERF-127dbd/inputs/request-s1.json" \
    --check-job "$rel/check_job.py" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/out" "${newargs[@]}" > "$w/stdout" 2> "$w/stderr" ); R_RC=$?; R_DIR=$w
  R_PASS=$(jq -r '.reconcile_pass | tostring' "$w/out/reconcile-result.json" 2>/dev/null || echo absent)
  cvec $id "CDPATH(relative argv as in runbook S02)"
  row $id c "K-7: the hijacked locator never runs; the genuine locator runs and reconcile passes" "$CV_OBS" "$([[ $CV_WR -gt 0 || $CV_MARKS -gt 0 ]] && echo BREAK-env || { [[ $R_PASS == true ]] && echo holds || echo differs; })" holds BREAK-env
  rm -rf "$CDA"; prune $id
fi
# C02b CDPATH=. with the relative argv: in v3b `here` got two lines and the locator was not found
id=C02b-CDPATH-dot
if want_case $id; then
  newcase $id; rc_reset
  REPO="$OUT/cases/$id/repo"; rel=experiments/EXP-ICPERF-127dbd/implementation; mkdir -p "$REPO/$rel" "$REPO/experiments/EXP-ICPERF-127dbd/inputs"
  cp "$IMPL/reconcile_run.sh" "$IMPL/locate_results.sh" "$CHECKJOB" "$REPO/$rel/"; chmod +x "$REPO/$rel/"*.sh; cp "$REQ1" "$REPO/experiments/EXP-ICPERF-127dbd/inputs/"
  w="$OUT/cases/$id/rec"; mkdir -p "$w/s3root" "$w/home" "$w/out"; cp -a "$OUT/cases/$id/fx/s3/." "$w/s3root/"; : > "$w/aws.log"; mk_bin "$w/bin" "$w/s3root" "$w/aws.log" plain
  rcd="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID"
  newargs=(--out-root "$w" --pin-status-sha256 "$(sha256sum "$rcd/status.json" | cut -d ' ' -f1)" --pin-objects-sha256 "$(sha256sum "$rcd/objects.json" | cut -d ' ' -f1)" --pin-not-after "$PIN_NA"); [[ $MODE == legacy ]] && newargs=()
  ( cd "$REPO" && env PATH="$w/bin:/usr/bin:/bin" HOME="$w/home" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" CDPATH=. \
    bash "$rel/reconcile_run.sh" --launcher-result "$OUT/cases/$id/fx/launcher/result.json" \
    --launcher-result-sha256 "$(sha256sum "$OUT/cases/$id/fx/launcher/result.json" | cut -d ' ' -f1)" --request "experiments/EXP-ICPERF-127dbd/inputs/request-s1.json" \
    --check-job "$rel/check_job.py" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/out" "${newargs[@]}" > "$w/stdout" 2> "$w/stderr" ); R_RC=$?
  row $id c "robustness: an exported CDPATH should not change the result" "reconcile rc=$R_RC; $(grep -m1 -o 'No such file or directory' "$w/stderr" || echo -)" "$([[ $R_RC == 0 ]] && echo holds || echo NOTE-fails-closed)" holds NOTE-fails-closed
  prune $id
fi
# C03 ISOLAB_BUCKET override (attacker bucket): must fail before any AWS call
id=C03-ISOLAB_BUCKET-override
if want_case $id; then
  newcase $id; rc_reset; RC_BUCKET=rt-9d2b6a-elsewhere; run_reconcile $id; rc_reset
  row $id c "refused with zero AWS calls (the version probe is not an AWS call)" "reconcile rc=$R_RC pass=$R_PASS aws_calls=$R_CALLS" "$([[ $R_PASS != true && $R_CALLS == 0 ]] && echo holds || { [[ $R_PASS == true ]] && echo BREAK || echo differs; })" holds holds
  prune $id
fi
# C04 --out through a symlink into a runs/ directory (v3b: lexical check only)
id=C04-out-symlink-into-runs
if want_case $id; then
  newcase $id; rc_reset; mkdir -p "$OUT/cases/$id/fakerepo/runs/RUN-X/job/empty"
  ln -s "$OUT/cases/$id/fakerepo/runs/RUN-X/job/empty" "$OUT/cases/$id/outlink"
  RC_OUTARG="$OUT/cases/$id/outlink"; run_reconcile $id; rc_reset
  n_in_runs=$(find "$OUT/cases/$id/fakerepo/runs" -type f | wc -l)
  row $id c "refuse an --out that resolves inside runs/ (K-7: realpath)" "reconcile rc=$R_RC files written under fakerepo/runs=$n_in_runs" "$([[ $n_in_runs -gt 0 ]] && echo NOTE-lexical-only || { [[ $R_RC == 2 ]] && echo holds || echo differs; })" holds NOTE-lexical-only
  find "$OUT/cases/$id/fakerepo/runs" -type f -path '*/artifacts/*' -delete; prune $id
fi
id=C04b-out-outside-out-root   # an --out that is a clean directory outside --out-root
if want_case $id; then
  newcase $id; rc_reset; mkdir -p "$OUT/cases/$id/elsewhere"; RC_OUTARG="$OUT/cases/$id/elsewhere"; run_reconcile $id; rc_reset
  n_out=$(find "$OUT/cases/$id/elsewhere" -type f | wc -l)
  row $id c "K-7: refuse an --out outside --out-root (exit 2), nothing written" "reconcile rc=$R_RC files written outside=$n_out" "$([[ $n_out -gt 0 ]] && echo NOTE-accepted || { [[ $R_RC == 2 ]] && echo refused || echo differs; })" refused NOTE-accepted
  prune $id
fi
id=C04c-out-runs-inside-out-root   # an --out inside --out-root whose path holds a runs/ segment: only the runs/ check refuses it
if want_case $id; then
  newcase $id; rc_reset; RC_OUTARG="$OUT/cases/$id/rec/runs/x"; run_reconcile $id; rc_reset
  n_runs=$(find "$OUT/cases/$id/rec/runs" -type f 2>/dev/null | wc -l)
  row $id c "K-7: refuse an --out with a runs/ segment even inside --out-root (exit 2), nothing written" "reconcile rc=$R_RC files written under runs/=$n_runs" "$([[ $n_runs -gt 0 ]] && echo NOTE-accepted || { [[ $R_RC == 2 ]] && echo refused || echo differs; })" refused NOTE-accepted
  prune $id
fi
# C06 AWS_ENDPOINT_URL* (the aws-cli service-specific endpoint redirect) and the aws-cli configuration surface
for vec in AWS_ENDPOINT_URL AWS_ENDPOINT_URL_S3; do
  id=C06-$vec
  want_case $id || continue
  newcase $id; rc_reset; run_reconcile $id "" plain "$vec=http://127.0.0.1:1"; rc_reset
  row $id c "K-7: refused (exit 2) before any aws call" "reconcile rc=$R_RC aws_calls=$R_CALLS; $(grep -o 'refused: AWS_ENDPOINT_URL[A-Z_]* is set' "$R_DIR/stderr" | head -1)" "$([[ $R_RC == 2 && $R_CALLS == 0 ]] && echo refused || { [[ $R_PASS == true ]] && echo NOTE-accepted || echo differs; })" refused NOTE-accepted
  prune $id
done
id=C06w-AWS_ENDPOINT_URL_S3-wrapper
if want_case $id; then
  newcase $id; rc_reset; run_wrapper $id "$REQ1" plain AWS_ENDPOINT_URL_S3=http://127.0.0.1:1
  row $id c "K-7 on launch_eks.sh: refused (exit 2), nothing submitted, no raw-result.json" "$(W)" "$([[ $W_RC == 2 && $W_RAW == absent ]] && echo refused || { [[ $W_CLASS == job_completed ]] && echo NOTE-accepted || echo differs; })" refused NOTE-accepted
  prune $id
fi
for vec in alias credential_process endpoint_url plugins; do
  id=C07-config-$vec
  want_case $id || continue
  newcase $id; rc_reset; hm="$OUT/cases/$id/home"; mkdir -p "$hm/.aws/cli"
  case $vec in
    alias) printf '[toplevel]\nwhoami = sts get-caller-identity\ncp = !cp\n' > "$hm/.aws/cli/alias" ;;
    credential_process) printf '[default]\nregion = us-east-2\ncredential_process = /bin/echo not-a-secret\n' > "$hm/.aws/config" ;;
    endpoint_url) printf '[default]\nregion = us-east-2\nservices = s3-ep\n[services s3-ep]\ns3 =\n  endpoint_url = http://127.0.0.1:1\n' > "$hm/.aws/config" ;;
    plugins) printf '[plugins]\ncli_legacy_plugin_path = /tmp/evil\n' > "$hm/.aws/config" ;;
  esac
  RT_HOME=$hm; run_reconcile $id; RT_HOME=""; rc_reset
  row $id c "K-7: refused (exit 2) and the entry name is printed, never its value" "reconcile rc=$R_RC aws_calls=$R_CALLS; $(grep -o 'aws-cli configuration entry:[^(]*' "$R_DIR/stderr" | head -1)" \
    "$([[ $R_RC == 2 && $R_CALLS == 0 && $(grep -c -E 'not-a-secret|127.0.0.1|/tmp/evil|sts get-caller' "$R_DIR/stderr" "$R_DIR/stdout" | awk -F: '{s+=$2} END {print s+0}') == 0 ]] && echo refused || { [[ $R_PASS == true ]] && echo NOTE-accepted || echo differs; })" refused NOTE-accepted
  prune $id
done
id=C07w-config-credential_process-wrapper
if want_case $id; then
  newcase $id; rc_reset; hm="$OUT/cases/$id/home"; mkdir -p "$hm/.aws"; printf '[default]\ncredential_process = /bin/echo not-a-secret\n' > "$hm/.aws/config"
  RT_HOME=$hm; run_wrapper $id "$REQ1"; RT_HOME=""
  row $id c "K-7 on launch_eks.sh: refused (exit 2), nothing submitted" "$(W)" "$([[ $W_RC == 2 && $W_RAW == absent ]] && echo refused || { [[ $W_CLASS == job_completed ]] && echo NOTE-accepted || echo differs; })" refused NOTE-accepted
  prune $id
fi
# C08 the version pin: an aws that does not report aws-cli/1.46.2
id=C08-aws-version-mismatch
if want_case $id; then
  newcase $id; rc_reset; run_reconcile $id; rc_reset   # first make the bin, then replace aws by a fake that reports another version
  w="$OUT/cases/$id/rec"; rm -f "$w/bin/aws"; printf '#!/usr/bin/env bash\n[[ ${1:-} == --version ]] && echo "aws-cli/2.15.0 Python/3.11 Linux/6" && exit 0\nexit 97\n' > "$w/bin/aws"; chmod +x "$w/bin/aws"
  rcd="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID"
  R_RC=0; env PATH="$w/bin:/usr/bin:/bin" HOME="$w/home" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" bash "$IMPL/reconcile_run.sh" --launcher-result "$OUT/cases/$id/fx/launcher/result.json" \
    --launcher-result-sha256 "$(sha256sum "$OUT/cases/$id/fx/launcher/result.json" | cut -d ' ' -f1)" --request "$REQ1" --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 \
    --out "$w/out2" --out-root "$w" --pin-status-sha256 "$(sha256sum "$rcd/status.json" | cut -d ' ' -f1)" --pin-objects-sha256 "$(sha256sum "$rcd/objects.json" | cut -d ' ' -f1)" --pin-not-after "$PIN_NA" > "$w/stdout2" 2> "$w/stderr2" || R_RC=$?
  row $id c "K-7: refused (exit 2) an aws that is not the pinned aws-cli/1.46.2" "reconcile rc=$R_RC; $(grep -o "reports '[^']*'" "$w/stderr2" | head -1)" "$([[ $R_RC == 2 ]] && echo refused || echo NOTE-accepted)" refused refused
  prune $id
fi
# C09 spoofing the phase marker: C1_ENV_PHASE=2 supplied by the caller together with a hostile variable
id=C09-phase-marker-spoof
if want_case $id; then
  newcase $id; rc_reset; run_reconcile $id "" plain C1_ENV_PHASE=2 BASH_ENV="$ATT/payload.sh" RT_VECTOR=spoof RT_MARK="$OUT/cases/$id/mark.txt"; rc_reset
  row $id c "K-7: refused (exit 2): the caller's environment holds variables outside the allowlist" "reconcile rc=$R_RC aws_calls=$R_CALLS; $(grep -o 'allowlist are set:[ A-Z_]*' "$R_DIR/stderr" | head -1)" "$([[ $R_RC == 2 && ! -f $R_DIR/out/reconcile-result.json ]] && echo refused || echo NOTE-accepted)" refused refused
  prune $id
fi
id=C09b-phase-marker-spoof-pythonpath   # the same spoof with a variable that no other check names: only the allowlist refuses it
if want_case $id; then
  newcase $id; rc_reset; run_reconcile $id "" plain C1_ENV_PHASE=2 PYTHONPATH=/nonexistent-pythonpath; rc_reset
  row $id c "K-7: refused (exit 2): PYTHONPATH is outside the allowlist" "reconcile rc=$R_RC aws_calls=$R_CALLS; $(grep -o 'allowlist are set:[ A-Z_]*' "$R_DIR/stderr" | head -1)" "$([[ $R_RC == 2 && ! -f $R_DIR/out/reconcile-result.json ]] && echo refused || echo NOTE-accepted)" refused NOTE-accepted
  prune $id
fi
id=C09w-phase-marker-spoof-wrapper   # the same spoof against launch_eks.sh, whose `here` line (section 1b, unchanged) uses a bare `cd`
if want_case $id; then
  newcase $id; rc_reset; run_wrapper $id "$REQ1" plain C1_ENV_PHASE=2 CDPATH=/tmp
  row $id c "K-7 on launch_eks.sh: refused (exit 2), nothing submitted, no raw-result.json (CDPATH is outside the allowlist)" "$(W); $(grep -o 'allowlist are set:[ A-Z_]*' "$W_DIR/stderr" | head -1)" \
    "$([[ $W_RC == 2 && $W_RAW == absent ]] && echo refused || { [[ $W_CLASS == job_completed ]] && echo NOTE-accepted || echo differs; })" refused NOTE-accepted
  prune $id
fi
id=C02w-CDPATH-wrapper   # an exported CDPATH never reaches launch_eks.sh's `cd`: env -i drops it, the run is the A00 control
if want_case $id; then
  newcase $id; rc_reset; run_wrapper $id "$REQ1" plain CDPATH=/nonexistent-cdpath
  row $id c "K-7 on launch_eks.sh: CDPATH is dropped before section 1b; job_completed as the control" "$(W)" \
    "$([[ $W_RC == 0 && $W_CLASS == job_completed ]] && echo holds || echo differs)" holds holds
  prune $id
fi
# C10 the credential variables cross the exec by name; other AWS_* variables and PYTHONPATH do not
id=C10-credentials-by-name
if want_case $id; then
  newcase $id; rc_reset; RT_CONF=(FAKE_LOG_ENVNAMES=1)
  run_reconcile $id "" plain AWS_ACCESS_KEY_ID=AKIAFAKEFAKEFAKE AWS_SECRET_ACCESS_KEY=fakefakefake AWS_SESSION_TOKEN=fakefakefake AWS_PROFILE=hostile AWS_CONFIG_FILE=/nonexistent PYTHONPATH=/nonexistent; rc_reset
  names=$(grep '^ENVNAMES' "$R_DIR/aws.log" | sed -n 2p | sed 's/^ENVNAMES //; s/PATHDIRS=.*//')
  row $id c "K-7: the aws process sees the three credential names and the region, and neither AWS_PROFILE, AWS_CONFIG_FILE nor PYTHONPATH" "reconcile rc=$R_RC pass=$R_PASS; names seen by aws: $names" \
    "$([[ $names == 'AWS_ACCESS_KEY_ID AWS_DEFAULT_REGION AWS_REGION AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN ' && $R_PASS == true ]] && echo holds || echo differs)" holds holds
  prune $id
fi
# C11 the executor's python and helper commands come from the clean PATH: a python3 shim ahead of the case aws directory is not run
id=C11-python-shim-ahead-of-aws
if want_case $id; then
  newcase $id; rc_reset; mkdir -p "$ATT/shim2"; printf '#!/bin/bash\necho "RT-PAYLOAD ran via PATH-python3-ahead phase=${C1_ENV_PHASE:-none} in pid $$" >> "${RT_MARK:?}"\nexec /usr/bin/python3 "$@"\n' > "$ATT/shim2/python3"; chmod +x "$ATT/shim2/python3"
  w="$OUT/cases/$id/rec"; mkdir -p "$w"
  run_reconcile $id "" plain RT_MARK="$OUT/cases/$id/mark.txt"   # the case bin comes first; the shim is made reachable only through PATH order below
  : > "$OUT/cases/$id/mark.txt"; rc_reset
  # PATH = shim2 : case bin : /usr/bin : /bin  (the case bin still holds the first aws that is found? no: shim2 holds no aws, so the aws directory is the case bin)
  w="$OUT/cases/$id/rec"; rcd="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID"; rm -rf "$w/out"; mkdir -p "$w/out"
  R_RC=0; env PATH="$ATT/shim2:$w/bin:/usr/bin:/bin" HOME="$w/home" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" RT_MARK="$OUT/cases/$id/mark.txt" \
    bash "$IMPL/reconcile_run.sh" --launcher-result "$OUT/cases/$id/fx/launcher/result.json" --launcher-result-sha256 "$(sha256sum "$OUT/cases/$id/fx/launcher/result.json" | cut -d ' ' -f1)" \
    --request "$REQ1" --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/out" --out-root "$w" \
    --pin-status-sha256 "$(sha256sum "$rcd/status.json" | cut -d ' ' -f1)" --pin-objects-sha256 "$(sha256sum "$rcd/objects.json" | cut -d ' ' -f1)" --pin-not-after "$PIN_NA" > "$w/stdout" 2> "$w/stderr" || R_RC=$?
  R_PASS=$(jq -r '.reconcile_pass | tostring' "$w/out/reconcile-result.json" 2>/dev/null || echo absent)
  row $id c "K-7: the python3 shim ahead of the aws directory does not run, and reconcile passes" "reconcile rc=$R_RC pass=$R_PASS shim_runs=$(grep -c RT-PAYLOAD "$OUT/cases/$id/mark.txt")" \
    "$([[ $(grep -c RT-PAYLOAD "$OUT/cases/$id/mark.txt") -gt 0 ]] && echo BREAK-env || { [[ $R_PASS == true ]] && echo holds || echo differs; })" holds BREAK-env
  prune $id
fi
# C05 static scan of the reconcile-path scripts
if want_case C05-static-scan; then
  {
    echo "# C05 static scan (the 9d2b6a patterns, over non-comment lines)"
    for f in reconcile_run.sh locate_results.sh; do
      echo "== $f"
      echo "-- submit/write tokens (case-insensitive): $(grep -v '^[[:space:]]*#' "$IMPL/$f" | grep -c -i -E 'launch-remote|codebuild|start-build|batch-get|put-object|delete-object|copy-object|s3 (rm|mv|sync|mb|rb|presign|website)|kubectl|isolab-eks-mcp|aws eks|aws sts|aws iam|curl|wget|/dev/tcp') non-comment lines"
      echo "-- s3api tokens: $(grep -v '^[[:space:]]*#' "$IMPL/$f" | grep -c 's3api') non-comment lines"
      echo "-- source / eval / exec of a variable: $(grep -v '^[[:space:]]*#' "$IMPL/$f" | grep -c -E '(^|[;&|[:space:]])(source|eval)[[:space:]]|(^|[;&|[:space:]])\.[[:space:]]+[^ ]')"
      echo "-- exec: $(grep -v '^[[:space:]]*#' "$IMPL/$f" | grep -E '(^|[;&|[:space:]])exec[[:space:]]' | sed 's/^[[:space:]]*//' | cut -c1-90 | tr '\n' '|')"
      echo "-- test hooks (FAKE_/RT_/TEST/DEBUG/HOOK env names): $(grep -v '^[[:space:]]*#' "$IMPL/$f" | grep -c -E 'FAKE_|RT_|TEST|DEBUG|HOOK')"
      echo "-- environment variables read: $(grep -v '^[[:space:]]*#' "$IMPL/$f" | grep -o -E '\$\{?[A-Z][A-Z0-9_]+' | tr -d '${' | LC_ALL=C sort -u | tr '\n' ' ')"
    done
  } > "$OUT/C05-static-scan.txt"
  n=$(grep -c -E -- '-- submit/write tokens \(case-insensitive\): 0 ' "$OUT/C05-static-scan.txt")
  row C05-static-scan c "no submit/write token in the bytes" "$n/2 scripts clean; details C05-static-scan.txt" "$([[ $n == 2 ]] && echo holds || echo BREAK)" holds holds
fi
rm -rf "$OUT/cases/C00-base"

echo "== summary: $NROW rows, $NFAIL differ from the expected outcome" | tee "$OUT/rt-summary.txt"
awk -F'\t' 'NR>1 {print $5}' "$TABLE" | sed 's/[(/].*//' | LC_ALL=C sort | uniq -c | tr '\n' ';' | tee -a "$OUT/rt-summary.txt"; echo
exit "$NFAIL"
