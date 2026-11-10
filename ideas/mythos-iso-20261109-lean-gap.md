# Mythos ECDLP ideation — lean-gap (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

# Preface: what this BRIEF actually exposes

The BRIEF as delivered quotes sections 0–2 only: five repositories, one Lean commit subject (`SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness`), and 27 hypothesis stubs (H-SSIQ-d724f2 … H-ALISO-017, plus KN-OPEN-095df5 referenced inside H-BINSTD-944a66). No `EXP-*`, `EV-*`, or `IDEA-*` id and no CryptoLean theorem name is quoted. Per the rules I cannot invent any. Every `LEAN:` line below is therefore `no Lean coverage` with the statement to formalize, every `EXP:` line is `none; nearest surface is …` naming the Autolab package or repo quoted in the BRIEF, and `CHECKED:` cites only the visible ids. The angle is the program's own record: closures scoped to three primes, probes without verifies, heuristic "supported" labels, and one open question (KN-OPEN-095df5) that admits an elementary certificate.

Nothing here touches SIDH/SIKE as a live assumption. The H-ALISO Kani-tagged packages are cryptanalytic tooling, not protocols; where a lead concerns them it says so.

## LEADS

### 1. Certify KN-OPEN-095df5 upward: 2 is a primitive root mod 131, so `Res_{F_{2^130}/F_2} G_m` has an F_2-point of order 131
- **Mechanism.** 2^65 ≡ −1 (mod 131) (check: 2^7 ≡ −3, 2^14 ≡ 9, 2^28 ≡ 81, 2^56 ≡ 11, 2^63 ≡ −33, 2^65 ≡ −132 ≡ −1); 2^k ≢ 1 for k ∈ {2,5,10,13,26} (2^10 ≡ 107, 2^13 ≡ 70, 2^26 ≡ 53). Hence ord_131(2) = 130 and 131 | 2^130 − 1. The Weil restriction of G_m from F_{2^130} has an F_2-rational point of order 131, answering the literal question in H-BINSTD-944a66 affirmatively if dimension is unconstrained.
- **Attacks/settles.** The SETTING clause of H-BINSTD-944a66 (Couveignes–Lercier reproduction, GGMP §). Not an attack; a parameter audit converting "open" into "answered, with dimension caveat".
- **Delta needed.** None (certificate). Dimension of the witness is 130.
- **Obstruction.** The construction almost certainly wants a low-dimensional group (elliptic curve or small abelian variety); the torus answer may be the wrong witness. That is exactly why Lead 2 exists.
- **Kill test.** `decide` fails on `orderOf (2 : ZMod 131) = 130` — impossible given the arithmetic above; the real kill is a scope note in H-BINSTD-944a66 saying dimension ≤ g for small g.
- **Tag.** `[adaptation]`
```
CHECKED: H-BINSTD-944a66 (sets the question but records no witness or non-existence proof); KN-OPEN-095df5 (the open item itself, dimension not quoted as constrained)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need `theorem orderOf_two_zmod_131 : orderOf (2 : ZMod 131) = 130` and `theorem dvd_131 : 131 ∣ 2^130 - 1` (both by `decide`/`norm_num`)
EXP: none; nearest surface is aburan28/crypto-lean (namespace SplitPrime.Obstruction, commit 8187529) for the Lean file; no Autolab package quoted for H-BINSTD-944a66
```

