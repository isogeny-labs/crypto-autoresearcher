# Exact degree-two closure dimension on the nonexceptional diagonal

2026-11-09. Derived by the parent from the reviewed degree-two structure and independently checked in `degree-two-codimension-review.md`. No execution or search.

Let n=2r+1, k=r+1, N=2k=n+1, z=a6=1. Assume trace is nonzero on V and the rank-one exception G2 is absent. This includes every V containing1, and the selected nonexceptional UNSAT subspaces in the companion theorem.

The saturated closure is W2=span(F)+ell B_(<=1), with ell=Tr(X+Y)+1. Three exact dimension calculations give its size:

1. span(F) has dimension n. The quadratic coefficient map has rank n-1 because span(VV)=K and the coefficient Frobenius map has a one-dimensional kernel. Its remaining row is the nonconstant affine trace consequence ell, so the complete row span has rank n.
2. ell B_(<=1) has dimension N. An invertible affine change turns ell into one Boolean coordinate u1. Its products with affine functions span u1 and u1*ui for i=2,...,N, exactly N independent monomials.
3. The intersection of those two spaces is precisely span(ell), of dimension one. A quadratic component in the intersection would either vanish or equal the rank-one trace product. G1 handles the first case and G2 excludes the second, as in the reviewed saturated-W2 proof.

Hence

    dim W2=n+N-1=2N-2,
    codim(W2 in B_(<=2))=1+N+binom(N,2)-(2N-2)
                         =(N²-3N+6)/2.

At N=4 the formula gives codimension5, matching the hand-derived F8 control. For the exactly-two-solution family this is a strict excess over the solution count, so it is also a direct degree-two count-bridge proof of LFD>=3.

The polynomial growth here is growth of quotient dimension at the fixed cap D=2. It does not show survival at D=3 or any growth of LFD. A smaller rank of an arbitrary accepted containing-kernel certificate is not a contradiction: this formula concerns the exact closure quotient.
