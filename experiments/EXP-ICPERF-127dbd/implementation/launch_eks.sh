#!/usr/bin/env bash
# Thin wrapper: submit one FROZEN C1 request through the isolab-eks route (launch-remote), once.
# No study logic. It runs only as the argv of a supervised trial (PROTOCOL section 18, revision 6; rulings of 2026-11-06).
#
# usage: launch_eks.sh [--dry-run] --protocol PROTOCOL.json
#          --experiment-id E --hypothesis-id H --task-id T --approved-by D --trial-id ID --run-id RUN
#          --out RUNDIR/job --record-dir RUNDIR  REQUEST.json
#
#   --protocol    the bound copy of the frozen protocol.json; its extensions.requests lists the four frozen
#                 request sha256 values (exit 2 if REQUEST.json is none of them)
#   ids           literal strings from the frozen trial plan's argv; echoed and recorded, never derived
#   --record-dir  the supervisor's run directory. It must exist and hold the supervisor's launch.json whose run_id
#                 and trial_id equal --run-id and --trial-id, and --out must be exactly <record-dir>/job (exit 2
#                 before any AWS call otherwise). --dry-run is exempt from that refusal.
#   --out         a directory that must not exist; receives launcher/, artifacts/, launch.log, request.json
#   --dry-run     print the exact commands and make NO AWS call (not even a read)
#
# raw-result.json and manifest.yaml are written once, at --record-dir (the trial's declared artifacts).
#
# Environment (never printed except the three non-secret names below):
#   AWS_REGION, ISOLAB_BUCKET, ISOLAB_CODEBUILD_PROJECT, CRYPTO_CHECKOUT   all required
#   CRYPTO_CHECKOUT is the checkout holding taskq/deploy/eks-karpenter/remote; the four scripts there are
#   checked against remote-pins.sha256 (exit 2). AWS credentials come from the caller's ambient identity.
#
# Exit codes: 0 launched and the job exit in {0,42,43} with job-exit.json and SHA256SUMS downloaded;
#   2 usage, unknown request hash, missing environment, pin mismatch or unsupervised run (nothing submitted);
#   3 this job (or this exact request) was already submitted (nothing submitted);
#   4 the duplicate check itself failed (nothing submitted);
#   5 submitted, but the outcome is not a completed job (see raw-result.json outcome_class).
# It never retries: a rerun is a new, separately authorised runbook session.
set -euo pipefail
set +x
# ---- K-7 environment prologue (v3c; DEC-20261107-a83c51 K-7). It is not study logic. ----
# Phase 1 drops every inherited shell function, refuses an AWS_ENDPOINT_URL* variable, and re-executes this script under `env -i`
# with an explicit allowlist: HOME, TMPDIR, AWS_REGION, AWS_DEFAULT_REGION, ISOLAB_BUCKET, CRYPTO_CHECKOUT
# (and ISOLAB_CODEBUILD_PROJECT in launch_eks.sh), the credential variables named in K7_CRED_VARS (never printed), and a PATH of
# exactly <directory of the first aws on the caller's PATH>:/usr/bin:/bin. env -i clears BASH_ENV, ENV, CDPATH, PYTHONPATH, the
# AWS_CONFIG_FILE family and every BASH_FUNC_* export. Phase 2 (C1_ENV_PHASE=2) refuses to start unless the environment is exactly
# that allowlist, no function is defined, aws reports the pinned version, and the aws-cli configuration files hold no
# credential_process, endpoint_url, plugin or alias entry (entry names are printed, values never). Two things no script can
# prevent are residual risks: code that BASH_ENV runs in the caller's bash before the first line here, and the choice of the
# directory that holds aws.
K7_PIN_AWS_CLI=aws-cli/1.46.2
K7_CRED_VARS=(AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN)
K7_CFG_ALLOWED=()   # aws-cli configuration entry names the executor identity is allowed to use; none is allowed
K7_PASS_VARS=(HOME TMPDIR AWS_REGION AWS_DEFAULT_REGION ISOLAB_BUCKET ISOLAB_CODEBUILD_PROJECT CRYPTO_CHECKOUT)
if [[ ${C1_ENV_PHASE:-} != 2 ]]; then
  k7_fns=""
  while IFS= read -r k7_l; do
    [[ -n $k7_l ]] || continue
    k7_fns+=" ${k7_l##* }"; builtin unset -f -- "${k7_l##* }" 2>/dev/null || true
  done < <(builtin declare -F)
  k7_hits=""
  [[ -v BASH_ENV ]] && k7_hits+=" BASH_ENV"
  [[ -v ENV ]] && k7_hits+=" ENV"
  for k7_n in $(builtin compgen -e); do
    [[ $k7_n == AWS_ENDPOINT_URL* ]] && { echo "k7: refused: $k7_n is set; no AWS_ENDPOINT_URL* variable is allowed" >&2; exit 2; }
  done
  k7_aws=$(builtin type -P aws 2>/dev/null) || { echo "k7: refused: no aws executable on PATH" >&2; exit 2; }
  k7_dir=${k7_aws%/*}
  [[ $k7_aws == /*/aws && $k7_dir != *[[:space:]:]* ]] || { echo "k7: refused: the aws on PATH is not an absolute path to a file named aws" >&2; exit 2; }
  k7_kv=()
  for k7_n in "${K7_PASS_VARS[@]}" "${K7_CRED_VARS[@]}"; do
    [[ -v $k7_n ]] && k7_kv+=("$k7_n=${!k7_n}")
  done
  [[ -x /usr/bin/env && -n ${BASH:-} ]] || { echo "k7: refused: /usr/bin/env or \$BASH is unavailable" >&2; exit 2; }
  exec /usr/bin/env -i "${k7_kv[@]}" "PATH=$k7_dir:/usr/bin:/bin" C1_ENV_PHASE=2 "C1_ENV_DROPPED=$(printf '%s%s' "$k7_hits" "$k7_fns" | tr -c 'A-Za-z0-9_ ' '?')" "$BASH" "$0" "$@"
