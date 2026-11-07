#!/usr/bin/env bash
# Offline fixture tests for launch_eks.sh (v3b), locate_results.sh and reconcile_run.sh (DEC-20261107-b74e2c T-1, T-2;
# TASK-20261107-c5a0f4 D-4, D-5). No AWS call: tests/fake-aws serves a local directory as the bucket, logs every call and refuses
# every S3 write; tests/fake-launch-remote stands in for the job. The T1 receipt shape (result.json, status.json) is the real one
# in tests/fixtures/receipt/; the job's own files are synthetic.
#
# usage: test_locator.sh [OUTDIR [REAL_CHECKOUT]]
#   OUTDIR         where case directories and RESULTS.txt are written (default: a new directory under $TMPDIR)
#   REAL_CHECKOUT  a checkout holding the four pinned launcher scripts, for the --dry-run case (optional)
# Exit 0 when every case gives its expected result.
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
IMPL=$(cd "$here/.." && pwd)
EXP=$(cd "$IMPL/.." && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/c1-locator-test.XXXXXX")}
REAL_CHECKOUT=${2:-}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
RES="$OUT/RESULTS.txt"; : > "$RES"
REQ="$EXP/inputs/request-s1.json"; PROTO="$EXP/inputs/protocol.json"; CHECKJOB="$IMPL/check_job.py"
RCPT="$here/fixtures/receipt"; V3A="$here/fixtures/launch_eks.v3a.sh"
BUCKET=isolab-results-104186811093-us-east-2; JOB=ic-c1-dg-s1-20261106
REAL_POD=5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7; LAUNCHER_ID=47cf1e4f-10a7-4ee3-862d-9e9700e122e3
OTHER_POD=0aaaaaaa-1111-2222-3333-444444444444
PIN_ECBENCH=73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01
PIN_COMMIT=ea8e9ef71c3c82027dd9e01535302725519c3fca
REAL_RESULT_SHA=7c3d9954a561a7a0d07e498afe3ecdf5b8c53359cfa28abb578a67dc8a6d60e7
EMPTY_SHA=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
npass=0; nfail=0
say() { printf '%s\n' "$*" | tee -a "$RES"; }
expect() { # expect CASE WHAT EXPECTED OBSERVED
  if [[ $3 == "$4" ]]; then npass=$((npass + 1)); say "PASS  $1 | $2 | expected=[$3] observed=[$4]"
  else nfail=$((nfail + 1)); say "FAIL  $1 | $2 | expected=[$3] observed=[$4]"; fi
}

planned=$(jq -r '(.job.spec.workloads.curves | length) * .job.spec.workloads.targets_per_curve
  * (.job.spec.measurement.warmup + .job.spec.measurement.rounds) * (.job.spec.arms | length)' "$REQ")

declare -A P
build_case() { # build_case ID [key=value ...]  : writes $OUT/cases/ID/fx ; keys documented inline below
  local id=$1; shift
  P=(); local kv
  for kv in "$@"; do P[${kv%%=*}]=${kv#*=}; done
  local je_exit=${P[je_exit]:-42} je_job=${P[je_job]:-$JOB} je_pod=${P[je_pod]:-$REAL_POD} cexit=${P[cexit]:-42}
  local sums=${P[sums]:-normal} rsum=${P[rsum]:-empty} status_mut=${P[status_mut]:-.} result_mut=${P[result_mut]:-.}
  local shape=${P[shape]:-failed} extra_prefix=${P[extra_prefix]:-0} no_status=${P[no_status]:-0}
  local fx="$OUT/cases/$id/fx"; rm -rf "$OUT/cases/$id"
  local pd="$fx/s3/runs/$JOB/$REAL_POD" rc="$fx/s3/runs/$JOB/launcher/$LAUNCHER_ID"
  mkdir -p "$fx/launcher" "$pd/session" "$rc"
  # the job's own files (synthetic, valid for check_job.py)
  printf '%s  ecbench\n' "$PIN_ECBENCH" > "$pd/binary.sha256"
  jq -n --arg b "$PIN_ECBENCH" --arg c "$PIN_COMMIT" '{ecbench_sha256:$b, source_revision:$c}' > "$pd/build-info.json"
  echo '{"accepted":true}' > "$pd/l2-gate.json"
  jq '.job.spec' "$REQ" > "$pd/input-spec.json"; cp "$pd/input-spec.json" "$pd/session/spec.json"
  yes '{}' 2>/dev/null | head -n "$planned" > "$pd/session/records.jsonl"
  echo '{"fixture":true}' > "$pd/session/plan.json"
  echo fixture > "$pd/audit.stderr"
  jq -n --argjson e "$je_exit" --arg j "$je_job" --arg p "$je_pod" '{exit_code:$e, job_name:$j, pod_uid:$p, node_name:"fixture"}' > "$pd/job-exit.json"
  if [[ $rsum == empty ]]; then : > "$pd/run-summary.json"; else echo '{"x":1}' > "$pd/run-summary.json"; fi
  case $sums in
    normal) (cd "$pd" && find . -type f ! -name SHA256SUMS | sed 's|^\./||' | LC_ALL=C sort | xargs sha256sum) > "$pd/SHA256SUMS" ;;
    unlisted_rs) (cd "$pd" && find . -type f ! -name SHA256SUMS ! -name run-summary.json | sed 's|^\./||' | LC_ALL=C sort | xargs sha256sum) > "$pd/SHA256SUMS" ;;
    empty) : > "$pd/SHA256SUMS" ;;
  esac
  if [[ ${P[tamper]:-0} == 1 ]]; then echo "changed after SHA256SUMS was written" >> "$pd/audit.stderr"; fi
  # the launcher receipt (T1 shape: the real result.json and status.json) and the launcher's own copy of result.json
  if [[ $shape == failed ]]; then
    jq "$result_mut" "$RCPT/result.json" > "$rc/result.json"
    jq --argjson cx "$cexit" '.pods[0].status.containerStatuses[0].state.terminated.exitCode = $cx' "$RCPT/status.json" | jq "$status_mut" > "$rc/status.json"
    [[ $no_status == 1 ]] && rm -f "$rc/status.json"
    echo 26 > "$fx/launch_rc"; jq -n '{builds:[{buildStatus:"FAILED"}]}' > "$fx/launcher/build.json"
  else # a succeeded Job: results_uri is non-empty and no receipt is needed
    jq --arg u "s3://$BUCKET/runs/$JOB/$REAL_POD/" --arg p "$REAL_POD" \
      '.state="succeeded" | .exit_code=0 | .pod_uid=$p | .results_uri=$u' "$RCPT/result.json" | jq "$result_mut" > "$fx/launcher/result.json"
    echo 0 > "$fx/launch_rc"; jq -n '{builds:[{buildStatus:"SUCCEEDED"}]}' > "$fx/launcher/build.json"
  fi
  [[ $shape == failed ]] && cp "$rc/result.json" "$fx/launcher/result.json"
  if [[ $shape != failed ]]; then rm -rf "$rc"; fi
  if [[ $shape == failed ]]; then
    (cd "$pd" && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while read -r f; do printf '%s %s\n' "$(stat -c %s "$f")" "$f"; done) \
      | jq -Rn --arg b "$BUCKET" --arg j "$JOB" --arg p "$REAL_POD" '{next_token:null, results_uri:("s3://"+$b+"/runs/"+$j+"/"),
          objects:[inputs | split(" ") | {Key:("runs/"+$j+"/"+$p+"/"+.[1]), Size:(.[0]|tonumber)}]}' > "$rc/objects.json"
  fi
  if [[ $extra_prefix == 1 ]]; then mkdir -p "$fx/s3/runs/$JOB/$OTHER_POD"; echo note > "$fx/s3/runs/$JOB/$OTHER_POD/note.txt"; fi
}

