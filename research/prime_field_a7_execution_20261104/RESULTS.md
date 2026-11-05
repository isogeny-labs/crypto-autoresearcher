# Checked source budgets expose earlier joint-target recovery

A7 completed **288 curve/schedule/budget/scope observations with no unknowns**
on all four already observed A6 curves/bases and their 32 fixed public targets.
No new curve or target was generated. Original columns stayed fixed; new
scheduled-point anchors and diagnostics used only the first b points at budget b.
The shared original-window 64-point prerequisite remained public and charged.

On **p65537-i0/window**, the joint system identified all five decomposed targets
at the checked budget **48**, while isolated natural rows first identified them
at **96**. At 48, source rank was 24/31 and target-column cancellation added
five dimensions, giving 29/31: two base directions remained unresolved. This
is a finite algebra/collection-budget observation, not a weighted-cost speedup
or an exact threshold between checked levels.

| Fixture | Schedule | First checked full source rank | First individual target | First joint target |
|:--|:--|--:|--:|--:|
| p8191-i0 |window|48|32|32|
| p8191-i0 |hash0|48|24|24|
| p8191-i0 |hash1|24|24|24|
| p8191-i0 |hash2|48|24|24|
| p8191-i1 |window|48|48|48|
| p8191-i1 |hash0|24|24|24|
| p8191-i1 |hash1|48|48|48|
| p8191-i1 |hash2|48|48|48|
| p65537-i0 |window|96|96|48|
| p65537-i0 |hash0|128|64|64|
| p65537-i0 |hash1|96|48|48|
| p65537-i0 |hash2|64|48|48|
| p65537-i1 |window|96|96|96|
| p65537-i1 |hash0|128|64|64|
| p65537-i1 |hash1|96|48|48|
| p65537-i1 |hash2|48|48|48|

This table uses the relation-only scope. First full source-rank budgets in the
explicit-anchor scope are identical here. All sixteen curve/schedule combinations
reach full original-column rank by 128 sources. Every checked budget
0/8/16/24/32/48/64/96/128 was retained regardless of earlier success; all
individual and joint target certificates remain available.

Across retained budgets, 15 distinct targets were identified. Ten were identified
while base uncertainty remained, in both the relation-only and all-scope views.
These are reused targets across budgets, schedules and scopes, not independent
target draws at every row. Both 64-budget scopes reproduce A6 source/target
descriptors, affine systems, complete kernels and target certificates exactly.
The finer grid exposes observations missed by A6's 0/16/64 grid.

## Prefix knowledge and costs

The earlier A6 p8191-i0/hash2/target5 case at prefix16 used the point from
source7192, which is at **index54** in the frozen stream. A6 deliberately made
all64points public at every prefix and charged their construction. A7 changes
that operational boundary: the target is first identified at checked budget24,
in either scope, through the available relation rows; the source54 anchor is
not yet available. The registered alternate public equation [53]Q=-[8]P
remains an explanation. The old A6 report and benchmark are preserved.

Future source scalars are publicly computable, and prior A6 records exist.
This is a controlled supplied-point/cost boundary, not a secrecy assumption or
an optimality claim. Prior recovered target labels are not solver inputs.
Budget-specific diagnostics use only first-b scheduled points plus original64
anchors and do not inject labels into the solver.

| Schedule | New scalar calls through16 | Through32 | Through64 | Through128 |
|:--|--:|--:|--:|--:|
| window |0|0|0|256|
| hash0 |64|128|256|512|
| hash1 |64|128|255|509|
| hash2 |64|128|256|511|

These measured calls sum scheduled construction over four curves. Add the
shared **256 prerequisite calls** for a cold interpretation of this physical
panel; a single-curve arm needs its64original anchor points. The window's
zero scheduled calls through64 are cache hits, not free cold setup. The exact
original64scalar-key cache is available uniformly to all arms; no future
cross-schedule point cache is credited. Full128source hash derivation is prepaid.

