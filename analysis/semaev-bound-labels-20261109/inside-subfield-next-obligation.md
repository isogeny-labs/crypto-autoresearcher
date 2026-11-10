# Inside-subfield normal form: concrete identities and the unresolved degree barrier

Date: 2026-11-09. Source-only derivation; no computational experiment, compilation or cloud work. This note does not establish bounded or unbounded LFD. It gives an exact alternate equation and degree-controlled finite-closure maps, then identifies why those maps do not yet decide LFD.

## 1. Setting and a useful alternate equation

Work over H=F_(2^k), with x,y unrestricted in H and z,a6 in H nonzero. The full-subfield case in a quadratic ambient extension has the same equation span as this H-descent, with redundant output coordinates removed. Write

 F(x,y)=(xy)^2+zxy+z²(x+y)²+a6,
 beta=sqrt(z), c=sqrt(a6)/z,
 r=sqrt(xy/z).

Square roots and multiplication by fixed field constants are F2-linear maps on coordinate vectors. Thus r is a vector of Boolean quadratics in (x,y), while r²+r+c is affine-linear in the Boolean coordinates of r.

The exact square-root identity is

 sqrt(F(x,y))/z = r²+r+x+y+c.                    (1)

Consequently every F-zero has x+y=r²+r+c. Define

 G(x,r)=x²+x(r²+r+c)+z r².                       (2)

This is a quadratic Boolean system in the x,r coordinates, despite its field-polynomial term x r²: field squaring is F2-linear. The following identities hold as H-valued Boolean polynomial functions:

 F(x, x+r²+r+c)=G(x,r)²+zG(x,r),                 (3)
 G(x, sqrt(xy/z))=x sqrt(F(x,y))/z.              (4)

For (3), put s=r²+r+c and P=x(x+s)=G+zr², substitute in P²+zP+z²s²+a6, and cancel z²c²=a6. For (4), use zr²=xy and (1).

## 2. Exact solution-set correspondence

Define maps

 tau:(x,r) -> (x,y=x+r²+r+c),
 sigma:(x,y) -> (x,r=sqrt(xy/z)).

If G=0, then F(tau)=0 by (3); if F=0, then G(sigma)=0 by (4). Their compositions are the identity on the respective zero sets:

 - sigma(tau(x,r)) has r-coordinate r+sqrt(G(x,r)/z), so it equals r on G=0;
 - tau(sigma(x,y)) has y-coordinate y+sqrt(F(x,y))/z, so it equals y on F=0.

Thus this is a bijection on the complete finite zero sets, including exceptional selector values. No division by a variable occurs in these two maps. The forward map tau is affine over F2, while sigma has Boolean degree two. This supplies a concrete normal form with an affine forward map and quadratic inverse, not a rational-parametrization assumption.

The original zero set is always nonempty: x=0,y=sqrt(a6)/z=c. Its image under sigma is x=0,r=0, which visibly solves G.

## 3. What the identities prove about bounded-degree closures

Use coordinate descent and the full Boolean closure W_D.

Pulling original F-polynomials back by tau is affine substitution. Identity (3) says every coordinate of F(tau) is an F2-linear combination of coordinates of G, since field squaring and fixed z-multiplication are F2-linear on output coordinates. Therefore

 tau^*(W_D(F)) subset W_D(G), D>=2.             (5)

Pulling G back by sigma substitutes quadratic coordinate polynomials for r. Identity (4) puts every initial coordinate of G(sigma) in W_3(F). A degree-at-most-D derivation in G can be substituted line by line; multiplication by a quadratic substituted variable can be implemented by at most two ordinary variable multiplications, and no substituted line or intermediate product exceeds degree 2D. Hence, for D>=2,

 sigma^*(W_D(G)) subset W_(2D)(F).              (6)

The D>=2 restriction in (5) ensures every quadratic input row is eligible; equation-span equality alone does not justify the low caps. Both are finite-degree inclusion statements. They also transport an explicit derivation/certificate if one is supplied. They do **not** by themselves show equal LFD, nor transfer a uniform LFD bound from G to F.

