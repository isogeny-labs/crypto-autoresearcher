#set page(paper: "a4", margin: 19mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.55em)

= Current-main formal target static audit

*Crypto-autoresearcher commit:* `4239648a889fe97d976a99862d178ba50324dc6e`.
*Result:* `integrity_fail`. The 125 current formal target specs contain two
duplicate task-ID groups. Every declared source and theorem file is readable
from this exact Git tree. This is a source inventory, not a Lean build or
scientific review.

#figure(image("coverage.svg", width: 100%), caption: [Declared provenance
topology at the pinned commit. Dashed obligations in the prose are not
established by these static links.])

== Counts and collision witnesses

The target set declares 83 distinct theorem files and 47 distinct source
paths. It contains 125 unique claim IDs and 125 unique theorem names. The
2,903 top-level `EXP-*` directory names are not a run-validity count. Only
24 specs mention an exact existing experiment directory ID, zero specs cite
a run explicitly, and zero declared source paths point into `/runs/`.

`TASK-20261104-df29f3` occurs in `binary-semaev-repair-20261105.yaml` and
`closure-two-sided-certificates-20261104.yaml`. `TASK-20261105-9e5cbb`
occurs in `boolean-lastfall-upper-20261105.yaml` and
`boolean-normalization-repair-20261105.yaml`. The earlier 87-target builder
requires unique task IDs and stops on this current tree; the new auditor's
`--require-clean` mode exits 1. Its repeat output was byte-identical.
As a positive control, the same strict mode passed on the earlier pinned
87-target tree with no collisions.

== Provenance and limits

The primary repository sources are `formal/targets/README.md`, the pinned
2026-10-25 formal target provenance report, and
`problems/formal-target-semantic-fidelity-unreviewed.md`. The replayable
`audit.py` reads Git objects, validates schema and declared paths, computes
SHA-256 values and emits `inventory.json` (SHA-256
`27cab7302451206d1204d4c4f92382519e1e156481782ea3bede59c399d73757`).
Source-status labels are copied from specs; they are not reviewer verdicts.

No frozen target or receipt was edited. The next step is to identify each
target's real task owner, then make a versioned correction that preserves the
old receipt bindings. A current-tree Lean build and per-claim semantic and
run-custody reviews remain open. This audit changes no performance graph or
dashboard value.
