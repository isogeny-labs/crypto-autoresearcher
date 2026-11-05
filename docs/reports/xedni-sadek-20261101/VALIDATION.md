# Validation and provenance

Base: a4054418d345c69df73be9381131298e4678cbd4 (origin/main at clone).
Branch: codex/xedni-sadek-bound-audit-20261101. The worktree was clean before
the scoped additions. No scientific experiment was launched in this PR session.

## Completed software/document checks

- `python3 docs/reports/xedni-sadek-20261101/test_bounds.py`: five tests passed;
  complete observed output in `software-tests.txt`. These are software controls,
  not independent mathematical review or a lifting benchmark.
- Python: 3.12.14, Clang 22.1.3; reportlab 4.4.9.
- `python3 docs/reports/xedni-sadek-20261101/render_report.py`: exit 0.
- `pdftoppm -scale-to 1200 -png docs/reports/xedni-sadek-20261101/report.pdf
  /tmp/xedni-sadek-review`: exit 0; both pages inspected for clipping and legibility.
- `git diff --check`: exit 0 before staging.
- IDs allocated with `tools/allocate_id.py --next`, then `--check`: both
  well formed and unused in the 47,705-path identifier inventory.
- Direct `check_ledger_record` calls from `tools.validate_ledger` on the two
  new YAML records returned `errors: []` and `advisories: []`. This is scoped
  schema testing only, not the refused full-tree validator or a cross-reference
  sweep. The existing question was resolved from the repository Git tree.
- `python3 tools/merge_digest.py --since HEAD --until origin/main`: initially
  failed because orchestration was outside the sparse checkout; after
  materializing that source directory, succeeded with zero paths changed.

## Full-tree validation unavailable locally

The initial staged whitespace check treated the ASCII85 PDF as text and
reported PDF object/xref whitespace (exit 2); no commit was made. The renderer
now writes ordinary binary compressed streams instead. The regenerated PDF
is visually checked again; no whitespace rule or Git attribute is overridden.

`python3 tools/validate_ledger.py` refused the sparse checkout because 163,819
tracked files were off disk. The sparse override was NOT used. This is a
validation infrastructure limitation, not a ledger pass or mathematical result.
GitHub required and applicable checks remain authoritative. No baseline,
validation rule, protected workflow or historical record was modified.

## Historical evidence distinction

The original arithmetic diagnostic's tool call exited 0. Its exact command
and raw dictionary output are imported, not represented as a new native run.
Its user-facing answer printed an equivalent but reformatted command/output;
that was not the literal tool transcript. This additive import corrects the
custody description without altering the original conversation.

The original run did not capture a protocol, host manifest, Python version,
CPU usage, source revision or dirty state. Those remain unknown. The new
software-test timing is merely unittest's observed diagnostic, not an attack
cost or a comparison. No full bounded grid was executed, and the full theorem
repair remains a proposed hypothesis awaiting independent review.
