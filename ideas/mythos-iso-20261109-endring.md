# Mythos ECDLP ideation — endring (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

# Preliminary note on the BRIEF as supplied

The BRIEF text I was given ends inside §2 (at H-ALISO-017). No `EV-*`, `EXP-*`, `IDEA-*`, or `KN-*` records other than `KN-OPEN-095df5` are quoted, and the only Lean surface quoted is the crypto-lean commit subject `SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness` — a module and three informal descriptors, not theorem names. Per the rules I will not invent ids. Consequently:

- `CHECKED:` cites only `H-*` ids visible in the BRIEF.
- `DISPROVEN:` is `H-ICINV-6c7920 [rejected_scoped]` where relevant (the only recorded refutation in the excerpt), else `none in the brief`.
- `LEAN:` is `no Lean coverage` with the exact statement that would need formalizing (the `SplitPrime.Obstruction` module is referenced as the nearest file, never as a theorem).
- `EXP:` is `none; nearest surface is <path>`, using the autolab package names the BRIEF quotes (`p1486_*`, `p1243_*`) or repository paths.

If the full brief has EV/EXP ids for these mechanisms, the records below should be re-cleared before filing.

---

## LEADS

### 1. Tightness audit of the OneEnd ⇒ EndRing reduction when no small-norm auxiliary endomorphism exists `[adaptation]`

**Mechanism.** The Page–Wesolowski equivalence EndRing ⇔ OneEnd proceeds: given a non-scalar α ∈ End(E) with disc(α) = Δ, compute Z[α]-orientation data, then saturate to the maximal order by repeatedly finding a second endomorphism via a Kani-type embedding in dimension 2 (degree-d endomorphism + degree-(N−d) isogeny glued into an (N,N)-isogeny of E²). The "degree-first Hecke" probes (H-ALISO-001/002) measure exactly which degree pairs (d, N−d) are realizable. **Attacks:** the reduction's *cost*, not the assumption. **Object computed:** the second-endomorphism lattice Z[α, β] ⊂ End(E) and its index in O. **Cost needed:** the reduction is claimed polynomial given a factoring oracle for Δ; the audit asks for the constant: number of (2^k,2^k)-isogeny evaluations in dimension 2 as a function of log |Δ| when the smallest auxiliary degree d admitting N−d a sum of two squares is ≫ 1. **Obstruction:** at |Δ| ≈ p the admissible-pair density is governed by the same two-square obstruction H-SSIQ-dfee7e studies; if the first admissible d exceeds the 2-power torsion available over F_{p²}, one must move to dimension 4 (cost ×~16 per step). **Kill test:** at p ≈ 2^40, sample α of varying disc and record the dimension-2 fallback rate; if the rate stays < 1% up to |Δ| = p^{1.5}, the lead is a non-finding.

