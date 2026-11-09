# Mythos ECDLP ideation — higher-dim (20261109)

Repository brief: `cryptanalysis/ecdlp-ideas/repo-brief.md` at the commits named in it. Records filed: see the `IDEA-*` ids in this PR.

# Isogeny lane — higher-dimensional and theta isogenies as a cryptanalytic tool

Preliminary note on what the BRIEF actually lets me cite. The excerpt supplied contains hypothesis ids H-SSIQ-d724f2, H-SSIQ-dfee7e, H-BINSTD-944a66, H-WESO-516558, H-ECDLP-3550b8, H-ECDLP-f8101e, H-ICINV-6c7920 (rejected_scoped), H-ICINV-82ee6a, H-ALISO-001 … H-ALISO-017, and the open question KN-OPEN-095df5. It names one Lean commit (`SplitPrime.Obstruction: scalar-only action, twist purity, tower faithfulness`) but quotes **no theorem names**, and it lists **no EXP-\*, EV-\* or IDEA-\* ids**. The record schema section is not in the excerpt. I therefore (a) cite only the ids above, (b) write every LEAN line as `no Lean coverage` with the statement that would need formalizing, (c) write every EXP line as `none` with the nearest Autolab package surface named in the BRIEF, and (d) build the five records from the fields mandated by the clearing-block contract. Nothing below is a break; every lead is a proposal with a kill test.

Shorthand used throughout: dimension-2 (2,2)-isogeny between principally polarised abelian surfaces; coordinate models are **level-2 theta** (4 projective coordinates, theta null point `(a:b:c:d)`), **Richelot/Mumford** (genus-2 Jacobian, Rosenhain or sextic model), or **Kummer**. "Kani" means the reducibility criterion: for an (N,N)-isogeny diagram with N = d1 + d2 and d1, d2 coprime, the kernel `{(P, ψ(P))}` on E1 × E2 yields a codomain that splits as a product iff the diagram is a Kani square.

---

## LEADS

### 1. Degree-first Kani chain in theta, dimension 2: cost model for the attack half of SQIsign2D-style verification
**Mechanism.** Given a secret isogeny φ: E0 → E1 of degree N with known images on 2^e-torsion and 2^e = N + a² + b² (or N + u with u a small norm), build the (2^e,2^e)-isogeny from E0 × E1 with kernel `{(a·P + b·ι(P) … , φ(P))}` in level-2 theta coordinates and walk e steps of (2,2). Each step: codomain theta null from 8-torsion lift (≈ 8 squarings + a handful of multiplications and one batched inversion per step, heuristic figure recalled from the theta-isogeny literature, not measured here), point pushes ≈ 4S + 4M each.
**Object attacked.** Not the scheme — the *cost calibration* of the Kani step used inside verification of SQIsign2D-type signatures (dimension 2, field F_{p²}, p ≈ 2^248·f − 1 at NIST-I scale, chain length e ≈ 250).
**Delta needed.** A verified constant-factor table (theta vs Richelot) so that any later "attack cost" claim about Kani-based schemes rests on measured, not recalled, per-step arithmetic.
**Obstruction.** The program's Kani packages (H-ALISO-001 … 017) measure Hecke/degree statistics, not per-step theta arithmetic; there is no filed cost ledger.
**Kill test.** Implement one (2,2) step in both models over F_{p²} for p of SQIsign2D-West shape; if theta is not ≥ 3× cheaper than Richelot at e ≈ 250, the "theta makes dimension-2 attacks cheap" framing is dropped.
**Tag.** [known] (algorithm) / [adaptation] (as a calibration deliverable).

```
CHECKED: H-ALISO-001 (degree-first Hecke probe — same degree-first ordering, no theta cost); H-ALISO-009 (hecke_support_cost_probe — a cost probe, but of Hecke support, not of (2,2) steps); H-ALISO-017 (auxiliary_lattice_kani — same a²+b² auxiliary search)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for a (2,2)-isogeny with kernel K ⊂ A[2] maximal isotropic, the level-2 theta null point of A/K is determined up to the action of the 8-torsion lift choice, and all such choices give isomorphic polarised codomains"
EXP: none; nearest surface is Autolab package `p1486_hecke_support_cost_probe` (H-ALISO-009), repository not specified in the BRIEF
```

