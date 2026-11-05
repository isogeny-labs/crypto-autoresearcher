# Sparse functional evaluation: matched A8 implementation control

A9 compares `dense_joint`, `dense_cancel`, `sparse_joint`, `sparse_cancel` on
all 288 immutable A7 systems, retaining four cold calls per case. The dense
modes must reproduce A8 outcomes, full kernels, certificates and Fr phase
vectors exactly. Sparse modes only change functional-kernel syndrome evaluation:
canonical coefficient support, a direct kernel-coordinate read for an exact
unit functional, otherwise a support-only dot product. All reduction, kernels,
certificate lifting, original-row and public checks remain unchanged.

This is a baseline control, not campaign completion. Fresh curve/target holdouts
and complete construction/collection/elimination/extraction/lifting/verification
accounting are required for the standing objective. No weighted/runtime/novelty
claim is prewritten. Sparse-only logical scans/visits are instrumented; dense
traversal is unmeasured, never falsely recorded as zero.

See design.md/literature.md and inputs.json for exact parent hashes and controls.
KB MCP/CLI were unavailable; the documented direct-source fallback was used.
Software command:
`PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -m pytest -q tests/test_sparse_functional_control.py research/prime_field_a9_execution_20261105/test_admin.py tests/test_cancellation_first_solver.py tests/test_progress_metrics_prime_field_panels.py`.

Publish exact source/inputs, freeze prospective protocol, obtain real canonical
S3 checkpoint, issue/commit/push root release, then gate and execute:
`PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -B research/prime_field_a9_execution_20261105/supervise.py --protocol research/prime_field_a9_execution_20261105/protocol.json --release research/prime_field_a9_execution_20261105/release.json --owner root-a9 --out research/prime_field_a9_execution_20261105/runs/a9-sparse-functionals-6be915`.
One existing workstation process/thread, 2 GiB, 21600 CPU/wall seconds, one
attempt/no automatic retry; no paid infrastructure submission. Retain every
failure prefix. Officially store/verify all eight raw gzip files; unified export
and raw Git publication precede report/PDF/database rendering. v12 preserves
v11 history. Final closed benchmark/progress, daily metrics, S3 checkpoint and
ready PR/auto-merge complete batch publication without satisfying the campaign.
