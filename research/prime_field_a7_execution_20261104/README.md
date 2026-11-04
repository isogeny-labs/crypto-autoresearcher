# Matched source budgets and joint-target recovery

Conditioned follow-up on every A6 curve/base and all 32 fixed public targets.
No new curve or target is generated. Copied public fixtures, projections and
targets carry parent paths/hashes; recovered target scalars are not input.
The original window's 64 known public points remain a shared, charged
prerequisite. Additional scheduled points and their anchors are credited only
through the checked source budget.

The four schedules extend to 128 source scalars, preserving the exact first
64 A6 entries. Budgets are 0/8/16/24/32/48/64/96/128. Each construction,
query and anchor block has disjoint costs; points already constructed for
the original 64 exact scalar keys are cached uniformly for all arms. No
cross-schedule future cache is used. All hash derivation is prepaid and charged
up front. Future scalars are publicly computable; this is a measured operational
input boundary, not a secrecy assumption. See design.md and literature.md.

One pair table and one target stream per curve serve all arms/budgets. Target
multiple points for diagnostics are constructed once; each diagnostic uses
only the original prerequisite and that arm's first b source points. The
relation-only and explicit-anchor scopes are separate. At budget 64, both
scopes reproduce A6 semantics; lower anchor scopes intentionally differ from
A6's all-64-points-at-every-prefix policy. There are 288 scoped observations,
not 288 physical executions. The first checked budget is not an exact first
source count between checked levels. No rank/recovery stop or favorable redraw.

Publish exact source and copied inputs, then freeze protocol.json with
prepare.py. After a real canonical S3 checkpoint, issue the explicit root
release, commit/push it and run its native checkpoint gate. Native command,
from the repository root with PYTHONPATH=src:.:

```
/workspace/factor-base-venv/bin/python -B research/prime_field_a7_execution_20261104/supervise.py --protocol research/prime_field_a7_execution_20261104/protocol.json --release research/prime_field_a7_execution_20261104/release.json --owner root-a7 --out research/prime_field_a7_execution_20261104/runs/a7-source-budgets-d1f98d
```

One existing workstation process/thread, 2 GiB and 21600-second protective
CPU/wall watchdog, one attempt/no automatic retry; no new paid capacity.
Retain all failure prefixes, budget journals and unknown costs. Collections
precede algebra; immutable final rows precede the separate complete checker.
Archive large closed raw files losslessly, use official artifacts push and
remote verification, then analyze/export --verify-files. Commit/push raw data
before rendering and inspecting the report. The v10 database preserves the
v9 parent and inherited rows. Cost vectors and shared work remain separate;
this study supplies no complete weighted cost or isolated timing comparison.
