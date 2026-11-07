#set page(paper: "a4", margin: (x: 17mm, y: 17mm))
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.5em)

= Dashboard corpus integrity baseline
Published snapshot `e23868a6e5` · 2026-11-07 UTC · Conductor T-1870

The published dashboard and an exact-commit local build have identical
`data/integrity.json` bytes (SHA-256
`805dbb6acbf7328baa2ca9df7c78748e949da75120fa35a874f6c0e8eb337f9d`).
The local build indexed 29,068 records and completed its exact parse sweep.

#table(
 columns: (2.1fr, .6fr, 3.3fr), inset: 5pt,
 [Diagnostic], [Count], [Reading],
 [Malformed YAML], [24], [Exact committed files fail parsing],
 [Duplicate IDs], [258], [Stored copies and collisions mixed],
 [ID/path mismatches], [358], [Diagnostic, not an invalidity verdict],
 [Dangling IDs], [1,048], [Unresolved by the dashboard index],
)

#image("integrity-flow.svg", width: 100%)

The read-only audit script rebuilt the index, asserted all counts, and retained
full duplicate-path hashes and all 1,048 unresolved IDs in `baseline.json`.
The public payload displays only the top 500 dangling IDs. No ledger record
was changed.

#pagebreak()
= Classification and next checks

Of 258 duplicate groups, 228 contain stored schema supersessions, 12 contain
archive copies, 12 contain other correction copies, five are active-ledger or
legacy-root pairs, and one is an experiment header fallback collision. Only
one group has byte-identical files; the other 257 require authority-aware
reading. A stored correction is not interchangeable with its predecessor.

Eleven dangling `EXP-*` IDs have matching experiment directories. Two use
nested IDs in their specifications; one specification fails YAML parsing;
eight directories have no specification at that path. The remaining 1,037
IDs have no such direct experiment-directory evidence and need record-by-record
custody review. Neither the dangling count nor a directory proves an
experiment was executed or is missing.

All 24 malformed paths failed an independent exact YAML parse and have source
hashes in `baseline.json`. They are current exact-detail coverage defects.
The dashboard reports them visibly. Review immutable correction paths before
any source change; inspect the 18 duplicate groups outside the explicit
schema-supersession/archive classes and classify dangling IDs against planned
work and correction inventories.

The nine primary IC benchmark rows and their graph values were independently
audited in PR #3165. This corpus-wide integrity review adds no performance
claim and changes no historical run record.

Reproduce with `audit.py` at commit `e23868a6e5`; see `report.md` for the
full command and interpretation.
