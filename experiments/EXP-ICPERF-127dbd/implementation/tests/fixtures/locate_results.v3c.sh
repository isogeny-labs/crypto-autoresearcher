#!/usr/bin/env bash
# Results locator for the C1 launch wrapper (v3c; C1-AMENDMENT-2 rule; DEC-20261107-b74e2c rulings 3 and 4;
# DEC-20261107-a83c51 controls K-1, K-2, K-4 and K-6).
# Read-only. It makes only three kinds of AWS call: `aws s3 cp <s3 source> <local file>`, `aws s3 ls <s3 prefix>` and
# `aws s3api list-objects-v2 --bucket B --prefix P --output json` (a listing that carries ETag and LastModified).
# It never starts a job, never starts a build and never writes to S3. It is used by launch_eks.sh (v3c, section 3)
# and by reconcile_run.sh, so that both apply the same rule to the same receipt. It is executed, never sourced, and it runs
# inside the clean environment that those two scripts establish (K-7).
#
# usage:
#   locate_results.sh locate --launcher-result RESULT.json --job JOB --bucket BUCKET --workdir DIR --out LOCATOR.json
#                            [--pin-status-sha256 HEX --pin-objects-sha256 HEX --pin-not-after YYYY-MM-DDTHH:MM:SSZ]
#   locate_results.sh objects --locator LOCATOR.json --artifacts DIR
#   locate_results.sh verify --locator LOCATOR.json --artifacts DIR
#
# locate: ONE rule for every outcome (K-1). The three pin options are all given or none is (reconcile gives them for T1).
#   1. result.json .job_name must equal JOB and .job_uid must be non-empty. .receipt_uri must be s3://BUCKET/runs/JOB/launcher/<ID>/
#      with <ID> a canonical lower-case UUID, and the part after the last colon of result.json .launcher must equal <ID> (K-6).
#   2. status.json and objects.json under the receipt are copied to DIR. With the pins: their sha256 values must equal the pins and
#      the S3 LastModified of both receipt objects, and of every listed pod object, must be at or before --pin-not-after (K-2).
#   3. status.json .job.uid must equal result.json .job_uid, .job.job_name must equal JOB, and .job.state must be failed (or, when
#      result.json .results_uri is non-empty, failed or succeeded). Exactly one pod is allowed. Its .uid must be a canonical
#      lower-case UUID with nothing after it (K-6). That pod must have exactly one container status, terminated with an integer
#      exitCode (recorded as pod_exit_code), restartCount 0 and an empty lastState (K-6).
#   4. A non-empty result.json .results_uri (and a non-empty .pod_uid) is accepted only if it equals the located
#      s3://BUCKET/runs/JOB/<pod_uid>/ exactly. Otherwise exit 24 (K-1); the wrapper classes the case as other.
#   5. objects.json .objects must be a non-empty array, .next_token must be null, every key must lie under runs/JOB/launcher/ or the
#      pod prefix, and the entries of the pod prefix need an integer Size and a string ETag with no duplicate key (K-2).
#   6. `aws s3 ls s3://BUCKET/runs/JOB/` must hold exactly two entries, the prefixes launcher/ and <pod_uid>/.
#   7. A listing of the pod prefix must equal the objects.json entries of the pod prefix as a set of (Key, Size, ETag) (K-2).
#   results_uri is s3://BUCKET/runs/JOB/<pod_uid>/ and results_locator is receipt_status_pod_uid, in every accepted case.
#   LOCATOR.json is written (schema c1.results-locator/v1) only when the rule located the results.
#   exit codes: 0 located; 10 usage; 11 launcher result unreadable, wrong job name or no job_uid; 12 receipt_uri or launcher id
#   unusable; 13 status.json could not be copied or is not JSON; 14 job identity or state mismatch; 15 pod count is not one, or
#   pod/container fields are malformed or the container restarted; 16 the job listing failed or holds anything else; 20 objects.json
#   could not be copied or is not JSON; 21 objects.json is malformed, truncated or lists a key outside launcher/ and the pod prefix;
#   22 the pod prefix listing failed or differs from objects.json; 23 a pin differs; 24 result.json names a results_uri or pod_uid
#   other than the located one.
#
# objects (after the download): every file under DIR must be listed in objects.json for the pod prefix, and every listed object
#   must exist under DIR, with the same size, and with the same MD5 where the ETag is a single-part MD5 (32 hex characters).
#   A multipart ETag (it holds a dash) is compared by size only; SHA256SUMS, which check_job.py verifies, covers those bytes.
#   exit codes: 0 match; 10 usage; 19 locator unusable; 25 the downloaded files differ from objects.json.
#
# verify (after the download): DIR/job-exit.json must exist and .pod_uid must equal the located pod_uid, .job_name must equal the
#   located job, and .exit_code must have jq type number, be spelled 0, 42 or 43, and equal pod_exit_code (K-4).
#   exit codes: 0 verified; 10 usage; 17 job-exit.json is absent or not JSON; 18 a field differs; 19 locator unusable.
set -euo pipefail
set +x

