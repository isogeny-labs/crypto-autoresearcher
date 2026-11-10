# Mythos ECDLP ideation — sqisign (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

# Preface on the delivered BRIEF

The BRIEF as delivered quotes 27 hypothesis ids (H-SSIQ-d724f2, H-SSIQ-dfee7e, H-BINSTD-944a66, H-WESO-516558, H-ECDLP-3550b8, H-ECDLP-f8101e, H-ICINV-6c7920, H-ICINV-82ee6a, H-ALISO-001…017) and one open question (KN-OPEN-095df5). It quotes **no EXP-\* or EV-\* ids**, **no Lean theorem names** (only the commit subject `SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness`), **no record schema section**, and **no SQIsign-specific hypothesis** on the signing distribution or the round‑3 response construction. I will not invent those ids. Every CHECKED line below cites the nearest filed mechanism that actually appears in the BRIEF (quaternion-order census, ideal-walk sampler distributions, Kani auxiliary-isogeny arms, smooth-integer split-window admissibility), every LEAN line says what statement is missing, and every EXP line is `none` with the nearest repository surface. The one terminal closure in the brief is H-ICINV-6c7920 [rejected_scoped] (ordinary toy-class invariants); it is cited only where a lead genuinely avoids it. The SQIsign-specific signing-distribution records the user refers to must be re-cleared when the untruncated brief is available; I flag this in each record.

Throughout: SQIsign (v1, HD, 2D-West) does not rest on SIDH. Its higher-dimensional representations use Kani's lemma *constructively*; the published torsion images belong to isogenies that are *meant* to be recoverable by the verifier, so the Castryck–Decru/Maino–Martindale/Robert attacks are the verifier's algorithm, not a break. Each lead states whether it is (a) a cryptanalytic key-recovery attack, (b) a security-proof (ZK-simulation) gap, (c) an implementation/fault attack, or (d) a parameter audit.

Notation (approximate, marked where recalled): SQIsign2D-West level I uses p = 5·2^248 − 1 (recalled); secret ideal I_sk is a left O_0-ideal with O_0 the standard maximal order of B_{p,∞} (i²=−1, j²=−p, exactly the order in H-SSIQ-d724f2); response ideal J has reduced norm q < 2^e with 2^e ≈ √p·2^s for a small slack s; the auxiliary isogeny φ_aux: E_pk → E_aux has degree 2^e − q; the signature encodes the Kani diamond (φ_rsp of degree q, φ_aux of degree 2^e − q) as a (2^e, 2^e)-isogeny Φ in dimension 2.

## LEADS

### Lead 1 — Response-norm q as a ZK-simulation distinguisher  `[adaptation]`
**Type:** security-proof gap (not key recovery).
**Mechanism.** The signer picks J as a short vector in the connecting-ideal lattice (a rank‑4 Z‑lattice, Gram matrix determined by the class of I_sk^{-1}·I_com·I_chl, with secret-dependent reduced basis). The sampler selects among lattice points of norm < 2^e via a specific procedure (reduced-basis enumeration with bounded coefficients). The simulator in the ZK proof must sample q from a secret-independent process. Leakage lives in the *procedure-induced* distribution over the candidate set, not in the class-level representation numbers (see Lead 8 for why class-level leakage is 2^{−e/2} and hence dead).
**Attacks:** the heuristic "response distribution is simulatable" step of the 2D-West ZK argument.
**Delta needed:** statistical distance between signer and simulator q-distributions ≥ N^{−1/2} for N signatures polynomial in λ.
**Obstruction:** the candidate set has ≈ 2π²·2^{2s} points (Lead 12); if the sampler is exactly uniform on it and the class is uniform, no gap exists.
**Kill test:** toy p ≈ 2^40–2^60 with the 2D-West structure; 10^6 signatures per key, 20 keys; two-sample tests on (q/2^e, q mod 2^k, number of candidate vectors tied at the chosen norm); kill if total variation vs simulator < 3·N^{−1/2} across all keys.
```
CHECKED: H-WESO-516558 (endpoint distribution of random non-backtracking norm-2 ideal walks — the filed sampler-uniformity test, here moved from the commitment walk to the response short-vector sampler); H-SSIQ-d724f2 (the same standard maximal order O of B_{p,∞}, census of GL_2 subgroups, no attack); H-SSIQ-dfee7e (integer-only admissible-divisor statistics in a split window — the arithmetic analogue of counting admissible q)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "for a fixed class [I_com·I_chl] the conditional law of Nrd(J) given (E_com, E_chl) is independent of I_sk" as a statement over left O_0-ideal classes of norm < 2^e
EXP: none; nearest surface is aburan28/cryptanalysis autolab package namespace (p1486_* / p1243_* packages referenced in H-ALISO-001…017)
```

