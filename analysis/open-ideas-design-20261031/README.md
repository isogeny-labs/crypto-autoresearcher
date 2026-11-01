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
PYTHONPATH=. python3 analysis/open-ideas-design-20261031/open_set.py --pre  # snapshot: 11
PYTHONPATH=. python3 analysis/open-ideas-design-20261031/open_set.py        # now: 0
```

`--pre` returns **11 ideas**, recorded in `open-set.txt`, and exits non-zero if
the snapshot differs from the designed set. The default mode reports the
current set and checks closure: it is **0**, because all 11 designed ideas now
carry a hypothesis record downstream. The 2,355 other `proposed` records are
either dominated (`dominated_by` set) or already carry a hypothesis/experiment
downstream, so they are not open under this definition.

## What was designed

`DESIGN.md` gives, per idea, the sentence under test and its class, the arms,
the A/A / positive / negative controls, the variable ledger, the seed and
blinding rule, the primary metrics with units, sample size, stopping and
invalidation rules, the decision rule, the falsifier and the inadmissible
moves. `protocols/<IDEA>.json` is the same design as an
`experiment.protocol/v1` record.

The designs are also **ledgered**: 11 hypotheses (`H-*`, status `specified`)
and 11 experiments (`EXP-*`, status `review_required`) under
`ledger/hypotheses/` and `experiments/`, each experiment carrying a frozen
`protocol.json`. The idea-to-record mapping is in `LEDGER_MAPPING.md`.

| area | open ideas | design theme |
|:--|--:|:--|
| WESO | 3 | audit quoted constants and the mixing budget behind the NIST-I row |
| SEMBIN | 4 | exact parity/confinement counts, a zero-background clustering detector, the exact first moment |
| KIC | 4 | Frobenius-stable bases, occupancy-null coverage, the relation ideal `(delta)`, the tau-Horner `m!` |

## Validation

```sh
for f in experiments/EXP-WESO-*/protocol.json experiments/EXP-SEMBIN-*/protocol.json experiments/EXP-KIC-*/protocol.json; do
  python3 tools/experiment_protocol.py validate "$f"
done
```

Current result: 11/11 `OK (0 finding(s))` on the frozen per-experiment copies
(the design copies under `protocols/` validate identically).

## Status and next action

The designs are frozen (`freeze.status: frozen`,
`filed_before_affected_data: true`), and the ledger records exist as
`specified` hypotheses and `review_required` experiments. They are not
approved authority and no data was taken. The next action is the ordinary
`design-experiment` approval path: run `experiment_preapproval.py`, write the
runbook and task card, and approve under the standing authorization in
`AGENTS.md`. That step is deliberately left to the Coordinator: approval
requires a preapproval packet, runbook lint and dispatch queue in the same
turn, and an incomplete contract must stay `review_required`.

## Files

- `open_set.py`, `open-set.txt` — the reproducible open-set query and its output.
- `DESIGN.md` — the narrative contract for all 11.
- `protocols/*.json` — machine-readable `experiment.protocol/v1` records.
- `validation.txt` — validator output for every protocol.
- `generate.py` — the generator that wrote `DESIGN.md` and `protocols/`.
