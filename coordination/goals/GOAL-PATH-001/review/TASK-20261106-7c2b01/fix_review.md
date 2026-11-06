# Focused re-review of the EXP-MONO-1a1be2 fixes (TASK-20261106-7c2b01)

| field | value |
| --- | --- |
| Task | TASK-20261106-7c2b01 (BATCH-69d9a2, GOAL-PATH-001); blocker B8 of DEC-20261106-843cf7; archived by TASK-20261106-649ebb |
| Commit reviewed | `9a0b5955146a6a87584774f8018da3559df86275` ("archive(TASK-20261106-5c1258): snapshot TASK-20261106-4c4831 fixes for EXP-MONO-1a1be2"). The worktree was clean at that commit (`git status --porcelain --untracked-files=all` empty) |
| Card | `ledger/handoffs/TASK-20261106-7c2b01.yaml`, sha256 `76c7cda7c4d38fe9a80753be432aaf3e9748cb7b47b4841e235e796b0aeb11bc`, verified on disk and at the commit |
| Role, policy | Validator, `review-adversarial`, fresh session; instrument re-review, not a claim-changing round, `review_plan: null`; blindness lifted for the 165da2 report only |
| Runs launched | 0. No contract cell was computed. Every gate call ran in a scratch experiment root under the session scratchpad, with a synthetic plan whose only cells are KAT-field cells at (q, n) = (13, 2) |
| Scope | Whether every must-fix of DEC-20261106-843cf7 is closed, whether the fixes regress anything 165da2 found holding, and whether the changed code lets an invalid cell pass as valid or misroutes an instrument defect into a scientific reading. Nothing here concerns the mathematics, H-MONO-23d347 or any prediction value |

## Result

**Terminal verdict for B8: `failed`.**

- **Must-fix items:** 5 closed (F-1, N-1, N-2, N-3, N-4) and 2 not closed (N-5, DEV-1).
- **New findings:** 1 blocking (NF-1) and 6 non-blocking (NF-2 to NF-7).

Three things fail the gate, and any one of them alone would:

- **DEV-1 is not closed.** The FX-16 substitute cell never ran. The producer stopped it on a measured projection of about 33,800 s against the 14,400 s budget (scope finding SF-1). The full cell cannot be run within this review's budget either: the kernel must enumerate all C(B+2, 3) = 1.61e11 multisets whatever the number of targets, and I measured about 4.6e6 to 5.0e6 multisets/s.
- **N-5 item (5) is not closed.** The `.py`-only refusal was implemented as specified. But the unhashed shadowing route it was meant to close stays open through sourceless bytecode.
  - A planted `code/yaml.pyc`, the finding's own example in compiled form, lets a cell pass the gate against the committed unapproved specification text.
  - A planted `code/pytest.pyc` makes the gate record a full "ran" self-test pass for a suite that never ran. That is the F-1 failure mode, and V2-1 cannot detect it after the fact.
- **NF-1 is blocking.** Bytecode in `code/__pycache__/` replaces any hashed module, and `stray_python_files` skips that directory explicitly. The executed code then differs from the approved build while `code_sha256` equals the approved value.

Everything else checked holds:

- **F-1 (a) to (e)** are closed. All 15 165da2 CR-1 scenarios and every RR-2 attack refuse with no `runs/` entry.
- **Full checkout:** the self-test inside the full main checkout collects 379 = `EXPECTED_KAT_ITEMS`.
- **M5** is killed by 8 new or strengthened items, and the vacuity guards are real.
- **FX-8 and FX-11:** every test fails on the 72f51766a6 code and passes on the 5c1258 code (one designed negative control excepted). My own attack on each item behaves as specified, except the gaps listed as NF-2 to NF-7.
- **Plan:** it regenerates byte-identically to `9ccbe614...fb4a`.
- **Regression:** CR-2, CR-4 and CR-5 still hold.

### Must-fix table

