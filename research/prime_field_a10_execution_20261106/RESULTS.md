# Fresh AP/hash source holdout

**Proof standing:** these panel observations are an unverified producer assertion,
recorded as `PCC-20261106-028bb6`; signed independent replay/recomputation and
execution coverage are absent. The local scalar-certificate pass for
`PCC-20261106-6f9635` has unverified standing and covers only the public toy
scalar equation. See [proof-status correction](PROOF-STATUS.md). [pcc:unverified]

The panel completed **432 paired row systems and 864 cold kernel-free solver
evaluations**, on four fresh curves and 32 fresh public target points. Both
solvers agree on every target outcome and scalar; all original-row, public-group,
negative-residual and dense-rank checks pass. One attempt, no rerun, zero unknown
cases. [Raw analysis](runs/a10-ap-holdout-276654/analysis.json),
[derived observations](observations.json), and the
[three-page inspected report](reports/a10-ap-holdout-276654/report.pdf) retain the
full finite comparison, including adverse outcomes.

A concrete natural-target example is `p8191-i0/ap0/prefix16/relations`: target
index1, point `(7855,3278)`, scalar7274, source rank6/14 and rank6/14 after target
cancellation. Its certificate uses two original equations. The target is absent
from the recorded constructor-point cache at this prefix. This establishes the
specified row-space recovery on this fresh input; it does not exclude other
public shifted-point shortcuts or establish novelty. The exact target,
certificate, immutable raw hash and cold panel-prefix cost vectors are in
[observations.json](observations.json).

## Panel and controls

| Curve | p | b | Prime order | Native atoms | Fixed projected columns |
|---|---:|---:|---:|---:|---:|
| p8191-i0 | 8191 | 8090 | 8233 | 16 | 14 |
| p8191-i1 | 8191 | 2681 | 8363 | 16 | 16 |
| p65537-i0 | 65537 | 38058 | 65213 | 32 | 31 |
| p65537-i1 | 65537 | 61540 | 65633 | 32 | 32 |

[Rules](inputs.json), [protocol](protocol.json), [design](design.md) and
[literature](literature.md) were published before generation. Separate domain
tags select curves, eight canonical-y target points per curve, AP start/step,
and hash sources. The eight enumerated A4/A6 curves are excluded. All147curve
candidates and their rejections remain; the separate generation checker reports
7,397,445 order point tests. Freshness is scoped to those exclusions, with no
corpus-wide absence claim.

Each curve uses AP/hash seeds0/1/2 and128sources, budgets
0/8/16/24/32/48/64/96/128, relation-only and explicit-anchor scopes, and both
joint and cancellation-first solvers. These are dependent views of four curves
and32target points. Shared1..64 public prerequisites use63walk additions per
curve. Projected columns remain fixed. Additional constructor/base matches and
direct target matches are explicit equations only at their first paid prefix.

The constructor policy compares actual binary and repository positional
FixedBaseMultiplier windows1..8, minimizing scalar-only group-add API calls
with deterministic ties. It charges nine integer simulations and runs one
selected EC constructor. All table/intermediate/APstep/walk points, exact-label
cache hits, sign negations, base/target scans and storage are recorded. No other
arm's or future prefix's constructed point enters a scope.

Physical collection: **147,456 source queries, 1,536 target queries, 4,928 pair
entries**, with all misses/buckets and1786source witnesses retained. The
independent signed-triple oracle enumerates88,320triples once over the four
curves. Fifteen natural target equations cover11of32public target points;
coverage is an explicit remaining bottleneck.

## Observations

Across216matched AP/hash curve/seed/prefix/scope comparisons, AP identifies more
targets in10cases, hash in37, and counts tie in169. AP source rank is higher in43
cases, hash in56. No curve, seed, miss or unfavorable case was discarded.
At128sources the selected AP window is1 and hash windows are5/6; constructor
API-call ranges are151–164 and426–526 respectively. These are separate component
counts, not a weighted or end-to-end advantage claim; all fields and query costs
remain available per prefix.

Both solvers identify605repeated target slots:292in relation-only scopes and313
with explicit anchors. Those are not605independent targets. Outside-adjusted
Delta is positive in64relation-only and67anchor cases.

