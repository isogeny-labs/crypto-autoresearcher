# FINDINGS: TASK-20261107-d07e94 (EXP-ICPERF-127dbd, C1 launcher v3c, re-session RBS-ICPERF-616277)

Author: experiment-director (Sonnet 5.5), 2026-11-07, worktree of crypto-autoresearcher at main 81b03b294b2ad1eeca852d0624827897290967fd (detached, sparse).
Zero runs, zero launches, zero AWS calls of any kind (read-only calls included). Previews only: nothing is staged, committed or pushed, no ledger record, queue, journal or run directory was edited, and nothing under the 9d2b6a review tree was changed.
No C1 outcome is in this file, and none was read. Every number below is copied from a named file in `evidence/` or from the command output saved there.

## 0. Resume note: the task resumed from a killed session

An earlier director session on this task was killed by a container restart before it returned. Its uncommitted partial work was found in this worktree. A copy is saved, unmodified, at
`scratchpad/d07e94-partial-1.diff` (sha256 `ed9aa2d10b05d08cfd07d42e2dde40ce95c4011bd7c3538b4950ed105c32f453`; `git diff` of the worktree matched it byte for byte when this session started) and
`scratchpad/d07e94-partial-1-untracked.tar.gz` (sha256 `89d1128156ee20b5f0d9a9371cd01694b2671745e811c29b8ae1a902589acf8b`). Treated as an unreviewed draft: every changed file was re-read against the handoff, E-2's scope was re-derived from `git diff HEAD`, and every test and lint below was re-run in this session.

Starting bytes at HEAD 81b03b294b, verified with `git show HEAD:<path> | sha256sum`: launch_eks.sh `f93e8858923765c390fb7bcb01ea04c2373325815f08cbaf7df24b584e521da8`, locate_results.sh `efcc29832806d604913c00afb6e92a2052cb784479cfc65dda42491655326c5e`, reconcile_run.sh `eac18f21de151b55b543e7ebdf51aeda71a23061ae2f8f5449a5064af569bb93` (all three as the handoff states).

| item of the partial work | disposition |
|---|---|
| `implementation/locate_results.sh` (K-1, K-2, K-4, K-6 rewrite) | KEPT as drafted after a full re-read; no byte changed by this session |
| `implementation/reconcile_run.sh` (K-7 prologue, pins, `--out-root`, `objects`/`verify` calls) | KEPT, no byte changed |
| `implementation/launch_eks.sh` (K-7 prologue, K-5 handler, new section 3) | KEPT, no byte changed. Its diff against `git diff HEAD` has exactly three hunks (section 4) |
| `tests/fake-aws`, `tests/fake-launch-remote`, `tests/test_locator.sh` | KEPT, no byte changed (re-run: 137 pass, 0 fail, 0 skip, with the checkout argument) |
| `tests/rt_regression.sh` (port of the 9d2b6a harness), `tests/rt_validity.py`, `tests/fixtures/{launch_eks,locate_results,reconcile_run}.v3b.sh`, `tests/fixtures/isobin-wrap/aws` | KEPT with CHANGES to `rt_regression.sh` listed below; the three v3b fixtures hash to the three starting hashes above |
| `tests/mutation_check.sh` | REPLACED: the draft was a 27-byte stub (`exit 0`). Now a real mutation runner with `tests/mutate.py` |
| `design/d07e94/evidence/00-isolation.txt` | REPLACED by a new record taken in this session's isolation directory (the draft's `isobin-d07e94` was left in the scratchpad and is not used) |
| `design/d07e94/{approval-preview,handoff-previews}/` | were empty directories; filled by this session |
| specification.yaml, trial-plan.json, runbook.yaml, runbook-lint.txt, CARD-EXP-ICPERF-127dbd-4.yaml, FINDINGS.md, SHA256SUMS | did not exist in the draft; written by this session |

Changes made by this session to the drafted test suite (`tests/rt_regression.sh`):
1. `C01-PATH_SHIM` was vacuous in the draft: it created the shim directory but never put it on PATH, so v3c "held" trivially. It now puts `PATH=<shim dir>:<case aws dir>:/usr/bin:/bin` and the legacy (v3b) replay reproduces the 9d2b6a break for it.
2. `C01-BASH_ENV` in legacy mode now classifies a write reaching aws as `BREAK-env` (the draft reported `differs`).
3. New cases `A01d` (result.json results_uri equals the located prefix but its pod_uid names another pod: nothing exercised the `K1-poduid` check, and its mutation survived), `C09w` and `C02w` (the same spoof and CDPATH vectors against launch_eks.sh), `A09c2`, `A09d2`, `A09j`, `C04c` and `C09b` (each isolates one check that a neighbouring check also refused).
4. `A09e` legacy expectation set to `BREAK`: the v3b wrapper ignores objects.json, whereas the 9d2b6a row judged reconcile only.
5. The expected outcome of every refusal case that goes through `launch_eks.sh` now also fixes the exit status of the check that must refuse it (tables `WANT_LRC`, `WANT_RLRC`, `WANT_VRC` at the top of `rt_regression.sh`; the K-4 cases also require an empty recorded `job_exit_code`). Reason: the first complete mutation run (on the suite as drafted plus items 1 to 4) left ten mutants alive because a neighbouring check refused the same input; the added cases and exit-status tables make each removal visible.
6. `rt_regression.sh` refuses to start when the environment holds an exported shell function. The first `mutation_check.sh` exported its runner function, which reached every suite run, made the phase-marker spoof case C09 refuse for the wrong reason (`shell functions are defined`) and hid the K7-allowlist mutant. The runner is now `mutation_check.sh --one NAME OUT`.
7. One director error, disclosed: an earlier mutation run was killed because this session edited the suite while it ran (a running bash reads its script incrementally). Its output was discarded. The tables in section 7 come from a complete run on frozen bytes (the hashes in section 2).

## 1. Ids (unchanged from the handoff; all still unused)

| what | id |
|---|---|
| runbook session | `RBS-ICPERF-616277` |
| S2 run id | `RUN-ICPERF-efb7ef` (T2 of the plan; T1 is the reconciliation of the consumed `RUN-ICPERF-8b0d47`) |
| executor / snapshot handoff previews | `TASK-20261107-f14df8` / `TASK-20261107-04d969` |
| approval decision (reserved, not a record) | `DEC-20261107-7802ec` |
| new card (card -3 is left as is, retired, never relayed) | `CARD-EXP-ICPERF-127dbd-4` |
| protocol | version 3, `protocol_sha256` `4b7bf35f34c0ddf5c0e4bee95e1791e6f5d2bc2fb68d4836db9db53d33e9b9cc`; not edited |

## 2. Hashes (all from `sha256sum`; the full list is `SHA256SUMS`)

