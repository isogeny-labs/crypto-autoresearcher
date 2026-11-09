# Mythos ECDLP ideation — post-sidh (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

# Isogeny lane — angle: what survives the SIDH break

**Reading note on the BRIEF as delivered.** The BRIEF quotes §0–§2 only: 28 hypothesis ids (H-SSIQ-*, H-BINSTD-944a66, KN-OPEN-095df5, H-WESO-516558, H-ECDLP-*, H-ICINV-*, H-ALISO-001…017), five repository heads, and one Lean commit subject (`SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness`). It quotes **no** EV-*, EXP-* or IDEA-* ids, no Lean theorem names, and no record-schema section. I therefore cite only the ids above; every EXP line reads `none` with the nearest autolab package named in the BRIEF; every LEAN line gives the exact statement that would need formalizing, with `SplitPrime.Obstruction` named only as the nearest module (not a theorem). Records use the fields named in the output contract. Literature facts (Castryck–Decru, Maino–Martindale, Robert, GPST, M-SIDH, binSIDH/terSIDH, FESTA, Castryck–Vercauteren, POKE, SQIsignHD/2D) are from memory and are marked as such; nothing below is a claim of a break.

**Shared backbone (stated once, referenced below).** The torsion-point attack is a *recovery* algorithm, not a distinguisher: given φ: E₀→E_A of known degree d and the images φ(P), φ(Q) of a basis of E₀[N], it recovers φ in polynomial time when N > d and N−d is realised by an isogeny from E₀ (dimension 2, Castryck–Decru / Maino–Martindale), when N−d is a sum of two squares (dimension 4, Robert), or unconditionally when N² > d (dimension 8, Robert via Zarhin). The three inputs are therefore: (i) **d known**, (ii) **images known up to at most a common scalar**, (iii) **torsion/degree ratio**. Every survivor removes exactly one input: binSIDH/terSIDH remove (i); M-SIDH/FESTA weaken (ii); POKE-style unbalanced parameters attack (iii); CSIDH, SQIsign, SQIsignHD/2D, CGL and the pure SSI/EndRing problems never exposed torsion images at all. The leads probe how far each removal actually goes.

---

## LEADS

### 1. Degree-first Kani with divisor census against secret-degree torsion schemes `[adaptation]`
**Mechanism.** binSIDH/terSIDH (Basso–Fouotsa, as recalled) publish images of E₀[N] under φ_A of secret degree d_A dividing A = ∏_{i≤t} ℓ_i (binary: subset product; ternary: exponents in {0,1,2}). Kani recovery needs d; the attacker enumerates candidates d ∈ D and runs one splitting test per candidate — a wrong d yields a non-split codomain of the (N,N)-isogeny, a correct d splits. Cost = |D| × T_Kani, with |D| = 2^t (bin) or 3^t (ter) naïvely.
**Object attacked.** The "hidden degree" assumption; concretely the count of admissible d in the window where N² > d (dim 8) or N > d with N−d suitably representable (dim 2/4).
**Security delta needed.** A filter that prunes D by more than a polynomial factor. Two candidate filters: (a) the Weil pairing e_N(φP,φQ) = e_N(P,Q)^{λ²d} if images are masked by a *common* scalar λ — this leaks the quadratic character of d modulo every prime q | N, i.e. ω(N) bits, which for N a product of many small primes could collapse |D| to ≈ 2^{t−ω(N)}; (b) if masking is *independent* per point (diag(λ,μ)), the pairing leaks nothing but the problem becomes FESTA-shaped (Lead 4).
**Obstruction.** If the spec masks with independent scalars, filter (a) is void; filter (b) reduces to the diagonal-masking problem whose only known polynomial attack (Castryck–Vercauteren) needs a small known endomorphism on E₀.
**Kill test.** Implement at toy p (t ≈ 8, N with ω(N) ≈ 6): measure |D_consistent| after the character filter under common-scalar masking vs. independent masking. If common-scalar masking leaves |D| ≈ 2^{t−ω(N)}, the lead is live and is a parameter audit; if the spec uses independent scalars and |D| stays 2^t, the lead dies (becomes Lead 4).
**Why not a re-run.** H-SSIQ-dfee7e counts admissible divisors in a split window but, per its text, is "integer-only Arm I; NO ATTACK; NO EXPONENT" — it never couples the count to a pairing filter or to a Kani splitting test.
```
CHECKED: H-SSIQ-dfee7e (counts admissible divisors k(d) of a B-smooth d in the split window, integer-only, no attack); H-ALISO-001, H-ALISO-002 (p1486_degree_first_hecke_probe/verify — degree-first probing, scoped measurement only); H-ALISO-006, H-ALISO-007 (hecke_degree_pair_support — degree-pair support statistics, no Kani coupling)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "for N coprime to d and P,Q a basis of E[N], e_N(λφP, λφQ) = e_N(P,Q)^{λ²·d}, hence the Legendre symbol (d/q) is determined for every prime q | N"
EXP: none in the BRIEF (no EXP-* ids quoted); nearest surface is autolab package `p1486_degree_first_hecke_probe` (H-ALISO-001), repository not identified in the BRIEF
```

