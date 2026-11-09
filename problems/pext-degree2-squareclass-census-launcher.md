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

## Published input, plan and generic-support progress, 2026-11-03

The [input manifest](../experiments/EXP-PEXT-bf8f96/inputs/manifest.json)
now binds the exact five complete class inputs/checks and q3/n5 legacy
bijection artifact. The [all-T plan builder](../experiments/EXP-PEXT-bf8f96/implementation/join_plan.py)
specifies canonical T targets and exact structure offsets for the four geometric
cohorts; fixed F3/F5/F27 plans match the separate Rust join producer. No full
production plan was generated before protocol freeze. The q11/n3 design count
is 5322 T blocks times 1,786,323 structures, or 9,506,811,006 positions;
the current per-position output design has no demonstrated fit within the
proposed 24 CPU-hour total budget across all stages.

The new [generic support classifier](../experiments/EXP-PEXT-bf8f96/implementation/generic_disjoint.py)
checks squarefree Frobenius-conjugate quartics and all projective support gcds.
Disjoint supports certify rank n, connectedness and geometric genus
`(n-1)*2^n+1`; any overlap retains its pair for full analysis. On the complete
F27 software fixture, 1358/1638 rows are generic and all agree with the
separate square-relation checker; 280 require exceptional handling. The
[report](../experiments/EXP-PEXT-bf8f96/reports/generic-disjoint-20261103/report.md)
and source-bound log show the exact control scope, diagram and checks.

Next construct an exact exceptional-index generator and independent completeness
certificate so the generic complement can be counted without visiting every
structure. Then implement exceptional rank/genus and the original P1-P4,
descent/Type2, H1, controls, analysis and frozen execution packet. The contract
remains review_required and unapproved; no scientific trial was launched.

## Exceptional geometric support progress, 2026-11-03

The [support calculator](../experiments/EXP-PEXT-bf8f96/implementation/generic_disjoint.py)
now computes the exact parity-support span for every emitted overlapping
conjugate family. Its rank, projective union size and Riemann–Hurwitz genus
agree with a character-subcover genus sum. On all 280 overlapping positions
of the fixed F27 software fixture, a separate polynomial-product relation
checker agrees on geometric rank. The rank/branch/genus fixture breakdown and
source hashes are in the [new report](../experiments/EXP-PEXT-bf8f96/reports/exceptional-geometry-20261103/report.md).

This closes the emitted-row **geometric** rank/genus arithmetic interface at
the stated input scope. An exact exceptional-index generator with independent
completeness remains the next throughput construction. Coefficient classes,
descent and Type2 predicates must still be added before the complete P1–P4
and H1 contract can be frozen. No scientific run or approval occurred.

## Native screening and complete-index derivation, 2026-11-03

The [native arithmetic](../experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs)
now checks exact geometric support rank, branch count and genus for a complete
squarefree Frobenius orbit. The [join path](../experiments/EXP-PEXT-bf8f96/implementation/join_core.rs)
screens exact ordinal shards, counts generic positions and emits overlapping
rows only; it defers cocycle construction on generic rows. Its full fixed F27
software fixture yields 1358 generic and 280 exceptional positions, and
113-position shard replay gives identical exceptional ordinals and genera.
Nine core and eleven join Rust tests pass, including q3/n5 rank-one validation.
This path still visits every ordinal, so no 24 CPU-hour fit is inferred.

The [prospective exceptional-index derivation](../experiments/EXP-PEXT-bf8f96/reports/exceptional-index-design-20261103/report.md)
handles all rational and degree-2/3/4 branch roots by finite-field orbit
normalization, a small linear system for each nonrational root pair and a
Lang/Hilbert-90 cocycle solve. It retains the existing left-coset ordinal order
and all cohort types. The full generator, independent completeness checker,
resource measurement, constant coefficient classes, descent, Type2 and frozen
execution packet remain to implement. No scientific trial or approval occurred.

## Rational-root exceptional-index generator, 2026-11-03

The [native arithmetic](../experiments/EXP-PEXT-bf8f96/implementation/quotient_core.rs)
now builds reusable, complete cocycle-to-ordinal and rational-image indices
for the exact left-coset structure order. It emits the full contribution from
K-rational branch roots, including simple infinity and collisions between
distinct roots. Nonrational point-orbit representatives are cached once per
field. The [independent checker](../experiments/EXP-PEXT-bf8f96/implementation/check_rational_collision_certificate.py)
recomputes the full fixed F27 candidate sets with polynomial-basis arithmetic
and rejects missing or inserted ordinals. Its first T block has 273 rational-
root exceptional indices; the second has none. Direct support checking leaves
six and one exceptional indices respectively for the degree-2/3/4 root
generator. Native 13-core/15-join and one independent Python test pass; the
[source-bound report](../experiments/EXP-PEXT-bf8f96/reports/rational-collision-index-20261103/report.md)
gives the exact scope and modeled index sizes.

