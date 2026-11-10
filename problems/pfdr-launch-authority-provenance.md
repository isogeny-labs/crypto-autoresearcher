# PFDR launch authority changes after archival commits

- **Status:** investigating
- **Kind:** implementation gap; bounded retry accounting
- **Affected work:** EXP-PFDR-ada71b; GOAL-PFDR-fd09e0
- **Next action owner:** Coordinator and Executor
- **Last updated:** 2026-11-09

## Problem

The frozen driver records live HEAD at completion, while the supervisor requires the launch authority commit. Archiving a completed selftest changes HEAD during the claimed multi-stage execution and invalidates the pilot manifest.

## Evidence and uncertainty

The preserved pilot RUN-PFDR-4fa30b reports commit a8a4f7b0854c6a013670761a1d078552cd7b47bb against launch authority 715df5e6018a7e85b7849d708df9372ed1fa7838. Git shows the former is the latter's immediate child and adds only eleven selftest result files. Original driver implementation/run.py reads HEAD at completion; tools/experiment_execution.py requires the authority commit. This explains the provenance rejection; it does not validate the old pilot scientifically.

The additive candidate [driver](../experiments/EXP-PFDR-ada71b/implementation/run_recovery_20261109.py) validates launch run/trial/plan hash and full commit before work, uses that authority in the manifest, and separately records completion HEAD. Four [regression tests](../experiments/EXP-PFDR-ada71b/implementation/test_recovery_provenance_20261109.py) pass using synthetic temporary fixtures and mocked scientific computation. No new scientific trial has run.

## What would unblock it

- [x] Reproduce differing authority and completion HEAD and verify candidate handling.
- [ ] Publish and approve the versioned source, plan, specification and exact hashes.
- [ ] Reconcile live ownership and checkpoint; admit one replacement pilot and four downstream stages within an explicitly amended seven-attempt total (two prior plus five new), with no further retry.
- [ ] Complete the admitted stages and required output/replay checks; retain failures.

The original valid selftest is reused as an immutable input, never relabeled as a trial under a new plan. The original invalid pilot remains invalid. The [draft recovery](../experiments/EXP-PFDR-ada71b/amendments/recovery-20261109.proposal.json) changes no scientific acceptance criteria.

## Next discriminating step

Complete the prospective recovery packet and run preapproval. Pass permits Coordinator approval and publication, followed by the existing runner admission; failure identifies a concrete remaining preparation requirement. No experimental spending or launch is authorized by this problem record. Recheck after the versioned packet and archive are available.

## Resolution and history

2026-11-09: diagnosed the archival-commit mismatch and tested a prospective source correction. Recovery execution remains unresolved.
