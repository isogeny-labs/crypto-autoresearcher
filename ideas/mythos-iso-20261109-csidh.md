# Mythos ECDLP ideation — csidh (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

# BRIEF coverage note (read first)

The BRIEF excerpt quoted to me lists 27 hypothesis ids (H-SSIQ-d724f2, H-SSIQ-dfee7e, H-BINSTD-944a66, H-WESO-516558, H-ECDLP-3550b8, H-ECDLP-f8101e, H-ICINV-6c7920, H-ICINV-82ee6a, H-ALISO-001 … H-ALISO-017), one open-knowledge id (KN-OPEN-095df5), one refuted record (H-ICINV-6c7920 `rejected_scoped`), and one crypto-lean commit subject (`SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness`). It quotes **no CSIDH-tagged hypothesis, no EV-\* record, no EXP-\* id, and no Lean theorem name**. I therefore cannot "cite the brief's CSIDH hypotheses and the evidence that weakened them" — they are not in my view. Every clearing block below cites only the ids above, says `none in the brief` where that is the truth, and states the exact Lean statement that would be needed. All literature costs are recalled from memory and are marked as such; none is a claim of a break.

## LEADS

### 1. Quantum cost re-audit: polynomial-time class group (Biasse–Song) + uniform effective-action oracle (Clapoti/PEGASIS-style) feeding Kuperberg
- **Mechanism.** The SQALE'd-CSIDH cost model (recalled: Chávez-Saab–Chi-Domínguez–Jaques–Rodríguez-Henríquez; p ≈ 4096–5280 bits for NIST-1) prices Kuperberg's hidden-shift oracle as an *exponent-vector* CSIDH evaluation ([-m,m]^n, n ≈ 130–400 small primes) in superposition, with Bonnetain–Schrottenloher-style gate counts. Two changes alter the audit: (i) Biasse–Song gives Cl(Z[√−p]) and its relation lattice in quantum polynomial time, so the shift lives in a *known* cyclic group of order N ≈ √p (recalled N ≈ 2^257.1, cyclic, for CSIDH-512 per Beullens–Kleinjung–Vercauteren); (ii) effective-group-action algorithms (Page–Robert Clapoti; PEGASIS 2025 with 4-dimensional isogenies, recalled seconds-scale at 4096-bit p) evaluate [𝔞]E for an *arbitrary* ideal 𝔞 in polynomial time without exponent vectors. The oracle becomes one 4-dim isogeny chain instead of ∑ e_i ℓ_i-isogenies with Elligator rejection.
- **Attacks.** Quantum cost assumption behind SQALE parameter choices (parameter audit with a quantum-circuit measurement component).
- **Delta needed.** Oracle gate count below the exponent-vector oracle by a factor ≥ 2^6 at 4096-bit p, or the audit is moot.
- **Obstruction.** 4-dim isogeny arithmetic in superposition (theta coordinates, 2^k-torsion of dimension-4 abelian varieties) has no reversible-circuit cost model; Clapoti needs a norm equation / lattice step whose quantum reversibility is unexamined.
- **Kill test.** Produce a T-count estimate for one PEGASIS-style action at p ≈ 4096 bits; if ≥ the exponent-vector oracle count, lead dies.
- **Tag.** `[adaptation]` (known quantum-cost-accounting lane; new oracle).
- CHECKED: H-ALISO-012 (quantum_aggregate_oracle_probe — aggregate oracle costing for Kani-type problems, same accounting style), H-ALISO-013 (quantum_cost_accounting_verify — cost-model verification harness), H-ALISO-017 (auxiliary_lattice_kani — lattice step inside a Kani evaluation, analogous to Clapoti's lattice step).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `theorem csidh_action_free_transitive (p : ℕ) [Fact p.Prime] (hp : p % 4 = 3) : ∀ E₁ E₂ : SupersingularFp p, ∃! a : ClassGroup (ℤ[√-p]), act a E₁ = E₂` (nearest module: crypto-lean `SplitPrime.Obstruction`, no theorem name quoted).
- EXP: none; nearest surface is `aburan28/crypto-autoresearcher` (shared pcc files per the cryptanalysis commit "Shared-code lock").

### 2. Decisional genus-character audit across CSIDH relatives (CSURF, SCALLOP / PEARL-SCALLOP, conductor-f oriented actions)
- **Mechanism.** Castryck–Sotáková–Vercauteren (recalled, Crypto 2020): for a class group action of Cl(O), disc(O) = Δ, each odd prime m | Δ gives a genus character χ_m: Cl(O) → {±1} computable from the m-torsion (Tate pairing / Frobenius on E[m]); for 2 | Δ characters via 4- or 8-torsion in some congruence cases. If χ is computable, DDH on the action is broken with advantage 1/2. CSIDH (Δ = −4p, p ≡ 3 mod 4) is immune only because the sole odd divisor is p and E[p] is unavailable. For orders of conductor f (Δ = f²·Δ_K) new odd divisors appear; the question is whether their torsion is *rational over the working field* in each relative.
- **Attacks.** Decisional assumption (DDH-type) of CSURF, SCALLOP, PEARL-SCALLOP, oriented-curve actions — a security-proof gap for IND-CPA KEMs built on them, not a key recovery.
- **Delta needed.** One relative with an odd prime m | Δ whose m-torsion is F_{p^k}-rational for small k.
- **Obstruction.** SCALLOP chooses f a large prime precisely so E[f] is not accessible; CSURF uses Δ = −p (p ≡ 7 mod 8) with odd class number, no 2-genus structure.
- **Kill test.** Table of (relative, Δ, odd m | Δ, smallest k with E[m] ⊂ E(F_{p^k})): if every k exceeds 2^40 field-element bits of work, lead dies as `[known]` immunity.
- **Tag.** `[adaptation]`.
- CHECKED: H-SSIQ-d724f2 (group-theoretic census of subgroups H_N ⊂ GL₂ for the maximal order — same torsion-subgroup census machinery, supersingular side), H-ICINV-82ee6a (endomorphisms from the Frobenius order Z[π]; the ordinary-order analogue of the conductor question).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `theorem genus_char_computable (O : Order K) (m : ℕ) (hm : m.Prime ∧ Odd m ∧ (m : ℤ) ∣ discr O) : ∃ χ : ClassGroup O →* ℤˣ, ∀ a, χ a = tatePairingChar m (act a E₀)`.
- EXP: none; nearest surface is `aburan28/ecbench`.

### 3. Self-pairing (CHMMvBV) conductor audit for conductor-f class group actions
- **Mechanism.** Castryck–Houben–Merz–Mula–van Buuren–Vercauteren (recalled, Crypto 2023): if the orientation order O has conductor divisible by ℓ^r for large r, a cyclic self-pairing on E[ℓ^r] lets one recover the action modulo the ℓ-part and descend the vectorization problem to the maximal order. CSIDH (conductor 1) is unaffected; the attack targets OSIDH-style and SCALLOP-style choices.
- **Attacks.** Vectorization (key recovery) for conductor-non-trivial relatives only.
- **Delta needed.** A deployed/proposed relative with smooth conductor part ℓ^r, r ≥ 2.
- **Obstruction.** Current SCALLOP/PEARL-SCALLOP pick prime f; the audit likely confirms immunity.
- **Kill test.** Enumerate published conductor choices; if all are prime or square-free with large prime factors, close as parameter audit.
- **Tag.** `[known]` parameter audit.
- CHECKED: H-SSIQ-dfee7e (admissible divisor count of a B-smooth integer in a split window — same smooth-divisor structure that controls self-pairing descent), H-ALISO-014 (auxiliary_discriminant_search — discriminant/conductor search harness).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `lemma self_pairing_nondegenerate_of_conductor (O : Order K) (ℓ r : ℕ) (h : ℓ^r ∣ conductor O) : ∃ e : E[ℓ^r] → μ_{ℓ^r}, cyclicNondegenerate e`.
- EXP: none; nearest surface is `aburan28/cryptanalysis`.

### 4. Disorientation-fault adaptation to dCTIDH / CTIDH Matryoshka batches
- **Mechanism.** Banegas–Krämer–Lange–Meyer–Panny–Reijnders–Sotáková–Stebila (recalled, Eurocrypt 2023): flipping the orientation (E vs. quadratic twist, i.e. the sign of an exponent coordinate during Vélu steps) yields a faulty public key [𝔞']E whose relation to the correct one leaks the signs/magnitudes of exponents; recovery with tens of faults. CTIDH (recalled: Banegas–Bernstein–Campos–Chou–Lange–Meyer–Smith–Sotáková 2021) batches primes and uses Matryoshka-doll isogenies; dCTIDH removes dummies. Adaptation: fault the per-batch sign bit; the Matryoshka structure means one fault disorients a whole batch, so the per-fault information is a batch sign vector (log₂ of batch size bits), fewer faults than plain CSIDH.
- **Attacks.** Implementation (fault) attack on CTIDH/dCTIDH signing/decapsulation with repeated key.
- **Delta needed.** Fault count ≤ 2× number of batches to recover the full key.
- **Obstruction.** Both implementations recompute/verify the output curve's supersingularity and may re-derive orientation from Elligator; a faulted sign may be caught by the "twist purity" check.
- **Kill test.** Simulated fault model (single sign flip per batch) on a reference CTIDH-511; if full key recovery needs > 2^10 faults or is blocked by output validation, lead dies.
- **Tag.** `[adaptation]`.
- CHECKED: H-WESO-516558 (sampler endpoint distribution of random walks — the analysis template for "what does a faulty endpoint reveal"), H-ECDLP-3550b8 (deterministic-walk basin structure with a distinguishing predicate — same basin counting for faulty-output classification).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; nearest is crypto-lean `SplitPrime.Obstruction` ("twist purity", theorem names not quoted); would need `theorem twist_action_inverse (a : ClassGroup (ℤ[√-p])) (E) : twist (act a E) = act a⁻¹ (twist E)`.
- EXP: none; nearest surface is `aburan28/crypto-autoresearcher`.

### 5. Elligator rejection-count and batch-order side channel in CTIDH
- **Mechanism.** CTIDH samples points by Elligator; a point is usable for prime ℓ_i only if the cofactor-cleared point has full ℓ_i-order, probability (1 − 1/ℓ_i). The *number of rejections per batch* is data-dependent on the current intermediate curve, which depends on the partial key. Power/EM traces count xDBLADD loops; the rejection statistics over many executions with the same key form a key-dependent fingerprint (a measurement attack, not a direct recovery).
- **Attacks.** Constant-time claim of CTIDH (implementation side channel).
- **Delta needed.** Mutual information between rejection-count vector and key > 1 bit per 2^10 traces.
- **Obstruction.** CTIDH's design argues the rejection distribution is key-independent conditioned on public data because the sampled point is uniform; the fingerprint may be pure noise.
- **Kill test.** Simulation: 2^16 executions × 2 keys, compare rejection-count histograms; if total variation < 2^−8, lead dies.
- **Tag.** `[adaptation]`.
- CHECKED: H-WESO-516558 (sampler part H-S: uniformity of walk endpoints — same question for Elligator-sampled points), H-ALISO-010 / H-ALISO-011 (parity_center_smoothness probe/verify — the brief's existing statistical-fingerprint harness).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `theorem elligator_rejection_independent (E : SupersingularFp p) (ℓ) : Pr[rejects ℓ | E] = 1/ℓ` as a statement independent of E.
- EXP: none; nearest surface is `aburan28/ecbench`.

### 6. Effective key entropy of exponent-vector keys via the relation lattice (CSIDH-512, CTIDH-511, dCTIDH)
- **Mechanism.** Keys e ∈ [-m,m]^n map to Cl(O) by e ↦ ∏ 𝔩_i^{e_i}; collisions are vectors of the relation lattice Λ ⊂ Z^n. For CSIDH-512, 11^74 ≈ 2^256.8 keys vs N ≈ 2^257.1 (recalled BKV), heuristically near-injective. CTIDH/dCTIDH use *weighted* batch exponents with a different key distribution; its image density on Cl and collision rate have not (to my knowledge) been tabulated with the BKV lattice. Lower effective entropy directly lowers the MITM/vOW classical cost 2^{H/2}.
- **Attacks.** Classical security level claim (parameter audit, measurable exactly at CSIDH-512 since Λ is known).
- **Delta needed.** Entropy loss ≥ 8 bits to matter.
- **Obstruction.** Expected loss is < 1 bit; only the batch-weighted distributions have any room.
- **Kill test.** Count exact collisions of the key distribution modulo Λ by LLL/BKZ-reduced Λ on CSIDH-512 and CTIDH-511 keyspaces (sample 2^20 keys, reduce, count repeats); loss < 2 bits kills.
- **Tag.** `[known]` parameter audit.
- CHECKED: H-SSIQ-dfee7e (integer-only Arm I: counting admissible representations in a window — same counting), H-ALISO-017 (auxiliary_lattice_kani — lattice-reduction harness).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `lemma key_map_injective_of_short (Λ : Submodule ℤ (Fin n → ℤ)) (h : ∀ v ∈ Λ, v ≠ 0 → ‖v‖∞ > 2m) : Function.Injective (fun e : Box m → ClassGroup O => act e)`.
- EXP: none; nearest surface is `aburan28/cryptanalysis`.

### 7. Low-memory vOW collision on Cl(Z[√−p]) with arbitrary-ideal steps
- **Mechanism.** Classical best for CSIDH is Delfs–Galbraith / MITM at O(p^{1/4}) ≈ 2^128 for 512-bit p. A van Oorschot–Wiener walk on the key space needs a deterministic step function; with Clapoti/PEGASIS-style evaluation the step can be an arbitrary ideal determined by a hash of the current curve (no exponent-vector restriction), giving a random walk on Cl itself with 2^{H/2} steps and polynomial memory. The time exponent is unchanged; what changes is the per-step cost (one 4-dim action vs. an exponent-vector action) and memory (poly vs 2^128).
- **Attacks.** Classical cost accounting of CSIDH / CSI-FiSh (parameter audit).
- **Delta needed.** Per-step cost ≤ exponent-vector step; else no change.
- **Obstruction.** 4-dim isogenies at 512-bit p are far slower than 74 small Vélu steps; the gain is only at SQALE'd sizes where the walk is infeasible anyway.
- **Kill test.** Benchmark step cost both ways at 511-bit p; if ratio > 1, close as `[known]` with no delta.
- **Tag.** `[known]`.
- CHECKED: H-ECDLP-3550b8 (deterministic walk f on a set of size N with distinguished-point density θ = 1/W; basin structure — exactly the vOW object), H-WESO-516558 (non-backtracking walk endpoints on ideals).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `theorem vow_expected_steps (N W : ℕ) : 𝔼[collisionTime] ≤ C * Real.sqrt N` for a random function on a set of size N.
- EXP: none; nearest surface is `aburan28/cryptanalysis`.

### 8. Security-proof gap: REGA proofs assume uniform Cl(O) sampling; CSIDH samples a box
- **Mechanism.** Proofs for CSIDH-based KEMs and CSI-FiSh-style signatures model the action as an (R)EGA with keys uniform on Cl(O). Actual keys are uniform on [-m,m]^n; statistical distance to uniform on Cl is bounded by the image density (≈ 1 − 2^{-0.3} for CSIDH-512) and is *not* negligible. Either the proofs need the "weak pseudorandomness of the box distribution" as an explicit extra assumption or a tightness loss of log₂(N / #image).
- **Attacks.** Security-proof gap (not a cryptanalytic attack).
- **Delta needed.** Exhibit a reduction loss ≥ 1 bit or a distinguisher between box and uniform (the latter would be a real result; expect none).
- **Obstruction.** With Λ known (CSIDH-512) one can rejection-sample uniformly, closing the gap at that size only; unknown Λ at 1024+ bits leaves the gap.
- **Kill test.** Write the reduction with explicit SD term; if the term is ≤ 2^{-64} under a heuristic equidistribution assumption, the gap is cosmetic.
- **Tag.** `[adaptation]`.
- CHECKED: H-WESO-516558 (H-S sampler uniformity claim — the same "is the induced distribution uniform on the target set" question), H-SSIQ-dfee7e (counting representations in a window).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `theorem box_to_class_sd_bound (m n : ℕ) (Λ) : statDist (pushforward act (uniform (Box m))) (uniform (ClassGroup O)) ≤ 1 - (2m+1)^n / Nat.card (ClassGroup O)`.
- EXP: none; nearest surface is `aburan28/crypto-lean`.

### 9. Genus characters on the brief's ordinary toy isogeny classes (CRS-type action sanity check)
- **Mechanism.** The brief's H-ICINV work uses complete F_p-isogeny classes of ordinary curves with Frobenius order Z[π] at p ∈ {2003, 4001, 6007} and a ladder below 2^24. These are exactly Couveignes–Rostovtsev–Stolbunov action spaces. CSV's genus attack applies whenever an odd m | disc(Z[π]) has E[m] rational over small extension — for ordinary classes this is frequent (disc = t² − 4p has many small odd factors). A direct computation of χ_m on these certified classes gives a ground-truth table of "DDH-broken vs DDH-plausible" toy classes, and tests whether the j-invariant/endomorphism features of H-ECDLP-f8101e correlate with genus (they should: genus is an isogeny-class-level invariant, so it is constant on the class — a useful null).
- **Attacks.** Decisional assumption of ordinary-curve commutative actions (toy-scale measurement; CRS itself is performance-dead, so this is a validation of the attack mechanics, not a new target).
- **Delta needed.** None for security; delta is a verified harness.
- **Obstruction.** Toy scale only; the only refuted H-ICINV record warns that invariant-selection claims did not survive scoping.
- **Kill test.** If χ_m computed via Tate pairing on E[m] disagrees with χ_m computed via the form-class genus of the connecting ideal on any certified class, the harness (or the recollection of CSV) is wrong.
- **Tag.** `[known]` (CSV mechanics) / measurement.
- CHECKED: H-ICINV-82ee6a (ordinary E/F_p, Frobenius order Z[π], toy ladder < 2^24 — the exact object), H-ECDLP-f8101e (public selection of isogenous representative via j-invariant / endomorphism features), H-ICINV-6c7920 (certified complete classes vs Hurwitz–Kronecker mass at p ∈ {2003, 4001, 6007}).
- DISPROVEN: H-ICINV-6c7920 `rejected_scoped` — invariant-based representative selection did not reduce ECDLP cost at toy scale; this lead makes no cost claim and uses the classes only as a DDH test bed.
- LEAN: no Lean coverage; would need `theorem genus_char_constant_on_horizontal_class (O : Order K) (m) (hm : (m:ℤ) ∣ discr O) : ∀ a b, horizontallyIsogenous (act a E₀) (act b E₀) → χ_m a = χ_m b`.
- EXP: none; nearest surface is `aburan28/ecbench`.

### 10. Structured relations for Cl(Z[√−p]) at 1024/1792 bits via smooth norm equations x² + p y² = ∏ ℓ_i^{e_i}
- **Mechanism.** BKV's class-group computation (recalled ≈ 52 core-years at 512 bits) is Hafner–McCurley relation collection, L_Δ(1/2). The CSIDH prime set {ℓ_i} is fixed and tiny, so relations are exactly representations ∏ ℓ_i^{e_i} = x² + p y² with the known splitting ℓ_i = 𝔩_i 𝔩̄_i. Lead: quantify whether the fixed small factor base plus sieving on the quadratic-form side (as opposed to generic large-prime variations) brings 1024-bit Δ within 2^70 operations. Knowing Λ at 1024 bits enables leads 6 and 8 and CSI-FiSh at that size; it is *not* an attack.
- **Attacks.** Enabling computation only (the "relation between the action and the class group" axis).
- **Delta needed.** ≥ 2^10 factor over generic L(1/2) at Δ ≈ 2^1026.
- **Obstruction.** The factor base is forced to be the CSIDH primes, far too small for L(1/2)-optimal smoothness; generic bases dominate.
- **Kill test.** Smoothness-probability estimate (Dickman ρ) with the forced base at 1024 bits; if expected relations per 2^60 trials < n = 130, dead.
- **Tag.** `[known]`.
- CHECKED: H-SSIQ-dfee7e (admissible divisors of B-smooth integers in a split window — the same smoothness census), H-ALISO-016 (auxiliary_geometric_principalization — principal-ideal / relation finding harness).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `lemma relation_of_norm_rep (x y : ℤ) (e : Fin n → ℤ) (h : x^2 + p*y^2 = ∏ i, ℓ i ^ e i) : ∃ s : Fin n → ℤˣ, ∏ i, (𝔩 i)^(s i * e i) = 1 in ClassGroup`.
- EXP: none; nearest surface is `aburan28/cryptanalysis`.

### 11. Vectorization via F_p-rational endomorphism ring: Castryck–Panny–Vercauteren reduction cost at SQALE'd sizes
- **Mechanism.** Castryck–Panny–Vercauteren (recalled, Eurocrypt 2020): given End(E) for a CSIDH curve E = [𝔞]E₀ as a maximal order in B_{p,∞} together with the Frobenius-fixed suborder Z[√−p], one computes the connecting ideal class 𝔞 in Cl(Z[√−p]) in polynomial time — so CSIDH vectorization reduces to End-ring computation for curves defined over F_p. The classical End-ring computation for F_p-curves is Delfs–Galbraith O(p^{1/4}) (same as MITM), so no classical gain; quantum, the reduction is dominated by Kuperberg anyway. Audit target: whether the F_p-rationality (the two-cycle structure of the Fp-isogeny graph, the "floor/surface" of 2-isogenies) gives any sub-p^{1/4} classical End computation. Expect no.
- **Attacks.** Vectorization (key recovery) via the quaternion side.
- **Delta needed.** Any classical End-ring algorithm for F_p-rational supersingular curves below p^{1/4}.
- **Obstruction.** None known; the Fp structure appears to give exactly √ of the general p^{1/2}.
- **Kill test.** Literature + heuristic argument that Fp-rational walks have the same mixing as general ones; if no sub-p^{1/4} path exists, close.
- **Tag.** `[known]`.
- CHECKED: H-SSIQ-d724f2 (standard maximal order O of B_{p,∞}, i² = −1, j² = −p — the quaternion object of the reduction), H-ALISO-001 / H-ALISO-003 (degree-first Hecke and Frobenius-midpoint sweeps — Frobenius-structured walks on the supersingular graph).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; nearest module crypto-lean `SplitPrime.Obstruction` ("scalar-only action", theorem name not quoted); would need `theorem connecting_ideal_from_endring (E : SupersingularFp p) (O_E : MaximalOrder) : ∃ a : ClassGroup (ℤ[√-p]), act a E₀ = E ∧ computable a from O_E`.
- EXP: none; nearest surface is `aburan28/crypto-lean`.
