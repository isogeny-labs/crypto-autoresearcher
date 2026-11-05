#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Cancellation-first and full-joint target recovery
Run #raw("a8-cold-solvers-7f32b1"), 288 paired supplied-row systems, 576 cold solver calls, one physical process. All four observed A7curves/bases, 32public targets, four source schedules, nine budgets and two scopes were retained. No relation collection or target generation was repeated. Unknown solver rows: 0. Both methods identify the same target slots and scalars in every checked case, with valid certificates over the original joint rows. The count summed over dependent systems is 486 identified target slots per arm; this is not 486 independent targets.
#image("primitive-counts.svg",width:100%)
#table(columns:(auto,auto,auto),inset:5pt,[logical unit],[full joint],[cancellation first],
[Fr.field_add],[1097774],[322672],
[Fr.field_sub],[537790],[506680],
[Fr.field_mul],[1616582],[813356],
[Fr.field_inv],[5508],[4428],)
These are direct measured logical primitive-call counts, including all solver construction, elimination, full-kernel, identification, lifting and original-row/public checks. Addition and subtraction are counted separately in the same new Frmeter for BOTH methods. Invocations of modular inversion are counted once; their internal arithmetic is not expanded. Do not combine different units with invented weights, compare these new split counters directly with old merged-add/sub counts, or infer wall-time, full-S or end-to-end advantage.

Both arms start cold from the same projected rows. Fulljoint eliminates [M,0;B,-E] at width U+8. Cancellation chooses first original row j(t) for each represented target and freshly constructs every same-target difference C_i=B_i-B_j at width U, using ALL target groups before representative recovery. It then eliminates [M;C], computes its full kernel, and tests representative vN=0. Targets with no row stay explicitly unidentifiable. Equal information does not require byte-identical kernels or equal representation ranks.

#pagebreak()
== Paid cancellation, lifting and checks
#table(columns:(auto,auto,auto,auto,auto,auto),inset:3pt,[arm],[phase],[Fradd],[Frsub],[Frmul],[Frinv],
[full_joint],[joint_matrix_construction],[0],[0],[0],[0],
[full_joint],[elimination],[0],[451750],[508756],[5508],
[full_joint],[kernel],[136564],[50106],[136564],[0],
[full_joint],[identification],[928528],[35934],[938580],[0],
[full_joint],[certificate_lifting],[0],[0],[0],[0],
[full_joint],[original_row_certificate_verification],[32682],[0],[32682],[0],
[full_joint],[public_target_verification],[0],[0],[0],[0],
[cancellation_first],[cancellation_construction],[0],[13824],[0],[0],
[cancellation_first],[elimination],[0],[386492],[428154],[4428],
[cancellation_first],[kernel],[57630],[18718],[57630],[0],
[cancellation_first],[identification],[232282],[87082],[294890],[0],
[cancellation_first],[certificate_lifting],[78],[564],[0],[0],
[cancellation_first],[original_row_certificate_verification],[32682],[0],[32682],[0],
[cancellation_first],[public_target_verification],[0],[0],[0],[0],)
If v_j=lambda M+mu C, lifted target-unit weights are lambda on original base rows and sum mu_i(e_i-e_j) minus e_j on original target rows. Their coefficient vector must equal [0,+e_t], and their weighted RHS must equal the recovered scalar. All coefficients, offsets and signs are checked independently, followed by public [k]P=Q checks. Original rows and their order are retained; no saved A7pivots, cancellation rows, scalar labels or kernels enter either solver. A7outcomes are read by the checker only after producer outputs are retained.

Shared projection is measured once per input system and excluded from both arm totals: #raw("{\"Fr.field_add\": 213296, \"Fr.field_mul\": 220048, \"Fr.field_sub\": 6752}"). Historical relation collection remains referenced in A7; it is neither replayed nor called free. The independent dense checker and Python/dictionary/serialization/OS work have diagnostic resources rather than a complete primitive model. Different certificates may have different density, so original-row verification remains in the comparison, not hidden behind elimination-only counts.

#image("budget-counts.svg",width:100%)
Counts sum the sixteen fixed curve/schedule combinations per budget and scope. Reused prefixes/targets are dependent observations; no population sample, significance test or p-value is inferred.

#pagebreak()
== Provenance, controls and limits
Scientific source #raw("a49d03dd5e19c402820484bc39e2373dd27e0589"), protocol #raw("c8b1bd1c7e6daadf691a1c79772654a380576491185b74226823cfe179c11074"). Exact source/input/parent publication, prospective freeze, administrative readiness, actual canonical S3checkpoint, explicit root release and ownership preceded execution. Exit0, timeoutFalse, source unchangedTrue. Diagnostic wall14.228s, CPUuser12.614s, CPUsys1.268s, peakRSS105558016B; wall_valid=false. Existing workstation1process/thread,2GiB21600sCPU/wall protective limits,1attempt/noautomaticretry, no paid capacity submitted.

The independent implementation checks plain projection, dense affine ranks/consistency, complete kernels and target-unit identifiability, exact difference/representative rules, lifted original coefficient/RHS certificates, independent public scalar multiplication and every A7joint target outcome. Component phase sums are checked; primitive internals are not independently audited. Tiny software controls exercise cancellation-required deficient recovery, absent/empty/width-zero targets, full kernels, deterministic A/A and corruption refusals. The unified 576row export carries exact instance/seed/file bindings. Full sparse-ledger validation is refused; no full pass or staffed scientific review/model-provider verification is asserted.

Raw records were committed and pushed before this report. Gzip files retain original hashes and lossless roundtrip receipts; official S3manifests preserve data custody. Database v11appends 288case records and576solver/certificate records to untouched v10history with no new curves or independent target draws. Report graphs use retained counts only. No previous raw, protocol, report or closed benchmark is rewritten.

Sources: A7RESULTS.md and four pinned gzip snapshots; design.md/literature.md; PKM2016 sections3.1–3.4, primary PDFpages7–9 reread2026-11-05 (SHAa53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b). That paper motivates separating relation and linear-algebra costs; it does not establish this implementation comparison. Exact finite costs and outcomes do not imply novelty, scalable rank laws or a weighted attack improvement. Future implementation choices require their own matched cost and correctness comparison.
