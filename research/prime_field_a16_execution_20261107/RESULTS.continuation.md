# Fresh target recovery with separately paid horizons

The bounded continuation [RUN-PRIMEFIELD-c4b950](runs/a16-target-effort-c4b950/execution.json)
completed all 1,260 systems, 2,520 actual partial-known/native-joint solver calls
and 576 separate old-coordinate information diagnostics. Four fresh coefficient
curves supplied 32 public target points; policy/source/scope/prefix views reuse
those points. Both methods agreed on every case, all checks and four closed
canonical checkpoints passed, and no planned case remains unknown. Raw
publication `861e62ded5dd3bab511f33bf2856d7d2c7105843` preceded report rendering.
[PCC-20261107-d1bac1](../../pcc/claims/PCC-20261107-d1bac1.json), producer-unverified.
[pcc:unverified]

## Named recovery

At each program's complete target horizon, the observed identified/requested
*dependent* target slots are:

| Program | Horizon | Checked cases | Identified / requested |
|---|---:|---:|---:|
| norm8 | 8 | 144 | 42 / 1,152 |
| hybrid8 | 8 | 144 | 1,018 / 1,152 |
| known32_8 | 8 | 12 | 54 / 96 |
| known48_8 | 8 | 12 | 90 / 96 |
| known48_24 | 24 | 12 | 96 / 96 |

Norm/hybrid rows include six source schedules and two scopes per policy/curve;
known programs have one supplied-scope case per policy/curve. Known labels are
paid supplied knowledge, not learned rank. Horizon 24 adds six policy-specific
recoveries relative to horizon 8 and loses none in this census. Horizon 8's
three-policy union already covers the same 32 distinct public targets. Its
single policies recover 30/32 (walk), 29/32 (hash offset), and 31/32 (general);
using their union incurs multiple constructor/query/solver costs. No adaptive
fallback or portfolio saving was executed or priced here. [pcc:unverified]

There are 89 dependent norm/hybrid prefix-8 cases with identified targets and
remaining original base kernel. Case 23, norm/AP0/general/anchors, has source
rank 19, after-cancellation base rank 24 over 32 columns, and target mask `0x2a`
(three targets). Local native-row/unit lifts and public point certificates check
those targets without requiring full factor-base rank. [pcc:unverified]

## Included costs

The following are labelled sums of four cold views, fixed policy general,
AP0/anchors/source128 for hybrid and source-free supplied scope for known bases,
partial_joint with the batch endpoint engine. They are component vectors.

| Program | Identified / 32 | Fp mul | Fp inv | Fr mul | Pair allocation bytes | Query allocation bytes |
|---|---:|---:|---:|---:|---:|---:|
| known48_8 | 31 | 200,217 | 10,301 | 790 | 1,023,520 | 2,093,568 |
| known48_24 | 32 | 434,654 | 15,504 | 1,767 | 1,023,520 | 6,271,488 |
| hybrid8 | 29 | 433,770 | 12,784 | 6,597 | 1,023,520 | 6,271,488 |

Other Fp/Fr dimensions, all policies and schedules, both actual endpoint-engine
controls, each paid constructor and every cold reference remain in analysis.
These illustrative views are nonadditive. Equal 192 logical endpoints do not
imply equal cost. Explicit allocation traffic is not peak memory; inversion/
pow/hash internals, generation, checker work, Python/NumPy, OS/I/O and complete
calibration remain partly unexpanded. No weighted runtime, complete attack-cost
advantage or novelty follows from these vectors. [pcc:unverified]

The actual endpoint census is derived from recorded counters: 6,144 source
queries + 160 natural queries + 4,890 newly cached affine queries = 11,194
QueryIndex executions and 22,388 actual scalar/batch endpoint-engine calls.
The 13,056 logical target requests include 8,166 geometry-cache hits. The 6,480
matched engine comparison views and 576 information diagnostics are separate
from target-solver execution counts. [pcc:unverified]

## Database, custody and reports

[Database v20](database/v20-target-effort/validation.json) preserves all 98 parent
nonmetadata tables/rows and parent bytes, adds four curves, 16 mathematical
bases, 20 program contexts and 32 public targets, and stores all 1,260 cases,
2,520 solver outputs and 180 constructor branches. The eight known48 program
contexts refer to four mathematical bases while preserving their separate paid
construction/knowledge/cost records. Foreign keys, integrity and gzip roundtrip
pass as producer checks. [pcc:unverified]

The v20 metadata format retains inherited historical values and stores the
three overwritten active metadata values plus a parent hash in a 518-byte
reference. Reconstruction matches the original parent's complete metadata hash;
copying the full recursively nested snapshot would encode 92,500,585 bytes.
Existing historical database files and metadata bytes are preserved. This is a
storage-format improvement, not an attack-cost measurement. [pcc:unverified]

The original [Git admission failure](RESULTS.md) remains a separate invalid
attempt with zero scientific data and all planned cells unknown. The explicit
continuation retained the original 07:46:38.570520 UTC deadline, 2 GiB and one
worker/thread, carried 9.066162 prior CPU seconds, and allowed exactly one
additional attempt. Both releases are consumed; no third A16 attempt is allowed.
Native execution ran 01:59:09.389092–02:08:06.471253 UTC, exit 0, no timeout,
source unchanged. CPU/RSS and the 537.082177-second shared-host wall interval
are diagnostic, with wall_valid=false. [pcc:unverified]

The [final four-page report](reports/a16-target-effort-c4b950-v2/report.pdf) was
rendered and every page viewed. Its first numerical render is preserved with
an inspection failure for generic resource prose; v2 clarifies the actual
original deadline/two-attempt scope and adds the existing deficient-rank example.
No new experiment was run for that correction. A16 has its own observed-data
graph; existing A14/A15 historical graphs retain their original scope and bytes.
No official hypothesis or goal status changes here. [pcc:unverified]
