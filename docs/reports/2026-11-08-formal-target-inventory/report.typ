#set page(paper: "a4", margin: 19mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.55em)

= Current-main formal target static audit

*Crypto-autoresearcher commit:* `4239648a889fe97d976a99862d178ba50324dc6e`.
*Result:* `structurally_consistent`. The 125 current formal targets have
distinct claim IDs and theorem names. Every declared source and theorem file
is readable. Two task IDs each own two targets, consistent with archived
handoffs. This is a source inventory, not a Lean build or scientific review.

#figure(image("coverage.svg", width: 100%), caption: [Declared provenance
topology at the pinned commit. Dashed obligations in the prose are not
established by these static links.])

== Counts and shared task ownership

The target set declares 83 distinct theorem files and 47 distinct source
paths. It contains 125 unique claim IDs and 125 unique theorem names. The
2,903 top-level `EXP-*` directory names are not a run-validity count. Only
24 specs mention an exact existing experiment directory ID, zero specs cite
a run explicitly, and zero declared source paths point into `/runs/`.

`TASK-20261104-df29f3` occurs in `binary-semaev-repair-20261105.yaml` and
`closure-two-sided-certificates-20261104.yaml`. `TASK-20261105-9e5cbb`
occurs in `boolean-lastfall-upper-20261105.yaml` and
`boolean-normalization-repair-20261105.yaml`. The proof-task archive names
the first ID as an archival owner; the dispatch queue and two separate CI
receipts bind the second ID to the Boolean module's two target theorems.
The earlier 87-target builder assumes unique task IDs and stops on this
current tree. Its assumption is obsolete for these documented multi-target
tasks. The corrected auditor's `--require-clean` mode passes here and on
the earlier 87-target tree; a repeat current run was byte-identical.

== Provenance and limits

The primary repository sources are `formal/targets/README.md`, the pinned
2026-10-25 formal target provenance report, and
`problems/formal-target-semantic-fidelity-unreviewed.md`. The replayable
`audit.py` reads Git objects, validates schema and declared paths, computes
SHA-256 values and emits `inventory.json` (SHA-256
`4c0d760ebf96caf06442091bfb3a63e27b3c65e591e97531ed3de6ffbb9577a5`).
Source-status labels are copied from specs; they are not reviewer verdicts.

No frozen target or receipt was edited. The target README now names the
many-to-one provenance rule. A current-tree Lean build and per-claim semantic and
run-custody reviews remain open. This audit changes no performance graph or
dashboard value.
