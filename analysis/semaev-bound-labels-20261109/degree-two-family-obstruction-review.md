# Independent review: degree-two obstruction and exceptional-subspace count

Date: 2026-11-09. Source-only review of `degree-two-family-obstruction.md`, with the degree-two closure proof checked against Proposition 2.6 of the current local theorem dossier. No computation, build, solver, or cloud execution.

**Verdict: both constant lower-bound conclusions are correct.** Every qualifying two-solution subspace containing 1 has LFD at least three. Infinitely many odd degrees admit trace-active unsatisfiable subspaces with LFD at least three. Neither argument establishes a growing degree bound.

## Product span and saturated degree-two closure

For nonzero mu the trace pairing B_mu(x,y)=Tr(mu xy) is nondegenerate. If mu annihilates every product of elements of V, then V is totally isotropic, so V is contained in its orthogonal complement and 2dim V<=n. On the odd diagonal, 2k=n+1, a contradiction. Thus the product span is the entire field for every V considered.

I checked the dossier's saturated-closure proof, not merely its proposition title. Initial equation combinations have quadratic parts parametrized injectively by mu in ker Tr under this full-product-span hypothesis. The initial affine span is the single trace relation ell. Adjoining ell times affine polynomials could create a new affine consequence only if the associated mixed bilinear form equals Tr(x)Tr(y). Pure x-x and y-y quadratic components restrict the multiplier exactly as stated in the dossier. When this rank-one exception is absent, the only affine consequences remain the multiples of ell, and further degree-two closure adds nothing. This justifies use of the full W2 statement. No universal first-fall assertion is needed here.

If 1 belongs to V, the exceptional equation evaluated at x=y=1 forces Tr(mu)=1, contradicting its required zero trace. The trace relation is nonconstant since Tr(1)=1. For a qualifying two-point subspace, the affine vanishing space has dimension 2k-1>1, while the affine part of W2 has dimension one. A missing affine vanisher therefore proves LFD>=3 for every such V.

## Exceptional-subspace geometry

For fixed nonzero trace-zero mu, C_mu=B_mu+Tr tensor Tr has radical equation

    mu*x+Tr(x)=0.

A nonzero radical exists precisely when Tr(1/mu)=1, and its dimension is one. Without it, a totally isotropic (r+1)-space in dimension 2r+1 is impossible. Put a=sqrt(mu), h=1/a. The diagonal of C_mu is Tr((a+1)x), so exceptional V lies in the 2r-dimensional hyperplane H_a. Here a+1 is nonzero because Tr(a)=0 whereas Tr(1)=1.

When Tr(h)=1, the radical of the alternating restriction to H_a is exactly span{h,h²}. Directly, both vectors lie in H_a; the associated linear operators are a+1 and zero respectively, so they annihilate H_a. Conversely, the equation a²x+Tr(x) in span{a+1} puts every radical element in that span. The two vectors are independent because h is neither zero nor one.

The quotient is symplectic of dimension 2r-2. An isotropic subspace of dimension r+1 must contain the two-dimensional radical, and its quotient is a Lagrangian of dimension r-1. The count product_(i=1)^(r-1)(2^i+1) follows by the stated nonzero-vector incidence recurrence; the empty product handles r=1. Counting all possible mu and using the elementary upper bounds gives at most 2^[r(r-1)/2+3r] exceptional subspaces. No probabilistic independence assumption is required.

## Comparison with trace-active UNSAT density

The previously reviewed trace-active expectation gives UNSAT fraction at least (2a²-a-4)/(2(a+1)(a²-2)) when t_n>=0. For a>=4 this is at least 1/(4a). The Gaussian-binomial population lower bound and the two conditioning fractions imply at least 2^(r²-4) trace-active UNSAT subspaces. For r>=7,

    r²-4 > r(r-1)/2+3r,

so at least one UNSAT subspace avoids every exceptional mu. It has no constant in W2 and therefore LFD>=3. The earlier irrational-Frobenius-angle argument supplies infinitely many eligible odd n with t_n>0, even after discarding all n<15.

This is a valid exceptional-set comparison at degree two. Its proof does not extend to W3 without a new description of that saturated closure. No mathematical correction is required.