| file | sha256 |
|---|---|
| implementation/launch_eks.sh (v3c; v3b `f93e8858...`) | `a61c55da15b149d00ee7e644c41d79ad8df4ae82f3c59dfca157ea9679fc9e76` |
| implementation/locate_results.sh (v3c; v3b `efcc2983...`) | `668a424be9f55c605dd907561fdda9ec6f9ef3c20a08b3cfb1c5c4221110791b` |
| implementation/reconcile_run.sh (v3c; v3b `eac18f21...`) | `a294b7dbc77b33ae4103dfa907a5effba03fe0e2c1837f3f51a44a5897055c16` |
| runbook.yaml | `36105be63adcd97000bfd1fa0b7b63414eafb247cc3774eec7446a7d34caf166` |
| task-cards/CARD-EXP-ICPERF-127dbd-4.yaml | `613bad15fe8f82e405ab3f0366cc57e0095b5cf1098c15cc7581b0b24b4a4429` |
| specification.yaml (canonical draft, review_required) | `64b859ca07ff17f3b718e3ed517c5723a366f0bdcd36e272c0581444032c1490` |
| trial-plan.json (canonical draft, candidate_only) | `4bc6e92782b865e094024409e697e99f0308caf84a855be347b96547959eb14b` |
| design/d07e94/approval-preview/specification.yaml (approved form, PREVIEW) | `5136eaddce2c449690d4cc5a29facb6fd6c22977e04cda6b6459fbcc1e86d723` |
| design/d07e94/approval-preview/trial-plan.json (approved form, PREVIEW) | `7be33749a33d2829577a187ca115bdba5ea6ef35fa59fadf7482fee39b0e64b6` |
| design/d07e94/handoff-previews/TASK-20261107-f14df8.yaml (executor) | `30d31ea211ff3dca46f959724e0c8a18342a8985fb97e4da6f8816bc58d196b0` |
| design/d07e94/handoff-previews/TASK-20261107-04d969.yaml (snapshot) | `0b5f7c6307622307c150db34ed91c94ffa614cdc206c507cfbbef8b871690171` |
| design/d07e94/handoff-previews/dispatch_queue.json (queue preview) | `99a0020f7a45e1b302a0e323aa9905338f22ce0c184ffce0f217d22d87d8ca98` |
| runbook-lint.txt | `f08f498375a57bd9a35329210726beebbe7ebd2cdad65a2c7aeddc503751a70f` |
| tests/test_locator.sh / rt_regression.sh / mutation_check.sh | `ba333838505434104679eca3a13fe0ad8a396f654b5dc9bee4ae4d33d10c6a11` / `5752cf68d6f58ff0731e63e7bfeecd698fc8c2af320884985a64ddbb84db91fb` / `a3b1130e2e2905400249d62ca0254f4f59df270459de2b698d0885ee399d3cae` |
| tests/mutate.py / rt_validity.py | `656879f70c25d96ec5465773b2ce066b0279184a4a7b54da31307505dcc24f23` / `d57b113dd6e5b2e8b16ca12f2039abd3d22f70a8ed66827364da39ba1a0b19c5` |
| tests/fake-aws / fake-launch-remote / fixtures/isobin-wrap/aws | `744733d6feba21bd016753bbec4348b1404337c6afb9506c4130ede6cf3a6571` / `64909705f2a2e4033f1be41565a95039526aa731ac257333fbeab8cab4cd19f4` / `a008160d1252695d20d28c5812984287952e31d092b0a55d1e00f2fc5f99488c` |

Unchanged (confirmed by `git status` and `git diff HEAD --stat`, which list none of them): check_job.py `d60564dd...`, analyze-c1.sh, probe_s01.sh `3d1826e4...`, remote-pins.sha256 `7b753189...`, request-s1/s2.json, spec-c1-s1/s2.json, protocol.json.
The 9d2b6a harness `rt_harness.sh` (sha256 `980abbd1cc35498bf65c2dc4f17677b3dd79805e3db679a5b50a19a9f13a9547`) and its `isobin-wrap/aws` (`bbaf62de63ae62214d7fa015c40d46a60d8e636ee82698dfb7285c5ce2d1a127`) are credited in the header of `tests/rt_regression.sh`.

## 3. The controls and where they are (all tests are offline; `tests/fake-aws` is the only `aws`)

| control | where | what a test refuses |
|---|---|---|
| K-1 one locator rule | `locate_results.sh locate` steps 3-4 (tags `K1-uri`, `K1-poduid`); `launch_eks.sh` `K1-class` | any non-empty `results_uri`/`pod_uid` that differs from `s3://BUCKET/runs/JOB/<pod_uid>/` (exit 24, class `other`): A01b, A01d, A02b, A03b |
| K-2 bytes bound to objects.json | `locate_results.sh` (non-empty `.objects`, `next_token` null, keys, entries, pod listing equals objects.json as (Key, Size, ETag), pins, LastModified), `objects` mode (size and single-part MD5, no extra or missing file); `launch_eks.sh` `K2-wrapper-objects`, `K2-wrapper-dl` | A09a, A09b, A09c to A09i, A10, A10b, A13a to A13e, B14a to B14c |
| K-3 runbook validity | runbook S03 (`download_exit '0'`, `objects_match true`, `objects_check 'true'`, `locate_exit '0'`, `results_locator receipt_status_pod_uid`; T2 pins `results_uri` to the s2 prefix) and S02 (`objects_match`, `receipt_pins_outcome`, the two receipt sha256 values, `env_hygiene`) | the runbook is evaluated by `tools/runbook.py` through `tests/rt_validity.py` (not transcribed) |
| K-4 strict job exit | `locate_results.sh verify` (`K4-type`, `K4-raw`), `launch_eks.sh` (`K4-wrapper`) | B05 to B11c, B12a, B12b, K4-a to K4-f |
| K-5 post-submission crashes | `launch_eks.sh` ERR trap `post_crash` after the submission line (no exit 2, 3 or 4 follows it) | B03, B04, B15a to B15c, B15e, B15f, K5, K5b: each writes raw-result.json (submitted true, class other) and exits 5 |
| K-6 receipt tightening | `locate_results.sh` (`K6-receipt-uuid`, `K6-launcher-id`, `K6-poduid`, `K6-restart`) | A06e, A06f, A07e, A08, A08b, A08c |
| K-7 environment | identical prologue in `launch_eks.sh` and `reconcile_run.sh` (`env -i` re-exec with an allowlist, phase-2 refusal of anything else); `reconcile_run.sh` `here` via `CDPATH= cd --` and `realpath`; `--out` inside `--out-root`, never under `runs/` | C01 (BASH_ENV, exported `BASH_FUNC_aws`, PATH shim), C01w, C02, C02w, C04, C04b, C06 (AWS_ENDPOINT_URL), C07 (alias, credential_process, endpoint_url, plugins), C07w, C08 (version pin), C09, C09w, C10, C11 |

## 4. E-2 diff scope (`evidence/launch_eks.v3b-to-v3c.diff`, `.hunks.txt`; `launch_eks.v3a-to-v3c.diff`, `.hunks.txt`)

`git diff HEAD -- implementation/launch_eks.sh` and the fixture diff (v3b fixture `f93e8858...` against the working file) are identical apart from the function-context text of the hunk headers (checked with `diff`). Three hunks, v3b line numbers:

