# A9 JSON archive-control repair: bounded corrective contract

Prospective delegated coordinate-step-4 design, 5 November 2026. The first A9
attempt stopped on a serialized-control interface error. This contract permits
assessment of one narrowly corrected additional pass; it does not alter the
exhausted one-attempt A9 protocol or authorize an automatic retry. The scientific
case list, algorithms, seeds, arms and costs remain fixed. No native work, producer
code, Git mutation, official scientific status change or execution release is
performed by this administrative design.

## Preserved failure and exact reason

Original run: `a9-sparse-functionals-6be915` under
`research/prime_field_a9_execution_20261105/runs/`.
Its source is `2df9510e016c5795ae8d47f5826031f70e567616`, original frozen protocol
hash `228b97f279b244bc4ec3283805dce30c92b62bfa683de225eaad721850de66af`.

The retained execution reports exit 1, no timeout, unchanged source, start
2026-11-05T22:14:15.825283Z and finish 22:14:19.283322Z. All four first-case solver
outputs and their public-check phases were journaled before the checker raised
`A8 dense control differs: representatives`. There is no `case_checked` record
and no finalized case file. Four producer calls were observed, zero complete
cases were verified; all remaining cases were unexecuted, not zero-cost or
zero-recovery observations. The original raw record, protocol, release,
administrative assessment, execution, stderr and artifact manifest stay immutable.

The live representative map uses integer target-index keys. Loading its archived
A8 JSON control produces string keys. Comparing those maps directly fails even
when their entries agree. Python's official JSON documentation explicitly states
that object keys become strings and that `loads(dumps(x))` can differ for maps
with non-string keys. The previous in-memory controls did not exercise that
actual archive boundary. This is a correctness/serialization limitation, not
negative mathematical evidence about sparse evaluation or cancellation.

## Only scientific-interface change allowed

Copy the frozen A9 implementation into the new study namespace. The only control
semantics changed is the archived `representatives` comparison: compare temporary
maps with the same canonical integer target-index keys, leaving values unchanged.
Apply it only to that field, with missing/None maps handled as before. Do not
canonicalize whole solver results, relax counters or compare only outcomes.
Malformed/ambiguous keys or changed row-index values must not be hidden by the
normalization. Reject invalid controls rather than weakening the comparison.

All other exact A8 dense controls and sparse/dense semantic/certificate controls
remain unchanged, including every phase vector, full kernel, row reduction,
weight, RHS, public check, logical traversal count and exact Fr add/mul delta.
The new normalization uses checker-side JSON/Python representation handling;
it adds no producer Fr operation or warm start. Administrative namespace,
source/protocol/input bindings, failure accounting and remaining-budget guards
are updated explicitly, without altering solver mathematics.

Keep all 288 original A7 row systems, 32 fixed public targets and the four arms
`dense_joint`, `dense_cancel`, `sparse_joint`, `sparse_cancel`. The additional
pass rebuilds all 1,152 solver calls cold, including the four previously observed
first-case calls. Do not resume from the unverified prefix, omit duplicates,
select successful budgets or change any outcome-conditioned input. Existing
A7 solver data and A8 checker-only control provenance remain byte-bound.

## Required regression at the actual serialization boundary

The software control must serialize a valid archived control with `json.dumps`
and reload it with `json.loads`, rather than use only a live copy or manually
renamed key. It must demonstrate that the original frozen comparison fails with
the recorded representative-map error and that the bounded corrected comparison
passes the identical round-tripped control.

Also retain refusals for changed representative values or target membership,
false kernels/certificates, changed arithmetic/phase vectors and false sparse
logical counts. Preserve all existing native-admission and four-arm retention
controls. Tiny/synthetic tests are explicit software work; they do not count as
native case outcomes. The new full pass must retain dense A8 replay and independent
dense/public checks, including the first case that was previously interrupted.

## Two attempts, two clearly separated measurement scopes

The original contract had one attempt and it is exhausted. This new corrective
contract has exactly one additional explicit attempt, no automatic retry, under
the shared original resource envelope and deadline below. It is not a new pool,
provider, account, region, spending allowance or reset clock.

If the new pass completes, distinguish:

- clean corrected panel: 288 verified systems and 1,152 new solver calls;
- campaign: two physical attempts and 1,156 observed producer calls, including
  the four retained failed-prefix calls. Each arm has 288 clean calls plus one
  original observed call, not 289 independently sampled systems.

The original four calls remain observed/unverified in their own attempt, even
if the new run verifies mathematically equivalent outputs. Do not retroactively
mark the failed attempt successful or relabel its 0 verified cases. Preserve
first-attempt raw bytes and original source/protocol identities in every link.

Campaign arm vectors are the clean new producer vectors plus the old observed
producer vectors, with both operands and statuses retained. The original
`prefix-work-observed.json` contains those four vectors. Also charge the old
shared-projection phase once from the retained case-input event. Historical
collection remains outside the supplied-row solver measurement, as in A9.

Failed checking, startup, input loading, JSON/IO and other overhead remain in
original process resources. Do not turn them into invented per-arm Fr calls or
add inclusive process clocks to their contained phase clocks. The failed checker
has no successful per-case timing record; an unavailable disjoint duration must
remain unknown rather than zero. Retain old attempt wall/CPU/RSS separately and
new attempt resources, with aggregate boundaries stated. Shared host clocks have
wall_valid=false. No weighted scalar cost, runtime/full-S advantage, fresh-holdout
claim or broader goal completion follows from this repair.

