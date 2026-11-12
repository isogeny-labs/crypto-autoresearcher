# SA-25 audit (main session, 2026-11-12)

An independent check of the executor's SA-25 report before its numbers are quoted. The verdict (KILL) stands, and the corank it rests on is now explained by a law that uses only class numbers. Code here (`floor_law.py`) is the main session's own and reads only `results/classes_p*.jsonl`. It does not reuse the executor's elimination code. Class files over 64 KiB are not in git under the artifacts policy. They stay on the campaign host, with their SHA-256 in `../OMITTED_FILES.tsv`. Re-run with `cd results && python3 ../audit/floor_law.py`.

## 1. Headline numbers recomputed from the raw class rows

| quantity | executor | recomputed |
|---|---|---|
| primes | 29 | 29 |
| min c_t/\|S_t\| over p >= 1e5 | 0.133 | 0.1333 (= 2/15) |
| min c_t among \|S_t\| >= 50 | 14 | 14 |
| classes with \|S_t\| >= 50 | 26,173 | 26,173 |
| classes with c_t <= 10 at 6800033, 10000019, 10000169 | 1, 0, 0 | 1, 0, 0 |

The identity c_t = \|S_t\| - (AL pairs) - (AL fixed points) - (reduced Hecke rank) holds in every class.

## 2. Structure of the relation module

- **Atkin-Lehner halves the Hecke rows.** After the AL substitution x_{w(s)} = -x_s (the AL constant has order 5, so its n-component is 0), the T_l row at w(s) equals the T_l row at s. The audit found the reduced Hecke rank equal to ceil(H/2) in 8,736 of 8,742 single-prime classes, where H is the number of Hecke rows.
- **Several Hecke primes saturate.** In 1,235 of 1,272 classes with two or more Hecke primes, the rank is below H/2. Relations for different l overlap.

## 3. Floor law (main-session hypothesis, tested here)

**Law.** c_t = (1/2) #{s in S_t : E_s is on the floor of the l-volcano for every l | f with l in L}, where L = {2,3,5,7,13,17,19,23} is the Hecke set used. A point on the floor of the l-volcano has v_l(conductor of End(E_s)) = v_l(f), so it has no full rational l-neighbourhood. Points off the floor for some l get their logs from closed relations. Floor points are left with only their AL partner.

**Prediction from class numbers alone.** The number of curves with End = O_{f'} is proportional to h(f'^2 D0) = h(D0) f' prod_{l | f'} (1 - (D0/l)/l), up to the unit index for D0 = -3, -4. Summing over f' | f gives the floor fraction. That fraction times \|S_t\|/2 predicts c_t with no relation data. Classes with f = 1 (corank \|S_t\|/2 trivially) and 11 | f are left out.

| subset | classes | \|c_t - predicted\| <= 1 | mean c/S measured | mean c/S predicted |
|---|---|---|---|---|
| one Hecke prime divides f | 8,528 | 99.7% | 0.3399 | 0.3398 |
| two | 1,202 | 96.9% | 0.2548 | 0.2541 |
| three | 51 | 84.3% | 0.1968 | 0.1952 |
| all with \|S_t\| >= 50 | 9,740 | 99.3% (99.8% within 2% of \|S_t\|) | | |

The largest mismatches are at p = 1009, where 14% of points are excluded as ambiguous, and at a few classes of p = 2081, 18341 and 37951 (up to 25% above prediction). They are not resolved here. Excluded neighbours drop relations, which can only raise c_t, consistent with every large mismatch being an excess.

**The minimum is analytic.** The per-prime floor fraction is smallest when l splits in Q(sqrt D0), where it equals 1 - 1/l. Hence:

    c_t/|S_t| >= (1/2) prod_{l | f, l in L} (1 - 1/l).

The measured minimum 0.1333 = 2/15 = (1/2)(1/2)(2/3)(4/5) is attained by exactly the three classes with f = 30 and 2, 3, 5 all split. In classes with \|S_t\| >= 50, the only cases below the bound are three f = 1 classes of odd size. There one AL-fixed point (2s = c0) pins its own unknown, giving c = (S - 1)/2.

## 4. Consequence beyond the measured range

With the frozen Hecke set the bound is (1/2) prod_{l in L} (1 - 1/l) = 0.090 at every p. So KILL's threshold of 0.05 cannot be reached at any size. Adding every Hecke prime only replaces the product by phi(f)/f >= e^{-gamma}/log log f (Mertens). Then the connection cost (c_t + 1) p/\|S_t\| is at least about p/(2 e^gamma log log p), which is p^{1-o(1)}. Getting phi(f)/f below 0.1 needs f divisible by every prime up to 257, so f > e^{237} (checked numerically). Since f^2 <= 4p, that rules out every p below about 2^{680}. **This relation source is linear in p, not square-root, for structural reasons.** The fitted exponent 0.88 in p is a finite-size effect of the \|S_t\| log p term and the minimum over classes.

## 5. Other checks

- **Relation validity.** The executor's true-log control (153,275 relations, 0 violations, 22 primes) and its point-identity verification of every relation cover this. Relation validity cannot be the source of a false KILL. A false KILL would need overestimated coranks, and the floor law rules that out independently.
- **Rho baseline.** n (the largest prime factor of #E11) is tiny at most primes, so rho on E11[n] is very cheap. The verdict does not depend on this. At the three primes picked with n >= #E/12 the ratio is still 2e3 to 8e3, and Section 4 makes the connection cost at least 0.09 p against sqrt(pi n/4) <= sqrt(p).
- **Prediction 4** (exponent at least 0.5) is ill-posed against log2 n, because n is not tied to p. Against log2 p it holds: 0.878 [0.858, 0.901]. As the executor states, the verdict does not depend on it.
- **"Relation source complete"** is met only literally, by classes with \|S_t\| <= 36. The audit agrees with the executor that this is degenerate.
