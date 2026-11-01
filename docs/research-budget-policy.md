# Research budgets and machine protection

The owner's 2026-11-01 instruction makes EKS/IsoLab cloud cost limits binding
across research areas, including ECC. It supersedes the 2026-09-06 advisory
spending policy for cloud builds, trials and retries. No stagnation review is
needed to honor an owner-imposed infrastructure or financial limit.

Before spending, commit and push the exact source, protocol, configuration,
seeds, inputs or content-addressed input manifest, and launch command to GitHub.
Verify the exact revision exists there; local commits are insufficient. Use the
`check-experiment-git` receipt described in the shared
[IsoLab cost-control runbook](https://github.com/aburan28/crypto/blob/main/taskq/deploy/eks-karpenter/COST_CONTROLS.md).
The check covers enumerated files; the caller must enumerate all launch inputs.
Current deployed backends do not independently enforce this new check.

Record a finite dollar ceiling, requested CPU/RAM, concurrency, original
absolute deadline and total retry allowance before cloud builds or runs.
Charge builds, queue/idle node time, failed attempts, Spot interruptions,
retries, storage and transfer to the same allowance. Check fresh account-budget
telemetry and charged/reserved lane cost. Unknown or exhausted remaining funds
stop new submissions; record the impediment without changing scientific status.
AWS alerts alone are not a spending stop. Never use another pool, account,
region, provider or renamed retry to evade a ceiling.

The shared desired EKS worker ceiling is 24 vCPUs / 160 GiB: `cpu-spot` gets
16 / 128 GiB, `cpu-l2-spot` gets 8 / 32 GiB. Namespace `isolab` requests and
limits are each capped at 16 CPU / 128 GiB, with eight active pods. Dedicated
ARC/CI NodePools and runner counts default to zero; routine CI uses hosted
runners. These are checked-in desired values, not proof of live enforcement.
Verify the actual Kubernetes objects after an authorized operator applies them.
The MCP overview's compiled-in numbers are not live quota evidence. Karpenter
limits can briefly overshoot during parallel provisioning; they are not dollar
caps. See the shared runbook for apply/readback commands and primary sources.

Queue oversized or competing work without shrinking frozen samples, inputs or
controls. Keep existing active jobs and checkpoints intact; do not evict them
merely to make observed capacity match a new ceiling. Larger capacity or cost
allowances require explicit owner authorization. Normal work inside recorded
allowances needs no repeated approval. Reconcile jobs and durable receipts
before resubmission, and preserve the original deadline and cumulative charges.

After every bounded attempt, publish source/image/input hashes, Job/Pod/build
IDs, commands, resource use, status, cost accounting and checks on the same
experiment branch/PR, including failures, OOMs and timeouts. For large artifacts,
commit hashes, byte counts, durable URIs and extraction/replay instructions.
Preserve immutable records and distinguish estimates from delayed billing data.

Scientific campaign totals may still be null; that means no fixed batch horizon,
not unlimited money or infrastructure. The existing shared stagnation validator
in `orchestration/research_budget.py` remains a scientific policy and is not the
cloud-cost admission mechanism. Memory/concurrency protection and justified
process watchdogs remain binding. Watchdogs stop workers, not campaigns.

## Design-record limits remain separate

ECC has one deliberately separate administrative guardrail, added by user
direction 2026-11-01: a session may file at most 3 new ECC ideas and 1 new ECC
experiment, and the repository may file at most 12 / 6 respectively per UTC
day. This is a design-record process budget, not a scientific spending cap.
It leaves unfiled work queued and never limits executions, replications,
validations, compute batches or evidence follow-up. The distinction prevents
"unlimited ECDLP research" from becoming "unlimited template paperwork".
`tools/ecc_priority.py --process-budget-violations` and
`tools/session_receipt.py` enforce it from its dated cutover.

## Exceptional restriction after months without progress

The minimum is **90 days**. A Coordinator may activate a scoped research cap
under this separate stagnation mechanism only after a committed assessment cites evidence of no meaningful progress
throughout that interval. New measurements, reproducible negative results,
resolved proof obligations and discriminating controls can all be progress;
paperwork counts and elapsed time alone cannot establish stagnation. Missing
telemetry, inactivity or infrastructure downtime is not a finding of stagnation.
No timer automatically retires a campaign or changes a hypothesis status.

The shared policy validates `budget.enforcement: stagnation` only with:

```yaml
stagnation_review:
  assessed_by: coordinator
  decision_id: DEC-YYYYMMDD-abcdef
  assessed_at: YYYY-MM-DD
  last_progress_at: YYYY-MM-DD
  no_progress: true
  infrastructure_only: false
  evidence_refs: [path/to/committed/assessment-evidence.md]
  scope: exact task or lane being restricted
  rationale: evidence of sustained stagnation and alternatives considered
  next_action: concrete successor or test that would clear the restriction
```

The cited decision must be committed, carry `decision: approve`,
`decided_by: coordinator`, the identical `stagnation_review` block, the
current target in `target_ids`, and exact numeric limits in `approved_budget`
(the budget mapping excluding `enforcement` and `stagnation_review`).
Evidence paths must also exist in that committed tree; inline self-grants and
uncommitted files cannot enable enforcement.

The assessment must be at least 90 days after the last documented progress and
no more than seven days old at enforcement. A stale or malformed restriction
must be reassessed, never silently renewed. A Coordinator must reassess when
new progress arrives. This is a review gate, not an automated scientific verdict.
`orchestration/research_budget.py` is the single source of the thresholds.

## What stays frozen

Approval, exact write scope, scientific controls, fixed sample counts, seeds,
locked trial lists, zero-run tasks and immutable receipts still bind. An advisory
run-count estimate does not authorize extra confirmatory samples or fishing for
a favorable result. Scientific changes require an additive amendment; ordinary
continuation within the recorded cloud allowance needs no repeated approval. Never relabel an old
run under the new runtime policy, rewrite archived budgets, or claim a watchdog
was enforced if it was not. New runs record the runtime policy they used.

Old bespoke experiment scripts may enforce their own frozen stopping rules.
Before continuing such a script, the Coordinator makes the minimal additive
amendment separating its scientific stopping criteria from obsolete spending
caps. Such amendments cannot waive current owner cloud-cost ceilings. The shared harness cannot safely rewrite arbitrary historical programs.