### 2. Torsion-ratio margin audit for schemes that reveal N-torsion with N² < d `[adaptation]`
**Mechanism.** POKE-style and some QFESTA/FESTA-component parameters (as recalled) deliberately publish torsion of order N with N² < d so Robert's dim-8 bound fails. Guess-then-Kani: write φ = φ' ∘ ψ with deg ψ = g; enumerate ψ (≈ g candidates for ℓ-power g, more for composite), then attack φ' with d' = d/g once N² > d/g. Heuristic security of the ratio ≈ log₂(d/N²) − log₂(T_Kani⁻¹ overhead) bits.
**Object attacked.** The parameter claim "N² < d suffices".
**Security delta needed.** d/N² ≥ 2^λ at every published parameter set, *after* accounting that the enumeration is embarrassingly parallel and that the Kani splitting test is the only per-guess work (no vOW-style memory bound).
**Obstruction.** Dim-8 (N,…,N)-isogenies over F_{p²} at p ≈ 1000–1300 bits are concretely heavy; if T_Kani ≈ 2^{30} the audit may show the margin is comfortable. Also some schemes bound N by design so that the guessed prefix g lives on the *attacker's* side (reveals nothing).
**Kill test.** Table (scheme, d, N, log₂(d/N²), estimated T_Kani) for every parameter set recalled; the lead dies if every margin ≥ λ + log₂T_Kani.
**Why not a re-run.** No BRIEF record audits a torsion/degree ratio; H-SSIQ-dfee7e's window [⌈d/X⌉, X] is a divisor-count window, not a ratio margin.
```
CHECKED: H-SSIQ-dfee7e (split-window divisor counting — gives the enumeration size for g, not the margin); H-ALISO-009 (p1486_hecke_support_cost_probe — a cost-probe surface, not ratio-specific)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "if φ = φ'∘ψ with deg ψ = g and the images of E[N] under φ are known, then the images of ψ(E)[N] under φ' are computable in poly(log N) field operations given ψ"
EXP: none in the BRIEF; nearest surface is autolab package `p1486_hecke_support_cost_probe` (H-ALISO-009)
```

### 3. Scalar-masking (M-SIDH) audit: square roots of unity vs. the Castryck–Vercauteren endomorphism condition `[adaptation]`
**Mechanism.** M-SIDH (Fouotsa–Moriya–Petit, recalled) keeps d known but publishes αφ(P), αφ(Q) with α² ≡ 1 (mod N), so the pairing is unchanged and α is hidden among 2^{ω(N)} square roots of unity. Castryck–Vercauteren (recalled) break instances where E₀ carries a known non-scalar endomorphism of small degree, by using it to pin α on each prime-power component. The audit: for each prime q | N, the attacker needs to decide α mod q ∈ {±1}; the endomorphism gives a linear relation on E₀[q] that fixes the sign whenever the endomorphism's action on E₀[q] is not scalar.
**Object attacked.** The repair "mask by α with α² = 1".
**Security delta needed.** A way to fix α mod q without a small endomorphism — e.g. exploit that E₀ with *unknown* End still has Frobenius π_p acting on E₀[q] (over F_{p²}, π_p² = −p is scalar, so no help unless E₀ is F_p-rational and one uses π_p itself).
**Obstruction.** For E₀ chosen by a trusted random walk (unknown End), Frobenius over F_{p²} is scalar on all torsion — exactly the "scalar-only action" obstruction named in the Lean commit; no non-scalar lever is available.
**Kill test.** At toy p, start M-SIDH from (a) j = 1728, (b) a random-walk curve; count how many of the 2^{ω(N)} signs the Frobenius/known-endomorphism relations determine. Dies if (b) determines zero signs.
**Why not a re-run.** H-SSIQ-d724f2's GL₂(Z/N) census is about the standard maximal order's action, not about which masking subgroups survive a given endomorphism lever.
```
CHECKED: H-SSIQ-d724f2 (census of H_N ⊂ GL₂(Z/N) for the standard maximal order of B_{p,∞}; supported, no attack); H-ALISO-014 (p1243_auxiliary_discriminant_search — searches small-discriminant auxiliary endomorphisms, which is the CV lever)
DISPROVEN: none in the brief
LEAN: no Lean coverage (BRIEF names only the module SplitPrime.Obstruction, "scalar-only action", via a commit subject, no theorem); would need "if E/F_{p²} is supersingular then π_{p²} acts on E[N] as the scalar −p for every N coprime to p"
EXP: none in the BRIEF; nearest surface is autolab package `p1243_auxiliary_discriminant_search` (H-ALISO-014)
```

