# Next bounded action: a paid known-log factor-base control

Prospective worklist only: no new protocol, execution approval, experiment,
source change, mathematical trial, Git mutation or scientific-state transition.
A12 producer measurements below are pinned by
[PCC-20261106-7a4122](../../pcc/claims/PCC-20261106-7a4122.json), with
unverified/not_covered standing; local arithmetic checks and S3 custody are not
trusted signed replay or recomputation. [pcc:unverified]

## Why this discriminator comes first

Read the published raw snapshot `15769eb216c6a8fa1da30f4772443a4c6d2f6ec5`,
its [metrics](runs/a12-batched-holdout-6ba98a/metrics.json) and lossless
[analysis archive](runs/a12-batched-holdout-6ba98a/analysis.json.gz).
The complete panel reports 1,152 dependent systems, 2,304 solver calls and zero
unknown systems, using four curves and the same 32 target points throughout
its dependent views. [pcc:unverified]

At target budget 8, relation-only identified slots across 48 views per policy
are walk 3, hash-offset 0 and general 7; explicit-anchor counts are 3, 4 and 96.
Each policy/scope has at most 384 slots from repeated views of those 32 points,
not 384 independent targets. Smaller-budget relation-only recovery is zero;
general-anchor recovery is 10 at budget 2 and 27 at budget 4. Source-system
ranks in the retained views range from 2 through 21 against 31 original
projected columns. These observations motivate testing the cost of supplying
base knowledge directly; they do not establish that natural relations are
useless or identify a cheapest target program. [pcc:unverified]

Both solvers identify 150 dependent slots overall. Joint Fr add/sub/mul/inv
counts are 4245/351255/311016/1384; outside-first counts are
31177/386075/347426/1869. The retained scalar and batch query engines agree,
with Fp add/sub/mul/inv vectors respectively
0/1691200/724800/241600 and 120800/1087200/1075875/3775.
These are finite component counts with different allocation/control costs,
not calibrated runtime or whole-attack advantage. The batch inversion is an
existing baseline that must apply symmetrically in the next comparison.
[pcc:unverified]

**Rank one next action:** on fresh matched curves and public targets, compare
the original 32-atom base with a separately paid 32-atom base whose public
scalar labels are known by construction. Ask whether the latter can recover
at least the same named targets within no greater included cold cost, without
learning unknown base logs. This is a falsifiable strong-control question for
the implemented direct signed-three-sum collector, not a proposed new attack.

## Existing code makes this a necessary control

[factor_base.py](../../src/crypto_autoresearcher/index_calculus/factor_base.py)
already defines H017 `known_log`: small multiples jP with known logs, retained
as a census control outside the default base families. Its builder explicitly
uses a separate Curve so construction is not charged to the caller's E.ops.
That convention cannot be copied into a complete-cost comparison. Rebuild and
meter every actual point and table instead of treating inherited labels or
legacy counters as free work.

[harvest.py](../../src/crypto_autoresearcher/index_calculus/harvest.py) already
provides `formal_basis_known_log` and reduction by e_j-j e_1. The A12
[source collector](source_collection.py) queries explicit signed E points;
its direct group decomposition does not require the cover's x-square
predicate. Therefore a public-labelled E-point base is an available semantic
control. This read does not establish that the existing control has measured
better recovery or costs on these new fields. No absence or novelty is claimed.

For the primary comparison use independently hash-selected nonzero public
scalar labels, rather than only 1..32: an interval of small multiples would
also change the distribution of attainable three-term sums. The old H017
interval remains a source pointer, not an extra arm added to this bounded test.
Normalize each resulting point's sign with the corresponding signed scalar;
reject identity and duplicate sign classes with a fixed finite draw cap.
Do not reject or redraw a base because of target recovery, rank, source/base
coincidences or measured cost.

## Fixed design sketch and semantic boundaries

- Freeze one new curve/target/base domain, four fresh coefficient curves on the
  same two 18/19-bit fields, base size 32, and eight independent public targets
  per curve. Exclude the explicitly bound earlier coefficient models; retain
  every accepted target, including public coincidences. No target scalar labels
  or checker knowledge enter collection. This changes the base, so a gain is
  not a fixed-base Delta comparison or evidence about the original cover alone.
- Pair the original base and one hashed public-labelled base on identical
  curves, public generators, targets, AP/hash seeds 0/1/2, source horizon 128,
  and target policies walk/hash-offset/general with budgets 1/2/4/8. Use only
  source prefix 128 for this discriminator; do not repeat a larger-field-only
  transfer or expand target budgets until success. Keep distinct signed
  three-atom semantics and record every hit, miss and exceptional group case.
- Each base gets its own correctly charged pair table and per-endpoint batch
  query path. Apply the same constructor selection, prepaid signs, denominator
  masking, exceptional fallbacks and paid knowledge scans. Any scalar engine
  replay is a separate physical control, not another target sample. Do not
  import another base's tables or future cache points as free prerequisites.
