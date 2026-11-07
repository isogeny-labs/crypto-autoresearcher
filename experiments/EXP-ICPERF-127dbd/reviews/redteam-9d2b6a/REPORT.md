# Red-team review TASK-20261107-9d2b6a: the C1 results locator (EXP-ICPERF-127dbd)

> Archive note (written by the top-level session acting as the coordinator-role archiver, not by the reviewer). The reviewer's runtime did not allow a subagent to write a report file, so it returned this report as text. This file contains that text, with no change of substance. The archiver re-ran `fixtures/rt_harness.sh` under the same env -i isolation (`command -v aws` gave the fake; `env | grep -c AWS_` gave 0). The verdict column of the new `rt-results.tsv` was identical to `evidence/rt-run/rt-results.tsv` for every case.

**Verdicts:**

| question | verdict | severity |
|---|---|---|
| (a) foreign, stale or attacker-placed prefix | conditional | fix before S2 |
| (b) job_completed or exit 0 without this pod's own accepted job-exit.json | conditional | fix before S2 |
| (c) can reconcile_run.sh submit or write | conditional | note |
| (d) `filed_before_affected_data: true` | conditional: holds only with the AMENDMENT-2 disclosure, must be qualified | fix before S2 (a qualifying record, no protocol edit) |

**test_locator.sh re-run:** 117 pass, 0 fail, 0 skip. It ran under the isolated environment with OUTDIR `evidence/test_locator-rerun/out` and the checkout argument `/home/user/crypto` (HEAD fe538b2dc8, whose four launcher scripts match the pins), so the dry-run case ran. The fake logged 123 calls, all reads.

**No input changed.** At the end, the three script hashes are identical in the worktree, at f1c5a7faa3 and at 0ea4ca81d0:
- launch_eks.sh `f93e8858…`
- locate_results.sh `efcc2983…`
- reconcile_run.sh `eac18f21…`

`git status` showed only the untracked `reviews/` directory, and HEAD was f1c5a7faa3.

Nothing in this report is about a C1 outcome.

---

## 0. Isolation and order of work

**No AWS.** `/usr/bin/aws` and `/bin/aws` are absent (`/bin` links to `usr/bin`). Every command that executed a C1 script ran under `env -i HOME TMPDIR=<scratchpad>/tmp PATH=<review>/evidence/isobin:/usr/bin:/bin`.
- In that environment `command -v aws` is `evidence/isobin/aws`, a link to `implementation/tests/fake-aws`, and `env | grep -c AWS_` is `0` (`evidence/00-isolation.txt`).
- The harness refuses to start otherwise.
- The fake logged 372 calls in the harness. Every one was `s3 cp s3://… <local>`, `s3 ls s3://…` or `codebuild list-builds-for-project`, except the attack payloads in (c), which the fake refused.

**Reads avoided.** Nothing under any pod-uid prefix was read, and `dl-8b0d47-receipt/` was not opened. No records.jsonl, audit, replay, run log, arm statistic or ratio was read.

**Order.** (a) to (c) were answered from the code and the reviewer's own fixtures. Those verdicts were written to `evidence/verdicts-before-findings.txt` at 04:06:10Z, and only then was FINDINGS.md opened.

**Harness.** `fixtures/rt_harness.sh` builds each case from the launcher receipt shape plus a synthetic job output set that check_job.py accepts.
- It runs a hash-checked copy of v3b with fake-launch-remote, runs reconcile_run.sh in place, and runs check_job.py on the download.
- It evaluates S03 validity as transcribed from runbook.yaml lines 343-402. That is a transcription, not tools/runbook.py.
- Results are in `evidence/rt-run/rt-results.tsv` (run 3, 69 rows).
- Generated trees were pruned and hashed in `cases/<id>/pruned-files.sha256`. They regenerate byte-identically (`evidence/rt-run-determinism.txt`: 68 cases, 0 differing inputs).

**Severity meaning.** "Fix before S2" means S02 and S03 should not run on these bytes unchanged. Because both steps are in one runbook, a fix needs new bytes and a new runbook_sha256 before DEC-20261107-7802ec names it, unless the Coordinator accepts the risk in writing. Nothing is rated "blocks approval", because every break needs someone other than the job and the pinned launcher to write to the bucket. None of them is reachable from genuine pinned-launcher bytes (A00, A04).

---

## (a) Foreign, stale or attacker-placed prefix — conditional, fix before S2

