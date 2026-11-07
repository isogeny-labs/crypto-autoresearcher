# Campaign summary: alternatives to Semaev summation polynomials (prime-field ECDLP)

Registered 2026-11-05 in isogeny-labs/crypto-autoresearcher#3028; results landed in #3033 and this follow-up. Each row links to `results/SA-NN/REPORT.md`. Corrections to the campaign report are in `ERRATA.md`.

**Bottom line.** No direction reported a usable success. Eight directions were killed against their frozen criteria. The lattice wall at reach 1/6, 1/24, 1/80 (arity 2, 3, 4) was reproduced from five independent directions (SA-01, 04, 06, 08, 18) and holds for every presentation tested: x-coordinates, Vieta coordinates, the Riemann–Roch norm system, special j-invariants and 2-torsion symmetrisation. Both new structural handles from the report (the Vieta conic and the Γ₀(p) binary-form view) are closed.

| ID | Direction | Verdict | Deciding number |
|---|---|---|---|
| SA-01 | Lattice ceilings, six presentations | INCONCLUSIVE (leans kill) | best m = 3 reach 0.0306 vs success line 0.25; none beats single-polynomial reach |
| SA-02 | Vieta-conic sieve | KILL | sieve exponent 1.04 [0.99, 1.08] at 64 bits; reach 1/6 |
| SA-03 | Γ₀(p) binary-form census | KILL | structured/small ratio ∝ B^-10; enumeration exponent 1.81 [1.64, 1.96] |
| SA-04 | Riemann–Roch norm presentation | KILL | reach equals S_{m+1}; F4 degree 5, 6, 7 at B = 4, 8, 16 (m = 3) |
| SA-05 | Height-closed Kummer ladders | SUCCESS on the letter, no IC value (criterion flaw) | all 1,722 relations global; 0 of 140,000 random targets pass |
| SA-06 | Special-j and torsion lattices | KILL | reach 1/80 at m = 4 in all six cells |
| SA-07 | Mixed Z/F_p integer programming | KILL (off-the-shelf SCIP) | node exponents 7.6–10.0 at m = 3; 0/76 solved at B ≥ 32 |
| SA-08 | Capacity / determinant ceiling | INCONCLUSIVE | determinant ceiling 1/6, 1/24 proved over all supports |
| SA-09 | Heegner norm relations | INCONCLUSIVE (practically negative) | rank/points 0.238; extrapolates to ~0.07 |
| SA-10 | Squarefree-part collisions | KILL | 1 pair up to 2^22; exponent 0.0 |
| SA-11 | Cavity solving-degree predictor | KILL | 11/25 cells within ±1; tower slope 1.0 vs 0.233 |
| SA-12 | Learned shift families (CPU search) | INCONCLUSIVE (scale-limited) | best certified reach 0.127 at n ≤ 150 |
| SA-13 | Lattice-query lower bound | INCONCLUSIVE | restricted bound p^(7/9) per relation (one step sketched) |
| SA-14 | Yokoyama for towers | INCONCLUSIVE | Macaulay degree 2t+4 proved; F4 degree 4–5 at t ≤ 9 |
| SA-15 | m = 4 instance set | INCONCLUSIVE (adoption) | 400/400 planted instances verified and hashed |
| SA-16 | Positive-control calibration | KILL (solver prediction) | `L3` and raw bivariate Coppersmith fail the controls |
| SA-17 | Function-field mirror | see `results/SA-17/REPORT.md` | — |
| SA-18 | Determinant-method oracle | KILL | provable reach rises toward 1/6, never above |

**Open threads the executors named.**
- An exact-arithmetic, lattice-reduced branch-and-bound (SA-07) must beat brute force at m = 3, B = 16 before integer programming is reconsidered.
- The F4 degree at tower length 10 (SA-14) decides whether PKM-tower degree growth is slower than the repository's fit.
- A successive-minima or first-minimum bound on the Rees lattice (SA-08) would extend the 1/6 ceiling beyond determinant arguments.
- Equidistribution mod p^k and structured search inside the lattice (SA-13) are the gaps between the restricted lower bound and the full conjecture.
- The non-CM curve y² = x³ + 7 was not run for Heegner relations (SA-09).

**Scope.** Toy-scale runs on a shared 4-core host; executors were Sonnet, with six resumed by Opus after a usage limit. Nothing here is a claim about a deployed curve, and no lead disposition was changed; each REPORT.md ends with a suggested lead-atlas update for separate review.
