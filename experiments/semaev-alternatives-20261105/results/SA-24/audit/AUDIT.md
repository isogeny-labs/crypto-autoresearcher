# SA-24 audit (main session, 2026-11-12)

An independent check of the executor's SA-24 report. **Verdict under the frozen criteria: INCONCLUSIVE, as the executor states.** The first half of KILL holds robustly. The second half fails only because the frozen text says "every cell" and five cells were never powered, although the protocol itself asks for more samples when the expected count is below 50. Following the campaign rule that inconclusive results get more experiments, the completion run is registered as SA-24c (`prereg/round6/SA-24c.md`). Nothing here is reinterpreted.

## 1. The A1 relation structure (checked algebraically and in the raw data)

- **Algebra.** For R = (X0, Y0) on E1 the pullback has u proportional to (r^2 - X0) z^2 + 2 r z + 1. Substituting z = 1/(x - r) gives (x^2 - X0)/(x - r)^2. So the roots of u are exactly the two points with x = +-sqrt(X0): the fibre of the double cover. A pullback splits over F exactly when X0 = x0^2 with 1 <= x0 <= B.
- **Consequence.** A1 as frozen, with R_j = a_j pb(P) + b_j pb(Q), never leaves pb(E1). Its relations are hits of the set {T in E1 : x(T) is a small square}, about B points out of p. Each relation carries one new unknown, the fibre sum l(P) + l(sigma P) = log T, so about B relations are needed at about p/B trials each. That is about p trials for every B.
- **Raw data agree** (recomputed from `results/a1_*.jsonl`, solved and verified runs only, 9 per cell):

| log2 p | delta 0.5: trials/p | (trials/relation)·(B/p) | delta 0.7: trials/p | delta 0.9: trials/p |
|---|---|---|---|---|
| 12 | 0.92 | 0.74 | 0.83 | 0.97 |
| 16 | 1.59 | 1.60 | 1.01 | 0.98 |
| 20 | 1.04 | 1.00 | 0.99 | 1.00 |
| 24 | 1.05 | 1.05 | 0.99 | 1.00 |

  The relation count is linear in p at every B, so A1's exponent in p is 1. The fitted 0.81 to 0.93 against log2 n1 sits below 1 because n1 = #E1/cofactor, with the cofactor varying from 1 to 16, and because of fixed overhead at small sizes. OLS on raw Jacobian-add counts gives 0.86, 0.91 and 0.89 at delta 0.5, 0.7 and 0.9 (sizes 10 to 20). That agrees with the executor's bootstrap values.
- **Rho** recomputed: 0.39 (n = 120, sizes 10 to 24) and 0.45 (n = 90, sizes 14 to 24) on counted E1 additions, the same as the executor's. Rho's slope below 0.5 comes from size-independent overhead. It makes rho look cheaper at small sizes, so it works against KILL, and the gap to A1 (0.4 or more) is far larger than that bias.

**Conclusion for A1.** The first clause of KILL ("A1's alpha CI lies entirely above rho's") holds in every variant the executor ran, and it is structural. As the prereg wrote it, the Jacobian factor base restricted to the target subgroup is a filter on E1 itself.

## 2. A2/A3: the ratio is an identity, and the 4-5 sigma cells are about 2 sigma

- The sampler draws a uniform monic u and weights it by w(u) = #v (deviation 1, validated by exhaustive enumeration at p = 1019 and 4091 for genus 2 and p = 211 and 307 for genus 3). The measured/null ratio is therefore a Monte Carlo estimate of the null itself, with expectation exactly 1. The executor is right that A2/A3 cannot show an excess for uniform elements. The prereg's "growing excess" route to SUCCESS was not reachable by construction.
- **Weights explain the apparent outliers.** A split pair in F has weight 4 in genus 2 (two sign choices at each of two roots), and a split triple has weight 8 in genus 3. In event counts, the cells whose bootstrap CI excludes 1 are:
  - 2^12/0.4: about 2.0 sigma;
  - 2^20/0.7: about 2.4 sigma;
  - 2^24/0.5: about 2.1 sigma (observed 604 weighted, about 151 events, against about 179 expected).
  
  Across 38 powered cells, a few 2-sigma cells are expected. No anomaly.
- **The flagged per-delta slope at delta 0.5** (CI [-0.035, -0.002]) rests on the 2^24/0.5 cell. SA-24c tops that cell up to at least 500 expected events, so the question is settled by data, not by reading. The frozen text defines the slope per genus ("at either genus, ... has a slope"), and both pooled per-genus CIs contain 0. The per-delta slopes are the executor's addition. Reported, not used to decide.

## 3. The unpowered cells

| arm | cell | expected weighted | expected events | trials run (3 curves) |
|---|---|---|---|---|
| A2 | 2^24, 0.3 | 1.05 | about 0.26 | 6e9 |
| A2 | 2^24, 0.4 | 26.8 | about 6.7 | 6e9 |
| A3 | 2^16, 0.5 | 22.7 | about 2.8 | 3e8 |
| A3 | 2^20, 0.5 | 0.35 | about 0.04 | 3e8 |
| A3 | 2^20, 0.6 | 23.7 | about 3.0 | 3e8 |

The executor judged these "unmeasurable" at 3e11 to 4e10 trials. A hash filter makes them cheap. In genus 2, uniform (c1, c0) is looked up in the set of (a + b, ab) over pairs of z-roots of F, about 1e4 entries, at a few ns per trial. In genus 3, c2 is drawn uniformly, then (c1, c0) is drawn against a per-c2 set. SA-24c runs them to at least 50 expected events (not weighted counts). At that power a ratio outside [0.5, 2] has probability below 1e-3 under the null. So the completed "every cell" clause becomes a real test rather than a coin toss.

## 4. What the frozen A1 did not test, and SA-24c's exploratory arm

The question behind SA-24 was index calculus with a factor base in the Jacobian. That is Gaudry's algorithm, whose random elements are uniform in Jac(C), not confined to pb(E1). A1 as frozen did not test it. SA-24c adds an exploratory arm, A1-full, which randomises each walk step with an element of the cofactor subgroup [n1]Jac(C). The n1-projection of each relation then constrains the logs of individual factor-base points, as in Gaudry's algorithm. It does not enter any verdict. Its frozen predictions are textbook: per-relation rate equal to the uniform null, cost about p^{4/3} at B about p^{2/3}, worse than both degenerate A1 and rho.

## 5. Why covers cannot help over a prime field (context)

The target lives in a subgroup of Jac(C) isomorphic to E1[n1]. A factor base in Jac(C) either stays inside pb(E1), where it is a filter on E1 (section 1), or uses the whole Jacobian, where Gaudry-type index calculus costs at least q^{2-2/g} in the size q of the field of definition. That is at least p for g >= 2 when the cover is defined over F_p. Covers beat rho only when the cover is defined over a smaller field than E (Weil descent, GHS: E over F_{q^n} and C over F_q). A prime field has no smaller field. This matches the round-5 classification.
