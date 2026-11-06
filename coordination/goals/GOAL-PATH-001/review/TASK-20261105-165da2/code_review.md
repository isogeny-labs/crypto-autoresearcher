# Independent code review of the EXP-MONO-1a1be2 instrument (TASK-20261105-165da2)

| field | value |
| --- | --- |
| Task | TASK-20261105-165da2 (BATCH-8517aa, GOAL-PATH-001); blocker B8 of DEC-20261105-f0b7c7; archived by TASK-20261105-49716d |
| Commit reviewed | `72f51766a67be05f6d8de0f4ed962c4c615d52bd` ("archive(TASK-20261105-7083a8): snapshot TASK-20261105-ac5ad6 for EXP-MONO-1a1be2"); the worktree was clean at that commit |
| Card | `ledger/handoffs/TASK-20261105-165da2.yaml`, sha256 `f3a20a014c062cabb328f30dc31bce347f5e11ea7d00806aae288b09e04d6e9b` (verified on disk and at the commit) |
| Role, policy | Validator, `review-adversarial`, fresh session; instrument review, not a claim-changing round, `review_plan: null` |
| Runs launched | 0. No contract cell was computed. The only computation on contract parameters was the two regenerations of the trial plan's identity fields that CR-2 requires (inputs, not outcomes) |
| Scope | Defects that could let an invalid cell pass as valid, or route an instrument defect into a scientific reading. Nothing here concerns the mathematics, H-MONO-23d347, or any prediction value |

## Result

**1 blocking finding, 6 non-blocking findings.** Terminal verdict for the B8 gate is `failed`, because F-1 is blocking. Every other CR check held. The verdict is about the instrument and changes nothing about the experiment's hypotheses.

| id | CR | severity | finding |
| --- | --- | --- | --- |
| F-1 | CR-1 | **blocking** | The start-up known-answer gate (stopping rule 1) is neither bound nor recorded. `tests/test_kat.py`, and the repository-level pytest configuration and `conftest.py` that run inside the self-test, are outside `code_sha256` and outside the lock. Exit code 0 counts as "pass in full". A hand-written or other-host `--selftest-receipt` skips the suite. The run package records none of this. |
| N-1 | CR-3 | non-blocking | Mutant M5 (32-bit target index) survives all 316 KATs. It is active only where Q > 2^31, i.e. arm-C n = 6, 7. The large-q arm-C KAT (W10) compares all-zero vectors at every n >= 4. The committed kernel itself was checked correct on this path by a reviewer differential. |
| N-2 | CR-1, CR-6 | non-blocking | The specification's invalidation and stopping rules (R1 recount VOID, group-law mismatch, F2 family stop) are not applied in the run package. A cell whose recount disagrees is written `status: completed`, and there is no validity field. |
| N-3 | CR-6 | non-blocking | lambda uses the closed form N_cf (the P2(vi) expression). The counted cancellation-free total is recorded beside it and never compared, so a P2(vi) defect would move lambda and could be read under F8. |
| N-4 | CR-4, CR-5 | non-blocking | KAT-mode arm-C packages still write lambda and the P2(vi) closed form next to the counted total. This is IM-3 hygiene only: the files go to a temporary directory, are not retained, and nothing is asserted. |
| N-5 | CR-1, CR-6 | non-blocking | Gate and record hardening: `execution_authorized` and `frozen` are not checked; the lock's `approved_by` is not compared with the specification's; `--run-id` is joined into `runs/` unsanitized; `cdf.json` does not carry the target seed; peak RSS excludes B1 worker processes. |
| N-6 | CR-2 | non-blocking | A B2 cell reuses one tuple seed for both of its rung instances. This path is unreachable in the regenerated plan: no instance has more than 10^4 subsets, so the seed is never consumed. |

What held:

- **CR-1:** every refusal condition refuses, with no `runs/` entry, and `code_sha256` covers every local module and source a cell imports or compiles.
- **CR-2:** the plan regenerates byte-identically (twice) to `9ccbe614...fb4a`. All 298 seed strings follow their rules, no seed is reused across roles, and `tuple_seed_aa` is consumed by the four curve-0 B1 cells.
- **CR-3:** all four n >= 4 mutants (Python and C, reduction and inversion) are killed by widened KATs: 92, 92, 56 and 40 failing items in the full suite, none of them an n <= 3 item.
- **CR-4:** P2(vii), (viii) and (ix) match an independent recomputation from naive enumeration on 33 KAT cell-and-base cases, using each base's own B, t2 and |X|, and KAT mode withholds them.
- **CR-5:** no KAT asserts a prediction or a cross-convention identity; the KAT refusal covers all 96 (pair, arm) combinations; the throughput harness records timings only and never calls `cell` or `run_cell`.
- **CR-6:** the sampler follows the rule and excludes S by class; lambda is an exact `Fraction`; `cdf.json` carries all 22 IDEA keys.