The obstruction is precise. A uniform d_LFD(G)<=C places a general ideal element of degree e into W_max(C,e)(G). Formula (6) only places its pullback into W_(2max(C,e))(F). LFD requires max(C',degree of the desired original polynomial), not twice that degree. The compositions introduce multiples of the quadratic coordinate errors in (1), and correcting those errors can also double the degree of an arbitrary high-degree polynomial. Without a further degree-compatible argument, the factor-two closure simulation is insufficient to establish a constant LFD for the satisfiable original family.

This issue would be less severe for refutations, whose output has degree zero, but these inside-H systems are always satisfiable. One must not use an unsatisfiable refutation-degree transfer theorem as a substitute.

## 4. A concrete rational/trace attempt and its denominator

For the open subset s=r²+r+c !=0, set

 t=x/s, q=beta r/s, u=t+q=(x+beta r)/s.

Equation G=0 becomes t²+t=q², and therefore

 u²+u=beta r/(r²+r+c).                          (7)

This is an Artin–Schreier normal form. Its finite-field consistency condition is

 Tr_(H/F2)(beta r/(r²+r+c))=0.                   (8)

For each allowed r with nonzero denominator, (7) gives two u-values and hence two x-values. The exceptional r-values with s=0 are at most two and must be retained separately; there G reduces to x²+zr²=0 and gives x=beta r.

The denominator r²+r+c has derivative 1 and, because c!=0, neither root is zero. Over an algebraic closure, the right side of (7) has two distinct simple poles without numerator cancellation. The standard Artin–Schreier genus formula gives genus one: each simple pole contributes two to the different, so 2g-2=-4+2+2=0. Thus the apparent quotient parametrization in r does not turn this into a rational curve. A rational parameterization of the whole curve cannot simply be assumed.

For odd k, applying half-trace to (7) describes u from its right-hand side whenever (8) holds. Half-trace is F2-linear, but evaluation of the right-hand side requires inversion of s. Its polynomial function on H^* is s^(2^k-2), whose binary-exponent weight is k-1. This observation exposes a potential degree cost; it is not a lower bound on LFD, because the ideal may admit completely different bounded-degree derivations.

Introducing an inverse variable v with s v=1 gives a quadratic extension system in the Boolean coordinates of r,v. That can help an algorithm, but a constant-degree proof for the extension would not automatically be a constant-degree proof for the original system: the inverse variable has no exhibited bounded-degree expression in the original coordinates. Its elimination is the unresolved obligation.

## 5. The exact missing identities for a constant-degree route

A proof of a uniform bound needs more than a bounded-degree model of the same solution set. One concrete sufficient route would be a constant C and a degree-compatible normal-form argument showing that, for every k, every original ideal polynomial f has a derivation in degree max(C,deg f). Equations (1)–(6) supply useful low-degree identities but do not establish that all high-degree reductions can be performed without the degree doubling identified in Section 3.

For the trace route, an alternative sufficient step would be a bounded-degree elimination theorem for the inverse extension s v=1, including the s=0 exceptional fibres. Merely writing v=s^(2^k-2), or adding an unconstrained rational expression for v, does not meet this condition.

For a lower-bound route, one must instead construct a full-closure obstruction surviving all identities (1)–(4). High degree of the explicit inversion formula or of the rational-trace condition (8) is not enough: they are descriptions of one computation, not universal obstructions to all bounded-degree derivations.

## 6. Status and next concrete check

Positive progress: exact alternate quadratic system G, an affine/quadratic pair of mutually inverse maps on finite zero sets, controlled closure inclusions, and a specific Artin–Schreier denominator explaining why a naive rational or half-trace solution does not yet prove bounded LFD.

Unresolved: a degree-compatible simulation eliminating the quadratic inverse map, or a full-closure lower-bound certificate family for G/F. The new identities should be checked against any proposed quotient-map family: the map must annihilate the original equations and all low-degree consequences generated by these identities, not only the initial Macaulay rows.

Sources: original dossier §§0–2 for closure conventions and coefficientwise Frobenius; `fibre-refinement.md` for the corrected witness and fixed-s factorization. The Artin–Schreier genus assertion uses the classical simple-pole genus formula; no new external theorem is claimed or novelty label assigned. All displayed algebraic identities are derived explicitly above and are independently reviewable without experiments.
