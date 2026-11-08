# Campaign summary: alternatives to Semaev summation polynomials (prime-field ECDLP)

Registered 2026-11-05 in isogeny-labs/crypto-autoresearcher#3028; results landed in #3033 and this follow-up. Each row links to `results/SA-NN/REPORT.md`. Corrections to the campaign report are in `ERRATA.md`.

**Bottom line.** No direction reported a usable success. Nine directions were killed against their frozen criteria. The other nine are open: an INCONCLUSIVE verdict is not a kill, and each open direction has a round-2 pre-registration in `prereg/round2/`. The lattice wall at reach 1/6, 1/24, 1/80 (arity 2, 3, 4) was reproduced from five independent directions (SA-01, 04, 06, 08, 18) and holds for every presentation tested: x-coordinates, Vieta coordinates, the Riemann–Roch norm system, special j-invariants and 2-torsion symmetrisation. Both new structural handles from the report (the Vieta conic and the Γ₀(p) binary-form view) are closed.

| ID | Direction | Verdict | Deciding number |
|---|---|---|---|
| SA-01 | Lattice ceilings, six presentations | INCONCLUSIVE (open; round 2 SA-01b) | best m = 3 reach 0.0306 vs success line 0.25; none beats single-polynomial reach |
| SA-02 | Vieta-conic sieve | KILL | sieve exponent 1.04 [0.99, 1.08] at 64 bits; reach 1/6 |
| SA-03 | Γ₀(p) binary-form census | KILL | structured/small ratio ∝ B^-10; enumeration exponent 1.81 [1.64, 1.96] |
| SA-04 | Riemann–Roch norm presentation | KILL | reach equals S_{m+1}; F4 degree 5, 6, 7 at B = 4, 8, 16 (m = 3) |
| SA-05 | Height-closed Kummer ladders | SUCCESS on the letter; criterion flaw (open; round 2 SA-05b) | all 1,722 relations global; 0 of 140,000 random targets pass |
| SA-06 | Special-j and torsion lattices | KILL | reach 1/80 at m = 4 in all six cells |
| SA-07 | Mixed Z/F_p integer programming | KILL (off-the-shelf SCIP) | node exponents 7.6–10.0 at m = 3; 0/76 solved at B ≥ 32 |
| SA-08 | Capacity / determinant ceiling | INCONCLUSIVE (open; round 2 SA-08b) | determinant ceiling 1/6, 1/24 proved over all supports |
| SA-09 | Heegner norm relations | INCONCLUSIVE (open; round 2 SA-09b) | rank/points 0.238; extrapolates to ~0.07 |
| SA-10 | Squarefree-part collisions | KILL | 1 pair up to 2^22; exponent 0.0 |
| SA-11 | Cavity solving-degree predictor | KILL | 11/25 cells within ±1; tower slope 1.0 vs 0.233 |
| SA-12 | Learned shift families (CPU search) | INCONCLUSIVE, scale-limited (open; round 2 SA-12b) | best certified reach 0.127 at n ≤ 150 |
| SA-13 | Lattice-query lower bound | INCONCLUSIVE (open; round 2 SA-13b) | restricted bound p^(7/9) per relation (one step sketched) |
| SA-14 | Yokoyama for towers | INCONCLUSIVE (open; round 2 SA-14b) | Macaulay degree 2t+4 proved; F4 degree 4–5 at t ≤ 9 |
| SA-15 | m = 4 instance set | INCONCLUSIVE, adoption (open; round 2 SA-15b) | 400/400 planted instances verified and hashed |
| SA-16 | Positive-control calibration | KILL (solver prediction) | `L3` and raw bivariate Coppersmith fail the controls |
| SA-17 | Function-field mirror | KILL | FF reach 1/9 (m = 2) and 1/50 (m = 3) vs 1/m needed; F_p gap 0.001 ± 0.003 |
| SA-18 | Determinant-method oracle | KILL | provable reach rises toward 1/6, never above |

**The deepest finding (SA-17).** The lattice wall is not caused by archimedean carries. In the function-field twin F_q[t]/(π), where lattice reduction is exact and there are no carries, the same lattices hit the same thresholds (1/9 at m = 2, 1/50 at m = 3). The bottleneck is the degree budget of S_{m+1} as a polynomial in x_R. A future lattice proposal has to lower that budget with a different relation polynomial or coordinates, not avoid carries.

**Open threads the executors named.**
- An exact-arithmetic, lattice-reduced branch-and-bound (SA-07) must beat brute force at m = 3, B = 16 before integer programming is reconsidered.
- The F4 degree at tower length 10 (SA-14) decides whether PKM-tower degree growth is slower than the repository's fit.
- A successive-minima or first-minimum bound on the Rees lattice (SA-08) would extend the 1/6 ceiling beyond determinant arguments.
- Equidistribution mod p^k and structured search inside the lattice (SA-13) are the gaps between the restricted lower bound and the full conjecture.
- The non-CM curve y² = x³ + 7 was not run for Heegner relations (SA-09).

