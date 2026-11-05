# EXP-ICPERF-283a70 analysis: stage-0 seeded geometric-sample instrument (version 2)

Coordinator evidence review under review plan REVIEW-ICPERF-283a70-20261105 (`review/review-plan.yaml`, frozen at f7eb8ae292, sha256 c4e49dbf7bfa986f187c53c354315d4fece373895ecd347577311f5254163368). Evidence record EV-ICPERF-84ff45; decision DEC-20261105-6e2616. Hypothesis H-ICPERF-5adc9b; approval DEC-20261029-0e40f3; session RBS-ICPERF-67df7d; goal GOAL-ICPERF-e6b6a4. Binding rulings DEC-20261029-9bc3ff, DEC-20261029-22e05b, DEC-20261029-5554ee. Version-1 runs RUN-ICPERF-943efa and RUN-ICPERF-b09be8 are invalidated and are not cited here as evidence.

Decision rule: the specification decisive_test and the DEC-20261029-0e40f3 restated pass rule. The run passes only on exact sample_sum 2943, sum_squares 289567 and median 28, with no median split. The CV and median-to-mean band flags are descriptive only. CTL-1 and CTL-2 must both fail the exact match.

The Coordinator had no shell. Every number below was read from the named committed files. Digests, git state and checker exit codes are as reported by the reviewers and the top-level session.

## Observation

Validity first (joint J1, validator TASK-20261105-558a8b, verdict holds):

- Three of three preregistered units exist, one run each: RUN-ICPERF-f21eb1 (primary), RUN-ICPERF-0ef41e (CTL-1, wrong shift triple), RUN-ICPERF-74e9a2 (CTL-2, support from 0).
- The bound inputs are equal at the snapshot and at all three relevant commits. 30 of 30 receipt digests match, and all three manifests pass `check_run`. The 9-entry journal chain is intact, and its tip equals the audit's and the report's. Raw results, RESULTS.md, the summary and the run report agree. The session preflight recorded a clean tree.
- Seed 20261017, p_den 50 and n_targets 64 are asserted in every unit. PYTHONHASHSEED 0 is set.
- A mutation test of the frozen runbook's assertions passed 18 of 18 cases as expected: integer changes always invalidate a unit, and band-flag flips never change validity.
- No unit claims a solve or relation (certificate kind none).

Recorded values (read here from each `runs/<RUN>/raw-result.json`):

| run | arm | sum | sum of squares | median (32nd = 33rd) | exact_match | CV^2 | median/mean | bands |
|---|---|---|---|---|---|---|---|---|
| RUN-ICPERF-f21eb1 | primary (13,17,5; support 1) | 2943 | 289567 | 28 | true | 9871039/8661249 = 1.13968 | 1792/2943 = 0.60890 | both true |
| RUN-ICPERF-0ef41e | CTL-1 (1,2,14; support 1) | 2938 | 290138 | 29 | false | 9936988/8631844 = 1.15120 | 1856/2938 = 0.63172 | both true |
| RUN-ICPERF-74e9a2 | CTL-2 (13,17,5; support 0) | 2879 | 283745 | 27 | false | 9871039/8288641 = 1.19091 | 1728/2879 = 0.60021 | both true |

Audit AUD-20261105T164530Z-b85ca9: clean, 3 of 3 replayed and matched exactly on 11 integer and boolean pointers, no tolerance. The recorded interpreter is CPython 3.11.17 and the replay used 3.13.18. The audit's "no environment drift" is a false negative (PARITY-1): `_recorded_python` reads a manifest key these manifests do not use. No value is affected.

Blind re-derivation (TASK-20261105-6d9502, written from the verbatim sampler definition, `sources_read: []`, `blind_from_respected: true`): A 2943/289567/28, B 2938/290138/29, C 2879/283745/27. The 32nd and 33rd order statistics are equal in every arm. The CV^2 and median/mean fractions equal the recorded ones after reduction. The blind primary draws equal the validator's spec-prose draws element by element.