fi
k7_ok=" PATH C1_ENV_PHASE C1_ENV_DROPPED PWD OLDPWD SHLVL _ ${K7_PASS_VARS[*]} ${K7_CRED_VARS[*]} "
k7_extra=""
for k7_n in $(builtin compgen -e); do [[ $k7_ok == *" $k7_n "* ]] || k7_extra+=" $k7_n"; done
[[ -z $k7_extra ]] || { echo "k7: refused: variables outside the allowlist are set:$k7_extra" >&2; exit 2; }
[[ -z $(builtin declare -F) ]] || { echo "k7: refused: shell functions are defined" >&2; exit 2; }
[[ -v BASH_ENV || -v ENV || -v CDPATH ]] && { echo "k7: refused: BASH_ENV, ENV or CDPATH is set" >&2; exit 2; }
k7_first=${PATH%%:*}
[[ $PATH == "$k7_first:/usr/bin:/bin" && $k7_first == /* ]] || { echo "k7: refused: PATH is not <absolute dir>:/usr/bin:/bin" >&2; exit 2; }
[[ $(builtin type -P aws 2>/dev/null) == "$k7_first/aws" ]] || { echo "k7: refused: aws does not resolve to $k7_first/aws" >&2; exit 2; }
k7_v=$("$k7_first/aws" --version 2>&1 | head -n 1 || true)
[[ ${k7_v%% *} == "$K7_PIN_AWS_CLI" ]] || { echo "k7: refused: aws reports '${k7_v%% *}', not the pinned $K7_PIN_AWS_CLI" >&2; exit 2; }
[[ ${HOME:-} == /* && -d ${HOME:-/nonexistent} ]] || { echo "k7: refused: HOME is not an absolute directory" >&2; exit 2; }
k7_cfg=""
for k7_f in "$HOME/.aws/config" "$HOME/.aws/credentials"; do
  [[ -f $k7_f ]] || continue
  for k7_k in credential_process endpoint_url cli_legacy_plugin_path; do
    grep -q -i -E "^[[:space:]]*$k7_k[[:space:]]*=" "$k7_f" && k7_cfg+=" $k7_k@${k7_f##*/}"
  done
  grep -q -i -E '^[[:space:]]*\[plugins\]' "$k7_f" && k7_cfg+=" plugins@${k7_f##*/}"
done
if [[ -f $HOME/.aws/cli/alias ]] && grep -q -E '^[[:space:]]*[^#;[:space:]\[][^=]*=' "$HOME/.aws/cli/alias"; then k7_cfg+=" alias@alias"; fi
for k7_e in $k7_cfg; do
  [[ " ${K7_CFG_ALLOWED[*]:-} " == *" $k7_e "* ]] || { echo "k7: refused: aws-cli configuration entry:$k7_cfg (names only; values are never printed)" >&2; exit 2; }
done
K7_STATUS="ok aws=$k7_first/aws version=${k7_v%% *} dropped=[${C1_ENV_DROPPED# }] config_entries=[${k7_cfg# }]"
echo "k7_env_hygiene=$K7_STATUS"
unset k7_ok k7_extra k7_n k7_first k7_v k7_f k7_k k7_e
# ---- end of the K-7 prologue ----

dry=0; protocol=""; eid=""; hid=""; tid=""; appr=""; trial=""; runid=""; out=""; rec=""; req=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry=1; shift ;;
    --protocol) protocol=${2:?}; shift 2 ;;
    --experiment-id) eid=${2:?}; shift 2 ;;
    --hypothesis-id) hid=${2:?}; shift 2 ;;
    --task-id) tid=${2:?}; shift 2 ;;
    --approved-by) appr=${2:?}; shift 2 ;;
    --trial-id) trial=${2:?}; shift 2 ;;
    --run-id) runid=${2:?}; shift 2 ;;
    --out) out=${2:?}; shift 2 ;;
    --record-dir) rec=${2:?}; shift 2 ;;
    -*) echo "unknown option $1" >&2; exit 2 ;;
    *) [[ -z $req ]] || { echo "one request only" >&2; exit 2; }; req=$1; shift ;;
  esac
