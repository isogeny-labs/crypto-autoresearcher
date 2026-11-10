# Independent review: no-wrap dyadic coefficients and r=2

Date: 2026-11-09. Source-only review of `no-wrap-coefficient-progress.md`. No execution.

**The positive-index dyadic relations and both cap-two derivations are correct.** One constant-coefficient qualification should be explicit in the equivalent q presentation.

For j>0 the coefficient equation is f_j=p_j+[j even]*(p_(j/2)+s_(j/2)); f_0=s_0 because the two copies of p_0 cancel. Descending through even indices beyond 2r gives p_j=0 for j>r. The remaining odd p_j vanish, and p_(2j)=p_j+s_j. Iteration on each odd-index dyadic chain gives exactly the sum-of-s chain relation claimed. These deductions use linear combinations of original coefficient rows.

After imposing the affine constant equation s_0=x_0+y_0+1=0, one has y_0=x_0+1, hence p_0=x_0*y_0=0 in the Boolean ring. This is an affine substitution, or equivalently a cap-two derivation using x_0*s_0, not an initial linear combination of the coefficient rows in general. With this step included, p=q² with zero-constant q of degree at most floor(r/2), and s=q²+q. The positive-index q coefficients are linear functions of s, uniquely determined because a zero-constant polynomial lies in the kernel of q->q²+q only when q=0. Thus the note's equivalent presentation using row operations AND affine substitutions is correct; it should not be shortened to a claim of row-span equivalence before eliminating s_0.

For r=1, b+d and bd are available at cap two; multiplying the affine b+d by b gives b+bd and hence b. This directly derives the full affine ideal. For r=2, after d=a+1,e=b+s,f=c+s, the four displayed expressions for p1,p3,p4,p2 are correct and their sum is identically zero. Combining the available p1,p3,p4,p2+s derives s. Strict cap-two multiplication by a or c then removes as or cs, deriving b,c and the remaining affine ideal. Every substitution correction to a quadratic row is a product of a known affine equation with an affine cofactor, so no cap-three step is hidden.

In the stated original polynomial-coordinate input presentation, these examples actually have exact LFD2: at cap one only the constant-index affine input x_0+y_0+1 is available, so a positive-index coordinate vanisher is missing. This extra exactness is not needed for the published upper bounds and should not be assumed invariant under arbitrary output row-basis changes at cap one.

The highest-polynomial-degree solution argument does not by itself supply an all-r cap-two derivation. The report correctly keeps that induction or counterexample as the unresolved general step. No growing lower bound or uniform all-r degree bound is established by this note.