**Scope.** Toy-scale runs on a shared 4-core host; executors were Sonnet, with six resumed by Opus after a usage limit. Nothing here is a claim about a deployed curve, and no lead disposition was changed; each REPORT.md ends with a suggested lead-atlas update for separate review.

## Round 2

Pre-registrations in `prereg/round2/`; results in `results/SA-NNb/`.

| ID | Direction | Verdict | Deciding number |
|---|---|---|---|
| SA-15b | Every solver on the frozen m = 4 set | KILL | pair table 100/100 at 1.2e4 and 8.6e5 adds (2^40, 2^56); every non-generic solver 0; Vieta lattice margin −138/−190 bits |
| SA-13b | Lattice-query lower bound, round 2 | INCONCLUSIVE (open) | volume inequality now proved (C = 2.86, worst measured 0.79); Ω(p^{7/9}) complete for per-target non-adaptive queries; mod p² proof has two named gaps; square-restricted enumeration exponent 1.016 [1.011, 1.023] |
| SA-05b | Kummer ladders, global floor subtracted | KILL | corrected ratio 0.836, 0.948, 0.900 at 2^32, 2^36, 2^40 (slope 0.008 [−0.011, 0.033]); random-target yield 0.98–1.01× generic |
| SA-09b | Heegner relations, non-CM curve and second field | KILL (sensitivity flag: ratio not monotone after B = 130; 0.151 at B = 300) | 37a1 rank/points 0.134 at B = 500; descent hit rate equal to control (diff CI [−0.014, +0.023]) |
| SA-14b | PKM tower F4 degree at t = 10 | KILL | degree 6 at t = 10 on 3/3 seeds and in the matched null; steps at t = 2, 6, 10 (slope 1/4); matrix rows ×3.1 per level |
| SA-08b | Rees-lattice first minima vs determinant | KILL (interpretation flag: "excess shrinks monotonically" read as signed excess; at 48 and 64 bits the excess crosses zero and its magnitude then grows slightly, by ≤ 0.004) | λ₂ crossing tracks the determinant threshold δ_K; extrapolations 0.145–0.165, all below 1/6; K = 1 excess (+0.05) is finite-size |
| SA-01b | Ceilings for norm/chained presentations at m = 3, m = 4 lattices | INCONCLUSIVE (open) | best m = 3 reach 0.0306 vs success 0.0467; (iii)/(iv) gain over Vieta/S_4 only 1.8–4.4% and shrinking; kill blocked by 3-point series and one LOO end 0.0007 above the band; cuso install blocked |
| SA-12b | Learned shift families at n ≤ 300 | KILL (noise flag: seed-to-seed search spread ≈ 0.007 exceeds the 0.002/0.005 thresholds; convex reference is a search lower bound, not an exact optimum) | full − convex by seed −0.0087, +0.0014, −0.0002; best reach 0.134 at n ≤ 300 |

**Round 2 outcome.** Of the eight open directions, SA-05b, SA-14b and SA-15b are clean kills; SA-08b, SA-09b and SA-12b are kills that depend on a stated reading of the criterion or on noise, and are flagged; SA-01b and SA-13b remain open. For SA-01b the decisive next step is an automated Coppersmith certificate (`cuso`), whose install was blocked in this session; for SA-13b it is the two named proof steps for modulus p².

## Round 3

Pre-registrations in `prereg/round3/`; results in `results/SA-NNc/` and `results/SA-19/`.

| ID | Direction | Verdict | Deciding number |
|---|---|---|---|
| SA-09c | Heegner relations to B = 4000, rare-hit descent | KILL (flags: primary descent run is a nominal 2σ excess under a one-sample interval that did not replicate; the 43a1/53a1 ranks are class-group data identical to 37a1, not independent evidence) | 37a1 rank/points in [0.1236, 0.1396] for every B in [750, 4000]; pooled descent 112 hits vs 99.4 expected in 660,000 targets (p = 0.115) |
| SA-19 | Lower the form-lattice degree budget | INCONCLUSIVE (open; frozen lines bracket the answer) | budget 8 in twisted-Edwards y (order-4 poles) vs 9 elsewhere, proved minimal among even degree-2 coordinates; measured reach 0.1246–0.1267 vs 0.112–0.114; m = 3 budget 46 vs 50 |
| SA-08c | Rees lattice at K = 7, 8 and exact-SVP check | KILL (resolves SA-08b's flag; note: the excess magnitude grows ~0.0008/K and would pass 0.005 near K ≈ 10–11, always on the side below δ_K) | absolute excess 0.0024 (K = 7), 0.0033 (K = 8); highest extrapolation 0.1637 < 1/6; exact SVP moves the crossing ≤ 0.0004, downward |
| SA-01c | cuso certificates, m = 3 presentations | KILL (conditional: cuso evaluates chosen polytopes, so the kill rests on a non-exhaustive search; ~210 polytopes for (iii), 18 for (iv)) | cuso δ* = 1/24 exactly for (i), (ii), (iii), (iv); no polytope exceeded 1/24; validated on S_3 (1/6) and cuso's own examples |
