# PEXT all-degree-two census lacks coefficient-aware executable coverage

- Status: open
- Kind: implementation and interface gap; not a mathematical obstruction
- Goal: GOAL-PEXT-4a1d6b
- Hypothesis: H-PEXT-c3a11d
- Experiment: EXP-PEXT-bf8f96 (review_required; no approval)
- Owner: Coordinator design lane
- Raised: 2026-11-02

The proposed all-map genus census cannot be admitted from the old x-line launcher. Its exact missing obligations are same-curve T-class enumeration, projective exceptional charts, full coefficient square relations and connectedness, descent certificates, full-cohort identity/stabilizer coverage, independent checker, analysis/export, frozen input/source hashes and an actual trial plan/queue/handoff.

The derived quartic identity in [design notes](../experiments/EXP-PEXT-bf8f96/design-obligations.md) is one construction component; it does not discharge those census obligations. Primary sources are accessible and read; their coefficient and hyperellipticity conditions sharpen the implementation requirement. Existing abstract-only knowledge records are not silently upgraded.

Exit criteria: preserve full cohorts, implement and independently check every named obligation, resolve lawful PEXT lane capacity with failed outcomes and continuation preserved, verify exact permitted Executor runtime, freeze the final analysis/protocol/source/input bytes and receive approvable:true from the prospective packet checker. Then publish approval and archives before separate /run.

Next test: complete the same-curve quotient/projective and square-class checker first; use the symbolic identity replay and existing T=O fixtures as instrument tests. No scientific census before freeze. Missing or failing admission is an operational fact, not evidence against P1-P4.

Recheck: actual completed implementation/archive or exact runtime/lane capability change, not periodic no-change polling. The active goal remains active; no official scientific status changes.

## Implementation progress, 2026-11-02

[The native quotient component](../experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs)
now implements rational points and the general group law, witnessed E(K)/2E(K)
partitions, both projective quotient charts, reproducible field identity, and
geometric/arithmetic square-class relations retaining nonsquare constants.
[Four fixed software tests pass](../experiments/EXP-PEXT-bf8f96/reports/implementation-20261102/software-tests.txt),
including characteristic-three and extension-field fixtures. These replace the
initial absence of those construction components; they do not constitute a
full-cohort census or independent scientific verification.

The remaining implementation path is certificate serialization and an independent
checker, exhaustive actual-curve/structure iteration with scalar-aware transforms,
Frobenius-descent certificates, full-cohort analysis and launch/export bindings.
The original exit criteria and admission requirements remain in force. See the
[implementation report](../experiments/EXP-PEXT-bf8f96/reports/implementation-20261102/report.md).

## Certificate replay progress, 2026-11-02

[The serializer](../experiments/EXP-PEXT-bf8f96/implementation/quotient_certificate.rs)
now emits one actual-curve standard-structure unit, including full point/coset
witnesses, chart images, exact Frobenius conjugates and complete square-class
relations. [The Python checker](../experiments/EXP-PEXT-bf8f96/implementation/check_quotient_certificate.py)
recomputes those finite objects with separate polynomial-basis arithmetic and
requires an external expected field/model. The source-bound software log records
four Rust test groups and six Python methods passing, including five fixed units,
eleven mutation variants, field/scalar/JSON controls and CLI expected-input checks.
This completes the serialization and per-unit checker components within their
stated standard-structure scope; it does not establish full-cohort coverage,
Frobenius descent or independent scientific review.

Next implement exhaustive actual-curve/projective-structure iteration, retaining
binary-form scalar bookkeeping, external frozen field/T identities and exact
coverage/stabilizer certificates. Descent/lift and Type2 checks, original geometric
P3 cohorts and descriptive q13 H1 output, analysis/export/checkpoint and frozen
launch bindings remain required. The original admission/exit criteria and active
goal status remain unchanged. See the fresh
[certificate report](../experiments/EXP-PEXT-bf8f96/reports/certificates-20261102/report.md).

## Projective-structure progress, 2026-11-02

