# KAT report, TASK-20261105-ac5ad6 (EXP-MONO-1a1be2, pre-approval, zero runs)

Authority: DEC-20261105-f0b7c7 F-1 (IM-3 widened) and F-2 (TP-0), card `ledger/handoffs/TASK-20261105-ac5ad6.yaml`
KX-1 to KX-11. Input pins verified against `input_pins_TASK-20261105-ac5ad6` in the c0d167 ledger receipt before
starting: all 13 listed files matched. Instrument only; no claim; the specification and every ledger record are untouched.
No contract cell was computed. No KAT asserts a cross-convention identity, a residual value, a ratio, a split frequency or a
predicted value. No residual value at any real KAT cell was printed or recorded (the log holds field names only).

## Result

* Command: `PYTHONDONTWRITEBYTECODE=1 KAT_LOG_PATH=<scratch>/kat-log-ac5ad6.json python3 -m pytest -q -p no:cacheprovider experiments/EXP-MONO-1a1be2/code/tests/test_kat.py --durations=8`
* **316 passed, 0 failed** (1188.65 s). Baseline before this task at the pinned bytes: 177 passed. New: 139 test items. The three
  PR-2707 regression tests (empty lock, B2 instance with few x-coordinates / empty tuple list, B1 A/A tuple seed; by DEC-20261105-f0b7c7 lines 34-39) are in the suite and pass (identified by their subject as `test_launcher_approval_gate_refuses_empty_or_non_object_lock`,
  `test_launcher_empty_tuple_list_yields_complete_zero_tally`, `test_launcher_b1_runs_the_aa_tuple_sample`, unchanged).
* Raw outputs of all KATs as text: `kat-log-ac5ad6.json` (244 entries; new ids W0 to W10 and X1).
* Scope findings (KX-9): **none**. No widened KAT exposed a defect; `fqn.py`, `curves.py`, `semaev.py`, `kernel.c` and
  `make_trial_plan.py` are byte-unchanged. Modified code files: `counters.py`, `launcher.py` (as the card requires), the test file,
  the README, and the new `throughput_calibration.py`. `launcher.CODE_FILES` digest therefore differs from the pinned bytes (expected; the
  approval lock does not exist yet).
* Plan determinism (KX-8): `make_trial_plan.py --out implementation/trial-plan.preview-ac5ad6.json` regenerated the plan; compared
  byte for byte with `trial-plan.preview.json`: **IDENTICAL** (both sha256 `9ccbe61445fba836ec44bdea6e55255220a4d08e8d09c9198e5bd28696d8fb4a`).

## Deviations and implementation choices (nothing absorbed silently)

