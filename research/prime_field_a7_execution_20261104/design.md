# A7: matched source-budget sweep

Prospective delegated administrative design, 4 November 2026. This is the first
ranked continuation after A6: inspect source-count and cost thresholds on the
same four curves and public targets, with prefix-correct anchor knowledge. It
is a conditioned follow-up on observed inputs, not a new blind holdout or a
population estimate. No source schedule, new point, relation or native experiment
is generated in preparing this note. Exact-byte assessment follows implementation.

## Fixed material and reference boundary

Copy all four A6 fixtures, bases, full EC1 identities, generators, signed public
projections and all 32 point targets, retaining original paths, source commits
and byte hashes. Keep these projected widths throughout:

| Fixture | p | b, with a = 2 | r | Fixed U |
|:--|--:|--:|--:|--:|
| p8191-i0 | 8191 | 2473 | 8101 | 15 |
| p8191-i1 | 8191 | 5699 | 8087 | 16 |
| p65537-i0 | 65537 | 30320 | 65053 | 31 |
| p65537-i1 | 65537 | 52897 | 65633 | 31 |

No target scalar labels, recovered A6 values, historical relation rows or selected
successful subsets enter the new matrices. Fixed window public anchors from
scalars 1 through 64 remain the common projected knowledge at every budget.
No new hash-source/base coincidence may shrink U silently.

A6 found eight relation-only distinct targets identified with base uncertainty
remaining, across 14 curve/schedule/target records. Its single-row and joint
sets sometimes differed. Its anchor scope also had one prefix-16 case whose
anchor was allowed to come from any of the 64 already constructed sources.
A7 changes that operational prefix boundary: only scheduled sources through the
current budget can contribute new point-derived anchor knowledge. A lower-budget
A6 anchor outcome need not reproduce when its anchor lies later in the schedule.
Preserve and explain that distinction; do not rewrite the A6 result.

## Exact schedules and budgets

Arms are `window`, `hash0`, `hash1`, `hash2`. Keep the exact A6 hash domain
`prime-field-fresh-source-control/20261104/v1`, seeds 0, 1, 2, canonical point
conventions and the complete first 64 source scalar/order arrays.

For hash schedules, extend the same accepted-index recipe to 128 distinct
nonzero scalars. For index 0 through 127, counters 0 through 9999, hash the
UTF-8 string `domain|full_EC1_UID|seed|index|counter`, take its big-endian integer
h and scalar 1 + h mod (r - 1). Accept the first scalar not previously selected
in that schedule. Reject exact within-schedule repeats only, retain signed
pairs, cross-arm/window overlap and all public-point coincidences. Preserve
complete payload digests, residues/scalars, reasons and counter attempts. The
first 64 selected scalars must exactly equal A6, independently checked.

Window begins with the exact original A6 64-element order, then appends scalars
65 through 128 sorted by SHA256 of the exact UTF-8 string
`domain|window-extension|full_EC1_UID|scalar`. It is not globally resorted.

Analyze all budgets [0, 8, 16, 24, 32, 48, 64, 96, 128]. Do not stop collection
at a rank or recovery event. Every arm executes all 128 scheduled queries in
successive disjoint blocks between budgets. Retain every miss and hit, pair
bucket, accepted index, block endpoint, digest and point-construction record.
The sweep describes these nine checkpoints. A first successful checkpoint is
not the exact first source index or an optimal stopping rule inside its block.

## Prefix-correct information and cost

Construct the original 64 window points once as a cold shared prerequisite;
verify the copied projection and retain the cost at budget 0. Window's first
64 scheduled points may then be reused from that prerequisite with explicit
cache-hit accounting. Reuse does not make their cold construction free. Later
window points and hash scheduled points are constructed in their budget blocks,
using the same cache policy for every arm: reuse only an exact scalar key in
the original 64-point prerequisite map. A negative/sign-equivalent scalar or a
point constructed earlier for another schedule is not a cache entry. Record
every cache hit; do not credit a full-horizon or cross-schedule cache.

At budget b, only the first b scheduled points and their source relation rows
are available to that arm's new-source analysis. Add new public anchor rows
only for scheduled indices below b. Full-schedule scalars are publicly computable
from the frozen seeds, so this is an operational input/cost restriction, not
cryptographic secrecy. The program must not consume later point constructions,
anchor rows or derived source knowledge in a lower-budget matrix or diagnostic.

