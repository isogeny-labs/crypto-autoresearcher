# SA-09b REPORT: Heegner norm relations beyond the CM toy

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary

**Verdict: KILL against the frozen criteria, with one sensitivity flag (below).**

Deciding numbers:
- **Non-CM curve 37a1, K = Q(sqrt-7).** Rank of the Kolyvagin norm-relation matrix over all conductors <= B gives rank/points = 0.1337 (3050/22813) at the largest bound reached, B = 500. That is under 0.15 and far under 1/2.
- **Trend.** Strictly decreasing over five bounds: 0.245 (B=15), 0.183 (39), 0.159 (65), 0.140 (100), 0.137 (130). After that it saw-tooths between 0.129 and 0.151 (160: 0.129, 200: 0.147, 250: 0.139, 300: 0.151, 500: 0.134). The character-count formula gives 0.1254 at B = 10^6 (conjectural).
- **Descent.** Hit rate of random targets as a signed sum of <= 3 Heegner points: 0.4587 vs random-set control 0.4540 on 37a1 (3 primes x 1000 targets, 100 control sets per prime). Difference +0.0047, 95% CI [-0.014, +0.023]. On 36a1: 0.2113 vs 0.2105, difference +0.0008, CI [-0.013, +0.016]. No excess.
- **Second field for 36a1, K = Q(sqrt-47), h = 5.** rank/points 0.0687 at B = 250, never above 0.12 at any bound >= 55. Character-count limit about 0.057.
- **SUCCESS is excluded.** The maximum rank/points on any curve at any bound is 0.314 (a 35-point set, {1,3,5,15} on 37a1). Both descent CIs contain 0.

**Sensitivity flag.** The KILL clause "decreasing trend over >= 3 bounds" is met by the run 15 -> 130 and by the overall trend, but the sequence is not monotone after B = 130. The ratio at B = 300 (0.1514) is just above 0.15. The criterion was read at the largest bound reached (B = 500, 0.1337). A reader who stops at B = 300 gets INCONCLUSIVE. The F_p-verified range is only B <= 15 (see Limitations).

## What was run

SA-09's directory was only read; its `heeg.gp`, `build.py` and `fp.py` ideas were reused.

1. **Non-CM Heegner points, exact F_p verification** (`heegN.gp`, `build_gen2.py`, `fpg.py`, `analyze_gen.py`).
   - E = 37a1 (y^2 + y = x^3 - x, rank 1, prime conductor 37, modular degree 2).
   - K = Q(sqrt-7): h = 1, 37 splits, beta = 17 mod 74. Inert primes 3, 5, 13 with a_3 = -3, a_5 = -2, a_13 = -2 (all nonzero); three were used instead of two, giving conductors {1, 3, 5, 13, 15}.
   - Points phi(tau) from ellan + ellztopoint at 800 digits; Galois labelling by composition in Pic(O_m); Lagrange interpolation; coefficients recognised in K by bestappr (max 150 digits against a 266-digit bound; errors < 1e-790).
   - Reduced mod 3 primes (266239, 267199, 268291) that split completely in the ring class field of conductor 195. Every relation checked with an independent integer group law on the model v^2 = u^3 - 16u + 16.
