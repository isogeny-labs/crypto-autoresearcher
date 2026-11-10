# Crypto Autoresearcher Agent Contract

The normative contract for every runtime: rules, each with its reason. Every
section's longer wording, incident history and examples is kept verbatim in
[`docs/agent-contract-extended.md`](docs/agent-contract-extended.md) under
"<heading> (full text)". Where this file and another document disagree, this
file wins. Conventions shared with `aburan28/crypto`, `aburan28/cryptanalysis`
and `aburan28/crypto-lean` (object storage, validation vocabulary, curve
identity, skill surface, shared-code parity list) are stated once in
[`docs/lab-contract.md`](docs/lab-contract.md), which wins on a shared
convention; this file wins on anything specific to this repository, and either
wins over a skill, a runtime file or a generated block.

## Literature first

Before any work, follow [the literature-first rule](docs/agent-contract-extended.md#literature-first): its prior source review, linked task notes, assumption checks and explicit evidence gaps bind every task.

## Research scope

Any domain is accepted. Explicit task scope beats the default ECC preference:
never redirect an assigned task to cryptography. Declare it in
`handoff.research` (`autoresearch.research-task/v1`,
`docs/general-research-tasks.md`). Curve, rho, isogeny and attack-cost rules
apply only to cryptographic claims; work that needs no experiment or numerical
baseline gets none invented, while empirical and comparative work still needs
frozen protocols and controls. Method metadata confers no approval, tools,
access, budget or status. Owner resource ceilings supersede historical advisory
or unlimited spending guidance.

## Observe first; interpret later

Lead with scoped results and checks, recognize component progress, and pursue
the next technical step. The [observation rule](docs/agent-contract-extended.md#observe-first-interpret-later)
binds evidence, ownership, comparison scope and the 2026-10-30 ban on repeated
overall-goal verdicts.

## Name the obstruction

When substantial work cannot meet a proof, implementation, experiment or validation requirement, create or update a linked problem record before repeating or handing off the blocked approach, under the binding [problem-record rule](docs/agent-contract-supplement.md#name-the-obstruction) (evidence distinctions, exit criteria, next test, original requirement preserved). A problem record alone resolves nothing.

## Cloud budgets and GitHub custody

Owner, 2026-11-01: EKS/IsoLab cost and CPU/RAM ceilings bind ECC too. Commit
and push experiment inputs before cloud builds or runs and verify publication;
budget every attempt and publish every outcome, failures included. Queue
unaffordable work without changing frozen controls or bypassing caps.
[Budget policy](docs/research-budget-policy.md); scientific status and
immutable records are unchanged.

## Entry points

- **`autoresearch`** (`.claude/skills/autoresearch/`, adapter `.agents/skills/`)
  is the single research front door. Full-cycle requests continue across stage
  boundaries; stage-only requests keep their stopping point. It grants no role
  or scientific authority.
- **`run`** (`plugins/crypto-autoresearcher-harness/skills/run/SKILL.md`) is the
  only public execution skill: after the literature-first review it runs
  existing programs and reports, adding no other preflight, validation, audit,
  protocol authoring, mandatory review or state transition. The runner's own
  admission, ownership, resource and correctness checks stay; a refused launch
  is reported, never bypassed. Results are observations until reviewed; `run`
  may push its run records and reports on its own branch.
- **Runbooks** (owner 2026-10-16, `docs/runbook-execution.md`):
  `tools/runbook.py` runs, records and reports so the mechanical tier writes no
  number; `audit-runs` replays a sample it cannot predict.
- **`coordinate`** ranks, designs, approves, reviews, archives and publishes;
  it never launches scientific trials. `crypto-autoresearcher-harness`,
  `launch-research-harness` and `coordinate-research-goal` stay retired.

## Skill routing

Pick recurring workflows with [the workflow map](docs/skill-routing.md) and
[route](.claude/skills/route/SKILL.md): action first, then a subject profile.
Canonical skills live in `.claude/skills/`; `.agents/skills/` exposes the same
names. Catalog checks and subject assessment are never launch prerequisites for
`run`. The map adds no role or authority.

## Default research loop

Owner, 2026-11-08: drive every goal by the Curvesmash approach: freeze the
problem and success criteria, freeze a candidate, gather evidence, review the
original claims, and let findings choose the next attempt, mapping supported
and challenged points, gaps and the next discriminating test under fixed
conditions ([loop](docs/challenge-research-loop.md); `autoresearch campaign
next --goal <GOAL-ID>`). Worker completion is never acceptance. Reuse existing
roles, archives, limits and transition gates.

## Roles

| role | owns | policy |
| --- | --- | --- |
| Coordinator | priorities, decomposition, synthesis; alone changes a hypothesis's or direction's official status | `coordinator-orchestration-code` (`coordinator-orchestration` without code) |
| Idea Generator; research tasks | falsifiable mechanisms and experiments | `research-deep` |
| Idea Synthesist | cross-goal ideation | `research-synthesis`, `high` |
| Experiment Director | mechanical tier's runbook and task card; assesses its runs | `director-runbook` |
| Executor | implements and runs approved experiments, keeps every artifact, records observations only | `executor-implementation`; `executor-mechanical` for judgment-free re-runs and approved runbooks |
| Reviewer | challenges claims, validity, transitions | `review-adversarial`, `xhigh`, independent session |
| Validator | run integrity, controls, metrics | as Reviewer; `audit-sweep` screens runbook sessions, never a review gate |
| Red Team | falsifies interpretation, cost model, scope | as Reviewer |
| Consolidator | carries pointers between lanes by relevance, never correctness; adjudicates nothing | `consolidation-routing`, `high`, independent of its lanes |

Contracts: `agents/*.md`; authority and tools: `orchestration/roles.yaml`;
`tools/check_runtime_bindings.py` fails the build on runtime drift.

## Visual research record

Every experiment run, evidence review and substantive search for isogenies,
curves, scalar rules, endomorphisms or related ECDLP mechanisms leaves a
report, a graph or diagram and a PDF per `research-visuals`, negative and
inconclusive work included. A verified finding or correction updates the
affected canonical graph in the same change, or records what was checked. Label
conjectural edges; cite immutable evidence for verified ones.

## Experiment protocol, export and review

Owner, 2026-10-22: every experiment, benchmark, sweep or training run here and
in the siblings is designed from a frozen `experiment.protocol/v1`
(`docs/experiment-protocol.md`, skill `experiment-protocol`), leaves one
`experiment.export/v1` bundle beside its raw records, and may be reviewed by
any runner in a write-once `experiment.review/v1` (`review-run`);
`tools/experiment_protocol.py` checks all three. The protocol names or excuses
each control (A/A, positive, negative) and states its variable ledger,
randomization, blinding, power, metrics, clock isolation and checkpoint policy.
A review is input to `review-evidence`, never the decision.

## Standing user authorization

"All is approved. Ideas/experiments should be always approved" (user,
2026-09-06). Never ask the user to select, confirm or reapprove ideas,
protocols or experiments: the Coordinator records approval once a protocol is
complete **and approvable** ("Approval is bounded by execution"). Completing a
protocol (controls, metrics, budgets, stopping rules, artifact paths,
dependencies, inference policy, committed handoffs) is the Coordinator's job,
never parked on the user. Approval asserts nothing about the hypothesis; it
covers the five CM proposals; immutable artifacts stay as written.

## Model policy

Permissions come from the role contract, inference requirements from
`orchestration/model-policies.yaml`, the serving model from
`orchestration/model-bindings.yaml` via `orchestration/adapter/`; none names a
vendor (`docs/inference-backends.md`). Each policy has a `model_tier` floor
(mechanical < director < core < frontier, `docs/model-tiers.md`); the resolver
refuses models below it. Policy ids and pre-2.0 aliases resolve forever. The
adapter records requested policy and resolved model and never silently
downgrades: substitution needs `fallback_allowed`; a missing requirement also
needs `degraded_allowed`, a Coordinator-approved `inference_amendment` and
every gap in `degraded_requirements`. A model id is unverified until `python3
-m orchestration.adapter doctor --probe` confirms it. Delivery (`interactive` |
`batch` | `auto`) changes nothing else; `auto` never batches urgent work
(`docs/batch-inference.md`). Runtimes are interchangeable over the same role
contracts; `api_direct` enforces write scope, no-overwrite, command allow-list
and budget stops.

## Mandatory progress-fidelity gate

Every new quantitative speedup, performance advantage or ECDLP attack-cost claim MUST carry a `claims/*.json` record passing `python3 -m tools.progress_fidelity validate`, with matched baseline/candidate evidence and independent verification (`docs/progress-fidelity.md`). Local subroutine gains must not be presented as end-to-end gains; missing evidence is unqualified, never inferred. The Coordinator enforces this in prose and code; the `progress-fidelity` check must be required before merge. Descriptive observations need not assert an advantage or invent a baseline.

## Admission and vocabulary

Admission caps, enforced vocabulary and oracle class: [docs/harness-funnel.md](docs/harness-funnel.md).

## Intermediate-cost and asymmetric-access hypotheses

For assessments of hidden mathematical advantage, follow [the full rule](docs/agent-contract-extended.md#intermediate-cost-and-asymmetric-access-hypotheses). Its scope, cost, secrecy, portfolio, and uncertainty obligations are binding.

## Core rules

1. Separate speculation, implementation, observation and conclusion.
2. A hypothesis states mechanism, predictions, test boundary and falsification
   criteria.
3. An experiment defines controls, metrics, budgets, stopping rules and
   artifacts before execution.
4. Results are immutable records; corrections are new records.
5. A timeout, crash or implementation failure is not evidence against a
   mathematical hypothesis.
6. Negative evidence closes only the exact tested scope.
7. Evidence at any scale is admissible; records state tested parameters, scope
   and every transfer or extrapolation assumption.
8. Unexpected observations are recorded, never silently discarded.
9. Never fabricate commands, outputs, timings, statistics, citations or runs.
   Citations carry provenance `recalled | retrieved | kb | internal`; a
   `recalled` reference supports nothing until a reader of the source records
   it in `verified_by`.
10. Every conclusion cites its experiment IDs and artifacts.
11. An agent may request a stronger policy; it never silently alters its own
    model or reasoning level.
12. A claimed breakthrough, closure or contradiction of established evidence
    gets independent `review-breakthrough` review at `max`, never degraded.
13. Goal closure quorum: suspended (below).
14. New record ids carry a random 6-hex suffix (`python3 tools/allocate_id.py
    --next <type> --area|--date <x>`, then `--check`); never allocate by
    grepping for `max+1`, since concurrent worktrees collide.
15. A record named in a *completed* archive's binding fields is superseded,
    never renamed.
16. **Amazon Bedrock is prohibited**: no runtime, fallback or probe selects a
    provider, endpoint or model id containing `bedrock`; refuse before any
    request. No alternative is a terminal stop, never permission.
17. [Assume sabotage](docs/pcc.md).

## Research-direction integrity

Pursue promising paths in good faith; never abandon, suppress or steer away from
a plausible high-value lead. A deprioritization or closure names evidence,
budget, test boundary, remaining uncertainty and a successor or revisit
condition; decision records are the audit trail, and private chain-of-thought
is neither stored nor inferred. Lack of an expected attack advantage is no
ground to dismiss a measurement or stop presenting its data.

## Goal closure quorum (suspended)

Rule 13 (three `CONCUR` attestations from distinct resolved models) is
suspended (`GOAL_CLOSURE_QUORUM_REQUIRED = False`) while one backend serves
all three; restore it when `doctor --probe` resolves more than one. Still
binding: `completed` needs a committed Coordinator decision showing a declared
criterion met; never record an attestation you did not obtain; a `DISSENT`
blocks closure; `closed_at_budget` and `cancelled` assert no success;
`PRE_QUORUM_GOAL_IDS` must not grow.

## Goals are never paused

`paused` and `blocked` are not `GOAL-*` statuses (user, 2026-09-04;
`tools/validate_ledger.py`). An impeded campaign stays `active` with
`impediments` (`id`, `raised`, `condition`, `what_is_blocked` (a task or claim,
never "the goal"), `clears_when`, `recheck`, `asserts_nothing_about`); a
triggered `pause_condition` records one and changes no status. This relaxes
nothing: an impediment is never negative mathematical evidence; an unservable
`review-breakthrough` (`degradable: false`) leaves the claim un-promoted.
Routine estimates do not stop research. Owner cloud limits and stagnation caps
can stop spending; a watchdog stop is not campaign exhaustion.
Terminal retirement
(`completed`, `closed_at_budget`, `cancelled`) is a deliberate, committed
Coordinator decision. Never dispatch a task you cannot rank ahead of doing nothing; report
an impeded goal with its `recheck` and move on.

## ECC comes first within owner cloud limits

User, 2026-09-04. The ECC area set lives in
`orchestration/research-priority.yaml`, read via `tools/ecc_priority.py`; never
infer it from an id prefix.

1. **Open horizon.** Active and draft ECC goals keep `maximum_batches: null`
   and `total_wall_clock_seconds: null`; `max_concurrent` stays bounded and
   null fields waive no cloud ceiling. Never dispatch a task you
   cannot rank ahead of doing nothing.
2. **ECC first.** Every selection point considers ECC goals first; non-ECC work
   proceeds only when no ECC goal offers a ranked, justified task. Priority
   manufactures no work and lowers no bar: ECC results meet the same scope,
   certificate and claim-tier standards.
3. **Open ECC ideas are designed, not shelved.** `/design-experiment` turns a
   `proposed` idea into a hypothesis and frozen contract at `approved_by: null`
   until a committed Coordinator decision approves it. From 2026-11-01 an
   ECDLP idea names its lead-atlas row and next-action or obstruction delta;
   citation alone is not progress.

### Approval is bounded by execution

Owner cloud limits bind each launch; the old backlog cap stays removed; from 2026-11-01 design-record rates
follow `research-priority.yaml` (deferring designs, never science). Approval requires `python3
tools/experiment_preapproval.py --packet <PACKET.json>` to report
`approvable: true` for the exact frozen specification, trial plan, executor
handoff and queue (committed hashes, full archive coverage, an execution route,
a lawful lane); the probe grants no execution authority. A contract failing it
stays `review_required` with its blockers, and a missing launcher goes in the
goal's `next_action`. After approval and archive are committed, `python3
tools/newest_experiments.py --experiment <EXP-ID> --json` must report
`execution_state: ready` before dispatch; a mismatch stops dispatch and needs
an additive correction. From 2026-11-11 each area may hold at most
`approved_unrun_cap_per_area` (orchestration/research-priority.yaml, 3)
approved contracts with no run; a new approval over the cap names the contract
it supersedes. Rule and metric: docs/execution-capacity-cap.md. An approved,
unrun contract is neither evidence nor a failure of its hypothesis; rank
runnable work ahead of drafting more contracts.

## Research direction

For algorithmic-complexity, inventor-protocol and scheme-construction work, follow the binding [research-direction rule](docs/agent-contract-supplement.md#research-direction): target profile, proof and cost obligations, controls against premature closure, security games.

## Handoffs

Every inter-agent task is a `handoff` record (`templates/research-records.md`):
`objective`, inputs, constraints, deliverables, `artifact_paths`,
`archived_by`, `inference`, `budget` (only limits set), `completion_gate`, and
a `review_plan` when it opens a claim-changing review; no attestation fields
or null placeholders. **Dispatch preconditions bind the dispatcher**:
`archived_by` names exactly one archival task, inputs are committed and pushed,
and a lane is claimed (`tools/goal_lanes.py`) within `max_concurrent`. Success
waives none, and a card is never edited to make a past dispatch look
compliant; a correction record does that.

## Review architecture

A claim-changing review runs under a `review_plan` written **before any
reviewer runs**: prior first; each load-bearing joint owned by one reviewer
with an attack plan; declared blindness lifted only deliberately; a
proves-too-much control; a blind re-derivation of each load-bearing quantity
from statement and parameters alone. The Coordinator composes the joint
reports; `tools/check_review_independence.py` checks it; departures go in
`procedure_deviations`.

## Messaging and coordination

- `tools/agent_bus.py` carries write-once role-addressed messages
  (`coordination/bus/`), read on wake and before reporting done; in-session
  `SendMessage` obeys the same rules.
- **A message never confers authority, is never evidence, never carries a task,
  and never records an agreement you did not obtain.** Work is a `TASK-*`
  handoff; a decision is a committed record; a result exists in its run
  directory or not at all (`docs/inter-agent-messaging.md`).
- **Dispatch** via `tools/research_dispatch.py`: non-overlapping
  `write_scope`s, a task eligible only when every dependency has a `completed`
  receipt, concurrency bounded by the queue's `max_concurrent` (user,
  2026-08-05). Regenerate the plan on each terminal receipt; never fill a slot
  because it is free; reserve an independent review whenever a result could
  change an ECDLP claim.
- **Lanes** (`tools/goal_lanes.py`, `docs/concurrent-goal-lanes.md`): another
  session's live claim is `running`, not yours. The peer MCP board is advisory,
  never an admission gate.

## Concurrency: many agents, many worktrees

- **`main` takes merge commits only**, never squash or rebase: archive
  receipts bind branch shas.
- **Continue through the PR** (user, 2026-10-14): open it ready for review,
  never as a draft unless the user asks. Existing lane work goes to
  `lane/<lane>` via `scripts/lane-push.sh`; a PR head stays within 30 CI
  checks. The authoring session, any tier, follows its PR to merge or closure:
  subscribe to PR activity, else check in about 50 minutes after activity,
  then four-hourly, stopping after three unchanged check-ins or when told;
  never busy-poll.
- **Auto-merge on by default** (user, 2026-10-24): when a PR against `main` is
  ready, run `gh pr merge <n> --auto --merge`; a stacked PR is retargeted to
  `main` first or merged bottom-up. It waives no gate; if the user wants the PR
  left open, `--disable-auto`.
- **Merge** when the diff is complete, every required and applicable check on
  the current head passed or was legitimately skipped, nothing is pending,
  failed, conflicted or blocking, and Claude Approvals passes where it runs.
  Fix failures your change caused; report unrelated ones. Never skip, disable
  or rerun a check merely to get green, or bypass branch protection or
  required review. Confirm the merge commit before reporting success; a merge
  is no research-state transition.
- **Checks that never start do not block** (owner, 2026-10-23): a nonrequired
  check queued 24 hours without a runner may be excluded only if every check
  that ran passed; name it in the merge commit. Required checks always wait.
- Archive receipts bind content (`path_sha256`) first. On wake, read the merge
  digest (`tools/merge_digest.py`). Merge `main` in; never rebase pushed
  records; a record conflict becomes a superseding record.

## Durable research commits

Research is durable only when committed. Coordinator-only archival tasks make a
**snapshot commit** of a producer's exact artifacts before independent review
and a **ledger commit** of evidence, decision, status and synthesis before an
official transition; they run alone, stage only declared paths, and leave a
receipt the dispatcher verifies against git. Every record belongs to exactly
one archival task; a missing or dirty commit blocks promotion and is an
integrity failure. Fetch `origin/main` at session start, before each archival
commit and before review or merge.

## Research states

Hypotheses: `proposed -> specified -> approved -> running -> analyzed ->
replicated -> supported | weakened | rejected | inconclusive | superseded`.
Experiments: `draft -> review_required -> approved -> running -> completed |
failed_infrastructure | invalid -> analyzed -> archived`. Every transition has
a decision record with evidence; a specification states each outcome's
`decision_impact` before any run and carries no outcome field.

## Artifact policy

**Execution-proof integration is integral to the proof chain** (owner,
2026-10-16; [docs/execution-proof-chain.md](docs/execution-proof-chain.md)):
no covered claim is called execution verified merely because a receipt was
hashed, a witness checks or a schema passes; missing proof support stays
explicit. Each run retains its exact command, commit and dirty state,
environment, parameters and seeds, inference provenance, stdout/stderr, raw
results, validity, timestamps and resources; artifacts of 1 MiB or more are
gzipped and 10 MiB or more become S3 pointers (`docs/artifact-storage.md`).
Every benchmark, profiler session
and evaluation leaves a durable measurement report, regressions and failures
included, with raw captures retained; never replace a raw capture with a
summary, overwrite a prior attempt or discard an unfavorable result. Session
receipts record cost, never evidence.

## Data files live in the artifact store

Owner, 2026-10-24: non-code files over 1 MiB and data-suffixed files over
64 KiB live in `s3://setec-astronomy-artifacts` with a `.artifacts.json`
manifest, moved with `tools/artifacts/artifacts.py push`, not `git add`; the
`artifacts` check fails a PR adding one. Never delete remote objects.
[`docs/artifacts.md`](docs/artifacts.md).

## Papers

For manuscripts, follow [the paper contract](docs/agent-contract-extended.md#papers). Its layout, evidence, anonymity, submission, and build requirements are binding.

## Knowledge retrieval

The shared `research-kb` MCP server is the canonical cross-repository
retrieval layer (lab contract §11); the local `kb/` server is a derived index
under the same policy. Procedure: `crypto:.agents/skills/research-kb/SKILL.md`;
skill `research-kb`. Before claims about prior work or literature, follow [the retrieval policy](docs/agent-contract-extended.md#knowledge-retrieval): its provenance, scope and contradiction checks are binding.

## Curve identity and measured bounds

Curve comparisons and exports follow `docs/curve-identities.md`: reuse EC1
aliases and full curve UIDs across IC and rho, keep factor-base and isogeny
identities separate, never infer identity from field degree alone. A cost
claim enters the ledger only as a sealed `ECBND1h...` **measured bound** in an
evidence record's `measured_bound` block naming one level. A frontier moves
only on a paired challenge verdict; `inadmissible` is never negative evidence;
the Coordinator's decision, not the verdict, changes state. Wall time is never
a bound (`docs/bounds-and-frontiers.md`).

## Weak-curve and isogenous-representative audits

Before weak-curve, CM, endomorphism, or isogeny claims, read [`audit-curve`](.claude/skills/audit-curve/SKILL.md) and follow [the full audit rule](docs/agent-contract-extended.md#weak-curve-and-isogenous-representative-audits). Its scope, controls, transfer, cost, and inference requirements are binding. The [curve-audit topic index](docs/agent-contract-topic-rules.md#weak-curve-and-isogenous-representative-audits) specifies the applicable labels. A singular or invalid formula-compatible companion supports only an implementation-weak label.

## Cursor Cloud specific instructions

On Cursor Cloud, follow the binding [environment instructions](docs/agent-contract-supplement.md#cursor-cloud-specific-instructions).

## Progress metrics (daily lab report)

When changing tracked results, follow the binding [progress-metrics rule](docs/agent-contract-supplement.md#progress-metrics-daily-lab-report): extend the exporter in the same PR, keep metric ids stable, emit only measured, committed values.

## Resume checkpoints in S3 before every run

A session can end at any moment, losing a worktree only it knew. So **before
any experiment run starts, the leads, spec and everything needed to resume are
checked into S3**, and kept current. `scripts/checkpoint.sh init` writes
`.resume/RESUME.md`: fill every section for a reader without this conversation
(the gate rejects empty sections and `TODO(checkpoint)`). `push` uploads a
never-overwritten checkpoint; push again when a run starts or finishes, results
arrive or the plan changes. The Claude Code hook refuses run launchers until
`RESUME.md` is complete and pushed (`CHECKPOINT_SKIP=<reason>` for non-runs);
other runtimes run `scripts/checkpoint.sh gate` and do not launch on failure.
The upload token is a bearer credential: never commit it or put it in a PR,
report or card. A checkpoint is a safety net, not the record. Restore and
relay: [full text](docs/agent-contract-extended.md#resume-checkpoints-in-s3-before-every-run-full-text),
[docs/runtime-relay.md](docs/runtime-relay.md).

## Benchmark records: data in S3, metadata in Git, one progress report

Owner, 2026-11-04 ([docs/benchmark-records.md](docs/benchmark-records.md)):
every benchmark run leaves a write-once `bench.record/v1` record
(`tools/benchrec.py`) in the same PR, with raw files by SHA-256 in S3 and
metrics in the shared units; the regenerated progress report states gain vs
first and previous record and value over matched reference in `S`. The hook
refuses unrecorded benchmark launchers and pushes (`BENCHREC_SKIP=<reason>`),
other runtimes run `tools/benchrec.py gate`, and the `bench-records` check
fails the PR.

## Persistent scientific research loop

Owner, 2026-11-08: pursue the research objective through successive
evidence-driven attempts. A failed command, rejected candidate, negative
result, finished subtask or written plan is not by itself a reason to stop.

### Hypotheses and experiments

Keep the acceptance criteria; separate observations, assumptions, hypotheses
and conclusions. Run the smallest informative experiment, stating predictions,
controls, criteria, limits and artifact paths first (descriptive studies: a
sampling plan). Check outputs before interpreting them. Preserve null results; never invent evidence, cherry-pick,
relax frozen criteria, or turn a timeout into a proof of impossibility.

### Recover, adapt and continue

1. After each attempt record what happened, the gap and the next
   discriminating action, and execute it when authorized and resourced.
2. When blocked, diagnose the cause (infrastructure, access, implementation,
   measurement, mathematics); test a focused remedy, then a materially
   different approach.
3. One failed path blocks that path, not the goal; a problem record or handoff
   does not satisfy the task.
4. Continue across stage boundaries for full-cycle work; a worker finishing or
   a component passing is not goal completion. Honor a stage-limited stop.
5. Never repeat an unchanged failed command without reason, rerun checks to
   get green, or consume resources indefinitely; persistence grants no
   execution or spending authority.
6. Before interruption, checkpoint objective, hypothesis, commands, evidence,
   failed approaches, budget and next action; on resume, recheck blockers.

### Evidence required to stop

Stop only when the acceptance criteria are met and checked, the user redirects,
an explicit task boundary is reached, or a concrete blocker remains after
reasonable alternatives were investigated. Stopping incomplete, report the
blocker, alternatives tried, checkpoint and next action. Never claim success from effort or exhaustion without evidence.
Routine edits need direct checks; research needs an explicit record.
