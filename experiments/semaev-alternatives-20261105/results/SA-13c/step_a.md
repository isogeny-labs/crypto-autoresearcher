# Step (a): removing H-sep. RESOLVED NEGATIVELY WITH A REPAIR (see A4): the classification without H-sep is complete (A1),
# Case B is bounded without H-sep (A2), Case A is bounded without H-sep for full boxes (A3), but for small boxes H-sep is
# NOT removable: the lattice (S^2, pS, p^2) contains non-polynomial certificates (squares of short lifts of S_x mod p) whose
# coverage is ~ omega^{3/10}, far above omega^{1/15} (A4, proved and measured). H-sep is therefore a hypothesis on the
# scheme class, and it holds automatically for p-independent polynomial schemes on factor-base decompositions (A4).

## A1. H-sep-free formulation (PROVED)
Fix an integer pair x (1 <= x1 <= x2 < p), S = S_x(T) = G0 + G1 T + G2 T^2. The level-2 certificate lattice is
  Lambda_x = { u in Z^5 : u(T) in (S^2, pS, p^2) subset Z[T] }  (u(T) = sum u_j T^j).
Every level-2 scheme psi(X,p) with sum psi_j T^j in (S^2, pS, p^2) over Z[p,X,T] evaluates into Lambda_x, so the covered set of a
box W is contained in  cov2(W) := #{x : Lambda_x meets box(W) \ 0}.  No digit hypothesis is used.
Structure: Lambda_x = Z s2(x) + p Z{s, Ts, T^2 s} + p^2 Z^5 (s = coefficient vector of S, s2 of S^2), and p s2 = G0 (ps) + G1 (pTs)
+ G2 (pT^2 s). If p does not divide N0 (content lemma) and S_x != 0 mod p, Lambda_x / p^2 Z^5 has order p^2 * p^3 / p = p^4, so
  det Lambda_x = p^6   (the oracle's kernel lattice L_{p^2}(T) has det p^2; Lambda_x is a sublattice of index p^4 in it).
Equivalent root form (PROVED): with tau_1, tau_2 = x(P1 + P2), x(P1 - P2) in F_p the roots of S_x mod p, u in Lambda_x iff
p^2 | u(tau_i~) for every lift tau_i~ and both i, iff p^2 | u(tau_i) and p | u'(tau_i) (Taylor). So Lambda_x depends only on
(tau_1, tau_2) mod p and the question is a question over F_p^2, not a short-interval question in Z/p^2.
Trichotomy for a nonzero u in Lambda_x with |u_j| <= Wj < p^2/2: write u = c s2 + p w (w mod p in V_x = span(s,Ts,T^2s)).
  Case A: p does not divide c  (u mod p = c S_x^2 mod p != 0);   Case B: p | c  (u mod p = 0, u/p in V_x + pZ^5).
H-sep's branch k* = 0 is Case A with w = 0; branch k* = 1 is Case B with u/p = q(T) S exactly over Z. Everything else is wraparound.

## A2. Case B without H-sep (PROVED): coverage <= K_B max(1, omega/p^2)
Let u = p v, v in Z^5, |v_j| <= Aj = Wj/p < p/2, so v is the symmetric lift of v mod p, and v mod p = beta S_x mod p with beta in
F_p[T]_{<=2}, beta != 0 (beta = 0 would give u in p^2 Z^5, impossible in the box). So S_x | v in F_p[T] and v != 0.
Dual count. For a fixed nonzero v in F_p[T]_{<=4}: the x in F_p^2 with S_x | v satisfy S_x = lambda m for a monic factor m of v
(<= 6 quadratic, <= 4 linear factors). For a monic quadratic m: {x : G0 = m0 G2, G1 = m1 G2} is the intersection of two plane curves
of degrees 4 and 3 in (x1, x2); it has no common component (a one-parameter family of pairs with x(P1+P2), x(P1-P2) fixed is
impossible: 2P1 in {+-Q1 +- Q2}), so Bezout gives <= 12 points. For a linear factor (G2 = 0 mod p, x1 = x2 = x): <= 4 values of x.
Hence #{x : S_x | v} <= 6*12 + 4*4 = 88 for every v != 0, and
  cov_B(W) <= 88 * #{v in box(A) \ 0, v != 0 mod p} <= 88 * prod_j (2 floor(Aj) + 1).
Let J = {j : Wj >= p}. Coordinates outside J are 0, so the product is <= 3^{|J|} Pi_J, Pi_J = prod_J Aj <= omega / p^{|J|}.
If |J| <= 1, v is a monomial and S_x | v_j T^j forces S_x proportional to T^2, T or 1: at most 12 + 4 + 3 pairs x (constant).
If |J| >= 2: cost >= omega/p^2 >= Pi_J and cov_B <= 88 * 243 Pi_J. So  cov_B(W) <= 21384 max(1, omega/p^2) + 19.
This is the H-sep-free version of step (b): it covers q(T) S over Z (step (b)) and every wraparound variant of it, by a different
argument (mod-p divisibility + Bezout instead of Gelfond + the level-1 volume lemma). Numerical check: exp_a_caseB.py.

## A3. Case A without H-sep: PROVED for full boxes, OPEN for small boxes
Fixed u with u mod p = c m^2 (c in F_p^*, m monic quadratic; the monic square root is unique). u in Lambda_x forces S_x proportional
to m mod p, hence x is one of <= 12 residue pairs (A2), and x_i < p makes the residue pair the integer pair. So
  cov_A(W) <= 12 * #{u in box(W) \ 0 : u mod p in Sq},   Sq = {c m^2} (|Sq| < p^3).                         (A3.1)
Full boxes (all Wj >= p/2): #{u in box : u = r mod p} <= prod_j (2Wj/p + 1) <= 4^5 omega/p^5, so
  cov_A(W) <= 12 * p^3 * 1024 omega/p^5 = 12288 omega/p^2 <= 12288 cost(W).                                   (PROVED)
Together with A2: for every box with min_j Wj >= p/2, cov2(W) <= 33672 cost(W) with no hypothesis at all. (Honest remark: this
is subsumed by the trivial count. There are at most p^2/2 pairs x, so for omega >= p^4, cov2(W) <= p^2/2 <= cost(W)/2 for every box;
full boxes have omega >= (p/2)^5 > p^4. The H-sep-free question is therefore non-trivial only for omega < p^4, and there A4 answers it.)
Small boxes (some Wj < p/2): (A3.1) is still valid but the count of u is dominated by vectors that are genuine small squares
c m^2 over Z (about omega^{3/10} of them for balanced boxes, exponent 1/5 in the worst direction), which is far above the
structural omega^{1/15}. The structural bound (step_volume.md) needs u = c s2(x) exactly, i.e. the k* = 0 digit statement; a
wraparound vector u = c s2(x) + p w with w != 0 would require s2(x) mod p^2 to land in the box by accident. For each x this has
heuristic probability 32 omega / p^6 (the p^4-element group Lambda_x / p^2 Z^5 against a box of p^{10}/(32 omega) residue classes),
so the heuristic wraparound coverage is 16 omega/p^4 in total, ratio 16/p^2 to the cost. I could not prove it: the obstacle is an
equidistribution statement for the second p-adic digit of x -> s2(x) over x in F_p^2 (A1 removes the short-interval aspect, but the
digit map is still a degree-8 map into F_p^5 with a codimension-2 target, and the error term of the natural Fourier argument is
O(p^3), which is below the cost only for omega >= p^5, the full-box regime already proved directly).
What suffices instead of H-sep (PROVED equivalence): the cost bound Omega(p^{13/15}) needs exactly
  (H-A) for boxes with min_j Wj < p/2:  #{x : exists u in Lambda_x meets box, u mod p != 0, u not proportional to s2(x) over Z}
        <= C p^{2/15} max(1, omega/p^2).
(H-A) is weaker than H-sep (it allows arbitrary wraparound in Case B and in full boxes, and arbitrary multipliers alpha(X)), and
it is the single remaining unproved step of the level-2 bound. Its heuristic value is 16 omega/p^4 << 1 for omega < p^4.
Numerical check: exp_a_caseA.py enumerates Lambda_x meets box exactly (fpylll) for all x in F_p^2 at p = 101 and classifies
every covered x as structural (x in Phi2), Case-A wraparound, or Case B.

## A4. Why H-sep cannot be dropped: squares of short lifts (PROVED), and the repair (PROVED)
Construction. Let m' in Z[T] be any quadratic with m' = lambda S_x (mod p) for some lambda in F_p^* (a "lift" of the projective
point (G0:G1:G2) mod p). Then m' = lambda S_x + p beta' over Z (lambda now an integer representative, beta' in Z[T]_{<=2}) and
  m'^2 = lambda^2 S_x^2 + p (2 lambda beta') S_x + p^2 beta'^2  in (S^2, pS, p^2),  so  u := coef(m'^2) in Lambda_x.
