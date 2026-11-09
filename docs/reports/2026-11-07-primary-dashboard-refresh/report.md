# Primary IC dashboard provenance and replay audit

The pinned Compare dashboard already contains the current nine primary toy
benchmark rows. Its source commit is cryptanalysis
`5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14`; the inspected cryptanalysis
`main` was `612427ead3d47565b92da3e663739d5c17ce71ed`. Every source-file
SHA-256 in the pin matches the latter tree. The independent exporter at that
current tree produced identical identities, coverage, source hashes, and all
nine row fields after excluding only the commit-qualified row ID. The pinned
commit was available and each pinned source hash was also checked against its
committed bytes. Thus no snapshot, selector, or rendered performance graph
needs a new data value for these nine rows.

## Checks and exact scope

The read-only [audit script](audit_primary.py) produced [audit.json](audit.json)
from the source archive `experiments/ic-bench/baseline/primary.jsonl` and the
pinned UI snapshot. It implements polynomial-basis GF(2^13) multiplication,
inversion, and binary-curve point addition separately from the producer code.
For each of nine rows it checked the generator's order, the frozen workload
target `[s]G`, the recorded descent and rho scalar, complete/verified fields,
run and curve identities, the sum of all recorded operation phases, and the
sum of the online phase times. The separate online-overhead field was checked
as a component of target descent rather than added twice. All assertions
passed. The three frozen target scalars are 1046, 606, and 861; each appears
under the three recorded factor-base configurations.

The cryptanalysis exporter independently checked committed source bytes,
candidate and workload digests, curve and workload identities, and target
counts. The UI snapshot SHA-256 is
`4cc3b31ab805b34d9f2d1103e574f8130a6902d09703d49337c467257568ae5e`.
The benchmark catalog and all nine `ui/receipts.json` selectors match that
digest and select the exact pinned row IDs. Focused UI tests passed **11/11**:
`tests/test_ui_benchmarks.py` and `tests/test_curve_identity.py` with
Python 3.11 in the sparse current-main checkout.

The earlier local working branch still carried an older nine-row snapshot
from cryptanalysis commit `3b26c95abf33434d762fc68eb5955bc9b043c5f9`.
Comparing that branch alone would have proposed an unnecessary refresh. This
audit used crypto-autoresearcher `origin/main` at
`598f4c6a4fb7fa405ad3a0800fc7456170f0a380` as the publication authority.

## Interpretation and graph decision

The independent replay checks the archived toy-curve answers and the
arithmetic of the recorded accounting fields. It does not reproduce the
historical wall clock or independently authenticate execution on the stated
host. The Compare page continues to label timings as source-reported and
keeps total operations separate from the paired online interval. No new
performance comparison or speedup claim is inferred here.

The graph data and selectors checked were
`ui/benchmarks/cryptanalysis-primary.json`, `ui/benchmarks/catalog.json`, and
`ui/receipts.json`. Their relevant source values are current by exact hash,
so the existing rendered Compare graph remains unchanged. Other experiment
families and dashboard panels were outside this nine-row audit.

## Reproduction

From a cryptanalysis checkout at `612427ea`, export the committed archive:

```sh
python3 tools/export_benchmark_snapshot.py > /tmp/current-primary.json
```

From a crypto-autoresearcher checkout at `598f4c6a`, run:

```sh
python3 docs/reports/2026-11-07-primary-dashboard-refresh/audit_primary.py \
  --source-repo /path/to/cryptanalysis-checkout \
  --ui-repo . --current-export /tmp/current-primary.json
```

The exact `audit.json` is retained beside this report. Neither command runs
an experiment, modifies an archived receipt, or accesses cloud resources.
