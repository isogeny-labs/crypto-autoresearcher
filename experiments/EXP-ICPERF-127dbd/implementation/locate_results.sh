#!/usr/bin/env bash
# Results locator for the C1 launch wrapper (C1-AMENDMENT-2 rule; DEC-20261107-b74e2c rulings 3 and 4).
# Read-only. It makes only two kinds of AWS call: `aws s3 cp <s3 source> <local file>` and `aws s3 ls <s3 prefix>`.
# It never starts a job, never starts a build and never writes to S3. It is used by launch_eks.sh (v3b, section 3)
# and by reconcile_run.sh, so that both apply the same rule to the same receipt.
#
# usage:
#   locate_results.sh locate --launcher-result RESULT.json --job JOB --bucket BUCKET --workdir DIR --out LOCATOR.json
#   locate_results.sh verify --locator LOCATOR.json --artifacts DIR
#
# locate: the rule, in order.
#   (a) result.json .results_uri non-empty: it is used as is, with no other check, as launch_eks.sh v3a did.
#       results_locator=launcher_result. No AWS call.
#   (b) otherwise: result.json .job_name must equal JOB and .job_uid must be non-empty. .receipt_uri must be s3://BUCKET/runs/JOB/launcher/<36 hex and dash>/ . status.json under it is copied
#       to DIR/status.json. status.json .job.uid must equal result.json .job_uid, .job.job_name must equal JOB, and
#       .job.state must be failed. Exactly one pod is allowed. Its .uid must be 36 hex and dash characters; it is the
#       pod_uid. That pod must have exactly one container status, and that status must be terminated with an integer
#       exitCode (recorded as pod_exit_code). Then `aws s3 ls s3://BUCKET/runs/JOB/` must hold exactly two entries,
#       the prefixes launcher/ and <pod_uid>/. results_uri is s3://BUCKET/runs/JOB/<pod_uid>/ and results_locator is
#       receipt_status_pod_uid.
#   LOCATOR.json is written (schema c1.results-locator/v1) only when the rule located the results.
#   exit codes: 0 located; 10 usage; 11 launcher result unreadable, or (rule b) wrong job name or no job_uid; 12 no results_uri
#   and no usable receipt_uri; 13 status.json could not be copied or is not JSON; 14 job identity or state mismatch;
#   15 pod count is not one, or pod/container fields are malformed; 16 the listing failed or holds anything else.
#
# verify (rule (b) only, after the download): DIR/job-exit.json must exist and .pod_uid must equal the located pod_uid,
#   .job_name must equal the located job, and .exit_code must be an integer in {0, 42, 43} equal to pod_exit_code.
#   exit codes: 0 verified; 10 usage; 17 job-exit.json is absent or not JSON; 18 a field differs; 19 locator is not a
#   receipt_status_pod_uid locator.
set -euo pipefail
set +x

