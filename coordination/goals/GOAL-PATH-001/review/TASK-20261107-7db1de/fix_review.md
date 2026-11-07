# Focused hardening re-review of the second EXP-MONO-1a1be2 fix round (TASK-20261107-7db1de)

| field | value |
| --- | --- |
| Task | TASK-20261107-7db1de (BATCH-c077fd, GOAL-PATH-001); blocker B8-H of DEC-20261106-24d2a2; archived by TASK-20261107-971edf |
| Commit reviewed | `5f6c0924502a804271cc100937bf706021985ed6` ("archive(TASK-20261106-dfd0ed): EXP-MONO-1a1be2 second fix round and DEV-1 record snapshot") |
| Checkout used | `/home/user/crypto-autoresearcher` at HEAD `a640b9f1dd` (descends from the commit), full and non-sparse, used read-only. Every mutant, attack and test ran in scratch extracts (`git archive 5f6c092450`) under the session scratchpad `.../scratchpad/r7db1de/` |
| Role, policy | Validator, `review-adversarial`, fresh independent session; instrument re-review, not a claim-changing round, `review_plan: null`; blindness lifted for the 165da2 `code_review.md` and the 7c2b01 `fix_review.md` only |
| Runs launched | 0. No contract cell was computed and no DEV-1 cell was run. Gate calls used scratch experiment roots with a synthetic plan of KAT-field cells at (13, 2) and (11, 2); the only contract-parameter computation was the trial-plan regeneration RR-1 requires (identity fields, which are inputs) |
| Scope | Whether every hardening must-fix of DEC-20261106-475620 is closed; whether anything 165da2 and 7c2b01 found holding has regressed; whether the changed code lets an invalid cell pass as valid or misroutes an instrument defect into a scientific reading; whether the 96fee7 stop record is honest; and an advisory red-team of the bc7a76 launch design. Nothing here concerns the mathematics, H-MONO-23d347 or any prediction |

## Result

**Terminal verdict for B8-H: `passed`.**

- **Must-fix items: 9 of 9 closed.** These are N-5 item 5, NF-1 to NF-7 and the receipt clash. The DEV-1 row reads "not run (open)" and does not count for B8-H.
- **Closed items of 7c2b01, as regression rows:** F-1 and N-1 to N-4 all still hold.
- **Mutants, all by my own runs under `launcher.run_selftest_suite`:**
  - M6 is **killed**, with 6 items failing in the full 438-item suite.
  - M5 is still killed (8 items) and M3 is still killed (62 items).
- **Plan:** it regenerates byte-identically to `9ccbe614...fb4a`.
- **New findings: 0 blocking, 4 non-blocking** (NF-H1 to NF-H4), plus 8 observations.
  - NF-H1 and NF-H2 are graded non-blocking for stated reasons that the Coordinator may weigh differently (see "Grading line").
  - Each comes with a cheap launcher-only fix.
  - This review does **not** make B8-H conditional on any of them.
  - Any fix adopted before DEV-1 changes `code_sha256` and so voids the bc7a76 binding (DEC-20261106-24d2a2 `dev1_rerun_decision.binds_code_sha256`). Whether to apply them, and when, is the Coordinator's to compose.
- **RR-5H (96fee7 stop record): agree.** The projection arithmetic recomputes from the recorded keys. One minor arithmetic discrepancy in the report's remaining-budget figure is noted (D-1); it does not change the conclusion.
- **RR-9 (advisory, bc7a76 launch design): 13 routes.**
  - **5 block release of bc7a76 as written:** R9-5, R9-7, R9-8, R9-9 and R9-10.
  - 8 do not block release.
  - Each route has a fix. All the blocking ones can be fixed in the releasing act's text and in the supervisor script. None needs a `code/` change.

### Must-fix table

| item | fix | status | evidence (sections below) |
| --- | --- | --- | --- |
| N-5 item 5 | HX-2 | **closed** | N5-Y (`code/yaml.pyc`) and N5-P (`code/pytest.pyc`) exit 3, naming the entry, with no `runs/`. Each control behaves (N5-Y control refuses on the unapproved specification; N5-P control fails the suite, exit 4). With the allow-list switched off in a scratch copy, the import order and the self-test's `-B -P -X pycache_prefix` still defeat both. My own attacks O1 to O4 and O6a refuse. RR-2 |
| NF-1 | HX-2 | **closed** | `code/__pycache__/counters.cpython-311.pyc` (source mtime and size, marker) exits 3. The threat is real (a plain import runs the plant), and the launcher's pycache prefix keeps the hashed source even with the allow-list off. The pytest rewrite-cache variant was **run**: a forged-hash plant makes plain pytest report a full pass for a failing stub, and the launcher exits 3. RR-2 |
| NF-2 | HX-3 | **closed** | The predecessor's `cdf_top_N` and `cdf_top_s` void on real arm-C cells. So do my own `m`+1, `N` as a string, a dropped `matched_random` block and an extra key inside it. The HX-3 tests fail on 9a0b5955 (9 of 13; the other 4 are regression cases already compared there) and pass on dfd0ed. RR-4 |
| NF-3 | HX-4 | **closed** | The predecessor's `recount_missing_convention` voids, with the summary still agreeing, so the reason is the recount. So do my own bool `compared`, an emptied base recount and an extra differing convention. The test fails on old code and passes on new. RR-4 |
| NF-4 | HX-5 | **closed** (non-blocking residual NF-H4) | Edges, each checked through both the library and the CLI: (a) refuses; (b) `family_runs_at_stop` lists the earlier package and the earlier manifest is byte-unchanged; (c) a broken symlink, directory, empty file and symlink to a valid sentinel all refuse arm A while B1 runs; (d) five reserved ids refuse, and a foreign entry at write time gives `invalid` while a valid one gives `void` and is left untouched. 12 of 14 HX-5 items fail on old code; 2 are regression-only. RR-4 |
| NF-5 | HX-6 | **closed** | **M6 is killed by my own run**: 6 new S-set items fail, the same node ids the producer claims. The independent recount confirms the guards are real, and m_S is zero on all 8 KAT cells. M5 and M3 are still killed. RR-3 |
| NF-6 | HX-7 | **closed as specified** (non-blocking residual NF-H3) | The predecessor's forged `GateResult` (token, fake hashes) gives `invalid`. `RID-runs-symlink` refuses and nothing is written outside. A symlinked `selftest-receipts/`, a file `runs/` and a pre-created symlinked run directory all refuse. The 3 HX-7 tests fail on old code and pass on new. RR-4 |
| NF-7 | HX-8 | **closed** | `rss_children` now separates `peak_rss_kb_children_pre_cell` (the self-test child), with `peak_rss_kb_cell_children: null` and its reason. With `workers=2` the workers' own figure is recorded, and the budget check reads self plus cell. RR-4 |
| receipt clash | HX-9 | **closed** | Two **concurrent** CLI `selftest` processes in the same UTC second both exit 0, write distinct receipt directories, both verify, and each then serves as the receipt of a valid KAT cell (P1). The HX-9 test fails on old code and passes on new. RR-4 |
| DEV-1 | (941825 RR-5, moved to B8-D) | **not run (open)** | Not part of B8-H. RR-5H checks only the attempt-1 stop record |

### Regression rows (7c2b01 closed items)

| item | status | evidence |
| --- | --- | --- |
| F-1 (a) to (e) | **closed, holds** | All 165da2 CR-1 scenarios (S1 to S17, incl. S4 ×5) and the 7c2b01 A table (A1 to A6b, incl. the venv entry-point plugin A4) and R table (R1a to R6, R2 ×4) refuse with no `runs/`. P1 (genuine receipt) and P2 (in-process) give `validity: valid`. The packages carry `gate`, `startup_selftest` (now with `pytest_file`) and `code_tree`. The full-checkout self-test collects 438 = `EXPECTED_KAT_ITEMS`. RR-6 |
| N-1 | **closed, holds** | M5 killed (8 items, the same 8 as 7c2b01), and M3 killed (62). RR-3 |
| N-2 | **closed, holds** | X second recount array differs: void. B2 group-law mismatch on the second instance: void. Arm-C `cdf.json` `hist` corrupted in the cdf only: void. Identity `N` missing: invalid. F2 on `matched_random_reseeded_aa`: void with the sentinel. RR-4, RR-6 |
| N-3 | **closed, holds** | Counted cancellation-free total +5 on a real arm-C KAT cell: on both bases the flag is false and lambda equals the counted definition, not the closed form. The reasons are present and `readings_withheld: [P6]`. Unperturbed, both flags are true. RR-6 |
| N-4 | **closed, holds** | The KAT-mode arm-C package (CLI) carries none of `lambda`, `lambda_exact`, `N_cf_formula`, `ncf_counted_equals_formula` or the Poisson block in any file. The counted total is present. `summary.json` carries the raw-histogram `max_count`, unchanged since 9a0b5955 and not a derived key. RR-6 |

### New findings