### Lead 2 — From q-statistics to key bits: Gram-matrix inversion of the connecting lattice  `[speculative]`
**Type:** cryptanalytic key recovery conditional on Lead 1 being positive.
**Mechanism.** If the sampler's q-law depends on the reduced Gram matrix G of the connecting lattice, then many signatures with *the same commitment class* (impossible honestly; possible via Lead 4/10 faults) would let one estimate G; given G up to GL_4(Z) and the public E_pk, E_chl, enumerate ideals of the class with that Gram (≤ |Aut| · #{short vectors}) and translate.
**Delta:** recover 4 successive-minima norms to relative precision 2^{−s}.
**Obstruction:** honest signatures vary I_com every time, so G varies; the mixture over I_com classes averages G toward a secret-independent law; without commitment reuse the signal is averaged to the class-level 2^{−e/2} floor of Lead 8.
**Kill test:** toy instance; feed the estimator signatures with *fresh* commitments; if the posterior over I_sk after 10^6 signatures has entropy within 1 bit of the prior, kill.
```
CHECKED: H-ECDLP-f8101e (publicly selecting an isogenous representative via endomorphism features to shorten a search — same "endomorphism feature leaks representative" shape, ordinary setting); H-SSIQ-d724f2 (group-theoretic census of O, no attack, no exponent)
DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — ordinary toy-class invariants did not reduce effort; this lead avoids it by working in the supersingular quaternion setting where G is a genuine secret object rather than a public class invariant
LEAN: no Lean coverage; would need "the map from left O_0-ideal classes to Gram-matrix GL_4(Z)-orbits of a Minkowski-reduced basis is injective up to automorphisms" (false in general; the lemma would bound the fibre)
EXP: none; nearest surface is aburan28/cryptanalysis (autolab packages of H-ALISO-017 p1243_auxiliary_lattice_kani)
```

### Lead 3 — Rejection-count and timing leakage in response/aux selection  `[adaptation]`
**Type:** implementation side channel → partial-information leakage (not full key recovery by itself).
**Mechanism.** The signer iterates over candidate short vectors until 2^e − q is admissible for the auxiliary step (parity/representability conditions). The rejected candidates are *other* short vectors of the secret-dependent lattice; the loop count (observable via timing) therefore leaks the ordering/admissibility pattern of the secret lattice's short norms, ≈ log₂(2π²·2^{2s}) bits per signature at most, in practice ~1–2 bits.
**Delta:** needs an attack that consumes partial lattice information (Lead 9).
**Obstruction:** constant-time enumeration over a fixed-size candidate list removes the channel at cost ×2^{2s} in that sub-step.
**Kill test:** instrument toy signer; mutual information between loop count and (I_sk-dependent) Gram entries over 10^5 signatures; kill if MI < 0.01 bit/signature.
```
CHECKED: H-SSIQ-dfee7e (count k(d) of admissible divisors of a B-smooth d in a split window — the admissibility-count statistic is the same object as the rejection count here); H-ALISO-010 and H-ALISO-011 (p1486 parity-center smoothness probe/verify — parity/smoothness admissibility measurements in the Kani setting)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "the number of candidate q with 2^e − q admissible, over lattice points of norm < 2^e, is a function of the class and the basis order"
EXP: none; nearest surface is aburan28/ecbench (timing harness repository, no isogeny subject in recent commits)
```

