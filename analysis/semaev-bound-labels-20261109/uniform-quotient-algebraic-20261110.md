# Uniform quotient attempt: obstruction to factorized x/y local models

2026-11-10. Source-only proof. No experiment, matrix search, build, or cloud job. The target remains a non-subfield fixed-m=2 family with caps D tending to infinity, full kernel closure, and an independent UNSAT or missing-consequence bridge. This note does not construct such a family. It rules out a concrete uniform quotient ansatz using the actual field tensor, even when the proposed quotient ranks grow without bound.

## 1. The attempted uniform ansatz

Let K=F_(2^n), z!=0, a6!=0, and let V have ordered F2-basis v1,...,vk. The original normalized system is the Boolean coordinate descent of

 F(X,Y)=(XY)²+zXY+z²(X+Y)²+a6,
 X=sum x_i v_i, Y=sum y_i v_i.

For D>=2, attempt a quotient C on Boolean polynomials of degree at most D whose monomial images factor across the two variable blocks:

 C(p(x) q(y))=C_x(p) tensor C_y(q)
                       whenever deg p+deg q<=D.             (1)

Here C_x,C_y are linear maps to arbitrary F2-vector spaces A_x,A_y; the spaces and their ranks may depend on n,D. Assume C(1)!=0 and C annihilates every original coordinate generator. The hoped-for further property is full low-degree kernel closure, which would make C an LFD separator.

Theorem below shows that if the Semaev system is UNSAT, these first two requirements already contradict (1). No choice of higher-degree images, growing rank, partial multiplication matrices, or closure proof can repair this factorized ansatz.

## 2. Extracting the actual multiplication tensor

Put u0=C_x(1), v0=C_y(1); both are nonzero. Let

 A_x^1=span(u0,C_x(x1),...,C_x(xk)),
 A_y^1=span(v0,C_y(y1),...,C_y(yk)).

For every linear functional phi on A_x^1 with phi(u0)=0, define

 u_phi=sum_i phi(C_x(x_i)) v_i in V.

These vectors form a subspace U of dimension dim(A_x^1)-1. Injectivity follows because the v_i are a basis and the listed quotient columns span A_x^1. Similarly obtain W subset V from functionals psi annihilating v0, with dimension dim(A_y^1)-1.

Apply phi tensor psi to the field-valued generator identity C(F)=0. Its affine terms disappear. Since the bilinear coefficient of x_i y_j is (v_i v_j)²+z v_i v_j, the exact result is

                   (u w)²+z u w=0 for all u in U,w in W.    (2)

No arbitrary MQ tensor has been substituted here. Equation (2) is forced by the actual field multiplication and its Artin-Schreier top.

The kernel of p->p²+zp is {0,z}. If U and W are both nonzero, multiplication by any nonzero u injects W into {0,z}, so dim W<=1; symmetrically dim U<=1. Therefore both dimensions are exactly one.

## 3. Both varying blocks force an actual four-point solution grid

Suppose dim U=dim W=1. Choose bases (u0,u1) and (v0,v1) of A_x^1 and A_y^1 and write

 C_x(x_i)=a_i u0+b_i u1,
 C_y(y_i)=c_i v0+d_i v1,

with binary coefficients. Let X0=sum a_i v_i, U1=sum b_i v_i, Y0=sum c_i v_i, W1=sum d_i v_i. The direction vectors U1,W1 are nonzero.

By (1), C(F) is exactly the coefficient vector of the Boolean two-bit polynomial

                 F(X0+s U1,Y0+t W1),  s,t in F2,

under the four independent tensors u0 tensor v0, u1 tensor v0, u0 tensor v1, u1 tensor v1. The original normalized F has only cross-block quadratic monomials and within-block linear terms, so this identification requires no unsupported claim about higher within-block moments.

Since C(F)=0, all four coefficients vanish. Thus all four ordered pairs in the affine grid

 {X0,X0+U1} times {Y0,Y0+W1}

are actual zeros in V times V. In particular the system is not UNSAT.

## 4. A constant block also forces an actual solution

If U=0, every C_x(x_i)=a_i u0 for a bit a_i. Set X0=sum a_i v_i. The tensor identity C(F)=0 then says

                      C_y(F(X0,Y))=0

coordinate by coordinate. For fixed X0, F(X0,Y) is affine in the Boolean y coordinates, because Frobenius Y² is linear. If this affine system were inconsistent, a constant linear combination of its rows would equal1, forcing C_y(1)=0, a contradiction. Hence it has a Boolean solution Y in V, giving an actual solution (X0,Y). The case W=0 is symmetric, including the case that both are zero.

This proves the theorem: every factorized map (1) with nonzero constant image and generator containment already implies an actual Semaev solution. Full multiplication closure was not needed.

## 5. Direct sums do not evade the obstruction

A direct sum of maps satisfying (1), with generator containment in every component, also cannot certify an UNSAT instance. Nonzero C(1) selects a component with a nonzero constant image, and that component supplies an actual solution by the theorem. Allowing cancellation between components rather than a direct sum changes the ansatz and must be analyzed anew; the theorem does not exclude such correlated constructions.

For a SAT instance known to have fewer than four ordered solutions, the two-varying-block case is also excluded. This observation does not by itself bound the rank contributed by higher-degree images in the remaining constant-block case, and no SAT LFD conclusion is inferred from it.

## 6. Consequence for the requested growing-cap construction

This removes a natural local-consistency construction in which independent x- and y-block pseudo-assignments are combined by tensor product. The failure already appears at input degree two, and holds for arbitrary V, including non-subfield half-diagonal choices. It is not a failure caused by finite computational capacity.

A successful uniform closed quotient for UNSAT inputs must correlate the x/y blocks already in their cross-degree-two images. It cannot preserve the product factorization (1), even if each block separately has an elaborate growing filtered representation.

The remaining required construction is still explicit: a family of correlated columns c_m and partial multiplication actions for all degrees through D(n) tending to infinity; exact annihilation of the field-tensor inputs; full low-degree kernel closure; and either an independent UNSAT proof, a named missing ideal consequence, or a solution-count bridge. The present note supplies none of those missing correlated constructions and does not establish unbounded LFD.

Local sources used: certificate-feasibility-contract.md (exact closed-kernel contract); algebraic-route.md and field-coupling-and-embedding-obstruction.md (field tensor restrictions). The factorized-quotient impossibility above is proved in full here and uses no external lower-bound theorem.