done
usage() { echo "usage: launch_eks.sh [--dry-run] --protocol P --experiment-id E --hypothesis-id H --task-id T --approved-by D --trial-id ID --run-id RUN --out RECORD/job --record-dir RECORD REQUEST.json" >&2; exit 2; }
for v in protocol eid hid tid appr trial runid out rec req; do [[ -n ${!v} ]] || usage; done
[[ -f $req && -f $protocol ]] || { echo "request or protocol file not found" >&2; exit 2; }

echo "experiment_id=$eid hypothesis_id=$hid task_id=$tid approved_by=$appr trial_id=$trial run_id=$runid"
t0=$(date -u +%FT%TZ); s0=$(date -u +%s)

# 1. The request must be byte-identical to one of the four frozen requests.
rsha=$(sha256sum "$req" | cut -d ' ' -f1)
if ! jq -e --arg h "$rsha" '.extensions.requests | to_entries | map(.value) | index($h) != null' "$protocol" >/dev/null; then
  echo "request sha256 $rsha is not one of $protocol extensions.requests" >&2
  exit 2
fi
job=$(jq -er .job.job_name "$req")
echo "request_sha256=$rsha job_name=$job"

for v in AWS_REGION ISOLAB_BUCKET ISOLAB_CODEBUILD_PROJECT CRYPTO_CHECKOUT; do
  [[ -n ${!v:-} ]] || { echo "$v is required" >&2; exit 2; }
done
remote="$CRYPTO_CHECKOUT/taskq/deploy/eks-karpenter/remote"
for f in launch-remote validate-request run-request current-run-request-buildspec.yml; do
  [[ -f $remote/$f ]] || { echo "missing $remote/$f" >&2; exit 2; }
done
echo "region=$AWS_REGION bucket=$ISOLAB_BUCKET codebuild_project=$ISOLAB_CODEBUILD_PROJECT remote=$remote"