Next implement symbolic factor roots and linear cocycle candidates for degrees
2/3/4, replay all factor patterns independently, then measure the full-cohort
resource route and finish the frozen execution packet. No scientific trial or
approval occurred.

## Symbolic extension arithmetic, 2026-11-03

The [native symbolic extension](../experiments/EXP-PEXT-bf8f96/implementation/symbolic_extension.rs)
represents degree-2/3/4 roots in an explicit irreducible polynomial basis over
the pinned K encoding. It validates the modulus by Frobenius and proper-subfield
checks and provides field arithmetic, inversion and polynomial evaluation
without tabulating all extension elements. Fourteen core native tests pass,
including the three degrees over F27 and invalid-modulus controls. The
[report](../experiments/EXP-PEXT-bf8f96/reports/symbolic-extension-20261103/report.md)
records its software scope. Next factor bound quartics, solve all nonrational
root collisions, replay completeness independently and measure the proposed
resource route. The contract remains review_required; no scientific trial or
approval occurred.

## Complete branch-factor input, 2026-11-03

The [native branch factorizer](../experiments/EXP-PEXT-bf8f96/implementation/branch_factorization.rs)
now returns exact irreducible factors for all five squarefree projective
quartic patterns, including a deterministic trace/norm split for `2+2` and
an explicit infinity flag. Fixed F27 fixtures exercise each pattern, the
equal-trace norm fallback, and actual quotient forms. Fifteen core and
seventeen join native tests pass; the [report](../experiments/EXP-PEXT-bf8f96/reports/branch-factorization-20261103/report.md)
states the construction and scope. Next embed all roots in a common symbolic
extension and solve the nonrational collision equations, then independently
replay completeness and measure the resource route. The contract remains
review_required; no scientific trial or approval occurred.

## All-degree exceptional candidates, 2026-11-03

The [common-extension roots](../experiments/EXP-PEXT-bf8f96/implementation/branch_roots.rs)
and [linear collision solver](../experiments/EXP-PEXT-bf8f96/implementation/root_collision.rs)
now emit candidate structure ordinals for branch roots of degrees 1 through 4.
Each of the five synthetic squarefree factor patterns matches a full fixed
F27 structure scan. The two actual quotient forms yield complete exceptional
unions of 279 and 1 ordinals; the degree-greater-than-one contribution is
7 and 1 before one overlap with the rational set. Seventeen core and nineteen
join native tests pass. The [report](../experiments/EXP-PEXT-bf8f96/reports/all-degree-collision-20261103/report.md)
states the exact fixed-fixture scope. Next independently replay all factor
patterns, check each production candidate against literal support gcd,
measure full-cohort resource feasibility, and complete descent, Type2,
controls and the frozen execution packet. The contract remains
review_required; no scientific trial or approval occurred.

## Independent all-pattern software replay, 2026-11-03

The [independent polynomial-basis checker](../experiments/EXP-PEXT-bf8f96/implementation/check_all_degree_collision_certificate.py)
now reconstructs the roots, projective linear kernels, cocycle norm and joined
Lang witnesses for all five squarefree factor patterns and both actual F27
quotient forms. Every exact candidate union agrees with a literal support-gcd
scan. The [source-bound report](../experiments/EXP-PEXT-bf8f96/reports/all-degree-independent-20261103/report.md)
records counts, 17 core and 19 join native tests, one independent Python test
and four mutation rejections. Next build production candidate receipts and
direct checks, measure the full-cohort 4 GB and 24 CPU-hour route, and finish
coefficient-aware descent, Type2, controls and the frozen execution packet.
The contract remains review_required; no scientific trial or approval occurred.

## Direct candidate checks and bounded q11 probe, 2026-11-03

The [checked candidate path](../experiments/EXP-PEXT-bf8f96/implementation/root_collision.rs)
now retains exact structure matrices, verifies every generated exceptional
ordinal against transported support, and partitions the generic complement
into exact half-open intervals. Fixed F27 full-scan and independent replay
checks still pass. A source-bound single-thread synthetic q11/n3 profile
measured three factor patterns with cached 1,786,323-entry cocycle and
21,435,876-entry rational-image indices: 2.347 seconds wall in total and
253,368 KiB peak RSS under a 4 GiB address-space cap. The host load was
recorded. The [report](../experiments/EXP-PEXT-bf8f96/reports/checked-candidates-20261103/report.md)
keeps that software scope explicit. Next serialize production source-bound
candidate/interval receipts and measure complete P1-P4, descent/Type2 and
control costs before the 24 CPU-hour execution decision. The contract remains
review_required; no scientific trial or approval occurred.

