# Fixed-s fibre refinement and the remaining subfield case

Date: 2026-11-09. Source-only proof work. No experiment, compilation or fresh certificate replay. New statements below are derived and require independent review. Neither a universal constant LFD bound nor unboundedness is proved.

## 1. Correction to the original subfield witness

The earlier `algebraic-route.md` correctly states that the full-subfield case z,a6 in H is satisfiable, but its proposed diagonal witness is wrong. It omitted zxy: on x=y the equation is x^4+zx²+a6=0, not x^4+a6=0.

A correct universal witness is

x=0, y=sqrt(a6)/z in H,

because S3(0,y,z)=z²y²+a6=0. The historical note and its archived bytes are retained; this is the explicit correction. The earlier z outside H proof did not use that diagonal witness and is unaffected.

## 2. Exact kernel classification for arbitrary V

Put s=x+y in V. Direct expansion gives

S3(x,x+s,z)=A_s(x)+z²s²+a6,
A_s(X)=X^4+(s²+z)X²+zsX
      =X(X+s)(X²+sX+z).

The map A_s:K->K is F2-linear. Thus every fixed-s solution set in V is either empty or an affine translate of ker(A_s|V).

For s!=0, the kernel always contains {0,s}. It has dimension two precisely when there is r in V satisfying r²+s r=z. In that case the four kernel elements are {0,s,r,r+s}; otherwise the kernel in V has dimension one. The extra roots cannot coincide with 0 or s because z!=0.

For s=0, A_0(X)=X²(X²+z), so ker(A_0|V) is {0}, or {0,sqrt(z)} when sqrt(z) belongs to V. Its dimension is at most one.

Equivalently, a dimension-two fibre is possible only at a nonzero sum s=u+v of distinct u,v in V with uv=z. This is a concrete factor-base/product condition; it is not inferred from ambient field trace alone. In the full field, roots of r²+s r=z exist exactly when Tr_K(z/s²)=0, but membership in V must still be checked.

Consequences: every fibre has at most four points. If z has no factorization uv with distinct u,v in V, every fibre has at most two points. This is a statement about the linear operator's kernel; actual nonempty fibres still require the inhomogeneous right side z²s²+a6 to belong to its image.

## 3. General affine-fibre closure bound

Here is a useful degree-controlled upper-bound lemma, rather than an elimination-degree heuristic.

Let a quadratic Boolean system have h selector coordinates c. On every fixed selector assignment sigma, its remaining equations are affine-linear and their common zero set is either empty or an affine space of dimension at most r. Then

 d_LFD <= max(h+2,h+r+1).

In particular r<=2 gives h+3, and r<=1 gives h+2. If the selectors have independent affine constraints already derivable in W2, first eliminate those constraints and use the number h of remaining selector coordinates.

**Proof sketch with closure accounting.** For each sigma let e_sigma be its degree-h Boolean indicator. For every original generator f, e_sigma f equals e_sigma f|sigma and belongs to W_(h+2), by multiplying the quadratic generator by the factors of e_sigma. Thus gated affine consequences of the restricted system belong to W_(h+2), including e_sigma itself for an empty fibre.

On a nonempty fibre choose r_sigma<=r free Boolean affine coordinates. A basis of functions on that fibre consists of their squarefree monomials. Their gated lifts have degree at most h+r. Let U span all these gated monomials, omitting empty fibres; dim U equals the number of solutions because disjoint indicators separate fibres and the monomials span all functions on each affine fibre.

Set D=max(h+2,h+r+1). Multiplication of a gated basis element by any original variable has degree at most h+r+1<=D. Its reduction to gated free-coordinate monomials follows from the gated affine relations, using cofactors of degree at most r; every step remains in W_D. The same is immediate for multiplication by selectors. The constant 1 reduces to the sum of the nonempty-fibre indicators, since empty indicators are in W_D.

By induction on monomial degree, every monomial of degree at most D is congruent modulo W_D to an element of U. Thus codim W_D is at most #solutions. It is also at least #solutions because all members of W_D vanish on the solution set and the gated basis realizes every function on it. Consequently W_D contains all vanishing polynomials of degree at most D.

Moreover the quotient algebra is spanned by polynomials of degree at most D-1 (the gated basis), so its degree filtration has stabilized by D-1. For a degree-compatible order this bounds the reduced Gröbner-basis degree by D: every degree-D monomial has a lower-degree representative, and no minimal leading generator can have higher degree. All those basis polynomials belong to W_D. Degree-compatible standard representations then put every ideal element f into V_(F,max(D,deg f)), proving the stated LFD bound. For an empty solution set the indicator sum derives 1 within the same budget.

