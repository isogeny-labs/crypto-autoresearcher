# SA-05 REPORT: Height-closed Kummer ladders on y^2 = x^3 + 7

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary

**Verdict: SUCCESS on the letter of the frozen criterion. The yield has no index-calculus value. The criterion is met because of a global-point floor that the prereg's own kill clause names. A coordinator review of the criterion is recommended before anything is opened.**

- The criterion was the measured 3-in-base yield per target divided by the generic rate B^3/p^2, counted exactly by enumerating every pair in the base. At h = 100 the ratio is 84 at p ~ 2^40, 2.1e4 at 2^48 and 6.7e6 at 2^56. Fitted slope of log2(ratio) against log2(p): **1.017 (95% bootstrap CI 0.994 to 1.048)**. The CI excludes a constant ratio, and the slope is about 1.0 at every h from 48 to 100. The kill condition (ratio within [0.8, 1.25] at every p) is not met at any p >= 2^40.
- The whole excess comes from *global* relations: P, Q and P - Q are reductions of points in one twist group E^d(Q), and S_3 = 0 holds exactly over Q. Of the 1,722 listed relations, all were confirmed in the group and every one was global; 0 were wrapped. The number of global relations per prime is **about 33 to 41 at h = 100 and does not depend on p**. So the per-target yield is about C(h)/p with C(h) ~ h^0.8-1.0. The ratio to B^3/p^2 grows like p only because, at toy scale, B^3 << p.
- No random target passed the square-divisibility filter: **0 of 100,000 at 2^40, 0 of 30,000 at 2^48 and 0 of 10,000 at 2^56**. The filter works as a known-answer test: it accepted 227 of the 237 true global relations.
- At small p (2^22 to 2^30), where generic relations are plentiful, the structured base gives the same count as a random base of equal size: struct/control is 0.94 to 1.07 at k = 22 and 24. With the global count subtracted, the excess is about 1.0 everywhere. Beyond the global points, the ladder structure adds nothing.

## What was run

All scripts are in this directory. Everything ran single-threaded under `nice`.

1. **(a) Closure** (`closure.py`, `closure_heights.py`). Exact heights over Q of x_{P+Q} + x_{P-Q} and x_{P+Q}·x_{P-Q} for random pairs with h = 8..128. Rational reconstruction mod p of x_{P±Q} for pairs in the same twist class and in different twist classes, plus 2-step chains, at h = 32 and p ~ 2^40, 2^48, 2^56. The twist class is d = core(b(a^3 + 7b^3)).
2. **(b, c) Yield** (`run_yield.py` driving `sumset.cpp`). For each p in {2^40, 2^48, 2^56}, 4 primes p ≡ 3 mod 4 just above 2^k, and h in {8, 12, 16, 24, 32, 48, 64, 80, 100}:
   - The base is all x = a/b with |a| <= h, 1 <= b <= h, x on the curve. B is up to about 6,100.
   - All B(B-1) values x(P±Q) were enumerated and those landing in the base counted. Each hit is a 3-in-base relation P, Q, D = P∓Q, whose target R = P±Q is the other sign.
   - The same count was run for a random base of equal B (control) and for an integer-only base (b = 1) of equal size.
   - Every listed relation was classified exactly over Q as global (S_3(x_P, x_Q, x_D) = 0 in Q) or wrapped.
   - Supplement (`yield_supp.jsonl`): the same design at k = 22, 24, 26, 28, 30, with 2 primes each, so the generic count is large enough to compare.
3. **(b) Random-target criterion** (`criterion.py`). Rational reconstruction of 100,000 random target abscissae per p; full factorization of v(u^3 + 7v^3) with PARI `core` for 100,000, 30,000 and 10,000 targets. A target passed when its squarefree core was at most 8h^4 (h = 100). The recall check fed the target abscissae of all true relations with h >= 48 through the same filter.
4. **Independent verification** (`verify.py`). Each of the 1,722 listed relations recomputed with Python big integers: x_D ∈ {x(P+Q), x(P-Q)} and x_D distinct from x_P, x_Q.
5. **Analysis** (`analyze.py`, `analyze_supp.py`). Per-cell table, bootstrap fits (2,000 resamples over primes within each k), and `fig_yield.png`.

## Results

### (a) Closure

| quantity | h=8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|
| exact max log2-height of x_{P+Q}+x_{P-Q} | 16.5 | 20.7 | 24.7 | 28.8 | 32.8 |
| exact max log2-height of x_{P+Q}·x_{P-Q} | 17.4 | 21.4 | 25.6 | 29.2 | 33.4 |
| 5·log2 h | 15 | 20 | 25 | 30 | 35 |

Sum and product are small-height rational functions of x_P, x_Q for every pair, with height about h^5. The individual x_{P±Q} are small only when P and Q are in the same twist class:

| p | both x_{P±Q} reconstruct small: same twist | different twist | 2-chain small (same twist) | twist classes with >=2 points / points (h=32) |
|---|---|---|---|---|
| 2^40 | 1339/2000 | 0/2000 | 327/2000 | 3 / 650 |
| 2^48 | 2000/2000 | 0/2000 | 836/2000 | 6 / 670 |
| 2^56 | 2000/2000 | 0/2000 | 1466/1754 | 4 / 670 |

Almost every base point is alone in its twist class, which is why so few global relations exist.

### (b, c) Yield, main scale (`table_main.md`; summed over primes)

