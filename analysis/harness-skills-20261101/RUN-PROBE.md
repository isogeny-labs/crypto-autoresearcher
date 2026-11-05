# `/run` probe: first approved-unrun candidate and its blocker — 2026-11-01

Follow-up to `REPORT.md`. The previous pass found `newest_experiments.py`
returning 0 rows because the 11 new `EXP-*` are `review_required` and the
sparse checkout hides the rest. This pass looked for an **approved, unrun,
cheap** experiment and tried to execute it.

## Candidate selection

- Approved specifications on `HEAD`: 1,632.
- Approved specifications with a `runs/` record: 625.
- Approved and **unrun**: 1,170.
- Of those, ECC-area experiments with a `trial-plan.json` or `runbook.yaml`:
  13. The only small one is `EXP-SSI-db46fa` (toy orbit-deficit census over
  `F_361`, one trial, `wall_clock_seconds_per_run: 120`, 512 MB).

Materialized with:

```sh
git sparse-checkout add experiments/EXP-SSI-db46fa
```

`tools/experiment_execution.py status --plan
experiments/EXP-SSI-db46fa/trial-plan.json` reports:

```json
{"experiment_id": "EXP-SSI-db46fa", "required": 1, "remaining": 1,
 "planned": 1, "measurement_complete": false,
 "trials": {"orbit-deficit-p19": "planned"}}
```

## Launch attempt and exact refusal

```sh
python3 tools/experiment_execution.py run \
  --plan experiments/EXP-SSI-db46fa/trial-plan.json --owner opencode --epoch 1
```

```text
execution impediment: dispatcher refused execution: dispatch error:
queue.schema must be crypto.autoresearch.dispatch_queue.v1
```

The trial plan points its `queue` field at the experiment-local
`experiments/EXP-SSI-db46fa/queue.json`, which is a design-time stub:

```json
{"task_id": "TASK-20261007-05f4b2", "state": "written_not_dispatched",
 "note": "Design commit only. The executor card is not a launch."}
```

No batch queue under `coordination/goals/GOAL-SSI-001/` mentions
`TASK-20261007-05f4b2`. The experiment is approved (`DEC-20261007-254d55`,
`execution_authorized: true`) but was never dispatched, so the supervisor's
admission check refuses it. This is the `/run` skill's
`needs_dispatch_queue` case: a real trial plan, a placeholder queue, and a
coordination impediment — not an implementation failure.

## What this establishes

- `/run` is not blocked by missing code: the experiment's `run.py` and
  `check.py` exist and the plan validates.
- It is blocked by an absent dispatch queue for an already-approved task. The
  fix is a Coordinator act (open a batch, write the
  `crypto.autoresearch.dispatch_queue.v1` queue and the executor card), not an
  edit to the experiment or its frozen plan.

## Still true

- 0 run manifests and 0 evidence records exist on this checkout, so
  `/review-evidence` has no completed run set to validate.
- `ecc_priority.py --open-ideas` still reports 195 open ECC ideas; our 11 are
  closed by their new hypotheses.
