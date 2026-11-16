# Step (b): the k* = 1 branch with general multipliers q(T). PROVED (with explicit constants).

Setting (SA-13b section 3.3). E: y^2 = x^3 + ax + b, integers a, b, b != 0. For integers 1 <= x1 <= x2,
S(T) = G0 + G1 T + G2 T^2 with G2 = (x2-x1)^2, G1 = -2(e1(e2+a)+2b), G0 = (e2-a)^2 - 4b e1 (e1 = x1+x2, e2 = x1x2).
Level-2 query: box W = (W0..W4), 1 <= Wj < p^2/2, omega = prod Wj; cost >= max(1, 2 floor(omega/p^2)) (van der Corput, index p^2).
Under H-sep the k* = 1 branch covers x iff some nonzero q in Z[T], deg q <= 2, has |coef_j(q S)| <= Aj := Wj/p for j = 0..4
(SA-13b 3.3 step 3; digit uniqueness gives |psi_{1,j}(x)| <= |v_j|/p when psi_{1,j}(x) != 0, and |v_j| < p forces v_j = 0, hence
psi_{1,j}(x) = 0 because |psi_{1,j}| < p/4; so the box is really floor(A), and coordinates with Wj < p are forced to zero).

Notation. J = {j : Wj >= p} (the coordinates that may be nonzero), Pi_J = prod_{j in J} Aj >= 1 (empty product 1),
A* = max_j floor(Aj) <= Pi_J. Then omega >= prod_{j in J} Wj = p^{|J|} Pi_J.

## Lemma B1 (extreme coefficients). PROVED.
Write q = T^l qt with qt(0) != 0, delta = deg qt in {0,1,2}. Then u = qS = T^l (qt S) and
  u_l = qt(0) G0,   u_{l+delta+2} = lead(qt) G2   (if G2 != 0).
Since qt(0), lead(qt) are nonzero integers, |G0| <= A_l and G2 <= A_{l+delta+2}. If G0 G2 != 0 then both indices lie in J
and they are distinct (delta + 2 >= 2), so |J| >= 2 and cost >= omega/p^2 >= Pi_J (because omega/p^2 >= Pi_J >= 1 and
2 floor(y) >= y for y >= 1).

## Lemma B2 (Gelfond). PROVED (standard).
For f, g in Z[T], ||f||_inf ||g||_inf <= 2^{deg f + deg g} ||fg||_inf  (Gelfond's inequality; e.g. Bombieri-Gubler, Heights in
Diophantine Geometry, Lemma 1.6.11 with the Mahler-measure chain ||f||_inf <= 2^{deg f} M(f), M multiplicative, M(h) <= ||h||_2
<= sqrt(deg h + 1) ||h||_inf; the sqrt factor is absorbed by using the sharper form, or kept: the constant below is K_G = 2^4 sqrt 5).
Applied to qt S = T^{-l} u with ||qt||_inf >= 1: every |G_k| <= K_G max_j |u_j| <= K_G A*,  K_G = 16 sqrt(5) < 36.

## Proposition B (coverage of branch k* = 1). PROVED.
Let c(U0,U1,U2) = #{1 <= x1 <= x2 : |G_k| <= U_k} (SA-13b Lemma 5: c(U) <= C (U0 U1 U2)^{2/9} + M(1+ln M), C = (9/5) 2^{2/3},
M = max(4|a|, 128|b|, 4), valid for U_k >= 1; for U_k < 1 replace U_k by 1, monotonicity).
Coverage of the branch, cov_b(W), is at most the sum over the 6 pairs (l, delta) of the counts below.

Case 1: G0 G2 != 0. By B1 and B2, x lies in c(A_l, K_G A*, A_{l+delta+2}), so
  count <= C K_G^{2/9} (A_l A* A_{l+delta+2})^{2/9} + M(1+ln M) <= C K_G^{2/9} Pi_J^{2/3} + M(1+ln M),
