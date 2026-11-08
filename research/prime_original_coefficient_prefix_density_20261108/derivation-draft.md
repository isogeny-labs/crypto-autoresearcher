# Nonvanishing conditional rejection after the global envelope

UNREVIEWED source-only derivation. This counts an explicitly stated auxiliary-prefix domain, not solver trajectories, nonempty original coefficient fibers or measured performance.

Let h in{3,4,5}, M=B−1>=1, K=h(h−1)M²/2, d=ceil(log2(K+1)), H=2^d. Assume hM<p and H<p; hence d<ell=ceil(log2 p) and at least one E value bit remains syntactically unassigned. The original coefficient variables are not assigned by the moment-prefix record. All source/stratum/interval and linked-moment premises of the published semantic interface remain required.

For offsets a_i in[0,M], their integer sum S lies in[0,hM], and E=sum_(i<j)a_i*a_j lies in[0,K]. There is no wrap in S or E under these assumptions, since K<H<p. This global E envelope is already cheap and must be the baseline; counting exclusions r>K as a benefit of conditioning on S would overstate the construction.

Take the domain D of pairs (S0,r) with 0<=S0<=hM and 0<=r<=K, where all S bits are fixed and only the d low E bits are fixed to r. There are (hM+1)(K+1) pairs. Because H>K, the only integer in[0,K] congruent to r modulo H is r itself. The other canonical field completions, if any, exceed the global envelope. Thus D records exactly the prefixes still possible after the global trace/E envelopes, not after original arithmetic constraints.

For every S0 in[0,M], Cauchy's elementary sum-of-squares inequality gives sum a_i² >= S0²/h and therefore E <= (h−1)S0²/(2h) <= (h−1)M²/(2h)=K/h². Consequently every integer r with floor(K/h²)<r<=K is rejected by the existing necessary-interval arc test at each such S0. The sharper balanced integer endpoint can only reject more. No support enumeration or coefficient grid is needed.

At least

  (M+1) * (K−floor(K/h²))

pairs in D are excluded, a fraction at least

  [(M+1)/(hM+1)] * [(K−floor(K/h²))/(K+1)].

For fixed h and growing M this lower bound tends to (1/h)(1−1/h²), positive for all three arities. This is an asymptotic family assertion conditional on primes satisfying the stated inequalities, not an asymptotic assertion for fixed p or all admissible B. For every finite M the displayed rational bound is the exact guaranteed lower bound. The excluded low prefixes are canonical-completable (r<=K<p). The semantic clause still fixes all ell S bits and d E bits; it is not a projected-only clause. It excludes every completion in the original interval source regardless of unassigned coefficients and witnesses.

Checking one proposed exclusion costs the previously derived O(h) endpoint integer operations plus O(ell) parsing/literal/authentication work. Enumerating all D or emitting every guaranteed clause would cost Theta(B³) in this no-wrap regime; that is explicitly not proposed. Query clauses on demand, cache only authenticated fixed-S intervals, and charge all compilation/new-variable/proof/model work.

The result resolves one narrow gap: useful partial-prefix exclusions need not have a vanishing density relative to the cheap auxiliary envelopes. It does NOT establish that a real search reaches these branches, that original coefficient assignments distribute across D, or that those branches were not already eliminated by other source reasoning. S,E are linked auxiliaries, not newly independent projected coordinates. A coefficient-ordering and cost theorem or bounded implementation evaluation remains necessary to establish end-to-end gain. No degree-of-regularity reduction follows from this cardinality statement.

Boundary controls: M0 outside theorem; hM>=p allows sum aliases; H>=p eliminates the claimed incomplete-bit guarantee or wraps moment values; denominator must retain the global-envelope baseline, not all field pairs; impossible original fibers are not counted as useful search visits; passing interval bounds is not a witness. Saturated cases require the earlier complete lift/arc algorithm and have no density conclusion from this proof.
