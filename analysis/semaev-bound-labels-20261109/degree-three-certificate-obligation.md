# Exact degree-three closure obligation and a W2-dimension barrier

Date: 2026-11-09. Source-only algebraic derivations. No experiments, certificate searches, code execution, builds or cloud jobs. This note gives an exact degree-three criterion and a counterexample to extrapolating hardness from the known degree-two profile alone. It does not prove a degree-four lower bound for Semaev systems.

## 1. Full W3 as a quadratic fixed point

Let B=F2[x_1,...,x_N]/(x_i²+x_i), E=B_(<=2), and H be the space of squarefree homogeneous cubics. For a quadratic generating list F, put A0=W2(F), already fully saturated at degree two. For any subspace A<=E define

    U(A)=A + sum_i x_i A <= B_(<=3),
    Phi(A)=U(A) intersect E.

Set A_(j+1)=Phi(A_j). This is an increasing sequence: A_j<=Phi(A_j). Since E is finite dimensional it stabilizes at A_*.

**Theorem (derived).**

    A_*=W3(F) intersect E,
    W3(F)=U(A_*).

**Proof.** Every A_j and U(A_j) lies in W3 by induction, since W3 admits multiplication of any source of degree at most two. At a fixed point, U(A_*) intersect E=A_*. Therefore every degree<=2 member of U(A_*) lies in A_*, and its product by any variable lies in U(A_*) by definition. Thus U(A_*) is a closed degree-three space containing F. Minimality of W3 gives W3<=U(A_*), and the reverse containment was established inductively. QED.

Starting from span(F) instead also converges to the same A_*; starting from the known exact W2 merely avoids repeating the degree-two saturation. One pass is not assumed sufficient.

For the nonexceptional odd-diagonal Semaev family, the established dimension is dim A0=2N-2, and dim E=(N²+N+2)/2. Thus there are at most (N²-3N+6)/2 strict dimension-increasing iterations. On a verified two-point input, every A_j lies in the affine-line vanishing ideal, whose degree-two part has codimension two, so the sharper iteration bound is (N²-3N+2)/2. These are finite-dimensional termination bounds, not observed iteration counts or hardness lower bounds.

## 2. Explicit cubic syzygy tensor and Boolean contraction

Write a vector of quadratic polynomials (a_i)_(i=1)^N, with

    a_i=c_i + sum_j b_(i,j) x_j + sum_(j<l) q_(i,jl) x_j x_l.

The cubic component Gamma((a_i)) of sum_i x_i a_i has, at each triple j<l<h, coefficient

    q_(j,lh) + q_(l,jh) + q_(h,jl).

These are exactly the exterior/square-zero top-form multiplication constraints in characteristic two. If every triple coefficient is zero, the product sum is quadratic. Its remaining Boolean-contraction coefficients L((a_i)) are:

- constant coefficient zero;
- x_j coefficient c_j+b_(j,j);
- x_j x_l coefficient, for j<l,

    b_(j,l)+b_(l,j)+q_(j,jl)+q_(l,jl).

The last two terms come from idempotent overlap x_j²=x_j and x_l²=x_l. Dropping these terms would replace the true Boolean closure by a different graded calculation.

Consequently the fixed-point operator has the exact tensor form

    Phi(A)=A + { L(a) : a in A^N and Gamma(a)=0 }.

This includes all cubic cancellations among all currently available quadratic rows, including rows created by earlier cancellation rounds. It is not limited to syzygies of the initial coordinate equations.

## 3. Necessary and sufficient rank conditions for a W3 separator

Choose a basis matrix P for A<=E. Form a matrix M(A) whose rows are the basis rows of A, followed by every x_i times every basis row. Order its columns as (cubics H, low part E), and let M3(A) be its cubic-column block. Then

    dim(U(A) intersect E)=rank M(A)-rank M3(A).

This is rank-nullity for the cubic projection restricted to the row space U(A). Since A<=U(A) intersect E, stability is equivalent to the equality

    rank M(A)-rank M3(A)=dim A.                 (S)

For a specified affine consequence g, the following are equivalent:

- g notin W3(F);
- there exists A<=E containing F, satisfying (S), with g notin A.

**Proof.** Such an A makes U(A) closed by the same fixed-point argument and contains F, so W3<=U(A). Since g is affine, g notin A=U(A) intersect E proves g notin W3. Conversely take A=W3 intersect E. QED.

The missing-form predicate is itself a rank condition:

    rank([P;g])=rank(P)+1.

This gives a finite, exact quadratic-space certificate format for degree-three nonmembership, potentially smaller than storing all degree-three quotient columns. No runtime or size advantage is asserted; a separate implementation and analysis would be required.

For a verified two-point Semaev input, use the known affine basis G={a_i,b_i:i>=2} union {a_1+b_1+1}. Then

    LFD>=4 iff some g in G is missing from A_*,
             iff dim(A_* intersect B_(<=1)) < N-1.

