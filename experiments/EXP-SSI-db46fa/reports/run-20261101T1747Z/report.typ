#set page(width: 15cm, height: auto, margin: 1.6cm)
#set text(size: 9.5pt)
#set par(justify: true)

#align(center)[
  #text(size: 15pt, weight: "bold")[EXP-SSI-db46fa — run report]
  #v(0.2em)
  Run `RUN-SSI-989893` · trial `orbit-deficit-p19` · 2026-11-01
]

#v(0.4em)

*Experiment.* Toy Galois-orbit deficit census of membership j-invariants in
$F_361$ (`p = 19`, `F_19[z]/(z^2 - 2)`), hypothesis `H-SSI-bff8d9`.
Frozen plan `experiments/EXP-SSI-db46fa/trial-plan.json`, sha256
`287aa0c3…6e90a`.

*What ran.* One trial, one process, the plan's argv verbatim: the driver
wrote `manifest.yaml` and `raw-result.json`, then the independent checker
ran on the run directory. Wall clock 10.54 s; driver and checker both exited 0;
the supervisor recorded `status: output_validated`.

#v(0.4em)
#figure(
  image("chart.svg", width: 100%),
  caption: [Recorded metric values from `raw-result.json`. The bars are the
  recorded numbers, not a comparison or a test.],
)

#v(0.2em)
#table(
  columns: (auto, auto),
  align: left,
  stroke: none,
  [*Metric*], [*Recorded value*],
  [`size_S`], [2],
  [`O`], [2],
  [`D`], [0],
  [`deficit_F19`], [0],
  [`deficit_instrument`], [1],
)

#v(0.4em)

*Controls reported by the driver.* `deficit_F19 = 0` on the same-shape null;
`frobenius_sends_z_to_minus_z = true`; `z_squared_is_2 = true`;
`roundtrip_ok = true`; `routes_agree = true`; `duplicate_ok = true`;
`twist_only_memberships = 0`; `roundtrip_failures = []`.

*Custody.* All nine declared artifacts and their SHA-256 values are in
`execution-receipt.json`; the release binds ten artifact hashes. The plan,
specification and source files were committed before launch
(`b78f54c1e7`); the run directory is committed after.

*Scope.* This report states what ran and what the run recorded. It contains
no verdict, no support or weakening, and no significance claim; those belong
to `/review-evidence`.
