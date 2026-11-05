#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Fresh curve and target source-selection holdouts
Run #raw("a6-fresh-holdouts-97bb80") completed 96 fixed curve/schedule/prefix/scope observations, unknown cells 0. Four curves and 32 public targets were generated only after exact source publication, prospective protocol freeze and native admission. Native base widths are 16 over 8191 and 32 over 65537; original-window projections are fixed within each curve and retain their actual measured width.

#image("rank.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[schedule],[rank/U],[source rows],[anchor gain],[joint targets],[with base uncertainty],
[p8191-i0],[window],[15/15],[34],[0],[3],[0],
[p8191-i0],[hash0],[15/15],[30],[0],[3],[0],
[p8191-i0],[hash1],[15/15],[35],[0],[3],[0],
[p8191-i0],[hash2],[15/15],[36],[0],[3],[0],
[p8191-i1],[window],[16/16],[35],[0],[4],[0],
[p8191-i1],[hash0],[16/16],[49],[0],[4],[0],
[p8191-i1],[hash1],[16/16],[38],[0],[4],[0],
[p8191-i1],[hash2],[16/16],[39],[0],[4],[0],
[p65537-i0],[window],[29/31],[34],[0],[5],[0],
[p65537-i0],[hash0],[28/31],[28],[0],[5],[5],
[p65537-i0],[hash1],[30/31],[42],[0],[4],[4],
[p65537-i0],[hash2],[31/31],[38],[0],[5],[0],
[p65537-i1],[window],[29/31],[31],[0],[0],[0],
[p65537-i1],[hash0],[30/31],[30],[0],[3],[3],
[p65537-i1],[hash1],[30/31],[48],[0],[2],[2],
[p65537-i1],[hash2],[31/31],[42],[0],[3],[0],
)
Measured exact finite counts/ranks at prefix 64. The relation-only scope uses the same original-window projection and target rows across all four arms. Anchor gain is rank(M plus explicit anchors) minus rank(M). A larger base or outside target block is never credited as independent base information. Single and joint target certificates, complete kernels, outside-target cancellation Delta and union ranks are retained at every prefix and in both scopes.

#pagebreak()
== Separate source-construction costs
#image("construction.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto),inset:4pt,
[fixture],[schedule],[scalar calls],[group additions],[Fp mul],[Fp inv],
[p8191-i0],[window],[64],[521],[2683],[457],
[p8191-i0],[hash0],[64],[1180],[6416],[1116],
[p8191-i0],[hash1],[64],[1214],[6594],[1150],
[p8191-i0],[hash2],[64],[1175],[6437],[1111],
[p8191-i1],[window],[64],[521],[2683],[457],
[p8191-i1],[hash0],[64],[1201],[6519],[1137],
[p8191-i1],[hash1],[64],[1164],[6328],[1100],
[p8191-i1],[hash2],[64],[1217],[6571],[1153],
[p65537-i0],[window],[64],[521],[2683],[457],
[p65537-i0],[hash0],[64],[1509],[8203],[1445],
[p65537-i0],[hash1],[64],[1476],[8076],[1412],
[p65537-i0],[hash2],[64],[1506],[8234],[1442],
[p65537-i1],[window],[64],[521],[2683],[457],
[p65537-i1],[hash0],[64],[1480],[8120],[1416],
[p65537-i1],[hash1],[64],[1525],[8283],[1461],
[p65537-i1],[hash2],[64],[1467],[8053],[1403],
)
These are measured per-arm construction counters for all 64 public source scalars, not total attack costs. Group additions overlap their Fp primitives, and inversions have unpriced internals. A hash arm also requires the fixed original-window anchors: include window construction, fixed projection and shared setup/sign/table work in a cold interpretation. Generation computed the window once to freeze its projection; collection computed it again. Both physical stages remain separately charged. Prefix 0 already has all schedule source points available; construction is not free at that prefix.

Actual physical collection: 4928 pair entries, 49152 source queries and 1536 target queries. Four tables and target streams are reused across 16 actually queried schedules; repeated source scalars are queried and charged in every arm. Every candidate, bucket, miss and accepted sign pattern is retained. Disjoint phase records cover construction, extraction, certification, projection, elimination, kernels, target-column cancellation, window-union rank and carried certificates. Per-arm summaries are references to those phases, not extra work.

Generation checked 122 candidate records and 4038640 order point tests, plus all target draws. The explicit previous four (p,b) pairs and selected duplicates are rejected before eligibility work. The first remaining eligible prime-order nonanomalous a=2 curve with sufficient distinct norm atoms is selected. The base is the existing first distinct x-squared norm construction, and P the first rational point. No rank, relation yield or target recovery selects a curve, target or seed.

#pagebreak()
== Public target functionals and verification
Across the retained relation-only prefix records, 15 distinct targets are identified, of which 8 are identified with base uncertainty remaining after target-column cancellation. There are 14 such curve/schedule/prefix/target records, reusing the same 32 public targets across schedules and prefixes. These are exact finite observations, not independent repeated target draws or a population success rate.

