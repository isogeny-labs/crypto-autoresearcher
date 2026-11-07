#!/usr/bin/env bash
# Offline fixture tests for launch_eks.sh (v3c), locate_results.sh and reconcile_run.sh (DEC-20261107-b74e2c T-1, T-2;
# TASK-20261107-c5a0f4 D-4, D-5; TASK-20261107-d07e94 E-4). No AWS call: tests/fake-aws serves a local directory as the bucket,
# logs every call and refuses every S3 write; tests/fake-launch-remote stands in for the job. The T1 receipt shape (result.json,
# status.json, objects.json) is the real one in tests/fixtures/receipt/; the job's own files are synthetic.
# v3c: the scripts re-execute themselves under `env -i` (K-7), so the fakes read their settings from conf files next to the `aws`
# symlink and next to launch-remote; no FAKE_* variable crosses the exec. The adversarial cases of the 9d2b6a review, re-targeted at
# v3c, are in tests/rt_regression.sh; the mutation cases are in tests/mutation_check.sh.
#
# usage: test_locator.sh [OUTDIR [REAL_CHECKOUT]]
#   OUTDIR         where case directories and RESULTS.txt are written (default: a new directory under $TMPDIR)
#   REAL_CHECKOUT  a checkout holding the four pinned launcher scripts, for the --dry-run case (a missing one is a failure, not a skip)
# Run it as: env -i HOME="$HOME" TMPDIR=<tmp> PATH=<dir holding only the fake aws>:/usr/bin:/bin bash test_locator.sh OUTDIR CHECKOUT
# Exit 0 when every case gives its expected result.
set -u
here=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
IMPL=$(cd "$here/.." && pwd)
EXP=$(cd "$IMPL/.." && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/c1-locator-test.XXXXXX")}
REAL_CHECKOUT=${2:-}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
RES="$OUT/RESULTS.txt"; : > "$RES"
REQ="$EXP/inputs/request-s1.json"; PROTO="$EXP/inputs/protocol.json"; CHECKJOB="$IMPL/check_job.py"
RCPT="$here/fixtures/receipt"; V3A="$here/fixtures/launch_eks.v3a.sh"; V3B="$here/fixtures/launch_eks.v3b.sh"; V3B_LOC="$here/fixtures/locate_results.v3b.sh"
BUCKET=isolab-results-104186811093-us-east-2; JOB=ic-c1-dg-s1-20261106
REAL_POD=5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7; LAUNCHER_ID=47cf1e4f-10a7-4ee3-862d-9e9700e122e3
OTHER_POD=0aaaaaaa-1111-2222-3333-444444444444
PIN_ECBENCH=73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01
PIN_COMMIT=ea8e9ef71c3c82027dd9e01535302725519c3fca
REAL_RESULT_SHA=7c3d9954a561a7a0d07e498afe3ecdf5b8c53359cfa28abb578a67dc8a6d60e7
REAL_STATUS_SHA=a2642563d10a8f80661cef79a759b892d44fad49057a409ae03a1bee3a960ae0
REAL_OBJECTS_SHA=783ea0e3ec77daf52d3ff815cb096295a3db76fe05b5cc9b1884c001126504d7
PIN_NA=2026-11-07T02:14:41Z
EMPTY_SHA=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
npass=0; nfail=0
say() { printf '%s\n' "$*" | tee -a "$RES"; }
expect() { # expect CASE WHAT EXPECTED OBSERVED
  if [[ $3 == "$4" ]]; then npass=$((npass + 1)); say "PASS  $1 | $2 | expected=[$3] observed=[$4]"
  else nfail=$((nfail + 1)); say "FAIL  $1 | $2 | expected=[$3] observed=[$4]"; fi
}

# isolation precondition: no AWS_* variable, and no aws binary in /usr/bin or /bin (every run puts the fake first on PATH anyway)
[[ $(env | grep -c '^AWS_') == 0 ]] || { echo "REFUSED: AWS_* variables are set; run this under env -i" >&2; exit 99; }
[[ ! -e /usr/bin/aws && ! -e /bin/aws ]] || { echo "REFUSED: an aws binary exists in /usr/bin or /bin" >&2; exit 99; }

planned=$(jq -r '(.job.spec.workloads.curves | length) * .job.spec.workloads.targets_per_curve
  * (.job.spec.measurement.warmup + .job.spec.measurement.rounds) * (.job.spec.arms | length)' "$REQ")

mk_bin() { # mk_bin DIR S3ROOT LOG : a directory holding only the fake as `aws`, with its conf file
  mkdir -p "$1"; ln -sfn "$here/fake-aws" "$1/aws"
  printf 'FAKE_AWS_LOG=%q\nFAKE_S3_ROOT=%q\n' "$3" "$2" > "$1/fake-aws.conf"
}

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
    cp "$rc/result.json" "$fx/launcher/result.json"
  else # a succeeded Job: results_uri is non-empty; v3c still reads the receipt (K-1)
    jq --arg u "s3://$BUCKET/runs/$JOB/$REAL_POD/" --arg p "$REAL_POD" \
      '.state="succeeded" | .exit_code=0 | .pod_uid=$p | .results_uri=$u' "$RCPT/result.json" | jq "$result_mut" > "$fx/launcher/result.json"
    cp "$fx/launcher/result.json" "$rc/result.json"
    jq --argjson cx "$cexit" '.job.state="succeeded" | .pods[0].status.containerStatuses[0].state.terminated.exitCode = $cx' "$RCPT/status.json" | jq "$status_mut" > "$rc/status.json"
    echo 0 > "$fx/launch_rc"; jq -n '{builds:[{buildStatus:"SUCCEEDED"}]}' > "$fx/launcher/build.json"
  fi
  # the launcher's objects.json: Key, Size and ETag (the md5 of each object) of the pod prefix, as the launcher listed it
  (cd "$pd" && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while read -r f; do printf '%s %s %s\n' "$(stat -c %s "$f")" "$(md5sum "$f" | cut -d ' ' -f1)" "$f"; done) \
    | jq -Rn --arg b "$BUCKET" --arg j "$JOB" --arg p "$REAL_POD" '{next_token:null, results_uri:("s3://"+$b+"/runs/"+$j+"/"),
        objects:[inputs | split(" ") | {Key:("runs/"+$j+"/"+$p+"/"+.[2]), Size:(.[0]|tonumber), ETag:("\""+.[1]+"\"")}]}' > "$rc/objects.json"
  if [[ $extra_prefix == 1 ]]; then mkdir -p "$fx/s3/runs/$JOB/$OTHER_POD"; echo note > "$fx/s3/runs/$JOB/$OTHER_POD/note.txt"; fi
  find "$fx/s3" -exec touch -d '2026-11-07T02:14:21Z' {} +   # every object is as old as the launcher's snapshot
}

