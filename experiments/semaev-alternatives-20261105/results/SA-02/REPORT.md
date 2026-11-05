# SA-02 Vieta-conic sieve with the integer-square constraint

## Summary

**VERDICT: KILL** against the frozen criterion. (a) The heuristic bivariate reach in (e1,u) is 1/8, and every presentation of the conic (including the unconstrained conic in (e1,e2) with box (B,B^2)) extrapolates to at most 1/6 (0.16666 +- 1e-5), so nothing exceeds 1/6. (b) The u-sieve has fitted time exponent 1.04 (95% bootstrap CI 0.99-1.08) at 64 bits, 1.02 (0.98-1.07) at 52 bits and 0.99 (0.94-1.03) at 40 bits over 9 doublings; no CI lies below 0.9 and all contain 1.0. Deciding numbers: reach 1/6 (not > 1/6), exponent 1.04 [0.99, 1.08]. Caveat on (a): this is a heuristic calculator, not the cuso/sumset certificate the prereg names (DEVIATIONS 1).

## What was run

- `check_conic.py`: closed form of the u-fibre. With a=0, b=7, 16*Q(e1,(e1^2-u^2)/4) = e1^4 - 8xR e1^3 - 2u^2 e1^2 + (8 xR u^2 - 448) e1 + 16 xR^2 u^2 - 448 xR + u^4. It vanishes at the planted e1 on 40/40 planted instances (64-bit p). As a polynomial in w = u^2 it is a quadratic with discriminant 256 (e1+xR)(xR^3+7) (sympy). So the square condition on u^2 is itself "e1+xR is a square", i.e. a genus-1 curve u^2 = quartic(s), s^2 = e1+xR: the genus returns exactly as the prereg predicts. (Symbolic, a=0 only; I did not check general a.)
- (a) `reach.py`, `reach2.py`: Jochemsz-May-type asymptotic reach delta*(t) for several presentations (outputs `reach_out.txt`, `reach2_out.txt`).
- (b) `sieve_u.py`, `fit_sieve.py`: sieve over u = 1,2,... (PARI polrootsmod on the quartic), planted instances with x1,x2 <= B uniformly on the curve y^2 = x^3+7, every recovery verified in the group (P1 +- P2 has x = xR). 1,560 trials, 1,560 recovered.
- Secondary: `batch.py`, `bilat.py`: windowed batch lattice (u in a window of size V, bivariate small roots by LLL + resultant), conic presentation vs plain control; `hybrid_asym.py`: asymptotic window prediction.

## Results

### (a) Heuristic reach (delta = log_p of the e1 / x1 bound)

| presentation (variables, bound exponents) | delta*(t=12) | extrapolated t->inf |
|---|---|---|
| P1 (x1,x2), (1,1), baseline S_3 | 0.1533 | 0.16666 (t = 12..24 fit) |
| P3 conic in (e1,e2), (1,2) | 0.1567 | 0.16666 (t = 12..24 fit) |
| P1b (x1, v=x1-x2), (1,1) | 0.1247 | not extrapolated (lower than P1 at every t) |
| P2 (e1,u), (1,1) | 0.1156 (sumset), 0.1137 (hull) | about 1/8 (Richardson of t=8,12: 0.1245) |
| P4 (e1,w=u^2), (1,2) | 0.1156 | about 1/8 |

Reading: the (e1,u) bivariate problem is the original (x1,x2) problem under a linear change of variables, so it cannot beat 1/6, and the rotated Newton polytope (a triangle rather than a square) is actually worse (1/8). The conic without the square condition reaches the same 1/6 in e1 (its box is B x B^2, XY = p^{1/2}); since the box then holds about B^3/p conic points the planted point is unique and the square condition adds nothing for the lattice. Hybrid prediction (`hybrid_asym.json`): window the second variable, the asymptotic frontier is delta(x1) + delta(window) <= about 1/3, so the number of windows is p^(2*beta-1/3) = B^(2-1/(3 beta)) for 1/6 < beta < 1/3 (e.g. B^0.67 at beta = 1/4). That is a standard guess-and-lattice hybrid, identical in plain coordinates, and local slope in B at fixed p is about 2, not below 1.

### (b) Sieve-by-u: time to recovery vs B (mean over trials; full table in `sieve_u_p*.txt/json`)