## Bounded per-form candidate unit, 2026-11-03

The [per-form Rust CLI](../experiments/EXP-PEXT-bf8f96/implementation/candidate_unit.rs)
now emits exact field identity, factors/roots, checked exceptional matrix and
geometry rows, and generic complement intervals under explicit count caps.
An [independent unit checker](../experiments/EXP-PEXT-bf8f96/implementation/check_candidate_unit.py)
replayed both actual F27 forms against the complete joined fixture, and seven
negative mutations or caps were rejected. A source-bound synthetic q11/n3
CLI smoke emitted a 3,623,945-byte JSON unit for 79,223 exceptional rows;
peak RSS was 267,204 KiB under a 4 GiB address-space cap. The
[report](../experiments/EXP-PEXT-bf8f96/reports/candidate-unit-20261103/report.md)
preserves the fixed software scope. Next bind each unit to the published
cohort/T plan and frozen source/protocol, add atomic success and failure
receipts, and complete the remaining controls and descent interfaces before
approval. The contract remains review_required; no scientific trial occurred.

## Published cohort/T candidate binding, 2026-11-03

The [read-only binding](../experiments/EXP-PEXT-bf8f96/implementation/candidate_binding.py)
recomputes the published all-T join plan, checks an optional plan byte for byte,
reconstructs the selected curve and canonical T list, and derives the exact
quotient form and structure-ordinal interval. The first q5/n3 class at T=O
binds form `[1,0,0,1,0]` to `[0,16275)`. Two software tests pass, including
mutated-plan and invalid-index refusals; the
[report](../experiments/EXP-PEXT-bf8f96/reports/candidate-binding-20261103/report.md)
records the exact scope. Next add frozen protocol/source/binary admission and
write-once success/failure receipts, then complete independent production
checks and the remaining full execution packet. The contract remains
review_required; no scientific trial occurred.

## Supervisor-gated candidate artifacts, 2026-11-03

The [candidate artifact helper](../experiments/EXP-PEXT-bf8f96/implementation/candidate_unit_artifact.py)
now requires the frozen plan's live supervisor claim and exact source/input
bindings for production construction. Each unit directory is exclusive;
successful raw output is compressed with digests, and started failures retain
partial stdout, stderr and a write-once failure record. Fixed F27 software
checks replayed one successful unit and a forced-cap failure, plus duplicate,
limit, digest and admission refusals. The
[report](../experiments/EXP-PEXT-bf8f96/reports/candidate-artifact-20261103/report.md)
binds the scope. Next build the full run driver, independent production
checker and exact trial/queue/runbook packet. The experiment remains
review_required and unfrozen; no cohort trial was launched.

## Independent candidate-set replay, 2026-11-03

The [independent Python checker](../experiments/EXP-PEXT-bf8f96/implementation/independent_candidate_unit.py)
now reconstructs the frozen structure ordinal map, exact rational and
higher-degree-root candidate unions, and generic complement intervals. All
fixed F27 rows match, including direct geometry checks; five mutation controls
are rejected. The retained synthetic q11 unit independently matches 79,223
exceptional ordinals and 58,530 complement intervals. Its 498,348 KiB peak
RSS and 96.04-second profile separate the 89.15-second one-time index from
3.98 seconds of unit verification. The
[report](../experiments/EXP-PEXT-bf8f96/reports/independent-candidate-20261103/report.md)
keeps this software-fixture scope explicit. Next bind the checker to
supervisor-owned cohort artifacts and complete the full controls, descent,
analysis and approval packet. EXP-PEXT-bf8f96 remains review_required and
unfrozen; no scientific trial occurred.

## Independent artifact custody and synthetic n=5, 2026-11-03

The [read-only artifact verifier](../experiments/EXP-PEXT-bf8f96/implementation/independent_check.py)
now checks external cohort/T form and binary identity, receipt and payload
hashes, command/caps, and failure/partial refusal before independent exact-set
replay. Twelve software tests pass, including altered input, receipt and
compressed-payload controls. A separate synthetic q3/n5 quartic exercises
both 597,861-entry cocycle indices: one exceptional ordinal and the full
generic complement match; checker time was 45.136 seconds at 211,592 KiB
peak RSS under a 4 GiB cap. The
[report](../experiments/EXP-PEXT-bf8f96/reports/artifact-integration-20261103/report.md)
keeps this software scope explicit. Next integrate a persistent supervised
driver and full trial artifact index, then complete descent, Type2, controls
and the approval packet. The contract remains review_required and unfrozen;
no scientific cohort trial occurred.

## Fixed candidate batch layout, 2026-11-03

