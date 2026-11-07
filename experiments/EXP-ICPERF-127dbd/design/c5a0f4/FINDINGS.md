# FINDINGS: TASK-20261107-c5a0f4 (experiment-director design for the C1 S2 re-session of EXP-ICPERF-127dbd)

Author: experiment-director (Sonnet 5.5), 2026-11-07. Zero runs, zero launches. Observations and previews only: no verdict, ratio or S1 content is in this file or was read.
Everything below that is a number was copied from the named tool output in `evidence/`.

## 1. Ids (allocator-checked with `tools/allocate_id.py --check`, "free across the union")

| what | id |
|---|---|
| new runbook session id | `RBS-ICPERF-616277` (random 6-hex token; `RBS-` is not in the allocator's prefix table, so the token was checked by grep only: no match under ledger/, coordination/, experiments/, docs/session-logs/, nor in the file names of origin/main) |
| S2 run id (fresh; `RUN-ICPERF-5ffa79` stays retired) | `RUN-ICPERF-efb7ef` |
| new executor task / snapshot task | `TASK-20261107-f14df8` / `TASK-20261107-04d969` |
| reserved approval decision (not a record) | `DEC-20261107-7802ec` |
| new card | `CARD-EXP-ICPERF-127dbd-3` |
| new trial id in the plan | `T2` (= S2; T1 is not a trial of the plan, it is the reconciliation of `RUN-ICPERF-8b0d47`) |
| protocol version / new `protocol_sha256` | version 3 / `4b7bf35f34c0ddf5c0e4bee95e1791e6f5d2bc2fb68d4836db9db53d33e9b9cc` (v2 `9844f78d...`, v1 `43b1ca91...` reproduce from the v3 file: `evidence/amendment-2-receipts.txt`) |
| `AMENDMENT-2.md` sha256 | `8fdc60321fb3f3f3741c2a21f65d50f42d563ed065663528d786ca4056393b19` |
| runbook sha256 | `488ae3acfd6378bd3351cad7081649db4c5f0b01a09d80979586c5edad156ece` (`runbook-lint.txt`: `LINT OK experiments/EXP-ICPERF-127dbd/runbook.yaml sha256 488ae3acfd6378bd3351cad7081649db4c5f0b01a09d80979586c5edad156ece`) |

(The token `f14df8` also occurs once, inside a git object hash, in `ledger/archives/TASK-20260917-0ef594.yaml`; it is not an id there, and `--check` reports the task id free.)

## 2. Files and sha256 (all copied from `sha256sum`; the full list is `SHA256SUMS`)

| file | sha256 |
|---|---|
| implementation/launch_eks.sh (v3b; v3a was `0fcdd67e...`) | `f93e8858923765c390fb7bcb01ea04c2373325815f08cbaf7df24b584e521da8` |
| implementation/locate_results.sh (new) | `efcc29832806d604913c00afb6e92a2052cb784479cfc65dda42491655326c5e` |
| implementation/reconcile_run.sh (new) | `eac18f21de151b55b543e7ebdf51aeda71a23061ae2f8f5449a5064af569bb93` |
| implementation/tests/test_locator.sh (new) | `2530c5e4b38ba453677f4e17fd7ccb7ec50b77474473066bc6128ac4a20ab715` |
| implementation/tests/fake-aws, fake-launch-remote (new) | `5f34a06affbb31a168015b4ab1410633aedb0d020584af3e318ef7d0f39315f2`, `21c07fc064249901a59ddebde9f4adfa334b9def5f2bd2e0127af2fdff0ef51d` |
| implementation/tests/fixtures/launch_eks.v3a.sh (v3a copy, for the A/B cases) | `0fcdd67e22f6105c36883bf9ba7edb62e512e6ff135979e0b63084fb2c9b7dc0` |
| inputs/protocol.json (byte-identical to crypto `protocol.json`) | `561b6a75247a52d7a99f0c636fcef42eb038fc1e7844d78f002c55d8767ca05d` |
| specification.yaml (revision 2) | `097462e3137770d6d1e69ba4e23ae7213a7dca0db3ccfcd1a347638abeb408e5` |
| trial-plan.json | `3f564ea2ad00f25aa0efd1c35ccbf164f8f7ef542c7b64a5dd209860796117f8` |
| runbook.yaml | `488ae3acfd6378bd3351cad7081649db4c5f0b01a09d80979586c5edad156ece` |
| task-cards/CARD-EXP-ICPERF-127dbd-3.yaml | `e55ebc137b0f22a3bf1aa6b3f9bc4e139960cbfdd3111bf6488902cae8f8dd1c` |
| design/c5a0f4/handoff-previews/TASK-20261107-f14df8.yaml (executor) | `1f68de074793672a57b69ca32c9094542a7f96344e4788560c7e1c96f6f7adac` |
| design/c5a0f4/handoff-previews/TASK-20261107-04d969.yaml (snapshot) | `ce0050d0f061436bcd057365078784bb95fe2cbd4d5563e0a3c76f798bcb32ab` |
| design/c5a0f4/handoff-previews/dispatch_queue.json (existing queue + the two tasks) | `8dbfbae8ddd55e843968add3317509536887d89b0c43d343bcbcf7f798ff328e` |
| crypto: AMENDMENT-2.md / protocol.json / amendment-2-receipts.txt | `8fdc60321fb3f3f3741c2a21f65d50f42d563ed065663528d786ca4056393b19` / `561b6a75247a52d7a99f0c636fcef42eb038fc1e7844d78f002c55d8767ca05d` / `49a230f375d052bcd94bf73c8aa56956178c9fbd27e5ed940d8b88a368cfde86` |

Unchanged and re-checked (evidence/binding-consistency.txt, 37 OK, ALL OK): check_job.py `d60564dd...`, analyze-c1.sh `66aa2ffd...`, probe_s01.sh `3d1826e4...`, remote-pins.sha256 `7b753189...`, request-s1/s2.json, spec-c1-s1/s2.json.

## 3. D-1 receipt copy (read-only; the only AWS call made)

`aws s3 cp s3://isolab-results-104186811093-us-east-2/runs/ic-c1-dg-s1-20261106/launcher/47cf1e4f-10a7-4ee3-862d-9e9700e122e3/{status.json,result.json,objects.json}` into a new empty directory, with `PATH=/tmp/claude-0/awsvenv/bin:$PATH AWS_REGION=us-east-2` (exit 0 for each):

| object | sha256 |
|---|---|
| status.json | `a2642563d10a8f80661cef79a759b892d44fad49057a409ae03a1bee3a960ae0` |
| result.json | `7c3d9954a561a7a0d07e498afe3ecdf5b8c53359cfa28abb578a67dc8a6d60e7` (equals the committed `runs/RUN-ICPERF-8b0d47/job/launcher/result.json` and the receipt binding) |
| objects.json | `783ea0e3ec77daf52d3ff815cb096295a3db76fe05b5cc9b1884c001126504d7` |

The dispatch also listed three saved copies under `scratchpad/dl-8b0d47-receipt/` while handoff D-1 says not to use that directory. Both were honoured by taking a fresh copy and comparing: the saved copies have the same three sha256 values; the fixtures use the fresh copy (`implementation/tests/fixtures/receipt/`). Nothing under the pod-uid S3 prefix was read, and no `aws` call other than these three was made (the fixtures use `tests/fake-aws`).

## 4. D-5 fixture tests (`implementation/tests/test_locator.sh`, no AWS call)

Output: `evidence/fixture-test-output.txt`; per-case outputs: `evidence/fixture-run/` (`README.txt` says what was left out). **117 pass, 0 fail.**

Positive cases (the first two named in D-5):
- P1: T1's real receipt shape (`state failed`, `exit_code 23`, empty `pod_uid` and `results_uri`, the real `result.json` and `status.json`) with a synthetic job-exit 42: v3b gives `job_completed`, exit 0, `results_locator receipt_status_pod_uid`, `pod_uid 5885ba61-...`; the same fixture on v3a gives `infrastructure_candidate`, exit 5 (the defect, reproduced). `reconcile_run.sh` passes (exit 0, `reconcile_pass true`, `check_job.py` last line `CHECK_JOB_OK`).
- P2: a succeeded-Job receipt with a non-empty `results_uri`: v3a and v3b both give `job_completed`, exit 0; `raw-result.json` and `manifest.yaml` equal apart from timestamps, the three new fields and the `locator/locator.json` inventory entry; no receipt object is read.

Negative cases (each gives exit 5 and never `job_completed` from the wrapper, and never `reconcile_pass true` from `reconcile_run.sh`): 0 pods; 2 pods; status `job.uid` != `job_uid`; an extra pod prefix under `runs/JOB/`; job-exit `pod_uid` mismatch; job-exit `job_name` mismatch; container `exitCode` 42 != job-exit 43; missing receipt (`status.json` absent); empty `SHA256SUMS`; `run-summary.json` unlisted; `run-summary.json` listed at a digest other than `e3b0c442...` (non-empty file, consistent sums, so `check_job.py` alone would pass it); plus launcher `result.json` job_name mismatch, status `job.job_name` mismatch, status `job.state` not `failed`, two container statuses, container not terminated, a listed file changed after `SHA256SUMS` (`check_job.py` sums FAIL), a wrong receipt sha256 (R-1), a succeeded-shape result given to the reconciler, and `--out` under a `runs/` directory (refused, nothing written).

The two `run-summary.json` cases and the changed-file case concern `SHA256SUMS`, which the wrapper never judges (`check_job.py` does, unchanged), so they are reconcile cases only.

Case table (full text, with the complete values, in `evidence/fixture-run/RESULTS.txt`):

| result | case | check | expected | observed |
|---|---|---|---|---|
| PASS | fixtures | real result.json sha256 equals the receipt binding | `7c3d9954a561a7a0d07e...67dc8a6d60e7` | `7c3d9954a561a7a0d07e...67dc8a6d60e7` |
| PASS | P1-wrapper-v3b | T1 real receipt shape + job-exit 42: exit status | `0` | `0` |
| PASS | P1-wrapper-v3b | outcome_class | `job_completed` | `job_completed` |
| PASS | P1-wrapper-v3b | results_locator | `receipt_status_pod_uid` | `receipt_status_pod_uid` |
| PASS | P1-wrapper-v3b | pod_uid recorded | `5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7` | `5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7` |
| PASS | P1-wrapper-v3b | job_uid recorded | `8a20d036-efc2-45d2-ada6-6442b93c5a52` | `8a20d036-efc2-45d2-ada6-6442b93c5a52` |
| PASS | P1-wrapper-v3b | no S3 write attempted (no fake-aws refusal in the log) | `0` | `0` |
| PASS | P1-wrapper-v3b | every aws call is a read (cp from s3, ls, codebuild list) | `0` | `0` |
| PASS | P1-wrapper-v3a | same fixture on v3a reproduces the defect: exit status | `5` | `5` |
| PASS | P1-wrapper-v3a | outcome_class | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | P2-wrapper-v3b | succeeded Job, non-empty results_uri: exit status | `0` | `0` |
| PASS | P2-wrapper-v3b | outcome_class | `job_completed` | `job_completed` |
| PASS | P2-wrapper-v3b | results_locator | `launcher_result` | `launcher_result` |
| PASS | P2-wrapper-v3b | no receipt object read (rule (a) makes no AWS call of its own) | `0` | `0` |
| PASS | P2-wrapper-v3a | succeeded Job on v3a: exit status | `0` | `0` |
| PASS | P2-wrapper-v3a | outcome_class | `job_completed` | `job_completed` |
| PASS | P2-wrapper | v3a and v3b raw-result.json equal apart from timestamps, the three new fields and the locator/locator.json inventory entry | `f930091ac6498799f0ee...bbd09638f  -` | `f930091ac6498799f0ee...bbd09638f  -` |
| PASS | P2-wrapper | manifest.yaml byte-identical between v3a and v3b | `66fd9c888676189ef457...c77547241  -` | `66fd9c888676189ef457...c77547241  -` |
| PASS | N1-0pods-wrapper-v3b | exit status | `5` | `5` |
| PASS | N1-0pods-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N2-2pods-wrapper-v3b | exit status | `5` | `5` |
| PASS | N2-2pods-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N3-status-job-uid-wrapper-v3b | exit status | `5` | `5` |
| PASS | N3-status-job-uid-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N4-extra-pod-prefix-wrapper-v3b | exit status | `5` | `5` |
| PASS | N4-extra-pod-prefix-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N5-jobexit-pod-uid-wrapper-v3b | exit status | `5` | `5` |
| PASS | N5-jobexit-pod-uid-wrapper-v3b | outcome_class (not job_completed) | `other` | `other` |
| PASS | N6-jobexit-job-name-wrapper-v3b | exit status | `5` | `5` |
| PASS | N6-jobexit-job-name-wrapper-v3b | outcome_class (not job_completed) | `other` | `other` |
| PASS | N7-container-exit-ne-jobexit-wrapper-v3b | exit status | `5` | `5` |
| PASS | N7-container-exit-ne-jobexit-wrapper-v3b | outcome_class (not job_completed) | `other` | `other` |
| PASS | N8-missing-receipt-wrapper-v3b | exit status | `5` | `5` |
| PASS | N8-missing-receipt-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N9-empty-sha256sums-wrapper-v3b | exit status | `5` | `5` |
| PASS | N9-empty-sha256sums-wrapper-v3b | outcome_class (not job_completed) | `other` | `other` |
| PASS | N10-result-job-name-wrapper-v3b | exit status | `5` | `5` |
| PASS | N10-result-job-name-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N11-status-job-name-wrapper-v3b | exit status | `5` | `5` |
| PASS | N11-status-job-name-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N12-status-job-not-failed-wrapper-v3b | exit status | `5` | `5` |
| PASS | N12-status-job-not-failed-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N17-two-container-statuses-wrapper-v3b | exit status | `5` | `5` |
| PASS | N17-two-container-statuses-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | N18-container-not-terminated-wrapper-v3b | exit status | `5` | `5` |
| PASS | N18-container-not-terminated-wrapper-v3b | outcome_class (not job_completed) | `infrastructure_candidate` | `infrastructure_candidate` |
| PASS | P1-reconcile | T1 real receipt shape: exit status | `0` | `0` |
| PASS | P1-reconcile | reconcile_pass | `true` | `true` |
| PASS | P1-reconcile | run_id | `RUN-ICPERF-8b0d47` | `RUN-ICPERF-8b0d47` |
| PASS | P1-reconcile | trial_id | `T1` | `T1` |
| PASS | P1-reconcile | pod_uid | `5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7` | `5885ba61-53c2-4e2e-8a47-ff1ff04ee2e7` |
| PASS | P1-reconcile | check_job_exit | `0` | `0` |
| PASS | P1-reconcile | check_job last line | `CHECK_JOB_OK` | `CHECK_JOB_OK` |
| PASS | P1-reconcile | every aws call is a read | `0` | `0` |
| PASS | P1-reconcile | no S3 write attempted | `0` | `0` |
| PASS | N1-0pods-reconcile | exit status | `4` | `4` |
| PASS | N1-0pods-reconcile | reconcile_pass | `false` | `false` |
| PASS | N2-2pods-reconcile | exit status | `4` | `4` |
| PASS | N2-2pods-reconcile | reconcile_pass | `false` | `false` |
| PASS | N3-status-job-uid-reconcile | exit status | `4` | `4` |
| PASS | N3-status-job-uid-reconcile | reconcile_pass | `false` | `false` |
| PASS | N4-extra-pod-prefix-reconcile | exit status | `4` | `4` |
| PASS | N4-extra-pod-prefix-reconcile | reconcile_pass | `false` | `false` |
| PASS | N5-jobexit-pod-uid-reconcile | exit status | `7` | `7` |
| PASS | N5-jobexit-pod-uid-reconcile | reconcile_pass | `false` | `false` |
| PASS | N6-jobexit-job-name-reconcile | exit status | `7` | `7` |
| PASS | N6-jobexit-job-name-reconcile | reconcile_pass | `false` | `false` |
| PASS | N7-container-exit-ne-jobexit-reconcile | exit status | `7` | `7` |
| PASS | N7-container-exit-ne-jobexit-reconcile | reconcile_pass | `false` | `false` |
| PASS | N8-missing-receipt-reconcile | exit status | `4` | `4` |
| PASS | N8-missing-receipt-reconcile | reconcile_pass | `false` | `false` |
| PASS | N9-empty-sha256sums-reconcile | exit status | `9` | `9` |
| PASS | N9-empty-sha256sums-reconcile | reconcile_pass | `false` | `false` |
| PASS | N10-result-job-name-reconcile | exit status | `3` | `3` |
| PASS | N10-result-job-name-reconcile | reconcile_pass | `false` | `false` |
| PASS | N11-status-job-name-reconcile | exit status | `4` | `4` |
| PASS | N11-status-job-name-reconcile | reconcile_pass | `false` | `false` |
| PASS | N12-status-job-not-failed-reconcile | exit status | `4` | `4` |
| PASS | N12-status-job-not-failed-reconcile | reconcile_pass | `false` | `false` |
| PASS | N17-two-container-statuses-reconcile | exit status | `4` | `4` |
| PASS | N17-two-container-statuses-reconcile | reconcile_pass | `false` | `false` |
| PASS | N18-container-not-terminated-reconcile | exit status | `4` | `4` |
| PASS | N18-container-not-terminated-reconcile | reconcile_pass | `false` | `false` |
| PASS | N13-run-summary-unlisted-reconcile | exit status | `9` | `9` |
| PASS | N13-run-summary-unlisted-reconcile | reconcile_pass | `false` | `false` |
| PASS | N19-file-hash-mismatch-reconcile | a listed file differs from SHA256SUMS (check_job.py sums FAIL): exit status | `8` | `8` |
| PASS | N19-file-hash-mismatch-reconcile | reconcile_pass | `false` | `false` |
| PASS | N14-run-summary-other-digest-reconcile | exit status | `9` | `9` |
| PASS | N14-run-summary-other-digest-reconcile | reconcile_pass | `false` | `false` |
| PASS | N14-run-summary-other-digest-reconcile | listed digest is not the empty-file digest | `yes` | `yes` |
| PASS | R1-wrong-receipt-sha256-reconcile | exit status | `3` | `3` |
| PASS | R1-wrong-receipt-sha256-reconcile | reconcile_pass | `false` | `false` |
| PASS | N15-launcher-result-locator-reconcile | T1 must be located by the receipt: exit status | `4` | `4` |
| PASS | N15-launcher-result-locator-reconcile | reconcile_pass | `false` | `false` |
| PASS | N16-out-inside-runs-reconcile | exit status | `2` | `2` |
| PASS | N16-out-inside-runs-reconcile | nothing written | `0` | `0` |
| PASS | bash -n launch_eks.sh | syntax | `0` | `0` |
| PASS | bash -n locate_results.sh | syntax | `0` | `0` |
| PASS | bash -n reconcile_run.sh | syntax | `0` | `0` |
| PASS | bash -n tests/test_locator.sh | syntax | `0` | `0` |
| PASS | bash -n tests/fake-aws | syntax | `0` | `0` |
| PASS | bash -n tests/fake-launch-remote | syntax | `0` | `0` |
| PASS | grep locate_results.sh | no job-submission, build-start or S3-write token (case-insensitive) | `0` | `0` |
| PASS | grep reconcile_run.sh | no job-submission, build-start or S3-write token (case-insensitive) | `0` | `0` |
| PASS | grep locate_results.sh | outside comments, the only aws invocations are the cp helper and the ls helper (read-only) | `aws s3 cp "$1" "$2" ...s s3 ls "$1"` | `aws s3 cp "$1" "$2" ...s s3 ls "$1"` |
| PASS | grep reconcile_run.sh | outside comments, the only aws invocation is the cp helper (read-only) | `aws s3 cp "$1" "$2" "${@:3}" --only-show-errors` | `aws s3 cp "$1" "$2" "${@:3}" --only-show-errors` |
| PASS | grep locate_results.sh,reconcile_run.sh | both helpers refuse a destination that is an S3 URI | `2` | `2` |
| PASS | v3a-v3b diff | v3a sha256 is the reviewed 0fcdd67e... | `0fcdd67e22f6105c3688...84fb2c9b7dc0` | `0fcdd67e22f6105c3688...84fb2c9b7dc0` |
| PASS | v3a-v3b diff | lines 1-234 (sections 1, 1b, 1c, 2, write_records, manifests) byte-identical | `` | `` |
| PASS | v3a-v3b diff | outcome-class block (deadline first, 42/43 accept branch) byte-identical | `` | `` |
| PASS | v3a-v3b diff | outcome-class block is non-empty | `yes` | `yes` |
| PASS | v3a-v3b diff | final exit lines identical | `` | `` |
| PASS | v3a-v3b diff | first changed line is in section 3 (v3a line >= 235) | `yes` | `yes` |
| PASS | dry-run | exit status | `0` | `0` |
| PASS | dry-run | aws calls made (fake-aws log lines) | `0` | `0` |
| PASS | dry-run | prints the DRY RUN banner | `1` | `1` |
| PASS | dry-run | remote scripts match 4 pinned values | `1` | `1` |

Static checks (in the same table and in separate files): `evidence/bash-n.txt` (bash -n OK for all scripts, py_compile OK for check_job.py); `evidence/grep-no-submit-no-s3-write.txt` (grep for `launch-remote|codebuild|start-build|batch-get-builds|s3api|put-object|delete-object|s3 (rm|mv|sync|mb|rb|presign)` in `reconcile_run.sh` and `locate_results.sh`: exit 1, no match; outside comments the only `aws` invocations are `aws s3 cp "$1" "$2" ... --only-show-errors` in both scripts and `aws s3 ls "$1"` in the locator, and both helpers refuse an S3 destination); `evidence/dry-run-plan-argv.txt` (the plan's T2 argv with `--dry-run`: exit 0, fake-aws log 0 calls, "remote scripts match 4 pinned sha256 values").

Mutation sensitivity: `evidence/mutation-sensitivity.txt` breaks one safeguard at a time in a scratch copy and re-runs the suite. Every safeguard whose refusal is not also made by another guard makes at least one case fail. Two guards report 0 failing checks because a second guard gives the same refusal (the integer check on the container exit code is also caught by `jq --argjson`; the empty-`SHA256SUMS` rule in `reconcile_run.sh` is also caught by the `run-summary.json` rule).

## 5. v3a to v3b

`evidence/launch_eks.v3a-to-v3b.diff` (`diff -u`), hunk list `evidence/launch_eks.v3a-to-v3b.hunks.txt`: `@@ -232,11 +232,29 @@`, `@@ -244,6 +262,14 @@`, `@@ -262,12 +288,16 @@` (v3a line numbers). The test asserts: v3a lines 1-234 (header, sections 1, 1b, 1c, 2, `write_records`, both manifests, `refuse`, the duplicate checks and the `launch-remote exit` line) are byte-identical; the outcome-class block (`# Outcome class.` to its `fi`, which holds the deadline-first rule and the 42/43 accept branch) is byte-identical; the last three lines (`echo outcome_class=...`, `exit 0` and `exit 5` logic) are byte-identical; the first changed line is v3a line 235 (section 3). Section 3 here includes its record call (`write_records` argument list, which gains `results_locator`, `job_uid`, `pod_uid`) and the tail echo, as in v3a.

What changed in section 3: (1) the results are located by `locate_results.sh locate`; (2) after the download and the `have_exit`/`have_sums` lines, `locate_results.sh verify` runs when the locator was `receipt_status_pod_uid` and `job-exit.json` is present; (3) after the unchanged class block one line vetoes `job_completed` to `other` when verify failed (a deadline_hit or infrastructure_candidate class is never overwritten); (4) `raw-result.json` gains `results_locator` (`none` when nothing was located), `job_uid`, `pod_uid`. The `--dry-run` banner is the unchanged v3a text and does not mention the locator, because the sections before 3 are byte-identical.

## 6. C1-AMENDMENT-2 (crypto repository, branch `claude/c1-amendment-2-20261107` from `origin/main` 151779ab97)

`evidence/amendment-2-receipts.txt`: `validate` before the freeze: `OK ... (0 finding(s))`, exit 0; the v2 hash and the v1 hash reproduce from the v3 file; `freeze ... --commit auto --filed-before-affected-data`: `protocol_sha256 4b7bf35f...`, commit `151779ab979469baaa168e1e88a4097227219084` (the base commit, so it does not move when the local commit is merged or rebased by someone else), `frozen_at 2026-11-07T02:54:43Z`, `filed_before_affected_data true`; `hash` equals `jq -r .freeze.protocol_sha256`; `validate` after the freeze: 0 findings; `PROTOCOL.md` unchanged (sha256 `d2dba321...`, empty `git diff --stat`). `inputs/protocol.json` is byte-identical to the crypto file (`cmp` and `binding-consistency.txt`).

## 7. Runbook, card, packet

- `evidence/runbook-lint-output.txt`: `LINT OK experiments/EXP-ICPERF-127dbd/runbook.yaml sha256 488ae3acfd6378bd3351cad7081649db4c5f0b01a09d80979586c5edad156ece` (run in a scratch layout whose queue path holds the preview queue; the lint reads the plan's queue and the canonical queue has no entry for `TASK-20261107-f14df8` until the approval archive, so in the real clone the lint prints exactly one finding: `S03-trial-s2: the plan's task TASK-20261107-f14df8 is not in .../dispatch_queue.json`).
- `evidence/card-lint-output.txt`: `CARD FAIL`, with exactly one finding: `no committed approval decision names this experiment and runbook_sha256 488ae3ac...` (the allowed finding). `evidence/card-prompt-simulated-approval.txt` shows the relay text and `CARD OK` in a scratch layout that holds a stand-in approval (not a record).
- `experiment_preapproval.py --packet` (`evidence/preapproval-packet.json`): in the real clone `approvable false`, 7 blockers, all about state and none about content (`evidence/preapproval-NOTE.txt`, `preapproval-output-real-clone.json`): the canonical specification is the approved-form preview and not a committed `review_required` draft, and the changed bound files are not at `origin/main`. In a scratch layout that simulates the pushed state with a `review_required` canonical draft, `approvable true`, 0 blockers (`preapproval-output-simulated-pushed.json`; a simulation, not a claim).

## 8. Design choices a reviewer should check (values the specification did not give, or checks I added)

1. **S03-trial-s2 `timeout_seconds` 5100 and `claim.ttl_minutes` 90.** Not in the specification. Derived by the formula of the ruled v3a values (`9600 = 2 x 4500 + 600`): `4500 + 600 = 5100`; the protocol gives the claim TTL as at least 90 minutes (5400 s covers 5100 s). The executor handoff `wall_clock_seconds` 12420 is the sum of the four step timeouts (120 + 1800 + 5100 + 5400). The reconciliation `timeout_seconds` 1800 is my value (S3 copy of about 92 MB).
2. **Locator strictness beyond D-3(a)-(d):** rule (b) also requires result.json `.job_name` = the job, status `.job.state` = `failed`, a 36-character pod uid, exactly one container status, terminated, with an integer exit code; `verify` also requires the exit code in {0, 42, 43}. Rule (a) is "as is" with no check, as in v3a. Each extra check only narrows what is accepted.
3. **Reconciler extras beyond R-1 to R-7:** objects.json is copied and its keys must lie under `runs/JOB/launcher/` or the pod prefix; `SHA256SUMS` non-empty; `run-summary.json` listed at the empty-file digest and 0 bytes (ruling 5); `records.jsonl` is hashed and its newlines counted (`reconcile-result.json` `records_jsonl_newlines`, asserted `10800` = curves x targets x (warmup + rounds) x arms from the frozen spec). An earlier draft that also compared the downloaded file sizes with objects.json was removed to avoid a false stop; byte integrity is `check_job.py`'s.
4. **`raw-result.json` fields:** only `results_locator`, `job_uid`, `pod_uid` were added (D-3). The locate/verify exit codes are printed to the wrapper's stdout and stderr, which the supervisor logs, but are not recorded in `raw-result.json`.
5. **Trial id `T2`** for S2 (the protocol's name for S2) with `depends_on []`; step ids `S01-probe`, `S02-reconcile-t1`, `S03-trial-s2`, `S04-verify`; queue priorities 30 and 40; `version: 2` for the specification.
6. **Validity assertions added to S03:** `/results_locator in [launcher_result, receipt_status_pod_uid]`, `/job_uid` and `/pod_uid` match 36 hex-and-dash characters; the `results_uri` pattern is kept as D-3 requires. Nothing asserts a verdict or an exit code of the job beyond the accepted set.
7. **Spec edits:** `crypto_merge_commit` and `crypto_pr` are not recorded for the v3 freeze (the merge cannot be known before the bound bytes are final; `freeze_commit` 151779ab... and the file sha256 values bind the protocol). The prior v1/v2 entries are kept as `first_version` and `prior_version`; `budget.maximum_runs` stays 2 (one consumed launch, `RUN-ICPERF-8b0d47`, plus this session's one).
8. **Carried unchanged from the previous runbook:** the `ecbench` path and `CRYPTO_CHECKOUT` under `/tmp/claude-0/.../scratchpad/v6/`, `PATH` overlay absent, `aws-cli/1.46.2`. They are session-scratch paths (specification RULINGS-COMPILE item 6d); I did not choose new ones.

## 9. Open blockers (by name)

- **B-RED-TEAM** T-3 of DEC-20261107-b74e2c and `follow_on` of this handoff: no approval can name `runbook_sha256` before the independent review of the locator joint is archived.
- **B-CANONICAL-SPEC-STATE** the packet needs a committed `review_required` canonical specification at the source ref and the approved form as the preview; this task's `artifact_paths` put the preview at the canonical path. The Coordinator decides how the canonical draft is reopened (see the simulation in section 7).
- **B-NOT-PUSHED** the 7 packet blockers of section 7 clear only after the archive commit is on `origin`; `newest_experiments.py --experiment EXP-ICPERF-127dbd --json` (`execution_state ready`) was not run for the same reason.
- **B-QUEUE-ENTRY** `runbook.py lint` of the real clone prints one finding until the approval archive adds the two tasks to `dispatch_queue.json` (the preview queue is in `handoff-previews/`).
- **B-CARD-APPROVAL** `task_card.py lint` prints the missing-approval finding until a committed DEC names the runbook sha256.
- **B-IN-PLACE-REPLACEMENT** the artifact paths replace `runbook.yaml`, `specification.yaml`, `trial-plan.json`, `launch_eks.sh` and `inputs/protocol.json` in place. The stopped session `RBS-ICPERF-de8978` binds the old bytes (still in git: commit `4166fb89d2`), so `runbook.py verify` or `audit` of that session against the working tree will report changed bound files. I did not touch the session or run directories.
- **B-S1-COPY-CUSTODY** the reconciled S1 copy lands in `runbook-sessions/RBS-ICPERF-616277/outputs/S02-reconcile-t1/attempt-1/` (about 96 MB, `records.jsonl` 91,783,489 bytes as asserted). It is not an artifact path of the executor task and the journal hashes it; its compaction to the artifact store (files of 1 MiB or more) and its custody are for the Coordinator.
- **B-PARTIAL-OUTPUT-RESIDUAL** the executor task lists only paths one trial can produce, so a path of a run that cannot exist is never listed. If S2 itself stops after a partial download, a source task in a failed state can still leave declared paths missing; that case is for the Coordinator's archive rules, not for this design.
- **B-SNAPSHOT-RECEIPT** `coordination/.../archives/TASK-20261107-c5a0f4/snapshot-receipt.json` is written by the archive step (commit-bound), not by the director; it does not exist.
- **B-FILED-BEFORE-AFFECTED-DATA** `true` is as ruled (D-6, `freeze --filed-before-affected-data`). The S1 job output existed before the filing; AMENDMENT-2 section 4 and the amendment text disclose PD-1. A reviewer should confirm the flag.
- **B-CRYPTO-PR** the crypto change needs its own Conductor task and ready-for-review PR (not opened, not pushed; Conductor is not installed in this container).
- **B-OWNER-NOTICE** the four-fact notice and the owner's go-ahead are for the top-level session, before the relay.
- **B-SESSION-LOG** `docs/session-logs/2026-11-07.md` was not written by this subagent (outside this task's write scope).

## 10. Commits and what was not done

No push, no PR, no AWS write, no launch, no `runbook.py run`, nothing under `runs/` or `runbook-sessions/` changed, no ledger record or queue edited (the queue change is a preview file). Local commits only, as the dispatch asked (handoff D-8 says not to commit; the dispatch's later instruction to leave commits local for review governs).
