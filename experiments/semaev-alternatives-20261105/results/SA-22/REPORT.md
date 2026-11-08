# SA-22 REPORT: projected total solve time at 64-256 bits for every measured oracle

## Summary
**INCONCLUSIVE pending SA-21** against the frozen criteria (both SUCCESS and KILL require the model validated against SA-21's 20-40 bit measurements, which did not exist when this ran). On the substitute check (Table B, below) the model passes. The deciding quantities point at KILL by a very wide margin; they do not depend on the validation.

Deciding numbers (log2 of projected cost / rho, unpriced work at 0 / 0.1 / 1 GAE per field op):
- **Best arm at 128 bits:** generic pair table, +21.96 / +22.05 / +22.50 (with Heegner discount 0.13: +21.96 / +22.05 / +22.50, differs by under 0.2). At **256 bits** +43.3 / +43.4 / +43.9. It exceeds rho under every pricing and the gap grows as N^(1/6) (fitted 0.1667 per bit of log2 N). Prediction part 2 holds.
- **Best non-generic arm at 256 bits:** Edwards form lattice (delta = 1/8), +97.3 at lambda 0.1 (pair-table-free, all pricings within 0.5). The prediction's bound "at least 2^40" holds with margin 2^57. Every non-generic arm is above 2^97 at 256 bits and above 2^49 at 128 bits.
- Every arm's excess exponent between 128 and 256 bits (log2 ratio per bit): form lattices 0.37-0.39, ladders 0.33-0.47, msolve 0.51-0.53, generic 0.167. All positive, so every ratio grows with N (the m=3 certified ladder has no admissible factor base, B < 4, below 36 bits).
- Even with ALL B/2 factor-base relations free (Heegner discount pushed to 100%, far above the measured 13%) the target's own relation costs more than rho for every arm: generic pair table 2^1.2 x rho, form lattices 2^67 at 256 bits.

## What was run (all in /home/user/semaev-runs/SA-22/)
- `lll_bench.py` -> `lll_bench.json`: fpylll LLL (delta 0.99, 1 thread) on Coppersmith-shaped triangular lattices, dimension (2t+1)^2 = 25, 49, 81, 121 at 64/128/256-bit p. Fit sec = exp(-23.79) d^4.63 n^1.07 (max log residual 0.07). The 256-bit, d = 121 point timed out at 40 s and is excluded.
- `fieldop.py` -> `fieldop.json`: gmpy2 mulmod 32/39/71 ns at 64/128/256 bits (interpreter overhead included); model uses 60 ns at 256 bits.
- `model.py` -> `model_out.json`, `summarize.py` -> `results_table.md`, `summary.json`, `fig.py` -> `fig_sa22.png`, `validate_tableB.py` -> `validate_tableB.json`.
- Model: T = R A (1 + c_o) + build + lambda (LA + descent). R = (B/2)(1 - disc) + 1 relations, A = max(1, m! N / B^m), B <= 2 N^delta (oracle reach), B optimised on a 0.0025 grid in log_N, ladder rung t optimised. Linear algebra 2 w (B/2)^2 field ops (Wiedemann); descent term is 2 m B/2 and negligible. Rho = sqrt(pi N / 4) GAE.
- Oracle inputs: pair table (build B^2/2, 1 GAE per lookup; m = 3 variant with B lookups per call); Weierstrass form lattice delta = 1/9 and Edwards delta = 1/8 (SA-13/17/19, 3-dim LLL, cost from the LLL fit); Coppersmith ladders from SA-01/SA-20 certified delta(t) (Weierstrass t = 2..16, Edwards t = 2..12, dimension from the fit) plus an optimistic variant (delta = 1/6, dim 85); m = 3 ladders (SA-01 t <= 6, asymptote 1/24, dim (t+1)^3); msolve norm m = 3 digit (SA-04: columns ~ B^3.09, time ~ cols^2.57 measured or ^2 favourable, anchored at 124 s for B = 16); msolve Kummer tower m = 2 (SA-14: rows = 0.6 C(2t+D, D), D = 4 + floor((t-2)/4), time ~ rows^3.17 measured or ^2, anchored at 412 s for t = 9); Heegner discount 0.13 on the relation count.

## Results
Full tables: `results_table.md` (three pricings, ten sizes, plus the target-only bound). Selected log2(cost/rho), lambda 0.1:

| arm | 64 b | 128 b | 192 b | 256 b |
|---|---|---|---|---|
| generic pair table m=2 | 11.5 | 22.2 | 32.9 | 43.5 |
| generic table m=3 | 12.6 | 23.3 | 33.9 | 44.6 |
| Weierstrass form 1/9 | 27.7 | 51.5 | 76.1 | 100.8 |
| Edwards form 1/8 | 26.8 | 49.7 | 73.5 | 97.3 |
| ladder Weierstrass (cert) | 41.7 | 66.8 | 92.1 | 117.1 |
| ladder Edwards (cert) | 36.4 | 60.5 | 84.8 | 109.2 |
| ladder m=2 optimistic 1/6 | 45.6 | 66.4 | 87.4 | 108.6 |
| cuso/ladder m=3 (cert) | inf | 77.4 | 107.0 | 136.9 |
| cuso/ladder m=3 optimistic 1/24 | 61.1 | 87.0 | 113.3 | 139.8 |
| msolve norm m=3 | 46.4 | 79.3 | 112.2 | 145.1 |
| msolve tower m=2 | 34.5 | 66.7 | 98.5 | 134.5 |

Order across the pricing band: lambda changes the generic arm by 0.5 bits at 256 bits and the others by under 0.5, so the order (generic < form lattices < ladders < tower < m=3 ladders < msolve m=3) holds at 0, 0.1 and 1 at 128 and 256 bits. The msolve arms drive B to the grid floor (about 6 points): their oracle cost grows faster than attempts shrink, so they degrade to roughly N times a constant (log2 cost 273 at 256 bits, worse than exhaustive search).

Why the exponent decides it: with reach delta, one relation needs about N^(1 - m delta) attempts; the form lattice gives 7/9 (matches SA-13's "p^(7/9) per relation"), the ladder at 1/6 gives 2/3, m = 3 at 1/24 gives 7/8, all above 1/2. A reach above 1/m would be needed for N^(1/2).

Cross-check with SA-15: model break-even oracle cost for m = 4 at B = p^(1/5) is 3.1 / 22 / 80 / 452 GAE at 40 / 56 / 72 / 96 bits against SA-15's 6.8 / 26 / 84 / 456 (difference at 40 bits is the linear-algebra term).

Free-oracle frontier (oracle cost 0, linear algebra priced at 0.1): log2(cost/rho) for m = 2, 3, 4, 5, 6 at 256 bits is +42.7, +0.7, -24.4, -40.2, -52.5. A free decomposition oracle with m >= 4 beats rho at every size; m = 3 loses by a constant (about 1.6x); m = 2 never wins. Everything here therefore rests on charging the oracle, and the measured oracles are far from free.

## Validation (step 4)
SA-21: not available (directory contained only its curve generator). Substitute: Table B prime-field rows, recipe "folded table, m = 2", which is the pair-table arm with B = |F| points and B/2 columns.

| log2 r | |F| meas / model | IC GAE meas / model (lambda 0.1) | model / measured |
|---|---|---|---|
| 9.7 | 10 / 9.8 | 657 / 162 | 0.25 |
| 11.9 | 32 / 15.9 | 976 / 425 | 0.44 |
| 14.0 | 26 / 25.3 | 1663 / 1088 | 0.65 |
| 16.0 | 40 / 38.9 | 2978 / 2687 | 0.90 |
| 18.0 | 64 / 61.4 | 4300 / 6683 | 1.55 |
| 20.0 | 102 / 97.0 | 10960 / 16698 | 1.52 |
| 21.7 | 148 / 143 | 23170 / 36455 | 1.57 |
| 23.4 | 222 / 211 | 46021 / 79711 | 1.73 |

Within a factor 3 at every size from 11.9 bits up for lambda 0.1 (0.25 at 9.7 bits misses by 4x; lambda 1 gives 0.36), and 1.5-1.7 across the overlap with the prereg window (20.0-23.4 bits). The model predicts the optimal factor-base size to within 5%. The measured slope of log2(IC/rho) is 0.116 per bit (bootstrap 95% CI 0.03-0.23, bits >= 14) against the model's 1/6, so the exponent is consistent but not tightly pinned; the model slightly over-predicts and the over-prediction drifts upward (1.52 to 1.73). Not validated: 24-40 bits and any non-generic oracle (no toy IC run exists for the lattice or msolve arms), and not against SA-21's own clock.

## Verdict reasoning
- SUCCESS (some oracle below rho at 256 bits under every pricing): no. Smallest excess anywhere is the generic table at +43 bits; no lambda reverses an order by more than 1 bit.
- KILL (all oracles above rho at 128 and 256 bits, every pricing, model validated): all arms satisfy the inequality by at least 22 bits (generic) and 49 bits (non-generic) at 128, 43 and 97 at 256. The validation clause is only partly met (Table B, 20-23.4 bits, factor 1.7), so the frozen criterion returns INCONCLUSIVE until SA-21's points are compared.
- What decides it: run `validate_tableB.py` logic on SA-21's 20-40 bit totals (the model needs only the pair-table row, `ARMS['PT2 generic pair table (m=2)']`, and the measured clock converted at SA-21's own GAE time). If every point lies within 3x, the verdict becomes KILL with no change to the numbers above; a failure would be corrected in the PT2 constant (shift of at most a few bits), which cannot close a gap of 43 to 97 bits.

## Limitations
- Idealised lattice oracles: success probability 1 per in-reach call, no list-decoding or root-finding cost, delta from certificates or planted thresholds at toy sizes (64-128 bits), extrapolated to 256 bits.
- Relation count B/2 assumes rank is reached with no excess; Heegner discount applied as a flat 0.13 and not tied to the oracle's factor base (the Heegner points are not small-x).
- LLL law extrapolated from d <= 81 at 256 bits; msolve and tower laws from 3-4 points; msolve measured at 31-bit primes and not scaled to the field size (favourable to IC). Any of these shifts costs by tens of bits at most for the arms whose gap exceeds 97 bits.
- Descent charged as a negligible term; a per-FB-element descent would only raise IC cost.
- Timings were short single-core micro-benchmarks; no SA-21 clock was used.

## Suggested lead-atlas update
LEAD (Semaev-alternatives, cost-model closure): record "projected cost above rho for every measured oracle at 128 and 256 bits under pricing 0, 0.1, 1 GAE per field op (generic pair table +22 / +43 bits, best non-generic +50 / +97 bits at 128 / 256), pending validation against SA-21; the exponent bound is structural (relation cost N^(1 - m delta) with delta < 1/m)". Next action: compare to SA-21 totals; the only open route is a decomposition oracle with m delta > 1/2 at some m (free-oracle frontier: m >= 4 wins), which no measured oracle approaches (best delta/m pair: 1/6 at m = 2, 1/24 at m = 3).
