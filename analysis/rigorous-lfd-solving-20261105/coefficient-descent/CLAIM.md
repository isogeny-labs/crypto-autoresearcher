# Raw binary two-S3 theorem for independent review

5 November 2026. Read this statement and independently rederive its degree
accounting before opening BinaryCoefficientDescent.lean or its attempt logs.

Let K be a field of characteristic2, ell>=1. In independent Boolean bits,
x,y,z are K-valued linear forms using respective base supports Sx,Sy,Sz of
size<=ell. Let u,v be arbitrary finite K-valued linear forms in auxiliary
bits, with no restriction on their number (v may be omitted). Fix r,a6 in K.
The source equations are

    S3(x,y,u), S3(u,z,r), optional v*(x+y)+1,
    S3(A,B,C)=(A*B+A*C+B*C)^2+A*B*C+a6.

For each selected equation, apply any finite family of additive coefficient
maps K -> F2 to obtain its actual raw coefficient polynomials. Each map acts
on polynomial coefficients and leaves monomial exponents unchanged; it is
NOT assumed multiplicative or unital. A basis-coordinate map is a particular
allowed map. Include all explicit bit equations. The assertion is:

    Boolean UNSAT implies ordinary lastFallDegree(F)<=3ell+1.

There are no assumed localized rows, low-degree refutations, finite last
fall degree, or normalized-support hypotheses in the final statement. The
final source theorem is intended to derive all of these from the displayed
raw equation shapes. Both linear base and auxiliary maps have zero constant
term. It does not require rational lifts, nonsingularity or an algebraic
field degree n for this syntactic result; those restrictions are allowable
specializations for curve relation semantics.

The formal selector 'which' chooses first S3, second S3 or guard per output
row, with arbitrary row-indexed additive projections. The second raw S3 is
written as S3(z,r,u), a cyclically equal polynomial; that identity must be
proved. Over finite K=F_(2^n), actual basis coordinate maps and full n-bit
u/v embeddings give the intended production presentation.

A separate reviewed generic core, BinaryLocalization.lean, supplies a
support-aware F2 bound from supported-affine normal forms. This new review
owns the raw shape, coefficient projection, normalization, support/cap
instantiation, and final theorem fidelity. The full workspace verifier is
resource-blocked by an old degree-three rank certificate (exit137, observed
cgroupOOM), so perform scoped source and axiom/kernel checks and state scope.
No scientific state or signed PCC status is asserted.
