# Safe finite-selector bounds and the missing coordinate-transfer bridge

2026-11-09. Pure proof and labeling contract; no dataset replay, search, solver, build, or cloud execution. Scope: the actual Boolean equations obtained by substituting finite selector maps into normalized m=2 S3, not the system on their linear span.

## Exact domain and reconstruction

Let X:{0,1}^a->K and Y:{0,1}^b->K be fully specified maps, with N=a+b selector bits. Maps may be nonlinear, noninjective, or represented by literal lookup tables. With z,a6 fixed, the equations are the coordinate bits of

    (X Y)^2 + z X Y + z^2(X^2+Y^2) + a6.

All operations are in the verified binary field K, and Boolean polynomial representation is the unique algebraic normal form (ANF). Each coordinate of X and Y has degree at most a and b respectively; if their actual maximum degrees are s_X,s_Y, the descended equations have degree at most s_X+s_Y (and at most N). Squaring in K applies Frobenius to coefficient vectors and does not double Boolean ANF degree. Replacing these maps by bases of their field-vector spans changes the Boolean system, number of code assignments, filtration, and potentially its LFD.

Every code must have defined semantics. A rejected/invalid code must be represented by explicit constraints in the actual Boolean system, or incorporated into a fully specified map according to producer semantics. Silently dropping codes while labeling the unconstrained substituted equations is incorrect. If the producer uses shared bits, additional constraints, or auxiliary variables, reconstruct that exact system and use its actual Boolean variable count rather than assuming two independent blocks.

## Universal LFD upper bound

**Lemma.** Every finite Boolean polynomial system in N variables has last fall degree at most N+1, in the strict multiplication-cap convention used here.

Proof: every Boolean polynomial has degree at most N. At cap N+1, every input is available and every derived polynomial can legally be multiplied by any variable. Thus W_(N+1) is an ideal of the entire Boolean ring containing the inputs; by minimality it equals their ideal I. For every f in I, deg f<=N, so f belongs to W_max(N+1,deg f). This proves the bound. The proof includes satisfiable and unsatisfiable systems, arbitrary input degrees, repeated selector codes, and nonlinear maps. It does not assert that cap N always suffices under the strict convention.

For an exactly reconstructed legacy selector system with actual N<=12, this gives the unconditional label LFD<=N+1<=13. It is a theorem-derived finite-dimensional bound, not a measured exact LFD. It needs no no-wrap recognition or factor-base span theorem. No lower bound, first fall degree, or exact LFD follows from this label alone.

## Exact finite enumeration and what it counts

Enumerating all 2^N Boolean code assignments and evaluating the exact equations gives the exact number S_code of solutions. For N<=12 this means at most 4096 assignments. This is a specification of a finite procedure, not a report that it has been run.

If one evaluation uses L binary arithmetic operations on the verified field/map representation, enumeration uses O(2^N L) such operations plus counter/output costs. For table maps and ordinary schoolbook polynomial field multiplication, a conservative direct evaluation has polynomial cost in n; the literal tables and field validation have their own input costs. With streaming evaluation, working space is the map/equation representation plus O(n+N) temporary bits. Listing all code solutions adds Omega(S_code N) output bits. Converting to field coordinates and deduplicating requires separately accounted output/storage or an explicitly described exact deduplication procedure.

Repeated codes matter. For independent selector blocks define mu_X(u)=#{alpha:X(alpha)=u} and mu_Y(v)=#{beta:Y(beta)=v}. Then

    S_code = sum_{u,v: S3(u,v,z)=0} mu_X(u) mu_Y(v),

whereas S_pairs counts each distinct accepted field pair once. Neither is interchangeable with rational curve-point lifts or a count over the span of the map images. With code-validity constraints, use the constrained assignment count and the corresponding constrained multiplicities; coupled constraints need not factor as the product above.