| p bits | B range | doublings | recovered | exponent | 95% CI (bootstrap, 2000) | top-5-doubling exponent (CI) |
|---|---|---|---|---|---|---|
| 40 | 2^6..2^15 | 9 | 520/520 | 0.986 | 0.937-1.026 | 1.064 (0.961-1.143) |
| 52 | 2^6..2^15 | 9 | 520/520 | 1.023 | 0.977-1.068 | 1.014 (0.927-1.096) |
| 64 | 2^6..2^15 | 9 | 520/520 | 1.039 | 0.986-1.082 | 1.024 (0.902-1.119) |

Mean calls to recovery are about B/2.5 (planted u uniform), cost per call 24-390 us (PARI, load dependent). Exponent in the call count is 1 by construction.

### Secondary: batch window lattice, 64-bit p, level t = 2 (`batch_*_p64_t2.json`, `fig_sa02.png`)

| B | plain control: V*, windows, expected time (s) | conic (e1,v): V*, windows, expected time (s) | per-u sieve (s) |
|---|---|---|---|
| 32 | 32, 1, 0.09 | 32, 1, 0.12 | - |
| 128 | 128, 1, 0.12 | 32 (8/10), 4, 0.38 | 0.011 |
| 256 | 64, 4, 0.44 | 2 (8/10), 128, 13.1 | 0.025 |
| 512 | 16 (8/10), 32, 3.1 | no recovery at V=1 | 0.041 |
| 1024 | 4, 256, 26 | no recovery | 0.088 |
| 4096 | 1, 4096, 335 | no recovery | 0.438 |

Plateau (single lattice call) ends at B = 128-ish (about 2^7, delta = 0.11 of 64 bits, versus asymptotic 1/6 = 2^10.7: LLL slack at t = 2). Beyond it the window count grows with slope about 2.3 between B = 128 and 4096, and the conic presentation is worse than the plain control throughout, as the calculator predicts. The lattice costs about 1000x a PARI root-finding call, so the sieve beats the batch for every B above the plateau. No batch exponent below 0.9 occurs outside the flat plateau (2 points).

## Verdict reasoning

Frozen criterion: SUCCESS if (a) reach > 1/6 or (b) fitted exponent < 0.9 with CI excluding 1.0; KILL if both fail. (a): best extrapolated reach 0.166659 (P1) and 0.166661 (conic), both equal to 1/6 within fit error, and the (e1,u) presentation is 1/8; not > 1/6. (b): the three exponents are 0.99, 1.02, 1.04 with upper CI ends above 1.0 and lower ends 0.94-0.99 > 0.9; not < 0.9. Both fail, so KILL. The conic observation becomes the lemma the prereg describes: in a convex-shift Coppersmith lattice the symmetric quotient does not lower the reach (1/6 again for the conic box, 1/8 in (e1,u)), and the u-sieve is linear in B.

## Limitations

- (a) is a heuristic calculator for the sumset/hull shift family at t <= 24, extrapolated by a 3-parameter fit; no cuso, no sumset or LP certificate, no Ehrhart check (DEVIATIONS 1). It cannot exclude non-convex or Gröbner-selected shifts, which is what cuso explores. Planted LLL confirmation was done only at t = 2 (and three t = 3 rows).
- Only a=0, b=7 (secp256k1-shaped) curves; the discriminant identity was checked for this case only.
- The batch variant was run at t = 2 only, 8-10 trials per cell, V* calibrated coarsely by halving; it is a secondary probe, and the criterion verdict rests on the per-u sieve and on (a).
- The per-u sieve uses PARI root finding instead of per-u Coppersmith (same asymptotic cost). Wall times are on a shared host, so absolute numbers vary (us per call drifted 24-390).
- Exponent over this range also reflects PARI's near-constant per-call cost; a 9-doubling fit cannot see log factors.

## Suggested lead-atlas update

LEAD-ICP-vieta-conic-square-sieve: disposition `closed (lemma)`, next_action none. Record: "Vieta quotient is a conic; the u-fibre over e1 is a quadratic in u^2 with discriminant 256(e1+xR)(xR^3+7), so the square condition reintroduces the genus-1 curve; heuristic JM-type reach is 1/6 for the conic box (B,B^2) and 1/8 in (e1,u), never above the 1/6 of (x1,x2); sieve-by-u time exponent 1.04 [0.99,1.08] at 64 bits over 9 doublings (1.02 and 0.99 at 52 and 40 bits)." Deciding number: reach 1/6 (not > 1/6) and exponent CI lower end 0.94-0.99 (not < 0.9). Mark the reach as heuristic until a cuso or sumset certificate is run (Idea 1).
