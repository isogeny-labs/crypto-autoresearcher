#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Fixed-base source selection and natural target recovery
Run #raw("a5-source-control-c0c8a9"). The three fixed hash schedules increased source coverage on the same four observed A4 fixtures. Hash2 reached full original-column rank on all four; hash0/hash1 recovered target functionals with uncertainty remaining on both65537fixtures. Exact original-window relations, targets, affine matrices, complete kernels and target certificates reproduce A4. All96scope observations completed, with zero unknowns.

#image("rank.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[schedule],[rank/U],[source rows],[extra anchor gain],[union gain over window],[joint targets],[with base uncertainty],
[p8191-i0],[window],[15/16],[30],[0],[0],[0],[0],
[p8191-i0],[hash0],[16/16],[31],[0],[1],[4],[0],
[p8191-i0],[hash1],[16/16],[48],[0],[1],[4],[0],
[p8191-i0],[hash2],[16/16],[34],[0],[1],[4],[0],
[p8191-i1],[window],[14/14],[34],[0],[0],[1],[0],
[p8191-i1],[hash0],[14/14],[27],[0],[0],[1],[0],
[p8191-i1],[hash1],[14/14],[40],[0],[0],[1],[0],
[p8191-i1],[hash2],[14/14],[31],[0],[0],[1],[0],
[p65537-i0],[window],[30/32],[45],[0],[0],[0],[0],
[p65537-i0],[hash0],[30/32],[41],[0],[2],[3],[3],
[p65537-i0],[hash1],[30/32],[35],[0],[2],[3],[3],
[p65537-i0],[hash2],[32/32],[52],[0],[2],[4],[0],
[p65537-i1],[window],[23/31],[27],[0],[0],[0],[0],
[p65537-i1],[hash0],[28/31],[31],[0],[8],[4],[4],
[p65537-i1],[hash1],[30/31],[42],[0],[8],[3],[3],
[p65537-i1],[hash2],[31/31],[43],[0],[8],[4],[0],
)
Values are measured exact finite counts/ranks at64sources. Union gain is derived rank(Mwindow+Marm)-rank(Mwindow), with unchanged columns; it includes extra collected window rows and is not a same-budget replacement result. On p65537-i0, window/hash0/hash1 each have rank30/32, yet either hash span plus the window reaches32/32. Equal ranks therefore concealed different identified functionals.

#pagebreak()
== Natural target certificates with deficient base rank
There are 13curve/schedule/target recovery records while base uncertainty remains, involving 8distinct fixed targets. They reuse eight public targets per curve; repeated schedules are not new independent target samples. All occur at prefix64 in the relation-only scope. Anchor-augmented results agree at this prefix. The single-natural-row and joint-system recovered target sets agree for these records.

#table(columns:(auto,auto,auto,auto,auto,auto),inset:4pt,
[fixture],[schedule],[target index],[recovered scalar],[rank/U],[bounded matches],
[p65537-i0],[hash0],[0],[19028],[30/32],[0],
[p65537-i0],[hash0],[2],[37811],[30/32],[1],
[p65537-i0],[hash0],[5],[43472],[30/32],[0],
[p65537-i0],[hash1],[0],[19028],[30/32],[0],
[p65537-i0],[hash1],[5],[43472],[30/32],[0],
[p65537-i0],[hash1],[7],[26799],[30/32],[0],
[p65537-i1],[hash0],[1],[50706],[28/31],[0],
[p65537-i1],[hash0],[2],[17359],[28/31],[0],
[p65537-i1],[hash0],[4],[3594],[28/31],[0],
[p65537-i1],[hash0],[6],[64966],[28/31],[0],
[p65537-i1],[hash1],[2],[17359],[30/31],[0],
[p65537-i1],[hash1],[4],[3594],[30/31],[0],
[p65537-i1],[hash1],[6],[64966],[30/31],[1],
)
Each recovery carries vN=0 and original-row weight/RHS certificates, plus an independently checked public [scalar]P=Q equation. These scalars are outputs, never supplied as source or target labels. Target points and original A4 projection were copied with parent hashes before this source-control run; none were redrawn based on yield.

Of these 13records, 11have no match in the registered [t]Q diagnostic, t=1..64, against signed original and scheduled public source points. Two records have bounded matches; all have no direct signed-source equality. These diagnostics explain only the tested finite coincidences. A bounded nonmatch does not exclude all alternative target-recovery constructions or establish novelty.

New source/base coincidences remain explicit affine anchor equations in the original U columns. Five anchor witnesses were retained across all16schedules: three reproduce already known A4 atoms, and two add one public anchor dimension each on p8191-i0/hash0 and hash1. Both extra dimensions are already in their full64relation spans, so their final marginal anchor gains are zero. Prefix0/16anchor effects remain in the complete records.