### Lead 4 — Commitment-randomness fault ⇒ one endomorphism ⇒ End(E_pk)  `[adaptation]`
**Type:** implementation/fault attack with full key recovery; the finishing step is a known reduction (external literature, recalled, not in brief).
**Mechanism.** 2D-West derives commitment randomness deterministically from (sk, msg). A fault (glitch the domain-separator byte or the message hash input) that makes two different messages share the commitment yields signatures with E_com equal and challenges c₁ ≠ c₂. Then α = φ̂_rsp,2 ∘ φ_chl,2 ∘ φ̂_chl,1 ∘ φ_rsp,1 ∈ End(E_pk), deg α = q₁q₂·2^{2e_chl}, non-scalar since c₁ ≠ c₂. One non-scalar endomorphism → End(E_pk) in heuristic polynomial time (Page–Wesolowski-style One-Endomorphism ⇒ EndRing reduction; recalled, not in brief), then I_sk by connecting-ideal computation — equivalently the secret key.
**Cost:** 2 faulted signatures (or 1 faulted + 1 honest on the same message, see Lead 10), plus one factorization of deg α (q_i ≈ 2^{e} ≈ 2^{126}: generic factoring of a 250-bit integer is feasible) and the heuristic-poly finishing.
**Obstruction:** standard countermeasure (verify-before-output does *not* help — both signatures are valid); needs hedged randomness (sk‖msg‖fresh nonce).
**Kill test:** toy implementation with fault injected in the PRF input; check α non-scalar and that the order Z[α] saturates to End(E_pk) in the toy; kill if the implementation already mixes fresh randomness.
```
CHECKED: H-WESO-516558 (commitment-walk endpoint distribution — the object whose collision is exploited here); H-SSIQ-d724f2 (standard maximal order O used for the End(E_pk) saturation target)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "two accepting transcripts (E_com, c₁, rsp₁), (E_com, c₂, rsp₂) with c₁ ≠ c₂ determine a non-scalar endomorphism of E_pk of degree q₁q₂·2^{2e_chl}" (the special-soundness extractor as a formal lemma)
EXP: none; nearest surface is aburan28/cryptanalysis (fault-injection harness would be a new autolab package alongside p1486_*/p1243_*)
```

### Lead 5 — Fault in ideal-to-isogeny translation of the auxiliary ideal leaks secret-path intermediates  `[speculative]`
**Type:** implementation/fault attack, potential key recovery.
**Mechanism.** The only secret-bearing computations in 2D-West signing are the ideal arithmetic and the translation of left O_pk-ideals to isogenies, which is done by pulling back through I_sk to O_0 (where End is known) and pushing forward along the secret path E_0 → E_pk. A fault that truncates the push-forward at an intermediate curve E_t of the secret path outputs a faulty E'_aux that is 2^e−q-isogenous to E_t rather than to E_pk. Each such faulty signature then places a public curve at known degree from a secret intermediate; with a fault at each of the k steps of the secret path (k ≈ length of the E_0→E_pk chain) the path is recovered step by step, each step costing a search over the ≈ ℓ+1 neighbours of the previous recovered curve plus a degree-(2^e−q) isogeny existence check (itself hard in general, but the attacker also receives the faulty torsion images, which pin φ'_aux by Kani in dimension 2 since 2^e > 2^e − q).
**Delta:** k faults, each with position control to within one step.
**Obstruction:** if the implementation re-derives E_aux from the final isogeny and verifies the Kani diamond before output, faulty signatures are suppressed; also the hypothesis that a truncated push-forward yields a *valid-looking* codomain is unverified.
**Kill test:** toy signer; inject step-truncation faults in the push-forward; check whether faulty E'_aux is (2^e−q)-isogenous to the true E_t (decidable at toy size by exhaustive class enumeration); kill if the faulty output never lands on the path.
```
CHECKED: H-ALISO-014, H-ALISO-015, H-ALISO-016 (p1243 auxiliary discriminant search / four-line descent / geometric principalization — the filed arms that study the auxiliary-isogeny construction in the Kani setting); H-ALISO-017 (p1243_auxiliary_lattice_kani — lattice side of the same auxiliary object)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "a (2^e,2^e)-isogeny with kernel {(φ_chl(P), φ_aux(P))} has codomain E_pk × E' iff deg φ_aux = 2^e − deg φ_rsp with the given torsion images" (Kani diamond well-formedness as a decidable check)
EXP: none; nearest surface is aburan28/cryptanalysis (p1243 auxiliary packages per H-ALISO-014…017)
```

