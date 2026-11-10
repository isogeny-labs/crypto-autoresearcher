# Uniform truncated quotients: the exact boundary a growing Semaev certificate must retain

2026-11-10. Proof-only continuation. No generator retry, solver, experiment, field-modulus search, build, or cloud work. This note strengthens the operator contract in `certificate-feasibility-contract.md` and specializes it to the actual non-subfield m=2 equations.

## 1. Exact Semaev identities in a prospective quotient

Fix an actual binary field K, an ordered linearly independent basis v_1,...,v_k of V, and nonzero z. Use independent Boolean variables x_i,y_i and put X=sum v_i x_i, Y=sum v_i y_i. The normalized polynomial is

    F=(XY)^2+zXY+z^2(X^2+Y^2)+a6.

Let c_m belong to an F2-vector space Q for every squarefree Boolean monomial m of degree at most D, D>=2. They must span Q. Write e=c_empty. The exact input-containment condition is the single K-tensored vector identity

    sum_(i,j)(v_i^2 v_j^2+z v_i v_j)c_(x_i y_j)
      + sum_i z^2 v_i^2(c_(x_i)+c_(y_i)) + a6 e = 0
                                                              (S)

in K tensor_F2 Q. This is equivalent to all n descended coordinate equations mapping to zero; it is not just a trace projection. For different ordered factor bases in the two blocks, replace the second occurrence of v_j and its linear coefficient accordingly.

For each of the N=2k Boolean variables h, choose a linear operator T_h on Q satisfying

    T_h c_m=c_(m union {h}) for every |m|<=D-1.                (M)

Then C(m)=c_m defines a map B_(<=D)->Q whose kernel contains all inputs and is closed under all legal variable multiplications. Conversely every full closed-kernel certificate gives such operators by extending the well-defined maps from C(B_(<=D-1)). Thus (S), (M), spanning, and a separately justified missing ideal consequence are necessary and sufficient finite certificate conditions. They apply to actual non-subfield V with its actual multiplication constants; no span substitution or independent tensor-block replacement is made.

For a uniform growing lower bound one must give explicit field/subspace/target data for infinitely many n, D(n)->infinity, columns and operators satisfying these identities for every index, and either UNSAT with e nonzero, a valid solution-count upper bound smaller than dim Q, or a named ideal consequence g with C(g) nonzero. This paragraph is a proof obligation, not a supplied family.

## 2. Global commutation ALONE destroys the desired obstruction

**Lemma.** Suppose D>=2, the columns span Q, (S) and (M) hold, and all T_h commute globally. Then these operators form a genuine cyclic Boolean representation supported on actual solutions of the Semaev system. In particular dim Q is at most the number of actual Boolean solutions, and C annihilates every ideal consequence of degree at most D.

Proof: (M) implies T_h^2 e=T_h e, using c_h and D>=2. Every c_m is an ordered squarefree product of the operators applied to e; thus e is cyclic. If the operators commute, then for every operator word P,

    (T_h^2+T_h)P e=P(T_h^2+T_h)e=0.

Cyclicity makes every T_h globally idempotent. Each quadratic coordinate equation f of (S) satisfies f(T)e=0. Commutation again yields f(T)P e=0, so f(T)=0 on Q. Commuting idempotents over F2 give a simultaneous direct sum of Boolean joint eigenspaces, indexed by assignments alpha. Equation annihilation removes all eigenspaces except actual solutions. In each surviving eigenspace, every P(T)e is a scalar multiple of the projection of e, so cyclicity bounds its dimension by one. Consequently Q is a quotient of the coordinate algebra of the actual solution set.

Finally C(g)=g(T)e for every g of degree at most D, so every polynomial vanishing on those solutions maps to zero. This proves all assertions.

This improves the prior warning that imposing *both* global commutation and global idempotence is too strong: imposing global commutation already forces idempotence. A feasible UNSAT separator, or a SAT quotient retaining an actual missing ideal consequence, therefore requires some nonzero global commutator. Globally idempotent but noncommuting extensions are not excluded by this lemma; no implication of global commutation from idempotence alone is asserted.

## 3. The defect must live at the filtration boundary

Put Q_t=span{c_m:|m|<=t}. Then (M) gives

    T_h(Q_t) subset Q_(t+1) for t<=D-1.

On Q_(D-2), the genuine Boolean relations hold:

    [T_h,T_l]=T_h T_l+T_l T_h=0,
    T_h^2+T_h=0.

