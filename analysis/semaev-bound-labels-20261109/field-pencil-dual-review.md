# Independent review: field-pencil dual obligation

Date: 2026-11-09. Source-only review of `field-pencil-dual-obligation.md`. No execution.

**The dual identities, conservative degree bounds, rank-drop calculation, and conditional minor theorem are correct.**

For fixed nonzero v, the unique-zero hypothesis makes v² lie outside the image of the binary linear map L_v on W. Trace-pairing separation therefore supplies lambda. The adjoint squaring identity Tr(a*w²)=Tr(a^(2^(n-1))*w) gives precisely the displayed field-specific equations. A polynomial separator on a coordinate-one slice gives an identity in its Boolean ring, because equality at every Boolean point is equivalent to equality of multilinear functions. Its degree-c coordinate multipliers can be applied to quadratic input rows at strict cap c+2. Lifting by the coordinate selector costs one more cap, including original quadratic eligibility. Once the v coordinates are derived, removing their quadratic products leaves u, so h<=c+3 is valid. Interpolation supplies c<=r-1 as stated.

Failure of this restricted multiplier form is not a refutation-degree lower bound: the report correctly requires a normalization theorem accounting for arbitrary u-dependent derivations and saturated feedback. No such normalization is assumed.

The full-field kernel for v nonzero and unequal to 1 is {0,(v+1)/v²}. After scaling u by that nonzero root, the equation becomes t²+t=1/kappa². Its trace condition simplifies to Tr(1/(v+1))=1 under Tr(v)=0 and odd n. It does not establish that a root belongs to W, so the stated limitation is essential.

If all minors are genuinely in W2(H), their double restrictions remain available at cap two. On u_i=1,v_i=b they produce the affine equations v_j=b*u_j. Substituting those affine equations into quadratic H at cap two is permitted: the difference is a sum of affine cofactors times available affine equations. For b=0 the result is u=0; for b=1 it is u⁴+u=0. The latter map is injective on W because its full-field kernel is F2 and W excludes 1. In either case the remaining constraint u_i=1 contradicts the derived affine equations at cap two. Two successive one-bit lifts give u_i at cap four. Then H gives v²=0, hence all v coordinates, at the same cap. Thus the conditional h<=4 theorem respects strict degree thresholds.

For the proposed square-stable, trace-isotropic W, A=w²+w is invertible on W and on ker Tr(K), since n is odd and 1 has trace one. Consequently projection of uv modulo W can indeed be obtained by a linear output transform of H modulo W; its off-diagonal coefficients are the displayed minors and its diagonal coefficients vanish modulo W. The dimension comparison r(r-1)/2>r+1 for r>=4 correctly rules out independence of all pair-product classes. Set-theoretic absence of decomposable tensors in a kernel remains weaker than deriving those minors at degree two, as the note emphasizes.

No mathematical correction is required. The result is a precise set of sufficient upper-bound constructions and missing normalization/lower-bound obligations; it supplies no growing lower bound by itself.
