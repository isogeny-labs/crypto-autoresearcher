# Next bounded test: paid affine-target translations after A10

Prospective worklist only, 6 November 2026. No protocol, approval, new experiment
record, official status, native execution or producer change is made here.

## Rank one action from the committed observations

Test incremental public translations `R_j=Q+[j]P`, j=0,...,7, at fixed per-target
query budgets 1/2/4/8, using both kernel-free joint and cancellation recovery.
Match them against independently hashed public offsets `Q+[rho_j]P` at the same
budgets, with rho_0=0 and a prospectively frozen distinct-offset recipe. Use the
optimized charged constructor portfolio for that reference, not repeated naive
scalar multiplication. Keep AP and optimized-hash source schedules and the
source prefixes 64/128 as matched factors; do not choose a source winner from
A10 and discard the other. The question is whether extra target rows deliver
useful outside-adjusted information/recovery at their full paid cost, and whether
consecutive offsets differ from same-budget affine randomization. More queries
alone are not evidence for a special translation mechanism.

Evidence is the committed A10 run `a10-ap-holdout-276654`, raw snapshot
`4b75db9c4a133f56c3d0e97e30007129faec9fc6`, source
`dfb7f95697a334223e79d6432de1f3de60738e60`. Its analysis and collection snapshots
were read directly, without re-running arithmetic:

- All 432 row systems and 864 kernel-free solver outputs passed separate checks;
  source was unchanged, exit0, no timeout and zero unknown cells.
- The natural j=0 target stream has only 15 rows for 32 fresh points: 2/5/2/6
  across the four curves. Both solvers identify 605 target slots over dependent
  views, not 605 independently drawn targets. There are 131 positive-Delta
  systems and 67 systems with recovery while source rank remains deficient.
- Across 216 matched AP/hash seed/scope/prefix pairs, AP has more identified
  targets in 10, hash in 37 and counts tie in 169. Source rank is higher for AP
  in 43 and hash in 56. These aggregates include different anchor information;
  they do not isolate a causal reason for the differences.
- AP's full-128 construction uses 151..164 group-add API calls; hashes use
  426..526, with selected AP window1 and hash windows5/6. These are exact local
  counts, not weighted field costs, runtime advantage or a full-attack saving.

The low number of natural target decompositions makes target-query coverage a
more discriminating next intervention than another source-only budget sweep.
A10's successful kernel-free controls remain the solver baseline, including
lifting and public verification. No regression to dense/full-kernel methods is
needed to make a candidate look favorable.

## Known method and exact target semantics

The production IC solver already constructs `aP+bQ`, with lazy charged fixed-base
P/Q tables (`src/crypto_autoresearcher/index_calculus/solver.py`, around lines
206..222; `targets.py`). Consecutive translations are the standard b=1 slice,
not a newly discovered symmetry or attack. The hashed-offset reference keeps
b=1 too, permitting a controlled constant-target-coefficient comparison. The
optimized general aP+bQ implementation remains a broader comparator before any
claim against the strongest whole solver; this bounded test does not establish
that comparison or a rho gap.

Every translated point has an unknown affine label `(target_id,1,j)`, not a
known public scalar. If its base decomposition is `v*z+known=q+j`, the recorded
partial equation is `[v,-1]*(z,q)=j-known (mod r)`. Hash-offset rows use rho_j
instead of j. Independently check both the public group equation and this RHS
sign. Charge offset subtraction/normalization rather than silently reusing the
j=0 RHS. Do not introduce a new unrelated unknown for every translated point.

Retain all individually nonidentifiable target rows and cancel target columns
using carried weights. Score
`Delta=rank([[M,0],[B,U]])-rank(U)-rank(M)` on the unchanged original base columns.
Test target unit functionals before requiring full base rank. Differences for
the same target cancel its -1 column, but their differing offsets remain in the
RHS. Both solver representations must use the same supplied rows and retain
original-row certificates, negative residual checks and public [k]P=Q checks.

Affine points must never enter the known-scalar source cache as though q were
known. If Q+jP equals a paid known point [k]P, record the explicit public target
equation q=k-j and its cost. If it is identity, retain q=-j as a labelled direct
public coincidence. If two targets' affine points coincide, retain the implied
public target-difference equation with correct offsets, or prospectively isolate
it as a diagnostic; never turn it into a fabricated individual scalar label.
No such coincidence permits target replacement or a success redraw.

## Proposed scope and matching controls

Use a new frozen domain and four new rule-selected curves at the existing
8191/base16 and 65537/base32 sizes, with eight new canonical-y public targets
per curve and the same three paired AP/hash source seeds. Bind explicit prior
A4/A6/A10 curve exclusions; freshness is within that stated list, not a global
absence or independent-isomorphism-class claim. No relation/rank/recovery enters
selection. Generate only after exact source/rules are published and prospectively
frozen. An old-A10 replay, if needed for debugging, is a conditioned diagnostic
with separate costs, never another independent holdout.

Collect one full source stream per schedule through128, retaining prefixes64/128.
Use relation-only and explicit paid-known-point scopes, constant projected base
columns, one pair table per curve and the same fresh target points in all arms.
Construct translated points incrementally, and query all scheduled offsets even
if a target is recovered early. Reuse a j=0 decomposition shared by both offset
policies through an explicit cache; retain request counts, actual lookup work,
cache costs and every alias so logical budgets are not mistaken for independent
physical executions. Source schedules and solver views do not recollect the
same target stream.

