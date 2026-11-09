# Mythos ECDLP ideation — invariants (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

## LEADS

Scope note on the BRIEF as received: the hypothesis list is truncated after H-ALISO-017; no `EV-*`, `EXP-*`, or `IDEA-*` ids and no CryptoLean theorem names are quoted (only the commit subject `SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness`). Every clearing block below therefore cites only the 26 hypothesis ids that appear, writes `LEAN: no Lean coverage` with the statement needed, and writes `EXP: none; nearest surface is …`. Nothing is cited that the BRIEF does not quote.

---

**1. Weil-pairing degree/determinant leakage audit for every protocol that publishes torsion images** `[known]` — parameter audit
- Mechanism: for φ: E→E′ of degree d and P,Q a basis of E[N], e_N(φP,φQ)=e_N(P,Q)^d. Any protocol publishing (φP,φQ) or masked images (M·φP, M·φQ), M∈GL_2(Z/N), leaks d·det M mod N in one pairing (cost ≈ 2 Miller loops of length log N over F_{p²}, ~10⁴–10⁵ F_p mults for N≈2^{128}), i.e. the det-character of the level-N structure.
- Attacks: the "torsion-point images are harmless" assumption in M-SIDH/FESTA-type masking and in SQIsign2D-style auxiliary points. SIDH itself is dead (torsion-point attacks); the only repairs that survive are those where d is already public and M is restricted to a subgroup on which det is forced (diagonal with ab fixed, or det≡1).
- Delta needed: none for a break; the audit asks whether any implementation lets det M vary (then Kani-splitting via a divisor of d·det M in a split window becomes available — exactly the integer-only admissibility question of H-SSIQ-dfee7e).
- Obstruction: deployed FESTA/M-SIDH already fix det; SQIsign2D publishes d.
- Kill test: enumerate published parameter sets; if det M is fixed by spec in all, lead reduces to a one-line checklist item.
- CHECKED: H-SSIQ-d724f2 (census of level-N structure subgroups H_N ⊂ GL_2(Z/N): the pairing leak is the det character of H_N); H-SSIQ-dfee7e (admissible-divisor count of B-smooth d in the split window — the Kani follow-on once d is leaked).
- DISPROVEN: none in the brief (SIDH closure is external to the brief's ids).
- LEAN: no Lean coverage; would need `weil_pairing_isogeny_compat : ∀ (φ : E → E') (P Q : E[N]), e_N (φ P) (φ Q) = (e_N P Q) ^ (deg φ)`.
- EXP: none; nearest surface is `aburan28/crypto-lean` module `SplitPrime.Obstruction` (commit 8187529).

**2. Reduced Tate self-pairing on masked torsion: recover individual masking-scalar squares, not just the product** `[speculative]` — cryptanalytic attack
- Mechanism: on supersingular E/F_{p²} with E(F_{p²})≅(Z/(p+1))², N | p+1, the reduced Tate pairing t_N: E[N]×E[N]→μ_N is defined on all of E[N]. If the self-pairing t_N(R,R) is non-trivial of full order for generic R, and φ-compatibility t_N(φP,φP)=t_N(P,P)^{deg φ} holds (true for Weil; for Tate requires the F_{p²}-rationality bookkeeping to go through, which is the uncertain step), then a diagonal mask (a,b) leaks a²·d and b²·d mod N separately from the two self-pairings, versus only ab·d from the Weil pairing. Cost: two Miller loops.
- Attacks: FESTA/QFESTA-style masked-torsion trapdoors; also any 2D-isogeny scheme publishing scaled points.
- Delta needed: a² mod N and b² mod N for N a product of small primes gives a, b up to 2^{ω(N)} sign choices — polynomial brute force, then full torsion images → Kani recovery.
- Obstruction (likely fatal): on curves where Frobenius acts as the scalar −p (the "scalar-only action" setting of the SplitPrime.Obstruction commit), the Tate self-pairing is known to degenerate for many N; the existing weak-instance results tie non-trivial self-pairings to orientation conductors, not to generic E[N].
- Kill test: sample 10³ random E/F_{p²} with (p+1)=2^a3^b·f at toy p≈2^{60}, compute t_N(R,R) for random R∈E[N]; if the self-pairing is trivial (or in a proper subgroup of μ_N) on >99% of samples, dead.
- CHECKED: H-SSIQ-d724f2 (level-N structure group — the mask M lives in H_N; self-pairing would cut H_N further than det); H-SSIQ-dfee7e (what Kani needs after full torsion images are recovered).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `tate_self_pairing_scalar_frobenius : (π = -p on E) → N ∣ p+1 → ∀ R : E[N], t_N R R = 1` (if provable, it is the kill).
- EXP: none; nearest surface is `aburan28/crypto-lean` `SplitPrime.Obstruction` (scalar-only action lemma family).

**3. Genus-character DDH distinguisher audit for oriented class-group actions** `[known]` — security-proof gap / parameter audit
- Mechanism: for an O-oriented supersingular curve with disc(O)=D, assigned characters of Cl(O) (Kronecker symbols attached to odd prime divisors of D, plus the 2-adic ones) are computable from the curve via pairings/Tate self-pairings on small torsion, in O(log p) field ops. They reveal the class of the secret ideal [a] in Cl(O)/Cl(O)² — up to 2^{t−1} bits where t = number of prime factors of D. This breaks DDH (not CDH) whenever Cl(O) has even order.
- Attacks: decisional assumptions in CSIDH-with-p≡1 mod 4, SCALLOP/PEGASIS-type orientations with composite conductor, and any "oriented" KEM proof that assumes uniform [a] mod 2-torsion of Cl.
- Delta: a constant number of bits; zero security loss for key recovery, full loss for IND-CPA proofs relying on DDH.
- Obstruction: CSIDH p≡3 mod 8 with Z[√−p] has odd h; the leak is then empty.
- Kill test: for each deployed orientation, factor D; if every D is a prime times {1,4,8} with Cl odd, close as "audited clean".
- CHECKED: H-ICINV-82ee6a (endomorphism features from Z[π] as class invariants, ordinary toy ladder); H-ECDLP-f8101e (publicly selecting isogenous representatives by cheap invariants); H-SSIQ-d724f2 (level structure as the home of the 2-adic characters).
- DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — ordinary isogeny-class invariants at p∈{2003,4001,6007} gave nothing; this lead avoids that route by using characters of the *oriented class group*, not of the Frobenius order on ordinary curves.
- LEAN: no Lean coverage; would need `genus_character_pairing : ∀ q ∣ D, q odd prime, χ_q [a] = (t_q-pairing invariant of a⋆E)` with `χ_q` the assigned character.
- EXP: none; nearest surface is `aburan28/crypto-autoresearcher` (autolab packaging of H-ALISO-* style probes).

**4. Φ_ℓ(j,j) small-endomorphism detector on public keys** `[known]` — parameter audit
- Mechanism: E has an endomorphism of degree ℓ iff Φ_ℓ(j(E), j(E))=0. Evaluating Φ_ℓ(X,X) at one point costs O(ℓ² log p) via direct evaluation (or ~ℓ^{2+o(1)} with Sutherland-style CRT), far cheaper than finding the endomorphism. A hit gives α∈End(E) of norm ℓ, hence an embedded quadratic order Z[α] of discriminant t²−4ℓ, which is the entry point of orientation-based (Love–Boneh / small-discriminant) key recovery.
- Attacks: "public key is a random vertex" assumption in SQIsign/SQIsign2D keygen.
- Delta needed: the smallest norm of a trace-zero element in a random maximal order is ≈ p^{2/3} (count of norms ≤ B is ≈ B^{3/2}/p). So B ≈ p^{2/3} ≈ 2^{170} at p≈2^{254}: no gain. Only biased keygens (short secret walk from j=1728 or j=0) are at risk — and there the small endomorphism has norm ≈ d², detectable only if d² ≤ B.
- Obstruction: expander mixing makes biased keys negligible at spec walk lengths.
- Kill test: compute for 10³ spec-generated keys at toy p whether any ℓ ≤ 2^{20} hits; expected 0; if so, record as closed audit.
- CHECKED: H-ALISO-014 (p1243 auxiliary discriminant search — searching for small auxiliary discriminants around a target); H-ALISO-016 (geometric principalization of the found order); H-SSIQ-d724f2 (standard maximal order as the reference lattice).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `modular_poly_self_root_iff_endo : Φ_ℓ (j E) (j E) = 0 ↔ ∃ α ∈ End E, deg α = ℓ ∧ cyclic kernel`.
- EXP: none; nearest surface is the autolab package `p1243_auxiliary_discriminant_search` (H-ALISO-014).

**5. F_p-neighbor count as a distance-to-spine oracle, driving a memory-light Delfs–Galbraith/vOW** `[adaptation]` — cryptanalytic algorithm
- Mechanism: for j∈F_{p²}, the factorization pattern of Φ_ℓ(X, j) over F_{p²} vs the number of roots in F_p (and of Φ_ℓ(X,j) roots whose own Φ_ℓ-neighbors are Frobenius-fixed) is computable in O(ℓ² log p); it reveals adjacency to the F_p-spine. Combine with van Oorschot–Wiener distinguished-point walks that terminate on spine vertices (Delfs–Galbraith), using the walk-basin statistics of H-ECDLP-3550b8 to tune the distinguished density θ=1/W.
- Attacks: generic path-finding E_0→E_A; relevant to SQIsign keys only as a baseline.
- Cost: O(p^{1/2}) classical walks to reach the spine, then O(p^{1/4}) on the spine; vOW parallelisation with memory W and time p^{1/2}/√m per machine. No exponent change; the delta is memory, which is what the spec's security estimates often ignore.
- Obstruction: Frobenius-fixed midpoints along a random walk are rare (that is exactly what H-ALISO-003/004/005 measure).
- Kill test: at toy p≈2^{40}, measure whether the Φ_ℓ-neighbor oracle reduces expected steps to spine below the random-walk baseline by more than the oracle's cost; if not, close.
- CHECKED: H-ALISO-003/-004/-005 (Frobenius midpoint sweep and verifies: where Frobenius-fixed vertices appear along walks); H-ECDLP-3550b8 (basin sizes of deterministic walks with distinguishing density θ=1/W).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `spine_vertex_iff_j_in_Fp : (j E ∈ F_p) ↔ ∃ E' ≅ E defined over F_p` (standard, but absent).
- EXP: none; nearest surface is the autolab package `p1486_frobenius_midpoint_sweep` (H-ALISO-003).

**6. Expander-mixing TV-distance audit of SQIsign commitment/challenge curves, Aut-weighted** `[adaptation]` — security-proof gap
- Mechanism: a non-backtracking 2-isogeny walk of length k from E_0 has endpoint distribution with ‖μ_k − μ_∞‖_TV ≤ C·(2√2/3)^k·√(p/12)-type bound (Ramanujan), where μ_∞ is proportional to 1/|Aut(E)|. The cheap invariant: |Aut(E)|∈{2,4,6} read from j∈{0,1728}. The zero-knowledge simulator in SQIsign-type proofs samples ideals; if the implementation's commitment walk is shorter than the bound requires, a verifier can distinguish real from simulated transcripts by frequency of j=0/1728 and of short cycles. H-WESO-516558 already samples this endpoint distribution on norm-2 left ideals at tested primes.
- Attacks: HVZK proof of SQIsign variants; also the "uniform challenge" assumption in Fiat–Shamir.
- Delta needed: TV ≥ 2^{−λ} with fewer than 2^λ transcripts — only if k < log_{3/2√2}(p^{1/2}·2^λ) ≈ needs k ≳ 2·log₂p for λ=128 at p≈2^{254}; spec lengths should be checked against this.
- Obstruction: spectral bound is tight enough that spec lengths pass; the lead then becomes a documented audit.
- Kill test: reuse the H-WESO-516558 sampler at the two largest tested primes; compute empirical TV to μ_∞ vs k; extrapolate; if spec k exceeds threshold by ≥ 20%, close.
- CHECKED: H-WESO-516558 (H-S sampler: endpoint of uniformly random non-backtracking walk on norm-2 left ideals); H-ALISO-008 (Hecke Krylov probe — spectral data of the adjacency/Brandt operator); H-ALISO-009 (Hecke support cost).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `nonbacktracking_walk_tv_bound : ‖μ_k − μ_∞‖_TV ≤ (second eigenvalue / (ℓ+1))^k · √(#vertices)` for the Ramanujan graph with weights 1/|Aut|.
- EXP: none; nearest surface is the sampler behind H-WESO-516558 (repo surface not quoted in brief).

**7. Hilbert-class-polynomial collision test for hidden small-conductor orientations** `[known]` — parameter audit
- Mechanism: for discriminant D with |D| ≤ B, roots of H_D(X) mod p are the supersingular j-invariants (when p is inert in Q(√D)) carrying an O_D-orientation. Precompute roots for all |D| ≤ B (cost Õ(B^{3/2}) total via CRT/floating methods, memory Õ(B^{3/2}) j-values); membership test per public key is a hash lookup. A hit yields an orientation of conductor-free discriminant D, enabling Kuperberg-type or classical O(|D|^{1/2})-ish attacks.
- Attacks: "random public curve" assumption; complementary to Lead 4 (which looks for norm-ℓ endomorphisms rather than full CM orders).
- Delta: a random curve has an orientation by |D| ≤ B with probability ≈ B^{3/2}/p; same wall as Lead 4 — no break, only an audit that keygen does not start at or stay near CM curves.
- Obstruction: identical to Lead 4.
- Kill test: table-lookup over 10⁶ spec keys at toy scale against |D| ≤ 2^{30}; zero hits closes it.
- CHECKED: H-ALISO-014 (auxiliary discriminant search — same object, searched per target rather than tabulated); H-BINSTD-944a66 (rational-point-of-order-131 constraint in the Couveignes–Lercier construction — a class-field-theoretic constraint of the same flavour); H-ALISO-016.
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `hilbert_root_iff_oriented : H_D (j E) = 0 [mod p] ↔ ∃ ι : O_D ↪ End E primitive`.
- EXP: none; nearest surface is `p1243_auxiliary_discriminant_search` (H-ALISO-014).

**8. Multi-target j-invariant collision across many public keys** `[known]` — parameter audit
- Mechanism: with M public keys {j(E_i)} stored, a single vOW/distinguished-point tree from E_0 of size T finds a collision with some key when T·M ≈ p/12 (vertices ≈ p/12). Per-key security drops from p^{1/2} to (p/M)^{1/2}; with M=2^{30} keys this is a 15-bit loss for the weakest key. The invariant is just j∈F_{p²} as a 2log p-bit hash key.
- Attacks: "security per key equals security of the one-key game" in parameter tables.
- Obstruction: still exponential; SQIsign targets ≈ 2^{128} with margin; relevant only where margin < 15 bits.
- Kill test: compare published classical security of each parameter set against (p/12/M)^{1/2} for M=2^{30}; flag any set with margin < 16 bits.
- CHECKED: H-ECDLP-3550b8 (basin analysis of deterministic walks with density θ=1/W — the vOW engine); H-WESO-516558 (endpoint distribution of the walk tree, which fixes the collision probability per step).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `multi_target_collision_bound : E[T to hit set of size M] ≤ (p/12)/(M)` on the Aut-weighted vertex set.
- EXP: none; nearest surface is the autolab surface of H-ECDLP-3550b8 (path not quoted in brief).

**9. Fault on the independence/pairing check of decoded torsion bases in 2D verification** `[speculative]` — implementation/fault attack
- Mechanism: SQIsign2D-style verifiers decode (P,Q) and must check they generate E[N] (via e_N(P,Q) ≠ 1, or an equivalent order check) before feeding the Kani/theta 2D-isogeny with kernel ⟨(P, ψP), (Q, ψQ)⟩. If a fault or omitted check lets ⟨P,Q⟩ be a proper subgroup, the 2D kernel is non-maximal-isotropic or non-cyclic in a direction the splitting lemma does not cover; the "split window" admissibility (H-SSIQ-dfee7e) is the integer side of exactly which products are accepted, so a forger could aim for an accepted degree with a malformed kernel.
- Attacks: unforgeability of the implementation, not the scheme.
- Cost: one skipped pairing (~10⁴ F_p mults) in the verifier; attacker cost: offline search for a malformed kernel that still passes the final j-invariant comparison — unknown, possibly exponential.
- Obstruction: theta-based 2D code typically fails loudly on degenerate kernels (zero theta null-point), giving a crash not an acceptance.
- Kill test: fuzz a reference 2D verifier at toy p with dependent (P,Q) pairs under a skipped pairing check; if 0 acceptances in 10⁶ trials, close.
- CHECKED: H-SSIQ-dfee7e (which divisors of a smooth degree the split window admits — the degree side of verification); H-ALISO-017 (p1243 auxiliary lattice Kani — construction of the 2D kernels); H-ALISO-015 (four-line descent on the auxiliary).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `kani_kernel_maximal_isotropic : (⟨P,Q⟩ = E[N]) → isotropic ⟨(P,ψP),(Q,ψQ)⟩ ∧ #kernel = N²`.
- EXP: none; nearest surface is `aburan28/ecbench` (verifier timing/fault harness surface; no isogeny subject recorded).

**10. Pairing-computable class-group characters as free "aggregate oracle" bits for Kuperberg** `[adaptation]` — quantum cost accounting
- Mechanism: in the hidden-shift formulation for an oriented action, every bit of [a] mod Cl(O)² obtained classically (Lead 3) shrinks the group Kuperberg must sieve by a factor 2. Kuperberg's cost 2^{O(√log h)} is only mildly sensitive: removing t bits changes √log h to √(log h − t), i.e. negligible for t ≤ 10. The lead is the negative accounting: a bound showing no classically-computable pairing invariant can save more than O(log log h) qubits of sieve.
- Attacks: nothing — it closes a hole in cost tables that implicitly assume the full group.
- Kill test: plug the H-ALISO-013 cost-accounting model with h→h/2^t for t∈{1,…,10}; report delta; if < 1 bit of security, record as audited.
- CHECKED: H-ALISO-012 (quantum aggregate oracle probe); H-ALISO-013 (quantum cost accounting verify); H-ICINV-82ee6a (cheap order-level features).
- DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — invariants of ordinary isogeny classes did not reduce work at toy scale; this lead expects the same conclusion for the quantum side and states the bound.
- LEAN: no Lean coverage; would need `kuperberg_cost_monotone : cost(h/2^t) ≥ cost(h) · 2^{−c·t/√log h}`.
- EXP: none; nearest surface is `p1486_quantum_cost_accounting_verify` (H-ALISO-013).

**11. Level-2 structure leakage from the published Montgomery coefficient** `[speculative]` — implementation leak
- Mechanism: a j-invariant with j≠0,1728 has 6 Montgomery A-values; choosing A fixes an ordering of the three 2-torsion points, i.e. an element of GL_2(Z/2)/H_2 for the implementation's canonicalization H_2. If the published A is derived from the secret walk's last 2-isogeny (kernel point lands at (0,0)), the last step of the secret path is one of 3 instead of 3 — zero bits — unless canonicalization is skipped, in which case the last edge is revealed: a 1.58-bit leak per key, and in signatures with reused structure, the first edge of the response path.
- Attacks: no assumption; implementation hygiene.
- Kill test: read spec/reference code canonicalization; if A is deterministic in j alone, close.
- CHECKED: H-SSIQ-d724f2 (H_N ⊂ GL_2(Z/N) census — N=2 case is the 2-torsion labeling); H-ALISO-010/-011 (parity/center smoothness probes on 2-power structure in the Kani setting).
- DISPROVEN: none in the brief.
- LEAN: no Lean coverage; would need `montgomery_coeff_fiber : #{A : j(A)=j} = 6 for j∉{0,1728}` and `last_edge_from_A : kernel of last 2-isogeny = ⟨(0,0)⟩`.
- EXP: none; nearest surface is `aburan28/ecbench` (coefficient/encoding surface).