```
CHECKED: H-ALISO-001 (degree-first Hecke probe: which auxiliary degrees d are realizable); H-ALISO-002 (its verify arm); H-ALISO-015 (p1243 four-line descent: saturation of a suborder to the maximal order); H-ALISO-017 (lattice Kani: gluing an endomorphism and an isogeny into a dim-2 kernel); H-SSIQ-dfee7e (admissible-divisor density of B-smooth d in a split window)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for a supersingular E/F_{p²} and non-scalar α ∈ End(E) with squarefree discriminant Δ, the index [End(E) : Z[α,β]] divides gcd(Δ, disc(β)) for any β found by the Kani embedding step"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1486_degree_first_hecke_verify`
```

### 2. Class-leakage of KLPT connecting ideals (SQIsign-style zero-knowledge gap) `[known]`

**Mechanism.** Classical KLPT (Kohel–Lauter–Petit–Tignol) outputs an ideal J ~ I of norm ℓ^e with e ≈ (3/2)·log_ℓ p by solving a norm equation in the special extremal order O_0 = Z⟨1, i, (i+j)/2, (1+k)/2⟩, then strong approximation. The output J is *not* uniform in the class; it is biased toward ideals whose first ℓ^{e₁} steps lie near O_0. This is the gap that SQIsign's response-sampling (and its "SigningKLPT") must close. **Attacks:** security-proof gap (zero-knowledge of the identification scheme), not EndRing search. **Object:** the empirical distribution of the first t steps of φ_J in the ℓ-isogeny graph vs the stationary distribution of the non-backtracking walk (exactly H-WESO-516558's sampler). **Cost:** polynomially many transcripts; statistical distance ≥ 1/poly suffices for a distinguisher. **Obstruction:** SQIsign's response is re-randomized and the verifier sees only the response isogeny; the bias must survive the re-randomization. **Kill test:** at p ≈ 2^60 (toy SQIsign), compute 10⁴ KLPT outputs for fixed input class; compare the first-8-step endpoint histogram against H-WESO-516558's walk histogram via χ²; non-finding if p-value > 0.05.

```
CHECKED: H-WESO-516558 (endpoint distribution of non-backtracking walks on norm-2 left ideals — the null model); H-SSIQ-dfee7e (integer-only arm of the norm-equation splitting that KLPT performs); H-SSIQ-d724f2 (census of O acting on level-N structure, the Galois-image side of the same bias)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "the pushforward of the uniform measure on {J : J ~ I, nrd(J) = ℓ^e} under the first-step map to the ℓ-isogeny neighbourhood of E_0 is uniform iff the number of norm-ℓ^e representatives is divisible by ℓ+1"
EXP: none; nearest surface is aburan28/cryptanalysis (pcc files shared with crypto-autoresearcher, per the "Shared-code lock" commit)
```

### 3. Norm-size gap between KLPT, lattice-KLPT, and dimension-2 "Clapoti-style" ideal-to-isogeny `[known]`

**Mechanism.** Three constructive-Deuring routes produce ideals of very different norms: KLPT ~ p^{3} (ℓ^e), the "generalized KLPT" with lattice reduction ~ p^{15/4}, and the dimension-2 route (embed an ideal of norm N ≈ p into an (N,N)-isogeny of E×E' using two equivalent ideals of coprime norms N₁+N₂ = 2^f). The dimension-2 route needs only norm ≈ p^{1/2}–p per ideal, which is why it is the current SQIsign2D-style default. **Attacks:** nothing — a parameter audit establishing which norm regime each filed probe measured. **Object:** the pair (N₁, N₂) with N₁ + N₂ = 2^f and the ideal lattice reduction producing them. **Cost:** dimension-2 gluing costs O(f) (2,2)-isogeny steps each ≈ 10³ F_{p²}-mults; finding (N₁,N₂) requires a Cornacchia-type step whose success probability is the admissible-divisor density H-SSIQ-dfee7e measured. **Obstruction:** 2^f must exceed p; over F_{p²} with p = 2^f·c − 1 this is free, otherwise one pays a field extension. **Kill test:** reproduce the admissible-pair rate for N ∈ [p^{1/2}, p] at p ≈ 2^64; if it matches 6/π² · (Σ over divisor pairs) to within 5%, nothing new.

```
CHECKED: H-SSIQ-dfee7e (admissible-divisor count k(d) in the split window [ceil(d/X), X] is literally the (N₁,N₂) split); H-ALISO-017 (lattice Kani: the gluing step); H-ALISO-016 (geometric principalization: the ideal-class side of choosing N₁,N₂)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "if I, J are left O-ideals with J ~ I, gcd(nrd I, nrd J) = 1 and nrd I + nrd J = 2^f, then the kernel K = {(φ_I(P), φ_J(P)) : P ∈ E[2^f]} is maximal isotropic for the 2^f-Weil pairing on E_I × E_J"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1243_auxiliary_lattice_kani`
```

### 4. Decisional EndRing via level-N Galois-image census `[speculative]`

**Mechanism.** H-SSIQ-d724f2 tabulates H_N ⊂ GL_2(Z/N) for the standard maximal order O of B_{p,∞}. The decisional question: given E and a candidate order O', decide whether End(E) ≅ O' by computing the image of a *small-degree* known endomorphism (e.g. Frobenius for E/F_p, or an explicit degree-2 endomorphism on j = 1728) on E[N] and comparing to the census. **Attacks:** a decisional variant of EndRing ("is End(E) this specific order"), which is weaker than search but matters for SQIsign public-key validity and for "special curve" detection à la Love–Boneh. **Object:** the conjugacy class of the mod-N representation of End(E) ∩ (known endomorphisms) in GL_2(Z/N). **Cost:** O(N³) group operations to compute the image, plus the census lookup; useful only if N is small (N ≤ 2^20) and the census separates orders at that level. **Obstruction:** for a generic supersingular E with no known non-scalar endomorphism, there is nothing to represent — the census is informative only for oriented or special curves, where End is already easy. **Kill test:** check whether the H_N census separates the ≈ p/12 maximal-order classes at N = 2^k for k ≤ 20; if the number of distinct H_N classes is o(p/12), the test cannot decide EndRing.

