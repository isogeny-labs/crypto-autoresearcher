#!/usr/bin/env bash
# Read-only reconciliation of one already-finished C1 job under its existing run id (DEC-20261107-b74e2c ruling 3, R-1 to R-7).
# It launches nothing: it contains no job-submission, build-start or S3-write path. Its only AWS calls are
# `aws s3 cp <s3 source> <local path>` and `aws s3 ls <s3 prefix>` (through locate_results.sh and the two helpers below).
# It reads no records.jsonl content: that file is hashed and its newlines are counted, nothing more, and no other
# downloaded file is opened except SHA256SUMS and job-exit.json (and everything check_job.py opens).
# It writes only under --out, and refuses an --out that lies inside a runs/ directory.
#
# usage: reconcile_run.sh --launcher-result RUN/job/launcher/result.json --launcher-result-sha256 HEX64 --request REQUEST.json
#                         --check-job check_job.py --run-id RUN --trial-id T --out OUTDIR
#   --out         an empty or absent directory. It receives locator/, artifacts/, object-list.txt, check_job.stdout and
#                 reconcile-result.json (schema c1.reconcile.result/v1, written on success AND on every failure after R-1).
# Environment: ISOLAB_BUCKET (required), AWS settings (ambient).
#
# R-1 launcher result sha256 equals --launcher-result-sha256; job name equals the request's job.job_name.
# R-2 locator (locate_results.sh locate): status.json job.uid = job_uid, job.job_name = job, exactly one pod.
# R-3 listing holds only launcher/ and that pod prefix (locator), and the launcher's objects.json lists keys only under
#     runs/JOB/launcher/ and runs/JOB/<pod_uid>/.
# R-4 aws s3 cp --recursive of the pod prefix into OUTDIR/artifacts; the exit code and the downloaded files with sizes are recorded
#     (OUTDIR/object-list.txt). Integrity of the bytes is judged by SHA256SUMS in check_job.py (R-6), never by this script.
# R-5 locate_results.sh verify: job-exit.json pod_uid, job_name, exit_code equal the located pod, the job and the status exitCode.
# R-6 python3 -I check_job.py OUTDIR/artifacts --request REQUEST --launcher-result RESULT prints CHECK_JOB_OK (exit 0).
# R-7 reconcile-result.json. Also: SHA256SUMS is non-empty and lists run-summary.json at the sha256 of the empty string, and
#     run-summary.json has 0 bytes (DEC-20261107-b74e2c ruling 5).
# Exit: 0 pass; 2 usage or refused --out; 3 R-1; 4 R-2; 5 R-3; 6 R-4; 7 R-5; 8 R-6; 9 run-summary or SHA256SUMS rule.
set -euo pipefail
set +x

EMPTY_SHA256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
s3_get() { # s3_get SOURCE LOCAL [--recursive] : the only download call; refuses a non-S3 source or an S3 destination
  [[ $1 == s3://* && $2 != s3://* ]] || { echo "reconcile_run: s3_get refused: $1 -> $2" >&2; return 99; }
  aws s3 cp "$1" "$2" "${@:3}" --only-show-errors
}
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
res=""; want_sha=""; req=""; checkjob=""; runid=""; trial=""; out=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --launcher-result) res=${2:?}; shift 2 ;;
    --launcher-result-sha256) want_sha=${2:?}; shift 2 ;;
    --request) req=${2:?}; shift 2 ;;
    --check-job) checkjob=${2:?}; shift 2 ;;
    --run-id) runid=${2:?}; shift 2 ;;
    --trial-id) trial=${2:?}; shift 2 ;;
    --out) out=${2:?}; shift 2 ;;
    *) echo "reconcile_run: unknown argument $1" >&2; exit 2 ;;
  esac
done
for v in res want_sha req checkjob runid trial out; do
  [[ -n ${!v} ]] || { echo "usage: reconcile_run.sh --launcher-result R --launcher-result-sha256 HEX --request Q --check-job C --run-id RUN --trial-id T --out DIR" >&2; exit 2; }
