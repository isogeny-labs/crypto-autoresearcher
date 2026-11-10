# Direct W4 rank on the independently reconstructed n51 slice

The one direct fixed-point calculation terminated normally with rank
226,437 in 272,052 degree-at-most-four columns, exactly the kernel
dimension of the separately checker-accepted sliced D4 quotient. It
reported `W4_one 0`, three closure iterations and low-degree dimension
10,194. Under the [audited direct-algorithm invariant](../../DIRECT-W4-RANK-AUDIT.md),
the computed rowspace is W4. Since the independent quotient check gives
`W4 subset ker(pi4)` and both spaces have dimension 226,437, the retained
sliced D4 kernel equals W4 under that native computation. This is an
independent direct-rank calculation and input reconstruction, not a
separately checked primal row-derivation certificate.

The [frozen V2 protocol](../../n51-poly01-direct-w4-rank-protocol-002.json),
[plan](../../n51-poly01-direct-w4-rank-plan-002.json) and runner were
committed and pushed at `ec169146c870d465e7f7deb29f1b4517ea9382eb`
before the one rank trial. The independently reconstructed input has 51
quadratic generators and 15,189 term masks, SHA-256
`d3c76b713b7fd9c54d84f0dc75a463766d84636f3c5e73c0b7c75aa1bedd9327`.
The native binary SHA-256 is
`f7f920e697b263129e91b44814e18c32b228392496770c29869ab4d00a9e6f04`.
The earlier V1 pretrial build failed before a rank run; its failure is
retained in the raw archive. V2 reused the pinned binary under the same
cumulative USD 12 ceiling and performed no second build.

The native child started at 19:10:01 UTC and finished at 21:00:37 UTC on
2026-11-05. The wrapper measured 6,636.46 seconds, exit zero and no
timeout under the 14,400-second watchdog and 32 GiB address-space cap.
Admission sampled 119,242,817,536 bytes MemAvailable. Its delayed AWS
budget readbacks were USD 108.214 / 200 and USD 48.383 / 200 for two
nonadditive daily thresholds, and USD 582.453 / 1,000 monthly. These
readbacks are not a measured per-attempt bill.

The [manifest](manifest.json) hashes all nine copied write-once files:
the V1 [build failure](raw/build.finished.json), V2 [admission](raw/v2.admission.json),
[start](raw/v2.started.json), [finish](raw/v2.finished.json),
[stdout](raw/v2.stdout.txt), [stderr](raw/v2.stderr.txt) and
[terminal result](raw/v2.result.json), with the associated build streams.
The finish receipt's stdout and stderr hashes match the archived bytes;
the result embeds that finish receipt and matches the prespecified target
rank. A fresh independent replay or a checked primal derivation would
further strengthen the computation, but is not needed as a premise for a
positive independently checked D5 quotient on the separate six-solution
polynomial-00 system.