| item | fixes | status | evidence (sections below) |
| --- | --- | --- | --- |
| F-1 | FX-2 to FX-6 | **closed** for gaps (a) to (e) | (a) S14 and S17 refuse. (b) A1 to A4 refuse; each attack's control shows it works without the isolation. The full-checkout run collects 379. (c) A5, A6 and A6b refuse. (d) R1 to R6 refuse; P1 runs. (e) The P1 and P2 packages carry the gate and startup_selftest blocks and the hash-matching copies, and `run_cell(kat=False)` raises without a gate. **Caveat:** the F-1 failure mode is reachable again through planted bytecode. It is classified under N-5 (5) and NF-1, not as an F-1 gap, and it clears only with them |
| N-1 | FX-7 | **closed** | M5, applied by me, fails 8 items in the full 379-item suite, all new or strengthened. The guards are recounted independently by brute force: at (41, 6), 169 of 300 random points have index of 2^32 or more, and the constructed keys number 23 at m = 2 and 26 at m = 3; at (29, 7), 266 of 300, and 46 and 44. Membership is nonzero on 50 of 50 throughout. M3 control: see RR-3 |
| N-2 | FX-8 | **closed** (with non-blocking NF-2 to NF-4) | All 11 FX-8 items fail on the old code except the designed KAT-mode negative control, and all pass on the new. My own attacks void or refuse as specified: X second-array recount, B2 group law, arm-C `cdf.json` hist, missing N, F2 on `matched_random_reseeded_aa`, and a hand-planted sentinel (arm A refused, B1 runs) |
| N-3 | FX-9 | **closed** | On a real arm-C KAT cell with a fabricated counted-total offset of +5: lambda equals the counted definition and not the closed form; the flag is false on both bases; the reason and `readings_withheld: [P6]` are present. Unperturbed, the flag is true and lambda follows the counted value |
| N-4 | FX-10 | **closed** | The KAT-mode arm-C package (CLI) has none of `lambda`, `lambda_exact`, `N_cf_formula`, `ncf_counted_equals_formula` or the Poisson keys in `raw-result.json`, `cdf.json` (both levels) or `summary.json` |
| N-5 | FX-11 | **not closed**: item (5). Items (1) to (4) are closed | (1) S15a, S15b and S16 refuse. (2) Encoded, Unicode, full-width and slash-lookalike ids refuse, and a symlinked run directory refuses. (3) `cdf.json` carries `target_seed` and `base_seed`. (4) The three RSS keys are present. (5) A sourceless `code/yaml.pyc` and `code/pytest.pyc` shadow their libraries, and `stray_python_files` returns `[]` (repros N5-Y and N5-P) |
| DEV-1 | FX-16 | **not closed** | `test_kat_extended.py` meets every card check: the q'' rule, the disjointness test, m = 3, n = 2, s = 50, no kernel call in the membership method, and a guard of 25 or more nonzero. Its two helper tests pass. **But the cell was not run in full** (`kat-log-4c4831.json` `FX16.status: stopped_projection_exceeds_budget`, `not_run_in_full: true`; fix report "STOPPED", SF-1). My reduced check (2,500-point sub-base, 10 of FX-16's 50 targets plus 5 constructed) agrees 15 of 15, but it is not the FX-16 cell |

### New findings

| id | severity | finding | repro |
| --- | --- | --- | --- |
| NF-1 | **blocking** | `code_sha256` and `test_file_sha256` hash sources, but Python and pytest execute cached bytecode. Bytecode in `code/__pycache__/` whose header carries the source's mtime and size is executed instead of the hashed `.py`. `stray_python_files` skips `__pycache__` by design (`dirs[:] = [d for d in dirs if d != "__pycache__"]`). By inspection, not run, the same holds for pytest's rewrite cache in `code/tests/__pycache__/` and `test_file_sha256`. A cell whose executed code differs from the approved build ("invalid", invalidation rule 3) therefore records the approved `code_sha256` and passes as valid | NF-1 below |
| NF-2 | non-blocking | The FX-8 raw/summary check compares only per-base `cdf.json` keys. The top-level keys `N`, `s`, `q`, `n`, `seed`, `curve_id` and `cell_id` are never compared. A writer defect in `N` or `s` leaves validity `valid` | own attacks `cdf_top_N` and `cdf_top_s` |
| NF-3 | non-blocking | The R1 check voids on a differing recount or an entirely absent recount, but not when one convention's recount is missing. With `recount["S"]` deleted, the cell stays `valid` | own attack `recount_missing_convention` |
| NF-4 | non-blocking | F2 enforcement edges. (a) The sentinel is checked only in `cmd_cell`; `gate()` plus `run_cell` ignores it. (b) Arm-A cells completed before the sentinel keep `valid`, although stopping rule 2 voids the family, so the analysis must apply `runs/STOP-F2.json`. (c) A broken-symlink sentinel is ignored (`os.path.exists`). (d) Run id `STOP-F2.json` is accepted for any arm: it creates a directory that acts as a false family stop, and `write_stop_f2` would then swallow a true F2 write (`FileExistsError: pass`) | F2 own attacks |
| NF-5 | non-blocking | The large-Q arm-C S-set path has no non-vacuous KAT. This path covers the S target keys of 2^32 or more, `S_counts` (`exceptional_targets`) and `m_S`, which feeds lambda and so P6. My mutant M6 (a uint32 truncation of `S_idx` in `counters.arm_c_cell`) is non-equivalent: the O count at (41, 6) and (29, 7), m = 2, is 14 committed against 0 under M6. M6 survives all 379 items. The committed bytes are correct where checked, so this is a regression-guard gap of the N-1 kind, at the S set instead of the sampled targets. Suggested: compare `S_counts` and `m_S` with the membership method at (41, 6) and (29, 7), including a matched_random base | RR-3 M6 |
| NF-6 | non-blocking | The launcher validity block does not reflect V2-1. A `GateResult` built in a library call with the module's own `_GATE_TOKEN` and fake hashes yields `validity: valid`. A `runs/` that is itself a symlink sends packages outside the experiment directory. The token stops accidental, not deliberate, bypass, so V2-1 must be applied by the analysis | RR-2 library checks; `RID-runs-symlink` |
| NF-7 | non-blocking | In "ran" mode, `peak_rss_kb_children` is the maximum over all reaped children, including the start-up pytest suite and gcc, not the cell's workers. In a KAT B2 cell, children was 58,212 kB against 46,112 kB for self. `peak_rss_kb_total_upper` is honest only as an upper bound; the field name suggests worker memory | own attack `rss_children` |

Observations, not findings:

- **Valid with reasons.** A validity status of `valid` with reasons present occurs only on the P6-withheld path (V2-3 by design: the reasons are recorded, and `readings_withheld: [P6]`). A consumer must honour `readings_withheld`.
- **m in cdf.json.** `cdf.json` carries no `m`. It is recoverable from `multisets` = C(B+m-1, m).
- **Receipt directory clash.** Two `selftest` runs within one second would collide on the receipt directory and exit with a traceback. That direction is a refusal.

## Review environment and bytes

- **Toolchain:** Python 3.11.17, numpy 2.4.6, PyYAML 6.0.1, pytest 9.2.0 (pluggy 1.7.0), gcc 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1). Host: Linux 6.18.44, 4 cores, 15 GiB. The pytest version equals the 5c1258 receipt's `sa5_suite` (9.2.0). `environment-4c4831.json` was not an input and was not read; only its sha256 was checked, by `git show HEAD:<path> | sha256sum`, and it equals the receipt.
- **Scratch:** every scratch file lived under `/tmp/claude-0/-home-user/d72a143b-1bef-500a-b9ca-d25907246d76/scratchpad/7c2b01/`, outside the repository, with `TMPDIR` pointed inside it and `PYTHONDONTWRITEBYTECODE=1`.
- **Extracts:** every extract is a fresh `git archive <commit> experiments/EXP-MONO-1a1be2/code experiments/EXP-MONO-1a1be2/specification.yaml`, for 9a0b5955 and for 72f51766a6.
- **Mutants:** each was applied by a guarded script that asserts the edited source text occurs exactly once. Every mutant kernel compiles with no warning under `-O3 -Wall -Wextra -shared -fPIC -std=c11`.

## RR-1 Byte checks

Commands:

- `git status --porcelain --untracked-files=all`: empty.
- For each FX-1 file, `git show 72f51766a6:<p> | sha256sum`, `git show HEAD:<p> | sha256sum` and `sha256sum <p>`.
- `launcher.code_sha256()`, `code_file_hashes()`, and the sha256 of both test files, from a fresh extract.
- `python3 make_trial_plan.py --out <scratch>/plan.json`, then `sha256sum`.

