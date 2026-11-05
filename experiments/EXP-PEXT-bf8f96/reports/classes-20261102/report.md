# Actual curve classes with explicit isomorphism witnesses

2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d

The prospective component now enumerates complete pointed K-isomorphism classes through normalized model families, retains actual twist classes and emits explicit model-isomorphism witnesses. A separate polynomial-basis checker reconstructs the normalized universe and every orbit, checking canonical representatives and complete coverage. The same experiment remains review_required and unapproved; no cover/genus census ran.

## Full isomorphism group and witness orientation

For source E:y^2=x^3+a2*x^2+a4*x+a6 and target E', the witness (u,r), u!=0, means x_source=u^2*x_target+r and y_source=u^3*y_target. Accordingly,

`a2'=(a2+3r)/u^2; a4'=(a4+2a2r+3r^2)/u^4; a6'=f_source(r)/u^6`.

The forward point map is ((x-r)/u^2,y/u^3). Composition of successive witnesses (u,r),(v,s) is (uv,r+u^2*s), and inverse is (u^-1,-r/u^2). The checker replays the coefficient transformation with separate polynomial-basis arithmetic; the software tests independently expand f_source(u^2*X+r)=u^6*f_target(X).

This is the full origin-preserving isomorphism family for the specified odd-characteristic Weierstrass models. Pole orders at O give x_source=c*x_target+r and y_source=v*y_target+s*x_target+t. Comparing leading terms gives v^2=c^3, hence u=v/c with u^2=c,u^3=v. Comparing the absent y_target-linear terms forces s=t=0. Origin and actual model identity are retained throughout; matching j is insufficient.

## Complete disjoint normalized families

For p>3, translate with r=-a2/3,u=1 to short form a2'=0. Between short models the equation a2'=3r/u^2=0 forces r=0. Thus scaling by (u^-4,u^-6) gives every intersection with the short family.

In characteristic3, if a2!=0, translate with r=-a4/(2a2),u=1 into family A=(a2,0,a6). Nonsingularity requires a6!=0. Any isomorphism between these normalized A models has r=0, leaving (a2,a6)->(a2/u^2,a6/u^6).

If a2=0, nonsingularity requires a4!=0 and every a6 is allowed. This is family B=(0,a4,a6), with all translations retained: (a4,a6)->(a4/u^4,(r^3+a4*r+a6)/u^6). Since a2'=a2/u^2 in characteristic3, A and B are disjoint and no class crosses between them. Every nonsingular long model normalizes into exactly one family type; full residual orbits therefore give complete pointed K-isomorphism classes.

Special automorphisms and twists are handled by actual orbit membership, not a universal two-classes-per-j rule. The fixed F3 control has8 classes, including4 distinct j=0 classes; F5 has12. These are software fixture expectations checked by the test suite.

## Implementation and independent replay

The core exposes transform_model, normalize_model, curve_model_domain_size and bounded visit_curve_classes, with ModelWitness and CurveClass outputs. Each emitted orbit lists every distinct normalized member and a representative-to-member witness. Candidate iteration uses A-before-B order in characteristic3 and the frozen field encoding. A callback error propagates immediately; the domain ceiling is checked before coverage allocation.

The separate checker verifies the external expected field, nonsingularity, complete normalized family universe, every full residual orbit, canonical representative order, exact witness transformations and absence of overlap or missing classes. It uses the existing independent polynomial-basis arithmetic, and tests verify witnesses by literal cubic expansion. It does not need rational point counts to verify these model identities.

Candidate_models counts all family candidate slots, including singulars: Q^2 for p>3, and2Q^2-Q in characteristic3. Normalized_models counts the covered nonsingular members. Class_count counts their orbits. These three quantities are distinct.

Static review found no blocking source correctness issue within this model-class interface. The actual source-bound software-tests.txt records compiler/interpreter versions, commands, source hashes and warnings:6Rust groups,6quotientPython methods,5structurePython methods and5classPython methods pass, zero failures. Class controls cover complete F3/F5/F9 fixed certificates, normalization of every nonsingular long model in those small fields, full affine-action partition at F3/F5, witness polynomial identities, a distinct F5 quadratic-twist pair,10 mutation variants, limits and CLI binding. These are fixed software checks, not the planned cover/genus census or independent scientific review.

## Historical488 convention and input custody

The original committed D-n5-q3-cosets.jsonl is SHA2568f03e3d1a28a989108a038cfffab51e0362d2397dd03e06fc0ccfe442d9123fa. Its archived totals record classes488/isogeny_classes45; a separate derived_checks record gives models_checked488. The original exhaustive source calls classes(&f) and emits every representative as role=class. The proposal's0of488 therefore refers to the full nonsingular K-isomorphism cohort, retaining twists and exceptional models, not split-only or j-only objects. The root also counted488 archived role=class rows, agreeing with the recorded totals and models_checked. This is an identification of existing fixture semantics, not a fresh target census. No old genus outputs are used to select new inputs.

The reduced-family enumerator orders A before B, whereas original classes loops a2=0 first. Ordinal class labels must not be joined directly. The new full488 model bijection has not been materialized; it must align exact field/model identities and provide correctly oriented isomorphism witnesses. Preserve the historical fixture and its hash.

Deterministic cohort construction is prospective input preparation only when its generation rule and scope are fixed before outputs, without genus-based selection. Publish the complete identities/witnesses/coverage manifest as inputs; it supplies no genus/descent result and does not authorize the scientific launcher.

## Remaining interface and next step

The current checker still accepts whole JSON with the inherited16MiB input cap and a1,000,000-candidate model ceiling. That ceiling excludes the original n3/q11 field Q=1331, whose short candidate domain is1,771,561. Extend the verifier to streaming partitions with exact coverage and input-binding receipts; do not shrink the cohort to fit the fixture interface.

Next materialize and independently reconcile the full actual-curve/twist input manifests, including the historical488 bijection, then join all rational T classes and projective structures with scalar-preserving transformations and exact cross-shard coverage. Frobenius-lift/descent, Type2 predicates, original geometric P3/descriptive q13 H1 analysis, exports/checkpoints and frozen launch bindings remain required. No scientific status or original protocol byte changes in this component.

## Sources and report custody

Family/action proofs above derive from the displayed Weierstrass identity and inspected classes/classes_fam source. Existing primary cover/descent references remain Iijima-Momose-Chao2015/805 sections3.1-3.3 (https://eprint.iacr.org/2015/805.pdf) and Chao ECC2007 slides25-26 (https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), source-reviewed in original notes. No novelty finding is asserted. Canonical lead-graph scientific edges are unchanged because no full-cohort genus/descent evidence was produced.

Fresh archive TASK-20261102-fce0e3 preserves this component, software log, report and additive problem progress; prior report snapshots and their native receipts remain intact.