```
CHECKED: H-SSIQ-d724f2 (the census of H_N ⊂ GL_2(Z/N) for the standard maximal order; explicitly NO ATTACK); H-ICINV-82ee6a (ordinary analogue: endomorphism features from Z[π] as class invariants); H-ECDLP-f8101e (ordinary analogue: j-invariant / endomorphism features as representative selectors)
DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — in the ordinary toy setting, isogeny-class invariant selection did not reduce end-to-end cost; the supersingular decisional variant must avoid the same "features do not separate" failure
LEAN: no Lean coverage; nearest file is crypto-lean `SplitPrime.Obstruction` ("scalar-only action" descriptor); would need: "for supersingular E/F_{p²} with End(E) ⊗ Z/N acting on E[N], the image of End(E) is all of M_2(Z/N) for every N coprime to p, hence the mod-N image alone does not determine the isomorphism class of End(E)"
EXP: none; nearest surface is isogeny-labs/crypto (no isogeny-specific commit surface quoted)
```

### 5. Frobenius-midpoint (Delfs–Galbraith) restricted to F_p-curves with an extra small-discriminant endomorphism `[known]`

**Mechanism.** For E/F_p supersingular, End(E) ⊇ Z[π], π² = −p, and the Delfs–Galbraith algorithm walks to the F_p-subgraph in Õ(p^{1/2}) then in Õ(p^{1/4}) within it. The "Frobenius midpoint sweep" probes (H-ALISO-003/004/005) measure the midpoint-collision statistics. The lead: when E additionally carries an endomorphism of discriminant D with |D| ≪ p (a Z[√D]-orientation), the Z[π, α]-generated suborder has index ≈ √(|D|p)/… in O and the EndRing problem reduces to a class-group computation of Q(√−p) plus saturation — cost Õ(p^{1/4}) → L_p(1/2) via subexponential class-group methods. **Attacks:** EndRing on the F_p-curve subpopulation only (size ≈ h(−p) ≈ p^{1/2}); SQIsign keys are not F_p-curves, so this is an audit that the F_p-restriction is correctly excluded, not an attack. **Object:** the Z[π]-ideal class [𝔞] with E = 𝔞 ⋆ E_0. **Cost:** class group of disc −4p: L_p(1/2, √2) classically, poly quantumly (Kuperberg for the group action, then DLOG). **Obstruction:** the public key must be an F_p-curve or isogenous to one by a *known* short isogeny; generic SQIsign keys are p^{1/2}-far. **Kill test:** confirm that no filed protocol parameter set places the public curve within distance O(log p) of the F_p-subgraph — if any does, that set is weak.