### 2. Splitting-detection as a decision oracle: one vanishing even theta constant
**Mechanism.** At the last (2,2) step of a Kani chain, the codomain is a product E' × E'' iff exactly one of the 10 even theta constants of the genus-2 surface vanishes (equivalently, in Richelot form, the quadratic splitting degenerates). This gives a one-field-element test deciding "degree guess N is right" vs wrong. Cryptanalytic use: when the attacker does *not* know deg φ exactly (as in M-SIDH / masked-torsion variants), iterate candidate N and use the oracle; cost per candidate = one chain of e steps.
**Object attacked.** Masked-torsion SIDH repairs (M-SIDH: scalar-masked torsion images). SIDH itself is dead; this lead only concerns repairs that hide the degree or the scalar.
**Delta needed.** Number of candidates ≪ 2^λ. For M-SIDH with mask α ∈ (Z/2^e)^× the oracle alone gives nothing new (the mask space is the problem, not the degree); it only pays off combined with lead 3.
**Obstruction.** Oracle is binary; without a structured candidate set it is a brute force.
**Kill test.** On toy M-SIDH parameters (p ≈ 2^60), measure whether the vanishing-theta oracle plus Weil-pairing mask-square recovery reduces candidate count below the plain search; if not, close.
**Tag.** [known] (oracle) / [adaptation] (use as degree decider).

```
CHECKED: H-ALISO-002 (degree_first_hecke_verify — degree-first guessing already filed); H-ALISO-015 (auxiliary_four_line_descent — descent over candidate auxiliaries, same iterate-and-test shape)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "a principally polarised abelian surface over a field of characteristic ≠ 2 is a product of elliptic curves with product polarisation iff some even theta constant of level 2 vanishes"
EXP: none; nearest surface is Autolab package `p1486_degree_first_hecke_verify` (H-ALISO-002)
```

### 3. Parameter audit of masked-torsion repairs: Weil-pairing recovery of α² then dimension-2 glue
**Mechanism.** In M-SIDH, images are α·φ(P), α·φ(Q) with α secret; the Weil pairing e(αφ(P), αφ(Q)) = e(P,Q)^{α²·deg φ} reveals α² mod 2^e, i.e. α up to the 2^{t} square-root ambiguity of (Z/2^e)^×, where t is the number of distinct prime factors of the torsion order. The repair's security is exactly the claim that the remaining ambiguity is exponential. Dimension-2 Kani then needs only one correct lift. Audit: for each proposed parameter set, compute t and the number of lifts, and check published reductions that exploit special-form p (recalled: Castryck–Vercauteren-type attacks on instances with p of restricted shape — treated here as recalled, not verified).
**Object attacked.** Parameter choices of M-SIDH / MD-SIDH-style schemes, not the generic problem.
**Delta needed.** Lift count below 2^λ for some proposed set, or a structural reason the lift count is smaller than 2^t.
**Obstruction.** For generic p with t ≥ λ distinct small primes the lift set is genuinely 2^t; the audit is only interesting where p has few prime factors or where additional torsion is exposed.
**Kill test.** Tabulate t for every published M-SIDH parameter set; if min 2^t ≥ 2^λ everywhere and no exposed extra torsion, file as `parameter audit: clean`.
**Tag.** [known].

```
CHECKED: H-ALISO-006 (hecke_degree_pair_support_probe — degree-pair support, the same "which (deg, scalar) pairs are consistent with the torsion data" question); H-ALISO-007 (its verify twin)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for φ: E→E' of degree N and α ∈ (Z/MZ)^×, e_M(αφ(P), αφ(Q)) = e_M(P,Q)^{α² N} for all P,Q ∈ E[M]"
EXP: none; nearest surface is Autolab package `p1486_hecke_degree_pair_support_probe` (H-ALISO-006)
```

