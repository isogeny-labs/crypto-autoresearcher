# SA-15b: every calibrated decomposition solver on the frozen m = 4 instance set

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary
**KILL** against the frozen criterion: every non-generic solver recovers 0 instances at p ~ 2^40 and p ~ 2^56. The prediction holds. Only the generic pair table recovers (100/100 at both sizes), at a cost of about B^2/3 to B^2 group additions, far above the p^(1/10) break-even.

The instances.json SHA-256 (e9b681a6...) was verified before use.

Deciding numbers:
- **Pair table.** Recovers 100/100 at 2^40 (B = 256) and 100/100 at 2^56 (B = 2352); every hit verified by group law and equal to the planted x's. Mean scan 11,949 adds (2^40) and 859,010 adds (2^56) per instance; one-off table build 36,720 and 2,651,904 adds. Against SA-15's break-even T* (6.8 ops at 2^40, 26 at 2^56) the scan is 1,760× and 33,000× over. Against matched rho the scan is 0.0129 and 0.0036 (single shot 0.052 and 0.0148); the rho ratio is not the comparison that matters for index calculus.
- **Vieta-graded t=1 lattice (dim 495).** 0 recoveries on 60 instances at 2^40 and 20 at 2^56. Howgrave-Graham margin (log2 p − log2 det^(1/dim)): −138 bits (2^40), −190 bits (2^56). No reduced vector has L1 norm below p, and none vanishes over Z at the planted e.
- **S_5 t=1 lattice (dim 6561).** Not executable on this host (basis over 1 GB; LLL far outside the 60 s cap). Exact HG margin −128 bits (2^40) and −179 bits (2^56). SA-01 certifies reach 0.0 at m=4, t=1; the asymptote is 1/80 against the 1/5 needed.
- **SA-16 lattices (vieta_cvp, L2diag, L3).** 0/100 at each of 2^40, 2^56, 2^72, 2^96 on the m=4 set. Positive controls on their native families at B = p^(1/5), 40 trials per cell: vieta_cvp 40/40 at both sizes on the degenerate conic; L2diag 6/40 (2^40) and 3/40 (2^56) on R = [2]P; L3 2/40 at both sizes on R = [2]P. Generic m=2: vieta_cvp 0 and L2diag 0 at both sizes; L3 1/40 at 2^40 and 0/40 at 2^56.
- **msolve.** Refuses characteristic ≥ 2^31, so it cannot read the instances (p ≥ 2^40). On a scaled replica (same builder, B = p^(1/5), p < 2^31) it solves B = 4 (0.2 s) and B = 8 (~8 s) and times out at 60 s from B = 16. The real set starts at B = 256.

## What was run
| file | role |
|---|---|
| pairtable.c, run_pairtable.py | Signed small points, table of all pair sums, scan of R − Q against the table; Python re-verifies each hit by group law. |
| vieta_poly.py, vieta_lattice.py, run_vieta_batch.sh | S_5 in e1..e4 (495 monomials) as the 1-dimensional kernel of evaluations at 520 random on-curve decompositions of the instance's R, checked to vanish at the planted e; then the t=1 basic Jochemsz–May lattice with column bounds (4B, 6B², 4B³, B⁴), fpylll LLL, 60 s cap. |
| s5_analytic.py | Exact size and HG margin of the t=1 S_5 lattice. |
| run_sa16_solvers.py | SA-16 solvers as positive controls, and applied to the 400 instances. |
| run_msolve.py | msolve on the SA-04 norm presentation with the vanishing-polynomial base, scaled replica. |
| make_fig.py, fig_sa15b.png, results_table.md | Figure and summary table. |

Everything ran single process under nice 10; nothing was left running.

## Results
| solver | p | run | recovered | cost / instance |
|---|---|---|---|---|
| pair table | 2^40 | 100 | 100 | 11,949 adds scan (+36,720 build); B² = 65,536 |
| pair table | 2^56 | 100 | 100 | 859,010 adds scan (+2,651,904 build); B² = 5.53e6; 0.77 s |
| pair table | 2^72, 2^96 | 0 | n/a | B²/2 = 2.3e8 and 1.8e11 table entries; over 7 GB; not run |
| Vieta t=1 lattice | 2^40 | 60 | 0 | LLL 4–5 s, dim 495, margin −138 bits |
| Vieta t=1 lattice | 2^56 | 20 | 0 | LLL ~5 s, margin −190 bits |
| S_5 t=1 lattice | 2^40, 2^56 | 0 | 0 | dim 6561, margin −128 / −179 bits |
| vieta_cvp, L2diag, L3 | 2^40 to 2^96 | 100 each | 0 | 0.05–10 ms |
| msolve | 2^40+ | 0 | 0 | not applicable (characteristic < 2^31 only); replica solves B ≤ 8 only |

## Verdict reasoning
KILL requires every non-generic solver to recover 0 at 2^40 and 2^56. Measured: the Vieta lattice recovered 0 of 80 instances run; the SA-16 solvers recovered 0 of 400 each; the S_5 lattice and msolve could not be run on the set at all. SUCCESS requires a non-generic solver to recover at least 10% at 2^56 at cost below the pair table; none did. The Vieta result is not luck: its HG margin is 138–190 bits negative, and the S_5 margin 128–179 bits negative.

## Limitations
- The S_5 lattice and msolve have no executed row on the real set; for them "recovers 0" rests on the exact HG margin, SA-01's certified 0.0 at m=4 t=1, and msolve's 31-bit characteristic limit with a scaled-replica ceiling at B = 8.
- The Vieta lattice covered 60 of 100 instances at 2^40 and 20 of 100 at 2^56. The margin depends only on (p, B), so it is the same for every instance. t=2 (dim 4845) was not run.
- The pair table at 2^72 and 2^96 was not run (memory); the prereg asks for those sizes only if a non-generic solver recovers at 2^56. The pair table skips decompositions with a repeated x and stops at the first hit.
- SA-16's solvers are two-unknown solvers; their m=4 row only shows they are not misled into false recoveries. Their control rows used fresh primes, not the SA-15 primes.
- The msolve replica uses a random curve rather than y² = x³ + 7; "solved" means the F4 run finished, without re-checking the planted point in the Gröbner basis.
- Host load was high, so wall times are indicative only; op counts are exact.

## Suggested lead-atlas update
The m=4 decomposition-oracle lead set against the SA-15 instance set: closed negative for the lattice, Vieta, SA-16 and Gröbner (msolve) presentations at p ~ 2^40 and 2^56. Deciding numbers: Vieta t=1 HG margin −138 and −190 bits with 0/80 recoveries; S_5 t=1 margin −128 and −179 bits; msolve ceiling B = 8 at 60 s; pair table the only solver that recovers (100/100 at both sizes) at ~1.2e4 and 8.6e5 additions, 3–4 orders of magnitude over the p^(1/10) oracle budget (T* = 6.8 and 26). Next action: any future oracle must first beat the pair-table cost line (~B²/3) on this frozen set and show a positive HG margin at t=1 for B = p^(1/5). The lead stays open only for structurally different (non-lattice, non-Gröbner) oracles.

## Deviations (full text in DEVIATIONS.md)
1. msolve refuses characteristic ≥ 2^31; a scaled replica was used.
2. The S_5 lattice was not executed (dim 6561, over the memory limit); the exact HG margin was computed instead.
3. The Vieta lattice ran on 60 instances (2^40) and 20 (2^56).
4. SA-16 solvers were run as native-family controls plus direct application to the m=4 set.
5. The pair table skips repeated-x decompositions; 2^72/2^96 were not run.
6. The pair table is a C program driven from Python, with Python group-law verification of every hit.
