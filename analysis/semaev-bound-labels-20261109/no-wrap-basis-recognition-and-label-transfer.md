# No-wrap recognition under factor-base and coordinate basis changes

2026-11-09. Source-only derivation and exact recognition contract. No solver, experiment, build, or cloud job. Sources are the reviewed `no-wrap-uniform-cap-four.md`, `no-wrap-r6-exact-degree-three.md`, and `no-wrap-fixed-obstruction-transfer.md` and their reviews.

## Filtered invariance lemma

Let B be the Boolean polynomial ring in N variables, and let F be a finite list of degree-at-most-two polynomials. Let phi be an invertible affine F2 change of the N Boolean variables. Let G be any list whose F2-linear span equals the span of phi(F); in particular an invertible constant row change is allowed. Then

    W_D(G)=phi(W_D(F)) for every D>=2.

Proof: phi and its inverse preserve the degree filtration. At D>=2 all source generators and all their row combinations are available. To transport an allowed multiplication by a source variable, multiply by its affine image: it is a sum of constant and single-variable multiplications, each within the same cap. Minimality of the closed space gives one inclusion; applying the inverse gives equality. Constant row changes preserve the generated ideal, and phi transports it isomorphically.

Consequently a source bound d_F<=4 transfers, as does d_F>=3 witnessed by a missing affine ideal element at D=2. If d_F(F)=3, then d_F(G)=3: the cap-two obstruction transfers and degree-controlled derivations at all caps at least three transfer. More generally exact LFD values at least three are invariant. The lemma deliberately makes no W_0 or W_1 assertion. Distinct source generators can combine into a new affine row.

## Application to arbitrary bases of the same no-wrap subspace

In a supplied polynomial field representation K=F2[t]/P with deg(P)=n>4r, put V_r=span(1,t,...,t^r), z=a6=1. Let v_0,...,v_r be any F2 basis of V_r, and use X=sum u_i v_i and Y=sum v'_i v_i with separate Boolean coefficient blocks. (The notation v'_i denotes Boolean coefficients, not field basis vectors.) If A is the coefficient matrix expressing this basis in 1,t,...,t^r, then the standard coefficient variables are A u and A v'. Since A is invertible, this is an invertible linear Boolean change. The descent systems are related by this substitution, and optional invertible changes of output field coordinates are constant equation-row changes.

Thus every such basis has LFD<=4. For r>=6 it also has LFD>=3. For r=6 it has **exact LFD=3**, by the independent symbolic cap-three proof. For r<=5 the known cap-two upper bounds transfer, but this contract does not assert exact LFD or first fall degree for those cases. The two factor blocks could mathematically use different bases of the same space, with independent invertible matrices; an implementation should only claim this extension if its exact input schema explicitly represents both and verifies both spans.

## Guarded recognition in the existing polynomial-basis representation

For a schema supplying an irreducible degree-n modulus and a list of k independent n-bit field vectors for the common factor base, set r=k-1. Exact sufficient checks are:

1. The system is precisely the Boolean m=2 S3 descent with z=a6=1, without additional lift constraints, auxiliary variables, quotient constraints, or a substituted alternative generator family.
2. The field representation is verified and n>4r.
3. Each listed factor-base vector has zero coordinates at indices k,...,n-1 in the declared polynomial basis.
4. Their k by k low-coordinate matrix has rank k over F2.

Checks 3-4 prove equality of subspaces, not merely containment or equal dimensions. The matrix itself is a finite transfer witness. Arbitrary basis ordering and invertible mixing are allowed; a sorted literal powers list is unnecessary. Require the schema's usual duplicate, length, integer-range, rank, and field validation before applying this rule. A reducible modulus or an unverified declaration of a field does not meet the hypotheses.

For arbitrary supplied equation lists, metadata alone is insufficient. Reconstruct the exact canonical coefficient list and verify equality of F2 row spans with the supplied list after the declared variable transformation. Equal row spans suffice even if zero rows or redundant rows occur. Coefficients of all Boolean monomials through degree two must be checked; numerical evaluation on a few points is insufficient. Binding the original exact input hash, ordered basis/matrix, equation hash, theorem identifier, and recognized r,n keeps the proof attached to its actual presentation.

Labels supported by this contract are upper_bound=4 and, when r>=6, lower_bound=3; at r=6 exact_lfd=3. Where earlier cap-two upper proofs apply, retain the stronger upper_bound=2. Do not infer a first_fall_degree label from row-span invariance alone; the final section gives a stronger fixed-output-coordinate permission. These are theorem-derived labels, not measured closure results, and do not by themselves grant dataset admission.