### 4. Dimension 8 → 4 → 2 via sum-of-squares structure: audit of which auxiliary degrees a scheme exposes
**Mechanism.** Robert's generic reduction needs dimension 8 (four-square Lagrange); if 2^e − N is a sum of two squares the attack runs in dimension 4 (Zarhin), and if an auxiliary endomorphism ι with ι² = −1 or −3 is available on E0 it runs in dimension 2 with a + bι. Audit any scheme (FESTA-, POKE-, QFESTA-like, SQIsign2D auxiliary curves) for whether the *attacker* can choose or influence the auxiliary degree so that 2^e − N lands in the dimension-2 or dimension-4 regime, lowering the cost from dimension 8 (≈ 2^8-coordinate theta null, per step cost ~ hundreds of multiplications) to dimension 2.
**Object attacked.** Cost assumptions in security arguments that quote "dimension 8 generic" rather than the dimension actually reachable.
**Delta needed.** A scheme-controlled degree where the attacker's freedom moves it from d=8 to d≤4; this is a cost exponent change only in the constant/polynomial factor, not in the exponent of λ — so it is an audit, not an attack.
**Obstruction.** In honest designs the secret degree is fixed by the prover; the attacker rarely controls 2^e − N.
**Kill test.** For each scheme, write the set of degrees the adversary can force; if it never intersects {sums of two squares} with non-negligible density beyond what the scheme already assumes, close.
**Tag.** [known].

```
CHECKED: H-ALISO-014 (auxiliary_discriminant_search — searches auxiliary discriminants, i.e. which ι is available); H-ALISO-017 (auxiliary_lattice_kani — the a²+b² lattice search)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "if N + a² + b² = 2^e with gcd(N, 2)=1 and φ of degree N, then the kernel {( [a]P + [b]ι(P), φ(P) ) : P ∈ E0[2^e]} is maximal isotropic for the product polarisation on E0 × E1"
EXP: none; nearest surface is Autolab package `p1243_auxiliary_lattice_kani` (H-ALISO-017)
```

### 5. 8-torsion lift ambiguity in theta gluing: malformed-signature acceptance test (implementation attack)
**Mechanism.** Computing the (2,2)-codomain theta null from a kernel K ⊂ A[2] in level 2 requires points of A[8] above K to fix signs (a "change of theta coordinates" step). Different lifts give isomorphic polarised codomains but *different* theta coordinates on pushed points. In a verifier that recomputes a Kani chain from signature-supplied 8-torsion data, a signature whose 8-torsion points are inconsistent (not above the stated kernel, or of wrong order) may still produce a chain that terminates on a product, with the final E-components permuted or twisted.
**Object attacked.** Verification soundness as implemented, not the hardness assumption.
**Delta needed.** A single accepted malformed signature. Cost of the search: for each of ≤ e steps, ≤ 2^4 sign choices — trivially enumerable.
**Obstruction.** Correct implementations check order and Weil-pairing compatibility of the supplied torsion; the lead targets implementations that skip these checks.
**Kill test.** Fuzz a reference theta-based verifier with 8-torsion points of order 4 or wrong pairing; if every malformed input is rejected before the chain, close.
**Tag.** [adaptation].

```
CHECKED: H-ALISO-016 (auxiliary_geometric_principalization — touches codomain identification after a Kani chain, closest filed object); H-WESO-516558 (walk endpoint distribution on norm-2 ideals — the only filed record on endpoint identification of 2-power walks)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for K maximal isotropic in A[2] and two lifts K', K'' ⊂ A[8] with 4·K' = 4·K'' = K, the induced level-2 theta structures on A/K differ by an element of the finite theta group acting by signs and permutation"
EXP: none; nearest surface is Autolab package `p1243_auxiliary_geometric_principalization` (H-ALISO-016)
```