### 4. Commutant census: which masking subgroups of GL₂(Z/N) are Kani-safe (FESTA diagonal/circulant masking) `[adaptation]`
**Mechanism.** FESTA (recalled) masks images by a matrix M from a commutative subgroup (diagonal in the original, with later variants). The attacker knows φ|_{E[N]} up to right-multiplication by M ∈ H. Kani recovery needs the actual images, so the effective search is over H / (stabiliser-induced equivalences). Castryck–Vercauteren show that if End(E₀) contains θ whose matrix on E₀[N] does not commute with H, one obtains equations that shrink H to a polynomial-size set. The lead is to compute, for the H_N in H-SSIQ-d724f2 (the action of the standard maximal order), the commutant C(H_N) ∩ GL₂(Z/N) and compare it with the masking groups actually used: masking inside C(H_N) is immune to this lever; masking outside it is not.
**Object attacked.** The "masked torsion is as hard as unmasked SSI" style assumption, per masking group.
**Security delta needed.** Show that FESTA's chosen masking group, for its chosen E₀, lies outside the commutant of some computable endomorphism's action — otherwise the lead only yields a positive-security census.
**Obstruction.** FESTA's authors (as recalled) already moved to parameters/curves where the CV lever is unavailable; the census will likely confirm immunity, which is still useful as a *measurement* record.
**Kill test.** Enumerate ⟨diag⟩, ⟨circulant⟩, scalars, and the full H_N commutant for N = ∏ small primes at toy size; report which masking groups intersect the non-commuting locus. Dies (as attack) if all deployed groups sit inside the commutant.
**Why not a re-run.** H-SSIQ-d724f2 is a census of H_N itself; it does not take the commutant or compare against masking groups.
```
CHECKED: H-SSIQ-d724f2 (H_N census, supported, "NO ATTACK; NO EXPONENT"); H-ALISO-014 (auxiliary discriminant search supplies the θ)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "for H ≤ GL₂(Z/N) and θ ∈ End(E₀) with matrix Θ on E₀[N], if M ∈ H satisfies MΘ ≠ ΘM then the relation Θ' φ = φ Θ on E[N] determines M modulo C(Θ) ∩ H"
EXP: none in the BRIEF; nearest surface is autolab package `p1243_auxiliary_discriminant_search` (H-ALISO-014)
```

### 5. Adaptive torsion (GPST) reaction attacks on *static-key* survivors `[adaptation]`
**Mechanism.** The 2016 GPST attack survives the break untouched: a static-key party that computes a shared curve from a received torsion basis can be fed maliciously scaled bases (P + [2^{k}]Q-type perturbations) and leaks one bit of the secret per query via equality/inequality of the derived key. Post-break schemes with torsion inputs and static keys (binSIDH/terSIDH used statically, M-SIDH used statically) inherit the oracle; FESTA/POKE wrap it in a Fujisaki–Okamoto / OAEP-type transform. Query count ≈ log₂(secret) with per-query validation bypass.
**Object attacked.** Static-key use of any secret-degree or masked-torsion key exchange; the validation step (pairing checks e_N(P',Q') = e_N(P,Q)^d) when d is secret — the receiver *cannot* run the standard degree check without knowing d, which is the new structural weakness.
**Security delta needed.** A malformed basis that passes whatever validation the static party can run (pairing order check only, since d unknown) while still biasing the shared key by the secret.
**Obstruction.** Ephemeral-only usage or FO transforms close the oracle; the spec may already mandate this.
**Kill test.** Toy implementation of static binSIDH with order-only validation; run a GPST-style sequence; dies if the key derivation rejects all perturbations or the response is secret-independent.
**Why not a re-run.** No BRIEF record addresses reaction/adaptive oracles; H-SSIQ-d724f2 is relevant only as the catalogue of which GL₂(Z/N) elements change the torsion basis without changing the subgroup.
```
CHECKED: H-SSIQ-d724f2 (GL₂(Z/N) subgroup census — identifies which basis changes preserve the generated kernel); H-SSIQ-dfee7e (divisor structure of the secret degree, relevant to what the receiver can validate)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "if the receiver's validation is e_N(P',Q') ∈ μ_N of exact order N only, then for every scalar c coprime to N the basis (P', cQ') passes and the derived kernel ⟨P' + [s]cQ'⟩ differs from ⟨P' + [s]Q'⟩ unless c ≡ 1 mod ord(sQ')"
EXP: none in the BRIEF; nearest surface is autolab package `p1486_degree_first_hecke_probe` (H-ALISO-001)
```

