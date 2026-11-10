# A11: paid affine-target coverage with general outside columns

The single prospective native attempt is complete and consumed. It records
1,152dependent systems/2,304cold solver calls on four fresh curves and32public
target points. Both methods return matching target identities/scalars; all
three policies cover the target panel at budget8. Smaller budgets show
coverage/construction trade-offs. Producer measurement claims
`PCC-20261106-70a1b5` and `PCC-20261106-648bb8` remain unverified, without
signed independent replay/recomputation. [pcc:unverified]

- [Results and scope](RESULTS.md), [recorded arithmetic views](observations.json)
- [Inspected report](reports/a11-affine-holdout-30245e/report.pdf)
- [Native record](runs/a11-affine-holdout-30245e/execution.json), [compact metrics](runs/a11-affine-holdout-30245e/metrics.json)
- [Append-only database v14 receipt](database/v14-affine-holdout/generation-v14.json)
- [Proof standing](PROOF-STATUS.md), [next worklist](next-leads.md)
- Prospective [design](design.md), [literature](literature.md), [frozen protocol](protocol.json)

The joint method keeps raw general U coefficients. Outside-first eliminates U,
retains sparse original-row weights, builds base-only rows and tests target
functionals without a full kernel. Both pay original-row lifting/checks and
public point verification with symmetric unit-sign pivot shortcuts. Affine
construction retains explicit signed base/public/identity/cross-target
coincidences, cold source-prefix availability and symbolic Q coefficients.
Physical cached point queries are distinct from repeated cold cost references.
[pcc:unverified]

Software controls (tiny fields<=211, mocked admission explicitly limited to
software fixtures; no native rerun):

```sh
PYTHONPATH=src:. /workspace/factor-base-venv/bin/python -m pytest -q research/prime_field_a11_execution_20261106 --tb=short
```

Artifact hydration and export inspection from a fresh checkout:

```sh
python3 tools/artifacts/artifacts.py pull research/prime_field_a11_execution_20261106
cd research/prime_field_a11_execution_20261106/runs/a11-affine-holdout-30245e
gzip -dk analysis.json.gz export.json.gz
cd ../../../..
python3 tools/experiment_protocol.py check-export research/prime_field_a11_execution_20261106/runs/a11-affine-holdout-30245e/export.json --protocol research/prime_field_a11_execution_20261106/protocol.json --verify-files
```

Existing hydrated logical JSON files need no decoding. No command here launches
a new experiment. The native owner release permits one attempt, already used;
a new test requires its own prospective inputs/custody/release and output path.
