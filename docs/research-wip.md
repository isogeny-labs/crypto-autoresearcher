# Cross-repository research WIP admission

`docs/research-wip-policy.json` is the shared operational admission policy for
`crypto`, `crypto-autoresearcher`, and `cryptanalysis`. The byte-identical
`tools/research_wip.py` reads current open-pull-request counts through the
authenticated GitHub CLI and emits a machine-readable report.

The initial envelope is twelve open pull requests across the three repositories:
eight in `crypto`, two in `crypto-autoresearcher`, and two in `cryptanalysis`.
These are concurrency limits, not closure targets or scientific judgments.
Changing a cap requires a coordinated update to all three policy copies.

```sh
python3 tools/research_wip.py --mode advisory --action portfolio
python3 tools/research_wip.py --mode enforce --action design
python3 tools/research_wip.py --mode enforce --action review
```

Modes have deliberately different authority:

- `off` performs no GitHub measurement and admits the action.
- `advisory` records exact counts and violations but admits the action.
- `enforce` blocks `run`, `design`, `prepare`, and `portfolio` while any cap is
  exceeded or the measurement is unavailable. It continues to admit `repair`
  and `review`, so the control can drain existing work rather than deadlock it.

The campaign supervisor caches measurements for the policy's
`refresh_seconds`. A rejected action is excluded only for that selection pass;
it receives no scientific cooldown and is reconsidered after the normal idle
interval. The event log records `admission_blocked`, and the campaign report
counts those events.

This report establishes only observed GitHub WIP at one time. It does not show
that a pull request is correct, independent, ready to merge, stale, or attached
to a valid scientific claim. The normal protocol, evidence, review, branch
protection, and repository-authority rules remain binding.