The [core API](../experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs)
now exposes complete bounded left-coset traversal, normalized coordinate cocycles
and literal scalar-preserving binary-form transport. The
[structure checker](../experiments/EXP-PEXT-bf8f96/implementation/check_structure_certificate.py)
checks distinct cocycles and the exact group index, which certifies complete left
PGL2(Fq) coset coverage, and independently recomputes every transformed coefficient.
The source-bound software log records5Rust,6quotientPython and5structurePython
test groups passing, including the full fixed F27 partition19,656=819*24 and
orientation/scalar controls. This completes the group/coordinate component at its
stated scope; it is no all-curve census or covering-descent certificate.

The present whole-JSON checker is capped at16MiB/100,000structures. Next implement
streaming coverage/partition receipts and full actual-curve/T/projective-structure
joins with exact external identities and scalar bookkeeping, preserving original
cohorts. Frobenius-lift/descent and Type2 checks, geometric P3/descriptive q13 H1
analysis, exports/checkpoints and frozen launch bindings remain required. See the
[fresh structures report](../experiments/EXP-PEXT-bf8f96/reports/structures-20261102/report.md).
Original exit/admission criteria remain; scientific and goal statuses do not change.

## Curve-class progress, 2026-11-02

The [core API](../experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs)
now normalizes all nonsingular long models into complete short or characteristic3
A/B families, enumerates their full residual isomorphism orbits and emits explicit
representative-to-member u,r witnesses. The separate
[class checker](../experiments/EXP-PEXT-bf8f96/implementation/check_curve_class_certificate.py)
reconstructs complete normalized family coverage and polynomial isomorphism
identities. Final software checks pass6Rust+6quotientPython+5structurePython+
5classPython groups, including fixed F3/F5/F9 certificates and exceptional twists.
This completes the class-enumeration component, not a scientific cover/genus census.

The historical n5/q3 fixture SHA2568f03e3d1a28a989108a038cfffab51e0362d2397dd03e06fc0ccfe442d9123fa
identifies488 as the complete K-isomorphism cohort with twists and exceptional
models. The new full488model bijection is still unmaterialized and must align
actual field/model identities and explicit isomorphisms, not reordered class IDs.
Current16MiB/1,000,000-candidate checker limits exclude the original n3/q11 cohort;
next implement streaming input/coverage partitions without cutting that cohort,
then exact curve/T/structure joins. Scalar/descent/lift, Type2, original geometric
P3/descriptive q13 H1 analysis, exports/checkpoints and frozen launch bindings
remain required. See the [fresh classes report](../experiments/EXP-PEXT-bf8f96/reports/classes-20261102/report.md).
The original exit/admission criteria and scientific/goal statuses remain unchanged.


## Full-cohort input progress, 2026-11-02

The [compact input producer](../experiments/EXP-PEXT-bf8f96/implementation/compact_class_inputs.rs)
and [separate checker](../experiments/EXP-PEXT-bf8f96/implementation/check_compact_class_inputs.py)
now materialize and verify every prescribed class cohort without whole-member JSON:
q3/n5 488 classes / 117,370 nonsingular normalized members; q5/n3 252 / 15,500;
q7/n3 690 / 117,306; q11/n3 2,662 / 1,770,230; descriptive q13/n3 4,400 /
4,824,612. The checker reconstructs disjoint complete residual orbits with independent
polynomial arithmetic and exact family cardinalities. The previous input-size
obstruction for these cohorts is resolved within Q<=2197/10,000,000-slot bounds.

The [legacy bijection](../experiments/EXP-PEXT-bf8f96/inputs/classes-20261102/legacy-q3-n5-bijection.json)
is newly materialized and verified for all 488 historical role=class rows, using
hash-pinned field/builder/fixture identities and literal representative-to-old
cubic isomorphism witnesses. All old models and new classes occur once; model
coefficients are interpreted in polynomial-basis encoding. No archived genus/order
outcomes affect input selection. Four source-bound software test methods, all five
full input checks and the independent bijection replay pass. See the
[fresh report](../experiments/EXP-PEXT-bf8f96/reports/cohorts-20261102/report.md)
and exact commands/hash log for this completed input-construction component.

