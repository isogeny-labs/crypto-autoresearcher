# FINDINGS: TASK-20261107-5f7d2b (EXP-ICPERF-127dbd, C1 launcher v3d, re-session RBS-ICPERF-616277)

Author: experiment-director (Sonnet 5.5), 2026-11-07, detached sparse worktree of crypto-autoresearcher at main d9a8ecd08b7a14b0ea07d5d9b075711c406f875b (after #3144 and #3146).
Zero runs, zero launches, zero AWS calls of any kind (read-only calls included), no call through the platform proxy. Previews only: nothing is staged, committed or pushed, no ledger record, queue, journal or run directory was edited, nothing under the 9d2b6a review tree or the d07e94 design tree was changed, nothing was written under /root/.ccr.
No C1 outcome is in this file, and none was read. Every number below is copied from a named file in `evidence/` or from the command output saved there. This task approves nothing and names no runbook_sha256.

## 0. Return block

| item | value |
|---|---|
| FINDINGS.md | `experiments/EXP-ICPERF-127dbd/design/5f7d2b/FINDINGS.md` (this file); `SHA256SUMS` beside it lists every deliverable file |
| launch_eks.sh v3d | `05580b585f36da483656f6d88487e21a32ff2a7a42cc2021fef4c539096e9b38` (v3c `a61c55da...`) |
| reconcile_run.sh v3d | `4664fa295b6f3b517f9e9bb3a8d7b8eb168e6af186b45cbaf463dc1d18786e31` (v3c `a294b7db...`) |
| locate_results.sh | `668a424be9f55c605dd907561fdda9ec6f9ef3c20a08b3cfb1c5c4221110791b` (byte-identical to v3c; not in artifact_paths) |
| runbook.yaml | `40b4b4bcbc69bc566621e977a83c7abb2621550389e45ff2b2cec68985e64a98` (v3c `36105be6...`) |
| card | `task-cards/CARD-EXP-ICPERF-127dbd-5.yaml` sha256 `19f10cabad1120b06d0ac579f640d9af2c4ecaf3d164101d7d092ef4f31d3039`; card -4 is untouched, retired, never relayed |
| V-5 argv outcome | ABSOLUTE `/bin/bash`, `-p`, then the script, in S01-probe, S02-reconcile-t1, S04-verify and the T2 trial argv. `runbook.py lint` and the supervisor's plan admission (`experiment_execution.load_plan`) accept the absolute argv[0]; the A-2 fallback (`bash`, `-p`) was NOT taken (section 6) |
| PY-1 | APPLIED. The first aws on the relay PATH (`/tmp/claude-0/awsvenv/bin/aws`) imports botocore from its venv (`awscli.botocore`), not from the user site; the omission condition is not met and no omission residual is recorded (section 5.2) |
| test_locator.sh (OUTDIR, checkout argument `/home/user/crypto`) | 156 pass, 0 fail, 0 skip (`evidence/test_locator-RESULTS.txt`) |
| rt_regression.sh | 259 rows: the 123 v3c rows (all keep their v3c expected outcome and observed outcome, 123 of 123 identical) plus 136 new rows (D01 to D16); 0 differ; legacy replay (v3b scripts): 123 rows, 123 identical to the d07e94 legacy table, unchanged |
| mutation_check.sh | 82 mutants (32 of d07e94, 50 new): 80 CAUGHT, 2 SUBSUMED; baseline clean; 0 survived or errored (section 8; the first pass found one survivor, `K7-allowlist`, which I fixed in the test and re-ran from the start) |

## 1. Ids (unchanged; all still unused)

`RBS-ICPERF-616277` (runbook session), `RUN-ICPERF-efb7ef` (T2; T1 is the reconciliation of the consumed `RUN-ICPERF-8b0d47`), `TASK-20261107-f14df8` (executor handoff preview), `TASK-20261107-04d969` (snapshot handoff preview), `DEC-20261107-7802ec` (reserved approval id, not a record). The only new id is the card `CARD-EXP-ICPERF-127dbd-5`. Protocol version 3, `protocol_sha256` `4b7bf35f34c0ddf5c0e4bee95e1791e6f5d2bc2fb68d4836db9db53d33e9b9cc`; not edited.

DP-1 was re-checked first (`sha256sum` of the worktree files against the d07e94 receipt): launch_eks.sh `a61c55da15b149d00ee7e644c41d79ad8df4ae82f3c59dfca157ea9679fc9e76`, locate_results.sh `668a424be9f55c605dd907561fdda9ec6f9ef3c20a08b3cfb1c5c4221110791b`, reconcile_run.sh `a294b7dbc77b33ae4103dfa907a5effba03fe0e2c1837f3f51a44a5897055c16`: all three equal. check_job.py `d60564dd...`, probe_s01.sh `3d1826e4...` and remote-pins.sha256 `7b753189...` also equal the receipt/handoff values.

## 2. Hashes

Every value is `sha256sum` of the file now in the worktree (the full list is `SHA256SUMS`).

| file | sha256 |
|---|---|
| implementation/launch_eks.sh (v3d) | `05580b585f36da483656f6d88487e21a32ff2a7a42cc2021fef4c539096e9b38` |
| implementation/reconcile_run.sh (v3d) | `4664fa295b6f3b517f9e9bb3a8d7b8eb168e6af186b45cbaf463dc1d18786e31` |
| implementation/locate_results.sh (UNCHANGED, v3c) | `668a424be9f55c605dd907561fdda9ec6f9ef3c20a08b3cfb1c5c4221110791b` |
| runbook.yaml | `40b4b4bcbc69bc566621e977a83c7abb2621550389e45ff2b2cec68985e64a98` |
| task-cards/CARD-EXP-ICPERF-127dbd-5.yaml | `19f10cabad1120b06d0ac579f640d9af2c4ecaf3d164101d7d092ef4f31d3039` |
| specification.yaml (canonical draft, review_required) | `d4b0d1aeec2441d78d59fd75795fb4ab533a8385539791f6b0f279a85c1b6023` |
| trial-plan.json (canonical draft, candidate_only) | `53efb5682bc1a26a9f1089ef4ad8af66d4d46560e94eecbf31caa2ee9b388a12` |
| design/5f7d2b/approval-preview/specification.yaml (approved form, PREVIEW) | `de94c9ef039937c4d1c9097bef753306d9617f8192d87a2dd52c53669acf95e7` |
| design/5f7d2b/approval-preview/trial-plan.json (approved form, PREVIEW) | `45f58da0b4e9307b4bc9dd73582d514c746d06b6864dde3a3dfdf4fe68cc890c` |
| design/5f7d2b/handoff-previews/TASK-20261107-f14df8.yaml (executor) | `bad29976a5c7990808f6b88ca2c79d5161ae92ef93d8bc804380a34910bcd4fd` |
| design/5f7d2b/handoff-previews/TASK-20261107-04d969.yaml (snapshot) | `d3a790c13624f927f5bae1285ab70e4231c141b5f516d89b4e7ffec681d13412` |
| design/5f7d2b/handoff-previews/dispatch_queue.json (queue preview) | `6ec416772237646208a31b15a42523fbb95e673f0fe16fa2b22569414286f654` |
| runbook-lint.txt | `70f9ffeb1ef5d38c649f2d1810991a3bf7cb1ef9baccd3f030c68b466886faf7` |
| tests/test_locator.sh | `d5d3ef520b3ebdaddff40cd19a056da055e9a153d489a880ea89b3daec538794` |
| tests/rt_regression.sh | `7b24322f7a5615d1fac41133a17394f4aa72539d92c28b1eda381614ae59214a` |
| tests/mutation_check.sh | `7f2685e889cc78eb8087d20cb94d1d0a59eb48ce1f8195b3edee2d5c1be4f9de` |
| tests/mutate.py | `6462e28b1f95443d87c52fe1bf797edaa916a19a1438d43edc23a57c47f2c795` |
| tests/fake-aws | `9e5ec96871923fa7612fc9daf229f1b001cca7c7bfa0e2dadf9a41f33be9a745` |
| tests/fixtures/isobin-wrap/aws | `ea2fd3f4ca389a75e4247b80a1fc71a58a8fc0271993e1377f8a244e9a5d5650` |
| tests/fixtures/{launch_eks,reconcile_run,locate_results}.v3c.sh (new, = v3c) | `a61c55da...` / `a294b7db...` / `668a424b...` (the receipt's v3c values) |

Unchanged and not listed above: check_job.py, probe_s01.sh, remote-pins.sha256, analyze-c1.sh, request-s1/s2.json, spec-c1-s1/s2.json, protocol.json (test_locator.sh asserts the first three).

## 3. What v3d changes (DEC-20261107-c3e91a R-1 to R-3), and where each control is tested

Both scripts carry the same prologue bytes except one array line (`K7_PASS_VARS` names `ISOLAB_CODEBUILD_PROJECT` in launch_eks.sh only). New constants: `K7_CFG_NAMES`, `K7_TRANSPORT_VARS=(HTTPS_PROXY https_proxy NO_PROXY no_proxy AWS_CA_BUNDLE)`, `K7_CA_BUNDLE_ALLOWED=(/root/.ccr/ca-bundle.crt)`, `K7_CONSTS=(AWS_EC2_METADATA_DISABLED=true PYTHONNOUSERSITE=1)`, `K7_PROXY_RE='^http://(127\.0\.0\.1|localhost):[0-9]{1,5}/?$'`, `K7_NOPROXY_RE='^[A-Za-z0-9.,:*/_-]*$'`.

| ruling | implemented as | refusal (exit 2, before any AWS call) text | cases | mutants |
|---|---|---|---|---|
| T-1 names | the five transport names are copied into the `env -i` exec only if set; HTTP_PROXY, http_proxy, ALL_PROXY, all_proxy, REQUESTS_CA_BUNDLE, SSL_CERT_FILE, SSL_CERT_DIR, CURL_CA_BUNDLE are still dropped | - | D01c, D01d, D05 (the aws process sees only `HTTPS_PROXY NO_PROXY PYTHONNOUSERSITE`) | V3d-transport-pass, V3d-transport-allowlist |
| T-2 proxy | pair byte-equal; each set value matches `K7_PROXY_RE`; the value is never printed on refusal | `HTTPS_PROXY and https_proxy differ`; `<name> does not match the loopback proxy pin ... (value not printed)` | D01, D01b to D01d, D02, D03 to D03h | V3d-proxy-pair, V3d-proxy-shape |
| T-3 no-proxy | pair byte-equal; each set value matches `K7_NOPROXY_RE` | `NO_PROXY and no_proxy differ`; `<name> does not match ...` | D04 to D04g | V3d-noproxy-pair, V3d-noproxy-shape |
| T-4 CA bundle | only with `HTTPS_PROXY` or `https_proxy` set; byte-equal to an entry of `K7_CA_BUNDLE_ALLOWED`; `realpath -e` returns the same string; `-f` and `-s`; sha256 computed in phase 2 | `AWS_CA_BUNDLE is allowed only when HTTPS_PROXY or https_proxy is set`; `... is not an entry of K7_CA_BUNDLE_ALLOWED`; `... is missing or its realpath differs`; `... is not a non-empty regular file`; `the sha256 of AWS_CA_BUNDLE could not be computed` | D06, D06b, D07, D07b, D08 to D08e, D09 to D09c, D10 | V3d-ca-needs-proxy, V3d-ca-entry, V3d-ca-realpath, V3d-ca-file, V3d-ca-sha |
| T-5 / CF-1 | `ca_bundle`, `role_arn`, `source_profile`, `credential_source`, `web_identity_token_file`, `sso_session`, `sso_start_url` join the scanned entry names (`K7_CFG_NAMES`; `K7_CFG_ALLOWED` stays empty); names are printed, values never | `aws-cli configuration entry: <name>@config` | D11 (seven names, both scripts), D11b (the container's real `[default] s3` block is admitted) | V3d-cfg-<name> (seven, both scripts) |
| T-6 recording | `K7_STATUS` keeps its prefix and appends ` transport=[names passed] proxy=<value or none> no_proxy=<value or none> ca_bundle=<path or none> ca_bundle_sha256=<hex or none>`; an empty but set NO_PROXY is recorded as `no_proxy=` | - | every `ok:` case compares the line; for reconcile_run.sh the `env_hygiene` field of reconcile-result.json equals the printed line | V3d-status |
| CR-1 | `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` must each be set and non-empty (two separate checks); `AWS_SESSION_TOKEN` stays optional; values never printed | `AWS_ACCESS_KEY_ID is not set or is empty`; `AWS_SECRET_ACCESS_KEY is not set or is empty` | D12 to D12f | V3d-cred-id, V3d-cred-secret |
| CR-2 / PY-1 | the exec adds `AWS_EC2_METADATA_DISABLED=true` and `PYTHONNOUSERSITE=1`. Phase 1 refuses a caller preset of another value (the handoff's V-6 asks for "refused"); phase 2 admits each only set to that value (absent also refuses) | `<name> is set to a value other than its constant <v>` (phase 1); `<name> is not set to its constant <v>` (phase 2) | D13 to D13e, D14 to D14d, D15 (a `.pth` under `$HOME/.local/lib/python3.13/site-packages` runs in a bare python3 and does not run in the aws process) | V3d-const-preset, V3d-const-value, V3d-const-metadata, V3d-const-pyuser |
| A-1 to A-4 | `/bin/bash`, `-p` in S01-probe, S02-reconcile-t1, S04-verify and the T2 trial argv; `environment.programs` lists `/bin/bash` (and no longer `bash`, which no step uses); the prologue comment no longer calls BASH_ENV an unavoidable residual; `python3 -I` stays in the check argv and in reconcile_run.sh | - | D16 (five vectors under `/bin/bash -p`, both scripts) and D16c (the same vectors under plain `bash`, recorded as the pre-v3d control) | (argv, not script bytes; no mutant) |

Test mechanics that a reviewer must know:
- Every run of a script under test carries literal dummy credentials (`AKIDFAKEFAKEFAKEFAKE`, `fakesecretfakesecretfakesecret0000`) and proxy values that point at the dead loopback port `127.0.0.1:1`; the fake aws never opens a socket. No real credential, proxy or endpoint was used. The suites refuse to start when an `AWS_*` variable is in their own environment.
- The allowed CA path is the constant `/root/.ccr/ca-bundle.crt`, which the suite must never write. Cases that need an allowed file the suite can create (D06 to D10) therefore run a test-only copy of the two scripts in which the single line `K7_CA_BUNDLE_ALLOWED=(/root/.ccr/ca-bundle.crt)` holds a path under the run's `ca-fixtures` directory. `mk_ca_impl` asserts that exactly one line differs (`diff | grep -c '^[<>]'` is 2) and aborts otherwise. Cases with another path, with no proxy, and all other cases run the shipped bytes.
- The links created by the suites are relative (`ln -s ../...`); the evidence holds no absolute link.
- D10 injects the fault "sha256sum fails" with a failing `sha256sum` in the trusted aws directory (the directory ahead of `/usr/bin` on the prologue PATH), because no other input makes `sha256sum` fail on a non-empty regular file for root.

## 4. V-2 scope proof (`evidence/test_locator-RESULTS.txt`, groups `v3c-v3d scope` and `v3b-v3d diff`; diffs and hunk lists beside it)

- launch_eks.sh: v3c lines 1 to 32 and v3c lines 97 to the end are byte-identical to v3d (`diff` empty); the prologue starts at line 33 in both; no changed v3c line lies outside lines 32 to 96 (normal-diff old ranges). v3b lines 1 to 32, v3b lines 34 to 233, the outcome-class block and the last three lines stay byte-identical, as in v3c, and the v3b to v3d diff still has exactly three hunks (`evidence/launch_eks.v3b-to-v3d.hunks.txt`: `@@ -30,6 +30,114 @@`, `@@ -232,43 +340,76 @@`, `@@ -288,15 +429,20 @@`; hunk 1 is the prologue).
- v3c to v3d hunks (v3c line ranges; the prologue is v3c lines 33 to 96 in launch_eks.sh and 38 to 101 in reconcile_run.sh): launch_eks.sh `@@ -30,20 +30,29 @@`, `@@ -56,22 +65,53 @@`, `@@ -81,7 +121,7 @@`, `@@ -90,9 +130,13 @@`; reconcile_run.sh `@@ -35,20 +35,29 @@`, `@@ -61,22 +70,53 @@`, `@@ -86,7 +126,7 @@`, `@@ -95,9 +135,13 @@` (`evidence/launch_eks.sh.v3c-to-v3d.diff`, `reconcile_run.sh.v3c-to-v3d.diff` and their `.hunks.txt`). Each hunk lies in the prologue; the context lines outside it are unchanged.
- reconcile_run.sh: v3c lines 1 to 37 and 102 to the end are byte-identical.
- locate_results.sh is byte-identical to v3c (`cmp` empty; sha256 `668a424b...`). check_job.py, probe_s01.sh and remote-pins.sha256 are unchanged. The 19 assertions of the `v3c-v3d scope` group all pass.
- Two things V-2 left unchanged and that are now slightly stale: the launch_eks.sh header comment (before `set +x`) still says "AWS credentials come from the caller's ambient identity", and reconcile_run.sh's header says "(v3c; ...)". Neither is code.

## 5. V-1 local checks and PY-1

### 5.1 Transport names and the CA bundle (`evidence/v1-local-checks.txt`; names and pass/fail only, no AWS_* value)

In the director session's own environment: `HTTPS_PROXY`, `https_proxy`, `NO_PROXY`, `no_proxy`, `AWS_CA_BUNDLE` are set; T-2 pair byte-equal: pass; T-2 shape (both names): pass; T-3 pair and shape: pass; T-4 `AWS_CA_BUNDLE` equals the allowed entry, `realpath -e` returns the same string, non-empty regular file: pass. `HTTP_PROXY`, `http_proxy`, `ALL_PROXY`, `all_proxy`, `SSL_CERT_DIR`, `AWS_SESSION_TOKEN`, `AWS_EC2_METADATA_DISABLED` and `PYTHONNOUSERSITE` are unset; `REQUESTS_CA_BUNDLE`, `SSL_CERT_FILE` and `CURL_CA_BUNDLE` are set (all three would be dropped by the prologue).
`realpath -e /root/.ccr/ca-bundle.crt` prints `/root/.ccr/ca-bundle.crt`; sha256 `f2e3619b6f6b3de595df54e3abf341f3f115470345ee4712e80e89a6c7b19127`; regular file, size 187173, mode 644; neither the file nor `/root/.ccr` is a symlink. Nothing under `/root/.ccr` was written, moved or replaced; the file was only hashed.
This is the director container, not the executor's. Whether the executor's container has the same proxy address and CA path is DEC-20261107-c3e91a's stated assumption; if not, T-2 or T-4 refuses before any AWS call.

### 5.2 PY-1 resolution (`evidence/py1-botocore-origin.txt`)

There is no `aws` on the director session's PATH, but the executor handoff preview already names the relay PATH `PATH=/tmp/claude-0/awsvenv/bin:$PATH`, and that venv exists here. `awsvenv/bin/aws` is a Python script (`#!/tmp/claude-0/awsvenv/bin/python3`, `import awscli.clidriver`); `awscli 1.46.2` vendors botocore as `awscli.botocore` at `/tmp/claude-0/awsvenv/lib/python3.13/site-packages/awscli/botocore`; the venv has `include-system-site-packages = false`, `site.ENABLE_USER_SITE` is False and the user site is not on `sys.path`; the user site (`/root/.local/lib/python3.13/site-packages`) holds no boto, awscli or s3transfer package. The aws executable itself was not run (only the venv's python imported `awscli.botocore`). Therefore botocore is not imported from the user site, the omission condition of PY-1 is false, and `PYTHONNOUSERSITE=1` is applied. For this venv aws it is redundant (the venv already excludes the user site); it closes the vector for an aws whose interpreter has the user site enabled. Consequence worth knowing: if the executor's aws were a pip `--user` install, `PYTHONNOUSERSITE=1` makes `aws --version` fail and the phase-2 version pin refuses (exit 2, fail closed).

## 6. V-5 argv outcome: absolute `/bin/bash`, A-2 fallback not taken

- `python3 tools/runbook.py lint` on the v3d runbook: in the worktree it prints exactly the four findings v3c printed (the two bind mismatches of the canonical drafts, `spec_bindings[1]` approved_by None, the queue entry of TASK-20261107-f14df8) and no finding about `/bin/bash` or `-p`; in the approved-state scratch layout it prints `LINT OK ... sha256 40b4b4bc...` (`evidence/runbook-lint-real-clone-and-approved-state-sim.txt`). `_lint_command` requires argv[0] in `environment.programs` (now `/bin/bash`), `_bound_token` skips `-p` and absolute non-repository paths, and `program_path("/bin/bash")` is `shutil.which`.
- The trial supervisor: `experiment_execution.load_plan` accepts the preview plan (strict, approved form) in the scratch layout and the canonical candidate plan in the worktree; it requires only an argv array of non-empty strings that contains one hash-bound source (here the launch_eks.sh path), and `subprocess.Popen(argv, ...)` runs argv[0] directly (`evidence/supervisor-load-plan.txt`).
- The plan's exact T2 argv with `--dry-run` appended, run from the worktree root under `env -i` (fake aws, dummy credentials, `CRYPTO_CHECKOUT=/home/user/crypto`): exit 0, the `k7_env_hygiene=` line with the new suffix, `remote scripts match 4 pinned sha256 values`, 0 aws calls other than `--version` (`evidence/dry-run-plan-argv.txt`).
- Under `/bin/bash -p` none of BASH_ENV, ENV, an exported `BASH_FUNC_aws%%`, an exported `BASH_FUNC_set%%` or `SHELLOPTS=xtrace` with a PS4 command substitution ran a payload (marker absent, run passes), for reconcile_run.sh and for launch_eks.sh (D16). The plain `bash` control (D16c, the v3c argv) shows BASH_ENV and `BASH_FUNC_set%%` firing before the prologue (marker present) and ENV, `BASH_FUNC_aws%%` and the PS4 vector not firing. The PS4 vector is inert in this container's bash 5.2.21 (an imported PS4 is ignored; `env PS4='X ' bash -xc true` prints `+ true`), so D16/D16c cannot discriminate that vector here; it is recorded, not claimed. `ENV` is never read by a non-interactive bash and `BASH_FUNC_aws%%` is unset by the prologue before aws is called, which is why those two controls also show no payload.
- Not covered by the K-7 prologue (unchanged from v3c, V-2): S01-probe (`probe_s01.sh`, which runs `aws sts get-caller-identity`) and S04-verify (`analyze-c1.sh`) do not re-exec under `env -i`; `-p` closes their shell-startup vectors only. See the residual risks.

## 7. Regression

Commands (each under `env -i HOME="$HOME" TMPDIR=<scratch> PATH=<scratch>/isobin:/usr/bin:/bin`; `isobin` holds two relative symlinks, `aws` -> `tests/fake-aws` and `fake-launch-remote`; `evidence/00-isolation.txt` records `command -v aws` (the fake), `readlink -f` (tests/fake-aws), `env | grep -c AWS_` = 0 and the absence of /usr/bin/aws and /bin/aws): `bash tests/test_locator.sh OUT /home/user/crypto`, `bash tests/rt_regression.sh OUT`, `bash tests/rt_regression.sh OUT x legacy`, `bash tests/mutation_check.sh OUT 3`.

- **test_locator.sh: 156 pass, 0 fail, 0 skip** with the checkout argument `/home/user/crypto` (the 137 cases of v3c all unchanged, plus the 19 assertions of the `v3c-v3d scope` group; `evidence/test_locator-RESULTS.txt`, `test_locator-output.txt`, `exit-statuses.txt`).
- **rt_regression.sh: 259 rows, 259 PASS, 0 differ** (`evidence/rt-results.tsv`, `rt-summary.txt`, `rt-header.txt`, `rt-output.txt`): the 123 rows of the v3c table (below) and the 136 new rows (section 7.2). `C05-static-scan` is among the old rows: 0 submit/write tokens in reconcile_run.sh and locate_results.sh (`evidence/rt-C05-static-scan.txt`).
- **Legacy replay** (`rt_regression.sh OUT x legacy`: the three v3b scripts through the same harness): 123 rows; every row has the same outcome, expected and verdict as in the d07e94 legacy table (123 of 123 identical; `evidence/rt-results-legacy-v3b.tsv`). The new section (d) is skipped in legacy mode because the v3b scripts have no v3d prologue. The suite exits 12 in legacy mode, as it did in d07e94 (rows whose 9d2b6a verdict is not the v3b-replayed one; unchanged).
- Changes to the pre-existing rows' mechanics (none changes an expected outcome): dummy credentials on every run (`RT_CREDS_DEFAULT`); `C10-credentials-by-name` now expects the aws process to see `AWS_EC2_METADATA_DISABLED` as well (and `fake-aws` logs `AWS_[A-Z0-9_]*`, so the digit in the name is not cut); `fake-aws` also logs an `ENVOTHER` line (names only) which the call counter ignores; `mk_bin` creates relative symlinks; `RT_BASH` and `RT_XIMPL` hooks; `fixtures/isobin-wrap/aws` gained a `pyprobe` mode (starts `python3 -c pass` inside the aws process); the internal mode label stays `v3c` and `v3d` is accepted as its alias.

### 7.1 The E-4 table of v3c: all 123 rows (expected outcome at v3c = expected outcome now; observed outcome now)

| case | expected (v3c and v3d) | observed now | verdict |
|---|---|---|---|
| A00-control-T1-shape | control | control | PASS |
| A01-ruleA-sibling-prefix | holds | holds | PASS |
| A01b-ruleA-sibling-prefix-with-receipt | holds | holds | PASS |
| A01c-ruleA-uri-equals-located | control | control | PASS |
| A01d-ruleA-uri-located-poduid-differs | holds | holds | PASS |
| A02-ruleA-cross-job | holds | holds | PASS |
| A02b-ruleA-cross-job-with-receipt | holds | holds | PASS |
| A03-ruleA-other-bucket | holds | holds | PASS |
| A03b-ruleA-other-bucket-with-receipt | holds | holds | PASS |
| A04-ruleA-verification-failed-genuine | holds | holds | PASS |
| A04b-ruleA-verification-failed-with-receipt | holds | holds | PASS |
| A05-uid-prefix-sibling | holds | holds | PASS |
| A06a-receipt-other-job | holds | holds | PASS |
| A06b-receipt-dotdot | holds | holds | PASS |
| A06c-receipt-other-bucket | holds | holds | PASS |
| A06d-receipt-deeper | holds | holds | PASS |
| A06e-receipt-second-launcher-id | refused | refused | PASS |
| A06f-receipt-id-all-dashes | refused | refused | PASS |
| A07a-poduid-dotdot | holds | holds | PASS |
| A07b-poduid-slash | holds | holds | PASS |
| A07c-poduid-35 | holds | holds | PASS |
| A07d-poduid-upper | holds | holds | PASS |
| A07e-poduid-trailing-newline | refused | refused | PASS |
| A12a-status-job-uid | holds | holds | PASS |
| A12b-status-job-name | holds | holds | PASS |
| A12c-two-pods | holds | holds | PASS |
| A12d-zero-pods | holds | holds | PASS |
| A08-restart-count | refused | refused | PASS |
| A08b-restart-count-only | refused | refused | PASS |
| A08c-laststate-only | refused | refused | PASS |
| A09a-added-object | holds | holds | PASS |
| A09b-replaced-object | holds | holds | PASS |
| A09c-objects-json-vacuous | holds | holds | PASS |
| A09c2-objects-json-empty-array | holds | holds | PASS |
| A09d-objects-json-truncated | holds | holds | PASS |
| A09e-objects-json-key-outside | holds | holds | PASS |
| A09d2-objects-json-next-token-only | holds | holds | PASS |
| A09j-objects-json-no-pod-entries | holds | holds | PASS |
| A09f-objects-json-missing-etag | holds | holds | PASS |
| A09g-objects-json-extra-entry | holds | holds | PASS |
| A09h-multipart-etag-size-only | control | control | PASS |
| A09i-multipart-size-changed | holds | holds | PASS |
| A10-toctou-after-listing | holds(prefix)/ok | holds(prefix)/ok | PASS |
| A10b-toctou-after-pod-listing | holds | holds | PASS |
| A13a-pin-status-wrong | holds | holds | PASS |
| A13b-pin-objects-wrong | holds | holds | PASS |
| A13c-receipt-object-too-new | holds | holds | PASS |
| A13d-pod-object-too-new | holds | holds | PASS |
| A13e-receipt-lastmodified-missing | holds | holds | PASS |
| B01-jobexit-missing | holds | holds | PASS |
| B02-jobexit-empty | holds | holds | PASS |
| B03-jobexit-not-json | holds | holds | PASS |
| B04-jobexit-is-directory | holds | holds | PASS |
| B05-exit-string-42 | holds | holds | PASS |
| B06-exit-true | holds | holds | PASS |
| B07-exit-false | holds | holds | PASS |
| B08-exit-null | holds | holds | PASS |
| B09-exit-42.5 | holds | holds | PASS |
| B10-exit-42.0 | holds | holds | PASS |
| B11-exit-array | holds | holds | PASS |
| B11b-exit-exponent | holds | holds | PASS |
| B11c-exit-negative-zero | holds | holds | PASS |
| B16a-jobexit-other-pod | holds | holds | PASS |
| B16b-jobexit-other-job | holds | holds | PASS |
| B16c-jobexit-ne-container | holds | holds | PASS |
| B12a-ruleA-exit-string-0 | holds | holds | PASS |
| B12b-ruleA-exit-string-42 | holds | holds | PASS |
| K4-a-string-0 | holds | holds | PASS |
| K4-b-string-42 | holds | holds | PASS |
| K4-c-true | holds | holds | PASS |
| K4-d-float-42.0 | holds | holds | PASS |
| K4-e-exponent | holds | holds | PASS |
| K4-f-float-0.0 | holds | holds | PASS |
| B13-pair-26-FAILED-42 | holds | holds | PASS |
| B13-pair-26-FAILED-43 | holds | holds | PASS |
| B13-pair-26-FAILED-0 | holds | holds | PASS |
| B13-pair-0-SUCCEEDED-42 | holds | holds | PASS |
| B13-pair-0-FAILED-42 | holds | holds | PASS |
| B13-pair-26-SUCCEEDED-42 | holds | holds | PASS |
| B13-pair-26-NONE-42 | holds | holds | PASS |
| B13-pair-25-FAILED-42 | holds | holds | PASS |
| B13-pair-1-FAILED-42 | holds | holds | PASS |
| B13-pair-26-TIMED_OUT-42 | holds | holds | PASS |
| B13-pair-0-SUCCEEDED-0 | NOTE-odd-pairing-accepted | NOTE-odd-pairing-accepted | PASS |
| B13-pair-26-STOPPED-42 | holds | holds | PASS |
| B14a-partial-listed-lost | holds | holds | PASS |
| B14b-partial-unlisted-lost | holds | holds | PASS |
| B14c-partial-nothing-lost | holds | holds | PASS |
| B15a-result-not-json | holds | holds | PASS |
| B15b-build-not-json | holds | holds | PASS |
| B15c-result-array | holds | holds | PASS |
| B15d-result-empty | holds | holds | PASS |
| B15e-status-not-json | holds | holds | PASS |
| B15f-objects-not-json | holds | holds | PASS |
| K5-newline-file-name | holds | holds | PASS |
| K5b-record-write-fails | holds | holds | PASS |
| C01-BASH_ENV | holds | holds | PASS |
| C01-EXPORTED_FUNCTION | holds | holds | PASS |
| C01-PATH_SHIM | holds | holds | PASS |
| C01w-BASH_ENV | holds | holds | PASS |
| C01w-EXPORTED_FUNCTION | holds | holds | PASS |
| C02-CDPATH-relative-argv | holds | holds | PASS |
| C02b-CDPATH-dot | holds | holds | PASS |
| C03-ISOLAB_BUCKET-override | holds | holds | PASS |
| C04-out-symlink-into-runs | holds | holds | PASS |
| C04b-out-outside-out-root | refused | refused | PASS |
| C04c-out-runs-inside-out-root | refused | refused | PASS |
| C06-AWS_ENDPOINT_URL | refused | refused | PASS |
| C06-AWS_ENDPOINT_URL_S3 | refused | refused | PASS |
| C06w-AWS_ENDPOINT_URL_S3-wrapper | refused | refused | PASS |
| C07-config-alias | refused | refused | PASS |
| C07-config-credential_process | refused | refused | PASS |
| C07-config-endpoint_url | refused | refused | PASS |
| C07-config-plugins | refused | refused | PASS |
| C07w-config-credential_process-wrapper | refused | refused | PASS |
| C08-aws-version-mismatch | refused | refused | PASS |
| C09-phase-marker-spoof | refused | refused | PASS |
| C09b-phase-marker-spoof-pythonpath | refused | refused | PASS |
| C09w-phase-marker-spoof-wrapper | refused | refused | PASS |
| C02w-CDPATH-wrapper | holds | holds | PASS |
| C10-credentials-by-name | holds | holds | PASS |
| C11-python-shim-ahead-of-aws | holds | holds | PASS |
| C05-static-scan | holds | holds | PASS |

### 7.2 The new cases (136 rows; full observations in `evidence/rt-results.tsv`)

Case ids ending `-w` are the launch_eks.sh mirror of the case without the suffix. A refusal row passes only if the exit status is 2, no aws call was made, no output file was written, no secret string (dummy credentials, the proxy password) was printed, and the refusing check's own text is on stderr.

| case | refusal text or pass condition fixed by the case | expected | outcome | verdict |
|---|---|---|---|---|
| D01-proxy-loopback-ip-ok | passes, k7 line has: transport[HTTPS_PROXY https_proxy] proxy=http://127.0.0.1:1 no_proxy=none | passes | passes | PASS |
| D01-proxy-loopback-ip-ok-w | passes, k7 line has: transport[HTTPS_PROXY https_proxy] proxy=http://127.0.0.1:1 no_proxy=none | passes | passes | PASS |
| D01b-proxy-localhost-slash-ok | passes, k7 line has: transport[HTTPS_PROXY https_proxy] proxy=http://localhost:8080/ no_proxy=none ca_bundle=none | passes | passes | PASS |
| D01b-proxy-localhost-slash-ok-w | passes, k7 line has: transport[HTTPS_PROXY https_proxy] proxy=http://localhost:8080/ no_proxy=none ca_bundle=none | passes | passes | PASS |
| D01c-proxy-lower-only-ok | passes, k7 line has: transport[https_proxy] proxy=http://127.0.0.1:1 no_proxy=none | passes | passes | PASS |
| D01c-proxy-lower-only-ok-w | passes, k7 line has: transport[https_proxy] proxy=http://127.0.0.1:1 no_proxy=none | passes | passes | PASS |
| D01d-proxy-upper-only-ok | passes, k7 line has: transport[HTTPS_PROXY] proxy=http://127.0.0.1:1 no_proxy=none | passes | passes | PASS |
| D01d-proxy-upper-only-ok-w | passes, k7 line has: transport[HTTPS_PROXY] proxy=http://127.0.0.1:1 no_proxy=none | passes | passes | PASS |
| D02-proxy-pair-mismatch | refuses: HTTPS_PROXY and https_proxy differ | refused | refused | PASS |
| D02-proxy-pair-mismatch-w | refuses: HTTPS_PROXY and https_proxy differ | refused | refused | PASS |
| D03-proxy-userinfo | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03-proxy-userinfo-w | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03b-proxy-non-loopback-host | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03b-proxy-non-loopback-host-w | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03c-proxy-path | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03c-proxy-path-w | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03d-proxy-newline | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03d-proxy-newline-w | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03e-proxy-https-scheme | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03e-proxy-https-scheme-w | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03f-proxy-lower-bad | refuses: https_proxy does not match the loopback proxy pin | refused | refused | PASS |
| D03f-proxy-lower-bad-w | refuses: https_proxy does not match the loopback proxy pin | refused | refused | PASS |
| D03g-proxy-empty | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03g-proxy-empty-w | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03h-proxy-no-port | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D03h-proxy-no-port-w | refuses: HTTPS_PROXY does not match the loopback proxy pin | refused | refused | PASS |
| D04-noproxy-ok | passes, k7 line has: transport[NO_PROXY no_proxy] proxy=none no_proxy=localhost,127.0.0.1,*.example.com:443 ca_bundle=none | passes | passes | PASS |
| D04-noproxy-ok-w | passes, k7 line has: transport[NO_PROXY no_proxy] proxy=none no_proxy=localhost,127.0.0.1,*.example.com:443 ca_bundle=none | passes | passes | PASS |
| D04b-noproxy-pair-mismatch | refuses: NO_PROXY and no_proxy differ | refused | refused | PASS |
| D04b-noproxy-pair-mismatch-w | refuses: NO_PROXY and no_proxy differ | refused | refused | PASS |
| D04c-noproxy-whitespace | refuses: NO_PROXY does not match | refused | refused | PASS |
| D04c-noproxy-whitespace-w | refuses: NO_PROXY does not match | refused | refused | PASS |
| D04d-noproxy-forbidden-char | refuses: NO_PROXY does not match | refused | refused | PASS |
| D04d-noproxy-forbidden-char-w | refuses: NO_PROXY does not match | refused | refused | PASS |
| D04e-noproxy-lower-bad | refuses: no_proxy does not match | refused | refused | PASS |
| D04e-noproxy-lower-bad-w | refuses: no_proxy does not match | refused | refused | PASS |
| D04f-noproxy-newline | refuses: NO_PROXY does not match | refused | refused | PASS |
| D04f-noproxy-newline-w | refuses: NO_PROXY does not match | refused | refused | PASS |
| D04g-noproxy-empty-ok | passes, k7 line has: transport[NO_PROXY] proxy=none no_proxy= ca_bundle=none | passes | passes | PASS |
| D04g-noproxy-empty-ok-w | passes, k7 line has: transport[NO_PROXY] proxy=none no_proxy= ca_bundle=none | passes | passes | PASS |
| D05-transport-dropped | T-1: the aws process sees HTTPS_PROXY, NO_PROXY and PYTHONNOUSERSITE only; the other six proxy or CA names are dropped; the run passes | passes | passes | PASS |
| D05-transport-dropped-w | T-1: the aws process sees HTTPS_PROXY, NO_PROXY and PYTHONNOUSERSITE only; the other six proxy or CA names are dropped; the run passes | passes | passes | PASS |
| D06-ca-allowed-ok | passes, k7 line has: transport[HTTPS_PROXY https_proxy AWS_CA_BUNDLE] proxy=http://127.0.0.1:1 no_proxy=none ca_bundle=/tmp/claude-0/-home-user/fe5... | passes | passes | PASS |
| D06-ca-allowed-ok-w | passes, k7 line has: transport[HTTPS_PROXY https_proxy AWS_CA_BUNDLE] proxy=http://127.0.0.1:1 no_proxy=none ca_bundle=/tmp/claude-0/-home-user/fe5... | passes | passes | PASS |
| D06b-ca-allowed-ok-lower-proxy-only | passes, k7 line has: transport[https_proxy AWS_CA_BUNDLE] proxy=http://127.0.0.1:1 no_proxy=none ca_bundle=/tmp/claude-0/-home-user/fe537fb0-7f2e-5... | passes | passes | PASS |
| D06b-ca-allowed-ok-lower-proxy-only-w | passes, k7 line has: transport[https_proxy AWS_CA_BUNDLE] proxy=http://127.0.0.1:1 no_proxy=none ca_bundle=/tmp/claude-0/-home-user/fe537fb0-7f2e-5... | passes | passes | PASS |
| D07-ca-other-path | refuses: AWS_CA_BUNDLE is not an entry of K7_CA_BUNDLE_ALLOWED | refused | refused | PASS |
| D07-ca-other-path-w | refuses: AWS_CA_BUNDLE is not an entry of K7_CA_BUNDLE_ALLOWED | refused | refused | PASS |
| D07b-ca-other-path-real-bundle-name | refuses: AWS_CA_BUNDLE is not an entry of K7_CA_BUNDLE_ALLOWED | refused | refused | PASS |
| D07b-ca-other-path-real-bundle-name-w | refuses: AWS_CA_BUNDLE is not an entry of K7_CA_BUNDLE_ALLOWED | refused | refused | PASS |
| D08-ca-allowed-is-symlink | refuses: AWS_CA_BUNDLE is missing or its realpath differs | refused | refused | PASS |
| D08-ca-allowed-is-symlink-w | refuses: AWS_CA_BUNDLE is missing or its realpath differs | refused | refused | PASS |
| D08b-ca-allowed-symlinked-parent | refuses: AWS_CA_BUNDLE is missing or its realpath differs | refused | refused | PASS |
| D08b-ca-allowed-symlinked-parent-w | refuses: AWS_CA_BUNDLE is missing or its realpath differs | refused | refused | PASS |
| D08c-ca-allowed-missing | refuses: AWS_CA_BUNDLE is missing or its realpath differs | refused | refused | PASS |
| D08c-ca-allowed-missing-w | refuses: AWS_CA_BUNDLE is missing or its realpath differs | refused | refused | PASS |
| D08d-ca-allowed-empty | refuses: AWS_CA_BUNDLE is not a non-empty regular file | refused | refused | PASS |
| D08d-ca-allowed-empty-w | refuses: AWS_CA_BUNDLE is not a non-empty regular file | refused | refused | PASS |
| D08e-ca-allowed-directory | refuses: AWS_CA_BUNDLE is not a non-empty regular file | refused | refused | PASS |
| D08e-ca-allowed-directory-w | refuses: AWS_CA_BUNDLE is not a non-empty regular file | refused | refused | PASS |
| D09-ca-without-proxy-allowed-file | refuses: AWS_CA_BUNDLE is allowed only when HTTPS_PROXY or https_proxy is set | refused | refused | PASS |
| D09-ca-without-proxy-allowed-file-w | refuses: AWS_CA_BUNDLE is allowed only when HTTPS_PROXY or https_proxy is set | refused | refused | PASS |
| D09b-ca-without-proxy-real-name | refuses: AWS_CA_BUNDLE is allowed only when HTTPS_PROXY or https_proxy is set | refused | refused | PASS |
| D09b-ca-without-proxy-real-name-w | refuses: AWS_CA_BUNDLE is allowed only when HTTPS_PROXY or https_proxy is set | refused | refused | PASS |
| D09c-ca-with-no-proxy-only | refuses: AWS_CA_BUNDLE is allowed only when HTTPS_PROXY or https_proxy is set | refused | refused | PASS |
| D09c-ca-with-no-proxy-only-w | refuses: AWS_CA_BUNDLE is allowed only when HTTPS_PROXY or https_proxy is set | refused | refused | PASS |
| D10-ca-sha256-fails | refuses: the sha256 of AWS_CA_BUNDLE could not be computed | refused | refused | PASS |
| D10-ca-sha256-fails-w | refuses: the sha256 of AWS_CA_BUNDLE could not be computed | refused | refused | PASS |
| D11-config-ca_bundle | CF-1: ca_bundle in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-ca_bundle-w | CF-1: ca_bundle in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-role_arn | CF-1: role_arn in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-role_arn-w | CF-1: role_arn in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-source_profile | CF-1: source_profile in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-source_profile-w | CF-1: source_profile in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-credential_source | CF-1: credential_source in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-credential_source-w | CF-1: credential_source in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-web_identity_token_file | CF-1: web_identity_token_file in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-web_identity_token_file-w | CF-1: web_identity_token_file in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-sso_session | CF-1: sso_session in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-sso_session-w | CF-1: sso_session in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-sso_start_url | CF-1: sso_start_url in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11-config-sso_start_url-w | CF-1: sso_start_url in ~/.aws/config is refused (exit 2, zero aws calls); the entry name is printed, never its value | refused | refused | PASS |
| D11b-config-container-shape-ok | the container's [default] s3 payload_signing_enabled block is admitted (K7_CFG_ALLOWED stays empty and the block names none of the refused entries) | passes | passes | PASS |
| D11b-config-container-shape-ok-w | the container's [default] s3 payload_signing_enabled block is admitted (K7_CFG_ALLOWED stays empty and the block names none of the refused entries) | passes | passes | PASS |
| D12-cred-id-missing | refuses: AWS_ACCESS_KEY_ID is not set or is empty | refused | refused | PASS |
| D12-cred-id-missing-w | refuses: AWS_ACCESS_KEY_ID is not set or is empty | refused | refused | PASS |
| D12b-cred-id-empty | refuses: AWS_ACCESS_KEY_ID is not set or is empty | refused | refused | PASS |
| D12b-cred-id-empty-w | refuses: AWS_ACCESS_KEY_ID is not set or is empty | refused | refused | PASS |
| D12c-cred-secret-missing | refuses: AWS_SECRET_ACCESS_KEY is not set or is empty | refused | refused | PASS |
| D12c-cred-secret-missing-w | refuses: AWS_SECRET_ACCESS_KEY is not set or is empty | refused | refused | PASS |
| D12d-cred-secret-empty | refuses: AWS_SECRET_ACCESS_KEY is not set or is empty | refused | refused | PASS |
| D12d-cred-secret-empty-w | refuses: AWS_SECRET_ACCESS_KEY is not set or is empty | refused | refused | PASS |
| D12e-cred-both-missing | refuses: AWS_ACCESS_KEY_ID is not set or is empty | refused | refused | PASS |
| D12e-cred-both-missing-w | refuses: AWS_ACCESS_KEY_ID is not set or is empty | refused | refused | PASS |
| D12f-cred-session-token-optional-ok | passes, k7 line has: aws= | passes | passes | PASS |
| D12f-cred-session-token-optional-ok-w | passes, k7 line has: aws= | passes | passes | PASS |
| D13-metadata-preset-false | refuses: AWS_EC2_METADATA_DISABLED is set to a value other than its constant true | refused | refused | PASS |
| D13-metadata-preset-false-w | refuses: AWS_EC2_METADATA_DISABLED is set to a value other than its constant true | refused | refused | PASS |
| D13b-pythonnousersite-preset-0 | refuses: PYTHONNOUSERSITE is set to a value other than its constant 1 | refused | refused | PASS |
| D13b-pythonnousersite-preset-0-w | refuses: PYTHONNOUSERSITE is set to a value other than its constant 1 | refused | refused | PASS |
| D13c-metadata-preset-true-ok | passes, k7 line has: aws= | passes | passes | PASS |
| D13c-metadata-preset-true-ok-w | passes, k7 line has: aws= | passes | passes | PASS |
| D13d-pythonnousersite-preset-1-ok | passes, k7 line has: aws= | passes | passes | PASS |
| D13d-pythonnousersite-preset-1-ok-w | passes, k7 line has: aws= | passes | passes | PASS |
| D13e-metadata-empty-preset | refuses: AWS_EC2_METADATA_DISABLED is set to a value other than its constant true | refused | refused | PASS |
| D13e-metadata-empty-preset-w | refuses: AWS_EC2_METADATA_DISABLED is set to a value other than its constant true | refused | refused | PASS |
| D14-phase2-direct-no-constants | refuses: AWS_EC2_METADATA_DISABLED is not set to its constant true | refused | refused | PASS |
| D14-phase2-direct-no-constants-w | refuses: AWS_EC2_METADATA_DISABLED is not set to its constant true | refused | refused | PASS |
| D14b-phase2-direct-metadata-false | refuses: AWS_EC2_METADATA_DISABLED is not set to its constant true | refused | refused | PASS |
| D14b-phase2-direct-metadata-false-w | refuses: AWS_EC2_METADATA_DISABLED is not set to its constant true | refused | refused | PASS |
| D14c-phase2-direct-pythonnousersite-0 | refuses: PYTHONNOUSERSITE is not set to its constant 1 | refused | refused | PASS |
| D14c-phase2-direct-pythonnousersite-0-w | refuses: PYTHONNOUSERSITE is not set to its constant 1 | refused | refused | PASS |
| D14d-constants-reach-aws | CR-2 and PY-1: the aws process sees AWS_EC2_METADATA_DISABLED and PYTHONNOUSERSITE | passes | passes | PASS |
| D14d-constants-reach-aws-w | CR-2 and PY-1: the aws process sees AWS_EC2_METADATA_DISABLED and PYTHONNOUSERSITE | passes | passes | PASS |
| D15-pth-user-site-does-not-run | PY-1: a .pth under the user site runs in a python3 without PYTHONNOUSERSITE (control=1) and does not run in the aws process (runs=0) | holds | holds | PASS |
| D15-pth-user-site-does-not-run-w | PY-1: a .pth under the user site runs in a python3 without PYTHONNOUSERSITE (control=1) and does not run in the aws process (runs=0) | holds | holds | PASS |
| D16-argv-bash-p-BASH_ENV | R-2 A-1: under /bin/bash -p the vector BASH_ENV runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-BASH_ENV-w | R-2 A-1: under /bin/bash -p the vector BASH_ENV runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-ENV | R-2 A-1: under /bin/bash -p the vector ENV runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-ENV-w | R-2 A-1: under /bin/bash -p the vector ENV runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-BASH_FUNC_aws | R-2 A-1: under /bin/bash -p the vector BASH_FUNC_aws runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-BASH_FUNC_aws-w | R-2 A-1: under /bin/bash -p the vector BASH_FUNC_aws runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-BASH_FUNC_set | R-2 A-1: under /bin/bash -p the vector BASH_FUNC_set runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-BASH_FUNC_set-w | R-2 A-1: under /bin/bash -p the vector BASH_FUNC_set runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-SHELLOPTS_PS4 | R-2 A-1: under /bin/bash -p the vector SHELLOPTS_PS4 runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16-argv-bash-p-SHELLOPTS_PS4-w | R-2 A-1: under /bin/bash -p the vector SHELLOPTS_PS4 runs no payload before line 1 (marker absent) and the run passes | holds | holds | PASS |
| D16c-control-plain-bash-BASH_ENV | pre-v3d control: under plain bash the vector BASH_ENV gives: payload-ran-before-line-1 | payload-ran-before-line-1 | payload-ran-before-line-1 | PASS |
| D16c-control-plain-bash-BASH_ENV-w | pre-v3d control: under plain bash the vector BASH_ENV gives: payload-ran-before-line-1 | payload-ran-before-line-1 | payload-ran-before-line-1 | PASS |
| D16c-control-plain-bash-ENV | pre-v3d control: under plain bash the vector ENV gives: marker-absent | marker-absent | marker-absent | PASS |
| D16c-control-plain-bash-ENV-w | pre-v3d control: under plain bash the vector ENV gives: marker-absent | marker-absent | marker-absent | PASS |
| D16c-control-plain-bash-BASH_FUNC_aws | pre-v3d control: under plain bash the vector BASH_FUNC_aws gives: marker-absent | marker-absent | marker-absent | PASS |
| D16c-control-plain-bash-BASH_FUNC_aws-w | pre-v3d control: under plain bash the vector BASH_FUNC_aws gives: marker-absent | marker-absent | marker-absent | PASS |
| D16c-control-plain-bash-BASH_FUNC_set | pre-v3d control: under plain bash the vector BASH_FUNC_set gives: payload-ran-before-line-1 | payload-ran-before-line-1 | payload-ran-before-line-1 | PASS |
| D16c-control-plain-bash-BASH_FUNC_set-w | pre-v3d control: under plain bash the vector BASH_FUNC_set gives: payload-ran-before-line-1 | payload-ran-before-line-1 | payload-ran-before-line-1 | PASS |
| D16c-control-plain-bash-SHELLOPTS_PS4 | pre-v3d control: under plain bash the vector SHELLOPTS_PS4 gives: marker-absent | marker-absent | marker-absent | PASS |
| D16c-control-plain-bash-SHELLOPTS_PS4-w | pre-v3d control: under plain bash the vector SHELLOPTS_PS4 gives: marker-absent | marker-absent | marker-absent | PASS |

rows: 136  PASS: 136


## 8. Mutation results (`evidence/mutation-results.tsv`, `mutation-output.txt`, `mutation-list.tsv`)

`tests/mutate.py` removes one check per mutant (a text edit that must match exactly once; `apply` fails otherwise, which the runner reports as ERROR); `tests/mutation_check.sh` runs the whole `rt_regression.sh` (259 rows) against each mutant. CAUGHT = at least one case differs from its expected outcome. Frozen bytes: the sha256 values of the scripts, tests and runbook at the start of the run are in `evidence/frozen-hashes.txt`; nothing was edited while it ran. The runner deletes each mutant's bulky case trees after reading the result (the container has little free disk); the tables and logs are kept.

Result: 82 mutants (32 of d07e94, 50 new): 80 CAUGHT, 2 SUBSUMED (`mutation_check.sh OUT 3`, 62 min 59 s real time, exit 0; `evidence/mutation-output.txt`). Baseline (unmutated scripts): BASELINE-CLEAN (0 differing cases). SURVIVED or ERRORED: none.

Disclosed iteration: the first complete pass of this check (on the first freeze) showed one survivor, the d07e94 mutant `K7-allowlist` (0 differing cases). Cause: the old case `C09b-phase-marker-spoof-pythonpath` starts the script in phase 2 with `PYTHONPATH` set and nothing else wrong; in v3d the new phase-2 constant check (`K7-const-value`) refuses that start first (the spoof carries no `AWS_EC2_METADATA_DISABLED` or `PYTHONNOUSERSITE`), so removing the allowlist check changed no outcome. That pass was stopped at 42 of 83 results (the baseline, the 32 d07e94 mutants and 9 of the V3d mutants; `evidence/mutation-first-freeze-partial.tsv`); there, 29 old mutants were CAUGHT, `K2-nonempty` and `K4-type` showed the raw SURVIVED that the aggregation turns into SUBSUMED (the aggregation did not run in the stopped pass), `K7-allowlist` SURVIVED, and the 9 V3d mutants were CAUGHT. Fix, in the test only: the spoof now also passes the two constants and the row requires the text `allowlist are set: PYTHONPATH` on stderr (the expected outcome `refused` of the row is unchanged). `rt_regression.sh` therefore changed (sha256 `7b24322f...`, was `9770f4ee...`); the three suites were re-run and the whole mutation check was re-run from the start on the new frozen bytes, which is the run reported here. All 123 old rows still match the d07e94 table.

The two SUBSUMED claims of d07e94 are re-verified by this run: `K2-nonempty` (subsumed by `K2-nonempty-and-entries`) and `K4-type` (subsumed by `K4-verify`); the SUBSUMED verdict is given only when the pair mutant is CAUGHT.

New mutants (one per new check, in each of the two scripts, suffix `-R` reconcile_run.sh and `-L` launch_eks.sh): proxy-pair, proxy-shape, noproxy-pair, noproxy-shape, ca-needs-proxy, ca-entry, ca-realpath, ca-file, ca-sha, const-preset, const-value, cred-id, cred-secret, seven configuration names, status suffix, transport-pass, transport-allowlist, const-metadata, const-pyuser (25 per script, 50 in all). A quick pre-pass of those 50 against the D rows alone (scratch, not evidence) had already shown each one caught.

| mutation | control | verdict | differing | first failing cases |
|---|---|---|---|---|
| BASELINE | - | BASELINE-CLEAN | 0 differing case(s) | none |
| K1-uri | K-1 | CAUGHT | 2 differing case(s) | A02b-ruleA-cross-job-with-receipt A03b-ruleA-other-bucket-with-receipt |
| K1-poduid | K-1 | CAUGHT | 1 differing case(s) | A01d-ruleA-uri-located-poduid-differs |
| K1-class | K-1 | CAUGHT | 4 differing case(s) | A01b-ruleA-sibling-prefix-with-receipt A01d-ruleA-uri-located-poduid-differs A02b-ruleA-cross-job-with-receipt A03b-r... |
| K2-nonempty | K-2 | SUBSUMED(by K2-nonempty-and-entries) | 0 differing case(s) | none |
| K2-nexttoken | K-2 | CAUGHT | 2 differing case(s) | A09d-objects-json-truncated A09d2-objects-json-next-token-only |
| K2-keys | K-2 | CAUGHT | 1 differing case(s) | A09e-objects-json-key-outside |
| K2-entries | K-2 | CAUGHT | 2 differing case(s) | A09j-objects-json-no-pod-entries A09f-objects-json-missing-etag |
| K2-listing | K-2 | CAUGHT | 6 differing case(s) | A09a-added-object A09b-replaced-object A09g-objects-json-extra-entry A09i-multipart-size-changed |
| K2-objects | K-2 | CAUGHT | 1 differing case(s) | A10b-toctou-after-pod-listing |
| K2-nonempty-and-entries | K-2 | CAUGHT | 3 differing case(s) | A09c2-objects-json-empty-array A09j-objects-json-no-pod-entries A09f-objects-json-missing-etag |
| K2-pin-status | K-2 | CAUGHT | 1 differing case(s) | A13a-pin-status-wrong |
| K2-pin-objects | K-2 | CAUGHT | 1 differing case(s) | A13b-pin-objects-wrong |
| K2-pin-lastmodified | K-2 | CAUGHT | 1 differing case(s) | A13c-receipt-object-too-new |
| K2-pin-podlm | K-2 | CAUGHT | 1 differing case(s) | A13d-pod-object-too-new |
| K2-wrapper-objects | K-2 | CAUGHT | 2 differing case(s) | A10b-toctou-after-pod-listing K5-newline-file-name |
| K2-wrapper-dl | K-2 | CAUGHT | 1 differing case(s) | B14c-partial-nothing-lost |
| K4-type | K-4 | SUBSUMED(by K4-verify) | 0 differing case(s) | none |
| K4-raw | K-4 | CAUGHT | 2 differing case(s) | B11b-exit-exponent K4-e-exponent |
| K4-wrapper | K-4 | CAUGHT | 13 differing case(s) | B05-exit-string-42 B06-exit-true B09-exit-42.5 B10-exit-42.0 |
| K4-verify | K-4 | CAUGHT | 5 differing case(s) | B10-exit-42.0 B11b-exit-exponent K4-d-float-42.0 K4-e-exponent |
| K5-trap | K-5 | CAUGHT | 1 differing case(s) | K5b-record-write-fails |
| K6-receipt-uuid | K-6 | CAUGHT | 1 differing case(s) | A06f-receipt-id-all-dashes |
| K6-launcher-id | K-6 | CAUGHT | 1 differing case(s) | A06e-receipt-second-launcher-id |
| K6-poduid | K-6 | CAUGHT | 5 differing case(s) | A07a-poduid-dotdot A07b-poduid-slash A07c-poduid-35 A07d-poduid-upper |
| K6-restart | K-6 | CAUGHT | 3 differing case(s) | A08-restart-count A08b-restart-count-only A08c-laststate-only |
| K7-out-runs | K-7 | CAUGHT | 1 differing case(s) | C04c-out-runs-inside-out-root |
| K7-out-root | K-7 | CAUGHT | 1 differing case(s) | C04b-out-outside-out-root |
| K7-endpoint | K-7 | CAUGHT | 2 differing case(s) | C06-AWS_ENDPOINT_URL C06-AWS_ENDPOINT_URL_S3 |
| K7-version | K-7 | CAUGHT | 46 differing case(s) | A00-control-T1-shape A09e-objects-json-key-outside A09h-multipart-etag-size-only A10b-toctou-after-pod-listing |
| K7-config | K-7 | CAUGHT | 11 differing case(s) | C07-config-alias C07-config-credential_process C07-config-endpoint_url C07-config-plugins |
| K7-allowlist | K-7 | CAUGHT | 1 differing case(s) | C09b-phase-marker-spoof-pythonpath |
| K7-launch-config | K-7 | CAUGHT | 8 differing case(s) | C07w-config-credential_process-wrapper D11-config-ca_bundle-w D11-config-role_arn-w D11-config-source_profile-w |
| V3d-const-preset-R | K-7/v3d | CAUGHT | 3 differing case(s) | D13-metadata-preset-false D13b-pythonnousersite-preset-0 D13e-metadata-empty-preset |
| V3d-const-value-R | K-7/v3d | CAUGHT | 3 differing case(s) | D14-phase2-direct-no-constants D14b-phase2-direct-metadata-false D14c-phase2-direct-pythonnousersite-0 |
| V3d-cred-id-R | K-7/v3d | CAUGHT | 3 differing case(s) | D12-cred-id-missing D12b-cred-id-empty D12e-cred-both-missing |
| V3d-cred-secret-R | K-7/v3d | CAUGHT | 2 differing case(s) | D12c-cred-secret-missing D12d-cred-secret-empty |
| V3d-proxy-pair-R | K-7/v3d | CAUGHT | 1 differing case(s) | D02-proxy-pair-mismatch |
| V3d-proxy-shape-R | K-7/v3d | CAUGHT | 8 differing case(s) | D03-proxy-userinfo D03b-proxy-non-loopback-host D03c-proxy-path D03d-proxy-newline |
| V3d-noproxy-pair-R | K-7/v3d | CAUGHT | 1 differing case(s) | D04b-noproxy-pair-mismatch |
| V3d-noproxy-shape-R | K-7/v3d | CAUGHT | 4 differing case(s) | D04c-noproxy-whitespace D04d-noproxy-forbidden-char D04e-noproxy-lower-bad D04f-noproxy-newline |
| V3d-ca-needs-proxy-R | K-7/v3d | CAUGHT | 3 differing case(s) | D09-ca-without-proxy-allowed-file D09b-ca-without-proxy-real-name D09c-ca-with-no-proxy-only |
| V3d-ca-entry-R | K-7/v3d | CAUGHT | 2 differing case(s) | D07-ca-other-path D07b-ca-other-path-real-bundle-name |
| V3d-ca-realpath-R | K-7/v3d | CAUGHT | 3 differing case(s) | D08-ca-allowed-is-symlink D08b-ca-allowed-symlinked-parent D08c-ca-allowed-missing |
| V3d-ca-file-R | K-7/v3d | CAUGHT | 2 differing case(s) | D08d-ca-allowed-empty D08e-ca-allowed-directory |
| V3d-ca-sha-R | K-7/v3d | CAUGHT | 1 differing case(s) | D10-ca-sha256-fails |
| V3d-cfg-ca_bundle-R | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-ca_bundle |
| V3d-cfg-role_arn-R | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-role_arn |
| V3d-cfg-source_profile-R | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-source_profile |
| V3d-cfg-credential_source-R | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-credential_source |
| V3d-cfg-web_identity_token_file-R | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-web_identity_token_file |
| V3d-cfg-sso_session-R | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-sso_session |
| V3d-cfg-sso_start_url-R | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-sso_start_url |
| V3d-status-R | K-7/v3d | CAUGHT | 8 differing case(s) | D01-proxy-loopback-ip-ok D01b-proxy-localhost-slash-ok D01c-proxy-lower-only-ok D01d-proxy-upper-only-ok |
| V3d-transport-pass-R | K-7/v3d | CAUGHT | 34 differing case(s) | D01-proxy-loopback-ip-ok D01b-proxy-localhost-slash-ok D01c-proxy-lower-only-ok D01d-proxy-upper-only-ok |
| V3d-transport-allowlist-R | K-7/v3d | CAUGHT | 34 differing case(s) | D01-proxy-loopback-ip-ok D01b-proxy-localhost-slash-ok D01c-proxy-lower-only-ok D01d-proxy-upper-only-ok |
| V3d-const-metadata-R | K-7/v3d | CAUGHT | 8 differing case(s) | C09b-phase-marker-spoof-pythonpath C10-credentials-by-name D13-metadata-preset-false D13e-metadata-empty-preset |
| V3d-const-pyuser-R | K-7/v3d | CAUGHT | 7 differing case(s) | C09b-phase-marker-spoof-pythonpath D05-transport-dropped D13b-pythonnousersite-preset-0 D14b-phase2-direct-metadata-f... |
| V3d-const-preset-L | K-7/v3d | CAUGHT | 3 differing case(s) | D13-metadata-preset-false-w D13b-pythonnousersite-preset-0-w D13e-metadata-empty-preset-w |
| V3d-const-value-L | K-7/v3d | CAUGHT | 3 differing case(s) | D14-phase2-direct-no-constants-w D14b-phase2-direct-metadata-false-w D14c-phase2-direct-pythonnousersite-0-w |
| V3d-cred-id-L | K-7/v3d | CAUGHT | 3 differing case(s) | D12-cred-id-missing-w D12b-cred-id-empty-w D12e-cred-both-missing-w |
| V3d-cred-secret-L | K-7/v3d | CAUGHT | 2 differing case(s) | D12c-cred-secret-missing-w D12d-cred-secret-empty-w |
| V3d-proxy-pair-L | K-7/v3d | CAUGHT | 1 differing case(s) | D02-proxy-pair-mismatch-w |
| V3d-proxy-shape-L | K-7/v3d | CAUGHT | 8 differing case(s) | D03-proxy-userinfo-w D03b-proxy-non-loopback-host-w D03c-proxy-path-w D03d-proxy-newline-w |
| V3d-noproxy-pair-L | K-7/v3d | CAUGHT | 1 differing case(s) | D04b-noproxy-pair-mismatch-w |
| V3d-noproxy-shape-L | K-7/v3d | CAUGHT | 4 differing case(s) | D04c-noproxy-whitespace-w D04d-noproxy-forbidden-char-w D04e-noproxy-lower-bad-w D04f-noproxy-newline-w |
| V3d-ca-needs-proxy-L | K-7/v3d | CAUGHT | 3 differing case(s) | D09-ca-without-proxy-allowed-file-w D09b-ca-without-proxy-real-name-w D09c-ca-with-no-proxy-only-w |
| V3d-ca-entry-L | K-7/v3d | CAUGHT | 2 differing case(s) | D07-ca-other-path-w D07b-ca-other-path-real-bundle-name-w |
| V3d-ca-realpath-L | K-7/v3d | CAUGHT | 3 differing case(s) | D08-ca-allowed-is-symlink-w D08b-ca-allowed-symlinked-parent-w D08c-ca-allowed-missing-w |
| V3d-ca-file-L | K-7/v3d | CAUGHT | 2 differing case(s) | D08d-ca-allowed-empty-w D08e-ca-allowed-directory-w |
| V3d-ca-sha-L | K-7/v3d | CAUGHT | 1 differing case(s) | D10-ca-sha256-fails-w |
| V3d-cfg-ca_bundle-L | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-ca_bundle-w |
| V3d-cfg-role_arn-L | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-role_arn-w |
| V3d-cfg-source_profile-L | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-source_profile-w |
| V3d-cfg-credential_source-L | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-credential_source-w |
| V3d-cfg-web_identity_token_file-L | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-web_identity_token_file-w |
| V3d-cfg-sso_session-L | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-sso_session-w |
| V3d-cfg-sso_start_url-L | K-7/v3d | CAUGHT | 1 differing case(s) | D11-config-sso_start_url-w |
| V3d-status-L | K-7/v3d | CAUGHT | 8 differing case(s) | D01-proxy-loopback-ip-ok-w D01b-proxy-localhost-slash-ok-w D01c-proxy-lower-only-ok-w D01d-proxy-upper-only-ok-w |
| V3d-transport-pass-L | K-7/v3d | CAUGHT | 34 differing case(s) | D01-proxy-loopback-ip-ok-w D01b-proxy-localhost-slash-ok-w D01c-proxy-lower-only-ok-w D01d-proxy-upper-only-ok-w |
| V3d-transport-allowlist-L | K-7/v3d | CAUGHT | 34 differing case(s) | D01-proxy-loopback-ip-ok-w D01b-proxy-localhost-slash-ok-w D01c-proxy-lower-only-ok-w D01d-proxy-upper-only-ok-w |
| V3d-const-metadata-L | K-7/v3d | CAUGHT | 6 differing case(s) | D13-metadata-preset-false-w D13e-metadata-empty-preset-w D14-phase2-direct-no-constants-w D14b-phase2-direct-metadata... |
| V3d-const-pyuser-L | K-7/v3d | CAUGHT | 6 differing case(s) | D05-transport-dropped-w D13b-pythonnousersite-preset-0-w D14b-phase2-direct-metadata-false-w D14c-phase2-direct-pytho... |

## 9. Records (E-5 as amended, V-8)

- Canonical `specification.yaml` stays `status: review_required`, `approved_by: null`, `execution_authorized: false`; canonical `trial-plan.json` stays `approved_by: null`, `candidate_only: true`, `approval_required: true`. Both carry the v3d wording and bytes (spec: v3d launcher version, the R-1 to R-3 sentence in the K-7 summary, DEC-20261107-c3e91a in the header and objective; plan: `source_sha256` of launch_eks.sh and the T2 argv `/bin/bash`, `-p`, script; `specification_sha256` is the canonical draft's). `evidence/pd3-check.txt`: no file outside `design/5f7d2b/` reads approved.
- The approved forms exist only under `design/5f7d2b/approval-preview/` (status approved, `approved_by DEC-20261107-7802ec`, `execution_authorized true`; the preview plan's `specification_sha256` is the preview specification's, `de94c9ef...`). No schema key was added to the specification; the narrowing of C1-AMENDMENT-2 (K-1) stays recorded under `experiment.inputs.locator_controls`.
- `runbook.yaml` binds the PREVIEW digests of those two files and says so in its header, plus the v3d launch_eks.sh and reconcile_run.sh digests and the unchanged locate_results.sh digest. Edits (exact-once text replacements on the v3c bytes): header and v3d wording, bound digests, `environment.programs`, the argv of S01, S02 and S04, the S02 and S03 `explain` text. No validity assertion, `on_failure`, metric, timeout or TTL changed.
- `tools/runbook.py lint`: worktree: four expected findings (above); approved-state layout: `LINT OK ... 40b4b4bcbc69bc566621e977a83c7abb2621550389e45ff2b2cec68985e64a98`, copied to `runbook-lint.txt`.
- `tools/task_card.py lint CARD-EXP-ICPERF-127dbd-5`: worktree: the four runbook findings (it stops at the runbook lint); approved-state layout: `CARD FAIL` with exactly one finding, `no committed approval decision names this experiment and runbook_sha256 40b4b4bc...` (`evidence/card-lint-real-clone-and-approved-state-sim.txt`). With a stand-in decision (`DEC-STANDIN-SIMULATION`, in a scratch git layout; not a record, not the reserved id) it prints `CARD OK` and the relay text (`evidence/card-prompt-simulated-approval.txt`). Card -5: runbook sha256 as above; its comment header and first `stop_when` name the red-team reconfirmation TASK-20261107-a9406e of the v3d bytes and the CA-bundle sha256 recorded by the top-level session (R-1 T-7); card -4 is unchanged (`git status`: no change).
- `tools/experiment_preapproval.py --packet evidence/preapproval-packet.json` (preview queue, preview executor handoff): in the worktree `approvable false`, 3 blockers, all "not committed with these bytes at origin/main" (canonical specification, lint receipt, launch_eks.sh; locate_results.sh is unchanged and therefore no longer a blocker); in a scratch git layout with the same files committed under `refs/remotes/origin/main` and the goal's lane files, `approvable true`, 0 blockers (`evidence/preapproval-output-real-clone.json`, `preapproval-output-simulated-pushed.json`). The simulation is not an approvability claim.
- Executor handoff preview `TASK-20261107-f14df8`: card -5, launcher v3d, the preview plan digest in `execution.trial_plan_sha256`, DEC-20261107-c3e91a in the inputs; the relay statement names TASK-20261107-a9406e, the top-level session's recorded sha256 of /root/.ccr/ca-bundle.crt (R-1 T-7), and a statement that the relay environment satisfies T-2 to T-4 and CR-1 (names and pass/fail only); two new constraints state the pinned transport and credential forms and the CA custody comparison. The snapshot handoff `TASK-20261107-04d969` has its header line updated and is otherwise the d07e94 preview. The queue preview is the d07e94 preview with the two handoffs replaced and its note rewritten for v3d.
- Card -3 and card -4 are untouched and never relayed. Session id, run id, the two task ids and the reserved decision id are unchanged and unused. The receipt `snapshot-receipt.json` for this task is written by the Coordinator's archive step, not by the director.

## 10. Values the specification did not give (each is a `specification_error` for the Coordinator, none is a default chosen silently)

1. **T-6 `raw-result.json`.** R-1 T-6 says the K7_STATUS "reaches reconcile-result.json and raw-result.json as env_hygiene does now". In v3c only reconcile-result.json carries `env_hygiene`; launch_eks.sh writes no such field to raw-result.json, and V-2 forbids changing launch_eks.sh outside the prologue. For S03 the status line is printed to the trial's stdout (`k7_env_hygiene=...`), which the supervisor captures in `runs/RUN-ICPERF-efb7ef/stdout.log` (an artifact path of the executor handoff). The executor handoff preview names that line, not raw-result.json, as the S03 custody record. If raw-result.json must carry it, that is a change to launch_eks.sh outside the prologue and needs a ruling.
2. **Empty NO_PROXY.** `NO_PROXY=` (set, empty) matches the pin (`*`), is passed, and is recorded as `no_proxy=` (empty after the equals sign), which differs from `no_proxy=none` (unset). R-1 T-6 says `<value|none>`.
3. **Constants.** R-3 says phase 2 "admits [each constant] only with that value". I made phase 1 refuse a caller preset of another value (the handoff's V-6 requires "preset to another value refused"; otherwise `env -i` would drop it silently) and phase 2 refuse when a constant is absent or different (a direct phase-2 start that skips the exec adds nothing).
4. **A preset of the constant value itself** (`AWS_EC2_METADATA_DISABLED=true`, `PYTHONNOUSERSITE=1`) is admitted (D13c, D13d).
5. **Proxy forms.** Port digits are matched as `[0-9]{1,5}` exactly as written (so `:99999` matches); `localhost` and `127.0.0.1` are the only hosts; a trailing slash is the only path. A proxy with no `AWS_CA_BUNDLE` is allowed (T-4 requires a proxy for the bundle, not the converse).
6. **CF-1 entry names** are matched like the v3c names: case-insensitive `^[[:space:]]*name[[:space:]]*=` in `~/.aws/config` and `~/.aws/credentials` (so an indented key inside a sub-section is found); `sso_session` also appears as a section header `[sso-session X]`, which is not matched (only the keys `sso_session =` and `sso_start_url =` are).
7. **Test-only copy for the CA cases** (section 3): the allowed path is a constant of the script, so passing and symlink cases need a copy with a different constant. The shipped constant line is never changed.
8. **`environment.programs`** now lists `/bin/bash` and no longer `bash` (A-1 says "lists /bin/bash"); every other program is unchanged.
9. **Descriptive edits** of the specification (K-7 summary, header, objective), of the runbook `explain` texts of S02 and S03, and the two additions to card -5's first `stop_when` and header are my wording; no value, threshold or assertion changed.
10. **The new prologue lines call `realpath`, `sha256sum` and `cut`** by name, resolved on the clean PATH `<aws dir>:/usr/bin:/bin`, like the `grep`, `head`, `jq` and `dirname` calls that were already there; the trusted-aws-directory residual of d07e94 section 10 therefore also covers them.
11. **Environment values carried unchanged from v3c**: the runbook `environment.env` `CRYPTO_CHECKOUT` and the ecbench path in S01 and S04 are absolute paths into a previous session's scratch directory (`.../scratchpad/v6/repo`, `.../v6/bin-pinned/ecbench`). V-8 does not ask for them to change and I did not change them; the relay must have those paths, or the Coordinator must say what replaces them.

## 11. Residual risk (for DEC-20261107-7802ec and the red team TASK-20261107-a9406e)

- **CA-bundle TOCTOU** (declared by R-1): the sha256 is computed in phase 2; the aws CLI reads the file later. A swap between them is not detected by T-6/T-7 (which catch a change between the top-level session's hash and the run). The platform proxy re-terminates TLS and is trusted as the container runtime is.
- **S03's custody record is a stdout line, not a raw-result.json field** (section 10 item 1).
- **K-8 is still not met**: no read-only IAM identity for S02 (owner-side change). With `AWS_PROFILE`, `AWS_ROLE_ARN`, web identity and container-credential variables dropped, the CLI uses the environment keys (CR-1); what those keys may do is not queried (no AWS call).
- **The directory of the first aws on PATH is trusted** (unchanged): a shim for `python3`, `grep`, `jq`, `realpath`, `sha256sum` or `cut` placed next to aws runs. The relay PATH `/tmp/claude-0/awsvenv/bin` also holds `pip`, `jp.py`, `docutils` and others.
- **The aws-cli configuration surface is still only scanned by name** in `~/.aws/config`, `~/.aws/credentials` and `~/.aws/cli/alias`; system-level configuration, installed plugins and the CLI's actual precedence among `AWS_CA_BUNDLE`, config `ca_bundle` and the environment credentials were not exercised against a real aws CLI (E-1: no real aws ran; the fake only logs). The refused `ca_bundle` entry removes the config route; the precedence statement in DEC-20261107-c3e91a (limitations) remains untested here.
- **S01-probe and S04-verify** are not K-7 scripts: `-p` closes BASH_ENV, ENV, imported functions and SHELLOPTS for them, but their environment is otherwise the caller's. `probe_s01.sh` runs `aws sts get-caller-identity` (an AWS read) in that environment.
- **PS4 vector inert here** (section 6): the argv test for it does not discriminate in this bash.
- **PYTHONNOUSERSITE=1 fails closed** for an aws installed with `pip --user` (section 5.2).
- **The executor container is assumed** to have the same proxy address, CA path and environment-key identity as this one (R-3 CR-3 returns to the Coordinator if not).
- Everything in d07e94 section 10 that v3d does not touch still holds (K-8, multipart ETags, synthetic job outputs, real-CLI behaviours the fake imitates).

### filed_before_affected_data qualification (DEC-20261107-a83c51, copied verbatim; B-FILED-BEFORE-AFFECTED-DATA stays open)

> For S1, filed_before_affected_data is qualified. Before the filing, S1's job-exit fields, the sizes of run-summary.json and records.jsonl, and the PD-1 audit and run.stderr counts had been read. No records.jsonl line, arm statistic, ratio, compare output or parity field had been read. The audit pass bit was already implied by the container exit 42 (run-ecbench exits 41 on an audit failure before 42). S1's bytes are bound to the launcher's 02:14:21Z objects.json by K-2.

## 12. Open blockers (by name)

Ruled by DEC-20261107-c3e91a and implemented here: B-K7-TRANSPORT-ENV (R-1), B-BASH-ENV-FIRST-SHELL (R-2), B-K7-CRED-NAMES and B-K7-CFG-ALLOWED (R-3). Their status after this task is "implemented in v3d bytes, awaiting the red-team reconfirmation", not closed by me.

- **B-RED-TEAM-RECONFIRM**: TASK-20261107-a9406e on the v3d bytes after the v3d snapshot archive; no `runbook_sha256` can be named before it.
- **B-K8-READ-ONLY-IAM**: no read-only IAM identity for S02 (owner-side change); DEC-20261107-7802ec states the residual.
- **B-AMENDMENT-2-WORDING**: v3c narrowed C1-AMENDMENT-2's "results_uri as is" (K-1); the approving decision should acknowledge it (d07e94 section 9 item 8, unchanged).
- **B-FILED-BEFORE-AFFECTED-DATA**: the qualification text above must be in DEC-20261107-7802ec and in the evidence review_plan's blindness joint, verbatim.
- **B-CANONICAL-SPEC-STATE**: the canonical specification and trial plan are review_required and candidate-only drafts; the approved forms exist only under `design/5f7d2b/approval-preview/`. The approval archive swaps them in at the canonical paths; their digests are the ones the runbook binds.
- **B-NOT-PUSHED**: the packet's three blockers clear only after the v3d snapshot archive commit is on `origin/main`.
- **B-QUEUE-ENTRY**: `dispatch_queue.json` has no entry for `TASK-20261107-f14df8` or `TASK-20261107-04d969` until the approval archive adds them (preview in `handoff-previews/`).
- **B-CARD-APPROVAL**: card -5 fails lint only on the missing committed approval decision naming the runbook sha256 (approved-state layout).
- **B-IN-PLACE-REPLACEMENT**: the artifact paths replace launch_eks.sh, reconcile_run.sh, runbook.yaml, specification.yaml, trial-plan.json in place; the stopped session RBS-ICPERF-de8978 binds old bytes. No session or run directory was touched.
- **B-SNAPSHOT-RECEIPT**: `.../archives/TASK-20261107-5f7d2b/snapshot-receipt.json` is written by the Coordinator's archive step; it must also record locate_results.sh unchanged at `668a424b...`.
- **B-S1-COPY-CUSTODY**: unchanged: the reconciled S1 copy (about 96 MB) lands under the session output directory; compaction and custody are the Coordinator's.
- **B-OWNER-NOTICE**: the four-fact notice and the owner's EKS go-ahead are for the top-level session before the relay; the notice now says S2 runs on v3d.
- **B-CA-CUSTODY-RELAY (new, from R-1 T-7)**: the top-level session records the sha256 of /root/.ccr/ca-bundle.crt before the relay; the card and the executor handoff preview state this.
- **B-ENV-PATHS (a carried item, named)**: section 10 item 11.
- **B-CRYPTO-PR**: the crypto change for AMENDMENT-2 still needs its own Conductor task and ready-for-review PR (not opened).
- **B-SESSION-LOG**: `docs/session-logs/2026-11-07.md` was not written by this subagent (outside its write scope).

## 13. What was not done or read

No `git add`, commit or push; no PR; no AWS, kubectl, CodeBuild or isolab call; no call through the platform proxy; no `runbook.py run`; nothing under `runs/` or `runbook-sessions/` written; no ledger record, queue, journal, session log, 9d2b6a or d07e94 file edited (the queue change is a preview file). No records.jsonl, audit, replay, run log, arm statistic or ratio was opened. No pod-uid prefix was read; nothing under `/dev/shm` was used; nothing under `/root/.ccr` was written (only `realpath -e` and `sha256sum` of the bundle; `/root/.ccr/README.md` was not re-read). The container's disk was nearly full (about 100 MB free during the mutation run): an early scratch pre-pass hit ENOSPC for some mutants, those results were discarded and re-run, and the final mutation run keeps only tables and logs. Running the repository tools and tests created gitignored `__pycache__` directories under `tools/` and `orchestration/` (outside the write scope, ignored by git, not staged; deleted again at the end, `git status --ignored` shows none). The scratch layouts used for the lint, card, packet and dry-run simulations (`stage5f`, `stage5g`, `stage5h`, `dryrun5f`) were not records, were never pushed and were deleted at the end; only their outputs are in `evidence/`.
