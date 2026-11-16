# Step 3: the level-2 volume inequality c2(W) <= C_2 omega^{1/15} + M(1 + ln M). PROVED.

Setting. y^2 = x^3 + ax + b, integers a, b != 0, M = max(4|a|, 128|b|, 4). For 1 <= x1 <= x2 put e1 = x1 + x2, e2 = x1 x2,
D = x2 - x1, g0 = |G0|, g1 = |G1|, g2 = G2 = D^2, and s2 = (G0^2, 2G0G1, 2G0G2 + G1^2, 2G1G2, G2^2) (coefficients of S_3^2).
For W = (W0..W4), all Wj >= 1, omega = prod Wj:   c2(W) = #{1 <= x1 <= x2 : |s2_j(x)| <= Wj, j = 0..4}.

Theorem V2.  c2(W) <= C_2 omega^{1/15} + M(1 + ln M),  C_2 = 5 * 2^{3/5} + 4^{1/15} < 8.7.

Proof. (Every step proved; the small pairs are handled as in SA-13b Lemma 5, step 1.)
0. Pairs with e2 < M number at most M(1 + ln M). From now on e2 >= M, and SA-13b step 2 gives
   G0 >= e2^2/2 > 0  (so G0 > 0),   g1 >= e1 e2 >= x1 x2^2,   g2 = D^2.
1. Since G0 > 0 and G2 >= 0, both terms of s2_2 = 2 G0 G2 + G1^2 are nonnegative, so |s2_2| <= W2 gives G1^2 <= W2 AND 2 G0 G2 <= W2.
   The five box conditions therefore imply the six inequalities
   (i)  G0^2 <= W0          -> (x1 x2)^4 / 4 <= W0      -> x1 x2 <= (4 W0)^{1/4}
   (ii) 2 G0 g1 <= W1       -> (x1 x2)^2 x1 x2^2 <= W1  -> x2 <= W1^{1/4} x1^{-3/4}
   (iii) g1^2 <= W2         -> x1^2 x2^4 <= W2          -> x2 <= W2^{1/4} x1^{-1/2}
   (iii') 2 G0 g2 <= W2     -> (x1 x2)^2 D^2 <= W2      -> D <= W2^{1/2} x1^{-2}          (x2 >= x1)
   (iv) 2 g1 g2 <= W3       -> x1 x2^2 D^2 <= W3        -> D <= W3^{1/2} x1^{-3/2}        (x2 >= x1)
   (v)  g2^2 <= W4          -> D <= W4^{1/4}.
2. Range of x1. x2 >= x1 and (i)-(iii) give x1 <= X1 := min((4W0)^{1/8}, W1^{1/7}, W2^{1/6}).
3. Diagonal (D = 0). The count is <= X1 <= ((4W0)^{1/8})^{8/15} (W1^{1/7})^{7/15} = 4^{1/15} (W0 W1)^{1/15} <= 4^{1/15} omega^{1/15}
   (min(u, v) <= u^{8/15} v^{7/15}, and W2, W3, W4 >= 1).
4. Off-diagonal (D >= 1). For fixed x1 the number of x2 = x1 + D is at most
   min( X2(x1), Dmax(x1) ),  X2 = min((4W0)^{1/4} x1^{-1}, W1^{1/4} x1^{-3/4}, W2^{1/4} x1^{-1/2}),
                             Dmax = min(W4^{1/4}, W3^{1/2} x1^{-3/2}, W2^{1/2} x1^{-2}).
   A minimum of six nonnegative numbers is at most any weighted geometric mean of them. Take the weights
   theta = (A: 4/15, B: 4/15, C: 0, E: 4/15, F: 2/15, G: 1/15) on the six terms in the order written (sum 1):
   min <= (4W0)^{1/15} x1^{-4/15} * W1^{1/15} x1^{-3/15} * W4^{1/15} * W3^{1/15} x1^{-3/15} * W2^{1/30} x1^{-2/15}
       = 4^{1/15} (W0 W1 W3 W4)^{1/15} W2^{1/30} x1^{-12/15}.
   Summing over 1 <= x1 <= X1:  sum x1^{-4/5} <= 5 X1^{1/5} <= 5 W2^{1/30}  (X1 <= W2^{1/6}).
   Hence the off-diagonal count is <= 5 * 4^{1/15} (W0 W1 W2 W3 W4)^{1/15} = 5 * 2^{2/15} omega^{1/15} < 5 * 2^{3/5} omega^{1/15}.
5. Adding 0, 3, 4 gives the theorem.                                                                                QED

Remarks.
* Exponent bookkeeping: W0: 1/15 (step 4) resp. 1/15 (step 3); W1: 1/15; W2: 1/30 (weight G) + 1/30 (from X1^{1/5}) = 1/15;
  W3: 1/15; W4: 1/15. The two halves of the W2 budget are what make the W1, W3 constraints usable (SA-13b could only prove
  (W0 W2 W4)^{1/9} because it used only (i), (iii), (v)).
* The exponent 1/15 is exact: in log variables (alpha, t, d) = (log x1, log x2, log D) the constraints are linear and the dual LP
  certificate with all five multipliers equal to 1/15 (the two uses of W2 sharing the weight 1/15, together with multipliers 5/15 and
  9/15 - 2 lambda_2'' on the free constraints t >= alpha, t >= d) shows alpha + d <= (sum_j log Wj)/15 on the feasible region, and
  balanced boxes Wj = B^{8-j} achieve c2 ~ B^2/2 = omega^{1/15}/2 up to constants. The numerical sup of SA-13b (0.59) is between 1/2
  and C_2 = 8.7, as it must be.
* Numerical check: exp_vol_level2.py evaluates c2(W) exactly on tight boxes (all pairs x1 x2 <= 3e6) and reports sup c2/omega^{1/15}.
* Consequence (with SA-13b 2.2 and step_b.md): under H-sep the level-2 coverage is cov2(W) <= C_2 omega^{1/15} + M(1+ln M) + K_b cost(W),
  so success per unit cost is <= 4 (C_2 p^{2/15} + M(1+ln M) + K_b)/N, i.e. cost Omega(p^{13/15}) per relation in class CE2-na.
