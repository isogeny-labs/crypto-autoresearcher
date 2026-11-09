# A necessary growing pure block in any degree-three invariant

2026-11-09. Source-only. No computation or scientific campaign. This note strengthens the failure of the rectangular ansatz quantitatively, but makes no inference from dimension to a growing fall degree.

Use n=2r+1, dim V=r+1, and the exact trace-slice system G=xt+D(x)+H(t)+g+epsilon, where D(x)=x²+ex. Let Q0 be its original coordinate span and Q1 the complete first quadratic feedback space. Every scalar consequence Tr(a xG), a in K, lies in Q1 by strict cap-three multiplication and Boolean reduction.

## The mandatory pure-x block has dimension at least r

Project a quadratic polynomial to its pure-x quadratic top, equivalently restrict t=epsilon=0 and then quotient by affine functions of x. Under this projection,

 Tr(a xG) maps to the class of Tr(a x³),

since xD(x)=x³+ex² and gx is linear. Define Phi:K -> quadratic forms on V modulo affine forms by this map.

Its kernel consists of those a for which the alternating form

 C_a(x,z)=Tr(a(xz²+zx²))

vanishes on V. For a!=0, C_a has rank n-1 and radical {0,a^(-1/3)}; the inverse cube exists since n is odd. This is the j=1 case of the previously proved radical formula. Since dim V=(n+1)/2, total isotropy forces this radical to lie in V. The map a->a^(-1/3) is a permutation of K*. Therefore

 |ker Phi|<=|V|=2^(r+1),
 dim ker Phi<=r+1,
 rank Phi>=n-(r+1)=r.                                      (1)

The projected first-feedback space consequently contains at least r independent pure-x quadratic classes. Q0 has zero projection there because its top is only xt. Thus

                        dim(Q1/Q0)>=r.                     (2)

This proves that no proposed invariant consisting of the original coordinate span plus a bounded number of additional pure-x directions can work along a growing half-diagonal family. It must at least include this growing block, with its linked mixed and epsilon terms retained.

The conclusion is about a necessary consequence-space component, not LFD. A large quadratic block can accelerate a refutation rather than obstruct one. Nor does (2) assert Q1 exceeds the full W2 by r: additional affine consequences and their variable multiples may already be present in W2.

If span(VW)=K, the trace-slice input span contains no nonzero affine polynomial, because its quadratic top map is injective on output functionals. Then its full W2 is exactly Q0, and (2) is genuinely a lower bound on the dimension added in W3. This optional condition does not imply that W3 omits1.

## A concrete feedback cycle that supplies no additional invariant

Write R=D(x)+H(t)+g+epsilon, an affine K-valued function, so G=xt+R. The already derived quadratic tG may be multiplied by x at cap three; also RG is obtainable from the input G by affine multipliers. Their sum is

                       x(tG)+RG=G².

The right side is only an output-Frobenius row transformation of G. Thus this tempting way to cancel the new cubic terms produces no additional quadratic direction beyond the input coordinate span. It does not justify closing the whole linked-block space: other scalar-trace syzygies need not be field-valued instances of this identity.

## Remaining construction

An invariant must accommodate at least the r-dimensional pure-x block from (1), its affine tails, and its coupled mixed and epsilon blocks. The simple field-product feedback cycle above does not specify their stable span. The missing step remains a description of all cubic cancellations among variable multiples of those linked polynomials for an explicit infinite V family, followed by an actual omission-of1 or affine-generator proof.

No uniform upper bound or growing LFD lower bound is established by this note. The new result is the universal minimum size of a mandatory block, and the exact failure of one natural field-product feedback cycle to add information.
