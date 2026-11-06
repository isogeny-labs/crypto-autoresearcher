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
ids=$(aws codebuild list-builds-for-project --project-name "$ISOLAB_CODEBUILD_PROJECT" --sort-order DESCENDING --max-items 100 --query 'ids[]' --output text); rc=$?
set -e
[[ $rc != 0 ]] && refuse 4 duplicate_check_failed "duplicate check failed (codebuild list)"
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

# 3. Whatever the launcher returned, fetch the job's own results if its receipt names them (read-only).
res="$client_out/result.json"
results_uri=""; state=""; build_status=""
[[ -s $res ]] && results_uri=$(jq -r '.results_uri // empty' "$res") && state=$(jq -r '.state // empty' "$res")
[[ -s $client_out/build.json ]] && build_status=$(jq -r '.builds[0].buildStatus // empty' "$client_out/build.json")
dl_rc="not_attempted"
if [[ -n $results_uri ]]; then
  set +e; aws s3 cp "$results_uri" "$out/artifacts/" --recursive --only-show-errors; dl_rc=$?; set -e
fi
have_exit=no; have_sums=no; job_exit_code=""
[[ -s $out/artifacts/job-exit.json ]] && have_exit=yes && job_exit_code=$(jq -r '.exit_code // empty' "$out/artifacts/job-exit.json")
[[ -s $out/artifacts/SHA256SUMS ]] && have_sums=yes

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

write_records "$(jq -n --arg class "$class" --arg started "$started" --arg finished "$finished" \
  --argjson launch_rc "$launch_rc" --arg uri "$results_uri" --arg state "$state" --arg bstatus "$build_status" --arg dl "$dl_rc" \
  --arg have_exit "$have_exit" --arg have_sums "$have_sums" --arg jec "$job_exit_code" \
  '{submitted:true, outcome_class:$class, launch_remote_exit:$launch_rc, launcher_state:$state, codebuild_status:$bstatus,
    results_uri:$uri, download_exit:$dl, job_exit_json_present:$have_exit, sha256sums_present:$have_sums,
    job_exit_code:$jec, started_at:$started, finished_at:$finished}')"
echo "outcome_class=$class job_exit_code=${job_exit_code:-none} record_dir=$rec"
[[ $class == job_completed ]] && exit 0
exit 5
