# Independent review: uniform cap four for the no-wrap family

Date: 2026-11-09. Source-only independent review of `no-wrap-uniform-cap-four.md`. No computation, new instance, solver, or build.

**The uniform upper bound is correct: every no-wrap polynomial-subspace instance in the stated regime has LFD at most four.** Together with the reviewed restriction obstruction, this gives 3<=LFD(F_r)<=4 for every r>=6, n>4r. The no-wrap subfamily cannot establish unbounded LFD.

## Leading-selector contradiction

The affine reduction to E=A(x)+x*A(q)+q² is valid at cap two, including the constant-coefficient step already audited. The q coefficients are affine coordinates, since coefficient Frobenius is linear on Boolean bits.

After fixing higher q coefficients to zero and q_j=1, the top coefficient of A(q) is one at polynomial degree 2j. For i>2j, the coefficient of T^(2i) is x_i plus terms involving strictly higher x indices: product indices are at least 2i-2j>i, and the nonsquared x term has index 2i. Descending elimination is therefore legitimate using affine consequences and their affine multiples, at cap two.

On the x_(2j)=0 branch, consider T^(i+2j) with 0<i<2j in descending i order. Its leading product contribution is x_i. Other product contributions use larger x indices. The possible square contribution has index j+i/2>i; the direct x contribution also has larger index. The q² contribution is zero at this exponent. Hence all positive x_i vanish. The coefficient at 2j then gives x_0+1, and substituting x_0=1 leaves E=q, whose j-th coefficient is the contradiction one. Each step costs cap two.

On the x_(2j)=1 branch, u=x+A(q) is an invertible affine change of Boolean coordinates. Expanding in characteristic two gives E=A(u)+u*A(q)+q exactly. The coefficient u_(2j)=0 and all higher u coefficients vanish. The same descending argument eliminates every positive u coefficient. At exponent 2j it gives u_0=0; the remaining equation q supplies the contradiction at j. This again is a cap-two refutation in the branch coordinates.

Two one-bit branch lifts therefore give a cap-three refutation under q_j=1. One-sided lifting with selector q_j derives q_j at cap four. Both lifts account for the original quadratic-generator threshold; neither treats branch equations as unconditional inputs.

## Why the degree cap does not accumulate

This is the critical induction point. If all higher q coefficients are already in W_C, setting them to zero changes each quadratic coefficient row by sums of those available affine equations times affine cofactors. Thus each transformed quadratic row is available in W_C, regardless of its original derivation cap.

The complete local peeling derivation from these transformed rows has cap four. It can be replayed inside W_max(C,4): its input rows are already present, and every subsequent multiplication uses a polynomial of actual degree at most three. It does not require the transformed rows to have original derivations in W2 or W3. Beginning with C=2 and continuing after the first peel with C=4 therefore keeps every later q_j in W4. The number of peeled coordinates does not add further selector degrees.

With q=0, removing its products from E uses only the already-derived q linears and affine multipliers. The remaining A(x) coefficient system derives every positive x coordinate by descending doubling chains. The affine y substitution gives the rest of the two-point ideal. Since that ideal has degree-nonincreasing representations in its affine generators, all ideal polynomials f are derivable at max(4,deg f). This is the required LFD conclusion, beyond mere solution recovery.

## Arithmetic corollary and exact scope

The immutable-echelon algorithm also checks out in the stated indexed-bit arithmetic model. With degree-first pivots, the rows whose leading monomials have degree at most three span the entire eligible intersection at every stage. New rows with higher-degree pivots cannot create unrepresented lower-degree combinations, because the largest selected pivot cannot cancel. Each low-pivot row needs processing only once; at most M_3 such pivots exist, so at most N*M_3 multiplication candidates occur. Dense insertion costs at most O(M_4²) binary operations, yielding the conservative O(N^12) arithmetic and O(N^8) stored-bit bounds. The note correctly separates indexing/input conversion and field-representation input length from this claim, and makes no timing or benchmark assertion.

No mathematical correction is required. The result resolves the uniform-cap question for this particular no-wrap family. It does not apply to the half-dimensional family, where actual modulus reduction is unavoidable, and it does not decide whether general no-wrap instances have degree three or four. The previously reviewed r=6 exact degree three result remains consistent.
