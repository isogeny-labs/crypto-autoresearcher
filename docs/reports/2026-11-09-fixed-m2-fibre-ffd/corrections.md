# Additive corrections to the November 9 proof-route notes

The earlier Git/S3 bundles remain immutable. This note corrects two statements without changing the higher-degree bounds established in the continuation.

## Incorrect diagonal witness

Affected: ../2026-11-09-fixed-m2-lfd-unbounded/algebraic-route.md, Lemma A last paragraph, and ../2026-11-09-fixed-m2-lfd-unbounded/report.md, result A last paragraph. The proposed witness X=Y=a6^(1/4) omitted the term zX^2:

    S3(X,X,z)=X^4+zX^2+a6.

It is not generally a zero. For z,a6 in the subfield H and z nonzero, the correct witness is

    X=0, Y=sqrt(a6)/z,
    S3(0,Y,z)=z^2Y^2+a6=0.

The SAT conclusion therefore stands. The original independent definition audit and the later SAT audit already use this valid witness. The outside-target decomposition, its UNSAT degree-3 refutation, its SAT extension, and the arbitrary-V k+3 upper bound do not use the erroneous diagonal witness.

## Low-degree row-span invariance qualification

Affected: the unchanged-field-embedding discussion in the first round's certificate-route.md and algebraic-route.md. An invertible row recombination of quadratic-or-lower inputs preserves the saturated closures W_D for D>=2, when all old and new inputs are eligible. It need not preserve W_0 or W_1: a recombination can expose an affine equation as an input. Thus exact small FFD/LFD values need not be invariant under arbitrary changes of equation presentation.

The finite degree-5 example cannot be amplified by unchanged field extension: its degree-4 non-refutation and degree-5 refutation are both in the invariant D>=2 range. More generally, late fall behavior above2 is unchanged. The earlier blanket phrase "every W_D" was too broad. The explicit F16 example in ffd-qualified-statement.md supplies a same-Semaev-system witness of this issue.

These corrections preserve the strict source-degree closure definition. No earlier artifact or measurement was silently replaced, and no new solver execution was performed.
