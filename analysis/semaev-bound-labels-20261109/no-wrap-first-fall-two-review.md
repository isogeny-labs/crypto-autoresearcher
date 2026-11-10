# Independent review: qualified first fall two for no-wrap coefficients

Date: 2026-11-09. Source-only review of `no-wrap-first-fall-two.md`. No execution.

**The statement is correct for the exact input presentation and both explicitly defined conventions.** The only nonzero affine input row is f0=x0+y0+1. Positive odd rows are quadratic p_j where nonzero; positive even rows at most 2r have disjoint quadratic supports p_j and p_(j/2); positive even rows above 2r are quadratic p_(j/2). Thus no positive-index nonzero row becomes affine accidentally.

For odd d<=r and 2^t*d<=r<2^(t+1)*d, the proposed sum f_d+sum_(i=0)^(t+1) f_(2^(i+1)*d) telescopes to sum_(i=0)^t s_(2^i*d). The final surviving p coefficient has index 2^(t+2)*d>2r and vanishes; the last s index exceeds r and also vanishes. All included rows have index at most4r and are nonzero quadratics. The residual is a nonzero linear form involving only positive-index bits, independent of f0.

Consequently constant multipliers give a literal nonzero fall from source degree two, while source degree one has only f0 and cannot give a nonzero constant result. The same residual lies in strict W2 but not W1, establishing the operational new-consequence version. The proof does not rely on a syzygy-quotient definition or conflate it with those conventions.

The presentation qualification is essential: row reduction can expose the linear residual as an input. The note correctly restricts its FFD conclusion rather than declaring row-span invariance. Together with the reviewed last-fall results, the family has first fall two and last fall between three and four for r>=6, with exact last fall three at r=6. The first/last gap is bounded in this family and supplies no unboundedness theorem.