```
CHECKED: H-ALISO-003 (Frobenius midpoint sweep: collision statistics on the F_p-spine); H-ALISO-004, H-ALISO-005 (verify arms); H-ALISO-008 (Hecke Krylov probe: Frobenius as a Hecke-commuting operator); H-ECDLP-3550b8 (basin analysis of deterministic walks with a distinguished-point predicate — the random-walk collision model the midpoint sweep inherits)
DISPROVEN: none in the brief
LEAN: no Lean coverage; nearest file is crypto-lean `SplitPrime.Obstruction` ("twist purity" descriptor is about F_p-twists); would need: "for supersingular E/F_p with p ≡ 3 mod 4, the order Z[π] with π² = −p has index 2 or 1 in Z[(1+π)/2] ⊂ End(E), and End(E) ∩ Q(π) is one of these two orders"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1486_frobenius_midpoint_sweep_verify`
```

### 6. Orientation-to-EndRing: the D ≈ p^{1/2} vs D ≈ p gap for oriented curves `[adaptation]`

**Mechanism.** Given a primitive O_D-orientation (ι: O_D ↪ End(E)) with |D| < p, End(E) is recoverable in time polynomial in log p times a class-group computation of discriminant D plus a vectorization step costing Õ(|D|^{1/4}) classically (Wesolowski's "orientations are hard to find but easy to use" framework). For CSIDH-like D ≈ 4p this is p^{1/4}, matching generic; for |D| ≈ p^{1/2} (e.g. an endomorphism of degree ≈ p^{1/4}) it is p^{1/8}. **Attacks:** the *one-endomorphism-of-moderate-degree* variant of EndRing — specifically "small-discriminant oriented" keys. **Object:** the class-group DLOG in Cl(O_D) and the induced ideal 𝔞 with E = 𝔞 ⋆ E_D. **Cost:** Õ(|D|^{1/4}) classical / L_{|D|}(1/2) with index calculus in Cl(O_D) / polynomial-depth quantum (Kuperberg Õ(2^{√(log |D|)})). **Obstruction:** finding an orientation of discriminant ≪ p on a *generic* curve is as hard as EndRing itself; the lead only bounds the damage from leaked endomorphisms (e.g. via faults or malformed keys). **Kill test:** at p ≈ 2^64, inject a known degree-2^20 endomorphism into a random E and measure wall-clock EndRing recovery vs generic Õ(p^{1/2}); non-finding if speedup < 2^10.

```
CHECKED: H-ALISO-014 (auxiliary discriminant search: finding small-D orientations); H-ALISO-016 (geometric principalization: the ideal-class step in Cl(O_D)); H-ALISO-015 (four-line descent: saturating Z[ι(O_D), π]-type suborders); H-ICINV-82ee6a (ordinary analogue: Frobenius-order endomorphisms as the orienting data)
DISPROVEN: none in the brief
LEAN: no Lean coverage; nearest file is crypto-lean `SplitPrime.Obstruction` ("tower faithfulness" descriptor); would need: "if ι: O_D ↪ End(E) is a primitive orientation and 𝔞 is an invertible O_D-ideal, then End(𝔞 ⋆ E) ≅ the right order of the left-End(E)-ideal End(E)·ι(𝔞), and the orientation pushes forward"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1243_auxiliary_discriminant_search`
```

### 7. Smoothness bottleneck in KLPT strong approximation: measured vs Dickman-heuristic density `[known]`

**Mechanism.** KLPT's strong-approximation step needs a value of the binary form f(x,y) = x² + y² (or p(x²+y²) after the j-twist) in an arithmetic progression mod N to be ℓ-power-smooth (or of the form ℓ^e exactly). The heuristic cost assumes values of size ≈ p³N are "random" for smoothness, i.e. probability ρ(u) with u = log(p³N)/log B. The parity-center smoothness probes (H-ALISO-010/011) measure a related quantity for the Hecke operator at 2. **Attacks:** nothing — a measurement that either confirms the heuristic or exposes a factor-of-c gap in KLPT's expected running time (a cost audit relevant to SQIsign signing time and to the attack cost of any EndRing method that uses KLPT as a subroutine). **Object:** empirical ℓ-smooth density of f(x,y) on the lattice coset. **Cost:** 10⁵–10⁶ form evaluations at p ≈ 2^60; trivially parallel. **Obstruction:** x² + y² values have local biases at primes ≡ 3 mod 4 (never divide primitively), so the correct heuristic is a sieve-adjusted Dickman, not ρ(u); the audit must use the adjusted baseline or it will falsely report a gap. **Kill test:** ratio of measured density to sieve-adjusted ρ(u) within [0.9, 1.1] at B = 2^16 ⇒ non-finding.