## Field isomorphisms: what is and is not established

An explicit F2-field isomorphism psi:K->K' carries S3(X,Y,1) to S3(psi(X),psi(Y),1), since it fixes 0 and 1 and preserves sums and products. If the factor base is transported element by element, the Boolean inputs remain the same and the output coordinate equations differ by an invertible F2-linear map. Therefore all the preceding cap-at-least-two conclusions transfer.

A usable isomorphism witness can be an explicit binary matrix, verified to have full rank, to send 1 to 1, and to preserve products on every pair of source field basis elements. Bilinearity then proves product preservation everywhere. Alternatively an image alpha of the source polynomial generator, satisfying its irreducible source modulus in the verified destination field of equal degree, determines an injective map and hence an isomorphism; one must still check that the factor-base list maps to the intended list or subspace. These are exact algebraic checks, not assumptions from equal field sizes.

Changing the irreducible modulus while taking literal powers in the *new* polynomial basis is independently covered by the no-wrap theorem, since it works for every modulus of degree n>4r. This should not be confused with transporting an arbitrary prior subspace: an unspecified isomorphism can send that subspace elsewhere. If the input uses an unknown basis, says only that a suitable generator or isomorphism exists, or supplies no checked witness, this recognition rule must not assign a no-wrap label. A more general recognizer based on powers of an explicitly verified field generator is mathematically possible, but is a separate implementation scope.

## Why first fall degree is not transported by the row lemma

The threshold D>=2 is essential. For a simple Boolean example take the ordered generators

    F=(xy+x, xy+x+1, xy).

Every input has degree two, and the first two sum to 1, so under the literal product-quotient first-fall convention the first fall is at degree two. The invertible row transformation

    G=(F1+F3, F2+F3, F3)=(x,x+1,xy)

exposes two affine inputs whose sum is 1; there is now a first fall at degree one. Neither list has a constant input. At every cap D>=2 their closed spaces coincide, but their W_1 spaces differ. This elementary example only demonstrates the presentation issue; it is not asserted to be a no-wrap Semaev member.

An invertible affine *variable* transformation without generator-row replacement preserves individual degrees and the filtration, and hence does not have this row-exposure issue. Nevertheless a label obtained from a literal coordinate-presentation theorem should not be transferred through an output-row change without an independent first-fall argument. In particular LFD=3 for the r=6 family transfers safely while an accompanying FFD=2 must not be copied merely because the equation row spans agree.

## Sharper FFD permission for fixed output coordinates

For r>=1, if the output rows remain the literal polynomial-coordinate rows, a change only of the factor-base input basis **does preserve first fall degree two**. This is a stronger, separate permission than row-span invariance.

First consider the standard powers input basis. Write p=xy and s=x+y+1. The coefficient rows are f_j=p_j+[j even](p_(j/2)+s_(j/2)). The constant row is f_0=s_0=x_0+y_0+1. Every other nonzero row is genuinely quadratic: for 1<=j<=2r its p_j contribution contains cross-block monomials with index sum j, which cannot cancel the p_(j/2) contribution of a different index sum; for j>2r a nonzero row is p_(j/2) at even j and is genuinely quadratic. Remaining rows are zero. Thus f_0 is the only nonzero affine row.

Evaluation at T=1 is a linear combination of all coefficient rows, and in the Boolean coefficient ring p(1)^2=p(1). Consequently

    sum_{j>0} f_j = sum_{i=1}^r (x_i+y_i).

For r>=1 this is a nonzero affine form, independent of f_0; it is a degree-two fall witness. A degree-one fall to a nonzero constant is impossible because the only nonzero degree-at-most-one input is the single nonconstant affine row f_0. This proves literal first fall degree two under the study's nonzero-fall product-quotient convention.

Now apply an invertible linear transformation to each Boolean input block, leaving output row identities fixed. An invertible filtered Boolean automorphism preserves exact degree: if degree dropped, applying its inverse would contradict the original degree. Therefore the one affine input remains nonconstant, every genuine quadratic row remains quadratic, and the displayed fall witness remains a nonzero degree-one relation independent of the affine input. The same two arguments give FFD=2 for every recognized factor-base basis in these fixed output coordinates.

This permission excludes r=0, arbitrary output-row mixing, field-isomorphism output changes, and alternative row-span presentations. It does cover using a different irreducible modulus with its own literal polynomial-coordinate descent, because the no-wrap coefficient formula is unchanged. An inspector may set FFD=2 for r>=1 only after confirming that it reconstructed those exact literal rows (up to their unchanged labels), not merely an equal equation span. Equal-span recognition continues to carry the LFD labels only.
