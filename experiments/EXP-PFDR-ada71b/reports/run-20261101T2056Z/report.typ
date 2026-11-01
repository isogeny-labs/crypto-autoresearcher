#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: none)

= EXP-PFDR-ada71b run report, session of 2026-11-01

*IDs.* Experiment EXP-PFDR-ada71b (v2 break-even growth ladder), hypothesis H-PFDR-ed7ccf, idea IDEA-20261018-a0830c, goal GOAL-PFDR-fd09e0, executor task TASK-20261101-8951b8 (claim epoch 1, owner `executor-pfdr-ada71b`), approval DEC-20261101-cb3277. Branch `run/pfdr-ada71b-20261101`.

*Outcome.* Of 6 planned trials, *1 output-validated* (selftest), *1 refused by the supervisor* (pilot, `invalid_output`), *4 not launched* (dependency-blocked behind the pilot). Supervisor exit code 3. This report describes outputs; it states no reading of H-PFDR-ed7ccf.

== What ran

Command (repo root): `python3 tools/experiment_execution.py run --plan experiments/EXP-PFDR-ada71b/trial-plan.json --owner executor-pfdr-ada71b --epoch 1`. Plan sha256 `6750eea3…9d7a`; specification sha256 `51753c34…6cb0`; launch authority commit `715df5e6018a`, tree clean (`dirty: false`). Host: Linux cloud container, 4 vCPU, 15 GB RAM, Python 3.13.18; plan defaults workers 4, memory cap 4 GB. Seed blocks: selftest 12900000, pilot 12000000 (main 12100000, replication 12200000 not reached).

#table(
  columns: (auto, auto, auto, auto, 1fr),
  [*trial*], [*run id*], [*wall s*], [*receipt status*], [*note*],
  [selftest], [RUN-PFDR-a4895b], [1.587], [output_validated], [driver and checker exit 0],
  [pilot], [RUN-PFDR-4fa30b], [178.418], [invalid_output], [driver exit 0; checker not run; refused on provenance (below)],
  [census-main], [RUN-PFDR-efce3d], [–], [not launched], [depends on pilot],
  [analyze-main], [RUN-PFDR-2d655b], [–], [not launched], [],
  [census-rep], [RUN-PFDR-b5f267], [–], [not launched], [],
  [analyze-final], [RUN-PFDR-fe2d35], [–], [not launched], [],
)

== Pilot refusal: an operational fault of this session

The supervisor's recorded reason: `driver manifest run.code.commit='a8a4f7b0854c…' contradicts the launch authority's '715df5e6018a…'`. While the pilot was running, this session committed the finished selftest run directory (commit `a8a4f7b085`), which moved HEAD; the driver stamped the moved HEAD into its manifest at completion. The code and inputs did not change between the two commits (a8a4f7b adds only `runs/RUN-PFDR-a4895b/`), but the supervisor correctly treats the mismatch as broken provenance. This is a process fault, not a mathematical result. Per `docs/experiment-execution.md`, the run directory is not reused; a retry needs a fresh immutable run id and additive Coordinator authorization. The pilot directory is preserved unedited.

== Measured values (recorded)

*Selftest (valid).* `selftest_pass: true`. 126 kernel-versus-brute-force coincidence-count checks across bases null, window, gap2, gap3, Z/N, and the four plants (gamma 0, 1/6, 1/3, 1/2), at bits 10–32: every kernel count equals its brute-force count (Figure 1). The selftest also records key-bound, plant-internal and order-certification checks (in `selftest.json`).

#figure(image("selftest-kernel-vs-brute.svg", width: 80%), caption: [Recorded kernel vs brute-force counts, RUN-PFDR-a4895b (n = 126 checks). Points on the diagonal are exact agreement.])

*Pilot (refused; shown for diagnosis only, not usable as input).* `design.json` records 30 cells ok of 30, 40 plant entries, and `curves_planned` 20,151 for census-main under the rule `n = clamp(ceil(1.5·2500/mean_null), 10, 4000)` over 32 pilot curves × 20 null replicates (Figure 2). Recorded per-cell planned curves by rung (two distinct values per rung, one per theta): 16 bits 3167 / 345; 20 bits 1516 / 90; 24 bits 812 / 30; 28 bits 455 / 10; 32 bits 282 / 10. The 20,151 total is the sum of the 30 recorded `n_curves` (derived: a sum of recorded values).

#figure(image("pilot-design-ncurves.svg", width: 80%), caption: [Recorded planned `n_curves` per cell vs rung, from RUN-PFDR-4fa30b design.json (30 cells; status invalid_output, so not an admissible design). The d = 1, 2, 3 lines coincide: the recorded planned n_curves is identical across d for each theta and rung, so only the d = 3 markers are visible.])

== Missing data and next step

No census, analysis, slope or bootstrap values exist from this session; none are reported. The unified export (`experiments/EXP-PFDR-ada71b/export.json`) is not written: no validated measurement rows exist yet. Next step: Coordinator reconciliation of TASK-20261101-8951b8 authorizing a pilot retry under a fresh RUN id (same trial identity, seeds and parameters), then the remaining four trials, with no commits to the working branch while a trial runs.