Initially that affine dimension is one, spanned by the known trace residual. Proving the degree-four lower bound requires showing the full tensor fixed point cannot create the remaining N-2 independent affine consequences. The degree-two profile alone does not do so.

## 4. A quadratic two-point family with exactly the same W2 profile and constant LFD3

This is a non-Semaev family. Its purpose is to rule out any lower-bound argument that uses only the stated row count, degrees, solution count and W2 dimensions. It is not a claim that it embeds into Semaev descent.

For every r>=2 let N=r+3 and use variables

    u,t,y,x_1,...,x_r.

Take the N-1 genuinely quadratic rows

    f_i=x_i*y+1                  (1<=i<=r),
    h=x_1*x_2+1,
    p=u+x_1*y+1.

All rows have degree two. Their span contains u=p+f_1. The equation f_i=0 forces y=1 and x_i=1; p+f_1 then forces u=0, and t is free. The redundant h vanishes automatically. Thus the zero set has exactly two points, with affine vanishing basis

    u, y+1, x_i+1 (1<=i<=r).

### Exact W2 profile

Let A=span(F)+u*B_(<=1). The space u*B_(<=1) has basis u and u*v for every other variable v, so dimension N. The N-1 rows of F are independent: their distinct quadratic supports x_i*y and x_1*x_2 give r+1 independent top components, and the remaining row combination is u. Its intersection with u*B_(<=1) is precisely span{u}. Hence

    dim A=(N-1)+N-1=2N-2.

The quadratic supports of u*B_(<=1), of the f_i, and of h are otherwise distinct. Therefore A intersect B_(<=1)=span{u}. Products of this sole affine direction by any variable already lie in A. A is thus fully closed at cap two, contains F, and equals W2(F).

In particular

    dim W2=2N-2,
    dim(W2 intersect B_(<=1))=1,
    codim(W2 in B_(<=2))=(N²-3N+6)/2.

These are exactly the degree-two dimensions established for the nonexceptional odd-diagonal Semaev family. Taking every even N>=6 also matches n=N-1 odd and the count n of coordinate equations.

### Exact LFD3

At cap three, Boolean multiplication yields

    x_i*f_i+f_i = x_i+1,
    y*f_i+f_i   = y+1.

These products are allowed because f_i has degree two and the cap is three, even though their squarefree reductions have degree at most two. Together with u they give the entire affine vanishing basis. Degree-nonincreasing affine reduction therefore gives LFD<=3. The affine basis is not contained in W2, so LFD>=3. Hence this infinite family has exact LFD3.

**Barrier.** An argument from "N-1 quadratic equations, two solutions, one affine W2 consequence and W2 dimension2N-2" cannot prove LFD>=4, much less unbounded growth. The actual Semaev multiplication tensors and their iterated syzygy contractions must enter the argument.

## 5. Why initial matrix dimension counting also fails

For the preceding counterfamily, the initial degree-three Macaulay space uses at most (N+1)(N-1)=N²-1 rows: each original row and its N variable multiples. There are 1+N+C(N,2)+C(N,3) squarefree columns. For every N>=6 the resulting row-count lower bound on the initial matrix codimension already exceeds two, and it grows on the order of N³.

Nevertheless the fully saturated W3 has codimension exactly two. The first products derive affine generators; multiplying those generators by further allowed variables fills all remaining degree-three ideal consequences. Therefore a large initial-Macaulay nullspace does not certify a large W3 quotient. It can disappear after newly produced low-degree rows are multiplied.

This counterexample separates three notions that a proposed proof must not identify:

1. initial Macaulay row count;
2. the first cubic cancellation kernel of the original rows;
3. the fixed point under every newly available quadratic row.

Only the third is the full-closure quantity needed for the LFD bridge.

## 6. Concrete next algebraic obligation

For the actual Semaev two-point family, one must supply either:

- a parameter-uniform proper quadratic subspace A containing W2 and satisfying the full stability rank identity (S), while missing a known affine form; or
- a classification of the iterated cubic syzygy contractions proving that A_* intersect B_(<=1) remains smaller than N-1 for infinitely many qualifying subspaces.

A result for only the initial Gamma kernel is insufficient unless accompanied by a proof that its quadratic additions are already stable. The explicit trace/Frobenius cubic identities are inputs to this analysis, not a certificate that no other contractions occur.

This describes the next exact degree-three obstruction. A successful D=3 argument would still establish only the constant lower bound4; unboundedness would require an analogous family of stable truncated spaces at growing caps.

Sources: `degree-two-family-obstruction.md` and its codimension review for the Semaev W2 profile; `two-point-lfd-characterization.md` for the affine-ideal equivalence; the historical theorem dossier for the strict Boolean closure convention. The fixed-point, contraction formulas and non-Semaev counterfamily are proved directly here. No external novelty claim is made.