UUID_RE='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
s3_get() { # s3_get SOURCE LOCAL [--recursive] : the only download call; refuses a non-S3 source or an S3 destination
  [[ $1 == s3://* && $2 != s3://* ]] || { echo "locate_results: s3_get refused: $1 -> $2" >&2; return 99; }
  aws s3 cp "$1" "$2" "${@:3}" --only-show-errors
}
s3_ls() { # s3_ls PREFIX : the only prefix listing call
  [[ $1 == s3://* ]] || { echo "locate_results: s3_ls refused: $1" >&2; return 99; }
  aws s3 ls "$1"
}
s3_list_objects() { # s3_list_objects BUCKET PREFIX : the only object listing call (Key, Size, ETag, LastModified); read-only
  [[ $1 =~ ^[a-z0-9.-]+$ && $2 == runs/* ]] || { echo "locate_results: s3_list_objects refused: $1 $2" >&2; return 99; }
  aws s3api list-objects-v2 --bucket "$1" --prefix "$2" --output json
}
usage() {
  echo "usage: locate_results.sh locate --launcher-result RESULT.json --job JOB --bucket BUCKET --workdir DIR --out LOCATOR.json [--pin-status-sha256 HEX --pin-objects-sha256 HEX --pin-not-after TIME]" >&2
  echo "       locate_results.sh objects --locator LOCATOR.json --artifacts DIR" >&2
  echo "       locate_results.sh verify --locator LOCATOR.json --artifacts DIR" >&2
  exit 10
}
lm_epoch='def lm: (.LastModified | sub("\\+00:00$"; "Z") | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601);'

mode=${1:-}; [[ -n $mode ]] || usage; shift
case $mode in
locate)
  res=""; job=""; bucket=""; workdir=""; outjson=""; pin_status=""; pin_objects=""; pin_na=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --launcher-result) res=${2:?}; shift 2 ;;
      --job) job=${2:?}; shift 2 ;;
      --bucket) bucket=${2:?}; shift 2 ;;
      --workdir) workdir=${2:?}; shift 2 ;;
      --out) outjson=${2:?}; shift 2 ;;
      --pin-status-sha256) pin_status=${2:?}; shift 2 ;;
      --pin-objects-sha256) pin_objects=${2:?}; shift 2 ;;
      --pin-not-after) pin_na=${2:?}; shift 2 ;;
      *) echo "locate_results: unknown argument $1" >&2; exit 10 ;;
    esac
  done
  for v in res job bucket workdir outjson; do [[ -n ${!v} ]] || usage; done
  [[ $job =~ ^[A-Za-z0-9-]+$ && $bucket =~ ^[a-z0-9.-]+$ ]] || { echo "locate_results: malformed job or bucket" >&2; exit 10; }
  pins=no
  if [[ -n $pin_status$pin_objects$pin_na ]]; then
    [[ $pin_status =~ ^[0-9a-f]{64}$ && $pin_objects =~ ^[0-9a-f]{64}$ && $pin_na =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] \
      || { echo "locate_results: the three pin options are given together and well formed, or not at all" >&2; exit 10; }
    pins=yes; na_epoch=$(date -u -d "$pin_na" +%s)
  fi
  jq -e 'type == "object"' "$res" >/dev/null 2>&1 || { echo "locate_results: $res is not a JSON object" >&2; exit 11; }
  mkdir -p "$workdir"
  [[ $(jq -r '.job_name // ""' "$res") == "$job" ]] || { echo "locate_results: launcher result job_name differs from $job" >&2; exit 11; }
  job_uid=$(jq -r '.job_uid // ""' "$res")
  [[ -n $job_uid ]] || { echo "locate_results: launcher result has no job_uid" >&2; exit 11; }
  r_uri=$(jq -r 'if (.results_uri | type) == "string" then .results_uri elif .results_uri == null then "" else "!non-string" end' "$res")
  r_pod=$(jq -r 'if (.pod_uid | type) == "string" then .pod_uid elif .pod_uid == null then "" else "!non-string" end' "$res")
  receipt_uri=$(jq -r '.receipt_uri // ""' "$res")
  receipt_prefix="s3://$bucket/runs/$job/launcher/"
  [[ $receipt_uri == "$receipt_prefix"* && ${receipt_uri#"$receipt_prefix"} =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/$ ]] \
    || { echo "locate_results: receipt_uri '$receipt_uri' is not s3://$bucket/runs/$job/launcher/<uuid>/" >&2; exit 12; } # [K6-receipt-uuid]
  rid=${receipt_uri#"$receipt_prefix"}; rid=${rid%/}
  lid=$(jq -r 'if (.launcher | type) == "string" then (.launcher | split(":") | last) else "" end' "$res")
  [[ $lid == "$rid" ]] || { echo "locate_results: result.json .launcher build id '$lid' differs from the receipt_uri launcher id" >&2; exit 12; } # [K6-launcher-id]
  rkey="runs/$job/launcher/$rid/"
  status="$workdir/status.json"; objects="$workdir/objects.json"
  rm -f -- "$status" "$objects"
  s3_get "${receipt_uri}status.json" "$status" || { echo "locate_results: could not copy ${receipt_uri}status.json" >&2; exit 13; }
  jq -e 'type == "object"' "$status" >/dev/null 2>&1 || { echo "locate_results: status.json is not a JSON object" >&2; exit 13; }
  s3_get "${receipt_uri}objects.json" "$objects" || { echo "locate_results: could not copy ${receipt_uri}objects.json" >&2; exit 20; }
  jq -e 'type == "object"' "$objects" >/dev/null 2>&1 || { echo "locate_results: objects.json is not a JSON object" >&2; exit 20; }
  status_sha=$(sha256sum "$status" | cut -d ' ' -f1); objects_sha=$(sha256sum "$objects" | cut -d ' ' -f1)
  if [[ $pins == yes ]]; then
    [[ $status_sha == "$pin_status" ]] || { echo "locate_results: status.json sha256 $status_sha differs from the pinned $pin_status" >&2; exit 23; } # [K2-pin-status]
    [[ $objects_sha == "$pin_objects" ]] || { echo "locate_results: objects.json sha256 $objects_sha differs from the pinned $pin_objects" >&2; exit 23; } # [K2-pin-objects]
    set +e; rl=$(s3_list_objects "$bucket" "$rkey" 2>/dev/null); rlrc=$?; set -e
    [[ $rlrc == 0 && -n $rl ]] || { echo "locate_results: listing of the receipt prefix failed (exit $rlrc) or is empty" >&2; exit 23; }
    jq -e --argjson na "$na_epoch" --arg a "${rkey}status.json" --arg b "${rkey}objects.json" "$lm_epoch"'
        [.Contents[]? | select(.Key == $a or .Key == $b)] as $c | ($c | length) == 2 and all($c[]; lm <= $na)' <<<"$rl" >/dev/null 2>&1 \
      || { echo "locate_results: a receipt object is missing from the listing or was modified after $pin_na" >&2; exit 23; } # [K2-pin-lastmodified]
  fi
  [[ $(jq -r '.job.uid // ""' "$status") == "$job_uid" ]] \
    || { echo "locate_results: status.json job.uid differs from the launcher result job_uid $job_uid" >&2; exit 14; }
  [[ $(jq -r '.job.job_name // ""' "$status") == "$job" ]] \
    || { echo "locate_results: status.json job.job_name differs from $job" >&2; exit 14; }
  jstate=$(jq -r '.job.state // ""' "$status")
  if [[ -z $r_uri ]]; then
    [[ $jstate == failed ]] || { echo "locate_results: status.json job.state is not failed" >&2; exit 14; }
  else
    [[ $jstate == failed || $jstate == succeeded ]] || { echo "locate_results: status.json job.state is neither failed nor succeeded" >&2; exit 14; }
  fi
  npods=$(jq -r '(.pods // []) | length' "$status")
  [[ $npods == 1 ]] || { echo "locate_results: status.json holds $npods pods; exactly one is required" >&2; exit 15; }
  jq -e '.pods[0].uid | type == "string" and test("\\A[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\z")' "$status" >/dev/null 2>&1 \
    || { echo "locate_results: the pod uid is not a canonical lower-case UUID" >&2; exit 15; } # [K6-poduid]
  pod_uid=$(jq -r '.pods[0].uid' "$status")
  ncs=$(jq -r '(.pods[0].status.containerStatuses // []) | length' "$status")
  [[ $ncs == 1 ]] || { echo "locate_results: the pod has $ncs container statuses; exactly one is required" >&2; exit 15; }
  pod_exit=$(jq -r 'if (.pods[0].status.containerStatuses[0].state.terminated.exitCode | type) == "number"
                    then (.pods[0].status.containerStatuses[0].state.terminated.exitCode | tojson) else "" end' "$status")
  [[ $pod_exit =~ ^[0-9]+$ ]] || { echo "locate_results: the container is not terminated with an integer exitCode" >&2; exit 15; }
  jq -e '.pods[0].status.containerStatuses[0] | .restartCount == 0 and (.lastState // {}) == {}' "$status" >/dev/null 2>&1 \
    || { echo "locate_results: the container restarted (restartCount is not 0 or lastState is not empty)" >&2; exit 15; } # [K6-restart]
  located="s3://$bucket/runs/$job/$pod_uid/"
  if [[ -n $r_uri ]]; then
    [[ $r_uri == "$located" ]] || { echo "locate_results: result.json results_uri '$r_uri' differs from the located $located" >&2; exit 24; } # [K1-uri]
    [[ -z $r_pod || $r_pod == "$pod_uid" ]] || { echo "locate_results: result.json pod_uid '$r_pod' differs from the located pod $pod_uid" >&2; exit 24; } # [K1-poduid]
  fi
  pfx="runs/$job/$pod_uid/"
  jq -e '(.objects | type) == "array" and (.objects | length) > 0' "$objects" >/dev/null 2>&1 \
    || { echo "locate_results: objects.json holds no non-empty .objects array" >&2; exit 21; } # [K2-nonempty]
  jq -e 'has("next_token") and .next_token == null' "$objects" >/dev/null 2>&1 \
    || { echo "locate_results: objects.json is truncated (next_token is not null)" >&2; exit 21; } # [K2-nexttoken]
  jq -e --arg a "runs/$job/launcher/" --arg b "$pfx" 'all(.objects[]; (.Key | type) == "string" and ((.Key | startswith($a)) or (.Key | startswith($b))))' "$objects" >/dev/null 2>&1 \
    || { echo "locate_results: objects.json lists a key outside launcher/ and the pod prefix" >&2; exit 21; } # [K2-keys]
  jq -e --arg b "$pfx" '[.objects[] | select(.Key | startswith($b))] as $p
      | ($p | length) > 0 and all($p[]; (.Size | type) == "number" and .Size >= 0 and .Size == (.Size | floor) and (.ETag | type) == "string" and (.ETag | length) > 0)
        and ($p | map(.Key) | length) == ($p | map(.Key) | unique | length)' "$objects" >/dev/null 2>&1 \
    || { echo "locate_results: objects.json pod entries are missing, duplicated or lack an integer Size or a string ETag" >&2; exit 21; } # [K2-entries]
  set +e
  listing=$(s3_ls "s3://$bucket/runs/$job/" 2>/dev/null); lrc=$?
  set -e
  [[ $lrc == 0 && -n $listing ]] || { echo "locate_results: listing of s3://$bucket/runs/$job/ failed (exit $lrc) or is empty" >&2; exit 16; }
  names=$(printf '%s\n' "$listing" | awk '{ if ($1 == "PRE") print $2; else print "FILE:" $NF }' | LC_ALL=C sort)
  want=$(printf '%s\n' "launcher/" "$pod_uid/" | LC_ALL=C sort)
  [[ $names == "$want" ]] \
    || { echo "locate_results: s3://$bucket/runs/$job/ holds something other than launcher/ and $pod_uid/: $(printf '%s' "$names" | tr '\n' ' ')" >&2; exit 16; }
  set +e; plist=$(s3_list_objects "$bucket" "$pfx" 2>/dev/null); prc=$?; set -e
  [[ $prc == 0 ]] || { echo "locate_results: listing of the pod prefix failed (exit $prc)" >&2; exit 22; }
  [[ -n $plist ]] || plist='{}'
  want_set=$(jq -S -c --arg p "$pfx" '[.objects[] | select(.Key | startswith($p)) | {Key, Size, ETag}] | sort_by(.Key)' "$objects")
  have_set=$(jq -S -c --arg p "$pfx" '[(.Contents // [])[] | select(.Key | startswith($p)) | {Key, Size, ETag}] | sort_by(.Key)' <<<"$plist" 2>/dev/null || echo bad)
  [[ $have_set == "$want_set" ]] \
    || { echo "locate_results: the listing of the pod prefix differs from the launcher's objects.json (Key, Size, ETag)" >&2; exit 22; } # [K2-listing]
  if [[ $pins == yes ]]; then
    jq -e --argjson na "$na_epoch" "$lm_epoch"' all(.Contents[]?; lm <= $na)' <<<"$plist" >/dev/null 2>&1 \
      || { echo "locate_results: a pod object was modified after $pin_na" >&2; exit 23; } # [K2-pin-podlm]
  fi
  jq -n --arg uri "$located" --arg juid "$job_uid" --arg job "$job" --arg puid "$pod_uid" --argjson pexit "$pod_exit" --arg ruri "$receipt_uri" \
    --arg lru "$r_uri" --arg obj "$objects" --arg pfx "$pfx" --arg ssha "$status_sha" --arg osha "$objects_sha" --arg pins "$pins" \
    '{schema:"c1.results-locator/v1", results_locator:"receipt_status_pod_uid", results_uri:$uri, job_name:$job, job_uid:$juid,
      pod_uid:$puid, pod_exit_code:$pexit, receipt_uri:$ruri, launcher_results_uri:$lru, objects_json:$obj, pod_prefix:$pfx,
      status_json_sha256:$ssha, objects_json_sha256:$osha, pins_checked:($pins == "yes")}' > "$outjson"
  echo "LOCATED results_locator=receipt_status_pod_uid results_uri=$located pod_exit_code=$pod_exit pins_checked=$pins"
  exit 0
  ;;
objects)
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
    || { echo "locate_results: objects applies only to a receipt_status_pod_uid locator" >&2; exit 19; }
  objects=$(jq -r '.objects_json // ""' "$loc"); pfx=$(jq -r '.pod_prefix // ""' "$loc")
  [[ -f $objects && -n $pfx && -d $art ]] || { echo "locate_results: the locator does not name an objects.json and a pod prefix, or $art is absent" >&2; exit 19; }
  nbad=$(cd "$art" && find . -mindepth 1 ! -type d ! -type f | wc -l)
  [[ $nbad == 0 ]] || { echo "locate_results: $art holds $nbad entries that are neither files nor directories" >&2; exit 25; }
  nl=$(cd "$art" && find . -mindepth 1 ! -type d \( -name $'*\n*' -o -name $'*\t*' \) | wc -l)
  [[ $nl == 0 ]] || { echo "locate_results: $art holds a file name with a newline or a tab" >&2; exit 25; }
  have=$(cd "$art" && find . -mindepth 1 ! -type d -printf '%s\t%P\n' | LC_ALL=C sort -t $'\t' -k2 \
    | while IFS=$'\t' read -r sz p; do printf '%s\t%s\t%s\n' "$sz" "$(md5sum -- "$p" | cut -d ' ' -f1)" "$p"; done \
    | jq -Rn '[inputs | split("\t") | {Key: .[2], Size: (.[0] | tonumber), md5: .[1]}] | sort_by(.Key)')
  diffs=$(jq -rn --arg p "$pfx" --slurpfile o "$objects" --argjson h "$have" '
      ($o[0].objects | map(select(.Key | startswith($p)) | {key: (.Key | ltrimstr($p)), size: .Size, etag: (.ETag | gsub("\""; ""))})) as $w
      | ($h | map({key: .Key, size: .Size, md5: .md5})) as $l
      | [ ($w[] | . as $x | ($l | map(select(.key == $x.key)) | first) as $m
          | if $m == null then "missing:" + $x.key
            elif $m.size != $x.size then "size:" + $x.key
            elif ($x.etag | test("^[0-9a-f]{32}$")) and $m.md5 != $x.etag then "md5:" + $x.key
            else empty end),
          ($l[] | . as $y | if ($w | map(.key) | index($y.key)) == null then "extra:" + $y.key else empty end) ]
      | .[:8] | join(" ")') \
    || { echo "locate_results: the downloaded files could not be compared with objects.json" >&2; exit 25; }
  [[ -z $diffs ]] || { echo "locate_results: the downloaded files differ from objects.json: $diffs" >&2; exit 25; } # [K2-objects]
  echo "OBJECTS_MATCH downloaded files equal objects.json: $(jq -r 'length' <<<"$have") files, $(jq -r --arg p "$pfx" '[.objects[] | select(.Key | startswith($p)) | select(.ETag | test("-"))] | length' "$objects") multipart by size only"
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
        (if ($j.exit_code | type) == "number" and ($j.exit_code | tojson | test("^(0|42|43)$")) and $j.exit_code == $l.pod_exit_code
         then empty else "exit_code" end) ] | join(",")') # [K4-type]
  [[ -z $bad ]] || { echo "locate_results: job-exit.json differs from the located pod in: $bad" >&2; exit 18; }
  grep -q -E '"exit_code"[[:space:]]*:[[:space:]]*(0|42|43)[[:space:]]*[,}]' "$art/job-exit.json" \
    || { echo "locate_results: job-exit.json exit_code is not spelled as the integer 0, 42 or 43" >&2; exit 18; } # [K4-raw]
  echo "VERIFIED job-exit.json equals pod_uid, job_name and container exitCode of the located pod"
  exit 0
  ;;
*) usage ;;
esac
