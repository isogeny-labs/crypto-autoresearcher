# Degree-three module peak memory on the hosted runner (frozen protocol, v2) — 2026-11-06

This run is for [problems/formal-workspace-build-exceeds-16gb.md](../../../problems/formal-workspace-build-exceeds-16gb.md)
and the PR #2677 review thread. It replaces the unfrozen 2026-10-29 container
measurement ([its report](../2026-10-29-degree-three-module-rss/README.md)).

## Verdict (the frozen analysis, verbatim)

**All three arms are invalid**, so the frozen verdicts are: **C1 inconclusive,
C2 invalid_measurement, C3 inconclusive**
([data/analysis.json](data/analysis.json); re-running `analysis.py` on
`data/` reproduces the same JSON).

Every arm ended because **this measurement's own watchdog** killed Lean, not
because the run finished or the runner ran out of memory. The watchdog fired
when `MemAvailable` fell below 300 MB. `MemAvailable` does not count swap, and
this runner has a 3 GiB swapfile that was still in use. So the guard stopped
runs that the CI build itself completes: the hosted gate finishes this module
in 579–671 s, and these arms were killed at 352–440 s. The protocol does not
allow re-running a job that reached its arms, so this run gets no do-over.

![lean memory over time per arm](memory.svg)

## What was observed (descriptive; not decided by the protocol)

| arm | killed at | max RssAnon | max VmSwap | max RssAnon + VmSwap (same sample) | min SwapFree |
| --- | ---: | ---: | ---: | ---: | ---: |
| default-a | 376.6 s | 14,054,488 kB | 2,240,000 kB | 15,789,592 kB (15.06 GiB) | 570,352 kB |
| threads1 (`LEAN_NUM_THREADS=1`) | 352.4 s | 14,463,800 kB | 2,234,948 kB | 15,966,500 kB (15.23 GiB) | 571,312 kB |
| default-b (A/A) | 440.4 s | 14,282,576 kB | 2,793,964 kB | 15,927,392 kB (15.19 GiB) | 324 kB |

Host ([data/host.json](data/host.json)): `ubuntu-latest`, image ubuntu26
20261101.186.1, 4 CPUs, MemTotal 16,365,628 kB (15.6 GiB), SwapTotal
3,145,724 kB (3 GiB `/swapfile`), cgroup `memory.max` = `max`, Lean 4.35.0,
module sha256 `e9db5830…0751e9`.

Read as lower bounds, since no arm finished:

- **The module needs more than about 15.2 GiB of anonymous memory** (resident
  plus swapped) on the current pins, and it was still running when killed.
  That is already near the runner's whole 15.6 GiB of RAM, so the hosted
  gate only gets through by **swapping**. Its headroom is the 3 GiB swapfile
  minus whatever the module needs beyond 15.2 GiB, which is unmeasured. In
  `default-b`, SwapFree reached 324 kB once, which suggests the gate's margin
  is thin.
- **`LEAN_NUM_THREADS=1` does not lower the footprint.** threads1 reached the
  highest combined value (15.23 GiB) and kept 8 OS threads. This agrees with
  the 2026-10-29 container run, but under the frozen rule C2 is
  invalid_measurement, not a supported "no effect".
- The 2026-10-29 container (no swap, 13.36 GiB memcg) died at 13.52 GB
  resident. That fits: the module's footprint is above that cap.

## Instrument defect

`measure.py` should have watched `MemAvailable + SwapFree`, or the cgroup
OOM, not `MemAvailable` alone. A v3 run would need that fixed, plus a floor
low enough for the module to finish (or no watchdog, if a runner OOM is
acceptable), filed as a new amendment before any data. **No v3 was run.**
Whether one is worth it is the owner's call: the gate already passes, and
what is still unknown is how much margin it has.

## Protocol history

- v1 (frozen 00:04:54Z, `08392f8a…`) produced no data. Run 42134422799 was
  cancelled during setup by a push. Run 42134558504 crashed in the pre-arm
  check because `jsonschema` was missing.
- v2 = amendment A1 (frozen 00:33:59Z at `fb78bec2`, `d3e6b677…`): fixed the
  workflow and reset the pre-arm rerun allowance. This report is v2's single
  run, 42137803829 (head `ad3ae7b9`).

## Files

- [protocol.json](protocol.json): the frozen v2 protocol.
  [analysis.py](analysis.py) is the frozen analysis (sha256 `4bfd334a…`) and
  [measure.py](measure.py) is the sampler. The workflow is
  `.github/workflows/formal-module-rss.yml`.
- [data/](data/) holds the artifact `formal-module-rss` (id 13467322317, zip
  sha256 in [data/ARTIFACT.txt](data/ARTIFACT.txt)): per-arm `samples.tsv`
  (0.5 s), `summary.json`, `host.json` and `analysis.json`.
- [rows.jsonl](rows.jsonl) and [export.json](export.json) form the
  `experiment.export/v1` bundle. `tools/experiment_protocol.py check-export
  --verify-files` reports 0 findings.
- [plot.py](plot.py) draws [memory.svg](memory.svg) (matplotlib).
- The `export.json` notes are observations only; the readings above are this
  report's.