Target columns are cancelled before scoring added base information: Delta=rank([[M,0],[B,Utarget]])-rank(Utarget)-rank(M). All target-row cancellation vectors carry weights and are checked against the dense oracle. At prefix64, the original-window p65537-i0 gains one base dimension from target cancellation; all hash arms have Delta0. Identifying target functionals does not require increasing base-only rank.

== Fixed controls and selection boundary
SHA256 schedules use seeds0/1/2,64distinct nonzero scalars percurve, with exact within-schedule duplicate rejection only. Signed duplicates, overlap with1..64, base/target coincidences and every miss remain. Native atom order, curve, generator, old public-anchor offsets and32targets are fixed. All64schedule source points are public even at prefix0, with charged construction. These four fixtures and targets were already observed in A4: this is a conditioned source-selection control, not a new blind holdout or an estimate of a population recovery rate.

#pagebreak()
== Work, verification and custody
One physical supervised process built4928signed pair entries in four tables and ran49152source queries plus1536shared target queries. All16source schedules were actually queried, including overlaps. There are591source witnesses,5explicit anchor witnesses and15shared target witnesses. Each table and target stream is charged once;96scope analyses retain disjoint projection, elimination, kernel, cancellation, union-rank and certificate phases. Larger hashed scalars have different construction costs; native source construction is one aggregate phase across arms. Query count is not a complete per-arm cost denominator.

The separate arithmetic oracle enumerated88320signed triples once over the four curves, mapping sums to every source/target. It checks every pair, query bucket, accepted/missed row, source recipe, explicit anchor, full affine rank/kernel, target-column cancellation, carried certificate and public recovery equation. Separate checker diagnostic timings are retained. This is independent implementation verification, not staffed scientific review or an independent primitive-counter audit.

Fp/Fr/group/logical counters overlap and remain a vector. Hash/serialization/storage/OS work and verifier internals lack a complete weighted model. Diagnostic wall 8.185s, userCPU 6.225s, systemCPU 1.375s, RSS 66674688bytes; wall_valid=false. Exit0, no timeout/exception, source unchanged. One existing workstation process/thread,2GiB/21600sCPU/wall protective watchdog; no new cloud submission. Missing partial work would be labelled unknown, never zero.

Scientific source #raw("5a68708415810cbac2bd9fa8aeb4accbcc73ad1a"). Frozen selected protocol version2 SHA256 #raw("b3c56e6057629ca9bb712fcc3560c0d2c852dc4e0113f15f277bc17d79fbb0ac"); 24bound dependency paths plus one copied input file. Administrative assessment, exact Git publication, prospective freeze, actual canonical S3checkpoint, root release and ownership preceded native collection. Unused version1 remains immutable: its export metadata mismatch was repaired before any native data.

Raw data were committed/pushed in2bdc2ce44d before this report. Ten raw snapshots/journals were losslessly gzip encoded, with original/archive hashes;12raw objects are officially stored and remote-verified in S3. The fresh v8database adds16schedules,591relation and5anchor witnesses,32targets,15target witnesses and96certificate records while preserving v7historical scientific tables and parent bytes. It reuses the same six historical curves/bases; this study adds one physical execution, not new curves.

- p8191-i0: p=8191, a=2, b=5009, r=8311. EC1 urn:ec-record:1:sha256:7c8a9fb8f80a71415703dd59235c80eacfd6a065a1d147e0fa749a5ed8f0914f.
- p8191-i1: p=8191, a=2, b=7229, r=8263. EC1 urn:ec-record:1:sha256:b698b3bed4d1e363a59ae9ae43264937945685b1165af5afded5b2207d4bd377.
- p65537-i0: p=65537, a=2, b=20845, r=65713. EC1 urn:ec-record:1:sha256:c1432a839801e1340ffcbe3f0009aeab187a4b3ab05737b91d8a1c58a826a479.
- p65537-i1: p=65537, a=2, b=55325, r=65539. EC1 urn:ec-record:1:sha256:3f84dd2ddd39802326329fd9bc0ed2f01aa8ec26e3d9d8679fcbed39c92ad077.

Sources: A4RESULTS.md, design.md and literature.md; PKM2016sections3.1–3.4 (https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf), primary pages7–9 reread. Software:38tests pass, including complete96row metadata export and corruptions. Full-ledger validation refused sparse off-disk records; no passing full-ledger or verified configured-model claim.

Next technical step: freeze new curve and target holdouts comparing these source schedules, retaining original columns and explicit anchors, with separate per-arm source-construction costs. No canonical scientific status changes; the scoped graph here supplements historical reports without rewriting them.