- Public-labelled base construction yields explicit equations z_i=l_i, with
  paid generation, normalization and public [l_i]P=F_i certificates. They are
  supplied knowledge, not newly learned relations. Source construction/cache
  prerequisites used by an affine-target branch remain charged. The known-log
  deployment may omit source-relation queries and learning algebra that it does
  not need; the original-base deployment must pay its actual learning stage.
  Show this intentional difference rather than forcing useless baseline work
  or pretending both start with the same information.
- Keep the original-base relation-only and explicit-anchor results distinct.
  The known-log base is an explicit-knowledge control, not a relation-only
  success. Retain coincidences as paid equations. For a target decomposition
  sum c_i F_i=alpha P+beta Q, recover only through checked original-row weights
  and the supplied base labels, paying beta normalization, certificate lifting
  and public [q]P=Q verification. Intermediate symbolic multiples of Q are not
  known-log points. Never learn target labels from an oracle.
- Use the sparse kernel-free joint solver as the primary implemented algebra
  baseline; retain outside-first as a separately charged control if its full
  comparison is included. A direct known-label evaluation is an additional
  deployable algebra path whose operations must actually execute and be counted,
  not an assumed zero-cost replacement. Independent complete signed-triple and
  bucket/miss checks, dense positive/negative membership checks and original-row
  public certificates remain required.

The primary output is the exact recovered target mask and cold vector for each
matched target program, plus attribution to natural decompositions and supplied
public knowledge. Report original-base rank/nullity and within-base Delta where
applicable, without interpreting a known base's zero uncertainty as relation
rank gain or comparing ranks across different point sets. Keep all incomparable
vectors. A control that recovers no additional targets, loses target identities,
or spends more included resources without a compensating coverage gain is a
negative result for this proposed explanation, not a reason to redraw.

Charge actual base/scalar construction and all retained intermediates, predictor
simulations, membership/sign scans, table construction and storage, source work,
target P/Q construction, queries/extraction, normalization, algebra, lifting,
public checks, independent controls and IO/checkpoints. Physical campaign totals
include both base arms and every control; conditional cold deployment references
must not sum duplicated phases. Keep separate Fp/Fr add/sub/mul/inv, group API,
logical and allocation vectors plus inclusive resources. Preserve unexpanded
legacy generation/rejection/pow/Python/checker work and unisolated wall limits;
no complete calibrated S, rho comparison or whole-attack verdict follows.

This note grants no execution. Any future test needs its own exact prospective
source/input freeze, independent software controls, real current S3 custody and
root release. Keep one existing worker/thread, 2 GiB and a fresh bounded
21600 CPU/wall-second single attempt, finite candidate/row/table guards,
retained failure prefixes and unknown unexecuted cells. No automatic retry or
new paid capacity is implied.

## Other original leads remain open

- **Outside-point partials:** [A1](../prime_field_a1_execution_20261030/RESULTS.md)
  reports Delta 2/6 on the old fixtures, and
  [A2](../prime_field_a2_execution_20261030/RESULTS.md) completes original-base
  rank through within-row norm cancellation. [pcc:unverified] A later fixed-base
  32-point pool comparison must cancel all pool and target columns, retain
  exact target-unit certificates and pay collection/elimination/lifting costs.
  Keep requested target indices separate from auxiliary outside indices, with
  an explicit width gate; the current eight-target API is not a pool API.
  Larger raw rank is not base information. This remains the next base-preserving
  alternative if the paid-known-log control does not resolve the baseline gap.
- **Prym:** [B1](../prime_field_b1_execution_20261029/RESULTS.md) tests the isolated
  zero completion without new rank directions on its two original fixtures;
  [B2](../prime_field_b2_execution_20261030/RESULTS.md) records matched shifted
  covers with partial costs. [pcc:unverified] Broader exceptional-source,
  admissibility and scalable cover/target collection remain open, without
  relabelling completed tests unexecuted or universally obstructed.
- **Dickson:** [C1 report](../prime_field_c1_execution_20261029/reports/c1-fixed-panel-4f8ab9/report.typ)
  records seven fixed cases under dimension 560. [pcc:unverified] Native repeated-
  coordinate positives, matrix-free/scalable extraction, lifting/sign costs
  and a matched full-cost baseline remain open. The cubic exterior dimension
  guard and uncounted FLINT internals do not establish a universal obstruction.
- **Full signed-triple atlas:** remains a distinct producer/control comparison.
  Oracle construction already exists, but its table/memory costs and amortization
  across many source programs cannot be granted free to one cold target program.

Retrieval was limited to the pinned A12 metrics/analysis/PCC, existing known-log
factor-base/formal-harvest code, A12 direct collector and retained A1/A2/B1/B2/C1
worklist pointers. The prior research-kb unavailable/direct-source fallback and
PKM2016 section 3.2 rough-cost warning remain in force; no new KB IDs, primary
retrieval, corpus-wide absence, novelty or scientific-goal completion is claimed.
