# Formal workspace build does not fit in 16 GB of RAM

- **Status:** `investigating` (narrowed 2026-10-29: does not affect the CI gate)
- **Kind:** resource limit. The module needs **more than about 15.2 GiB**
  of anonymous memory, resident plus swapped (lower bound, hosted runner,
  2026-11-06). The cloud containers cap Bash commands at a 13.36 GiB memory
  cgroup with no swap, so they cannot build it. The `ubuntu-latest` gate
  runner (15.6 GiB RAM + 3 GiB swap) builds it only by swapping, with an
  unmeasured and possibly thin margin
- **Affected work:** the `formal-workspace` proof gate
  (`tools/verify_formal_targets.py`, `.github/workflows/lean-verification.yml`,
  active as of 2026-10-28; it was disabled when this record was opened); every `autoresearch formal verify` run, which starts
  with a whole-workspace `lake build`; sheriff SHF-20261017-e4d7f6 CI1
  (`lean-verification` never built the Quotient target);
  [the 2026-10-23 rename report](../docs/reports/2026-10-23-translation-commutes-rename/report.md)
- **Next action owner:** unassigned (formal lane maintainer)
- **Last updated:** 2026-11-06

## Problem

`lake build` of `formal/` cannot finish on a 16 GB host because compiling
`CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate` is killed out
of memory. The formal gate's first step is that build, so on such a host it
reports **every** target as not verified, whatever the target is.
`BooleanParityFiltrationCertificate` imports the module and is blocked with it.

That mattered because 16 GB is what a standard GitHub-hosted Linux runner has,
so re-enabling `lean-verification` there looked like it would fail the gate for
a reason that says nothing about any theorem.

**Correction, 2026-10-28:** that prediction did not hold. The hosted
`formal workspace (lake build + axiom audit)` job built the same module and the
whole workspace on `ubuntu-latest` and verified all 87 targets (see the
2026-10-28 entry below). The OOM is therefore seen on one container, not
established for the standard runner; why the two differ is unknown.

## Evidence and uncertainty

- **Observed:** on 2026-10-23, on Lean 4.35.0-rc1 and Mathlib `7fa22735`, with
  4 CPUs, 15 GiB RAM and no swap. The whole-workspace build was killed with
  `Lean exited with code 137` on that module after about 470 s. A retry with
  only it and its dependants left was killed the same way.
  `verify_formal_targets.py` then returned `formalization_blocked` ("lake build
  failed") for `quotient-translation-descent`. With the two modules moved out,
  the same workspace built (8,973 jobs), passed `AxiomAudit.lean` (640
  theorems) and verified that target. Logs:
  `docs/reports/2026-10-23-translation-commutes-rename/evidence/`.
- **Also observed:** the module was built and audited on 2026-10-22 on a
  different host (`docs/reports/2026-10-22-semaev-first-fall-replay/`,
  degree-three-rank evidence). That host's memory is not recorded there.
- **Derived or proved:** not established.
- **Suspected explanation (conjecture):** the file sets
  `set_option maxHeartbeats 0` and checks a large finite rank certificate by
  kernel reduction. Peak elaboration memory grows with the certificate. Peak
  RSS was not measured.
- **Missing capability:** the module's full peak memory (only a lower
  bound is measured: about 15.2 GiB resident plus swap), and a container
  with more than ~16 GB available to commands.
- **Observed, 2026-11-06, hosted runner, frozen protocol v2**
  ([report](../docs/reports/2026-11-06-degree-three-module-rss-rerun/README.md),
  PR #3057, run 42137803829). Lean 4.35.0, Mathlib `cfc55fc5`, module sha256
  unchanged. Three arms ran in order: default threads, `LEAN_NUM_THREADS=1`,
  then default again. The measurement's own watchdog (MemAvailable < 300 MB,
  which does not count swap) killed every arm at 352–440 s, before the 579–671 s
  the CI build needs. So the frozen verdicts are inconclusive or
  invalid_measurement. At the kills, lean held 14.05–14.46 GB resident and
  2.23–2.79 GB in swap. The per-sample maximum of resident plus swap was
  15.06 / 15.23 / 15.19 GiB, and in one arm SwapFree reached 324 kB. The
  runner has MemTotal 15.6 GiB, a 3 GiB swapfile, and cgroup `memory.max` set
  to `max`.
- **Derived, 2026-11-06 (from lower bounds):** the hosted gate builds this
  module only because the runner has swap. The module already uses about as
  much anonymous memory as the runner has RAM, and it was still running when
  killed. `LEAN_NUM_THREADS=1` showed no reduction (descriptive only; frozen
  C2 is invalid_measurement).
