# A8: cancellation-first versus full joint target recovery

Prospective delegated administrative design, 5 November 2026. The user selected
this next component comparison after A7. It is ranked first in this bounded
continuation because A7 found joint target recovery at a lower checked source
budget than isolated natural rows, and already retains the original rows needed
to compare two implementations of that same joint information. This design
performs no native mathematics, producer implementation, Git mutation or official
status transition. Exact-source readiness will be assessed after implementation.

## Immutable inputs and matched cases

Use all 288 A7 curve/schedule/budget/scope systems, without recollection, new
curves, new targets, new source selection or import of recovered scalar labels.
The reviewed parent snapshot is main commit
`5440a26b36693841b89fc803baf73d4061df4826`; raw-data publication provenance also
names `6673f55a98184593e96594fd8a0e9c1bf3702ae3`. Bind both roles explicitly.

The input manifest references the exact four compressed A7 final records and
the copied original public-fixture input with its original path, hash and source
commit, plus the local copied-file hash. Verify those original/public fields
match the retained parent bytes. Artifact hydration is byte retrieval, not
scientific regeneration. The four final gzip hashes in the pinned manifest are:

| Fixture | SHA-256 of final JSON gzip |
|:--|:--|
| p8191-i0 | `14eedcccd9ce4f53f234077de29fa96eedd7a3ce3d81a15ab29815037dd2cd20` |
| p8191-i1 | `296d00d50a5349f6af845d303b14f7d7b0d7cda1f8bfe7b0c43cfcafc706d718` |
| p65537-i0 | `c583d418c0133ed57539b2d617ed3d996157f83ec33cbd1d3e9f296a669c0287` |
| p65537-i1 | `49700268f115b0a229c78cb96c36032f4797ce001c396245a303d441ec8005fc` |

Each case keeps its exact curve/base/generator, fixed projected width U, eight
public target points, source schedule, checked budget and relation/anchor scope.
Extract source rows M and RHS a from original witnessed source rows plus only
that scope's legal prefix anchors. Extract natural target rows from the original
target witnesses and fixed projection. Do not feed either solver saved A7
cancellation rows, solved scalars, kernels, pivots, rank summaries or row weights.
Saved results may be read only by the independent checker/control after the new
solver records have been retained.

Keep original row order, duplicates and affine offsets. Projection is an explicit
shared cost; declare whether performed per case or cached at a broader input
scope, with the physical work counted once. Both solver arms receive identical
projected rows. No method gets a deduplicated or selectively filtered matrix
unless the same transformation is prospective, shared and charged.

There are two solver arms, `full_joint` and `cancellation_first`, giving 576 cold
solver executions on 288 paired cases in one supervised physical panel. These
are not 576 independent curves or experiments. All 32 old targets remain fixed;
repeated slots across schedules, budgets, scopes and solver arms are dependent.

## Exact row convention

Work over the prime subgroup field Fr. A source system is M z = a on U fixed
base columns. Natural row i for target t is

`v_i z - k_t = b_i`.

Thus its original joint coefficient row is `[v_i, -e_t]`, with RHS b_i. Every
natural row carries exactly one target index and target coefficient -1. Reject
unsupported coefficient encodings or explicitly normalize them in a separately
frozen, metered extension; never apply the difference formula silently to
unequal coefficients. Invalid or inconsistent affine systems are failures,
not target-recovery outcomes.

The original joint order for certificate verification is all source rows M,
then all original target rows. Keep that order and complete RHS vector in every
case, including absent targets and zero/dependent rows.

## Baseline: full joint system

For each case, construct a fresh `CertifiedSystem(U + 8)`. Insert `[M, 0]` and
all original target rows `[v_i, -e_t]`, retaining affine consistency and original-
row weights. Compute its full kernel and test all eight target unit vectors.
Identifiable target t must have a complete original-row certificate whose
weighted coefficient vector is `[0, +e_t]` and whose RHS is its scalar k_t.
Check that scalar by public multiplication `[k_t]P = Q_t`.

No solver, elimination state, kernel, target certificate or result is reused
from an earlier case, budget, source schedule, scope, A7 record or candidate arm.
A full-rank source matrix does not recover a target with no natural row.

## Candidate: cancel first and lift certificates

For every represented target t, choose its first row j(t) in original target-row
order. For every additional row i of that same target, construct from the
original projected target rows, paying the arithmetic:

`c_i = v_i - v_j`, `d_i = b_i - b_j`.

Collect these rows as C z = d. Build a fresh width-U system D with M first and
C second, carrying weights on those original D rows. Use cancellations from
all target groups before testing any representative: this matches joint recovery,
not the isolated-single-row test on the old source matrix.

For a represented target, identify its representative vector v_j in D by the
full-kernel criterion v_j N_D = 0. If identified with weights (lambda, mu),

`v_j = lambda M + mu C`,

then its scalar is

`k_t = lambda a + mu d - b_j`.

Lift to the original joint rows before claiming recovery:

- base-row weights are lambda;
- target-row weights are the sum of `mu_i (e_i - e_j(i))`, minus one additional
  `e_j(t)` for the selected representative of the recovered target.

This exact sign gives target unit `+e_t`: cancellation differences carry zero
target coefficients and subtracting `[v_j, -e_t]` leaves the desired positive
unit. Verify every coefficient and RHS against the full original joint matrix,
then require the same public multiplication check. Keep both the reduced-system
weights and lifted original-row weights with representative/cancellation indices.
Never substitute saved A7 cancellation rows or certificates for construction.

