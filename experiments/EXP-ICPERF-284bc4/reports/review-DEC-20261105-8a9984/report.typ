#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set par(justify: false)

= Decision report: EXP-ICPERF-284bc4, DEC-20261105-8a9984

Evidence review of the stage-0 price-ratio identity instrument, version 2, for hypothesis H-ICPERF-2f52d1 under goal GOAL-ICPERF-e6b6a4. Composed by the Coordinator from review plan REVIEW-ICPERF-284bc4-20261105 (frozen at f7eb8ae292, sha256 `f4a34e9bd2aa961039c8371d09a110198ce8904a1dfc949e12ba718972fd6985`). No trial was run for this review.

== Decision

#table(columns: 2,
  [*Decision*], [support, scoped to the arithmetic identity as stated in H-ICPERF-2f52d1],
  [*Evidence strength*], [preliminary],
  [*Claim tier*], [toy (scale label only; no field, curve or target exists)],
  [*Proof status*], [derivation (blind exact-rational re-derivation; not proved)],
  [*Hypothesis status*], [H-ICPERF-2f52d1: approved to supported (via analyzed)],
  [*Evidence record*], [EV-ICPERF-08f6f9],
  [*Approval*], [DEC-20261029-ca33b3],
  [*Session*], [RBS-ICPERF-8cdc92],
  [*Runs*], [RUN-ICPERF-8e3acd (primary), RUN-ICPERF-2d715d, RUN-ICPERF-2c627f, RUN-ICPERF-779d41, RUN-ICPERF-30596e, RUN-ICPERF-850008],
  [*Reviews*], [J1 validator TASK-20261105-576b11 (holds); J2 red team TASK-20261105-c44b03 (holds); blind re-derivation TASK-20261105-b543c3 (derived)],
  [*Audit*], [AUD-20261105T164527Z-d5036c (flagged; pointer-coverage defect, no value differs)],
  [*Binding rulings*], [DEC-20261029-9bc3ff, DEC-20261029-22e05b, DEC-20261029-5554ee],
  [*Not evidence*], [RUN-ICPERF-943efa, RUN-ICPERF-b09be8 (version 1, invalidated)],
)

== Exact scoped claim

At c#sub[probe] = 370 ns, c#sub[state] = 2100 ns and c#sub[step] = 40 ns (assumed constants, equal to the n=83 inferred and assumed prices of IDEA-20261015-7a3c9e), BL constant 21/10 and 10 states, `run.py` (sha256 `ef13257e...`) evaluates the stated closed-form online-time model in exact rationals. The reduced price ratio and the online ratio at each of the cells (r, A) = (1000, 2), (4000, 2), (1000, 4) are 925/4, and the probe counts 50, 200 and 25 equal the enumerated BSGS maxima. A planted c#sub[probe] = 371 gives 1855/8, and a planted 10-step precomputation gives 185/42. An implementation written blind from the statement agrees on every value. The record measures no price, latency, step count or cost. It compares nothing with Pollard rho, ranks index calculus against Bernstein-Lange in neither direction, and makes no latency or n=83 statement.

== Graph

#image("graph.svg", width: 100%)

Panel A: reduced ratio (IC online ns over BL online ns at assumed prices, dimensionless, log scale) for every unit and cell. Filled circles are recorded values from `raw-result.json`, open squares the blind re-derivation, crosses the preregistered value or control pass condition. The dashed line is the preregistered success value 925/4 = 231.25. NEG-1 sits at 1855/8 = 231.875 and NEG-2 at 185/42 = 4.405. Panel B: CON-3 (RUN-ICPERF-779d41), enumerated BSGS worst-case lookups against the probe formula, with the red team's BSGS mean shown for contrast (not a run value). One deterministic execution per unit (n = 1, no seeds). The values are exact rationals, so there are no error bars. Data: `data.json` in this directory.

== Observation