**What holds (rule (b), the failed-Job path):**
- A `receipt_uri` pointing at another job, using `../`, in another bucket or deeper than the launcher directory is refused with locator exit 12 (A06a-d).
- A pod uid containing `../`, a slash, 35 characters or upper case is refused with exit 15 (A07a-d).
- A status.json job uid or job name that differs, 0 pods or 2 pods are refused with exit 14 or 15. Reconcile returns 4 (A12a-d).
- A sibling prefix `<uid>0/` gives a third listing entry and is refused with exit 16 (A05).
- objects.json listing a key outside launcher/ and the pod prefix is refused by R-3 with exit 5 (A09e).
- A pod prefix that appears late, after the listing, is never downloaded (A10).

**Break 1 — rule (a) binds whatever URI result.json names.**
- *How it is reached.* A non-empty `.results_uri` selects rule (a). Rule (a) checks nothing: not the bucket, the job, the pod, the listing or the job-exit. On the failed path, launch-remote never authenticates result.json: it downloads it from the S3 receipt (line 50) and checks it only when the build is SUCCEEDED (lines 52-57). The class logic still accepts (launcher exit 26, FAILED, 42 or 43) under rule (a).
- *Input (A01).* S2 request. result.json has `results_uri=s3://…/runs/ic-c1-dg-s2-20261106/0bbbbbbb-…/` and pod_uid 0bbbbbbb. Launcher exit 26, build FAILED. The genuine pod prefix also exists, next to an attacker-placed, self-consistent set that claims s2, 0bbbbbbb and exit 42.
- *Output.* v3b exits 0 with `job_completed`, `results_locator launcher_result`. check_job.py prints `CHECK_JOB_OK`. S03 validity passes.
- *Cross-job variant (A02).* result.json names S1's prefix. v3b gives job_completed and validity still passes, because the pattern `s[12]` admits s1. check_job.py catches it (job_name and spec FAIL).
- *Other-bucket variant (A03).* v3b gives job_completed. Only the validity regex catches it.
- *The pinned launcher's own exit-26 shape with a non-empty results_uri (A04)* (`state verification_failed`, naming the exit-0 pod) is correctly refused as class `other`.

**Break 2 — the content under the correct prefix is not bound to the launcher's snapshot.** The launcher's objects.json lists Key, Size and ETag for all 19 keys at 02:14:21Z. Reconcile downloads it but uses it only to check that keys are under the right prefixes.
- *A09a.* An added session/extra.json after the snapshot, with SHA256SUMS regenerated. Reconcile exits 0, `reconcile_pass true`, CHECK_JOB_OK.
- *A09b.* audit.stderr replaced (8 bytes became 37) the same way. Same result.
- *A10 (TOCTOU).* A write between the listing and the download. Both v3b and reconcile accept it.
- *Control.* Compare the downloaded (Size, MD5, path) set with objects.json (Size, ETag, Key). It needs no AWS call. It reports `DIFFERS` on A09a/b and A10 and `same` on the genuine shape A00.

**Notes:**
- A06e: a `receipt_uri` naming a second launcher id, not the build that ran, is accepted.
- A06f: a launcher id of 36 dashes is accepted.
- A07e: a trailing newline in the pod uid is silently stripped.
- A08: `restartCount` 2 with a non-empty `lastState` is accepted. The observed template (restartCount 0 after exit 42) implies restartPolicy Never, so this is unreachable today.
- A09c: objects.json without an `.objects` array passes R-3 vacuously.
- A09d: a truncated listing (`next_token` set) passes R-3.

## (b) job_completed or exit 0 without this pod's own accepted job-exit.json — conditional, fix before S2

**Rule (b) has no break.**
- B01-B11: job-exit.json missing, empty, not JSON, a directory, `"42"`, true, false, null, 42.5, 42.0 or `[42]`. None gives job_completed or exit 0.
- B16a-c: job-exit.json from another pod, another job, or with exit ≠ container exit. v3b gives `other`, reconcile exits 7.
- B13 pairing matrix: job_completed only for (26, FAILED, 42/43). TIMED_OUT gives deadline_hit.

**Breaks on rule (a):**
- A01: another pod's job-exit.json gives exit 0.
- B12a: exit_code `"0"` as a string with (0, SUCCEEDED) gives job_completed and exit 0. check_job.py catches it.
- B12b: exit_code `"42"` as a string with (26, FAILED) gives job_completed and exit 0. check_job.py catches it.

