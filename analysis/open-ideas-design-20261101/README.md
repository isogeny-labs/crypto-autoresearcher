# Open-idea experiment designs — 2026-11-01 (PFDR)

Design pass under `design-experiment` over the ideas that remain open on a
corrected definition. Nothing here is approved or run.

## Correction to the 2026-10-31 pass

The earlier pass counted an idea as designed when its `IDEA-*` id appeared
anywhere in a hypothesis (including an incidental mention), so it reported
"0 open" after designing 11. The harness's own link is explicit:
`hypothesis.proposal_id` / `source_proposal`, or
`experiment.derived_from_idea` / `source_idea` (what `ecc_priority.py
--open-ideas` reads). This pass uses that definition, and it also repaired the
11 records from 2026-10-31, which had been written without those links.

Query (`--pre` reproduces the five; the default asserts closure):

```sh
PYTHONPATH=. python3 analysis/open-ideas-design-20261101/open_set.py --pre   # 5
PYTHONPATH=. python3 analysis/open-ideas-design-20261101/open_set.py         # 0
```

The pre-design snapshot is **5 ideas**, all `RQ-PFDR-ae2fba`, added
2026-10-29:

| priority | idea | design |
|:--|:--|:--|
| high | `IDEA-20261029-3d0e71` | shared divisor coefficients with a Graeffe membership tower |
| medium | `IDEA-20261029-2e292c` | strong algebraic backdoors selected without witnesses |
| medium | `IDEA-20261029-8d82e6` | prime-field CDCL with certificate-producing finite-domain theory |
| medium | `IDEA-20261029-e4edce` | partial multigraded Macaulay layers |
| medium | `IDEA-20261029-ec08bc` | complete chart-local saturation before closure |

## Deliverables

- `DESIGN.md` — per idea: claim classes, arms, A/A + positive + negative
  controls, variable ledger, seeds/blinding, metrics, sample size, stopping,
  decision rule, falsifier.
- `protocols/<IDEA>.json` — five `experiment.protocol/v1` records, all
  validating with 0 findings.
- Ledger records (linked): five `H-PFDR-*` `specified` hypotheses; **one**
  `EXP-PFDR-*` contract (`EXP-PFDR-3569b5`, the high-priority Graeffe tower)
  lands in this PR. The 2026-11-01 process budget allows one new ECC
  experiment per session, so the other four are deferred — see `DEFERRED.md`.

## Status

Designed and ledgered; `review_required`, no implementation, no run, no data.
Approval still requires a preapproval packet, runbook/task card and dispatch
queue, exactly as for the earlier batch.
