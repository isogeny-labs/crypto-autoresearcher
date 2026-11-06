# A9: matched sparse functional evaluation in both solvers

Prospective delegated coordinate-step-4 design, 5 November 2026. This is the first
ranked continuation after A8: isolate the dense functional-evaluation boundary
that accounts for much of its recorded arithmetic difference, by applying the
same sparse rule to both solver representations. This note performs no native
solver mathematics, producer implementation, Git mutation or scientific status
transition. Exact-byte administrative readiness follows the parent implementation.

## Fixed cases and four matched implementations

Use all 288 original A7 curve/schedule/budget/scope row systems, all four observed
curves/bases, their fixed projected columns and 32 public targets. No recollection,
new target draw, revised source schedule or recovered target label enters a solver.
Bind the four original A7 final gzip files and copied public fixtures by immutable
source snapshot, original path, byte hash and copy equality. Bind the four A8 final
gzip files separately as checker-only historical controls. Their outcomes, pivots,
kernels, cancellation rows and weights are not warm starts or solver inputs.

The four implementation arms are:

- `dense_joint`: A8 full joint system with its unchanged dense functional routine;
- `dense_cancel`: A8 cancellation-first system with the same unchanged routine;
- `sparse_joint`: full joint with the support-aware functional routine below;
- `sparse_cancel`: cancellation-first with that identical support-aware routine.

Every arm rebuilds cold for every case: fresh matrix or same-target differences,
elimination, complete kernel, identification, certificate lifting, original-row
verification and public multiplication checks. Projection is shared once per case
and separately paid. This is 1,152 solver calls in one physical panel, not 1,152
new curves or independent target samples. Source schedule, checked budget and
relation/explicit-anchor scope remain paired case attributes, not solver randomness.

## Exact change allowed

Keep the full A8 `CertifiedSystem` reduction, pivot ordering, RHS handling, row
weights, complete kernel construction, representatives, cancellation construction,
lifted original-row checks and public equations unchanged. Change only how
`identify(vector, kernel)` evaluates its syndrome vector vN.

The dense control computes every coordinate product and sum for every kernel
basis vector, including zero coefficients. The sparse routine first scans the
functional vector, reduces coefficients to their canonical Fr representatives
and builds its support in the same coordinate order. Then:

1. If support is exactly one coordinate j with coefficient 1, each syndrome
   component is simply that kernel vector's j coordinate. Record a coordinate
   read and perform no Fr addition or multiplication for that dot product.
2. Otherwise, for each kernel vector, accumulate only support entries using the
   same `f.add(value, f.mul(coefficient, coordinate))` rule. Coefficients equal to
   -1 or other nonunit values use this generic path unless a separately frozen
   change explicitly adds a further optimization. Multiple support entries all
   remain in original coordinate order.
3. An empty support gives one zero syndrome entry per kernel vector, with no
   Fr dot-product calls. An empty kernel gives an empty syndrome vector. Keep
   both cases explicit; neither changes the subsequent row-reduction algorithm.

After constructing the syndrome, use exactly the same row dictionary, reduction,
RHS and certificate logic as A8. Do not return early merely because the syndrome
is nonzero, omit kernel vectors, use incomplete kernels, change unit queries to
another basis, skip unsuccessful targets or reuse another arm's identification.
Apply the same rule to both solver representations, including representative
functionals that happen to be units in the cancellation-first solver.

The full joint query for target t is the positive unit vector at U+t. The
cancellation-first query is the selected original target representative vector,
after fresh cancellations from all target groups. Missing target groups retain
the same explicit unidentifiable records. Original target coefficient -1,
scalar offsets and lifted certificate signs remain those specified in A8.

## Exact controls and independent checks

For every original case and both representations, dense A9 must reproduce A8:
all input rows/order, system summaries, complete kernels, identified flags,
syndromes, values, reduced and lifted weights, scalars, cancellation metadata,
phase order and Fr/Fp/logical operation vectors. Ignore only diagnostic clocks
and explicit new arm/mode labels when comparing; do not mask changed arithmetic.
No precomputed A8 value can be read before the new solve as a shortcut.