### 6. Fault on the theta null point: skip-one-step and zero-coordinate faults in a (2,2) chain
**Mechanism.** A level-2 theta null `(a:b:c:d)` with one coordinate forced to zero lies on the locus of products (lead 2). A fault that zeroes one coordinate mid-chain converts a Jacobian step into a "product" step; the chain still runs and the final splitting check can pass with a wrong E-component. Alternatively, skipping one doubling in the kernel-generator scalar multiplication shifts the kernel by a 2-torsion point and produces a different but valid-looking codomain.
**Object attacked.** Signing or verification implementations (dimension 2, theta model, chain length e).
**Delta needed.** One fault location whose output leaks a bit of the response isogeny kernel (for signing) or forces acceptance (for verification).
**Obstruction.** Signing in SQIsign2D-type schemes is randomised per signature; a single-fault DFA needs repeatable intermediate state.
**Kill test.** Simulate the two fault models on a toy chain (p ≈ 2^40); if faulty outputs are always detected by the final product-splitting check plus a pairing check, close.
**Tag.** [adaptation].

```
CHECKED: H-ALISO-010 (parity_center_smoothness_probe — only filed record probing a "center" invariant along a chain; nearest to a mid-chain state); H-ALISO-011 (its verify twin)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "a level-2 theta null point with exactly one zero coordinate is the theta null of a product of two elliptic curves with product polarisation"
EXP: none; nearest surface is Autolab package `p1486_parity_center_smoothness_probe` (H-ALISO-010)
```

### 7. Hecke degree-pair statistics of exposed auxiliary curves in dimension-2 signatures (distinguisher, not break)
**Mechanism.** SQIsign2D-style signatures expose an auxiliary curve E_aux and the degrees (q, 2^e − q) of the two legs of the Kani square. Over many signatures from one key, the empirical distribution of (q, E_aux) is a sample from a Hecke correspondence of degree q on the supersingular graph starting near the public key. Test whether this distribution is distinguishable from the uniform-walk endpoint distribution the proof models.
**Object attacked.** The security-proof idealisation ("auxiliary curve is a random curve"), i.e. a proof-gap record, not an attack.
**Delta needed.** Statistical distance > 1/poly between the real and modelled distribution at toy scale, growing with the number of signatures.
**Obstruction.** H-ALISO-006/007/008 already measured Hecke degree-pair supports at p ≈ 1486-scale primes and found (per their "analyzed" status) nothing filed as a distinguisher; the new element here is per-key conditioning rather than global support.
**Kill test.** At p ≈ 2^30, generate 10^5 signatures from one key and 10^5 from another; if a two-sample test on (q, j(E_aux)) does not separate keys at p < 10^{-3}, close.
**Tag.** [adaptation].

```
CHECKED: H-ALISO-006 (hecke_degree_pair_support_probe — degree-pair support measured); H-ALISO-008 (hecke_krylov_probe — Hecke spectral data); H-WESO-516558 (sampler part: endpoint distribution of norm-2 walks, the uniformity baseline)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "the Hecke operator T_q on the supersingular graph has all non-trivial eigenvalues bounded by 2√q (Ramanujan), so k-step walks mix to within (2√q/(q+1))^k of uniform"
EXP: none; nearest surface is Autolab package `p1486_hecke_krylov_probe` (H-ALISO-008)
```

### 8. Richelot-only distinguisher: the quadratic splitting carries a square-root sign bit absent in theta
**Mechanism.** A Richelot (2,2) step from a genus-2 Jacobian in sextic model requires choosing the quadratic splitting {G1, G2, G3}; the Richelot operator δ = det(G_i, G_j) must be inverted, and when the kernel is given only as a Galois-stable set the step needs a square root in F_{p²}. Theta needs none. An implementation that uses Richelot for signing and theta for verification (or vice versa) introduces a field-sqrt in signing whose branch is secret-dependent — a timing/branch side channel on the kernel.
**Object attacked.** Implementation constant-time property, not the assumption.
**Delta needed.** Non-constant-time sqrt with branch depending on kernel bits; standard Tonelli–Shanks variants on F_{p²} with p ≡ 3 mod 4 are constant-time if written so, so the lead lives or dies on the code.
**Obstruction.** Most modern code uses theta throughout; Richelot survives mainly in research code.
**Kill test.** Audit the reference implementations named in the repositories for any Richelot step on a secret-dependent path; if none, close as "no surface".
**Tag.** [speculative].