| file | 72f51766a6 | 9a0b5955 (= disk) | equal |
| --- | --- | --- | --- |
| fqn.py | `c5c967f1...0f09` | `c5c967f1...0f09` | yes |
| curves.py | `9e52804c...fc7f` | `9e52804c...fc7f` | yes |
| semaev.py | `936af457...a9c1` | `936af457...a9c1` | yes |
| kernel.c | `e0152279...c021` | `e0152279...c021` | yes |
| make_trial_plan.py | `b7010bd2...eef9` | `b7010bd2...eef9` | yes |
| throughput_calibration.py | `22a84f63...0f733` | `22a84f63...0f733` | yes |
| specification.yaml | `d81a85b3...c373` | `d81a85b3...c373` | yes |

| recomputed at 9a0b5955 | value | 5c1258 receipt |
| --- | --- | --- |
| `code_sha256()` (seven CODE_FILES) | `5e16c7577d9f0b8820369e2350530d2df52aa9e82aa35313eb1dcf2bdd1de1e3` | equal |
| counters.py | `f085e26ef7efaeb1f6727a102738c03d472b9f62e8ce4e020f5a35bafba024e1` | equal |
| launcher.py | `41afc2cc0db2e091559da97ad0b16aaf6d8d86121a53b6eff2303f298befb1c7` | equal |
| tests/test_kat.py | `c34b8fe0c94faedad8e35a8135a639aa09bfa6b13f1aac2f26d4cc899df2539a` | equal |
| tests/test_kat_extended.py | `79894702c2ee086aa33522233c7933281b4d217abab9dd39163e8f9503ed06b5` | equal |
| `EXPECTED_KAT_ITEMS`, `DESIGNED_SKIPS` | 379; `{"approved": ("tests/test_kat.py::test_launcher_refuses_contract_cell_while_specification_not_approved",)}` | equal |
| regenerated trial plan | `9ccbe61445fba836ec44bdea6e55255220a4d08e8d09c9198e5bd28696d8fb4a`, 135,868 bytes, 453 s | equals the required value and the committed `trial-plan.preview-ac5ad6.json` |

The other declared files (README.md, fix-report, kat-log, mutant-check, and environment-4c4831.json, hashed by `git show`) also equal the receipt's `path_sha256`. The diff 72f51766a6..9a0b5955 under the experiment touches only:

- `code/README.md`, `counters.py` (2 lines), `launcher.py`, `tests/test_kat.py` and the new `tests/test_kat_extended.py`;
- the four `implementation/*-4c4831.*` files;
- the DEC-20261106-843cf7 report directory.

**Outcome: holds.**

## RR-2 F-1: the gate and the start-up self-test

### Method

A harness builds a fresh scratch experiment root for every scenario: `<scratch>/gate/<id>/experiments/EXP-MONO-1a1be2/`.

- **Contents of each root:**
  - a copy of the committed `code/`;
  - the specification text, with only the four status lines changed as stated;
  - a synthetic plan whose single cell is a KAT-field B1 cell, `KAT-B1-gate-n2-q13` at (13, 2) with 30 tuples;
  - a five-field lock hashed exactly as `check_approval` expects (code hash re-implemented independently from the documented definition).
- **Stub suite:** `tests/test_kat.py` is replaced by a 379-item stub: 377 trivial items, `test_host_arith` (passing, or failing where the scenario says so), and the designed-skip node. The lock binds the stub, so the real gate runs in seconds. `launcher.py`, and hence `code_sha256`, is unchanged.
- **Execution:** each scenario calls the real CLI in a subprocess, `python3 -B <root>/code/launcher.py cell --cell-id KAT-B1-gate-n2-q13 --plan <root>/plan.json --run-id RUN-gate [...]`. It then records the exit code, the first stderr lines and whether `runs/` exists.
- **Why a plan cell:** the new `cmd_cell` looks the cell up in the plan before the self-test runs. A `NO-SUCH-CELL` id, which 165da2 used, would never reach the receipt or suite checks, so a KAT-field plan cell is needed for those scenarios. A passing gate runs that KAT cell in the scratch root (positive controls P1 and P2).

### 165da2 CR-1 scenarios (lock and specification)

| id | scenario | exit | `runs/` | first reason |
| --- | --- | --- | --- | --- |
| S1 | missing lock | 3 | no | approval lock missing |
| S2 | empty lock (0 bytes) | 3 | no | unreadable; empty or not a JSON object |
| S3 | lock `{}` | 3 | no | empty or not a JSON object; no approved_by |
| S4 | `[]`, `null`, `"x"`, `7`, `[{"approved_by":"coordinator"}]` | 3 each | no | empty or not a JSON object |
| S5 | lock `approved_by: null`, hashes correct | 3 | no | lock has no approved_by |
| S6 | wrong specification hash | 3 | no | specification_sha256 differs |
| S7 | wrong code hash | 3 | no | code_sha256 differs (invalid build) |
| S8 | wrong plan hash | 3 | no | trial_plan_sha256 differs |
| S9 | specification `review_required` (lock hashed to it) | 3 | no | status is 'review_required'; approved_by is null |
| S9b | status `running`, approved_by set | 3 | no | status is 'running' |
| S10 | specification approved, `approved_by: null` | 3 | no | approved_by is null; lock approved_by differs |
| S11 | `--plan` omitted | 2 | no | argparse usage error |
| S12 | 165da2 hand-written receipt | 3 | no | see R1a to R1c |
| S13 | `curves.py` edited after the lock | 3 | no | code_sha256 differs |
| S14 | `tests/test_kat.py` replaced after the lock (CLI) | 3 | no | test_file_sha256 differs |
| S15a and S15b | approved specification with `execution_authorized: false` / `frozen: false` | 3 | no | execution_authorized / frozen is False, not true |
| S16 | lock `approved_by` differs from the specification's | 3 | no | approved_by differs |
| S17 | v1 four-field lock without `test_file_sha256` | 3 | no | lock has no test_file_sha256 |

### Self-test attacks

Each attack tries to hide a failing item, or to pass with a missing or extra-skipped item.