Within each representation, sparse and dense must have byte-equal algebraic
outputs, including complete kernels, original-row certificates and scalar values,
after excluding only phase clocks/counters and explicit mode metadata. A valid
alternative certificate is insufficient for this control: the change should
leave the same reduction path and weights. Across full joint and cancellation-
first representations, certificate weights/kernel widths need not be identical;
both must independently satisfy the same original joint target-unit equations.

Use the separate plain projection and dense affine rank/consistency/full-kernel/
unit-identifiability oracle. Independently verify every lifted coefficient and
RHS on the original rows and every public [k]P = Q equation. Keep the A7 outcome
control as well as the stricter A8 dense implementation control. The independent
oracle must not adopt the producer's sparse evaluator as its only truth source.

The expected arithmetic change is restricted to the identification phase's
syndrome evaluation. All construction, elimination, kernel, lifting, original-row
verification and public-check Fr/Fp vectors remain identical between modes of
one representation. Retain per-case and per-phase differences, including adverse
results or unexpected non-identification changes. Validate new logical counters
by the actual support/kernel dimensions; conservation alone is insufficient.

Software controls include deterministic A/A, unit and nonunit single support,
several support entries, coefficient 0 and canonical -1, zero-width/zero-vector/
empty-kernel systems, absent targets, deficient-rank recovery, a failed functional
that still follows the same reduction, malformed width/encoding, dense control
mismatches, false sparse syndromes/logical counts, lifted coefficient/RHS/kernel
corruptions, public checks, no-admission refusal and immediate completed-arm/failure
retention. Retain all tests as marked synthetic/tiny controls, separate from the
native retained-row panel.

## What is counted and what remains outside the measurement

Both modes use the same distinct Fr add/sub/mul/inv API counters, including all
RHS, reduction, weight and original-row checks. Keep shared projection, every
cold solver stage, public Fp/group checks, separate verifier diagnostics and
whole-process resources separately owned. Do not replace four primitive units
with an invented weighted scalar, isolated timing advantage or complete S.

Sparse mode additionally records logical work such as functional coefficients
scanned to build support, support entries retained, generic support/kernel visits
and direct kernel-coordinate reads. Define each count precisely: a scan is not
an Fr multiplication, and a coordinate read is not a complete memory/CPU cost.
Keep support-building cost visible even if the kernel is empty. Dense modes do
not instrument these sparse-only metrics; omit them or label them unmeasured/
not applicable, rather than reporting zero as if dense evaluation did no scans.

Skipping zero Fr products and reading unit coordinates can change logical API
call counts while Python branching, dictionary/list allocation, traversal,
integer reduction, serialization, OS and inversion internals remain unpriced.
The broader research objective still needs an independently checked complete-cost
comparison against the strongest implemented matched baseline and fresh holdouts;
this fixed-row component experiment does not substitute for those requirements.
Its scoped question is whether representation differences persist when both
implementations use the same functional sparsity rule.

All 288 old systems remain even when full-rank, empty or adverse. The 32 targets
are reused across schedules, budgets, scopes, representations and modes; repeated
recovery slots are not new target samples. No rank, recovery or cost result
changes the fixed case list or stopping rule.

## Input custody, records and execution boundary

Keep the original A7 rows and public fixtures as solver data, and A8 raw solver
files as checker-only controls. Record their immutable source commits and gzip
hashes in the input manifest; hydrate exact bytes before admission. Never use
an earlier source/checkpoint/tool hash map as the new one: protocol/checkpoint
scripts and their imports have changed in current main and must be bound by
current `common.SOURCES` and actual input dependencies.

Retain every case input and shared-projection record, each completed solver arm
immediately, and any failed arm's partial phases/counters/result before propagation.
Preserve the A8 failure-retention repair. Save new solver outputs before independent
historical/dense controls can fail. Missing/censored work remains unknown, with
finalized coverage stated. Original and gzip hashes, S3 locations, literal statuses,
command/interpreter/packages, owner and resources remain in the export.