| Scope | Recovery while source rank deficient | Recovery while rank remains deficient after target cancellation | Latter cases with a target absent from recorded direct constructor matches |
|---|---:|---:|---:|
| Relations | 29 | 24 | 23 |
| Anchors | 38 | 32 | 23 |

These tests use direct row-space reduction and complete certified echelon spans.
Neither production solver builds a full kernel. Independent dense membership
and residual checks cover unrecovered targets as well as positive certificates.

| Logical Fr primitive, all432cold calls/method | Joint | Cancellation first |
|---|---:|---:|
| add | 35,920 | 35,965 |
| sub | 700,348 | 706,961 |
| mul | 786,587 | 764,255 |
| inv | 7,970 | 6,774 |

Totals include construction/cancellation, elimination, identification, original-row
lifting/verification and public checks. Shared projection stays separate and is
charged once per system. Counts in different primitives, Fp/Fr fields, or
 overlapping group operations are not combined into scalar-equivalent work.
The complete vectors preserve mixed and adverse component outcomes.

## Custody, cost coverage and limits

Scientific source `dfb7f95697a334223e79d6432de1f3de60738e60` binds52source and4input
files. Frozen protocol SHA
`7f7bb92d8f6793e0ae0d57522f468e9d2d5efcb6ec6b24fa3fcfd9f2bd4182db`;
run `a10-ap-holdout-276654`; observed launch head
`122777cdbec927ef59ce40da0ea737d2719f21ab`. Actual S3 custody, explicit release and
normal admission preceded native work. Raw commit
`4b75db9c4a133f56c3d0e97e30007129faec9fc6` was pushed **before** report rendering.
The [unified export](runs/a10-ap-holdout-276654/export.json) passes
`check-export --verify-files` with zero findings. Thirteen lossless raw encodings
and the report/database are in the official store:15remote entries, zero
verification problems. Restore with `artifacts pull`; encoding receipts bind
all original bytes. No previous report, protocol or closed raw record changed.

One existing worker/thread,2GiB,21600CPU/wall-second watchdog, one attempt;
no new paid compute. Actual inclusive child user/system CPU
27.469328/1.788709seconds, diagnostic wall29.237755809seconds, peak RSS96,124,928bytes.
Shared-host clocks are not isolated performance measurements. An in-flight S3
checkpoint tar noticed a changing journal and failed; its receipt is retained,
and a subsequent closed-run checkpoint succeeded. Native work was not retried.

New collector/solver Fp/Fr add/sub/mul/inv counters are split. Legacy fixture
construction merges subtraction into field_add, and some rejected-fixture,
inversion/pow/hash/sort/Python/IO/checker internals are not primitive-expanded.
Candidate traces and inclusive CPU remain distinct. Cold prefix vectors include
the experiment's shared setup, including allsixsource-recipe derivations; this
can overcharge a deployment choosing one arm. Query/checker intermediate points
are outside the supplied constructor cache, an operational boundary rather than
secrecy. Complete calibrated attack costs remain unmeasured.

Forty relevant software/metadata tests pass (1.79seconds). The committed-only
exporter emits7,996new measured samples with explicit scope/units.
Full-ledger validation refused the sparse checkout (114862tracked files off
disk); no full-ledger pass is claimed. Administrative readiness and independent
software checks are distinguished from staffed scientific review, model
verification and execution-proof settlement, none of which occurred here.

The [v13 database receipt](database/v13-ap-holdout/generation-v13.json) verifies
unchanged parentv12bytes, every inherited row, foreign keys, SQLite integrity and
lossless gzip. It adds4curves/32fresh targets/432cases/864solver certificates and
6746labelled-point records. Combined history:14curves,14bases,15executions.
No canonical mathematical graph edge changes from these component observations. [pcc:unverified]

The [next worklist](next-leads.md) ranks matched paid target translations against
optimized randomized offsets on fresh holdouts, identifies the existing general
`aP+bQ` implementation as a broader baseline, and retains the Dickson/Prym/
outside-point continuations. This note records observations, not an official
scientific status transition or a novelty claim.
