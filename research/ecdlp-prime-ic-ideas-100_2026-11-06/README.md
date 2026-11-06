# ECDLP prime-field index calculus: 100 delphi directions

- **Date:** 2026-11-06
- **Run:** `goal-20261106-102030-46542`
- **Goal:** generate 100 novel ideas for ecdlp index calculus for prime fields and make sure to thoroughly review ideas we've tested previously in isogeny-labs/crypto cryptanalysis and crypto-autoresearcher repos
- **Method:** delphi staged pipeline (frame -> expand -> critique -> synthesize), preceded by the ECDLP lead-atlas review in `prior-work.md`.

## Prior work

The sweep was checked against the program's ECDLP lead atlas (`crypto-autoresearcher/knowledge/leads/ecdlp/`, 154 leads, 2,178/2,185 ledger records mapped) and the measured prime-field IC, summation-polynomial, p256 factor-base and lattice-IC rounds in `isogeny-labs/crypto`, `isogeny-labs/cryptanalysis` and `isogeny-labs/crypto-autoresearcher`. The full digest is in [`prior-work.md`](prior-work.md). A direction marked *variant* must name what differs; a direction marked *closed* is not a new idea until the named obstruction is escaped.

## Directions

### 1. **FAM-1 growth-ladder with planted positive controls at 16/20/24/28/32 bits** — measure κ_rel for the best FAM-1 geometry across 5 rungs, requiring 2^(8·δ*) growth per rung; promotes LEAD-ICP-coincidence-harvest-structured-base from `open_next_step` to `verified` or `closed`. *(advances LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 10  LEAD-RHO-best-of-candidates-indegree         open_next_step     Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree | 10  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 7  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves

### 2. **H-PFDR-6189d0 normal-form sweep over all PFDR/PATH proposals** — compute canonical polynomial-system normal forms for every prime-field IC proposal in the ledger; deduplicate 47 proposals down to ≤ 12 distinct systems. *(advances LEAD-ICP-construction-normal-form)*

**Prior-art check:** 19  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range) | 12  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 10  LEAD-ICP-digit-presentation-solving-degree   open_nex

### 3. **Certified finite degree-growth ladder for digit-presented S_3/S_4 at m=2,3 with independent primes per s** — run H-PFDR-d5f90f with support-matched nulls and block-factored controls at s=2..8; fixes pseudoreplication in EV-PFDR-99c699. *(advances LEAD-ICP-digit-presentation-solving-degree)*

**Prior-art check:** 4  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 4  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 4  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k

### 4. **JV/Granger source freeze + C_pdp4 measurement at toy p' → projection to p=2^64** — implement H-GFPN-3366ea: freeze oracle-assisted Static DH sources, measure 4-point decomposition cost at p'=2^16-2^20, project to gfp5 with full error budget. *(advances LEAD-ICP-gfp5-oa-sdhp-jv)*

**Prior-art check:** 23  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1

### 5. **Odd-characteristic cover genus for EcGFp5/EcMasFp5 + isogeny-class control** — compute Diem bound for both curves plus a random isogenous curve at same conductor; certify genus ≥ 9 for all. *(advances LEAD-ICP-gfp5-odd-char-cover)*

**Prior-art check:** 18  LEAD-TRF-odd-prime-ghs-cover-floor           open_next_step     Odd-characteristic GHS cover genus floors at prime extension degree and their isogeny-class reach | 13  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 13  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers

### 6. **Degree-4 Macaulay rank of double-odd 2-torsion quotient at toy p'** — run H-GFPN-6cc6aa with cofactor-1 null; if rank < generic, re-run C1 ladder at 3 primes spanning ≥ 12 bits with honest memory envelope. *(advances LEAD-ICP-gfp5-symmetrized-gaudry)*

**Prior-art check:** 12  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 6  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm

### 7. **Boolean-native Groebner (BRiAl) with parseable d_solv + RSS watchdog on l∈{5,6}** — implement H-ICPERF-c9380d: side-classified exhaustive table as ground truth; compare WDSat vs BRiAl on descended binary PDP. *(advances LEAD-ICP-icperf-binary-pdp-solver)*

**Prior-art check:** 16  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary

### 8. **Complete the 17 missing arms of EXP-ECTD-0cf008 (32,768 targets each)** — finish crater/floor pairs with conductor steps 8209/131101, native vs random factor bases, verified arity-3 occupancy; report coverage + variance. *(advances LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 15  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 13  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection | 10  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at

### 9. **Admitted polynomial successor for lattice IC relation construction** — deliver one pipeline on explicit prime cyclic subgroup (F43/F97/F101 + rank-2 F25 control) certifying density, valid roots, independent rank, complete relation cost; then four-track review. *(advances LEAD-ICP-lattice-ic-relation-construction)*

**Prior-art check:** 15  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 14  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups | 13  LEAD-ICP-full-width-arity-grid               open_blocked  

### 10. **Preregistered prime fall-degree study: stages g4, hky-A, d-A, cap-A, hky-C, hky-B, d-B** — dedicated host, multiply-add counts kept; stage A must reproduce Kummer m=2 d_F medians 3,4,4,4,4,5,5,5,5,6 at t=1. *(advances LEAD-ICP-pkm-tower-algebraic-oracle)*