run_wrapper() { # run_wrapper ID v3a|v3b|v3c  : prints nothing; sets W_RC, W_CLASS, W_LOC, W_POD, W_DIR
  local id=$1 ver=$2; local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/wrap-$2"
  rm -rf "$w"; mkdir -p "$w/impl" "$w/checkout/taskq/deploy/eks-karpenter/remote" "$w/rec" "$w/s3root" "$w/bin" "$w/home"
  case $ver in
    v3c) cp "$IMPL/launch_eks.sh" "$IMPL/locate_results.sh" "$w/impl/" ;;
    v3b) cp "$V3B" "$w/impl/launch_eks.sh"; cp "$V3B_LOC" "$w/impl/locate_results.sh" ;;
    v3a) cp "$V3A" "$w/impl/launch_eks.sh" ;;
  esac
  chmod +x "$w/impl/"*.sh
  local r="$w/checkout/taskq/deploy/eks-karpenter/remote" f
  cp "$here/fake-launch-remote" "$r/launch-remote"
  printf 'FAKE_CASE_DIR=%q\nFAKE_S3_ROOT=%q\n' "$fx" "$w/s3root" > "$r/fake-launch-remote.conf"
  printf '#!/usr/bin/env bash\ncat "$1"\n' > "$r/validate-request"
  echo '#!/usr/bin/env bash' > "$r/run-request"; echo 'version: 0.2' > "$r/current-run-request-buildspec.yml"
  chmod +x "$r/launch-remote" "$r/validate-request" "$r/run-request"
  : > "$w/impl/remote-pins.sha256"
  for f in launch-remote validate-request run-request current-run-request-buildspec.yml; do
    printf '%s  %s\n' "$(sha256sum "$r/$f" | cut -d ' ' -f1)" "$f" >> "$w/impl/remote-pins.sha256"
  done
  : > "$w/aws.log"; mk_bin "$w/bin" "$w/s3root" "$w/aws.log"
  printf '{"run_id":"RUN-TEST","trial_id":"T1"}\n' > "$w/rec/launch.json"
  W_RC=0
  env PATH="$w/bin:/usr/bin:/bin" HOME="$w/home" TMPDIR="$w" AWS_REGION=us-east-2 \
    ISOLAB_BUCKET="$BUCKET" ISOLAB_CODEBUILD_PROJECT=isolab-experiment-launcher CRYPTO_CHECKOUT="$w/checkout" \
    bash "$w/impl/launch_eks.sh" --protocol "$PROTO" --experiment-id EXP-TEST --hypothesis-id H-TEST --task-id TASK-TEST \
    --approved-by DEC-TEST --trial-id T1 --run-id RUN-TEST --out "$w/rec/job" --record-dir "$w/rec" "$REQ" \
    > "$w/stdout" 2> "$w/stderr" || W_RC=$?
  W_DIR=$w
  W_CLASS=$(jq -r '.outcome_class // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_LOC=$(jq -r '.results_locator // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_POD=$(jq -r '.pod_uid // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
}