| id | attack | control without the defence | exit | `runs/` | reason |
| --- | --- | --- | --- | --- | --- |
| A1 | root `pyproject.toml` (`addopts = "-k 'not host_arith'"`) and root `conftest.py` deleting the failing item | plain `pytest -q` in that tree: exit 0, "377 passed, 1 skipped" | 4 | no | pytest exit code 1; failures 1 |
| A2 | `PYTEST_ADDOPTS="-k 'not host_arith'"` | n/a | 4 | no | failures 1 |
| A3 | path-visible plugin: `PYTEST_PLUGINS=hideplug`, `PYTHONPATH=<dir with hideplug.py>` | FX-3 flags with that environment kept: exit 0, "377 passed, 1 skipped, 1 deselected" | 4 | no | failures 1 |
| A3b | the same plugin placed in `code/tests/`, with `PYTHONPATH` inside code/ | n/a | 3 | no | code/ holds .py files outside the expected set |
| A4 | installed `pytest11` entry-point plugin (scratch venv `--system-site-packages`, dist-info with `entry_points.txt`); launcher run with that interpreter | venv python, FX-3 flags, autoload on: exit 0, "1 deselected" | 4 | no | failures 1 |
| A5 | one extra skip (379 collected) | n/a | 4 | no | skipped node ids differ from the designed skips |
| A6 | one missing item (378 collected) | n/a | 4 | no | ran 378, expected 379; collection reports 378 |
| A6b | one failing item, no hiding (stub negative control) | n/a | 4 | no | failures 1 |

### Receipts

R0 is a launcher-written receipt from `launcher.py selftest` in the scratch root:

- 15 fields;
- counts 379 tests, 378 passed, 1 designed skip;
- rootdir equals the code dir, and inifile resolves to `/dev/null`.

| id | attack | exit | `runs/` | reason |
| --- | --- | --- | --- | --- |
| R1a | 165da2 hand-written receipt (`code_sha256`, `test_file_sha256`, `result`) inside `selftest-receipts/` | 3 | no | fields differ (13 missing, `result` extra) |
| R1b | the same, with a genuine `junit.xml` beside it | 3 | no | fields differ |
| R1c | the same, outside `selftest-receipts/` | 3 | no | does not resolve inside selftest-receipts |
| R2 | launcher-written receipt with one `env_key` field changed: `node`, `compiler_version_sha256`, `python_version`, `cpu_model` (4 runs) | 3 each | no | env_key differs from a recomputation |
| R3 | genuine receipt directory copied outside `selftest-receipts/` | 3 | no | does not resolve inside |
| R3b | symlink inside `selftest-receipts/` to that outside copy | 3 | no | does not resolve inside |
| R3c | `selftest-receipts/../../../../R3-outside/receipt.json` | 3 | no | does not resolve inside |
| R4 | `junit.xml` beside the receipt edited (one testcase renamed) | 3 | no | junit_sha256 differs |
| R5 | lock rewritten after the receipt with identical fields but different bytes (sha256 differs) | 3 | no | lock_sha256 differs |
| R6 | receipt `counts` altered | 3 | no | counts differ from the junit beside it |
| P1 | POSITIVE: genuine receipt | 0 | `runs/RUN-p1` | `validity: valid` |
| P2 | POSITIVE: no receipt, in-process self-test | 0 | `runs/RUN-p2` | `validity: valid` |

### Packages and library checks

- **P1 (receipt mode)** carries:
  - a `gate` block: specification, lock, plan, code and test-file sha256, `check_approval_passed: true`, with `code_sha256` = `5e16c757...e1e3`;
  - a `startup_selftest` block: mode, receipt and junit sha256, tests 379, passed 378, the designed skip id, failures 0, errors 0, pytest version, rootdir, inifile and env_key;
  - `selftest/receipt.json` and `selftest/junit.xml`, whose sha256 equal the block's.
- **P2 (ran mode)** carries the same blocks, with `receipt_sha256: null` and the junit copy only.
- **Stubbed package:** a stubbed contract-mode B1 package (`run_arm_b` replaced, real `gate()`) also carries both blocks and the hash-matching junit copy.
- **No gate:** `run_cell(kat=False)` raises `PermissionError` with no gate, with `object()`, and with a `GateResult` built without the token. Nothing is written.
- **Forged token** (NF-6): a `GateResult` built with `launcher._GATE_TOKEN` and fake hashes is accepted.

### Full-checkout self-test (VP-3 substitute)

No separate full worktree fits on this disk. As the dispatching session directed, I used the full main checkout `/home/user/crypto-autoresearcher` strictly read-only.

**Byte identity.** Main HEAD `1378475d64` descends from 9a0b5955. At both commits these objects are identical:

- `experiments/EXP-MONO-1a1be2`: tree `327b6ad1...`;
- `conftest.py`: blob `afaa38ee...`;
- `pyproject.toml`: blob `8b60f44a...`.

`diff -r` of the on-disk experiment directory against `git archive 9a0b5955` differs only by two ignored `reports/*/report.pdf` files outside `code/`.

**Command.** I ran `launcher.run_selftest_suite(<scratch out>)` (the FX-3 command), importing `launcher` from `/home/user/crypto-autoresearcher/experiments/EXP-MONO-1a1be2/code`. The junit and result went to scratch, with `TMPDIR` in scratch.

| run | collected | tests | passed | failures, errors, skips, xfail | rc | rootdir | inifile | wall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full checkout | **379 = `EXPECTED_KAT_ITEMS`** | 379 | 379 | 0, 0, 0, 0 | 0 | `/home/user/crypto-autoresearcher/experiments/EXP-MONO-1a1be2/code` | `../../../../../../dev/null` | 1286.4 s |

**Contrast in the same checkout, without isolation.** `pytest --collect-only -p no:cacheprovider tests/test_kat.py` gives `rootdir: /home/user/crypto-autoresearcher`, `configfile: pyproject.toml`, and the root conftest (`apply_supersession`) is loaded. It collects 379, because the supersession hook does not touch test_kat.py at this commit. The F-1 (b) hazard is therefore live in the real layout, and the FX-3 flags remove it.

**Read-only check.** `git status --porcelain --ignored --untracked-files=all` over the experiment, `conftest.py`, `pyproject.toml` and `tests/conftest.py` was identical before and after. No file under the experiment was newer than the launch, and no `__pycache__` or `.pyc` was created.

**Outcome:** F-1 (a) to (e) closed. NF-6 is non-blocking. The bytecode route is under N-5 (5) and NF-1.

