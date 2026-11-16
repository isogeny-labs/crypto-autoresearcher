# Independent v5 source review

TASK-20261104-448845 · BATCH-e9f035 · 4 November 2026

**The source and public-workload joints hold at the declared fixed-software scope; the custody joint breaks on static reconciliation of actual child exits.** All results here are unverified assertions; no CI-signed PCC standing or execution proof exists. [pcc:unverified]

| Joint | Scoped result |
| --- | --- |
| J-source-authority | Holds: exact59source closure and actual launch identity controls refuse reseals; real production admission remains unexecuted. [pcc:unverified] |
| J-public-workload | Holds: original full48static schedule, fixed two-child workload, both wrong scalars and both wrong prepared bases checked. [pcc:unverified] |
| J-custody-lifecycle | Breaks: static checker accepts invented complete child exits against held-fixed trusted failure waits; tested cleanup itself holds. [pcc:unverified] |

## Concrete custody counterexample

An actual unchanged native `execute_trial` fixture ran candidate nonzero and a genuinely failed baseline; finalized `root-custody.json` records both `driver_reported_wait.returncode = 1`, and the native receipt remains `infrastructure_error`. [pcc:unverified]

The untouched same-path static checker first returned0 with `operational_status: incomplete`. [pcc:unverified]

With the trusted root file held byte-exact, I transplanted only this review’s earlier valid raw output for the identical disclosed public input/plan, aligned its summary provenance, set both child process returncodes/acks to0 and operational completion true, then resealed child files, registry and typed export. [pcc:unverified]

The unchanged static checker returned0 and `operational_status: complete`, although the trusted closure still says both exits were1. [pcc:unverified]

`observer.py:123` writes `closures[arm].process_sha256` and `driver_reported_wait`; `load_custody` at lines140–142 reads the current process but checks only launch facts, leaving both closure fields unreconciled. [pcc:unverified]

`check.py:32` checks the child ack against the child’s own returncode, so consistent child resealing crosses this missing comparison. [pcc:unverified]

The narrow next fix is to compare current process bytes and exit/ack fields with the held-fixed closure before deriving completion, retaining all other source, launch, public and lifecycle guards. [pcc:unverified]

The exact witness is `raw/custody-exit-counterexample.json`, helper `helpers/custody_exit_attack.py` SHA256 `08bdd4cf18f59a746ecb036c19823cefbd111e64e36a43121e4c92e13bf3ed1e`, with full before/attacked trees in the checks capsule. [pcc:unverified]

## Observed controls

All95frozen logical/stored identities match; own AST scan reconstructs44Python files and exactly59capture keys before imports, and all59 remain unchanged afterwards. [pcc:unverified]

All50current source-archive stored bindings match when the captured R2 queue is used for its immutable binding; current queue differs only by the two completed states and actual archive binding. [pcc:unverified]

The final431,983,729-byte delivery matches `d2c10e4e…65950d`; all3pool compressed/tar SHA, gzip CRC and19,419chunk SHA checks completed, and only3bounded members were restored. [pcc:unverified]

Fixed F11/F23 execution produced16setups,16singles,20traces/intents and24cells, two distinct physical children, all six `(t,e)` cells and BSGS answers `[7,7]` for **two targets**. [pcc:unverified]

Static48 enumeration gives216setups,345,600singles,36,864traces/intents and73,728cells from24calibration curves×8arms×(1800singles+128starts), plus24confirmation curves×64targets×8replicates×6cells. [pcc:unverified]

29same-path source/public/process/custody/envelope mutations were refused with trusted custody held fixed, including scalar7→0/8, prepared base→invalid[0,0]/valid2G, native/transitive source omission, extra/altered captures and forged PID/parent/start/argv/input. [pcc:unverified]

Seven additional structural/duplicate-key controls refused malformed metadata; seven bounded-child controls retained actual partials for nonzero, timeout, TERM→KILL, log/file/tree caps and document128, while a genuine failed typed export remained accepted as incomplete. [pcc:unverified]

All18lifecycle controls behaved as expected: six12-second active-worker watchdog/expiry cases across candidate/baseline/generator yielded12actual adopted service+selected-worker waits; nine active helper exception/TERM/KILL cases and three delayed-install races yielded12more actual worker waits. [pcc:unverified]

Earlier completed candidates in baseline cases have their own ordinary direct waits and are never counted as adopted waits; only the candidate marker supplies an entry timestamp. [pcc:unverified]

The retained producer six2-second cases remain failed active-worker coverage; the corrected producer six and this independent six do not retroactively turn them into passes. [pcc:unverified]

## Scope, procedure and evidence

This review made0scientific runs/draws,0newIDEA/EXP and no source/native/schema/gate edits, network/storage writes or official status changes. [pcc:unverified]

