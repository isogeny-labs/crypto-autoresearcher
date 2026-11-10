# An infinite no-wrap family carrying the checked degree-two obstruction

Date: 2026-11-09. This is a symbolic transfer theorem from one frozen, independently replayed finite certificate. This author inspected the recorded files and hashes but performed no new closure run or replay. The result is the uniform constant lower bound LFD>=3, not unboundedness and not a growing lower bound.

## 1. The finite seed and its immutable identity

The seed is r=6 from

    analysis/semaev-bound-labels-20261109/no-wrap-w2/attempt-1/

in `/home/ec2-user/crypto-lfd-unbounded-20261109`.

- `r6-certificate.json`: 17,353 bytes; SHA-256 `5ac88ce608653f45509b5d6ab0e91169bcbd2c30f289085acf0f7b02b60e9850`.
- `r6-result.json`: SHA-256 `0298038717a1edd1e9efd4835adcd7af4d95bd94e3b09311f0839c78f488f4b6`.

The recorded independent replay establishes full closure and derivation provenance: 14 Boolean variables, exact W2 rank71, affine intersection dimension5. In B_(<=2), the monomial count is 1+14+C(14,2)=106, so the exact quotient has dimension35. The named missing affine generator is x_1, encoded by the single monomial mask2. The result also records all x_i,y_i for 1<=i<=6 as individually missing.

The input source and independent replay expand the full normalized no-wrap S3 coefficient list. Their implementation-level r<=12 guard limits that bounded run, not the mathematical definition of the coefficient family below. No larger value is claimed to have been executed by this transfer theorem.

## 2. Uniform mathematical family

For any integer r>=6 and any irreducible p(T) over F2 of degree n>4r, let

    K=F2[T]/p(T),
    V_r=span_F2(1,T,...,T^r),
    z=a6=1.

Use Boolean coefficient variables x_0,...,x_r,y_0,...,y_r and write x(T),y(T) for the corresponding polynomials. The normalized S3 expression is

    F_r(T)=(x(T)y(T))²+x(T)y(T)+x(T)²+y(T)²+1.

Every T-degree is at most4r<n. Therefore the descended equations are exactly its ordinary polynomial coefficients, with Boolean coefficient variables normalized. No field-modulus reduction occurs and the equations do not depend on which degree-n irreducible p was selected.

### Exact two-point bridge for every r

If deg x=a>0 and deg y=b>0, the term (xy)² has degree2(a+b), strictly greater than a+b,2a,2b. Its leading coefficient cannot cancel, so F_r(T) cannot vanish. If x is constant, it is 0 or1: x=0 gives y²+1=0 and hence y=1; x=1 gives y=0. The symmetric cases give the same two solutions. Thus the Boolean zero set is exactly

    (x,y)=(0,1),(1,0).

In particular x_1 vanishes on every solution for every r. This is the independent source ideal-consequence bridge needed for the restriction argument; it is not inferred merely from the r=6 solutions. It proves x_1 belongs to the Boolean ideal of the larger system.

If a rational target point is required, choosing a2=0 gives the nonsingular ordinary curve y²+xy=x³+1, on which (z,0)=(1,0) lies. This is the known special target, not a generic prime-order-target guarantee.

This family has fixed m=2 and k=r+1, but it is off the half-dimensional diagonal: n>4r, so k is approximately at most n/4 rather than ceil(n/2). The result must not be represented as a new lower bound on the half-dimensional family.

## 3. Exact affine restriction to the seed

Define rho_(r,6) on the coefficient variables by

    x_i -> x_i, y_i -> y_i for 0<=i<=6,
    x_i -> 0,   y_i -> 0   for i>6.

This is a surjective Boolean-ring homomorphism and does not increase degree. The y-variable indices must be renumbered: source y_j has mask 2^(r+1+j), whereas seed y_j has mask 2^(7+j). Source x_1 remains mask2. A monomial involving a discarded variable maps to zero; a retained monomial maps to the union of the corresponding seed masks.

Coefficient extraction commutes with rho. Hence

    rho(F_r(T))=F_6(T).

Each source coefficient row restricts to the corresponding seed coefficient row for T-degrees0 through24, and to zero above24. The nonzero row lists omit zeros, but their images still lie in the seed generating span.

At degree cap two, every source row is eligible. If u is an allowed affine source in W2 and a variable multiplies it, rho(u) is still affine; the substituted variable is either a seed variable or zero. Therefore the strict multiplication rule is preserved, yielding

    rho(W2(F_r)) subset W2(F_6).

There is no selector and no indicator-degree loss.

## 4. Infinite lower-bound theorem

**Theorem (computer-assisted seed plus symbolic transfer).** For every r>=6, every n>4r, and every irreducible polynomial p of degree n, the preceding normalized Boolean m=2 Semaev system satisfies

    x_1 notin W2(F_r),
    d_LFD(F_r with Boolean field equations)>=3.

**Proof.** If x_1 belonged to W2(F_r), applying rho would place x_1 in W2(F_6), contradicting the checked seed certificate. The uniform two-point argument proves x_1 belongs to the larger system's ideal, with degree one. The polynomial/Boolean closure bridge therefore yields LFD>=3. QED.

All individually missing seed generators x_i,y_i for1<=i<=6 transfer in the same manner. Their absence does not imply twelve independent missing dimensions; only the separately stated quotient construction below supplies a numerical codimension lower bound.

Taking, for example, n=4r+1 and any irreducible polynomial of that degree gives infinitely many admissible finite-field instances with growing dimension. Their lower bound remains the fixed number three.

## 5. Explicit constant-rank infinite family of full closed kernels

Let U_6 be the 71-dimensional seed W2 space, supplied by the independent raw certificate events and verified by the replay. Define

    U_r={f in B_(r,<=2) : rho(f) belongs to U_6}.

This space contains every coefficient equation of F_r. If f in U_r is affine, then for each source variable v, rho(vf) is either zero or a seed variable times rho(f); seed closure places it in U_6. Thus U_r is a full closed containing space at cap two, and x_1 is absent from it.

Because rho:B_(r,<=2)->B_(6,<=2) is surjective, the induced quotient map has image all of B_(6,<=2)/U_6. Therefore

    codim(U_r in B_(r,<=2))=35,
    codim(W2(F_r) in B_(r,<=2))>=35.

This is a constructive, uniformly specified infinite family of closed-kernel certificates at the fixed cap D=2. It is encoded by the one seed certificate plus the explicit mask restriction, rather than by independently executing every r. It does not assert U_r equals the exact W2(F_r) for r>6. The rank remains35 and the cap remains2, so neither rank nor degree growth is claimed.

## 6. What has changed and what remains

The frozen r=6 result is no longer merely one isolated finite lower bound: the stated symbolic restriction and uniform ideal bridge propagate it to every r>=6 in the no-wrap polynomial-subspace family. The earlier cap-two upper bounds through r=5 and the new lower bound from r=6 onward show a genuine finite threshold in this family.

The theorem does not establish LFD>=4 at any r, does not give an exact LFD above the known upper-bound cases, and does not prove unboundedness. For a growing lower bound, one must find higher-cap missing consequences on seeds of increasing size or a different inductive certificate that increases the cap. Repeating this fixed seed only reproduces the same constant obstruction.

Sources: `polynomial-subspace-candidate.md` and `no-wrap-coefficient-progress.md` for the no-wrap family/solution bridge; `no-wrap-w2-source-review.md` for the independent full-closure/DAG checker contract; the exact r=6 artifacts identified above; `closure-transport-and-amplification.md` for the strict affine substitution principle. The finite evidence is not rewritten by this additive continuation note.