In scope `relations`, use prefix source rows with the fixed original-window
projection only. In scope `anchors`, add the same prefix's explicit public
source/base affine equations in those U columns. Retain scalar, schedule index,
point, atom/sign, projected vector and RHS for every anchor. Duplicate and
already-known anchor witnesses remain, with equation counts and rank separated.
Report relation rank, anchor-only rank, anchor-augmented rank and marginal gain.
At budget 0, no newly scheduled anchor enters either scope, despite the fixed
original window knowledge and charged common prerequisite.

Public target diagnostics at budget b use only the fixed original 64 window
points plus that arm's first b scheduled points. Keep direct signed-source and
base matches, and [t]Q matches for 1 <= t <= 64, labelled as original or scheduled
knowledge with source indices. Do not use the future 128-point diagnostic as if
available earlier. Diagnostics remain explanatory, not extra target label rows.
A bounded nonmatch excludes only the declared comparisons.

Budget cost views must identify what was actually paid by b:

- cold common prerequisite point construction, fixed projection, signs, shared
  table and the one fixed target stream;
- that arm's incremental schedule derivation, construction/cache operations,
  query/extraction/certification and anchor/diagnostic work through b;
- each checkpoint's algebra and certificate verification, as actually run.

The implementation derives all 128-source hash schedules upfront and records
every candidate attempt plus 64 window-extension hashes. Charge that entire
phase as prepaid rather than inventing an unmeasured first-b hashing cost. If
an all-prefix cumulative experiment recomputes diagnostics or elimination at
nine checkpoints, its physical total includes those actual computations. A
hypothetical one-checkpoint cold cost must be explicitly derived from declared
components, excluding earlier checkpoint analysis only as a labelled counterfactual.
Never present a budget-b view as a second native execution or ignore the fixed
64-point prerequisite when comparing window with hashes.

## Constant relation set and algebraic measurements

Build one complete signed distinct-pair table per curve and query the same eight
fixed targets once, reusing those rows across budgets and scopes. Include infinity
keys and all bucket entries. Every source/target query covers every third atom
and both signs, accepting every hit with j < k < third. Source overlap is queried
in every arm even when a point construction can be reused. Target queries use Q,
not target multiples. No target miss or coincidence is discarded.

For each budget/scope M, retain full affine consistency/rank/kernel records and
normalized equations. Test each natural target row by vN = 0 with complete
original-row weights/RHS. Joint analysis appends all eight target columns and
identifies target-unit functionals with carried weights and public [k]P = Q
checks. Source-only base nullity and base uncertainty after target cancellation
are separate observables. Report single-row and joint sets, their difference,
and first checked budget of each recovery without mixing repeated target slots
with independently drawn targets.

Score base-only target information exactly:

Delta = rank([[M, 0], [B, Utarget]]) - rank(Utarget) - rank(M).

Keep outside rank, stacked rank, explicit target cancellation vectors/RHS and
weights, dense oracle agreement, resulting base rank and nullity. Outside target
unknowns never inflate the score. Retain prospectively charged union rank with
the window relation span at the same budget. Union gains require both source
collections and must not be described as replacement at equal budget cost.

Within one arm/scope, increasing source budgets give nested matrices and known
anchor sets. Rank and identified target sets must not decrease. Keep nested
source/anchor indices and kernel-action evidence; a failed monotonicity check
is a concrete integrity issue. Such checks complement, not replace, separate
arithmetic and dense algebra verification.

## Controls and independent verification

At budget 64, `relations` must reproduce the A6 source descriptor set, target
rows, projection, ranks, kernels and recovery semantics for every arm/curve.
The `anchors` scope at 64 must also match because all original 64 schedule points
are then available. Physical cold costs differ because A7 explicitly caches the
shared prerequisite; no A6/A7 timing equality is required. At lower budgets,
A6 anchor scopes used all 64 points, whereas A7 uses only the prefix. Compare
those only with the changed knowledge boundary explicitly recorded.

The separate implementation reconstructs all scalar/extension recipes, the
first-64 controls, fixed public projection, prefix construction/cache records,
complete signed-triple sums mapped to all scheduled/target points, every pair,
query bucket and journal, each anchor's point/sign/RHS and budget membership,
all dense ranks, full kernels, cancellation/union and recovery certificates.
It uses separate arithmetic and no target-label sidecars or producer arithmetic.
The oracle may reconstruct the full 128-source semantic truth for verification;
it must still verify every published prefix record uses only its legal inputs.

Software controls include deterministic A/A, repeated-hash rejection, window
extension order, exact first-64 preservation, a deliberately future-only anchor
that must not affect an earlier budget, cache/prerequisite accounting, missing
block endpoints, false prefix diagnostics, kernels, cancellation weights and
target-unit RHS, plus actual export instance/seed lint and no-admission refusal.
This is implementation verification, not independently staffed scientific review.

