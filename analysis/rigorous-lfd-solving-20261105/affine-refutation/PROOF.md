# Affine inconsistency and a scalar polynomial refutation

2026-11-05. Root proof construction, with no experiments or status changes.

Let k be a field, i and j finite row/variable index types, A=(a_ij), c=(c_i).
Assume there is no t in k^j with c_i+sum_j a_ij*t_j=0 for every i.
Then there are w_i in k such that

    sum_i w_i*c_i=1,  sum_i w_i*a_ij=0 for every j.

Let U be the span in k^i of A's column vectors. If c were in U, negating
its column coefficients would give a solution t, contradiction. Choose a
linear functional phi vanishing on U and nonzero on c, by separation in the
quotient vector space k^i/U. Its coefficients are phi(e_i). Scaling by
phi(c)^(-1) gives w_i. Applying phi to c and to each column proves the two
identities. Thus the actual polynomial identity is

    sum_i w_i*(c_i+sum_j a_ij*T_j)=1.

The Lean proof uses Mathlib's `exists_dual_map_eq_bot_of_notMem` for this
standard separation and derives the polynomial identity by finite-sum
expansion. It proves inconsistency over the COEFFICIENT FIELD. It makes no
false transfer from Boolean UNSAT to field inconsistency in odd
characteristic. Over k=F2, every field coordinate is Boolean, so the
hypothesis is exactly the required affine-fibre inconsistency.

`AffineFibreRefutation.lean` currently lives here as a compiling candidate
outside formal while another verification freezes formal/. build-01.log
preserves two unsuccessful rewrite steps; build-02.log proves the scalar
certificate; build-03.log proves both exact statements. Both successful
axiom outputs are only propext, Classical.choice, Quot.sound. Full formal
module staging and any verification receipts are recorded separately.
