# A symbolic full-W2 obstruction at r=6, and its restriction extension

2026-11-09. Source-only proof prompted by the parent's frozen r=1,...,12 W2 campaign. The saved r6-result.json reports affine dimension5, rank71, and verified lower bound3. This note independently explains those exact numbers algebraically. It runs no checker or new computation.

## Reduction by five available affine consequences

Use the no-wrap family n>4r, V=span(1,t,...,t^r), z=a6=1. For r=6 the established affine elimination gives

 y=x+1+A(q),  A(p)=p²+p,
 E=A(x)+x A(q)+q²,
 deg x<=6, q=q1 T+q2 T²+q3 T³.

This eliminates four original coordinates: the constant trace relation and three positive-index dyadic chain relations. The further available affine consequence E(1)=q(1)=q1+q2+q3 removes a fifth coordinate. Put

 q=b(T+T³)+c(T²+T³).

The remaining independent Boolean coordinates are x0,...,x6,b,c: nine coordinates. These are affine substitutions, and their corrections to original quadratic equations lie in the degree-two span of multiples of the five known affine relations.

## Exact quadratic-top rank from a polynomial gcd

Define

 h1=A(T+T³)=T+T²+T³+T6,
 h2=A(T²+T³)=T²+T³+T4+T6.

The coefficient vector attached to the quadratic Boolean monomial x_i b in E is T^i h1; that attached to x_i c is T^i h2, for 0<=i<=6. These 14 Boolean monomials are distinct. The other terms A(x)+q² are linear.

We have gcd(h1,h2)=T(T+1). Indeed both vanish at0,1;

 h1+h2=T+T4=T(T+1)(T²+T+1),

whose three factors are squarefree and pairwise coprime. Modulo T²+T+1, h1 equals1, so the third factor is absent from the gcd.

Let P_6 denote polynomials of degree at most6. Each space h_i P_6 has dimension7. Their intersection consists exactly of multiples of lcm(h1,h2), which has degree10, of total degree at most12. This intersection therefore has dimension3. Hence

 dim(h1 P_6+h2 P_6)=7+7-3=11.

The sum is precisely the 11-dimensional space of polynomials of degree at most12 vanishing at0 and1. This proves the quadratic-top rank11 without a matrix computation or a generic-rank assumption.

## No surviving affine consequence: exact strict closure

E has zero constant coefficient. On its twelve positive coefficient rows, the only functional annihilating all quadratic tops is the sum of the coefficient rows, because the top span is the full even-parity subspace on indices1,...,12. That sum is E(1)=0 identically after q(1)=0. It produces no nonzero affine polynomial.

Therefore the span Q of the reduced E coordinate equations has dimension11 and

                 Q intersect B_(<=1) = {0}.

At strict cap two, only consequences of degree at most one may be multiplied by a variable. There are none in Q. Thus Q is already the full reduced W2, not merely the initial Macaulay span. In particular every nonzero coordinate linear, including x1, is absent from W2. The exact two-point zero set requires x1=0 in its ideal. Consequently the original no-wrap r=6 system has LFD at least3.

To transfer the stable statement back, let L be the span of the five already derived affine relations. All degree-two elements of their affine ideal lie in original W2: affine elimination expresses them as linear multiples of L. Quotienting by L maps original degree-two equations onto Q. Since Q contains no affine consequence, no additional original affine consequence exists beyond L; all permitted cap-two multiplications are already accounted for. This proves full stability in the original coordinates as well.

## Exact dimensions agree with the saved certificate

The original Boolean degree-at-most-two space has dimension 1+14+C(14,2)=106. After the five independent affine eliminations it has dimension 1+9+C(9,2)=46. The affine-ideal kernel has dimension60; adding Q gives

 rank W2 =60+11=71,       codim W2=35.

The affine part is exactly five-dimensional. These are precisely the reported r6 dimensions, now derived symbolically.

## Infinite constant lower bound by restriction

For any r>=6, set all x_i,y_i with i>6 to zero. In the no-wrap coefficient presentation the system restricts exactly to the r=6 system. Restriction sends any strict degree-two derivation to a strict degree-two derivation of the restricted system (or to zero).

Every larger member still has exactly the two constant solutions, so x1 belongs to its ideal. If x1 were in its W2, restriction would put x1 into W2 of the r=6 system, a contradiction. Hence

 d_LFD(F_r)>=3 for every r>=6 and every field degree n>4r.

This extends the finite campaign's lower bound to an explicit infinite family. It is a constant lower bound, not a growing one. The factor-base dimension is r+1; these parameters do not satisfy the odd-diagonal condition dim V=ceil(n/2).

## A short upper bound for the first obstruction

The r=6 affine-reduced system has only two q-coordinates b,c. Fixing both makes E linear in x. For each nonzero q the restricted system is inconsistent, since the original polynomial family has only constant solutions. For q=0 its affine solution set is exactly x=x0 constant. Each restricted affine ideal therefore has linear derivations. Lifting through the two Boolean selector coordinates, while allowing the original quadratic-generator threshold, gives all required affine ideal generators at cap at most2+2=4. Thus the symbolic bracket is

                     3 <= d_LFD(F_6) <=4.

The note does not decide whether degree three suffices. For growing lower bounds, the next obstruction must concern saturated W3 or higher; the rank71 computation alone cannot supply it.