done
[[ -n ${ISOLAB_BUCKET:-} ]] || { echo "ISOLAB_BUCKET is required" >&2; exit 2; }
[[ -f $res && -f $req && -f $checkjob ]] || { echo "launcher result, request or check_job.py not found" >&2; exit 2; }
case "/$out/" in */runs/*) echo "refused: --out lies inside a runs/ directory ($out)" >&2; exit 2 ;; esac
if [[ -e $out ]]; then
  [[ -d $out && -z $(ls -A -- "$out") ]] || { echo "refused: --out $out exists and is not an empty directory" >&2; exit 2; }
fi
mkdir -p "$out"

o_r1=not_run; o_r2=not_run; o_r3=not_run; o_r4=not_run; o_r5=not_run; o_r6=not_run; o_sums=not_run
job=""; job_uid=""; pod_uid=""; results_uri=""; results_locator=""; receipt_uri=""; pod_exit=""; dl_rc="not_attempted"
sums_sha=""; job_exit=""; check_rc="not_run"; rs_digest=""; rs_bytes=""; rec_sha=""; rec_lines=""; got_sha=""
finish() { # finish EXIT_CODE REASON : write reconcile-result.json, then exit
  local pass=false
  [[ $1 == 0 ]] && pass=true
  jq -n --arg run_id "$runid" --arg trial_id "$trial" --arg job "$job" --arg job_uid "$job_uid" --arg pod_uid "$pod_uid" \
    --arg results_uri "$results_uri" --arg locator "$results_locator" --arg receipt_uri "$receipt_uri" --arg lsha "$got_sha" \
    --arg dl "$dl_rc" --arg sums "$sums_sha" --arg jec "$job_exit" --arg pexit "$pod_exit" --arg crc "$check_rc" \
    --arg rsd "$rs_digest" --arg rsb "$rs_bytes" --arg rsha "$rec_sha" --arg rlines "$rec_lines" \
    --arg r1 "$o_r1" --arg r2 "$o_r2" --arg r3 "$o_r3" --arg r4 "$o_r4" --arg r5 "$o_r5" --arg r6 "$o_r6" --arg rsum "$o_sums" \
    --argjson pass "$pass" --arg reason "$2" --argjson code "$1" \
    '{schema:"c1.reconcile.result/v1", run_id:$run_id, trial_id:$trial_id, job_name:$job, job_uid:$job_uid, pod_uid:$pod_uid,
      results_uri:$results_uri, results_locator:$locator, receipt_uri:$receipt_uri, launcher_result_sha256:$lsha,
      download_exit:$dl, sha256sums_sha256:$sums, job_exit_code:$jec, status_container_exit_code:$pexit, check_job_exit:$crc,
      run_summary_listed_sha256:$rsd, run_summary_bytes:$rsb, records_jsonl_sha256:$rsha, records_jsonl_newlines:$rlines,
      r1_outcome:$r1, r2_outcome:$r2, r3_outcome:$r3, r4_outcome:$r4, r5_outcome:$r5, r6_outcome:$r6, run_summary_outcome:$rsum,
      reconcile_exit:$code, reconcile_pass:$pass, failure:$reason,
      note:"read-only transfer bound to the consumed run id; records.jsonl is hashed and its newlines counted, never parsed"}' \
    > "$out/reconcile-result.json"
  echo "reconcile_pass=$pass reconcile_exit=$1 ${2:+reason=$2}"
  exit "$1"
}

# R-1
got_sha=$(sha256sum "$res" | cut -d ' ' -f1)
echo "launcher_result_sha256=$got_sha"
job=$(jq -r '.job.job_name // ""' "$req" 2>/dev/null || true)
if [[ $got_sha != "$want_sha" ]]; then o_r1=fail; finish 3 "launcher result sha256 $got_sha differs from $want_sha"; fi
if [[ -z $job ]] || [[ $(jq -r '.job_name // ""' "$res") != "$job" ]]; then o_r1=fail; finish 3 "launcher result job_name differs from the request job name '$job'"; fi
job_uid=$(jq -r '.job_uid // ""' "$res"); receipt_uri=$(jq -r '.receipt_uri // ""' "$res")
if [[ -z $job_uid || -z $receipt_uri ]]; then o_r1=fail; finish 3 "launcher result has no job_uid or receipt_uri"; fi
o_r1=pass

# R-2 and R-3 (listing): the shared locator
mkdir -p "$out/locator"
set +e
"$here/locate_results.sh" locate --launcher-result "$res" --job "$job" --bucket "$ISOLAB_BUCKET" \
  --workdir "$out/locator" --out "$out/locator/locator.json"
loc_rc=$?
set -e
echo "locate_results exit $loc_rc"
if [[ $loc_rc != 0 ]]; then o_r2=fail; finish 4 "locator exit $loc_rc"; fi
results_locator=$(jq -r .results_locator "$out/locator/locator.json")
results_uri=$(jq -r .results_uri "$out/locator/locator.json")
pod_uid=$(jq -r '.pod_uid // ""' "$out/locator/locator.json")
pod_exit=$(jq -r '.pod_exit_code // ""' "$out/locator/locator.json")
if [[ $results_locator != receipt_status_pod_uid ]]; then o_r2=fail; finish 4 "results_locator is $results_locator, expected receipt_status_pod_uid (T1's result.json names no results_uri)"; fi
o_r2=pass
set +e
s3_get "${receipt_uri}objects.json" "$out/locator/objects.json"; orc=$?
set -e
if [[ $orc != 0 ]]; then o_r3=fail; finish 5 "could not copy ${receipt_uri}objects.json (exit $orc)"; fi
bad_keys=$(jq -r --arg a "runs/$job/launcher/" --arg b "runs/$job/$pod_uid/" \
  '(.objects // []) | map(.Key) | map(select((startswith($a) or startswith($b)) | not)) | length' "$out/locator/objects.json" 2>/dev/null || echo bad)
if [[ $bad_keys != 0 ]]; then o_r3=fail; finish 5 "objects.json lists keys outside launcher/ and the located pod prefix ($bad_keys)"; fi
o_r3=pass

# R-4
mkdir -p "$out/artifacts"
set +e
s3_get "$results_uri" "$out/artifacts/" --recursive
dl_rc=$?
set -e
echo "download_exit=$dl_rc"
if [[ $dl_rc != 0 ]]; then o_r4=fail; finish 6 "download exit $dl_rc"; fi
(cd "$out/artifacts" && find . -type f -printf '%s %P\n' | LC_ALL=C sort -k2) > "$out/object-list.txt"
echo "downloaded $(wc -l < "$out/object-list.txt") files"
o_r4=pass

# SHA256SUMS and run-summary.json rule (ruling 5)
if [[ ! -s $out/artifacts/SHA256SUMS ]]; then o_sums=fail; finish 9 "SHA256SUMS is absent or empty"; fi
sums_sha=$(sha256sum "$out/artifacts/SHA256SUMS" | cut -d ' ' -f1)
rs_digest=$(awk '$2 == "run-summary.json" { print $1 }' "$out/artifacts/SHA256SUMS")
rs_bytes=$(stat -c %s "$out/artifacts/run-summary.json" 2>/dev/null || echo absent)
if [[ $rs_digest != "$EMPTY_SHA256" || $rs_bytes != 0 ]]; then
  o_sums=fail; finish 9 "run-summary.json is unlisted, listed at '${rs_digest:-none}' instead of $EMPTY_SHA256, or not 0 bytes (bytes $rs_bytes)"
fi
o_sums=pass

# R-5
set +e
"$here/locate_results.sh" verify --locator "$out/locator/locator.json" --artifacts "$out/artifacts"
vrc=$?
set -e
echo "locate_results verify exit $vrc"
if [[ $vrc != 0 ]]; then o_r5=fail; finish 7 "verify exit $vrc"; fi
job_exit=$(jq -r '.exit_code' "$out/artifacts/job-exit.json")
o_r5=pass

# R-6
set +e
python3 -I "$checkjob" "$out/artifacts" --request "$req" --launcher-result "$res" > "$out/check_job.stdout" 2> "$out/check_job.stderr"
check_rc=$?
set -e
cat "$out/check_job.stdout"
if [[ $check_rc != 0 || $(tail -n 1 "$out/check_job.stdout") != CHECK_JOB_OK ]]; then o_r6=fail; finish 8 "check_job.py exit $check_rc"; fi
o_r6=pass

# R-7: hash and newline count only
if [[ -f $out/artifacts/session/records.jsonl ]]; then
  rec_sha=$(sha256sum "$out/artifacts/session/records.jsonl" | cut -d ' ' -f1)
  rec_lines=$(wc -l < "$out/artifacts/session/records.jsonl" | tr -d ' ')
fi
finish 0 ""
