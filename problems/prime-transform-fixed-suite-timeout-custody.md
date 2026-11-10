# Prime transform fixed suite timeout and whole-file custody memory

- **Status:** open
- **Kind:** observed resource limit; implementation gap in bounded-memory custody; unresolved repeated-stage cost
- **Affected work:** [EXP-PNEXT-3064e5](../experiments/EXP-PNEXT-3064e5/specification.yaml), [native failed receipt](../experiments/EXP-PNEXT-3064e5/runs/RUN-PNEXT-8223e9/execution-receipt.json), TASK-20261107-c87fa6 and snapshot TASK-20261107-6011ae; downstream EXP-PNEXT-624f41 full106+6 comparison
- **Next action owner:** Coordinator for failed custody and separately bounded source-only repair design; independent reviewer retains its original blinded scope
- **Last updated:** 2026-11-08

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


## 2026-11-08 refinement: bounded native-ref preparation custody

The source-only streaming repair and shortest scalar-constant prefix construction,
followed by an independently authored finite validation harness and metadata
supervisor, have been published. These are completed source components; no new
candidate execution is claimed. The immediate blocking gate is now **metadata
preparation custody under the existing 4 MiB diagnostic cap**, before manifest
materialization or its independent audit.

### Actual evidence

- [Metadata report](../research/prime_scalar_manifest_metadata_20261107/report.md)
  and [root custody envelope](../research/prime_scalar_manifest_metadata_20261107/supervisor-receipts.json)
  were published at `08887e0bf17eed3c155e8b5c454b23daf84e1968`.
  The envelope SHA256 is
  `d79211504a3dc98994f8a7276061719f32ea114779c7de3323ca6d21a24734fc`.
- Root observed preparation handle95245 terminate with exit1 at01:01:11Z on
  2026-11-08. A new full ref-mapping write exceeded the aggregate4MiB diagnostic
  allocation; the attempted exception diagnostic write also refused the same cap.
  Retained diagnostics total3,952,503bytes. The native readiness worker joined;
  this was a preparation failure, not a systemd metadata-phase timeout.
- No launch/config/parentargv, attempt marker, reservation or phase service was
  created. Builder, auditor, candidate and oracle invocation counts were zero.
  `manifest.json`, `builder-receipt.json` and `audit-receipt.json` remain absent.
  The published seven metadata files are layout plus actual descriptive custody
  and report artifacts; missing native outputs were not fabricated.
- Initial resolved-interpreter readiness failed for missing yaml; its failure and
  existing-venv dependency correction are retained. An earlier preparation refused
  an inactive synthetic slice; its failure and narrow read-only absence-predicate
  correction are retained. Neither correction began a metadata phase.

### Diagnosis and uncertainty

**Observed resource boundary:** the operational evidence allocation was exhausted
by retained preparation/ref reconciliation material. **Source-derived mechanism:**
full ref-to-tip mappings are content-addressed, but any unrelated tip movement
changes a full mapping digest, even when the native claims subtree is unchanged.
**Unmeasured:** exact contribution of unrelated tip churn versus fixed receipts to
future preparation cost. No metadata-builder, auditor or candidate runtime result
was obtained, and no mathematical obstruction is inferred.

### Current gate-specific exit criteria

- [ ] Publish the failed metadata release with its actual seven hashes and complete
  the existing snapshot using an exact terminal amendment: four source files plus
  seven metadata files plus the real snapshot receipt,12paths. Preserve failed
  metadata disposition and the original missing-three inventory.
- [ ] Design a compact lossless ref-custody representation: retain one initial full
  ref mapping, actual fetch/observation receipts, then explicit added/deleted/changed
  ref deltas and exact claims-tree equivalence classes. Reconstruction must recover
  every observed mapping and its canonical digest; missing subtrees and failed
  lookups must remain distinct. No relevant native ownership ref may be omitted.
- [ ] Derive an explicit worst-case byte budget that includes two launches/configs,
  every selected readback, failure receipts and report custody within the existing
  4MiB diagnostic and128MiB aggregate caps. Refuse before losing failure-custody
  space. Byte savings alone do not waive five-second startup or freshness checks.
- [ ] Obtain an independent static review of that representation and its counted
  integration into root preparation. Any later metadata attempt requires explicit
  fresh native admission; this record supplies no retry or allowance reset.

### Next discriminating construction

Coordinator scopes a source/design-only compact ref-custody construction with exact
reconstruction invariants and byte accounting, using retained observations as input
without invoking candidate, oracle, builder, auditor or services. Compare a fixed
initial map plus deltas with the retained full mappings by mathematical/structural
reasoning first; any executable replay/control requires separately explicit scope.
If reconstruction or worst-case accounting cannot be justified, revise that design
while retaining the current cap. If justified and independently reviewed, prepare
an exact bounded future metadata admission rather than resuming this failed task.

This refinement preserves all original producer failures, the exhausted two-slot
producer budget, reserved independent slot and full106+6/five-lead requirements.
The present problem remains open. Source completion, metadata custody and future
semantic validation are distinct gates.
