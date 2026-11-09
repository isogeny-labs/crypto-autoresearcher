# Benchmark records: data in S3, metadata in Git, one progress report

Owner's rule, 2026-11-04. Byte-identical in `crypto`, `crypto-autoresearcher`
and `cryptanalysis` (lab contract, section 7; owner `crypto-autoresearcher`).

**Every benchmark run leaves a record.** The raw data goes to S3; a small
JSON record naming it (by SHA-256 and S3 location), the commit, the host, the
command, and the measured values in the shared units goes into Git in the
same PR; and the progress report is regenerated from the records in the same
PR. This is enforced, not requested: a Claude Code hook refuses an unrecorded
benchmark launcher and an unrecorded push, and a required CI check fails the
PR when a record is missing, incomplete, edited after closing, or when the
progress report is stale.

## The record

`tools/benchrec.py` writes one `bench.record/v1` file per run at
`benchmarks/records/<YYYYMMDD>T<HHMM>Z-<slug>.json` (`crypto-autoresearcher`
uses `docs/benchmarks/records/`; `.benchrec.json` at the root sets the
layout). Records are written once: a rerun is a new record, and CI rejects a
change to a closed one.

| field | meaning |
|:--|:--|
| `problem` | the stable key the series is drawn under, e.g. `ecdlp:EC1P40Cgh1a2b3c4d5e6`, `kernel:rho_zp_step`, `ic:N53` |
| `curve_uid` | the curve UID or EC1 alias when the run is about a curve (`docs/curve-identities.md`) |
| `commit`, `commit_dirty`, `branch`, `host` | where and on what the run happened (`BENCHREC_ISOLATION` names the isolation level) |
| `commands[]` | every launcher run under the record: argv, cwd, start, wall, exit |
| `raw[]` | every raw data file: path, `sha256`, bytes, `s3_uri`, `uploaded` |
| `metrics[]` | name, value, unit (from the table below), better, n, spread, baseline, reference and its kind |
| `reports`, `validation`, `entries` | the report PDF and graphs, the `VALIDATION.json`, the `benchmarks/<date>-<slug>/` directories this run fills |
| `status`, `summary` | `measured`, `invalid` or `censored`, and one line saying what was measured or why not |

The S3 location of a raw file is content-addressed,
`s3://setec-astronomy-artifacts/store/sha256/<aa>/<hex>`, the same store
`tools/artifacts/artifacts.py` writes, so the Git side is fixed as soon as the
file is hashed and the object can be checked by anyone with read access. A
file that already lives elsewhere in S3 (an isolab results prefix) is recorded
with `--s3-uri`. A raw file counts as stored when it is in Git (small files),
in a `.artifacts.json` manifest, or marked `uploaded` by `benchrec.py upload`
(which needs AWS credentials: CI has them, a session usually does not). CI
with `--verify-s3` HEADs every object.

### Closed raw data when a checkout path is reused

`living_paths` remains an accepted configuration field for evolving catalogs.
It never waives byte verification: configured and other changed paths follow
the same strict archival checks below.

The record and its original hashes, byte counts, URI, metrics and status stay
immutable. A newer generated file at the same checkout path is not the raw
data of the historical run. For a closed record only, the checker can verify
the original bytes from its existing canonical content-addressed store URI.
Online verification requires both the recorded length and a fresh bounded GET
whose complete SHA-256 matches the original pin; HEAD alone, the filename and
the `uploaded` flag are insufficient. Denied, missing, truncated, oversized or
corrupt archive reads fail the check. Open runs never use this fallback.
Closing an open record also cannot use the fallback: its current raw bytes must
match the original capture before the closed record is written. The fallback
only verifies records that were already closed before the command.

For offline checking, exact original bytes may be staged at
`.benchrec/raw-archive-cache/<sha256>` (inside the checkout). The checker
recomputes both length and digest and rejects symlinks or escapes. This proves
the recorded bytes locally, not their availability in S3. `--verify-s3` still
performs a fresh archive GET even when that cache is populated, and retains
the original per-object HEAD checks. Missing cache bytes do not relax an
offline failure. `upload` never uploads the differing newer file or marks it
uploaded; it accepts only the independently verified existing archive.

These checks concern the old recorded bytes only. They do not validate the
different current file, change a closed record, promote a measurement or
replace any current-source/scientific validation gate. Prefer immutable raw
output paths for new runs so this compatibility handling is unnecessary.

## One unit vocabulary

### Measurement admission and historical exclusions

Metric values, optional baselines/references, and both supplied spread endpoints
must be finite numbers, never booleans. A spread requires two ordered endpoints;
`n`, when supplied, must be a positive integer. Zero remains a valid value or
reference; division by a zero reference has no derived ratio. Non-finite derived
arithmetic is rejected before progress files are written.

A measured record needs successful integer exit codes (`0`) for every recorded
command. Failed attempts belong in invalid/censored records. When a historical
record mixes failed and successful commands without attributing each metric to
its command, its values cannot automatically enter aggregate comparisons.
Documentary commands with unknown exits do not establish successful execution.
These are metadata admission rules, not mathematical correctness certificates.

Closed records stay immutable. An additive `integrity-exclusions.json` next to
the configured records directory may explicitly exclude a historical measured
record from **all** progress series and derived comparisons:

```json
{
  "schema": "bench.integrity-exclusions/v1",
  "records": {
    "benchmarks/records/20261104T0000Z-example.json": {
      "sha256": "<SHA-256 of the exact closed record bytes>",
      "reason": "Specific measurement or execution-provenance deficiency."
    }
  }
}
```

