# A control separating top-part regularity from solving work

Root derivation, 2026-11-01. UNREVIEWED, UNEXECUTED. This is a proposed metric control for the full chart comparison, not a replacement for its complete k=0..5 cohort or a measured solver improvement.

Metric source. Caminata and Gorla, Solving degree, last fall degree, and related invariants, arXiv:2112.05579v2, Definition 1.4, define degree of regularity from when the ideal of highest homogeneous parts fills an entire graded component. Their Definition 1.1 defines solving degree using the Macaulay computation; these are distinct quantities. Source read on 2026-11-01: https://arxiv.org/pdf/2112.05579 . The construction and counts below are our derivation, not a claim attributed to that paper.

Public premises. Let p>3 be prime, E:y^2=x^3+alpha*x+beta nonsingular, and T=(a,b) a rational affine target. Put Z=X-a, so f(Z+a)=Z^3+c2*Z^2+c1*Z+b^2, with c2=3a and c1=3a^2+alpha. This is a polynomial-basis translation, not an assertion that the current short-Weierstrass source API accepts a nonzero quadratic curve coefficient. Use the k=2 finite-target chart A=A1*Z+A0, B=1, and U=Z^2+u1*Z+u0. Its norm is f(Z+a)-A^2=Z*U, and its target-sign equation is L=A0-b.

Retained equations before substitution:

    E2 = c2-A1^2-u1
    E1 = c1-2*A1*A0-u0
    E0 = b^2-A0^2
    L  = A0-b

Add the four explicit field equations v^p-v for v=A0,A1,u0,u1. No interval-membership equations are included in this diagnostic. The ideal of highest homogeneous parts is exactly (A0,A1^2,u0^p,u1^p). Indeed L kills A0, making E0 and the leading part of E1 redundant; A1^p is redundant modulo A1^2. The quotient's nonzero monomials have A1 exponent at most1 and u0,u1 exponents at most p-1. Its largest nonzero degree is 2p-1, so this definition gives dreg=2p.

After substituting A0=b, omit the zero equation E0 and L. E2 remains quadratic, but E1 becomes c1-2b*A1-u0, a linear equation (also when b=0). Retain all three remaining field equations. The new top-part ideal is (A1^2,u0+2b*A1,u1^p); the equation u0^p is redundant after the linear substitution. Its largest nonzero quotient degree is p, giving dreg=p+1. This is an exact formal count under the specified field-equation representation. It has not been computer-checked or independently reviewed.

The source and reduced solutions correspond bijectively by A0=b. The redundant equation satisfies E0=-(A0+b)*L. Thus the observed change in this invariant is caused by exposing a lower-degree consequence through linear substitution. It does not establish a change in solving degree: an elimination solver can itself derive the same linear E1 consequence. No timing, matrix-rank computation, complete SAT model comparison or degree-of-regularity value for the full interval-constrained system is asserted.

Use as a control. A future metric implementation should recover the two displayed Hilbert staircases, then measure solving degree, matrix size and charged output recovery separately. Include b=0 and b!=0. Adding interval or rationality equations changes the top-part ideal and requires a fresh derivation; do not carry 2p or p+1 into the complete chart by assumption. The original 24-group correction suite and its frozen source remain unchanged.
