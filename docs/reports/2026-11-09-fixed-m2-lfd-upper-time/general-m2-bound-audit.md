# Independent audit: general normalized m=2 bound k+3

Date: 2026-11-09. Source-only mathematical review of the certificate-route proposal communicated by the parent. No build, experiment, replay, or cloud execution. Status: **the proof is valid under the stated normalized Boolean presentation**. This note spells out the induction and two easily missed prerequisites.

## Statement

Let K=F_(2^n), z∈K×, a6∈K×, and let V⊂K be any k-dimensional F2-subspace. Let F be the multilinear-normalized coordinate equations of

S3(X,Y,z)=(XY+z(X+Y))²+zXY+a6,

for X,Y∈V, and include explicit Boolean field equations in Ftilde. Then

**d_LFD(Ftilde)≤k+3**, for SAT and UNSAT instances.

The earlier k+2 UNSAT bound remains stronger in its scope. This is a growing **upper** bound and does not imply any growing lower bound. It is independent of n except through k.

## 1. Coordinate change and small affine fibres

Use Boolean coordinate vectors a,b for X,Y and replace b by c=a+b, so s=X+Y∈V has coordinates c. This is an invertible F2-linear change; it preserves degree, strict closures, and the span of explicit field equations. In these coordinates

S3(X,X+s,z)=X⁴+(s²+z)X²+zsX+z²s²+a6.

For each fixed s=σ∈V, every descended coordinate equation is affine-linear in a. Its homogeneous field-valued map is

Lσ(X)=X⁴+(σ²+z)X²+zσX.

This is a nonzero degree4 polynomial with leading coefficient1. Therefore its kernel in K has at most4 elements, and its kernel intersected with V has F2-dimension at most2. Each Boolean fibre is empty or an affine subspace of dimension qσ≤2.

## 2. Selected affine equations are derivable

For σ represented by k Boolean bits, let eσ(c)=Π_i(c_i+σ_i+1). These selectors have degree k, partition1, and satisfy eσ f(a,c)=eσ f(a,σ) in the Boolean algebra.

Every input has degree≤2. Thus eσ f_i∈W_(k+2): successively multiply the input by the k affine factors, using linear combinations and variable products, never exceeding degree k+2.

If the fibre is empty, affine Gaussian elimination gives 1 as an F2 scalar combination of f_i(a,σ), and hence eσ∈W_(k+2).

For a nonempty fibre choose qσ actual coordinate variables t=(a_(j1),...,a_(jq)) as free variables. Gaussian elimination expresses every a_j=L_(σ,j)(t), with L affine, and each equation a_j−L_(σ,j)(t) is an F2 scalar combination of the restricted equations. Hence

eσ(a_j−L_(σ,j)(t))∈W_(k+2).

Its **actual multilinear degree** is at most k+1, even though its derivation cap is k+2. This degree distinction makes the next step valid.

## 3. Canonical fibre normal form

Define N on the full Boolean algebra by substituting c=σ and a=Lσ(t) on each nonempty fibre, reducing in the qσ free Boolean variables, and multiplying the result by eσ. Sum over nonempty fibres. Empty fibres contribute0.

The normal-form basis consists of eσ t_J for J⊂{1,...,qσ}. Its degree is at most k+2. These basis functions are linearly independent when restricted to the zero set: selectors have disjoint support, and the free squarefree monomials are independent Boolean functions on each affine fibre. Therefore

N(f)=0 iff f vanishes on the Boolean zero set.

This criterion must be established semantically before the induction below; it is not inferred from closure ranks. The construction also gives N(x N(f))=N(x f) because f and N(f) have the same values on every fibre and N chooses a unique basis representative.

## 4. Multiplication defects are in W_(k+3)

It suffices to check each normal basis monomial v=eσ t_J.

- For a c-coordinate, c_i eσ=σ_i eσ holds exactly in the Boolean algebra. Thus c_i v is already a normal-form combination.
- For an a-coordinate, subtract its affine fibre expression:

  a_j v−eσ t_J L_(σ,j)(t)=eσ t_J(a_j−L_(σ,j)(t)).

The selected affine constraint on the right is already in W_(k+2), has actual degree≤k+1, and is multiplied by at most two free variables. The intermediate actual degrees are at most k+2 and k+3. Thus every multiplication is permitted in W_(k+3). The expression eσ t_J L_(σ,j)(t), after Boolean reduction among at most2 free variables, is exactly the normal form N(a_j v).

By linearity, for every normal-form polynomial h and every coordinate x,

x h−N(x h)∈W_(k+3).

No multiplication is justified solely by the degree of its reduced product; the source-degree-plus-one cap is respected throughout.

## 5. Full-degree induction, including its base case

Set C=k+3. Claim: for every squarefree monomial m of degree d,

m−N(m)∈W_max(C,d).

**Base d=0:** 1−N(1)=Σ_(empty fibres σ) eσ. Each summand lies in W_(k+2), so the base is proved even when some fibres are empty. Omitting this base would leave a genuine gap in a SAT proof.

**Induction:** write a nonconstant squarefree monomial as m=x m', deg m'=d−1. Put D=max(C,d). By induction m'−N(m') lies in W_D and its actual degree is at most max(d−1,k+2)≤D−1, because all normal forms have degree≤k+2. Therefore strict multiplication gives

x(m'−N(m'))∈W_D.

The multiplication defect xN(m')−N(xN(m')) lies in W_C⊂W_D by §4. Since N(xN(m'))=N(xm'), adding the two identities proves the induction.

Linearity yields f−N(f)∈W_max(C,deg f) for every Boolean polynomial f.

## 6. Transfer to ordinary polynomial LFD

The Boolean ideal of F is precisely the functions vanishing on its zero set. Thus for every Boolean ideal member f, N(f)=0 and f∈W_max(C,deg f).

For an ordinary polynomial p∈(Ftilde), its Boolean normal form lies in that Boolean ideal and has degree≤deg p. The strict quotient/polynomial bridge (valid at these caps, since C≥2) and the degree-bounded field-equation repair lift its derivation back to p∈V_(Ftilde,max(C,deg p)). This is exactly the last-fall-degree definition, proving the all-instance bound.

## 7. Conditions and limits

- Inputs must be the normalized multilinear coordinate polynomials plus Boolean equations. Raw presentation transfer needs separate repair-degree accounting.
- The scalar Gaussian-elimination argument uses the **entire original restricted coordinate system**, rather than a selected subset with potentially different fibres.
- Each fibre normal form uses at most2 actual free a-coordinates; no nonlinear parameterization or unproved degree-preserving encoding is introduced.
- The proof is constructive but sums over 2^k fibres. Its algebraic degree bound is not a polynomial-time bound for computing the whole normal form or enumerating all solutions.
- The argument improves the SAT-family upper-bound coverage; it does not provide a lower-bound mechanism or establish unboundedness.
- This audit is independent written reasoning only, not formalization or runtime validation.
