#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set par(justify: false)

= Decision report: EXP-ICPERF-283a70, DEC-20261105-6e2616

Evidence review of the stage-0 seeded geometric-sample instrument, version 2, for hypothesis H-ICPERF-5adc9b under goal GOAL-ICPERF-e6b6a4. Composed by the Coordinator from review plan REVIEW-ICPERF-283a70-20261105 (frozen at f7eb8ae292, sha256 `c4e49dbf7bfa986f187c53c354315d4fece373895ecd347577311f5254163368`). No trial was run for this review.

== Decision

#table(columns: 2,
  [*Decision*], [support, scoped to the exact integers of the specified sampler (H-ICPERF-5adc9b integer statement)],
  [*Evidence strength*], [preliminary],
  [*Claim tier*], [toy (scale label only; 64 synthetic draws, no field, curve, table or host)],
  [*Proof status*], [derivation (blind from-prose implementation; not proved)],
  [*Hypothesis status*], [H-ICPERF-5adc9b: approved to supported (via analyzed)],
  [*Evidence record*], [EV-ICPERF-84ff45],
  [*Approval*], [DEC-20261029-0e40f3],
  [*Session*], [RBS-ICPERF-67df7d],
  [*Runs*], [RUN-ICPERF-f21eb1 (primary), RUN-ICPERF-0ef41e (CTL-1, wrong triple), RUN-ICPERF-74e9a2 (CTL-2, support from 0)],
  [*Reviews*], [J1 validator TASK-20261105-558a8b (holds); J2 red team TASK-20261105-b3b41a (holds); blind re-derivation TASK-20261105-6d9502 (derived)],
  [*Audit*], [AUD-20261105T164530Z-b85ca9 (clean, 3 of 3 exact; parity check did not run)],
  [*Binding rulings*], [DEC-20261029-9bc3ff, DEC-20261029-22e05b, DEC-20261029-5554ee],
  [*Not evidence*], [RUN-ICPERF-943efa, RUN-ICPERF-b09be8 (version 1, invalidated)],
)

== Exact scoped claim

Under session RBS-ICPERF-67df7d, `run.py` (sha256 `53965863...9a38`) ran at seed 20261017, p = 1/50, n = 64, shifts (13, 17, 5), support from 1. It wrote sample sum 2943, sum of squares 289567 and median 28, with no median split. These equal the integers fixed on 2026-10-17. The wrong-triple arm wrote 2938, 290138, 29 and the support-from-0 arm 2879, 283745, 27, and both failed the exact match. An implementation written blind from the specification prose reproduces all three arms. Both band flags were true on all three units, so the bands distinguished none of them. Nothing follows about geometric shape beyond this sample, about p, about any table's probe counts, about host latency, or about any index-calculus or rho cost.

== Graph

#image("graph.svg", width: 100%)

Panel A: sample sum, sum of squares and median for each arm. Filled circles are recorded values from `raw-result.json`, open squares the blind re-derivation, crosses the preregistered value or control pass condition. The dashed line is the primary pass value. Only the primary has an exact match. Panel B: CV squared and median-to-mean for each arm, against the shaded descriptive bands (0.81 to 1.21, and 0.6 to 0.8). All three arms, including both wrong samplers, lie inside both bands. Each arm has 64 draws, one seed and one execution. The values are exact integers and fractions, so there are no error bars. Data: `data.json` in this directory.

== Observation

- Validity (J1): 3 of 3 units; 30 of 30 receipt digests; `check_run` clean; journal chain intact (9 entries, tip `c97b6c9d...`); raw results, RESULTS.md, summary and run report agree. A mutation test of the frozen runbook shows that only the integers decide validity and that band flips never do. No median split (order statistics 32 and 33: 28 and 28, 29 and 29, 27 and 27). No version-1 run cited.
- Primary RUN-ICPERF-f21eb1: 2943, 289567, 28; exact match true; CV squared 9871039/8661249 = 1.13968; median-to-mean 1792/2943 = 0.60890.
- CTL-1 RUN-ICPERF-0ef41e: 2938, 290138, 29; exact match false; 1.15120 and 0.63172, both bands true.
- CTL-2 RUN-ICPERF-74e9a2: 2879, 283745, 27; exact match false; 1.19091 and 0.60021, both bands true.
- Audit: clean, 3 of 3 exact on 11 integer and boolean pointers. Recorded CPython 3.11.17, replay 3.13.18. The audit's "no environment drift" is a false negative, because its parity check did not run.
- Blind re-derivation: equal to every recorded value for all three arms, with fractions equal after reduction.

== Comparison

- Against the preregistered integers (out of sample, fixed 2026-10-17): exact equality on the primary.
- Against the control pass conditions (in-sample calibration): both controls record their frozen integers and fail the exact match, as required.
- Against the blind from-prose implementation: exact equality at every value in all three arms. This is the only check that can fail on an error shared by the prose, both runners and the design code.
- Bands: 3 of 3 arms pass both bands, while the exact match passes in 1 of 3. The bands do not separate the frozen sampler from either wrong sampler.
- Against Pollard rho: none.

== Inference

The specification text determines the integers, and the producer's code is one faithful evaluation of it. Within the xorshift family, the exact integers discriminate the declared parameters and conventions: according to the red team, 0 of 21202 completing wrong triples match both the sum and the sum of squares, and a seed-tested convention misses by 1 in the sum. The bands discriminate nothing on this record. The v1 shape wording of H-ICPERF-5adc9b is not adopted. Section 5a: no comparison against rho is made and the set of priced arms is empty, so no band is owed.

== Limitation

- One seed and one execution per arm. No pcc claim or execution proof covers the integers. The draws are not persisted in the run artifacts.
- The audit's parity check was inoperative. Only two interpreter versions were exercised.
- CTL-2 is an affine image of the primary, and CTL-1 is a known-outcome control. Neither detects a common-mode code error on its own.
- The run report labels the band flags "measured" for the primary only and omits the controls' flags. They are tabulated for all three units here and in EV-ICPERF-84ff45.
- The parent idea's band test for real probe panels is weak at n = 64 (red-team scratch computation, not evidence). This pass does not validate it.
- Memory is not recorded.

== Next actions

+ *Primary (NA-1).* One tooling handoff repairs the replay contract in `tools/runbook.py`. The interpreter parity check must read the manifest version keys, a pointer absent on both sides must count as not applicable rather than a mismatch, and compare pointers may be declared per trial. Regression tests run on both sessions' bytes, and the existing audits stay as recorded.
+ NA-2. At the next goal rerank, rank a stage-1 design for IDEA-20261015-b41f68 that fixes the predicted p in advance and uses a goodness-of-fit test plus a mean check, with power stated against lognormal and wrong-p null objects. It does not reuse the bands.
+ NA-3. The red team's reversal reading (a work-identity certificate for cross-host ns per probe) may be filed as a proposal and ranked on its merits.
+ NA-4. Top-level session: render, inspect, validate, archive together with DEC-20261105-8a9984, push, and refresh the PR with auto-merge.

== Earlier reports and canonical graphs

- Earlier run report: `experiments/EXP-ICPERF-283a70/reports/run-20261030T1525Z/` (report.pdf, graph.svg, data.json). It is unchanged.
- Canonical graphs checked: `knowledge/frontiers/ecdlp/` (README.md and the generic-rho and index-calculus KR rows; there is no rendered graph source there). No row cites this experiment, its runs, H-ICPERF-5adc9b or IDEA-20261015-b41f68. No canonical graph changes, because a toy instrument pass moves no frontier.
