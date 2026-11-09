# Modular correction and controlled quotient-variable transport

2026-11-09. Pure symbolic work; no computations, instance search, build, or cloud jobs. The no-wrap uniform bound does not automatically extend to this setting.

Let P(T) be an irreducible degree-n polynomial, K=F2[T]/P, V=span(1,t,...,t^r), with r<n, and fix z=a6=1. Use Boolean coefficient polynomials x,y of degree<=r, p=xy, s=x+y+1, and

                 F(T)=p²+p+s².

Write unique polynomial division F=P Q+R, deg R<n. The actual descended system is the coefficient system R=0. The no-wrap argument instead imposes F=0. When n<=4r the difference is the quotient polynomial Q, of degree at most4r-n. All its coefficients are Boolean polynomials of degree at most two: polynomial division is linear on coefficients, and the coefficients of F have Boolean degree at most two.

## Exact failures of the polynomial identities

At a modular solution,

                 p²+p+s²=P Q,                               (1)
                 p'=P' Q+P Q'.                              (2)

Thus the no-wrap inference p'=0, or that p is a polynomial square, is invalid. In characteristic two P is separable, so P' is invertible modulo P. Equation (2) gives

                 Q = (P')^(-1) p' mod P                     (3)

whenever deg Q<n. In particular (3) applies on the half diagonal n=2r+1, since deg Q<=2r-1. It is an exact necessary identity, not a new low-degree input. It exhibits how odd-index product coefficients feed the modular correction.

The no-wrap dyadic telescoping identity also acquires an explicit error. Let f_j be the formal coefficients of F and let d be odd, 2^t d<=r<2^(t+1)d. Define the coefficient functional

 C_d(G)=G_d+sum_(i=0)^(t+1) G_(2^(i+1)d).

The formal identity C_d(F)=sum_(i=0)^t s_(2^i d)=L_d always holds. At modular solutions it says

                         L_d=C_d(P Q),                       (4)

rather than L_d=0. The right side is linear in the quotient coefficients but quadratic in the original Boolean coordinates. Therefore neither the former affine chains nor their first-fall witness survive unchanged.

Likewise, a leading-coefficient comparison in F no longer forces the highest x or y coefficient to vanish: the highest coefficient can equal the corresponding coefficient of P Q. The polynomial argument that both positive degrees are impossible is specifically an argument for Q=0, not for R=0.

## A half-diagonal linear section that avoids false polynomial square roots

Suppose n=2r+1. Since Tr(1)=1 and 1 lies in V, S=V intersect ker Tr has dimension r. The trace of the original field equation A(p)+s²=0 is Tr(s)=0. On K0=ker Tr the map A(w)=w²+w is a linear bijection: its full kernel is F2, which meets K0 trivially, and its image is K0. Let J denote this inverse on K0.

On the trace slice s in S, the original system is exactly equivalent to

             xy=J(s)²+epsilon,    epsilon in F2.             (5)

Indeed A(J(s)²)=s²; the two preimages under A differ by1. The bit is epsilon=Tr(xy), since J(s) has trace zero. Thus J(s) is linear in the original coordinates, while epsilon is a quadratic definitional bit. This is a field-linear section, not the bounded-degree-in-T polynomial q from the no-wrap proof. Its coefficient support can extend throughout degree n-1. Consequently the previous highest-T-degree selectors have no justified analogue.

Equation (5), together with the trace slice, gives a concrete presentation of the half-diagonal problem: a restricted field multiplication tensor equals a prescribed linear map plus one bit. It preserves the actual multiplication tensor and introduces no arbitrary MQ coefficients.

## Quotient variables have a uniform factor-two refutation transport

Introduce one Boolean auxiliary variable z_j for each coefficient of Q, and impose the coefficient equations

                       F(T)+P(T) Z(T)=0,                    (6)

with deg Z<=4r-n. Call this extended system G, and call the original remainder system R. All equations in both lists have degree at most two. Linear polynomial division of (6) shows that its row span is exactly the span of the remainder equations and the definitional equations

                       z_j+h_j(x,y)=0,                      (7)

where h_j is the jth quotient coefficient of F. In particular (6) forces the unique intended quotient; the auxiliary bits are not unconstrained witnesses.

Let sigma substitute z_j=h_j. Each h_j has Boolean degree at most two. For strict caps D>=2,

 W_D(R) subset W_D(G),
 sigma(W_D(G)) subset W_(2D)(R).                              (8)

The first inclusion uses the constant row combinations obtained by taking remainders. For the second, substitute a derivation. Every input equation becomes a constant row combination of remainder equations or zero, still at degree at most two. An original-variable multiplication increases substituted degree by at most one. Multiplication by an auxiliary variable becomes multiplication by h_j, a sum of monomials of degree at most two; expanding and multiplying each variable successively stays within cap2D. The bound does not depend on the number of quotient variables.

For unsatisfiable instances whose refutation degrees are compared at caps at least two, (8) yields

                     max(2,e_G) <= max(2,e_R) <= 2 max(2,e_G).             (9)

Thus a growing refutation lower bound in the extended system genuinely transfers to the original; quotient-variable count by itself does not incur a growing multiplicative distortion. Conversely a growing original refutation degree forces growth in the extended system up to factor two. Exact degrees and additive-constant transport are not asserted.

For SAT systems, (8) alone is not an unrestricted LFD equivalence: substituting a tested polynomial can change its degree. One may use the known affine ideal or a separately proved bounded-solution-count transport, but must state that extra hypothesis. The many quotient definitions are not a license to ignore this degree-of-target issue.

## Concrete next lower-bound object

The half-diagonal extension has at most2r quotient bits and exposes the exact corrected chain relations (4). A useful lower-bound construction must retain those corrections and the definitions (7), or work directly with (5). A hard UNSAT subfamily of this exact quadratic extension would transfer with the uniform factor-two bound (9). Setting every quotient bit to zero instead recovers the bounded no-wrap system and therefore cannot supply a growing obstruction by itself.

The new usable lemmas are the exact error term (4), the half-diagonal single-bit linear-section form (5), and the auxiliary-count-independent refutation transport (8)-(9). No growing lower bound is claimed here.
