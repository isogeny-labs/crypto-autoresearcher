# SA-08b: first-minimum bound for the Rees lattice (S_3, m = 2)

## Summary

**Verdict: KILL** (against the frozen criterion: the lambda_2 crossing extrapolates to within 0.01 of 1/6 or below, and its excess over the determinant prediction shrinks monotonically in K). No SUCCESS condition is met: no crossing exceeds 0.1395 at any (bits, K) measured, and no family beating the determinant bound by a K-growing factor was found.

Deciding numbers (planted, box support, lambda_2 crossing of the Howgrave-Graham bound p^K/sqrt(n)):

| bits | K=1 | 2 | 3 | 4 | 5 | 6 | Minkowski delta_K (K=1..6) |
|---|---|---|---|---|---|---|---|
| 48 | .1048 | .1139 | .1185 | .1278 | .1333 | .1370 | .0556 .1000 .1190 .1296 .1364 .1410 |
| 64 | .1125 | .1076 | .1216 | .1305 | .1359 | .1395 | same |
| 96 | .1079 | .1118 | .1248 | .1332 | - | - | same |

- Excess over determinant (crossing minus delta_K), signed, strictly decreasing in K in every series: 48 bits +.049, +.014, -.001, -.002, -.003, -.004; 64 bits +.057, +.008, +.003, +.001, -.0004, -.002; 96 bits +.052, +.012, +.006, +.004. The K = 1 excess (0.126 measured in SA-08 versus 0.056) is therefore a finite-size effect, as predicted.
- Extrapolation to K -> infinity (K >= 3 points, 64 bits): plain crossing fit 0.157 (in 1/K, LOO 0.157-0.157) or 0.145 (in 1/K^2); excess-corrected estimator 1/6 + extrapolated excess = 0.161 (1/K) / 0.164 (1/K^2), all leave-one-out values 0.160-0.165. 48 bits: 0.159-0.162. Every estimate is below 1/6 and within 0.01 of it (corrected) or below it; none is near the SUCCESS bar 0.1767.
- Honest caveat on the second KILL clause: the excess is monotone decreasing as a signed number, but at 48 and 64 bits it changes sign and keeps falling (HG's 1/sqrt(n) and Gaussian-constant losses, an O(log n / bits) effect that is larger at 48 bits than at 96), so its absolute value is not monotone. I read "excess" as the signed advantage over the determinant prediction, which is what the criterion cares about (an advantage that persists or grows would be positive).

## What was run

Scripts in /home/user/semaev-runs/SA-08b/ (SA-08's planted.py imported unmodified for S_3 and polynomial multiplication):

- lam.py: builds the Rees/Coppersmith lattice of SA-08 (rows x^(a-2k) y^(b-2k) f^k p^(K-k), k = min(K, floor(min(a,b)/2)), columns scaled by B^(u+v)) on a down-closed support, LLL then BKZ-20, records log of the three shortest basis norms, the HG bound log(p^K/sqrt n) and the Gaussian-heuristic length from the exact log-determinant. Planted instances (x_1, x_2 <= B on y^2 = x^3 + 7, r = x(P_1+P_2)) and random instances (random r, no small solution).
- sweep.sh, sweep2.sh: grids delta in {.06,.08,.10,.11,...,.18,.20,.22}, 2 instances per type per point, boxes K = 1..6 (48 bits), K = 1..6 (64 bits), K = 1..4 (96 bits), truncated simplex u+v <= 3K, K = 2..5 (48 bits).
- analyze.py (crossings, crossing_table.md/crossings.json), fit.py (extrapolations, LOO; extrapolation.json, extrapolation_excess.json), final.py (fig_crossing.png). Raw rows: raw/*.json (about 360 KB total).

## Results

Full table: crossing_table.md. Excerpt (planted; random instances agree to within 0.0005 for K >= 3, and are below planted by up to 0.01 at K = 1, 2):

| support | bits | K | n | Minkowski delta_K | GH crossing | lambda_1 crossing | lambda_2 crossing |
|---|---|---|---|---|---|---|---|
| box | 64 | 3 | 49 | .1190 | .1099 | .1219 | .1216 |
| box | 64 | 4 | 81 | .1296 | .1213 | .1309 | .1305 |
| box | 64 | 5 | 121 | .1364 | .1288 | .1360 | .1359 |
| box | 64 | 6 | 169 | .1410 | .1341 | .1395 | .1395 |
| box | 96 | 4 | 81 | .1296 | .1240 | .1344 | .1332 |
| simplex | 48 | 3 | 43 | .0957 | .0832 | .1105 | .1093 |
| simplex | 48 | 5 | 106 | .1158 | .1057 | .1223 | .1222 |

Observations.
- lambda_1 and lambda_2 cross the HG bound at the same delta to within 0.0003 for K >= 3 (and up to 0.003 at K <= 2). Above the crossing both are the trivial vector of norm p^K (and its multiples), so the transition is sharp: log lambda_2 - log HG goes from about -2 to +2 within 0.01 in delta. Whether one needs lambda_1 or lambda_2 does not change the threshold.
- Gaussian heuristic: lambda_2 crosses 0.005-0.012 above the GH crossing (planted, 64 bits: .0174, .0117, .0093, .0072, .0054 for K = 2..6), shrinking monotonically; the true first minima are below the GH length at fixed delta (log lambda_2/GH about -2 to -7 at delta = 0.15) because the Rees lattice has a very skewed Gram-Schmidt profile, so GH of the whole lattice is not the relevant prediction. The determinant (Minkowski) prediction on the best sublattice, delta_K, is.
- The truncated simplex support is worse than the box at every K (limit of its Minkowski value 0.1504 at K = 200, versus 0.1658 for the box), consistent with SA-08's LP: the cube is optimal among supports. Its crossing excess over its own delta_K is +.026, +.014, +.010, +.006 (planted, K = 2..5), decreasing; extrapolated crossings 0.12-0.14, far below 1/6. (The 1/6 + excess estimator is not applicable to it.)
- Proxy check (48 bits, K = 4): LLL, BKZ-20, BKZ-30 crossings differ by less than 0.001.

## Theory: why lambda_1 cannot beat the determinant bound asymptotically (status of each step)

Setup as in SA-08: L_K is the lattice of coefficient vectors, scaled by B^(u+v), of polynomials in the Rees algebra Z[x,y][f/p] of degree <= (2K, 2K) (or another down-closed support) lying in the p^K-multiples; HG needs a vector of norm < p^K / sqrt(n).

1. [proved, standard] Minkowski I gives lambda_1 <= sqrt(n) det^(1/n) and Minkowski II gives prod lambda_i <= 2^n det / vol(B_n). These are upper bounds on minima, so they show methods succeed below delta_K and say nothing about failure above it.
2. [sketched, depends on SA-08 T3: the shift family is a basis of the full lattice] A lower bound that is unconditional on the basis: for a lattice with a triangular basis, lambda_1 >= min_i ||b_i^*|| = min over the support of p^(K-kappa) B^(a+b). For the box this is min(p^K, B^(4K)) up to constants, so for delta > 1/4 there is no vector below p^K at all (HG fails for every support whose top corner has k = K). This is a proved-given-T3 ceiling of 1/4, weaker than 1/6.
3. [proved] Banaszczyk transference gives 1 <= lambda_1(L) lambda_n(L*) <= n. A lower bound lambda_1(L) >= c det^(1/n) is therefore equivalent (up to n) to lambda_n(L*) <= c^-1 det^(-1/n) n: the dual must have n independent vectors of length comparable to its own determinant^(1/n). The dual of a triangular Rees basis has the explicit independent set e_i^*/d_i only after undoing the off-diagonal part; the off-diagonal entries are the f^k coefficients, of size p, i.e. exactly the part that is not controlled.
4. [conjectured] Zhang-type route: Zhang's inequality relates the successive essential minima of the adelic line bundle (polydisc at infinity, {|f/p| <= 1} at p) on X = Spec Z[x,y,t]/(pt - f) to its height, with e_1 >= h/((d+1) deg). To use it one needs the sectional capacity of that adelic set and the height of the arithmetic threefold; neither was computed (SA-08 deviation 2) and I do not know a reference computing them for a bidegree-(2,2) f. If the Zhang bound is tight (the two sides of Zhang's inequality agree up to a factor 2^d, i.e. the successive minima are balanced), then lambda_1 is within a bounded factor of the determinant prediction, giving the 1/6 ceiling up to O(1/K).
5. [empirical, this run] The two sides are balanced to the resolution measured: the true crossing of lambda_1 and lambda_2 tracks the exact determinant threshold delta_K within 0.004 for all K >= 3 and the signed excess decreases monotonically to below zero (K = 1..6). This is evidence for the balance statement in step 4, with no growth in K of any advantage.

Net: nothing proved beyond the 1/4 triangular bound; the argument for 1/6 reduces to the Zhang balance statement (step 4) and the numerics support it.

## Verdict reasoning

SUCCESS needs an extrapolated crossing above 0.1767 or a written family beating the determinant bound by a K-growing factor. Measured crossings are at most 0.1395 up to K = 6, equal the determinant threshold to within 0.004 for K >= 3, and the advantage over it is strictly decreasing. Estimators give 0.145-0.165. No family beating the determinant was found in the supports tried (box, truncated simplex). KILL needs (a) extrapolated crossing within 0.01 of 1/6 or below: yes, all estimators; (b) excess shrinking monotonically: yes as a signed quantity in every series. KILL is stated for the Rees-lattice first-minimum question at S_3, m = 2, not as a nonexistence theorem for auxiliary-polynomial methods.

## Limitations

- BKZ-20 proxy, not exact SVP; lambda_2 is the second basis vector. A genuinely shorter vector missed by BKZ-20 would lower the crossing (helping the SUCCESS side); the LLL/BKZ-20/BKZ-30 comparison moved the crossing by less than 0.001, and the crossing coincides with the determinant to 0.001-0.004.
- K <= 6 only (K <= 4 at 96 bits); the extrapolation is from K = 3..6 where delta_K is still 0.025 below 1/6. This is why the estimator that extrapolates the excess (which is nearly flat) was used; a pure crossing fit is biased low by about 0.01. Two instances per point, grid step 0.01.
- Only box and truncated-simplex supports, one curve (y^2 = x^3 + 7), f-shift family of SA-08 only. Non-triangular or extended shift families (Jochemsz-May style) are not covered; a family with a K-growing advantage would have to be outside these.
- The theory section is not a proof; step 4 is conjectural.

## Suggested lead-atlas update

LEAD-ICP-coppersmith-smallroot-semaev: add that the measured first minima of the Rees lattice (S_3, m = 2, box supports K = 1..6, 48-96 bits, BKZ-20 proxy) cross the Howgrave-Graham bound at the Minkowski determinant threshold delta_K to within 0.004 for K >= 3, with the excess over delta_K strictly decreasing in K (+0.05 at K = 1 to -0.004 at K = 6, 48 bits), planted and random alike; extrapolated ceiling 0.16-0.165, i.e. 1/6 with no K-growing gain. Disposition: SA-08b KILL for "small-K excess signals a >1/6 reach"; keep the SA-08 statement "closed for determinant arguments" and strengthen it to "first minimum tracks the determinant on the realised lattices". Remaining open step: the Zhang-type balance statement (sectional capacity and height of the threefold), still needed for a proof; next_action for an executor with exact SVP (or flatter/G6K) is K >= 7 at 96 bits.