**Prior-art check:** 9  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 7  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range) | 6  LEAD-EXO-curve-model-representation          closed_obst

### 11. **Section 13 second-host replay of 20-bit holdout at N>45** — all 1,008 original records reproduced exactly on isolab-eks; promote to leaderboard; extend to 24-bit with same constant-engineering recipe. *(advances LEAD-ICP-prime-ic-constant-engineering)*

**Prior-art check:** 6  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class | 6  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models) | 5  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for

### 12. **Prove chart correspondence for shared divisor-coefficient circuits** — freeze k=3,4 censuses after checking ≥ 5 usable distinct x; compare per-root PKM, symmetric, quotient, Graeffe circuits; k=2 as empty squarefree-chart negative control. *(advances LEAD-ICP-shared-coefficient-membership)*

**Prior-art check:** 27  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for high-degree implicit factor-base membership | 7  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequen

### 13. **Macaulay ranks of digit/chained S_4 at j=0, j=1728 vs generic + coefficient-block vanishing null** — three toy primes, degree-d ranks for d=2..6; H-PFDR-df0127 + H-PFDR-6b9f1a. *(advances LEAD-ICP-xline-symmetry-special-j)*

**Prior-art check:** 6  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 6  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm | 6  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison

### 14. **Simulation lemma for class-group action in curve-aware GGM** — write/review H-CLGP-63f471: show ECDLP still needs Ω(√N) group ops when adversary gets free class-group action on curves; quantifier order + size-gap argument (h~p^{1/2} vs N). *(advances LEAD-STR-class-group-ecdlp-bridge)*

**Prior-art check:** 10  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms | 10  KR-RHO-817bf8                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves | 9  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the ref

### 15. **Preregistered ecbench IC study: three arms (floor-on-floor, floor→crater via 2-isogeny, crater-on-best-model)** — calibration targets for model selection, measurement on held-out; transport cost charged. *(advances LEAD-STR-class-representative-ic-selection)*

**Prior-art check:** 22  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 15  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 8  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory c

### 16. **Matched-order families: first-fall degree, F4 solve time, charged IC cost for S_3/S_4 at j=0/j=1728 vs generic** — automorphism-orbit factor base + sham-curve null of same support; fixed N per MATCHED-ORDER-DESIGN.md. *(advances LEAD-STR-special-j-ic-semaev)*

**Prior-art check:** 18  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 18  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 15  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field

### 17. **Even-degree Mumford arithmetic + general binary norm φ_*: Jac(H)→E** — certify subgroup order, kernel, image for each of 1,940 prime quadratic + 160 binary cubic pullback bindings. *(advances LEAD-TRF-cover-catalog-jacobian-transfer)*

**Prior-art check:** 35  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery | 12  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases | 9  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engi

### 18. **Freeze numeric tolerances for JV sieve positive control (R0 S) + rho A/A rule** — re-run paired sieve vs strong-rho at p∈{1009,1511,1823} with corrected hash accounting, F4/LA additions, charged isogeny walk. *(advances LEAD-TRF-jv-sieve-fp6-weak-class)*

**Prior-art check:** 17  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class | 11  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 11  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano lev

### 19. **Test H1 of IDEA-20261017-e3a6f1 at toy size** — equidistribution of ℓ(k)=log_g U(kP) in Z/(p-1), Smart-ratio success, correlation with Z/N characters; special + matched random p, planted-structure positive control. *(advances LEAD-TRF-miller-cocycle-nonhom-transfer)*

**Prior-art check:** 7  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier | 6  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j

### 20. **Implement Smith's Props 2 & 4 / trigonal construction on odd-char genus-3 descents** — test F_q-rationality and non-degeneracy on already-enumerated descents; pipeline to Diem q^{4/3}. *(advances LEAD-TRF-odd-char-descent-smith-quartic)*

**Prior-art check:** 19  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 9  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 3  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicabil

### 21. **Run approved n=7 EXP-PEXT-212d5c plan with Lean finite lemmas** — exhaustive placement spectrum, q=3 stratified controls + q=3,5,7 census; independent check of 2-torsion floors + isogeny-walk cost accounting. *(advances LEAD-TRF-odd-prime-ghs-cover-floor)*

**Prior-art check:** 9  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls) | 8  LEAD-TRF-odd-prime-ghs-cover-floor           open_next_step     Odd-characteristic GHS cover genus floors at prime extension degree and their isogeny-class reach | 6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inve

### 22. **Certified toy tower-field DLP: coprime tower splits n∈{4,5,6,8,12} + one certified log in F_121** — then small same-shape GF(p^12) calibration against published record before deployed estimate. *(advances LEAD-TRF-pairing-target-field-recost)*

**Prior-art check:** 12  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged | 9  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant | 8  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)

### 23. **Re-run 20-arm panel EXP-ECTD-0cf008 with psutil import fixed** — H-ECTD-e88346: crater/floor pairs, conductor steps 8209/131101, native vs random factor bases, verified arity-3 occupancy. *(advances LEAD-TRF-teske-secret-isogeny-trapdoor)*

**Prior-art check:** 15  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 9  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection | 8  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structur

### 24. **Measure public ISO-1 walk cost to nearest JV-weak curve in random F_{p^6} classes** — compare against ~1e10 attack cost; determine if any class places weak curve beyond public walk. *(advances LEAD-TRF-teske-trapdoor-fp6-weak-class)*