The [batch sealer](../experiments/EXP-PEXT-bf8f96/implementation/candidate_batch.py)
now provides deterministic 16-unit tar chunks, per-member and tar digests,
readback-before-source-removal, failure retention, and a complete full-cohort
index verifier. The [layout inventory](../experiments/EXP-PEXT-bf8f96/reports/candidate-batches-20261103/layout-inventory.json)
finds 8,178 class/T units in 513 fixed chunks across the four original cohorts.
Eleven related software tests pass, including tamper and partial-chunk refusal.
The 49 MiB chunk ceilings sum to 24.54 GiB, so the final storage route must
be checked against the current local 20 GiB free space before approval. The
[report](../experiments/EXP-PEXT-bf8f96/reports/candidate-batches-20261103/report.md)
records exact counts and fixture scope. Next integrate the supervised full
driver and persistent checker, then complete descent, Type2, controls,
analysis and the approval packet. The contract remains review_required and
unfrozen; no scientific cohort trial occurred.

## Supervised candidate batch driver and replay, 2026-11-03

The [candidate driver](../experiments/EXP-PEXT-bf8f96/implementation/candidate_census_driver.py)
now iterates the fixed full-cohort class/T slots through the live-admitted
unit runner, enforces bounded per-unit/stage limits, stops on failure and
seals a complete index only after every unit succeeds. The
[persistent checker](../experiments/EXP-PEXT-bf8f96/implementation/candidate_census_check.py)
verifies that index and independently replays each unit against its bound form
and binary digest using one reusable field index. Fourteen related software
tests pass; the F27 two-unit fixture gives 280 exceptional and 1,358 generic
structure ordinals with all exceptional geometry checked. The
[report](../experiments/EXP-PEXT-bf8f96/reports/candidate-driver-20261103/report.md)
records the exact software scope. Next integrate binary build provenance and
supervisor-compatible stage artifacts in `run.py`, then the remaining descent,
Type2, controls, analysis and approval packet. The contract remains
review_required and unfrozen; no scientific cohort trial occurred.

## Candidate build provenance and nested cohort slots, 2026-11-03

The [build helper](../experiments/EXP-PEXT-bf8f96/implementation/candidate_build.py)
checks seven transitive Rust source hashes and records the invoked rustc shim,
real compiler executable, version, flags, logs and binary digest in a
write-once receipt. Production candidate units may now live in an exact
`cohorts/<cohort>` subdirectory of one supervisor run, so q5/n3 and q7/n3
fit the prescribed `n3core` stage without a new run. Sixteen related software
tests pass, including source/binary tamper refusal and nested F27 replay. The
[report](../experiments/EXP-PEXT-bf8f96/reports/candidate-build-20261103/report.md)
records the software scope. Next integrate this build and the cohort slots in
the six-stage launcher, then complete the remaining descent, Type2, controls,
analysis and approval packet. EXP-PEXT-bf8f96 remains review_required and
unfrozen; no scientific cohort trial occurred.

## Exact published four-cohort join-plan inputs, 2026-11-03

The four [canonical join plans](../experiments/EXP-PEXT-bf8f96/inputs/join-plans-20261103/)
are now materialized and recomputed against the published compact
class manifest. Their [set receipt](../experiments/EXP-PEXT-bf8f96/inputs/join-plans-20261103/receipt.json)
binds 4,092 classes, 8,178 class/T blocks and 10,262,826,642 structure
ordinals to exact plan hashes. The draft specification now names the four
input paths and reflects the actual readiness state. The
[report](../experiments/EXP-PEXT-bf8f96/reports/join-plans-published-20261103/report.md)
keeps this input-preparation scope explicit. Next bind the plans in the frozen
six-stage trial plan and run entry point, then complete the remaining descent,
Type2, controls, analysis and approval packet. No candidate or scientific
cohort trial row was produced.

## Supervisor-bound candidate stage component, 2026-11-03

The [stage adapter](../experiments/EXP-PEXT-bf8f96/implementation/candidate_stage.py)
now binds the source-checked Rust build, fixed cohort loops and persistent
independent checker to the original `n3core`, `n3ext` and `n5` supervisor
stages. It requires the approved plan's exact launch, live claim, six-stage
watchdogs, cohort caps and declared artifacts. The
[inventory](../experiments/EXP-PEXT-bf8f96/reports/candidate-stage-20261103/candidate-artifacts.json)
lists 1,056 candidate-component artifact paths across those three stages.
Driver and checker share the supervisor launch deadline, and the checker now
compares every retained unit's limits to the frozen cohort config. The
[report](../experiments/EXP-PEXT-bf8f96/reports/candidate-stage-20261103/report.md)
records software checks and exact scope. Next complete the full six-stage
`run.py`/`check.py`, descent, Type2, C0-C7 controls, analysis and approval
packet. No scientific cohort trial was launched.

