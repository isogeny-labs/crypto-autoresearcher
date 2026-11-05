# Matched source-selection control

Conditioned follow-up on the four observed A4 fixtures. The original curves,
bases, public projections and32targets stay fixed. Compare the original64source
scalars with64hash-selected scalars under each of three frozen seeds. Record
new public-anchor equations explicitly, preserving the old unknown columns.

See [design.md](design.md) and [literature.md](literature.md). No curve/target
regeneration, recovered target labels, outcome-based seed choice or rank stop.
One physical panel has4shared pair tables/target streams,16source schedules and
96curve/arm/prefix/scope analyses. Query overlap is actually executed and charged.
The separate checker reconstructs all signed triples once percurve, every pair
and query, explicit anchors, affine kernels/cancellation/target certificates.

Administrative preparation commits and pushes exact inputs and sources first.
`prepare.py protocol --source-commit <sha> --out <study>/protocol-v2.json --freeze`
freezes the new protocol. An actual canonical S3checkpoint then precedes
`prepare.py release --source-commit <sha> --protocol <study>/protocol-v2.json
--out <study>/release.json --owner root-a5 --authorize-root`; commit/push that
release and checkpoint again before launching. All are native built-in gates.

Exact native command (repository root, PYTHONPATH=src:.):

```
/workspace/factor-base-venv/bin/python -B research/prime_field_a5_execution_20261104/supervise.py --protocol research/prime_field_a5_execution_20261104/protocol-v2.json --release research/prime_field_a5_execution_20261104/release.json --owner root-a5 --out research/prime_field_a5_execution_20261104/runs/a5-source-control-c0c8a9
```

One existing workstation process/thread,2GiB and21600seconds CPU/wall protective
watchdog, one attempt/no automatic retry. No new EKS/IsoLab resources or paid
submission; unknown budget telemetry authorizes no new cloud capacity. Native
scientific trial output is always write-once, including failure prefixes.
After exit, `archive.py --run <run>` losslessly compresses large closed raw
snapshots, then official artifacts push/remote verification stores them. Run
`analyze.py --run <run> --protocol <study>/protocol-v2.json`, verify export files,
and commit/push raw data before rendering the inspected report. A fresh SQLite
extension retains the v7parent and indexes every arm/anchor/prefix certificate.
