# Independent review: actual-field coupling and embedding restrictions

Date: 2026-11-09. Source-only review of `field-coupling-and-embedding-obstruction.md`. No execution.

**The stated coefficient identities and restricted embedding obstructions are correct.**

The normalized Boolean coefficient expansion follows because Frobenius squares fix Boolean variables and eliminate cross terms within each squared sum. For z=1, the diagonal coefficient has unreduced degree exactly 4deg(v_i) for each nonconstant representative. A k-dimensional polynomial-coordinate subspace needs a basis representative of degree at least k-1, giving the necessary no-wrap condition 4(k-1)<n. This indeed fails at k=ceil(n/2) for every n>=3. It concerns the full actual coefficient representation; discarding or replacing modularly reduced coordinates would change the system.

Since u²+zu=u(u+z), a cross coefficient vanishes precisely when the corresponding nonzero basis product is z. Distinct nonzero vectors give at most one such partner per row and column. Invertible output-coordinate changes preserve whether a full coefficient vector is zero; separate invertible changes within the X and Y blocks merely choose new bases. This proves the dense-interaction restriction exactly within the stated transformation class. It does not extend to arbitrary affine mixing, nonlinear substitutions, or coefficient subsets, which the note explicitly excludes.

The reconstruction v_i=sqrt(L_i)/z and compatibility identity C_ij=L_i*L_j/z⁴+sqrt(L_i*L_j)/z have the correct powers of z. Independent L_i recover an independent basis because squaring and nonzero scaling are binary-linear automorphisms. Constant term c!=0 yields a6=c, so necessity and sufficiency hold for the specified zero-origin K-valued polynomial. Separate bases require the corresponding two linear coefficient lists and equality of their recovered spans, as stated.

For the top tensor alone, U_ij=v_i*v_j/z is symmetric rank one and satisfies U_ij²+U_ij=C_ij/z². Conversely a symmetric rank-one lift with nonzero diagonal satisfies U_ij²=U_ii*U_jj; unique square roots recover U_ij=v_i*v_j/z. Independence of the recovered v_i remains a necessary separate condition. Trace-zero compatibility gives the Artin-Schreier lifts but does not itself guarantee rank one. All these restrictions concern actual field elements, not freely chosen coefficient vectors.

The odd-diagonal product-span result makes the unnormalized C_ij span the n-1 dimensional image of u->u²+zu, while normalized C_ij/z² lie in the trace-zero space. The distinction is respected by the note. This top rank does not determine saturated higher-degree closure.

No mathematical correction is required. These are direct coefficient-recognition and transformation-scope results, not a lower-bound amplification or an arbitrary hard-MQ embedding.