using A_l, A*, A_{l+delta+2} <= Pi_J. With cost >= Pi_J (B1): count/cost <= C K_G^{2/9} + M(1+ln M) =: K_1.

Case 2: G2 = 0, i.e. x1 = x2 = x. Then S = G0 + G1 T with G1 = -4 f(x), f = x^3 + ax + b, and G0 = x^4 - 2a x^2 - 8b x + a^2.
 2a. G0 G1 != 0: the extreme coefficients are qt(0) G0 and lead(qt) G1 at indices l != l+delta+1, so |J| >= 2, cost >= Pi_J,
     and |G0(x,x)| <= A_l <= Pi_J. For x >= M, G0(x,x) >= x^4/2, so the count is <= (2 Pi_J)^{1/4} + M <= 2 Pi_J + M.
 2b. G0 = 0: x is a root of the quartic G0(x,x), at most 4 values.  2c. G1 = 0: f(x) = 0, at most 3 values.

Case 3: G0 = 0, x1 < x2. Then S = T (G1 + G2 T).
 3a. G1 != 0: extreme coefficients qt(0) G1 (index l+1) and lead(qt) G2 (index l+delta+2), distinct, so |J| >= 2, cost >= Pi_J,
     |G1| <= Pi_J, G2 <= Pi_J. Count <= #{x : |G1| <= Pi_J, G2 <= Pi_J}. For e2 >= M, |G1| >= e1 e2 >= x1 x2^2 and
     x2 - x1 <= sqrt(Pi_J), so the count is <= sum_{x1 <= Pi_J^{1/3}} (2 sqrt(Pi_J)) + M(1+ln M) <= 2 Pi_J^{5/6} + M(1+ln M).
 3b. G1 = 0 too: G0 = G1 = 0 forces e1 = (e2-a)^2/(4b) and (e2-a)^2 (e2+a) = -8b^2, a cubic in e2: at most 3 pairs.

Summing the six (l, delta) pairs and the cases:
  cov_b(W) <= 6 [ K_1 Pi_J + 2 Pi_J^{5/6} + 2 Pi_J + 2 M(1+ln M) + 10 ]  and  cost >= Pi_J whenever the Pi_J terms are nonzero.
Therefore   cov_b(W) / cost(W) <= K_b := 6 (K_1 + 4 + 2M(1+ln M) + 10)   for every level-2 box W.         (QED)

Sharper form actually proved in Case 1 (the generic case): cov_b(W) <= 6 C K_G^{2/9} (omega/p^2)^{2/3} + const for omega >= p^2,
and cov_b(W) <= const for omega < p^2. In the language of the pre-registration the branch has coverage exponent 2/3 in omega/p^2
and, measured against the k* = 0 branch (coverage C omega^{1/15}, cost max(1, omega/p^2), ratio maximal C p^{2/15} at omega = p^2),
its contribution to success-per-unit-cost is O(1/N) instead of O(p^{2/15}/N): it never dominates. Prediction "(b) holds with
exponent >= 1/15" is met, in the stronger sense that the branch is negligible.

Why SA-13b's Mahler argument lost p^{1/3}: it bounded all three |G_k| by the maximum weight and then counted omega >= p A*
(one coordinate). The repair is that a nonzero product q S always has two nonzero extreme coefficients at distinct indices
(B1), which forces |J| >= 2, omega >= p^2 Pi_J, and gives the two extreme |G_k| the sharp bounds A_l, A_{l+delta+2} for free.

Limits. The statement is inside H-sep (no wraparound), as is the whole k* classification; removing H-sep is step (a).
Constants are crude (K_G = 16 sqrt 5; M(1+ln M) = 896 (1 + ln 896) = 6986 for y^2 = x^3 + 7); nothing depends on them.
Numerical check: exp_b_branch_coverage.py computes cov_b(W) exactly for many boxes (exact enumeration of q) and reports
sup cov_b/Pi_J and sup cov_b/Pi_J^{2/3} (see exp_b_out.txt).