run_reconcile() { # run_reconcile ID [sha] [outsub] [tag] [pin_status] [pin_objects] : sets R_RC, R_PASS, R_DIR (cases/ID/reconcileTAG)
  local id=$1 sha=${2:-$REAL_RESULT_SHA} outsub=${3:-out} tag=${4:-}; local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/reconcile$tag"
  local rcdir="$fx/s3/runs/$JOB/launcher/$LAUNCHER_ID"
  local ps=${5:-$(sha256sum "$rcdir/status.json" 2>/dev/null | cut -d ' ' -f1)} po=${6:-$(sha256sum "$rcdir/objects.json" 2>/dev/null | cut -d ' ' -f1)}
  [[ -n $ps ]] || ps=0000000000000000000000000000000000000000000000000000000000000000
  rm -rf "$w"; mkdir -p "$w/s3root" "$w/home" "$w/$outsub"
  cp -a "$fx/s3/." "$w/s3root/"; : > "$w/aws.log"; mk_bin "$w/bin" "$w/s3root" "$w/aws.log"
  R_RC=0
  env PATH="$w/bin:/usr/bin:/bin" HOME="$w/home" TMPDIR="$w" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" \
    bash "$IMPL/reconcile_run.sh" --launcher-result "$fx/launcher/result.json" --launcher-result-sha256 "$sha" --request "$REQ" \
    --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/$outsub" --out-root "$w" \
    --pin-status-sha256 "$ps" --pin-objects-sha256 "$po" --pin-not-after "$PIN_NA" > "$w/stdout" 2> "$w/stderr" || R_RC=$?
  R_DIR=$w
  R_PASS=$(jq -r 'if has("reconcile_pass") then (.reconcile_pass | tostring) else "absent" end' "$w/$outsub/reconcile-result.json" 2>/dev/null || echo absent)
}