Use four protocol arms and 288 paired instance labels for 1,152 rows, deterministic
metadata seed 0 throughout. Exercise actual export lint, including wrong ID/seed
controls, rather than only schema validation. Shared costs occur once per case;
arm/mode totals refer to actual cold calls and must not duplicate inclusive process
or checker costs. Parent appends the v12 database while preserving v11 and all
historical rows. Immutable raw publication precedes report/observation sidecar,
graphs, inspected PDF, final benchmark/progress custody and PR/S3 publication.

Only one existing workstation process/thread is covered: 2 GiB address space,
21,600-second CPU/wall watchdog, one attempt, no automatic retry and no new paid
capacity or EKS/IsoLab submission. Keep the 4,096-original-row and width-64
protective gates, preserving failure prefixes rather than truncating controls.
Unknown account allowance does not authorize new paid resources.

Parent owns exact GitHub source/input/configuration/command publication, fresh
prospective protocol freeze on the actual source revision, real current S3
checkpoint/gate and explicit exact root release before native mathematics through
run. No A8 release authorizes A9. This delegation claims no native result,
verified model/provider/probe, independent staffed scientific review, full-ledger
pass, official status transition or completion of the broader research goal.
Exact-byte administrative assessment follows the completed implementation.

## Exact prospective implementation inspection

Read the new core, common dependency/input bindings, admitted driver, checker,
protocol builder, supervisor, compact exporter and software controls. Sparse
`identify` changes the support/syndrome path only and calls the inherited
reduction unchanged. Dense replay, semantic/kernel/certificate equality, cold
per-arm reconstruction and immediate result/failure journaling remain explicit.
The compact export omits redundant row-level counter payloads only; complete
phase vectors remain in raw data and backend arm/phase totals. Dense sparse-only
traversal is displayed as unmeasured, not zero.

Direct metadata testing passed: one test in 0.23 seconds exercised the actual
1,152-row export identity/seed interface and corruptions without solver calls.
All 24 dependency paths exist; the current builder has zero schema/lint findings
and all 1,152 seed-0 cells match. Copied fixtures match original source bytes,
and all eight original/control gzip hashes and sizes match their pinned Git
artifact manifests. A8 control data is read only for checks after new results.

The first inspection found a validation gap: only coefficient-scan logical counts
were independently checked, while other new traversal counts and unchanged
identification counters could pass a matching phase/total mutation. Before final
approval, require support/kernel-derived visits/coordinate counts, exact preserved
non-add/mul identification counters, and exact expected add/mul changes. This
refines the planned cost controls and is not a mathematical result or native run.

## Final administrative readiness

Parent repaired the prospective cost-control gap before native execution.
The checker now reconstructs canonical query supports from the case and validated
arm identity, checks all four traversal counts, and derives the identification
add/mul difference as dense dot visits minus sparse generic visits. It requires
every other identification counter, including Fr sub/inv, and every other phase
counter vector to remain unchanged. New matched phase-plus-total corruption
controls cover support entries, coordinate reads and identification sub/inv.

The final saved preparation record reports 50 software controls passed in 1.40
seconds, including four-arm equality, valid public checks, third-arm failure
retention and cost corruptions. This delegate directly ran only the metadata test
noted above; it did not rerun the scientific software suite or native row panel.
The final draft has zero findings, and all 1,152 metadata seed-0 cells match.

The exact 24 source dependencies and all explicit/content-addressed input hashes
are bound in admission-assessment.json. Administrative approvability grants no
execute authority or scientific state change. Parent must still publish those
exact bytes, freeze against the actual published source SHA, obtain the real
current S3 checkpoint/gate and publish the exact root release before native
mathematics. Bound byte changes require additive reassessment. The KB backend
remains unavailable; only the documented direct-source fallback was used.

The parent subsequently committed exact producer/dependency bytes as
`2df9510e016c5795ae8d47f5826031f70e567616` and saved a final rerun of
50 software controls passing in 1.25 seconds. The earlier 1.40-second pass was
also observed; the current preparation-file hash in the assessment binds the
newer run. Read-only committed-byte bindings were checked successfully.
Publication verification, prospective freeze and execution release remain
parent-owned conditions.