Original-window and constructor-derived base/target anchors retain their exact
paid prefix availability. Offset-reference P tables and other known labelled
intermediates may supply additional anchors; retain their full construction,
scan/storage cost and information instead of hiding them. Other-arm/future or
checker-recovered labels cannot enter a chosen operational prefix. The boundary
is declared computation/knowledge availability, not secrecy of public recipes.

Use a separate complete signed-triple oracle once per curve to check every
requested affine target and every pair/query miss, not only successful rows.
Independent group arithmetic must reconstruct all point additions and offset
recipes; independent dense affine checks must validate cancellation, rank,
residual nonmembership, coefficient/RHS weights and final original-Q recovery.
Tiny controls should include j=0 equality to the old target path, corrupted
j/RHS/sign/target index, missing query, identity, public/cross-target collisions,
JSON roundtrips, duplicate cache references and future-knowledge refusal. These
are proposed controls, not controls executed by this note.

## Cost, stopping and interpretation

Charge fresh generation and rejections; shared public prerequisites and table;
AP/hash source selection/construction/collection; offset recipes and constructor
selection; target translation and sign work; all query failures/extraction;
projection/normalization and explicit anchors; cold elimination/cancellation;
certificate lifting, original-row checks, public checks and collision scans;
cache/storage/IO and separate checker work. If a direct-E path performs no
cover lift, label that stage not applicable rather than invent a zero-cost
implementation of a different geometric extractor. Any actual lift is paid.

Keep Fp/Fr add/sub/mul/inv, group calls, logical requests/scans and byte counts
separate. Preserve A10's explicit legacy-generation merged-subtraction and
unexpanded rejected-fixture/pow/IO/checker limitations; process CPU/wall/RSS
retain inclusive scopes. A complete retained phase record is not a calibrated
weighted S. Give cold single-arm and actual physical-panel totals without
summing nested budgets, shared phases or solver views twice. Shared-host wall
clocks do not establish an isolated timing speedup.

Stop at the frozen source prefixes and maximum target budget8, not at success.
A cap, bad certificate, watchdog or execution failure retains all observed
rows/points/phase counters and marks unrecorded work unknown; no truncation,
selected replacement curve/target or automatic retry. One existing local
worker/thread, 2 GiB, finite 21600-second CPU/wall ceiling and one recorded
attempt remain the proposed machine limits; no new paid capacity is implied.
Any eventual run needs its own fresh absolute deadline, exact freeze, actual
S3 custody and explicit root release. This note grants none of those.

If budget8 adds no useful rows/Delta/recovery, retain the finite coverage result
and do not expand offsets under that contract. If recovery increases only with
more queries or direct public collisions, attribute it accordingly. If offset
policies differ after paid construction and matched source knowledge, the next
decision is whether a separately frozen larger-field/cold-cost comparison is
justified. No novelty, guaranteed improvement or automatic goal completion
follows from either outcome.

## Original leads remain open within their actual evidence

| Lead | What has actually run | Remaining bounded question and pointer |
|---|---|---|
| Outside-point partial cancellation | A1 independently checked Delta2/6 on the two original p4099 curves; A2 later admitted any norm-cancelling pair without a pool. | Complete scalable collection/elimination cost and fresh-curve behavior remain open: [A1 results](../prime_field_a1_execution_20261030/RESULTS.md), [A2 results](../prime_field_a2_execution_20261030/RESULTS.md) and [cancel_outside](../../src/crypto_autoresearcher/index_calculus/relation_quality.py). Target-column partials here do not replace outside-point pool work. |
| Isolated Prym x=0 | B1 completed all four cells; additional witnesses gave zero new distinct equations/rank/kernel directions on those fixtures. | Do not rerun it as unexecuted or infer universal failure. Broader exceptional-source/cover questions need a new fixed mechanism: [B1 results](../prime_field_b1_execution_20261029/RESULTS.md). [B2 results](../prime_field_b2_execution_20261030/RESULTS.md) retains matched shifted-cover gains with partial cost coverage; its scalable/target behavior is still open. |
| Dickson depth4 | C1's seven fixed P256 cases completed with guard560 and full finite oracle; constructed positives had one solution, fixed public-generator queries zero. | Repeated-coordinate native positives, matrix-free/scaling extraction and matched signed-decomposition cost remain open. See [C1 report](../prime_field_c1_execution_20261029/reports/c1-fixed-panel-4f8ab9/report.typ) and [symmetry/C1 record](../prime_field_symmetries_20261029/README.md); FLINT internal operations were unmetered. A size guard is not a universal method lower bound. |
| Natural target recovery | D1 completed, but bounded public-multiple coincidences explain its isolated successes. A10 supplied fresh targets, joint recovery and full retained local vectors. | Paid affine reuse with independent fresh targets is the ranked test above. [D1 results](../prime_field_d1_execution_20261030/RESULTS.md) and A10 raw analysis preserve both limitations; old preparation plans saying these runs are unexecuted are historical. |

These are pointers and priorities, not closure or status transitions. No full
search round was performed. The research-kb outage/direct-source fallback from
A10 literature remains in force; no source IDs, corpus freshness, absence or
novelty is invented. Primary PKM2016 section3.2's earlier cost-separation reading
is carried, not a new paper retrieval. Sources checked for this note are A10
committed analysis/collection/execution, the production affine-target code,
C1 native report, B1/B2/A1/A2/D1 RESULTS and the original four-track PLAN.