## RR-3 N-1: M5, the vacuity guards and the M3 control

**M5**, my own two-line edit of `kernel.c` `p_idx`:

- `return 2 * Q_;` becomes `return (uint32_t)(2 * Q_);`
- `return 2 * e_code(&p->x) + (yc > nyc ? 1 : 0);` becomes `return (uint32_t)(2 * e_code(&p->x) + (yc > nyc ? 1 : 0));`

I ran the full suite under the FX-3 command (`launcher.run_selftest_suite`) in that extract:

| run | tests | passed | failed | rc | wall |
| --- | --- | --- | --- | --- | --- |
| baseline (unmodified extract; RR-6) | 379 | 379 | 0 | 0 | 1265.5 s |
| **M5** | 379 | 371 | **8** | 1 | 1275.6 s |
| M3 (control) | 379 | 321 | **58** | 1 | 1063.9 s |
| M6 (own extra mutant, below) | 379 | 379 | **0** | 0 | 1245.0 s |

The M5 failing items are all new (FX-7) or strengthened (W10 at n = 6, 7):

- `test_large_q_kernel_point_index_matches_python_index_beyond_2_32[41-6]` and `[29-7]`: kernel index 4035796388 ≠ 8330763684, and 2784965439 ≠ 19964834623;
- `test_large_q_sampled_counter_on_constructed_targets_matches_membership_method[41-6]` and `[29-7]`;
- `test_large_q_sampled_counter_against_membership_method[41-6-2]`, `[41-6-3]`, `[29-7-2]` and `[29-7-3]`.

M5 survived all 316 items at 72f51766a6 (165da2). It is now killed. This agrees with `mutant-check-4c4831.json`, which I treated as a claim, not as evidence.

**Vacuity guards, recounted independently.** I wrote my own script, which uses the test module only to regenerate the test's own constructed keys. It works on the KAT curves `kat|large|q|n` and the full line base (B = 28):

- 300 random points from my own generator (`default_rng(0x7c2b01 + q)`);
- the truth for every target from a brute-force enumeration of all C(29, 2) = 406 and C(30, 3) = 4,060 multisets with Python `E.add` and `counters.target_index` (pure Python);
- the committed kernel and the M5 kernel compared with that truth.

| field | random points with index ≥ 2^32 | kernel = Python index (committed / M5) | test's constructed keys ≥ 2^32 (m = 2 / m = 3) | nonzero truth on those keys | kernel = brute force (committed / M5), m = 2 and m = 3 |
| --- | --- | --- | --- | --- | --- |
| (41, 6), Q = 4,750,104,241 | 169 / 300 | 300 / 131 of 300; O index committed 2Q, M5 wrong | 23 / 26 of 50 | 50 / 50 and 50 / 50 | 50, 50 / 27, 24 |
| (29, 7), Q = 17,249,876,309 | 266 / 300 | 300 / 34 of 300; O index committed 2Q, M5 wrong | 46 / 44 of 50 | 50 / 50 and 50 / 50 | 50, 50 / 4, 6 |

Interpretation:

- **Guard counts are real.** The test's own guards (at least 100 points with index ≥ 2^32; at least 10 keys ≥ 2^32; nonzero membership on every key) are properties of these fields, not artifacts of the producer's code. The producer's logged counts (167, 266; 23, 46) agree with mine on the test's own points and keys.
- **Internal negative control.** My own m = 3 key set happened to have every key below 2^32, and there M5 equals the truth on 50 of 50, as expected.

**M3 control** (`kernel.c` `e_mul`: `for (int k = 2 * n - 2; k >= n; k--)` becomes `for (int k = (n >= 4 ? 2 * n - 3 : 2 * n - 2); k >= n; k--)`): **still killed**, with 58 failed and 321 passed. Every failing item is at n ≥ 4:

| KAT | failing items |
| --- | --- |
| E1 exhaustive, 3 bases × 8 n = 4, 5 cells | 24 |
| E2 at (5, 6, 6) and (5, 7, 7), 2 bases | 4 |
| W2 wide axioms and kernel ops | 8 |
| W4 large-q kernel ops, n = 4..7 | 4 |
| W5 wide group law | 8 |
| W10 at n = 4..7 | 8 |
| FX-7 constructed targets at (41, 6) and (29, 7) | 2 |

That is the 165da2 count of 56 plus the 2 new FX-7 items.

**M6, my own extra mutant** (`counters.arm_c_cell`: `S_idx.astype(np.uint64)` becomes `S_idx.astype(np.uint32).astype(np.uint64)`). It truncates the S-set target keys of 2^32 or more before the kernel call.

- **Non-equivalent.** At (41, 6) and (29, 7), m = 2, the count at S = {O} (index 2Q) drops from 14 to 0. `m_S` and lambda are unchanged on these KAT cells (`m_S` = 0), but `exceptional_targets` changes. At contract arm-C cells (m = n = 6, 7) the S set holds many more points, and `m_S` feeds lambda.
- **Full suite: M6 survives all 379 items** (rc 0, 1245.0 s).
- **Why no test sees it.**
  - W10 and FX-7 compare only the sampled counts (W10 through `arm_c_cell`, FX-7 by calling `run_sampled` directly) and `multisets`.
  - `S_counts` and `m_S` are compared with naive enumeration only on the small E2 fields, where Q ≤ 5^7 and every index is below 2^32.
  - The line base used at large Q has x in F_q, so its S points at m = 3 have small indices.
- **The committed bytes are correct where checked:** the O count of 14 equals the 14 ± pairs of the 28-point base.
- This is NF-5.

**Outcome:** N-1 closed. M5 is confirmed killed by my own mutant run, the guards are real, and M3 is still killed. NF-5 concerns M6.

## RR-4 N-2 (FX-8) and N-5 (FX-11)

### Producer tests on old and new code

The new `tests/test_kat.py` was run with `-k "fx8 or fx11"` (27 items) against:

- a 72f51766a6 extract with only the test file replaced (old `launcher.py` and `counters.py`; the other code files are byte-identical);
- the 9a0b5955 extract.

Both runs used the FX-3 isolation flags and plugin autoload off.