```
CHECKED: H-ALISO-010 (parity-center smoothness probe); H-ALISO-011 (its verify arm); H-SSIQ-dfee7e (B-smooth divisor density in the split window — the same sieve-adjusted Dickman baseline); H-ALISO-009 (Hecke support cost probe: cost accounting that consumes this density)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for the norm form f(x,y) = x² + y² on Z², the proportion of values ≤ X divisible primitively by a prime q ≡ 3 mod 4 is 0, and the density of B-smooth values is bounded above by ρ(u)·∏_{q≤B, q≡3(4)} (1−1/q)^{-1}·(1−2/q)"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1486_parity_center_smoothness_verify`
```

### 8. Hecke-Krylov subspace as a certificate of End(E) ⊗ Q, not End(E) `[speculative]`

**Mechanism.** The Hecke operators T_ℓ on the supersingular module (functions on the ≈ p/12 vertices) commute with the Brandt-matrix action; the Krylov subspace of a vertex indicator under T_2, T_3 (H-ALISO-008) encodes the local Brandt data of its ideal class. The lead asks whether the Krylov dimension profile after k steps identifies the *isomorphism class of End(E)* (a maximal order) or only its genus / local type (which is trivial — all maximal orders in B_{p,∞} are locally conjugate). **Attacks:** EndRing decisional; also a guard against over-claiming by the filed H-ALISO-008 probe. **Object:** the sequence dim span{v, T_2 v, …, T_2^k v} for a vertex indicator v. **Cost:** O(k · p) field ops per vertex; infeasible as an attack at p ≈ 2^256 but a valid proof-gap check at toy p. **Obstruction:** by Eichler's theorem all maximal orders are locally isomorphic; any invariant computed from finitely many Hecke operators in a bounded Krylov depth sees only local data unless depth ≈ log_ℓ p (the graph's diameter), at which point the cost is the full graph. **Kill test:** at p ∈ {1486-adjacent primes used by the autolab packages}, check whether Krylov profiles up to depth log_2 p/2 are identical across all vertices; if yes, the invariant is genus-only and the lead closes.

```
CHECKED: H-ALISO-008 (Hecke Krylov probe); H-ALISO-006 (Hecke degree-pair support probe); H-ALISO-007 (its verify arm); H-SSIQ-d724f2 (census of the standard maximal order — the "all maximal orders are locally the same" baseline)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for any two maximal orders O, O' of B_{p,∞} and any prime q ≠ p, O ⊗ Z_q ≅ O' ⊗ Z_q ≅ M_2(Z_q), hence any invariant factoring through finitely many local completions is constant on the set of maximal orders"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1486_hecke_krylov_probe`
```

### 9. Fault on ideal-to-isogeny translation: non-cyclic kernel leaks a secret endomorphism `[speculative]`

**Mechanism.** In SQIsign-family signing, the response ideal J (norm 2^f) is translated to an isogeny by computing ker φ_J = E[J] = {P ∈ E[2^f] : α(P) = 0 ∀α ∈ J}, via evaluating a generator α ∈ J on a basis of E[2^f]. A fault that skips or corrupts one generator evaluation yields a kernel K' ⊋ E[J] (possibly non-cyclic). If the signer then outputs a non-cyclic or wrong-degree isogeny, the verifier rejects — but the *faulty output itself*, compared with a correct signature on the same challenge, exposes α(P) for a basis point P, i.e. the mod-2^f action of a secret endomorphism. With f ≈ log₂ p this is a full mod-2^f representation of one endomorphism, from which Z[α] and then (Lead 1) End(E) follow. **Attacks:** implementation (fault) → one-endomorphism → EndRing. **Object:** the matrix of α on E[2^f] in a known basis; recovery of α ∈ End(E) by CRT over the basis (requires the degree of α to be < 2^{2f}, which holds for the secret ideal generators used). **Cost:** one or two faults plus a correct signature; poly post-processing. **Obstruction:** implementations check cyclicity / degree before output and re-randomize the kernel basis; the attack needs an unchecked output path. **Kill test:** on a reference implementation at toy p, simulate the skip-fault; if the output is rejected before serialization and nothing is emitted, close.

```
CHECKED: H-SSIQ-d724f2 (mod-N action of O on E[N] — the object the fault exposes); H-ALISO-015 (four-line descent — the saturation step needed after recovering Z[α]); H-WESO-516558 (norm-2 ideal walks: the response-isogeny structure)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for α ∈ End(E) with deg α < 2^{2f}, the matrix of α on E[2^f] with respect to a fixed basis determines α uniquely among endomorphisms of that degree bound"
EXP: none; nearest surface is aburan28/cryptanalysis (pcc shared-code files)
```

### 10. Quantum EndRing: is there a hidden-shift structure without an orientation? `[known]`

**Mechanism.** Quantum speedups for isogeny problems (Kuperberg/Regev subexponential) require an abelian group action — i.e. an orientation. For generic supersingular EndRing the best known quantum algorithm is Grover/claw-finding at Õ(p^{1/4}) (or Tani's at p^{1/3} in the claw model, which is not applicable to EndRing directly). The lead is a proof-gap record: formally state why the Brandt/Hecke structure (non-abelian, the quaternion ideal class *set* is not a group) blocks a hidden-shift reduction, and audit H-ALISO-012/013's quantum cost accounting for any step that implicitly assumed an abelian action. **Attacks:** EndRing (quantum), as an audit. **Object:** the left-ideal class set Cl(O), of size ≈ p/12, with no group structure; the Hecke algebra acting on functions on it. **Cost:** generic Õ(p^{1/4}) quantum; a hidden-shift reduction would give L_p(1/2)-type cost and would be a major result. **Obstruction:** Cl(O) is a set with a right action by the normalizer-group-like structure only through two-sided ideals, which number O(1) (just the ideals of norm p and principal multiples); no free transitive abelian action exists. **Kill test:** inspect H-ALISO-012's oracle model; if every oracle call is a graph-neighbourhood or Hecke evaluation and no abelian group is invoked, the accounting is sound and this closes as a non-finding.

```
CHECKED: H-ALISO-012 (quantum aggregate oracle probe); H-ALISO-013 (quantum cost accounting verify); H-ALISO-008 (Hecke Krylov probe — the only algebraic structure on Cl(O) the program uses)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "the set of left ideal classes of a maximal order O ⊂ B_{p,∞} carries no free transitive action by an abelian group that is computable from O alone; the two-sided ideal group of O is generated by the unique ideal of norm p and scalars"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1486_quantum_cost_accounting_verify`
```