Equivalently, in the root form of A1: m'(tau_i) = 0 mod p so m'^2(tau_i~) = 0 mod p^2 for every lift. Nothing about x is used.
Coverage. x is covered by a box W as soon as SOME lift m' of (G0:G1:G2) mod p has coef(m'^2) in the box. The number of integer
quadratics m' with coef(m'^2) in the box is about #{(m0,m1,m2) : m0^2 <= W0, 2|m0 m1| <= W1, m1^2 + 2|m0 m2| <= W2, 2|m1 m2| <= W3,
m2^2 <= W4}, which for the balanced box Wj = B^{8-j} is about B^9 = omega^{3/10} (m ~ (B^4, B^3, B^2)), and each m' covers the
<= 12 pairs x with S_x proportional to m' mod p. The x's covered this way are arbitrary residues in F_p^2 (the pairs whose S_x mod p
happens to have a short lift), not small integers, so this coverage is omega^{3/10} against the structural omega^{1/15}.
Consequence in model CE2 as stated (success = "the answer contains a certificate of SOME decomposition x of the target"):
a balanced box with omega = p^2 (cost O(1)) covers about 12 p^{3/5} pairs, success probability about 48 p^{-2/5} per unit cost,
i.e. "cost per relation" p^{2/5}: the level-2 bound is FALSE without H-sep, and so is the level-1 bound without H-int (the same
mechanism at level 1: any short lift m' of S_x mod p is itself in L_p(x(R)); it is the decomposition R = P1 + P2 with
P1 = (R+Q)/2, P2 = (R-Q)/2 for an arbitrary point Q read off from the oracle's vector). These relations involve arbitrary points,
so they are useless for index calculus; the defect is in the success criterion of CE/CE2, exactly as in SA-13 section 1 for the
literal lattice-query model. Measured (exp_a_caseA.py, p = 103, all 1431 pairs with distinct roots): every covered pair in every
box is of this kind ('A_sq'), none is structural, and the count follows 12 * #{m'} rather than the random heuristic 16 omega/p^4
(e.g. 25 covered pairs at omega = p^{2.5} against a heuristic 0.004).
Repair (what suffices instead of H-sep; PROVED). Restrict success to factor-base decompositions x in [1,B]^2 and schemes whose
digit polynomials are p-independent: psi = psi_0 + p psi_1 + p^2 (anything), psi_0 = alpha(X) s2(X), psi_1 = beta(X,T) S, with
alpha, beta in Z[X] (resp. Z[X,T]) of degree <= d and height <= H (SA-13b 3.3 step 1 gives this shape from the ideal identity with
p an indeterminate). Digit uniqueness only needs the LOWEST nonzero digit to be < p/2 in every coordinate (if the tail is a nonzero
multiple of p, |psi_{k*,j} + tail| >= p - |psi_{k*,j}| >= |psi_{k*,j}|). On x in [1,B]^2 the lowest digit is bounded by
C_S H B^{d+8} (C_S = sup of the s2 coefficient sizes at x = 1: for y^2 = x^3 + 7 the entries of s2 are <= 10 (x1 x2)^4 for
e2 >= M). Hence  H-sep holds for all x in [1,B]^2 whenever  C_S H B^{d+8} < p/2,  which includes the whole index-calculus regime
B <= p^{1/15} once d + 8 <= 14 (d <= 6) and H < p^{1/15}/(2 C_S). Under this restriction the k* analysis of SA-13b 3.3 is exact,
and the level-2 theorem follows from step_b.md and step_volume.md:
  Theorem L2 (class CE2-na, polynomial schemes with C_S H B^{d+8} < p/2, factor base [1,B]):  for every level-2 box,
  Pr[success] <= 4 (C_2 omega^{1/15} + M(1+ln M) + K_b cost(W)) / N, hence cost per relation Omega(p^{13/15}).
Status of "remove H-sep": it cannot be removed from the lattice formulation (false), it is not needed for Case B or for full boxes,
and it is implied by bounded scheme complexity on the factor-base range. The equidistribution question of the earlier version of A3
(random wraparound) is not the issue; the structured short-lift squares dominate it by far.
