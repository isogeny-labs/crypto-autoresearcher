# Fresh curve/target source-selection holdouts

Prospective continuation of A5 on four new curves (two each over 8191 and
65537), with native base widths 16 and 32 and eight new public targets per
curve. Rules in inputs.json precede all native generation. The four prior A4
curve pairs and newly selected duplicates are excluded before eligibility work;
there is no rank, relation-yield or target-success selection.

Within each generated curve, the base, original-window projection and eight
targets stay fixed across window/hash0/hash1/hash2. Each arm constructs exactly
64 public source points in its own metered phase. All 64 original-window anchors
are public at every prefix; new anchors are explicit rows in the same columns.
Cold hash-arm costs include the prerequisite window-anchor construction and
shared setup/table work. Generation computes window points to fix the projection;
collection computes them again, and both physical stages remain charged.

Read design.md and literature.md. One physical process holds four shared pair
tables/target streams, 16 actual source schedules and 96 prefix/scope analyses.
Construction fields, group calls and logical scalar multiplications form a cost
vector; no complete weighted cost or isolated clock is asserted.

After committing/pushing exact source, freeze with `prepare.py protocol
--source-commit <sha> --out <study>/protocol.json --freeze`. An actual canonical
S3 checkpoint precedes the explicit `prepare.py release --source-commit <sha>
--protocol <study>/protocol.json --out <study>/release.json --owner root-a6
--authorize-root`. Commit/push the release, checkpoint and run its native gate.

Exact native command, from repository root with PYTHONPATH=src:.:

```
/workspace/factor-base-venv/bin/python -B research/prime_field_a6_execution_20261104/supervise.py --protocol research/prime_field_a6_execution_20261104/protocol.json --release research/prime_field_a6_execution_20261104/release.json --owner root-a6 --out research/prime_field_a6_execution_20261104/runs/a6-fresh-holdouts-97bb80
```

One existing workstation process/thread, 2 GiB, 21600 seconds CPU/wall protective
watchdog, one attempt, no automatic retry or new paid infrastructure. Every
failure prefix survives. Generation is written before its separate check,
collection before algebra, and final data before the complete independent
checker. Use archive.py, explicit official artifacts push/remote verification,
then analyze.py and export --verify-files. Commit/push raw results before report
rendering; preserve the v8 database parent when creating v9. Inspect all report
pages, publish the PR and enable auto-merge. Never rewrite earlier results.