## Review environment and bytes

- **Toolchain:** Python 3.11.17, numpy 2.4.6, PyYAML 6.0.1, pytest 9.2.0, gcc 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1). Host: Linux 6.18, 4 cores, 15 GiB. This is the same toolchain as `implementation/environment*.json`.
- **Bytes:** all execution used fresh `git archive HEAD experiments/EXP-MONO-1a1be2/code experiments/EXP-MONO-1a1be2/specification.yaml` extracts in a scratch directory outside the repository, `/tmp/claude-0/-home-user/d72a143b-1bef-500a-b9ca-d25907246d76/scratchpad/165da2/`, deleted at the end. Every pytest call used `PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider`, with `TMPDIR` pointed into the scratch directory.

Hashes at the reviewed commit (for the approval act's `approval_lock_binding`):

| file | sha256 |
| --- | --- |
| code/fqn.py | `c5c967f1ba6d0c7cfd34c08ee3ff67f7551d0b3163e695c464b8e93b49f80f09` |
| code/curves.py | `9e52804cbac32ce5d9fae7e9627dd97a9ad200917b3ffaaa9aa7b5b975b5fc7f` |
| code/semaev.py | `936af457d9fb52a4ff9286fed361861f0e2ad99bb901eee999e26a01bf9ba9c1` |
| code/counters.py | `5e6d6f24854d520fa3bf28ffbd5af89bf11778262ba97c156478ecfab1977727` |
| code/kernel.c | `e0152279833973b1f7bdcba70ae28e5d7d9d456caab985ee206604a91c4aa021` |
| code/launcher.py | `d2833c702412e17b6288dc68fcbf53aa77960c92222e09f04f568963cf52b40f` |
| code/make_trial_plan.py | `b7010bd2bdd5df9f28dcedffb53a628e61425fb3d83aae1806895a313ac7eef9` |
| `launcher.code_sha256()` over the seven | `e12fe0f3f07dc79bc093d70174cf05dff7ab3fc90f04711f903a56565cb4fd38` |
| code/tests/test_kat.py | `4305f722e8c6839584177b23817bfe4e20a917677cd5fad58344c3f183169e07` |
| code/throughput_calibration.py (not executed by a cell) | `22a84f636387f40cb6d6933b5c0cc738d9ba0d0c59220c1dce3bf444271f0733` |
| specification.yaml (v1, equals the DEC's `d81a85b3...c373`) | `d81a85b36961647d6d6caccdf988d5650a7376fa581173f9761ab3ed594bc373` |

**Baseline control.** On the unmodified committed bytes:

`python3 -m pytest -q -p no:cacheprovider -rs tests/test_kat.py`

gave **316 passed in 1159.52 s, exit 0**. This is the count reported in `kat-report-ac5ad6.md`, and it is the reference for every mutant run.

## CR-1 Launcher gate

**What was tried.** I used a scratch extract with its own `specification.yaml`. Each scenario called the real CLI in a subprocess:

`python3 code/launcher.py cell --cell-id NO-SUCH-CELL --plan <synthetic plan> --run-id RUN-gate-<k>`

The cell id is not in the plan, so even a passing gate cannot execute a cell. After every scenario I checked that `<exp>/runs` was absent.

- **Approved-spec variant:** the v1 text with `status: approved` and `approved_by: coordinator`.
- **Correct lock:** JSON with the four fields hashed as `check_approval` expects.
- **Edits:** each scenario changed exactly one thing.

| scenario | exit | `runs/` created | reason printed |
| --- | --- | --- | --- |
| S1 missing lock | 3 | no | approval lock missing |
| S2 empty lock file (0 bytes) | 3 | no | unreadable; empty or not a JSON object; no approved_by |
| S3 lock `{}` | 3 | no | empty or not a JSON object; no approved_by; spec hash differs ... |
| S4 non-object lock: `[]`, `null`, `"x"`, `7`, `[{"approved_by":"c"}]` | 3 each | no | empty or not a JSON object; ... |
| S5 lock `approved_by: null`, hashes correct | 3 | no | lock has no approved_by |
| S6 wrong specification hash | 3 | no | specification_sha256 differs |
| S7 wrong code hash | 3 | no | code_sha256 differs (invalid build) |
| S8 wrong plan hash | 3 | no | trial_plan_sha256 differs from the plan passed |
| S9 spec status `review_required` (lock hashed to that spec) | 3 | no | status is 'review_required'; approved_by is null |
| S9b spec status `running`, approved_by set | 3 | no | status is 'running', not 'approved' |
| S10 spec approved, `approved_by: null` | 3 | no | specification approved_by is null |
| S11 `--plan` omitted | 2 (argparse) | no | usage error, `--plan` required |
| S13 `curves.py` edited after the lock was written | 3 | no | code_sha256 differs |
| S12 positive control: correct lock plus a hand-written receipt | 3 | no | passes the gate and the self-test (by receipt); refused only at "cell NO-SUCH-CELL not in the plan" |
| S14 `tests/test_kat.py` replaced after the lock (library `check_approval`) | n/a | no | `check_approval -> (True, [])` |
| S15 approved spec still carrying `execution_authorized: false`, `frozen: false` | n/a | no | `check_approval -> True` |

**Coverage of `code_sha256`.**

- **Python modules:** after `import launcher`, the modules loaded from `code/` are exactly `counters`, `curves`, `fqn`, `launcher`, `make_trial_plan` and `semaev`, all in `CODE_FILES`.
- **Kernel source:** `kernel.c` is compiled at run time from `code/` and is in `CODE_FILES`.
- **No import outside `CODE_FILES`:** no module the launcher imports lies outside it.
- **Executed but unbound:** a contract cell does execute local files that `code_sha256` does not cover, namely the start-up self-test's `tests/test_kat.py` and the repository-level pytest configuration and conftest chain (F-1).

**Outcome.** The lock gate itself is sound for every condition the card lists. The start-up self-test that follows it is not bound: F-1, blocking. Smaller gate hardening items are in N-5.

## CR-2 Seeds and plan

**What was tried.**

1. **Regeneration:**
   `python3 code/make_trial_plan.py --out <scratch>/plan{1,2}.json`
   I ran this twice, concurrently, from the committed bytes. Each run took 444 s.
2. **Seed audit:** a script over the regenerated plan. It recomputes every `seed_int` from SHA-256, checks every seed string against the specification's rule for its arm, role and replicate, and looks for any string reused across roles.
3. **A/A consumption:** each of the 12 real B1 plan cells went through `launcher.spec_from_plan_cell` and then `launcher.run_arm_b`. Two stubs kept this free of contract computation:
   - `build_instance` returned a KAT curve (13, 2), so no contract curve was built;
   - `_analyse_all` returned a zero tally, so no fibre was analysed.

**Outcome.**

- **Determinism.** Both regenerations are byte-identical to each other and to the committed `trial-plan.preview.json` and `trial-plan.preview-ac5ad6.json`: sha256 `9ccbe61445fba836ec44bdea6e55255220a4d08e8d09c9198e5bd28696d8fb4a` (135,868 bytes).
- **Cell counts.** The plan has A 54, B1 12, B2 12, C 18, for a total of 96. The generated arm-C q_n agrees with the specification's list for n = 2..7.
- **Seed rules.** No violation among the 298 distinct seed strings:
  - curve seeds are `f15270|A|n|q|i` for arm A and arm B, and `f15270|C|n|q|i` for arm C;
  - base seeds are `f15270|base|<cell_id>|random|0`, `|twin|0`, and `|random|1` for C-aa-baseseed, the last on every arm-A cell;
  - tuple seeds are `f15270|tuples|<cell_id>|0`, plus `|1` for C-aa-tupleseed on exactly `B1-n2-q251-c0`, `B1-n3-q41-c0`, `B1-n4-q23-c0` and `B1-n5-q11-c0`;
  - target seeds are `f15270|targets|<cell_id>`.
- **Seed reuse.** No seed string is used in two roles. The only shared strings are the 24 arm-A curve seeds that arm B reuses, as the specification requires.
- **`tuple_seed_aa` is consumed.** The four curve-0 B1 cells ran samples `['primary', 'aa']` with seeds `0` and `1`. The other eight ran `['primary']` only.
- **B2 random path.** No B2 instance has C(|X|, n) above 10^4: the largest is 8,515, and several are 0 or 1. The random-subset path, and with it the B2 tuple seed, is therefore never used by this plan (N-6).

## CR-3 KAT strength (mutants)

**What was tried.** I built five scratch mutants. Each is a fresh `git archive` extract with one guarded edit, applied by a script that asserted the edit's source text occurred exactly once. Every mutant kernel compiled with no warning under the producer's flags (`-O3 -Wall -Wextra -shared -fPIC -std=c11`), so no kill below comes from a build failure.

| mutant | file | edit (active only where stated) |
| --- | --- | --- |
| M1 | fqn.py `FQ.mul` | for n >= 4, skip reducing the top term t^(2n-2) (`if n >= 4 and k == 2*n-2: continue`) |
| M2 | fqn.py `FQ.inv` | for n >= 4, inversion loop `range(1, n-1)`: last Frobenius conjugate missing |
| M3 | kernel.c `e_mul` | for n >= 4, reduction loop starts at k = 2n-3 (top term dropped) |
| M4 | kernel.c `e_inv` | for n >= 4, norm-method loop stops one conjugate early (`i < n_-1`) |
| M5 | kernel.c `p_idx` | 64-bit to 32-bit truncation of the target index: `return (uint32_t)(2*code(x) + bit)` and `(uint32_t)(2*Q_)` for O. This affects only indices >= 2^32, i.e. Q > 2^31. The contract has such Q only in arm-C n = 6 (Q = 37^6, about 2.57e9) and n = 7 (Q = 23^7, about 3.40e9). |

Commands:

- **First failing widened KAT:** `pytest -x -q -p no:cacheprovider tests/test_kat.py -k "wide or large_q"`.
- **Full suite, every mutant:** `pytest -q -p no:cacheprovider --tb=no -rf tests/test_kat.py`.

**Outcome.**

| mutant | first widened KAT to fail | full suite |
| --- | --- | --- |
| M1 | `test_wide_field_axioms_and_kernel_ops[5-4]` (AssertionError in the field axioms) | **92 failed**, 224 passed (1330.6 s) |
| M2 | `test_wide_field_axioms_and_kernel_ops[5-4]` (AssertionError; `FQ.inv` also asserts the norm is scalar) | **92 failed**, 224 passed (1326.2 s) |
| M3 | `test_wide_field_axioms_and_kernel_ops[5-4]` (`kernel.mul` differs from Python: `(3, 1, 0, 1) != (2, 2, 4, 1)`) | **56 failed**, 260 passed (987.2 s) |
| M4 | `test_wide_field_axioms_and_kernel_ops[5-4]` (`kernel.inv` differs from Python) | **40 failed**, 276 passed (1145.8 s) |
| M5 | none | **316 passed in 1155.38 s, exit 0: survives** (N-1) |

Failing items in the full-suite runs, by test function:

| KAT (id) | M1 | M2 | M3 | M4 |
| --- | --- | --- | --- | --- |
| E1 `test_exhaustive_counters_match_naive_enumeration`: all n = 4, 5 items (3 bases x 8 cells) | 24 | 24 | 24 | 24 |
| E2 `test_sampled_counter_matches_naive_enumeration` at (5,6,6), (5,7,7), 2 bases | 4 | 4 | 4 | 4 |
| W2 `test_wide_field_axioms_and_kernel_ops` | 8 | 8 | 8 | 8 |
| W4 `test_large_q_kernel_ops_match_python`, n = 4..7 | 4 | 4 | 4 | 4 |
| W5 `test_wide_group_law_and_point_count_three_ways` | 8 | 8 | 8 | 0 |
| W10 `test_large_q_sampled_counter_against_membership_method`, n = 4..7 | 8 | 8 | 8 | 0 |
| W3 (4), W5a (wide 8, large 4), W6 (6), W7 (3), S1+ n >= 4 (3), W8 (4), W9 (4): Python paths | 36 | 36 | 0 | 0 |

- **Only widened KATs kill.** No n <= 3 item failed for any of M1 to M4, because each edit is guarded by n >= 4. Every kill therefore comes from the KATs that TASK-20261105-ac5ad6 added.
- **M4 shows why the small-q enumeration KATs matter.** The kernel inversion is used by point addition inside the enumerations, but not by the point count or the character batch. W5 and W10 therefore pass under M4; E1 at n = 4, 5 and E2 at n = 6, 7 carry the kill, together with the field-level W2 and W4.
- **W10 kills M3 only through its chi check.** The sampler computes chi with the kernel's arithmetic, so the chi check on sampled keys fails. W10's count vectors are zero at n >= 4 and play no part in the kill (see below).

**Why M5 survives.** W10 (`test_large_q_sampled_counter_against_membership_method`) is the only KAT that exercises the arm-C counter at large Q. It draws s = 50 random targets. At n >= 4 the expected count per target is far below 1/50, so the count vectors from the kernel and from the membership method are both all zeros. W10's chi and arithmetic checks still work (they killed M1 to M3), but its count comparison cannot see an index or lookup defect. The producer's own `kat-log-ac5ad6.json` (W10 entries, read by key) shows this:

| W10 cell | targets with nonzero count |
| --- | --- |
| (32779, 2, m = 2) | 22 of 50 |
| (1033, 3, m = 2) | 0 of 50 |
| (1033, 3, m = 3) | 8 of 50 |
| (193, 4, m = 2), (193, 4, m = 3) | 0 of 50 |
| (71, 5, m = 2), (71, 5, m = 3) | 0 of 50 |
| (41, 6, m = 2), (41, 6, m = 3) | 0 of 50 |
| (29, 7, m = 2), (29, 7, m = 3) | 0 of 50 |

Nine of the eleven W10 cells compare zero vectors. No other KAT computes a target index at Q > 2^31: `kpoint_index` against `target_index` is checked only on small fields.

**M5 is a real (non-equivalent) mutant, and the committed kernel is correct on the path.** I ran a reviewer differential on the widened KAT fields (41, 6) (Q = 4,750,104,241) and (29, 7) (Q = 17,249,876,309), on the KAT curves `kat|large|q|n`:

- **Target index, 300 random points per field:** the committed kernel equals Python `target_index` on all of them. M5 differs on 164 of 300 and 251 of 300, exactly the points whose index is >= 2^32, and on O.
- **Sampled counter, m = 2:** the 50 targets are sums of two base points, so the true counts are nonzero. The committed kernel equals a naive enumeration on all 50 at both fields. At (29, 7), where 32 of the 50 keys are >= 2^32, M5 returns only 18 nonzero counts where the truth has 50.

## CR-4 Residuals P2(vii), (viii), (ix)

**What was tried.** I read `counters.exhaustive_cell`, `residual_special_targets`, `residual_n2_tm_vs_tx`, `symmetric_coverage_ceiling` and `csym_coefficient` against DEC-20261105-f0b7c7 `predictions_to_freeze`. I read the kernel's `kcount_points` mask, `kcmp` and `khist_stats` for the target sets.

I then recomputed all three residuals independently on KAT cells and compared them with `exhaustive_cell`'s identities. The comparison printed equality only, never a residual value. The independent side:

- **Naive arrays.** T_S came from ordered x-tuples times sign vectors over the lifts, T_A weighted by 2^j from ordered point tuples, T_M from multisets, and T_X from x-multisets with distinct sums.
- **Target sets.** Valid targets came from all points by the definition. The special set was O plus (r, 0) for every root of f in F_Q.
- **C_sym.** A truncated-series evaluation built from repeated (1+z) products and prefix sums, with no binomials, using B, t2 and |X| counted from the base itself.

The cases:

- (q, n, m) = (13,2,2), (5,4,2), (5,4,3), (13,4,2) and (5,5,2), each with the line, random and twin bases. Every one of these has t2 = 0.
- The prime-field KAT curves q = 11, 23, 101 at m = 2, 3, with three bases each, where t2 = 3 in the base. These exercise the 2-torsion weighting and the E[2] targets inside the base.

**Outcome: 33 of 33 cases match on all three residuals.**

- **(vii)** compares exactly the valid targets with mask value 3, i.e. O and E(F_Q)[2]. These are the targets (iii) skips (`kcmp(..., skip=2)`), so (iii) and (vii) together cover every valid target. T_S is the code convention: sign vectors summing to R over the lifts, with the 2-torsion lift appearing twice in D'.
- **(viii)** is computed only at m = 2 (m = n throughout the plan). It ranges over the valid targets with 2R != O (mask value 1, S included), comparing T_M (from `K_MS` over the base) with T_X (from `K_XM` over the lifts).
- **(ix)** observes the count of valid targets (all N, O included) with T_M >= 1. It computes C_sym = [z^m](1+z)^(|X|-1)(1-z)^(-(B-t2)/2-1) from the base's own `len(D)`, its own count of y = 0 points, and `len(X_lifts)`. `run_arm_a` passes `x_lifts(F, pts)` for each base: line, matched_random, half_twin and matched_random_reseeded_aa. The record carries observed, C_sym, N, `min(N, C_sym)` and the margin, as the DEC specifies.
- **KAT mode withholds them.** `run_arm_a` pops `identities` when `kat` is true, and `_cell_summary_arm_a(derived=False)` adds no `composition_residuals`. The tests `test_launcher_kat_cell_writes_package_in_temp_dir_only[A-13-2]` and `test_launcher_summary_names_residuals_when_derived_and_withholds_them_in_kat_mode` cover this, and both pass in the baseline run.
- **t2 in the contract.** The plan's identity fields have t2 = 0 in every n >= 2 contract cell. t2 > 0 occurs only at the n = 1 anchors.

## CR-5 Discipline

**What was tried.** I read all 316 test items (1,571 lines) for assertions against predictions or cross-convention identities. I drove the KAT CLI over every contract pair. I read `throughput_calibration.py` and listed every key in the committed `throughput-calibration.json`.

**Outcome.**

- **No KAT asserts a predicted value or a cross-convention identity.**
  - Every counter KAT compares the kernel with a naive enumeration of the same convention: E1, E2 and W10.
  - The recount asserts agreement between two code paths of the same convention.
  - X0 and X1 test the residual functions on fabricated arrays only. X2 asserts that the fields are present, and that `C_sym` equals `csym_coefficient` (the function equals itself).
  - `r["multisets"] == C(B+m-1, m)` (E2 line 763, W10 line 1453) is an enumeration-completeness check on the leaf count. It is not the P1/P2(i) per-target mass identity, which no KAT asserts.
- **The KAT refusal covers every contract pair.** `launcher.main(["--kat", "kat", "--arm", A|B1|B2|C, "--q", q, "--n", n, ...])` refused (exit 3, "REFUSED") for all 24 contract pairs (18 arm-A/B, 6 arm-C) and all four arms: 96 of 96, with no `runs/` created. The suite itself covers the six arm-C pairs and one arm-A pair.
- **`throughput_calibration.py` never calls `launcher.py cell` or `run_cell`.** It calls `launcher._analyse_all`, `counters.exhaustive_cell` and `counters.arm_c_cell` in child processes, on the proxies (257,2), (43,3), (29,4), (13,5), (103,4) and (32779,2), none of which is a contract pair. It discards each result (`del box["r"]`).
- **The committed JSON holds no count, statistic or residual.** Its keys are timings (`wall_s`, `cpu_*`, `peak_rss_*`), host data, modeled projections, TP-1 flags, and input identity fields (B, t2, `size_X`, Q, `multisets` = C(B+n-1, n)).

## CR-6 Arm C

**What was tried.** I read `counters.sample_targets`, `s_set_indices`, `arm_c_cell`, kernel `krun_sampled` and `leaf_ms` (`case 6`), and `launcher.run_arm_c`, `arm_c_entry` and `arm_c_flat`. I then assembled an arm-C package with `launcher.run_cell(kat=False)` on a KAT curve (13, 2). `counters.arm_c_cell` was stubbed with fabricated counts, so no count was computed; the point was to check the `cdf.json` keys against the IDEA's `validation_arm.machine_readable_output`, which I read by key at the commit.

**Outcome.**

- **The sampler follows the rule.**
  - x is uniform in F_Q, drawn coefficient-wise as `rng.integers(0, q, size=(block, n))`.
  - Only x with chi(f(x)) = +1 is kept, so O and E[2] are excluded.
  - The sign is uniform, and there is one representative per ± class: x is deduplicated.
  - Classes whose x lies in S are excluded. S is all sums of (m - 2l)-multisets of the base for l >= 1, including the empty sum (O) at even m; it is symmetric, so excluding by x excludes by class.
  - Draws continue until s classes are held.
  - Both bases of a cell reuse the target stream, and each excludes its own S.
- **lambda is exact.** It is `Fraction(N_cf - m_S, N - |S|)`, where N_cf is a Python integer, m_S is the kernel's count of cancellation-free multisets summing into S (slots `>= nsampled`, `viol == 0`), N is the BSGS or kernel integer, and |S| is `S_idx.size`. It is recorded as `lambda_exact = [num, den]` beside the float. N_cf is the closed form (N-3).
- **`cdf.json` keys.** All 22 IDEA keys are present at the top level for the line base: `cell_id n q curve_id seed B t2 N lambda s hist cdf_empirical cdf_poisson ks_stat chi2_stat chi2_df zero_fraction coverage dispersion_index max_count p_max_pred exceptional_targets`. The extras are `N_cf_formula S_size cancellation_free_multisets draws lambda_exact m_S multisets wall_seconds`, plus a nested `matched_random` block. `seed` is the curve seed; the target seed is only in `manifest.yaml` (N-5).

## CR-7 Compliance

- **Experiment cells:** zero. No `launcher.py cell` reached a cell: every gate call used `NO-SUCH-CELL`.
- **What did run:**
  - the KAT suite (baseline and five mutants), in scratch extracts;
  - unit-level checks on KAT fields only;
  - two regenerations of the plan's identity fields.
- **Contract curves in the A/A check:** these were stubbed; no contract curve was built there and no fibre was analysed.
- **Scratch:** every scratch file lived under the session scratchpad, outside the repository, and was deleted at the end.
- **Writes:** only this file and `review_attestation.yaml`, under the task's `write_scope`. Nothing was committed.
- **Prediction values:** no finding states one.
- **Model provider:** not Bedrock.

## Findings in detail

### F-1 (blocking). The start-up known-answer gate is neither bound nor recorded

**Requirement.** The specification's stopping rule 1 reads: "Stop before any cell if the launcher's start-up known-answer suite does not pass in full; that is infrastructure." DEC-20261105-f0b7c7 `f1_decision` adds that the KATs are the only guard against arithmetic defects on the executing host. The R1 recount cannot be that guard, because it reuses the same kernel arithmetic and differs only in base order and inversion method.

**What the code does.** `cmd_cell` calls `check_approval`, then `run_startup_selftest(args.selftest_receipt)`. This runs `python -m pytest -q -p no:cacheprovider <code>/tests/test_kat.py` with cwd set to `code/` and treats exit code 0 as a pass. Otherwise it accepts any receipt JSON whose `code_sha256` and `test_file_sha256` match and whose `result` is `"passed"`. Five gaps follow, and each one alone lets a contract cell start without the full suite having passed on the executing host:

- **(a) `tests/test_kat.py` is in neither `CODE_FILES` nor the lock.**
  - Repro S14: replace the file with `def test_placeholder(): pass`. `check_approval` returns `(True, [])` and `run_startup_selftest(None)` returns `(True, "... 1 passed")`.
  - DEC `approval_lock_binding` records this file's sha256 in the approval decision, but the launcher never checks it.
- **(b) Repository-level pytest configuration and conftests run inside the self-test, unbound.**
  - The self-test does not fix its rootdir. In the repository, pytest's rootdir is the repository root (`pyproject.toml` has `[tool.pytest.ini_options]`), so the root `conftest.py` is loaded.
  - That conftest imports `orchestration.adapter.config` and rewrites the collected items through `tools.ci_test_supersession.apply_supersession`, driven by `tests/fixtures/p192_role1_replay_correction/supersession.json`. That hook does not touch test_kat.py at this commit, but it is executable code outside every binding.
  - Repro: a scratch tree with `<root>/pyproject.toml` (`[tool.pytest.ini_options]`) and `<root>/conftest.py` containing `def pytest_collection_modifyitems(items): del items[1:]`, with the code at `<root>/experiments/EXP-MONO-1a1be2/code`. There `launcher.run_startup_selftest(None)` returns `(True, "1 passed in 0.37s")`, and `--collect-only` lists 1 node id.
  - With `--noconftest -c /dev/null --rootdir <code>` added, the same tree collects all 316.
- **(c) "Pass in full" is not checked.** Exit code 0 is accepted whatever the skipped or deselected count. The suite already skips `test_launcher_refuses_contract_cell_while_specification_not_approved` (test_kat.py lines 922-925) once the specification is approved, so every post-approval self-test passes with at least one skip, and nothing separates that skip from others.
- **(d) The receipt is unauthenticated and not bound to the environment.**
  - Repro S12: write `{"code_sha256": launcher.code_sha256(), "test_file_sha256": launcher.sha256_file(launcher.TEST_FILE), "result": "passed"}` to any path and pass `--selftest-receipt <path>`. The gate and the self-test pass with no test run. The CLI then refused only because `NO-SUCH-CELL` is not in the plan; a real cell id would have executed.
  - The key has no compiler, flags, Python, numpy or host. A receipt written on one host stands in on another.
  - Practical weight: the suite takes about 19 minutes (1159.5 s here, 1188.7 s for the producer) and the contract has about 100 cells, so receipts will be used in practice.
- **(e) The run package records none of this.**
  - `run_cell`'s manifest (launcher.py lines 524-536) has no field for the self-test mode (ran or receipt), the receipt bytes or hash, the test-file hash, the pass, skip and deselect counts, or the pytest rootdir and inifile.
  - It also has no gate evidence (specification, lock and plan sha256). `run_cell` is itself ungated, so a library call produces a package indistinguishable from a gated cell.
  - `command.txt` shows a `--selftest-receipt` path when one was given, but not whether the receipt was accepted (a mismatched one falls through to a full run) or what it contained.

**Why this is blocking.** A cell that started without the full suite passing on its host violates stopping rule 1, so it is not a valid contract cell. Yet its package carries a matching `code_sha256` and `status: completed`, and is indistinguishable from a gated cell: it would pass as valid. If such a host had an arithmetic difference, it would surface first as a P2 identity failure, which the contract reads under F7. DEC-20261105-f0b7c7 `f1_decision` names that as the program's most expensive misreading, and it is exactly what the start-up suite exists to prevent.

**Suggested minimal resolution.** This is for the Coordinator to scope; the repair belongs to a new implementation task, not to this review.

1. Add `test_file_sha256` to `approval.lock` and check it in `check_approval`. This would also amend `approval_lock_binding`'s lock content.
2. Run the suite isolated from repository configuration:
   `python -m pytest -q -p no:cacheprovider --noconftest -c /dev/null --rootdir <code> <code>/tests/test_kat.py`
   Under the hostile rootdir conftest above, this collected 316.
3. Require "in full" explicitly. For example, read `--junitxml` and require the expected pass count, exactly the one designed skip, and zero deselected.
4. Either drop `--selftest-receipt` for contract cells, or key it also on the environment record (compiler path, version and flags; Python; numpy; host) and copy the receipt bytes into the run package.
5. Add a `startup_selftest` block (mode, test_file_sha256, receipt sha256, counts, pytest version, rootdir and inifile) and the gate hashes (specification, lock, plan) to `manifest.yaml`.

Each item is a small change; together they change `code_sha256`.

### N-1 (non-blocking). Surviving mutant M5: no non-vacuous KAT on the large-Q arm-C index path

**Reproduction.** Apply the M5 edit to `kernel.c` `p_idx`, two lines, as shown in the CR-3 table. Then run:

`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_kat.py`

It gives 316 passed. The reason is the W10 zero vectors shown above.

**Effect, if such a defect were present.**

- In arm-C cells at n = 6, 7, sums with code(x) >= 2^31 would be filed under aliased indices.
- Sampled targets in the upper range would lose their counts, and targets in the lower range could gain aliased ones.
- The S-set exclusion would also go wrong.
- The resulting change in coverage and dispersion would be read under F8.

**Why non-blocking.** The approved bytes do not have this defect. The reviewer differential above shows the committed kernel computing the index and the sampled counts correctly at Q = 4.75e9 and 1.72e10, including 32 keys >= 2^32. The arithmetic is plain C11 `uint64_t` with no data-dependent width. So the gap is in the start-up regression guard, not in the instrument. It becomes material if the kernel changes again before approval, which F-1 would already cause.

**Suggested KAT.** At (41, 6) and (29, 7), with the KAT curves `kat|large|q|n`:

- check `kernel.point_index` against `counters.target_index` on points whose index is >= 2^32;
- run `run_sampled` with targets drawn from sums of base points, including keys >= 2^32, against the membership method.

The second check is what killed M5 here.

### N-2 (non-blocking). Invalidation and stopping rules are not applied in the run package

`exhaustive_cell` records `recount[*].differ` (R1), and `_analyse_block` counts `gl_mismatch_generic` and `gl_mismatch_nongeneric`. Neither changes `manifest.status`, which stays `completed`. No `validity` field is written, although AGENTS.md "Artifact policy" requires validity status and reason. The F2 family stop is not implemented: the launcher runs single cells.

All the data needed is in `raw-result.json` and `summary.json`, and the specification places invalidation at analysis. So this is not an instrument defect. Carry it to B5: the runbook and the analysis must mark VOID or invalid from these fields, and implement the F2 stop, before any reading. A launcher-side `validity` block would remove the dependency.

### N-3 (non-blocking). lambda uses the P2(vi) closed form for N_cf

`arm_c_cell` sets `lam = Fraction(ncf_coefficient(B, t2, m) - m_S, N - |S|)`, while the kernel's counted `cancellation_free` is recorded (`cancellation_free_multisets`) and never compared. If P2(vi) failed, lambda would be wrong in every arm-C cell, and a P6 deviation could be read as F8 rather than traced to F7. The risk is low: P2(vi) is decided on every arm-A cell, and both numbers are in the package.

Suggested: require equality per arm-C cell and base, either in the launcher or in the analysis, before any P6 reading, or use the counted value.

### N-4 (non-blocking). KAT-mode arm-C packages write lambda and the P2(vi) closed form

`arm_c_entry` always writes `lambda`, `lambda_exact` and `N_cf_formula`, the last next to `cancellation_free_multisets`. Only the Poisson block is gated by `derived`. In KAT mode this records a derived statistic, and a predicted closed form beside its counted value, contrary to the letter of IM-3 ("no derived statistic recorded"). The impact is nil: KAT packages are written to a temporary directory and not retained, no test asserts them, and `kat-log-ac5ad6.json` records only counts.

Suggested: gate these three keys on `derived`.

### N-5 (non-blocking). Gate and record hardening

1. **Specification flags.** `check_approval` ignores `execution_authorized` and `frozen` (S15), and does not compare the lock's `approved_by` with the specification's.
2. **Run id.** `outdir = os.path.join(RUNS_DIR, args.run_id)` is not sanitized: `../x` or an absolute path writes outside `runs/`.
3. **Target seed.** `cdf.json` `seed` is the curve seed. The target seed and base seed that define the sample are only in `manifest.yaml`.
4. **Peak RSS.** `peak_rss_kb_measured` uses `RUSAGE_SELF` only, so B1 cells with `--workers > 1` under-report. This is a secondary metric.
5. **Shadowing (hardening only, no current instance).** `sys.path.insert(0, HERE)` would let a stray `numpy.py` or `yaml.py` in `code/` shadow the library while being hashed by nothing. A refusal when `code/` holds an unexpected `.py` file would close this.

### N-6 (non-blocking). B2 reuses its tuple seed across the two rung instances

`run_arm_b` recreates `make_rng(tuple_seed)` for each instance of a B2 cell, so both rungs draw from the same stream. In the regenerated plan the random-subset path is never reached: max C(|X|, n) is 8,515, below 10^4. The seed is therefore never consumed, and nothing in this plan depends on it.

Suggested: derive per-instance seeds (for example, add a rung field) if the plan ever changes.

## What this review does not establish

- **Mathematical correctness.** It checks the instrument against its definitions, against naive enumerations and against the KAT suite. It does not re-derive any lemma, and it does not judge whether the definitions are the right ones.
- **Contract scale.** All mutant and residual checks ran on KAT fields. Behaviour at contract fields is inferred from identical code paths, plus the regenerated identity fields.
- **The real repository layout.** The self-test was not executed there, because this checkout is sparse. The rootdir and conftest behaviour in F-1 (b) was reproduced on a scratch tree with the same pytest mechanism (pytest 9.2.0).
- **Pre-approval scope.** The runbook, the analysis code, the approval lock and protocol.json do not exist yet (B4 to B6). N-2 and N-3 are carried to them.
- **Model independence.** Independence is between sessions, not between models (see `review_attestation.yaml`).
