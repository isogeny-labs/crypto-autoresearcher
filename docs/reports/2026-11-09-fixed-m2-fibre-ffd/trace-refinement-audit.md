# Independent audit of affine-fibre and trace refinements

Date: 2026-11-09. Source-only mathematical review of `fibre-refinement.md`; no experiments, builds, replay or cloud work. Verdict: **the stated upper-bound refinements are valid for the normalized Boolean presentation**, subject to the explicit qualifications below.

## 1. General affine-fibre bound

For quadratic Boolean inputs with h selector coordinates, suppose each fixed-selector restricted system is affine-linear in the remaining variables and has empty zero set or an affine solution space of dimension at most r. Then the proposed bound

C=max(h+2,h+r+1)

is valid. Choose actual remaining coordinate variables as free coordinates in each affine fibre. Selected original equations are derivable at cap h+2. Their affine Gaussian-elimination consequences have actual degree≤h+1; multiplying by a free squarefree monomial of degree≤r fits cap h+r+1. The normal basis consists of selected free monomials of degree≤h+r≤C−1.

The constant normal-form defect is the sum of empty-fibre selectors, each already derivable at cap h+2. For higher monomials m=xm', the normal-form defect m'−N(m') has actual degree≤max(deg m−1,h+r), so strict multiplication by x fits max(C,deg m). These facts prove full ideal membership at the LFD cap, rather than merely a stabilized low-degree profile. The Gröbner-basis completion route in `fibre-refinement.md` is also sound: the normal basis realizes all functions on the Boolean zero set by degree C−1, so every degree-C monomial has a lower-degree representative; a degree-compatible reduced Gröbner basis has degree≤C and is contained in W_C.

Empty solution sets cause no exception: the empty selectors sum to1 at cap h+2. The formula remains valid for h=0 and for r=0 because C≥2.

## 2. Elimination of selector constraints available in W2

The potentially delicate step is using an affine relation that is a derived row rather than a literal affine generator. Let l(c)=0 be a nonconstant affine selector relation already in W2. Solve for one selector variable c_j=L(c') and substitute. For any multilinear polynomial f, the difference

f(c,a)−f(L(c'),c',a)

is a sum of l times cofactors with total degree no greater than deg f (in the Boolean ring). Successive elimination of several independent affine constraints has the same degree property. Since l has actual degree1 and is already derivable at cap2, the repair lies in W_max(2,deg f).

In particular the substituted original equations lie in W2; they remain of degree≤2. Any subsequent proof using these substituted rows at cap C≥2 is therefore a valid proof from the original list. For a final ideal polynomial f, the same elimination repair costs no more than max(C,deg f). Consequently reducing the selector count does **not** incur an additional hidden degree beyond C.

This is the missing justification that would be required if one merely said "Gaussian eliminate the trace row." It is supplied here and is compatible with the strict source-degree-plus-one closure convention.

## 3. Ambient trace refinement

For alpha=a6/z², the identity

Tr_K(S3/z²)=Tr_K(s)+Tr_K(alpha)

puts ell(s)=Tr_K(s)+Tr_K(alpha) in the original degree≤2 equation span, hence in W2.

- If Tr_K|V is nonzero, ell is a nonconstant affine equation. It removes exactly one selector coordinate, so h=k−1. With fibre dimension≤2 the bound becomes k+2.
- If also z has no factorization uv with distinct u,v∈V, every fibre has dimension≤1 by the independently checked factorization X(X+s)(X²+sX+z), giving k+1.
- If Tr_K|V=0 and Tr_K(alpha)=1, ell=1 gives a refutation at cap≤2. No formal "negative selector count" or nonconstant elimination is used.
- If Tr_K|V=0 and Tr_K(alpha)=0, ell=0 gives no reduction. Counting it as one independent equation would be incorrect.

For k=1 and nonzero restricted trace, h=0. The combined product-exclusion formula gives C=2=k+1, which is safe even though the original list may have consisted entirely of quadratics: the eliminated affine relation is derived at cap2, not assumed available at cap1. The looser r≤2 formula gives C=3=k+2; actual remaining dimension may improve it, but no improvement is needed for validity.

## 4. Full-subfield inside-target case

Suppose K/H is quadratic, V=H, and z,a6∈H with z≠0. The actual field-valued polynomial S3 takes values in H. Every F2-linear functional H→F2 extends to a functional K→F2; equivalently, the H-coordinate output equations and K-coordinate equations span the same space once all degree≤2 rows are eligible. Thus the functional h↦Tr_(H/F2)(h/z²) gives a legitimate original row-span relation

Tr_(H/F2)(s)+Tr_(H/F2)(a6/z²)=0.

It is not obtained by using the ambient absolute trace, which is zero on H. Trace_H itself is a nonzero linear functional because finite fields are separable; it is not necessary that Tr_H(1) be nonzero. This remains true when k is even.

Accordingly one selector coordinate is removable in W2, and the all-instance normalized LFD bound k+2 is valid. The system is in fact always SAT: X=0 and Y=sqrt(a6)/z is a valid pair in H. The earlier diagonal witness omitted the zXY term and is correctly withdrawn in `fibre-refinement.md`; the corrected witness is direct.

This argument yields a linear-in-k upper bound, not a constant one. The zero set can occupy exponentially many selector fibres. The small-total-zero-set Gröbner argument from the outside-target case cannot be reused here.

## 5. Scope and wording corrections

- Every bound here concerns normalized multilinear coordinate inputs together with explicit Boolean field equations. A raw S3 presentation needs its repair-degree accounting.
- Equal equation row spans imply identical strict closures for D≥2 for these degree≤2 input lists. They need not imply identical W0,W1, small exact LFD values, or first-fall statistics. Section7 of `fibre-refinement.md` should state this cap qualification explicitly for output field-basis changes. Invertible affine input-coordinate changes preserve the relevant filtered structure, but mixing output equations can expose lower-degree literal generators.
- None of these refinements proves a growing lower bound. They sharpen the upper-bound and candidate-family classification while leaving the fixed-m=2 binary unboundedness problem open.
- No formalization or computational validation is asserted by this independent written audit.
