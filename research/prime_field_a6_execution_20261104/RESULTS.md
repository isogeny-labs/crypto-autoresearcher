# Fresh holdouts retain target recovery before full base rank

The prospectively frozen A6 panel completed **96 scope observations with no
unknowns** on four new coefficient curves and 32 new public point targets.
Selection used the first eligible hash-derived curves, excluding the four A4
curve pairs before eligibility work. Neither relation yield, rank nor target
recovery selected an input. Base and original-window projection stayed fixed
within each curve across all schedules and prefixes.

| Fixture | b (a=2) | Group order | Fixed U | Window rank | Hash0 rank | Hash1 rank | Hash2 rank |
|:--|--:|--:|--:|--:|--:|--:|--:|
| p8191-i0 |2473|8101|15|15|15|15|15|
| p8191-i1 |5699|8087|16|16|16|16|16|
| p65537-i0 |30320|65053|31|29|28|30|31|
| p65537-i1 |52897|65633|31|29|30|30|31|

These are relation-only ranks at 64 sources. Native bases have 16/32 atoms;
the measured U widths include the original window's known public anchors.
New anchors were retained as explicit affine rows. Every final marginal anchor
gain is zero. The fixed hash2 schedule reaches full original-column rank on all
four fresh fixtures; its outcome was not used to change the other schedules.

**Eight distinct fresh targets were identified with base uncertainty remaining
after target-column cancellation**, across 14 curve/schedule/target records.
All occur at prefix 64 in the relation-only scope; targets are reused across
schedules, so these are not 14 independent target draws. Eleven records have
no registered t=1..64 public-multiple match; three have bounded matches. The
diagnostic excludes only its declared finite coincidences.

| Fixture/schedule | Source rank/U | After target cancellation | Single-row targets | Joint targets |
|:--|:--|:--|--:|--:|
| p65537-i0/window |29/31|31/31|0|5|
| p65537-i0/hash0 |28/31|30/31|2|5|
| p65537-i0/hash1 |30/31|30/31|4|4|
| p65537-i0/hash2 |31/31|31/31|5|5|
| p65537-i1/window |29/31|29/31|0|0|
| p65537-i1/hash0 |30/31|30/31|3|3|
| p65537-i1/hash1 |30/31|30/31|2|2|
| p65537-i1/hash2 |31/31|31/31|3|3|

The joint system on p65537-i0/hash0 recovers five targets where isolated natural
rows identify two, while one base direction remains unresolved. Every identified
target carries row weights, RHS, full-kernel checks and separate public [k]P=Q
verification. Target scalar labels were outputs only. Across all four arms,
15 of the 32 targets were recovered; targets without a usable relation remain
in the retained records. No relation-only early recovery occurred at prefix
0/16. The explicit-anchor scope has one additional earlier case: p8191-i0,
hash2, target5 at prefix16, scalar7948. A public atom10 anchor raises rank10/15
to11/15 and identifies that target, while all64schedule source points remain
public and charged. The registered diagnostic also finds [53]Q=-[8]P, an
alternate public explanation. Across both scopes there are nine distinct
deficient-base targets; the eight-target count above is explicitly relation-only.

Target cancellation is scored by
`Delta = rank([[M,0],[B,Utarget]]) - rank(Utarget) - rank(M)`.
At prefix 64 on p65537-i0 it adds two dimensions for window and hash0;
all other final cases add zero. Full cancellation vectors carry original-row
weights and match the dense rank oracle. New outside target unknowns do not
inflate the base-only score.

## Separate source-construction costs

Each arm constructed exactly 64 public source scalars in its own phase.
This table transcribes Fp multiplication counters for that phase only.

| Fixture | Window | Hash0 | Hash1 | Hash2 |
|:--|--:|--:|--:|--:|
| p8191-i0 |2683|6416|6594|6437|
| p8191-i1 |2683|6519|6328|6571|
| p65537-i0 |2683|8203|8076|8234|
| p65537-i1 |2683|8120|8283|8053|

