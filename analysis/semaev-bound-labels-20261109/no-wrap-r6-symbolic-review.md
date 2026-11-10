# Independent review: symbolic r=6 obstruction and infinite restriction family

Date: 2026-11-09. Mathematical source review of `no-wrap-r6-symbolic-obstruction.md`. Separate existing-certificate replay is recorded in `no-wrap-r6-independent-replay.json`; no new campaign was run by this reviewer.

**The symbolic obstruction and its extension are correct: LFD(F_r)>=3 for every r>=6 in the no-wrap regime n>4r. The r=6 bracket 3<=LFD(F_6)<=4 is also justified.**

The dyadic coefficient relations eliminate four coordinates at r=6, including the constant relation. Summing the reduced coefficients gives q(1)=0 and a fifth independent affine elimination. The remaining nine independent coordinates are x_0,...,x_6,b,c, with q=b(T+T³)+c(T²+T³).

The two displayed h polynomials are correct. Their sum T+T⁴ factors as T(T+1)(T²+T+1) with three pairwise coprime squarefree factors. Both h polynomials vanish at zero and one; reducing h1 modulo T²+T+1 gives one. Hence gcd(h1,h2)=T(T+1), so their lcm has degree ten. Each h_i P_6 has dimension seven; their intersection is exactly the degree-at-most-twelve multiples of that lcm and has dimension three. The quadratic-top coefficient span therefore has dimension eleven and is the entire polynomial subspace vanishing at zero and one.

On the twelve positive coefficient rows, the only functional annihilating their quadratic tops is their total sum. It gives E(1)=0 identically after eliminating q(1). Thus the reduced row span has dimension eleven and contains no nonzero affine polynomial. Under the strict cap-two multiplication convention it is already saturated: no eligible nonzero affine source is available to multiply. In particular x_1 is missing.

The ideal of the five eliminated affine relations contributes a degree-two kernel of dimension 106-46=60. All of that kernel is derivable at cap two using affine relations times affine cofactors. The reduced row span contributes eleven more independent directions, yielding original rank71, codimension35, and exactly five affine directions. This symbolic calculation establishes full closure, not merely an initial matrix rank, and agrees with the independently replayed certificate.

For any r>=6, setting higher x and y coefficients to zero gives exactly the r=6 coefficient system, with extra zero output rows. Every eligible quadratic input maps to a quadratic input combination at the same cap; affine restriction preserves strict cap-two derivations. The coefficient x_1 is a known vanisher for every larger member by the exact two-point theorem and maps to the missing r=6 x_1. Therefore it cannot be derived at cap two in any larger member. No indicator-degree cost is required, because this is direct nonmembership transport of a polynomial independently known to remain in the larger ideal.

For the upper bound at r=6, fix the two remaining q bits. Each restricted input system is affine in x. Three branches are inconsistent; the zero-q branch has precisely the affine line of constant x. Derivations of their affine ideals lift through degree-two branch selectors at cap four, retaining the original quadratic eligibility threshold. Summing the nonzero branch contradictions derives the q bits; combining branch consequences derives every positive x coefficient. The five original affine eliminations already belong to W2, so they add no further cap. This proves the conservative upper bound four, without deciding whether W3 suffices.

This is an explicit infinite constant-lower-bound family, distinct from the half-dimensional diagonal. It does not show growth above three as r increases.
