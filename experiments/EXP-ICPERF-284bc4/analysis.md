# EXP-ICPERF-284bc4 analysis: stage-0 price-ratio identity instrument (version 2)

Coordinator evidence review under review plan REVIEW-ICPERF-284bc4-20261105 (`review/review-plan.yaml`, frozen at f7eb8ae292, sha256 f4a34e9bd2aa961039c8371d09a110198ce8904a1dfc949e12ba718972fd6985). Evidence record EV-ICPERF-08f6f9; decision DEC-20261105-8a9984. Hypothesis H-ICPERF-2f52d1; approval DEC-20261029-ca33b3; session RBS-ICPERF-8cdc92; goal GOAL-ICPERF-e6b6a4. Binding rulings DEC-20261029-9bc3ff, DEC-20261029-22e05b, DEC-20261029-5554ee. Version-1 runs RUN-ICPERF-943efa and RUN-ICPERF-b09be8 are invalidated and are not cited here as evidence.

The Coordinator had no shell. Every number below was read from the named committed files. Digests, git state and checker exit codes are as reported by the reviewers and the top-level session.

## Observation

Validity first (joint J1, validator TASK-20261105-576b11, verdict holds):

- Six of six preregistered units exist, one run each, as the stopping rule requires: RUN-ICPERF-8e3acd (primary, price-ratio-identity), RUN-ICPERF-2d715d (CON-1 A-change), RUN-ICPERF-2c627f (CON-2 r-change), RUN-ICPERF-779d41 (CON-3 BSGS enumeration), RUN-ICPERF-30596e (NEG-1 c_probe 371), RUN-ICPERF-850008 (NEG-2 precomputation 10 steps).
- 60 of 60 receipt digests and 180 of 180 manifest cross-bindings match. All six manifests pass `check_run`, and a corrupted-manifest control shows the check discriminates. The 12-entry journal chain is intact, and its tip equals the audit's and the report's. `tools/runbook.py verify --rerun-checks` is OK. `check.py` returns rc 0 on all six. Independent code re-evaluated 268 of 268 runbook assertions. RESULTS.md, the journal summary, data.json and report.pdf all agree with raw-result.json. Session preflight commit 9d13fcfde5 recorded a clean tree.
- Seeds: none, by design (deterministic exact arithmetic, `replication.seeds: []`); PYTHONHASHSEED 0 in the session overlay.
- No unit claims a solve or relation (`attack_claimed: false`, certificate kind none), so no certificate is owed.

Recorded values (read here from each `runs/<RUN>/raw-result.json`):

| run | trial | recorded |
|---|---|---|
| RUN-ICPERF-8e3acd | primary | price ratio 925/4; precomputation_steps 525; cells (1000,2) probes 50, bsgs 50, bl_steps 2, ic 18500 ns, bl 80 ns, ratio 925/4; (4000,2) 200, 200, 8, 74000, 320, 925/4; (1000,4) 25, 25, 1, 9250, 40, 925/4; ratios_agree true; all_match_bsgs true; matches_preregistered true |
| RUN-ICPERF-2d715d | CON-1 | cells (1000,2) and (1000,4) both 925/4; same_reduced_ratio true; matches_preregistered true |
| RUN-ICPERF-2c627f | CON-2 | cells (1000,2) and (4000,2) both 925/4; same_reduced_ratio true; matches_preregistered true |
| RUN-ICPERF-779d41 | CON-3 | enumerated 50, 200, 25 equal formula 50, 200, 25; all_match true |
| RUN-ICPERF-30596e | NEG-1 | price ratio 1855/8; online ratio 1855/8 at all three cells; ic 18550, 74200, 9275 ns; matches_preregistered false |
| RUN-ICPERF-850008 | NEG-2 | precomputation_steps 10; bl_steps 105, 420, 105/2; bl 4200, 16800, 2100 ns; online ratio 185/42 at all three cells; matches_preregistered false; no price ratio field |

Audit AUD-20261105T164527Z-d5036c: verdict flagged, matched 0 of 6. The validator re-read all 66 compared rows with its own resolver:
- 27 present on both sides and exactly equal;
- 39 absent from both the recorded and the replayed file;
- 0 absent on one side, 0 differing.

With only /elapsed_seconds and /interpreter excluded, recorded and replayed documents are type-strictly equal in all six units.

The audit's `environment_drift: []` is a false negative. The recorded interpreter is CPython 3.11.17 and the audit replay used 3.13.18, but `_recorded_python` reads a manifest key these manifests do not use. The validator replayed the bound run.py under 3.11.18, 3.12.3 and 3.13.18: 18 of 18 replays were identical, with check.py rc 0.

Blind re-derivation (TASK-20261105-b543c3, `sources_read: []`, `blind_from_respected: true`):
- precomputation 525 steps; price ratio 925/4;
- probes and BSGS maxima 50/200/25 at the three cells; bl_steps 2/8/1; online times 18500/74000/9250 ns against 80/320/40 ns, each ratio 925/4;
- c_probe 371 gives 1855/8 everywhere;
- precomputation 10 gives 185/42, with bl_steps 105/2 at (1000,4).

## Comparison

