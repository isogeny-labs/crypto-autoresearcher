#set page(paper:"a4",margin:15mm)
#set text(size:9pt)
= Fresh progression/hash source holdout
Run #raw("a10-ap-holdout-276654"): four fresh curves (p8191/base16 and p65537/base32, two each),32public target points,3pairedAP/hash seeds,128sources/schedule,9prefixes,two knowledge scopes,two cold kernel-free solvers. All432dependent systems and864solver calls checked; zero unknowns. Prefixes/scopes/seeds reuse these32points. Identified repeated slots in each solver: 605. Separate independent generation, complete signed-triple and query-miss oracles, dense membership/negative residual/echelon span checks and original-row/public certificates pass. No independent staffed scientific review has occurred.
#image("target-recovery.svg",width:100%)
Target counts are determined unit columns, without requiring full factor-base rank. Anchor scope includes only paid constructor/public-prerequisite base and direct-target equations; relations scope uses natural collected triples. Ucolumns stay fixed. Delta is joint rank minus outside-column rank minus source rank. Every per-prefix Delta, normalized equation count and identified target index remains in analysis.json and raw certificates.

Source #raw("dfb7f95697a334223e79d6432de1f3de60738e60"); protocol #raw("7f7bb92d8f6793e0ae0d57522f468e9d2d5efcb6ec6b24fa3fcfd9f2bd4182db"). Exact commands, environment, ownership and immutable file digests are in execution.json/host.json/admission and the unified export. Inclusive user/system CPU 27.469328/1.788709s; diagnostic wall 29.237756s; RSS 96124928bytes. One existing shared-host worker/thread,2GiB,21600CPU/wall-second protective limit,one attempt. Clocks are not isolated performance measurements.
#pagebreak()
= Charged source construction and retained knowledge
#image("constructor-calls.svg",width:100%)
Each cell below is AP/hash, at the fixed128source budget with explicit anchors. Window0 is binary; windows1..8 use the actual repository FixedBaseMultiplier. The policy minimizes exact group-add API calls using all public horizon labels, with binary then ascendingwindow ties. It does not optimize weighted Fp/Fr cost. Nine scalar-only simulations are measured policy work; only one selected EC constructor runs per schedule. Setup is lazy and charged at first positive budget; lower-budget policies are not reoptimized after outcomes.
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[curve],[seed],[window],[constructor calls],[source rank],[targets],
[p65537-i0],[0],[1/6],[164/520],[30/31],[2/2],
[p65537-i0],[1],[1/6],[156/523],[31/31],[2/2],
[p65537-i0],[2],[1/6],[157/526],[31/31],[2/2],
[p65537-i1],[0],[1/6],[161/523],[32/32],[3/3],
[p65537-i1],[1],[1/6],[153/521],[32/32],[3/3],
[p65537-i1],[2],[1/6],[159/515],[32/32],[3/3],
[p8191-i0],[0],[1/5],[152/436],[14/14],[2/2],
[p8191-i0],[1],[1/5],[151/428],[14/14],[3/2],
[p8191-i0],[2],[1/5],[155/426],[14/14],[2/2],
[p8191-i1],[0],[1/5],[153/437],[16/16],[4/4],
[p8191-i1],[1],[1/5],[154/437],[16/16],[4/6],
[p8191-i1],[2],[1/5],[156/436],[16/16],[4/4],)
All constructor table/intermediate/APstep/walk points have public scalar labels and first-paid-prefix records. Cache lookup, sign negation, base/target scanning and storage are charged. The shared1..64 prerequisite uses63walk adds. Constructor branches never import other schedules' or future prefixes' points. Query/checker intermediates are outside this supplied-cache boundary, which is operational and makes no secrecy claim.
#pagebreak()
= Separate component vectors and scope
#table(columns:(auto,auto,auto),inset:4pt,[logical unit],[joint],[cancellation first],
[Fr.field_add],[35920],[35965],
[Fr.field_sub],[700348],[706961],
[Fr.field_mul],[786587],[764255],
[Fr.field_inv],[7970],[6774],)
Solver totals include cold construction/cancellation, elimination, direct row-space identification, certificate lifting, original-row verification and public checks. Neither method computes a full production kernel. Every phase, negative residual and complete certified echelon span is retained. Shared projection is charged once per scope case outside these arm totals, not free or multiplied across views.
#table(columns:(auto,auto),inset:3pt,[physical collection unit],[calls],
[Fp.field_add],[4280],
[Fp.field_sub],[1313810],
[Fp.field_mul],[507027],
[Fp.field_inv],[165922],
[source_queries],[147456],
[target_queries],[1536],
[pair_table_insertions],[4928],
[constructor_group_add_calls],[7599],
[constructor_policy_simulated_adds],[104515],
[labelled_points_stored],[6746],)
Physical collection counts sum each shared table/target stream and each disjoint schedule increment once. Cold prefix cost references include shared setup, prepaid policy, that arm's construction/query/knowledge prefix, projection and chosen solver. Prefix views overlap; do not sum them as new physical work. Other actual arm and diagnostic work stays in campaign accounting. Group calls overlap Fp primitives; Fp and Fr add/sub/mul/inv stay distinct, with no invented scalar-equivalent weights.

Generation retains every rejected candidate and point-test trace. Its legacy field_add merges subtraction and some rejected-fixture arithmetic is not primitive-expanded. Inversion/pow/hash/sort/Python/IO and independent checker internals also are not fully primitive-expanded; inclusive process CPU/RSS and separate generation/checker diagnostics remain recorded. These finite component vectors do not establish an end-to-end runtime advantage or a population effect.

Sources checked: A4/A6/A7/A8/A9 internal results and exact implementation; repository targets.py fixed-base constructor; Petit, Kosters and Messeng 2016 prime-ECDLP primary paper pp7-9, retained SHA a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b. The research-kb service was unavailable (wrapper127); direct scoped source retrieval is documented in literature.md, without corpus-wide absence or novelty claims. No canonical isogeny graph edge changes: this is a source/solver comparison on fresh synthetic curves.
