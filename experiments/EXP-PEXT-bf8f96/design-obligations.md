# EXP-PEXT-bf8f96: prospective design obligations

Status: review_required, unapproved, zero scientific runs. Hypothesis H-PEXT-c3a11d; source IDEA-20261024-d84f20.

The design extends all named cohorts: n=3, q=5,7,11 and n=5,q=3 (the proposal's 488 cohort, whose exact class/twist convention must match the input manifest before freeze). Abstract n=7 placement enumeration is separate; no enlarged n=7 field census is substituted.

## Same-curve constructive component

For E: y²=x³+a2*x²+a4*x+a6 and nonzero rational T=(u,v), let t=(y+v)/(x-u). Removing the known root x=u of the line intersection gives

`x²+(a2+u-t²)x+(u²+a2*u+a4+u*t²+2*v*t)=0`.

With w=2*x+a2+u-t² the quotient quartic is

`w²=t⁴-2*(a2+3*u)*t²-8*v*t+(a2²-2*a2*u-3*u²-4*a4)`.

The inverse on its affine chart is x=(t²-a2-u+w)/2 and y=t*(x-u)-v. Use a6=v²-u³-a2*u²-a4*u. Root as producer reports SymPy 1.14.0 symbolic checks of residual factor, discriminant, inverse and removable-point equation PASS; the root-owned `implementation/degree2_identity.py` retains the replay. This is algebra/software verification, not an all-T census or independent mathematical review. The x=u chart, origin, T, -T, v=0 and infinity must be accounted for in the projective extension. Characteristic3 is allowed; dividing by3 is prohibited. T=O uses the original x map.

## Exact implementation work

1. Reuse finite-field and binary-quartic code from EXP-PEXT-212d5c and EXP-PEXT-0b2c75 only after source hashing. Generate complete K-isomorphism classes, retaining twists, special j and char3 a2; each identity collision needs explicit model isomorphism.
2. Compute E(K)/2E(K) with representative/coset certificates, not just a guessed two-torsion rank. Build the quartic above on the same actual E and certify branch action under P -> T-P.
3. Compute Frobenius conjugate branch polynomials and projective infinity incidence. Factor their product over K, weighting irreducible factors by degree for r; factor membership vectors suffice for F2 incidence rank m without constructing enormous K^4 fields. Prove the chosen representation implements the same full branch set.
4. Independently compute full K(t)*/K(t)*² relations, including constants. A relation with nonsquare constant changes connectedness/admissibility. Provide actual Frobenius-lift order-n certificate, or a proved applicable criterion, before labeling descent valid. A missing certificate is unknown, never true.
5. Exhaust structures through certified PGL2(K)/PGL2(Fq) representatives or an equivalent orbit enumeration with stabilizer accounting. Aggregate geometric and admissible minima separately on actual curve/twist/T identities. Type2 signature and trace-zero Mobius predicate are separate columns; emit matrix witness or exhaustive nonexistence certificate.
6. Freeze run/check/analyze scripts, inputs manifest, exact trial plan and all generated artifacts; include independent checker and report/export writer. A second implementation rechecks the prescribed subset and all counterexamples; it must not simply call producer helpers for load-bearing rank/descent checks.

## Primary source review and boundary

Retrieved 2026-11-02 through indexed full PDF: https://eprint.iacr.org/2015/805.pdf, sections3.1-3.3, in particular (12)-(18) and Example3.2. Its square-class and coefficient conditions make twist-aware admissibility necessary. Direct URL initially403 but indexed full content was accessible; this is no remaining access blocker.

Retrieved https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf, slides25-26. The Type2 polynomial uses exponents0,1,3,4 of a degree-six element; the next slide separates a hyperelliptic exception using a trace-zero GL2(Fq) transformation. The design records both tests and assumes no universal Type2/nonzero-T equivalence.

Neither source review proves the new all-map minima or novelty. The old abstract-only KN-LIT record stays immutable. This source-bound note upgrades only this design's citations.

## Readiness, lane, and archival path

Open PEXT lanes from the completed refs scan are BATCH-21339c and BATCH-a4886a, at cap2. Existing BATCH-68a56c is closed on its interface impediment. Drafting creates no third live lane. Coordinator may close a preserved failed lane only through an additive lifecycle act that retains both invalid-output receipts and the four unrun obligations/continuation; closure never marks the original experiment complete. Otherwise queue design execution until capacity is lawful.

No trial plan, executor handoff, queue, lawful reserved lane or exact Executor serving route is supplied. Protocol stays draft and specification review_required. `tools/experiment_preapproval.py --experiment EXP-PEXT-bf8f96` diagnoses the current draft; passing protocol schema is not preapproval. Freeze analysis and protocol only after the complete implementation and prospective packet pass. Root handles publication and archive under TASK-20261102-4673e7; nothing in this draft grants launch authority.


Scope clarification: P3 tests the original geometric genus minima. Descent-admissible minima are a separate descriptive output, never a strengthened P3 criterion. The original H1 configuration/curve-count ratio arm retains q=5,7,11,13, with q=13 separate from the P3 cohort. H1 equidistribution is not asserted or gated. Symbolic replay command: `/var/tmp/pext-design-report-venv/bin/python experiments/EXP-PEXT-bf8f96/implementation/degree2_identity.py`; four checks PASS, recorded in symbolic-check.json. The root is the producer; this is no independent scientific review.
