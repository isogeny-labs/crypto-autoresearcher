#set page(paper: "a4", margin: 15mm)
#set text(size: 9pt)
= Exact quotient-coordinate and scalar transport
2026-11-03 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d | TASK-20261103-69adf4

The new algebraic component constructs a normalized Mobius matrix A and nonzero weighted-ordinate scale kappa for supplied rational T,Q on the same nonsingular odd-characteristic curve. The destination is T'=T+2Q. Five source-bound software methods pass. This completes the explicit coordinate/scalar witness component; the scientific contract remains review_required and unapproved.

#image("transport-flow.svg", width: 100%)

#table(columns: (2fr,2fr,1fr), inset: 4pt,
 [*Software scope*],[*Coverage*],[*Pairs*],
 [F3],[All 8 classes; every T,Q],[156],
 [F5],[All 12 classes; every T,Q],[500],
 [F9 A / twist / B],[Every T,Q on each control],[144 / 225 / 256],
 [F27 / F125],[One fixed model each; selected],[12 / 9])

*Exact identities:* with t=t_T(P), w=w_T(P), t'=t_T'(P+Q), w'=w_T'(P+Q), and A=(a,b;c,d), verify t'(ct+d)=at+b; w'(ct+d)^2=kappa*w; and F_T'(aX+bZ,cX+dZ)=kappa^2*F_T(X,Z). The baseline T=O retains the homogeneous cubic/infinity branch. Finite T uses t=(y+v)/(x-u), w=2x+a2+u-t^2. Characteristic 3 is included without division by 3.

*Construction:* reduce rational functions in K(x)[y]/(y^2-f(x)), clear denominators and solve the unique projective kernel of [-t,-1,t*t',t']. Normalize A by its first nonzero coefficient and require det(A) and kappa nonzero. Verify both rational identities by cross multiplication and every literal binary-form coefficient. External expected field/model/T/Q binding is exact. Synthesis and verification share the rational engine and field/form helpers; this is software replay with separate Coordinator static inspection, not independent arithmetic reimplementation.

*Controls:* all small-field class/pair cases; three complete characteristic-3 extension/twist controls; selected larger inputs;216F3 composition triples;3F27 cocycle matrices;11certificate mutations; external-input and CLI controls. If A2*A1=s*A12, composition requires kappa12=kappa1*kappa2/s^2. Software-tests.txt records all10source/dependency hashes, commands, Python3.11.17, rustc1.99.1, retained unused-import warnings and ALL_TRANSPORT_SOFTWARE_CHECKS_PASS. Static inspection found no defect in the inspected formula, normalization, transform and binding paths.

*Reindexing:* T'=T+2Q requires HN -> HN A^-1 and C(N A^-1)=A C(N) sigma(A)^-1. Three F27 controls check the projective cocycle formula. A full ordinal permutation and integration of all normalized reindexed form scalars into the streaming join remain a next interface.

*Sources and scope:* internal design-obligations.md and prior join report were inspected. Chao ECC2007 slides25-26 were retrieved on2026-11-03 and keep Type2 and hyperellipticity predicates separate; this component computes neither. Direct ePrint2015/805 retrieval returned403; earlier source-reading provenance is retained in the design notes. No novelty conclusion uses that failed retrieval.

*Next:* integrate published full-cohort/plan identities, transport scales, streaming shard custody and checkpoints. Preserve q3/n5(488), q5/n3(252), q7/n3(690), q11/n3(2662), descriptive q13/n3(4400), original controls, abstract n3/5/7placements, geometric P3 and separate H1 arms. Connectedness/genus, Frobenius descent/Type2 and scientific analysis/export remain. Preapproval is still approvable:false, with implementation/runbook/route, lane, trial plan, queue and published/frozen source/approval bindings missing. No approval, freeze or scientific trial follows from these checks.

Full derivation and limitations: report.md. The12-path handoff requires parent PDF inspection, deduplicated manifest, native content-at-commit archive and remote publication. Historical reports and scientific graphs/status stay immutable; the new diagram records component progress only.
