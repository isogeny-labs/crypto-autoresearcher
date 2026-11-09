# Independent review: explicit half-diagonal affine-separator family

2026-11-09. Source-only mathematical review of `explicit-half-diagonal-affine-separator-family.md`. No solver, experiment, build, or software test was executed for this review.

**Verdict: the construction proves the stated infinite family of UNSAT normalized Boolean m=2 systems with LFD at most three.** The reviewed final source distinguishes the target z=1 from the auxiliary trace-zero element eta, resolving the notation collision found during review.

## Frobenius module and trace pairing

The minimal-polynomial proof is sufficient without importing the normal basis theorem. A relation of degree d<n among powers of Frobenius would define a nonzero linearized polynomial of degree at most 2^d vanishing at all 2^n field elements. Thus the minimal and characteristic polynomials both equal X^n-1. Because n is odd, the polynomial is squarefree, so every irreducible constituent occurs once.

For n=3*7^j the reciprocal-factor classification is correct. The order of 2 modulo 7^h divides the odd integer 3*7^(h-1), excluding -1 from its cyclic subgroup. Any root order divisible by 7 inherits this exclusion by reduction modulo the relevant power of 7. The only remaining orders are 1 and 3, giving precisely X+1 and X^2+X+1 as self-reciprocal factors.

The trace pairing is Frobenius invariant. On extension to a splitting field, eigenvectors of eigenvalues alpha and beta can pair nontrivially only when alpha*beta=1. Selecting one constituent from each remaining reciprocal pair therefore gives an isotropic, Frobenius-stable L of dimension (n-3)/2, orthogonal to both 1 and S. This proves all the orthogonality assertions used later; no multiplication closure of L is needed.

## Factor base and quadratic trace identity

For independent nonzero w,eta in S, W=<w>+L and V=W+<1+eta> have the asserted dimensions and trace properties. In particular, 1 is excluded because eta is outside <w>+L. Absolute trace restricted to F8 is its usual trace since n/3 is odd.

On K0, F+I is invertible: its kernel in K is <1>, and Tr(1)=1. Its inverse J and H=FJ preserve L and S. Isotropy gives Q(l)=Tr(lH(l))=0 on L and vanishing mixed S,L terms. On S, J(u)=u^2 and H(u)=u^4. For nonzero u in S, u^3=u+1, hence u^5=u^2+u+1 and Q(u)=1. Therefore Q(eta+bw+l)=1 for either bit b and every l in L.

## Separator and strict degree cap

With e=1+eta and lambda=t+eta, one has t+e=lambda+1. The adjoint coefficient of x in Tr(lambda F_t(x)) is

    F^(-1)(lambda)+(t+e)lambda
      = F^(-1)(lambda)+F(lambda)+lambda.

The operator on the right vanishes on S and preserves L, so its value belongs to L, which is orthogonal to V. The remaining term is Q(lambda)=1. This proves the literal polynomial identity, not only its pointwise evaluation on a presumed solution set. Boolean functions have unique multilinear representatives, so the computation is also valid in the stated Boolean quotient.

The degree-three claim survives the original presentation. The trace relation is a cap-two consequence. Substitution along this affine relation has quadratic corrections that are multiples of it by affine polynomials, so the sliced quadratic coordinate equations can be lifted at cap two. The constant field-linear row changes used to obtain F_t do not raise that cap. Multiplying the resulting degree-at-most-two equations by the affine coordinate functions of lambda costs at most cap three. Lifting the final identity through the same affine relation has degree-at-most-three corrections. No selector of unbounded degree is involved.

For an UNSAT Boolean system, a refutation at cap three implies LFD at most three: after deriving 1, all monomials of degree d can be derived within cap max(3,d). The note properly refrains from an exact-degree claim.

## Edge cases and scope

At j=0, n=3 and L=0; the construction still works with W=<w> and V=<w,1+eta>. There is no missing nonzero-L assumption.

The necessity statement for this specific natural separator is also correct: when 3 does not divide n, F^(-1)+F+I is invertible; its image of W has dimension r, while V_perp intersect K0 has dimension r-1 because 1 is not in V. This excludes that candidate separator, not all affine separators.

If a rational curve target is desired, the choice a2=0,a6=1 gives the nonsingular curve y^2+xy=x^3+1 with rational target (1,0). It is a low-order target (order four), so no generic-target or prime-order-target conclusion follows. The theorem itself is explicitly about full vector-space domains V x V and does not transfer automatically to nonlinear finite-selector encodings.

This is an infinite, growing half-diagonal family with a constructive constant upper bound. It establishes that trace-active UNSAT instances alone do not supply a growing lower bound. It makes no universal statement about other fixed-m=2 families.

Final source readback: auxiliary element eta is consistent throughout and the compatible curve/target is explicit. Reviewed source SHA256: `38fcc07811a9a0ef15c745b5119fe835e779f49cbab5643c88e8bf38a0aaf392`.