**Prior-art check:** 24  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class | 23  LEAD-TRF-teske-trapdoor-fp6-weak-class       open_unexamined    Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class | 19  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant

### 25. **n=2 control + exhaustive n=3 point-count census for q=2,3** — fixed-seed higher-q samples; require explicit F_q-isogeny of controlled degree before pricing DLP route. *(advances LEAD-TRF-weil-restriction-jacobian-class)*

**Prior-art check:** 7  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 7  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k

### 26. **Measure digit-character family (IDEA-20260921-1ec106) for (λ, PGL_2-stability)** — against PGL_2-orbit-matched null at census sizes 2^20-2^26; one natural candidate never measured. *(advances LEAD-EXO-coordinate-statistic-leakage)*

**Prior-art check:** 7  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases | 7  LEAD-RHO-best-of-candidates-indegree         open_next_step     Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree | 7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed s

### 27. **Measure relative bucket variance W of O2 agreement kernel (H-ECDLP-2ade73)** — across N, fit decay vs 1/√N; EXP-ECDLP-5cad48 never assigned W class. *(advances LEAD-EXO-four-list-ktree-join)*

**Prior-art check:** 11  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class | 9  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks | 7  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost

### 28. **Time T_section(d,χ,p) for bounded-height section through prescribed fibre on E1 surfaces** — ≥3 primes, random-system Groebner control; IDEA-20261009-581f5d. *(advances LEAD-EXO-global-lift-height)*

**Prior-art check:** 11  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces) | 7  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t) | 6  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, bel

### 29. **Independent audit of hashed-factor-base ECDL correctness + complexity proof** — check if LEAD-ICB-decomposition-encoding-and-sat obstruction applies to Akshima/Bochum encoding; #SAT exponent vs enumeration. *(advances LEAD-EXO-hashed-factor-base-tensor-ecdl)*

**Prior-art check:** 10  LEAD-EXO-hashed-factor-base-tensor-ecdl      open_next_step     Hashed-factor-base ECDL with a compact low-degree Boolean encoding and exact tensor contraction (Akshima et al., Bochum v0.2), conditional on the openai/math #k-SAT result | 5  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)

### 30. **Price Thue-Morse/Rudin-Shapiro conversion (H-ECDLP-a4be60) once nonzero log-bit advantage exists** — exponent 2β vs 1/2, memory/cost table; IDEA-20260904-f68c7f. *(advances LEAD-EXO-hnp-advice-leakage)*

**Prior-art check:** 9  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice | 7  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps | 6  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win

### 31. **Supply named constructors/theorems for 15 active IDEA registry rows** — start with IDEA-012 (finite-deck weighted endpoint, REVISE_SCOPED_REDUCTION); run zero-compute contract preflight. *(advances LEAD-EXO-ideas-corpus-algebraic-transforms)*

**Prior-art check:** 5  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness | 4  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows) | 3  LEAD-ICP-coppersmith-smallroot-semaev        closed_obstructed  Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describab

### 32. **Measure A(1) and A(d) (max agreement of deg-d polys with log graph Γ_E) on toy ladder** — against random-labelling null; H-ECDLP-f6a43a cell never measured. *(advances LEAD-EXO-invertible-hint-subset)*

**Prior-art check:** 6  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO) | 6  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases | 6  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied

### 33. **Run disjoint projection panel of IDEA-20260817-84755b in probabilistic regime** — exact-arithmetic fibre tests (KN-FIND-7d098b caveat) + random-relabelling null. *(advances LEAD-EXO-lossy-object-propagation)*

**Prior-art check:** 3  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces) | 3  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 3  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator 

### 34. **Inject 3 planted-signal families (IDEA-20260807-efc8de) into real pipeline** — replay every ECDLP mechanism screen against synthetic positives (IDEA-20260815-bc26a3); measure false-negative rate. *(advances LEAD-EXO-methodology-instruments)*

**Prior-art check:** 13  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 7  LEAD-EXO-cryptoscale-candidate-screen        exhausted_at_scale GOAL-CRYPTO-001 discovery screen for a reproducible non-generic crypto-size algorithm

### 35. **Verify K1 (Weil-reciprocity cocycle) + K2 (U(kP)=c·r_k·C^{k/N}) on toy prime-order curves** — gcd(N,p-1)=1; measure if k recoverable from U(kP) in <√N group ops once r_k charged. *(advances LEAD-EXO-miller-pairing-cocycle)*

**Prior-art check:** 12  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves | 11  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 10  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups

### 36. **Learnability control on toy prime-order groups: predict log bit from coordinates** — planted homomorphic leak positive control + random-relabelling null at N≤2^24; parallel ec_hardness_predictor phases 0-3. *(advances LEAD-EXO-ml-learned-models)*

**Prior-art check:** 11  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines | 9  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 9  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup

### 37. **Replace per-step cswaps in binary-GCD inverse with safegcd/jump-GCD** — narrow apply + ipmul/quotient phases; validate on full input space, not Fiat-Shamir island. *(advances LEAD-EXO-quantum-ecdlp-resources)*

**Prior-art check:** 5  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 4  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice | 4  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1

