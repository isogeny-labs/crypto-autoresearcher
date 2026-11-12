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
| SA-20 | Coppersmith ladder on the Edwards polynomial | INCONCLUSIVE (open) | ceiling unchanged: 1/6 (m = 2), 1/24 (m = 3) by polytope formula and cuso; planted Edwards-minus-Weierstrass gap at 64 bits: .022 (t = 2), .016 (t = 3), .0086 [.0068, .0114] (t = 5), .0121 [.0065, .0144] (t = 6) vs certified gap ≈ .0025; the residual looks like a finite-dimension LLL effect |
| SA-13c | Modulus-p² proof steps | INCONCLUSIVE (open; needs a model ruling) | (b) and the 1/15 volume inequality proved; H-sep shown not removable (short-lift squares cover index-calculus-useless pairs); with factor-base success the level-2 bound Ω(p^{13/15}) is a complete theorem |
| SA-12c | Learned shifts, equal episodes, 8 seeds | KILL (resolves SA-12b's noise flag) | mean(full − convex reference) = −0.0058, 95% CI [−0.0095, −0.0022]; best full run equals the convex reference 0.13609 at n = 169 |

**Round 3 outcome.** SA-08c and SA-12c resolved their parents' flags as clean kills. SA-01c (cuso: exactly 1/24 for all four m = 3 presentations) and SA-09c (Heegner ratio below 0.15 for every B in [750, 4000]) are kills with recorded caveats. Three directions remain open: SA-13c needs a model ruling (accepting factor-base success makes the Ω(p^{13/15}) level-2 bound a complete theorem); SA-19 found that twisted-Edwards y lowers the form-lattice budget from 9 to 8 (proved minimal among even degree-2 coordinates); SA-20 found the same coordinates leave the Coppersmith ceiling at 1/6 but give a finite-depth gain of 0.009–0.022 in planted reach. No experiment in any round moved an asymptotic exponent toward the 1/m existence threshold.

## Round 4: total solve time

Pre-registrations in `prereg/round4/`. The metric is end-to-end solve time against matched rho, priced in group-addition equivalents (GAE) at 0, 0.1 and 1 GAE per unpriced field operation.

| ID | Direction | Verdict | Deciding number (log2 of projected cost ÷ rho; 0 / 0.1 / 1 GAE) |
|---|---|---|---|
| SA-22 | Projected total cost at 64–256 bits | KILL (lattice-arm validation is in-sample after a two-factor correction; ladder and msolve arms not validated end to end) | validated against SA-21: pair table within 1.1–2.1×; best IC arm (pair table) +22 at 128 bits, +43 at 256 bits; Edwards form lattice +55 / +103; every arm ≥ 2^43 above rho at 256 bits under every pricing |
| SA-21 | Measured end-to-end solve time, 20–40 bits | INCONCLUSIVE by the letter (IC-pair statistically tied with rho at k = 20–24 under π = 1, where solves take < 3 ms); KILL in substance | α: rho 0.52 [0.47, 0.56], IC-pair 0.65 [0.64, 0.67], IC-lattice-W 0.86, IC-lattice-E 0.83; at k = 40 IC-pair is 57–147× rho; lattice arms 1.4e4–4.2e5× rho at 20–32 bits |

**Round 4 outcome (total solve time).** Measured end to end at 20–40 bits (SA-21), every index-calculus arm's cost grows faster than rho's: exponent 0.65 for the pair table and 0.83–0.86 for the lattice oracles, against 0.52 for rho. The validated projection (SA-22) puts the best index-calculus arm 2^22 above rho at 128 bits and 2^43 at 256 bits, and every non-generic oracle more than 2^100 above rho at 256 bits. The decomposition oracle dominates the cost (96–98% of wall time); linear algebra is negligible. The only change that would flip the outcome is an oracle that reaches past p^{1/m} at a per-call cost near one group addition; no measured oracle comes close.

## Round 5: a representation in which "small" is algebraic

Pre-registration in `prereg/round5/`. Rounds 1–4 established that every presentation of the decomposition problem is a coordinate system on the same genus-1 fibres and that the factor-base condition "x ≤ B" is not algebraic, which is what pins every lattice oracle to the multivariate-Coppersmith wall. Round 5 tested the one remaining setting in which smallness is an algebraic condition and the ambient group can have large rank: points of E(F_p) as specialisations of integral sections (height ≤ 2χ) of an elliptic surface over F_p(t). In that representation the oracle is a zero-dimensional polynomial system with no box, and the index calculus has no relation collection and no linear algebra; its whole cost is r + 2 lifts.

| ID | Direction | Verdict | Deciding number |
|---|---|---|---|
| SA-23 | Section representation on the supersingular surface y² = x³ + t^d + 1 over F_p(t), p ≡ −1 (mod d), 6 \| d | KILL (first clause: ĉ's CI entirely above 0.5 at 64, 128 and 256 bits; the second clause is not met, since small-p cells with S ≥ p/2 exist) | integral sections S ≈ 2^{0.39 d} (α = 0.387 [0.357, 0.413]), bounded in p at fixed d (d = 6: 8 at all 22 primes; d = 12: 34–62 over 8 primes; d = 18: 240 at p = 17); msolve lift time ≈ 2^{0.80 U} in the unknown count U = 5d/6 + 2 (u = 0.80 [0.76, 0.89]; the first d = 18 lift did not finish in 600 s); projected total exponent ĉ = 1.84 [1.65, 2.11] at 64 bits, 1.85 [1.66, 2.11] at 256 bits; 5/5 verified discrete logs at d = 12, p = 131 ran 4e4–1.5e5× slower than rho |

**Round 5 outcome (as corrected by the main-session audit, `results/SA-23/audit/AUDIT.md`, ERRATA 8–9).** The representation delivers the structure it promised and fails on count and on cost. Count: integral sections are the minimal vectors of the Mordell–Weil lattice (every fibre is irreducible, so all have height exactly 2χ); the measured growth is 2^{0.39 d} in the frozen family, flat in p, and the disjoint-caps bound κ(r) ≤ C√r·2^r with r ≤ 2d − 4 caps it at S < 2^{2d} for every surface in the class, so covering p points needs U ≥ 0.42·log₂ p unknowns. Cost: the executor's slope u = 0.80 per unknown was an artefact of the msolve start-up floor at d = 6; measured with planted sections, msolve takes 0.05–0.10 s at U = 12, 328–796 s at U = 17 (2.4–2.7 bits per unknown), and more than 4,463 s and 3,099 s at U = 22 and 27 (killed, lower bounds). At fixed U = 12 the lift is also 15–7,000× slower when the surface has 704 sections instead of 34, so the slope is a lower bound in the covering regime. Together: total exponent ≥ 0.42 × 2.4 ≈ 1.0 for any surface in the class, against rho's 0.5. The one assumption left is the lift solver's slope; only msolve was tested. Flagged and open: two ordinary cells outside the frozen family are rich in sections (p = 37, d = 12: 704, rank 12; p = 109: 224, rank 8), near the kissing cap; the ζ₃₆ and p = 3d + 1 explanations are falsified, and the surviving separator ("7 is a square mod p") is an untested hypothesis with a stated prediction. Limitations: j = 0 fibres only; the feasible cells have tiny prime-order subgroups (3–29) because d | p + 1; the end-to-end solves verify the pipeline, not exponents. Reopen only for a lift solver that is strongly sub-exponential in the unknown count on this structured system (for instance one that uses the explicit lattice). Across five rounds and 23 registered experiments, no representation yields a prime-field ECDLP index calculus whose cost exponent is below rho's.

## Round 6: covers, Jacobians and points as moduli

Pre-registration in `prereg/round6/`. Round 6 tests the two factor-base classes left open by the round-5 classification: a factor base inside the Jacobian of a cover of E (SA-24), and relations that come from the moduli meaning of a point rather than from decomposition (SA-25). It also tests the mechanism behind SA-23's two section-rich cells (SA-23b). Rows are added as each executor reports and its main-session audit is done.

| ID | Direction | Verdict | Deciding number |
|---|---|---|---|
| SA-25 | Closed Hecke and Atkin–Lehner relations inside trace classes S_t of X0(11)(F_p) = 11a1(F_p), p up to 1e7 (29 primes) | KILL (min c_t/\|S_t\| is 0.133 at every p ≥ 1e5, above the 0.05 line; projected and measured cost above rho at the two largest primes) | corank c_t/\|S_t\| from 0.133 to 0.50 in every class; no class with \|S_t\| ≥ 50 has c_t ≤ 10 (smallest 14); end-to-end solves 2e3–3e4× slower than matched rho at p ≈ 1e7, 300–1,400× at p ≈ 1e6; all relations verified as point identities, true-log control 153,275 relations with 0 violations |
| SA-24 | Factor base in Jac(C) of bielliptic genus-2 (and genus-3) covers of E1; index calculus for E1[n1] inside Jac(C) | INCONCLUSIVE as first reported (5 unpowered cells); **KILL** once SA-24c powered them | A1 alpha 0.865 [0.821, 0.923] against rho 0.344 [0.293, 0.395] on counted E1-add equivalents, p = 2^10..2^20 (0.931 [0.895, 0.973] up to 2^24); trials per relation set ≈ p at every B; splitting ratio measured/null = 1 within noise in all 38 powered cells, pooled slopes −0.0040 [−0.0142, 0.0027] (g = 2) and −0.0007 [−0.0096, 0.0076] (g = 3) |
| SA-23b | Mechanism for SA-23's section-rich cells: MW rank of y² = x³ + t¹² + 1 over F_p(t) equals R_J = #{Jacobi-sum pieces with J = p} | INCONCLUSIVE (mechanism confirmed at all 3 new primes and the control; the frozen residue-symbol law class reached 50.8% held-out, short of 99%; follow-up SA-23c) | Gram rank vs R_J: 16 vs 16 at p = 157 (1784 sections), 3 vs 4 at 181 and 193 (8 sections); "7 is a square" refuted at 157 and 193; R_J ∈ {4, 8, 12, 16} at 50.8 / 24.4 / 16.8 / 7.9% of 2374 primes below 1e5, always 16 algebraic pieces |
| SA-23c | Held-out test of the post-hoc SA-23b laws (48-cell exponent table; closed form for R_J), and enumeration at p = 229 | SUCCESS (audited) | 0 exceptions to either law in all 17,190 primes p ≡ 1 (mod 12), 1e5 < p < 1e6; R_J frequencies 0.501 / 0.248 / 0.167 / 0.084, each CI containing 1/2, 1/4, 1/6, 1/12; p = 229: R_J = 8, S = 224, Gram rank 8, det 256, identical to p = 109 |
| SA-24c | Completion of SA-24 (power the 5 splitting cells) and an exploratory full-Jacobian Gaudry arm | Part 1: SA-24 → **KILL**; Part 2: DEVIATES (exploratory; a wrong prediction, ERRATA 10) | 43/43 cells powered, pooled measured/null 0.96–1.15, slope CIs [−0.0016, 0.0056] (g = 2) and [−0.0091, 0.0119] (g = 3); the SA-24 (2^24, 0.5) deficit returned to 1.05; full-Jacobian Gaudry alpha 1.005 [0.993, 1.018] in p (predicted 4/3), cost 1.5–2.5× the degenerate arm and 3–5 orders above rho |

**SA-25 (audited, `results/SA-25/audit/AUDIT.md`).** The relations are real, and the module they span has a corank that is a fixed fraction of the class. The main-session audit explains that fraction with a floor law. Half the points on the floor of every ℓ-volcano, ℓ in the Hecke set, account for the corank. It is predicted from class numbers h(f′²D0) alone, without the relation data. It matches the measured corank within ±1 in 99.3% of the 9,740 classes with a Hecke prime and |S_t| ≥ 50. The reason is that floor points have no full rational ℓ-neighbourhood, and Atkin–Lehner makes the Hecke rows at s and w(s) identical. That gives c_t/|S_t| ≥ ½∏_{ℓ|f}(1 − 1/ℓ). The measured minimum 2/15 is exactly this bound for f = 30 with 2, 3 and 5 split. With every Hecke prime allowed, the bound becomes ½φ(f)/f, at least about 1/(2e^γ log log p). So the connection step costs at least about p/log log p for structural reasons, and no Hecke set brings this source near √p. One modular curve was measured. The law depends only on the volcano structure, so it should carry to any X0(N).

**SA-24 (audited, `results/SA-24/audit/AUDIT.md`).** The pullback of R = (X0, Y0) has Mumford u with roots exactly x = ±√X0, the fibre of the cover. Every element of the frozen A1 walk lies in pb(E1), so a "Jacobian relation" is a point of E1 whose x-coordinate is a small square. That is about B points out of p, with one new unknown per relation. The raw data show trials per relation × B/p ≈ 1.00 and total trials ≈ p at every B, so A1 is linear in p and the KILL's first clause is structural. The splitting ratio is a Monte Carlo of the null itself (the sampler is the null's weighted sum), so it cannot show an excess. The "4–5σ" cells are about 2σ in event counts, because a split pair carries weight 4. SA-24c (`prereg/round6/SA-24c.md`) powers the five cells to ≥ 50 expected events, as SA-24's own protocol asked. It adds an exploratory full-Jacobian Gaudry arm, frozen prediction p^{4/3}, which answers the round-6 question directly. Context: over a prime field a cover is defined over the same field as E. Jacobian index calculus then costs at least p^{2−2/g} ≥ p, so covers only help when they descend to a smaller field (Weil descent, GHS), which F_p does not have.

**SA-23b (audited, `results/SA-23b/audit/AUDIT.md`).** Main-session code shares nothing with the executor's. It confirms the enumeration: 1784 distinct signed sections at p = 157, all satisfying the equation, Gram rank 16. The ranks at 181 and 193 are 3. The character and the residue symbols were taken at the same prime of Z[ζ₁₂], so the law failure is real. It is also structural. The exponent string is a function of (π mod 3, (2/p)₃, (2/p)₄), for the primary Gaussian prime π = a + bi of p. That is 48 cells, exact at all 2374 primes, and the sign of π mod 3 is not a residue symbol of any rational integer. A closed form for the rank also fits every prime, post hoc:

    R_J = 4 + 4·[2 is a cube mod p] + 8·[3 | b and ((a ≡ 1 mod 3) ≠ (p ≡ 5 mod 8))]

It explains the rich cells: R_J is 12 at p = 37, 8 at 109 and 16 at 157. Both rules are registered for a held-out test on 1e5 < p < 1e6 (SA-23c, frozen table SHA-256 d7391376…). SA-23c also enumerates p = 229, predicting R_J = 8 and S = 224. SA-23's ECDLP verdict does not depend on any of this.

**SA-23c (audited, `results/SA-23c/audit/AUDIT.md`).** The post-hoc laws survived a held-out test on data they had not seen. The main session rescored all 17,190 primes with its own code. It recomputed R_J at eight of them with the independent floating-point algorithm, matching 8 of 8, and re-verified the p = 229 sections. **Result:** for p ≡ 1 (mod 12), the Mordell–Weil rank of y² = x³ + t¹² + 1 over F_p(t) is

    R_J = 4 + 4·[2 is a cube mod p] + 8·[3 | b and ((a ≡ 1 mod 3) ≠ (p ≡ 5 mod 8))]

where p = a² + b² is written with a + bi primary. In the 10 enumerated cells, the number of integral sections depends only on R_J: S = 8, 224, 704 and 1784 at R_J = 4, 8, 12 and 16. Tested numerically to 1e6, not proved. This closes the rich-cell anomaly from the SA-23 audit. The cause was arithmetic at the bad primes 2 and 3 of Z[ζ₁₂]: π mod 3, p mod 8, and whether 2 is a cube. "7 is a square" played no part. No ECDLP consequence: SA-23's corrected bound covers every prime, and the richest cell, 1784 sections, sits under the kissing cap.

**SA-24c (audited, `results/SA-24c/audit/AUDIT.md`).** With all 43 splitting cells powered, SA-24's frozen KILL holds. The cover-Jacobian factor base gives no relation source beyond E1 itself. The exploratory arm ran real Gaudry index calculus with elements uniform in Jac(C). Its per-relation rate equals the uniform null, and its cost scales as p^1.00. The prereg predicted p^{4/3}, which wrongly assumed linear algebra quadratic in the factor base (ERRATA 10). In genus 2 each relation has exactly two unknowns, so the linear algebra is graph propagation, 1–4% of cost. Cost is then trials alone, p^{2−δ}, falling toward p as δ → 1. That is the p^{2−2/g} floor stated in SA-24, reached and not beaten, and still a factor of p^{1/2} above rho on E1. **Round 6 conclusion on covers:** over F_p a cover is defined over the same field as E. Its Jacobian's index calculus cannot beat p, while rho on E costs p^{1/2}. Covers help only through descent to a smaller field, which a prime field lacks.