If the corrective pass also fails, keep its exact completed/failed prefix and
actual costs; do not assert that the planned 1,152 new calls executed. There is
no third pass under this contract. A further continuation requires a separately
specified bounded action and preserves all existing attempts.

## Original deadline and cumulative machine protection

The original start is 2026-11-05T22:14:15.825283Z. Preserve the original absolute
21,600-second wall deadline: **2026-11-06T04:14:15.825283Z**. Publication, review
and checkpoint delay do not move that deadline. Reject a new launch if expired;
this note cannot silently grant a fresh six-hour window.

The retained first attempt used 1.694653 user CPU seconds and 1.384321 system
CPU seconds, total **3.078974 CPU seconds**, plus diagnostic wall
**3.45804065899938 seconds**. New admission/supervision must subtract those prior
resources from any cumulative 21,600-second CPU/worker-wall allowance, while also
enforcing the stricter remaining absolute wall time. Record units and rounding;
never round a protective ceiling upward. Kernel grace or termination allowance
must not be presented as extra permitted campaign work. Retain actual start/finish
and resource receipts after the new attempt rather than claiming future usage.

Use one existing workstation process/thread and 2 GiB throughout. Matrix limits
remain 4,096 original rows and 64 joint columns. No paid capacity, EKS/IsoLab
job, cloud build, pool change or new financial allowance is authorized. Account
telemetry is unknown. These guards protect the machine and preserve the explicit
bounded repair; they assert nothing about the mathematical lead's status.

## Custody, approval and exact readiness

Publish the original failed raw record and explicit unknown/incomplete export
before rendering its report/PDF. Parent owns official S3 storage, original/archive
hashes and remote verification. The corrective input manifest references original
A9 source/protocol/release/execution and failure-prefix artifacts by hash, as
well as all original A7/A8 solver/control inputs. Retain the original assessment
unchanged; create a new readiness assessment for the corrective bytes.

Before any additional native mathematics, parent must publish exact runnable
corrective source/dependency/input/configuration and command, complete the actual
JSON-roundtrip software regression, obtain administrative exact-byte readiness,
freeze a fresh source-bound corrective protocol, obtain a current real canonical
S3 checkpoint/gate and issue/publish an explicit corrective root release. Use new
study/protocol/run paths; no mutation or reuse of original release authority.
Current actual bindings, including changed protocol/checkpoint tooling, apply.

The later report/database/benchmark distinguishes clean-panel equivalence and
vectors from cumulative attempts/calls/resources and observed unverified prefix
work. It preserves all historical evidence and does not claim an executed launcher
or review that did not occur. KB remains unavailable under the previously recorded
explicit direct-source fallback. Configured role resolution is unverified; no
model/provider/probe, full-ledger or staffed scientific review claim is made.

Final approval is pending exact runnable bytes, concrete remaining-resource guards,
input/cost bindings and the regression result. No user reapproval is requested;
standing authorization covers completing this bounded corrective contract.

## Exact-byte administrative readiness, final corrective source

The final assessment binds published source
`d8c25fa8cf20dc94ed627e1742a57ca401dd569f` and the SHA maps in
`admission-assessment.final.json`. All 24 source bindings, nine explicit input
bindings and content-addressed parent/control/failure artifacts match. The
original core differs only in its importlib module alias; the driver is
byte-identical. The checker normalizes only the temporary representative-map
keys. Values, complete kernels, certificates and exact arithmetic controls stay
strict. The prospective metadata validates with zero schema/lint findings.

The inspection found an additional custody issue before freeze: a stopped new
pass could have completed outputs without a finalized case file. The final
exporter now charges all journaled completed outputs, failed solver phase
prefixes and shared projection, independently of finalized verified records.
A hard-killed or otherwise incomplete pass explicitly retains unknown work even
without a terminal failure event. The prior four outputs remain unverified and
charged. A completed new panel means 1,152 verified calls; the campaign then has
1,156 observed completed calls across two attempts. Further failure retains its
actual prefix and does not authorize another attempt.

The supervisor recomputes the floored remaining allowance at actual launch from
the root release cap, original absolute deadline and prior CPU/wall use. Both
CPU soft/hard limits equal that allowance, and timeout or supervisor error kills
the process group immediately. There is no extra scientific-work grace. Actual
termination and resource receipts remain authoritative; shared-host wall clocks
remain invalid for performance inference.

The parent's final software receipt records 78 controls passed in 1.51 seconds,
including the actual JSON old-fail/new-pass, altered-value/counter refusals,
stopped-prefix accounting and hard-kill coverage controls. This delegation read
those controls and reran only the metadata export test: one passed in 0.23
seconds. It did not execute tiny solver mathematics or any native case.

This is administrative approvability for the existing standalone route, not an
execution release, official ledger approval, model verification or independent
scientific review. Parent must publish this assessment, freeze the fresh
prospective protocol against the exact source, complete the current actual S3
checkpoint and explicit committed root release, then use the admitted supervisor
through the run skill. The old contract and failure records remain unchanged.