### 38. **Replicate EV-ECDLP-f6b3f5 re-scoped support (T_sel∈{0.65T,0.75T}) on EC walk at N=2^30** — independent implementation; repair fixture_gate_v2 for basin instrument (EV-ECDLP-31e91c failed). *(advances LEAD-RHO-advice-table-variants)*

**Prior-art check:** 9  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 6  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps | 6  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)

### 39. **Build best-of-P±R into gpu/nist kernel at W=16-32 walks/thread** — kernel's own inversion + fruitless-cycle escape; paired rate + steps-to-collision vs shipping kernel on P-256 with DP-corpus replay. *(advances LEAD-RHO-best-of-candidates-indegree)*

**Prior-art check:** 8  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves) | 6  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 6  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device an

### 40. **Port tag-tracing r-adding walk to 64-bit prime toy curve in rho_walk_leads harness** — ns/step paired vs plain step at 8-1024 walks/inversion, steps/collision with DP replay; also halving-step on sect113r1-size binary. *(advances LEAD-RHO-cheaper-step-primitives)*

**Prior-art check:** 16  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing

### 41. **Approve revised protocol for typed quantity H-AUXIN-6db354 (per-branch, supply-capped E(r))** — join completed census RUN-AUXIN-fd1edc with supply roster IDEA-20260930-68326c under cap. *(advances LEAD-RHO-cheon-deployed-applicability)*

**Prior-art check:** 11  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply | 4  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law | 3  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters

### 42. **Run EXP-AUXIN-25a29a end-to-end (56-bit r, divisor 65536, stage counts + gain fractions)** — recovered scalars certified, memory/DP costs reported beside ρ on same group. *(advances LEAD-RHO-cheon-toy-reproduction)*

**Prior-art check:** 6  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor | 6  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models) | 5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions und

### 43. **Build + pair TABLE_PHASE_POPC (phase via popc planes) vs 15.88 B/s sigma-table control** — one RTX PRO 6000, identical sorted DP corpora, 300-report re-walk gate. *(advances LEAD-RHO-ecc2k130-gpu-fpga-throughput)*

**Prior-art check:** 14  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks | 10  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 7  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion 

### 44. **Measure v3 table-walk kernel paired rate vs fused sigma-table control** — 5 alternating pairs A/A drift + planted-log + re-walk gate; price iterations × rate per solve for sigma, SIGMA_SIGN=2, table-v3. *(advances LEAD-RHO-ecc2k130-iteration-function)*

**Prior-art check:** 13  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt) | 10  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 8  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

### 45. **Run EXP-GRUMPY-eb8675 (certified exhaustive ladder Z/l 2^10..2^20)** — covered-set counter vs per-target simulation, negation map separate arm; file evidence for EXP-GRUMPY-cd7b82 Stage 1. *(advances LEAD-RHO-grumpy-store-all-schedules)*

**Prior-art check:** 8  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw) | 6  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)

### 46. **Run EXP-LHW-9adf78 (residue-guess price on W(m,w) with Mersenne/Fermat M)** — or write proof obligation of H-LHW-371a91 as checked derivation. *(advances LEAD-RHO-lhw-modular-filter-price)*

**Prior-art check:** 4  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups | 2  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300 | 2  LEAD-RHO-cheon-aux-acquisition               closed_obstructed  Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourse

### 47. **Re-run EXP-LHW-b49bc6 Stage 1 with checkpointed sumset counts + run length inside claim TTL** — hash-realisable jump sums on frozen (m,w) ladder m∈{20,24}; score E1 vs E2. *(advances LEAD-RHO-lhw-polymem-collision-walks)*

**Prior-art check:** 7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks | 4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP

### 48. **Price two incumbent rows of IDEA-20260930-79abd9 at m∈{32,40} in group ops** — Coppersmith-split advice tables + weight-restricted BL table; measure one with planted low-weight logs. *(advances LEAD-RHO-lhw-preprocessing-frontier)*

**Prior-art check:** 19  LEAD-RHO-lhw-preprocessing-frontier          open_unexamined    Low-weight DLP with preprocessing: the (P, S, T, epsilon, U) frontier | 12  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables | 11  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks

### 49. **Seal ecbench bounds for ρ.negation, ρ.plain, bsgs.negation on prime curves at log2 r 32-48** — ≥24 runs/size, replay certs, section 5a band; fit R(N)=1+c/N^β to toy-to-medium ratio (H-ECDLP-ff38dc). *(advances LEAD-RHO-matched-rho-calibration)*

**Prior-art check:** 10  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw) | 9  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier

### 50. **Price Koblitz canonicaliser in field-mul equivalents: EXP-CERTBIN-b4d29c at n=131** — design C (canonicalise every step) vs Bailey sigma (normalise only at DPs) + rotation-invariant polynomial key IDEA-20261015-2d8e5a; callgrind Ir. *(advances LEAD-RHO-native-step-cost)*

**Prior-art check:** 17  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 9  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

### 51. **Prove/refute H-EWALK-29cb90 per-step canonicalisation bound** — show for h=|H|>6 on ordinary prime-field curves any canonicaliser costs Ω(log h) group ops/step (charged gain ≤1); search encoding for non-constant H-invariant at h~N^{1/3} on toy curves (exhaustive). *(advances LEAD-RHO-non-automorphism-equivalence)*