```
@@ -30,6 +30,70 @@      the K-7 prologue, between `set +x` and `dry=0;`
@@ -232,43 +296,76 @@   the K-5 handler (after the `launch-remote exit` line) and the new section 3
@@ -288,15 +385,20 @@   the tail of section 3: the K-1/parse class vetoes and the added raw-result.json fields
```

v3a to v3c: the same three hunks (v3a numbers `@@ -30,6 +30,70 @@`, `@@ -232,18 +296,77 @@`, `@@ -262,12 +385,21 @@`). `tests/test_locator.sh` asserts, and passed, that v3b lines 1 to 32, v3b lines 34 to 233 (sections 1, 1b, 1c, 2, `write_records`, both manifests, `refuse`, the duplicate checks and the `launch-remote exit` line), the outcome-class block (deadline first, the 42/43 accept pairing) and the last three lines are byte-identical, and that there are exactly three hunks.
`remote-pins.sha256`, `check_job.py`, `probe_s01.sh`, the requests and the specs are untouched. `locate_results.sh` and `reconcile_run.sh` are rewrites (`evidence/locate_results.v3b-to-v3c.diff`, `evidence/reconcile_run.v3b-to-v3c.diff`).

Two consequences of E-2 that a reviewer should see: (a) section 1b's `here=$(cd "$(dirname ...)" && pwd)` in launch_eks.sh stays byte-identical; CDPATH cannot reach it because the prologue's `env -i` drops CDPATH and phase 2 refuses it (cases C02w, C09w); (b) section 1c keeps its lexical `--out` check (`<record-dir>/job`); the realpath/`runs/` check of K-7 is in reconcile_run.sh only, because the wrapper's `--out` lives under the supervisor's own `runs/` directory by design and 1c may not change.

## 5. E-3 receipt pins

`reconcile_run.sh` has no default for them (`grep a2642563 783ea0e3 02:14:41` over the three scripts: no match; the values appear in the runbook S02 argv, the specification (`experiment.inputs.s1_reconciliation.receipt_pins`) and the tests). The runbook S02 argv carries `--pin-status-sha256 a2642563d10a8f80661cef79a759b892d44fad49057a409ae03a1bee3a960ae0`, `--pin-objects-sha256 783ea0e3ec77daf52d3ff815cb096295a3db76fe05b5cc9b1884c001126504d7`, `--pin-not-after 2026-11-07T02:14:41Z`, and `--out-root '{session_dir}/outputs/S02-reconcile-t1'`. `locate_results.sh` requires each LastModified of the two receipt objects and of every listed pod object to be at or before the pin (cases A13a to A13e, and the real receipt bytes in `test_locator.sh` P1R).

## 6. E-4 regression

Commands (each under `env -i HOME TMPDIR PATH=<dir with only fake aws and fake-launch-remote>:/usr/bin:/bin`; `evidence/00-isolation.txt` records `command -v aws` and `env | grep -c AWS_` = 0):
`bash tests/test_locator.sh OUT /home/user/crypto`, `bash tests/rt_regression.sh OUT`, `bash tests/rt_regression.sh OUT x legacy`, `bash tests/mutation_check.sh OUT 4`.
The checkout argument `/home/user/crypto` (HEAD c2f01f13fd) holds the four launcher scripts whose sha256 values equal `remote-pins.sha256`, so the dry-run case ran.

- **test_locator.sh: 137 pass, 0 fail, 0 skip** (`evidence/test_locator-RESULTS.txt`, `test_locator-output.txt`).
- **rt_regression.sh (v3c): 123 rows, 123 PASS** (`evidence/rt-results.tsv`, `rt-summary.txt`). Of the 69 rows of the 9d2b6a harness, 27 carried a non-holding 9d2b6a verdict (BREAK, BREAK-wrapper, BREAK-env, NOTE-crash, NOTE-accepted, ...); 26 of them are now refused/holding (not flipped: B13-pair-0-SUCCEEDED-0 (NOTE-odd-pairing-accepted); the (0, SUCCEEDED, 0) pairing stays accepted by design: it is the unchanged outcome-class block, which E-2 keeps byte-identical, and the pinned launcher cannot produce it). 40 of the 40 rows that 9d2b6a recorded as `holds` still hold. A00 and the genuine T1 shape pass (A00, A01c, P1/P2 in test_locator.sh). 54 rows are new in this task (K-4 to K-7 and the extra K-1/K-2 cases).
- **Legacy replay (port check)**: `rt_regression.sh ... legacy` runs the three v3b scripts through the same harness. Of the 69 case ids of 9d2b6a, 68 reproduce the 9d2b6a verdict exactly; differing: A09e-objects-json-key-outside (`evidence/rt-results-legacy-v3b.tsv`). `A09e` differs by construction: the v3b wrapper ignores objects.json, while the 9d2b6a row judged reconcile's R-3 only.

### 6.1 The seven cases named by the ruling, individually

