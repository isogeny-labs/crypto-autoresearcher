# Degree-two obstructions on the count-controlled fixed-m=2 family

Date: 2026-11-09. Derived source-only results, pending independent review. No random search, solver run, compilation or new experiment. The lower bound obtained is the fixed value three, not a growing function of n.

## 1. Setting and outcome

Fix odd n=2r+1, k=r+1, K=F_(2^n), z=a6=1 and a k-dimensional F2-subspace V. Let F be the Boolean descent of

 x²y²+xy+x²+y²+1=0, x,y in V.

Two results follow without assuming random generic ranks:

1. **Every exactly-two-solution V containing 1 from the preceding existence theorem has LFD at least three.** This gives an infinite SAT family with a proved lower bound three and exactly two zeros.
2. **For infinitely many odd n, there is a trace-active UNSAT V, with 1 not in V, that also has LFD at least three.** Thus the trace-active UNSAT existence family cannot consist entirely of degree-two refutations. The proof bounds the number of exceptional subspaces satisfying the dossier's rank-one condition and compares it with the number of UNSAT subspaces guaranteed by the counting argument.

Neither result says that LFD grows beyond three on those chosen families.

## 2. The product-span condition is automatic on the odd diagonal

The dossier's degree-two lemma uses (G1): the annihilator of span(V*V) intersects the trace-zero space trivially. In the present dimensions a stronger statement holds:

 span_F2{xy:x,y in V}=K.

If a nonzero mu annihilated all products, the nondegenerate bilinear form

 B_mu(x,y)=Tr_K(mu x y)

would vanish identically on V*V. Thus V would be contained in its B_mu-orthogonal complement, forcing

 k<=n-k.

But k=r+1 and n-k=r. This contradiction proves the full product-span statement, and hence (G1), for **every** V of the required dimension. No genericity assumption is needed.

## 3. Exact rank-one exceptional condition

For trace-active V, the remaining dossier condition (G2) fails exactly when there exists mu in ker Tr_K such that

 Tr_K(mu x y)=Tr_K(x)Tr_K(y) for all x,y in V.  (1)

There is at most one such mu: the difference of two would annihilate V*V, contradicting Section 2. It is nonzero because trace is nonzero on V.

When (1) has no solution, the dossier's Proposition 2.6 gives the exact degree-at-most-one part of the saturated degree-two closure:

 W2(F) intersect B_(<=1) = F2*ell,
 ell=Tr_K(x+y)+1.

Here ell is nonconstant when V is trace-active. Thus 1 is not in W2. This statement concerns the fully saturated closure, not only the first Macaulay matrix.

The exceptional condition (1) is a precise algebraic test; this note does not assert that its failure automatically implies a degree-two refutation. When it holds, additional affine consequences and further degree-two saturation must be examined. The counting argument below avoids that exceptional set entirely.

## 4. The containing-1 SAT family automatically avoids the exception

If 1 belongs to V, substituting x=y=1 into (1) gives

 Tr_K(mu)=Tr_K(1)^2=1,

because n is odd. This contradicts mu in ker Tr_K. Therefore (G2) holds for every V containing 1.

Take any qualifying V from `low-solution-count-family.md`, whose zeros are exactly (0,1),(1,0). Its solution set is an affine line in 2k Boolean coordinates. Its affine vanishing ideal has dimension 2k-1, whereas the affine part of W2 has dimension only one, spanned by ell. For k>=2, there are affine ideal generators absent from W2. The LFD definition therefore gives

 d_LFD(F)>=3.

This proves a fixed lower bound on every member of the existential two-solution family, rather than merely on a typical random subspace. The n=3 literal control reviewed in `degree-three-control-review.md` attains equality; no equality is claimed for larger n.

## 5. Counting the exceptional rank-one subspaces

For a fixed nonzero mu in ker Tr_K, put a=sqrt(mu) and h=1/a. Define

 C_mu(x,y)=Tr_K(mu x y)+Tr_K(x)Tr_K(y).

Condition (1) says V is totally isotropic for C_mu.

The form C_mu is a rank-one update of the nondegenerate B_mu, so its rank is at least n-1. A totally isotropic subspace of dimension r+1 in dimension 2r+1 forces degeneracy. Solving the radical equation explicitly gives

 mu x+Tr_K(x)=0.

A nonzero solution exists exactly when Tr_K(1/mu)=1, equivalently Tr_K(h)=1; then the radical is F2*h². If this trace condition fails, there is no exceptional V for that mu.

