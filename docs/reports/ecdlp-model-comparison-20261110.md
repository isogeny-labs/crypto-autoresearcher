# Mythos 5.1 vs Fable 5.1 — ECDLP ideation comparison (2026-11-10)

Inputs: the same eight angles, the same dedup index, one model per run. Fable's leads cite Mythos records because the index included them; Mythos did not see Fable's. The asymmetry is stated in the report and the per-shared-angle counts are given alongside the overall counts.

## Preliminary note on the premise

Fable's leads repeatedly cite Mythos-titled records ("the filed wave-1 record *Trace-one p-adic attack…*", "extends the barriers-wave record *Exhaustive hybrid-sum matrix…*", "the wave-2 drinfeld record", "the relations-wave incidence-determinant record"). Mythos never cites a Fable record. So the index was not symmetric: Fable saw Mythos's records, Mythos did not see Fable's. Everything below is read with that in mind — a Fable lead that "extends" a Mythos record counts as a refinement, not a new family, and a Fable lead that merely restates one counts as a restatement.

Second asymmetry: the eight shared angles are transfer, p-adic, barriers, wildcards, automorphic, drinfeld, torsion, complexity. Mythos additionally ran sweep, relations, port, synthesis; Fable additionally ran descent, cohomology, moduli, quantum-classical. Mythos's extra lanes concentrate on one concrete attack family (μ_B); Fable's extra lanes are mostly closure mathematics. Counts in §4 are given both overall and restricted to the shared angles.

---

## 1. Mechanism inventory

"≈" marks approximate matches (same object or same move, different presentation or regime).

### In both

