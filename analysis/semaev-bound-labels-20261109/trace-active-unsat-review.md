# Independent review: trace-active unsatisfiable existence family

Date: 2026-11-09. Source-only review of `trace-active-unsat-family.md`, identified by the author/parent as frozen SHA-256 `2cd17a8c79ef9c02864f2b7e01bc3559d274c2d0e10f52c4132ee7a3e030c8f0`. No scientific execution, build, sampling, or cloud job.

**Verdict: the stated infinite existential family is correct.** The refinement removes subspaces on which the single trace relation is already the constant contradiction. It does not exclude other degree-two refutations or establish a positive growing LFD lower bound.

## Conditional counting

For odd n, Tr(1)=1. Writing P=xy and s=x+y gives F=(P+s)²+P+1; applying absolute trace yields Tr(s)+1. Consequently any subspace V contained in ker Tr has no solutions, and its contribution to the solution-count expectation is exactly zero.

For uniform k-dimensional V in an n-dimensional binary space, the probabilities in Section 3 are correct. Their ratio simplifies directly to

    (2^(n-k)-1)/(2^n-2^k)=2^(-k).

Since k=r+1 and a=2^r, the excluded trace-zero fraction is exactly 1/(2a). Its complement is positive for all a>=2. This computation conditions on 1 not belonging to V throughout; it makes no independence assumption.

The earlier independently reviewed formula p_excl=(2a-1)/(2(a+1)(a²-2)) therefore gives

    E[N_V | 1 not in V, trace active]
       =a(N-2)/((a+1)(a²-2)).

The point-count identity N=#E(K)-2=2a²-1-t_n was checked in the companion review. The required difference from twice the denominator is precisely

    2(a+1)(a²-2)-a(2a²-3-t_n)=2a²-a-4+a*t_n.

For a>=2 and t_n>=0 it is strictly positive (the non-trace part is already 2 at a=2). Absence of diagonal zeros makes the restricted counts even. Thus expectation below two supplies an unsatisfiable trace-active subspace, with the stated dimension and exclusion of 1.

## Infinitely many eligible odd degrees

The four displayed F2-points on E are all its points, so its base trace is -1 and its Frobenius characteristic polynomial is T²+T+2. If alpha=(-1+i sqrt(7))/2, its conjugate is the other root and |alpha|=sqrt(2). The extension formula t_n=alpha^n+conj(alpha)^n follows from powering Frobenius. This input is explicitly supported by the characteristic-polynomial discussion (Fact 1.11) and extension point-count formula (Exercise 17) in [CTNT, Curves over Finite Fields](https://ctnt-summer.math.uconn.edu/wp-content/uploads/sites/1632/2020/06/Notes__Curves_over_Finite_Fields_Final.pdf), which I opened and checked for those statements. The recurrence t_n=-t_(n-1)-2t_(n-2) follows immediately from the quadratic equation.

With alpha=sqrt(2) exp(i theta),

    exp(2i theta)+exp(-2i theta)=(alpha²+conj(alpha)²)/2=-3/2.

A root of unity and its inverse are algebraic integers; their rational sum could not equal the noninteger -3/2. Thus exp(2i theta) is not a root of unity, and theta/pi is irrational. The odd-degree sequence of angles is theta+r(2theta), so it is an irrational rotation orbit modulo 2pi. It is dense, and every tail is dense as well. Therefore it visits the nonempty open region cos>0 infinitely often, not merely once. These visits give infinitely many odd n with t_n>0; deleting n=1 and any finite initial segment does not change infinitude. The note's density argument is sufficient; no probabilistic or equidistribution assertion is needed.

## Scope and publication qualification

For every eligible odd degree the argument supplies a subspace existentially. It supplies neither an efficiently describable sequence of bases nor a computation of one. The target retains order four, as established in the companion review.

Trace activity means Tr(s)+1 is a nonconstant affine equation in the selector coordinates. It only removes the particular constant contradiction caused by trace-zero V. It does not establish that 1 is absent from the full degree-two closure: additional row combinations and subsequent degree-limited closure operations remain uncontrolled. The source note states this limitation correctly. A future lower-bound theorem must add a simultaneous growing closure obstruction; the present averaging proof places no lower bound on its probability.

No mathematical correction is needed to the frozen statement reviewed here.