say "== C1 locator / v3c / reconcile fixture tests, $(date -u +%FT%TZ); outputs in $OUT"
say "== real receipt fixtures: $(cd "$RCPT" && sha256sum status.json result.json objects.json | tr '\n' ';')"
expect fixtures "real result.json sha256 equals the receipt binding" "$REAL_RESULT_SHA" "$(sha256sum "$RCPT/result.json" | cut -d ' ' -f1)"
expect fixtures "real status.json sha256 equals the K-2 pin (E-3)" "$REAL_STATUS_SHA" "$(sha256sum "$RCPT/status.json" | cut -d ' ' -f1)"
expect fixtures "real objects.json sha256 equals the K-2 pin (E-3)" "$REAL_OBJECTS_SHA" "$(sha256sum "$RCPT/objects.json" | cut -d ' ' -f1)"
say "== planned executions per fixture session: $planned"

say "== wrapper v3c / v3a, positive cases"
build_case P1
run_wrapper P1 v3c
expect P1-wrapper-v3c "T1 real receipt shape + job-exit 42: exit status" 0 "$W_RC"
expect P1-wrapper-v3c "outcome_class" job_completed "$W_CLASS"
expect P1-wrapper-v3c "results_locator" receipt_status_pod_uid "$W_LOC"
expect P1-wrapper-v3c "pod_uid recorded" "$REAL_POD" "$W_POD"
expect P1-wrapper-v3c "job_uid recorded" 8a20d036-efc2-45d2-ada6-6442b93c5a52 "$(jq -r .job_uid "$W_DIR/rec/raw-result.json")"
expect P1-wrapper-v3c "objects_match recorded true" true "$(jq -r .objects_match "$W_DIR/rec/raw-result.json")"
expect P1-wrapper-v3c "download_exit recorded 0" 0 "$(jq -r .download_exit "$W_DIR/rec/raw-result.json")"
expect P1-wrapper-v3c "the k7 environment line is printed" 1 "$(grep -c '^k7_env_hygiene=ok ' "$W_DIR/stdout")"
expect P1-wrapper-v3c "no S3 write attempted (no fake-aws refusal in the log)" 0 "$(grep -c 'REFUSED' "$W_DIR/stderr" "$W_DIR/stdout" | awk -F: '{s+=$2} END {print s+0}')"
expect P1-wrapper-v3c "every aws call is a read (version, cp from s3, ls, list-objects-v2, codebuild list)" 0 \
  "$(grep -v -E '^aws (--version|s3 cp s3://[^ ]+ [^ ]+|s3 ls s3://[^ ]+|s3api list-objects-v2 --bucket [^ ]+ --prefix [^ ]+ --output json|codebuild list-builds-for-project )' "$W_DIR/aws.log" | grep -c . || true)"
run_wrapper P1 v3a
expect P1-wrapper-v3a "same fixture on v3a reproduces the defect: exit status" 5 "$W_RC"
expect P1-wrapper-v3a "outcome_class" infrastructure_candidate "$W_CLASS"

build_case P2 shape=succeeded je_exit=0 cexit=0
run_wrapper P2 v3c
expect P2-wrapper-v3c "succeeded Job, non-empty results_uri equal to the located prefix: exit status" 0 "$W_RC"
expect P2-wrapper-v3c "outcome_class" job_completed "$W_CLASS"
expect P2-wrapper-v3c "results_locator (one rule for every outcome)" receipt_status_pod_uid "$W_LOC"
expect P2-wrapper-v3c "the receipt is read even though results_uri is non-empty (K-1)" 1 "$(grep -c 'launcher/' "$W_DIR/aws.log" | awk '{print ($1 >= 1) ? 1 : 0}')"
jq -S 'del(.started_at, .finished_at, .results_locator, .job_uid, .pod_uid, .objects_match, .objects_check, .locate_exit, .parse_failures, .job_files["locator/locator.json"], .job_files["locator/status.json"], .job_files["locator/objects.json"])' "$W_DIR/rec/raw-result.json" > "$OUT/cases/P2/raw-v3c.norm.json"
cp "$W_DIR/rec/manifest.yaml" "$OUT/cases/P2/manifest-v3c.yaml"
run_wrapper P2 v3b
expect P2-wrapper-v3b "succeeded Job on the v3b fixture: exit status" 0 "$W_RC"
expect P2-wrapper-v3b "outcome_class" job_completed "$W_CLASS"
jq -S 'del(.started_at, .finished_at, .results_locator, .job_uid, .pod_uid, .job_files["locator/locator.json"])' "$W_DIR/rec/raw-result.json" > "$OUT/cases/P2/raw-v3b.norm.json"
expect P2-wrapper "v3b and v3c raw-result.json equal apart from timestamps, the new fields and the locator inventory entries" \
  "$(sha256sum < "$OUT/cases/P2/raw-v3b.norm.json")" "$(sha256sum < "$OUT/cases/P2/raw-v3c.norm.json")"