| Family | Mythos form | Fable form | Match |
|---|---|---|---|
| MOV/pairing transfer with embedding-degree certificate | transfer L1 | transfer L1 | exact (first lines near-identical) |
| Anomalous p-adic transfer incl. ascent to F_{p^{k_p}} | transfer L2; drinfeld R1 (Drinfeld distance ord_p(t)) | transfer L2; p-adic "CM/Z[ω] reading" | exact |
| Sextic genus-2 cover y²=x⁶+b feasibility | transfer L3 | transfer L3 | exact mechanism; Fable uses the other involution (x,y)↦(1/x²,y/x³) |
| Higher-genus covers / size law | superelliptic towers | Diem g=3 plane quartics | ≈ |
| Kani (ℓ,ℓ)-gluing with E′ free | transfer L5 | transfer L5 | exact |
| Self-gluing E×E along ⟨(P,Q)⟩ → product; cyclic quotient is [k] / (1,N)-polarisation | w2 transfer R2 | moduli R4; torsion "ratio lattice L(P,Q)", "Robert/Kani evaluation ≡ DL" | exact; Fable adds the Hermitian-class and Robert-evaluation readings |
| Generalized Jacobians (G_m/G_a extensions) | transfer | transfer | exact |
| Weil-restriction ascent + Gaudry/Diem | transfer | transfer | exact |
| Volcano descent / floor; vertical motion only | transfer, sweep, w2 automorphic "Hecke-lane audit" | transfer, moduli "vertical only", "vertical transport is relabelling" | exact |
| Twist / F_{p²} decomposition; twist-pair S_m roots | sweep, synthesis | transfer; torsion "Lattès on twist" (≈) | exact / ≈ |
| Affine-target vanishing (Hom(E,H_aff)=0) | transfer R2 | drinfeld "complete list of F_p-linear carriers / Scanlon" | ≈ |
| Torsion-section (Teichmüller) lift via CM Frobenius; canonical lift lost at 256 bits | p-adic R1, L2, L5 | p-adic R1, "costs ≥√p for first digit" | exact; Fable prices it |
| Additivity radius of t=−x/y | p-adic R3 | p-adic R3 ("coordinate property", p·r−1) | ≈ extension |
| Compatible lift ⇔ discrete log | p-adic L10 | p-adic "fibre-digit formula"; automorphic "complex elliptic logarithm" | exact |
| Ext¹(Z/N,·)=0 / Smart's gate | sweep L9, p-adic L1 | p-adic R4 (Ext-class reading), cohomology "Newton polygon" | ≈ |
| Witt-digit factor base | p-adic L11 (speculative) | p-adic "behaves as random set" (null) | exact object, opposite verdict |
| EDS valuation/periodicity vs Lauter–Stange | p-adic L8–9, wildcards, torsion, complexity | p-adic "EDS precision vs height"; torsion "rank-2 CM nets" (≈) | ≈ |
| Global lifts / xedni / height obstruction | p-adic L7 | p-adic "Mestre–Howe lifts and xedni" | ≈ |
| Hybrid-sum / DL-graph spectrum | barriers R1 (level p) | p-adic R2 (level p²) | ≈ extension |
| Additive energy of x-interval base pulled back to Z/N | sweep R2 | barriers "Gowers U³" (strictly stronger norm) | ≈ |
| Fourier certification floor for relation supply | barriers R3, L3, L11 | barriers "total relation-count certification floor"; "variance = 2m-th moment" (≈ extension) | exact / ≈ |
| Sum–product (BKT) obstruction | barriers L5 | barriers "elliptic sum–product gap" | ≈ |
| Incidence barrier | barriers L9 | barriers "Elekes–Szabó blindness" | ≈ |
| Coordinate vs group structure of F | barriers R4 | barriers "coordinate-side dichotomy" | ≈ |
| Energy–Freiman / planted structure | barriers L10 | barriers "planted-structure calibration suite" | ≈ |
| Multiplicative-coset base / trace sums over subgroups | barriers L13; wave-1 μ_B | barriers "BGK gap"; wildcards "torsion-translate on μ_B grids" | ≈ |
| Elliptic Burgess for K_b / character orbit sums | barriers L6 | QC "small-order autocorrelation of χ orbit" | ≈ |
| Sumset / energy of X_L = x({kP: k≤L}) | barriers L8 | barriers L5 (additive energy + Sidon) | exact set, ≈ statistic |
| Bit-blasted SAT/SMT for F_p PDP | sweep R3, relations, wildcards R2 | wildcards R3 (WDSat carry-free XOR fraction); complexity R2 (direct ECDLP CNF) | ≈ |
| Joint-solve exponent e_k on μ_B^k | relations R2 | wildcards R2 (e_k ≤ k−1 constructively) | exact; Fable makes it constructive |
| Riemann–Roch / incidence determinant (coplanarity in L((m+1)O)) | sweep L5, relations L5 | wildcards R4 (hyperplane degeneracy of elliptic normal curve) | ≈ exact |
| Symmetrised / isotypic Macaulay reduction | relations L6 (FGHR), port L4 (μ₃-graded) | wildcards "Faugère–Svartz isotypic splitting" | ≈ |
| Coppersmith / lattice small-root region | wildcards R1, synthesis L4 | wildcards "Siegel/LLL null control" | ≈ |
| ISD / elliptic AG code | sweep L6, wildcards L7 | wildcards "ISD and Wagner numbers" | exact |
| Unlikely-intersection yield audit on μ_B grids | relations L9 | wildcards "torsion-translate structure (Lang, IST)" | ≈ — Fable supplies the theorem behind Mythos's test |
| 3SUM / collinear points | wildcards L9 | wildcards "Zech-twisted 3SUM" | ≈ |
| TFNP placement | wildcards L13 (PPP) | wildcards "PLS reading" | ≈ |
| Diamond operators / Lefschetz count on X_1(N) | w2 automorphic R1, L2 | automorphic R2 | exact |
| Spectral statistics on the fibre reduce to ord_N(k) | w2 automorphic L3 | automorphic "power traces / dynamical zeta" | ≈ |
| Ray-class / ring-class reformulation on the CM curve | w2 torsion "ray-class"; port "Lenstra module" | transfer "ring class group of conductor N"; automorphic "ray class field of 𝔫" | ≈ |
| Analytic rank of lifts / pencils / K3 over F_p(t) | w2 automorphic L6, R3; drinfeld R4 | automorphic "two-point lifts rank ≥ 2", "F_p(t)-pencil"; drinfeld "elliptic surfaces = XEDN lane" | ≈ (different theorems, same lane) |
| Isotrivial j=0 small-norm sections / GLV box | w2 automorphic R4; wildcards GLV-HNP | moduli "small-norm k is GLV box search"; "NS curves are GLV tautologies" | ≈ |
| Modular symbols / Euler systems give no bridge | w2 automorphic L12 | automorphic "group-ring elements never compute a DL" | ≈ |
| Katz–Sarnak | w2 automorphic L14 (zeros as supply barrier) | automorphic (lift family instance-blind) | ≈ by name only |
| E[N] eigenbasis = MOV; Schoof asymmetry; X_0(N)/X_1(N) fibre, w_N | w2 torsion L1–5 | torsion L1–2, "Fricke/AL and diamond" | exact (first lines near-identical) |
| ψ_N eigenline factorisation h_1·h_p | w2 torsion L3 | torsion "derivative h_1′(x_P)", "rank-2 nets evaluate h_1" | Mythos origin, Fable extends |
| Interpolation degree of scalar graph Γ_k | w2 torsion R2 | torsion R2 (j=0: GLV-minimal norm K(k)) | exact + refinement |
| Small-multiplier free relations | w2 torsion R3 | torsion R4 (Eisenstein multipliers) | exact + j=0 refinement |
| Heegner points | w2 automorphic R2 (GKZ, rank-1 lift) | torsion "Kronecker congruence Φ_N(0,0)" | name only — different mechanisms |
| Flattening rank / exceptional-target locus of specialised Semaev tensor | w2 complexity R1, L12 (Δ_2) | complexity R4 | exact |
| Ternary cubic of S_3 (j=0, Waring rank 3) | w2 complexity R4 | wildcards R1 (étale-algebra trace form) | ≈ same object; Fable extracts the cost consequence |
| Nullstellensatz / PC refutation degree | w2 complexity L3, R2 | complexity R3 (exact NS-degree formula) | ≈ |
| Bilinear complexity of addition law | w2 complexity L8 | complexity L6 | exact |
| Strassen / Paterson–Stockmeyer nonscalar bounds | wildcards L14, w2 complexity L7 | complexity L10 | ≈ |
| SA/SoS/MILP relaxation kill test | w2 complexity L11, w2 wildcards R2 | complexity L12 | exact |
| Algebraic-degree / Boolean-degree profile of DL bits | w2 wildcards R1, w2 complexity R3 | QC R3 (Walsh concentration); cohomology "one harness" | ≈ |
| Half-arity claw | sweep, relations | QC "Grover dequantizes to claw" | ≈ |
| Cheon / scalar torsor | port L2; torsion "static-key vs Cheon" | barriers "ring-access barrier"; QC "coset-state supply"; drinfeld "Carlitz–Hayes" | ≈ |
| HNP / Boneh–Venkatesan | port L7, wildcards L10 | QC "noisy dual-lattice samples" | ≈ |
| Theta group | wildcards L11 | descent "non-abelian theta torsors" | ≈ |
| Summation fibre ≅ E^{m−1} / étale cohomology | wildcards L12 | complexity "no algebraic families (Lang–Néron)" | ≈ |
| Carlitz module | w2 drinfeld R2 | drinfeld "Carlitz torsion = ASW filtration" | ≈ |
| Hecke-lane audit of toy isogeny classes | synthesis L2, L6 | moduli R3 (class-number audit, h=1 arm) | ≈ |

