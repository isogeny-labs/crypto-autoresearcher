# EXP-MONO-1a1be2 toolchain (TASK-20261029-a97206; extended by TASK-20261105-ac5ad6)

Proof-of-concept implementation of the instrument for the draft contract
`experiments/EXP-MONO-1a1be2/specification.yaml` (status `review_required`, not approved). Zero experiment
runs exist. No contract cell has been computed; known-answer tests (KATs) use cells disjoint from the
contract. Nothing here asserts a predicted value.

TASK-20261105-ac5ad6 (DEC-20261105-f0b7c7 F-1, F-2) widened the instrument before approval: KATs at n = 4..7 and at
large q, the composition residuals P2(vii) to (ix), the arm-C KAT refusal, and a timing-only throughput harness. Zero
runs; no contract cell computed; the specification is untouched.

## Module map

| File | Content |
| --- | --- |
| `fqn.py` | `FQ`: F_q[t]/(g), g the lexicographically least monic irreducible of degree n (constant term first), n <= 7; add/mul/inv (norm method), `chi`, Tonelli-Shanks `sqrt`, Frobenius. `FQ2`: F_Q[s]/(s^2-d) for the group-law cross-check. Univariate polynomials over either field: gcd, powmod, squarefreeness, distinct-degree factorisation (`ddf`), complete-split tests (`splits_completely_ddf`, independent `splits_completely_xq`), `roots`. |
| `curves.py` | Seed rule (SHA-256, first 16 bytes big-endian, `numpy.random.Generator(PCG64)`), `generate_curve` with the singular and j-in-F_q rejections, generic group law (`WCurve`, works over `FQ` and `FQ2`), `Curve` (factor base D, X, t2, lifts, 2-torsion roots), point counting by three independent routes (definition-level square table, quadratic-character sum, baby-step giant-step on the Hasse interval with the quadratic twist) and `count_points` (exhaustive below 2^27, BSGS above). |
| `semaev.py` | Numeric S_{n+1}(x_1..x_n, T) by the resultant recursion (interpolating the resultant of S_3 and the previous polynomial, formal degrees kept), `analyse_fibre` (degree, squarefreeness, chi(f(x_i)), ddf, complete split), `roots_via_group_law` (x of signed sums of lifts over F_{Q^2}). |
| `kernel.c` | Compiled inner loops: F_Q arithmetic (n <= 7), affine point addition, exhaustive point count with valid-target mask, ordered / multiset / x-multiset (canonical sign patterns) enumerations, S-set marking and collection, the target-sampled arm-C counter (open-addressing hash of target indices), quadratic-character batch, histogram statistics and comparisons. Built at run time; no binary is committed. |
| `counters.py` | ctypes wrapper `Kernel`; matched random and half-size twin bases; `exhaustive_cell` (T_A, T_M, T_S, T_X over all N targets, P2 residuals, independent recount); `arm_c_cell` (target-sampled counter, exact lambda); Poisson statistics (`poisson_summary`); `ncf_coefficient`. Composition residuals (KX-5): `csym_coefficient`, `residual_special_targets` (P2(vii)), `residual_n2_tm_vs_tx` (P2(viii)), `symmetric_coverage_ceiling` (P2(ix)); `exhaustive_cell` carries them as identities `vii_TS_vs_TA_weighted_2j_special`, `viii_n2_TM_eq_TX_off_2torsion` (m = 2 only) and `ix_symmetric_coverage_ceiling`, and `launcher` lists them under `composition_residuals` in a derived summary. In KAT mode all identities are withheld. |
| `launcher.py` | Per-cell runner and gates (see below). `arm_c_pairs()` and `contract_pairs()` give the arm-C and the full set of contract (q, n) pairs a KAT cell must avoid. |
| `throughput_calibration.py` | Timing-only calibration (KX-7), never calls `launcher cell`/`run_cell`: B1 analysis at the proxies (257,2), (43,3), (29,4), (13,5), the arm-A proxy (103,4) with all three bases and recount, the arm-C proxy (q'_2,2); each in a child process, results discarded unread, outputs in a temporary directory deleted unread; writes wall/CPU time, peak RSS, workers, host and MODELED per-class projections. |
| `make_trial_plan.py` | Deterministic trial-plan generator (cells, curves, seeds, `q_rule`, `sample_size_rule`, identity fields). |
| `tests/test_kat.py` | The KAT suite (the start-up self-test). |
| `tests/test_kat_extended.py` | The m = 3 large-q substitute cell (FX-16); not part of the start-up suite. |

Definitions (also in the `counters.py` docstring): T_A ordered point tuples, T_M point multisets, T_S ordered
x-tuples with sign vectors (`sum eps_i L(x_i)`, L the lift with the smaller y code), T_X x-multisets for which
at least one point multiset over them sums to R. Targets are indexed `2 code(x) + [code(y) > code(-y)]`,
`2Q` for O. Generic target: not O, not in E[2], not in S = sums of (m-2l)-multisets of the base, l >= 1.

## Build and test

```sh
# kernel: built into a temporary directory by counters.build_kernel (gcc -O3 -Wall -Wextra -shared -fPIC -std=c11),
# compiler and flags are in environment.json.
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider experiments/EXP-MONO-1a1be2/code/tests/test_kat.py
# raw KAT outputs as text (the file the approval act re-checks):
KAT_LOG_PATH=experiments/EXP-MONO-1a1be2/implementation/kat-log.json  <same command>
python3 experiments/EXP-MONO-1a1be2/code/make_trial_plan.py [--out PATH] [--check]
python3 experiments/EXP-MONO-1a1be2/code/launcher.py environment --out PATH
python3 experiments/EXP-MONO-1a1be2/code/launcher.py --kat kat --arm A --q 13 --n 2 --curve-seed SEED   # KAT cell, temp dir
python3 experiments/EXP-MONO-1a1be2/code/launcher.py selftest                                             # after approval: writes selftest-receipts/<id>/
python3 experiments/EXP-MONO-1a1be2/code/launcher.py cell --cell-id ID --plan PLAN --run-id RUN-ID [--selftest-receipt PATH]  # contract cell, gated
```

## KAT cells (widened by DEC-20261105-f0b7c7)

* q in {5, 13} at n = 2..3 (original) and n = 4..7 (widened); prime fields as before;
* q'_n = least prime above the arm-C q_n, n = 2..7: (32779,2), (1033,3), (193,4), (71,5), (41,6), (29,7);
* every pair is checked disjoint from the arm-A, arm-B and arm-C contract pairs (`test_widened_kat_fields_disjoint_from_every_contract_pair`);
* tests compare optimised code with naive enumeration of the same definition; no cross-convention identity, residual value, ratio, split frequency or predicted value is asserted or recorded. Not runnable in budget: the large-q E2 check at (q'_2, 2, m = 3) (about 6e12 multisets), recorded as DEV-1 in `implementation/kat-report-ac5ad6.md`.

```sh
python3 experiments/EXP-MONO-1a1be2/code/throughput_calibration.py --out PATH     # timing only, not a run
```

Requirements: Python 3.11+, numpy, PyYAML (launcher), pytest, gcc. Without `PYTHONDONTWRITEBYTECODE` and
`-p no:cacheprovider` pytest writes `__pycache__` and `.pytest_cache`, which are not artifacts.

## Launcher gates (IM-8; hardened by TASK-20261106-4c4831)

* `cell` refuses unless `specification.yaml` has `experiment.status: approved`, a non-null `approved_by`,
  `execution_authorized: true` and `frozen: true`, and `experiments/EXP-MONO-1a1be2/approval.lock` exists. The lock is JSON
  with five fields: `approved_by` (must equal the specification's), `specification_sha256`, `code_sha256` (digest over the
  seven `CODE_FILES`, `launcher.code_sha256`, unchanged definition), `trial_plan_sha256` and `test_file_sha256` (sha256
  of `code/tests/test_kat.py`). Every hash must match the files on disk and the plan passed; a lock missing any field
  refuses (exit 3) with no `runs/` entry.
* Start-up self-test (stopping rule 1). `launcher.py selftest` runs `check_approval`, then the suite as
  `python -m pytest -q -p no:cacheprovider --noconftest -c /dev/null --rootdir <code> --junitxml <tmp>/junit.xml tests/test_kat.py`
  in cwd `code/`, with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_ADDOPTS`/`PYTEST_PLUGINS` removed
  and `PYTHONPATH` reduced to entries inside `code/`. "Pass in full" means: exit code 0, junit tests equal
  `EXPECTED_KAT_ITEMS`, failures and errors 0, no xfail or xpass, no deselection, and skipped node ids equal `DESIGNED_SKIPS`
  for the specification status (none before approval; exactly `test_launcher_refuses_contract_cell_while_specification_not_approved`
  after). On a pass it writes `selftest-receipts/<receipt_id>/receipt.json` and `junit.xml`. The receipt holds code, test file, lock and
  junit hashes, counts, skipped node ids, pytest version, the rootdir and inifile pytest reports, start and finish UTC, and an
  `env_key` (Python, numpy, pytest, compiler path, sha256 of `--version`, flags, machine, node, kernel release, CPU model).
* `cell --selftest-receipt PATH` accepts only a `receipt.json` that resolves inside `selftest-receipts/` and whose every
  recomputable field equals a recomputation on this host (including the env key, the junit hash against the `junit.xml` beside it
  and the full-pass rule applied to that junit). Any failed check REFUSES the cell (exit 3); it never falls through to a run.
  Without the flag the cell runs the suite itself.
* `run_cell(kat=False)` raises unless given the `GateResult` that `launcher.gate()` returns. A contract package's `manifest.yaml`
  carries `gate` (specification, lock, plan, code and test-file sha256, `check_approval_passed`) and `startup_selftest` (mode `ran` or
  `receipt`, receipt and junit sha256, counts, skipped node ids, pytest version, rootdir, inifile, env key); copies of `junit.xml`
  (and of `receipt.json` in receipt mode) are in `selftest/`.
* Validity block. A contract `manifest.yaml` carries `validity: {status: valid|void|invalid, reasons, readings_withheld}`, computed
  by the launcher from: the R1 recount (differ: void), `gl_mismatch_generic`/`gl_mismatch_nongeneric` > 0 (void), identity-field
  completeness (q, n, g, a, b, N, t2, B, |X|, seed; missing: invalid), raw/summary agreement (the launcher re-reads what it wrote and
  re-derives the summary and, for arm C, the cdf.json from `raw-result.json`; disagreement: void), and the curve selection rule
  (singular or j in F_q, re-derived from the recorded g, a, b: void). A failed execution is void. `status` keeps the execution status
  (`completed` or `failed`) as a separate field.
* STOP-F2. When an arm-A contract cell fails the CTL-null all-target identity (here: `identities.i_sum_M`, observed sum of the T_M
  histogram over valid targets against C(B+m-1, m), on the `matched_random` or `matched_random_reseeded_aa` base), the launcher
  writes `runs/STOP-F2.json` (cell id, identity name, role, UTC; exclusive create, never overwritten) and marks the cell void;
  `cell` then refuses every arm-A cell (exit 3, "F2 family stop") while it exists. Arm B and arm C are not refused. KAT mode writes
  no sentinel. Removing the sentinel needs a new implementation commit and a Coordinator decision (V2-4).
* Arm-C lambda = (N_cf_counted - m_S)/(N - |S|), N_cf_counted the kernel's counted cancellation-free total. The P2(vi) closed form is
  recorded as `N_cf_formula` with `ncf_counted_equals_formula` per cell and base; when false the validity block adds
  "P2(vi) mismatch; P6 reading withheld (F7 first)" and `readings_withheld: [P6]`. In KAT mode `lambda`, `lambda_exact`,
  `N_cf_formula` and `ncf_counted_equals_formula` are not written.
* `--run-id` must match `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$` and resolve inside `runs/`. `cdf.json` carries `target_seed` and
  `base_seed` (string and integer) per base. Peak RSS is recorded as `peak_rss_kb_self`, `peak_rss_kb_children` and their sum
  `peak_rss_kb_total_upper`. The launcher refuses to start (exit 3, before any import `sys.path` could redirect) when `code/` holds
  a `.py` file outside: the seven `CODE_FILES` sources, `throughput_calibration.py`, `tests/test_kat.py`, `tests/test_kat_extended.py`.
* `kat` requires the explicit global `--kat` flag, refuses every (q, n) that is an arm-A/arm-B or arm-C contract cell (arm-C pairs by the `q_rule`, KX-6),
  writes under a fresh temporary directory (never `runs/`), and withholds derived statistics and cross-convention
  residuals.
* Run directories are never overwritten. `--timeout-seconds` is a watchdog (a cell over it is `failed`,
  `resource_exhaustion`, void) and `--memory-gb` caps address space (default 16, the specification's cap).
* A run package holds `manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
  `raw-result.json`, `summary.json`, `selftest/` and, for arm C, `results/<cell_id>.cdf.json`.

## `tests/test_kat_extended.py` (FX-16, not part of the start-up suite)

The m = 3 large-q substitute cell for DEV-1: F_{q''^2}, q'' = 10,007 (least prime above 10,000, by trial division, disjoint from every
contract pair), curve seed `kat|large|10007|2|m3`, line base, `counters.arm_c_cell` at m = 3 on 50 sampled targets, against a
membership method in Python field arithmetic (sorted int64 pair-sum index table, `searchsorted`; no kernel call). It is not in
`CODE_FILES`, not collected by `test_kat.py`, never run by a cell. Run it by hand
(`KAT_EXT_LOG_PATH=PATH python3 -m pytest -p no:cacheprovider tests/test_kat_extended.py`); budget 14,400 s and 16 GB.

## Implementation choices where the specification is silent

1. Cell ids: `A-n<n>-q<q>-c<i>`, `B1-n<n>-q<q>-c<i>`, `B2-n<n>-c<i>` (two instances, first and second rung),
   `C-n<n>-q<q>-c<i>`. Replicate 0 is the primary draw, 1 the A/A re-draw (every arm-A cell's random base;
   curve index 0 of every B1 cell's tuples).
2. Curve draw: one `rng.integers(0, q, size=2n)` per attempt, first n integers coefficients of a, last n of b,
   constant term first; a rejected attempt redraws.
3. n = 1: every j lies in F_q, so only the singular rejection applies.
4. T_X is defined from IDEA L4 (see definitions above); T_S from IDEA L3.
5. Random base: t2 points from `rng.permutation` of the code-sorted 2-torsion roots, then pairs by rejection
   sampling of x (`rng.integers(0, q, size=n)` per attempt, f(x) a nonzero square, y the smaller-code root).
6. B1: group-law subsample is every 100th tuple; B2: unordered n-subsets of X, all when `C(|X|, n) <= 10^4`,
   otherwise 10^4 random subsets; both checks recorded as tallies of mismatches.
7. Arm C targets: x uniform with chi = +1 and a uniform sign drawn in blocks, distinct classes, classes whose x
   lies in S excluded; both bases of a cell use the same target seed stream (the S exclusion may make the
   target lists differ).
8. Recount (R1) of each exhaustive histogram: same enumeration with the base list reversed and the kernel
   in reference-arithmetic mode (inversion by Fermat z^(Q-2) instead of the norm method), compared target by target.
9. Poisson chi-square pools bins from the right until each expected count is at least 5 (the last bin carries
   the Poisson tail).

## Reuse provenance

No code from `src/crypto_autoresearcher/index_calculus/*` or `experiments/EXP-SMON-e5cbe6/code/semaev_cover.py`
is imported or copied; those pinned inputs were hash-verified and not otherwise read. Everything was written
from the definitions in the specification and the IDEA, and the KATs compare it with naive independent
computations. The S_3 formula is the standard Semaev form for y^2 = x^3 + ax + b and is checked against the
group law (`test_semaev_s3_matches_definition_and_known_answer`, the defining-property tests).

## Randomness

numpy PCG64 per the specification seed rules (curves, bases, tuples, targets); `random.Random(20261029)`
chooses points in the BSGS point counter and Cantor-Zassenhaus split elements in `fqn.roots` (neither affects
its output: N is accepted only as the single surviving candidate, the root set is deterministic).
