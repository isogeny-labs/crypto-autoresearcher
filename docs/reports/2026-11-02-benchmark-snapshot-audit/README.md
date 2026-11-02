# Nine-row benchmark dashboard provenance audit

**Checked result (2026-11-02 UTC).** The public crypto-autoresearcher site at build commit `6d5e7c5c6d442e85e0a78864e84d74898becab73` serves all nine rows of the pinned cryptanalysis primary benchmark snapshot. The live `data/comparisons.json` benchmark object equals the committed `ui/benchmarks/cryptanalysis-primary.json` object. The catalog SHA-256 and all nine `ui/receipts.json` registrations resolve to that same snapshot (`4cc3b31ab805b34d9f2d1103e574f8130a6902d09703d49337c467257568ae5e`). Pages [run 41512121316](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512121316) completed successfully; the captured live `data/meta.json` names that exact commit and build time `2026-11-02T19:45:50+00:00`.

The snapshot intentionally names cryptanalysis source commit `5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14`, the archive revision recorded by [the UI contract](../../../ui/README.md). I ran `tools/export_benchmark_snapshot.py` from cryptanalysis `bf155c25e57c6eefbaeed2c19b84786e402851f7`: it returned nine rows and seven source files, with every measurement, curve identity, run ID, and source SHA-256 equal to the pinned snapshot. A structured comparison found differences only in the top-level `source_commit`, the nine row IDs derived from it, and seven source URLs. `git diff --quiet` between those two cryptanalysis commits returned zero for the primary archive, candidate and workload manifests, exporter, and curve-identity tool. Repinning would change provenance labels without changing benchmark evidence, so this audit leaves the committed snapshot and graphs unchanged.

## Reproduce the recorded comparison

The [offline checker](check.py) reads the committed snapshot, catalog, and receipts plus the captured [current source export](current-export.json), [live comparison payload](live-comparisons.json), and [live meta payload](live-meta.json):

```sh
python3 docs/reports/2026-11-02-benchmark-snapshot-audit/check.py
```

Its captured [result](check-result.json) is `pass`, with nine rows, seven source files, nine registered receipts, and zero measurement or source-hash differences. As a negative control, increasing the first current-export `wall_ns` by one made the checker exit 1 with `measurement, identity, or source hash mismatch`, even under `python -O`. The source export was generated from the clean cryptanalysis worktree at `bf155c25e57c6eefbaeed2c19b84786e402851f7` by:

```sh
python3 tools/export_benchmark_snapshot.py --repo .
```

The source-byte comparison returned exit 0 with:

```sh
git diff --quiet 5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14 bf155c25e57c6eefbaeed2c19b84786e402851f7 -- experiments/ic-bench/baseline/primary.jsonl experiments/ic-bench/candidates experiments/ic-bench/workloads tools/export_benchmark_snapshot.py tools/curve_identity.py
```

The exporter checks committed source bytes, manifest/workload hashes, curve identities, target counts, and run-ID bindings. This audit compares the resulting metadata; it does not rerun the archived benchmark or independently certify its runtime measurements. The pin covers exactly nine N13 toy rows in `experiments/ic-bench/baseline/primary.jsonl`, as the snapshot's coverage field states. Other experiments, performance panels, and the rho operations feed are outside this check.

The [provenance diagram](provenance.svg) and [inspected PDF](report.pdf) show the source-to-site path. No canonical performance graph was regenerated: its nine numeric rows and their seven source hashes are unchanged. The live site itself was refreshed by the completed Pages workflow; the stored benchmark pin remains the exact archived source revision.