The diagonal of C_mu is

 C_mu(x,x)=Tr_K((a+1)x).

Since Tr_K(a)=Tr_K(mu)=0 and Tr_K(1)=1, a+1 is nonzero. Every exceptional V is contained in the hyperplane

 H_a={x:Tr_K((a+1)x)=0}, dim H_a=2r.

The restriction of C_mu to H_a is alternating. Its radical is exactly span_F2{h,h²}, of dimension two. To verify this, its orthogonality equation is

 a²x+Tr_K(x) in F2*(a+1).

Solving expresses x as an F2 combination of h,h², and direct substitution verifies both vectors are in the radical. They are independent because h is neither 0 nor 1. Therefore H_a/rad is a nondegenerate symplectic space of dimension 2r-2.

An exceptional V has dimension r+1, the maximal isotropic dimension of H_a, so it contains the two-dimensional radical. Its image in the quotient is a Lagrangian of dimension r-1. Thus the number of exceptional V for this mu is at most

 L_(r-1)=product_(i=1)^(r-1)(2^i+1).

For clarity, the standard count follows by counting pairs (nonzero v,Lagrangian L containing v): L_s(2^s-1)=(2^(2s)-1)L_(s-1), hence L_s=(2^s+1)L_(s-1), with L_0=1.

There are fewer than 2^(2r+1) possible mu. Using 2^i+1<=2^(i+1), the total number of exceptional V is bounded above by

 #exceptional <= 2^((r(r-1))/2+3r).

The union bound is valid even without uniqueness of mu; uniqueness was established separately above. Every exceptional V is trace-active and excludes 1, but the upper bound need not use those additional restrictions.

## 6. More trace-active UNSAT subspaces exist than exceptions

Use the population A of all k-subspaces with 1 not in V and trace nonzero on V. Put a=2^r, q=2a², b=2a. The preceding trace-active counting note establishes, when the elliptic Frobenius trace t_n>=0,

 E_A[N_V]=a(2a²-3-t_n)/((a+1)(a²-2)).

Every positive N_V is an even integer at least two. Thus the UNSAT fraction is at least

 delta=1-E_A[N_V]/2
       >=(2a²-a-4)/(2(a+1)(a²-2)).

For a>=4 this is greater than or equal to 1/(4a): the numerator is at least a² and the denominator is less than 4a³.

The total number of k-subspaces in n dimensions is at least 2^(k(n-k))=2^(r(r+1)), by the product formula for the Gaussian binomial coefficient. The fraction excluding 1 is (q-b)/(q-1)>1/2, and, within that population, the trace-active fraction is 1-1/b>=3/4. In particular

 #A >= 2^(r(r+1)-2).

Consequently the number of trace-active UNSAT subspaces is at least

 #UNSAT in A >= 2^(r²-4).

For r>=7 this exceeds the exceptional upper bound, because

 r²-4 > r(r-1)/2+3r.

Therefore, whenever r>=7 and t_(2r+1)>=0, some trace-active UNSAT V is not exceptional. For that V, Sections 2–3 give 1 not in W2; unsatisfiability and the closure/refutation bridge imply

 d_LFD(F)>=3.

The preceding `trace-active-unsat-family.md` proves that t_n>0 for infinitely many odd n using the irrational Frobenius angle of E/F2. Discarding the finitely many n<15 leaves infinitely many parameters satisfying the required r>=7 threshold.

## 7. Exact scope of the progress

This proves that the infinite trace-active UNSAT construction is not forced to be degree-two easy: infinitely many admissible subspaces avoid the complete rank-one exceptional condition and require degree at least three. It also proves the same lower bound for every member of the exactly-two-solution containing-1 family.

The lower bound remains constant. No statement here shows absence of 1 from W3, absence of linear ideal generators from W3 on the SAT family, or growth with n. The next genuinely stronger step is to classify degree-three saturated consequences beyond the explicit trace/Frobenius identities and bound the exceptional family for a larger D. The degree-two count does not automatically iterate: W3 includes many new consequences, so replacing D=2 by a symbolic D without a new closure theorem would be invalid.

All existence choices remain nonconstructive or finite-enumeration specifications. The target remains order four, as in the companion notes. No prime-order-target or typical-case cryptographic claim is made.

Sources: local theorem dossier Proposition 2.6 for the exact W2 affine-part conclusion; local count-controlled and trace-active family proofs for solution-count expectations and Frobenius subsequence. New bilinear-form and subspace-count deductions are explicitly proved above and await independent review.
