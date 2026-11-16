# SA-23 REPORT: section representation (integral sections of y^2 = x^3 + t^d + 1 over F_p(t))

**Verdict: KILL** (frozen criterion, first clause): c_hat's 95% CI lies entirely above 0.5 at k = 64, 128 and 256.
Deciding numbers: c_hat(64) = 1.84 [1.65, 2.11]; c_hat(128) = 1.86 [1.65, 2.12]; c_hat(256) = 1.85 [1.66, 2.11] (u = 0.80 [0.76, 0.89]; alpha = 0.387 [0.357, 0.413]).
The second KILL clause is NOT met (cells with S >= p/2 and p >= 47 exist: d=12, p=47 S=34, p=59 S=38, p=71 S=38); the verdict rests on the first clause only. Nothing about SUCCESS is open: the end-to-end solve is about 4e4 to 1.5e5 times slower than rho.

## What was run
- Enumerator in C (`src/enum.c`): exhaustive over X, top-down DFS, same set as the scout's square test (matches scout: d=6 gives 8 at every p; d=12 gives 62 at p=11 and 58 at p=23). One CPU, nice 10, host load about 1.0 during timings.
- Cells finished: d=6 at 22 primes (11..197), d=12 at 8 primes (11, 23, 47, 59, 71, 83, 107, 131), d=18 at p=17 only; 3 ordinary controls at d=12 (p=13, 37, 61). Each cell appended to `results/cells.jsonl`.
- Gram matrix, rank, exact lattice determinant, coverage on 3 fibres (t0 = 2, 3, 5) per cell. Facts 1-4 verified: surface identity on all sections, Gram PSD in every cell, d=6 rank 4 at all 22 p, specialisation homomorphism (2742 fibre checks over 4 cells, 0 mismatches; fibres where P+Q has a pole skipped), #E = p+1.
- Gate B: msolve 0.10.1 (found at `/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/msolve`), 20 planted + 20 random targets per cell at d=6 (22 cells) and d=12 (8 cells), 1201 calls, each logged with wall time, rc, closure degree, number of F_p sections, and verification on the surface and through R. Every verified call matched the enumeration table exactly.
- Fits: `analyze.py`, bootstrap over cells, 2000 resamples, seed 23. `fig_sa23.png` (12 KB). Full tables in `results/analysis.md`.
- End to end: `src/e2e.py` on d=12, p=131 (the largest cell where a lift is feasible): 5 DLs in G (order 11, r=7, 9 relation lifts + target lifts), all 5 verified [k]G0 = Q.

## Gate A results
| d | p | S | rank | det(lattice) | coverage_G (mean of 3 fibres) | |G| |
|---|---|---|---|---|---|---|
| 6 | 11..197 (22 primes) | 8 (all) | 4 (all) | 16 | 0.23..1.0 | 3..29 |
| 12 | 11 | 62 | 9 | 12288 | 1.0 | 3 |
| 12 | 23 | 58 | 8 | 4096 | 1.0 | 3 |
| 12 | 47 | 34 | 7 | 3072 | 1.0 | 3 |
| 12 | 59 | 38 | 8 | 9216 | 1.0 | 5 |
| 12 | 71 | 38 | 8 | 9216 | 1.0 | 3 |
| 12 | 83 | 34 | 7 | 3072 | 0.905 | 7 |
| 12 | 107 | 34 | 7 | 3072 | 1.0 | 3 |
| 12 | 131 | 34 | 7 | 3072 | 0.939 | 11 |
| 18 | 17 | 240 | 16 | 18939904 | 1.0 | 3 |

Minimum height of the sections is 2 chi in every cell (as the theory says). Coverage of the whole group E(F_p) (supplement): 0.92 at p=11 down to 0.25 at p=131 (d=12), 0.04 at p=197 (d=6).

Controls: d=6: 8 sections, rank 4 at every p (pass). Random polynomials g of degree d (20M each): 0 hits at (47,12) and (23,12), 7 at (11,12) (expected 11), 100 at (47,6) (expected 193 before the leading-coefficient factor); consistent with about p^{-3chi}. Ordinary cells at d=12: p=13: 8 sections (rank 3), p=61: 8 (rank 3), **p=37: 704 sections (rank 12)**, so the expectation "far fewer sections" fails at p=37 (37 = 1 mod 36). Flagged, not reinterpreted.

Fit log2 S = alpha d + beta log2 p + gamma over 31 supersingular cells with S >= 2: alpha = 0.387 [0.357, 0.413]; beta = -0.072 [-0.147, -0.003]; gamma = 1.12 [0.76, 1.69]. alpha <= 0.8 and S is bounded or slowly falling in p at fixed d, as predicted. d*(2^k) = 174, 354, 708 for k = 64, 128, 256 (rounded up to a multiple of 6); U = 147, 297, 592. Out of sample: fit without the largest cell (d=18, p=17) predicts log2 S = 7.74, observed 7.91.