The key difference from naive fibre interpolation is the stable normal-form space of degree <=D-1. Directly multiplying an arbitrary high-degree vanisher by each degree-h indicator would not prove a constant LFD bound and is not the argument above.

## 4. Applying the bound to the Semaev fibres

The fixed-s Semaev equations are affine-linear in x, so the lemma applies with at most k selectors and r<=2:

 d_LFD <= k+3.

This is an all-instance statement, including satisfiable systems, subject to the closure lemma's independent review. The dossier's k+2 bound for unsatisfiable systems remains sharper in that case.

There is a systematic one-degree improvement whenever the trace relation gives a nonconstant affine constraint on s. Let alpha=a6/z². The known linear relation is

 Tr_K(s)+Tr_K(alpha)=0.

If Tr_K restricted to V is nonzero, eliminate one selector coordinate within W2. Then h=k-1 and

 d_LFD <= k+2.

If additionally there is no distinct-pair product uv=z inside V, so all fibres have dimension at most one, the same argument gives d_LFD<=k+1. Without the trace reduction but with that product exclusion it gives k+2.

If V is contained in ker Tr_K and Tr_K(alpha)=1, the system is immediately inconsistent. If V is contained in ker Tr_K and Tr_K(alpha)=0, this particular trace relation is identically zero and gives no selector reduction. It must not be counted as a nontrivial equation.

## 5. Remaining full-subfield case z,a6 in H

Take K quadratic over H=V and z,a6 in H, z!=0. The K-descent is just the H-descent plus redundant linear-combination/zero output equations. The valid witness in Section 1 proves satisfiability for every such parameter pair.

Absolute trace from K vanishes on H, so the ambient trace relation is identically zero. However, because the entire equation has coefficients in H, its descent over H has the separate relation

 Tr_(H/F2)(s)+Tr_(H/F2)(a6/z²)=0.

Trace_H is a nonzero F2-linear map on the entire H, even when k is even. Thus one selector coordinate can be eliminated. Section 4, using the H-valued descent, gives the all-instance bound

 d_LFD <= k+2.

No constant bound for this remaining case is established. In contrast to the z outside H case, the trace constraint leaves 2^(k-1) possible selector values rather than at most two. Fibres have at most four points, but their union can have order 2^k points; the earlier 'at most four total solutions' argument is unavailable.

The factorization condition does not resolve this: in the full subfield H, u v=z has many solutions as u varies, so dimension-two kernels occur for many sums u+v. Their existence does not itself give a lower bound or imply high LFD. Nor does the existence of the easy witness (0,sqrt(a6)/z) control the vanishing ideal of all other solutions.

## 6. Consequences for the research target

The precise unresolved region is now clearer. Full-subfield bases with z outside H have constant LFD<=3 by the previous note. Full-subfield bases with z,a6 inside H are always satisfiable and have the derived linear upper bound k+2, but neither a constant upper bound nor a growing lower bound was obtained here. Arbitrary V may have many more complex fibre-consistency patterns, although every individual fibre remains affine of dimension at most two.

A growing lower-bound construction must therefore exploit the interaction among many selector fibres, not hardness within a fixed fibre. Conversely, a constant upper-bound theorem must find bounded-degree relations tying those fibres together; solving each affine fibre separately only gives the h-dependent indicator proof.

## 7. Coordinate transformations do not close the remaining gap

Replacing field bases, applying invertible affine Boolean coordinate changes, or applying a field automorphism preserves the relevant closure degree. These transformations can simplify an explicit instance but cannot amplify a fixed lower bound. Frobenius sends (V,z,a6) to their simultaneous conjugates, preserving the instance's proof-degree behavior.

Even with V=H, replacing x,y by z times new variables does not normalize the target to 1 while preserving the normalized S3 family: after division by z^4,

 S3(zX,zY,z)/z^4=(XY+X+Y)^2+z^(-1)XY+a6/z^4.

The cubic-coefficient normalization changes. Such a substitution is a valid degree-preserving coordinate change for the same instance, but treating its result as S3(X,Y,1) without retaining the z^(-1) factor changes the system. No constant upper bound for all inside-H targets follows from a special z=1 calculation alone.
