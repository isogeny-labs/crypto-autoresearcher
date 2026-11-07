# A15: bounded signed-pair construction comparison

The ranked lead is [A14 next-leads](../prime_field_a14_execution_20261106/next-leads.md).
Implement the production-known signed-sum and batch-inversion techniques at
A14's pair-construction stage. No native A15 construction or query has run.

## Fixed workload and scope

All 16 retained geometries, in four curve order then norm/hybrid/known32/known48,
are committed as small public snapshots. Each snapshot includes the original
native slots, aliases, geometry, ordered pair commitment and every retained
source/natural/extra-cache query's full native row/trace and signed-point
commitment. Input transcription checks old Git/CAS bytes and does no new group
arithmetic. There are 51,968 ordered pair entries and 8,960 queries per method.
This is deliberately conditioned input reuse, with zero fresh targets and zero
new target-solver executions. Old coverage is not remeasured.

Per table execute unchanged A14 scalar QueryIndex, then a cold batched builder.
Each pays its own sign/native/query setup. The batch contains all unordered
geometric pairs within that table only. Compute two signed sums using their
common reciprocal and derive the two opposite outputs, preserving exact old
(++),(+-),(-+),(--) insertion order. Native distinct sign classes have unique
x-coordinates and nonzero y; refuse invalid geometry, no dummy denominators.
All multiply results reduce modulo p before subsequent multiplication; p<2^32
keeps each uint64 product representable. Query exceptional identity, doubling
and opposite cases use the unchanged executed A12 scalar/batch engines.

Both methods then execute every fixed query. The independent plain full triple
atlas checks all rows, pair buckets and misses. Original native row/trace and
signed-point commitments must match. Each query engine has an independently
coded exact field-operation schedule check. This is 32 builds, 17,920 actual
QueryIndex calls, and 35,840 executed signed-endpoint engines. No solver calls
are inferred from component parity.

## Counted work and controls

Disjoint paid phases retain sign/native setup, validation, batch input arrays,
denominators, padded product tree/root inverse, shared formulas, output
negations, conversion/table insertion and query replay. Count Fp operations
actually executed by scalar/vector APIs, explicit allocated elements/bytes,
integer conversions, padding, pair entries and query events. The independent
checker reconstructs both the arithmetic and explicit allocation schedule.
No EC API call is invented for a vector formula. Explicit traffic is not peak
RSS. Inversion/pow internals, NumPy hidden temporaries, Python/checker/OS/IO and
hash/storage overhead remain unexpanded; this is no calibrated runtime or
complete-cost comparison.

Before native use, marked p<=211 software controls cover 35 field/geometry
configurations, reversed representatives and native aliases, singleton/odd
batches, complete triple/query semantics, invalid sign classes/order-two/shape/
field/native indices/caps/admission, corrupted points/signs/native slots/counters/
allocations, actual mid-inversion failure and checker rejection after output.
A first protocol-preview schema refusal for design='paired' is retained; the
schema uses design='one_factor'. No native execution occurred on that refusal.

## Custody and boundaries

The complete runnable source closure, 16 snapshots plus input manifest and
prior protocol template are published before a prospective frozen protocol.
The administrative Coordinator assesses exact prospective bytes, without running
scientific code. Root then records explicit one-attempt release after actual
current canonical S3, unchanged committed protocol and normal admission. The
existing supervisor owns a lease and consumed-release marker, records interpreter/
NumPy identities, constrains one worker/thread to 2GiB and 21600 CPU/wall seconds
with a fresh deadline and kills the process group on timeout. No retries or new
paid capacity.

Pair output events and bound cost summary flush before pair checking. Query
output, its actual counters and endpoint records flush before query checking.
Phase journals flush completed or failed prefixes. Rejection leaves unchecked
producer output and unknown remaining work. Close table writers, losslessly gzip
journals with encoded/decoded hashes, then pause for a real canonical S3 checkpoint
after each curve. No restore/retry; restored wall clocks never become valid.
Analysis preserves missing rows for all planned methods and verifies output/check
commitments and full phase conservation before complete status. Raw records are
pushed before any report rendering. Publish every outcome with report/graphs/
inspected PDF, exporter, append-only database and closed benchmark/progress in
the same PR, plus truthful artifact-pinned PCC standing and official S3 custody.

The earlier A14 release is consumed and cannot authorize A15. A source-ready
assessment does not itself release execution or provide independent scientific
standing. After this bounded result, rank the stronger known48 target-effort or
unknown16 outside-pool tests; do not close the standing campaign for batch/PR
completion.