**Prior-art check:** 18  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^* | 12  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 10  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm

### 52. **Measure trap rate on real campaign curve at production DP density** — before enabling negation-class walk (ecc-challenges PR #56); test CUDA path on GPU; design Koblitz Frobenius class walk (further √m). *(advances LEAD-RHO-pool-class-quotient)*

**Prior-art check:** 18  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 14  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0 | 12  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) 

### 53. **Run gpu-match workload on CUDA host with qualified traffic telemetry** — interleaved CPU/GPU repeats with A/A controls, then matched P-256 toy-to-medium ladder in ecbench.gae. *(advances LEAD-RHO-prime-gpu-rho)*

**Prior-art check:** 6  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier | 6  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison | 5  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)

### 54. **Hybrid FAM-1 + digit-presentation: use digit decomposition to generate FAM-1 seeds** — run digit-presented S_3 at m=2 to produce candidate x-coordinates, filter by FAM-1 membership polynomial; measure yield vs pure FAM-1 at 24/28/32 bits. *(variant of LEAD-ICP-coincidence-harvest-structured-base + LEAD-ICP-digit-presentation-solving-degree; differs: uses digit system as FAM-1 seed generator, not standalone decomposition)*

**Prior-art check:** 15  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks | 10  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)

### 55. **Isogeny-transported FAM-1 base: walk volcano to curve where FAM-1 geometry has maximal κ_rel** — use EXP-ECTD-0cf008 crater/floor data to select target curve; transport FAM-1 factor base via isogeny; charge transport cost; measure net κ_rel. *(advances LEAD-ICP-isogeny-transported-relation-yield + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 26  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 23  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 17  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels

### 56. **Lattice-assisted FAM-1 relation generation: use Coppersmith on FAM-1 membership polynomial** — despite Ryan 2025 bound, test if FAM-1's specific algebraic structure (low-degree parameterization) allows beating generic bound at m=3,4; toy primes 16-32 bits with positive controls. *(variant of LEAD-ICP-coppersmith-smallroot-semaev; differs: applies to FAM-1's specific parameterized locus, not generic Semaev)*

**Prior-art check:** 19  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets) | 13  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems | 10  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recogniza

### 57. **PKM-tower on isogeny volcano: use isogeny chain as tower levels instead of Kummer** — each 2-isogeny step gives new curve; factor base = union of small-x bases across chain; relations from multi-curve Semaev; test at conductor steps 8209/131101. *(variant of LEAD-ICP-pkm-tower-algebraic-oracle; differs: tower = isogeny chain, not Kummer; uses existing volcano census data)*

**Prior-art check:** 26  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 26  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 21  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-le

### 58. **Special-j digit presentation: j=0/j=1728 automorphisms reduce digit-system variables** — exploit x→ζx symmetry to fold digit equations; measure first-fall degree vs generic j at m=2,3 on matched-order families. *(advances LEAD-ICP-digit-presentation-solving-degree + LEAD-STR-special-j-ic-semaev)*

**Prior-art check:** 16  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks | 9  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 8  LEAD-STR-special-j-ic-semaev              

### 59. **Miller cocycle + FAM-1: use U(kP) as filter for FAM-1 decompositions** — if U(kP) leaks log-bit info (LEAD-EXO-miller-pairing-cocycle), use as pre-filter before FAM-1 relation search; measure combined yield at toy scale. *(variant of LEAD-ICP-coincidence-harvest-structured-base + LEAD-EXO-miller-pairing-cocycle; differs: Miller cocycle as statistical filter, not standalone transfer)*

**Prior-art check:** 13  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves | 10  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 9  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificat

### 60. **Cover-catalog transfer to prime-field IC: pushforward JV weak-class relations to prime field via cover map** — use LEAD-TRF-cover-catalog-jacobian-transfer Mumford arithmetic to transfer genus-3 JV relations from F_{p^6} down to E(F_p); test if transferred relations have usable smoothness. *(advances LEAD-TRF-cover-catalog-jacobian-transfer + LEAD-TRF-jv-sieve-fp6-weak-class)*

**Prior-art check:** 24  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery | 17  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models) | 16  LEAD-ICP-residual-partial-relations          closed_obstructed  Crediting residuals as partial rel

### 61. **Odd-char Smith quartic + FAM-1: use Smith isogeny to map FAM-1 base to plane quartic** — if Smith's Props 2/4 work (LEAD-TRF-odd-char-descent-smith-quartic), transport FAM-1 factor base to quartic model; test if decomposition easier on quartic. *(variant of LEAD-TRF-odd-char-descent-smith-quartic + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 25  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 18  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 17  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater 

### 62. **Quantum-classical hybrid: use quantum subroutine for FAM-1 relation generation** — Grover search over FAM-1 parameter space for smooth decompositions; classical linear algebra; cost model: quantum queries + classical ops in S units. *(variant of LEAD-EXO-quantum-ecdlp-resources + LEAD-ICP-coincidence-harvest-structured-base; differs: quantum only for relation search, not full Shor)*

**Prior-art check:** 15  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction) | 14  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 10  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops

### 63. **ML-guided FAM-1 seed selection: train predictor on (curve, target) → κ_rel** — use EXP-ECTD-0cf008 crater/floor data + LEAD-EXO-ml-learned-models pipeline; predict which FAM-1 seeds yield relations; measure speedup vs uniform sampling. *(advances LEAD-ICP-coincidence-harvest-structured-base + LEAD-EXO-ml-learned-models)*

**Prior-art check:** 8  LEAD-ICP-residual-partial-relations          closed_obstructed  Crediting residuals as partial relations (single/double large prime) in prime-field IC | 8  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)

### 64. **Tag-tracing FAM-1 walk: use tag-tracing (LEAD-RHO-cheaper-step-primitives) for FAM-1 relation search** — each FAM-1 seed = tag; walk combines tags; measure if in-degree concentration reduces FAM-1 relation cost. *(variant of LEAD-RHO-cheaper-step-primitives + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-RHO-best-of-candidates-indegree         open_next_step     Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree | 10  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 9  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)

### 65. **Best-of-candidates FAM-1: at each step, evaluate multiple FAM-1 seeds and pick best** — extend LEAD-RHO-best-of-candidates-indegree to FAM-1 parameter space; measure κ_rel improvement at 24/28/32 bits. *(variant of LEAD-RHO-best-of-candidates-indegree + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 10  LEAD-RHO-best-of-candidates-indegree         open_next_step     Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree | 6  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 6  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing

### 66. **Grumpy-giants FAM-1: store-all schedule for FAM-1 relation generation** — apply EXP-GRUMPY-eb8675 exhaustive ladder to FAM-1 seed space; measure if compiled reservoir-guided schedule beats uniform. *(variant of LEAD-RHO-grumpy-store-all-schedules + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 14  LEAD-RHO-grumpy-store-all-schedules          open_next_step     Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks) | 10  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)

### 67. **Low-Hamming-weight FAM-1: restrict FAM-1 seeds to low-HW exponents** — combine LEAD-RHO-lhw-* leads with FAM-1; test if low-HW seeds have higher smoothness probability; price preprocessing frontier. *(variant of LEAD-RHO-lhw-preprocessing-frontier + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 7  LEAD-RHO-lhw-preprocessing-frontier          open_unexamined    Low-weight DLP with preprocessing: the (P, S, T, epsilon, U) frontier | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class

### 68. **Non-automorphism equivalence classes for FAM-1: quotient FAM-1 seed space by H⊂(Z/N)^*** — test H-EWALK-29cb90 bound on FAM-1 parameter space; if canonicaliser cheap, measure κ_rel gain. *(variant of LEAD-RHO-non-automorphism-equivalence + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 19  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^* | 14  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant | 9  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0

### 69. **Digit-presentation on isogeny volcano: use digit system at each volcano level, transport relations** — combine LEAD-ICP-digit-presentation-solving-degree with EXP-ECTD-0cf008 data; digit decomposition at crater + floor, charge transport. *(variant of LEAD-ICP-digit-presentation-solving-degree + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 23  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 13  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks | 12  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic mode

### 70. **Lattice IC on isogeny volcano: use volcano structure to build better lattice** — LEAD-ICP-lattice-ic-relation-construction + volcano census; isogeny-adjoint witnesses vary predictably across volcano; exploit for relation construction. *(advances LEAD-ICP-lattice-ic-relation-construction + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 19  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups | 16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 14  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost ac

### 71. **Shared-coefficient membership for isogeny-chain factor base** — LEAD-ICP-shared-coefficient-membership + isogeny chain; factor base = union across chain; shared Graeffe/quotient circuits across curves in chain. *(advances LEAD-ICP-shared-coefficient-membership + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 18  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for high-degree implicit factor-base membership | 16  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 15  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic 

### 72. **x-line symmetry + isogeny transport: j=0/j=1728 symmetry preserved under isogeny?** — test if automorphism folding (LEAD-ICP-xline-symmetry-special-j) survives 2-isogeny transport; measure Macaulay ranks on transported systems. *(variant of LEAD-ICP-xline-symmetry-special-j + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 25  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j | 10  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class | 9  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables

### 73. **Class-group action + FAM-1: use class-group action to find curve with optimal FAM-1 geometry** — LEAD-STR-class-group-ecdlp-bridge simulation lemma + FAM-1; if simulation lemma holds, class-group action can't help; but test empirically at toy scale. *(variant of LEAD-STR-class-group-ecdlp-bridge + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 8  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition

### 74. **Matched-order special-j + FAM-1: j=0/j=1728 automorphism-orbit factor base for FAM-1** — LEAD-STR-special-j-ic-semaev matched-order design + FAM-1 geometry; measure κ_rel vs generic-j FAM-1. *(advances LEAD-STR-special-j-ic-semaev + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems | 10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO) | 10  LEAD-ICP-coppersmith-smallroot-semaev        closed_obstructed  Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases

### 75. **JV sieve + class-representative selection: solve JV weak-class instance on best isomorphic model** — LEAD-TRF-jv-sieve-fp6-weak-class + LEAD-STR-class-representative-ic-selection; calibrate model selection on toy JV instances. *(advances LEAD-TRF-jv-sieve-fp6-weak-class + LEAD-STR-class-representative-ic-selection)*

**Prior-art check:** 16  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 7  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class | 7  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-3