## Comparison

- Primary against the preregistered integers (CMP-PRIMARY, out of sample, fixed 2026-10-17 in EXP-ICPERF-b2f2d0): exact equality, no median split.
- Controls against their pass conditions (CMP-CTL-1, CMP-CTL-2; in-sample calibration): both record their frozen integers and fail the exact match, as required. Session control validity passed.
- All three arms against the blind from-prose implementation: exact equality at every value. This is the only check that can fail on an error shared by the prose, v1 run.py, v2 run.py and the design scratch code.
- A/A (CMP-AA): 3 of 3 exact across process, host and interpreter changes.
- Bands: cv_in_band and median_ratio_in_band are true in 3 of 3 arms, while exact_match is true in 1 of 3. The bands do not separate the frozen sampler from either wrong sampler.
- Against Pollard rho: no comparison exists. There is no rho arm, no index-calculus arm, no group and no GAE counter.

## Inference

The specification's sampler prose determines 2943/289567/28 and both control triples. The producer runner, the audit replay, the validator's spec-prose sampler, the red team's recomputation and the blind from-prose implementation all agree, so the text is the definition and the code is one faithful evaluation of it.

Red-team joint J2 (TASK-20261105-b3b41a, verdict holds) showed that the exact integers discriminate the declared parameters and conventions within the xorshift family. 0 of 21202 completing wrong triples match both the sum and the sum of squares, and a seed-tested convention misses by 1 in the sum. The bands discriminate nothing on this record.

This supports H-ICPERF-5adc9b's integer statement, and the band clauses only as arithmetic consequences of the integers. The hypothesis's v1 shape wording is not adopted (DEC-20261029-22e05b F4), because both wrong samplers also pass both bands: "Stage 0 checks that shape", "The CV band is the shape control", both_bands_hold read as a shape check, and "draws from the geometric law". Nothing follows about geometric shape beyond this sample, about p, about any table's or probe panel's probe-count law, about host latency or huge pages, or about IDEA-20261015-b41f68 claims (1)-(4).

The pass does not validate the parent idea's stage-1 band test. Red-team scratch computations, which are not evidence, put that test's rejection of a truly geometric 64-sample near 53 percent and its acceptance of a CV = 1 lognormal near 30 percent (98 percent at n = 4096).

Section 5a (crypto AGENTS section 5a, docs/sheriff.md B5): no comparison against rho is made and the set of priced arms is empty, so no band is owed. Pricing 64 synthetic draws in GAE would be a category error, and elapsed_seconds is never a bound.

## Limitation

- One seed and one execution per arm; no independent second run. No pcc claim or execution proof covers the integers (verified_units 0), so cite them as producer assertions, recomputed by the reviewers.
- The 64 draws are not persisted in raw-result.json. The reviewers regenerated them; they were not read from the run.
- The audit's interpreter-parity check was inoperative. Only two interpreter versions were exercised: 3.11.17 recorded, and 3.13.18 replayed by both the audit and the validator.
- CTL-2 is an affine image of the primary (S - 64, Q - 2S + 64, median - 1, with the same CV^2 numerator). CTL-1 is a known-outcome choice from a design scan. Both share step(), draw() and moments() with the primary, so neither detects a common-mode code error on its own; the blind implementation does.
- The run report (reports/run-20261030T1525Z) labels the band flags "measured" for the primary only (n = 1) and omits the controls' flags. They are tabulated for all three units here and in EV-ICPERF-84ff45.
- The specification's verbatim v1 success_criterion still names the band flags. They are entailed by the integers and are not used as a criterion.
- Memory is not recorded; timing only (about 0.6 s driver wall time per unit).
- Scope: seed 20261017, p = 1/50, n = 64, shift triples (13,17,5) and (1,2,14), support_min 1 and 0; run.py sha256 53965863...9a38; CPython 3.11.17. Claim tier toy.