#table(columns:(auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[schedule],[prefix],[target],[scalar],[rank/U],[bounded matches],
[p65537-i0],[hash0],[64],[0],[61032],[28/31],[0],
[p65537-i0],[hash0],[64],[2],[60584],[28/31],[0],
[p65537-i0],[hash0],[64],[3],[6296],[28/31],[2],
[p65537-i0],[hash0],[64],[5],[55495],[28/31],[0],
[p65537-i0],[hash0],[64],[7],[17990],[28/31],[0],
[p65537-i0],[hash1],[64],[2],[60584],[30/31],[0],
[p65537-i0],[hash1],[64],[3],[6296],[30/31],[2],
[p65537-i0],[hash1],[64],[5],[55495],[30/31],[0],
[p65537-i0],[hash1],[64],[7],[17990],[30/31],[0],
[p65537-i1],[hash0],[64],[0],[46161],[30/31],[0],
[p65537-i1],[hash0],[64],[1],[6779],[30/31],[0],
[p65537-i1],[hash0],[64],[6],[25803],[30/31],[0],
[p65537-i1],[hash1],[64],[1],[6779],[30/31],[0],
[p65537-i1],[hash1],[64],[6],[25803],[30/31],[1],
)
Display rule: first 24 retained deficient-base records in fixed fixture/arm/prefix/target order; all records and full misses are in plotted-data.json and the raw panel. Every reported scalar carries vN=0 or target-unit row weights, RHS and independently checked [k]P=Q. Target scalar labels never enter generation or solver inputs. The separately retained t=1..64 public-multiple diagnostic distinguishes original/scheduled source membership and signed base coincidences. A bounded nonmatch excludes only those finite coincidences.

Across both scopes, 9 distinct targets are identified while base uncertainty remains. The extra case is p8191-i0/hash2/target5 at prefix16 in the explicit-anchor scope: rank10 becomes11 of15 after inserting the public atom10 equation -z10=7192 (mod8101). Its scalar7948 is checked publicly. All64schedule points were constructed and known at this prefix, so this is not a cold16source construction. The registered diagnostic also records [53]Q=-[8]P, an alternate public explanation; this extra case is kept separate from the eight relation-only targets. The original report directory remains a valid relation-only summary; this expanded report adds scope accounting without changing native data.

The separate implementation reconstructs all curve/exclusion/EC1/base/projection/target recipes, the full 88,320 signed-triple census once across four curves, all pair and source/target queries, explicit anchors, affine consistency/ranks/full kernels, union and outside-target cancellation ranks, carried weights and public recovery equations. Counter conservation and 64-call construction checks do not independently audit every primitive call. This is separate implementation checking, not staffed scientific review.

- p8191-i0: p=8191, a=2, b=2473, r=8101, native atoms=16, U=15. EC1 urn:ec-record:1:sha256:ea55ad1027fbd5d2927db683800e86b814d3e19dd362c9ddb5ae7114819567d3.
- p8191-i1: p=8191, a=2, b=5699, r=8087, native atoms=16, U=16. EC1 urn:ec-record:1:sha256:83485f9c29de5433fa292b34f1f6e5a860fe9ccc2c5e24730f9cc2b2097af06e.
- p65537-i0: p=65537, a=2, b=30320, r=65053, native atoms=32, U=31. EC1 urn:ec-record:1:sha256:2415f1721f88e860fd929042205599af3a878a9c8e9b74b78e8e137f61d576b6.
- p65537-i1: p=65537, a=2, b=52897, r=65633, native atoms=32, U=31. EC1 urn:ec-record:1:sha256:3ab32b566e73a3eeb42d8614471cde029405420f5cb5da0f75438e3cf7f26544.

Scientific source #raw("be5067af0c343fd7bd303d1c8b096c151d6018a8"); selected protocol SHA256 #raw("65636567c71435e240c5b8820592c15ff6fa4471b2d994c6241a03ce2fd49935"); 24 dependency paths plus one rules input. Exit 0, timeout False, source unchanged True. Diagnostic wall 10.649s, user CPU 8.585s, system CPU 1.671s, RSS 66740224 bytes; wall_valid=false. One existing workstation process/thread, 2 GiB/21600-second protective CPU/wall watchdog; no new paid submission.

Raw records were committed and pushed before this report. Manifest-backed raw files and lossless gzip hashes preserve all outcomes; the fresh v9 database retains the v8 parent and inherited rows. Sources: A5 RESULTS.md, design.md/literature.md and PKM2016 primary sections 3.1–3.4, reread pages 7–9 (https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf). Four small hash-selected fixtures and three fixed source seeds bound transfer; no general rank law follows. Software controls and the unified export were checked. The scoped graph supplements historical reports without changing official scientific states. Configured model identity remains unverified; sparse full-ledger validation was refused rather than claimed passed.