### 2. Certify KN-OPEN-095df5 downward: no elliptic curve over F_2 has a point of order 131, and no abelian surface either
- **Mechanism.** Over F_2 there are 32 Weierstrass tuples (a1..a6); exhaustive point counting gives #E(F_2) ∈ {1,…,5}, so 131 ∤ #E(F_2) for every E/F_2. For abelian surfaces, #A(F_2) ≤ (1+√2)^4 < 34 < 131. Lower bound on the dimension of any witness is therefore g ≥ 3 ((1+√2)^6 ≈ 198 ≥ 131 is the first dimension not excluded).
- **Attacks/settles.** The same open question, from below: the Couveignes–Lercier-style construction must use dimension ≥ 3 over F_2, or extend the base field.
- **Delta needed.** None; this is a certificate.
- **Obstruction.** g = 3 is not excluded by the bound, so the question remains open in dimension exactly 3 (Jacobians of genus-3 curves over F_2 with 131 | #J). A small experiment enumerating genus-3 curves over F_2 (finitely many) and their zeta functions would close it entirely.
- **Kill test.** Lean enumeration finds an E/F_2 with 131 | #E — impossible, but the formal check is the deliverable. Experiment kill: a genus-3 curve over F_2 with 131 | #J(F_2) exists (then the question is closed positively in dimension 3).
- **Tag.** `[adaptation]`
```
CHECKED: H-BINSTD-944a66 (records the need for an order-131 point but not the elliptic-curve exclusion); KN-OPEN-095df5 (open status)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need `theorem no_order_131_over_F2 : ∀ (a1 a2 a3 a4 a6 : ZMod 2), ¬ (131 ∣ Fintype.card (WeierstrassCurve.Point ⟨a1,a2,a3,a4,a6⟩))` proved by exhaustive `decide` over the 32 tuples, plus the elementary bound `Fintype.card … ≤ 5`
EXP: none; nearest surface is aburan28/crypto-autoresearcher (Autolab package convention `p****_*_probe`, no package quoted for H-BINSTD-944a66)
```

### 3. Lift the `rejected_scoped` of H-ICINV-6c7920 to a prime ladder with a control arm
- **Mechanism.** H-ICINV-6c7920 rejects representative-selection benefits at p ∈ {2003, 4001, 6007}, exact m = 3, with classes certified against the Hurwitz–Kronecker mass formula. Three toy primes cannot distinguish "no effect" from "effect below noise at 11–13 bits". Rerun on the ladder already used by H-ICINV-82ee6a (primes below 2^24), m ∈ {3,5,7}, with a control arm where the representative is chosen uniformly from the class, and measure Pollard-rho iteration count ratio (selected / control) with ≥ 10^3 instances per rung.
- **Attacks.** The parent claim H-ECDLP-f8101e (isogenous representative selection reduces end-to-end ECDLP cost).
- **Delta needed.** For the claim to survive it must show ratio < 1 − 3σ on at least one rung; a constant-factor ≤ 2 effect is the most that any class-invariant-preserving selection could plausibly yield since #E(F_p) is a class invariant.
- **Obstruction.** Rho cost is dominated by √(πN/2) with N the class-invariant group order; only the group structure (cyclic vs. Z/n × Z/m) and the field arithmetic of the chosen model vary. Expect ratio ≈ 1.
- **Kill test.** Ratio within 3σ of 1 on every rung → upgrade `rejected_scoped` to `rejected` on ordinary prime-field classes below 2^24; deviation → the rejection was a toy artifact and H-ECDLP-f8101e reopens.
- **Tag.** `[adaptation]`
```
CHECKED: H-ICINV-6c7920 (rejection at three primes, m = 3); H-ICINV-82ee6a (ladder below 2^24, Z[π] features); H-ECDLP-f8101e (parent claim, analyzed)
DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — this lead widens, not repeats, its scope
LEAN: no Lean coverage; would need `theorem isogenous_card_eq (E E' : EllipticCurve (ZMod p)) (φ : E →ᵢ E') : Fintype.card E.Points = Fintype.card E'.Points` (Tate; not in the BRIEF's quoted scope)
EXP: none; nearest surface is aburan28/ecbench (rho harness repo quoted in §1, no isogeny-specific commit)
```

### 4. Show the endomorphism "features" of H-ICINV-82ee6a are class-constant, so H-ECDLP-f8101e has nothing to select on
- **Mechanism.** H-ICINV-82ee6a draws endomorphisms from the Frobenius order Z[π]. Disc(Z[π]) = t² − 4p is the same for every curve in an F_p-isogeny class; the only class-varying datum is the conductor f = [O_K : End(E)] with Z[π] ⊆ End(E) ⊆ O_K. Any feature computed from Z[π] alone is therefore constant on the class, and selection by it is vacuous. Certify this as a Lean statement in the conductor arithmetic the BRIEF says CryptoLean has (no theorem name quoted).
- **Attacks.** Security-proof-gap style audit of the program's own hypothesis: separates "feature from Z[π]" (vacuous) from "feature from End(E)" (needs endomorphism-ring computation, which is a different cost model).
- **Delta needed.** None; it removes a false degree of freedom.
- **Obstruction.** If H-ICINV-82ee6a actually computed End(E) via the Kohel/Fouquet–Morain conductor-walk, the features vary and this lead is void; the stub does not say which.
- **Kill test.** Feature vector identical across all members of each certified class at p = 2003 → vacuous; otherwise the record is misdescribed and should be re-scoped.
- **Tag.** `[known]` in mathematical content (standard CM theory), `[adaptation]` as an audit
```
CHECKED: H-ICINV-82ee6a (Z[π]-sourced endomorphisms, ladder < 2^24); H-ECDLP-f8101e (selection by j-invariant or endomorphism features); H-ICINV-6c7920 (the negative result this explains)
DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — this lead supplies the structural reason for the rejection rather than more data
LEAN: no Lean coverage quoted; would need `theorem frobenius_order_disc_const (E E' isogenous over ZMod p) : discr (Z[π_E]) = discr (Z[π_E'])` and `theorem conductor_divides (Z[π] ≤ End E ≤ O_K) : conductor (End E) ∣ conductor Z[π]`
EXP: none; nearest surface is aburan28/cryptanalysis (pcc files shared with crypto-autoresearcher per commit "Shared-code lock")
```

### 5. Give H-ECDLP-3550b8 the random-mapping control it lacks
- **Mechanism.** The basin B(d) of a distinguished point under a deterministic walk f on N points with distinguishing density θ = 1/W is compared against the Flajolet–Odlyzko random-mapping prediction: expected basin size of a distinguished point ≈ W, tail geometric, total mass in basins of the ~N/W distinguished points covering (1 − o(1))·N. Measure the empirical basin-size distribution for the program's f (r-adding walk, r ∈ {20, 32}) and for a truly random f on the same N ∈ {2^16, 2^20, 2^24}.
- **Attacks.** The implicit claim that basin structure of the *specific* walk is exploitable (shortcuts, biased collisions).
- **Delta needed.** A KL divergence between empirical and random-mapping basin distributions that grows with N; for an exploitable effect you need a constant-factor change in expected rho length, i.e. basin mean deviating by ≥ 10% at N = 2^24.
- **Obstruction.** r-adding walks with r ≥ 20 are known to be within a few percent of random-mapping behaviour; the deviation is a small constant, not an exponent.
- **Kill test.** Basin-size histograms indistinguishable (KS test p > 0.05) at all three N → H-ECDLP-3550b8 is a restatement of random-mapping statistics; record it as `analyzed, no delta`.
- **Tag.** `[known]` (the control is standard), `[adaptation]` (applying it to the filed object)
```
CHECKED: H-ECDLP-3550b8 (defines basin B(d) and θ = 1/W but quotes no random-mapping baseline)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need `theorem basin_partition (f : Fin N → Fin N) (D : Finset (Fin N)) : (⋃ d ∈ D, basin f d) ∪ cyclesAvoiding f D = univ` (deterministic part only; the expectation statement is probabilistic and out of Lean scope)
EXP: none; nearest surface is aburan28/ecbench (rho/distinguished-point harness repo quoted in §1)
```

### 6. Bound the sampler bias in H-WESO-516558 by the Ramanujan mixing rate and test on a prime ladder
- **Mechanism.** Part (H-S) of H-WESO-516558 asserts the endpoint distribution of a length-k non-backtracking walk on norm-2 left ideals of a maximal order O ⊂ B_{p,∞}, scoped to tested primes. The 2-isogeny graph is 3-regular Ramanujan (Pizer), so the total-variation distance to the Aut-weighted stationary distribution after k steps is ≤ C·√(p/12)·(2√2/3)^k for simple walks and strictly faster for non-backtracking walks. Compute TV(k) empirically on p ∈ {ladder of ~10 primes in [2^10, 2^20]}, split by p mod 12 (presence of j = 0, 1728 with extra automorphisms), and compare with the bound.
- **Attacks.** Correctness of the program's own sampler, which downstream hypotheses (Hecke probes) rely on.
- **Delta needed.** None; it is a control. The useful number is the smallest k at which TV < 2^−20 — should be ≈ log_{3/(2√2)}(√(p/12)·2^20).
- **Obstruction.** Non-backtracking endpoints converge to the stationary measure of the *non-backtracking* chain, which coincides with the simple-walk stationary measure only on regular graphs — fine here, but the j = 0, 1728 vertices have degree-with-multiplicity subtleties that the sampler must weight by 1/#Aut.
- **Kill test.** Observed TV(k) exceeds the Ramanujan bound at any rung by > 2× → the sampler, not the graph, is biased; (H-S) is weakened on that prime range and must be re-scoped.
- **Tag.** `[known]` control, `[adaptation]` to the filed sampler
```
CHECKED: H-WESO-516558 (two-part, scoped to tested primes; (H-S) sampler claim); H-ALISO-008 (hecke_krylov_probe consumes walk statistics on the same graph family)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need `theorem nonbacktracking_walk_count (G : SimpleGraph V) [3-regular] (k) : card (NBWalks G v k) = 3 · 2^(k-1)` (the combinatorial part only; the spectral bound is out of reach)
EXP: none; nearest surface is aburan28/crypto-autoresearcher (Autolab packages `p1486_hecke_*` quoted in H-ALISO-006..009)
```

### 7. Turn the "supported" census H-SSIQ-d724f2 into a `decide` certificate for N ∈ {3, 5, 7}
- **Mechanism.** H-SSIQ-d724f2 is a group-theoretic census of a subgroup H_N ⊂ GL_2(Z/N) attached to the standard maximal order O (i² = −1, j² = −p). For fixed small N the census is a finite computation: the generating matrices recorded in the hypothesis generate a subgroup whose order and conjugacy class in GL_2(Z/N) can be checked by `decide` (|GL_2(Z/3)| = 48, |GL_2(Z/5)| = 480, |GL_2(Z/7)| = 2016). "Supported (heuristic)" becomes "certified for N ≤ 7" with no new mathematics.
- **Attacks.** The label itself; a heuristic census feeding later cost estimates should not stay heuristic where it is finite.
- **Delta needed.** None.
- **Obstruction.** The stub truncates before stating H_N precisely; the Lean statement must take the generating set from the full record. `decide` on subgroup closure in `Matrix (Fin 2) (Fin 2) (ZMod 7)` may need a `Fintype` instance and a kernel-reduction budget; N = 7 may require `native_decide`, which is weaker evidence — report which was used.
- **Kill test.** `decide` returns a different order than the census → the census is wrong at that N and the hypothesis drops to `weakened`.
- **Tag.** `[adaptation]`
```
CHECKED: H-SSIQ-d724f2 (supported, heuristic census of H_N ≤ GL_2(Z/N), "NO ATTACK; NO EXPONENT"); H-SSIQ-dfee7e (sibling SSIQ record, integer-only arm)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need `theorem H_N_card (N ∈ {3,5,7}) : Nat.card (Subgroup.closure (S_N : Set (GL (Fin 2) (ZMod N)))) = <census value>` by `decide`, with S_N the generators recorded in H-SSIQ-d724f2
EXP: none; nearest surface is aburan28/crypto-lean (commit 8187529 namespace SplitPrime.Obstruction, "scalar-only action" is the nearest proved shape)
```

### 8. Run Arm II for H-SSIQ-dfee7e: do the integer-admissible divisors actually occur as ideal-norm factorisations?
- **Mechanism.** H-SSIQ-dfee7e counts k(d), admissible divisors of a B-smooth d in the split window [⌈d/X⌉, X], purely as integers (Arm I). The quaternion object it stands in for is: given a left O-ideal I of norm d, the number of factorisations I = I_1·I_2 with nrd(I_1) in the window. For a prime-power-free d every divisor is realised (ideal factorisation is unique up to the usual ambiguity), but for ℓ^e ∥ d with e ≥ 2 the count of norm-ℓ^a sub-ideals is ℓ^{a−1}(ℓ+1)·(…) not 1, so k_II(d) ≥ k_I(d) with equality iff d is squarefree. Arm II at the same p and the same d-sample measures the gap.
- **Attacks.** Validity of the integer-only proxy that later cost estimates may rest on.
- **Delta needed.** If k_II/k_I is bounded by a constant on B-smooth d, the proxy is fine; if it grows like ∏ ℓ^{e−1} it is off by a polynomial factor and any cost derived from Arm I is optimistic.
- **Obstruction.** Arm II needs ideal arithmetic in O (left ideal of norm ℓ^e, enumeration of sub-ideals) — O(e·ℓ) per prime power, cheap at B ≤ 2^10.
- **Kill test.** k_II(d) = k_I(d) on all squarefree d and k_II(d)/k_I(d) = ∏_{ℓ^e ∥ d, e≥2} (number of norm-ℓ^{a} left sub-ideals) on the rest → proxy certified with an explicit correction factor; otherwise Arm I is miscounting.
- **Tag.** `[adaptation]`
```
CHECKED: H-SSIQ-dfee7e (Arm I, integer-only, no quaternion control); H-SSIQ-d724f2 (same order O, census)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need `theorem kI_le_divisors (d X : ℕ) : k_I d X ≤ (Nat.divisors d).card` and `theorem kI_squarefree_eq (hd : Squarefree d) : k_I d X = ((Nat.divisors d).filter (fun e => d/X ≤ e ∧ e ≤ X)).card`
EXP: none; nearest surface is aburan28/crypto-autoresearcher (Autolab package convention; no SSIQ package name quoted)
```

### 9. File the missing `_verify` controls for H-ALISO-008, -009, -012
- **Mechanism.** The H-ALISO series pairs probes with verifies: 001/002 (`degree_first_hecke`), 003–005 (`frobenius_midpoint`), 006/007 (`hecke_degree_pair_support`), 010/011 (`parity_center_smoothness`). Three probes have no verify: 008 `p1486_hecke_krylov_probe`, 009 `p1486_hecke_support_cost_probe`, 012 `p1486_quantum_aggregate_oracle_probe` (013 verifies *cost accounting*, a different quantity). The program's own convention says a probe without a verify is a measurement without a control. Write the three verifies: same seed, independent re-implementation of the statistic, and for 012 a classical-baseline oracle count so "quantum aggregate" is a ratio, not a number.
- **Attacks.** Archival status of three "scoped empirical measurements" the brief says can be archived as harness evidence.
- **Delta needed.** None.
- **Obstruction.** Krylov statistics (008) are sensitive to floating-point / finite-field reduction order; the verify must use exact arithmetic over Z or a disjoint prime to avoid merely re-running the same code.
- **Kill test.** Verify disagrees with probe beyond stated tolerance on any of the three → the probe is downgraded from archivable to `analyzed, unreplicated`.
- **Tag.** `[adaptation]` (tooling/control)
```
CHECKED: H-ALISO-008, H-ALISO-009, H-ALISO-012 (probes without verifies); H-ALISO-013 (verifies cost accounting, not the aggregate oracle); H-ALISO-002/004/005/007/011 (the verify convention being extended)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need nothing new (these are measurements); the one formalizable piece is `theorem krylov_dim_le (A : Matrix n n ℚ) (v) : finrank (Krylov A v) ≤ Fintype.card n`
EXP: none; nearest surface is aburan28/crypto-autoresearcher Autolab packages `p1486_hecke_krylov_probe`, `p1486_hecke_support_cost_probe`, `p1486_quantum_aggregate_oracle_probe`
```

### 10. Give the p1243 auxiliary-Kani packages (H-ALISO-014..017) a random-discriminant control
- **Mechanism.** `p1243_auxiliary_discriminant_search`, `_four_line_descent`, `_geometric_principalization`, `_lattice_kani` are four probes and zero verifies. They are Kani-lemma tooling (the mechanism that killed SIDH) aimed at an auxiliary discriminant structure; they are cryptanalysis, not a protocol, so the SIDH standard is satisfied by stating that no torsion-repair is being proposed. The missing control: run the descent/principalization pipeline on uniformly random fundamental discriminants of the same bit-size and the same class-number parity as the "auxiliary" ones found by 014. If success rate and descent length are statistically identical, the auxiliary search (014) contributes nothing and 015–017 measure the generic behaviour.
- **Attacks.** Whether the "auxiliary" structure is a real lever or a selection artifact.
- **Delta needed.** Success-rate ratio (auxiliary / random) ≥ 2 at matched size, or descent length shorter by a constant factor; otherwise no delta.
- **Obstruction.** Matching class-number parity and 2-rank of the class group is needed to make the control fair; both are cheap for |D| ≤ 2^40.
- **Kill test.** Ratio within 3σ of 1 → mark 014 `analyzed, no selection effect`; 015–017 keep their measurements but lose the "auxiliary" adjective.
- **Tag.** `[adaptation]`
```
CHECKED: H-ALISO-014 (discriminant search), H-ALISO-015 (four-line descent), H-ALISO-016 (geometric principalization), H-ALISO-017 (lattice Kani) — all probes, no verifies, no control arm quoted
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need `theorem kani_degree_split (a b : ℕ) (h : a + b = N) : …` (Kani's lemma, not in the BRIEF's quoted Lean scope); the control itself is a measurement
EXP: none; nearest surface is aburan28/crypto-autoresearcher Autolab packages `p1243_auxiliary_*`
```

### 11. Dickman baseline for H-ALISO-010/011 `parity_center_smoothness`
- **Mechanism.** Smoothness probability of integers of size ~x with smoothness bound y is ρ(u), u = log x / log y, to leading order. A "parity center smoothness" statistic is only meaningful as a ratio against ρ(u) for the same (x, y) and against random integers of the same size and parity. Add the two baselines to the verify (011): analytic ρ(u) via the standard delay-differential integration, and empirical smoothness on uniform random integers conditioned on the same parity.
- **Attacks.** Whether the "center" is smoother than generic — the only way the probe could feed a cost exponent.
- **Delta needed.** Smoothness probability exceeding ρ(u) by a factor growing in u; a constant factor ≤ 2 is noise at the exponent level.
- **Obstruction.** Center values are structured (norm forms), so the correct baseline may be ρ for norms from the same quadratic order, not uniform integers; include both controls and report both ratios.
- **Kill test.** Ratio ≤ 2 on every rung and flat in u → no exponent; record `analyzed, matches Dickman`.
- **Tag.** `[known]` baseline, `[adaptation]` to the filed probe
```
CHECKED: H-ALISO-010 (parity_center_smoothness_probe), H-ALISO-011 (its verify; no ρ(u) or random-integer baseline quoted)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need nothing beyond measurement (Dickman ρ is analytic); the formalizable piece is the trivial `theorem smooth_divisors_bound (n B) : B-smooth n → ∀ p ∣ n, p.Prime → p ≤ B`
EXP: none; nearest surface is aburan28/crypto-autoresearcher Autolab packages `p1486_parity_center_smoothness_probe` / `_verify`
```

### 12. Replace the Hurwitz–Kronecker certification in H-ICINV-6c7920 with a twist-count theorem
- **Mechanism.** H-ICINV-6c7920 certifies "complete F_p-isogeny classes" by comparing against the mass formula Σ_t H(4p − t²). An equivalent p-independent certificate: the number of F_p-isomorphism classes of elliptic curves over F_p (p > 3) is 2p + 6 if p ≡ 1 (mod 12), 2p + 2 if p ≡ 11 (mod 12), 2p + 4 otherwise — every j ≠ 0, 1728 has exactly 2 twists, j = 1728 has 4 or 2, j = 0 has 6 or 2, depending on whether −1 / −3 are squares. The BRIEF's Lean commit mentions "twist purity"; this is the statement that would make it usable: the class-union over all t must have exactly that cardinality. Summing per-class counts and checking against 2p + c is a one-line check the harness can run at every rung of Lead 3, and the Lean theorem makes the target number a certificate rather than a computed H(D).
- **Attacks.** The certification method inside the scoped rejection; it is a parameter-audit repair.
- **Delta needed.** None.
- **Obstruction.** Proving the twist count in Lean needs the automorphism groups at j = 0, 1728 over F_p, which the "twist purity" commit may or may not cover — no theorem name is quoted, so this must be treated as uncovered.
- **Kill test.** Harness class-union count ≠ 2p + c at any rung → either the class enumeration or the mass-formula comparison in 6c7920 was wrong; the scoped rejection loses its "complete classes" clause.
- **Tag.** `[known]` mathematics, `[adaptation]` as a certificate
```
CHECKED: H-ICINV-6c7920 (certification via Hurwitz–Kronecker at p ∈ {2003,4001,6007}); H-ICINV-82ee6a (ladder the certificate would be reused on)
DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — this repairs its certification method, not its conclusion
LEAN: no Lean coverage quoted (commit 8187529 subject mentions "twist purity" but no theorem name); would need `theorem card_iso_classes (p : ℕ) [Fact p.Prime] (hp : 3 < p) : Nat.card (EllipticCurve (ZMod p) ⧸ Iso) = 2*p + (if p % 12 = 1 then 6 else if p % 12 = 11 then 2 else 4)`
EXP: none; nearest surface is aburan28/cryptanalysis (pcc files per "Shared-code lock" commit) for the class-enumeration code
```
