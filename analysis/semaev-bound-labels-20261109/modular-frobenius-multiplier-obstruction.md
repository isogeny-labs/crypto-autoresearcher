# Frobenius multipliers: automatic falls and a necessary subspace condition

2026-11-09. Pure symbolic analysis, with no computation or campaign. Continue the exact half-diagonal presentation ell=0, G=xy+B(x,y)+epsilon=0 from modular-degree-three-field-falls.md. Here n is odd, dim V=k=(n+1)/2, B is affine, and epsilon is an independent definitional bit before imposing the equations.

## 1. Simultaneously twisting the known falls gives no new span

For every j, the field equation G^(2^j)=0 is a constant invertible row transformation of the coordinate equations of G: Frobenius is F2-linear on the output field. Consequently

 x^(2^j) G^(2^j)=(xG)^(2^j)

is already in the coordinate span of the previously derived quadratic equation xG. The same holds for y. Thus simultaneous Frobenius shifts do not generate an independent ladder of cap-three consequences. For arbitrary shifts j,l, x^(2^j)G^(2^l) is a Frobenius transform of x^(2^(j-l))G, with indices interpreted modulo n. Only their relative shift matters.

## 2. An untwisted multiplier is not automatically quadratic

Consider x^(2^j)G. Its possible cubic part comes entirely from x^(2^j)xy. As a K-valued polynomial on independent Boolean coordinates x,y in V, this disappears precisely when x->x^(2^j+1) is additive on V, equivalently

 x z^(2^j)+z x^(2^j)=0 for every x,z in V.                    (1)

For nonzero z, (1) forces the restriction of Frobenius^(j) to V to be scalar multiplication. If j is not zero modulo n, any nonzero solution space of X^(2^j)=aX has dimension at most gcd(j,n). This follows because the ratio of any two nonzero solutions lies in the fixed field F_(2^gcd(j,n)). Since n is odd, any proper divisor is at most n/3, strictly below k. Hence (1) is impossible on the half diagonal for every nonzero relative shift.

So the known automatic field-valued falls occur only at relative shift zero. This does not rule out scalar trace cancellations of a nonzero field-valued cubic.

## 3. Exact trace-level condition for an additional shifted fall

Let a in K be nonzero. The scalar polynomial

                       Tr(a x^(2^j) G)

has Boolean degree at most two before eliminating ell if and only if

 Tr(a w (x z^(2^j)+z x^(2^j)))=0
           for every x,z,w in V.                            (2)

This follows by polarizing the two x factors and allowing the independent y factor to vary over V. The affine B and epsilon terms have degree at most two and cannot alter this cubic condition. In equivalent subspace form,

 a(x z^(2^j)+z x^(2^j)) belongs to V_perp for all x,z in V.

Equation (2) is a precise field-specific obstruction to extra shifted trace falls. It is stronger than the existence of one isotropic pair or a favorable initial matrix rank.

## 4. Coprime shifts force closure under an inverse power permutation

Choose the representative 1<=j<n and assume gcd(j,n)=1. For lambda nonzero define the alternating bilinear form

 C_lambda(x,z)=Tr(lambda (x z^(2^j)+z x^(2^j)))

on the entire n-dimensional field. Its radical is one-dimensional, with unique nonzero element r_lambda determined by

                       r_lambda^(2^j+1)=lambda^(-1).        (3)

To verify this, nondegeneracy of trace identifies the radical equation as

 (lambda x)^(2^(n-j))+lambda x^(2^j)=0.

Raise it to 2^j to obtain lambda x+lambda^(2^j)x^(2^(2j))=0. Since n is odd and gcd(j,n)=1, both gcd(2j,n)=1 and gcd(2^j+1,2^n-1)=1. For nonzero x the resulting exponent equation has precisely the solution (3); zero is the other radical element. Thus the alternating form has rank n-1.

If (2) holds, V is totally isotropic for C_(a w) for every nonzero w in V. Its dimension k=(n+1)/2 is maximal possible for such a form, so it must contain the radical. Otherwise its image in the nondegenerate quotient of dimension n-1 would be an isotropic subspace of dimension k>(n-1)/2. Therefore the following is a necessary condition for a shifted trace fall:

        (a w)^(-1/(2^j+1)) belongs to V
                         for every nonzero w in V.          (4)

The exponent means the inverse of 2^j+1 modulo 2^n-1, followed by negation. It is well-defined by the coprimality above. Since this power map is a permutation of K*, condition (4) makes its restriction a permutation of V\{0}. This is a substantial multiplicative closure constraint on an additive half-dimensional subspace.

Condition (4) is necessary, not asserted sufficient: containing the radical does not imply that a subspace is totally isotropic. Nor is the impossibility of (4) established for all trace-active V. A proposed infinite family could use failure of (4) to exclude these particular additional trace falls, but that would still not exclude other linear multipliers or subsequent quadratic feedback.

## 5. What this settles about the proposed Frobenius ladder

There is no automatic expanding ladder obtained merely by simultaneously Frobenius-twisting xG or yG; those coordinates stay in the old span. Off-diagonal shifts cannot even be field-valued quadratic consequences on a half-diagonal V. Scalar trace cancellations can occur only under the explicit trilinear condition (2), with the necessary inverse-power invariance (4) for coprime shifts.

These statements concern the independent-coordinate presentation before affine elimination of ell. The actual trace-slice quotient may admit additional cancellations modulo multiples of ell, and a complete W3 invariant must include those. The note therefore provides a concrete obstruction test and rules out an automatic closure-collapse argument, but does not certify a stable W3 space or an unbounded LFD family.
