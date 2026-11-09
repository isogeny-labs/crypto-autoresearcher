# Next bounded action: larger-field holdouts with a batched query baseline

Prospective worklist only. No new experiment record, approval, protocol, source
change, trial or scientific-status transition is made here. A11 observations
below are producer measurements under PCC-20261106-70a1b5 and PCC-20261106-648bb8, standing unverified/
not_covered because signed replay/recomputation is absent. The pinned metrics
and separately coded local checks are not signed verification. [pcc:unverified]

## Basis for the next comparison

Read the published raw snapshot e23280b606dd0802226d50edb912bbd59cdfa124:
[metrics](runs/a11-affine-holdout-30245e/metrics.json), hydrated analysis and
[PCC record](../../pcc/claims/PCC-20261106-70a1b5.json). It reports 1,152 systems,
2,304 solver calls, four fresh curves and 32 target points, source unchanged,
with matching target outcomes from both methods. [pcc:unverified]

At target budget8 every policy reports384 identified slots across48 dependent
views per scope: the same32-point panel is reused, not384independent targets. [pcc:unverified]
At budget2 the relation-only counts are walk275/hash311/general260; anchor
counts are276/325/348. [pcc:unverified] These different knowledge/cost boundaries do not name
a winning target program. [pcc:unverified]

Both solvers report7,317 identified slots over the dependent systems. [pcc:unverified] Joint Fr
add/sub/mul/inv totals are456714/6703275/6415404/4952; outside-first totals are
602296/7199490/6850637/4762. [pcc:unverified] Fewer inversions trade against more other units,
so cancellation is not established as faster. [pcc:unverified] Cold budget8 constructor EC-add
counts over48branches are walk2688/hash8537/general28116; these are not weighted
costs or a whole-attack saving. [pcc:unverified]

Rank one next action: **freeze a fresh larger-field comparison of the same
source/target programs and query budgets, with scalar versus per-endpoint
batched signed-subtraction arithmetic as shared baseline controls, and compare
cold information/cost Pareto fronts.** Do not expand target budget beyond8
merely because the present small panel reaches complete recovery there.

## Existing arithmetic is a prerequisite, not a new mechanism

Targeted source reads found an implemented product-tree batch_inverse in
[src/_accel.py](../../src/crypto_autoresearcher/index_calculus/_accel.py), plus
subtract_many/m2_candidates_multi. [tails.py](../../src/crypto_autoresearcher/index_calculus/tails.py)
and [harvest.py](../../src/crypto_autoresearcher/index_calculus/harvest.py) already
use it. It requires NumPy, nonzero input denominators and p<2^32 for its uint64
products; zero denominators are masked and exceptional group cases are handled
separately. This is standard arithmetic and an existing baseline pointer, not
a novelty claim.

For one endpoint R, the signed third-point queries R±F_i share x-denominators.
Batch those denominators within that endpoint, handling identities, doubling,
zero-y and coincident-x cases exactly, and preserve every ordered bucket/miss
and signed distinct-triple descriptor. Apply the same path to all source and
target policies; retain a scalar pair-query control and independent plain group/
full-triple oracle. Tiny controls must establish exact semantic equality before
the fresh experiment is frozen. They are a prerequisite implementation check,
not another native parameter sweep on the already observed A11 targets.

The current accelerated decomposition helper deliberately preserves historical
scalar abstract counters while only locating work. Those counters cannot be
reported as actual batched Fp work. Meter the executed product-tree/field/vector
operations, inversion, mask/fallback, lookup, allocation and conversion scope.
Bind the actual NumPy version/build, dtype bounds and single-thread settings;
unavailable acceleration must not silently change a frozen engine comparison.
Do not give the helper free setup or hide the scalar-control execution costs.
If both query engines run, charge both physically but reuse identical matrices
for algebra; that does not create extra independent solver outcomes.

Keep the batch inside one endpoint so its cold query counter record does not
borrow other source arms' or future targets' denominators. A cross-endpoint
batch would require a different declared deployment and amortization scope.
The available projective arithmetic is another known reference, but the current
representation_arithmetic.py interface is restricted to p<=10000/lift settings;
it is not a drop-in larger-field cost baseline. No projective port or measured
constructor optimum is claimed by this note.

## One falsifiable larger-field panel

A concrete next design would use two publicly rule-selected prime fields of
18 and19bits, two first-eligible curves each and eight fresh canonical-y targets
per curve. Freeze a fresh hash domain and first-prime/curve candidate rules
before generation, retain all candidate/primality/order costs, exclude the
listed prior models, and never select by yield or recovery. These sizes remain
within the existing batch helper's p<2^32 domain. No field or curve is generated
here.

