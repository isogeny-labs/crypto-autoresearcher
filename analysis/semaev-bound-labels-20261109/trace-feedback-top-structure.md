# The first feedback tops and failure of the rectangular invariant ansatz

2026-11-09. Pure proof; no scientific execution. This note computes the actual quadratic outputs of the trace-slice multiplier conditions and shows why the original rectangular bilinear form is not a preserved class.

Use independent x in V, t in W=V intersect ker Tr, and epsilon in F2, with e in V of trace1. Write the exact trace-slice equation as

 G=xt+D(x)+H(t)+g+epsilon,
 D(x)=x²+ex, H(t)=J(t)², g=J(e+1)².

Here D,H are F2-linear. The previous note proves that a scalar multiplier

 m=a+L(x)+M(t)+c epsilon

has Tr(mG) of degree at most two exactly when

 beta_L(V,V) subset W_perp, beta_M(W,W) subset V_perp,
 c in (VW)_perp,

where beta_L(x,z)=xL(z)+zL(x), and similarly for M. These include every affine scalar-output multiplier, not just field-valued scalar multiples of x and t.

## 1. Intrinsic diagonal contractions

Under the first condition, the map

 x -> xL(x) modulo W_perp

is F2-linear: its polarization is beta_L and vanishes in that quotient. It therefore defines a well-defined bilinear scalar form

 T_L(x,t)=Tr(xL(x)t).

Similarly T_M(x,t)=Tr(xtM(t)) is bilinear under the second condition. This is an intrinsic description; no choice of Boolean basis or arbitrary dropping of repeated indices is required.

Thus a cubic-looking contraction supplies a specific new rectangular quadratic form. Its dependence on L or M is linear, so the full family remains explicitly parametrized by the actual field trace tensor.

## 2. Complete first-feedback polynomial formula

For every admissible multiplier, Boolean reduction gives the exact identity

 Tr(mG) = Tr(aG)
          +T_L(x,t)+T_M(x,t)
          +Tr(L(x)D(x))+Tr(M(t)H(t))
          +Tr(L(x)H(t))+Tr(M(t)D(x))
          +Tr(g(L(x)+M(t)))
          +epsilon Tr(L(x)+M(t))
          +epsilon Tr(c(D(x)+H(t)+g+1)).                     (1)

The term epsilon Tr(cxt) is zero by c in (VW)_perp, and epsilon²=epsilon accounts for the final1. Every term on the right is of degree at most two. Formula (1) is therefore an explicit parametrization of the complete first-feedback space, including its lower-degree tails, not merely its dimension or homogeneous rank.

The possible quadratic blocks are now:

* pure x terms from Tr(L(x)D(x));
* pure t terms from Tr(M(t)H(t));
* rectangular x,t terms from the contractions and mixed linear maps;
* epsilon,x and epsilon,t terms.

Their coefficients are linked by the common admissible L,M,c. Treating these blocks as independently available consequences would enlarge the closure without justification.

## 3. The rectangular-plus-affine class genuinely fails

The pure-x block is not a formal possibility that can always be discarded. Take the admissible multiplier m=a x for any a in K. Admissibility holds because x*(a z)+z*(a x)=0. On the slice t=epsilon=0, its consequence becomes

                  Tr(a xG)=Tr(a(x³+e x²+g x)).

The last two terms are linear. The polarization of x³ is

                         xz²+zx²=xz(x+z).

For any linearly independent x,z in V this field element is nonzero. Nondegeneracy of trace supplies an a for which the scalar polarization is1. Since dim V>=2, such x,z exist. Consequently at least one mandatory cap-three consequence has a genuinely nonzero pure-x quadratic top.

Every original coordinate of G, restricted to t=epsilon=0, is affine in x. Thus that consequence is outside the original coordinate span. In particular, a proposed invariant consisting only of rectangular xt forms plus affine terms cannot contain the first feedback step. This does not assert W3 differs from W2: additional affine consequences and their W2 multiples might already generate some of these polynomials. It rules out the stated rectangular ansatz, not every possible stable space.

## 4. Why first-step multiplier parametrization does not finish closure

After adjoining (1), multiplication by a variable acts on polynomials with pure-x, pure-t, and epsilon-coupled tops. Their cubic cancellation conditions involve those new blocks. Reapplying only the old beta_L/beta_M test would omit valid falls because that test assumed the original top xt.

Equivalently, multiplying a quadratic first-step consequence Tr(mG) by a linear h creates an expression Tr(hmG) whose coefficient multiplier has degree two. A degree-three derivation can continue with higher multiplier degree through repeated falls; it need not have a representation using only affine multipliers of G. Consequently no bound on the dimension of the affine multiplier space proves saturation.

An exact prospective invariant must specify a space of the linked block forms in (1), include their affine tails, and verify that every cancellation of cubic terms among all their variable products returns to that same space. The missing lemma is preservation of such a linked-block space under this operation for an explicit infinite V family. The present calculation supplies the first space and proves a narrower tempting invariant impossible; it does not establish an invariant omitting1 or a uniform closure collapse.