## Exact geometric reducer component, 2026-11-03

The [reducer](../experiments/EXP-PEXT-bf8f96/implementation/geometric_reducer.py)
now recomputes P1 factor-pattern mismatches, P2 nonzero-T genus-spectrum
violations and P3 same-curve geometric minimum drops from complete candidate
units. It requires a full independent geometry review of every exceptional
row, sealed chunk and review hashes, published class/T bindings, and exact
cohort totals. Ten related software tests pass on fixed F27 units, including
Riemann–Hurwitz and incomplete-coverage refusals. The
[report](../experiments/EXP-PEXT-bf8f96/reports/geometric-reducer-20261103/report.md)
records the fixture's spectra and boundaries. Next integrate the reducer in
full analysis with descent, Type2, C0-C7 controls and frozen output bindings.
No approved scientific cohort was reduced or launched.

## Coefficient-aware square-class relations, 2026-11-03

The [relation ledger](../experiments/EXP-PEXT-bf8f96/implementation/squareclass_relations.py)
now enumerates the branch-support and leading-coefficient square class of
every subset of a checked n=3/5/7 conjugate quartic orbit. It distinguishes
geometric from arithmetic relations over K(X), including a nonsquare constant
relation in a synthetic rank-two coefficient twist. Three software tests pass
against the independent polynomial-square routine. The
[report](../experiments/EXP-PEXT-bf8f96/reports/squareclass-relations-20261103/report.md)
records the exact fixture result. Next construct and check the Frobenius lift
and cocycle before assigning any descended/admissible genus. No scientific
cohort trial was launched.

## Radical-algebra Frobenius lift component, 2026-11-03

The [lift checker](../experiments/EXP-PEXT-bf8f96/implementation/radical_frobenius.py)
now constructs coherent polynomial-square witnesses for arithmetic relations,
checks their cyclic Frobenius images, solves the generator sign equations and
checks an order-n action. Seven related software tests pass, including a
nonzero sign correction on a fixed F27 repeated-support orbit and refusal of
the synthetic nonsquare rank-two relation as an arithmetic square. The
[report](../experiments/EXP-PEXT-bf8f96/reports/radical-frobenius-20261103/report.md)
records the exact algebraic scope. Next bind the action to the actual source
elliptic map and construct/check the descended model before reporting an
admissible genus. No scientific cohort trial was launched.

## Source elliptic map to moved quotient quartic, 2026-11-03

The [binding checker](../experiments/EXP-PEXT-bf8f96/implementation/source_map_binding.py)
now checks the named elliptic model and canonical T map into the quotient
quartic, then the projective structure change with its determinant-dependent
ordinate factor. It verifies the quartic equation and rational inverse in the
elliptic function field and binds the result to a published class/T and an
independent structure ordinal. Seven related software tests pass on F27
fixtures and the q5/n3 published input binding, including wrong-matrix and
wrong-ordinal refusals. The
[report](../experiments/EXP-PEXT-bf8f96/reports/source-map-binding-20261103/report.md)
records the exact scope. Next construct and check the fixed-field model and
full compositum source-map compatibility before assigning an admissible
genus. No scientific cohort trial was launched.

## Type2 orbit and trace-zero predicate instrument, 2026-11-03

The [Type2 instrument](../experiments/EXP-PEXT-bf8f96/implementation/type2_predicate.py)
now checks the length-six Frobenius orbit signature with exponents
`{0,1,3,4}` and separately searches the trace-zero base-field Möbius
predicate. Three software tests pass: two synthetic F27 quartics have the
Type2 signature, one with a matrix witness and one with an exhaustive
no-witness result; a different `(2,2)` pattern and an irreducible quartic do
not have the signature. The
[report](../experiments/EXP-PEXT-bf8f96/reports/type2-predicate-20261103/report.md)
records the exact forms and source. Next bind Type2 rows into the full
checker/analysis and independent witness review. No scientific cohort trial
was launched.

## Type2 full-review unit scanner, 2026-11-03

The [unit scanner](../experiments/EXP-PEXT-bf8f96/implementation/type2_unit_scan.py)
now cross-tabs Type2 signatures and trace-zero predicate results only after
every exceptional candidate row has passed independent geometry review.
Type2's length-six root placement forces overlap with a Frobenius-conjugate
branch set, so the certified generic complement is excluded without scanning
each generic structure. Five related software tests pass; three complete F27
units give signature counts `6,8,6` and trace-zero-positive counts `2,0,2`,
and partial reviews are refused. The
[report](../experiments/EXP-PEXT-bf8f96/reports/type2-unit-scan-20261103/report.md)
records the exact fixture scope. Next persist the rows in the frozen checker
and cross-tab by published curve/T identity; full-cohort runtime remains to
be measured. No scientific cohort trial was launched.

