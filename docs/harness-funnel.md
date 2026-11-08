# Harness funnel and experiment WIP policy

`tools/harness_funnel.py` counts how work moves through the harness, and
`tools/experiment_wip.py` limits how many approved experiment contracts may sit
unrun. Both are operational measurements of the ledger. Neither is research
evidence, and neither changes a hypothesis, evidence record or goal.

## Running

```
python3 tools/harness_funnel.py            # text table
python3 tools/harness_funnel.py --json     # same numbers as JSON
python3 tools/harness_funnel.py --check    # four headline lines, always exit 0
python3 tools/experiment_wip.py --report
python3 tools/experiment_wip.py --check
python3 tools/experiment_wip.py --expire   # dry run
```

Both read the repository only, use the standard library and PyYAML, and finish
in a few seconds. `--as-of YYYY-MM-DD` fixes the date used for ages. Records may
nest their body under the type key (`experiment:`, `evidence:`) or be flat.
Unparsable files and bare strings are skipped and counted under
`unreadable_records`.

## Metrics

| Stage | Meaning |
| --- | --- |
| proposals, ideas | Files in `ledger/proposals/` and `ledger/ideas/`. |
| hypotheses | `ledger/hypotheses/*.yaml`, with a histogram of `status`. |
| specifications | `experiments/*/specification.yaml`, with a histogram of `status`. |
| approved | Specifications whose `status` is `approved`. Also shown: how many carry `approved_by`, have a run, or are cited by evidence. |
| approved_unrun | Approved, with no entry under `experiments/<id>/runs/` and no evidence record citing the id in `experiment_ids` (or `experiment_id`). Hidden files such as `.gitkeep` do not count as runs. |
| aging buckets | Days since approval for approved_unrun contracts: 0-7, 8-14, 15-30, 31-60, 61-90, 91+, unknown. |
| runs | Entries under `experiments/*/runs/`, with a histogram of manifest `status` (`manifest.json` or `manifest.yaml`). |
| evidence | `ledger/evidence/*.yaml` plus legacy `ledger/EV-*.yaml`, by `claim_tier` and `direction`, with the count whose `certificate.verified` is true. |
| decisions | `ledger/decisions/*.yaml`, by `decision` kind. |
| goals | `ledger/goals/*.yaml` and `ledger/goals/*/goal.yaml`, by `status`. |
| per goal | Approved and approved_unrun contracts for each goal. |
| ratios | Decisions per evidence record, and evidence records per approved contract. |

A contract's goal is its own `goal_id`, then the first of its `goal_ids`, then
the `goal_id` of its hypothesis, else `(no goal)`. Contracts without a goal
share one bucket and one cap.

### Approval date rule

The first date found wins:

1. `approved_at` on the specification.
2. The date of the decision named by `approval_decision` (`decided_at`, then
   `recorded_at`, then `date`, then the date inside the `DEC-YYYYMMDD-...` id).
3. The same lookup for `execution_authorized_decision`.
4. `frozen_at`, then `specified_at`, then `updated`.
5. The date of the earliest `approve` decision whose `target_ids` name the
   experiment.
6. Unknown. Unknown ages get their own bucket and are never treated as overdue.

The `approval_date_source` field of the JSON report counts which rule fired.
Rules 4 and 5 are weaker than rules 1 to 3, so read ages from those as
approximate.

### Runs source

In a sparse blobless checkout the run directories are not in the working tree.
`--runs-source auto` (the default) uses the working tree and falls back to
`git ls-tree`, which needs tree objects only. `--runs-source git` forces that.
In git mode the manifest status histogram reads `not_fetched`, because
manifests are blobs.

## Experiment WIP policy

`coordination/experiment_wip_policy.json`, schema `lab.experiment-wip/v1`:

| Field | Meaning |
| --- | --- |
| `mode` | `off`, `advisory` or `enforce`. `--mode` overrides it for one run. |
| `cutoff` | Contracts approved on or after this date are subject to `--check`. Earlier ones are reported, never blocked. |
| `approved_unrun_cap_per_goal` | Most approved-unrun contracts one goal may hold. |
| `approved_unrun_expiry_days` | Age after which an approved-unrun contract is overdue. |
| `first_measurement_max_seconds` | Upper bound for `first_measurement.max_seconds`. |

`--check` reports a contract approved on or after the cutoff when:

- it was past its goal's cap when approved. The goal's current approved-unrun
  contracts are ordered by approval date, then id (unknown dates first); the
  n-th is the n-th open contract at its approval, and breaks the cap when n is
  above the cap. Contracts since run are not in the list, so history can only
  look more lenient than it was.
- its specification lacks a `first_measurement` block, or the block lacks a
  non-empty `command`, a positive `max_seconds` not above the policy bound, or a
  `null_object`.

In `advisory` mode the problems print and the exit code is 0. In `enforce` mode
any problem gives exit code 1. `--report` shows approved-unrun counts per goal
against the cap and the overdue contracts with their ages.

A `first_measurement` block looks like this:

```
first_measurement:
  command: python3 experiments/EXP-X/run.py --smoke
  max_seconds: 600
  null_object: shuffled-label panel
```

## Expiry procedure

Expiry returns an overdue approved-unrun contract to draft so that approval
means a run is close, not that one is hoped for.

1. `python3 tools/experiment_wip.py --expire` lists every overdue contract and
   the exact change. It writes nothing.
2. For each contract it would set `status: draft`, set `execution_state: draft`
   if that key exists, and add:

   ```
   expired_from_approved:
     at: '2026-11-08'
     age_days: 38
     policy: lab.experiment-wip/v1
   ```

   The edit is textual, so comments and key order survive, and it is checked by
   reparsing before anything is written. A contract whose layout the edit cannot
   handle is listed with an error and left alone.
3. `--expire --apply` performs the change. This is a Coordinator action, because
   it changes research state. Nobody else runs `--apply`.
4. The Coordinator logs the action with a decision record in `ledger/decisions/`
   that names the policy, the date and the expired contract ids, and lands the
   spec changes and that record in one pull request.

An expired contract can be approved again through the normal design and approval
path. Expiry does not delete runs, evidence or the contract's history.

## CI

`.github/workflows/harness-funnel.yml` runs on pull requests that touch the
ledger, specifications, the policy or these tools, and weekly. It uses a
blobless sparse checkout (`ledger`, `coordination`, `tools`, `schemas`,
`experiments/*/specification.yaml`), uploads the funnel JSON and text as an
artifact, runs `experiment_wip.py --check` in the policy's mode, and runs the
unit tests. The real-repository test asserts the headline counts are within 5%
of the 2026-11-08 review (proposals and ideas 2,825, hypotheses 2,263,
specifications 2,847, approved 1,661, approved-unrun 1,187, runs 3,843, evidence
826, decisions 3,642), so large drift is visible.