| k | h | B | relations (all global) | control | integer base | generic N·B/M | ratio |
|---|---|---|---|---|---|---|---|
| 40 | 32 | 656 | 69 | 0 | 0 | 0.002 | 3.4e4 |
| 40 | 100 | 6115 | 105 (3 primes) | 3 | 0 | 1.25 | 84 |
| 48 | 32 | 662 | 33 | 0 | 0 | 2e-4 | 4.0e6 |
| 48 | 100 | 6072 | 132 | 0 | 0 | 0.006 | 2.1e4 |
| 56 | 32 | 658 | 69 | 0 | 0 | 3e-5 | 2.2e9 |
| 56 | 100 | 6065 | 165 | 0 | 0 | 2.5e-5 | 6.7e6 |

Global relations per prime at h = 100: 35.0, 33.0, 41.3 at k = 40, 48, 56 — flat in p.

Fits (`fits.json`), point estimate and 95% bootstrap CI:
- Slope of log2(ratio) vs log2 p: h=48 1.014 (0.969–1.085); h=64 1.009 (0.973–1.085); h=80 1.007 (0.989–1.040); h=100 1.017 (0.994–1.048).
- Exponent of the relation count in h: k=40 0.74 (0.46–1.15); k=48 1.05 (0.72–1.54); k=56 0.81 (0.65–1.08).

### Supplement, small p (`table_supp.md`, `supp_ratios.json`)

| k | h | struct / control (95% CI) | (struct − global floor) / control |
|---|---|---|---|
| 22 | 64 | 0.97 (0.95–1.00) | 0.97 |
| 22 | 100 | 1.00 (0.99–1.00) | 1.00 |
| 24 | 100 | 0.98 (0.97–1.00) | 0.98 |
| 26 | 32 | 7.00 (3.48–14.07) | 4.17 |
| 26 | 100 | 0.96 (0.94–0.99) | 0.96 |
| 28 | 80 | 0.83 (0.75–0.91) | 0.76 |
| 30 | 48 | 3.80 (2.15–6.71) | 1.35 |
| 30 | 100 | 1.14 (0.99–1.31) | 1.04 |

Sum-collision counts in the structured base and the control agree within 0.5% in every cell.

### Random-target filter (`criterion_results.json`)

| p | targets factored | median core bits | passing (core <= 8h^4) | recall on true relations |
|---|---|---|---|---|
| 2^40 | 100,000 | 77.5 | 0 | 35/45 |
| 2^48 | 30,000 | 93.5 | 0 | 72/72 |
| 2^56 | 10,000 | 109.4 | 0 | 120/120 |

At 2^40 recall falls short because x_R reaches about h^5 ≈ 2^33 > √p = 2^20, so rational reconstruction returns the wrong representative. Halving verification was never invoked because no random target passed.

Verification: 1,722 / 1,722 listed relations are genuine group relations (`verify_results.json`).

## Verdict reasoning

The success clause asks for a yield above B^3/p^2 by a factor that grows with p, with a CI excluding a constant. Exhaustive enumeration makes the yield exact; the ratio grows like p^{1.02 ± 0.03}. The kill clause needs a ratio in [0.8, 1.25] at every p; it is ≥ 84 everywhere at main scale. The verdict on the frozen criterion is therefore **SUCCESS**.

That success does not carry the intended meaning. The yield splits into a global floor C(h) ≈ 35–40 relations at h = 100, the same at every p (characteristic-0 relations in the few twist classes holding two or more base points), plus a generic part of size B^3/p^2 that the small-p supplement reproduces at 1.00 ± 0.04. So ratio − 1 ≈ C(h)·p/B^3 grows linearly in p whenever any global relation exists — the outcome the kill clause's stated reason ("global points over quadratic fields are independent") meant to exclude. The criterion did not subtract the floor.

In absolute terms the yield per target is about 40/p. A random target passes only if it is itself the reduction of a global small-height point: 0 times in 140,000 targets. The relations sit in twist groups holding O(1) base points each and cannot tie a random target's logarithm to the base. The predicted density h^c/√p with c ≤ 3 is not observed either; it is about h^{0.9}/p.

Under the other reading ("yield per target" = the random-target sample of step (b)), the measured yield is 0 at every p against a generic expectation of about 1e-8 per run; the ratio is not estimable, giving INCONCLUSIVE. Neither reading gives KILL.

## Limitations

- p only up to 2^56; h capped at 100 (B ≤ 6,200, about p^{0.12} at 2^56) against the prereg's p^{0.05..0.25}.
- Three main-scale p values, fewer than four doublings; the k = 22..30 supplement has only 2 primes each.
- PARI `core` (full factorization) instead of trial division plus ECM; random-target subsets cut to 30,000 and 10,000 at 2^48 and 2^56.
- The core threshold 8h^4 is a heuristic bound on the twist class.
- The k = 40, h = 100 cell has 3 primes.
- Bootstrap over only 3–4 primes per k.
- Nothing here is a claim about secp256k1 at 256 bits.

## Suggested lead-atlas update

Proposed **LEAD-ICP-kummer-ladder-height-closure**: disposition `closed_no_ic_value`, pending coordinator review of the criterion. Ladder closure is real but holds only inside quadratic-twist classes; every relation found is global; their count (~40 per prime at h = 100) is independent of p, so the per-target yield is ~h^{0.9}/p; the frozen criterion is met (slope 1.017, CI 0.994–1.048) only through this floor; 0 of 140,000 random targets passed the filter. Next action: amend the criterion template for global-floor leads so the generic comparison subtracts the characteristic-0 relation count or requires a yield above 1/B. The same reason applies to the adjacent LEAD-TRF-global-lift-small-height.