## Type2 persistent checker integration, 2026-11-03

The [batch checker](../experiments/EXP-PEXT-bf8f96/implementation/candidate_census_check.py)
now persists Type2 signature rows and a hash-linked summary for cubic
cohorts after full independent exceptional-geometry review. The candidate
check binds the Type2 summary hash. The
[stage adapter](../experiments/EXP-PEXT-bf8f96/implementation/candidate_stage.py)
requires this mode and declares both files per cubic cohort; its candidate
artifact inventory is now 254 paths in `n3core`, 677 in `n3ext` and 131 in
`n5`, 1,062 total. Eight related software tests pass, including the F27
write-once batch and refusal of Type2 without full geometry. The
[report](../experiments/EXP-PEXT-bf8f96/reports/type2-stage-integration-20261103/report.md)
records the exact fixture scope. Next bind these outputs in full analysis and
measure full-cohort checker time/storage before approval. No scientific
cohort trial was launched.

## Type2 curve/T analysis join, 2026-11-03

The [geometric reducer](../experiments/EXP-PEXT-bf8f96/implementation/geometric_reducer.py)
now verifies the hash-linked Type2 batch and joins retained signatures to
sealed exceptional unit rows by published class/T, ordinal, raw hash and
matrix. It keeps signature and trace-zero predicate counts separate at unit,
actual-curve and cohort level, and rejects stray Type2 files on noncubic
cohorts. Four reducer software tests pass, including digest and matrix
tampering refusal. The [report](../experiments/EXP-PEXT-bf8f96/reports/type2-analysis-20261103/report.md)
records the fixture scope. Next bind the reducer into the complete analysis
stage and implement descent and C0–C7 controls. The contract remains
`review_required`; no scientific cohort trial was launched.

## Four-cohort geometric analysis component, 2026-11-03

The [campaign reducer](../experiments/EXP-PEXT-bf8f96/implementation/geometric_campaign.py)
now requires the frozen supervisor trial plan and all three checked census
stage directories, then binds q5/q7/q11 n3 and q3 n5 to their published
join plans and sealed full-cohort candidate units. It reconciles class order,
per-curve P1/P2/P3 totals, and separate cubic Type2 counts before emitting a
read-only campaign table. Seven focused software tests pass. The
[report](../experiments/EXP-PEXT-bf8f96/reports/geometric-campaign-20261103/report.md)
records the checked scope. Next build the full analyze-stage writer and add
descent and C0–C7 controls. The contract remains `review_required`; no
scientific cohort trial was launched.

## Geometric analyze-stage component, 2026-11-03

The [geometric analysis stage](../experiments/EXP-PEXT-bf8f96/implementation/geometric_analysis_stage.py)
now writes and rechecks exact curve rows and a hash-bound campaign summary
inside a frozen supervisor analyze trial. It requires the validated supervisor
execution receipt for each of the three prior census stages, the current
analyze claim, plan/source bindings and declared output paths. Six focused
software tests pass, including write-once and tampered-row refusal. The
[report](../experiments/EXP-PEXT-bf8f96/reports/geometric-analysis-stage-20261103/report.md)
records the component scope. Next implement descent and controls, then bind
the final analyze/export artifacts. The contract remains `review_required`;
no scientific cohort trial was launched.

## Source radical binding, 2026-11-03

The [source-radical binder](../experiments/EXP-PEXT-bf8f96/implementation/source_radical_binding.py)
now identifies generator zero of the coherent radical algebra with the exact
moved quartic reached from the named elliptic curve and T. It checks the full
coefficient Frobenius orbit and order-n radical action, with optional
published class/T/ordinal binding. Nine related software tests pass, including
wrong-source and wrong-conjugate refusal. The
[report](../experiments/EXP-PEXT-bf8f96/reports/source-radical-binding-20261103/report.md)
records the scope. Next construct the fixed-field model and independently
check its descent and connectedness before assigning admissible genus. The
contract remains `review_required`; no scientific cohort trial was launched.

## Exact radical-algebra table, 2026-11-05

The [radical-algebra model](../experiments/EXP-PEXT-bf8f96/implementation/radical_algebra_model.py)
now builds an arithmetic-relation quotient basis, exact multiplication factors
and a sign-corrected semilinear Frobenius table. It checks every basis-pair
action identity and the order-n identity, and can bind generator zero to the
named source curve and T. Ten related software tests pass, including the F27
constant-twist rank increase from 2 to 3. The
[report](../experiments/EXP-PEXT-bf8f96/reports/radical-algebra-model-20261105/report.md)
records the fixture scope. Next construct the fixed-invariant basis and
base-field multiplication, then independently check connectedness and genus.
The contract remains `review_required`; no scientific cohort trial was launched.

