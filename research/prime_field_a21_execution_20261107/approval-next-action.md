# A21 prospective source assessment — blocked partial-JSON handling

Reviewed exact source `4431dc4dfdf34384c50af59e2368b3d6b6c8a6cd` and metadata
`de7c5373081e97fa0ac2dfd4950df4f0e05982ea`. All 203 source and 46 input hashes
match local and exact committed bytes; Python ASTs parse. All 194 inherited
A20 source hashes are unchanged. This exact prospective source is **not yet
administratively approvable**. Execution authorization and normal runtime
readiness remain false; no native A21 work or new allowance is approved.

## Concrete reporting/custody blocker

`analyze21.summarize.optional` directly loads every existing result, checker
receipt and completion JSON. There is no parse-error wrapper. The inherited
`write_once` opens the final destination with `x` and streams `json.dump`
(non-atomic), so a hard stop can leave a truncated existing JSON file. Reading
such a partial file raises before the analyzer emits the planned 12 rows or
retains the valid paid journal totals in a partial export. The current truncated-
prefix software control covers a bad JSONL tail, not this JSON-file case.
This is a static code finding, not an executed fault trial. [pcc:unverified]

Guard optional per-run JSON reads, retain path/error in `errors`, return `None`
and continue through planned cells while preserving valid journal prefixes and
paid counters. Add marked controls for truncated result/check/completion JSON
alongside an actual retained solver-paid prefix; require incomplete/unknown
cells and exact preserved paid counters. Publish corrected source/controls and
preview for an additive assessment, preserving this first snapshot. No source
was edited by this assessor.

## Other static observations

The direct mathematical producer boundary is coherent in this review. It binds
all four original A20 formal case/preparation inputs, excludes historical
checker rows/pivots/certificates/scalars from producer inputs, and reloads its
own public data per cold method. Historical solver outputs are only read after
all three actual producer calls finish a case. There is no recollection,
favorable case selection, new curve/target or fresh-holdout inference.
[pcc:unverified]

Acquisition validates ordered common units, the k/d definition-row positions,
original signed old-coordinate basis and one signed definition per auxiliary.
Numeric auxiliary labels are rejected. Expansion preserves repeated coefficients
and target coordinates; common numeric units and definition rows are explicitly
elided with actual producer work retained. Positive lifting actually combines
native rows, cancels auxiliary coefficients with original definitions and then
common-known coefficients with their original unit rows. The plain checker
reconstructs projected rows, dense/native rank, positive and negative target
membership and native/public certificates. Different valid certificate weights
need not equal old weights. [pcc:unverified]

Actual mapping, expansion/projection, elimination, target membership, native
lifting and public checks are metered; each method's parse bytes/CPU are
separately retained. Inherited sparse/kernel-free shortcuts remain available.
The grid of three methods by four common case IDs has 12 seeds/calls/export rows,
not a new 32-target holdout. A20 construction and collection remain historical
prerequisites; this is an unweighted algebra component comparison, not complete
attack cost or calibrated runtime. [pcc:unverified]

The retained producer receipt reports 13 controls passed in 0.44 seconds. I read
it and the marked/synthetic controls without executing them. The four archive
IDs repeat a tiny mathematical fixture and mock admission/S3 checkpoints; they
are not native pilots, scientific replicates or trusted remote custody. No
additional concrete semantic/grid/source blocker was found, but the partial-
JSON gap prevents approval. [pcc:unverified]

## Remaining execution boundary

After correction/additive assessment, root still owns exact publication,
prospective protocol freeze, current actual canonical S3, explicit bounded
release and normal supervisor/admit with exclusive lease/one consumed marker,
real start PIDs and four closed-case checkpoints. Original
`2026-11-07T07:46:38.570520+00:00` and 21600-second ceiling remain. The preview
pins 23 prior measured native/postprocessing records totaling 1314.131071 CPU
seconds, plus conservative elapsed-original-worker-window reservation. Elapsed
reservation is not measured CPU; preview 3799 seconds is historical metadata,
not current allowance. Release/launch must refuse exhaustion, not reset or
rename spending. One existing worker/thread, 2 GiB, one A21 attempt, no automatic
retry/newcapacity or reopened A20 release.

This is static delegated administrative review, not independently signed
scientific proof/replay/execution or a status transition. No project imports,
tests, group/matrix/oracle/native runs, gate/lease, Git mutation, freeze/release,
PCC signature or formal record allocation occurred. Configured model identity
remains unverified with no new resolver/provider probe. Research-kb remains
unavailable under carried direct-source fallback; no new KB ID, paper retrieval,
absence or novelty assertion is added. Exact hashes/blocker/budget are in
`admission-assessment.a21-source.json`; post-builders outside the 203-source
closure were not assessed as launch dependencies. [pcc:unverified]