```
CHECKED: H-ALISO-003 (frobenius_midpoint_sweep — only filed record that sweeps a mid-chain Frobenius/Galois condition on supersingular data, nearest to the Galois-stable-kernel requirement); H-ALISO-005 (frobenius_midpoint_verify)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "a Richelot (2,2)-isogeny from a Jacobian with sextic model f = G1·G2·G3 has codomain with model δ^{-1}·(G2'G3' … ) where δ = det of the coefficient matrix, and is defined over the field of definition of the unordered splitting"
EXP: none; nearest surface is Autolab package `p1486_frobenius_midpoint_sweep` (H-ALISO-003)
```

### 9. Dimension-2 Kani from non-maximal auxiliary orders: widening the solvable degree set
**Mechanism.** H-ALISO-014 searches auxiliary discriminants from the maximal order of E0 (ι² = −1, −3). Allow ι from an order of conductor f (ι² = −f² or −3f², degree f² or 3f² endomorphism) so that 2^e − N = a² + f²b² has solutions for more N (binary quadratic forms of discriminant −4f²). Cost: one extra endomorphism evaluation of degree f² per kernel generator; needs E0 with that endomorphism, i.e. a special starting curve.
**Object attacked.** The "attacker needs 2^e − N to be a sum of two squares" gap in dimension-2 reductions; this enlarges the attacker's dimension-2 regime for schemes using special E0.
**Delta needed.** Density of representable N by Σ over f ≤ F forms vs. by x²+y² alone; this grows slowly (log-factor), so the delta is a polynomial factor only.
**Obstruction.** Non-maximal orders on supersingular E0 mean ι is an endomorphism of a non-maximal suborder; it still exists (any element of End(E0)), the question is only its norm.
**Kill test.** Count, for e = 60, the fraction of odd N < 2^e with 2^e − N represented by x² + f²y² for some f ≤ 10 vs f = 1; if the gain is < 2×, file as negligible.
**Tag.** [speculative].

```
CHECKED: H-ALISO-014 (auxiliary_discriminant_search — maximal-order discriminants only); H-SSIQ-d724f2 (census of subgroups of GL_2 acting via the standard maximal order of B_{p,∞}, same order object, no attack)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "for ι ∈ End(E0) with ι² = −m, the endomorphism a + bι has degree a² + m b²"
EXP: none; nearest surface is Autolab package `p1243_auxiliary_discriminant_search` (H-ALISO-014)
```

### 10. Theta coordinates for the *ordinary* isogeny-class problems of H-ECDLP-f8101e: a negative control
**Mechanism.** H-ECDLP-f8101e asked whether selecting an isogenous representative helps ECDLP; H-ICINV-6c7920 rejected (scoped) the invariant-based version. A dimension-2 variant would glue two ordinary curves of the same trace and walk a (2,2) chain to a product with a "better" representative. Since any such walk composes with the DLP-preserving isogeny, this is a negative control: it should give nothing, and running it on the same toy primes (p ∈ {2003, 4001, 6007}) is a cheap sanity check that the dimension-2 machinery does not accidentally expose a representative the dimension-1 search missed.
**Object attacked.** Nothing; this is a control to prevent future dimension-2 "isogeny-class shortcut" claims.
**Delta needed.** None expected; the value is a recorded null.
**Obstruction.** Already effectively closed in dimension 1.
**Kill test.** Reproduce the H-ICINV-6c7920 census with (2,2)-glued products; any non-null result would be a surprise worth a record, otherwise file as control.
**Tag.** [known] (negative).