- Recorded against preregistered (CMP-PRIMARY, out of sample, fixed 2026-10-17 in EXP-ICPERF-e467a5): every primary integer and flag equals the verbatim success criterion and the derived cell values in the specification. Exact equality, no tolerance.
- Recorded against blind re-derivation: every value in the table above equals the blind value, at all six units, including the NEG-2 non-integer bl_steps 105/2.
- Controls against their pass conditions (calibration, in-sample PRED-CONTROLS): CON-1, CON-2 and CON-3 hold. NEG-1 reduces to 1855/8 and NEG-2 to 185/42, and both fail the preregistered match, as designed. Session control validity passed.
- A/A (CMP-AA): no value differs between recorded and replayed units across process and interpreter changes. The tool's mismatch count comes only from pointers absent on both sides: the runbook's replay.compare flattens an 11-pointer union over five trial kinds, while the specification's own 17-row contract is fully present and equal.
- Against Pollard rho: no comparison exists. No arm is rho, no target is solved, and no counted unit exists. Against Bernstein-Lange: only a closed-form step count priced at an assumed 40 ns.

## Inference

The stage-0 instrument evaluates the stated closed-form online-time model of H-ICPERF-2f52d1 in exact rationals and returns the preregistered integers: 925/4 for the price formula and for each of the three cells' online ratios, and probe counts 50/200/25 equal to the enumerated BSGS maxima. Its output moves under a planted change of c_probe (1855/8) and of the precomputation model (185/42). An implementation written blind from the statement reproduces every value. The audit flag is a replay-coverage defect of the runbook pointer list plus a key-name gap in the audit tool, not a value mismatch. The session is therefore citable with those disclosures, in the sense of DEC-20261029-5554ee `citability_meaning`.

This supports H-ICPERF-2f52d1 as stated, and only as stated: an arithmetic identity on three toy cells. The identity holds by construction. Red-team joint J2 (TASK-20261105-c44b03, verdict holds) showed that r and A cancel for every price vector once precomputation_steps = states * c_state / c_step (2000 of 2000 random price triples). So ratios_agree, CON-1 and CON-2 carry no information about prices. NEG-2 shows the identity is equivalent to that equal-precomputation-time definition. Only the literal 925/4 carries information, and it is a function of the frozen inputs alone.

Nothing transfers to IDEA-20261015-7a3c9e, the section-23 table, n=83, any host latency, or rho. The three prices are the parent idea's n=83 inferred (c_probe, c_state) and assumed (c_step) prices, so 925/4 = 231.25 is numerically the idea's "231 against the measured 235". This pass adds no information to that comparison, and the 235x figure is itself unverified in the ledger. The record makes no latency or n=83 statement; it does not establish that there is no latency effect.

Section 5a (crypto AGENTS section 5a, docs/sheriff.md B5): no comparison against rho is made, so no band is owed. The red team's illustrative band uses an assumed counter model in which every native unit is priced at 0, 0.1 or 1 GAE. It puts the IC/BL online ratio at 10/21 under uniform weights and anywhere in [0.119, 1.905] across the 27 corners, against 231.25 at the record's ns prices. The order is set entirely by the price assumption, and no ranking in either direction is licensed.

## Limitation

- One deterministic execution per unit; independent_instances 1; no seeds. No pcc claim covers 925/4, so cite it as an unverified assertion of the producer, recomputed by the validator and the blind re-deriver.
- The audit stays flagged as recorded (matched 0 of 6). Replay assurance rests on the validator's row-level classification and 18 scratch replays, which are not durable audit records. The interpreter-parity check required by DEC-20261029-5554ee did not run; the actual drift, 3.11.17 to 3.13.18, changed no value. The recorded 3.11.17 build cannot be re-obtained (nearest available: 3.11.18).
- Labels: runbook.yaml, the run report and data.json call computed integers "measured". tools/progress_metrics.py exports the assumed prices, including NEG-1's planted 371, in physical units without an "assumed" or "planted" qualifier. This needs an additive correction, not an edit.
- Discriminating power: only NEG-1 and NEG-2 can fail when the primary passes, and they catch implementations that ignore their inputs (mutants M1-M4). Four mutants pass every assertion:
  - M5: BSGS enumeration replaced by ceil(m/s), the v1 SF-1 defect;
  - M7: price ratio taken from the online ratio;
  - M8: exactness rule removed;
  - M11: common-ratio check on the first row only.

  The hypothesis's proof obligation "the price formula is computed separately from the online times" is met by code reading and by the blind re-derivation, not by any run assertion.
- CON-3 compares the BSGS worst case with r/(A*states), which the parent idea defines as a geometric mean. The deterministic BSGS mean is 25.5, 100.5 and 13.0 against 50, 200 and 25, so CON-3 does not support "IC equals BSGS on the quotient" at expected cost. In this configuration (contiguous baby steps, stride equal to table size, s dividing m) the enumerated maximum equals m/s as a theorem.
- The BL closed form is evaluated outside its regime at all three cells: P = 525 is at least m at two cells, and the implied BL table of about 20.9 entries exceeds m^(1/3). The bl_steps values are formula values, not walk lengths.
- Integrality depends on the rounded BL constant 21/10. The unrounded 1.77 * 1.2 = 2.124 or 1.93 * 1.21 = 2.335 forces an inexact division, which the specification classifies as instrument failure. The exactness rule has no positive control (M8).
- Memory is not recorded; resource records are timing only (under 0.05 s per run).
- Scope: prices 370/2100/40 ns as assumed constants, BL constant 21/10, 10 states, cells (1000,2), (4000,2), (1000,4); run.py sha256 ef13257e...; CPython 3.11.17. Claim tier toy (no field or curve instance exists).
