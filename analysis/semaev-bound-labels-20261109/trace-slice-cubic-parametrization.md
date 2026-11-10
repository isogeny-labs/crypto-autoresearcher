# Exact cubic-cancellation parametrization on the trace slice

2026-11-09. Source-only proof; no execution, campaign, or build. This replaces the independent-x,y cubic test by a test on genuinely independent coordinates after eliminating the trace relation. It describes the first quadratic feedback step exactly, not the eventual stable W3.

## 1. Rectangular bilinear coordinates after eliminating the trace

Let n=2r+1, dim V=r+1, and assume Tr is nonzero on V. Put W=V intersect ker Tr, so dim W=r, and choose e in V with Tr(e)=1. On the affine trace slice Tr(x+y+1)=0, set

                 t=x+y+e in W,       y=x+t+e.

Now x in V and t in W are independent coordinate groups. With J the inverse of A(w)=w²+w on ker Tr, define B(t)=J(t+e+1)²; this is well-defined because Tr(t+e+1)=0. The exact one-bit extension becomes

 G(x,t,epsilon)=xt+x²+ex+B(t)+epsilon=0.                      (1)

The only quadratic top is the rectangular field product xt. All other terms are affine in the Boolean coordinates. This affine parametrization automatically accounts for every multiple of the eliminated trace relation; no pre-slice independence assumption is retained.

## 2. Complete parametrization of first-step quadratic feedback

Every sum of original G coordinate equations multiplied by affine Boolean polynomials can be written uniquely at the level of its output multipliers as

                    Tr(m(x,t,epsilon) G),
 m=a+L(x)+M(t)+c epsilon,

where a,c lie in K and L:V->K, M:W->K are arbitrary F2-linear maps. This follows from nondegeneracy of the output trace pairing. The resulting scalar polynomial has degree at most two if and only if

 x L(z)+z L(x) belongs to W_perp   for all x,z in V,          (2)
 t M(u)+u M(t) belongs to V_perp   for all t,u in W,          (3)
 c belongs to (span(VW))_perp.                               (4)

Proof: the only possible cubic terms have the three distinct multidegrees (2,1,0), (1,2,0), and (1,1,1) in the coordinate groups x,t,epsilon. Polarizing the repeated group gives (2) or (3), and the last group gives Tr(cxt)=0 for all x,t. Distinct group multidegrees cannot cancel each other. Repeated Boolean indices produce lower-degree terms and impose no additional cubic condition. Thus these conditions are both necessary and sufficient.

Consequently, if Q0 is the coordinate span of G, then

 (Q0+sum_Z Z Q0) intersect B_(<=2)

is exactly the image of the multiplier space (2)-(4) under m -> Tr(mG), where Z runs through the independent x,t,epsilon coordinates. This is the full first feedback step after trace elimination, including any cubic cancellations that previously could be described as multiples of the trace relation.

The conditions differ materially from their pre-slice counterparts: W_perp replaces V_perp in (2), and the epsilon coefficient need not vanish.

## 3. The epsilon exception has dimension at most one

For r>=1, define C=(span(VW))_perp. Then

                         dim C <=1.                         (5)

Indeed if c is a nonzero element of C, then cW is contained in V_perp. Both spaces have dimension r, so cW=V_perp. If c,d are distinct nonzero elements of C, alpha=d/c satisfies alpha W=W. Hence W is a vector space over the subfield F2(alpha). Its degree divides both n and dim W=r. But gcd(2r+1,r)=1, so that subfield is F2 and alpha=1, contradicting c!=d. This proves (5).

Thus span(VW) is either K or a codimension-one subspace. If the exception exists, its coefficient c is unique.

## 4. Exact identification with a rank-one trace form

A nonzero c lies in C if and only if

                 Tr(cuv)=Tr(u)Tr(v) for all u,v in V.        (6)

The reverse direction is immediate since W is trace zero. For the forward direction, cW=V_perp implies W_perp=cV. Because Tr(cw²)=0 for w in W, the trace identity Tr(cw²)=Tr(sqrt(c)w) shows sqrt(c) belongs to W_perp=cV. Therefore rho=1/sqrt(c) lies in V.

It cannot lie in W: otherwise sqrt(c)=c rho would belong to V_perp and its pairing with rho in V would be Tr(1)=1, a contradiction. Hence Tr(rho)=1 and V=W direct_sum F2*rho. The form Tr(cuv) vanishes whenever one argument lies in W and takes value Tr(c rho²)=Tr(1)=1 on (rho,rho). This proves (6).

When this exception occurs, Tr(c epsilon G) is an additional quadratic consequence available at cap three. Its formerly cubic term epsilon*Tr(cxt) vanishes on the trace-slice coordinates. A purported complete first-step description that simply carries forward the pre-slice conclusion c=0 would miss it.

No condition Tr(c)=0 is asserted here. For example, if 1 belongs to V, equation (6) forces Tr(c)=1. The appearance of this exceptional multiplier therefore should not be conflated with an earlier exception that imposed a trace-zero output coefficient.

## 5. Remaining stability obligation

Equations (2)-(4) exactly characterize the first quadratic feedback space in the correct independent coordinates. The scalar multipliers corresponding to xG and tG satisfy these equations, as expected. New quadratic consequences may themselves have different quadratic tops; their affine multiples require a fresh cancellation analysis. Iterating this operation to a fixed point is still necessary before claiming a full W3 obstruction.

A concrete next construction is therefore to solve (2)-(3) for a specified infinite V family, include the at-most-one exception (6), and prove that the resulting quadratic space is invariant under further degree-three feedback while omitting1 on UNSAT instances. The present note proves the trace-slice parametrization and the exact epsilon-exception theorem, but neither that invariant nor a uniform refutation bound.