### Lead 6 — Commitment-class entropy audit (birthday to Lead 4 without faults)  `[adaptation]`
**Type:** parameter audit / proof-gap.
**Mechanism.** Two honest signatures with equal E_com yield the Lead‑4 endomorphism with zero faults. Security therefore needs min-entropy of the commitment *class* ≥ 2λ bits across all signatures of a key. The commitment ideal is sampled by drawing an element of bounded coefficients in O_0 and taking the ideal it generates together with a norm; element-box sampling induces a non-uniform class law whose collision probability exceeds 12/p when the box is small relative to √p·N.
**Quantitative:** need collision probability ≤ 2^{−2λ}; the class number is ≈ p/12 ≈ 2^{2λ−3.6} at level I, so even perfectly uniform sampling has only ~3.6 bits of margin below the 2λ target — any sampler non-uniformity of factor 12 eats it.
**Obstruction:** the 2D-West commitment sampler is designed to be near-uniform; the audit may simply confirm it.
**Kill test:** toy p; enumerate all classes; run the sampler 10^7 times; compute collision probability vs 12/p and the χ² against uniform; kill if within 1.1× of uniform.
```
CHECKED: H-WESO-516558 (H-S SAMPLER part — uniformity of random non-backtracking norm-2 walk endpoints; this lead replaces the walk by the bounded-box element sampler and asks the same question); H-SSIQ-d724f2 (census of the same order, no attack)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "the pushforward of the uniform law on elements of O_0 with coefficients in a box B to left-ideal classes has collision probability ≤ c·12/p when vol(B) ≥ c'·p²" (a quaternion equidistribution bound)
EXP: none; nearest surface is aburan28/crypto-autoresearcher (shared pcc files per the cryptanalysis "Shared-code lock" commit)
```

### Lead 7 — Auxiliary-isogeny sampler (FixedDegreeIsogeny over O_pk) uniformity  `[adaptation]`
**Type:** security-proof gap (the aux side of the ZK simulation).
**Mechanism.** The ZK simulator must produce E_aux distributed as the codomain of a uniformly random isogeny of degree d = 2^e − q from E_pk, among the ≈ d·∏_{ℓ|d}(1+1/ℓ) such isogenies. The signer instead computes φ_aux by solving a norm equation in O_pk (via the secret I_sk) with a KLPT-style solver, whose output is known in the v1 KLPT setting to be concentrated on a small sub-family. If the 2D-West solver inherits this, E_aux is a distinguisher independent of q. Unlike v1 (where the response itself was the KLPT output), the gap here sits entirely in φ_aux, which is public and recoverable by the verifier — so it is a *simulation* gap, not a torsion-point attack: the published torsion images are of the aux isogeny the verifier is supposed to reconstruct; there is no SIDH-type secret smooth isogeny with published images.
**Kill test:** toy p where all ideals of norm d from O_pk can be enumerated; 10^6 runs of the solver per (E_pk, d); χ² over codomain classes; kill if p-value > 0.01 across 20 keys.
```
CHECKED: H-ALISO-014 (p1243 auxiliary discriminant search — searching auxiliary discriminants for the Kani construction, the same norm-equation object); H-ALISO-016 (p1243 auxiliary geometric principalization — principalizing the auxiliary ideal, i.e., the translation this lead measures); H-SSIQ-dfee7e (integer-only admissibility of split-window divisors, the Arm I analogue of "which d are representable")
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "for d coprime to p and a maximal order O_pk, the set of left O_pk-ideals of norm d has cardinality d·∏_{ℓ|d}(1+1/ℓ) and the solver's output law is the uniform law on it" (the second clause is the heuristic to be formalized or refuted)
EXP: none; nearest surface is aburan28/cryptanalysis (p1243_auxiliary_* packages)
```

### Lead 8 — Siegel–Weil floor: class-level q leakage is 2^{−e/2}  `[adaptation]` (a closure candidate for Leads 1–2)
**Type:** proof-gap analysis (negative result / bound).
**Mechanism.** All left O_0-ideals in the same genus share the Eisenstein (genus-average) representation numbers; the class-level deviation of r_J(n) from the genus average is a cusp-form coefficient of size O(n^{1/2+ε}) against a main term ≍ n. Hence any q-statistic that depends only on *which ideals of norm q exist in the class* deviates from the simulator by relative ≈ q^{−1/2} ≈ 2^{−e/2} ≈ 2^{−63} at level I — undetectable with polynomially many signatures. Consequence: the only viable leakage is *procedural* (which candidate the sampler picks), confirming the scope of Lead 1 and killing the "representation-number fingerprint" version of Lead 2.
**Kill test:** at toy p, compute r_J(n) for all classes J and n < 2^e; verify max deviation ≤ C·n^{1/2+ε}; if a class shows deviation ≫ √n for a positive-density set of n (e.g., due to a nontrivial automorphism group), the floor is wrong for that class and Lead 2 revives for keys with extra automorphisms.
```
CHECKED: H-SSIQ-d724f2 (heuristic census of subgroups H_N ≤ GL_2 for the standard O — the genus/level structure this bound lives on); H-SSIQ-dfee7e (integer-only divisor statistics, Arm I)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "representation numbers of the norm form of a left O_0-ideal differ from the genus average by O(n^{1/2+ε})" — a modular-forms statement far outside current CryptoLean scope; a weaker formalizable surrogate is "genus of Nrd|_J depends only on O_0 and N(J)"
EXP: none; nearest surface is aburan28/crypto-lean (SplitPrime.Obstruction namespace, commit subject only)
```

