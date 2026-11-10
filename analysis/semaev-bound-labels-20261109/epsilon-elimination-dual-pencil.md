# Eliminating epsilon and an exact one-variable refutation criterion

2026-11-09. Pure proof, no execution. This note eliminates the auxiliary bit and gives an explicit criterion for a degree-three refutation in the original trace-slice system. It does not assume that every refutation has this form.

Let K have odd degree n=2r+1, dim V=r+1, W=V intersect ker Tr, and choose e in V with Tr(e)=1. As before use independent x in V,t in W, and write

 G=xt+D(x)+H(t)+g+epsilon,
 D(x)=x²+ex, H(t)=J(t)², g=J(e+1)².

Here J is the inverse of w²+w on K0=ker Tr, so H(t) and g have trace zero.

## Exact elimination in the original system

Taking trace gives

 epsilon=q(x,t)=Tr(xt)+Tr((1+e)x).

Let pi(z)=z+Tr(z). Substitution yields the epsilon-free system

 F_t(x)=pi(x²+(t+e)x)+H(t)+g=0.                              (1)

Its outputs lie in K0 and it is a constant row transformation of the original equations after the trace affine relation has been eliminated. For each fixed t this is an affine linear system in x.

The mandatory quadratic auxiliary consequences xG need not remain quadratic under this substitution: epsilon*x becomes x*q(x,t), generally cubic. Hence the pure-block lower dimension in the auxiliary presentation is not automatically a pure quadratic block of the original presentation. Direct original cap-three consequences must respect this distinction.

## One-variable dual separators

Assume the original system is UNSAT. For every t in W, the target H(t)+g is outside the image of the linear map

 S_t:V -> K0,       S_t(x)=pi(x²+(t+e)x).

The trace pairing restricted to K0 is nondegenerate when n is odd: its orthogonal complement in K is F2, and K0 meets F2 trivially. Therefore there exists lambda(t) in K0 satisfying

 lambda(t)^(2^(n-1))+(t+e)lambda(t) in V_perp,                (2)
 Tr(lambda(t)(H(t)+g))=1.                                   (3)

These conditions are exactly separation of the target from the image: for trace-zero lambda, pairing with pi does not change the pairing, and Tr(lambda x²)=Tr(lambda^(2^(n-1))x).

If a Boolean polynomial map lambda:W->K0 of degree at most c satisfies (2)-(3) identically, then

                        Tr(lambda(t) F_t(x))=1              (4)

is a literal original-system refutation. Multiplying the quadratic generators by the coefficient polynomials of lambda costs at most c+2 in strict closure. In particular an affine lambda yields an original degree-three refutation. No auxiliary substitution or growing gate count is hidden in this claim.

Arbitrary pointwise separators can always be interpolated with degree at most r, recovering a cap r+2 bound. The useful question is whether low-degree separators can be constructed for a specified family.

## Constant separators are excluded by a precise field condition

If lambda(t)=a is constant, subtracting (2) at t and at0 forces aW subset V_perp, that is a in C=(VW)_perp. The previous note proves dim C<=1. Thus when span(VW)=K, no constant separator exists. This excludes this particular cap-two certificate form; it is not by itself a characterization of all W2 refutations.

## Explicit necessary and sufficient equations for affine separators

Write lambda(t)=a+L(t), where a in K0 and L:W->K0 is F2-linear. Define B_L(t,u)=tL(u)+uL(t). Then (2) holds identically exactly when all of the following hold:

 a^(2^(n-1))+ea in V_perp;                                  (5)
 B_L(W,W) subset V_perp;                                    (6)
 (L(t))^(2^(n-1))+eL(t)+at+tL(t) in V_perp for every t in W. (7)

In (7), once (6) holds, the class tL(t) modulo V_perp is linear, so checking a basis of W suffices. Condition (5) is the constant term; polarization gives (6); (7) gives the remaining linear terms.

Similarly (3) holds identically exactly when

 Tr(ag)=1;                                                  (8)
 Tr(L(t)H(u)+L(u)H(t))=0 for every t,u in W;                 (9)
 Tr(aH(t)+gL(t)+L(t)H(t))=0 for every t in W.                (10)

After (9), the last expression is linear in t, so again a basis suffices. These are explicit linear conditions on a and the coefficients of L: H and field multiplication are fixed. Thus (5)-(10) give a concrete field-specific linear feasibility problem equivalent to an affine t-only refutation certificate, rather than a generic MQ heuristic or determinant-degree argument.

Condition (6) is exactly the t-side quadratic-feedback condition found earlier. The additional equations encode epsilon elimination, the x-side annihilation, and the nonzero constant residual. They explain which part of that feedback actually provides a direct original cap-three refutation.

## Limits and next construction

Solving (5)-(10) symbolically for an explicit infinite UNSAT V family would prove a uniform original cap-three bound for that family. Proving this affine system inconsistent excludes affine t-only dual certificates, but not all W3 refutations: arbitrary closure may use x-dependent multipliers and repeated quadratic falls.

No solution or impossibility of (5)-(10) for the entire existential trace-active UNSAT family is claimed. The new reduction is the exact elimination (1), a direct refutation identity (4), and a complete affine-separator criterion that respects the actual multiplication tensor and all modular corrections.