| item | 72f51766a6 | 9a0b5955 |
| --- | --- | --- |
| FX-8: 11 items (valid baseline, recount, group law ×2, raw/summary ×2, identity and curve rule, failed execution, F2 sentinel and refusal, KAT-mode negative control, passing-identity control) | 10 failed (AttributeError: no `gate` or `_write_file`; F2: `assert 3 == 0`); 1 passed (`test_fx8_kat_mode_never_writes_a_sentinel`, a designed negative control that holds on both) | 11 passed |
| FX-11 (1): 3 items | 3 failed (`assert (not True)`) | 3 passed |
| FX-11 (2): 10 run ids | 10 failed (no `resolve_run_dir`) | 10 passed |
| FX-11 (3), (4), (5): 1 item each | failed (KeyError `target_seed`; RSS keys missing; no `stray_python_files`) | passed |
| total | 26 failed, 1 passed | 27 passed |

### My own attacks

All ran on real KAT-field cells at (13, 2) through `gate()` and `run_cell(kat=False)` in scratch roots. These are not the producer's fakes: real arm A, B2 and C computation, with one stated perturbation each.

| item | attack | expected | observed |
| --- | --- | --- | --- |
| baseline | real arm-A (4 bases), B2 and C cells, unperturbed | valid; no false void | A, B2 and C `valid`, no reasons; no sentinel |
| FX-8 R1 | X convention, second recount array only (`differ_second = 1`) on `matched_random` | void | void: "R1 recount differs for base matched_random, convention X" |
| FX-8 R1 | the `S` convention's recount removed entirely | void | **valid** (NF-3) |
| FX-8 group law | B2 cell, third `roots_via_group_law` result perturbed | void | void: `gl_mismatch_generic = 1` |
| FX-8 raw/summary | arm C, `cdf.json` `hist` corrupted by the writer | void | void: "cdf.json key 'hist' (line) differs" |
| FX-8 raw/summary | arm C, `cdf.json` top-level `N` + 1 | void | **valid** (NF-2) |
| FX-8 raw/summary | arm C, `cdf.json` top-level `s` + 1 | void | **valid** (NF-2) |
| FX-8 identity | arm A with `N` missing from the identity | invalid | invalid: "identity field(s) missing ... ['N']" |
| FX-8 F2 | arm A, `i_sum_M` observed + 1 on `matched_random_reseeded_aa` (the producer tested `matched_random`) | void; sentinel inside `runs/` | void; `runs/STOP-F2.json` with `role: matched_random_reseeded_aa`; resolves inside runs/ |
| FX-8 F2 | `runs/STOP-F2.json` planted by hand: arm-A cell, then B1 cell (CLI) | A refused, B runs | A exit 3 "F2 family stop"; B1 exit 0, `runs/RUN-b` |
| FX-8 F2 | sentinel as an empty file / a directory / a broken symlink | refused | refused / refused / **runs** (NF-4 c) |
| FX-11 (1) | lock `approved_by` differing (S16); `execution_authorized: false`, `frozen: false` (S15) | refused | refused |
| FX-11 (2) | run ids `RUN%2e%2e`, `RUN٣`, `ＲUN`, `RUN-∕x` | refused | exit 3, regex |
| FX-11 (2) | `runs/RUN-link` pre-created as a symlink to a directory outside | refused | exit 3, does not resolve inside runs/ |
| FX-11 (2) | `RUN-..-x` (a single component) | accepted, harmless | accepted |
| FX-11 (2) | run id `STOP-F2.json` on a B1 cell, then an arm-A cell | NF-4 d | B1 runs into `runs/STOP-F2.json/`; the next arm-A cell is refused as an F2 stop |
| FX-11 (2) | `runs/` itself a symlink outside the experiment | NF-6 | the run is written outside the experiment |
| FX-11 (3) | KAT arm C `cdf.json` seeds | present | `target_seed` and `base_seed` as {string, int} per base; `m` is not carried (recoverable) |
| FX-11 (4) | contract-mode B2 KAT cell, ran mode | keys present | self 46,112 kB, children 58,212 kB, total_upper 104,324 kB (NF-7) |
| FX-11 (5) | stray module under a different name | refused at import | **not refused**: see N5-Y, N5-P and NF-1 |

### Repro N5-Y (the finding's own example, compiled)

Setup:

- the scratch root keeps the committed specification text (`status: review_required`, `execution_authorized: false`, `frozen: false`);
- a five-field lock is written over those bytes;
- `py_compile.compile(fake_yaml.py, cfile=code/yaml.pyc)`, where the fake delegates to the real PyYAML and rewrites `experiment` to approved, authorized and frozen.

| case | outcome |
| --- | --- |
| control, nothing planted | exit 3: "status is 'review_required'", "approved_by is null" |
| with `code/yaml.pyc` | exit 0; the B1 KAT cell ran; `validity: valid`; `stray_python_files` → `[]` |

V2-1 would still catch this case afterwards, because the gate block records the unapproved specification sha256.

### Repro N5-P (F-1 failure mode)

Setup:

- a scratch root with the stub suite containing a **failing** item, and a correct lock;
- `py_compile.compile(fake_pytest.py, cfile=code/pytest.pyc)`. The fake runs nothing: it writes a junit with 378 passes and the designed skip, prints a `--collect-only` header (`rootdir`, `configfile` → `/dev/null`, "collected 379 items"), and sets `__version__ = "9.2.0"`.

`python -m pytest`, run with cwd = code/, resolves `pytest` to `code/pytest.pyc`.

| case | outcome |
| --- | --- |
| control, nothing planted | exit 4, failures 1 |
| with `code/pytest.pyc` | exit 0; the cell ran; `validity: valid`; `startup_selftest` = {mode ran, tests 379, passed 378, failures 0, pytest_version 9.2.0}; gate `code_sha256` = `5e16c757...e1e3` (the approved value); `stray_python_files` → `[]` |

Every gate hash equals the approved value and the block shows a full pass, so a V2-1 check after the fact passes this cell.

### Repro NF-1 (`__pycache__`)

1. In an extract, copy `counters.py` and replace one 30-or-more-character comment line with `MARKER = "PLANTED-PYC" #xxx…`, padded to the same length, so the size is equal.
2. Set its mtime to that of `code/counters.py`.
3. `py_compile.compile(copy, cfile=code/__pycache__/counters.cpython-311.pyc)`.
4. `import launcher, counters`.

Result:

