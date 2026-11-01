# Open-idea experiment designs — 2026-10-31

A design pass under the `design-experiment` skill over **every open idea in the
ledger**. Produced by one session; nothing was approved, dispatched or run.

## What "open" means here

An idea is open when its proposal record satisfies all three:

1. `idea.status == "proposed"`;
2. `idea.dominated_by` is empty;
3. its `IDEA-*` id appears in no hypothesis record and in neither the
   hypothesis nor the experiment index.

That query is executable and reproducible:

```sh
PYTHONPATH=. python3 analysis/open-ideas-design-20261031/open_set.py
```

It returns **11 ideas**, recorded in `open-set.txt`, and exits non-zero if the
recomputed set differs from the designed set. The 2,355 other `proposed`
records are either dominated (`dominated_by` set) or already carry a
hypothesis/experiment downstream, so they are not open under this definition.

## What was designed

`DESIGN.md` gives, per idea, the sentence under test and its class, the arms,
the A/A / positive / negative controls, the variable ledger, the seed and
blinding rule, the primary metrics with units, sample size, stopping and
invalidation rules, the decision rule, the falsifier and the inadmissible
moves. `protocols/<IDEA>.json` is the same design as an
`experiment.protocol/v1` record.

| area | open ideas | design theme |
|:--|--:|:--|
| WESO | 3 | audit quoted constants and the mixing budget behind the NIST-I row |
| SEMBIN | 4 | exact parity/confinement counts, a zero-background clustering detector, the exact first moment |
| KIC | 4 | Frobenius-stable bases, occupancy-null coverage, the relation ideal `(delta)`, the tau-Horner `m!` |

## Validation

```sh
for f in analysis/open-ideas-design-20261031/protocols/*.json; do
  python3 tools/experiment_protocol.py validate "$f"
done
```

Current result: 11/11 `OK (0 finding(s))`, captured in `validation.txt`.

## Status and next action

These records are `freeze.status: draft` until a Coordinator freezes them on a
commit; they are not published authority and no data was taken. The next
action is the ordinary `design-experiment` path: mint `H-*`/`EXP-*` ids, write
the hypothesis and specification records, run `experiment_preapproval.py`, and
approve under the standing authorization in `AGENTS.md`. That step is
deliberately not taken here: it would add ledger records without the runbook,
preapproval packet and dispatch queue the skill requires in the same turn, and
a half-published contract is worse than an unpublished design.

## Files

- `open_set.py`, `open-set.txt` — the reproducible open-set query and its output.
- `DESIGN.md` — the narrative contract for all 11.
- `protocols/*.json` — machine-readable `experiment.protocol/v1` records.
- `validation.txt` — validator output for every protocol.
- `generate.py` — the generator that wrote `DESIGN.md` and `protocols/`.