run_wrapper() { # run_wrapper ID v3a|v3b  : prints nothing; sets W_RC, W_CLASS, W_LOC, W_POD, W_DIR
  local id=$1 ver=$2; local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/wrap-$2"
  rm -rf "$w"; mkdir -p "$w/impl" "$w/checkout/taskq/deploy/eks-karpenter/remote" "$w/rec" "$w/s3root" "$w/bin"
  if [[ $ver == v3b ]]; then cp "$IMPL/launch_eks.sh" "$IMPL/locate_results.sh" "$w/impl/"; else cp "$V3A" "$w/impl/launch_eks.sh"; fi
  chmod +x "$w/impl/"*.sh
  local r="$w/checkout/taskq/deploy/eks-karpenter/remote" f
  cp "$here/fake-launch-remote" "$r/launch-remote"
  printf '#!/usr/bin/env bash\ncat "$1"\n' > "$r/validate-request"
  echo '#!/usr/bin/env bash' > "$r/run-request"; echo 'version: 0.2' > "$r/current-run-request-buildspec.yml"
  chmod +x "$r/launch-remote" "$r/validate-request" "$r/run-request"
  : > "$w/impl/remote-pins.sha256"
  for f in launch-remote validate-request run-request current-run-request-buildspec.yml; do
    printf '%s  %s\n' "$(sha256sum "$r/$f" | cut -d ' ' -f1)" "$f" >> "$w/impl/remote-pins.sha256"
  done
  ln -s "$here/fake-aws" "$w/bin/aws"
  printf '{"run_id":"RUN-TEST","trial_id":"T1"}\n' > "$w/rec/launch.json"
  : > "$w/aws.log"
  env PATH="$w/bin:$PATH" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" FAKE_CASE_DIR="$fx" AWS_REGION=us-east-2 \
    ISOLAB_BUCKET="$BUCKET" ISOLAB_CODEBUILD_PROJECT=isolab-experiment-launcher CRYPTO_CHECKOUT="$w/checkout" \
    bash "$w/impl/launch_eks.sh" --protocol "$PROTO" --experiment-id EXP-TEST --hypothesis-id H-TEST --task-id TASK-TEST \
    --approved-by DEC-TEST --trial-id T1 --run-id RUN-TEST --out "$w/rec/job" --record-dir "$w/rec" "$REQ" \
    > "$w/stdout" 2> "$w/stderr"
  W_RC=$?; W_DIR=$w
  W_CLASS=$(jq -r '.outcome_class // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_LOC=$(jq -r '.results_locator // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_POD=$(jq -r '.pod_uid // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
}

run_reconcile() { # run_reconcile ID [sha] [outsub] [tag]  : sets R_RC, R_PASS, R_DIR (work directory cases/ID/reconcileTAG)
  local id=$1 sha=${2:-$REAL_RESULT_SHA} outsub=${3:-out} tag=${4:-}; local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/reconcile$tag"
  rm -rf "$w"; mkdir -p "$w/bin" "$w/s3root" "$w/$outsub"
  cp -r "$fx/s3/." "$w/s3root/"; ln -s "$here/fake-aws" "$w/bin/aws"; : > "$w/aws.log"
  env PATH="$w/bin:$PATH" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" \
    bash "$IMPL/reconcile_run.sh" --launcher-result "$fx/launcher/result.json" --launcher-result-sha256 "$sha" --request "$REQ" \
    --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/$outsub" > "$w/stdout" 2> "$w/stderr"
  R_RC=$?; R_DIR=$w
  R_PASS=$(jq -r 'if has("reconcile_pass") then (.reconcile_pass | tostring) else "absent" end' "$w/$outsub/reconcile-result.json" 2>/dev/null || echo absent)
}

say "== C1 locator / v3b / reconcile fixture tests, $(date -u +%FT%TZ); outputs in $OUT"
say "== real receipt fixtures: $(cd "$RCPT" && sha256sum status.json result.json objects.json | tr '\n' ';')"
expect fixtures "real result.json sha256 equals the receipt binding" "$REAL_RESULT_SHA" "$(sha256sum "$RCPT/result.json" | cut -d ' ' -f1)"
say "== planned executions per fixture session: $planned"

say "== wrapper v3b / v3a, positive cases"
build_case P1
run_wrapper P1 v3b
expect P1-wrapper-v3b "T1 real receipt shape + job-exit 42: exit status" 0 "$W_RC"
expect P1-wrapper-v3b "outcome_class" job_completed "$W_CLASS"
expect P1-wrapper-v3b "results_locator" receipt_status_pod_uid "$W_LOC"
expect P1-wrapper-v3b "pod_uid recorded" "$REAL_POD" "$W_POD"
expect P1-wrapper-v3b "job_uid recorded" 8a20d036-efc2-45d2-ada6-6442b93c5a52 "$(jq -r .job_uid "$W_DIR/rec/raw-result.json")"
expect P1-wrapper-v3b "no S3 write attempted (no fake-aws refusal in the log)" 0 "$(grep -c 'REFUSED' "$W_DIR/stderr" "$W_DIR/stdout" | awk -F: '{s+=$2} END {print s+0}')"
expect P1-wrapper-v3b "every aws call is a read (cp from s3, ls, codebuild list)" 0 \
  "$(grep -v -E '^aws (s3 cp s3://[^ ]+ [^ ]+|s3 ls s3://[^ ]+|codebuild list-builds-for-project )' "$W_DIR/aws.log" | grep -c . || true)"
run_wrapper P1 v3a
expect P1-wrapper-v3a "same fixture on v3a reproduces the defect: exit status" 5 "$W_RC"
expect P1-wrapper-v3a "outcome_class" infrastructure_candidate "$W_CLASS"

build_case P2 shape=succeeded je_exit=0
run_wrapper P2 v3b; p2b_rc=$W_RC; p2b_class=$W_CLASS
expect P2-wrapper-v3b "succeeded Job, non-empty results_uri: exit status" 0 "$W_RC"
expect P2-wrapper-v3b "outcome_class" job_completed "$W_CLASS"
expect P2-wrapper-v3b "results_locator" launcher_result "$W_LOC"
expect P2-wrapper-v3b "no receipt object read (rule (a) makes no AWS call of its own)" 0 "$(grep -c 'launcher/' "$W_DIR/aws.log" || true)"
jq -S 'del(.started_at, .finished_at, .results_locator, .job_uid, .pod_uid, .job_files["locator/locator.json"])' "$W_DIR/rec/raw-result.json" > "$OUT/cases/P2/raw-v3b.norm.json"
run_wrapper P2 v3a
expect P2-wrapper-v3a "succeeded Job on v3a: exit status" 0 "$W_RC"
expect P2-wrapper-v3a "outcome_class" job_completed "$W_CLASS"
jq -S 'del(.started_at, .finished_at, .results_locator, .job_uid, .pod_uid, .job_files["locator/locator.json"])' "$W_DIR/rec/raw-result.json" > "$OUT/cases/P2/raw-v3a.norm.json"
expect P2-wrapper "v3a and v3b raw-result.json equal apart from timestamps, the three new fields and the locator/locator.json inventory entry" \
  "$(sha256sum < "$OUT/cases/P2/raw-v3a.norm.json")" "$(sha256sum < "$OUT/cases/P2/raw-v3b.norm.json")"
expect P2-wrapper "manifest.yaml byte-identical between v3a and v3b" \
  "$(sha256sum < "$W_DIR/rec/manifest.yaml")" "$(sha256sum < "$OUT/cases/P2/wrap-v3b/rec/manifest.yaml")"

say "== wrapper v3b, negative cases (none may give job_completed; exit status 5 expected)"
declare -a NEG=(
  "N1-0pods|infrastructure_candidate|status_mut=.pods=[]"
  "N2-2pods|infrastructure_candidate|status_mut=.pods+=[(.pods[0]|.uid=\"$OTHER_POD\")]"
  "N3-status-job-uid|infrastructure_candidate|status_mut=.job.uid=\"00000000-0000-0000-0000-000000000000\""
  "N4-extra-pod-prefix|infrastructure_candidate|extra_prefix=1"
  "N5-jobexit-pod-uid|other|je_pod=$OTHER_POD"
  "N6-jobexit-job-name|other|je_job=ic-c1-dg-s2-20261106"
  "N7-container-exit-ne-jobexit|other|je_exit=43"
  "N8-missing-receipt|infrastructure_candidate|no_status=1"
  "N9-empty-sha256sums|other|sums=empty"
  "N10-result-job-name|infrastructure_candidate|result_mut=.job_name=\"ic-c1-dg-s2-20261106\""
  "N11-status-job-name|infrastructure_candidate|status_mut=.job.job_name=\"ic-c1-dg-s2-20261106\""
  "N12-status-job-not-failed|infrastructure_candidate|status_mut=.job.state=\"succeeded\""
  "N17-two-container-statuses|infrastructure_candidate|status_mut=.pods[0].status.containerStatuses+=[.pods[0].status.containerStatuses[0]]"
  "N18-container-not-terminated|infrastructure_candidate|status_mut=del(.pods[0].status.containerStatuses[0].state.terminated)"
)
for row in "${NEG[@]}"; do
  IFS='|' read -r nid nclass nkv <<<"$row"
  build_case "$nid" "$nkv"
  run_wrapper "$nid" v3b
  expect "$nid-wrapper-v3b" "exit status" 5 "$W_RC"
  expect "$nid-wrapper-v3b" "outcome_class (not job_completed)" "$nclass" "$W_CLASS"
done

say "== reconcile_run.sh, positive case"
run_reconcile P1
expect P1-reconcile "T1 real receipt shape: exit status" 0 "$R_RC"
expect P1-reconcile "reconcile_pass" true "$R_PASS"
expect P1-reconcile "run_id" RUN-ICPERF-8b0d47 "$(jq -r .run_id "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "trial_id" T1 "$(jq -r .trial_id "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "pod_uid" "$REAL_POD" "$(jq -r .pod_uid "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "check_job_exit" 0 "$(jq -r .check_job_exit "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "check_job last line" CHECK_JOB_OK "$(tail -n 1 "$R_DIR/out/check_job.stdout")"
expect P1-reconcile "every aws call is a read" 0 \
  "$(grep -v -E '^aws (s3 cp s3://[^ ]+ [^ ]+( --recursive)?( --only-show-errors)?|s3 ls s3://[^ ]+)' "$R_DIR/aws.log" | grep -c . || true)"
expect P1-reconcile "no S3 write attempted" 0 "$(grep -c 'REFUSED' "$R_DIR/stderr" || true)"

say "== reconcile_run.sh, negative cases (none may pass)"
declare -a RNEG=(
  "N1-0pods|4"  "N2-2pods|4"  "N3-status-job-uid|4"  "N4-extra-pod-prefix|4"  "N5-jobexit-pod-uid|7"  "N6-jobexit-job-name|7"
  "N7-container-exit-ne-jobexit|7"  "N8-missing-receipt|4"  "N9-empty-sha256sums|9"  "N10-result-job-name|3"  "N11-status-job-name|4"
  "N12-status-job-not-failed|4"  "N17-two-container-statuses|4"  "N18-container-not-terminated|4"
)
for row in "${RNEG[@]}"; do
  IFS='|' read -r nid ncode <<<"$row"
  run_reconcile "$nid" "$(sha256sum "$OUT/cases/$nid/fx/launcher/result.json" | cut -d ' ' -f1)"
  expect "$nid-reconcile" "exit status" "$ncode" "$R_RC"
  expect "$nid-reconcile" "reconcile_pass" false "$R_PASS"
done
build_case N13-run-summary-unlisted sums=unlisted_rs
run_reconcile N13-run-summary-unlisted
expect N13-run-summary-unlisted-reconcile "exit status" 9 "$R_RC"; expect N13-run-summary-unlisted-reconcile "reconcile_pass" false "$R_PASS"
build_case N19-file-hash-mismatch tamper=1
run_reconcile N19-file-hash-mismatch
expect N19-file-hash-mismatch-reconcile "a listed file differs from SHA256SUMS (check_job.py sums FAIL): exit status" 8 "$R_RC"; expect N19-file-hash-mismatch-reconcile "reconcile_pass" false "$R_PASS"
build_case N14-run-summary-other-digest rsum=nonempty
run_reconcile N14-run-summary-other-digest
expect N14-run-summary-other-digest-reconcile "exit status" 9 "$R_RC"; expect N14-run-summary-other-digest-reconcile "reconcile_pass" false "$R_PASS"
expect N14-run-summary-other-digest-reconcile "listed digest is not the empty-file digest" "yes" \
  "$([[ $(jq -r .run_summary_listed_sha256 "$R_DIR/out/reconcile-result.json") != "$EMPTY_SHA" ]] && echo yes || echo no)"
run_reconcile P1 0000000000000000000000000000000000000000000000000000000000000000 out -wrongsha
expect R1-wrong-receipt-sha256-reconcile "exit status" 3 "$R_RC"; expect R1-wrong-receipt-sha256-reconcile "reconcile_pass" false "$R_PASS"
build_case N15-succeeded-shape shape=succeeded
run_reconcile N15-succeeded-shape "$(sha256sum "$OUT/cases/N15-succeeded-shape/fx/launcher/result.json" | cut -d ' ' -f1)"
expect N15-launcher-result-locator-reconcile "T1 must be located by the receipt: exit status" 4 "$R_RC"; expect N15-launcher-result-locator-reconcile "reconcile_pass" false "$R_PASS"
run_reconcile P1 "$REAL_RESULT_SHA" out/runs/x -outinruns
expect N16-out-inside-runs-reconcile "exit status" 2 "$R_RC"
expect N16-out-inside-runs-reconcile "nothing written" 0 "$(find "$R_DIR/out/runs/x" -type f 2>/dev/null | wc -l)"

say "== static checks"
for f in launch_eks.sh locate_results.sh reconcile_run.sh tests/test_locator.sh tests/fake-aws tests/fake-launch-remote; do
  bash -n "$IMPL/$f"; expect "bash -n $f" "syntax" 0 "$?"
done
forbidden='launch-remote|codebuild|start-build|batch-get-builds|s3api|put-object|delete-object|s3 (rm|mv|sync|mb|rb|presign)'
for f in locate_results.sh reconcile_run.sh; do
  expect "grep $f" "no job-submission, build-start or S3-write token (case-insensitive)" 0 "$(grep -c -i -E "$forbidden" "$IMPL/$f" || true)"
done
cpl='aws s3 cp "$1" "$2" "${@:3}" --only-show-errors'; lsl='aws s3 ls "$1"'
expect "grep locate_results.sh" "outside comments, the only aws invocations are the cp helper and the ls helper (read-only)" "$cpl|$lsl" \
  "$(grep -v '^[[:space:]]*#' "$IMPL/locate_results.sh" | grep -E '(^|[^[:alnum:]_.-])aws([[:space:]]|$)' | sed 's/^[[:space:]]*//' | tr '\n' '|' | sed 's/|$//')"
expect "grep reconcile_run.sh" "outside comments, the only aws invocation is the cp helper (read-only)" "$cpl" \
  "$(grep -v '^[[:space:]]*#' "$IMPL/reconcile_run.sh" | grep -E '(^|[^[:alnum:]_.-])aws([[:space:]]|$)' | sed 's/^[[:space:]]*//' | tr '\n' '|' | sed 's/|$//')"
expect "grep locate_results.sh,reconcile_run.sh" "both helpers refuse a destination that is an S3 URI" 2 \
  "$(grep -c -F '[[ $1 == s3://* && $2 != s3://* ]]' "$IMPL/locate_results.sh" "$IMPL/reconcile_run.sh" | awk -F: '{s+=$2} END {print s}')"
# v3a -> v3b: lines 1-234 byte-identical, class block identical, last two lines identical
expect "v3a-v3b diff" "v3a sha256 is the reviewed 0fcdd67e..." 0fcdd67e22f6105c36883bf9ba7edb62e512e6ff135979e0b63084fb2c9b7dc0 "$(sha256sum "$V3A" | cut -d ' ' -f1)"
expect "v3a-v3b diff" "lines 1-234 (sections 1, 1b, 1c, 2, write_records, manifests) byte-identical" "" \
  "$(diff <(head -n 234 "$V3A") <(head -n 234 "$IMPL/launch_eks.sh") | head -n 3)"
blk() { sed -n '/^# Outcome class\./,/^fi$/p' "$1"; }
expect "v3a-v3b diff" "outcome-class block (deadline first, 42/43 accept branch) byte-identical" "" "$(diff <(blk "$V3A") <(blk "$IMPL/launch_eks.sh") | head -n 3)"
expect "v3a-v3b diff" "outcome-class block is non-empty" yes "$([[ $(blk "$V3A" | wc -l) -ge 12 ]] && echo yes || echo no)"
expect "v3a-v3b diff" "final exit lines identical" "" "$(diff <(tail -n 3 "$V3A") <(tail -n 3 "$IMPL/launch_eks.sh") | head -n 3)"
diff -u "$V3A" "$IMPL/launch_eks.sh" > "$OUT/launch_eks.v3a-to-v3b.diff"
grep -n '^@@' "$OUT/launch_eks.v3a-to-v3b.diff" > "$OUT/launch_eks.v3a-to-v3b.hunks.txt"
say "== hunk list (v3a line ranges): $(sed 's/^[0-9]*://' "$OUT/launch_eks.v3a-to-v3b.hunks.txt" | tr '\n' ';')"
expect "v3a-v3b diff" "first changed line is in section 3 (v3a line >= 235)" yes \
  "$(awk '/^--- |^\+\+\+ / {next} /^@@/ {split($2,a,","); ln=-a[1]; next} /^ / {ln++; next} /^-/ {print ln; exit} /^\+/ {print ln; exit}' "$OUT/launch_eks.v3a-to-v3b.diff" | awk '{print ($1 >= 235) ? "yes" : "no"}')"

say "== --dry-run of v3b (no AWS call)"
if [[ -n $REAL_CHECKOUT && -d $REAL_CHECKOUT ]]; then
  w="$OUT/dryrun"; rm -rf "$w"; mkdir -p "$w/bin" "$w/rec"; ln -s "$here/fake-aws" "$w/bin/aws"; : > "$w/aws.log"
  env PATH="$w/bin:$PATH" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" \
    ISOLAB_CODEBUILD_PROJECT=isolab-experiment-launcher CRYPTO_CHECKOUT="$REAL_CHECKOUT" \
    bash "$IMPL/launch_eks.sh" --dry-run --protocol "$PROTO" --experiment-id EXP-TEST --hypothesis-id H-TEST --task-id TASK-TEST \
    --approved-by DEC-TEST --trial-id T2 --run-id RUN-TEST --out "$w/rec/job" --record-dir "$w/rec" "$EXP/inputs/request-s2.json" \
    > "$w/stdout" 2> "$w/stderr"
  expect dry-run "exit status" 0 "$?"
  expect dry-run "aws calls made (fake-aws log lines)" 0 "$(grep -c . "$w/aws.log" || true)"
  expect dry-run "prints the DRY RUN banner" 1 "$(grep -c '^DRY RUN: no AWS call is made' "$w/stdout")"
  expect dry-run "remote scripts match 4 pinned values" 1 "$(grep -c '^remote scripts match 4 pinned sha256 values' "$w/stdout")"
else
  say "SKIP  dry-run: no REAL_CHECKOUT argument"
fi

say "== SUMMARY $npass pass, $nfail fail"
[[ $nfail == 0 ]]