### 76. **Miller cocycle + class-group bridge: U(kP) as invariant under class-group action** — test if Miller cocycle (LEAD-TRF-miller-cocycle-nonhom-transfer) transforms covariantly under class-group action; if so, could bridge ECDLP to class group. *(variant of LEAD-TRF-miller-cocycle-nonhom-transfer + LEAD-STR-class-group-ecdlp-bridge)*

**Prior-art check:** 18  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class | 11  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves | 7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines

### 77. **Smith quartic + special-j: j=0/j=1728 on plane quartic model** — if Smith isogeny works (LEAD-TRF-odd-char-descent-smith-quartic), test if special-j curves give simpler quartics; measure genus/Diem cost. *(variant of LEAD-TRF-odd-char-descent-smith-quartic + LEAD-STR-special-j-ic-semaev)*

**Prior-art check:** 24  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 15  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 10  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree

### 78. **Tower-field DLP recost + FAM-1: use exTNFS cost model to price FAM-1 linear algebra over extension fields** — if FAM-1 relations live in extension field (LEAD-ICP-extension-field-embedding closed but...), use H-PAIR-62e9cc tower-DLP calibration to price LA. *(variant of LEAD-TRF-pairing-target-field-recost + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 20  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged | 14  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 10  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)

### 79. **Teske trapdoor + FAM-1: secret isogeny to curve with optimal FAM-1 geometry** — LEAD-TRF-teske-secret-isogeny-trapdoor + FAM-1; if heavy tail of Semaev meters exists, FAM-1 might amplify it; test at toy scale. *(variant of LEAD-TRF-teske-secret-isogeny-trapdoor + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 34  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness | 17  LEAD-TRF-teske-trapdoor-fp6-weak-class       open_unexamined    Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class | 9  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost

### 80. **Weil-restriction Jacobian + FAM-1: FAM-1 on genus-2 Jacobian in Weil class** — LEAD-TRF-weil-restriction-jacobian-class n=2 control + FAM-1 geometry on Jac(C); test if FAM-1 decomposition works on Mumford coordinates. *(variant of LEAD-TRF-weil-restriction-jacobian-class + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 14  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor | 12  LEAD-TRF-weil-restriction-jacobian-class     open_next_step     Genus-n Jacobians in the isogeny class of a Weil-restricted elliptic curve | 11  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite

### 81. **Coordinate-statistic leakage + FAM-1: digit-character family as FAM-1 membership test** — LEAD-EXO-coordinate-statistic-leakage digit-character (λ, PGL_2-stability) as fast filter for FAM-1 seeds; measure false positive/negative rate. *(variant of LEAD-EXO-coordinate-statistic-leakage + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 6  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets) | 6  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for high-degree implicit factor-base membership | 5  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply i

### 82. **Four-list k-tree + FAM-1: Wagner join on FAM-1 seed space** — LEAD-EXO-four-list-ktree-join O2 agreement kernel on FAM-1 parameter tuples; measure bucket variance W for FAM-1 seeds. *(variant of LEAD-EXO-four-list-ktree-join + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 18  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)

### 83. **Global lift height + FAM-1: bounded-height sections as FAM-1 relation source** — LEAD-EXO-global-lift-height T_section(d,χ,p) for E1 surfaces; if sections through prescribed fibre exist at low height, use as FAM-1 seeds. *(variant of LEAD-EXO-global-lift-height + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 26  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t) | 21  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces) | 21  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation sourc

### 84. **Hashed factor base + FAM-1: Akshima/Bochum tensor contraction for FAM-1 decomposition counting** — if audit passes (LEAD-EXO-hashed-factor-base-tensor-ecdl), apply to FAM-1 Semaev systems; measure #SAT exponent vs enumeration. *(variant of LEAD-EXO-hashed-factor-base-tensor-ecdl + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 30  LEAD-EXO-hashed-factor-base-tensor-ecdl      open_next_step     Hashed-factor-base ECDL with a compact low-degree Boolean encoding and exact tensor contraction (Akshima et al., Bochum v0.2), conditional on the openai/math #k-SAT result | 20  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 18  LEAD-STR-specia

### 85. **Invertible hint subset + FAM-1: low-degree poly agreement with FAM-1 log graph** — LEAD-EXO-invertible-hint-subset A(d) measurement on FAM-1 parameter space; if A(d) high, use as FAM-1 seed predictor. *(variant of LEAD-EXO-invertible-hint-subset + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 21  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p) | 8  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines | 6  LEAD-EXO-hashed-factor-base-tensor-ecdl      open_next_step     Hashed-factor-base ECDL with a compact low-degree Boolean encoding and exact tensor contraction (Akshima et al., Bochum v0.2), cond

### 86. **Lossy object propagation + FAM-1: propagate lossy FAM-1 seed through scalar multiplication** — LEAD-EXO-lossy-object-propagation disjoint projection panel on FAM-1 seed space; test if rigidity theorem leaves probabilistic regime for FAM-1. *(variant of LEAD-EXO-lossy-object-propagation + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 37  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation) | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/desc

### 87. **Methodology instruments + FAM-1: planted FAM-1 signals in pipeline** — LEAD-EXO-methodology-instruments 3 planted-signal families specialized to FAM-1 geometry; measure false-negative rate of FAM-1 screens. *(advances LEAD-EXO-methodology-instruments + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 13  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 4  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, b