Keep base32 in both fields, rather than add unknowns until recovery looks good.
Retain AP/hash seeds0/1/2,128source streams, source prefixes64/128, target programs
walk/hash_offset/general, target budgets1/2/4/8, relations/anchors and both
kernel-free solvers with symmetric unit/sign shortcuts. The larger fields are
new draws; an A11 replay is only a conditioned correctness diagnostic. All
curves, targets, seeds, failed decompositions and source/base/public/cross-target
coincidences stay in the panel, including zero recovery at the largest budget.

The falsifiable question is whether the reported early target coverage survives
field growth at fixed base/source/query programs and paid information boundaries,
and which programs remain nondominated after the stronger arithmetic controls.
If fixed budgets become sparse or give no recovery, record that scale boundary;
do not enlarge base, sources or queries inside the same contract. The study
compares specified supplied-row programs, not a globally strongest IC/rho attack.

## Pareto and cost boundaries

Compare each source-prefix/target-budget/knowledge scope on the same fresh target
identities. Keep recovered target masks, not just equal counts; different sets
of the same size are not interchangeable. Report source rank, original-column
nullity and Delta after outside-target cancellation, with original-row/public
certificates. Keep direct public/identity/cross-target knowledge and natural
relation recovery separate; a larger raw U rank is not base information.

Use vectors of actual Fp/Fr add/sub/mul/inv, memory and setup/lookup/storage work.
Do not invent inversion-to-multiplication weights or claim runtime dominance
from primitive counts. A Pareto comparison requires the stated information
observable and all included cost components; otherwise retain incomparable arms.
Independent signed replay and full calibration remain separate missing evidence.

A deployable cold view includes one chosen source program, its paid prerequisite,
one target policy and its actual eight-target P/Q tables, query work, elimination,
normalization, lifting and public checks. The physical research panel additionally
pays every source arm, query-engine control, diagnostic, oracle and checkpoint.
Do not amortize a cold solve across all six source arms simply because the panel
ran them. Reuse geometric query aliases only with explicit request/physical-work
records, not invented reexecutions or clocks. Preserve legacy generation merged-
subtraction/unexpanded rejected-fixture/pow/OS/IO/checker limits, inclusive process
resources and wall_valid=false; complete phase retention is not calibrated S.

Finite row/label/memory/candidate gates must refuse with retained prefixes rather
than truncate or redraw. Continue fixed census after early success. A failure or
watchdog retains all observed work and leaves later cases unknown, with no retry
under the contract. Proposed limits remain one existing worker/thread,2GiB and
21600CPU/wall seconds, one attempt, no new paid capacity. Any run requires its
own published exact source/rules, prospective freeze, current actual S3 custody,
fresh absolute deadline/root release and ordinary admission. Typed outcome claims
must precede citation with actual PCC standing. This note grants no execution
authority or claim of improvement. [pcc:unverified]

## Other leads retained, not closed

- **Full signed-triple atlas versus pair queries:** retain as a later distinct
  collector comparison. A complete atlas already exists as a validation oracle;
  using it as producer requires paid construction/memory and a separate checker.
  Amortization over all six source arms is not automatically available to one
  cold target program. Base changes and repeated-atom tail tables must not be
  confused with the current signed-distinct-triple workload.
- **Dickson:** [C1 report](../prime_field_c1_execution_20261029/reports/c1-fixed-panel-4f8ab9/report.typ)
  reports seven fixed cases completed under560; repeated-coordinate native
  positives, matrix-free/scaling extraction and matched signed cost remain
  open. FLINT internals were not counted; this is not a universal obstruction.
  [pcc:unverified]
- **Prym:** [B1](../prime_field_b1_execution_20261029/RESULTS.md) reports no new
  equation/rank directions from the isolated zero completion on its two fixtures;
  [B2](../prime_field_b2_execution_20261030/RESULTS.md) reports matched shifted-cover
  gains with partial costs. [pcc:unverified] Broader exceptional-source and scalable cover/target
  questions remain open; do not label the completed tests unexecuted or
  universally negative. [pcc:unverified]
- **Outside-point partials:** [A1](../prime_field_a1_execution_20261030/RESULTS.md)
  reports Delta2/6 and [A2](../prime_field_a2_execution_20261030/RESULTS.md) reports
  full original base rank through norm cancellation. [pcc:unverified] Fresh-scale collection,
  complete elimination cost and deployable pool choices remain open; target-
  column cancellation does not settle outside-point descent. [pcc:unverified]

Source search was scoped to available local src/tools/research implementations,
A11 committed metrics/analysis/PCC and the prior worklist pointers. The existing
research-kb outage/direct-source fallback is carried; no source IDs, corpus-wide
absence or novelty is invented. No extra source search, mathematical trial,
new experiment approval or official scientific transition is implied.