### Only in Mythos

- Scheme-degree barrier |F| ≤ deg E·deg Z, and the wave-2 exceptional-map barrier (group-scheme predicates exhaust cheap complete splitters). *Cousin in Fable: conductor barrier — different mechanism.*
- Digit-box factor base from the special prime (Dirichlet-kernel indicator).
- The μ_B resultant-tower factor base and its satellites: F4 on the membership system, large primes μ_B ⊂ μ_{B′}, union-of-cosets predicate, rejection-sampling null, charged multiplications per relation. (Fable analyses this object but did not introduce it.)
- Auxiliary-curve torsion factor base through an x-only ladder; Dickson line D_B(x)=2 / norm-one torus for B | p+1; chained-ladder presentation; cross-curve log-independence control.
- Chained S_3 tower vs flat S_{m+1} ("three presentations").
- j=0 symmetry reduction: U_m in u=x³, weighted homogeneity with 3 | B, μ₃-graded Semaev, u=b/x³ for division polynomials, GLV spectral forcing.
- Modular-parametrisation cover X_0(M)→E and "Hecke pushforward is a scalar".
- Lift-and-reduce to a bad fibre. *(Fable's Hyodo–Kato lead is a cousin.)*
- Automorphism-orbit factor base on the cover.
- Frobenius-difference log μ=ψ∘(Φ−1) (Buium δ-character).
- Zero k-linearity radius experiment across lift rules; isogeny-class invariance of p-adic handles; local pairings over Q_p trivial unless N | p−1.
- Spectral norm of small-x base / known-DL target-set boosting.
- Short-window fingerprints of k ↦ x(kP).
- Rigorous interval index calculus above β = m/(2(m−1)).
- Minkowski column-count floor for Macaulay solves.
- Function-field Coppersmith for the binary base.
- Polynomial-method / parity-counting exponents for Boolean PDP.
- Incremental CDCL with learnt-clause retention.
- Rank-2 tensor ⟹ multiplicative k-sum (the implication; flattening itself is shared).
- Slope sieve; enumeration-floor conditional statement; charged decomposition-cost slope; exact toy spectrum suite.
- Kummer-line polynomial-semiconjugacy rigidity.
- Torsion-on-ascent parity lemma (symmetrisation available only where Gaudry floor ≥ p^{10/7}).
- Scalar-side transfer: Maurer–Wolf auxiliary curve over F_N and implicit-representation barrier.
- Positive controls: trace-2 toy curves with k=1; measured genus-2 IC slope vs rho.
- Exact interpolation degree and sparsity of the DL function on structured bases (Fable's Walsh/harness/Eisenstein leads are cousins; origin is Mythos).
- Cross-characteristic proof-degree barrier; Alekhnovich–Razborov expansion precondition; algebraic natural-proofs meta-barrier; UNSAT-side PC degree of the μ_B system.
- ApproxMC hash-based model counting of decomposition counts.
- Cube attack / higher-order differential on δ ↦ LSB x(Q+δP).
- Zero-sum / restricted-sumset (Olson; Dias da Silva–Hamidoune) certificates at β=1/2.
- Heegner via Gross–Kohnen–Zagier (specific DL in an L-value, coverage bound).
- Function-field analytic rank of K3 surfaces with bounded-coefficient reach; isotrivial j=0 section DLs as small-norm Z[ω] elements.
- Cuspidal degeneration of X_1(N) = pairing transfer; Hecke transport T_ℓ on X_1(N).
- Static-key sample reconstruction vs Cheon.
- Determinantal complexity of S_{m+1} is m+1.
- Port lane: exit-dimension theorem; NFS two-ring smoothness; Menezes–Wu → mod-ℓ Galois reps; FFS "Frobenius preserves degree"; Hafner–McCurley equidistribution rigour port.

### Only in Fable

- Unit-sibling curves / CM mirrors in six (and more) characteristics as F_N^*-torsors; anomalous 512-bit sibling; closure "cross-field CM transfer = compatible lift".
- Pushforward (square-x) factor base from the cover.
- GHS Weil descent as positive control (repo control, not new mathematics).
- Deformation law of the torsion digit / Serre–Tate–Kodaira–Spencer coordinate of the two-point lift / Greenberg extension class (one family).
- Finotti degree of the second Witt digit; x-only torsion lift (refinements).
- Mazur–Tate and Coleman–Gross p-adic heights between torsion lifts.
- Summation polynomials over Z/p² (null).
- Gowers U³ uniformity (DL image of coordinate bases; orbit sequences).
- Conductor barrier for Legendre/Kummer-pattern bases and the Legendre-pattern base as a charged algorithm with degree-2 encoding floor.
- Variance of decomposition counts = 2m-th spectral moment; Poisson dispersion floor.
- Type II bilinear-form certification for product-structured bases.
- Étale-algebra trace form of S_3 → 3 or 6 multiplications per evaluation; Zech-twisted 3SUM.
- Monodromy of S_{m+1} in its last variable = regular (Z/2)^{m−1}.
- Slice rank / Croot–Lev–Pach negative.
- WDSat carry-free XOR fraction bound.
- Descent lane: π−1 isogeny descent on the CM lift over Q(√−3); Cassels–Tate / Brauer–Manin blindness at 𝔭 | p; phantom points; Lang torsor of Q as Z/N² ⊂ E(F_{p^N}) with N-adic eigenline; 4-Selmer parity bit; anabelian sections; period–index; full 256-bit cost audit.
- Cohomology lane: translation rigidity / Kato–Saito collapse; zeta k-blindness of point-decorated varieties + Weil converse; Kummer covers of the Miller quotient; Kummer F-isocrystals only in the MOV field; canonical Frobenius splitting of H¹_rig(E∖{O,P,Q}) with Miller-computable Abel–Jacobi block; Cartier defect of ω_P^alg; Prym of the double cover branched at ±P,±Q; Dieudonné/Bloch–Kato negative; motivic class (1,k²,k) of Γ_k; "one harness".
- Automorphic: L-function of the 1-motive of a point; modular units at (E,P); Vélu at π−1 → Lamé three-term recurrence on power sums of x(E(F_p)); forced rank ≥ 2 of two-point lifts and k-blind root number; Hecke equidistribution of Grössencharacter residues (CM-Chebotarev exponent 1).
- Moduli: Chebotarev density of cover-defined bases; X_1(N)(F_p) single isogeny class with no sections; Hilbert-class-polynomial base (killed); scaled isomorphic models (null); CM-shaped calibration ladder.
- Drinfeld: Scanlon framing; rank-2 Drinfeld module as positive control; degenerate module over own characteristic field; Drinfeld-submodule bases on prime-degree binary fields; Lucas sparsity as quasi-subfield candidate; Drinfeld isogenies additive; Carlitz–Hayes = Cheon with hardness swapped; t-motive/Dieudonné.
- Torsion: theta series of L_k / Siegel–Weil mean claw yield; h_1′(x_P) derivative statistic; rank-2 CM elliptic nets; Lattès cycle structure on the twist.
- Quantum-classical lane (entire): non-dequantizability statement; Schmidt-rank/Toffoli floors; Kuperberg label hardness χ_q(k); Fourier-sparse hidden shift; x-only hiding function; BHT; Boneh–Lipton dichotomy; Tang-style SQ dequantization.
- Complexity: degree = yes-size floor and its Borodin–Cook time–space version; algebraic/bit-level dichotomy with the (N/d)^{1/3} gap; group-algebra Wedderburn rank; DFT-diagonalisation of the μ_B membership ring ("F4 progress is point evaluation").

---

## 2. Restatements of the prior index in disguise

### Mythos

Repo/index items re-filed as leads (cited index keys or `RESEARCH_*.md` in the lead itself):
- Half-arity claw / k-SUM — filed twice (sweep, relations "re-costed"); IDEA-20260731-007.
- Elliptic-code / ISD — filed twice (sweep, wildcards).
- Hecke/volcano position for j=0; volcano descent — KR-RHO-755e35, `RESEARCH_VOLCANO_FLOOR_RHO.md`.
- Torsion-lift p-adic coordinates, CM-module port, "Transfer: covers/MOV/twist" (sweep, all `[known]`).
- Symmetrised S_{m+1} — KR-IC-955fd6 / `RESEARCH_SYMMETRIZED_SEMAEV.md` (re-filed again in synthesis as "automorphism-quotient coordinates").
- Large-prime variation — KR-IC-a4dd54, IDEA-20260731-012 (filed in relations and again in port as a "port").
- SAT on the μ_B system — KR-IC-5765d2 pipeline.
- Automorphism-orbit base on the cover — `RESEARCH_KOBLITZ_INDEX_CALCULUS.md` / KR-IC-b0fcda (re-filed in port as "μ₃-graded Semaev").
- Port lane as a whole is a re-reading: Cheon (`ca_cheon`), Jacobian/Gaudry (KR-IC-a4dd54, KR-IC-46…), NFS descent → descent trees ("ports filed"), class-group large primes ("filed: IDEA-20260731-012"), HNP.
- Synthesis: lattice β_max (KR-IC-5931ee, IDEA-20260727-003 — explicitly "closure with a price tag"); twist-pair accounting (KR-IC-5a43e5); GLV spectral forcing (KR-RHO-0528e7, IDEA-20260727-001); EDS frontier row (`RESEARCH_EDS_RESIDUE.md`); Hecke-lane audit of existing experiment directories.
- Wildcards: theta groups (IDEA-20260806-0c9de1); EDS/Strassen (`RESEARCH_EDS_RESIDUE.md`, re-filed in wave-2 complexity); Coppersmith region re-filed in synthesis.
- p-adic: global lifts/xedni/HKT; p-adic EDS law ("control extending `RESEARCH_EDS_RESIDUE.md`"); compatible-lift advice.
- Wave-2 `[known]` closures: Hecke eigenform knows only Frobenius polynomial, spectral stats ⟨k⟩-invariant, cuspidal degeneration = pairing, Galois rep separates nothing, Hecke pushforward scalar, complex elliptic log, Bosma–Lenstra bilinear complexity, "no lower-bound tool" (KR-RHO-13bf67), determinantal complexity, Kummer/local pairings vacuous (same content as p-adic L12), EDS reading of ψ_k (third filing of Lauter–Stange).

Internal self-duplication (not index restatement but inflates the count): Riemann–Roch determinant ×2, Aut-quotient u=x³ ×4 (sweep, relations, port, synthesis), SAT/SMT ×4, claw ×2, ISD ×2, EDS/Strassen ×3, Coppersmith ×2.

Roughly 30 of ~165 Mythos lead lines are restatements; another ~12 are self-duplicates.

### Fable

Restatements of Mythos records (visible in the index to Fable) — first lines near-verbatim:
- Transfer L1, L2, L3, L5, L10, L11, L12, L14 (pairing, anomalous, sextic cover, Kani, generalized Jacobians, ascent+Gaudry/Diem with the same `RESEARCH_*` citations, volcano floor, twist).
- Torsion L1, L2, L11 (MOV eigenbasis, Schoof asymmetry, Fricke/diamond = Mythos torsion L1–5).
- p-adic: "Separation of classical p-adic attacks" (Mythos sweep L9 + p-adic R4); "fibre-digit formula" (self-described: "wave-1 lead … made explicit"); "canonical lift costs √p" ("refines wave-1 lead"); "Witt-digit base random" (Mythos's speculative route with a null verdict); "CM/Z[ω] reading" (Mythos drinfeld R1); "Mestre–Howe/xedni" (KR-IC-cd159a); "EDS precision vs height" (`RESEARCH_EDS_RESIDUE.md`); "summation polynomials over Z/p²" (KR-IC-5a43e5).
- Barriers `[known]`: total relation-count floor (= Mythos Fourier certification), Elekes–Szabó (= incidence barrier), coordinate-side dichotomy (= coordinate vs group), ring-access barrier (= Cheon); elliptic sum–product gap cites IDEA-20260726-005 / IDEA-20260801-003.
- Wildcards: ISD/Wagner numbers; hyperplane degeneracy (= Riemann–Roch determinant); Siegel/LLL null (= lattice closure); Faugère–Svartz (= symmetrised Semaev); WDSat (KR-IC-5765d2); PLS (= TFNP).
- Descent: "descent on J_1(N)" (= diamond operator); "Brauer–Manin on Kummer-K3" (= moduli wave, itself = Mythos K3 census); "anabelian", "period–index", "Brauer constant" are textbook vanishing statements.
- Cohomology: Newton polygon (= Ext-vanishing again); Kummer F-isocrystals (= N | p^k−1, MOV); Hyodo–Kato (= lift-and-reduce / Tate-curve degeneration); motivic class of Γ_k (= interpolation degree k²); Dieudonné/Bloch–Kato (= "torsion prime to p invisible", also filed in drinfeld as t-motive).
- Automorphic: power traces → ord_N(k) (= Mythos spectral stats); ray class field (= Mythos ray-class); Hecke equidistribution exponent 1 (= Hecke-lane audit); Katz–Sarnak; group-ring elements (= modular symbols); pencil analytic rank (= K3 record / xedni lane).
- Moduli `[known]`: NS curves are GLV tautologies (= GLV spectral forcing + K3 census); vertical only / relabelling (= Hecke lane, isogeny-class invariance); no étale torsor (= local pairings vacuous); small-norm k is GLV box (= isotrivial record + GLV-HNP); X_1(N)(F_p) single isogeny class (Hasse bound restated).
- Drinfeld: "Survivor 1" (= anomalous exits), "Survivor 2" (= affine-target vanishing), τ-adic Koblitz line (= Koblitz lane), "elliptic surfaces = XEDN lane" (= Mythos drinfeld R4), Carlitz/ASW (= Mythos drinfeld R2).
- Torsion: Eisenstein-multiplier free relations (= small-multiplier statistic at j=0); Robert/Kani evaluation (= self-gluing record); cross-field CM transfer (closure of its own unit-sibling record).
- QC `[known]`: Grover→claw (IDEA-20260731-007), dual-lattice→HNP ("filed as wave-2 QC lead"), Fourier-sparse hidden shift ("already measured"), coset-state = Cheon chain, BHT, Boneh–Lipton.
- Complexity: bilinear rank of addition law; MILP kill test (= Mythos SA/SoS + wave-2 MILP record); no algebraic families (= summation fibre ≅ E^{m−1}).

Roughly 55 of ~175 Fable lead lines are restatements, and the `[known]` tag rate is ≈49% of tagged Fable leads vs ≈32% for Mythos. Fable's restatements are disproportionately of Mythos's own records, which is the asymmetry flagged at the top.

---

## 3. Ten most valuable unique leads (across both)

1. **Mythos — Dickson line D_B(x)=2 for B | p+1 / auxiliary-curve torsion base via x-only ladder.** Removes the deployability dependence on p−1 having a divisor near p^{1/m}; the only new cheap-membership factor-base family in either portfolio.
2. **Mythos — Scheme-degree barrier + exceptional-map barrier.** One Bézout line bounds every algebraically cut factor base and the wave-2 follow-up shows group-scheme predicates are the only cheap complete splitters; a reusable closure for all "clever predicate" proposals.
3. **Fable — Variance of decomposition counts = 2m-th spectral moment, Hölder ⟹ Poisson floor.** Turns every empirical yield histogram into an exact identity and gives the first rigorous dispersion floor for Semaev relation supply.
4. **Fable — Legendre-pattern base with conductor barrier.** A genuinely different deployable base (membership = r Legendre symbols) with its own built-in character-sum barrier; both algorithm and limit stated together.
5. **Mythos — Zero-sum / restricted-sumset certificates at β=1/2.** The only non-Fourier relation-existence tool filed; sidesteps the √p character-sum loss that kills certification below p^{1/2+1/(m+1)}.
6. **Fable — Degree equals yes-size.** The first provable lower bound outside the generic-group model (rational tests on a single target), directly answering Mythos's "algebraic adversaries have no lower-bound tool"; the time–space version is a free corollary.
7. **Fable — Étale-algebra trace form of S_3 → 3 or 6 multiplications, Zech-twisted 3SUM.** Concrete constant-factor win in the only step every prime-field index-calculus variant pays for, plus a clean fine-grained reduction.
8. **Mythos — Torsion-on-ascent parity lemma.** Kills the "symmetrise after ascent" route with an exact threshold (p^{10/7}) rather than a heuristic.
9. **Mythos — Scalar-side Maurer–Wolf transfer and implicit-representation barrier.** The only lead in either set treating the exponent ring F_N as a target; identifies precisely why auxiliary-curve tricks don't port.
10. **Fable — DFT-diagonalisation of the μ_B membership ring.** Structurally explains the F4-on-μ_B wall (progress ≡ point evaluation), closing Mythos's degree lead with an argument rather than a benchmark.

Near misses: Fable's unit-sibling CM mirrors (novel object, already self-closed), Vélu-at-π−1 Lamé recurrence (`[unverified]`, potentially the most original identity in the pack), Walsh/LMN concentration test (cheap, decisive); Mythos's cube attack on LSB x(Q+δP) and ApproxMC counting (cheap experiments at real sizes).

---

## 4. Which model added more genuinely new mechanism families

Method: a "family" is a distinct mathematical object or move; leads sharing an object (e.g. all μ_B satellites; all SAT/SMT variants; the whole π−1 descent/Selmer/BM cluster) are one family. Excluded: anything in the "both" table, anything that is a restatement per §2, and pure textbook-vanishing `[known]` lines with no new object. Approximate-match families were assigned to the model whose record came first (Mythos, given the citation direction).

- **Mythos: 33 new families** overall (list in §1 "Only in Mythos", merging μ_B satellites, j=0 symmetry reductions, proof-complexity barriers, positive controls, and the toy-suite into one family each). Restricted to the eight shared angles (dropping sweep/relations/port/synthesis-only families): **≈24**.
- **Fable: 45 new families** overall (list in §1 "Only in Fable", merging the descent cluster into two families, the cohomology negatives into three, the QC lane into five, the Drinfeld dictionary into three). Restricted to the eight shared angles (dropping descent/cohomology/moduli/QC-only families): **≈28**.

Verdict: **Fable added more by count, both overall (45 vs 33) and on the shared angles (≈28 vs ≈24)**, with three caveats that narrow the real gap:
- Fable had Mythos's records in its index; roughly a third of Fable's lines are restatements or refinements of them, and its new families are ~50% closures/negatives versus ~30% for Mythos.
- Mythos's single largest cluster (μ_B / torus / auxiliary-torsion bases, 8–10 lead lines) is the most attack-shaped new material in the pack; Fable's largest clusters (descent, cohomology, QC) are almost entirely "the invariant is k-blind" closures.
- Counting tolerance is about ±3 per model depending on how the cohomology negatives and the Mythos port lane are merged; the ordering does not change under any merging I tried, but the shared-angle margin (4) is within that tolerance.