The checker rejects missing records, non-measured records, empty reasons and
digest mismatches. An exclusion waives only measurement-metadata admission for
that pinned record; raw hashes, byte counts, reports and storage checks still
apply. JSON, Markdown, SVG and PDF progress outputs disclose exclusions; original
status counts retain the historical statuses. Exclusion is conservative: it
does not establish that the quoted measurements or underlying results are false.

Progress rendering independently checks eligible measurement metadata. A stable
series `(problem, metric name, unit)` must keep the same `better` direction;
changing direction requires a new metric identity. Invalid metadata, direction
drift or arithmetic overflow rejects the report before any output is replaced.
Closing checks cross-record comparability before making a record immutable.
Local raw files must match both their recorded SHA-256 and byte count.

A metric is rejected unless its unit is one of these. The headline unit of
every progress chart is `S`; every other unit gets its own panel and is never
mixed with another.

| unit | meaning | better |
|:--|:--|:--|
| `S` | group operations / sqrt(n), every phase priced (the ECDLP cost unit) | lower |
| `gae`, `log2_gae` | counted group-addition equivalents | lower |
| `ns_per_gae` | wall nanoseconds per GAE | lower |
| `ir`, `ir_per_op` | Callgrind instructions, whole run or per operation | lower |
| `cycles_per_op`, `ipc` | perf stat counters | lower / higher |
| `wall_s`, `cpu_s` | seconds | lower |
| `ops_per_s` | operations per second | higher |
| `fmul` | field multiplications | lower |
| `ratio` | reference / candidate (say otherwise in the note) | higher |
| `percent` | percent of the reference | lower |
| `count`, `bytes` | counts and sizes | neutral / lower |

Progress is always stated the same way: **gain vs first record** and **gain
vs previous record** in percent, derived from recorded values within one
series (same problem, metric and unit), and **value / reference** (the
distance remaining to the matched rho, 1.0 = parity) where the record carries
a reference. The report labels every such number derived; the measurements
are the recorded values.

## The workflow

```sh
python3 tools/benchrec.py init --slug rho-zp-step --problem kernel:rho_zp_step --entry benchmarks/20261104-rho-zp-step
python3 tools/benchrec.py run benchmarks/records/<id>.json -- scripts/perf/perfindex.py compare ...
python3 tools/benchrec.py add-raw benchmarks/records/<id>.json experiments/rho-zp-step-20261104/data/*.json
python3 tools/benchrec.py metric benchmarks/records/<id>.json --name ir_per_op --value 67.2 --unit ir_per_op --n 3 --baseline 107.0
python3 tools/benchrec.py metric benchmarks/records/<id>.json --name cost --value 1.41 --unit S --reference 1.30 --reference-kind matched_rho
python3 tools/benchrec.py close benchmarks/records/<id>.json --status measured \
    --report benchmarks/20261104-rho-zp-step/report.pdf --svg benchmarks/20261104-rho-zp-step/ir.svg \
    --validation benchmarks/20261104-rho-zp-step/VALIDATION.json --summary "rho step fused: 107.0 -> 67.2 Ir/op"
```

`close` validates the record, regenerates `benchmarks/progress/`
(`progress.json`, `PROGRESS.md`, `progress.svg`, `progress.pdf`) and takes the
record off the session's open list. Commit the record and the progress files
with the run's PR. A run that produced nothing usable is still closed, as
`invalid` or `censored`, with the reason in `--summary`.

The record does not replace anything: the study directory, the run report and
graphs (`research-visuals`), the `benchmarks/` entry and README row, the
`VALIDATION.json` gate, the leaderboard and `tools/progress_metrics.py` all
stay as they are. The record is the index that ties them to the raw data and
feeds the progress report.

## Enforcement

- **Claude Code** (`.claude/hooks/benchrec-hook.sh`): a command that matches
  a benchmark launcher (`ecbench`, `perfindex`, `perf_ipc`, `perf stat`,
  `callgrind`, `hyperfine`, `cargo bench`, `isolated_bench`,
  `tools/profile.sh`, `task_card.py run`, `autolab`, `icms`, `scripts/*bench*`,
  `make bench`) is refused unless it runs as `tools/benchrec.py run <record>
  -- ...` or carries `BENCHREC=<record>`; `git push` and `gh pr create` are
  refused while `tools/benchrec.py gate` fails (an open record, an incomplete
  record, a stale progress report). `BENCHREC_SKIP=<reason>` opts a
  non-benchmark command out; the reason is visible in the transcript.
- **Other runtimes (Codex, CI launchers)** run `python3 tools/benchrec.py
  gate` before pushing and do not push if it fails.
- **CI** (`bench-records` workflow, every PR): `python3 tools/benchrec.py check
  --base origin/<base> --verify-s3` fails the PR when a new `benchmarks/<date>-
  <slug>/` directory has no record naming it, a record is malformed, open,
  missing its raw files, report or summary, a closed record changed, a raw
  object is absent from S3, or the progress report differs from what the
  records produce. Where the runner has write credentials it first runs
  `benchrec.py upload` on raw files that are in Git, so a small raw file
  reaches the store from the PR itself.
- `tools/test_benchrec.py` is the tool's test and runs in the same workflow.

A record is not evidence of a result: validation, matched-rho references and
the §5a band still decide what may be shown as a result. It is evidence that
the run happened, where its data is, and what it measured in which unit.