The unchanged native fixture uses explicit synthetic software authority; actual allocated production admission, full-cost/counter/isolated-clock qualification and full48RSS/storage fit remain future qualifications. [pcc:unverified]

The trust boundary is the pinned root driver/observer, kernel `/proc` and held-fixed finalized custody file; arbitrary replacement of that entire boundary, hostile sameUID isolation and cryptographic history authentication are outside this fixture claim. [pcc:unverified]

Initial orientation displays had no persisted live read timestamps and some truncated output; complete byte capture began before target imports/tests, and the attestation distinguishes byte/AST/semantic scope. [pcc:unverified]

A reviewer sys.path error after a successful native positive, two exploratory metadata decoding/path errors a queue-diff granularity assertion and an initial Typst syntax error are preserved; none is presented as a source failure or silently retried. [pcc:unverified]

Sources read first: frozen handoff/plan/statement, retained historical v4 counterexamples, primary Linux `PR_SET_PDEATHSIG`/`PR_SET_CHILD_SUBREAPER` descriptions and Python Popen excerpts in `lifecycle-references.json`; current PCC guidance was read separately from the774-based source freeze. [pcc:unverified]

Editable Typst/diagram/render/test sources, commands, environment overrides, logs, failures, partials, actual wait/OS facts and selected restored historical bytes are embedded losslessly in `checks.json`; the producer delivery is referenced by hash and is not duplicated. [pcc:unverified]

The actual native independence command uses the final read-attestation and external literal plan pin `7603d65f28b31d42fa6f4d249c62542d7e786f2ce61f750f11445f6369df4ed7`; its output is retained in the checks capsule. [pcc:unverified]

No canonical mathematical graph changes: original math/host pins and schedule remain unchanged; `diagram.svg` depicts only this software custody seam. [pcc:unverified]

## Review attestation

The authoritative machine attestation is `read-attestation.yaml`; it records all3owned joints, per-joint verdicts, actual read scope, no same-round sibling report reads and unverified/null serving-model status. [pcc:unverified]