**Gap — a partial download still yields job_completed.** The class logic ignores `download_exit` once job-exit.json and SHA256SUMS exist, and S03 validity does not assert `download_exit '0'` (S02 does).
- B14a: a listed file is lost and the download exits 1. v3b gives job_completed and exit 0, validity passes. check_job.py FAILs (missing file).
- B14b: an unlisted object is lost and the download exits 1. v3b gives job_completed, CHECK_JOB_OK, and validity passes.
- Reconcile refuses both (exit 6).

**Notes (crash paths that already exist in v3a, lines 238, 239 and 245):**
- B03: a non-JSON job-exit.json makes v3b exit 5 with no raw-result.json.
- B04: job-exit.json as a directory makes v3b exit 2. The header documents exit 2 as "nothing submitted", so a submitted job would be reported as never submitted.
- B15a-c: a non-JSON or array result.json, or a non-JSON build.json, makes v3b exit 5 with no raw-result.json.
- B13 (0, SUCCEEDED, 0) on the rule-(b) shape gives job_completed. The pinned launcher cannot produce that combination.

## (c) Can reconcile_run.sh submit or write — conditional, note

**The bytes are clean.** C05 finds no submit or write token. The only `source`/`eval` matches are false positives: a comment, and `find .` (C05-static-scan.txt). There are no test hooks; the tests inject only through PATH and CRYPTO_CHECKOUT. Environment variables read: ISOLAB_BUCKET only. Overriding it fails closed with exit 4 and 0 AWS calls (C03). locate_results.sh is executed, not sourced.

**The environment is the gap.** The script does no environment hygiene. Each of these vectors issued `aws s3 cp /etc/hostname s3://…` and `aws codebuild start-build` to the aws on PATH; the fake refused both, and reconcile still passed:
- C01: BASH_ENV.
- C01: an exported function `BASH_FUNC_aws%%`.
- C01: a `python3` shim earlier on PATH.
- C02: CDPATH together with the runbook S02 argv's relative path. `here=$(cd "$(dirname …)" && pwd)` resolves to an attacker directory, so an attacker locate_results.sh runs.

C02b: even `CDPATH=.` makes `here` two lines, and reconcile fails closed with exit 4. The S03 argv is also relative, and launch_eks.sh uses the same idiom for its pins file and locator.

Not exercised: the documented aws-cli configuration surface, because no aws CLI is present here and RT-2 forbids one. `credential_process` runs an external program, aliases support `!` external commands, and `AWS_ENDPOINT_URL_S3` redirects reads to another host. Whether an alias can shadow the `s3` command is not confirmed.

C04: `--out` given as a symlink into a `runs/` directory passes the lexical check and writes there.

**What a structural guarantee would need:** a read-only IAM identity for S02, an `env -i` allowlist, absolute argv paths or `CDPATH= cd --`, and a `realpath` check on `--out`.

## (d) `filed_before_affected_data: true` — conditional, fix before S2

