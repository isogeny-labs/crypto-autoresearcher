# Quantitative density obligation for simultaneous low count and high LFD

Date: 2026-11-09. Source-only deduction from the independently reviewed two-solution existence theorem. No experiment, matrix construction, build, or cloud job. This note proves a positive finite-size density bound and identifies the precise additional exceptional-set estimate sufficient for unboundedness. It does not establish that estimate.

## 1. Exact population and a proved density bound

Let n=2r+1>=3, k=r+1, a=2^r, K=F_(2^n), and let Omega_r be the uniform finite population of k-dimensional binary subspaces V containing 1. Its cardinality is the Gaussian binomial coefficient

    T_r = [2r choose r]_2.

Use z=a6=1 and the normalized Boolean descent of

    F(x,y)=x²y²+xy+x²+y²+1.

Write N_V for the number of ordered zeros in V², S_r={V:N_V=2}, and t_n for the Frobenius trace of E:Y²+xY=x³+1 over K. The reviewed algebra gives N=2a²-1-t_n full-field zeros, N_V even and at least two, and

    p_r = (a-2)/((a+1)(a²-2)),
    E[N_V-2] = (2a²-3-t_n) p_r.

The formula includes r=1, when p_r=0. Put J_V=(N_V-2)/2, a nonnegative integer. Since 1[J_V>=1]<=J_V,

    Pr(S_r) >= delta_r := 1 - (2a²-3-t_n)p_r/2
      = (6a²-a-10+t_n(a-2))/(2(a+1)(a²-2)).              (1)

This is an exact lower bound from the first moment, not an assertion that the density equals delta_r. It is never greater than one, since N>=2. No independence assumptions enter.

Using only the weaker bound already employed in the companion proof gives the explicit positive bound

    Pr(S_r) >= delta_r >= delta_safe(a)
      := 3(a+2)(a-1)/(2(a+1)(a²-2)) > 0.                (2)

Indeed (N-2)<=2a²+3a-1 and

    2(a+1)(a²-2)-(2a²+3a-1)(a-2)=3(a+2)(a-1).

Thus |S_r|>=ceil(T_r*delta_safe(a)). The density lower bound tends to zero, approximately (3/2)*2^(-r); this is not a uniform positive-density theorem. The absolute lower count is nevertheless large because T_r is of order 2^(r²).

One may retain the stronger Hasse estimate to replace (2) by

    delta_H(a)=(6a²-a-10-2sqrt(2)*a*(a-2))
                /(2(a+1)(a²-2)),

or use the exact integer recurrence t_0=2, t_1=-1, t_n=-t_(n-1)-2t_(n-2) in (1). No point-count execution is needed to state these formulas. These first-moment bounds remain of order 1/a.

## 2. A precise low-degree easy set

Fix an exact field representation and a deterministic ordered V basis beginning with 1, so coordinate inputs and strict closure W_D are unambiguous. Let the x and y coordinate bits be A_i,B_i, i=1,...,k. Define the fixed list of affine forms

    L_V = { A_i,B_i : 2<=i<=k } union { A_1+B_1+1 }.

For each V, define

    E_(r,D) = { V in Omega_r : every ell in L_V belongs to W_D(F_V) },

where D>=2 and F_V is the original normalized quadratic coordinate input list with the agreed Boolean convention. This is a statement about full saturated degree-limited closure, not the initial Macaulay row space or an F4 prefix.

Every V in E_(r,D) necessarily belongs to S_r: W_D is contained in the Boolean vanishing ideal, so its zeros obey all these affine equations, while the two known zeros always remain. Within S_r, these forms generate the whole Boolean vanishing ideal. If all are in W_D, their arbitrary consequences can be derived at cap max(D,degree f): after an invertible affine coordinate change, their ideal is a coordinate ideal, so a polynomial vanishing on the line decomposes into these generators without increasing its degree. Multiplication of generators and return to the original coordinates preserve that degree bound. Consequently

    E_(r,D) = S_r intersect { V : d_LFD(F_V)<=D }.       (3)

Conversely, the defining LFD property implies membership of each degree-one ideal generator in W_D whenever d_LFD<=D. This proves the other direction of (3). The coordinate changes here concern derived affine ideal generators and degree-preserving reasoning; no unqualified low-cap input-row invariance is being assumed.

For any V in S_r outside E_(r,D), some named linear vanisher is missing from W_D, which directly implies d_LFD(F_V)>=D+1. This is the precise lower-bound witness required by this route.

## 3. Sufficient exceptional-set inequalities

The following inequalities would suffice, in decreasing order of information available:

    |E_(r,D)| < |S_r|;                                 (exact criterion)
    |E_(r,D)| < T_r*delta_r;                           (using exact trace)
    |E_(r,D)| < T_r*delta_safe(a).                     (uniform sufficient bound)

A slightly sharper integer formulation is |E_(r,D)|<=ceil(T_r*delta)-1, where delta is either proved density lower bound. This leaves at least one qualifying V with LFD>D. Equivalently, any proved bound Pr(E_(r,D))<delta suffices. A bound on the larger set {V:d_LFD(F_V)<=D} is also sufficient, but is stronger than necessary and may waste information from nonqualifying subspaces.

For unboundedness, it is enough to establish such an inequality for arbitrarily large D, allowing r to depend on D. To obtain an explicit rate, establish it for an infinite sequence r_j with a specified D_j tending to infinity; then the selected systems satisfy d_LFD>=D_j+1. No claim of a rate follows without such a choice and proof.

For example, a rigorous upper bound Pr(E_(r,D(r)))=o(2^(-r)) along a sequence with D(r) tending to infinity would suffice by (2). This is a demanding exponential-in-r exceptional-set estimate, not an estimate furnished by the present counting proof. It is sufficient, not necessary: the true density of S_r could be much larger than our first-moment lower bound.

## 4. What a valid dimension-count argument still needs

The Grassmannian population is finite over F2, with dimension and field degree linked. The original equation coefficients are correlated polynomial functions of a V basis, and the basis must have full rank and contain 1. Neither generic rank over an algebraic closure nor a real-valued heuristic for random matrices bounds |E_(r,D)| in this finite population.

Moreover, W_D is the fixed point of repeated linear combinations and degree-limited multiplications of every newly derived low-degree consequence. A rank bound on only the initial Macaulay matrix does not characterize it. Any matrix or determinantal encoding used for E_(r,D) must first be proved equivalent to saturated closure membership, including cancellations that drop degree.

It is invalid to count a nonzero polynomial equation as having tiny probability merely because the coefficient parametrization is algebraic: over F2, a formally nonzero polynomial can vanish on all Boolean parameter values. Basis parametrizations also overcount each subspace; that multiplicity must be uniform or explicitly corrected, and the conditioning on the distinguished vector 1 must be retained.

A useful next theorem would therefore be a concrete combinatorial or algebraic upper bound on the exact easy set E_(r,D), or a direct lower bound on S_r minus E_(r,D). No such bound is proved here. The existing solution-count theorem supplies the explicit target inequality (1)-(3), not a genericity assumption that settles it.
