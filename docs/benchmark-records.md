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

## One unit vocabulary

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