expect P2-wrapper "manifest.yaml byte-identical between the v3b fixture and v3c" "$(sha256sum < "$W_DIR/rec/manifest.yaml")" "$(sha256sum < "$OUT/cases/P2/manifest-v3c.yaml")"

say "== wrapper v3c, negative cases (none may give job_completed; exit status 5 expected)"
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
  run_wrapper "$nid" v3c
  expect "$nid-wrapper-v3c" "exit status" 5 "$W_RC"
  expect "$nid-wrapper-v3c" "outcome_class (not job_completed)" "$nclass" "$W_CLASS"
done

say "== reconcile_run.sh, positive cases"
run_reconcile P1
expect P1-reconcile "T1 real receipt shape: exit status" 0 "$R_RC"
expect P1-reconcile "reconcile_pass" true "$R_PASS"
expect P1-reconcile "run_id" RUN-ICPERF-8b0d47 "$(jq -r .run_id "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "trial_id" T1 "$(jq -r .trial_id "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "pod_uid" "$REAL_POD" "$(jq -r .pod_uid "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "check_job_exit" 0 "$(jq -r .check_job_exit "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "objects_match" true "$(jq -r .objects_match "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "receipt_pins_outcome" pass "$(jq -r .receipt_pins_outcome "$R_DIR/out/reconcile-result.json")"
expect P1-reconcile "check_job last line" CHECK_JOB_OK "$(tail -n 1 "$R_DIR/out/check_job.stdout")"
expect P1-reconcile "every aws call is a read" 0 \
  "$(grep -v -E '^aws (--version|s3 cp s3://[^ ]+ [^ ]+( --recursive)?( --only-show-errors)?|s3 ls s3://[^ ]+|s3api list-objects-v2 --bucket [^ ]+ --prefix [^ ]+ --output json)' "$R_DIR/aws.log" | grep -c . || true)"
expect P1-reconcile "no S3 write attempted" 0 "$(grep -c 'REFUSED' "$R_DIR/stderr" || true)"
# the real receipt hashes (E-3) pass the pin check; the synthetic pod objects then differ from the real objects.json, so the run stops later
rm -rf "$OUT/cases/P1R"; mkdir -p "$OUT/cases/P1R"; cp -a "$OUT/cases/P1/fx" "$OUT/cases/P1R/fx"
cp "$RCPT/status.json" "$RCPT/objects.json" "$OUT/cases/P1R/fx/s3/runs/$JOB/launcher/$LAUNCHER_ID/"
find "$OUT/cases/P1R/fx/s3" -exec touch -d '2026-11-07T02:14:21Z' {} +
run_reconcile P1R "$REAL_RESULT_SHA" out "" "$REAL_STATUS_SHA" "$REAL_OBJECTS_SHA"
expect P1R-reconcile "real status.json and objects.json bytes: the pins pass and the real listing differs (stops at R-3, exit 5)" 5 "$R_RC"
expect P1R-reconcile "locator exit 22 (listing differs), not 23 (pin)" "locate_results exit 22" "$(grep -o 'locate_results exit [0-9]*' "$R_DIR/stdout")"

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
run_reconcile N13-run-summary-unlisted "$(sha256sum "$OUT/cases/N13-run-summary-unlisted/fx/launcher/result.json" | cut -d ' ' -f1)"
expect N13-run-summary-unlisted-reconcile "exit status" 9 "$R_RC"; expect N13-run-summary-unlisted-reconcile "reconcile_pass" false "$R_PASS"
build_case N19-file-hash-mismatch tamper=1
run_reconcile N19-file-hash-mismatch "$(sha256sum "$OUT/cases/N19-file-hash-mismatch/fx/launcher/result.json" | cut -d ' ' -f1)"
expect N19-file-hash-mismatch-reconcile "a listed file differs from SHA256SUMS (check_job.py sums FAIL): exit status" 8 "$R_RC"; expect N19-file-hash-mismatch-reconcile "reconcile_pass" false "$R_PASS"
build_case N14-run-summary-other-digest rsum=nonempty
run_reconcile N14-run-summary-other-digest "$(sha256sum "$OUT/cases/N14-run-summary-other-digest/fx/launcher/result.json" | cut -d ' ' -f1)"
expect N14-run-summary-other-digest-reconcile "exit status" 9 "$R_RC"; expect N14-run-summary-other-digest-reconcile "reconcile_pass" false "$R_PASS"
expect N14-run-summary-other-digest-reconcile "listed digest is not the empty-file digest" "yes" \
  "$([[ $(jq -r .run_summary_listed_sha256 "$R_DIR/out/reconcile-result.json") != "$EMPTY_SHA" ]] && echo yes || echo no)"