```
CHECKED: H-ECDLP-f8101e (isogenous representative selection — same question in dimension 1); H-ICINV-6c7920 (rejected_scoped — invariant-based selection on complete F_p isogeny classes at toy primes); H-ICINV-82ee6a (Frobenius-order endomorphisms on ordinary curves)
DISPROVEN: H-ICINV-6c7920 [rejected_scoped] — this lead is explicitly a dimension-2 control of that closure, not an attempt to reopen it
LEAN: no Lean coverage; would need: "an isogeny between ordinary elliptic curves over F_p of degree coprime to the group order induces a group isomorphism on the prime-order subgroup and preserves discrete-log instances"
EXP: none; nearest surface is the toy-prime census of H-ICINV-6c7920 (p ∈ {2003, 4001, 6007}), repository not specified in the BRIEF
```

### 11. Frobenius-midpoint condition as a splitting filter in Kani chains over F_p (vs F_{p²})
**Mechanism.** H-ALISO-003/004/005 sweep a "Frobenius midpoint" condition on supersingular data. In a Kani chain defined over F_p (both curves F_p-rational, kernel Galois-stable), the midpoint surface must be an F_p-rational principally polarised surface; if it is a Jacobian, its Frobenius characteristic polynomial is constrained (degree 4, real Weil). Filter candidate degrees N by whether the predicted midpoint polynomial is consistent with an F_p-rational surface — a cheap pre-test before running the full chain.
**Object attacked.** Attack cost of degree-guessing in F_p-rational settings (relevant to CSIDH-adjacent or F_p-restricted designs, dimension 2).
**Delta needed.** Rejection of a constant fraction of wrong N before the e-step chain; saves at most a constant factor.
**Obstruction.** Most dimension-2 targets live over F_{p²} where the filter is vacuous.
**Kill test.** At toy p, compute the midpoint Frobenius polynomial for right and wrong N; if wrong N are rejected at rate < 25%, close.
**Tag.** [adaptation].

```
CHECKED: H-ALISO-003 (frobenius_midpoint_sweep); H-ALISO-004 (frobenius_midpoint_sweep_verify); H-ALISO-005 (frobenius_midpoint_verify) — all three measure a Frobenius midpoint condition; the new part is using it as a pre-filter over F_p
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "the Frobenius characteristic polynomial of an F_p-rational principally polarised abelian surface is a degree-4 Weil polynomial P(T) = T⁴ − a T³ + b T² − a p T + p² with |a| ≤ 4√p"
EXP: none; nearest surface is Autolab package `p1486_frobenius_midpoint_sweep` (H-ALISO-003)
```

### 12. Quantum cost accounting for dimension-2 vs dimension-1 oracles in Kani-style reductions
**Mechanism.** H-ALISO-012/013 account for quantum aggregate oracle costs. A dimension-2 Kani chain used as a classical decision oracle (lead 2) inside Grover over degree guesses has cost e·C_{(2,2)} per oracle call; compare with a dimension-1 pairing-based oracle (one Weil pairing, cost ≈ log p multiplications). The audit asks whether any filed quantum accounting implicitly assumed the cheaper dimension-1 oracle while the reduction actually requires the dimension-2 one.
**Object attacked.** Internal consistency of the program's own quantum cost accounting; a measurement/audit record.
**Delta needed.** A factor e·C_{(2,2)} / C_pair ≈ 250 × (≈ 20 mults) / (≈ 500 mults) ≈ 10× in oracle cost, which shifts a Grover exponent by log₂(10) ≈ 3.3 bits — small but real.
**Obstruction.** It is bookkeeping, not cryptanalysis.
**Kill test.** Re-derive the H-ALISO-013 accounting with the dimension-2 oracle cost inserted; if the resulting bit-shift is < 1 bit at every parameter set, close.
**Tag.** [adaptation].

```
CHECKED: H-ALISO-012 (quantum_aggregate_oracle_probe — oracle cost aggregation); H-ALISO-013 (quantum_cost_accounting_verify — the accounting this lead re-derives)
DISPROVEN: none in the brief
LEAN: no Lean coverage; would need: "Grover search over M candidates with oracle cost C has total cost Θ(√M · C)"
EXP: none; nearest surface is Autolab package `p1486_quantum_cost_accounting_verify` (H-ALISO-013)
```

---