Indeed both orders of multiplying a degree-at-most-D-2 monomial have the same union mask. For every quadratic input f, f(T) also vanishes on Q_(D-2): multiply f by each monomial of degree at most D-2 within the legal closure and apply C. These statements use an ordered quadratic interpretation of f(T), which is immaterial on this low subspace.

Thus every defect operator factors linearly through Q/Q_(D-2), and its rank is at most dim Q-dim Q_(D-2). Any construction that sets the boundary commutators to zero by a convenient extension choice collapses to the actual solution algebra by the preceding lemma. The commutation defect cannot be confined to an unused noncyclic auxiliary summand: all of Q must be spanned by the prescribed monomial columns. Surjectivity/spanning is therefore a substantive condition, not a normalization detail.

The already-proved plateau obstruction applies: if Q_t=Q_(t+1) for some t<=D-2, multiplication becomes a genuine commuting idempotent action on the generated quotient, so it cannot preserve a missing ideal consequence. Therefore any useful obstruction has

    dim Q_0 < dim Q_1 < ... < dim Q_(D-1),

and dim Q>=D. In fact the independently reviewed initial-monomial argument strengthens this to **dim Q>=2^(D-1)** for a certificate retaining a missing ideal consequence (including UNSAT and rank-excess bridges). Here is the short mechanism. Order squarefree monomials by a degree-compatible ordinary monomial order. If a kernel polynomial has leading monomial m, multiplying by a variable outside m, within cap D, keeps that product as leading monomial: Boolean reduction can only lower competing terms. The truncated leading-monomial set is upward closed, so its complementary standard monomials form a downset and count dim Q. Strict growth at filtration D-1 supplies a standard monomial of degree D-1, and all of its 2^(D-1) divisors are standard.

Consequently every uniform operator construction must provide an exponentially large quotient in D, equivalently D<=1+floor(log2 dim Q). Polynomial-size quotients in n can still support D of order log n; the statement does not exclude growing D. Fixed-size quotients, or quotients growing only polynomially in D, cannot support arbitrarily large cap witnesses. The defect-bearing boundary cannot disappear at a fixed filtration level while D grows. Growth of rank at one fixed cap, however, supplies no such uniform certificate. The separate independent derivation is in `quotient-exponential-rank-review.md`.

## 4. Dual functional formulation includes feedback

Let U be a finite-dimensional subspace of the dual of B_(<=D), with C the evaluation map against a basis of U. Exact closed-kernel containment is equivalent to the following two conditions:

* every lambda in U annihilates each actual input equation;
* for every variable h and every lambda in U, there is mu in U such that

      lambda(h u)=mu(u) for all u in B_(<=D-1).             (D)

To prove necessity, the functional u -> lambda(hu) must vanish on ker C restricted to B_(<=D-1), so it factors through C on that subspace and extends to a linear functional on Q. Conversely (D) makes every lambda vanish on h u whenever every member of U vanishes on u. This is exactly the legal kernel-closure requirement, including all feedback-produced low-degree relations.

A single scalar functional annihilating only the initial equation multiples need not satisfy (D). Such an initial-matrix dual is insufficient. In particular, an ansatz of moment values must prove the restriction identities for its *entire* dual span, not merely its distinguished functional or initial generators.

For Hankel-style moments lambda(uv), one must also be careful at the boundary: multiplying a test monomial of degree D by h can require a degree-D+1 test that was absent from the original kernel definition. Symmetry of a moment matrix alone does not supply the closure implication. One may verify (D) explicitly or provide a suitable larger truncation with proved compatibility; a flat extension producing global commuting Boolean multiplication instead yields actual solution evaluations and cannot certify an absent ideal consequence.

## 5. Concrete consequence for further constructions

A viable infinite-family ansatz must solve the K-valued identity (S), retain the local union identities (M), and explicitly control a nonzero commutation defect reachable at the last two filtration layers for arbitrarily large D. Requiring an everywhere-commuting quotient, using actual evaluation functionals only, or allowing a fixed low-level plateau rules out the needed lower-bound witness before any Semaev-specific details are considered.

The note supplies a stronger impossibility result for globally commuting ansatzes and an exact dual feedback criterion, not an explicit infinite growing-degree certificate. The remaining constructive obligation is a genuinely truncated noncommuting extension compatible with the actual field multiplication constants and an independent ideal-membership/solution-count bridge. No claim is made that every family satisfying the generic operator conditions can be embedded into Semaev equations.
