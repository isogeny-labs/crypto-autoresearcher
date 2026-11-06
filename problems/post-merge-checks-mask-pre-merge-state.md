# Post-merge check runs mask the pre-merge state of a PR head

- **Status:** open
- **Kind:** repository governance and CI evidence-integrity gap (companion to [pr-merge-checks-not-enforced.md](pr-merge-checks-not-enforced.md))
- **Affected work:** [`.github/workflows/validate.yml`](../.github/workflows/validate.yml) and [`.github/workflows/lab-parity.yml`](../.github/workflows/lab-parity.yml) (`pull_request_target: types: [closed]`), [`.github/scripts/ci_scope.py`](../.github/scripts/ci_scope.py) `resolve_base`, the merge rule in [AGENTS.md](../AGENTS.md#concurrency-many-agents-many-worktrees), and any review that reads a merged PR's check rollup as evidence that the head passed before merge
- **Next action owner:** repository owner for the ruleset; CI maintainer for the workflow and scope script; independent Validator for the controlled test
- **Last updated:** 2026-11-06
- **Raised by:** sheriff case [SHF-20261106-a114e7](../research/sheriff/SHF-20261106-a114e7/REPORT.md) (findings CIX-1, CIX-2, CIX-3)

## Problem

Two observations on 2026-11-06, read back through the GitHub API
(evidence: [`checks/ci/merge_timings.yaml`](../research/sheriff/SHF-20261106-a114e7/checks/ci/merge_timings.yaml)):

1. **Applicable checks still do not gate merge.** PR #3065 (head
   `4a55bcc5f6`) merged at 02:20:55Z while its own `validate` run
   42149688322 (`pull_request`) still had `ledger`, `merge-hygiene`,
   `ledger-and-harness`, `static-checks`, `records` and the harness shards
   running. Only `progress-fidelity`, `formal workspace`, `artifacts` and a few
   fast checks had finished. All later passed, which does not satisfy the
   pre-merge rule.
2. **A post-merge run overwrites a failed pre-merge result on the same SHA.**
   PR #3056 (head `51a2e0fa34`) merged at 02:20:46Z with `lab-parity` run
   42137487481 (`pull_request`) concluded `failure`. A `pull_request_target`
   (`closed`) run, 42149730300, created at 02:20:50Z, reports `success`
   against the same head SHA. The PR's rollup now reads green. These runs check
   out the base branch after the merge, not the head that was merged, and
   GitHub attributes them to the head SHA.

A latent third issue, not demonstrated: on `closed`, `ci_scope.py` diffs
`HEAD^1..HEAD` of whatever base-branch commit GitHub checks out, without
checking that `HEAD^2` is the PR's head. If two merges land before the run
checks out, the post-merge validation can attribute another PR's diff to this PR.

## Evidence and uncertainty

- **Observed:** the timelines above (check-run ids, run ids, events and
  timestamps in the evidence file).
- **Not observed:** the ruleset configuration. This session had no
  ruleset API. The #3065 timeline is consistent with the required set recorded
  in the companion problem (`progress-fidelity`, `artifacts`, formal workspace).
- **Does not establish:** that any merged content is wrong. Every pending
  check on #3065 later passed. #3056's parity failure was on an earlier test
  merge, and its post-merge parity on main passed.

## What would unblock it

- [ ] Require `ledger-and-harness` (the aggregate) and `merge-hygiene` in the
  main ruleset, or keep auto-merge disabled whenever applicable checks extend
  beyond the required set. Then show it on a controlled PR, with a pending
  and a failed check blocking the merge.
- [ ] Give post-merge runs a distinct check name (e.g. `post-merge / ...`), or
  post them only on the merge commit, so they never land on the PR head SHA.
- [ ] In `ci_scope.py`, refuse a `closed` event whose `HEAD^2` differs from
  `pull_request.head.sha` (or check out `pull_request.merge_commit_sha`
  explicitly).

## Next discriminating step

Read back the ruleset and run one controlled PR with a deliberately failing
`merge-hygiene`. Merge must be refused. A completed post-merge run must not
change that PR head's rollup. A recurrence is a merged PR whose head had an
applicable check pending or failed at `merged_at`.

## Resolution and history

2026-11-06 UTC: opened from SHF-20261106-a114e7. Nothing repaired.
