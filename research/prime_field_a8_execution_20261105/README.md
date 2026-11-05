# Cold cancellation-first versus full-joint recovery

User-authorized successor to [A7](../prime_field_a7_execution_20261104/RESULTS.md).
All 288 immutable supplied-row systems are compared, two cold solvers each.
No new collection, curve, base or target draw; old scalars are not solver inputs.

Inputs bind four parent gzip snapshots, their exact public fixtures and the
reviewed main/data commits. See [design](design.md) and [literature](literature.md).
Both methods retain complete kernels and target outcomes. The candidate pays
for all same-target differences and lifts recovered target certificates back
to the original joint rows. Fr add/sub/mul/inv are separate logical units;
inversion internals, Python traversal, IO and dense checking remain outside
a complete primitive cost model. No weighted or end-to-end gain is asserted.

Software controls: `PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -m pytest -q tests/test_cancellation_first_solver.py research/prime_field_a8_execution_20261105/test_admin.py`.
Exact source/input publication and prospective freeze precede root release;
a real canonical S3 checkpoint is required. One existing workstation process
and thread, 2 GiB, 21600 CPU/wall seconds, one attempt/no automatic retry.
No paid cloud capacity may be submitted with unknown budget telemetry.

Run after release:
`PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -B research/prime_field_a8_execution_20261105/supervise.py --protocol research/prime_field_a8_execution_20261105/protocol.json --release research/prime_field_a8_execution_20261105/release.json --owner root-a8 --out research/prime_field_a8_execution_20261105/runs/a8-cold-solvers-7f32b1`.
Then lossless archive.py, official explicit-file S3 push/remote verify, analyze.py
and unified export --verify-files. Commit/push raw results before report.py.
Build v11 from untouched v10; inspect every report/progress PDF page. Publish
ready PR with auto-merge; observe actual merged state before claiming merge.
