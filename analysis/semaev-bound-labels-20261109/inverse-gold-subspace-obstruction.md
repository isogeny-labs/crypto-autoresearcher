# Inverse-Gold subspace invariance: a trace-active counterexample and exact constraints

2026-11-09. Source-only algebra, no experiments, computations, builds, or cloud work. This continues `modular-frobenius-multiplier-obstruction.md`.

## The necessary condition is not universally impossible

Put K=F8=F2[alpha]/(alpha^3+alpha+1), j=1, V=span_F2(1,alpha), and a=alpha^4. Then n=3 is odd, gcd(j,n)=1, and dim V=2=(n+1)/2. The space is trace-active because 1 lies in V and Tr(1)=1.

On K*, the inverse of 3 modulo 7 is 5, and -5=2 modulo 7. Therefore the necessary map in the earlier note is

    R(w)=(a w)^(-1/3)=(a w)^2=alpha w^2.

It permutes V minus zero in the explicit cycle

    1 -> alpha -> 1+alpha -> 1.

Indeed alpha^3=alpha+1 and alpha^8=alpha. Thus the necessary inverse-power condition holds for a trace-active half-dimensional additive space, even one containing 1. Any theorem excluding it for all odd n is false.

In fact this example satisfies the stronger original trilinear condition, not only the radical condition. The alternating F2-bilinear map B(x,z)=xz^2+zx^2 on V has image contained in span(alpha^2+alpha), because its value on the basis pair (1,alpha) is alpha^2+alpha. Multiplying by a gives

    alpha^4(alpha^2+alpha)=alpha^8=alpha.

For w in V, Tr(alpha w)=0: Tr(alpha)=0 and Tr(alpha^2)=0, by the irreducible polynomial's zero quadratic coefficient and Frobenius invariance. Hence Tr(a w B(x,z))=0 for all x,z,w in V. This supplies an actual exception to exclusion of these shifted scalar cubic terms before trace-slice elimination.

This is a symbolic three-dimensional field counterexample, not a measured closure result or a construction for growing n.

## Scaling and the small-dimension mechanism

The condition is invariant under scaled subspaces. If (V,a) satisfies R(V*)=V*, then for c nonzero, (cV, a c^(-(2^j+2))) also satisfies it. Indeed the inverse-power image of a c^(-(2^j+2)) times cw is c times the original inverse-power image of aw. The trilinear condition has the same scaling rule because its three-variable expression scales by c^(2^j+2).

The n=3 exception arises because the inverse-Gold exponent is itself a Frobenius exponent. This mechanism cannot hold globally for odd n>=5. If -(2^j+1)^(-1)=2^h modulo 2^n-1, then

    2^((j+h) mod n)+2^h+1 = 0 mod (2^n-1),

with h represented in 0,...,n-1. The left side is positive and at most 2^n+1, so for n>=3 its only possible positive multiple of 2^n-1 is 2^n-1. A sum of three powers of two has binary weight at most three, whereas 2^n-1 has weight n. Thus n<=3. This does not exclude invariant subspaces for n>=5; it only removes the automatic globally linear power-map explanation.

## Exact finite algebraic criterion for any n

Let q=2^j, d=q+1, and k=dim V. Let the monic subspace polynomial be

    L(X)=product_(v in V)(X+v)=sum_(i=0)^k c_i X^(2^i),
    c_k=1, c_0 nonzero.

The inverse-power permutation R(w)=(aw)^(-1/d) has inverse R^(-1)(x)=a^(-1)x^(-d). Since it is a permutation of K*, R(V*)=V* is equivalent to a^(-1)x^(-d) belonging to V* for every x in V*. Therefore it is equivalent to the explicit divisibility condition in K[X]

    L(X)/X divides H(X),
    H(X)=sum_(i=0)^k c_i a^(-2^i) X^(d(2^k-2^i)).

Proof: for nonzero x, H(x)=x^(d 2^k) L(a^(-1)x^(-d)). The polynomial L(X)/X has precisely the distinct roots V*, so it divides H exactly when H vanishes at every such root. Membership then gives equality because the inverse map is injective. This criterion is exact, rather than a sufficient condition inferred from inverse-closed-subspace classifications. A candidate coefficient tuple still needs to define a subspace polynomial with all roots in the intended field.

## Product and moment obstructions

Let M=2^k-1 and P=product_(v in V*)v=c_0. Taking the product of the inverse images yields the necessary identity

    c_0^(d+1)=a^(-M).

For k>=2, the additive-subspace power sums satisfy

    sum_(v in V*) v^m=0 for 1<=m<M.

One proof is the formal Laurent identity sum_(v in V)1/(T+v)=L'(T)/L(T)=c_0/L(T): its leading exponent is T^(-2^k), so the preceding power-sum coefficients vanish. Invariance therefore forces

    sum_(v in V*) v^(-dm)=0 for 1<=m<M.

These are necessary constraints independent of a, because its nonzero scalar power cancels from each zero equality. Together with the product identity and divisibility criterion they are concrete algebraic rejection tests; no sufficiency is claimed for the moments alone.

For the important shift j=1, d=3, the first moment has a particularly small coefficient form. The reciprocal-root polynomial has first elementary coefficients e_1=c_1/c_0, e_2=0, e_3=c_2/c_0 (for k>=2). Newton's identities in characteristic two give

    sum_(v in V*)v^(-3)=(c_1/c_0)^3+c_2/c_0.

Thus inverse-cube invariance necessarily implies

    c_2 c_0^2 = c_1^3.

This is an explicit subspace-polynomial obstruction for every k>=2. It is compatible with the displayed F8 example and does not by itself prove impossibility in larger odd dimensions.

## Remaining proof obligation

The blanket half-dimensional impossibility route fails at n=3, including the trace-active containing-1 case. For odd n>=5, the exact divisibility and power-sum restrictions remain available, but this note does not prove that they are inconsistent at k=(n+1)/2 or exhibit an infinite family satisfying them. The inverse-power exponent is not ordinary inversion; no classification of inverse-closed additive spaces has been imported. Even proving the radical condition impossible in a chosen family would exclude only these shifted trace multipliers, not all cap-three feedback or higher closed-kernel obstructions.
