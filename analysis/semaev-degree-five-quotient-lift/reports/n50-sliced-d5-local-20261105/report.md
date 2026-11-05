# One bounded n50 sliced D5 lift: projected quotient kills the constant

The single frozen degree-five producer attempt on `fresh-n50-poly-03` ended with `projection_kills_one`. Its provisional quotient had 79,556 working coordinates and relation rank 79,556; the native program emitted no D5 certificate. The fresh exact solution count was zero. The result does not provide a D5 nonmembership certificate or an LFD ≥ 6 lower bound, and it does not prove that 1 belongs to the true degree-five closure: the native construction is an over-approximation.

The input was the independently accepted 49-variable affine-sliced D4 map, SHA-256 `2f0facb6b047c857908e7f44e8558248af426dae10454263294df1a93d39cce8`. The [seed report](../n50-sliced-seed-rebase-20261105/report.md) records its checker acceptance. [Protocol V2](../../n50-poly03-sliced-d5-local-protocol-002.json) and the [exact plan](../../n50-poly03-sliced-d5-local-plan-002.json) were frozen and pushed before D5 data. The producer ran once, with one CPU core, a 36 GiB child address-space cap, a six-hour watchdog, no checkpoint, and no automatic retry. The terminal result was written about 3,110 seconds after producer start, within the watchdog. The last sampled RSS was approximately 25 GB; it is not a measured peak.

| Stage | Recorded result |
| --- | --- |
| Fresh original count | 0; exit 0 |
| Producer admission | 79,556 working coordinates; 40,927 border coordinates; binary-reported envelope 35,385,141,521 bytes |
| Provisional map | Constructed; 466 rewrite blocks, 17,405,931 internal edges, 35,519,710,481 external edges |
| Relation processing | Rank 79,556, equal to working dimension; `projection_kills_one`; exit 0 |
| D5 certificate | None |

The source-side profile estimated 34,760,782,170 bytes for the bounded native envelope, while the binary reported 35,385,141,521 bytes at admission. Both are below the 36 GiB child cap, and the discrepancy remains unresolved; neither figure is measured RSS. The attempt reserved USD 12 under one shared USD 200 daily allowance. At the observed Spot price of USD 0.7956/hour, 3,110 seconds corresponds to about USD 0.69 of whole-host time, but the host carried concurrent n51 seed work, so this is not an attributable AWS charge. Build, idle, failure, storage, and transfer remained inside the reservation.

The [flow diagram](flow.svg) shows where this route stopped. [Evidence metadata](evidence.json) pins the exact result, stage transcripts, hashes, launch revision, limits, and local seed. The raw receipts are in [raw/](raw/). The next proof-producing route is the independently checked n51 affine-sliced D4 seed. A n51 D5 producer needs its unit-coordinate layout and bounded native profile before launch; any emitted D5 map must pass the independent D5 checker and exact-count bridge before an LFD ≥ 6 claim.