- Validity (J1): 6 of 6 units; 60 of 60 receipt digests; 180 of 180 manifest bindings; `check_run` clean on all six; journal chain intact (tip `534b1a29...`); runbook verify OK; 268 of 268 assertions re-evaluated by independent code; raw results, RESULTS.md, summary and run report agree; no version-1 run cited.
- Primary RUN-ICPERF-8e3acd: price ratio 925/4, precomputation 525 steps; cells (1000,2) probes 50, BSGS 50, BL steps 2, 18500 ns over 80 ns; (4000,2) 200, 200, 8, 74000 over 320; (1000,4) 25, 25, 1, 9250 over 40; each ratio 925/4.
- Controls: CON-1 and CON-2 give 925/4 at both cells; CON-3 enumerates 50, 200, 25; NEG-1 gives 1855/8 at the price and every cell; NEG-2 gives 185/42 at every cell, with BL steps 105, 420 and 105/2.
- Audit: flagged, matched 0 of 6. Of 66 compared rows, 27 are present on both sides and exactly equal, 39 are absent from both files, and none differs. The parity check did not run: recorded CPython 3.11.17, replay 3.13.18. The validator replayed under 3.11.18, 3.12.3 and 3.13.18, and 18 of 18 replays were identical.
- Blind re-derivation: equal to every recorded value above.

== Comparison

- Against the preregistered integers (out of sample, fixed 2026-10-17): exact equality at every primary quantity.
- Against the blind re-derivation: exact equality at all six units, including the NEG-2 non-integer 105/2.
- Controls against their pass conditions (in-sample calibration): all behave as designed; session control validity passed.
- A/A: no value differs across process and interpreter changes.
- Against Pollard rho: none. Against Bernstein-Lange: only a closed form priced at an assumed 40 ns.

== Inference

The instrument evaluates the stated algebra correctly, and its output moves under the two planted perturbations. The identity holds by construction. r and A cancel for every price vector once the precomputation is defined as equal time (the red team's null-price control agreed in 2000 of 2000 cases), and NEG-2 shows that the identity is equivalent to that definition. Only the literal 925/4 carries information, and it is a function of the frozen inputs. Because the prices are the parent idea's n=83 estimates, 925/4 = 231.25 is numerically that idea's "231 against the measured 235", and this pass adds no information to that comparison. Section 5a: no comparison against rho is made, so no band is owed. The red team's illustrative band (10/21 under uniform 0, 0.1 and 1 GAE weights; 0.119 to 1.905 across corners; 231.25 at the record's prices) shows that any order would be set entirely by the price assumption. No ranking is licensed.

== Limitation

- One deterministic execution per unit; no pcc claim covers 925/4; the audit stays flagged, and its interpreter-parity check was inoperative.
- Computed integers are labelled "measured" in the runbook, the run report and the progress export; the assumed prices are exported in physical units. A correction is ruled (labelling ruling in DEC-20261105-8a9984) and pending as a record.
- Only NEG-1 and NEG-2 discriminate beyond the primary's literal pins. Mutants M5, M7, M8 and M11 pass every assertion.
- CON-3 compares the BSGS worst case with a quantity the parent idea defines as a mean (BSGS mean 25.5, 100.5, 13.0).
- The BL closed form is evaluated outside its regime. Integrality depends on the rounded constant 21/10. The exactness rule has no positive control. Memory is not recorded.

== Next actions

+ *Primary (NA-1).* File one additive correction record carrying the labelling ruling: computed, not measured; the n=83 provenance of the prices; "makes no latency or n=83 statement".
+ NA-2. Tooling handoff: the ICPERF exports of `tools/progress_metrics.py` label the prices as assumed or planted inputs and never use the `ratio` unit for 925/4.
+ NA-3. The `tools/runbook.py` audit defects are covered by the single tooling handoff opened as DEC-20261105-6e2616 NA-1.
+ NA-4. At the next goal rerank, rank the parent idea's zero-compute receipt stage (read the prices from receipts and verify the 235x figure). Any successor instrument adopts the red team's RC-2 to RC-5.
+ NA-5. Top-level session: render, inspect, validate, archive, push, refresh the PR with auto-merge, and checkpoint the goal with one next action.

== Earlier reports and canonical graphs

- Earlier run report: `experiments/EXP-ICPERF-284bc4/reports/run-20261030T1520Z/` (report.pdf, graph.svg, data.json). It is unchanged.
- Canonical graphs checked: `knowledge/frontiers/ecdlp/` (README.md and the generic-rho and index-calculus KR rows; there is no rendered graph source there). No row cites this experiment, its runs, H-ICPERF-2f52d1 or IDEA-20261015-7a3c9e. KR-RHO-ea34b8 is unchanged. No canonical graph changes, because a toy instrument pass moves no frontier.
