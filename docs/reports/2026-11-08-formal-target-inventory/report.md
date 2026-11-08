# Current-main formal target static audit — 2026-11-08

**Result:** Static target integrity fails at crypto-autoresearcher main
`4239648a889fe97d976a99862d178ba50324dc6e`: 125 target specs contain
two duplicate `task_id` groups. The 125 claim IDs and theorem names are
distinct. Every declared source and theorem file was readable from this exact
Git commit. This audit does not run Lean or validate a scientific claim.

## Sources and method

The repository's [formal target contract](../../../formal/targets/README.md)
states one file per frozen formal task and warns that committed specs are
receipt-bound. The earlier [87-target inventory](../2026-10-25-formal-target-provenance/report.md)
used distinct task, claim and theorem identifiers on its pinned tree. The
current [semantic-fidelity problem](../../../problems/formal-target-semantic-fidelity-unreviewed.md)
separates kernel acceptance from claim fidelity and execution provenance.
These primary repository sources set the scope of this audit; no new
mathematical or novelty claim is made.

The [replay script](audit.py) reads exact Git objects at the named main commit,
parses each target YAML, requires its schema, reads its declared source and
theorem file, hashes all three files, and records literal identifier
collisions. It counts an exact `EXP-*` directory token in a spec or its
declared source as a **syntactic pointer only**. It does not use the dirty
working tree, run Lean, replay experiment rows, inspect theorem types or
decide whether a claim is faithful. [The inventory](inventory.json) is
108 KiB and has SHA-256
`27cab7302451206d1204d4c4f92382519e1e156481782ea3bede59c399d73757`.

| Current-main static quantity | Count | Interpretation |
| --- | ---: | --- |
| Target YAML specs | 125 | 38 more than the earlier pinned 87-target snapshot; no transfer of that build receipt |
| Distinct theorem files | 83 | Multiple declarations can share one module |
| Distinct declared source paths | 47 | All readable at this commit |
| `EXP-*` top-level directories | 2,903 | Directory names only, not valid-run count |
| Specs mentioning an exact existing `EXP-*` directory ID | 24 | Syntactic link, not proof suitability |
| Specs with explicit run reference | 0 | Does not rule out provenance in source documents |
| Declared sources under `/runs/` | 0 | No spec directly takes a sealed run artifact as source |

Source labels are 67 `COMPUTED`, 29 `PROVED`, 19 `STATED`, seven
`DERIVATION`, one `MEASURED_WITH_ALGEBRAIC_EXPLANATION`, one
`EXTERNAL_CLAIM_WITH_PRINTED_PROOF`, and one `not_verified`. These labels
come from the target specs and are not independent review outcomes.

## Identity collisions

| Reused task ID | Target files |
| --- | --- |
| `TASK-20261104-df29f3` | `binary-semaev-repair-20261105.yaml`; `closure-two-sided-certificates-20261104.yaml` |
| `TASK-20261105-9e5cbb` | `boolean-lastfall-upper-20261105.yaml`; `boolean-normalization-repair-20261105.yaml` |

The first pair was introduced in separate commits (`9e9e3054aa` on
November 4 and `2ede864c11` on November 5); the second pair arrived together
in `2ede864c11`. The archived 87-target builder explicitly requires unique
task IDs and stopped on the current 125-target tree at that assertion. The
new script emits an `integrity_fail` record rather than silently publishing
a green count; `--require-clean` exits 1 on this exact main. A repeat run
produced byte-identical JSON. As a positive control, the same script with
`--require-clean` on the earlier `0b38ac1157f777cb4a77d35e53d7ed583c541eb4`
tree exited 0 with 87 specs and no identifier collisions.

Replay from a checkout containing the named Git commit with Python and
PyYAML installed:

```sh
python3 docs/reports/2026-11-08-formal-target-inventory/audit.py \
  --commit 4239648a889fe97d976a99862d178ba50324dc6e \
  --out /tmp/current-formal-inventory.json
sha256sum /tmp/current-formal-inventory.json
```

The optional `--require-clean` flag must exit 1 on this commit. The report
and `report.pdf` were rendered from `report.typ`; the single PDF page was
visually inspected.

![Current target provenance and open bridges](coverage.svg)

## Boundaries and next action

No frozen spec was changed. A task-ID repair must first identify the actual
owner task for each target and use a versioned correction that accounts for
receipts bound to the original YAML bytes; inventing new task IDs or editing
an old receipt would hide the provenance defect. Independently review theorem
meaning and source/run linkage claim by claim. A full pinned Lean build and
axiom audit are still needed for the 125-target current tree; the older
87-target machine receipts cannot establish them.

The public performance dashboard and scientific graphs are unchanged because
this is a formal-target identity audit, not a new measurement or decision.