### Lead 9 — Key recovery from partial reduced-basis information (small-root norm equation)  `[speculative]`
**Type:** cryptanalytic finishing step for partial leakage (consumes Leads 3/2 output).
**Mechanism.** I_sk = O_0·b + O_0·N for any b ∈ I_sk with gcd(Nrd(b), N²) = N, N = N(I_sk). A Minkowski-reduced basis vector b has coefficients of size ≈ (N√p)^{1/2} each (four coordinates in the basis 1, i, j, ij of O_0, covolume ≍ N²p). If the leakage gives the top t bits of each coordinate, the unknowns are four integers of size 2^{(log₂(N√p))/2 − t}, constrained by the quadratic Nrd(b) ≡ 0 mod N — a 4-variable modular small-root problem. Heuristic Coppersmith-style feasibility when total unknown bits u < (log₂ N)·(1 − δ) for a degree-2 form; with N ≈ 2^{λ…2λ} and total coordinate bits ≈ 2(log₂N + ½log₂p), one needs t ≳ ¼ to ½ of each coordinate.
**Obstruction:** no side channel in Leads 3/6 plausibly leaks a quarter of each coordinate; the lead is a *threshold measurement*, not an attack.
**Kill test:** toy N, p; plant partial-coordinate leakage at fraction t; run lattice small-root solver; report minimal t for success at ≥ 50%; if t_min > 0.6, mark the partial-info route closed for timing-class leakage.
```
CHECKED: H-ALISO-017 (p1243_auxiliary_lattice_kani — lattice-side auxiliary computation in O); H-ECDLP-3550b8 (basin-size analysis of deterministic walks with a distinguishing predicate — the only filed "partial-information search cost" model, ordinary setting; cited for its cost-accounting shape, not its object)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "if b ∈ I_sk with Nrd(b) = N·m, gcd(m, N) = 1, then I_sk = O_0 b + O_0 N" (ideal generation from one element and the norm — elementary and formalizable)
EXP: none; nearest surface is aburan28/cryptanalysis (p1243_auxiliary_lattice_kani per H-ALISO-017)
```

