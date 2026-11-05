#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Sparse functional evaluation in both solver representations
Run #raw("a9-json-control-4e271c"): 288 immutable paired input systems, four cold modes, 1152solvercalls in one scientific process, 0unknowns. Four previously observed curves/bases,32fixedpublictargets,4schedules,9budgets,2scopes. This is the explicit JSON-key correctness repair after a retained failed attempt, with no collection or independent curve/target draw. Allfour modes match target outcomes/scalars, full kernels and original-row certificates; dense modes exactly replay the two A8arms and all their recorded Frphasevectors. Identified target slots per mode: 486, summed over dependent systems, not independent target draws.
#image("primitive-counts.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto),inset:4pt,[logical unit],[dense joint],[dense cancel],[sparse joint],[sparse cancel],
[Fr.field_add],[1097774],[322672],[169246],[114394],
[Fr.field_sub],[537790],[506680],[537790],[506680],
[Fr.field_mul],[1616582],[813356],[688054],[605078],
[Fr.field_inv],[5508],[4428],[5508],[4428],)
Complete method totals include construction/cancellation, elimination, full kernel, identification, original-row lifting/verification and public checks. Shared projection is separate and counted once/case. Historic collection is referenced, not rerun or called free. Fradd/sub/mul/inv are distinct logical primitive calls; inverse internals, Python traversal/allocation/IO and verifier internals are not expanded. No unit weights, runtime or end-to-end advantage are inferred. These are implementation controls on fixed observed inputs; the campaign still requires fresh holdouts and complete cost accounting.

Dense identification evaluates every coefficient of vN, including zero products. Sparse builds the canonical nonzero coefficient support. Exactly one coefficient equalto1 reads the corresponding kernel coordinate; all other supports use the same Fradd/Frmul dot product over support only, including zero kernel entries. Negative/non-unit coefficients do not take the unit shortcut. Zero support yields zero syndromes without dot arithmetic. This identical rule is applied to BOTH representations. Row reduction and certificate construction remain unchanged. Kernels are fully built and retained; this does not test a kernel-free recovery algorithm.

#pagebreak()
== Controlled phase and traversal accounting
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[mode],[phase],[Fradd],[Frsub],[Frmul],[Frinv],
[dense_joint],[certificate_lifting],[0],[0],[0],[0],
[dense_joint],[elimination],[0],[451750],[508756],[5508],
[dense_joint],[identification],[928528],[35934],[938580],[0],
[dense_joint],[kernel],[136564],[50106],[136564],[0],
[dense_cancel],[certificate_lifting],[78],[564],[0],[0],
[dense_cancel],[elimination],[0],[386492],[428154],[4428],
[dense_cancel],[identification],[232282],[87082],[294890],[0],
[dense_cancel],[kernel],[57630],[18718],[57630],[0],
[sparse_joint],[certificate_lifting],[0],[0],[0],[0],
[sparse_joint],[elimination],[0],[451750],[508756],[5508],
[sparse_joint],[identification],[0],[35934],[10052],[0],
[sparse_joint],[kernel],[136564],[50106],[136564],[0],
[sparse_cancel],[certificate_lifting],[78],[564],[0],[0],
[sparse_cancel],[elimination],[0],[386492],[428154],[4428],
[sparse_cancel],[identification],[24004],[87082],[86612],[0],
[sparse_cancel],[kernel],[57630],[18718],[57630],[0],)
#table(columns:(auto,auto,auto,auto,auto),inset:3pt,[mode],[coefficients scanned],[support entries],[support visits],[coordinate reads],
[dense_joint],[unmeasured],[unmeasured],[unmeasured],[unmeasured],
[dense_cancel],[unmeasured],[unmeasured],[unmeasured],[unmeasured],
[sparse_joint],[72000],[2304],[0],[27936],
[sparse_cancel],[25704],[3024],[24004],[0],)
Logical traversal counters are instrumented only for sparse modes. Dense traversal is UNMEASURED, not zero; no comparison of total CPU/memory work is supplied by these counters. Support construction, direct coordinate reads and dot products remain distinct operations. Dense algebra/certificate outputs and phasevectors must exactly match archived A8; sparse may change only identification add/mul/logical calls, not other phasevectors. Original lifted coefficients/RHS and public[k]P=Q are checked in every mode. Missing target groups remain unidentifiable.

