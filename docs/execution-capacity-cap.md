# Execution capacity cap (per area)

Proposal I2 of `crypto:docs/autoresearcher-harness-review-20261110.md`
(§1.1, §4 I2), adopted on the owner's "fix it all" instruction of 2026-11-10.
It reverses the 2026-10-11 removal (commit `304547eb2c`) of the P0.1
capacity gate, which was keyed per goal. The cap is now per area.

## Rule

An approve-kind `coordinator_decision` may not leave an area (the
`EXP-<AREA>-` token) holding more than **3** approved contracts with no run.
An approval that would do so must name, under `supersedes:`, one retired
contract of the same area for each contract it approves. A retired contract
is no longer approved-unrun (superseded, withdrawn or run), or another
specification lists it under `supersedes`. Contracts that a later decision
approved do not count against an earlier one. A target that already ran is a
continuation and does not count as a new approval.

## Record

`orchestration/research-priority.yaml`, top-level
`approved_unrun_cap_per_area: 3`. This is the same record as the 2026-11-01
`process_budget` design-rate rule. Its readers:

- `tools/check_approval_capacity.py` (`check_approval_capacity(ctx)`), run
  by `tools/validate_ledger.py`;
- `python3 tools/portfolio_kpis.py --capacity area:AREA`, which prints the
  backlog, cap and headroom and exits 1 at the cap.

## Dates

- Approvals dated (by id) from 2026-10-07 to 2026-11-10 get **advisories**.
  2026-10-07 is when P0.1 was first enforced.
- Approvals dated from **2026-11-11** get validation **errors**.

## Readiness is the same predicate as admission

`experiment_execution.archive_coverage_gaps(root, plan, task)` is the only
archive-coverage test. `authorize()` refuses on its first gap. The selector
(`newest_experiments.py`) reports a plan with gaps as
`needs_archive_coverage`, never `ready`. The preapproval probe
(`experiment_preapproval.py`) reports the same list as
`archive_coverage_gaps` and returns `approvable: false`. The regression test
is `tests/test_archive_coverage_predicate.py`.

## Metric

- Approved-unrun per area (`portfolio_kpis.py --backlog`, and `--capacity`
  for each area) falls monotonically. The baseline on 2026-11-10 was 1,208 in
  total: ECDLP 145, BINSTD 65, MLKEM 53, SQISIGN 48, AES 45, SSI 45. A swap
  under `supersedes:` keeps an area's count level. Only runs and retirements
  lower it.
- The `needs_implementation_or_plan` share falls to 0 for contracts approved
  after 2026-11-11. The baseline was 74 of 225 selectable rows.

## Falsifier

The rule is falsified if evidence records per week drop while the cap
holds. That would show that execution capacity was the limit all along, not
approvals. The remedy would then be review I3/I9, not more approvals.

## Not covered

- The cap does not make an unapproved packet's launcher dry-run.
- It does not supersede the 17 queues that lack coverage. That remains a
  Coordinator act.

## Relation to the per-goal WIP cap (PR #3180, same day)

`tools/experiment_wip.py` (policy `coordination/experiment_wip_policy.json`,
mode `advisory`, cutoff 2026-11-08) caps approved-unrun contracts at 3 **per
goal** and requires a `first_measurement` block; this document's rule caps them
at `approved_unrun_cap_per_area` **per area** (error from 2026-11-11). They
measure the same backlog at two granularities and both are registered in
`docs/harness-mechanisms.yaml` with a 2026-12-10 review date: the one whose
metric moves the approved-unrun count survives, the other is retired, so the
program does not keep two caps for one rule.