An absent target has no representative and remains explicitly unidentifiable,
with no fabricated zero scalar or certificate. Include it among all eight output
slots. A single target row creates no cancellation for that group, but may still
be identified using source rows or cancellations from other targets.

With h represented target groups, row elimination predicts

`rank(full joint) = rank(D) + h`.

Compare this exact rank identity and target identifiability/scalars independently.
The two kernel bases have different widths and dimensions; do not require their
coordinate arrays to be identical. Joint nullity is `(U - rank(D)) + (8 - h)`;
remaining base uncertainty is `U - rank(D)`. Rank deficiency is a retained input,
not grounds to discard a case or demand full base rank first.

## Cost ownership and counting

Both methods rebuild cold for every case. Fix method order prospectively and
retain all cases regardless of the first method's result. Shared projection/
input extraction is charged once at its declared scope. For each method retain
disjoint stages for matrix/cancellation construction, elimination, kernel,
identification, certificate lifting, original-row certificate verification and
public group verification. Baseline lifting may simply expose its original-row
weights, but that work remains an explicit stage. Candidate construction and
lifting are never hidden under free preprocessing.

Count Fr additions, subtractions, multiplications and inversions separately,
including RHS updates, weight propagation, representative scalar subtraction,
lifting and original-row verification. The existing old Field implementation
merges add and sub into `field_add`; it is insufficient for this requirement.
Both methods must use the same compatible Fr instrument with distinct counters.
Do not infer subtraction counts after execution from an aggregated value.
State the coverage of modular encoding/reduction, zero skips, loop/control,
allocation, hashing, serialization and inversion internals. Counter conservation
is not an independent primitive-operation audit.

Keep Fp field/group costs of public multiplication separate from Fr algebra.
No sum of additions, inversions, multiplications or group calls is an invented
weighted cost. Diagnostic CPU/wall clocks are retained with wall_valid=false;
there is no timing-speedup or full-S claim. Report paired operation vectors and
per-stage differences on the exact row systems, with distributions across cases
labelled as dependent observations. Do not present width reduction alone as
measured savings: constructing C, lifting weights and checking them are paid.

Historical curve/target/source collection costs are inherited provenance and
outside this solver-only comparison. They are neither executed again nor assumed
free in an end-to-end attack interpretation. Shared projection and separate
checker work retain their own records rather than being duplicated per arm or
mixed with inclusive process totals.

## Controls, independent checks and reporting

The primary criterion is exact recovery equivalence: both methods and a separate
dense affine oracle agree on identifiable target sets and scalars, rank identities
and certificate validity for every paired case. Certificates need not have the
same weights, but both must reproduce the original matrix target unit/RHS and
pass public checks. Baseline semantic outcomes must match retained A7 joint
outcomes, without using those outcomes as solver inputs.

Software controls cover deterministic A/A, deficient base rank with identifiable
targets, no target rows, absent target groups, several target groups whose
cancellations jointly supply information, duplicate/zero cancellation rows,
wrong target coefficient/index, false cancellation sign/RHS, corrupt lifted
weights, inconsistent affine systems, size refusals and native admission.
Use an independent dense implementation for ranks/kernels and row-space tests,
not the candidate's own cancellation construction or producer arithmetic as
its only oracle. Synthetic tests are distinct from the native retained panel.

Retain complete case identity/provenance, input row hashes and counts, per-arm
cold records, phase/counter vectors, kernels, representative and cancellation
maps, all recovery and original-row weights, independent verification and
checker diagnostics. Save computed solver records before validation can fail,
with every failed/censored case retained. Unknown results and missing costs
remain unknown, not zeros or mathematical negatives. Keep original and gzip
hashes and content-addressed artifact references; hydrate exact inputs before
checking exports. Publish immutable results before report/observation sidecar,
graphs, inspected PDF, benchmark/progress records and database updates.

Export two solver arms over 288 paired instance labels, yielding 576 rows.
All solves are deterministic; source schedule seeds are case attributes, not new
solver randomness. Use an explicit metadata seed interface that matches actual
export cells, and exercise real exporter lint with ID/seed corruption controls.
One physical execution owns shared resources; per-arm solver records own their
cold algebra costs. Repeated target recoveries are not new target samples.

## Admission and limits

Use only one existing workstation process/thread, 2 GiB address space and a
21,600-second CPU/wall protective watchdog, one attempt and no retry. No new
EKS/IsoLab resources or paid submissions are covered; account allowance telemetry
is unknown. Fixed maximum 4,096 input rows and width 64 protect each case before
matrix/certificate allocation; refuse with preserved prefixes rather than
truncation or selection. All 288 paired systems and 576 solves remain scheduled.

Parent owns exact GitHub publication of source/dependencies, the input manifest,
configuration and launch command, fresh prospective source-bound protocol freeze,
actual current canonical S3 checkpoint/gate and explicit exact root release
before native solver mathematics. No A7 release authorizes A8. This delegation
provides administrative design/readiness only: no official scientific ledger or
status records, independent staffed review, verified resolver/provider/probe,
full-ledger pass or native execution is inferred. Exact-byte assessment follows
the parent's completed implementation and selected software checks.