### 11. Explicit vs implicit EndRing: does a Z-basis of End(E) suffice to solve isogeny-path without KLPT? `[adaptation]`

**Mechanism.** Given Z-bases of End(E₁), End(E₂) (as orders O₁, O₂ ⊂ B_{p,∞}), the connecting ideal is I = O₁·O₂ scaled: concretely I = N·O₁·O₂ where N is the index-denominator, computable by 4×4 integer linear algebra (Hermite normal form) in O(log³ p) bit ops. Translating I to an isogeny of smooth degree is the KLPT step — but the lead notes the dimension-2 route (Lead 3) replaces KLPT with: find J ~ I with nrd J ≤ p^{1/2}·polylog via Minkowski reduction of I (4-dim lattice, nrd(I)-scaled norm form; shortest vector gives nrd J ≈ √p·√nrd(I)/nrd(I)… i.e. ≈ √p), then glue. So EndRing ⇒ isogeny-path costs O(log³ p) + one dim-2 gluing with f ≈ log₂ p — no norm-equation search. **Attacks:** confirms the "EndRing ⇔ isogeny path" equivalence is *tight in constants*, affecting how much "an endomorphism ring computation actually reveals" (answer: a p^{1/2}-norm connecting ideal immediately, a smooth-degree isogeny after one gluing). **Object:** HNF of O₁O₂; Minkowski-reduced basis of I. **Cost:** stated above. **Obstruction:** Minkowski reduction of a rank-4 lattice is exact and cheap; the gluing requires (N₁,N₂) coprime with N₁+N₂ = 2^f — the admissible-pair density of H-SSIQ-dfee7e, which fails with probability ≈ 1 − 6/π²·c per attempt, so expect O(1) retries with re-randomized J. **Kill test:** implement at p ≈ 2^64 and count retries; if the mean exceeds 10, the constant is worse than claimed and the record is downgraded.

```
CHECKED: H-SSIQ-dfee7e (admissible-pair density governs the retry count); H-ALISO-017 (lattice Kani: the gluing); H-ALISO-016 (geometric principalization: choice of J in the class); H-SSIQ-d724f2 (standard maximal order O used as O₁)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for maximal orders O₁, O₂ ⊂ B_{p,∞} with Z-bases given, the Z-module O₁O₂ is a left O₁- right O₂-ideal, and its Minkowski-reduced shortest vector has reduced norm at most c·√p·nrd(O₁O₂)^{1/2} for an absolute constant c"
EXP: none; nearest surface is aburan28/crypto-autoresearcher autolab package `p1243_auxiliary_geometric_principalization`
```

---