# 1b. The launcher scripts must be byte-identical to the pinned v6 versions (remote-pins.sha256).
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
pins="$here/remote-pins.sha256"
[[ -f $pins ]] || { echo "missing $pins" >&2; exit 2; }
npins=0
while read -r want name; do
  [[ -n $want ]] || continue
  have=$(sha256sum "$remote/$name" 2>/dev/null | cut -d ' ' -f1)
  if [[ $have != "$want" ]]; then
    echo "PIN MISMATCH: $remote/$name sha256 ${have:-absent} != pinned $want" >&2
    exit 2
  fi
  npins=$((npins + 1))
done < "$pins"
[[ $npins == 4 ]] || { echo "remote-pins.sha256 must pin exactly 4 scripts, found $npins" >&2; exit 2; }
echo "remote scripts match $npins pinned sha256 values"

# 1c. Supervised run only: the record directory is the supervisor's, for this run and trial (before any AWS call).
if [[ $dry == 0 ]]; then
  [[ -d $rec && -f $rec/launch.json ]] || { echo "not supervised: $rec/launch.json is absent" >&2; exit 2; }
  lrun=$(jq -er .run_id "$rec/launch.json") && ltrial=$(jq -er .trial_id "$rec/launch.json") \
    || { echo "unreadable $rec/launch.json" >&2; exit 2; }
  [[ $lrun == "$runid" && $ltrial == "$trial" ]] \
    || { echo "launch.json run_id/trial_id ($lrun/$ltrial) differ from the argv ($runid/$trial)" >&2; exit 2; }
  want_out="$(cd "$rec" && pwd)/job"
  case "$out" in /*) have_out=$out ;; *) have_out="$(pwd)/$out" ;; esac
  [[ $have_out == "$want_out" ]] || { echo "--out must be exactly <record-dir>/job ($want_out), got $have_out" >&2; exit 2; }
  [[ ! -e $out ]] || { echo "$out already exists" >&2; exit 2; }
fi

# The digest launch-remote will compute: sha256 of validate-request's output (local, no AWS).
validated=$("$remote/validate-request" "$req") || { echo "validate-request refused the request" >&2; exit 2; }
digest=$(printf '%s\n' "$validated" | sha256sum | cut -d ' ' -f1)
key="inputs/requests/$digest.json"
echo "validated_request_sha256=$digest request_key=$key"

client_out="$out/launcher"
cmd_launch=(env "ISOLAB_CLIENT_OUTPUT=$client_out" "$remote/launch-remote" "$req")
if [[ $dry == 1 ]]; then
  echo "DRY RUN: no AWS call is made. Commands that a real run executes, in order:"
  echo "  aws s3 ls s3://$ISOLAB_BUCKET/runs/$job/                       # read: refuse (exit 3) if anything is listed"
  echo "  aws s3 ls s3://$ISOLAB_BUCKET/$key                              # read: refuse (exit 3) if it exists"
  echo "  aws codebuild list-builds-for-project --project-name $ISOLAB_CODEBUILD_PROJECT --sort-order DESCENDING   # read"
  echo "  aws codebuild batch-get-builds --ids <first 100>               # read: refuse (exit 3) if one carries ISOLAB_REQUEST_KEY=$key"
  echo "  ${cmd_launch[*]} > $out/launch.log 2>&1                       # the one submission (writes S3 and starts CodeBuild); never retried"
  echo "  aws s3 cp <results_uri from $client_out/result.json> $out/artifacts --recursive   # read-only download"
  echo "  then raw-result.json and manifest.yaml are written under $rec"
  exit 0
fi

# Records written once at the record directory (the trial's declared artifacts).
inventory() { # job_files: path -> sha256 for every file under $out (empty object if none)
  if [[ -d $out ]]; then
    (cd "$out" && find . -type f | LC_ALL=C sort | while read -r f; do printf '%s  %s\n' "$(sha256sum "$f" | cut -d ' ' -f1)" "${f#./}"; done) \
      | jq -Rn '[inputs | capture("^(?<h>[0-9a-f]{64})  (?<p>.+)$") | {(.p): .h}] | add // {}'
  else
    echo '{}'
  fi
}
write_records() { # write_records JSON_FIELDS_OBJECT
  local extra=$1
  jq -n --arg job "$job" --arg rsha "$rsha" --arg digest "$digest" --arg eid "$eid" --arg hid "$hid" --arg tid "$tid" \
    --arg appr "$appr" --arg trial "$trial" --arg runid "$runid" --argjson files "$(inventory)" --argjson extra "$extra" \
    '{schema:"c1.launch.raw-result/v1", attack_claimed:false, experiment_id:$eid, hypothesis_id:$hid, task_id:$tid,
      approved_by:$appr, trial_id:$trial, run_id:$runid, job_name:$job, request_sha256:$rsha,
      validated_request_sha256:$digest, retried:false, job_files:$files,
      note:"launch evidence only; the job exit is judged from job-exit.json by check_job.py and analyze-c1.sh"} + $extra' \
    > "$rec/raw-result.json"
  # Exit-0 path (outcome job_completed): the flat manifest below, byte-identical to v2; the supervisor completes it
  # (complete_manifest) and validity stays with check_job.py and S03-verify. Exit 3, 4 and 5 paths get no supervisor
  # completion, so they get a schema-complete manifest (schemas/run-manifest.schema.json) instead (DEC-20261106-ecf261
  # ruling on v3a; RBS-ICPERF-e2a5c2 published a schema-invalid manifest).
  if [[ $(jq -r '.outcome_class // empty' <<<"$extra") == job_completed ]]; then
  cat > "$rec/manifest.yaml" <<MANIFEST
run:
  id: $runid
  experiment_id: $eid
  hypothesis_id: $hid
  task_id: $tid
  trial_id: $trial
  approved_by: $appr
  attack_claimed: false
  result:
    raw_result: raw-result.json
MANIFEST
  else
    local commit cmd s1
    commit=$(jq -r '.commit // empty' "$rec/environment.json" 2>/dev/null || true)
    [[ -n $commit ]] || commit=$(git rev-parse HEAD 2>/dev/null || echo unknown)
    cmd=$(cat "$rec/command.txt" 2>/dev/null || true)
    s1=$(date -u +%s)
    jq -n --slurpfile raw "$rec/raw-result.json" --arg commit "$commit" --arg cmd "$cmd" \
      --arg t0 "$t0" --arg t1 "$(date -u +%FT%TZ)" --argjson wall "$((s1 - s0))" \
      '$raw[0] as $r
       | (if $r.submitted != true then "failed_implementation" else "failed_infrastructure" end) as $status
       | {run: {id: $r.run_id, experiment_id: $r.experiment_id, hypothesis_id: $r.hypothesis_id, task_id: $r.task_id,
           trial_id: $r.trial_id, approved_by: $r.approved_by, attack_claimed: false, status: $status,
           code: {commit: $commit, dirty: false, command: $cmd},
           environment: {file: "environment.json", note: "interpreter and source hashes are in the supervisor environment.json"},
           inputs: {parameters: {job_name: $r.job_name, request_sha256: $r.request_sha256,
             validated_request_sha256: $r.validated_request_sha256}},
           timing: {started_at: $t0, finished_at: $t1, wall_seconds: $wall},
           resources: {peak_rss_bytes: null, cpu_seconds: null},
           result: {raw_result: "raw-result.json",
             metrics: {submitted: $r.submitted, outcome_class: $r.outcome_class,
               launch_remote_exit: ($r.launch_remote_exit // null), job_exit_code: ($r.job_exit_code // null)},
             valid: false,
             invalid_reason: ("outcome " + ($r.outcome_class // "none") + (if $r.refusal then ", refusal " + $r.refusal else "" end)
               + "; mechanical wrapper label; the Coordinator classifies the stop"),
             certificate: {kind: "none", verified: false, verifier: "none (launch wrapper; no discrete-log or decomposition claim)"}},
           artifacts: {raw_result: "raw-result.json", job_dir: "job", job_files: ($r.job_files // {})}}}' \
      > "$rec/manifest.yaml"
  fi
}

# 2. Refuse a second submission for this job name or this exact request. Read-only AWS calls.
refuse() { # refuse CODE REASON MESSAGE
  echo "$3" >&2
  write_records "$(jq -n --arg r "$2" '{submitted:false, outcome_class:"other", refusal:$r}')"
  exit "$1"
}
set +e
listing=$(aws s3 ls "s3://$ISOLAB_BUCKET/runs/$job/" 2>/dev/null); rc=$?
set -e
[[ $rc == 0 && -n $listing ]] && refuse 3 duplicate "DUPLICATE: s3://$ISOLAB_BUCKET/runs/$job/ already has objects"
[[ $rc != 0 && $rc != 1 ]] && refuse 4 duplicate_check_failed "duplicate check failed (aws s3 ls exit $rc)"
set +e
aws s3 ls "s3://$ISOLAB_BUCKET/$key" >/dev/null 2>&1; rc=$?
set -e
[[ $rc == 0 ]] && refuse 3 duplicate "DUPLICATE: s3://$ISOLAB_BUCKET/$key exists: this exact request was already submitted"
[[ $rc != 1 ]] && refuse 4 duplicate_check_failed "duplicate check failed (aws s3 ls exit $rc)"
set +e
# --no-paginate: one page (at most 100 ids). aws-cli v1 with --max-items appends the pagination
# token ("None" or a token) to text output, which batch-get-builds rejects as a build id (RBS-ICPERF-e2a5c2).
ids_raw=$(aws codebuild list-builds-for-project --project-name "$ISOLAB_CODEBUILD_PROJECT" --sort-order DESCENDING --no-paginate --query 'ids[]' --output text); rc=$?
ids=$(printf '%s\n' "$ids_raw" | tr '\t ' '\n\n' | grep -E "^${ISOLAB_CODEBUILD_PROJECT}:[0-9a-f-]+$" || true)
set -e
[[ $rc != 0 ]] && refuse 4 duplicate_check_failed "duplicate check failed (codebuild list)"
[[ -n ${ids_raw//[[:space:]]/} && -z $ids ]] && refuse 4 duplicate_check_failed "duplicate check failed (codebuild list returned no build id: $ids_raw)"
if [[ -n $ids ]]; then
  set +e
  # shellcheck disable=SC2086
  hit=$(aws codebuild batch-get-builds --ids $ids --query "builds[?environment.environmentVariables[?name=='ISOLAB_REQUEST_KEY' && value=='$key']].id" --output text); rc=$?
  set -e
  [[ $rc != 0 ]] && refuse 4 duplicate_check_failed "duplicate check failed (codebuild batch-get-builds)"
  [[ -n $hit ]] && refuse 3 duplicate "DUPLICATE: CodeBuild build(s) already carry $key: $hit"
fi
echo "no existing prefix, request object or build for $job: submitting once"

mkdir -p "$out"
cp -- "$req" "$out/request.json"
started=$(date -u +%FT%TZ)
set +e
"${cmd_launch[@]}" > "$out/launch.log" 2>&1
launch_rc=$?
set -e
finished=$(date -u +%FT%TZ)
echo "launch-remote exit $launch_rc (no retry)"

# K-5 (v3c): the job is submitted from here on. A failing command or a parse failure writes raw-result.json with submitted true and
# outcome_class other, then exits 5. Exit 2, 3 and 4 are never used after the submission line (DEC-20261107-a83c51 K-5).
post_crash() { # post_crash LINE : the ERR trap (set -E hands it to functions and subshells; only the main shell acts)
  [[ $BASHPID == "$$" ]] || return 0
  trap - ERR
  set +e
  echo "post-submission failure at line $1: raw-result.json is written with outcome_class other and the exit status is 5" >&2
  inventory() { echo '{}'; }
  write_records "$(jq -n --arg started "${started:-}" --arg finished "$(date -u +%FT%TZ)" --arg line "$1" --arg rc "${launch_rc:-}" --arg uri "${results_uri:-}" \
    '{submitted:true, outcome_class:"other", launch_remote_exit:($rc | tonumber? // null), results_uri:$uri, started_at:$started,
      finished_at:$finished, parse_failures:("post-submission failure at line " + $line)}')"
  exit 5
}
set -E   # the ERR trap is inherited by functions (write_records), so a failure inside one reaches post_crash
trap 'post_crash $LINENO' ERR

# 3. Whatever the launcher returned, fetch the job's own results (read-only). v3c (C1-AMENDMENT-2; DEC-20261107-a83c51 K-1 to K-6): the
# results are located by locate_results.sh, by one rule for every outcome. The receipt's status.json pod uid, bound to the Job uid and
# to the launcher id, names the one results prefix. A non-empty result.json .results_uri is accepted only if it equals that prefix, and
# locate_results.sh checks the prefix listing against the launcher's objects.json (Key, Size, ETag). After the download the files must
# equal objects.json and the pod's job-exit.json must equal that pod, this job and the container exit code, or the outcome is never
# job_completed.
res="$client_out/result.json"
results_uri=""; state=""; build_status=""
results_locator=none; job_uid=""; pod_uid=""; located_ok=yes; loc_rc="not_attempted"; objects_check=not_checked; parse_bad=""
if [[ -s $res ]]; then
  state=$(jq -r '.state // empty' "$res" 2>/dev/null) || { state=""; parse_bad+=" result.json"; }
fi
if [[ -s $client_out/build.json ]]; then
  build_status=$(jq -r '.builds[0].buildStatus // empty' "$client_out/build.json" 2>/dev/null) || { build_status=""; parse_bad+=" build.json"; }
fi
if [[ -s $res && $parse_bad != *result.json* ]]; then
  loc_rc=0
  "$here/locate_results.sh" locate --launcher-result "$res" --job "$job" --bucket "$ISOLAB_BUCKET" \
    --workdir "$out/locator" --out "$out/locator/locator.json" || loc_rc=$?
  echo "locate_results exit $loc_rc"
  if [[ $loc_rc == 0 ]]; then
    results_uri=$(jq -r .results_uri "$out/locator/locator.json" 2>/dev/null) || { results_uri=""; parse_bad+=" locator.json"; }
    results_locator=$(jq -r .results_locator "$out/locator/locator.json" 2>/dev/null) || { results_locator=none; parse_bad+=" locator.json"; }
    job_uid=$(jq -r '.job_uid // ""' "$out/locator/locator.json" 2>/dev/null) || { job_uid=""; parse_bad+=" locator.json"; }
    pod_uid=$(jq -r '.pod_uid // ""' "$out/locator/locator.json" 2>/dev/null) || { pod_uid=""; parse_bad+=" locator.json"; }
  fi
fi
dl_rc="not_attempted"
if [[ -n $results_uri ]]; then
  dl_rc=0
  aws s3 cp "$results_uri" "$out/artifacts/" --recursive --only-show-errors || dl_rc=$?
fi
have_exit=no; have_sums=no; job_exit_code=""
if [[ -s $out/artifacts/job-exit.json ]]; then
  have_exit=yes
  # K-4: the exit code is read only when .exit_code has jq type number and is spelled 0, 42 or 43 (no string, boolean or float)
  if jq -e '(.exit_code | type) == "number" and (.exit_code | tojson | test("^(0|42|43)$"))' "$out/artifacts/job-exit.json" >/dev/null 2>&1 \
     && grep -q -E '"exit_code"[[:space:]]*:[[:space:]]*(0|42|43)[[:space:]]*[,}]' "$out/artifacts/job-exit.json" 2>/dev/null; then # [K4-wrapper]
    job_exit_code=$(jq -r '.exit_code | tojson' "$out/artifacts/job-exit.json" 2>/dev/null) || job_exit_code=""
  fi
fi
[[ -s $out/artifacts/SHA256SUMS ]] && have_sums=yes
if [[ -n $results_uri ]]; then
  objects_rc=0
  "$here/locate_results.sh" objects --locator "$out/locator/locator.json" --artifacts "$out/artifacts" || objects_rc=$?
  echo "locate_results objects exit $objects_rc"
  if [[ $objects_rc == 0 ]]; then objects_check=true; else objects_check=false; located_ok=no; fi # [K2-wrapper-objects]
  [[ $dl_rc == 0 ]] || located_ok=no # [K2-wrapper-dl]
  if [[ $have_exit == yes ]]; then
    verify_rc=0
    "$here/locate_results.sh" verify --locator "$out/locator/locator.json" --artifacts "$out/artifacts" || verify_rc=$?
    echo "locate_results verify exit $verify_rc"
    [[ $verify_rc == 0 ]] || located_ok=no
  fi
fi

# Outcome class. Deadline first, whatever was downloaded (PROTOCOL section 9: a session that ends at its deadline is
# infrastructure whether or not it wrote a job-exit.json). launch-remote exits 26 for ANY terminal CodeBuild status other
# than SUCCEEDED, TIMED_OUT included, so the launcher exit alone never decides. job_completed only in the two expected
# pairings (launcher exit, CodeBuild status, job exit); every other combination is "other" (exit 5).
# V6_COUNTED_CODEBUILD_STATUS is the status of the v6 counted launcher build 6f759bb0-5992-49a8-8e95-a52b74a98ceb, whose
# pod exited 42 (CodeBuild batch-get-builds buildStatus FAILED; scratchpad v6/run/gate-line-s3.txt, sha256 cbc3e905...).
V6_COUNTED_CODEBUILD_STATUS=FAILED
class=other
if [[ $build_status == TIMED_OUT || $state == *deadline* || $state == *timed_out* || $state == *timeout* ]]; then
  class=deadline_hit
elif [[ $have_exit != yes || $have_sums != yes ]]; then
  if [[ -z $results_uri || $dl_rc != 0 ]]; then class=infrastructure_candidate; fi
elif [[ $launch_rc == 0 && $build_status == SUCCEEDED && $job_exit_code == 0 ]]; then
  class=job_completed
elif [[ $launch_rc == 26 && $build_status == "$V6_COUNTED_CODEBUILD_STATUS" && ( $job_exit_code == 42 || $job_exit_code == 43 ) ]]; then
  class=job_completed
fi
# v3c: result.json named a results_uri or pod_uid other than the located prefix (K-1): the class is other, never job_completed.
if [[ $loc_rc == 24 && $class != deadline_hit ]]; then class=other; fi # [K1-class]
# v3c: a launcher file that did not parse (K-5), or files that do not equal objects.json or a job-exit.json that does not match the
# receipt (K-2, K-4), are never job_completed.
if [[ -n $parse_bad && $class != deadline_hit ]]; then class=other; fi
[[ $located_ok == yes || $class != job_completed ]] || class=other

write_records "$(jq -n --arg class "$class" --arg started "$started" --arg finished "$finished" \
  --argjson launch_rc "$launch_rc" --arg uri "$results_uri" --arg state "$state" --arg bstatus "$build_status" --arg dl "$dl_rc" \
  --arg have_exit "$have_exit" --arg have_sums "$have_sums" --arg jec "$job_exit_code" \
  --arg locator "$results_locator" --arg juid "$job_uid" --arg puid "$pod_uid" --arg oc "$objects_check" --arg lrc "$loc_rc" --arg pbad "$parse_bad" \
  '{submitted:true, outcome_class:$class, launch_remote_exit:$launch_rc, launcher_state:$state, codebuild_status:$bstatus,
    results_uri:$uri, results_locator:$locator, job_uid:$juid, pod_uid:$puid, download_exit:$dl,
    objects_match:($oc == "true"), objects_check:$oc, locate_exit:$lrc, parse_failures:$pbad,
    job_exit_json_present:$have_exit, sha256sums_present:$have_sums,
    job_exit_code:$jec, started_at:$started, finished_at:$finished}')"
echo "outcome_class=$class job_exit_code=${job_exit_code:-none} record_dir=$rec"
[[ $class == job_completed ]] && exit 0
exit 5