Next join the byte-bound classes with all rational-T cosets and projective
structures, scalar-preserving quartic transport and exact cross-shard coverage.
Connectedness/geometric genus, Frobenius descent/Type2, original geometric P3 and
descriptive q13 H1 analysis, exports/checkpoints and frozen launcher/runtime
bindings remain. Original admission/exit criteria and scientific/goal statuses
are unchanged; the experiment remains review_required/unapproved.


## Streaming join progress, 2026-11-02

The [join plan](../experiments/EXP-PEXT-bf8f96/implementation/join_core.rs)
now streams exact class/T/structure ordinal ranges with checked immutable prefixes,
direct structure unranking and literal scalar-preserving quartic/conjugate rows.
The [separate fixture checker](../experiments/EXP-PEXT-bf8f96/implementation/check_join_certificate.py)
reconstructs complete supplied model/T coverage, distinct projective cocycles and
exact adjacent-shard union. F3 complete classes pass8classes/14T-blocks/14rows;
F5 passes12/24/24; one F27 model passes2T-blocks*819structures=1638rows.
Eight Rust tests and25Python methods pass with source-bound logs, including
nested-reference unranking, malformed shards and all-control-point translation
involution. These checks complete the supplied-input arithmetic join component;
no full target join or scientific cover/genus trial was launched.

Next bind the complete published cohort and plan identities to production
streaming/checkpoint/shard custody, then implement explicit all-T Mobius/scalar
transport: T'=T+2Q requires reindexing HN to HN*A^-1, not fixed-ordinal equality.
The present group identity is checked; the coordinate/scalar witness is still
missing. Preserve all original five cohorts, abstract placements and controls.
Scientific descent/genus/analysis and frozen launcher remain subsequent interfaces.
See the [fresh join report](../experiments/EXP-PEXT-bf8f96/reports/joins-20261102/report.md).
Original criteria and scientific/goal statuses remain unchanged; review_required
and unapproved status persists.

## Exact target-coordinate transport progress, 2026-11-03

The new [transport component](../experiments/EXP-PEXT-bf8f96/implementation/target_transport.py)
constructs normalized Mobius A and nonzero weighted-ordinate kappa for supplied
T,Q with T'=T+2Q. It verifies both rational coordinate identities in K(E) by
clearing denominators and the literal quartic identity F_T'(A(X,Z))=kappa^2*F_T(X,Z).
The [source-bound software log](../experiments/EXP-PEXT-bf8f96/reports/transport-20261103/software-tests.txt)
records five methods PASS: all T,Q on all8F3classes(156pairs), all12F5classes(500),
F9A/twist/B(144/225/256), selected F27(12)/F125(9),216F3composition triples,
three F27 projective-cocycle reindex controls, mutations and CLI expected-input
checks. Coordinator static inspection found no defect in the inspected paths.
Synthesis and verification share the rational engine; this is exact component
software replay, not an independent arithmetic implementation or scientific review.

The explicit coordinate/scalar witness gap named in the previous entry is now
implemented at that scope. Next integrate transport and normalization scales with
the complete published cohort/plan identities and production streaming/checkpoint/
shard custody, including an exact full structure reindexing certificate. Preserve
all original cohorts: q3/n5(488), q5/n3(252), q7/n3(690), q11/n3(2662), descriptive
q13/n3(4400); abstract n3/5/7placements, original coordinate/random-branch controls,
geometric P3 and separate q5/7/11/13H1 arms retain their original requirements.
Connectedness/geometric genus, Frobenius lift/descent, Type2 and analysis/export
remain scientific interfaces. The fresh read-only preapproval diagnostic remains
approvable:false for missing implementation/runbook/route, lawful lane, trial-plan,
queue/handoff and published/frozen source/approval bindings. The original exit
criteria remain; no approval, freeze or scientific status transition occurs.
See the [fresh transport report](../experiments/EXP-PEXT-bf8f96/reports/transport-20261103/report.md)
and TASK-20261103-69adf4 for exact successor custody scope.