## Size, resources and records

There are four curves, 16 full source schedules, 32 fixed target points and
288 curve/arm/budget/scope records in one physical panel. Expected complete work
is 98,304 source queries, 1,536 shared target queries and 4,928 signed pair entries.
A single common oracle enumerates 88,320 signed triples across four curves,
mapping sums to all sources/targets. There are 2,048 queried source slots, not
2,048 independent random instances. All repeated budgets/scopes are dependent.

Use 72 paired export instance labels, one per curve/budget/scope, mapped to
decimal 0 through 71. The four arms give 288 rows, with constant arm seeds
window/hash0 = 0, hash1 = 1, hash2 = 2; an explicit seed list must match that
layout. Exercise the real exporter lint, not only its schema. Shared physical
collection counters have one owner per curve; budget/cost references and
cumulative views do not multiply them.

Retain input/provenance hashes, exact source/interpreter/package and actual
admission bindings, ownership/resource records, complete construction/query
journals, collection before algebra, final records before separate verification,
stdout/stderr, checker clocks and every failed prefix. Missing ranks or work
remain unknown; finalized-work subtotals are labelled with their coverage.
Lossless gzip/artifact manifests bind original and retained bytes. Parent
publishes immutable data before report/observation sidecar/graphs/PDF and database,
with benchmark/progress records in their actual measured units. Fp/Fr/group/logical
vectors overlap and do not give a calibrated complete S or scalar cost ratio.

Only the existing shared workstation is covered: one process/thread, 2 GiB,
21,600-second CPU/wall protective watchdog, one attempt, no retry. Use the prospectively declared
4,096-row-per-stream, 4,096-pair and 10,000-candidate-per-scalar protective refusal
gates. The row cap is increased from the initial 2,048 proposal for the doubled
source horizon before protocol freeze. It refuses with retained prefixes and
never truncates or changes the declared workload based on outcomes. No
EKS/IsoLab build, paid submission or capacity increase is authorized by this
local design. Account allowance telemetry is unknown.

Root owns publication of exact source/configuration/seeds/input manifest and
command, verification on GitHub, fresh prospective protocol freeze, actual current
S3 checkpoint/gate, exact explicit root release and execution through run. No
A6 release authorizes A7. This delegation changes no official scientific status
and creates no ledger records. Configured coordinator resolution remains
anthropic:claude-opus-5-5, effort high, unverified; no successful model probe,
full-ledger validation or staffed scientific review is inferred. Exact-byte
administrative approvability is recorded below for the exact reviewed bytes.

## Exact implementation assessment

The new core, independent checker, driver, common bindings, prepare, supervisor,
exporter, rules and tests have been read. Administrative metadata testing passed:
one synthetic test in 0.29 seconds, using the real 288-row export lint and false
instance/seed controls. The final builder reports zero schema/lint findings;
all 288 export identities/seeds match its table. All four copied fixture/order/
projection/target records and five declared A6 parent artifact hashes were
verified without generating a source schedule or point.

Budget cost records reference construction, query and anchor-discovery blocks
through b, with the cold prerequisite separate. Full shared target-multiple
construction is performed once; each budget's diagnostic lookup phases remain
charged separately. All algebra phases are retained in the immutable raw result;
compact analysis cost records reference that result rather than duplicating
those phase arrays. No complete scalar cost or hidden zero-cost reuse follows.

A prospective inspection identified that the initial row cap applied only to
individual query blocks rather than the cumulative source stream. Parent added
a cumulative retained_before count and refusal at cap + 1, before matrix work.
The new small-field regression sets a cap greater than every individual block
but less than the stream total, so it specifically detects the original defect.
No scientific execution preceded this repair. Parent reports the final selected
69 software controls passed in 2.57 seconds, including the cumulative-cap test,
prefix knowledge/cost controls and the 288-row export interface. Exact source
and input hashes are bound in admission-assessment.json before publication
and freeze.

The exact-byte source/interface contract is administratively approvable. The
analysis now references the actual retained raw JSON or gzip encoding for its
phase records, rather than an abstract filename pattern. This delegation directly
ran only the metadata test described above and checked copied artifact bytes;
it did not rerun the parent's scientific software suite or any native panel.

Root must publish the exact assessed source/input/configuration and command,
freeze the fresh protocol against that actual published full source SHA, obtain
the current actual canonical S3 checkpoint/gate and issue/publish the exact root
release before the admitted local run. The assessment is not an execution
release, independently staffed scientific review or official state change.
Changing a bound source/input requires additive reassessment before using it.
