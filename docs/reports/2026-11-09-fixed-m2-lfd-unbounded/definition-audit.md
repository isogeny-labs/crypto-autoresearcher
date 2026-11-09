# Fixed-m=2 LFD definition audit and subfield obstruction

Date: 2026-11-09. Scope: theoretical derivation and read-only source review; no build, solver run, certificate replay or cloud job. Status: new pen-and-paper lemma below, independently derived in parallel with the algebraic route; not a proof of unboundedness. Existing computation records were inspected, not rerun.

## Exact objective and source conventions

For n≥3, K=F_(2^n), a6≠0 and z≠0, let F be the coordinate equations over F2 of

S3(X,Y,z)=(XY+z(X+Y))²+zXY+a6,

with X,Y in an F2-subspace V of dimension ceil(n/2), together with Boolean field equations. The desired worst-case theorem is: for every D there is such an F with d_LFD(F)>D. Fixing m=2 does not fix dim V; the latter must grow. Restricting further to the default polynomial subspace is a distinct, stronger target.

Sources inspected:

- `crypto-autoresearcher/analysis/semaev-m2-last-fall-degree/theorem-dossier.md`, definitions §0.2, Propositions 1.1–1.4, Corollary 2.2, Theorem 2.5.
- The companion `results/verification.md` (recorded exact-degree and independent-reproduction scope).
- Primary literature located: Huang–Kosters–Yeo, *Last fall degree, HFE, and Weil descent attacks*, https://eprint.iacr.org/2015/573.pdf; Caminata–Gorla, *Solving degree, last fall degree, and related invariants*, https://arxiv.org/abs/2112.05579 and https://doi.org/10.1016/j.jsc.2022.05.001. The publisher description confirms that its Theorem 3.1 uses a degree-compatible order and the maximum of LFD and reduced-GB degree. Full external proof text was not independently audited in this round. The arguments below are self-contained in the dossier's closure convention.

## 1. Bridge audit

The Boolean closure W_D is the smallest subspace of multilinear polynomials of degree≤D containing the input equations of degree≤D and closed under multiplication by a variable when the source has degree≤D−1. The polynomial closure modulo Boolean field equations agrees with W_D for D≥2 by the dossier's Proposition 1.1. Its three proof steps are sound under the stated polynomial-degree convention: field-equation reduction does not raise degree; lift differences lie in the degree-truncated field ideal; successive monomial multiplication stays within the cap.

For UNSAT systems the ideal is the unit ideal. Therefore d_LFD=min{D:1 in W_D}: the lower direction uses f=1 in the LFD definition; the upper direction multiplies a derived 1 by any desired polynomial at its own degree cap. This is the clean bridge for the proposed unbounded-family proof.

For SAT systems, 1 is outside the full ideal, so `1 not in W_D` says nothing by itself. The dossier's condition codim(W_D in B_≤D)>#solutions is sufficient: the evaluation kernel has codimension at most #solutions, giving a low-degree vanishing polynomial absent from W_D. This is not a necessary criterion.

Caution: the README's blanket first-fall-degree phrasing is stronger than the actual Corollary 2.2. That corollary assumes every selected coordinate generator has degree exactly 2; the Petit–Quisquater statement additionally assumes the trace relation is nonzero. These qualifications must survive in a theorem statement. They do not invalidate the UNSAT LFD/refutation bridge or the new lemma below.

## 2. Derived theorem: the diagonal subfield family has UNSAT LFD at most 3

**Statement.** Let K=F_(2^(2k)), L=F_(2^k)⊂K and V=L (thus dim_F2 V=k=n/2). Let z∈K× and a6∈K×. For every unsatisfiable Boolean descent of S3(X,Y,z), X,Y∈L, the refutation degree is at most 3. Consequently its LFD is at most 3 under the dossier convention. Thus this natural infinite subfield family cannot witness unbounded UNSAT LFD.

**Case z∈L.** The variable-dependent portion of S3 lies in L. If a6∉L, any F2-linear functional vanishing on L but taking a6 to 1 gives the constant equation 1 in the row span, hence a degree≤2 refutation. If a6∈L, taking X=0 and Y=sqrt(a6)/z gives a solution in L; this case is not unsatisfiable.

**Case z∉L.** Write

z²=pz+q,       a6=A+Bz,       p,q,A,B∈L.

The minimal polynomial of z over L is irreducible and separable, so p≠0 and q≠0. Set s=X+Y and P=XY, both in L. Expressing S3 in the L-basis (1,z) gives the two L-valued equations