An exact count is useful for a separately verified full-closure certificate: the Boolean coordinate ring has dimension S_code, so exact codimension of W_D greater than S_code proves a missing ideal consequence and a lower bound beyond D (with the study's stated cap/degree assumptions). The count itself supplies no such nonmembership certificate. UNSAT is exactly S_code=0; membership/nonmembership of 1 must still be established at the claimed cap to infer a degree lower bound.

## Transport through nonlinear coordinate maps

Let the source Boolean ring be B_M in vector-space coordinates u, the target ring B_N in selector bits v, and p:{0,1}^N->{0,1}^M a polynomial coordinate map of degree at most s. Substitution psi(f)=f(p(v)) has degree at most s deg f. A source cap-D derivation transports to target cap sD when the substituted source inputs are target inputs, or more generally cap max(c,sD) if substituted inputs already have target derivations at cap c. This is a derivation-transport statement, not by itself an LFD upper bound for the entire target ideal.

There are two independent obstacles:

1. An injective p can have a proper image. The source system F on the full vector space must then be strengthened by equations H defining image(p) before a selector-ideal consequence can be lifted back. A bound for F alone does not supply a bound for F+H.
2. Even with a polynomial inverse q on the image, a target consequence of degree e lifts to degree at most t e when deg q<=t. Transport can yield cap s max(d,t e), which is not automatically max(sd,e). This target-degree issue cannot be discarded when asserting an LFD bound.

Here is a sufficient precise bridge. Assume:

* p is injective, H generates its image ideal, and q is a specified inverse on image(p), with deg p<=s and deg q<=t;
* the source system F+H has a proved LFD upper bound d;
* the actual target equations are G=psi(F), and psi(H)=0;
* a degree-compatible Groebner basis J of I(G), or another ideal generating family with degree-nonincreasing reductions, has maximum degree L.

For h in J, h(q(u)) vanishes on solutions of F+H and hence lies in its ideal: Boolean ideals are exactly vanishing ideals on their finite solution sets. Its degree is at most tL, so it is source-derivable at cap max(d,tL). Substitution gives h(q(p(v)))=h(v), with target cap

    D0 = s max(d,tL).

All members of J are therefore in W_D0(G). Degree-nonincreasing reduction by J derives any target ideal polynomial f at cap max(D0,deg f). This proves **LFD(G)<=D0**. One may take the smaller of this bound and N+1. Degenerate zero-variable/constant-map cases can use the universal bound rather than interpreting s=0 or t=0 formulas.

This bridge is useful, for example, when the target solution set is a nonempty affine Boolean subspace and its exact affine vanishing ideal is known: one may take L=1. If in addition the source image-constrained system has bound d, then LFD(G)<=s max(d,t). For a Boolean affine coordinate isomorphism, s=t=1, image is the whole source space, and the familiar filtration-preserving transfer is recovered. The nonempty affine hypothesis matters; for UNSAT the vanishing ideal is generated by 1 and a separate transported refutation is the direct bridge.

For nonlinear bijections of equal-size Boolean cubes, H is unnecessary, but the inverse-degree/target-reduction obligation remains. For noninjective repeated-code maps, no inverse q exists; the theorem does not apply. The universal N+1 bound and exact enumeration remain valid in both cases.

## Label and custody rules

A finite-selector label should bind the exact original input bytes, field representation and validation, selector tables or map polynomials, invalid-code policy, variable order, exact descended equation hash, and theorem identifier. Report N, upper_bound=N+1, and a reason such as `finite_boolean_ring_full_cap`; retain exact_lfd and first_fall_degree as unknown unless separately proved. An enumeration record must say whether it counts code assignments or distinct field pairs and retain its exhaustive-domain definition and check evidence.

Neither theorem recognition nor a finite enumeration automatically admits the record to a dataset. Existing custody, schema, certificate, and admission gates remain separate. In particular a failed no-wrap join is not permission to substitute a span or silently change the selector domain.