### 88. **Quantum FAM-1: Grover on FAM-1 parameter space with quantum oracle for smoothness** — LEAD-EXO-quantum-ecdlp-resources circuit for FAM-1 smoothness test; cost model: quantum queries × classical LA. *(variant of LEAD-EXO-quantum-ecdlp-resources + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction) | 12  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 9  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, par

### 89. **Advice table variants for FAM-1: batch-reselected FAM-1 seed table** — LEAD-RHO-advice-table-variants T_sel∈{0.65T,0.75T} applied to FAM-1 seed table; grow table from solved FAM-1 relations. *(variant of LEAD-RHO-advice-table-variants + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 23  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables | 8  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7) | 8  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputatio

### 90. **Cheaper step primitives for FAM-1: tag-tracing + halving on FAM-1 seed space** — LEAD-RHO-cheaper-step-primitives ported to FAM-1 parameter walk; measure ns/step vs plain FAM-1 seed enumeration. *(variant of LEAD-RHO-cheaper-step-primitives + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 14  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 13  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 9  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

### 91. **Cheon auxiliary input for FAM-1: generate [x^d]P via FAM-1 relations** — if FAM-1 gives relations, can we compute [x^d]P cheaper? LEAD-RHO-cheon-deployed-applicability census + FAM-1; test at toy scale. *(variant of LEAD-RHO-cheon-deployed-applicability + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 21  LEAD-RHO-cheon-aux-acquisition               closed_obstructed  Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourself | 16  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply | 14  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition

### 92. **ECC2K-130 iteration function + FAM-1: sigma walk on FAM-1 seed space** — LEAD-RHO-ecc2k130-iteration-function v3 table walk adapted to FAM-1 seeds; Frobenius action on FAM-1 parameters? Test at binary toy then prime. *(variant of LEAD-RHO-ecc2k130-iteration-function + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 30  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps | 15  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)

### 93. **Grumpy store-all for FAM-1: compiled reservoir-guided FAM-1 schedule** — LEAD-RHO-grumpy-store-all-schedules exhaustive ladder on FAM-1 seed space Z/l 2^10..2^20; measure coverage vs uniform. *(variant of LEAD-RHO-grumpy-store-all-schedules + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 23  LEAD-RHO-grumpy-store-all-schedules          open_next_step     Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks) | 6  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance | 5  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and t

### 94. **Low-Hamming-weight modular filter for FAM-1: residue-guess price on FAM-1 seeds** — LEAD-RHO-lhw-modular-filter-price EXP-LHW-9adf78 on FAM-1 parameter space with Mersenne/Fermat M. *(variant of LEAD-RHO-lhw-modular-filter-price + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 13  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups | 4  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters | 3  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)

### 95. **Low-Hamming-weight collision walks for FAM-1: jump-sum walk on weight-w FAM-1 seeds** — LEAD-RHO-lhw-polymem-collision-walks EXP-LHW-b49bc6 Stage 1 re-run on FAM-1 seed space; checkpointed sumset counts. *(variant of LEAD-RHO-lhw-polymem-collision-walks + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 19  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class | 8  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm | 7  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

### 96. **Matched rho calibration for FAM-1: seal FAM-1 ρ baseline at 32-48 bits** — LEAD-RHO-matched-rho-calibration ecbench bounds for FAM-1 relation generation cost; fit R(N)=1+c/N^β. *(variant of LEAD-RHO-matched-rho-calibration + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 17  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier | 13  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo) | 12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny cl

### 97. **Native step cost for FAM-1: price FAM-1 canonicaliser in field-mul equivalents** — LEAD-RHO-native-step-cost EXP-CERTBIN-b4d29c design C vs Bailey for FAM-1 seed canonicalisation; callgrind Ir. *(variant of LEAD-RHO-native-step-cost + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 20  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 8  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion pa

### 98. **Non-automorphism equivalence for FAM-1: quotient FAM-1 seeds by H⊂(Z/N)^*** — LEAD-RHO-non-automorphism-equivalence H-EWALK-29cb90 bound on FAM-1 parameter space; search for cheap H-invariant. *(variant of LEAD-RHO-non-automorphism-equivalence + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 16  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^* | 11  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant | 6  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters

### 99. **Pool class quotient for FAM-1: negation + Frobenius classes in distributed FAM-1 search** — LEAD-RHO-pool-class-quotient trap rate measurement on FAM-1 campaign curve; design Koblitz Frobenius class walk for FAM-1 seeds. *(variant of LEAD-RHO-pool-class-quotient + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 28  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 20  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0 | 16  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)

### 100. **GPU FAM-1: gpu-match workload for FAM-1 relation generation on CUDA** — LEAD-RHO-prime-gpu-rho interleaved CPU/GPU with A/A controls; matched P-256 toy-to-medium ladder for FAM-1 kernel. *(variant of LEAD-RHO-prime-gpu-rho + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison | 10  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt) | 9  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)

## Critique

_critique stage did not complete_

## Synthesis

_synthesis stage did not complete_

## Next step

Take the highest-ranked direction from the critique, run its first falsifying experiment, and record the result as a new experiment protocol and PR. Directions that the critique closes stay in this document with their obstruction; they are not deleted.