E1=P+p s²+B=0,
E0=P²+q s²+A=0.

The descended F2 coordinates of E0 and E1 have exactly the same F2 row span as the original descent (the choice of K-coordinate basis is immaterial). Boolean squaring of an L-valued polynomial is coefficientwise Frobenius: if E1=Σ e_i f_i with f_i Boolean F2-valued coordinate polynomials, then E1²=Σ e_i² f_i because f_i²=f_i in the Boolean ring. Therefore every coordinate of

Q(s)=E0+E1²=p²s⁴+q s²+A+B²

is an F2-linear combination of the original coordinate equations, not a degree-4 derivation. Since Frobenius powers of s are linear in its Boolean coordinates, Q(s)=0 is an affine-linear Boolean system available inside W_2(F).

The linear map T(s)=p²s⁴+q s² has kernel exactly

{0, sqrt(q)/p}.

Indeed T(s)=s²(p²s²+q), and squaring is bijective on L. Its kernel has dimension 1 over F2. Thus Q(s)=0 is either inconsistent, yielding 1 in the original equation span, or its solution set is an affine line s=s0+u h with u∈F2 and h=sqrt(q)/p.

Perform the invertible F2-linear coordinate change (X,Y)↦(X,s), and affine Gaussian elimination on Q(s). This gives k−1 affine-linear constraints expressing all but one s-coordinate in terms of u. Such constraints lie in W_2(F). Substituting them into any quadratic input f costs no degree above 2: the difference f−f_sub is a sum of these linear constraints multiplied by affine-linear polynomials. Consequently all the substituted E0,E1 coordinates belong to W_2(F) and depend only on X's k Boolean coordinates and u.

Fix u=b for b=0,1. Now s is a field constant. Because P=XY=X(X+s)=X²+sX, P and P² are F2-linear in X. Every restricted equation is affine-linear in X. The original UNSAT assumption implies each restricted affine system is inconsistent, so a scalar F2-linear combination of its equations equals 1.

To lift without a hidden degree loss, let H_b be that same scalar combination of the un-restricted, substituted equations. Then H_b∈W_2(F) and H_b|_(u=b)=1. In the Boolean ring the selector e_b=u+b+1 satisfies e_b H_b=e_b, and multiplication of H_b by u is allowed in W_3. Hence e_0,e_1∈W_3(F), so 1=e_0+e_1∈W_3(F). This proves the bound.

**Independent cross-check.** The algebraic-route agent obtained the same decomposition and ≤3 claim independently. The initial degree≤4 estimate in this audit was sharpened by factoring T(s), which improves the kernel-size bound from the loose quartic bound 4 to the exact bound 2. The final proof above includes the potentially delicate degree-preserving elimination and selector-lifting steps.

**Scope limit.** This is an UNSAT theorem for V equal to the exact index-two subfield. It does not prove a uniform LFD bound for SAT systems, arbitrary half-dimensional subspaces, scaled subfields, or default polynomial subspaces. It therefore rules out one candidate construction without settling the user's target.

## 3. Why naive amplification does not prove unboundedness

### 3.1 Extending the field while retaining V preserves the old equations

Let K⊂K' be finite fields and retain all old parameters and the old F2-space V. S3 still takes values in K. Any F2-coordinate descent in K' is therefore obtained from the old coordinates by injective linear embedding, and conversely the old coordinates are linear combinations of the new ones. The quadratic input row spans agree, and their W_D agree for D≥2. This changes the ambient field but does not increase the hard instance's LFD in the relevant degree≥2 range. It also fails k=ceil(n/2) once n grows and V is held fixed.

Enlarging V to repair the diagonal introduces new assignments and equations. Neither unsatisfiability nor growing lower bounds follow from the old certificate. An old hard restriction provides at most its fixed old lower bound; it does not automatically add degree at each extension.

### 3.2 Independent copies have an immediate short refutation

For a fixed UNSAT system F with 1∈W_d(F), a conjunction of any number of variable-disjoint copies contains one whole copy. Reuse that copy's derivation to obtain 1 at degree d. Thus repetition/direct-sum conjunction has refutation degree≤d, independently of copy count. Tensor-product terminology does not change this fact if the construction still contains a copy's equations. A genuine amplification gadget must avoid this shortcut and must itself be realizable by a single field S3 equation with half-dimensional V.

### 3.3 Elimination degree is not a lower bound on LFD

A resultant, determinant, or truth-table eliminant of large degree can be derived through low-degree equations, or coexist with a short refutation. Its degree alone does not rule out an alternative derivation of 1. A growing determinant degree therefore requires a separate minimality/closure argument.

