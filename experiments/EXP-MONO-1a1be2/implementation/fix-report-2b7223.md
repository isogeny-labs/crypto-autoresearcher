# EXP-MONO-1a1be2 second pre-approval fix report (TASK-20261106-2b7223)

Authorized by DEC-20261106-475620. Executor record. Zero experiment runs; no contract cell computed; no KAT asserts a
predicted value or a cross-convention identity. Files changed: `code/launcher.py`, `code/tests/test_kat.py`,
`code/README.md`, plus the four `implementation/*-2b7223` files. Every HX-1 file is byte-identical to 9a0b5955146a
(checked with `git diff 9a0b5955146a` before the work; the card's frozen list was not touched).

## Headline numbers (measured)

| item | value |
| --- | --- |
| full `test_kat.py` suite under `launcher.run_selftest_suite` (hardened command), real code directory | 438 collected, 438 passed, 0 failed, rc 0, 1397 s (four suites ran in parallel on 4 cores) |
| `EXPECTED_KAT_ITEMS` | 438 (was 379); equals the collected count |
| new `launcher.code_sha256()` | `5d5a607d59741b699065c02066d56a2883a34b44431da56c7bfd439b1f731464` |
| `allowlist_sha256` (paths joined by newlines, trailing newline) | `1832f8552b8d0cb0df9824fa0fd61c1a0308675383d8c795ebecaac9d38c11d1` |
| regenerated trial plan sha256 (temporary path outside the repository) | `9ccbe61445fba836ec44bdea6e55255220a4d08e8d09c9198e5bd28696d8fb4a`, equal to the required value |
| M6 | killed: 6 new S-set items fail (full suite, 438 items) |
| M5 | killed: 8 items fail |
| M3 | killed: 62 items fail |

The mutant extracts live outside the experiment directory, so `test_launcher_refuses_contract_cell_while_specification_not_approved`
also fails in each of them (its specification path does not exist there). It passes on the real tree and is excluded from the counts
above (raw counts: M6 7, M5 9, M3 63). Details and node ids: `mutant-check-2b7223.json`.

## Per HX item

Old-code outcome = the final `test_kat.py` run against the 9a0b5955 `launcher.py` in a scratch extract (node id -> outcome in
`mutant-check-2b7223.json`, `old_code_runs`). "fails" means the new test fails there, as required.

**HX-2 (N-5 item 5, NF-1).** Change: `CODE_TREE_ALLOWLIST` (11 files); `scan_code_tree` (lstat, any depth, symlinks and non-regular
allow-listed paths included), run at import before any other import, in `gate()` and in `write_selftest_receipt`;
`sys.dont_write_bytecode` and a fresh `sys.pycache_prefix` before non-stdlib imports; numpy, yaml and pytest imported before
`code/` is on `sys.path` (and `code/` dropped from `sys.path` when run as a script); `module_origins` recorded and refused if inside
`code/`; the self-test runs `python -B -P -X pycache_prefix=<fresh> -c <wrapper>` in a fresh cwd with `--rootdir <code>`, the
wrapper prints `pytest.__file__` (new `pytest_file` in the receipt and the `startup_selftest` block; refused if inside `code/`);
no -P support: refused, no fallback; `code_tree` block in every contract manifest; post-cell plant or re-hash difference sets
validity `invalid`. Environment sanitising now removes `PYTHONPATH` entirely (previously entries inside `code/` were kept; the
FX-3 test assertion was updated accordingly). Receipt format gained the `pytest_file` field.

| new test | closes | old-code outcome |
| --- | --- | --- |
| `test_hx2_clean_extract_passes_allowlist_equals_the_file_list_and_no_bytecode_is_written` (positive control) | NF-1 | fails (no allow-list; also writes `__pycache__`) |
| `test_hx2_n5y_sourceless_yaml_pyc_refuses_...` | N5-Y | fails (exit 0) |
| `test_hx2_n5p_pytest_pyc_refuses_...` | N5-P | fails (forged pass accepted) |
| `test_hx2_nf1_pycache_pyc_..._refuses_and_with_the_check_off_the_source_runs` | NF-1 | fails (old: marker imported, exit 0) |
| `test_hx2_pytest_rewrite_cache_variant_refuses` | NF-1 variant | fails |
| `test_hx2_non_python_strays_and_symlinks_refuse[8 kinds]` | N-5 item 5 | all 8 fail. For `yaml_dir` and `pyo_in_tests` the old launcher's CLI already refused (the old `.py` rule), so the node fails there on the missing scan API, not on the CLI half |
| `test_hx2_selftest_refuses_when_the_host_python_lacks_the_P_flag` | HX-2 d | fails |
| `test_hx2_gate_and_selftest_subcommand_refuse_a_stray_without_writing` | HX-2 a | fails |
| `test_hx2_trace_block_is_in_every_contract_manifest` | V2-6 | fails |
| `test_hx2_post_cell_plant_or_rehash_difference_makes_the_cell_invalid` | V2-6 | fails |
| `test_fx5_receipt_outside_...` (extended with two `pytest_file` values) | HX-2 d | passes on old (old receipts have no such field and were refused for other reasons); regression only |

Bytecode repro outcomes (scratch roots): N5-Y, N5-P, NF-1 and the pytest rewrite-cache variant all refuse (exit 3, reason names the
entry); with the check switched off in a scratch copy, yaml and the planted-pyc target still resolve to the library and the hashed
source (marker absent), and the self-test resolves pytest outside `code/` and sees the failing stub; the positive control passes.

**HX-3 (NF-2).** `cdf.json` carries `m`; every top-level key (`cell_id`, `n`, `q`, `m`, `curve_id`, `seed`, `B`, `t2`, `N`, `s`,
plus per-base keys) is compared with `raw-result.json` or the plan cell; a missing or unexpected key voids. Tests:
`test_hx3_cdf_baseline_is_valid_and_top_level_N_plus_one_or_s_plus_one_voids`, `..._key_perturbation_voids[q,n,m,seed,curve_id,cell_id]`,
`..._missing_or_unexpected_top_level_key_voids`, `test_hx3_cdf_json_of_a_real_kat_cell_carries_m`: all fail on old.
`[B]`, `[t2]`, `[target_seed]`, `[base_seed]` pass on old (those keys were already compared via the per-base check): regression only.
The `_fake_c` fabricated record was completed with the top-level keys.

**HX-4 (NF-3).** `RECOUNT_CONVENTIONS = (A, M, S, X)`; a missing, empty or non-numeric convention voids. Test
`test_hx4_recount_convention_missing_empty_or_non_numeric_voids_and_a_full_recount_stays_valid`: fails on old; its positive control stays valid.

**HX-5 (NF-4).** (a) sentinel check in `gate(cell_id=...)` and again in `run_cell`; (b) `family_runs_at_stop`, `family_void`, `run_id`, `writer` in the
sentinel; (c) `os.path.lexists`; (d) reserved run ids, `FileExistsError` not swallowed, foreign entry -> `invalid` + exit 5, valid
sentinel -> void with the sentinel untouched. Tests: `test_hx5a_...`, `test_hx5b_...`, `test_hx5c_...[broken_symlink,directory,empty_file]`,
`test_hx5d_run_id_...[5 ids]`, `test_hx5d_write_stop_f2_never_swallows...[3 kinds]`, `test_hx5d_a_valid_sentinel_...`. All fail on old except
`test_hx5c[directory]` and `[empty_file]` (old already refused those; regression only). The existing F2 test now expects `FileExistsError`
from a second `write_stop_f2`. The sentinel check is structural: a hand-made file with the launcher's keys is indistinguishable.

**HX-6 (NF-5).** `test_large_q_arm_c_S_set_counts_and_m_S_match_a_pure_python_membership_count`, 8 cells: (41, 6) and (29, 7); m = 2, 3; line and
matched_random bases. `S_counts`, `exceptional_targets`, `m_S`, the cancellation-free total and S itself are compared with a pure-Python enumeration
(no kernel call). Vacuity guards: at m = 2 (any base) and at m = 3 on the matched_random base at least one S key of 2^32 or more has
nonzero truth (S = {O} at index 2Q for even m); at m = 3 on the line base the S keys are below 2^32, as the review said. Observed `m_S`:
**zero on every KAT cell examined (all 8), so the guard applies to `S_counts`**. Evidence: M6 applied in a scratch extract fails 6 of the new items
(the m = 2 cells of both fields on both bases, and the m = 3 matched_random cells); M5 and M3 are still killed. On old code and on the committed bytes
these items pass, by design. Added wall time: standalone 128 s, of which about 125 s is shared fixture construction (`large_base` factor bases) that
the existing large-q tests also use; the per-cell comparison itself is about 21 s at (41, 6) m = 2 line and a few seconds elsewhere. A placeholder N = Q is passed to
`arm_c_cell` (N enters only lambda, which is not compared) to avoid a minutes-long baby-step giant-step count. Full suite wall: 1397 s (parallel load).

**HX-7 (NF-6).** `compute_validity` takes the manifest and the `GateResult`; `invalid` unless the gate block equals values recomputed from disk and the
startup_selftest block is a full pass for the status; `runs/` and `selftest-receipts/` must be real directories inside the experiment directory (gate, `resolve_run_dir`,
selftest). Tests `test_hx7_a_hand_built_gate_result_with_fake_hashes_is_invalid`, `test_hx7_gate_edited_after_the_fact_or_a_failing_selftest_block_is_invalid`,
`test_hx7_symlinked_runs_directory_refuses_and_nothing_is_written_outside`: all fail on old.

**HX-8 (NF-7).** Keys `peak_rss_kb_self`, `peak_rss_kb_children_pre_cell`, `peak_rss_kb_cell_children` (+ reason), `peak_rss_kb_budget_check` (self + cell figure vs 16 GB; exceeding voids). Worker
RSS is self-reported with each finished block via `getrusage(RUSAGE_SELF)` (a forked worker starts from its parent's resident set). Tests
`test_hx8_memory_keys_...`, `test_hx8_a_cell_with_workers_reports_their_own_peak_rss`: fail on old.

**HX-9.** `new_receipt_dir`: exclusive `mkdir`, suffix pid + counter. `test_hx9_two_back_to_back_receipts_in_one_second_both_verify` (clock frozen): fails on old (directory clash).

**HX-10.** Full suite 438/438; CR-1 and RR-2 producer tests all pass (fx2 to fx11 tests unchanged apart from the edits named above). Plan regenerated: equal. A smoke check
of a real arm A, arm C and arm B2 cell on KAT field (13, 2) through the contract-mode pipeline in a scratch root (not a run, nothing recorded in the repository) gave validity `valid` for
all three and recorded worker RSS for B2.

## Test edits to existing tests (all in the allowed file)

FX-3 PYTHONPATH assertion (now removed entirely); FX-6 startup_selftest key set (+ `pytest_file`); FX-8 second sentinel write expects `FileExistsError`; FX-11 (4)
key list; FX-13 collection uses `-B -P`; `_fake_c` cdf completed; `import yaml` before `code/` is put on `sys.path`.

## Scope findings

None. No fix needed a file outside the write scope. Residual scope (as in the DEC): a file planted and removed between the pre-gate and post-cell scans is unseen;
a hand-made sentinel with the launcher's keys is accepted; forged receipts remain checkable after the fact only.

## Files written (sha256, excluding this report)

| file | sha256 |
| --- | --- |
| code/launcher.py | a7dcb7de6c07c2f870c1696e5c021b6af8abec67308bdb430683533189adc2be |
| code/tests/test_kat.py | 6da794c6d53bf6d4b39f079994e4d09d5245e358594bc1de819b11ffb05e5a66 |
| code/README.md | 44fc3004180b9769ed320b8736a660deac323b449afb1623ca9dd95b2f458aab |
| implementation/environment-2b7223.json | 416b1847cf6ac7a44f92036c02811797ec38fad93943575a3abeb50d4e5f40b5 |
| implementation/kat-log-2b7223.json | 3f0ba330907d3eb289d962006fd6ddeccdb21f430025e77042237e221583845d |
| implementation/mutant-check-2b7223.json | c5b05c287e3490b8f8efaa02453a5a1cdac4e3c471bc0835f877712acdce4527 |