run_reconcile P1 0000000000000000000000000000000000000000000000000000000000000000 out -wrongsha
expect R1-wrong-receipt-sha256-reconcile "exit status" 3 "$R_RC"; expect R1-wrong-receipt-sha256-reconcile "reconcile_pass" false "$R_PASS"
build_case N15-succeeded-shape shape=succeeded je_exit=0 cexit=0
run_reconcile N15-succeeded-shape "$(sha256sum "$OUT/cases/N15-succeeded-shape/fx/launcher/result.json" | cut -d ' ' -f1)"
expect N15-launcher-result-locator-reconcile "T1's result.json names no results_uri: exit status" 4 "$R_RC"; expect N15-launcher-result-locator-reconcile "reconcile_pass" false "$R_PASS"
run_reconcile P1 "$REAL_RESULT_SHA" out/runs/x -outinruns
expect N16-out-inside-runs-reconcile "exit status" 2 "$R_RC"
expect N16-out-inside-runs-reconcile "nothing written" 0 "$(find "$R_DIR/out/runs/x" -type f 2>/dev/null | wc -l)"
run_reconcile P1 "$REAL_RESULT_SHA" out "" 0000000000000000000000000000000000000000000000000000000000000000 "$(sha256sum "$OUT/cases/P1/fx/s3/runs/$JOB/launcher/$LAUNCHER_ID/objects.json" | cut -d ' ' -f1)"
expect R2-wrong-status-pin-reconcile "exit status" 10 "$R_RC"; expect R2-wrong-status-pin-reconcile "receipt_pins_outcome" fail "$(jq -r .receipt_pins_outcome "$R_DIR/out/reconcile-result.json")"

say "== static checks"
for f in launch_eks.sh locate_results.sh reconcile_run.sh tests/test_locator.sh tests/rt_regression.sh tests/mutation_check.sh tests/fake-aws tests/fake-launch-remote; do
  bash -n "$IMPL/$f"; expect "bash -n $f" "syntax" 0 "$?"
done
nc() { grep -v '^[[:space:]]*#' "$1"; } # non-comment lines
forbidden='launch-remote|codebuild|start-build|batch-get-builds|put-object|delete-object|s3 (rm|mv|sync|mb|rb|presign)'
for f in locate_results.sh reconcile_run.sh; do
  expect "grep $f" "no job-submission, build-start or S3-write token in non-comment lines (case-insensitive)" 0 "$(nc "$IMPL/$f" | grep -c -i -E "$forbidden" || true)"