| case | question | sound result (expected for v3c) | 9d2b6a verdict on v3b | v3b replayed by this port | v3c observed (compact) | v3c outcome | v3c expected | verdict |
|---|---|---|---|---|---|---|---|---|
| A01-ruleA-sibling-prefix | a,b | not job_completed (two pod prefixes; not this pod) | BREAK | BREAK | `rc=5 class=infrastructure_candidate locator=none raw=present sub=true dl=not_attempted objects_match=absent locate_exit=13 validity=INVALID s3_write_attempts=0 uri=; check_job=no-artifacts` | holds | holds | PASS |
| A02-ruleA-cross-job | a,b | not job_completed (another job's prefix) | BREAK-wrapper | BREAK-wrapper | `rc=5 class=infrastructure_candidate locator=none raw=present sub=true dl=not_attempted objects_match=absent locate_exit=13 validity=INVALID s3_write_attempts=0 uri=; check_job=no-artifacts` | holds | holds | PASS |
| A09a-added-object | a | K-2: refuse (reconcile exit 5 from the pod listing; wrapper not job_completed) | BREAK | BREAK | `wrapper: rc=5 class=infrastructure_candidate locator=none raw=present sub=true dl=not_attempted objects_match=absent locate_exit=22 validity=INVALID s3_write_attempts=0; reconcile rc=5 pass=false locate_exit=22; control(object-list vs objects.json)=n/a` | holds | holds | PASS |
| A09b-replaced-object | a | K-2: refuse (reconcile exit 5 from the pod listing; wrapper not job_completed) | BREAK | BREAK | `wrapper: rc=5 class=infrastructure_candidate locator=none raw=present sub=true dl=not_attempted objects_match=absent locate_exit=22 validity=INVALID s3_write_attempts=0; reconcile rc=5 pass=false locate_exit=22; control(object-list vs objects.json)=n/a` | holds | holds | PASS |
| A10-toctou-after-listing | a | late prefix not bound; late bytes are not this job's output; both refused | holds(prefix)/content-not-bound | holds(prefix)/content-not-bound | `rc=5 class=infrastructure_candidate locator=none raw=present sub=true dl=not_attempted objects_match=absent locate_exit=22 validity=INVALID s3_write_attempts=0; check_job=no-artifacts; late.json=absent; other-prefix files downloaded=0; reconcile rc=5 pass=fals...` | holds(prefix)/ok | holds(prefix)/ok | PASS |
| B14a-partial-listed-lost | b | not job_completed when the download exit is nonzero; reconcile refused | BREAK-wrapper-only | BREAK-wrapper-only | `rc=5 class=other locator=receipt_status_pod_uid raw=present sub=true dl=1 objects_match=absent locate_exit=0 validity=INVALID s3_write_attempts=0; check_job=CHECK_JOB_FAILED; reconcile rc=6 pass=false` | holds | holds | PASS |
| B14b-partial-unlisted-lost | b | not job_completed when the download exit is nonzero; reconcile refused | BREAK-wrapper+check_job | BREAK-wrapper+check_job | `rc=5 class=infrastructure_candidate locator=none raw=present sub=true dl=not_attempted objects_match=absent locate_exit=22 validity=INVALID s3_write_attempts=0; check_job=no-artifacts; reconcile rc=5 pass=false` | holds | holds | PASS |

Observed strings are shortened here (`validity=INVALID` stands for the S03 validity message); the full text is in `evidence/rt-results.tsv` and the per-case directories of the run. "9d2b6a verdict" is the verdict column of `reviews/redteam-9d2b6a/evidence/rt-run/rt-results.tsv`. "v3b replayed" is this port's outcome on the v3b scripts.

### 6.2 All cases (expected and observed outcome)

| case | 9d2b6a (v3b) | v3b replayed | v3c expected | v3c outcome | verdict |
|---|---|---|---|---|---|
| A00-control-T1-shape | control | control | control | control | PASS |
| A01-ruleA-sibling-prefix | BREAK | BREAK | holds | holds | PASS |
| A01b-ruleA-sibling-prefix-with-receipt | (new in d07e94) | BREAK | holds | holds | PASS |
| A01c-ruleA-uri-equals-located | (new in d07e94) | BROKEN | control | control | PASS |
| A01d-ruleA-uri-located-poduid-differs | (new in d07e94) | BREAK-wrapper | holds | holds | PASS |
| A02-ruleA-cross-job | BREAK-wrapper | BREAK-wrapper | holds | holds | PASS |
| A02b-ruleA-cross-job-with-receipt | (new in d07e94) | BREAK-wrapper | holds | holds | PASS |
| A03-ruleA-other-bucket | BREAK-wrapper | BREAK-wrapper | holds | holds | PASS |
| A03b-ruleA-other-bucket-with-receipt | (new in d07e94) | differs | holds | holds | PASS |
| A04-ruleA-verification-failed-genuine | holds | holds | holds | holds | PASS |
| A04b-ruleA-verification-failed-with-receipt | (new in d07e94) | holds | holds | holds | PASS |
| A05-uid-prefix-sibling | holds | holds | holds | holds | PASS |
| A06a-receipt-other-job | holds | holds | holds | holds | PASS |
| A06b-receipt-dotdot | holds | holds | holds | holds | PASS |
| A06c-receipt-other-bucket | holds | holds | holds | holds | PASS |
| A06d-receipt-deeper | holds | holds | holds | holds | PASS |
| A06e-receipt-second-launcher-id | NOTE-accepted | NOTE-accepted | refused | refused | PASS |
| A06f-receipt-id-all-dashes | NOTE-accepted | NOTE-accepted | refused | refused | PASS |
| A07a-poduid-dotdot | holds | holds | holds | holds | PASS |
| A07b-poduid-slash | holds | holds | holds | holds | PASS |
| A07c-poduid-35 | holds | holds | holds | holds | PASS |
| A07d-poduid-upper | holds | holds | holds | holds | PASS |
| A07e-poduid-trailing-newline | NOTE-accepted | NOTE-accepted | refused | refused | PASS |
| A12a-status-job-uid | holds | holds | holds | holds | PASS |
| A12b-status-job-name | holds | holds | holds | holds | PASS |
| A12c-two-pods | holds | holds | holds | holds | PASS |
| A12d-zero-pods | holds | holds | holds | holds | PASS |
| A08-restart-count | NOTE-accepted | NOTE-accepted | refused | refused | PASS |
| A08b-restart-count-only | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| A08c-laststate-only | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| A09a-added-object | BREAK | BREAK | holds | holds | PASS |
| A09b-replaced-object | BREAK | BREAK | holds | holds | PASS |
| A09c-objects-json-vacuous | NOTE-vacuous | NOTE-vacuous | holds | holds | PASS |
| A09c2-objects-json-empty-array | (new in d07e94) | BREAK | holds | holds | PASS |
| A09d-objects-json-truncated | NOTE-truncated-accepted | NOTE-truncated-accepted | holds | holds | PASS |
| A09e-objects-json-key-outside | holds | BREAK | holds | holds | PASS |
| A09d2-objects-json-next-token-only | (new in d07e94) | BREAK | holds | holds | PASS |
| A09j-objects-json-no-pod-entries | (new in d07e94) | BREAK | holds | holds | PASS |
| A09f-objects-json-missing-etag | (new in d07e94) | BREAK | holds | holds | PASS |
| A09g-objects-json-extra-entry | (new in d07e94) | BREAK | holds | holds | PASS |
| A09h-multipart-etag-size-only | (new in d07e94) | control | control | control | PASS |
| A09i-multipart-size-changed | (new in d07e94) | BREAK | holds | holds | PASS |
| A10-toctou-after-listing | holds(prefix)/content-not-bound | holds(prefix)/content-not-bound | holds(prefix)/ok | holds(prefix)/ok | PASS |
| A10b-toctou-after-pod-listing | (new in d07e94) | BREAK | holds | holds | PASS |
| A13a-pin-status-wrong | (new in d07e94) | BREAK | holds | holds | PASS |
| A13b-pin-objects-wrong | (new in d07e94) | BREAK | holds | holds | PASS |
| A13c-receipt-object-too-new | (new in d07e94) | BREAK | holds | holds | PASS |
| A13d-pod-object-too-new | (new in d07e94) | BREAK | holds | holds | PASS |
| A13e-receipt-lastmodified-missing | (new in d07e94) | BREAK | holds | holds | PASS |
| B01-jobexit-missing | holds | holds | holds | holds | PASS |
| B02-jobexit-empty | holds | holds | holds | holds | PASS |
| B03-jobexit-not-json | NOTE-crash | NOTE-crash | holds | holds | PASS |
| B04-jobexit-is-directory | NOTE-crash | NOTE-crash | holds | holds | PASS |
| B05-exit-string-42 | holds | holds | holds | holds | PASS |
| B06-exit-true | holds | holds | holds | holds | PASS |
| B07-exit-false | holds | holds | holds | holds | PASS |
| B08-exit-null | holds | holds | holds | holds | PASS |
| B09-exit-42.5 | holds | holds | holds | holds | PASS |
| B10-exit-42.0 | holds | holds | holds | holds | PASS |
| B11-exit-array | holds | holds | holds | holds | PASS |
| B11b-exit-exponent | (new in d07e94) | BREAK | holds | holds | PASS |
| B11c-exit-negative-zero | (new in d07e94) | holds | holds | holds | PASS |
| B16a-jobexit-other-pod | holds | holds | holds | holds | PASS |
| B16b-jobexit-other-job | holds | holds | holds | holds | PASS |
| B16c-jobexit-ne-container | holds | holds | holds | holds | PASS |
| B12a-ruleA-exit-string-0 | BREAK-wrapper | BREAK-wrapper | holds | holds | PASS |
| B12b-ruleA-exit-string-42 | BREAK-wrapper | BREAK-wrapper | holds | holds | PASS |
| K4-a-string-0 | (new in d07e94) | BREAK | holds | holds | PASS |
| K4-b-string-42 | (new in d07e94) | BREAK | holds | holds | PASS |
| K4-c-true | (new in d07e94) | holds | holds | holds | PASS |
| K4-d-float-42.0 | (new in d07e94) | holds | holds | holds | PASS |
| K4-e-exponent | (new in d07e94) | BREAK | holds | holds | PASS |
| K4-f-float-0.0 | (new in d07e94) | holds | holds | holds | PASS |
| B13-pair-26-FAILED-42 | holds | holds | holds | holds | PASS |
| B13-pair-26-FAILED-43 | holds | holds | holds | holds | PASS |
| B13-pair-26-FAILED-0 | holds | holds | holds | holds | PASS |
| B13-pair-0-SUCCEEDED-42 | holds | holds | holds | holds | PASS |
| B13-pair-0-FAILED-42 | holds | holds | holds | holds | PASS |
| B13-pair-26-SUCCEEDED-42 | holds | holds | holds | holds | PASS |
| B13-pair-26-NONE-42 | holds | holds | holds | holds | PASS |
| B13-pair-25-FAILED-42 | holds | holds | holds | holds | PASS |
| B13-pair-1-FAILED-42 | holds | holds | holds | holds | PASS |
| B13-pair-26-TIMED_OUT-42 | holds | holds | holds | holds | PASS |
| B13-pair-0-SUCCEEDED-0 | NOTE-odd-pairing-accepted | NOTE-odd-pairing-accepted | NOTE-odd-pairing-accepted | NOTE-odd-pairing-accepted | PASS |
| B13-pair-26-STOPPED-42 | holds | holds | holds | holds | PASS |
| B14a-partial-listed-lost | BREAK-wrapper-only | BREAK-wrapper-only | holds | holds | PASS |
| B14b-partial-unlisted-lost | BREAK-wrapper+check_job | BREAK-wrapper+check_job | holds | holds | PASS |
| B14c-partial-nothing-lost | (new in d07e94) | BREAK-wrapper+check_job | holds | holds | PASS |
| B15a-result-not-json | NOTE-crash | NOTE-crash | holds | holds | PASS |
| B15b-build-not-json | NOTE-crash | NOTE-crash | holds | holds | PASS |
| B15c-result-array | NOTE-crash | NOTE-crash | holds | holds | PASS |
| B15d-result-empty | (new in d07e94) | holds | holds | holds | PASS |
| B15e-status-not-json | (new in d07e94) | holds | holds | holds | PASS |
| B15f-objects-not-json | (new in d07e94) | BREAK | holds | holds | PASS |
| K5-newline-file-name | (new in d07e94) | NOTE-crash | holds | holds | PASS |
| K5b-record-write-fails | (new in d07e94) | NOTE-crash | holds | holds | PASS |
| C01-BASH_ENV | BREAK-env | BREAK-env | holds | holds | PASS |
| C01-EXPORTED_FUNCTION | BREAK-env | BREAK-env | holds | holds | PASS |
| C01-PATH_SHIM | BREAK-env | BREAK-env | holds | holds | PASS |
| C01w-BASH_ENV | (new in d07e94) | holds | holds | holds | PASS |
| C01w-EXPORTED_FUNCTION | (new in d07e94) | BREAK-env | holds | holds | PASS |
| C02-CDPATH-relative-argv | BREAK-env | BREAK-env | holds | holds | PASS |
| C02b-CDPATH-dot | NOTE-fails-closed | NOTE-fails-closed | holds | holds | PASS |
| C03-ISOLAB_BUCKET-override | holds | holds | holds | holds | PASS |
| C04-out-symlink-into-runs | NOTE-lexical-only | NOTE-lexical-only | holds | holds | PASS |
| C04b-out-outside-out-root | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C04c-out-runs-inside-out-root | (new in d07e94) | refused | refused | refused | PASS |
| C06-AWS_ENDPOINT_URL | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C06-AWS_ENDPOINT_URL_S3 | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C06w-AWS_ENDPOINT_URL_S3-wrapper | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C07-config-alias | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C07-config-credential_process | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C07-config-endpoint_url | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C07-config-plugins | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C07w-config-credential_process-wrapper | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C08-aws-version-mismatch | (new in d07e94) | refused | refused | refused | PASS |
| C09-phase-marker-spoof | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C09b-phase-marker-spoof-pythonpath | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C09w-phase-marker-spoof-wrapper | (new in d07e94) | NOTE-accepted | refused | refused | PASS |
| C02w-CDPATH-wrapper | (new in d07e94) | holds | holds | holds | PASS |
| C10-credentials-by-name | (new in d07e94) | differs | holds | holds | PASS |
| C11-python-shim-ahead-of-aws | (new in d07e94) | differs | holds | holds | PASS |
| C05-static-scan | holds | holds | holds | holds | PASS |

## 7. Mutation results (K-1, K-2, K-4, K-6 required; K-5 and K-7 added)

`tests/mutate.py` removes one check per mutant (a text edit that must match exactly once), `tests/mutation_check.sh` runs the whole `rt_regression.sh` against each mutant; CAUGHT means at least one case differs from its expected outcome. Baseline (unmutated): BASELINE-CLEAN. 32 mutations: 30 caught, 2 subsumed (K2-nonempty (SUBSUMED(by K2-nonempty-and-entries)), K4-type (SUBSUMED(by K4-verify))), survived or errored: none (`evidence/mutation-results.tsv`, `mutation-list.tsv`, `mutation-output.txt`). All K-1, K-2, K-4 and K-6 checks listed in `tests/mutate.py` make at least one case fail when removed, except the two subsumed ones, whose pair-removal mutants do.

| mutation | control | verdict | differing cases | first failing cases |
|---|---|---|---|---|
| BASELINE | - | BASELINE-CLEAN | 0 differing case(s) | none |
| K1-uri | K-1 | CAUGHT | 2 differing case(s) | A02b-ruleA-cross-job-with-receipt A03b-ruleA-other-bucket-with-receipt  |
| K1-poduid | K-1 | CAUGHT | 1 differing case(s) | A01d-ruleA-uri-located-poduid-differs  |
| K1-class | K-1 | CAUGHT | 4 differing case(s) | A01b-ruleA-sibling-prefix-with-receipt A01d-ruleA-uri-located-poduid-differs A02b-ruleA-cross-job-with-receipt A03b-ruleA-other-bucket-with-receipt  |
| K2-nonempty | K-2 | SUBSUMED(by K2-nonempty-and-entries) | 0 differing case(s) | none |
| K2-nexttoken | K-2 | CAUGHT | 2 differing case(s) | A09d-objects-json-truncated A09d2-objects-json-next-token-only  |
| K2-keys | K-2 | CAUGHT | 1 differing case(s) | A09e-objects-json-key-outside  |
| K2-entries | K-2 | CAUGHT | 2 differing case(s) | A09j-objects-json-no-pod-entries A09f-objects-json-missing-etag  |
| K2-listing | K-2 | CAUGHT | 6 differing case(s) | A09a-added-object A09b-replaced-object A09g-objects-json-extra-entry A09i-multipart-size-changed A10-toctou-after-listing B14b-partial-unlisted-lost  |
| K2-objects | K-2 | CAUGHT | 1 differing case(s) | A10b-toctou-after-pod-listing  |
| K2-nonempty-and-entries | K-2 | CAUGHT | 3 differing case(s) | A09c2-objects-json-empty-array A09j-objects-json-no-pod-entries A09f-objects-json-missing-etag  |
| K2-pin-status | K-2 | CAUGHT | 1 differing case(s) | A13a-pin-status-wrong  |
| K2-pin-objects | K-2 | CAUGHT | 1 differing case(s) | A13b-pin-objects-wrong  |
| K2-pin-lastmodified | K-2 | CAUGHT | 1 differing case(s) | A13c-receipt-object-too-new  |
| K2-pin-podlm | K-2 | CAUGHT | 1 differing case(s) | A13d-pod-object-too-new  |
| K2-wrapper-objects | K-2 | CAUGHT | 2 differing case(s) | A10b-toctou-after-pod-listing K5-newline-file-name  |
| K2-wrapper-dl | K-2 | CAUGHT | 1 differing case(s) | B14c-partial-nothing-lost  |
| K4-type | K-4 | SUBSUMED(by K4-verify) | 0 differing case(s) | none |
| K4-raw | K-4 | CAUGHT | 2 differing case(s) | B11b-exit-exponent K4-e-exponent  |
| K4-wrapper | K-4 | CAUGHT | 13 differing case(s) | B05-exit-string-42 B06-exit-true B09-exit-42.5 B10-exit-42.0 B11b-exit-exponent B11c-exit-negative-zero K4-a-string-0 K4-b-string-42 K4-c-true K4-d-float-42.0 K4-e-exponent K4-f-float-0.0  |
| K4-verify | K-4 | CAUGHT | 5 differing case(s) | B10-exit-42.0 B11b-exit-exponent K4-d-float-42.0 K4-e-exponent K4-f-float-0.0  |
| K5-trap | K-5 | CAUGHT | 1 differing case(s) | K5b-record-write-fails  |
| K6-receipt-uuid | K-6 | CAUGHT | 1 differing case(s) | A06f-receipt-id-all-dashes  |
| K6-launcher-id | K-6 | CAUGHT | 1 differing case(s) | A06e-receipt-second-launcher-id  |
| K6-poduid | K-6 | CAUGHT | 5 differing case(s) | A07a-poduid-dotdot A07b-poduid-slash A07c-poduid-35 A07d-poduid-upper A07e-poduid-trailing-newline  |
| K6-restart | K-6 | CAUGHT | 3 differing case(s) | A08-restart-count A08b-restart-count-only A08c-laststate-only  |
| K7-out-runs | K-7 | CAUGHT | 1 differing case(s) | C04c-out-runs-inside-out-root  |
| K7-out-root | K-7 | CAUGHT | 1 differing case(s) | C04b-out-outside-out-root  |
| K7-endpoint | K-7 | CAUGHT | 2 differing case(s) | C06-AWS_ENDPOINT_URL C06-AWS_ENDPOINT_URL_S3  |
| K7-version | K-7 | CAUGHT | 19 differing case(s) | A00-control-T1-shape A09e-objects-json-key-outside A09h-multipart-etag-size-only A10b-toctou-after-pod-listing A13a-pin-status-wrong A13b-pin-objects-wrong A13c-receipt-object-too-new A13d-pod-object-too-new A13e-receipt-lastmodified-missing B16a-jobexit-other-pod B16b-jobexit-other-job B16c-jobexit-ne-container  |
| K7-config | K-7 | CAUGHT | 4 differing case(s) | C07-config-alias C07-config-credential_process C07-config-endpoint_url C07-config-plugins  |
| K7-allowlist | K-7 | CAUGHT | 1 differing case(s) | C09b-phase-marker-spoof-pythonpath  |
| K7-launch-config | K-7 | CAUGHT | 1 differing case(s) | C07w-config-credential_process-wrapper  |

Reading of the table. `CAUGHT`: at least one case differs from its expected outcome. `SUBSUMED(by X)`: removing the check alone changes no outcome because the next check refuses the same inputs with the same exit status, and the mutant that removes the pair X is CAUGHT. Two pairs are of that kind and are kept as defence in depth: `K2-nonempty` is subsumed by `K2-entries` (which also requires at least one pod entry; an empty `.objects` is then refused by the entries check with the same exit 21), and the jq type test of `verify` (`K4-type`) is subsumed by the equality with the container exit code (a string or boolean is never equal to a number) plus the raw-spelling test `K4-raw` (which refuses 42.0, 4.2e1 and -0). `K4-raw`, `K4-wrapper` and `K4-verify` are each caught by the K-4 cases that require both `verify` exit 18 and an empty recorded `job_exit_code`.
The mutants edit the three scripts only; `tests/mutate.py list` prints the edits, and each edit must match exactly once (otherwise the helper fails rather than test nothing).

## 8. Records (E-5)

- Canonical `specification.yaml` stays `status: review_required`, `approved_by: null`, `execution_authorized: false`; canonical `trial-plan.json` stays `approved_by: null`, `candidate_only: true`, `approval_required: true`; its `specification_sha256` is the canonical draft's. Both carry the new source bytes (`source_sha256` of launch_eks.sh and locate_results.sh in the plan).
- The approved forms exist only under `design/d07e94/approval-preview/` (status approved, `approved_by DEC-20261107-7802ec`, `execution_authorized true`; the plan's `specification_sha256` is the preview specification's). Nothing at a canonical path reads approved (PD-3 check below).
- `runbook.yaml` binds the PREVIEW digests of those two files and says so in its header. `tools/runbook.py lint`: in the unmodified worktree it prints the four expected findings and nothing else (`evidence/runbook-lint-real-clone.txt`: the two bind mismatches, `spec_bindings[1]` (`approved_by` is None in the draft) and the missing queue entry for `TASK-20261107-f14df8`); in the scratch layout that swaps the previews in and uses the preview queue (`scratchpad/d07-stageA`) it prints `LINT OK ... sha256 36105be63adcd97000bfd1fa0b7b63414eafb247cc3774eec7446a7d34caf166` (`evidence/runbook-lint-approved-state-sim.txt`, copied to `runbook-lint.txt`).
- `tools/task_card.py lint CARD-...-4`: in the worktree it prints the four runbook findings (it stops at the runbook's lint); in the approved-state scratch layout `CARD FAIL` with exactly one finding, `no committed approval decision names this experiment and runbook_sha256 36105be63adcd97000bfd1fa0b7b63414eafb247cc3774eec7446a7d34caf166` (`evidence/card-lint-approved-state-sim.txt`). With a stand-in approval in a scratch git layout (not a record) it prints `CARD OK` and the relay text (`evidence/card-prompt-simulated-approval.txt`).
- `tools/experiment_preapproval.py --packet evidence/preapproval-packet.json` (preview queue and executor handoff from `handoff-previews/`): in the worktree `approvable false`, 4 blockers, all "not committed with these bytes at origin/main" (canonical specification, lint receipt, launch_eks.sh, locate_results.sh); in a scratch git layout with the same files committed under `refs/remotes/origin/main`, `approvable true`, 0 blockers (`evidence/preapproval-output-real-clone.json`, `preapproval-output-simulated-pushed.json`, `preapproval-NOTE.txt`). The simulation is not an approvability claim.
- Executor handoff preview: card -4, launcher v3c, the preview plan digest in `execution.trial_plan_sha256`, DEC-20261107-a83c51 in the inputs, the relay statement names the red-team reconfirmation of the v3c bytes, and a constraint forbids BASH_ENV, ENV, CDPATH, AWS_ENDPOINT_URL*, BASH_FUNC_ exports and aws-cli alias/endpoint_url/credential_process entries in the relay environment. The snapshot handoff is the c5a0f4 preview with a header line. The queue preview is the canonical queue plus the two entries and one note.
- Card -3 is untouched (`git status` shows no change to it), retired, never relayed.
- Session id, run id, the two task ids and the reserved decision id are unchanged and unused.

## 9. Values the specification did not give (each is a `specification_error` for the Coordinator, none is a default chosen silently)

1. **K-7 credential variables.** The handoff says "only the credential variables that the executor identity needs, enumerated by name". The prologue passes `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` (array `K7_CRED_VARS`). That is my choice. In this container the ambient AWS variables (names only) are `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY`; `AWS_SESSION_TOKEN` is not set here.
2. **K-7 transport variables.** Nothing says whether `HTTPS_PROXY`/`https_proxy`/`NO_PROXY`/`no_proxy` and `AWS_CA_BUNDLE` pass. This container's runtime notes say outbound HTTPS goes through a pre-configured proxy with its own CA bundle, and `env -i` drops all of those variables, so on these bytes S02 is expected to stop at its first aws call (locator exit 13, reconcile exit 4) in a proxy-only network. That is an inference: no AWS call is allowed here, so it was not tested. Not added: widening the allowlist is the Coordinator's call (blocker B-K7-TRANSPORT-ENV).
3. **K-7 permitted aws-cli configuration entries.** `K7_CFG_ALLOWED` is empty: any `credential_process`, `endpoint_url`, `cli_legacy_plugin_path`, `[plugins]` or alias entry refuses. "Beyond those the executor identity already uses" names no entry, and this container's `~/.aws/config` holds none of those (it holds an `[default]` `s3` block with `payload_signing_enabled`, names only).
4. **`--out-root`.** The handoff says "the step's session output directory"; the runbook passes `{session_dir}/outputs/S02-reconcile-t1` (so `{out}` = `.../attempt-1` is strictly inside it).
5. **Pinned aws CLI.** `aws-cli/1.46.2` is the version already in the runbook (S01) and DEC-20261107-a83c51 K-7.
6. **S03 validity extras** beyond the three of K-3: `objects_check 'true'` and `locate_exit '0'` (both are fields the v3c wrapper writes). The generic `results_uri` pattern admitting `s[12]` was removed from the common block; the T2 pin replaces it (K-3, the 9d2b6a disagreement 4).
7. **No other timeout or TTL changed**: S03 `timeout_seconds` 5100, `claim.ttl_minutes` 90, S02 `timeout_seconds` 1800 are the c5a0f4 values.
8. **AMENDMENT-2 wording.** The frozen C1-AMENDMENT-2 text says a non-empty `results_uri` is used "as is". v3c narrows that to "only when it equals the located prefix" (K-1). The specification's amendment summary was not edited (the protocol and its amendment are frozen); the narrowing is recorded in `experiment.inputs.locator_controls`. DEC-20261107-7802ec should say so.

## 10. Residual risk (E-6, for DEC-20261107-7802ec)

- **K-8 (no read-only IAM identity for S02)** is not met: it needs an owner-side IAM change. Without it, S02's write-safety rests on K-7, on the static scan of the bytes (`evidence/grep-no-submit-no-s3-write.txt`: no submit or write token, every aws call is a read), and on the permissions the executor identity actually has, which this task did not and could not query (no AWS call).
- **The aws-cli configuration surface was not exercised.** No real aws CLI ran (E-1); every test uses `tests/fake-aws`. K-7's scan reads only `~/.aws/config`, `~/.aws/credentials` and `~/.aws/cli/alias` (entry names, never values) for `credential_process`, `endpoint_url`, `cli_legacy_plugin_path`, `[plugins]` and alias lines. It does not cover `/etc` or system-level config, `ca_bundle`, `sso`/`source_profile`/`role_arn` chaining, `metadata_service` settings, pre-installed plugins, or whether an alias can shadow `s3` (unconfirmed by the 9d2b6a review as well). Behaviours of the real CLI that the fake imitates (v1 output of `s3api list-objects-v2` including the empty-prefix case, pagination, quoted ETags, `LastModified` format) are unverified against the real CLI; the first real call of `list-objects-v2` will be in S02.
- **Multipart ETags.** An ETag with a dash is compared as a string with the launcher's listing and, after the download, by size only; its MD5 cannot be recomputed. For S1 this is covered by the LastModified pin (a re-upload gets a newer time, so it fails the pin). For S2 there is no pin: a same-size replacement of a multipart object (records.jsonl is about 92 MB, so it is multipart) between the pod-prefix listing and the end of the download would pass `objects`; the only remaining check is `SHA256SUMS`, which the job itself wrote. A second listing after the download would narrow but not close that window and was not added (E-2 limits section 3 to K-1, K-2, K-4, K-6).
- **BASH_ENV runs before the first line.** `env -i` removes BASH_ENV for everything after the re-exec, and phase 2 refuses it, but a non-interactive bash sources BASH_ENV before executing the script's first line. Case `C01-BASH_ENV` shows this: the payload ran once (in the caller's shell) and its write reached the fake aws (which refuses it) while the clean phase ran none. `bash -p script ...` ignores BASH_ENV (`evidence/bash-env-observation.txt`), so argv beginning `bash -p` would close it. Not adopted: it changes the runbook S02 argv and the plan's trial argv, which are not mine to choose; Coordinator decision (blocker B-BASH-ENV-FIRST-SHELL).
- **The directory of the first `aws` on PATH is trusted.** The prologue keeps only that directory plus `/usr/bin:/bin`, so a shim in the aws directory itself (for example `python3` next to `aws`) still runs.
- **launch_eks.sh sections 1 to 2 are unchanged by E-2**: `here` uses a bare `cd` (protected by the prologue), and `--out` has only the lexical check of 1c.
- **Synthetic job outputs.** The harness builds the job output sets itself (check_job.py is the real one) and uses the real launcher receipt shape for T1. No real S1 or S2 pod-prefix bytes were read, so the T1 pins were exercised against the real receipt bytes only up to the listing comparison (`test_locator.sh` P1R), and the full S02 path with the real pins has not run end to end anywhere. `s3api list-objects-v2` needs `s3:ListBucket`, the same permission as `aws s3 ls`; the executor identity's policy was not queried.

### filed_before_affected_data qualification (DEC-20261107-a83c51, copied verbatim)

> For S1, filed_before_affected_data is qualified. Before the filing, S1's job-exit fields, the sizes of run-summary.json and records.jsonl, and the PD-1 audit and run.stderr counts had been read. No records.jsonl line, arm statistic, ratio, compare output or parity field had been read. The audit pass bit was already implied by the container exit 42 (run-ecbench exits 41 on an audit failure before 42). S1's bytes are bound to the launcher's 02:14:21Z objects.json by K-2.

## 11. Open blockers (by name)

- **B-K7-TRANSPORT-ENV** (decide before the red-team reconfirmation is dispatched, because it changes the three-script bytes): the K-7 allowlist drops `HTTPS_PROXY`, `https_proxy`, `NO_PROXY`, `no_proxy` and `AWS_CA_BUNDLE`, which this container needs to reach AWS (names only: the first three of those and `AWS_CA_BUNDLE` are set here). In a proxy-only network S02 stops at its first aws call. Decide: add the names to `K7_PASS_VARS` in both prologues (one array line each; widens the allowlist by five names) or run S02 where no proxy is needed.
- **B-K7-CRED-NAMES**: `K7_CRED_VARS` is `AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN`, my choice (section 9 item 1). If the executor identity uses other variables (`AWS_WEB_IDENTITY_TOKEN_FILE`, `AWS_ROLE_ARN`, `AWS_CONTAINER_CREDENTIALS_*`, `AWS_PROFILE`), the Coordinator names them.
- **B-K7-CFG-ALLOWED**: `K7_CFG_ALLOWED` is empty (section 9 item 3).
- **B-BASH-ENV-FIRST-SHELL**: BASH_ENV in the caller's environment is sourced by the caller's bash before the script's first line; only `bash -p` in the runbook S02 argv and the plan's trial argv (both outside what I may choose) would close it (section 10).
- **B-K8-READ-ONLY-IAM**: no read-only IAM identity for S02 (owner-side change); DEC-20261107-7802ec states the residual risk (section 10).
- **B-RED-TEAM-RECONFIRM**: the independent red-team reconfirmation of the v3c bytes (follow_on of this handoff; DEC-20261107-a83c51 `reconfirmation`) has not happened; no `runbook_sha256` can be named before it. It should re-run `tests/rt_regression.sh`, try to break K-1, K-2 and K-7, and exercise the real aws CLI surface that these tests could not (section 10).
- **B-AMENDMENT-2-WORDING**: v3c narrows C1-AMENDMENT-2's "results_uri as is" (section 9 item 8); the decision that approves the runbook should acknowledge it.
- **B-FILED-BEFORE-AFFECTED-DATA**: the qualification text of section 10 must be in DEC-20261107-7802ec and in the evidence review_plan's blindness joint, verbatim.
- **B-CANONICAL-SPEC-STATE**: the canonical specification and trial plan are review_required and candidate-only drafts; the approved forms exist only under `design/d07e94/approval-preview/`. The approval archive swaps them in at the canonical paths; their digests are the ones the runbook binds. Until then `runbook.py lint` of the real tree reports exactly the four findings of section 8, and `task_card.py lint` reports the runbook findings.
- **B-NOT-PUSHED**: the packet's four blockers (section 8) clear only after the archive commit is on `origin/main`.
- **B-QUEUE-ENTRY**: `dispatch_queue.json` has no entry for `TASK-20261107-f14df8` or `TASK-20261107-04d969` until the approval archive adds them (preview in `handoff-previews/`).
- **B-CARD-APPROVAL**: card -4 fails lint only on the missing committed approval decision naming the runbook sha256 (in the approved-state layout).
- **B-IN-PLACE-REPLACEMENT**: the artifact paths replace `launch_eks.sh`, `locate_results.sh`, `reconcile_run.sh`, `runbook.yaml`, `specification.yaml`, `trial-plan.json` in place. The stopped session `RBS-ICPERF-de8978` (and its journal) binds the old bytes, so `runbook.py verify`/`audit` of that session against the new tree will report changed bound files. No session or run directory was touched.
- **B-SNAPSHOT-RECEIPT**: `coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-0e0902/archives/TASK-20261107-d07e94/snapshot-receipt.json` is written by the coordinator's archive step (commit-bound, `dispatcher_verified false`); it does not exist and the director cannot write it.
- **B-S1-COPY-CUSTODY**: unchanged from c5a0f4: the reconciled S1 copy (about 96 MB) lands under `runbook-sessions/RBS-ICPERF-616277/outputs/S02-reconcile-t1/attempt-1/`; its compaction and custody are the Coordinator's.
- **B-OWNER-NOTICE**: the four-fact notice and the owner's EKS go-ahead are for the top-level session before the relay; the notice now says S2 runs on v3c.
- **B-CRYPTO-PR**: the crypto change for AMENDMENT-2 still needs its own Conductor task and ready-for-review PR (not opened).
- **B-SESSION-LOG**: `docs/session-logs/2026-11-07.md` was not written by this subagent (outside its write scope).

## 12. What was not done or read

No `git add`, commit or push; no PR; no AWS or kubectl or CodeBuild call; no `runbook.py run`; nothing under `runs/` or `runbook-sessions/` written; no ledger, queue, journal, session log or 9d2b6a file edited (the queue change is a preview file); `docs/session-logs/2026-11-07.md` was not written (outside this task's write scope). No records.jsonl, audit, replay, run log, arm statistic or ratio was opened. No pod-uid prefix was read; `scratchpad/dl-8b0d47-receipt/` was not opened. Running the repository linters created gitignored `__pycache__` directories under `tools/` and `orchestration/` (outside the write scope, ignored by git, not staged). Scratch layouts used for simulations (`d07-stageA`, `d07-stageB`, `d07-stageC`) are in the scratchpad, are not records, and were never pushed.
