# A11: affine target queries and general outside cancellation

The single frozen attempt completed all 1,152 row systems and 2,304 cold solver
calls on four fresh synthetic curves and 32 fresh public targets. Both methods
returned the same target identities and scalars, with original-row/public
certificates and separately coded dense/oracle checks. Zero systems are unknown.
These are producer observations: `PCC-20261106-70a1b5` and
`PCC-20261106-648bb8` have unverified standing, without independent signed
replay/recomputation. [pcc:unverified]

At eight queried endpoints per target, every policy recovers all eight targets
in each of the 48 source-schedule/prefix views. The 384 slots below reuse the
same 32 target points. Early-budget behavior and construction cost differ:
[pcc:unverified]

| Policy | Relations slots at budgets 1/2/4/8 | Anchor slots at budgets 1/2/4/8 | Target construction EC adds at budget 8 |
|---|---|---|---|
| Consecutive Q+jP | 174 / 275 / 360 / 384 | 196 / 276 / 360 / 384 | 2,688 |
| Hashed Q+alphaP | 174 / 311 / 336 / 384 | 196 / 325 / 348 / 384 | 8,537 |
| General alphaP+betaQ | 174 / 260 / 336 / 384 | 196 / 348 / 368 / 384 | 28,116 |

Construction totals sum 48 cold many-target branches per policy, each sharing
one paid P table across eight targets and using only its own source cache.
They include uncached scalar EC additions and endpoint additions, with wrapper,
selection, sign, lookup and storage counters separately retained. Source/query,
projection, solver and independent checker costs remain separate; this table
alone is not an end-to-end comparison or a weighted speedup. General aP+bQ is
an existing baseline family, not a new symmetry. [pcc:unverified]

The solvers each identify 7,317 dependent target slots across all budgets,
policies and knowledge scopes. Their complete solver-phase totals, including
lifting and checks, show an inversion-versus-other-work trade-off:
[pcc:unverified]

| Fr unit | Joint raw U | Outside first |
|---|---:|---:|
| additions | 456,714 | 602,296 |
| subtractions | 6,703,275 | 7,199,490 |
| multiplications | 6,415,404 | 6,850,637 |
| inversions | 4,952 | 4,762 |

No weighted overall solver winner follows from these vectors. Both methods
use symmetric unit-sign pivot shortcuts and avoid a full production kernel.
The outside method pays general U elimination, sparse cancellation weights,
base-functional reduction and lifting back to original rows. Delta always
subtracts outside-column rank; base columns remain fixed. Recovery with the
base still deficient after target cancellation occurs in some early-budget
views; at budget8 it remains in two hashed-offset views per knowledge scope.
It is not attributed to a new mechanism without excluding recorded direct
and intermediate affine coincidences. [pcc:unverified]

The physical collector issued 147,456 signed source queries and 33,728 signed
target queries, with 4,928 pair insertions and 702 cached endpoint points.
There were 9,216 logical target requests across repeated source branches.
Coordinate aliases account for the reduction from the 704 formal endpoint
expressions. CPU user/system was 283.158592/8.522576s, diagnostic wall
294.757356401s, peak RSS160,694,272bytes; clocks are unisolated. All four
closed-curve canonical S3 checkpoint receipts were retained. [pcc:unverified]

Code source: `26d24174c4cc079d8318c87ab82a9686f121b9bf` (65 source/four input
bindings). Frozen protocol canonical hash:
`2c1ce7e6ab833a5491ae2583b60d5c91f82c5fe6e6d89fa1b6ddafdb3c210b6b`.
Native run: [a11-affine-holdout-30245e](runs/a11-affine-holdout-30245e/execution.json).
Raw commit `e23280b606dd0802226d50edb912bbd59cdfa124` was pushed before report
rendering. The [three-page report](reports/a11-affine-holdout-30245e/report.pdf)
was inspected on every page. The unified export passes file-hash checking;
30 raw/derived S3 entries passed the official remote storage check. These are
producer custody checks, not execution proofs. [pcc:unverified]

[Database v14](database/v14-affine-holdout/generation-v14.json) preserves the
parent v13 bytes and historical rows and adds four curves,32targets,144target
branches,74,291affine-label records,702query records,1,152cases and2,304solver
certificates. History now contains18curves/18bases and16physical execution
records. Foreign keys, SQLite integrity and gzip roundtrip passed locally.
No historical failed or invalid run was removed. [pcc:unverified]

The 48 tiny software controls passed locally in1.07s; separate committed-only
A10/A11 metric controls passed in1.68s. Whole-ledger validation refused this
sparse checkout because114,831tracked files are off disk; no whole-ledger pass
is asserted. Legacy fixture/rejection, pow/inversion/hash, checker/Python/OS/IO
internals are not fully primitive-expanded. Full calibrated cost and signed
independent replay remain dependencies. The [next worklist](next-leads.md)
keeps the campaign active; this finite batch is not goal closure.
[pcc:unverified]

To inspect from a fresh checkout, pull the official artifact manifests under
this study. Decode the retained `analysis.json.gz` and `export.json.gz` into
their ignored logical JSON names before `check-export --verify-files` or a
database rebuild. These are lossless hydration steps, not new experiments.
Do not rerun the consumed one-attempt native release.
