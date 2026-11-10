# Independent review: factorized quotient obstruction

2026-11-10. Source-only review of `uniform-quotient-algebraic-20261110.md`; no computational experiment or build.

Accepted. The proposed tensor factorization cannot certify an UNSAT normalized m=2 Semaev instance. The source proof is sound, and its central existence conclusion admits the following shorter, more general proof.

Let u0=Cx(1), v0=Cy(1), both nonzero. Choose arbitrary linear functionals phi,psi with phi(u0)=psi(v0)=1 on the respective affine-column spans. Define Boolean assignments alpha_i=phi(Cx(x_i)) and beta_j=psi(Cy(y_j)). Every normalized input row has the form

    constant + sum a_i x_i + sum b_j y_j + sum c_ij x_i y_j.

Applying phi tensor psi to its vanishing image under C gives exactly its evaluation at (alpha,beta), because the only quadratic terms use one coordinate from each block. Thus every such pair of normalized functionals produces an actual solution. No kernel closure or higher-degree columns are needed.

More strongly, the assignments obtained from all normalized functionals form affine subspaces A,B in the two Boolean coordinate blocks, of dimensions dim(Ax^1)-1 and dim(Ay^1)-1. Their entire Cartesian product lies in the actual zero set. The field-coordinate maps are injective because the supplied v_i form a basis, so this is also an affine solution rectangle in V x V.

The source's additional field-specific restriction is correct: applying functionals vanishing on u0 and v0 forces (uw)^2+zuw=0 for all variation directions u,w. Since z is nonzero, the kernel of p->p^2+zp is {0,z}. When both variation spaces are nonzero, each has dimension one. The source's four independent tensor coordinates then force all four points of the rectangle to solve the equations. Its constant-block affine-consistency proof is also valid, though the normalized-functional proof already covers it.

The direct-sum claim is correct provided each component separately annihilates every input: a component with nonzero constant image supplies a solution. A correlated sum with cancellations is outside this argument. Likewise the obstruction does not establish a SAT LFD bound or constrain arbitrary high-degree images without the separately required closure conditions.

The shortcut's precise hypothesis is block-bilinearity of the normalized input rows. Arbitrary nonlinear within-block monomials would not evaluate correctly under a freely chosen functional unless additional multiplicative identities were proved. The current Semaev normalization satisfies the hypothesis because Frobenius squaring is linear on the Boolean coordinate functions.

Together with the operator review, this identifies two independently fatal restrictions on a uniform UNSAT quotient ansatz: full global commutation, and tensor-factorization of the two input blocks. Correlated, genuinely truncated columns remain a construction obligation; these obstructions do not supply them or a growing lower bound.