Construction, query, anchor scan, shared setup/table/target work, budget
diagnostics and each algebra phase have separate counters. Prefix cost views
reference disjoint physical blocks and are not summed again over budgets or
scopes. Optional window-union rank uses extra window relations and has separate
cost. Overlapping Fp/Fr/group/logical units do not form a weighted scalar total.
First checked budgets do not locate exact first-source counts between checks.

## Execution and retained checks

One supervised process executed **98,304 source queries**, 1,536 shared target
queries and 4,928 pair entries across16source schedules. Twelve closed raw
snapshots/journals were losslessly gzip encoded and officially S3stored and
remote-verified. The independent implementation reconstructed the full88,320
signed-triple census once over four curves, every source/target query bucket,
candidate and sign, prefix-only anchor and diagnostic, cache/block counter
references, affine rank/full kernel, cancellation/union rank, target weights
and public [k]P=Q equation. Information/identified-target monotonicity was checked.
This is separate implementation checking, not staffed scientific review or an
audit of every primitive operation.

The 4096-row protective limit is cumulative across the entire source stream;
a tiny regression exercises several individually small blocks whose sum
exceeds the cap. Refusals retain the accepted journal prefix. Native resource
limits were one existing workstation process/thread, 2 GiB and21600CPU/wall
seconds, one attempt/no automatic retry. No paid capacity was submitted.

Run **a7-source-budgets-d1f98d**, source
**af75ea40a8af8e31aa0fc2a75417b4f41fdad112**, protocol
**ef7445037a2714476a522a0defac1eeb5be66382760e81c60b5861b873e00332**.
Exact24dependency paths plus copied inputs, prospective administrative assessment,
Git publication/freeze, actual canonical S3checkpoint, explicit root release
and ownership preceded native work. Exit0, no exception/timeout, source unchanged.
Diagnostic wall15.981814699s, userCPU14.055564s, systemCPU1.450716s,
RSS98,545,664bytes; wall_valid=false.

All69software controls passed, including cumulative cap, future-anchor/diagnostic,
cache/cost/journal/certificate corruption, deterministic A/A and288row export/seed
checks. Export --verify-files has zero findings. Full-ledger validation refused
112982sparse off-disk records; a full pass is not claimed. The committed exporter
emits1731A7samples without multiplying physical work across views.

Raw data were committed/pushed in **6673f55a98** before rendering the
[inspected three-page report](reports/a7-source-budgets-d1f98d/report.pdf).
The [rank graph](reports/a7-source-budgets-d1f98d/rank.svg),
[target graph](reports/a7-source-budgets-d1f98d/targets.svg) and
[plotted data](reports/a7-source-budgets-d1f98d/plotted-data.json) retain the full
displayed table and all recovery records. The [raw manifest](runs/a7-source-budgets-d1f98d/raw/.artifacts.json)
and unified export bind every encoded scientific record. Hydrate with
`python3 tools/artifacts/artifacts.py pull research/prime_field_a7_execution_20261104`.

The [v10 database receipt](database/v10-source-budgets/generation-v10.json)
records unchanged v9parent bytes, inherited-row preservation, integrity/FKs and
gzip roundtrip. It adds one execution,16schedules,1167source/anchor witnesses,
32reused target slots,21target witnesses,288certificate records and144budget
diagnostics. Historical totals are10curves/bases and11physical executions.
The archive and PDF are officially S3stored/remote-verified. No old run, report,
closed benchmark record or official scientific state is rewritten.

A concrete next comparison is **cancellation-first target recovery versus the
full joint solver on these same immutable rows**, including certificate lifting
and separate Fr costs. A7 already retains all target-column cancellation vectors;
using them as base-only equations may simplify the implementation without
changing identifiable functionals. Equivalence and costs require the next
controlled implementation comparison; no such result is claimed here.
Sources: [design.md](design.md), [literature.md](literature.md), A6 results and
PKM2016 primary sections3.1–3.4. Four observed curves and three fixed hash seeds
bound this conditioned follow-up; no population threshold is inferred.