### 3.4 Original Macaulay annihilators are insufficient

A linear functional annihilating the original degree-D Macaulay matrix only proves 1∉M_D if it takes 1 to 1. Since M_D⊂W_D and successive falls can strictly enlarge the space, this does not prove 1∉W_D. Certificates used to infer LFD must control the saturated closure or a proved containing invariant space.

## 4. A rigorous route that would suffice

Construct explicit admissible fields/parameters/subspaces F_n, a function D(n)→∞, and a linear map

φ_n : B_≤D(n) → Q_n

with (i) φ_n(1)≠0; (ii) every input equation lies in ker φ_n; and (iii) whenever h∈ker φ_n has degree≤D(n)−1, x_i h∈ker φ_n for every Boolean variable. Then ker φ_n is a proper closed containing space, so W_D(n)(F_n)⊂ker φ_n and 1∉W_D(n). A separate exact argument that F_n has no Boolean zero completes d_LFD(F_n)>D(n).

Finite quotient-map certificates can suggest Q_n and φ_n, but all three conditions must be proved uniformly, including the low-degree part of the kernel after cancellations. This is a more direct theorem target than extrapolating measured ranks. For SAT families, replace the separation of 1 by an explicitly known vanishing polynomial absent from closure, or a rigorously controlled codimension gap against the exact zero count.

**Next precise target.** Search for half-dimensional V with provable multiplication-tensor/annihilator structure beyond subfields. The subfield theorem shows that closure invariance must exploit a different structure: the most obvious tower construction instead creates a low-degree refutation mechanism. No infinite unbounded family has been established by this audit.

## 5. Additive reconciliation with current main (dadfb1b2a5b6)

After the derivation above, read the following exact Git objects from main commit `dadfb1b2a5b6e8e6045f8547d26ec2b40d4ff81a` in `/home/ec2-user/crypto-lfd-unbounded-20261109`:

- `problems/growing-boolean-semaev-lower-bound.md`;
- `analysis/rigorous-lfd-solving-20261105/problems/remaining-binary-obligations.md`;
- `analysis/boolean-fall-certificates-20261104/THEORY.md`.

The latest record explicitly leaves the characteristic-two growing lower bound open. It already identifies the full closed-kernel separator strategy in §4 above, so that strategy is **reused existing program work**, not a new proposal or novelty claim. Reuse the existing problem record rather than opening a duplicate question. Its next discriminating step is to control multiplication of the whole low-degree kernel after known trace and degree-three falls.

There is now a written and independently reviewed **prime-digit** family lower bound `4+floor(s/2)`, at the exact stated Boolean-digit/F_p-coefficient presentation. It does not transfer to characteristic two: the needed low-degree square-zero multiplication injectivity uses invertible odd-characteristic inclusion factors. Thus the older dossier and this audit must not be read as a claim that no growing-family result exists anywhere in the repository. The remaining gap is precisely binary.

The closure convention agrees exactly: strict multiplication permits `b_i*w` only when the squarefree source degree satisfies `deg(w)+1<=D`, rather than accepting a multiplication merely because its reduced product happens to have degree≤D. This audit's subfield proof uses only permitted operations: coordinate row combinations; linear-constraint multipliers of degree≤1 at cap2; and selector multiplication of quadratic rows at cap3. It does not use the forbidden reduced-product shortcut.

The new subfield theorem is for **multilinear-normalized Boolean coordinate inputs plus explicit bit equations**. Current main warns that replacing raw input polynomials by their normal forms does not transfer small exact LFD without paying for raw input/repair degrees. Accordingly, the bound≤3 in §2 is not asserted for an unspecified raw quartic S3 presentation. A raw-presentation transfer would require its own degree bookkeeping; a blanket identification with raw degree3 or4 inputs would be incorrect.

Current main also has a compiled scoped raw binary two-S3-chain upper-bound formalization, `lastFallDegree_binary_two_S3_chain_le` with bound `3ell+1`, plus explicit limits on full-workspace verification. The new subfield lemma is a different, more restricted single-S3 statement and is a written argument only; no Lean claim or supersession is made.

Finally, a family theorem must state target admissibility and rational-lift/sign semantics separately when calling its Boolean systems ECDLP relation instances. The subfield **upper bound** applies to every z≠0, so it also holds on any rational-target subset, but an eventual unbounded **lower-bound** family must explicitly meet whichever target-admissibility restriction is chosen.