## Gate B results
Planted lifts, median wall time: d=6 (U=7): 4.7 ms at every p (this is the process-start floor); d=12 (U=12): 0.07 to 0.16 s (p=23: 0.157, p=47: 0.067, p=131 about 0.066; closure degree 3 to 12). d=18, p=17 (U=17): first planted lift **did not finish in 600 s** (censored, rc -9). Only one d=18 call was made. d=12, p=11: msolve returned an empty output on all 40 calls (solver failure, excluded). Random targets in G are liftable with frequency 0 to 1 depending on the cell (coverage of the image set), as expected.

Fit log2 T = u U + b0 over 30 cell medians: u = 0.80 [0.76, 0.89]. Out of sample (drop d=12, p=131): predicted log2 T = -3.69, observed -3.93. Using the censored d=18 point (T > 600 s against about 0.07 s at U=12) gives u >= 2.6 between U=12 and 17, so the reported u is conservative. c_hat = u U(2^k)/k, with the out-of-sample fits: 1.85, 1.87, 1.88 (same conclusion).

End to end (d=12, p=131, |G| = 11, r = 7): 5/5 DLs verified. Time per DL 0.57 to 2.6 s including a share of the shared precompute (2.06 s for 9 relation lifts) versus rho 1.0e-5 to 1.7e-5 s on the same group, a ratio of about 4e4 to 1.5e5; ratio CI excludes 1, in the wrong direction. A cell with d=18 could not be attempted (lift > 600 s).

## Borderline readings and limitations (flagged, not resolved)
1. d* rounded up to a multiple of 6 (6 | d is required). With continuous d* the c_hat values are lower by about 1 percent; the conclusion does not change.
2. u rests on d=6 timings at the process-start floor and on d=12; the d=18 cell is censored and excluded from the fit. Either correction would raise u, hence c_hat.
3. Bootstrap resamples Gate A cells and Gate B cells independently (they overlap).
4. Gate A coverage: |G| is the largest prime factor of p+1, which is 3 to 29 in all feasible cells (d divides p+1), so coverage_G is nearly trivial; the frozen definition was used. Step 8's "largest cell with coverage >= 1/2" is therefore d=18 p=17 by cell order, but its lift is infeasible; the e2e was run on d=12 p=131 instead.
5. Only d=6, 12 have >= 4 primes; d=18 has one cell (p=17); d=24, 30 have none. Exhaustive cost (about 100 ns per leaf at chi=2, 210 ns at chi=3) puts d=18 p=53 at about 1e5 s and d=24 p=23 at about 3e5 s; msolve full-system enumeration does not finish even for d=6 p=11 within 600 s, so "cross-check one cell per d both ways" was replaced by msolve-vs-table agreement on every Gate B lift. alpha therefore rests essentially on d=6, 12 and one d=18 point.
6. d=12 p=167 (about 1.9 h) was not run. Two initial Gate B records at (23, 12, R=(0,16)) failed verification once and not on 40 repeats; that batch was rerun and replaced (cause unknown).
7. Baselines: enumeration-and-specialise (enumeration 0.01 s to 1830 s per cell) and a hash lookup of R in the sp-image table (7e-5 s build, d=12) stand in for "MITM on the known lattice"; a lattice-coefficient MITM was not implemented. Only msolve was tested as lift solver; a solver that uses the explicit lattice is not excluded.
8. j = 0, supersingular family only. The ordinary p=37 cell has far more sections (704, rank 12) than any supersingular cell and is outside the frozen family; it was not pursued.

All departures are in `DEVIATIONS.md` (D1 to D8). Files: `/home/user/semaev-runs/SA-23/{REPORT.md, DEVIATIONS.md, analyze.py, fig_sa23.png, results/*, src/*, logs/*}`.

## Suggested lead-atlas line
SA-23 (2026-11-10): section representation on y^2=x^3+t^d+1, p=-1 mod d. KILL. Integral sections S(p,d) about 2^{0.39 d} (bounded in p; d=6: 8, d=12: 34 to 62, d=18: 240 at p=17); msolve lift costs about 2^{0.8 U} (U=5d/6+2; d=18 > 600 s), so c_hat about 1.85 [1.65, 2.11] at k=64..256 (> 0.5); e2e 4e4x slower than rho on a group of order 11. Unexplored: ordinary p=1 mod d cells (p=37, d=12 has 704 sections), d >= 24, a lift solver that uses the lattice.