### 6. Auxiliary-isogeny lattice leakage in constructive Kani (SQIsignHD / QFESTA / POKE) `[speculative]`
**Mechanism.** The same (N,N)-isogeny step used offensively is now a *constructive* primitive: to embed φ of degree d into a dimension-2/4 isogeny, the honest party computes an auxiliary γ of degree N − d (or a² + b² decomposition) from the known End(E₀) by a lattice/norm-form search (H-ALISO-017's "lattice kani", H-ALISO-016's "geometric principalization", H-ALISO-015's "four-line descent" are exactly this toolchain by name). The question: does the published object (kernel of the higher-dimensional isogeny, or the codomain/split data) expose γ, and does γ's selection correlate with the secret (e.g. because the search is seeded by, or truncated according to, d or the secret ideal's reduced norm form)?
**Object attacked.** Zero-knowledge / key-privacy of responses in HD/2D signatures and of ciphertexts in Kani-based PKEs.
**Security delta needed.** A statistical test on published auxiliary data distinguishing two secrets, or a leak of the ideal's norm form (which with a few samples gives the ideal).
**Obstruction.** In SQIsignHD/2D (as recalled) the response ideal is sampled uniformly from a fixed-norm set and γ is a deterministic function of public data; then nothing leaks. QFESTA/POKE similarly randomise.
**Kill test.** For a toy SQIsign2D-like instance, fix two secret ideals, sample 10³ responses each, compute auxiliary degrees/norm-form coefficients, run a two-sample test. Dies at p > 0.05 across all extracted features.
**Why not a re-run.** H-ALISO-015/016/017 are scoped *constructive* measurements of the auxiliary toolchain; none frames the auxiliary data as a leakage channel.
```
CHECKED: H-ALISO-017 (p1243_auxiliary_lattice_kani — constructive lattice search for the Kani auxiliary); H-ALISO-016 (p1243_auxiliary_geometric_principalization — principalising the auxiliary ideal); H-ALISO-015 (p1243_auxiliary_four_line_descent — descent step in the same toolchain)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "if the auxiliary isogeny γ is a function of (E₀, N, d, public randomness r) only, then the distribution of the published Kani kernel is identical for any two secrets of equal degree d"
EXP: none in the BRIEF; nearest surface is autolab package `p1243_auxiliary_lattice_kani` (H-ALISO-017)
```

### 7. SQIsign response-sampler independence as the real survivor assumption `[adaptation]`
**Mechanism.** SQIsign reveals the entire response isogeny σ but no torsion images under the secret τ: E₀→E_A, so Kani adds nothing — *provided* the response ideal class is distributed independently of τ. H-WESO-516558 (H-S, sampler) tests whether endpoints of non-backtracking walks on norm-2 left ideals are uniform; the lead couples that sampler statistic to the zero-knowledge requirement: a sampler bias is an attack on the signature even though no torsion is exposed.
**Object attacked.** Honest-verifier zero-knowledge of SQIsign-family; the "sampler" half of H-WESO-516558.
**Security delta needed.** Total-variation distance ≥ 2^{−λ/2} between response distributions for two secrets, detectable with ≤ 2^{40} signatures.
**Obstruction.** H-WESO-516558 is "analyzed" at tested primes only and (per its text) is scoped; extrapolating to 256-bit p is heuristic.
**Kill test.** Reproduce the H-WESO-516558 walk statistics but conditioned on two distinct starting ideals of the same norm; dies if the χ² over endpoint classes is at noise level.
**Why not a re-run.** H-WESO-516558 asks about uniformity of endpoints; this lead asks about *independence from the start*, a different statistic on the same walk.
```
CHECKED: H-WESO-516558 (uniformity of non-backtracking norm-2 ideal walk endpoints, two separately falsifiable parts, tested primes only); H-ALISO-008 (p1486_hecke_krylov_probe — Hecke/Krylov spectral data governing mixing)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "for a left O-ideal I of norm n and the Brandt matrix B_2, the k-step non-backtracking walk distribution from [I] has TV distance ≤ C·(2√2/3)^k from uniform, independent of [I]"
EXP: none in the BRIEF; nearest surface is autolab package `p1486_hecke_krylov_probe` (H-ALISO-008)
```

### 8. Fault on the (2,2)-gluing step in verifiers/decryptors that run higher-dimensional isogenies `[adaptation]` (implementation record)
**Mechanism.** SQIsignHD/2D verification, FESTA decryption and QFESTA/POKE decryption all execute a chain of (2,2)-isogenies (Richelot or theta-coordinate) starting with a *gluing* step E × E' → Jac(C). A fault injected into the gluing kernel point (or into the theta-null point) produces either a non-split codomain where a split was expected or a wrong split; the sign/branch of the failure, observable via accept/reject or via the recovered torsion, is a 1-bit oracle on the secret-dependent kernel. Cost: tens to hundreds of faults, each a single skipped/flipped word in the gluing routine.
**Object attacked.** Implementation of the step that *made* the attack feasible (CD: ≈1 h on SIKEp434 originally, minutes after Oudompheng–Pope), now sitting inside honest code.
**Security delta needed.** A secret-dependent branch or output in the gluing/splitting detection that is not masked.
**Obstruction.** Verification in signatures touches only public data (no secret in verifier); decryption in FESTA/POKE is the real target but is behind FO re-encryption, which detects wrong outputs — although fault *timing* through the re-encryption may still leak.
**Kill test.** Instrument a toy theta-based (2,2) chain with a fault-injection harness; dies if rejection is constant-time and output-independent for all injected faults.
**Why not a re-run.** The BRIEF's Kani packages (H-ALISO-015/016/017) are algebraic measurements, not side-channel or fault studies.
```
CHECKED: H-ALISO-017 (lattice Kani — the honest (2,2) pipeline being faulted); H-ALISO-010, H-ALISO-011 (p1486_parity_center_smoothness_probe/verify — the only BRIEF records touching parity-type branch structure in the Kani harness)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "a (2,2)-isogeny from E × E' with kernel ⟨(P,P'),(Q,Q')⟩ has a split codomain iff the Kani diamond degrees satisfy d + c = N for the given kernel; a one-coordinate perturbation of (P,P') yields a non-split codomain with probability 1 − O(1/p)"
EXP: none in the BRIEF; nearest surface is autolab package `p1243_auxiliary_lattice_kani` (H-ALISO-017)
```

### 9. Frobenius-midpoint meet-in-the-middle as the generic bound for pure SSI survivors `[adaptation]`
**Mechanism.** With torsion gone, the best generic classical attacks on the surviving SSI instances are: vOW/MITM on ℓ-power paths at Õ(p^{1/4}) (with memory trade-offs), and Delfs–Galbraith Õ(p^{1/2}) via descent to F_p-curves. The "Frobenius midpoint" sweep in H-ALISO-003/004/005 — by name, sampling where a walk meets its Frobenius conjugate E^{(p)} — is a test of whether paths from E₀ (F_p-rational) to a conjugate pair admit a midpoint on the F_p-subgraph, which would turn a p^{1/2} descent into a p^{1/4}-type collision for schemes whose public curve is a *conjugate* of a reachable curve.
**Object attacked.** The security-level accounting of SQIsign/FESTA/POKE against generic attacks.
**Security delta needed.** Evidence that F_p-midpoints occur with frequency ≫ (number of F_p-curves)/(number of all curves) ≈ p^{−1/2}.
**Obstruction.** For random supersingular curves the F_p-subgraph has size O(√p); a uniform walk hits it with probability ≈ p^{−1/2}; the sweep most likely confirms this.
**Kill test.** Re-run the midpoint sweep statistic at the p's used in H-ALISO-003 and fit the hit rate against p^{−1/2}; dies if the fit holds.
**Why not a re-run.** H-ALISO-003/004/005 are scoped measurements; the lead attaches them to a specific generic-attack accounting for named survivors.
```
CHECKED: H-ALISO-003, H-ALISO-004, H-ALISO-005 (p1486_frobenius_midpoint_sweep / verify — midpoint statistics vs. Frobenius conjugates, scoped); H-WESO-516558 (walk-endpoint statistics on the same graph)
DISPROVEN: none in the brief
LEAN: no Lean coverage (nearest module SplitPrime.Obstruction, "twist purity"/"tower faithfulness", named only in a commit subject); would need "the number of supersingular j ∈ F_p is O(√p) and a uniform random supersingular j over F_{p²} is F_p-rational with probability O(p^{−1/2})"
EXP: none in the BRIEF; nearest surface is autolab package `p1486_frobenius_midpoint_sweep` (H-ALISO-003)
```

### 10. Quantum cost accounting split between commutative and non-commutative survivors `[adaptation]` (parameter audit)
**Mechanism.** Collateral-damage sorting is incomplete without the quantum column: CSIDH-type group actions survive Kani but sit under Kuperberg's subexponential hidden-shift (L_p[1/2]-type cost), whereas SQIsign/EndRing/pure SSI have only Grover-type square-root speedups on generic search. H-ALISO-012/013 ("quantum aggregate oracle probe", "quantum cost accounting verify") are the program's existing surfaces; the lead is to re-run the accounting restricted to the *post-break* survivor set and flag any scheme whose claimed quantum level relies on a torsion-based reduction that no longer holds.
**Object attacked.** Quantum security claims inherited from SIDH-era reductions.
**Security delta needed.** Identification of at least one survivor whose quantum level was argued via SSI-T (torsion-augmented) rather than SSI/EndRing.
**Obstruction.** Most current specs re-based their claims after 2022; the audit may find nothing.
**Kill test.** Table of (scheme, assumption named in spec, torsion-free?, quantum attack cited); dies if every survivor's quantum claim cites a torsion-free problem.
**Why not a re-run.** H-ALISO-012/013 are generic cost probes, not keyed to the survivor set.
```
CHECKED: H-ALISO-012 (p1486_quantum_aggregate_oracle_probe — oracle-call aggregation); H-ALISO-013 (p1486_quantum_cost_accounting_verify — cost accounting, scoped)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "a hidden-shift instance on the class group Cl(O) of size h admits Kuperberg's algorithm with 2^{O(√log h)} queries" (statement only; not a formalization target for CryptoLean as described)
EXP: none in the BRIEF; nearest surface is autolab package `p1486_quantum_cost_accounting_verify` (H-ALISO-013)
```

### 11. Formalise the scalar-only commutant lemma that every masking repair silently assumes `[speculative]` (tooling)
**Mechanism.** Leads 3–5 rest on one algebraic fact: on a supersingular E/F_{p²}, Frobenius acts on E[N] as the scalar −p, so the only "free" non-scalar lever is an explicitly known endomorphism; and the subgroup of GL₂(Z/N) preserving the Weil pairing up to a fixed character is GSp₂ = GL₂ with determinant constraint. The Lean commit `SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness` suggests adjacent machinery exists but no theorem is named in the BRIEF. Formalising "scalar-only action of π_{p²} on E[N]" and "a masking matrix M with det M ≡ 1 commuting with a non-scalar Θ lies in Z/N[Θ]" would give the LEAN line for Leads 3, 4, 5 real content.
**Object attacked.** The gap between informal masking arguments and anything machine-checked.
**Security delta needed.** None (tooling); value is turning three `no Lean coverage` lines into named theorems.
**Obstruction.** Elliptic-curve torsion as a Z/N-module with Frobenius action may not be available in the Lean library at the required generality.
**Kill test.** Attempt the statement over an abstract rank-2 free Z/N-module with a distinguished scalar endomorphism; dies only if the algebraic lemma is already in the library under another name (then cite it).
```
CHECKED: H-SSIQ-d724f2 (the H_N census is the finite-group side of the same lemma); H-ALISO-014 (auxiliary discriminant search — supplies the non-scalar Θ instances)
DISPROVEN: none in the brief
LEAN: no Lean coverage (BRIEF names only the module SplitPrime.Obstruction via commit subject); would need "(a) π_{p²} acts on E[N] as [−p] for supersingular E/F_{p²}, gcd(N,p)=1; (b) if Θ ∈ M₂(Z/N) is non-scalar modulo every prime q | N and MΘ = ΘM, then M ∈ (Z/N)[Θ]"
EXP: none; nearest surface is the aburan28/crypto-lean repository at head 8187529 (module SplitPrime.Obstruction)
```

---