* **DEV-1 (not runnable in budget).** KX-4 asks for the E2 sampled counter at m in {2, 3} for every n = 2..7. At (q'_2, n = 2) = (32779, 2)
  the line base has B about 3.3e4 points and m = 3 has C(B+2, 3) about 6e12 multisets (about 17 h at 1e8 multisets/s, over the 8 h budget, and
  the independent membership method would need about 5e8 Python additions for its sum table). That one cell, (32779, 2, m = 3), was NOT run.
  (32779, 2) is run at m = 2; every other n is run at m = 2 and m = 3. Coverage gap recorded: m = 3 at n = 2 over a large q. The small-q
  m = 3 coverage at n = 2 (13^2) is from the pre-existing E2 test. The card is silent on a substitute; none was invented.
* P2(ix) "number of targets with T_M >= 1" is counted over all N valid targets (valid bit set), consistent with `min(N, C_sym)`;
  the card does not say generic-only. P2(vii) compares exactly the valid targets with mask value 3 (O and E[2]), the set iii skips.
  P2(viii) counts valid targets with mask bit 1 clear (2R != O) with T_M != T_X, computed only when m = 2 (the contract has m = n).
  The `ix` record carries observed, C_sym, N, bound and margin (bound minus observed, negative means excess).
* Existing tests modified only by extending parameter lists (`EXH_CELLS`, `ARMC_CELLS`, `SEMAEV_CASES`), a docstring, one log label and one
  record condition. No existing assertion was changed.
* The membership method for large-q E2 (`membership_counts`) counts each m-multiset once as an (m-1)-multiset plus its largest-index element.
* `launcher.contract_pairs()` and `arm_c_pairs()` were added to the launcher (not to `make_trial_plan.py`), so the plan generator is unchanged.
* Throughput harness: see below and `throughput-calibration.json`. The run of the harness was not a hook-blocked benchmark; BENCHREC_SKIP was not needed.

## New KATs, cells and results (all passed)

| ID | Test (parametrization) | Cells | Checks |
| --- | --- | --- | --- |
| W0 | `test_widened_kat_fields_disjoint_from_every_contract_pair` | all widened fields | every (q, n) disjoint from arm-A, arm-B and arm-C pairs; q'_n least prime above arm-C q_n (independent trial division); launcher sets agree |
| W1 | `test_wide_least_irreducible_matches_definition` (8) | q in {5, 13}, n = 4..7 | least irreducible g by trial division by every monic polynomial of degree <= n/2 |
| W2 | `test_wide_field_axioms_and_kernel_ops` (8) | q in {5, 13}, n = 4..7 | 400 random elements: assoc, distrib, comm, Frobenius = q-th power, norm-method inverse = Fermat inverse, sqrt, chi by Euler's criterion and by chi_q of the norm; kernel mul, inverse (norm and reference) = Python; d nonsquare for F_{Q^2} |
| W3 | `test_large_q_field_axioms_inverses_chi_10k` (6) | (32779,2), (1033,3), (193,4), (71,5), (41,6), (29,7) | same checks on 10^4 random elements each |
| W4 | `test_large_q_kernel_ops_match_python` (6) | large-q fields | 500 pairs mul/inverse (both modes) and 300 chi_batch x-tuples vs Python |
| W5a | `test_wide_curve_rules` (8), `test_large_q_curve_rules` (6) | wide and large | j in F_q rejects, singular reject, 20 generated curves with j^q != j |
| W5 | `test_wide_group_law_and_point_count_three_ways` (8) | q in {5, 13}, n = 4..7 (all Q < 2^27) | compiled exhaustive = BSGS = kernel character sum (`chi_batch` over every x); plus definition-level table and Python chi sum where Q <= 10^6; N in the Hasse interval; associativity on random triples, N P = O |
| W6 | `test_wide_factor_base_from_definition` (6) | (5,4), (13,4), (5,5), (13,5), (5,6), (5,7) | D, X, t2, 2-torsion from a table of squares built by direct multiplication (Q <= 10^6) |
| W7 | `test_wide_semaev_roots_agree_with_group_law_signed_sums` (3) | (5,4,k=4), (13,4,k=4), (5,5,k=5) | roots of S_{n+1} at k = n against group-law signed sums over F_{Q^2}, 100 tuples each; the two completeness tests agree |
| S1+ | `test_semaev_defining_property_200_tuples` (+3) | (5,4,4), (13,4,4), (5,5,5) | S_{n+1} defining property, 200 tuples |
| W8 | `test_large_q_curve_count_hasse_group_order_and_twist` (6) | large-q fields | BSGS N in Hasse interval; N P = O on 5 random points; N + N_twist = 2Q + 2; group law |
| W9 | `test_large_q_factor_base_symmetric_on_curve_and_t2_from_roots_in_Fq` (6) | large-q fields | D symmetric and on the curve; t2 = number of roots of f in F_q by integer arithmetic mod q |
| E1+ | `test_exhaustive_counters_match_naive_enumeration` (+24) | (5,4,m=2..4), (13,4,m=2), (5,5,m=2..5), each with line, random, twin base | T_A, T_M, T_S, T_X and the weighted helpers, S set, special/generic targets, recount: optimised vs naive enumeration of the same definition |
| E2+ | `test_sampled_counter_matches_naive_enumeration` (+4) | (5,6,m=6), (5,7,m=7), line and random | sampled counter, S counts, cancellation-free count, m_S vs naive; determinism |
| W10 | `test_large_q_sampled_counter_against_membership_method` (11) | six large-q fields at m = 2, and n = 3..7 at m = 3; (32779,2,m=3) not run, DEV-1 | s = 50 sampled targets, line base; counts equal the independent membership method |
| X0 | `test_csym_coefficient_against_independent_series_expansion` | fabricated | C_sym vs truncated power-series multiplication (no binomials), plus tiny known answers and error cases |
| X1 | `test_composition_residuals_on_fabricated_inputs_only` | fabricated arrays | hand-computed expected values for the three residual functions, including the min(N, C_sym) branch and a negative margin |
| X2 | `test_exhaustive_cell_carries_the_three_residual_fields_without_recording_values` (2) | (13,2), m = 2 and 3 | field presence only (viii only at m = 2); no value asserted or recorded |
| X3 | `test_launcher_summary_names_residuals_when_derived_and_withholds_them_in_kat_mode` | fabricated | `composition_residuals` in a derived summary; absent in KAT mode |
| L6 | `test_launcher_kat_refuses_every_arm_c_pair` (18) | 6 arm-C pairs x arms A, B1, C | `--kat` refuses with EXIT_REFUSED |
| L7 | `test_launcher_kat_accepts_widened_fields_beyond_the_refusal_list` | widened fields | none is a contract pair |
| T3 | `test_trial_plan_dumps_is_independent_of_instance_builder_cache_state` | stub builder | two builds give identical text; the full regeneration is compared separately (above) |

KAT mode withholds the residuals like the existing identities (`run_arm_a` pops `identities` when not derived).

## Disjointness table

Contract pairs: arm A/B ladder n=1: 61, 251; n=2: 61, 251, 1021, 4093; n=3: 17, 41, 101, 251; n=4: 11, 23, 53, 101; n=5: 7, 11, 17, 29.
Arm C (q_n, n): (32771,2), (1031,3), (191,4), (67,5), (37,6), (23,7).

| KAT field family | pairs | in a contract pair? |
| --- | --- | --- |
| q = 5, n = 4..7 | (5,4) (5,5) (5,6) (5,7) | no |
| q = 13, n = 4..7 | (13,4) (13,5) (13,6) (13,7) | no |
| q'_n, n = 2..7 | (32779,2) (1033,3) (193,4) (71,5) (41,6) (29,7) | no (note (29,5) is arm A, (29,7) is not) |
| original KAT fields | (5,2) (5,3) (13,2) (13,3), primes 7 11 17 19 23 101 1009 at n=1 | no |

## Throughput (KX-7)

`code/throughput_calibration.py` was run once, completely, from a quiet host (nothing else running), writing only timing fields to
`throughput-calibration.json`; its temporary directory was deleted unread. Measured: B1 analysis at (257,2), (43,3), (29,4), (13,5) with 10^4 tuples
at 1 and 4 workers, B1 with the group-law check on every tuple (500 tuples, the B2 path), the arm-A proxy (103,4) with line, matched-random and
half-twin bases with recount, in full, and the arm-C proxy (32779,2) line base in full. Host: 4 usable cores, 15 GiB. The projections to the
contract cell classes are MODELED (model and assumptions are stored beside them) and are kept separate from the MEASURED fields. Transfer assumptions:
the proxy q differs from the contract q (B1 second-rung q are smaller than the proxies), so only the n-dependence is transferred; the arm-C per-multiset
cost at n > 2 is scaled by (n/2)^2 in the headline and held constant in the optimistic variant. This is an instrument calibration, not a benchmark result.
Rule TP-1 (a projection for one B1 cell of 10^6 tuples above 24 h at the sustainable worker count): **would not trigger** (also not when the A/A
sample doubles the tuples, and not at one worker). The numbers are in `throughput-calibration.json` (no timing values are repeated in this report).

## Artifacts

`code/counters.py`, `code/launcher.py`, `code/tests/test_kat.py`, `code/throughput_calibration.py`, `code/README.md`,
`implementation/kat-report-ac5ad6.md`, `implementation/kat-log-ac5ad6.json`, `implementation/environment-ac5ad6.json`,
`implementation/throughput-calibration.json`, `implementation/trial-plan.preview-ac5ad6.json`.