- **Observed, 2026-10-29, peak memory on the container**
  ([evidence](../docs/reports/2026-10-29-degree-three-module-rss/README.md)).
  `LEAN_NUM_THREADS=1 lake env lean` on the module at `main` `1896454c`,
  with its dependencies already built. The kernel **OOM-killed it at 339 s**
  with `anon-rss:13520596kB` (13.52 GB, 12.89 GiB), still growing about
  0.12 GiB/s. `dmesg` says `constraint=CONSTRAINT_MEMCG`: the limit was the
  session's command cgroup, `memory.limit_in_bytes` = 14,341,885,952
  (13.36 GiB), not the 15.7 GiB of physical RAM. Lean still ran 8 OS
  threads. So `LEAN_NUM_THREADS=1` does **not** bring the module under the
  limit. The mapped Mathlib `.olean` pages (up to 6.5 GiB `RssFile`) were
  reclaimed before the kill. Only the anonymous heap counts.
- **Derived, 2026-10-29:** this explains both the container OOM and the
  hosted success. The module's peak heap is above 13.5 GB. The container's
  commands get at most 13.36 GiB (14.34 GB) including page cache, while the
  hosted runner gives its process ~16 GB. The earlier "15 GiB container"
  description was the RAM, not the limit that applied. The hosted margin is
  unknown and may be thin: the run here was killed at about 340 s, and the
  module takes 579 to 671 s hosted.
- **Observed, 2026-10-28, hosted runner:** `lean-verification` run
  [40713787875](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40713787875),
  job `formal workspace (lake build + axiom audit)`
  ([122905972990](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40713787875/job/122905972990)),
  head `b0e03a1620237b135d3bbf81ad826f9a9e41532c`, `ubuntu-latest`, plain
  `lake build` followed by `tools/verify_formal_targets.py`. It ran 15:13:54 to
  15:36:44 UTC, concluded `success`, and printed `87 verified, 0 not verified,
  0 infrastructure, 0 undischarged`, including
  `semaev-s3-semantic-rank-degree3-20261022` (the module that was killed here).
  Receipts: artifact `formal-verification-receipts` (ID 12828902787, 87 files).
  The same job also passed on the three earlier heads of the same PR on
  2026-10-28: `f6372f1e70` (03:35 to 03:58 UTC), `e040f506f8` (04:28 to 05:02)
  and `edd834c742` (05:15 to 05:39).
- **Not observed:** peak memory on either host, runner RAM and swap, and any
  lake or Lean thread setting that differs between the two.
- **Observed, 2026-10-29, both hosted job logs read** (job
  [122905972990](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40713787875/job/122905972990),
  head `b0e03a16`, #2496; job
  [123070123680](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40760275078/job/123070123680),
  head `d75b7d47`, #2654). Both ran on runner image `ubuntu-26.04`
  `20261025.179.1` (Azure), with the plain `lake build` step and no `-j`.
  `LEAN_NUM_THREADS` was not in the step environment. In both, the module built
  **alone**: it started when `BooleanParitySemanticRankCertificate` finished,
  and every other module had already finished.

  | | module time | lake jobs running at once |
  | --- | --- | --- |
  | #2496 hosted | 579 s, success (15:20:39 to 15:30:18) | 1 |
  | #2654 hosted | 671 s, success (20:13:00 to 20:24:11) | 1 |
  | 2026-10-23 container, full build | killed (137) at 471 s | 1 (its predecessors were done) |
  | 2026-10-23 container, retry | killed (137) at 500 s | 1 (only it and its dependants left) |

  The logs do **not** print RAM, swap or CPU count. GitHub documents 4 vCPU
  and 16 GB for standard Linux runners on public repositories, and this
  repository is public. A cloud container of the same class, inspected on
  2026-10-29, has `MemTotal` 16,477,352 kB (15.7 GiB), **`SwapTotal` 0**,
  4 CPUs and an ext4 root, not tmpfs. So cached Mathlib oleans do not count
  against RAM there.
- **Derived, 2026-10-29:** lake's parallelism is **not** the cause. In every
  case, failed or successful, the module was the only lake job running, and
  the hosts have the same nominal RAM and CPU count. A `-j` / serialized-build
  fix is therefore not supported by the evidence, and no `-j` setting is
  recommended. The remaining differences are untested: swap (none in the
  container; not logged on the runner), the cgroup or VM memory limit, and
  Lean's own thread count inside one file (`LEAN_NUM_THREADS`, default = cores
  on both hosts). The container also ran slower: `SemanticRank` took 261 s
  there against 92 s and 137 s hosted. So it was killed before reaching the
  579 to 671 s the module needs even on the hosted runner.