2. **Class-group structure of the relations** (`arith.py`, `validate_arith.py`, `rank_arith.py`, `rank_arith2.py`).
   - Fibres of Pic(O_{nl}) -> Pic(O_n) computed from binary quadratic forms. Rank of the relation matrix mod a 31-bit prime (random projection for B = 500).
   - Validated against complex-analytic Hecke neighbour lists (`nb_gen.py`, 120 digits, residuals about 1e-126). Fibres identical in 9/9 edges for 37a1 up to conductor 65 (levels 1, 3, 5, 13, 15, 39, 65), 4/4 edges for 36a1 with Q(sqrt-23) (SA-09's data), and 4/4 edges for 36a1 with Q(sqrt-47) up to conductor 55 (360 points).
3. **Second field for 36a1**: K = Q(sqrt-47), h = 5, 2 and 3 split, beta = 23 mod 72. Same rank pipeline up to B = 250. SA-09's field Q(sqrt-23) was also rerun for all conductors <= B up to 130.
4. **Descent test** (`descent.py`, `dump36.py`).
   - Per prime, 1000 random targets R in E(F_p). Hit = R is a sum of <= 3 elements of +-S, repeats allowed.
   - S = the Heegner points reduced mod p: 49 points on 37a1, 45 points on 36a1 (SA-09 levels 1, 5, 7).
   - Control: 100 random sets of N points of E(F_p) on the same targets. Paired bootstrap over targets.
   - A second variant (targets and control drawn from the subgroup spanned by S) is in `descent_*.json`.

## Results

### Table 1. Exact verification in E(F_p), 37a1, conductors {1,3,5,13,15} (`res37c.json`)

| p | #E(F_p) | on curve | distinct | 1>3 | 1>5 | 1>13 | 3>15 (l=5) | 5>15 (l=3) | wrong embedding (60 tests) | random signed subsets (2 x 20000) |
|---|---|---|---|---|---|---|---|---|---|---|
| 266239 | 266280 | yes | 49/49 | 1/1 | 1/1 | 1/1 | 4/4 | 6/6 | 0 pass | 0 pass |
| 267199 | 266526 | yes | 49/49 | 1/1 | 1/1 | 1/1 | 4/4 | 6/6 | 0 pass | 0 pass |
| 268291 | 268713 | yes | 49/49 | 1/1 | 1/1 | 1/1 | 4/4 | 6/6 | 0 pass | 0 pass |

All 13 relations hold exactly on each prime (39/39). An earlier run on {1,3,5,15} (`res37.json`) also passed. Level 39 (h = 56) could not be algebraised in the time available: recognition failed at 1300 and 1900 digits (heights exceed about 640 digits).

### Table 2. rank/points, 37a1, all conductors <= B (`results_rank_ratio_table.csv`)

| B | points N | relations | rank | rank/N | character count N - sum m |
|---|---|---|---|---|---|
| 3 | 5 | 1 | 1 | 0.200 | 1 |
| 5 | 11 | 2 | 2 | 0.182 | 2 |
| 13 | 25 | 3 | 3 | 0.120 | 3 |
| 15 | 49 | 13 | 12 | 0.245 | 12 |
| 17 | 67 | 14 | 13 | 0.194 | 13 |
| 19 | 87 | 15 | 14 | 0.161 | 14 |
| 39 | 175 | 34 | 32 | 0.183 | 32 |
| 65 | 623 | 104 | 99 | 0.159 | 99 |
| 100 | 1325 | 194 | 186 | 0.140 | 186 |
| 130 | 1699 | 242 | 233 | 0.137 | 233 |
| 160 | 2513 | 335 | 324 | 0.129 | 324 |
| 200 | 4061 | 633 | 597 | 0.147 | 597 |
| 250 | 6689 | 971 | 929 | 0.139 | 929 |
| 300 | 10343 | 1667 | 1566 | 0.151 | 1566 |
| 500 | 22813 | 3204 | 3050 | 0.134 | 3050 |

Rank equals the character count N - h_K * sum(m) at all 33 (curve, field, B) combinations tested. Beyond B = 500 the count is extrapolated: 0.1354 (B = 10^3), 0.1274 (10^4), 0.1263 (10^5), 0.1254 (10^6). The ratio jumps up whenever a new inert prime enters and its small composites fill in, then decays; hence the saw-tooth. The relation count is far below the point count (3204 relations for 22813 points at B = 500): the tree-shaped relation graph of SA-09 again.

### Table 3. 36a1, second field Q(sqrt-47) (h = 5) and SA-09's Q(sqrt-23) (`rank36_47*.json`, `rank36_23*.json`)

| B | Q(sqrt-47) N | rank | rank/N | Q(sqrt-23) N | rank | rank/N |
|---|---|---|---|---|---|---|
| 5 | 35 | 5 | 0.143 | 21 | 3 | 0.143 |
| 35 | 695 | 35 | 0.050 | 339 | 54 | 0.159 |
| 65 | 1905 | 225 | 0.118 | 1149 | 117 | 0.102 |
| 100 | 3215 | 360 | 0.112 | 3381 | 333 | 0.098 |
| 130 | 6235 | 525 | 0.084 | 5121 | 420 | 0.082 |
| 160 | 11085 | 1025 | 0.092 | 6939 | 510 | 0.073 |
| 200 | 16525 | 1055 | 0.064 | 9993 | 735 | 0.074 |
| 250 | 27345 | 1880 | 0.069 | 13605 | 984 | 0.072 |

The Q(sqrt-23) values at B = 35 cover all conductors <= 35 (N = 339), a superset of SA-09's {1,5,7,35} (0.238). Character-count limits: about 0.057 for Q(sqrt-47), about 0.070 for Q(sqrt-23).

### Table 4. Descent test (`descent_37a1.json`, `descent_36a1.json`)

| curve | S size | p | E(F_p) | Heegner hit rate | control mean (100 sets) | diff 95% CI |
|---|---|---|---|---|---|---|
| 37a1 | 49 | 266239 | cyclic | 0.466 | 0.453 | [-0.015, +0.045] |
| 37a1 | 49 | 267199 | cyclic | 0.451 | 0.456 | [-0.035, +0.025] |
| 37a1 | 49 | 268291 | cyclic | 0.459 | 0.454 | [-0.026, +0.036] |
| 37a1 | pooled 3000 targets | | | 0.4587 | 0.4540 | **[-0.014, +0.023]** |
| 36a1 | 45 | 530251 | Z/6 x Z/88134 | 0.210 | 0.213 | [-0.028, +0.022] |
| 36a1 | 45 | 535481 | cyclic | 0.214 | 0.212 | [-0.023, +0.026] |
| 36a1 | 45 | 539009 | cyclic | 0.210 | 0.206 | [-0.021, +0.031] |
| 36a1 | pooled 3000 targets | | | 0.2113 | 0.2105 | **[-0.013, +0.016]** |

The Heegner points generate E(F_p) on 37a1 (span index 1). The subgroup-restricted variant gives the same answer: pooled diff -0.006, CI [-0.024, +0.012] on 37a1 and +0.006, CI [-0.008, +0.021] on 36a1.

## Verdict reasoning

- **SUCCESS** needs rank/points >= 1/2 at the largest bound on either curve, or a descent hit rate above control with a CI excluding equality. The maximum observed anywhere is 0.314; at the largest bounds it is 0.134 on 37a1 and 0.069 on 36a1. Both descent CIs contain 0. Not met.
- **KILL** needs (a) rank/points < 0.15 at the largest bound on the non-CM curve: 0.1337 at B = 500, yes; (b) a decreasing trend over >= 3 bounds: yes for 15 -> 39 -> 65 -> 100 -> 130 and in the overall trend, but not monotone afterwards (flag above); (c) descent not above control: yes. Taken at the largest bound reached, KILL.
- The prediction (non-CM <= 0.3 and decreasing, descent equal to control) held, except that the F_p-verified set {1,3,5,13,15} has ratio 0.245 and the ratio is not monotone at small B.
- The non-CM curve behaves like the CM curve in SA-09. The ratio settles at 0.12 to 0.15 for K = Q(sqrt-7) (h = 1), against about 0.07 for h = 3 and about 0.06 for h = 5. A larger class number lowers it, since the unrelated part is h_K * sum m.

## Limitations

- Exact F_p verification covers B <= 15 only (49 points, 13 relations). Level 39 and above are not algebraised.
- For 15 < B <= 65 the structure rests on complex-analytic Hecke relations at 120 digits (residuals about 1e-126) matched exactly to the class-group fibres. For B > 65 it rests on the class-group fibres alone, validated at every edge tested (17 of 17).
- Rank is the rank of the Euler-system relation matrix, not of the full relation module. SA-09's LLL check (no further small relations) was not repeated for 37a1.
- The B = 500 rank used a random projection mod a 31-bit prime (rank <= true rank, with equality w.h.p.); the same method reproduced the exact B = 130 and B = 300 values.
- The extrapolation beyond B = 500 is the conjectural character count; it matched the measured rank at every tested B.
- The descent test uses sets of 45 to 49 points on p about 2.7e5 to 5.4e5, where the control hit rate is 0.21 to 0.45. Power is about +-0.02 on the rate; a small structured advantage would not be detected, and no scale where hits are rare was tried.
- 36a1 with Q(sqrt-47) was not reduced mod p (the F_p check for 36a1 is SA-09's, for Q(sqrt-23)).
- No discrete-log consequence was measured.

## Suggested lead-atlas update

LEAD-ICP-heegner-norm-free-relations: keep "closed negative", now also for non-CM curves and a second field; next_action none. Deciding numbers: non-CM 37a1 (K = Q(sqrt-7)) rank/points = 3050/22813 = 0.134 at conductor bound 500 (saw-tooth between 0.129 and 0.151 for B >= 130, character-count limit about 0.125); 36a1 with K = Q(sqrt-47) 0.069 at B = 250; descent hit rate 0.459 vs control 0.454 (diff CI [-0.014, +0.023]) on 37a1 and 0.2113 vs 0.2105 on 36a1. All 13 relations at conductors {1,3,5,13,15} verified exactly on 3 primes near 2^18, controls fail (0/60, 0/40000). Caveat: exact verification beyond conductor 15, and a descent test at a scale where hits are rare, are untested.