### Lead 10 — Single-fault differential on deterministic signing via the challenge hash  `[adaptation]`
**Type:** implementation/fault attack, key recovery; sharpens Lead 4 to one fault.
**Mechanism.** Deterministic commitment means signing the same message twice produces the same E_com honestly. Fault the *challenge-hash* evaluation on the second run (one instruction skip or bit flip in the hash input buffer) so the signer answers challenge c' ≠ c for the same E_com. The attacker holds the honest (E_com, c, rsp) and the faulty (E_com, c', rsp'). If the faulty output determines E_chl' (the response's target), then φ_chl': E_com → E_chl' is a 2^{e_chl}-isogeny with unknown kernel: recover it by meet-in-the-middle in time ≈ 2^{e_chl/2}, or for free if the signature's challenge hint pins the kernel. Then Lead 4's α and finishing apply.
**Cost:** 1 fault + 2^{e_chl/2} MITM worst case; at e_chl ≈ λ this is 2^{λ/2} — marginal at level I, feasible at toy and possibly at level I with memory 2^{λ/2}.
**Obstruction:** if the signer re-derives c from the output and aborts on mismatch (verify-before-output on the challenge only — cheap), the attack is blocked.
**Kill test:** toy signer; fault the hash; check E_chl' determinability from output; measure MITM cost; kill if the implementation includes a challenge re-derivation check.
```
CHECKED: H-WESO-516558 (commitment-endpoint object reused across two transcripts); H-ALISO-012, H-ALISO-013 (p1486 quantum aggregate oracle probe / quantum cost accounting — the only filed cost-accounting arms; cited to distinguish this classical 2^{e_chl/2} MITM from their quantum accounting)
DISPROVEN: none in the brief
LEAN: no Lean coverage; same missing extractor statement as Lead 4, plus "a 2^{e_chl}-isogeny between given E_com, E_chl' is unique up to automorphism when 2^{e_chl} < √p/2" (uniqueness of short connecting isogenies)
EXP: none; nearest surface is aburan28/ecbench (timing/fault harness, no isogeny commits)
```

### Lead 11 — Formalize the extractor and the class-independence lemma in CryptoLean  `[adaptation]`
**Type:** tooling for the proof-gap / key-recovery distinction.
**Mechanism.** Two statements separate "ZK gap" from "key recovery" cleanly: (S1) special soundness — equal commitment, distinct challenges ⇒ non-scalar endomorphism of E_pk of degree q₁q₂2^{2e_chl} (every fault lead above terminates in S1); (S2) class-independence — the class of J = I_sk^{-1}·I_com·I_chl's reduced representative depends on I_sk only through [I_sk], and for uniform [I_com] the law of [J] is independent of I_sk. S2 is the *exact* part of the ZK proof; the *heuristic* part is the sampler-uniformity assumption of Leads 1 and 7. Formalizing S1/S2 pins down precisely which residual claims are heuristic.
**Obstruction:** CryptoLean currently has only `SplitPrime.Obstruction` (commit subject: scalar-only action, twist purity, tower faithfulness) on the isogeny side — no quaternion-order or ideal-class infrastructure is quoted in the brief.
**Kill test:** none (tooling); acceptance is a compiling lemma for S1 over an abstract isogeny-graph structure with degree multiplicativity.
```
CHECKED: H-SSIQ-d724f2 (standard maximal order O with i²=−1, j²=−p — the concrete order S2 would be stated over); H-ALISO-001…009 (p1486 Hecke/Frobenius-midpoint probes — the filed supersingular measurement arms whose outputs would be the formal lemma's test cases)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need S1 "transcripts (E_com,c₁,rsp₁),(E_com,c₂,rsp₂), c₁≠c₂ ⇒ ∃ α ∈ End(E_pk) non-scalar, deg α = q₁q₂·2^{2e_chl}" and S2 "law of [I_sk^{-1}·I_com·I_chl] for uniform [I_com] is independent of I_sk" (nearest module: SplitPrime.Obstruction, commit subject only, no theorem name quoted)
EXP: none; nearest surface is aburan28/crypto-lean
```

### Lead 12 — Slack-parameter audit: candidate-response count ≈ 2π²·2^{2s}  `[adaptation]`
**Type:** parameter audit.
**Mechanism.** The number of lattice points of norm < 2^e in the connecting lattice (rank 4, covolume ∝ p after normalization) is ≈ (π²/2)·2^{2e}/covol ≈ 2π²·2^{2s} when 2^e = √p·2^s. If s is small (s ≈ 1–3), each class offers only ~20–1300 candidate responses; the sampler's choice among them is the *entire* leakage surface of Lead 1, and the simulator's job reduces to matching a small discrete law. Also audit the failure probability that *no* candidate has admissible 2^e − q (Lead 3), which forces re-commitment and leaks via Lead 3's timing channel.
**Kill test:** at toy p with s ∈ {1,…,6}, count candidates per class exactly; fit to 2π²·2^{2s}; report the distribution of counts (variance across classes is itself a leakage proxy); kill the audit if variance/mean² < 2^{−λ/4} (then procedural leakage is negligible).
```
CHECKED: H-SSIQ-dfee7e (count k(d) of admissible divisors in the split window [ceil(d/X), X] — the direct integer analogue of the candidate-count statistic); H-SSIQ-d724f2 (same order O); H-ALISO-006, H-ALISO-007 (p1486 Hecke degree-pair support probe/verify — support counts of degree pairs in the Kani setting)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need "the number of elements of a rank-4 lattice of covolume V in a ball of radius R is (π²/2)R⁴/V + O(R³/V^{3/4})" (Gauss-circle-type bound in dimension 4)
EXP: none; nearest surface is aburan28/cryptanalysis (p1486_hecke_degree_pair_support_* per H-ALISO-006/007)
```

---
