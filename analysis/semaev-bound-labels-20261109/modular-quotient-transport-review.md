# Independent review: modular correction and quotient-variable transport

Date: 2026-11-09. Source-only review of `modular-quotient-transport.md`. No execution.

**The correction identities, half-diagonal section, and factor-two strict refutation transport are correct.**

Polynomial division in T is linear on coefficient functions. Hence the quotient coefficients h_j retain Boolean degree at most two. Differentiating F=P Q at a solution gives p'=P'Q+P Q'; separability makes P' invertible modulo P. When deg Q<n, the displayed modular expression uniquely determines Q. On n=2r+1 its degree bound 2r-1 is indeed below n.

The positive-index dyadic telescoping functional C_d is the previously checked exact formal identity. Applying it to P Q yields the stated error term, rather than a new affine zero relation. Thus neither the no-wrap square-root argument nor the leading-polynomial-degree contradiction survives after merely imposing the remainder equations.

For odd n, ker(A) is F2 and intersects the trace-zero subspace trivially, while A maps that subspace to itself. Its inverse J is therefore binary-linear. With Tr(s)=0, A(J(s)²)=s², and the two solutions for p differ by the constant bit one. Since J(s) has trace zero, epsilon=Tr(p). This verifies the single-bit presentation without importing a false low-T-degree polynomial square root.

For the quotient extension, taking remainder and quotient is an invertible linear coefficient operation on the bounded polynomial space. Thus the full coefficient equations F+PZ have exactly the claimed row span R together with z_j+h_j. After sigma:z_j->h_j, their images are remainder-row combinations. For D>=2 all these source rows are eligible. Substitution of a source polynomial of degree at most D-1 has degree at most 2(D-1); multiplying by one quadratic h_j can be implemented one variable at a time within cap 2D. This proves the transfer regardless of the number of auxiliary bits.

The numerical refutation comparison is valid with the stated cap-at-least-two qualifier. To remove any ambiguity about low-cap row exposure, an entirely unconditional truncated formulation is

    max(2,e_G) <= max(2,e_R) <= 2*max(2,e_G),

for UNSAT instances. The simpler e_G<=e_R follows whenever e_R>=2. At caps zero or one row combinations may expose affine or constant generators, so that qualifier should remain attached. This does not affect growing-degree transfer.

If 4r<n there are no quotient variables; the construction can be read with an empty quotient list. In its intended modular regime 4r>=n the stated degree bound and variable count are literal. Setting the quotient to zero imposes the full unreduced coefficient system, whose uniform cap-four proof concerns those formal coefficient equations; it does not remove modular corrections from the original remainder system without adding constraints.

The note correctly does not infer unrestricted SAT LFD equivalence from degree-doubling substitution. Degree of a target consequence can change, and a separate affine-ideal or count-controlled bridge is necessary. No substantive correction is required beyond preserving the explicit low-cap qualifier.