- `counters.MARKER == "PLANTED-PYC"`;
- `launcher.code_sha256()` = `5e16c757...e1e3`, unchanged;
- `counters.py` source sha256 `f085e26e...24e1`, unchanged;
- `stray_python_files` → `[]`.

pytest's assertion-rewrite cache (`tests/__pycache__/test_kat.cpython-311-pytest-9.2.0.pyc`) is read on the same mtime and size rule even when writing is off. By inspection, the same applies to `test_file_sha256`; I did not run that variant.

**Severity reasoning for N-5 (5) and NF-1.**

- **Both need a file deliberately planted in `code/`.** No accidental route exists: Python never writes sourceless `.pyc` next to sources, and a stale `__pycache__` entry is used only when the source mtime and size match exactly.
- **165da2 graded the `.py` variant non-blocking.**
- **I grade NF-1 blocking, and the N5-P consequence as blocking-grade, for two reasons:**
  - The card's definition: either lets an invalid cell (stopping rule 1, or invalidation rule 3) be recorded as valid.
  - The DEC's accepted limitation for forgeable receipts rests on the receipt and junit bytes being archived and checkable after the fact. These routes leave nothing in the package and pass V2-1.
- The Coordinator composes.

**Suggested repair (for the Coordinator to scope).** All of these are in `launcher.py`, and none touches an FX-1 file:

- Refuse when `code/` holds any file outside an explicit allow-list of every file, not only `.py`; this includes any `__pycache__`, `*.pyc` or `*.so`.
- Run the launcher and the self-test with `PYTHONPYCACHEPREFIX` set to a fresh empty directory. pytest honours `sys.pycache_prefix`.
- Start the self-test without the code directory on `sys.path`: `-P`, or a cwd outside `code/`.
- Import third-party libraries before inserting `HERE` on `sys.path`.

**Outcome:**

- N-2 closed, with non-blocking NF-2, NF-3 and NF-4.
- N-5 items (1) to (4) closed. Item (5) is **not closed** (N5-Y, N5-P).
- NF-1 is blocking.

## RR-5 N-3, N-4 and DEV-1

### N-3 (FX-9)

- **Code:** `counters.arm_c_cell` now sets `lam = Fraction(st["cancellation_free"] - st["m_S"], N - |S|)` and `ncf_counted_equals_formula = (counted == ncf_coefficient(B, t2, m))`. The counting loops are untouched: the diff is these 2 lines.
- **Fabricated mismatch.** On a real arm-C KAT cell (13, 2), m = 2, s = 20, line and matched_random bases, `Kernel.run_sampled` was wrapped to add 5 to the counted cancellation-free total. On both bases:
  - `ncf_counted_equals_formula: false`;
  - `lambda_exact` equals (counted − m_S)/(N − |S|) and does not equal the closed-form version;
  - validity has reasons "P2(vi) mismatch; P6 reading withheld (F7 first)" and "N_cf counted != P2(vi) closed form at base line / matched_random", with `readings_withheld: [P6]`.
- **Status.** The status stays `valid`, as V2-3 intends, because only P6 is withheld.
- **Unperturbed:** the flag is true on both bases, and lambda equals the counted definition.
- **Outcome:** closed.

### N-4 (FX-10)

The CLI `--kat kat --arm C --q 13 --n 2 --s 12` package has none of the four keys or the Poisson keys:

- in `raw-result.json`, either base;
- in `cdf.json`, top level and `matched_random`;
- in `summary.json`.

The counted total is present. **Outcome:** closed.

### DEV-1 (FX-16)

**Code review of `tests/test_kat_extended.py`,** read in full:

| card check | finding |
| --- | --- |
| q'' rule | `Q2 = least_prime_above(10_000)` by trial division |
| disjointness test | present: asserts 10,007, no prime in 10,001..10,006, `(Q2, 2) ∉ launcher.contract_pairs()`, `∉ mtp.contract_cells_qn()`, `∉` the arm-C rule set |
| m and n | m = 3 at n = 2 |
| s | s = 50 |
| membership method | `pair_sum_table` and `membership_counts_m3` use only `E.add`, `E.neg`, `F.sqrt` and `counters.target_index`, which is pure Python (counters.py lines 80 to 85). The kernel is called only by `arm_c_cell` on the compared side |
| vacuity guard | `nonzero >= 25` of 50 is present |

I ran both helper tests, `-k "not m3_large_q_sampled"` with the FX-3 flags: **2 passed** in 3.35 s.

**Did it run in full? No.**

- `kat-log-4c4831.json` `FX16`: `status: stopped_projection_exceeds_budget`, `not_run_in_full: true`, `wall_time_full: null`.
- The fix report: "STOPPED ... The full cell was not run".
- The 5c1258 receipt: `open_for_approval_act: SF-1`.

**Re-run feasibility.** The kernel enumerates every C(B+2, 3) = 161,080,269,536 multiset of the full base (B = 9,886) whatever the number of targets. The card's fallback (a random subset of 10 or more of the 50 targets) therefore does not reduce the cost: the multiset enumeration dominates, and the target count barely affects it. My measured rates:

| sub-base | rate (multisets/s) | conditions | projected full kernel |
| --- | --- | --- | --- |
| 200 | 4.97e6 | loaded host | 32,394 s |
| 2,500 | 4.64e6 | loaded host | 34,727 s |

Both projections lie above the 14,400 s cell budget and above this review's budget. They corroborate SF-1, which measured 4.8e6/s for a projected 33,800 s.

**Closest feasible check (a procedure deviation, stated).** On the substitute curve (F_{10007^2}, seed `kat|large|10007|2|m3`):

- The 50 FX-16 targets came from `counters.arm_c_cell` with the FX-16 target seed. The kernel enumeration was skipped by a capturing wrapper.
- I took the subset `random.Random(0x7c2b01).sample(range(50), 10)` = indices [4, 9, 15, 21, 24, 25, 33, 34, 39, 43], plus 5 targets constructed as sums of 3 sub-base points.
- The base was a sub-base of the first 2,500 line-base points, giving C(2502, 3) = 2,607,292,500 multisets.
- I compared `kernel.run_sampled` at m = 3 with my own Python membership count: a dict from pair-sum index to the sorted larger indices, then `bisect`; no kernel call.

Result:

- 15 of 15 equal;
- nonzero on 10 of 10 FX-16 targets and 5 of 5 constructed;
- multiset count exact;
- kernel 562.1 s, table 42.5 s.

