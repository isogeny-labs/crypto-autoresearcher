# A12: larger-field holdouts with executed scalar/batch query controls

The single native attempt is complete and consumed:1,152dependent systems,
2,304solver calls,four fresh curves/32public targets on F262139/F524287 with
base32. Both methods agree. Recovery is sparse at the unchanged budgets;
query batching trades inversions for multiplications and allocations. The
producer measurement claim PCC-20261106-7a4122 remains unverified, without
signed independent replay/recomputation. [pcc:unverified]

- [Results](RESULTS.md), [derived observations](observations.json), [proof standing](PROOF-STATUS.md)
- [Inspected report](reports/a12-batched-holdout-6ba98a-render2/report.pdf), [retained first-render failure](reports/a12-batched-holdout-6ba98a/render-failure.json)
- [Native execution](runs/a12-batched-holdout-6ba98a/execution.json), [compact metrics](runs/a12-batched-holdout-6ba98a/metrics.json)
- [Database v15 receipt](database/v15-batched-holdout/generation-v15.json)
- [Next paid known-log-base control](next-leads.md)
- Prospective [design](design.md), [literature](literature.md), [frozen protocol](protocol.json)

Both query engines actually execute at each endpoint and compare exact signed
point arrays before one relation/matrix stream. Scalar reuses prepaid signs;
NumPy batch shares within-endpoint denominators and pays padding/masked work/
exceptional fallbacks. Source/target engine phases, independent point/count
checks, cold engine subtraction and exact-mask counter frontiers are retained.
They are not calibrated all-cost or runtime dominance. [pcc:unverified]

Software-only controls, no native replay:

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -m pytest -q research/prime_field_a12_execution_20261106 --tb=short
```

Fresh-checkout hydration/inspection:

```sh
python3 tools/artifacts/artifacts.py pull research/prime_field_a12_execution_20261106
cd research/prime_field_a12_execution_20261106/runs/a12-batched-holdout-6ba98a
gzip -dk analysis.json.gz export.json.gz
cd ../../../..
python3 tools/experiment_protocol.py check-export research/prime_field_a12_execution_20261106/runs/a12-batched-holdout-6ba98a/export.json --protocol research/prime_field_a12_execution_20261106/protocol.json --verify-files
```

Decode only when ignored logical JSON is absent. These commands hydrate or check
stored records. The native one-attempt release is already consumed; a new test
requires its own prospective source/input custody, freeze, release and output.
