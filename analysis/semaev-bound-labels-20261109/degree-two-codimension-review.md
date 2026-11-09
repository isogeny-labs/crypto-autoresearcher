# Independent review: exact degree-two codimension

Date: 2026-11-09. Source-only audit of the parent's proposed addendum and the previously reviewed saturated degree-two formula. The addendum file was not yet present at the initial read; the derivation below independently checks the mathematical claim. No execution or matrix computation.

**Verdict: the formula is correct.** Let n=2r+1, k=r+1, N=2k=n+1 and V contain 1. For the normalized z=a6=1 family,

    dim W2 = 2N-2,
    dim(B_(<=2)/W2) = (N²-3N+6)/2.

The previously reviewed result supplies W2=span(F)+ell*B_(<=1), with ell=Tr(x+y)+1 nonconstant and the rank-one exception absent.

1. The quadratic coefficient rank of the original equation span is n-1: product span is K, and u->u²+u has one-dimensional kernel. Its one-dimensional coefficient-functional kernel produces the nonzero affine trace relation ell. Therefore dim span(F)=n.

2. An invertible affine Boolean coordinate change sends ell to one coordinate u_1. Multiplying u_1 by all affine polynomials gives the independent basis u_1 and u_1*u_j for j=2,...,N, because u_1²=u_1. Hence dim(ell*B_(<=1))=N. This is a dimension argument inside the degree filtration, not a change of the original input presentation.

3. If a polynomial in span(F) equals ell times an affine form, cancellation of the pure x-x and y-y quadratic parts restricts its mixed quadratic part to either zero or Tr(x)Tr(y). The latter is excluded by G2; the former, by G1 and the initial affine-span calculation, leaves precisely span{ell}. Thus the intersection has dimension one.

Adding dimensions gives n+N-1=2N-2. The ambient squarefree degree-at-most-two space has dimension 1+N+binomial(N,2), proving the displayed codimension. At N=4 this is five, consistent algebraically with the separate literal control, without relying on that control as evidence for the general formula.

The same derivation applies to any trace-active nonexceptional V on the odd diagonal, including those selected by the UNSAT existence/counting argument; containing 1 is a sufficient way to guarantee the required nonexceptional condition, not necessary for the dimension calculation.

This is the exact full-closure codimension at the single fixed cap D=2. An arbitrary accepted certificate can have smaller rank than this exact quotient. Conversely, the fact that this codimension grows quadratically in N does not imply that LFD grows: all the excess directions could disappear at cap three. The fixed LFD lower bound remains three where the established solution-count or UNSAT bridge applies.