```yaml
review_attestation:
  task_id: TASK-20261104-448845
  session: /root/production_source_review_v5
  role: validator
  requested_policy: review-adversarial
  requested_reasoning_effort: xhigh
  serving_model: null
  model_verified: false
  fallback_used: null
  fallback_evidence: No serving-model doctor evidence obtained; no inferred model
    or fallback claim.
  authored_v5_source: false
  joints_owned:
  - J-source-authority
  - J-public-workload
  - J-custody-lifecycle
  verdicts:
    J-source-authority: holds
    J-public-workload: holds
    J-custody-lifecycle: breaks
  sources_read:
  - .claude/skills/coordinate/SKILL.md
  - .claude/skills/research-visuals/SKILL.md
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-design/materialized-v5-before-integration/driver.py
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/DEL-selected/work/development-01/stderr.log
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/DEL-selected/work/integration/active_lifecycle_six.py
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/DEL-selected/work/integration/integration_suite.py
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/new-main-policy-fb9/.github/workflows/pcc-gate.yml
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/new-main-policy-fb9/AGENTS.md
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/new-main-policy-fb9/docs/SABOTAGE_RESISTANCE.md
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/new-main-policy-fb9/docs/agent-runtime-core.md
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/new-main-policy-fb9/docs/lab-contract.md
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/new-main-policy-fb9/docs/pcc.md
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/dispatch_queue.json
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/queue-after.json
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/source-archive-bind-api/receipt.json
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/source-archive-bind-command.json
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/source-archive-bind.stderr.txt
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/source-archive-bind.stdout.txt
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/source-archive-completed-queue.json
  - /workspace/classical-ecdlp-endpoint-reuse/production-repair-20261104-review/TASK-20261104-448845/captures/root-queue/source-archive-release-api/receipt.json
  - AGENTS.md
  - agents/coordinator.md
  - agents/executor.md
  - agents/validator.md
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/archives/TASK-20261030-f1dfba/receipt.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/composition/observations.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/composition/proposed-ledger.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/fixed-fixture-input.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/review-plan.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/checks.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/diagram.svg
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/read-attestation.yaml
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/report.md
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/report.pdf
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/source-review.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/visual-inspection.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/statement.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/actual-source-storage-7cafcd/effective-handoff-addendum.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/archives/TASK-20261104-fcd2f6/receipt.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/declaration.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/design-note.md
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/dispatch_queue.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/fixed-fixture-input.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/focus_queue.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/frozen-inputs.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/ids.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/lifecycle-references.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/native-closure.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/native-integration-0d3554/effective-handoff-addendum.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/orientation-capture.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/plans/TASK-20261104-448845.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/plans/TASK-20261104-70efca.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/plans/TASK-20261104-abea09.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/plans/TASK-20261104-b846bb.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/plans/TASK-20261104-fcd2f6.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/resource-control-scope.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/review-plan.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/source-artifact-paths.json
  - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/statement.json
  - docs/agent-contract-extended.md
  - docs/agent-contract-supplement.md
  - docs/artifact-storage.md
  - docs/artifacts.md
  - docs/concurrent-goal-lanes.md
  - docs/confound-control.md
  - docs/experiment-protocol.md
  - docs/lab-contract.md
  - docs/research-budget-policy.md
  - experiments/EXP-ECDLP-787704/protocol.json
  - harness/classical_ecdlp_controlled_followup/cohort.py
  - harness/classical_ecdlp_controlled_followup/compute-plan.json
  - harness/classical_ecdlp_controlled_followup/constructor.py
  - harness/classical_ecdlp_controlled_followup/curve.py
  - harness/classical_ecdlp_controlled_followup/engine.py
  - harness/classical_ecdlp_controlled_followup/host/reference.py
  - harness/classical_ecdlp_controlled_followup/host/verify.py
  - harness/classical_ecdlp_controlled_followup/prior-exclusions.json
  - harness/classical_ecdlp_controlled_followup_v4/.artifacts.json
  - harness/classical_ecdlp_controlled_followup_v4/baseline.py
  - harness/classical_ecdlp_controlled_followup_v4/candidate.py
  - harness/classical_ecdlp_controlled_followup_v4/check.py
  - harness/classical_ecdlp_controlled_followup_v4/cohort_adapter.py
  - harness/classical_ecdlp_controlled_followup_v4/delivery.json
  - harness/classical_ecdlp_controlled_followup_v4/delivery.json.blob.json
  - harness/classical_ecdlp_controlled_followup_v4/driver.py
  - harness/classical_ecdlp_controlled_followup_v4/export.py
  - harness/classical_ecdlp_controlled_followup_v4/fixtures.json
  - harness/classical_ecdlp_controlled_followup_v4/format-contract.json
  - harness/classical_ecdlp_controlled_followup_v4/interface.json
  - harness/classical_ecdlp_controlled_followup_v4/resource-envelope.json
  - harness/classical_ecdlp_controlled_followup_v4/source-manifest.json
  - harness/classical_ecdlp_controlled_followup_v4/test_contracts.py
  - harness/classical_ecdlp_controlled_followup_v5/.artifacts.json
  - harness/classical_ecdlp_controlled_followup_v5/.gitignore
  - harness/classical_ecdlp_controlled_followup_v5/baseline.py
  - harness/classical_ecdlp_controlled_followup_v5/candidate.py
  - harness/classical_ecdlp_controlled_followup_v5/check.py
  - harness/classical_ecdlp_controlled_followup_v5/cohort_adapter.py
  - harness/classical_ecdlp_controlled_followup_v5/delivery.json
  - harness/classical_ecdlp_controlled_followup_v5/delivery.json.blob.json
  - harness/classical_ecdlp_controlled_followup_v5/driver.py
  - harness/classical_ecdlp_controlled_followup_v5/export.py
  - harness/classical_ecdlp_controlled_followup_v5/fixtures.json
  - harness/classical_ecdlp_controlled_followup_v5/format-contract.json
  - harness/classical_ecdlp_controlled_followup_v5/interface.json
  - harness/classical_ecdlp_controlled_followup_v5/lifecycle.py
  - harness/classical_ecdlp_controlled_followup_v5/observer.py
  - harness/classical_ecdlp_controlled_followup_v5/public_verify.py
  - harness/classical_ecdlp_controlled_followup_v5/resource-envelope.json
  - harness/classical_ecdlp_controlled_followup_v5/source-manifest.json
  - harness/classical_ecdlp_controlled_followup_v5/source_closure.py
  - harness/classical_ecdlp_controlled_followup_v5/test_contracts.py
  - ledger/corrections/schema-supersessions/20261030/ledger__evidence__EV-ECDLP-78ed38.comparison-ids-v2.yaml
  - ledger/decisions/DEC-20261030-ffb927.yaml
  - ledger/decisions/DEC-20261104-0d3554.yaml
  - ledger/decisions/DEC-20261104-7cafcd.yaml
  - ledger/decisions/DEC-20261104-ac9548.yaml
  - ledger/evidence/EV-ECDLP-78ed38.yaml
  - ledger/goals/GOAL-ECDLP-e70832/goal.yaml
  - ledger/handoffs/TASK-20261104-448845.yaml
  - ledger/handoffs/TASK-20261104-70efca.yaml
  - ledger/handoffs/TASK-20261104-abea09.yaml
  - ledger/handoffs/TASK-20261104-b846bb.yaml
  - ledger/handoffs/TASK-20261104-fcd2f6.yaml
  - ledger/hypotheses/H-ECDLP-6674c9.yaml
  - orchestration/__init__.py
  - orchestration/adapter/__init__.py
  - orchestration/adapter/batch.py
  - orchestration/adapter/config.py
  - orchestration/adapter/manifest.py
  - orchestration/adapter/prompt_cache.py
  - orchestration/adapter/resolver.py
  - orchestration/adapter/transport.py
  - orchestration/fast_yaml.py
  - orchestration/model-bindings.yaml
  - orchestration/model-policies.yaml
  - orchestration/research-priority.yaml
  - orchestration/research_budget.py
  - orchestration/roles.yaml
  - problems/classical-ecdlp-full-cohort-production-route.md
  - schemas/experiment-export.v1.json
  - schemas/experiment-protocol.v1.json
  - schemas/experiment-review.v1.json
  - tools/allocate_id.py
  - tools/artifact_store.py
  - tools/build_frontier_map.py
  - tools/check_review_independence.py
  - tools/ecc_priority.py
  - tools/experiment_execution.py
  - tools/experiment_preapproval.py
  - tools/experiment_protocol.py
  - tools/fast_yaml.py
  - tools/goal_lanes.py
  - tools/newest_experiments.py
  - tools/research_dispatch.py
  - tools/review_phase_seals.py
  - tools/run_supersession_registry.yaml
  - tools/schema_supersession_registry.yaml
  - tools/sparse_checkout.py
  - tools/task_recovery.py
  - tools/validate_dispatch_reference.py
  - tools/validate_ledger.py
  - tools/validate_ledger_baseline.txt
  read_sibling_reports: false
  blind_rederivation_required: false
  read_scope:
    semantic_foundation:
    - AGENTS.md
    - docs/agent-contract-extended.md#literature-first
    - agents/validator.md
    - .claude/skills/review-evidence/SKILL.md
    - .claude/skills/research-visuals/SKILL.md
    - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/statement.json
    - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/resource-control-scope.json
    - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/review-plan.json
    - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-e9f035/lifecycle-references.json
    - coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-d9a94d/reviews/TASK-20261030-e6c474/report.md
    - current new-main-policy-fb9 AGENTS17/docs/pcc.md/docs/SABOTAGE_RESISTANCE.md
    ast_before_imports: 44Python files; exact59 closure, raw/independent-closure.json
    captured_bytes_only_scope: Not all95frozen files were semantically read; preflight
      records exact byte/hash scope. Source inspection focused on all11v5 Python files,
      unchanged native execute_trial/run_process/complete_manifest, original cohort
      jobs, BSGS-before-oracle ordering and assigned joints.
    primary_document_scope: Locally retained primary Linux PDEATHSIG and CHILD_SUBREAPER
      DESCRIPTION/CAVEATS plus Python Popen preexec/start_new_session/process_group/timeout
      excerpts; no new retrieval or full-manual read claim.
    historical_hardening_sources: Historical v4 report/counterexamples and v5 producer
      source/integration helper are deliberately permitted by frozen plan; no sibling
      review report in this new round.
  procedure_deviations:
  - Initial orientation displays occurred before persisted read instrumentation; some
    tool output was truncated. Their exact session transcript is external to this
    capsule. No retrospective orientation timestamps or full semantic read of every
    captured byte are claimed.
  - Before target imports/tests, the preflight helper actually read/hash-captured95
    frozen payloads and59 runtime files. Its small text/source snapshots are retained.
    Large historical delivery payloads were hashed without duplicating them.
  - 'One reviewer helper initially omitted the old engine directory from sys.path:
    native execute_trial had already returned output_validated, then static cohort
    import failed. The failed helper/command/stdout/stderr and positive tree remain
    preserved; the corrected static pass ran in joint_controls.py with an explicit
    path.'
  - Two exploratory metadata inline attempts failed (root proof tar treated as JSON;
    Path+string concatenation). A later queue-helper first assertion treated50 added
    digest keys as one dictionary delta; its exact failed version/command/error are
    retained. The final comparison groups only those50 authorized additions and the2
    states/2 commit fields.
  - No final source or native code/schema/gate was edited. Source release/Git history/cloud/network/storage
    custody remain root-owned; this worker cross-checked current stored bytes/computed
    Git blob OIDs and root-provided immutable publication evidence without making
    independent remote or historical Git requests.
  - The counterexample deliberately retains an isolated attacked tree with altered
    child records. Its actual native receipt remains infrastructure_error. It is evidence
    of a static checker reconciliation break, not an official run, scientific draw
    or production-admission success.
  pcc_standing: unverified
  qualification: All result assertions are unverified assertions under current PCC
    guidance; native independence checks consistency of declarations, not serving
    identity, truthful reading, signatures or execution proofs.
  recorded_at: '2026-11-04T19:36:08.373622+00:00'
```