## Fixed-invariant radical basis, 2026-11-05

The [fixed-invariant basis](../experiments/EXP-PEXT-bf8f96/implementation/fixed_invariant_basis.py)
now constructs and directly checks Frobenius-fixed vectors orbit by orbit from
the exact radical-algebra table. It verifies full polynomial-basis Moore rank
and the expected vector dimension without dividing by n, including the
characteristic-3 cubic case. Nine related software tests pass across F27 and
published q3/n5 fixtures. The
[report](../experiments/EXP-PEXT-bf8f96/reports/fixed-invariant-basis-20261105/report.md)
records the scope. Next compute multiplication over the base rational-function
field and independently check connectedness and genus. The contract remains
`review_required`; no scientific cohort trial was launched.

## Fixed-field multiplication table, 2026-11-05

The [fixed-field multiplication builder](../experiments/EXP-PEXT-bf8f96/implementation/fixed_field_multiplication.py)
computes every invariant-basis product in the exact radical algebra, decomposes
it over k(x) by Frobenius-norm rationalization, and reconstructs the ambient
product. It checks the unit identity and binds a table to the named source
curve and T. Ten related software tests pass across F27 source rows, a
constant twist, and a published q3/n5 class/T fixture. The
[report](../experiments/EXP-PEXT-bf8f96/reports/fixed-field-multiplication-20261105/report.md)
records the fixture scope. Next independently check descent and geometric
connectedness, then implement the controls and remaining six-stage pipeline.
The contract remains `review_required` and unfrozen.

## Source-fixed component geometry, 2026-11-05

The [component-geometry checker](../experiments/EXP-PEXT-bf8f96/implementation/fixed_model_geometry.py)
replays square relations with the quotient checker's separate arithmetic and
cross-checks rank, fixed-algebra dimension, component count and branch genus.
It suppresses a connected-curve genus when a constant twist gives two geometric
components. Thirteen related software tests pass on F27 source rows, the
constant twist and a mismatch rejection. The
[report](../experiments/EXP-PEXT-bf8f96/reports/fixed-model-geometry-20261105/report.md)
records the fixture scope. Next independently review the model multiplication
and descent claim, then bind admissible minima and implement the controls.
The contract remains `review_required` and unfrozen.

## Exact census-stage capacity check, 2026-11-05

The [capacity checker](../experiments/EXP-PEXT-bf8f96/implementation/stage_capacity.py)
rederives the published join plans and counts 8,178 class/T units and
10,262,826,642 logical positions across the three census stages. The q11/n3
stage has 5,322 units under a 28,800-second watchdog, giving a best-case
average ceiling of 4,800/887 seconds per unit before build, checker and
supervisor overhead. The sparse collision method can certify generic ranges
without iterating every position; no measured runtime qualification exists.
The [report](../experiments/EXP-PEXT-bf8f96/reports/stage-capacity-20261105/report.md)
also records the independent read-only review's exact full-model replay gap.
The contract remains `review_required` and unfrozen.

## Independent source-fixed model replay, 2026-11-05

The [standalone checker](../experiments/EXP-PEXT-bf8f96/implementation/independent_fixed_model_check.py)
reconstructs the radical quotient and semilinear algebra action with separate
field and polynomial arithmetic. It replays every fixed basis vector, product
and unit after scalar extension, plus the named curve/T/matrix quartic and
source generator square. A separate character-sum checker derives geometric
components and genus without the producer geometry reducer. The
[report](../experiments/EXP-PEXT-bf8f96/reports/independent-fixed-model-20261105/report.md)
records the fixture and tamper checks. Next bind this gate to every source-bound
unit and qualify full-cohort runtime under the fixed watchdogs. The contract
remains `review_required` and unfrozen.

## Published exceptional-row fixed-model binding, 2026-11-05

The [single-row adapter](../experiments/EXP-PEXT-bf8f96/implementation/source_fixed_unit.py)
binds one retained exceptional ordinal and matrix to the published actual
curve/T, the source quartic and its rational inverse charts, the fixed algebra
and the separate algebra/character-genus replay. Two focused software tests
pass on a q5/n3 class-zero T-zero fixture, including wrong-matrix and
wrong-genus rejection. The
[report](../experiments/EXP-PEXT-bf8f96/reports/source-fixed-unit-20261105/report.md)
records the scope. Next implement frozen row selection, stage custody,
deadlines and C5 review strata. The contract remains `review_required` and
unfrozen.

## Prospective C5 independent-review roster, 2026-11-05

