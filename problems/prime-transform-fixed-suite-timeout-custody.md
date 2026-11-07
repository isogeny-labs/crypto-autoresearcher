# Prime transform fixed suite timeout and whole-file custody memory

- **Status:** open
- **Kind:** observed resource limit; implementation gap in bounded-memory custody; unresolved repeated-stage cost
- **Affected work:** [EXP-PNEXT-3064e5](../experiments/EXP-PNEXT-3064e5/specification.yaml), [native failed receipt](../experiments/EXP-PNEXT-3064e5/runs/RUN-PNEXT-8223e9/execution-receipt.json), TASK-20261107-c87fa6 and snapshot TASK-20261107-6011ae; downstream EXP-PNEXT-624f41 full106+6 comparison
- **Next action owner:** Coordinator for failed custody and separately bounded source-only repair design; independent reviewer retains its original blinded scope
- **Last updated:** 2026-11-07

## Problem

The fixed transform software suite has not completed within its frozen600-second,
1CPU-equivalent,2GiB/no-swap envelope, and its launcher/adapter failed to finish
custody metadata when whole-file hashing encountered multi-gigabyte archives.

Both original producer slots are consumed. Independent slot3 remains reserved,
not a replacement producer attempt. Required exact controls, complete projected
model sets, chart handling, reconstruction and certificate-cost accounting remain
unchanged. This software suite does not substitute for the full106coordinate+
6coefficient comparison or all-five-lead work.

## Evidence and uncertainty

- **Observed:** immutable native receipt RUN-PNEXT-8223e9 records infrastructure_error,
  returncode1, checker null and manifest_completion null. It was published at
  `42f38ea45b07386960b0b03cbe42dfe3ea1e1ecd`.
- **Observed:** preserved systemd terminal values show Result=timeout,
  RuntimeMaxUSec=10min, MemoryMax=2147483648, MemorySwapMax=0, MainPID=0,
  ExecMainCode=2 and ExecMainStatus=9. Launcher records termination established.
- **Observed:** launcher failed with MemoryError while building artifact-manifest,
  then FileNotFoundError binding the absent manifest. Adapter traceback separately
  identifies `hashlib.sha256(Path(p).read_bytes())` while hashing attempt-files.tar.
  The native supervisor preserved logical archive SHA and4,587,520,000bytes, plus
  compressed SHA and127,211,514bytes. The native manifest.yaml and bundle-manifest.json
  were never emitted; they must not be reconstructed as native outputs.
- **Observed:** final available root checkpoint sequence474 contains472 accepted
  control records, including exact expected multiplier and projection exceptions.
  Its counters6nativeinstances/12nativecalls/32censusassignments are last-durable
  observations, not final totals. The root checkpoint status remains begun.
- **Derived or proved:** direct source inspection identifies whole-file allocations
  in both custody hash helpers; such allocation requires memory proportional to
  file size. No mathematical obstruction or complete-suite cost bound is proved.
- **Suspected explanation:** cumulative nested transcript serialization may account
  for archive growth and contribute to the timeout. This remains unmeasured;
  the checkpoint does not isolate solver cost from serialization or other work.
- **Missing capability:** bounded-memory hashing/manifest construction and a
  separately justified way to retain the fixed suite's complete coverage within
  its authorized execution envelope.
- **What this evidence does not establish:** no completed protocol, final native
  counts, independent acceptance, or impossibility of the mathematical construction.

## What would unblock it

- [ ] Preserve exact actual native receipts and missing-file inventory through a
  failed-producer terminal snapshot; physical Git metadata and logical stored
  archive verification are recorded separately.
- [ ] A source-only custody repair replaces whole-file archive hashing with streaming
  hashing, preserves digest semantics and failure precedence, and names separately
  admitted integrity controls for large-file, corruption and missing-file cases.
- [ ] Source analysis identifies the repeated-stage cost boundary and a structural
  change or proof obligation that preserves all fixed controls. No silently reduced
  fixtures, checkpoints, model sets, certificates or counters count as completion.
- [ ] Any later execution receives explicit new bounded authorization; the exhausted
  producer allowance is not reset by a new EXP, task, host or renamed retry. The
  original independent reviewer remains separate and blinded.

Custody repair establishes reliable evidence handling only. Full software acceptance
still needs complete required observations and independent review; the full106+6
scientific comparison remains downstream.

## Next discriminating step

- **Action:** archive the failed attempt, then inspect existing source and retained
  artifact sizes to separate whole-file custody allocation from repeated-stage
  computational work. Prepare bounded streaming changes and an explicit cost
  decomposition without importing or executing candidate modules.
- **Inputs and controls:** unchanged launcher/adapter/receipt writers and original
  workload contract; integrity controls must preserve hashes and reject corrupt or
  absent data. Do not disclose producer controls/results to the blinded reviewer.
- **Execution limits and stop condition:** this next step is source-only, zero
  scientific runs. Existing producer budget remaining is zero. Independent slot3
  retains600s/1CPU/2GiB/no-swap and requires its own exact admission; it cannot serve
  as a producer diagnostic or a retry.
- **Outcomes:** a justified streaming patch can proceed to separately authorized
  software integrity validation. If no bounded coverage-preserving stage change is
  found, retain the precise incomplete scope and original requirements.
- **Recheck trigger:** published source-only repair/cost decomposition and exact
  separately authorized validation plan, or independent evidence satisfying the
  original requirements.

## Resolution and history

2026-11-07: opened from actual second-producer timeout and custody failure. Both
producer attempts remain immutable. Related mechanisms are recorded in
[artifact serialization memory](lattice-ic-artifact-serialization-memory.md) and
[native snapshot manifest resolution](native-snapshot-artifact-manifest-resolution.md);
those records have different workloads and do not supply evidence of this repair.
Unresolved.