**How the tool treats the flag.**
- `freeze()` records the CLI flag as given and verifies nothing (tools/experiment_protocol.py lines 375-390).
- `protocol_hash` excludes the freeze block (lines 133-136), so the freeze-level flag is bound only by the file's own sha256 (561b6a75).
- lint_protocol turns any `amendments[].filed_before_affected_data: false` into a finding that "the amended cells decide nothing" (lines 330-332).
- validate reports 0 findings (`evidence/D-protocol-validate.txt`; its hash equals the freeze's protocol_sha256 4b7bf35f). So amendments[1]'s flag must also be true. That is an inference: under the read limits, `amendments[]` was not opened.
- D-6 required both "0 findings" and `--filed-before-affected-data`, so `true` was a ruled value, not an independent determination.

**What "affected data" means.** docs/experiment-protocol.md line 37 says an amendment "says whether it preceded the data it affects", and the rule exists to guard against silent edits and predictions re-dated after the fact. So affected data are the observations whose admission or analysis the amended text governs.

**Applied to AMENDMENT-2.**
- Part (b) governs S1's admission. S1's output existed from about 02:14:21Z (objects.json LastModified), roughly 40 minutes before the freeze at 02:54:43Z.
- Before the filing, S1 data had been read out of band: job-exit.json fields, the size of run-summary.json and records.jsonl (DEC-20261107-b74e2c rulings 2 and 5), and PD-1's audit and run.stderr counts.
- On the literal reading, `true` is false for S1 and true for S2.

**Ruling.** The flag holds only in the narrower scope that AMENDMENT-2 states: no S1 records.jsonl content, arm statistic, ratio, compare output or parity field was read. Wherever the bare boolean is consumed without that text, it must be qualified.

That scope is defensible for two reasons:
- In run-ecbench at the pinned source revision ea8e9ef71c, exit 41 (audit) comes before exit 42. So the pass/fail bit that PD-1 read was already implied by the container exit code in the launcher receipt.
- Part (b) only transports data.

But the disclosure's substantive claim, that nothing about S1 could be shaped after the fact, assumes S1's bytes are still those of 02:14:21Z, and reconcile does not check that (A09). The title phrase "before any S1 record is read" is accurate only if "record" means a records.jsonl line.

**Remedy.** Put the qualified scope in DEC-20261107-7802ec and in the evidence review_plan's blindness joint, and bind S1's bytes to objects.json. Do not edit the frozen protocol.

---

## Where I disagree with FINDINGS.md

1. **§8.2, "Rule (a) is 'as is' with no check, as in v3a. Each extra check only narrows what is accepted."** Matching v3a is not a safety argument. Rule (a) is chosen by a field that is unauthenticated on the failed path and skips every check rule (b) needs. A01 is accepted by v3b, by check_job.py and by S03 validity.
2. **§8.3, the objects.json size comparison "removed to avoid a false stop; byte integrity is check_job.py's".** SHA256SUMS sits in the same prefix and certifies itself. objects.json is the only snapshot of the prefix written by someone other than the job, and the S1 prefix stayed writable for more than a day, with out-of-band reads by a session holding write-capable credentials (PD-1). The false-stop risk was not quantified. S3 has been strongly read-after-write consistent since December 2020, and the launcher lists the prefix after the container has terminated. The control gives `same` on the genuine shape (A00).
3. **§4 and the mutation evidence.** All negative cases are rule (b). There are none for rule (a), for receipt_uri, for the uid regex, for the objects.json key check (A09e here), for restartCount, for a partial download or for the crash paths. mutation-sensitivity.txt does not mutate receipt_uri, the uid regex, the objects.json check or the {0,42,43} set. So "every safeguard … makes at least one case fail" holds only for the mutated subset.
4. **§8.6, "the results_uri pattern is kept as D-3 requires".** The pattern admits S1 prefixes for T2 (A02). D-3 required keeping it, but `by_trial` could still pin T2 to s2.
5. **P2, "no receipt object read (rule (a) makes no AWS call of its own)".** It is presented as a property. It is the gap in Break 1.
6. **B-FILED-BEFORE-AFFECTED-DATA, "true is as ruled".** Agreed it was ruled. The answer is (d): it holds only with the disclosure and must be qualified.
7. **Agreed:** 117 pass and 0 fail (reproduced), the input hashes, a v3a-to-v3b diff confined to section 3 (`evidence/v3a-to-v3b.diff`), and no AWS call during the tests.

## Required controls, cheapest first

**Next concrete action.** Before naming runbook_sha256, the Coordinator rules on these changes and then re-runs test_locator.sh plus the harness cases A01, A02, A09a, A09b, A10, B14a and B14b:
1. locate_results.sh applies the receipt rule (status.json, the listing and verify) to every outcome. A non-empty results_uri is accepted only if it equals the located `s3://BUCKET/runs/JOB/<pod_uid>/`.
2. reconcile_run.sh (and v3b) compare the downloaded (Key, Size, ETag) set with objects.json. They require `.objects` to be non-empty and `next_token` to be null.
3. S03 validity adds `download_exit '0'` and pins T2's results_uri to s2.

Further hardening:
- Write raw-result.json even when post-submission parsing fails, and never exit 2/3/4 after a submission.
- Require `restartCount == 0`.
- Use `CDPATH= cd` or absolute argv paths.
- Give S02 a read-only identity.
- Record the (d) qualification in DEC-20261107-7802ec.

## Procedure deviations

- **PD-RT-1.** The partial-download and TOCTOU cases used `fixtures/isobin-wrap/aws` (sha256 bbaf62de). It is a wrapper that passes every call to tests/fake-aws by path and then simulates a failed object or a write by a third party. It is not an aws client.
- **PD-RT-2.** Harness run 1 was invalid: a bug fed the genuine job-exit.json to B16a and B16b. It is kept as `evidence/rt-run-1-invalid.tar.gz`. Its NOTE still says "superseded by evidence/rt-run (run 2)"; that run is now `rt-run-2-superseded.tar.gz`, which is valid and differs from run 3 only by the added case A09e.
- **PD-RT-3.** Reads beyond the declared inputs, to test named assumptions:
  - crypto launch-remote (who writes the client result.json);
  - run-ecbench lines 1-35 and 114-146 at HEAD and at ea8e9ef71c (the job-exit shape and the order of exit codes);
  - validate-request (grep only);
  - schemas/experiment-protocol.v1.json (only the amendments and freeze definitions);
  - FINDINGS evidence files dry-run-plan-argv.txt and mutation-sensitivity.txt (after recording the verdicts);
  - AWS documentation on endpoints, aliases and credential_process, via web search.
- **PD-RT-4.** `experiment_protocol.py validate` and `hash` were run locally under env -i.
- **Not read:** trial-plan.json (so check_job.py's argv in S03 was not checked; this relies on the runbook's "followed by check_job.py"), tools/runbook.py and its environment handling, specification.yaml, DEC-20261107-e41c08, DEC-20261107-6b0f3d.
- **Not done:** no session log (outside the reviewer's write scope), and no research-kb queries; this is a code review with no novelty claim.

## red_team_report

```yaml
red_team_report:
  id: RT-20261107-9d2b6a
  task_id: TASK-20261107-9d2b6a
  claim_under_review: "locate_results.sh / launch_eks.sh v3b / reconcile_run.sh cannot bind wrong bytes, report job_completed without this pod's job-exit.json, or submit; and the C1-AMENDMENT-2 freeze flag filed_before_affected_data is true"
  objections:
    - "Rule (a) is selected by an unauthenticated results_uri and binds any URI with no identity check; it accepts (26, FAILED, 42/43). A01 passes v3b, check_job.py and S03 validity."
    - "Content under the located prefix is not compared with the launcher's objects.json (Key/Size/ETag); A09a, A09b and A10 are admitted."
    - "S03 validity does not assert download_exit '0', and its results_uri pattern admits s1 for T2 (B14a, B14b, A02)."
    - "The read-only property is textual. BASH_ENV, an exported function, PATH and CDPATH (with the relative argv) each reach aws with a write and a start-build (C01, C02)."
    - "filed_before_affected_data is an unverified operator assertion that protocol_hash does not cover. S1 data existed and was partly read before the filing."
  required_controls:
    - "Compare the downloaded (Size, MD5/ETag, Key) set with objects.json; zero AWS calls. It reports same on A00 and DIFFERS on A09a, A09b and A10."
    - "Rule (a) only when results_uri equals s3://BUCKET/runs/JOB/<pod_uid>/, with the listing and verify applied."
    - "S03 validity: download_exit '0', and T2 results_uri pinned to ic-c1-dg-s2-20261106."
  counterexample_or_mutation: "fixtures/rt_harness.sh cases A01, A09a, B14b and C02; outputs in evidence/rt-run/cases/<id>/"
  baseline_comparison: "not applicable (transport joint; no cost claim)"
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges:
    - "(d): affected data per docs/experiment-protocol.md line 37 includes S1 (AMENDMENT-2 part b). The flag holds only in AMENDMENT-2's disclosed scope and must be qualified in DEC-20261107-7802ec."
  proof_architecture_challenges: []
  narrowest_supported_statement: "For genuine pinned-launcher receipts, the locator binds the one named pod prefix, v3b's rule (b) needs that pod's verified job-exit.json, and the reconcile bytes issue only S3 GET/List. There is no defence against a bucket writer after the job, and read-only is not enforced."
  next_concrete_action: "Coordinator rules on the rule-(a) unification, the objects.json binding and the two S03 validity assertions, then re-runs test_locator.sh plus harness cases A01, A02, A09a, A09b, A10, B14a and B14b, before naming runbook_sha256."
  artifact_paths:
    - experiments/EXP-ICPERF-127dbd/reviews/redteam-9d2b6a/SHA256SUMS
    - experiments/EXP-ICPERF-127dbd/reviews/redteam-9d2b6a/fixtures/
    - experiments/EXP-ICPERF-127dbd/reviews/redteam-9d2b6a/evidence/
  review_attestation:
    joints_owned: [a-locator-binding, b-job-completed, c-no-submit, d-filed-before-affected-data]
    read_sibling_reports: false
    producer_findings_read_after_verdicts: "design/c5a0f4/FINDINGS.md, opened after 2026-11-07T04:06:10Z"
    verdicts: {a: conditional, b: conditional, c: conditional, d: conditional}
```

Sources consulted by the reviewer (PD-RT-3):
- AWS SDK reference, service-specific endpoints: https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html
- AWS CLI, creating and using aliases: https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-alias.html
- AWS CLI, sourcing credentials with an external process: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html