- **What this evidence does not establish:** nothing about the module's
  correctness (it was audited elsewhere), nothing about any other theorem, and
  nothing about why the container and the hosted runner differ.

## What would unblock it

- [ ] `lake build` of the committed `formal/` workspace exits 0 on the host
  class the gate runs on (16 GB, or a declared larger runner), with peak RSS
  recorded. The exit-0 half is met by the hosted runs of 2026-10-28 (two job
  logs read on 2026-10-29); the peak-RSS half is not; or
- [ ] the gate builds the requested module and its closure (`lake build
  +Module`) and runs the axiom audit on a root restricted to built modules,
  and records which modules it did not build. That is a verifier change, and
  it needs its own review.

Either condition makes a gate failure mean something about the target again.
The first keeps the whole-workspace guarantee. The second weakens it to
per-target.

## Next discriminating step

- **Action:** either measure the full peak, or act without it.
  - **Measure:** a v3 amendment to the 2026-11-06 protocol, with a watchdog
    that counts swap (`MemAvailable + SwapFree`) and a floor low enough to
    let the module finish, run through `.github/workflows/formal-module-rss.yml`.
  - **Act:** treat the gate as fragile now, since the lower bound already
    reaches the runner's RAM. The 2026-11-06 run did not measure the full
    peak: its watchdog ignored swap.
- **Outcomes:** if the hosted peak is within about 1 GB of the runner's
  available memory, the gate is fragile. Then restructure the module (a
  smaller certificate per declaration, or `decide` split across lemmas) or
  declare a larger runner. Otherwise the gate is safe, and the containers stay
  unable to build the whole workspace. `-j` and `LEAN_NUM_THREADS=1` are both
  ruled out as fixes (2026-10-29; LEAN_NUM_THREADS=1 again showed no reduction
  on 2026-11-06, descriptively).
- **Recheck trigger:** any change to that module, to the toolchain pin, or to
  `lean-verification.yml` runner sizing.

## Resolution and history

- 2026-10-23: opened after the L-N9 rename build. Unresolved.
- 2026-10-28: the hosted gate passed with the whole workspace built (see
  Evidence). Status changed from `open` to `investigating`, and the claim that
  standard runners would fail is withdrawn. Kept open: the cause of the
  container OOM is unknown, no peak memory was measured anywhere, and a repeat
  on a 16 GB host could still fail. Unresolved.
- 2026-10-29: both hosted job logs read (#2496 `b0e03a16`, #2654
  `d75b7d47`). Plain `lake build`, no `-j`, no `LEAN_NUM_THREADS`; the module
  built alone in 579 s and 671 s. The container was killed while the module
  was alone too, so lake parallelism is ruled out and no `-j` setting is
  recommended. The workflow is `active` (GitHub API, 2026-10-29), so the
  re-enable question is moot. The gate is not blocked by this record: it has
  built the full workspace on `ubuntu-latest` on both heads read. Still
  `investigating` only for swapless ~16 GB containers. On such a host, use
  `tools/verify_formal_targets.py` results with care until peak RSS is
  measured: a `formalization_blocked` from this module's OOM says nothing
  about the target.
- 2026-10-29 (later): peak memory measured on the container with
  `LEAN_NUM_THREADS=1`. It was OOM-killed by the 13.36 GiB command memcg at
  339 s, with 13.52 GB of anonymous memory and still growing. The cause of the
  container failure is now known: a lower bound of 13.5 GB on the module's
  heap against a 13.36 GiB cgroup cap. `LEAN_NUM_THREADS=1` is not a fix.
  Still `investigating`, now about the hosted margin and the true peak.
  Unresolved.
- 2026-11-06: hosted-runner rerun under frozen protocol v2 (PR #3057, run
  42137803829). Every arm was cut short by the measurement's own watchdog,
  which ignored swap, so the frozen verdicts are inconclusive. Descriptively,
  the module needs more than about 15.2 GiB of anonymous memory (resident
  plus swap), and the gate runner gets through only by swapping. Still
  `investigating`: the full peak and the margin are unmeasured. The next
  step is either a v3 measurement or treating the gate as fragile now (owner's
  call). Unresolved.