This exercises the depth-3 enumeration at n = 2 on FX-16's own targets. It is **not** FX-16: the base is a sub-base, and 10 of the 50 targets were used.

**Outcome: DEV-1 not closed.** Closure needs a Coordinator act on SF-1. The options the producer listed are a larger budget for the cell (about 9.5 h at the measured rate), a smaller substitute field, or a limitation with a trigger, which the owner direction ruled out for this round.

## RR-6 Regression

**Baseline.** The full `tests/test_kat.py` on a fresh 9a0b5955 extract, under the FX-3 command (`launcher.run_selftest_suite`):

- collected 379, tests 379, **passed 379**;
- failures 0, errors 0, skips 0 (the specification is `review_required`, so the designed skips are `[]`), xfail 0;
- rc 0, 1265.5 s;
- rootdir = the extract's code dir, inifile → `/dev/null`;
- 379 distinct testcase names.

This equals the 5c1258 receipt's `sa5_suite` (379 passed).

**CR-2 seed audit (spot check),** on my regenerated plan:

| check | result |
| --- | --- |
| seed entries | 334 |
| distinct seed strings | **298** |
| `seed_int` ≠ first 16 bytes of SHA-256 | 0 |
| rule violations (curve `f15270\|A\|n\|q\|i` for arms A and B, `f15270\|C\|...` for arm C; base `random\|0`, `twin\|0`, `random\|1`; tuples `\|0` and `\|1`; targets) | 0 |
| cross-role reuse | 0 |
| shared seed strings | 24, all arm-A curve seeds reused by arm B |
| `tuple_seed_aa` | exactly `B1-n2-q251-c0`, `B1-n3-q41-c0`, `B1-n4-q23-c0`, `B1-n5-q11-c0` |
| cells | 96 (A 54, B1 12, B2 12, C 18) |
| curve instances missing a validity identity field | 0 |

The last row means the FX-8 identity check will not mark real cells invalid. **Holds.**

**CR-4 residual withholding:**

- KAT-mode CLI arm A (13, 2): no `identities` in raw, no `composition_residuals` and no `derived` in the summary, no `validity` or `gate` in the manifest, `kat: true`.
- Derived (contract-path) real arm-A KAT cell: the summary names the three residual fields (`vii_…`, `viii_…`, `ix_…`) on all four bases. Only key names were inspected; no value was read.
- The two 165da2 tests for this pass in the baseline.

**Holds.**

**CR-5 KAT refusal.** The contract pairs were taken from the regenerated plan, not from the launcher: 24 pairs, which equal `launcher.contract_pairs()`. `launcher.main(["--kat", "kat", "--arm", a, "--q", q, "--n", n, ...])` for all 24 × {A, B1, B2, C}: **96 of 96 exit 3 with "REFUSED"**, with no `runs/` and no KAT temp directory created. **Holds.**

## RR-7 New-code read

I read every line of the new `launcher.py` (1,301 lines, all of it rather than only the hunks) and the 2-line `counters.py` diff. On the card's examples:

1. **A validity status that is valid while a reason is present.** Only on the P6-withheld path (V2-3, by design, with `readings_withheld`). Every other reason sets void or invalid: `st = "invalid" if invalid else ("void" if void else "valid")`, and the notes come only from the arm-C P2(vi) path.
2. **A receipt check that compares a field to itself.** None found:
   - `code_sha256`, `test_file_sha256`, `lock_sha256`, `expected_items`, `designed_skips` and `env_key` are compared with fresh recomputations;
   - `junit_sha256` with the file beside the receipt;
   - `counts` and the skipped ids with a parse of that file;
   - the pytest version with the host;
   - rootdir with the code dir, and the inifile with `os.devnull`.

   A fully self-consistent forgery (receipt plus junit, `env_key` recomputed) is accepted. That is the DEC's recorded limitation, not new.
3. **A skip set that depends on the cwd.** None:
   - the designed skips follow the specification status (absolute path);
   - the junit node ids follow the fixed `--rootdir`;
   - my CLI runs used cwd = scratch, and the designed skip matched.

   Without the fixed rootdir, the node ids become `experiments/EXP-MONO-1a1be2/code/tests/test_kat.py::…`, as in the full-checkout contrast. That would refuse, which is the safe direction.
4. **A sentinel path outside runs/.** Through the CLI the sentinel is always `RUNS_DIR/STOP-F2.json` (verified). Through the library it is written beside any `outdir`, and the refusal lives only in `cmd_cell` (NF-4 a). A symlinked `runs/` moves both outside (NF-6).

Other defects found by reading are NF-1 to NF-7 above. Compared with the old code:

- the old `run_startup_selftest` fall-through, where a mismatched receipt ran the suite, is gone; a failed receipt raises `GateRefused`;
- `cmd_cell` refuses, in order, on approval, plan cell, run id, F2 sentinel, existing run directory, then gate;
- the self-test temp directory is removed after the cell.

## RR-8 Compliance

- **Experiment cells:** zero. Every gate call ran in a scratch experiment root under the session scratchpad, with a synthetic plan holding only KAT-field (13, 2) cells. KAT computation ran only on KAT fields: (13, 2), (41, 6), (29, 7) and F_{10007^2}. No contract curve was built except in the two plan regenerations (identity fields, which are inputs).
- **Full checkout:** it was used read-only, as directed. Only the KAT suite ran there, with every output in scratch; its state was verified unchanged.
- **Writes:** only `fix_review.md` and `review_attestation.yaml` under `coordination/goals/GOAL-PATH-001/review/TASK-20261106-7c2b01/`.
- **Git and messages:** no commit, push, claim or release. No message was sent, and no prediction value appears anywhere.
- **Scratch:** deleted at the end. Raw outputs (junit files, harness JSON) were not retained; the tables above carry them, and each repro is stated well enough to re-run.
- **Model:** not Bedrock.

## What this review does not establish

- **Mathematics.** Nothing about any lemma, H-MONO-23d347 or any prediction.
- **Contract scale.** Mutant and attack checks ran on KAT fields. Contract-scale behaviour is inferred from identical code paths.
- **FX-16.** The FX-16 cell itself was not run, by the producer or by me.
- **Model independence.** Independence is between sessions only, not between models (see the attestation).
