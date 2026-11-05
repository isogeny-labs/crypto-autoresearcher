# SA-10: Global-relation harvesting through squarefree-part collisions

## Summary
**KILL.** Collision exponent = 0.0 (bootstrap 95% CI [0, ~0]), criterion for kill is <= 0.6, success needs >= 0.9. Only ONE pair x1<x2<=2^22 has equal squarefree part of x^3+7: (x1,x2)=(2,212), s=15. Its twist y^2=x^3+7*15^3 has rank 2 (ellrank certified 2..2) and the two points are independent (height-pairing det 0.842), so no global relation exists. Verified relations: 0.

## What was run
- cores.py: PARI core(x^3+7) for all x = 1..2^22 (4,194,304 values, ~32 CPU-min). count.py: count pairs with equal core, cumulative counts for B = 2^8..2^22, slope fit and Poisson bootstrap.
- verify.py: for each colliding pair, twist E^s: Y^2=X^3+7 s^3, points (s x_i, s^2 m_i) with f(x_i)=s m_i^2; ellrank, elltors, ellheightmatrix to decide dependence, bestappr for (c1,c2), reduction to a 40-bit prime p with s a QR to test c1*P1=c2*P2 in E(F_p).
- control.py: positive control of the verification path (see DEVIATIONS).
- x=0 (core 7) and x=-1 (core 6) added by hand: no extra collisions.

## Results
| log2 B | 8..22 (all) |
|---|---|
| colliding pairs x1<x2<=B | 1 (appears at B>=212, constant afterwards) |

Class sizes among 4,194,304 values: 4,194,302 singletons, one class of size 2. Fitted log-log slope 0.0 (ranges e>=8, 12, 16 all 0.0). Prediction B^{1/2} (anchored at 1) would give about 2^7 = 128 pairs at 2^22; observed 1. Figure: fig_collisions.png; raw: count.out, pairs.json, verify_out.json, cores.log.

Pair (2,212): s=15, ellrank [2,2,0], torsion trivial, heights 0.490 and 4.534, det 0.842: independent. (E(Q) for y^2=x^3+7 has rank 0, so E(Q(sqrt15)) rank = rank of the twist = 2.)

Why the heuristic fails (measured): median log core / log f = 1.0; only 0.0007 of x have core <= f^0.7 and 1.7e-5 have core <= f^0.5. For generic x the squarefree part is essentially f(x) itself, so a collision needs f(x1)/f(x2) to be a rational square, i.e. an integral point on a twist y^2=x^3+7 (s-fold); by Siegel each twist has finitely many and in practice 0-1. "Random divisor" was the wrong model: the squarefree part is not a uniform random divisor, it is nearly the whole number.

## Verdict reasoning
Frozen criterion: kill if exponent <= 0.6. Measured 0.0 over 15 doublings (2^8..2^22). KILL. Even the single collision gives no relation (rank 2, independent). The harvest is O(1) total, not B^{1/2}, not B.

## Limitations
- Only integer x (the factor base) and only the curve y^2=x^3+7 (secp256k1 shape); other (a,b) not tested. Rational/negative x not in scope (f>0 only for x>=-1).
- Exponent from a count of 1 is "no growth observed", not a measured positive exponent; a true slow growth (e.g. log B) cannot be excluded but is far below 0.6.
- Only one real pair, so rank-1 relation recovery was validated only on a synthetic control.

## Suggested lead-atlas update
LEAD-ICP-squarefree-mordell-weil-collisions: disposition KILL (closed, count-based). Deciding number: 1 collision pair among x<=2^22 for x^3+7 (slope 0.0 vs required >=0.9), and that pair has twist rank 2 with independent points. Next action: none; note that integer-x factor-base points essentially never share a quadratic field, so rank-1 MW-collision relations are unavailable as a free-relation source.