The [C5 selector](../experiments/EXP-PEXT-bf8f96/implementation/c5_selection.py)
now defines first/lower-middle/last canonical class/T units per occupied
cohort/torsion-count/T-index/descent-status stratum and forces every flagged
counterexample, special-j class and Type2 hyperelliptic-witness unit into the
blind review roster. It refuses incomplete or misordered metadata and retains
the flagged structure ordinals. The
[report](../experiments/EXP-PEXT-bf8f96/reports/c5-selection-20261105/report.md)
records two focused tests and a four-plan shape-only exercise over 8,178
units. Actual selection awaits certificate-bound descent and exception
metadata, stage write-once custody, independent recomputation and comparison.
The contract remains `review_required` and unfrozen.

## Source-derived special-j selection, 2026-11-05

The [C5 special-j check](../experiments/EXP-PEXT-bf8f96/implementation/curve_special_j.py)
derives the review flag from each named K-model and refuses false metadata
flags. A second cubic-discriminant formula agrees on every published class:
the four plans have 6, 8, 4 and 4 special-j classes respectively. The
[report](../experiments/EXP-PEXT-bf8f96/reports/c5-special-j-20261105/report.md)
records the five focused tests and the provisional roster sizes with
placeholder descent labels. This grounds one C5 stratum in source arithmetic;
descent and witness metadata, blind custody and independent recomputation
remain. The contract remains `review_required` and unfrozen.

## Retained Type2 witness identities for C5, 2026-11-05

The [geometric reducer](../experiments/EXP-PEXT-bf8f96/implementation/geometric_reducer.py)
now carries every predicate-true Type2 ordinal from the hash-bound checked
batch into its curve/T output, with the raw candidate-unit and Type2-check
digests. It rejects duplicate or out-of-order signature ordinals. The
[report](../experiments/EXP-PEXT-bf8f96/reports/c5-type2-witness-custody-20261105/report.md)
records four focused F27 software tests and the exact scope of this retained
instrument output. Next assemble the complete C5 metadata table from
validated stages, add descent and counterexample certificates, then seal and
recompute the blind roster. The contract remains `review_required` and
unfrozen.

## Complete preliminary C5 metadata binding, 2026-11-05

The [C5 metadata assembler](../experiments/EXP-PEXT-bf8f96/implementation/c5_metadata_preview.py)
binds every canonical curve/T row to the published join plan, checked unit
hash, Type2 batch hash and predicate-true witness ordinals. It derives the
special-j flag and forces P1/P2 discrepancies into review. Descent is
explicitly `unresolved`; the selector refuses such a table for review unless
preview mode is requested, and preview output is labeled incomplete. The
[report](../experiments/EXP-PEXT-bf8f96/reports/c5-metadata-preview-20261105/report.md)
records seven focused tests and the evidence boundary. Next certify descent
and control-valid counterexamples, then seal complete metadata and the blind
independent roster. The contract remains `review_required` and unfrozen.

## Write-once four-cohort C5 analyze preview, 2026-11-05

The [C5 preview stage](../experiments/EXP-PEXT-bf8f96/implementation/c5_preview_stage.py)
now writes preliminary metadata, incomplete roster and summary artifacts
once, binding all four published plan hashes and source RUN IDs. The analyze
component requires their names and source closure in the eventual frozen
trial plan; its checker recomputes every byte. The
[report](../experiments/EXP-PEXT-bf8f96/reports/c5-preview-stage-20261105/report.md)
records five focused tests and the preview boundary. Next build certified
descent/counterexample metadata and the final sealed blind C5 review; the
contract remains `review_required` and unfrozen.

## Exceptional descent classification and capacity, 2026-11-09

The [design correction](../experiments/EXP-PEXT-bf8f96/reports/exceptional-descent-admission-20261109/report.md) identifies a false-negative hazard: the current sign solver searches one coherent relation-witness presentation. A miss cannot be used as a proof of inadmissibility. Under the exact Frobenius-stable multiquadratic premises, the extension of the odd cyclic field automorphism by a 2-group splits, so an order-n lift exists. The source now raises an instrument error on a miss and refuses a non-exhibiting result. Positive checked actions are unchanged.

The single published exceptional fixed-model check is not joined to sealed unit bytes or extended to every exceptional row. q11/n3 has 5,322 units and 5.41 seconds per unit under its stage watchdog. Applying existing synthetic candidate counts to matching plan factor patterns gives an **81,749,543-row workload scenario** before [1,3] and [4]; it is not a cohort count or lower bound. A full fixed multiplication table for each row has no qualified time/storage fit.

Next test: design and independently check a compact source-map, square-relation/component-genus and positive action certificate joined to each sealed exceptional row; reserve explicit fixed-model replay for blinded C5 units. Define complete status semantics and account for every unresolved lower-genus row before a minimum or final C5 stratum is emitted. Independently review the lift premise and solver completeness; qualify full-cohort CPU/RSS/storage against the unchanged finite ceilings. The original exit criteria remain.