| id | severity | finding | repro |
| --- | --- | --- | --- |
| NF-H1 | non-blocking (see grading line) | The **launcher process** honours the parent environment's interpreter variables, though the self-test subprocess scrubs them. A stdlib module that the launcher imports after start-up can be replaced from outside `code/`. Neither the manifest nor `environment.json` records `PYTHONPATH`, `PYTHONPYCACHEPREFIX`, `sys.path` or `sys.flags`, and `module_origins` covers only numpy, yaml and pytest. Two variants: (a) `PYTHONPATH=<dir>` holding a `fractions.py` shadow; (b) `PYTHONPYCACHEPREFIX=<dir>` holding planted bytecode for `/usr/lib/python3.11/fractions.py` with the source's mtime and size. Launcher line 156 imports `fractions` before line 171 resets the prefix. In both, the shadow ran, the cell completed with `validity: valid`, and the package holds no trace. The same planted-counters bytecode under the same environment prefix is **not** used (O6b), so `code/` modules are protected | RR-2 O6c, O7c |
| NF-H2 | non-blocking (see grading line) | **Time-of-check gaps inside the cell.** (a) `code/` is `sys.path[0]` in the cell process, and some stdlib modules are first imported during the cell: `multiprocessing` for `--workers > 1`, and `hmac` and `secrets` in arm A. A module planted in `code/` after the gate's last scan, which deletes itself on import, executes with no trace: the post-cell scan is clean and the cell is `valid`. (b) `kernel.c` is compiled from `code/` inside `run_cell`, after the gate's last re-hash. An edit, compile and restore produces a kernel built from other source (marker symbol present in the `.so`) while `rehash_differences: []` and `validity: valid`. Both need a live process writing into `code/` during the cell | RR-2/RR-4 `toctou_lazy_import`, `toctou_kernel_c` |
| NF-H3 | non-blocking | `compute_validity` checks the `startup_selftest` block's fields but not the junit copy in the package. A `GateResult` built in a library call with the private `_GATE_TOKEN`, the **real** on-disk hashes and paths and a real `code_tree` state, but a fabricated full-pass block for a suite that never ran, yields `validity: valid`, and the package has no `selftest/junit.xml`. This is the accepted accident-guard limitation of DEC-20261106-475620 NF-6, now narrowed to "real hashes plus a fabricated block", and it is checkable after the fact (no junit copy) | RR-4 `forged_gate_real_hashes_no_selftest` |
| NF-H4 | non-blocking | The F2 refusal in `run_cell` looks for the sentinel beside `dirname(outdir)`, and `gate()` checks F2 only when given `cell_id`. A library `gate()` without a cell id, followed by `run_cell` on an arm-A cell with `outdir` outside `runs/`, runs while `runs/STOP-F2.json` exists, and the cell is `valid`. The CLI is unaffected (`cmd_cell` passes the cell id and `resolve_run_dir` forces `runs/`). V2-5 at analysis covers any such package that reaches `runs/` | RR-4 `f2_a_library` |

**Observations, not findings:**

- **O-1 (for SC-4).** `launcher.allowlist_sha256()` hashes the entries with a trailing newline, giving `1832f855...11d1`. That is the value written into every manifest's `code_tree.allowlist_sha256` and into `environment.json`. SC-4 makes the dfd0ed form `8a242ebc...6445` (no trailing newline) primary. Any comparison of a manifest's value with the approval record must use the launcher's method, or every cell will look mismatched (false-invalid direction).
- **O-2.** By construction, raw/summary/cdf agreement cannot see a writer defect that is consistent across all three files: N+1 written to all three stays `valid`. `raw["N"]`, `B` and `t2` are compared with the plan identity before writing (`run_arm_c` raises), but not in `compute_validity`. The analysis recomputes, per V2-2.
- **O-3.** m_S is zero on all 8 HX-6 KAT cells (the producer says the same). The large-Q `m_S` accumulation is therefore exercised only with zero counts, and the guard rests on `S_counts`.
- **O-4.** When the gate refuses, the self-test temporary directory is left behind in `TMPDIR` (hygiene only).
- **O-5.** `pytest_file` is taken from the `--collect-only` invocation, as HX-2 (d) specifies, not from the run invocation. The two use identical argv, environment, cwd and prefix.
- **O-6.** In the self-test, pytest's prepend import mode puts `code/tests` first on `sys.path`. The defence of `tests/` therefore rests on the allow-list alone. With the allow-list off, a `tests/yaml.pyc` was imported by the suite (O1, defence-in-depth row). The allow-list runs at import, at the gate (before and after the self-test) and in `selftest`.
- **O-7.** 7c2b01 states, by inspection, that pytest's rewrite cache is read on the mtime-and-size rule. For pytest 9.2.0 it is hash-checked (flags 3, source hash). It is still forgeable, because the header carries only the hash of the real source, and the forged plant works and is refused.
- **O-8.** A hard-linked allow-listed file is a regular file and is accepted. The bytes are still hashed.

### Grading line (NF-H1, NF-H2)

The card's definition of blocking is "could let an invalid cell pass, or misroute an instrument defect into a scientific reading". DEC-20261106-475620 graded NF-1 blocking although it needs a deliberate plant, because it is static, leaves no trace and is cheap to fix. I grade NF-H1 and NF-H2 non-blocking for these reasons:

- **NF-H2 needs a live process with the launcher's uid writing into `code/` during the cell.** Such a process can equally patch the running process (`/proc/<pid>/mem`, ptrace) or swap the kernel `.so` in the launcher's 0700 temp directory. No file-scan design can make "executed = hashed" hold against it. The program's evidence model is also stated against static state at launch and traces checkable afterwards. The producer recorded the generic residual ("a file planted and removed between the pre-gate and post-cell scans is unseen"); this review makes it concrete and cheap to narrow.
- **NF-H1 is outside the approved-build boundary the frozen rules define.** Those rules are specification invalidation rule 3 ("code sha256 differs from the approved build") and V2-6 (a) to (c), which cover `code/` and the origins of numpy, yaml and pytest. A cell under a shadowed stdlib meets both to the letter. The class also includes routes no launcher can close: a modified site-packages numpy, `LD_PRELOAD`, or a planted `site` bytecode under the same prefix, which runs before the launcher does. NF-H1 is nonetheless the most serious of the four:
  - an accidental route exists (a `PYTHONPATH` that happens to hold a stdlib-named module);
  - it leaves no trace;
  - the instrument already treats `PYTHONPATH` as hostile for its self-test (FX-3, HX-2 d) but not for the process that runs the counting code.

  If the Coordinator applies the NF-1 reasoning to NF-H1, that reasoning would make it blocking. I record that reading explicitly.

Recommended fixes, all in `launcher.py`, none touching an FX-1 or HX-1 file. They are listed in "New findings in detail".

## Review environment and bytes

- **Toolchain:**
  - Python 3.11.17 (`/usr/local/bin/python3`; stdlib `/usr/lib/python3.11`), numpy 2.4.6, PyYAML 6.0.1, pytest 9.2.0, gcc 13.3.0.
  - Host: Linux 6.18.44-fc-v300, 4 cores, 15 GiB.
  - This is the toolchain of `environment-96fee7.json`, which I read.
- **Host state:**
  - Boot id `e0e8df54...d550` at the start and at the end, so there was no container restart during the review.
  - No DEV-1 attempt was live. The dispatching session states this (VP-6), and every pytest or `test_kat` process seen in the process table during the review was one of this review's own.