The window uses 521 group additions per curve; hashes use 1164–1525, with
different scalar bit lengths. Per-arm inversions, Fp calls and diagnostic
times are retained. Group additions overlap their field primitives, so these
units are not summed into a weighted total. A cold hash-arm interpretation must
include original-window anchor construction, fixed projection, shared setup/sign
and table work. Generation constructed the window to freeze its projection;
collection constructed it again, and both actual stages are charged separately.
The measured higher construction cost accompanies the changed relation spans;
equal query counts alone are not a complete cost comparison.

One physical process collected 49,152 source queries, 1,536 shared target
queries and 4,928 signed pair entries. It retained 589 source witnesses, five
explicit anchor witnesses and 21 shared target witnesses. Sixteen schedules
were actually queried, including overlap. Generation retained 122 candidate
records and checked 4,038,640 order point tests, plus every target draw.
The separate oracle enumerated all 88,320 signed triples once over the four
curves and checked all source/target query buckets, accepted/missed rows,
recipe/exclusion/EC1/projection facts, anchors, affine consistency, complete
kernels, union/cancellation ranks, carried weights and public equations.
This is separate implementation verification, not staffed scientific review
or an audit of every primitive counter.

Native run **a6-fresh-holdouts-97bb80** finished with exit 0, no timeout or
exception, and source unchanged. Diagnostic wall 10.649069378 s, user CPU
8.585481 s, system CPU 1.670991 s, RSS 66,740,224 bytes; wall_valid=false.
One existing workstation process/thread, 2 GiB and 21600-second protective
CPU/wall watchdog, one attempt; no new paid infrastructure was submitted.

## Source, checks and publication

Scientific source **be5067af0c343fd7bd303d1c8b096c151d6018a8**;
[frozen protocol](protocol.json), SHA256
**65636567c71435e240c5b8820592c15ff6fa4471b2d994c6241a03ce2fd49935**.
Exact 24 dependency paths and one rules input, prospective administrative
assessment, Git publication, actual S3 checkpoint, explicit root release and
ownership preceded native generation. All 55 software controls passed,
including tiny generation/exclusion/target corruption, deterministic A/A,
per-arm construction, complete 96-row export and committed-metric checks.
Export --verify-files has zero findings. Full-ledger validation refused a sparse
checkout with 112982 off-disk records; a full-ledger pass is not claimed.

Raw data were committed/pushed in **2ab24a2aa1** before report rendering.
Fourteen primary raw objects are officially stored and remote-verified under
[the raw manifest](runs/a6-fresh-holdouts-97bb80/raw/.artifacts.json).
Ten large raw files were losslessly gzip encoded, with original/archive hashes.
The [expanded inspected report](reports/a6-fresh-holdouts-97bb80-all-scopes/report.pdf)
includes both [rank](reports/a6-fresh-holdouts-97bb80/rank.svg) and
[construction](reports/a6-fresh-holdouts-97bb80/construction.svg) graphs;
[plotted-data.json](reports/a6-fresh-holdouts-97bb80/plotted-data.json)
retains the original relation-only observations; the expanded directory adds
all-scope accounting. The original three-page PDF remains intact and valid for
its stated relation-only summary. The benchmark record's eight-target metric
uses that same scope, rather than silently mixing in the extra anchor case.
Hydrate pointers with
`python3 tools/artifacts/artifacts.py pull research/prime_field_a6_execution_20261104`.

The [v9 database receipt](database/v9-fresh-holdouts/generation-v9.json)
records unchanged v8 parent bytes, inherited-row preservation, integrity/FKs
and gzip roundtrip. It adds four curves/bases, one execution, 16 schedules,
594 source/anchor witnesses, 32 targets, 21 target witnesses, 96 certificate
records and the full generated selection trace. Historical totals are now
10 curves/bases and 10 physical executions. The archive and PDF are S3 verified.
The benchmark record and generated progress index use measured units without
inventing S or a matched reference. The committed exporter emits 643 A6 samples,
charging construction once per arm rather than per prefix/scope.

This is a four-curve finite holdout result under exact hash-defined recipes,
not a population law. Field and base widths remain coupled. A useful next
control is a matched source-budget sweep with fine-grained construction costs
and single-row versus joint-target recovery, retaining fixed columns and all
shared prerequisites. The scoped graphs supplement historical reports; no
official scientific state changed. Sources: [literature.md](literature.md),
[design.md](design.md), A5 results and PKM2016 primary sections 3.1–3.4.
