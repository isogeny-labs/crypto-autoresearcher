# Independent review: epsilon elimination and affine dual refutations

Date: 2026-11-09. Source-only review of `epsilon-elimination-dual-pencil.md`. No execution.

**The original-system elimination, separator conditions, and affine feasibility criterion are correct.**

Tracing G yields epsilon=Tr(xt)+Tr((1+e)x), since H and g have trace zero and Tr(x²)=Tr(x). Substitution gives the displayed F_t=pi(x²+(t+e)x)+H(t)+g. This lies in K0. Applying A to it recovers the original trace-sliced equation, and A is invertible on K0, so the claimed constant output-row equivalence is valid. The warning that substituting epsilon into xG can raise Boolean degree to three is necessary and correct.

The trace form restricted to K0 is nondegenerate in odd degree. For an UNSAT instance each fixed-t affine system has target outside its linear image, yielding a separator lambda in K0. Pairing with pi removes no information for such lambda, and adjoint squaring gives exactly condition (2). A polynomial separator of degree c produces a literal refutation by multipliers of degree at most c, at strict cap c+2. The original affine trace elimination is already available at cap two, so lifting that coordinate parametrization adds no degree overhead at these caps.

For affine lambda=a+L(t), expanding the annihilator condition gives its constant part (5), quadratic polarization (6), and residual linear part (7). Once (6) holds, the quotient class of tL(t) is binary-linear, so a basis test suffices. Expanding the normalization pairing gives constant Tr(ag), polarization (9), and residual (10). Again the remaining basis tests are sufficient after polarization vanishes. Every condition is linear in the unknown coefficients of a and L because H and all field operations on fixed arguments are prescribed.

For a constant separator, variation in t forces aW contained in V_perp. If span(VW)=K this leaves only a=0, incompatible with the normalization. This excludes the stated multiplier form, not arbitrary cap-two or cap-three derivations. Pointwise interpolation gives the general cap r+2 as an upper construction, while failure of the affine feasibility system cannot be promoted to full W3 nonrefutation without a separate normalization or stability theorem.

No mathematical correction is required. The result supplies a direct original-system criterion rather than relying on an auxiliary presentation's degree profile.
