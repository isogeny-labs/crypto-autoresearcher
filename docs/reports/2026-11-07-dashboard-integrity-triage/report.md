# Dashboard corpus integrity baseline at the published snapshot

2026-11-07 UTC, Conductor T-1870. The [public dashboard](https://isogeny-labs.github.io/crypto-autoresearcher/)
and a fresh local build both use crypto-autoresearcher commit
`e23868a6e59297d0f97875b6454692c59f1cc11d`. Their
`data/integrity.json` files have the same SHA-256:
`805dbb6acbf7328baa2ca9df7c78748e949da75120fa35a874f6c0e8eb337f9d`.
The local build indexed 29,068 records and completed its exact ledger parse
sweep. This report classifies the panel's exceptions; it does not change any
ledger record or reinterpret a recorded experiment result.

| Published panel measure | Count | Reading |
| --- | ---: | --- |
| Unparseable ledger YAML files | 24 | Exact parser errors in committed source bytes; header-only index entries cannot supply verified details. |
| Duplicate IDs | 258 | Raw records with the same extracted ID; storage copies and active collisions must be separated. |
| ID/path mismatches | 358 | Extracted ID differs from ledger filename stem; a diagnostic, not proof of an invalid record. |
| Dangling reference IDs | 1,048 | Well-formed cited IDs unresolved by the dashboard index; the public payload lists only the top 500. |

## Recomputed classes

The read-only [audit script](audit.py) rebuilds the current index, asserts all
published counts, hashes each duplicate path and malformed file, and writes
the complete 1,048-ID reference list to [baseline.json](baseline.json).

| Duplicate-ID class | IDs | Interpretation |
| --- | ---: | --- |
| Stored `schema-supersessions` copy | 228 | Explicit retained correction history; do not delete or rewrite to make the panel green. |
| `ledger/archives` copy | 12 | Archived path plus another indexed path; inspect archive semantics before any UI suppression. |
| Other correction copy | 12 | Historical branch/merge correction copies, not yet individually certified as harmless aliases. |
| Active ledger collision or legacy root alias | 5 | Root `ledger/` file and a subdirectory record share an ID; needs pairwise authority check. |
| Experiment header collision | 1 | Two `specification.yaml` files fall back to ID `specification`, indicating index identity extraction rather than a shared experiment ID. |

Only one of the 258 duplicate groups has byte-identical files. The other 257
are **not** interchangeable copies. In particular, the 228 supersession
groups are retained history and must be interpreted by their correction
links, not collapsed by filename or byte comparison.

The full 1,048 dangling IDs split into 11 `EXP-*` IDs whose corresponding
`experiments/<ID>/` directories exist and 1,037 with no such direct
experiment-directory evidence. Among the 11, `EXP-AUXIN-339fb0` and
`EXP-RT1476-001` have specifications with nested IDs that the dashboard's
header extractor does not recognize as a top-level identity;
`EXP-FB-001/specification.yaml` itself fails YAML parsing. The other eight
directories have no `specification.yaml` at that path. Their existence does
not make the references valid, but calling all 11 absent would be wrong.
The 1,037 unresolved IDs include planned, superseded, or genuinely missing
possibilities. The baseline deliberately leaves those meanings open.

All 24 malformed paths and their source SHA-256 values are in the baseline.
An independent `yaml.safe_load` attempt failed at a concrete line in each
committed file. Examples include an unquoted flow sequence in
`ledger/H-BKKMV-001.yaml` and an invalid block entry in
`ledger/corrections/CORR-20260727-004.yaml`. These are real exact-detail
coverage defects for the current dashboard, independent of any claim about
the underlying research result.

## Decision and next checks

The public page honestly displays these exceptions. The nine primary IC
benchmark rows and their plotted values were separately source-audited in
PR #3165; this corpus-wide integrity baseline does not alter that audit.
Before changing dashboard logic, review the 18 duplicate groups outside
explicit schema supersession or archive paths, and verify correction authority
for the 12 archive groups. Review the 24 malformed records through their
immutable correction protocol; do not repair historical bytes in place.
For dangling references, compare each cited ID with the formal record,
planned work, and supersession inventory. Record per-ID dispositions rather
than interpreting the dashboard's count as 1,048 missing experiments.

![Integrity classification and boundary](integrity-flow.svg)

The diagram separates source facts, index diagnostics, and interpretation.

## Reproduction

At the pinned commit with Python 3.11 and PyYAML installed, build the site and
run the read-only classifier:

```sh
python3.11 -m ui.build --out site --report site-report.json
python3.11 docs/reports/2026-11-07-dashboard-integrity-triage/audit.py \
  --repo . --site-integrity site/data/integrity.json \
  --out docs/reports/2026-11-07-dashboard-integrity-triage/baseline.json
```

The committed `baseline.json` is the result of this command at the published
commit; re-running it on a different main revision must use a new output path.