#image("budget-counts.svg",width:100%)
Counts sum sixteen fixed curve/schedule combinations at each budget/scope; prefixes and target points are reused. All budgets/modes retained regardless of cost or success. Charts are exact sums of recorded counters, not significance estimates or new independent observations.

#pagebreak()
== Failed-attempt costs and remaining campaign requirements
The prior frozen A9attempt exited1 after four producer outputs, with zero accepted cases. Its integer-key versus archivedJSON-string comparison failed; the repair canonicalizes only representative map keys and has an actualJSONroundtrip regression. The old protocol/run/source remainimmutable. The new contract authorizes one explicit corrective pass, records2physicalattempts and1156observedproducer calls ifcomplete, and enforces original2026-11-06T04:14:15.825283Z deadline minus priorCPU/wall allowance. No blindautomaticretry, hiddenprefix or newcapacity.
#table(columns:(auto,auto,auto,auto,auto),inset:3pt,[cumulative logical unit],[dense joint],[dense cancel],[sparse joint],[sparse cancel],
[Fr.field_add],[1101614],[323347],[169406],[114514],
[Fr.field_sub],[537850],[506680],[537850],[506680],
[Fr.field_mul],[1620439],[814031],[688231],[605198],
[Fr.field_inv],[5511],[4428],[5511],[4428],)
These cumulative vectors charge the old four observed/unverified output costs plus the successfulpanel. Oldprojection is charged separately once, and oldinclusive processCPU/wall retain failedchecker/IO/startup overhead. No inclusiveclock/phase doublecounting or inventedFrweights. The firstpage table reports the cleanpanel only; neither the oldfailedacceptance nor overhead is erased.

== Provenance
Scientific source #raw("d8c25fa8cf20dc94ed627e1742a57ca401dd569f"); protocol #raw("c07abf57a49fb5779c13f6f4e830d4fba72313ac6f39bea60e4b0eb45389cc52"). Published exact source/inputs and frozen prospective protocol, actual canonical S3checkpoint, explicit root release and owner lease preceded native mathematics. Exit0, timeoutFalse, source unchangedTrue. Diagnostic wall24.655s, userCPU22.915s, systemCPU1.341s, RSS112435200B; wall_valid=false. One existing workstation scientific process/thread,2GiB21600sCPU/wall,1attempt/noautomaticretry; no new paid capacity.

Independent plain projection/dense-affine rank/consistency/full-kernel spans/unit-row identifiability checks, original-row coefficient/RHS and independent public multiplication validate every mode. Dense A8cost/control and sparse semantic/certificate/unchanged-phase controls are mandatory. Tiny controls include unit/nonunit/negative/zero supports, absent/empty/width-zero cases, deterministic A/A, corruption/refusal and immediate completed-arm/failed-phase retention. Export identities/seeds/files bind all1152rows. No staffed scientific review/model-provider verification or full sparse-ledger pass is claimed.

Raw records were committed/pushed before this report. Lossless gzip hashes and official S3manifests bind all snapshots/journals. v12appends the retained failed attempt and this completed factorial study/1152solver-certificate records to untouched v11history; no old data is rewritten. The pipeline/protocol/export/benchrecord/report/database/progress artifacts preserve finite observations, not campaign completion. Fresh curves/targets with all construction/collection/elimination/extraction/lifting/verification costs remain necessary before claiming an improvement over the strongest baseline.

Sources: A8RESULTS.md and archived dense controls; A4CertifiedSystem.identify; design.md/literature.md. PrimaryPKM2016p8section3.2 reread (SHAa53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b) separates relation and linear-algebra costs without calibrating these Frcalls. Canonical research-kb skill read viaGitHub crypto commit bc10008055; MCP unavailable and wrapperstatus127/noexecutable. Explicit direct-source/rg fallback used; no KBsourceIDs, absence or novelty claim. All generated graphs describe retained counters only.