done
expect "grep locate_results.sh" "the only s3api use is the list-objects-v2 helper line" 1 "$(nc "$IMPL/locate_results.sh" | grep -c 's3api' || true)"
expect "grep reconcile_run.sh" "no s3api token" 0 "$(nc "$IMPL/reconcile_run.sh" | grep -c 's3api' || true)"
cpl='aws s3 cp "$1" "$2" "${@:3}" --only-show-errors'; lsl='aws s3 ls "$1"'; lol='aws s3api list-objects-v2 --bucket "$1" --prefix "$2" --output json'
aws_cmds() { nc "$1" | grep -E '(^|[;&|(]|[$][(]|[{])[[:space:]]*aws[[:space:]]' | sed 's/^[[:space:]]*//' | tr '\n' '|' | sed 's/|$//'; }
expect "grep locate_results.sh" "outside comments, the only aws invocations are the cp, ls and list-objects-v2 helpers (read-only)" "$cpl|$lsl|$lol" "$(aws_cmds "$IMPL/locate_results.sh")"
expect "grep reconcile_run.sh" "outside comments, the only aws invocation is the cp helper (read-only)" "$cpl" "$(aws_cmds "$IMPL/reconcile_run.sh")"
expect "grep locate_results.sh,reconcile_run.sh" "both helpers refuse a destination that is an S3 URI" 2 \
  "$(grep -c -F '[[ $1 == s3://* && $2 != s3://* ]]' "$IMPL/locate_results.sh" "$IMPL/reconcile_run.sh" | awk -F: '{s+=$2} END {print s}')"
expect "k7" "the prologue carries the pinned aws-cli version 1.46.2" 2 "$(grep -c -F 'K7_PIN_AWS_CLI=aws-cli/1.46.2' "$IMPL/launch_eks.sh" "$IMPL/reconcile_run.sh" | awk -F: '{s+=$2} END {print s}')"
expect "k7" "the two prologues differ only in the ISOLAB_CODEBUILD_PROJECT pass-through name" 1 \
  "$(diff <(sed -n '/^# ---- K-7 environment prologue/,/^# ---- end of the K-7 prologue/p' "$IMPL/launch_eks.sh") <(sed -n '/^# ---- K-7 environment prologue/,/^# ---- end of the K-7 prologue/p' "$IMPL/reconcile_run.sh") | grep -c '^[<>]' | awk '{print ($1 == 2) ? 1 : 0}')"
# v3b -> v3c: only the K-7 prologue and section 3 (with the K-5 handler) change; sections 1, 1b, 1c, 2, the 42/43 pairing and the manifests do not
expect "v3b-v3c diff" "v3b fixture sha256 is the reviewed f93e8858..." f93e8858923765c390fb7bcb01ea04c2373325815f08cbaf7df24b584e521da8 "$(sha256sum "$V3B" | cut -d ' ' -f1)"
expect "v3b-v3c diff" "lines 1-32 (header, set -euo pipefail, set +x) byte-identical" "" "$(diff <(head -n 32 "$V3B") <(head -n 32 "$IMPL/launch_eks.sh") | head -n 3)"
expect "v3b-v3c diff" "v3b lines 34-233 (sections 1, 1b, 1c, 2, write_records, both manifests, refuse, duplicate checks, the launch-remote exit line) byte-identical" "" \
  "$(diff <(sed -n '34,233p' "$V3B") <(sed -n '/^dry=0; protocol=/,/^echo "launch-remote exit /p' "$IMPL/launch_eks.sh") | head -n 3)"