s3_get() { # s3_get SOURCE LOCAL [--recursive] : the only download call; refuses a non-S3 source or an S3 destination
  [[ $1 == s3://* && $2 != s3://* ]] || { echo "locate_results: s3_get refused: $1 -> $2" >&2; return 99; }
  aws s3 cp "$1" "$2" "${@:3}" --only-show-errors
}
s3_ls() { # s3_ls PREFIX : the only listing call
  [[ $1 == s3://* ]] || { echo "locate_results: s3_ls refused: $1" >&2; return 99; }
  aws s3 ls "$1"
}
usage() {
  echo "usage: locate_results.sh locate --launcher-result RESULT.json --job JOB --bucket BUCKET --workdir DIR --out LOCATOR.json" >&2
  echo "       locate_results.sh verify --locator LOCATOR.json --artifacts DIR" >&2
  exit 10
}

mode=${1:-}; [[ -n $mode ]] || usage; shift
case $mode in
locate)
  res=""; job=""; bucket=""; workdir=""; outjson=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --launcher-result) res=${2:?}; shift 2 ;;
      --job) job=${2:?}; shift 2 ;;
      --bucket) bucket=${2:?}; shift 2 ;;
      --workdir) workdir=${2:?}; shift 2 ;;
      --out) outjson=${2:?}; shift 2 ;;
      *) echo "locate_results: unknown argument $1" >&2; exit 10 ;;
    esac
  done
  for v in res job bucket workdir outjson; do [[ -n ${!v} ]] || usage; done
  [[ $job =~ ^[A-Za-z0-9-]+$ && $bucket =~ ^[a-z0-9.-]+$ ]] || { echo "locate_results: malformed job or bucket" >&2; exit 10; }
  jq -e 'type == "object"' "$res" >/dev/null 2>&1 || { echo "locate_results: $res is not a JSON object" >&2; exit 11; }
  mkdir -p "$workdir"
  results_uri=$(jq -r '.results_uri // ""' "$res")
  if [[ -n $results_uri ]]; then # rule (a): used as is, exactly as launch_eks.sh v3a did
    jq -n --arg uri "$results_uri" --arg job "$job" --arg juid "$(jq -r '.job_uid // ""' "$res")" --arg puid "$(jq -r '.pod_uid // ""' "$res")" \
      '{schema:"c1.results-locator/v1", results_locator:"launcher_result", results_uri:$uri, job_name:$job, job_uid:$juid,
        pod_uid:$puid, pod_exit_code:null, receipt_uri:null}' > "$outjson"
    echo "LOCATED results_locator=launcher_result results_uri=$results_uri"
    exit 0
  fi
  # rule (b): the launcher result must be this job's, and must carry the Job uid
  [[ $(jq -r '.job_name // ""' "$res") == "$job" ]] || { echo "locate_results: launcher result job_name differs from $job" >&2; exit 11; }
  job_uid=$(jq -r '.job_uid // ""' "$res")
  [[ -n $job_uid ]] || { echo "locate_results: launcher result has no job_uid" >&2; exit 11; }
  receipt_uri=$(jq -r '.receipt_uri // ""' "$res")
  receipt_prefix="s3://$bucket/runs/$job/launcher/"
  [[ $receipt_uri == "$receipt_prefix"* && ${receipt_uri#"$receipt_prefix"} =~ ^[a-f0-9-]{36}/$ ]] \
    || { echo "locate_results: results_uri is empty and receipt_uri '$receipt_uri' is not s3://$bucket/runs/$job/launcher/<id>/" >&2; exit 12; }
  status="$workdir/status.json"
  rm -f -- "$status"
  s3_get "${receipt_uri}status.json" "$status" || { echo "locate_results: could not copy ${receipt_uri}status.json" >&2; exit 13; }
  jq -e 'type == "object"' "$status" >/dev/null 2>&1 || { echo "locate_results: status.json is not a JSON object" >&2; exit 13; }
  [[ $(jq -r '.job.uid // ""' "$status") == "$job_uid" ]] \
    || { echo "locate_results: status.json job.uid differs from the launcher result job_uid $job_uid" >&2; exit 14; }
  [[ $(jq -r '.job.job_name // ""' "$status") == "$job" ]] \
    || { echo "locate_results: status.json job.job_name differs from $job" >&2; exit 14; }
  [[ $(jq -r '.job.state // ""' "$status") == failed ]] \
    || { echo "locate_results: status.json job.state is not failed" >&2; exit 14; }
  npods=$(jq -r '(.pods // []) | length' "$status")
  [[ $npods == 1 ]] || { echo "locate_results: status.json holds $npods pods; exactly one is required" >&2; exit 15; }
  pod_uid=$(jq -r '.pods[0].uid // ""' "$status")
  [[ $pod_uid =~ ^[a-f0-9-]{36}$ ]] || { echo "locate_results: the pod uid is not 36 hex and dash characters" >&2; exit 15; }
  ncs=$(jq -r '(.pods[0].status.containerStatuses // []) | length' "$status")
  [[ $ncs == 1 ]] || { echo "locate_results: the pod has $ncs container statuses; exactly one is required" >&2; exit 15; }
  pod_exit=$(jq -r 'if (.pods[0].status.containerStatuses[0].state.terminated.exitCode | type) == "number"
                    then (.pods[0].status.containerStatuses[0].state.terminated.exitCode | tostring) else "" end' "$status")
  [[ $pod_exit =~ ^[0-9]+$ ]] || { echo "locate_results: the container is not terminated with an integer exitCode" >&2; exit 15; }
  set +e
  listing=$(s3_ls "s3://$bucket/runs/$job/" 2>/dev/null); lrc=$?
  set -e
  [[ $lrc == 0 && -n $listing ]] || { echo "locate_results: listing of s3://$bucket/runs/$job/ failed (exit $lrc) or is empty" >&2; exit 16; }
  names=$(printf '%s\n' "$listing" | awk '{ if ($1 == "PRE") print $2; else print "FILE:" $NF }' | LC_ALL=C sort)
  want=$(printf '%s\n' "launcher/" "$pod_uid/" | LC_ALL=C sort)
  [[ $names == "$want" ]] \
    || { echo "locate_results: s3://$bucket/runs/$job/ holds something other than launcher/ and $pod_uid/: $(printf '%s' "$names" | tr '\n' ' ')" >&2; exit 16; }
  jq -n --arg uri "s3://$bucket/runs/$job/$pod_uid/" --arg juid "$job_uid" --arg job "$job" --arg puid "$pod_uid" \
    --argjson pexit "$pod_exit" --arg ruri "$receipt_uri" \
    '{schema:"c1.results-locator/v1", results_locator:"receipt_status_pod_uid", results_uri:$uri, job_name:$job, job_uid:$juid,
      pod_uid:$puid, pod_exit_code:$pexit, receipt_uri:$ruri}' > "$outjson"
  echo "LOCATED results_locator=receipt_status_pod_uid results_uri=s3://$bucket/runs/$job/$pod_uid/ pod_exit_code=$pod_exit"
  exit 0
  ;;
verify)
  loc=""; art=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --locator) loc=${2:?}; shift 2 ;;
      --artifacts) art=${2:?}; shift 2 ;;
      *) echo "locate_results: unknown argument $1" >&2; exit 10 ;;
    esac
  done
  [[ -n $loc && -n $art ]] || usage
  [[ $(jq -r '.results_locator // ""' "$loc" 2>/dev/null) == receipt_status_pod_uid ]] \
    || { echo "locate_results: verify applies only to a receipt_status_pod_uid locator" >&2; exit 19; }
  jq -e 'type == "object"' "$art/job-exit.json" >/dev/null 2>&1 || { echo "locate_results: $art/job-exit.json is absent or not a JSON object" >&2; exit 17; }
  bad=$(jq -rn --slurpfile l "$loc" --slurpfile j "$art/job-exit.json" '
    $l[0] as $l | $j[0] as $j
    | [ (if $j.pod_uid == $l.pod_uid then empty else "pod_uid" end),
        (if $j.job_name == $l.job_name then empty else "job_name" end),
        (if ($j.exit_code | type) == "number" and ([0, 42, 43] | index($j.exit_code)) != null and $j.exit_code == $l.pod_exit_code
         then empty else "exit_code" end) ] | join(",")')
  [[ -z $bad ]] || { echo "locate_results: job-exit.json differs from the located pod in: $bad" >&2; exit 18; }
  echo "VERIFIED job-exit.json equals pod_uid, job_name and container exitCode of the located pod"
  exit 0
  ;;
*) usage ;;
esac