- **Extracts:** every run used a fresh `git archive 5f6c0924502a 'experiments/EXP-MONO-1a1be2/code' 'experiments/EXP-MONO-1a1be2/specification.yaml'` extract. The specification is included, so the not-approved refusal test passes there (the producer's mutant extracts lacked it; see RR-3).
- **9a0b5955 extract:** a `git archive 9a0b5955146a` extract for RR-4, with only `tests/test_kat.py` replaced by the dfd0ed bytes.
- **Python settings:** `PYTHONDONTWRITEBYTECODE=1` and `-B` everywhere, and `TMPDIR` inside the scratchpad.
- **Mutant edits:** each was applied by a script that asserts the edited text occurs exactly once, keeping the file mtime. The M5 and M3 kernels compile with no warning under `-O3 -Wall -Wextra -shared -fPIC -std=c11`.
- **Checkout used (deviation PD-1):** there is no disk for a second full worktree, so VP-3 was met with the main checkout, read-only.
  - HEAD `a640b9f1dd` descends from `5f6c092450` (`git merge-base --is-ancestor`).
  - The dispatch said the experiment tree is byte-identical. It is not quite: the experiment tree object differs (`9332429b` at the commit, `174873d4` at HEAD), solely because HEAD adds `reports/review-DEC-20261106-24d2a2/` (7 files, the 24d2a2 visual report).
  - The `code/` (`d8e76adb`), `specification.yaml` (`3b585041`) and `implementation/` (`88d7cb6e`) tree objects are identical at both commits.
  - The root `conftest.py` (`afaa38ee`) and `pyproject.toml` (`8b60f44a`) blobs are identical too.
  - Nothing in this review reads the added report.
- **Concurrent activity in the shared checkout:** another session wrote into the checkout during the review. I record this; I did not cause it.
  - HEAD moved from `a640b9f1dd` to `54a0f238a0`. Two commits by `coordinator-portfolio-4y7t3o` opened BATCH-342e48 and added only `coordination/goals/GOAL-PATH-001/batches/BATCH-342e48/dispatch_queue.json` and `lanes/BATCH-342e48.lane.json`.
  - Uncommitted changes appeared from 03:02Z: a modified `ledger/goals/GOAL-PATH-001.yaml`, and untracked `ledger/decisions/DEC-20261107-f46a40.yaml` and `ledger/handoffs/TASK-20261107-{5b2b59,88b2fc,af7359,d279a7}.yaml`.
  - None of these touches the reviewed objects. `code/`, `specification.yaml`, `implementation/`, `conftest.py` and `pyproject.toml` are the same objects at the new HEAD, and the experiment's ignored/untracked status was unchanged before and after the full-checkout self-test.
  - None of these files was opened. `DEC-20261107-f46a40` is the id bc7a76 BP-2 names for the releasing act, so not reading it keeps RR-9 independent of it.

## RR-1 Byte checks

Commands:

- `git status --porcelain --untracked-files=all` on the whole repository: empty.
- For each file: `git show 9a0b5955146a:<p> | sha256sum`, `git show 5f6c092450:<p> | sha256sum` and `sha256sum <p>`.
- An independent re-implementation of `code_sha256` (name and sha256 of each of the seven `CODE_FILES`, joined as documented) in a fresh extract.
- Both allow-list serialisations.
- `python3 -B code/make_trial_plan.py --out <scratch>/plan.json`, then `sha256sum`.

| file | 9a0b5955 = 5f6c092450 = disk |
| --- | --- |
| fqn.py | `c5c967f1...0f09`, equal |
| curves.py | `9e52804c...fc7f`, equal |
| semaev.py | `936af457...a9c1`, equal |
| counters.py | `f085e26e...24e1`, equal |
| kernel.c | `e0152279...c021`, equal |
| make_trial_plan.py | `b7010bd2...eef9`, equal |
| throughput_calibration.py | `22a84f63...0733`, equal |
| tests/test_kat_extended.py | `79894702...06b5`, equal |
| specification.yaml | `d81a85b3...c373`, equal |
| launcher.py, tests/test_kat.py, README.md | changed (the 2b7223 write scope); the commit equals disk |

| recomputed at 5f6c092450 | value | dfd0ed receipt |
| --- | --- | --- |
| `code_sha256` (independent and `launcher.code_sha256()`) | `5d5a607d59741b699065c02066d56a2883a34b44431da56c7bfd439b1f731464` | equal (`sa6_code_binding`) |
| launcher.py | `a7dcb7de...c2be` | equal |
| tests/test_kat.py | `6da794c6...5a66` | equal |
| tests/test_kat_extended.py | `79894702...06b5` | equal |
| all 11 `path_sha256` entries | equal (sha256sum on disk) | equal |
| `EXPECTED_KAT_ITEMS`, `DESIGNED_SKIPS` | 438; `{"approved": ("tests/test_kat.py::test_launcher_refuses_contract_cell_while_specification_not_approved",)}` | equal |
| `CODE_TREE_ALLOWLIST` sha256, entries joined by `\n` **without** a trailing newline | `8a242ebc1c51564041564ecc7edc46eef353bba62611ea33da9f1b8604ba6445` | **this is the dfd0ed receipt's `sa5_allowlist.sha256`** |
| the same **with** a trailing newline | `1832f8552b8d0cb0df9824fa0fd61c1a0308675383d8c795ebecaac9d38c11d1` | **this is the fix-report-2b7223.md value, and also what `launcher.allowlist_sha256()` returns and every manifest records** (O-1) |
| allow-list against the committed tree | the 11 sorted entries equal `git ls-tree -r --name-only 5f6c092450 experiments/EXP-MONO-1a1be2/code` exactly; the scan of a clean extract and of the real checkout's `code/` is `ok` | equal |
| regenerated trial plan | `9ccbe61445fba836ec44bdea6e55255220a4d08e8d09c9198e5bd28696d8fb4a`, 135,868 bytes | equal to the required value and to `trial-plan.preview-ac5ad6.json` at the commit |

Neither `throughput_calibration.py` nor `README.md`, the two allow-listed files outside `code_sha256` and the lock, is imported by any cell or by the start-up suite. `grep` over `launcher.py`, the five library modules and `tests/test_kat.py` finds no import. `test_kat_extended.py` is compiled (not run) by one HX-2 test.

**Outcome: holds.**

## RR-2 Executed-code integrity (N-5 item 5 and NF-1)

### Method

My harness (`tools/h.py` in the scratchpad) shares no code with the producer's tests. For every scenario it builds a fresh scratch root `<scratch>/roots/<id>/experiments/EXP-MONO-1a1be2/` containing:

- a copy of the committed `code/`;
- the committed specification with only the four status lines edited (approved, `approved_by: coordinator`, `execution_authorized: true`, `frozen: true`), or left as committed where stated;
- a synthetic plan of KAT-field cells: `KAT-B1-n2-q13`, `KAT-A-n2-q13`, `KAT-A2-n2-q13`, `KAT-C-n2-q13` and `KAT-B2-n2` (instances at q = 13 and 11). Each carries a full identity regenerated from a reviewer seed. (13, 2) and (11, 2) are not contract pairs;
- a 438-item stub `tests/test_kat.py`: 435 trivial items, `test_host_arith` (passing or failing per scenario), a probe item that dumps `sys.flags`, `sys.path`, `sys.pycache_prefix`, cwd, `pytest.__file__` and the relevant environment when `R7_PROBE_OUT` is set, and the designed-skip node;
- a five-field lock, computed by my own code.

Each scenario then runs the real CLI in a subprocess (`python3 <root>/code/launcher.py cell --cell-id ... --plan ... --run-id ...`, cwd in scratch) and records the exit code, the first reasons and the state of `runs/`. A passing gate runs the KAT cell in the scratch root.

### Card repros

| id | plant | exit | `runs/` | first reason | control / defence in depth |
| --- | --- | --- | --- | --- | --- |
| P | positive control, clean root | 0 | `RUN-p` | `validity: valid` | n/a |
| N5-Y | sourceless `code/yaml.pyc` (a delegating fake that rewrites `experiment` to approved, authorized and frozen) against the **unapproved** committed specification | 3 | none | `code/ entry outside CODE_TREE_ALLOWLIST: yaml.pyc (file)` | No plant: exit 3, "status is 'review_required'". Allow-list off in a scratch copy, plant kept: exit 3, "status is 'review_required'" (yaml resolves to the library) |
| N5-P | `code/pytest.pyc` (a fake that writes a 438-item passing junit and a collect header), with a **failing** stub | 3 | none | `... pytest.pyc (file)` | No plant: exit 4, "pytest exit code 1". Allow-list off, plant kept: exit 4 (the real pytest ran and saw the failure) |
| NF-1 | `code/__pycache__/counters.cpython-311.pyc` with the source's mtime and size and a marker line of equal length | 3 | none | `... __pycache__ (directory)` | Threat proof: a plain `import counters` (no prefix) runs the marker. Allow-list off: the cell runs, the marker is **not** executed (the pycache prefix holds) and validity is `invalid` (the post-cell scan still sees `__pycache__`) |
| rewrite cache (**run**) | `tests/__pycache__/test_kat.cpython-311-pytest-9.2.0.pyc`: pytest's rewritten code of a **passing** stub, with the header's source hash forged to the **failing** stub in `code/` | 3 | none | `... tests/__pycache__ (directory)` | Threat proof: plain `python -m pytest` (no prefix) on that tree reports a full pass (437 passed, 1 skipped), while the same tree without the plant fails 1. Allow-list off: exit 4, failures 1 (`-X pycache_prefix` hides the plant from pytest) |

My first rewrite-cache plant copied mtime and size and was rejected by pytest as out of date, so plain pytest still failed. pytest 9.2.0 checks the source hash (O-7). The forged-hash plant above is the working attack.

### My own attacks (not the producer's tests)

| id | attack | exit | `runs/` | outcome |
| --- | --- | --- | --- | --- |
| O1 | sourceless `code/tests/yaml.pyc`. pytest's prepend mode puts `code/tests` **first** on the self-test's `sys.path` (my probe shows it), and the real `test_kat.py` imports yaml | 3 | none | refused, naming `tests/yaml.pyc`. Allow-list off: the self-test imported the fake (the junit collection traceback runs through it at `import yaml`) and then failed collection (exit 4), i.e. the allow-list is the only defence of `tests/` (O-6) |
| O2 | `code/zz_evil.pth` | 3 | none | refused (a `.pth` in `code/` is inert anyway) |
| O2b | zip-importable `code/numpy.zip` | 3 | none | refused |
| O3 | the allowed directory `tests/` replaced by a symlink to an identical copy outside `code/` | 3 | none | refused: "allow-listed path is not a regular file: tests (symlink)" and "allow-listed file missing: tests/test_kat.py" (lstat semantics, the link is never followed) |
| O3b | `code/kernel.c` a hard link to an outside file with the same bytes | 0 | run | `valid`, as expected. A hard link is a regular file and its bytes are hashed (O-8) |
| O4 | planted `code/__pycache__/fqn.cpython-311.pyc` compiled from **different, longer** source, with its header mtime and size **forged** to the real `fqn.py` | 3 | none | refused. Threat proof: a plain import runs it. Allow-list off: the marker is not executed and validity is `invalid` |
| O5 | post-cell plant of a **module shadow** by a stubbed cell: `code/multiprocessing.py` and a `code/json/` directory created during `run_arm_b` | n/a (library) | package | `validity: invalid`: "post_cell_scan ... json (directory); ... multiprocessing.py (file)" |
| O6a | `PYTHONPYCACHEPREFIX=code/.pyc-prefix` holding a path-mirrored planted counters pyc | 3 | none | refused: `.pyc-prefix (directory)` |
| O6b | `PYTHONPYCACHEPREFIX=<outside>` holding a path-mirrored planted **counters** pyc | 0 | run | marker **not** executed: the launcher's own prefix (line 171) precedes the local imports. Valid, correctly |
| O6c | `PYTHONPYCACHEPREFIX=<outside>` holding a planted **stdlib** pyc (`fractions`, imported at line 156, before line 171) | 0 | run | the plant **executed**; `validity: valid`; neither `environment.json` nor the manifest mentions the prefix. **NF-H1** |
| O7 | `PYTHONSAFEPATH=` and `PYTHONPYCACHEPREFIX=<dir>` in the parent environment | 0 | run | The self-test probe shows `safe_path` true, a fresh `mono1a1be2-selftest-pyc-*` prefix, cwd a fresh temporary directory, and `PYTHONPATH`, `PYTHONPYCACHEPREFIX`, `PYTHONSAFEPATH`, `PYTEST_ADDOPTS` and `PYTEST_PLUGINS` absent, with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. The overrides cannot weaken the self-test |
| O7c | `PYTHONPATH=<dir>` holding a `fractions.py` source shadow (it loads the real module afterwards) | 0 | run | the shadow **ran** in the launcher process; `validity: valid`; no trace in the package. **NF-H1** |
| TOCTOU-a | during a real B1 cell with `workers=2`, a hook inside `run_cell` (after the gate's last scan) plants a self-deleting `code/multiprocessing.py` | n/a (library) | package | the planted module **ran**, the post-cell scan is `ok`, and the cell is `valid`. **NF-H2** |
| TOCTOU-b | `kernel.c` edited just before the in-cell compile and restored after (bytes and mtime) | n/a (library) | package | the compiled `.so` has the marker symbol; `rehash_differences: []`; `valid`. **NF-H2** |

Which stdlib top-level modules a real cell imports for the first time (library run, real KAT cells): arm A imports `hmac`, `secrets` and two Cython runtime modules; B1 with `workers=2` imports `multiprocessing`, `_multiprocessing`, `queue`, `_queue` and `__mp_main__`; B1 serial, B2 and C import none.

### Positive control and trace

- **P2:** the clean root runs the B1 KAT cell with `validity: valid`. The manifest's `code_tree` block has all nine keys: `allowlist_sha256` (the trailing-newline value), `pre_gate_scan` and `post_cell_scan` (both `ok`), `file_sha256_at_gate`, `file_sha256_after_cell`, `rehash_differences: []`, `module_origins`, `module_origins_inside_code: []` and `code_dir`.
- **`module_origins`:** numpy `/usr/local/lib/python3.11/dist-packages/numpy/__init__.py`, pytest `/usr/local/lib/python3.11/dist-packages/pytest/__init__.py`, yaml `/usr/lib/python3/dist-packages/yaml/__init__.py`, all outside `code/`.
- **Stubbed package:** a stubbed contract-mode package (the arm function wrapped) carries the same block.
- **`startup_selftest.pytest_file`:** `/usr/local/lib/python3.11/dist-packages/pytest/__init__.py`, outside `code/`.

**Outcome:** N-5 item 5 and NF-1 are **closed**. NF-H1 and NF-H2 are new and non-blocking.

## RR-3 Mutants and vacuity guards

All three edits are mine, each in a fresh extract. The full start-up suite ran through each extract's own `launcher.run_selftest_suite`, so the hardened argv, rootdir, inifile and `pytest_file` checks were the launcher's.

| run | collected | passed | failed | rc | `suite_passed` | wall (4 suites in parallel on 4 cores) |
| --- | --- | --- | --- | --- | --- | --- |
| baseline (unmodified) | 438 | 438 | 0 | 0 | true | 1520.9 s |
| **M6**: `counters.arm_c_cell` `S_idx.astype(np.uint64)` becomes `S_idx.astype(np.uint32).astype(np.uint64)` | 438 | 432 | **6** | 1 | false | 1522.7 s |
| M5: `kernel.c` `p_idx` uint32 truncation of `2 * Q_` and of `2 * e_code(&p->x) + ...` | 438 | 430 | **8** | 1 | false | 1518.1 s |
| M3: `kernel.c` `e_mul` reduction loop starts at `2n-3` for n ≥ 4 | 438 | 376 | **62** | 1 | false | 1364.4 s |

**M6, failing items (killed):**

- `test_large_q_arm_c_S_set_counts_and_m_S_match_a_pure_python_membership_count[41-6-2-line]`
- `[41-6-2-matched_random]`
- `[41-6-3-matched_random]`
- `[29-7-2-line]`
- `[29-7-2-matched_random]`
- `[29-7-3-matched_random]`

All six are new HX-6 items; each fails on the `S_counts` comparison. The two line-base m = 3 items survive, as expected: their S keys are below 2^32.

**M5, failing items (still killed):**

- `test_large_q_sampled_counter_against_membership_method[41-6-2]`, `[41-6-3]`, `[29-7-2]` and `[29-7-3]`;
- `test_large_q_kernel_point_index_matches_python_index_beyond_2_32[41-6]` and `[29-7]`;
- `test_large_q_sampled_counter_on_constructed_targets_matches_membership_method[41-6]` and `[29-7]`.

These are the same 8 items as 7c2b01 found.

**M3, failing items by test function (still killed):**

| test function | failing items |
| --- | --- |
| E1 exhaustive | 24 |
| E2 sampled | 4 |
| W2 wide axioms | 8 |
| W4 large-q ops | 4 |
| W5 wide group law | 8 |
| W10 large-q sampled | 8 |
| FX-7 constructed targets | 2 |
| HX-6 S-set at m = 3 | 4 |

All 62 are at n ≥ 4. That is the 7c2b01 count of 58 plus the 4 new m = 3 HX-6 items.

**Comparison with the producer's claim** (`mutant-check-2b7223.json`, treated as a claim): my failing node-id sets equal the producer's for all three mutants, once the producer's spec-path artefact is netted out. The producer's extracts lacked `specification.yaml`, so `test_launcher_refuses_contract_cell_while_specification_not_approved` also failed there; its own report gives raw counts of 7, 9 and 63. Mine include the specification and show no such failure.

**Independent recount of the HX-6 guards** (`tools/recount_s.py`, my own code):

- **S:** built per the definition (sums of (m − 2l)-multisets of the base, l ≥ 1).
- **Index:** my own implementation of the kernel's `p_idx` (2Q for O; otherwise 2·code(x) + [code(y) > code(−y)], with code(a) = Σ aᵢqⁱ), not `counters.target_index`.
- **Truth:** brute force over all m-multisets with the Python group law.
- **Compared against:** the committed `counters.arm_c_cell` and the M6 truncation, applied to the same keys through `Kernel.run_sampled`.
- **Test module use:** only to regenerate its KAT curves `kat|large|q|n` and bases.

| field | base | m | S keys | S keys ≥ 2^32 | of those, nonzero truth | committed `S_counts` = truth | m_S (committed / mine) | M6 `S_counts` = truth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| (41, 6) | line | 2 | 1 | 1 | 1 | yes | 0 / 0 | **no** |
| (41, 6) | line | 3 | 28 | 0 | 0 | yes | 0 / 0 | yes |
| (41, 6) | matched_random | 2 | 1 | 1 | 1 | yes | 0 / 0 | **no** |
| (41, 6) | matched_random | 3 | 28 | 10 | 10 | yes | 0 / 0 | **no** |
| (29, 7) | line | 2 | 1 | 1 | 1 | yes | 0 / 0 | **no** |
| (29, 7) | line | 3 | 28 | 0 | 0 | yes | 0 / 0 | yes |
| (29, 7) | matched_random | 2 | 1 | 1 | 1 | yes | 0 / 0 | **no** |
| (29, 7) | matched_random | 3 | 28 | 26 | 26 | yes | 0 / 0 | **no** |

How to read the table:

- The guards are properties of the construction. On both fields, at least one S key of 2^32 or more has nonzero truth: S = {O} at index 2Q for even m, and the matched_random points for m = 3.
- The committed bytes are correct on every cell.
- M6 departs from the truth on exactly the 6 cells whose items failed.
- **m_S is zero on every KAT cell examined (all 8)**, so the guard applies to `S_counts` (O-3).

**Outcome:** NF-5 is closed. M6 is killed by my own run, and M5 and M3 are still killed.

## RR-4 NF-2, NF-3, NF-4, NF-6, NF-7 and the receipt clash

### Tests on old and new code

I ran the dfd0ed `tests/test_kat.py` with `-k "hx2 or hx3 or hx4 or hx5 or hx7 or hx8 or hx9 or large_q_arm_c_S_set or <the five changed FX tests> or expected_kat_items_equals"`, 66 items. It ran against a 9a0b5955 extract (old `launcher.py`; every other code file is byte-identical) and against the dfd0ed extract. Both runs used `-B -P -X pycache_prefix`, `--noconftest -c /dev/null --rootdir <code>`, autoload off and a scrubbed environment.

| group | items | old: failed / passed | new: passed |
| --- | --- | --- | --- |
| HX-2 | 17 | 17 / 0 | 17 |
| HX-3 | 13 | 9 / 4 (`[B]`, `[t2]`, `[target_seed]`, `[base_seed]`: already compared per base at 9a0b5955; regression only) | 13 |
| HX-4 | 1 | 1 / 0 | 1 |
| HX-5 (a, b, c ×3, d ×9) | 14 | 12 / 2 (`hx5c[directory]` and `[empty_file]`: old already refused them) | 14 |
| HX-6 S-set KATs | 8 | 0 / 8 (correct bytes pass by design; the M6 kill is the evidence) | 8 |
| HX-7 | 3 | 3 / 0 | 3 |
| HX-8 | 2 | 2 / 0 | 2 |
| HX-9 | 1 | 1 / 0 | 1 |
| changed FX tests and FX-13 | 7 | 6 / 1 (`fx5`, extended with `pytest_file` values: regression only) | 7 |
| **total** | 66 | **51 / 15** | **66** |

These per-node outcomes match the producer's old-code claims in `fix-report-2b7223.md`. Every HX-2 to HX-9 item has its defining test failing on 9a0b5955 and passing on dfd0ed.

### Predecessor attacks and my new attacks (real KAT-field cells)

These are real arm A, B1, B2 and C cells through `gate()` and `run_cell(kat=False)` in scratch roots. Each has one stated writer-side perturbation, injected by wrapping the arm function (as 7c2b01 did), or one CLI condition. Baseline: unperturbed A, B1, B2 and C are all `valid`, with no sentinel.

| item | attack | origin | outcome |
| --- | --- | --- | --- |
| NF-2 | `cdf.json` top-level `N` + 1 | 7c2b01 `cdf_top_N` | **void**: "top-level key 'N' differs" |
| NF-2 | top-level `s` + 1 | 7c2b01 `cdf_top_s` | **void** |
| NF-2 | top-level `m` + 1 | new | void |
| NF-2 | top-level `N` written as a string | new | void |
| NF-2 | `matched_random` block dropped | new | void (per-key differences) |
| NF-2 | an extra key inside `matched_random` | new | void ("unexpected key 'zz'") |
| NF-2 | N + 1 written consistently to raw, summary and cdf | new | `valid` (O-2, by construction) |
| NF-3 | `recount["S"]` deleted (summary shares the dict, so raw and summary still agree) | 7c2b01 `recount_missing_convention` | **void**: "R1 recount missing ... convention S"; no raw/summary reason |
| NF-3 | `X.compared = True` (bool) | new | void |
| NF-3 | one base's recount emptied | new | void: "R1 recount absent for base matched_random_reseeded_aa" |
| NF-3 | extra convention `Z` with a difference | new | void |
| NF-4 (a) | sentinel present; library `gate(cell_id=A)` | 7c2b01 F2 (a) | **refused** |
| NF-4 (a) | the same; library `gate()` without a cell id, then `run_cell` in `runs/` | new | **refused**, no directory created |
| NF-4 (a) | the same; `run_cell` with `outdir` **outside** `runs/` | new | ran, `valid` (**NF-H4**, library only) |
| NF-4 (b) | a valid arm-A cell, a corrupt-manifest directory, then an F2-failing arm-A cell (`matched_random_reseeded_aa`) | 7c2b01 F2 (b), extended | `family_runs_at_stop: [RUN-a0, RUN-corrupt]`, `family_void: true`, the first manifest byte-unchanged, the failing cell void, `sentinel_problem: None` |
| NF-4 (c) | `runs/STOP-F2.json` as a broken symlink, directory, empty file, or **symlink to a valid sentinel** (CLI) | 7c2b01 F2 (c), extended | arm A exits 3 "F2 family stop" in all four; B1 runs in all four |
| NF-4 (d) | run ids `STOP-F2.json`, `stop-f2.JSON`, `STOP-F2.json.bak`, `Stop-x`, `sToP-` (CLI) | 7c2b01 F2 (d), extended | all exit 3 "reserved"; `STOPPED-ok` accepted |
| NF-4 (d) | a directory / a symlink to a valid sentinel planted at `runs/STOP-F2.json` during an F2-failing arm-A cell | new | `invalid`, `f2_sentinel_invalid` set (not a regular file), entry left |
| NF-4 (d) | a valid sentinel written during the cell | new | `void`, "already recorded", `sentinel_already_existed: true`, sentinel untouched |
| NF-6 | `GateResult` with `_GATE_TOKEN` and fake hashes | 7c2b01 forged GateResult | **invalid**: V2-1 reasons for specification, lock, plan and code |
| NF-6 | `GateResult` with `_GATE_TOKEN`, **real** hashes and paths, a real `code_tree` state and a fabricated full-pass self-test block | new | `valid`; the package has no `selftest/junit.xml` (**NF-H3**) |
| NF-6 | `runs/` a symlink outside (CLI) | 7c2b01 `RID-runs-symlink` | **exit 3** "runs/ is not usable ... is a symlink"; the outside directory stays empty |
| NF-6 | `runs/` a regular file; `runs/RUN-x` pre-created as a symlink; `selftest-receipts/` a symlink (library `gate` and CLI `selftest`) | new | all refuse; nothing is written outside |
| NF-7 | contract-mode B2 KAT cell, "ran" mode | 7c2b01 `rss_children` | `peak_rss_kb_children_pre_cell` holds the self-test child; `peak_rss_kb_cell_children: null` with reason "cell spawns no child process"; the budget check reads self + cell |
| NF-7 | B1 with `workers=2` | new | `peak_rss_kb_cell_children` is the workers' own figure; the reason is "max over the workers' own getrusage(RUSAGE_SELF) reports"; the budget value is self + cell; `valid` |
| clash | two **concurrent** CLI `selftest` processes (one UTC second) | new | both exit 0; directories `<stamp>-5d5a607d-<pid1>-0` and `<stamp>-5d5a607d-<pid2>-0`; both verify; each serves as a receipt for a `valid` cell |

**Outcome:** NF-2, NF-3, NF-4, NF-6, NF-7 and the receipt clash are **closed**. NF-H3 and NF-H4 are new and non-blocking.

## RR-5H The DEV-1 attempt-1 record (not DEV-1 closure)

Read in full: `dev1-report-96fee7.md`, `dev1-kat-log-96fee7.json`, `dev1-junit-96fee7.xml` and `environment-96fee7.json`. Their sha256 equal the dfd0ed `path_sha256`. Treated as claims.

| check | result |
| --- | --- |
| outcome is `stopped_infrastructure` | yes: kat-log `outcome`, the report heading, the receipt's `dev1_outcome_detail` |
| junit is a labelled placeholder | yes: a comment states that no pytest junit exists and that the file is written by the Executor, with `testsuite name="placeholder-no-junit-produced" tests="0"` |
| no per-target pair, guard count or full-pass rate presented as data | yes: `count_pairs_kernel_membership`, `guard_nonzero_targets`, `kernel_multisets_per_s_full_pass`, `peak_rss_kb_test_process`, `multiset_count` (top level) and `junit_cases` are all null, and `junit_counts` is `{}`. The only rates are under `dx3_projection.kernel_multisets_per_s_partial` (projection sub-bases, labelled partial) |
| before, after and repo hashes equal the dfd0ed committed bytes | yes: `dx1_hashes_before.files`, `dx1_hashes_after.files` and `repo_code_hashes_after` each equal the 11 sha256 of `git show 5f6c092450:...` exactly; `code_sha256` is `5d5a607d...1464` before and after |
| `test_kat_extended.py` unmodified | yes, `79894702...06b5` |
| projection measured before the cell by the DX-3 sub-base method | yes. Sub-bases of 800, 1,250 and 2,500 points, the pair-sum table's first 200 rows, a one-target query. `dx3_projection.started` and `finished` convert to 23:11:23Z and 23:23:28Z, before the cell's `start_utc` 23:24:12Z. `wall` equals finished − started and is within the 1,200 s limit |
| modelled total follows from its recorded inputs | **agree.** Recomputed from the keys alone (nothing re-run): each `multisets` = C(sub_B + 2, 3); `multiset_count` = C(B + 2, 3) for `B`; each `fraction_of_multisets` = multisets / multiset_count; `kernel_projection_each` = seconds / fraction (all three); `kernel_multisets_per_s_partial` = multisets / seconds; `kernel_linear_in_multisets` = the largest sub-base's projection; `pair_sum_table.fraction_of_entries` = Σ_{i<200}(B − i) / C(B + 1, 2); its projection = seconds / fraction; `queries_50_targets` = 50 × `queries_one_target_seconds`; `total` = the sum of the three. Every one agrees to float rounding. The total is within the 39,600 s go threshold (margin under 5%). The go decision is robust to the choice of sub-base: the most pessimistic of the three projections, plus the same table and query terms, is also within the threshold |
| the cell was not shrunk | yes: the recorded argv ends in the whole `tests/test_kat_extended.py` with no `-k` and no node id. The test reads only `KAT_EXT_LOG_PATH` from the environment and has no size hook |
| the cell was not restarted | yes: one `start_utc`, one kill. The report states the reason for not restarting (the remaining budget was below the projection) |

Discrepancies (findings of the record, all non-blocking):

- **D-1.** The report says "at the 01:32Z kill-detection time about 33,500 s remained". From its own stated task start (about 23:05Z) and the 43,200 s budget (deadline about 11:05Z), the figure is about 34,380 s. The understatement is about 880 s. The conclusion (below the projection, so no restart) is unchanged.
- **D-2.** The cell start is given as 23:24:10Z in the report and as 23:24:12Z (`start_utc`) in the kat log, 2 s apart. Trivial.
- **D-3.** The statement that `stdout.log` showed two progress dots is not checkable: the log is not archived. It is not presented as data.
- **OBS-1 of DEC-20261106-24d2a2**, the before-record written by a second hashing pass after the cell started, is confirmed as described. The values equal the committed bytes.

**RR-5H outcome: agree.** The record is honest. DEV-1 stays open.

## RR-6 Regression

**Baseline.** The full `tests/test_kat.py` on the committed bytes, under `launcher.run_selftest_suite` in a fresh extract:

- collected 438; tests 438; **passed 438**; failures 0, errors 0, skips 0 (the specification is `review_required`, so the designed skips are `[]`); xfail 0;
- rc 0, `suite_passed: true`;
- rootdir = the extract's code dir, inifile → `/dev/null`, `pytest_file` outside `code/`.

This equals `EXPECTED_KAT_ITEMS` and the dfd0ed receipt's `sa6_suite`.

**Full checkout (read-only).** The self-test ran inside `/home/user/crypto-autoresearcher`, full and not sparse: `launcher.run_selftest_suite(<scratch out>)`, importing `launcher` from `/home/user/crypto-autoresearcher/experiments/EXP-MONO-1a1be2/code`, with junit and results in scratch and `TMPDIR` in scratch.

- **Stray files:** the checkout's `code/` holds **no** stray ignored file. `git status --porcelain --ignored --untracked-files=all` lists only the four `reports/review-*/report.pdf` files outside `code/`. `launcher.scan_code_tree` of the real `code/` is `ok`, with 12 entries. So there was nothing for the gate to refuse, and nothing was cleaned.
- **Result:** collected **438 = `EXPECTED_KAT_ITEMS`**; tests 438; passed 438; failures, errors, skips and xfail all 0; rc 0; `suite_passed: true`; wall 1334.6 s. rootdir = `/home/user/crypto-autoresearcher/experiments/EXP-MONO-1a1be2/code`, inifile → `/dev/null`, `pytest_file` = `/usr/local/lib/python3.11/dist-packages/pytest/__init__.py` (outside `code/`).
- **Contrast without isolation, same checkout:** `python3 -B -X pycache_prefix=<scratch> -m pytest --collect-only -p no:cacheprovider tests/test_kat.py` from `code/` reports rootdir `/home/user/crypto-autoresearcher` and configfile `pyproject.toml`, and node ids carry the `experiments/EXP-MONO-1a1be2/code/` prefix. The F-1 (b) hazard is therefore live in the real layout, and the hardened command removes it. Without isolation, the prefixed node ids would not match `DESIGNED_SKIPS`, so the result would be a refusal (the safe direction).
- **Read-only check:** `git status --porcelain --ignored --untracked-files=all` over the experiment, `conftest.py`, `pyproject.toml` and `tests/conftest.py` is identical before and after the run and the contrast. No file under those paths is newer than the launch marker, and no `__pycache__`, `.pyc` or `.pytest_cache` exists under the experiment.

**165da2 CR-1 scenarios and the 7c2b01 RR-2 S, A and R tables.** These were re-implemented on my harness; each refuses as before.

- **S1 to S17:** S1 exit 3; S2; S3; S4 `[]`, `null`, `"x"`, `7` and `[{"approved_by":"coordinator"}]`; S5; S6; S7; S8; S9; S9b; S10; S11 (exit 2, argparse); S12 (the hand-written receipt); S13; S14; S15a; S15b; S16; S17. Every one exits 3 (S11 exits 2), with no `runs/`, and the first reason names the condition.
- **A1, root `pyproject.toml` `addopts` plus a root `conftest.py` that deletes the failing item:** the control (plain pytest in that tree) gives 436 passed, 1 skipped, so the hiding works. The launcher exits 4, "pytest exit code 1".
- **A2 (`PYTEST_ADDOPTS`), A3 (`PYTEST_PLUGINS` with a `PYTHONPATH` plugin), A5 (one extra skip), A6 (437 collected) and A6b (one failing item):** all exit 4.
- **A3b, the plugin placed inside `code/tests`:** exit 3, naming the stray.
- **A4, a `pytest11` entry-point plugin in a scratch venv (`--system-site-packages`), run with the venv interpreter:** the control (venv, autoload on) gives 436 passed, 1 skipped. The launcher exits 4.
- **R0:** a launcher-written receipt with 16 fields (15 plus the new `pytest_file`); counts 438 tests, 437 passed, 1 skipped; rootdir = the code dir; inifile → `/dev/null`.
- **R1a/S12, R1b, R1c, R2 (`node`, `compiler_version_sha256`, `python_version`, `cpu_model`), R3, R3b, R3c, R4, R5 and R6:** all exit 3 with the expected reason.
- **R7 (new), a receipt `pytest_file` inside `code/`:** exit 3.
- **P1 (genuine receipt) and P2 (in-process self-test):** both exit 0 with `validity: valid`.

**Spot checks.**

- **CR-2 seed audit** of my regenerated plan:
  - 334 seed entries and 298 distinct strings; no `seed_int` mismatch against SHA-256.
  - No rule violation (curve, base, tuple and target strings per arm); no cross-role reuse. The 24 strings used twice are all arm-A curve seeds that arm B reuses.
  - `tuple_seed_aa` is on exactly `B1-n2-q251-c0`, `B1-n3-q41-c0`, `B1-n4-q23-c0` and `B1-n5-q11-c0`.
  - 96 cells (A 54, B1 12, B2 12, C 18). **Holds.**
- **CR-4 residual withholding:**
  - The KAT-mode CLI arm-A cell (13, 2) has no `identities` in raw, no `composition_residuals` or `derived` in the summary, no `validity` or `gate` in the manifest, and `kat: true`; it is not under `runs/`.
  - A contract-path (derived) real arm-A KAT cell names the residual fields `vii_`, `viii_` and `ix_` on all four bases. I inspected key names only.
  - **Holds.**
- **CR-5 KAT refusal:**
  - The contract pairs were taken from the regenerated plan: 24, equal to `launcher.contract_pairs()`.
  - `launcher.main(["--kat", "kat", "--arm", a, "--q", q, "--n", n, ...])` over 24 pairs × {A, B1, B2, C} gives **96 of 96** exits of 3 with "REFUSED", with no `runs/` and no KAT temporary directory created.
  - **Holds.**

**Outcome:** no regression.

## RR-7 New-code read

I read every line of the new `launcher.py` (1,794 lines). For `tests/test_kat.py` I read every changed hunk of the 9a0b5955..5f6c092450 diff and the whole new HX section (lines 2293 to 2919). For the card's examples:

1. **An allow-list that follows symlinks, or is computed from the tree it checks.** Neither.
   - `CODE_TREE_ALLOWLIST` is a constant tuple in `launcher.py`, so `code_sha256` binds it.
   - `scan_code_tree` uses `os.scandir` plus `os.lstat` and never follows a link; a symlinked allowed directory is `not_regular` (O3).
   - `allowed_dirs` is derived from the constant, not from the tree.
2. **A post-cell scan whose result is not wired into validity.** It is wired. `run_cell` builds `code_tree_block(gate.code_tree)` after the cell, and `compute_validity` adds `code_tree_problems` to the invalid reasons. O5 and the producer test show it. Even with `ALLOWLIST_CHECK_ENABLED = False`, a planted `__pycache__` still makes the cell `invalid` (NF-1 and O4 defence rows).
3. **A pycache prefix set after a local import.** Not after a local import: lines 167 to 171 precede the local imports at line 196. It is, however, set after the stdlib imports at lines 139 to 156, which is the NF-H1 (b) route.
4. **A `module_origins` check that compares a path to itself.** No.
   - `module_origins` compares each module's `__file__` with `code_dir` by realpath.
   - `verify_receipt` compares the receipt's `pytest_file` with this process's `pytest.__file__`.
   - `gate_and_selftest_problems` compares the gate block with a recomputation from the files named in `GateResult.paths` (hence NF-H3 for a forged `paths`).
   - Two checks are tautological at write time but harmless: `code_tree_problems` compares `allowlist_sha256` with the same constant's digest, and `file_sha256_at_gate != file_sha256_after_cell` duplicates `rehash_differences`. They only guard a later edit of the manifest.
5. **An F2 sentinel check reachable only by the CLI.** No: `gate(cell_id=...)` and `run_cell` both check. The remaining library-only gap is NF-H4.

Other points from the read:

- `gate()` re-scans and re-hashes after the self-test, so the "at the gate" hashes postdate the suite.
- A failed receipt raises; it never falls through to a run.
- `cmd_cell` refuses, in order, on approval, plan cell, run id (regex, reserved `STOP-`, `runs/` a real directory inside the experiment), an existing run directory, then the gate (code tree, `runs/` and `selftest-receipts/` real, approval, F2, self-test).
- `code_sha256()` always hashes `HERE`, while `gate(code_dir=...)` scans `code_dir`. Through the CLI they are the same directory; a library call with another `code_dir` would scan one tree and hash another (library only, part of NF-H3's class).
- `resolve_run_dir` is checked before the multi-minute gate, and `run_cell` then uses `makedirs(exist_ok=True)` without re-checking. That is a live-writer window of the NF-H2 kind.
- Nothing else found would let an invalid cell pass as valid or route an instrument defect into F7 or F8.

## RR-8 Compliance

- **Experiment cells:** zero. No DEV-1 cell was run, and `test_kat_extended.py`'s cell item was never invoked. Every gate call used a scratch experiment root with the synthetic KAT-field plan.
- **Contract-parameter computation:** the one trial-plan regeneration only.
- **Full checkout:** used read-only, with outputs in scratch and its state compared before and after (RR-6).
- **Writes:** only `fix_review.md` and `review_attestation.yaml` under `coordination/goals/GOAL-PATH-001/review/TASK-20261107-7db1de/`. No commit, no state-changing git command, no claim or release (the top-level session holds claim `a640b9f1dd`).
- **Long commands:** each full suite (about 1,520 s under load) and the full-checkout suite ran as harness background tasks well below the 6,000 s detach threshold. None needed `setsid nohup`.
- **Infrastructure:** no container restart hit a review command (boot id unchanged).
- **Bytecode:** no `__pycache__` or `.pyc` was created in the repository (`find` before and after).
- **Messages:** none sent, and no prediction value anywhere.
- **Model:** not Bedrock.
- **Scratch:** retained under the session scratchpad, outside the repository. It is not an artifact.

## RR-9 Advisory red-team of the bc7a76 launch design (LD-1 to LD-12)

**Method.** I read LD-1 to LD-12 and `tests/test_kat_extended.py`, which bc7a76 runs unchanged. I then exercised the LD-8 classification on a toy stub (`sleep`, exit codes and stub files, never the cell). That used a **toy supervisor I wrote from the LD-4 text** (`tools/toy_sup.sh`) and a **literal LD-8 classifier** (`tools/rr9.py`).

Facts that shape the routes:

- The test writes the KAT log **only** in a module-scoped autouse fixture's teardown, and **only if `KAT_EXT_LOG_PATH` is set**. pytest writes junit at session end.
- In this container, PID 1 is `process_api`. A detached supervisor killed with `-9` stays a zombie (state Z) for about 2 s before it is reaped, and during that window `/proc/<pid>/stat` still shows the recorded start time.
- The session scratchpad survives container restarts here: its files date back to 2026-10-22 and it is on the same ext4 root as the repository. The LD-7 basis for the state directory can cite this.

"Blocks release" means the route can record a killed, restarted, partial, substituted or re-run cell as passed or mismatch, or lets the executed command or bytes differ from the bound ones without a trace. The fixes are to the card or releasing-act text and to the supervisor script; none touches `code/`.

| id | route | toy result (literal LD-8) | severity | fix |
| --- | --- | --- | --- | --- |
| R9-1 | **kill -9 of the supervisor while the cell lives.** `timeout` and the cell are orphaned and run on unsupervised; the cell may later write junit and the KAT log into the state directory with no `exit.json` | zombie window: C7; then **C6** while the orphan still runs; C6 again after the orphan wrote junit and the KAT log | does not block (yields a stop, never passed or mismatch) | The supervisor writes `child.json` (the `timeout` pid and start time, the cell's pid, start time and `/proc/<pid>/cmdline`) right after spawning. On C6, the check-in finds the recorded session or process group (`pgrep -s <sid>`), records any survivor and kills it (TERM, then KILL) before the class is final. Anything written after the supervisor's death is recorded but never collected as a result. Liveness requires state ∉ {Z, X} |
| R9-2 | **kill -9 of the cell (or an OOM kill) while the supervisor lives.** `timeout` returns 137, which LD-4 (d) equates with a watchdog kill | rc 137 → `timeout_fired: true` → **C3 watchdog** after 2 s of a 30 s watchdog. The genuine kill-after case (R2b) gives the same rc | does not block (both are no-retry stops), but the cause is misattributed and an anomalous OOM is hidden | `timeout_fired` only if rc = 124, or rc = 137 with `elapsed_s` ≥ the watchdog. Run `timeout --verbose` and keep its stderr line. Otherwise C8, with `dmesg` checked for an OOM of the recorded pid |
| R9-3 | **PID reuse after a restart.** The recorded supervisor pid is reused by an unrelated process, or a zombie keeps the pid with the same start time | (zombie shown in R9-1) | does not block (can hang in C7; never passed or mismatch) | If restart evidence is present, the supervisor is dead by definition (skip the pid test). Otherwise require state ∉ {Z, X}, equal start time, and `/proc/<pid>/cmdline` naming the supervisor script and state directory. Give C7 an absolute deadline (launch + watchdog + kill-after + 1,800 s), after which C6 |
| R9-4 | **A container restart that leaves boot_id, the PID 1 start time and uptime unchanged** (a VM snapshot restore; or a shared PID namespace) | not exercisable here | does not block passed or mismatch: all processes lost gives C6 (no retry, safe); processes restored means the cell resumes. But `timeout` runs on the real-time clock and the kernel wall time feeds SC-3's full-pass rate, so a pause or restore can fire the watchdog early or distort the rate | Heartbeats also record `/proc/uptime`, `CLOCK_BOOTTIME` and the cell's utime + stime (`/proc/<pid>/stat` 14 and 15). Mark the attempt `timing_unreliable` (rate not usable for SC-3) on any heartbeat gap > 2× the interval or a wall-versus-CPU divergence. Add a tmpfs marker (`/dev/shm/<attempt>.marker`); its absence is restart evidence |
| R9-5 | **A wall-clock jump.** LD-8's third restart test ("uptime shorter than the time elapsed since launch") uses wall-clock elapsed time | the supervisor killed (no restart): no jump gives C6; **a forward jump gives C5, "retry allowed"**; a backward jump gives C6 | **blocks release**: a false C5 authorizes a retry after an unexplained kill while the attempt's orphaned cell (R9-1) may still run. The retry (a re-run) can then be recorded as passed while the earlier cell's own completion, possibly a mismatch, is never read | Restart evidence only from boot_id, the PID 1 start time and **uptime_now < uptime_at_launch**, never from wall-clock elapsed time. Before any C5 retry, require no live process in the recorded session or process group, and no `junit.xml` or `kat_ext_log.json` in the attempt's state directory |
| R9-6 | **A state directory on a path that does not survive a restart** | gone without restart evidence: C6; gone with restart evidence: C5, as LD-8 says | does not block | Keep it. Also write the launch record (pid, start, sid, boot_id, PID 1 start, uptime, launch UTC) into `dev1-attempts-bc7a76.json` in the working tree before launch, so classification does not rest on RESUME.md alone. Here the scratchpad is observed to survive restarts |
| R9-7 | **A stale `exit.json` from an earlier attempt.** LD-8 says to ignore one "whose attempt id differs", but LD-4 (d) writes no attempt id, and nothing makes the supervisor refuse a non-empty state directory | in a reused directory, a toy's `exit.json` (rc 0), junit (3 passed) and KAT log, with the real launch then lost: **C1 passed** from stale artefacts. `attempt_id` is absent from `exit.json` | **blocks release** (the staleness rule is unimplementable as written, and the result is a false "passed") | `exit.json` and every heartbeat line carry `attempt_id`, the supervisor pid and start time and the argv sha256. The supervisor `mkdir`s a **new, empty** state directory and refuses otherwise. Classification requires `exit.json.attempt_id` = `state.json.attempt_id` = the RESUME attempt id, and `exit.json` end later than launch |
| R9-8 | **junit present while the KAT log is absent** (for example, `KAT_EXT_LOG_PATH` not exported to the detached child) | rc 0, junit 3 passed, no KAT log: **C1 "mismatch"** (DX-6 cannot be shown, and C1 says "otherwise mismatch") | **blocks release**: it records an infrastructure defect as a terminal KAT mismatch (B1 reopens, never re-run) | C1 requires `kat_ext_log.json` to be present and parseable, with the FX16 entry and the DX-7 keys, before DX-6 is evaluated. junit 3 passed with the log absent or incomplete is `stopped_infrastructure (record_missing)`, no retry, never mismatch. The test's own assertions mean 3 passed already implies equal pairs, the guard and the multiset count |
| R9-9 | **The cell completed (junit written) but a restart hit before `exit.json`** | junit present (here, with a failure), no `exit.json`, restart evidence: **C5, "retry allowed"** | **blocks release**: a completed attempt, possibly a mismatch, is re-run, and the re-run can be recorded as passed ("never re-run for a different answer" is defeated) | Before C5: if `junit.xml` or `kat_ext_log.json` exists in the state directory, the cell reached session end. Classify from junit and the KAT log (C1 or C2 rules) or as `completed_without_exit_record` (no retry, fresh act). Never C5 |
| R9-10 | **The executed command and environment are neither applied nor recorded by the supervisor.** LD-2 binds the argv and a scrubbed environment (plus `KAT_EXT_LOG_PATH`), but LD-4 and LD-5 run the argv under whatever environment the harness shell passes to `setsid nohup bash ...`, and nothing records `/proc/<cell>/cmdline` or `environ`. A word-split argv file (the `-c` wrapper contains spaces) would also run a different command | n/a (design text) | **blocks release**: the executed command or environment can differ from the bound ones without a trace, and a missing `KAT_EXT_LOG_PATH` feeds R9-8 | A NUL-delimited argv file and env file. The supervisor runs `env -i "${ENV[@]}" timeout ... "${ARGV[@]}"` (`mapfile -d ''`) and records in `child.json` the cell's `/proc/<pid>/cmdline` and the sha256 of its `environ`, both compared with the bound files at the first heartbeat (a mismatch is C8, stop) |
| R9-11 | **VmHWM of the wrong process.** The supervisor's direct child is `timeout`, so `/proc/<child>/status` is timeout's memory, not pytest's | n/a | does not block (measurement) | Resolve the grandchild (`/proc/<timeout pid>/task/*/children`), check its cmdline, and record that pid in `child.json` |
| R9-12 | **The trap signals the wrong process group.** `timeout` puts the cell in its own process group; signalling the supervisor's own (setsid) group kills the supervisor before `exit.json`. HUP is ignored under `nohup` and cannot be trapped | n/a | does not block (gives C6 instead of C4) | Signal the `timeout` pid (it forwards the signal), `wait`, then write `exit.json`. Document that HUP is ignored |
| R9-13 | **Two sessions acting on one attempt.** Re-attach "from RESUME.md alone" lets the top-level session and an executor both classify C5 and both relaunch | n/a | does not block passed or mismatch, but concurrent cells break LD-11 and bias the SC-3 rate | An exclusive `O_EXCL` attempt lock (`<state root>/attempt-<n>.lock`, recording the claimant) is created before any launch. Only the lock holder classifies, retries or collects |

Also checked, with no route found:

- **Partial cell:** the test asserts the full multiset count C(B + 2, 3) for the full line base and reads no size variable. The DEV-1 verifier should still confirm the logged `B` is the full base.
- **Substituted cell:** LD-1 re-hashes the copy before and after.
- **Watchdog:** `timeout --kill-after` bounds the cell.

**Counts:** 13 routes. **5 block release of bc7a76 (R9-5, R9-7, R9-8, R9-9, R9-10) and 8 do not (R9-1, R9-2, R9-3, R9-4, R9-6, R9-11, R9-12, R9-13).** RR-9 is advisory and non-blocking for B8-H; it goes to the releasing act (BP-2, BP-3).

## New findings in detail

### NF-H1 (non-blocking). The launcher process honours the parent environment's interpreter variables

**Reproduction (O7c).**

1. In a scratch root (approved specification, lock, stub suite), create `<dir>/fractions.py`. It writes a marker file, then loads the real `fractions` through `importlib.machinery.PathFinder` with `<dir>` removed from the path.
2. Run `PYTHONPATH=<dir> python3 <root>/code/launcher.py cell --cell-id KAT-B1-n2-q13 --plan <root>/plan.json --run-id RUN-o7c`.
3. Result: exit 0, the marker exists, the manifest says `validity: valid`, and `<dir>` and `PYTHONPATH` appear in neither `environment.json` nor the manifest.

**Reproduction (O6c).**

1. Compile a same-size copy of `/usr/lib/python3.11/fractions.py` (one comment line replaced by a marker statement) with the real file's mtime, into `<prefix>/usr/lib/python3.11/fractions.cpython-311.pyc`.
2. Run the same command with `PYTHONPYCACHEPREFIX=<prefix>`. Same result.

**Why it matters.**

- The counting and recording code (`counters`, `fqn`, `curves`, `fractions` for lambda, `json` for every record) runs in this process.
- A shadowed stdlib module can install an import hook and replace a local module after it is hashed.
- The self-test subprocess drops these variables (FX-3, HX-2 d); the cell process does not.

**Fix (launcher.py only).** Before line 139:

- refuse unless `sys.flags.isolated` (run as `python3 -I`), or refuse when any of `PYTHONPATH`, `PYTHONHOME`, `PYTHONPYCACHEPREFIX`, `PYTHONUSERBASE`, `PYTHONSTARTUP`, `LD_PRELOAD` or `LD_LIBRARY_PATH` is set, or when `sys.pycache_prefix` was already non-`None`;
- record `sys.path`, `sys.flags` and every `PYTHON*` and `LD_*` variable in `environment.json` and in the `code_tree` block.

### NF-H2 (non-blocking). Time-of-check gaps inside the cell

**Reproduction (a).**

1. In a scratch root, wrap `counters.build_kernel` (called inside `run_cell` after the gate's last scan) so that, after compiling, it writes `code/multiprocessing.py`. That module writes a marker, `os.remove(__file__)`, then loads and re-exports the real `multiprocessing`.
2. Run a real `KAT-B1-n2-q13` cell with `workers=2` through `gate()` and `run_cell`.
3. Result: the marker exists, `code_tree.post_cell_scan.ok` is true, and `validity: valid`.

**Reproduction (b).**

1. Wrap `counters.build_kernel` to rewrite `code/kernel.c` (the M3 edit plus `int r7_toctou_marker(void){return 7;}`), compile, then restore the bytes and mtime.
2. Result: `ctypes.CDLL(so).r7_toctou_marker() == 7`, `rehash_differences: []`, and `validity: valid`.

**Fix (launcher.py only).**

- Import the local modules by explicit file location, or insert `HERE` only around the local imports and remove it afterwards.
- Pre-import `multiprocessing`, `secrets` and `hmac` before `HERE` is on the path.
- After the cell, check that every `sys.modules` entry whose `__file__` lies in `code/` is an allow-listed `.py`.
- Compile the kernel from a private copy whose sha256 is checked against `file_sha256_at_gate["kernel.c"]` before compiling.
- Re-check `runs/<id>` with `real_dir_problem` after the gate.

### NF-H3 (non-blocking). The self-test junit copy is not checked by the launcher's validity

**Reproduction.** In a scratch root, build a `GateResult` with these fields, and run `run_cell` on `KAT-B1-n2-q13`:

- `_token=launcher._GATE_TOKEN`;
- the real sha256 of the on-disk specification, lock, plan, code and test file;
- `paths` naming those files;
- `code_tree=launcher.code_tree_state(code)`;
- `startup_selftest={mode: "ran", tests: 438, failures: 0, errors: 0, skipped_node_ids: designed, pytest_file: "/usr/x/pytest/__init__.py", ...}`;
- `selftest_files={}`.

Result: `validity: valid`, and there is no `selftest/junit.xml` in the package.

**Fix:** `gate_and_selftest_problems` requires `selftest/junit.xml` in the package, with sha256 equal to `startup_selftest.junit_sha256`, and re-runs `evaluate_suite` on it (and in receipt mode requires `selftest/receipt.json`, sha-equal to `receipt_sha256`).

### NF-H4 (non-blocking). F2 refusal keyed to the output directory

**Reproduction.** In a scratch root:

1. `launcher.write_stop_f2(runs, ...)`;
2. `g = launcher.gate(plan, None)` (no `cell_id`);
3. `launcher.run_cell(arm_A_spec, <root>/elsewhere/RUN-out, kat=False, gate=g)`.

Result: it runs, with `validity: valid`.

**Fix:** `run_cell(kat=False)` requires `realpath(outdir)` to lie inside `gate.paths["runs_dir"]` and checks the sentinel there. Alternatively, `gate()` requires `cell_id` for contract use.

## What this review does not establish

- **Mathematics.** Nothing about any lemma, H-MONO-23d347 or any prediction.
- **DEV-1.** The FX-16 cell was not run by me. B8-D is untouched, and this review's RR-5H is not DEV-1 closure.
- **Contract scale.** Mutant and attack checks ran on KAT fields. Contract-scale behaviour is inferred from identical code paths.
- **Environment integrity beyond `code/`.** Routes through a modified Python installation, `LD_PRELOAD` or a live same-uid process are outside what the launcher can check (see NF-H1, NF-H2).
- **RR-9.** The toy exercise tests the classification rules as written, on stubs. It is not a test of the bc7a76 supervisor script, which does not exist yet.
- **Model independence.** Independence is between sessions, not between models (see the attestation).