blk() { sed -n '/^# Outcome class\./,/^fi$/p' "$1"; }
expect "v3b-v3c diff" "outcome-class block (deadline first, 42/43 accept branch) byte-identical" "" "$(diff <(blk "$V3B") <(blk "$IMPL/launch_eks.sh") | head -n 3)"
expect "v3b-v3c diff" "outcome-class block is non-empty" yes "$([[ $(blk "$V3B" | wc -l) -ge 12 ]] && echo yes || echo no)"
expect "v3b-v3c diff" "final exit lines identical" "" "$(diff <(tail -n 3 "$V3B") <(tail -n 3 "$IMPL/launch_eks.sh") | head -n 3)"
diff -u "$V3B" "$IMPL/launch_eks.sh" > "$OUT/launch_eks.v3b-to-v3c.diff"; diff -u "$V3A" "$IMPL/launch_eks.sh" > "$OUT/launch_eks.v3a-to-v3c.diff"
grep -n '^@@' "$OUT/launch_eks.v3b-to-v3c.diff" > "$OUT/launch_eks.v3b-to-v3c.hunks.txt"; grep -n '^@@' "$OUT/launch_eks.v3a-to-v3c.diff" > "$OUT/launch_eks.v3a-to-v3c.hunks.txt"
say "== hunk list v3b to v3c (v3b line ranges): $(sed 's/^[0-9]*://' "$OUT/launch_eks.v3b-to-v3c.hunks.txt" | tr '\n' ';')"
say "== hunk list v3a to v3c (v3a line ranges): $(sed 's/^[0-9]*://' "$OUT/launch_eks.v3a-to-v3c.hunks.txt" | tr '\n' ';')"
expect "v3b-v3c diff" "exactly three hunks (prologue; section 3 up to the class block; the lines after the class block)" 3 "$(wc -l < "$OUT/launch_eks.v3b-to-v3c.hunks.txt")"
expect "v3b-v3c diff" "the first hunk starts after v3b line 32 (the prologue)" yes "$(head -n 1 "$OUT/launch_eks.v3b-to-v3c.hunks.txt" | sed -E 's/^[0-9]+:@@ -([0-9]+).*/\1/' | awk '{print ($1 >= 30 && $1 <= 33) ? "yes" : "no"}')"
expect "v3b-v3c diff" "the second hunk starts in section 3 (v3b line >= 232)" yes "$(sed -n 2p "$OUT/launch_eks.v3b-to-v3c.hunks.txt" | sed -E 's/^[0-9]+:@@ -([0-9]+).*/\1/' | awk '{print ($1 >= 232) ? "yes" : "no"}')"

say "== --dry-run of v3c (no AWS call)"
if [[ -n $REAL_CHECKOUT && -d $REAL_CHECKOUT ]]; then
  w="$OUT/dryrun"; rm -rf "$w"; mkdir -p "$w/bin" "$w/rec" "$w/s3root" "$w/home"; : > "$w/aws.log"; mk_bin "$w/bin" "$w/s3root" "$w/aws.log"
  drc=0
  env PATH="$w/bin:/usr/bin:/bin" HOME="$w/home" AWS_REGION=us-east-2 ISOLAB_BUCKET="$BUCKET" \
    ISOLAB_CODEBUILD_PROJECT=isolab-experiment-launcher CRYPTO_CHECKOUT="$REAL_CHECKOUT" \
    bash "$IMPL/launch_eks.sh" --dry-run --protocol "$PROTO" --experiment-id EXP-TEST --hypothesis-id H-TEST --task-id TASK-TEST \
    --approved-by DEC-TEST --trial-id T2 --run-id RUN-TEST --out "$w/rec/job" --record-dir "$w/rec" "$EXP/inputs/request-s2.json" \
    > "$w/stdout" 2> "$w/stderr" || drc=$?
  expect dry-run "exit status" 0 "$drc"
  expect dry-run "aws calls made other than --version (fake-aws log lines)" 0 "$(grep -v '^aws --version$' "$w/aws.log" | grep -c . || true)"
  expect dry-run "prints the DRY RUN banner" 1 "$(grep -c '^DRY RUN: no AWS call is made' "$w/stdout")"
  expect dry-run "remote scripts match 4 pinned values" 1 "$(grep -c '^remote scripts match 4 pinned sha256 values' "$w/stdout")"
else
  expect dry-run "REAL_CHECKOUT argument names a directory (no skip is allowed)" yes "no"
fi

say "== SUMMARY $npass pass, $nfail fail"
[[ $nfail == 0 ]]
