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

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: FAM-1 Growth-Ladder Validation** **1. Construction & Algorithm (FAM-1 Structured Base)** * **Field:** Prime fields $\mathbb{F}_p$ with $p \approx 2^b$, $b \in \{16, 20, 24, 28, 32\}$. * **Curve:** $E: y^2 = x^3 + ax + b$ with $j$-invariant 0 (CM by $\sqrt{-3}$) to maximize endomorphism ring structure for relation generation. * **Factor Base $\mathcal{F}$:** All points $P \in E(\mathbb{F}_p)$ with $x(P) \in \mathcal{B}$, where $\mathcal{B} \subset \mathbb{F}_p$ is the set of **structured polynomials**: $x = u^2 + c$ (quadratic) or $x = u$ (linear), $u \in \mathbb{F}_p$, $|u| <...

### 2. **H-PFDR-6189d0 normal-form sweep over all PFDR/PATH proposals** — compute canonical polynomial-system normal forms for every prime-field IC proposal in the ledger; deduplicate 47 proposals down to ≤ 12 distinct systems. *(advances LEAD-ICP-construction-normal-form)*

**Prior-art check:** 19  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range) | 12  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 10  LEAD-ICP-digit-presentation-solving-degree   open_nex

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Ingest & Parse**: Load all 47 PFDR/PATH proposals from `isogeny-labs/crypto` and `crypto-autoresearcher` ledgers. Extract the polynomial system $\mathcal{F} = \{f_1, \dots, f_m\} \subset \mathbb{F}_p[x_1, \dots, x_n]$ defining the relation generation (descent/sieving) step. Normalize coefficient encoding (Montgomery vs. Barrett, limb-size). 2. **Invariant Signature**: For each system, compute the **Macaulay Matrix** $M_d$ at degree $d = \max(\deg f_i) + 1$ (first fallback degree). Compute the **Hilbert Series** $H_{\mathcal{F}}(t)$ via Gröbner basis (F4, `msol...

### 3. **Certified finite degree-growth ladder for digit-presented S_3/S_4 at m=2,3 with independent primes per s** — run H-PFDR-d5f90f with support-matched nulls and block-factored controls at s=2..8; fixes pseudoreplication in EV-PFDR-99c699. *(advances LEAD-ICP-digit-presentation-solving-degree)*

**Prior-art check:** 4  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 4  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 4  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Digit presentation**: For target curve $E/\mathbb{F}_p$, fix $m \in \{2,3\}$. Represent $S_m$ (Semaev’s $m$-th summation polynomial) in the *digit basis* $\{x^{p^i}\}_{i=0}^{m-1}$ over $\mathbb{F}_p$ via repeated Frobenius reduction, yielding a polynomial system $\mathcal{F}_m \subset \mathbb{F}_p[x_1,\dots,x_m]$ of degree $\leq 2^{m-1}$ in each variable. 2. **Factor base**: Choose $B = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{V}\}$ where $\mathcal{V} \subset \mathbb{F}_p$ is a degree-$g$ subvariety (e.g., $g=2$ for $m=2$, $g=3$ for $m=3$) defined over $\ma...

### 4. **JV/Granger source freeze + C_pdp4 measurement at toy p' → projection to p=2^64** — implement H-GFPN-3366ea: freeze oracle-assisted Static DH sources, measure 4-point decomposition cost at p'=2^16-2^20, project to gfp5 with full error budget. *(advances LEAD-ICP-gfp5-oa-sdhp-jv)*

**Prior-art check:** 23  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1

**Plan (abridged; full text in `expanded-plans.md`):** **Construction/Algorithm: H-GFPN-3366ea (Oracle-Assisted Static DH Source Freeze)** 1. **Factor Base $\mathcal{F}$:** $x$-coordinates in $\mathbb{F}_p$ with $x < B \approx p^{1/3}$ (standard JV bound). 2. **Oracle $\mathcal{O}$ (Static DH):** Pre-compute $Q_i = [d]P_i$ for fixed secret $d$ and all $P_i \in \mathcal{F}$. Freeze this dataset. $\mathcal{O}(R) = x([d]R)$ for arbitrary $R$. 3. **Relation Generation (4-Point Decomposition $\mathcal{D}_4$):** For random $a,b \in [1, n-1]$, compute $R = [a]G + [b]Q_{target}$. Use $\mathcal{O}$ to evaluate Semaev polynomial $f_4(x_1, x_2, x_3, x_4; x_R...

### 5. **Odd-characteristic cover genus for EcGFp5/EcMasFp5 + isogeny-class control** — compute Diem bound for both curves plus a random isogenous curve at same conductor; certify genus ≥ 9 for all. *(advances LEAD-ICP-gfp5-odd-char-cover)*

**Prior-art check:** 18  LEAD-TRF-odd-prime-ghs-cover-floor           open_next_step     Odd-characteristic GHS cover genus floors at prime extension degree and their isogeny-class reach | 13  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 13  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Odd-Characteristic Cover Genus Certification for EcGFp5/EcMasFp5** **1. Exact Construction & Algorithm** * **Target Curves**: `EcGFp5` (generator curve for GF(p^5) DLP via Weil descent) and `EcMasFp5` (Masser curve, typically higher genus model). Both defined over `F_p` with prime `p ~ 2^64` (or current lab standard). * **Isogeny Class Sampling**: Compute the isogeny volcano for the conductor `N` (trace `t = p+1-#E`). Use `isogeny-labs/crypto` volcano traversal to sample a *random* curve `E_rand` in the same isogeny class (same `End(E) ⊗ Q`), distinct from the two targets. * *...

### 6. **Degree-4 Macaulay rank of double-odd 2-torsion quotient at toy p'** — run H-GFPN-6cc6aa with cofactor-1 null; if rank < generic, re-run C1 ladder at 3 primes spanning ≥ 12 bits with honest memory envelope. *(advances LEAD-ICP-gfp5-symmetrized-gaudry)*

**Prior-art check:** 12  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 6  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Curve & Quotient**: For a toy prime `p' ≈ 2^40`, select a *double‑odd* curve `E/𝔽_p'` (i.e. `#E = 4·ℓ`, `ℓ` prime). Let `G = E[2] ≅ (ℤ/2)²`. The *double‑odd 2‑torsion quotient* is the set of `x`‑coordinates of `G \ {O}` modulo the involution `x ↦ x` (trivial here) — effectively the three roots of the 2‑division polynomial `ψ₂(x)`. 2. **Polynomial System**: For the symmetrized Gaudry index‑calculus (LEAD‑ICP‑gfp5), the relation search uses the `x`‑coordinates of factor‑base points. At degree 4, build the Macaulay matrix `M₄` from the Semaev polynomial `s₅(x₁,…,...

### 7. **Boolean-native Groebner (BRiAl) with parseable d_solv + RSS watchdog on l∈{5,6}** — implement H-ICPERF-c9380d: side-classified exhaustive table as ground truth; compare WDSat vs BRiAl on descended binary PDP. *(advances LEAD-ICP-icperf-binary-pdp-solver)*

**Prior-art check:** 16  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary

**Plan (abridged; full text in `expanded-plans.md`):** **Construction/Algorithm** 1. **Ground truth generation**: For each l∈{5,6}, enumerate all factor-base elements (x-coordinates) and precompute exhaustive side-classified relation tables: for every target point T, list all decompositions T = Σ P_i with P_i in factor base, tagged by sign-pattern (side) of y-coordinates. Store as CSV: `target_x, decomposition_id, [fb_indices], side_mask`. 2. **Binary PDP formulation**: Encode each decomposition as a Boolean polynomial system over GF(2): variables `z_i ∈ {0,1}` indicate factor-base membership; equations enforce `Σ z_i·x_i = x_T` (via lookup-table...

### 8. **Complete the 17 missing arms of EXP-ECTD-0cf008 (32,768 targets each)** — finish crater/floor pairs with conductor steps 8209/131101, native vs random factor bases, verified arity-3 occupancy; report coverage + variance. *(advances LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 15  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 13  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection | 10  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: EXP-ECTD-0cf008 Completion (17 Missing Arms)** **1. Exact Construction / Algorithm** * **Target Set:** 32,768 random ECDLP instances $(P, Q=[k]P)$ on $E/\mathbb{F}_p$ ($p \approx 2^{128}$). * **Factor Bases (FB):** * *Native:* $\mathcal{F}_{nat} = \{R \in E(\mathbb{F}_p) : x(R) \in \mathcal{B}\}$ where $\mathcal{B}$ is the set of $x$-coordinates of $\mathbb{F}_p$-rational points on the 17 specific isogenous curves $E_i$ reached via $\ell=8209$ and $\ell=131101$ isogeny walks (crater/floor pairs) from $E$. * *Random:* $\mathcal{F}_{rand} \subset E(\mathbb{F}_p)$, $|\mathcal{F}_...

### 9. **Admitted polynomial successor for lattice IC relation construction** — deliver one pipeline on explicit prime cyclic subgroup (F43/F97/F101 + rank-2 F25 control) certifying density, valid roots, independent rank, complete relation cost; then four-track review. *(advances LEAD-ICP-lattice-ic-relation-construction)*

**Prior-art check:** 15  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 14  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups | 13  LEAD-ICP-full-width-arity-grid               open_blocked  

**Plan (abridged; full text in `expanded-plans.md`):** **Construction (Admitted-Polynomial Lattice IC Pipeline)** 1. **Factor Base**: $\mathcal{F} = \{ (x - \alpha_i) \mid \alpha_i \in S \}$ where $S \subset \mathbb{F}_p$ is a structured set (e.g., subgroup coset, trace-zero variety intersection, or low-height rational points). Target $|\mathcal{F}| \approx p^{1/2}$. 2. **Admitted Polynomial Successor**: Define $f_{k+1}(x) = f_k(x) \cdot g_k(x) + h_k(x) \mod (x^p - x, E_{a,b})$. $g_k$ is chosen from a lattice $\Lambda_k \subset \mathbb{F}_p[x]_{<d}$ to force $f_{k+1}$ to split over $\mathcal{F}$ with probability $\rho$. $h_k$ corrects the curve eq...

### 10. **Preregistered prime fall-degree study: stages g4, hky-A, d-A, cap-A, hky-C, hky-B, d-B** — dedicated host, multiply-add counts kept; stage A must reproduce Kummer m=2 d_F medians 3,4,4,4,4,5,5,5,5,6 at t=1. *(advances LEAD-ICP-pkm-tower-algebraic-oracle)*

**Prior-art check:** 9  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 7  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range) | 6  LEAD-EXO-curve-model-representation          closed_obst

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** Implement a staged Gröbner basis / XL fall-degree pipeline targeting the Semaev polynomial system for ECDLP over prime fields $\mathbb{F}_p$, using the PKM tower representation ($m=2$ Kummer surface) to reduce variable count. Stages: - **g4**: Generate Macaulay matrix at degree $D=4$ for the $m=2$ summation polynomial $S_3$ on the Kummer $x$-coordinates. - **hky-A / d-A / cap-A**: Apply hybrid F4 (hky), sparse $F_5$ (d), and Cap-optimized (cap) linear algebra at degree $D$ to compute the degree of regularity $d_{reg}$ and fall-degree $d_F$ median over 100 random in...

### 11. **Section 13 second-host replay of 20-bit holdout at N>45** — all 1,008 original records reproduced exactly on isolab-eks; promote to leaderboard; extend to 24-bit with same constant-engineering recipe. *(advances LEAD-ICP-prime-ic-constant-engineering)*

**Prior-art check:** 6  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class | 6  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models) | 5  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** Reproduce the *constant-engineering recipe* from Section 13 (isogeny-labs/crypto#IC-constant-engineering) for prime-field index calculus targeting the 20-bit holdout set (1,008 curves, N=46…50). The recipe fixes: 1. **Polynomial selection**: `f(x) = x^N + c_{N-1}x^{N-1} + … + c_0` where coefficients `c_i` are drawn from the pre-computed “leaderboard” distribution (Pareto-optimal for `log2(p) ≈ 20`, `N>45`). 2. **Factor base**: Degree-1 primes `π` with `Norm(π) < B = 2^{12.3}`. 3. **Relation search**: Structured sieving on `a + b·x` with `|a|,|b| ≤ 2^7`, using the c...

### 12. **Prove chart correspondence for shared divisor-coefficient circuits** — freeze k=3,4 censuses after checking ≥ 5 usable distinct x; compare per-root PKM, symmetric, quotient, Graeffe circuits; k=2 as empty squarefree-chart negative control. *(advances LEAD-ICP-shared-coefficient-membership)*

**Prior-art check:** 27  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for high-degree implicit factor-base membership | 7  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequen

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Input:** Prime $p$, factor base $\mathcal{F}$ (deg $k=3,4$), $N \ge 5$ distinct usable $x_i \in \mathbb{F}_p$ yielding split polynomials $f_{x_i}(t) = \prod_{j=1}^k (t - r_{ij})$. 2. **Circuit Construction per $x_i$:** For each root set $\{r_{ij}\}$, build four arithmetic circuits computing the divisor coefficient vector $\mathbf{c} \in \mathbb{F}_p^m$ (targeting symmetric sums or PKM basis): * **PKM:** Direct power-sum $p_\ell = \sum_j r_{ij}^\ell$ via Horner, Newton identities to $\mathbf{c}$. * **Symmetric:** Elementary symmetric polynomials $e_\ell$ via Vi...

### 13. **Macaulay ranks of digit/chained S_4 at j=0, j=1728 vs generic + coefficient-block vanishing null** — three toy primes, degree-d ranks for d=2..6; H-PFDR-df0127 + H-PFDR-6b9f1a. *(advances LEAD-ICP-xline-symmetry-special-j)*

**Prior-art check:** 6  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 6  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm | 6  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Direction 13 — Macaulay Ranks of Chained S₄ at Special j** **1. Exact Construction / Algorithm** * **Polynomial System:** Construct the *chained S₄* summation polynomial system for relation search: $S_4(x_1, x_2, x_3, x_4) = 0$ where $x_i = f_i(u_i)$ are rational functions (degree $\delta$) mapping factor base variable $u_i \in \mathbb{F}_p$ to $x$-coordinates. Use "digit" decomposition: $u_i = \sum_{k=0}^{D-1} u_{i,k} B^k$ for base $B \approx p^{1/D}$. * **Specialization:** Instantiate curve $E/\mathbb{F}_p$ at $j=0$ ($y^2 = x^3 + b$) and $j=1728$ ($y^2 = x^3 + ax$). Compare...

### 14. **Simulation lemma for class-group action in curve-aware GGM** — write/review H-CLGP-63f471: show ECDLP still needs Ω(√N) group ops when adversary gets free class-group action on curves; quantifier order + size-gap argument (h~p^{1/2} vs N). *(advances LEAD-STR-class-group-ecdlp-bridge)*

**Prior-art check:** 10  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms | 10  KR-RHO-817bf8                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves | 9  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the ref

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Simulation Lemma for Class-Group Action in Curve-Aware GGM (H-CLGP-63f471)** **1. Construction / Algorithm: The Simulator $\mathcal{S}$** Define the **Curve-Aware Generic Group Model (CA-GGM)**. The adversary $\mathcal{A}$ receives: * Standard group oracles: `Add`, `Neg`, `Eq` for an unknown target curve $E_0/\mathbb{F}_p$ (order $N \approx p$). * **Class-Group Action Oracle $\mathcal{O}_{\text{cl}}$**: On query $(\mathfrak{a}, [P])$ where $\mathfrak{a} \in \text{Cl}(\mathcal{O})$ (represented as reduced ideal) and $[P] \in E/\mathbb{F}_p$ (handle), returns handle for $[\mathf...

### 15. **Preregistered ecbench IC study: three arms (floor-on-floor, floor→crater via 2-isogeny, crater-on-best-model)** — calibration targets for model selection, measurement on held-out; transport cost charged. *(advances LEAD-STR-class-representative-ic-selection)*

**Prior-art check:** 22  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 15  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 8  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory c

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Preregistered ecbench IC Study (Three Arms)** **1. Construction / Algorithm** * **Target:** Prime field $\mathbb{F}_p$, $p \approx 2^{128}$ (scaled to $2^{60}$–$2^{80}$ for experiment). Curve $E_0/\mathbb{F}_p$ with $N = \#E_0 = h \cdot r$ ($r$ prime). * **Factor Base $\mathcal{F}$:** $x$-coordinates of points with $x \in [0, B]$ (or $y^2 = x^3+ax+b$ smoothness bound $B$). Size $|\mathcal{F}| \approx \pi(B)$. * **Arm A (Floor-on-Floor):** Standard $x$-only Gaudry–Diem IC on $E_0$. Decompose random $R = [a]G + [b]Q$ via summation polynomials $S_{m+1}(x_1,\dots,x_m, x_R)$. Solve...

### 16. **Matched-order families: first-fall degree, F4 solve time, charged IC cost for S_3/S_4 at j=0/j=1728 vs generic** — automorphism-orbit factor base + sham-curve null of same support; fixed N per MATCHED-ORDER-DESIGN.md. *(advances LEAD-STR-special-j-ic-semaev)*

**Prior-art check:** 18  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 18  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 15  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Factor Base**: For target curve $E/\mathbb{F}_p$ with $j(E) \in \{0, 1728\}$, define factor base $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{X}\}$ where $\mathcal{X} \subset \mathbb{F}_p$ is the set of $x$-coordinates of points whose automorphism orbit size divides $|\text{Aut}(E)|$ (3 for $j=0$, 2 for $j=1728$). For generic $j$, $\mathcal{X}$ is random subset of same cardinality $N = \#\mathcal{F} \approx p^{1/2}$. 2. **Relation Generation**: Use Semaev's summation polynomials $f_m$. For $j=0,1728$, exploit symmetry: $f_m(x_1,\dots,x_m) = 0$ im...

### 17. **Even-degree Mumford arithmetic + general binary norm φ_*: Jac(H)→E** — certify subgroup order, kernel, image for each of 1,940 prime quadratic + 160 binary cubic pullback bindings. *(advances LEAD-TRF-cover-catalog-jacobian-transfer)*

**Prior-art check:** 35  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery | 12  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases | 9  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engi

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Input**: The 2,100 precomputed pullback bindings (1,940 prime-quadratic, 160 binary-cubic) from `LEAD-TRF-cover-catalog-jacobian-transfer`. Each binding defines a degree-`d` cover `φ: H → E` with `H` genus-2, `E` elliptic, `d ∈ {2,3}`. 2. **Mumford Representation**: For each `H`, implement even-degree (`d=2`) Cantor addition/doubling in projective Mumford coordinates `(U, V, W)` avoiding inversions. For `d=3` bindings, derive explicit `φ_*` via resultant-based norm: `φ_*(D) = Norm_{K_H/K_E}(D - ∞)` computed as polynomial resultant `Res_U(u_H, u_E)` evaluated a...

### 18. **Freeze numeric tolerances for JV sieve positive control (R0 S) + rho A/A rule** — re-run paired sieve vs strong-rho at p∈{1009,1511,1823} with corrected hash accounting, F4/LA additions, charged isogeny walk. *(advances LEAD-TRF-jv-sieve-fp6-weak-class)*

**Prior-art check:** 17  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class | 11  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 11  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano lev

**Plan (abridged; full text in `expanded-plans.md`):** **Construction/Algorithm** 1. **JV Sieve (R0 S)**: Factor base ℬ = {E : j(E) ∈ S₀} where S₀ = {j ∈ 𝔽ₚ : ∃E/𝔽ₚ, #E = p+1−t, |t|≤2√p}. Relations from split-curve walks: start at random E, take ℓ-isogeny steps (ℓ∈ℒ={2,3,5,7,11,13}) until j(E)∈S₀. Record relation when path length ≤ L_max=12. Use corrected hash accounting: each relation weighted by 2⁻ˡ where l = path length. 2. **Strong-Rho (A/A rule)**: Parallel distinguished-point walk on isogeny graph with step function φ(E) = [x(E) mod 3] selecting ℓ∈ℒ. Charge rule: each step costs log₂(ℓ) + 0.5 (F4/LA overhead). Collision when j(E₁)=j(E₂) and...

### 19. **Test H1 of IDEA-20261017-e3a6f1 at toy size** — equidistribution of ℓ(k)=log_g U(kP) in Z/(p-1), Smart-ratio success, correlation with Z/N characters; special + matched random p, planted-structure positive control. *(advances LEAD-TRF-miller-cocycle-nonhom-transfer)*

**Prior-art check:** 7  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier | 6  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Direction 19 — Toy-Size Test of H1 (Miller Cocycle Transfer)** **1. Exact Construction & Algorithm** * **Curve & Field:** Select a 64-bit prime `p` (toy) and `p' ≈ p` (matched random control). Generate `E/F_p` with `N = #E(F_p) = h·r` (`r` prime, `h` small). Fix generator `P ∈ E[r]`, `g ∈ F_p^*` generator. * **Planted Positive Control:** Construct `E_planted` via CM method or `r`-torsion polynomial solving such that `∃ φ: E → E'` (deg `ℓ` small) where `U = x ∘ φ` (or `f_{ℓ,P}` Miller function) yields `log_g U(kP)` with known bias (e.g., image lies in subgroup of `F_p^*` of ind...

### 20. **Implement Smith's Props 2 & 4 / trigonal construction on odd-char genus-3 descents** — test F_q-rationality and non-degeneracy on already-enumerated descents; pipeline to Diem q^{4/3}. *(advances LEAD-TRF-odd-char-descent-smith-quartic)*

**Prior-art check:** 19  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 9  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 3  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicabil

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Input:** Odd-char prime field $\mathbb{F}_q$, target elliptic curve $E/\mathbb{F}_q$, factor base $\mathcal{F} \subset E(\mathbb{F}_q)$ of smoothness bound $B \approx q^{1/3}$. 2. **Descent Enumeration:** For each $R \in \mathcal{F}$, compute the fiber $S \in \mathrm{Sym}^3(E)$ mapping to $R$ under $x$-coordinate summation (Diem’s $G_3$ descent). Filter fibers where the Mumford representation $(u(x), v(x))$ has $\deg u = 3$ and $\deg v \leq 2$. 3. **Trigonal Check (Prop 2):** For each fiber, test if the associated genus-3 curve $C: y^3 = f(x)$ (or trigonal mod...

### 21. **Run approved n=7 EXP-PEXT-212d5c plan with Lean finite lemmas** — exhaustive placement spectrum, q=3 stratified controls + q=3,5,7 census; independent check of 2-torsion floors + isogeny-walk cost accounting. *(advances LEAD-TRF-odd-prime-ghs-cover-floor)*

**Prior-art check:** 9  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls) | 8  LEAD-TRF-odd-prime-ghs-cover-floor           open_next_step     Odd-characteristic GHS cover genus floors at prime extension degree and their isogeny-class reach | 6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inve

**Plan (abridged; full text in `expanded-plans.md`):** **Construction/Algorithm** Implement the n=7 placement-exhaustion engine for odd-prime-degree ℓ-isogeny graphs over 𝔽_p (p ≈ 2^212). For each rational point placement P ∈ E(𝔽_p)[ℓ] (ℓ ∈ {3,5,7}), compute the full ℓ-isogeny volcano walk to the floor, recording: (a) 2-torsion subgroup structure at each level, (b) endomorphism ring discriminant Δ, (c) relation density ρ = #{smooth norms}/#{total norms}. Use Lean 4 to formally verify: (i) every walk terminates at a unique floor, (ii) floor 2-torsion is isomorphic to (ℤ/2ℤ)² × (ℤ/2^kℤ) with k ≥ 2, (iii) the cover map φ: E → E' induced by the walk h...

### 22. **Certified toy tower-field DLP: coprime tower splits n∈{4,5,6,8,12} + one certified log in F_121** — then small same-shape GF(p^12) calibration against published record before deployed estimate. *(advances LEAD-TRF-pairing-target-field-recost)*

**Prior-art check:** 12  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged | 9  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant | 8  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Tower definition**: For each n ∈ {4,5,6,8,12} build a coprime tower `F_p ⊂ F_{p^a} ⊂ F_{p^{ab}} = F_{p^n}` with a,b > 1, gcd(a,b)=1. Use Conway polynomials (or minimal-weight irreducibles) for each step; store the explicit embeddings. 2. **JLSV-style descent** (Joux–Lercier–Smart–Vercauteren) inside the tower: - Factor base: all degree-1 elements in the top field represented in the *bottom* basis. - Relation generation: random linear combinations of basis elements → smoothness test in the subfield `F_{p^a}` (for a|n) via norm map to `F_p`. - Individual logarit...

### 23. **Re-run 20-arm panel EXP-ECTD-0cf008 with psutil import fixed** — H-ECTD-e88346: crater/floor pairs, conductor steps 8209/131101, native vs random factor bases, verified arity-3 occupancy. *(advances LEAD-TRF-teske-secret-isogeny-trapdoor)*

**Prior-art check:** 15  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 9  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection | 8  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structur

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Volcano Setup**: For each of the 20 arms, instantiate the ℓ-isogeny volcano (ℓ=3) over 𝔽ₚ with p ≈ 2²⁵⁶, target conductor `f ∈ {8209, 131101}`. Compute crater (cyclic) and floor (depth-1) curves via `isogeny_volcano` module. 2. **Factor Bases**: - *Native*: All 𝔽ₚ-rational points on crater curves (size ≈ p). - *Random*: Uniformly sampled subsets of same cardinality. 3. **Relation Collection**: Walk arity-3 graphs from random floor curves; record (crater, floor) pairs where discrete log of target point factors over the active factor base. Use Teske’s `radding`...

### 24. **Measure public ISO-1 walk cost to nearest JV-weak curve in random F_{p^6} classes** — compare against ~1e10 attack cost; determine if any class places weak curve beyond public walk. *(advances LEAD-TRF-teske-trapdoor-fp6-weak-class)*

**Prior-art check:** 24  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class | 23  LEAD-TRF-teske-trapdoor-fp6-weak-class       open_unexamined    Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class | 19  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant

**Plan (abridged; full text in `expanded-plans.md`):** **Construction / Algorithm** 1. **Parameter selection**: Fix a 256-bit prime `p ≡ 3 mod 4` (e.g., `p = 2^256 − 189`). Work in `F_{p^6} = F_p[u]/(u^6 − ξ)` with `ξ` a quadratic non-residue in `F_{p^2}`. Use the `l = 2`-isogeny graph on supersingular `j`-invariants (or `(a,b)`-models for Montgomery curves). 2. **JV-weak class definition**: A curve `E/F_{p^6}` is *JV-weak* iff its endomorphism ring contains an order `O` with `disc(O) = disc(End(E)) / D^2` where `D` is `B`-smooth (`B = 2^16`) and `O` admits an explicit `B`-smooth isogeny to a curve with known endomorphism ring (e.g., `j = 0` or `1...

### 25. **n=2 control + exhaustive n=3 point-count census for q=2,3** — fixed-seed higher-q samples; require explicit F_q-isogeny of controlled degree before pricing DLP route. *(advances LEAD-TRF-weil-restriction-jacobian-class)*

**Prior-art check:** 7  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 7  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Direction 25 — Weil Restriction Census & Isogeny-Gated Index Calculus** **Construction / Algorithm** 1. **Base setup**: Fix prime `p ≈ 2^64` (large enough for non-trivial DLP, small enough for exhaustive census). Work over `F_{p^2}` and `F_{p^3}`. 2. **Weil restriction**: For every elliptic curve `E/F_{p^n}` (`n=2,3`), compute `Res_{F_{p^n}/F_p}(E)` — an abelian variety of dimension `n` over `F_p`. For `n=2`, this is a genus-2 Jacobian (or product of elliptic curves); for `n=3`, dimension-3 abelian variety. 3. **Exhaustive n=2 control**: Enumerate all `E/F_{p^2}` up to `F_p`-i...

### 26. **Measure digit-character family (IDEA-20260921-1ec106) for (λ, PGL_2-stability)** — against PGL_2-orbit-matched null at census sizes 2^20-2^26; one natural candidate never measured. *(advances LEAD-EXO-coordinate-statistic-leakage)*

**Prior-art check:** 7  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases | 7  LEAD-RHO-best-of-candidates-indegree         open_next_step     Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree | 7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed s

**Plan (abridged; full text in `expanded-plans.md`):** **Construction & Algorithm** Define the *digit-character family* $\chi_{b,k}: \mathbb{F}_p \to \mathbb{C}^\times$ by $\chi_{b,k}(x) = \exp(2\pi i \cdot \text{digit}_b(x; k) / b)$, where $\text{digit}_b(x; k)$ extracts the $k$-th base-$b$ digit of the canonical integer representative of $x \in [0, p-1]$. For a target curve $E/\mathbb{F}_p$ and factor base $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{I}\}$ (interval $\mathcal{I}$ of size $\approx p^{1/3}$), compute the **stability statistic** for parameter $\lambda$ (Möbius transform $x \mapsto (ax+b)/(cx+d)$): $$S(\lambda) = \frac...

### 27. **Measure relative bucket variance W of O2 agreement kernel (H-ECDLP-2ade73)** — across N, fit decay vs 1/√N; EXP-ECDLP-5cad48 never assigned W class. *(advances LEAD-EXO-four-list-ktree-join)*

**Prior-art check:** 11  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class | 9  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks | 7  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Relative Bucket Variance W of O2 Agreement Kernel** **1. Exact Construction / Algorithm** * **O2 Agreement Kernel ($K_{O2}$):** For a fixed factor base $\mathcal{F}$ of size $N$, define the $O2$ relation set $\mathcal{R} = \{(u,v) \in \mathcal{F}^2 : u+v \in \mathcal{F} \}$. Partition $\mathcal{F}$ into $B = \lceil \sqrt{N} \rceil$ buckets $\mathcal{B}_i$ via $x$-coordinate interval hashing (width $\approx p/N$). * **Bucket Weight ($w_i$):** For bucket $\mathcal{B}_i$, compute $w_i = |\{(u,v) \in \mathcal{R} : u \in \mathcal{B}_i \lor v \in \mathcal{B}_i \}|$. * **Relative Var...

### 28. **Time T_section(d,χ,p) for bounded-height section through prescribed fibre on E1 surfaces** — ≥3 primes, random-system Groebner control; IDEA-20261009-581f5d. *(advances LEAD-EXO-global-lift-height)*

**Prior-art check:** 11  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces) | 7  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t) | 6  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, bel

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Bounded-Height Section Timing on E1 Surfaces (Dir. 28)** **1. Construction / Algorithm** Target: Compute a section $s: \mathbb{P}^1 \to \mathcal{E}$ of an elliptic surface $\mathcal{E}/\mathbb{F}_p$ (E1: $j$-map degree 1) passing through a prescribed fibre $E_t$, with logarithmic height $h(s) \leq B$. * **Model:** $\mathcal{E}: y^2 = x^3 + A(t)x + B(t)$, $\deg A \leq 4, \deg B \leq 6$. Section $s(t) = (x(t), y(t))$, $\deg x \leq 2, \deg y \leq 3$. * **Constraint System:** Enforce $s(t_0) = P_{target} \in E_{t_0}$ and $y(t)^2 \equiv x(t)^3 + A(t)x(t) + B(t) \pmod{p}$. * **Gröbn...

### 29. **Independent audit of hashed-factor-base ECDL correctness + complexity proof** — check if LEAD-ICB-decomposition-encoding-and-sat obstruction applies to Akshima/Bochum encoding; #SAT exponent vs enumeration. *(advances LEAD-EXO-hashed-factor-base-tensor-ecdl)*

**Prior-art check:** 10  LEAD-EXO-hashed-factor-base-tensor-ecdl      open_next_step     Hashed-factor-base ECDL with a compact low-degree Boolean encoding and exact tensor contraction (Akshima et al., Bochum v0.2), conditional on the openai/math #k-SAT result | 5  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Audit of Hashed Factor Base ECDL via Akshima/Bochum SAT Encoding** **1. Construction / Algorithm** Target curve: $E/\mathbb{F}_p$, $p \approx 2^n$. Factor base $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{H}\}$ where $\mathcal{H} \subset \mathbb{F}_p$ is a hash-defined set $|\mathcal{H}| = p^\alpha$, $\alpha \in (0,1)$. Relation search: find $a,b$ such that $aG + bT = \sum_{i=1}^m P_i$, $P_i \in \mathcal{F}$. Decomposition problem: given $R \in E(\mathbb{F}_p)$, find $m$-tuple $(P_1,\dots,P_m) \in \mathcal{F}^m$ summing to $R$. Encode as SAT via **Akshima/Bochum*...

### 30. **Price Thue-Morse/Rudin-Shapiro conversion (H-ECDLP-a4be60) once nonzero log-bit advantage exists** — exponent 2β vs 1/2, memory/cost table; IDEA-20260904-f68c7f. *(advances LEAD-EXO-hnp-advice-leakage)*

**Prior-art check:** 9  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice | 7  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps | 6  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Price Thue-Morse/Rudin-Shapiro Conversion for HNP Advantage Amplification** **1. Exact Construction / Algorithm** *Target*: Given an ECDLP instance $Q = [k]P$ over $\mathbb{F}_p$, and an oracle $\mathcal{O}$ returning MSB$_k$ (or LSB$_k$) with advantage $\epsilon = 2^{-\beta}$ ($\beta < \log_2 p$), recover $k$ in subexponential time $L_p[1/2, c]$ beating Pollard's Rho ($L_p[1/2, 1/2]$). *Algorithm (Price Sequence Sieve)*: 1. **Basis Generation**: Construct $m \approx p^{1/2}$ linear relations $k \equiv \sum_{i=1}^n a_i x_i \pmod p$ using a **Thue-Morse (TM)** sequence for coef...

### 31. **Supply named constructors/theorems for 15 active IDEA registry rows** — start with IDEA-012 (finite-deck weighted endpoint, REVISE_SCOPED_REDUCTION); run zero-compute contract preflight. *(advances LEAD-EXO-ideas-corpus-algebraic-transforms)*

**Prior-art check:** 5  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness | 4  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows) | 3  LEAD-ICP-coppersmith-smallroot-semaev        closed_obstructed  Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describab

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: IDEA-012 Finite-Deck Weighted Endpoint (REVISE_SCOPED_REDUCTION)** **1. Named Constructor & Theorem** Define `FiniteDeckWeightedEndpoint(𝔽_p, E, 𝒟, w, ℛ)` where: - `𝒟 = {D_1,…,D_m} ⊂ E(𝔽_p)` is a fixed “deck” of divisor representatives. - `w: 𝒟 → ℝ_{>0}` assigns a cost weight (e.g., `w(D) = log ‖ψ(D)‖` for a chosen isogeny `ψ`). - `ℛ: Div^0(E) → 𝒟^*` is a *scoped reduction* mapping any degree‑0 divisor to a multiset of deck elements, satisfying: (i) `supp(ℛ(D)) ⊆ 𝒟`, (ii) `∑_{D_i∈ℛ(D)} n_i D_i ∼ D` (linear equivalence), (iii) `cost(ℛ(D)) = ∑ n_i w(D_i) ≤ C·h(D)` for explicit c...

### 32. **Measure A(1) and A(d) (max agreement of deg-d polys with log graph Γ_E) on toy ladder** — against random-labelling null; H-ECDLP-f6a43a cell never measured. *(advances LEAD-EXO-invertible-hint-subset)*

**Prior-art check:** 6  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO) | 6  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases | 6  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Direction 32 — Measure A(1) and A(d) on Toy Ladder** **1. Exact Construction / Algorithm** * **Toy Ladder Setup:** Fix a small prime `p` (e.g., `p ≈ 2^16`) and an elliptic curve `E/F_p` with smooth order `#E = ∏ q_i^{e_i}`. Construct the "ladder" graph `G`: vertices `V = E(F_p)`, edges `(P, Q)` iff `Q = P ± R_j` for a fixed small basis `R_j` (e.g., `j=1..k`, `k=4`). * **Log-Graph `Γ_E`:** Assign discrete log labels `ℓ(P) ∈ Z/#E` relative to a generator `G`. Target function `f: V → Z/#E`, `f(P) = ℓ(P)`. * **Agreement Metric `A(d)`**: For degree `d ∈ {1, 2, 3}`, define the hypot...

### 33. **Run disjoint projection panel of IDEA-20260817-84755b in probabilistic regime** — exact-arithmetic fibre tests (KN-FIND-7d098b caveat) + random-relabelling null. *(advances LEAD-EXO-lossy-object-propagation)*

**Prior-art check:** 3  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces) | 3  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 3  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator 

**Plan (abridged; full text in `expanded-plans.md`):** **Research Plan: Disjoint Projection Panel in Probabilistic Regime (IDEA-20260817-84755b)** **1. Construction / Algorithm** * **Factor Base:** Define $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{V}\}$ where $\mathcal{V} \subset \mathbb{F}_p$ splits completely under $m$ disjoint rational projection maps $\pi_i: E \dashrightarrow \mathbb{P}^1$ (e.g., $x$-coordinate, $x+\lambda$, isogenous $x$-maps from low-degree $\phi_i$). * **Relation Generation (Probabilistic Regime):** For random $a,b \in \mathbb{Z}$, compute $R = aG + bT$. Decompose $R = \sum_{j=1}^k P_j$ using Semaev’s $m$-th...

### 34. **Inject 3 planted-signal families (IDEA-20260807-efc8de) into real pipeline** — replay every ECDLP mechanism screen against synthetic positives (IDEA-20260815-bc26a3); measure false-negative rate. *(advances LEAD-EXO-methodology-instruments)*

**Prior-art check:** 13  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 7  LEAD-EXO-cryptoscale-candidate-screen        exhausted_at_scale GOAL-CRYPTO-001 discovery screen for a reproducible non-generic crypto-size algorithm

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and repository audit - Freeze commits of `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher`. Locate IDEA-20260807-efc8de, IDEA-20260815-bc26a3, and LEAD-EXO-methodology-instruments; extract the **actual three signal generators**, prior results, rejected variants, screening thresholds, and configurations. Repository contents are not available here; do not assume the families’ definitions. - Inventory every ECDLP mechanism screen, including abandoned implementations. Map each to its input stage, claimed detectable signal, acceptance threshold, and smallest previou...

### 35. **Verify K1 (Weil-reciprocity cocycle) + K2 (U(kP)=c·r_k·C^{k/N}) on toy prime-order curves** — gcd(N,p-1)=1; measure if k recoverable from U(kP) in <√N group ops once r_k charged. *(advances LEAD-EXO-miller-pairing-cocycle)*

**Prior-art check:** 12  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves | 11  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 10  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups

**Plan (abridged; full text in `expanded-plans.md`):** 1. **Audit prior work before claiming novelty.** Inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for `LEAD-EXO-miller-pairing-cocycle`, Weil reciprocity, Miller functions, carry terms, and character extraction. Record commit/file references, tested identities, charged costs, and negative results. Repository contents were not provided here; this review remains a prerequisite. 2. **Exact construction.** Choose \(E/\mathbb F_p\), \(P\) of prime order \(N\), with \(\gcd(N,p-1)=1\). Let \[ \operatorname{div}(f_m)=m[P]-[mP]-(m-1)[O], \qquad d=N^{-1}\pmod{p-1}. \] For an auxiliary \(T\), de...

### 36. **Learnability control on toy prime-order groups: predict log bit from coordinates** — planted homomorphic leak positive control + random-relabelling null at N≤2^24; parallel ec_hardness_predictor phases 0-3. *(advances LEAD-EXO-ml-learned-models)*

**Prior-art check:** 11  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines | 9  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 9  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup

**Plan (abridged; full text in `expanded-plans.md`):** **Hypothesis.** Coordinate-based models predict a balanced scalar-log bit on unseen points more efficiently than generic discrete-log recovery; planted leakage and random relabelling distinguish genuine signal from pipeline artifacts. **Phase 0 — prior-work audit.** Inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `ec_hardness_predictor`, `LEAD-EXO-ml-learned-models`, coordinate classifiers, leakage controls, and failed runs. Record commit, construction, splits, seeds, compute, and outcome in a deduplication table. Repository contents are unavailable here; this audit...

### 37. **Replace per-step cswaps in binary-GCD inverse with safegcd/jump-GCD** — narrow apply + ipmul/quotient phases; validate on full input space, not Fiat-Shamir island. *(advances LEAD-EXO-quantum-ecdlp-resources)*

**Prior-art check:** 5  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 4  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice | 4  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Implement coherent, fixed-schedule **batched divsteps** for inversion modulo an odd prime \(p\), with \(n=\lceil\log_2p\rceil\). Initialize \((\delta,f,g)=(1,p,x)\). Each divstep uses \[ (\delta',f',g')= \begin{cases} (1-\delta,g,(g-f)/2),&\delta>0,\ g\text{ odd},\\ (1+\delta,f,(g+(g\bmod2)f)/2),&\text{otherwise}. \end{cases} \] For blocks of \(b\) steps, reversibly derive the integer transition matrix \(M\) from \(\delta\) and the low \(b+1\) bits of \(f,g\); apply \[ (f',g')^T=2^{-b}M(f,g)^T \] once to full-width registers. Track coefficients \(a,c\) satisfying \(f\equiv ax,...

### 38. **Replicate EV-ECDLP-f6b3f5 re-scoped support (T_sel∈{0.65T,0.75T}) on EC walk at N=2^30** — independent implementation; repair fixture_gate_v2 for basin instrument (EV-ECDLP-31e91c failed). *(advances LEAD-RHO-advice-table-variants)*

**Prior-art check:** 9  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 6  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps | 6  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and replication gate - Obtain **EV-ECDLP-f6b3f5**, **EV-ECDLP-31e91c**, `fixture_gate_v2`, and **LEAD-RHO-advice-table-variants** from `isogeny-labs/crypto` and `crypto-autoresearcher`. Review linked experiments, failed controls, selection rules, and accounting conventions; produce an overlap matrix before coding. Repository contents are unavailable here, so prior findings remain unverified. - Freeze the original definitions of \(T\), \(T_{\rm sel}\), “support,” and “basin.” Independently implement the recorded walk and advice construction, without importing experimental code....

### 39. **Build best-of-P±R into gpu/nist kernel at W=16-32 walks/thread** — kernel's own inversion + fruitless-cycle escape; paired rate + steps-to-collision vs shipping kernel on P-256 with DP-corpus replay. *(advances LEAD-RHO-best-of-candidates-indegree)*

**Prior-art check:** 8  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves) | 6  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 6  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device an

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - First audit `isogeny-labs/crypto`, its cryptanalysis work, and `crypto-autoresearcher` for best-of-candidate, indegree, batching, cycle-escape, and DP-replay experiments. Record commits, parameters, negative results, and reproducibility; repository access is required before claiming novelty. - Target P-256’s prime-order subgroup, with \(Q=dG\). Track \(P=aG+bQ\). - Define one globally shared, deterministic transition. Set \(j=h_0(P)\bmod m\), with precomputed \(R_j=u_jG+v_jQ\). Form \(C_\pm=P\pm R_j\), score both using an independently seeded point hash, and choose the lower...

### 40. **Port tag-tracing r-adding walk to 64-bit prime toy curve in rho_walk_leads harness** — ns/step paired vs plain step at 8-1024 walks/inversion, steps/collision with DP replay; also halving-step on sect113r1-size binary. *(advances LEAD-RHO-cheaper-step-primitives)*

**Prior-art check:** 16  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing

**Plan (abridged; full text in `expanded-plans.md`):** **Construction.** First audit `isogeny-labs/crypto` and `crypto-autoresearcher` for tag-tracing, paired affine addition, batch inversion, DP replay, and point-halving experiments. Record commit IDs, parameters, negative results, and reusable code; repository contents are unavailable here, so novelty remains unverified. Use a nonsingular short-Weierstrass curve over a 64-bit prime, with a verified large prime-order subgroup. Implement in `rho_walk_leads`: - Plain \(r=16\) adding walk: \(P\leftarrow P+R_{h(P)}\), with canonical-coordinate hashing and coefficient tracking \(P=aG+bQ\). - Speculati...

### 41. **Approve revised protocol for typed quantity H-AUXIN-6db354 (per-branch, supply-capped E(r))** — join completed census RUN-AUXIN-fd1edc with supply roster IDEA-20260930-68326c under cap. *(advances LEAD-RHO-cheon-deployed-applicability)*

**Prior-art check:** 11  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply | 4  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law | 3  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction / approval gate Treat **H-AUXIN-6db354** as a conditional protocol approval, not a validated speedup. Repository contents were not supplied; reviewing the named artifacts and prior experiments is a prerequisite. 1. Inspect `isogeny-labs/crypto` cryptanalysis records and `crypto-autoresearcher` for RUN-AUXIN-fd1edc, IDEA-20260930-68326c, and prior Cheon/auxiliary-input tests. Record commit hashes, configurations, negative results, and duplicate hypotheses. 2. Normalize census and roster into typed records: curve, prime subgroup order \(\ell\), generator \(P\), target \(Q=[x]P\)...

### 42. **Run EXP-AUXIN-25a29a end-to-end (56-bit r, divisor 65536, stage counts + gain fractions)** — recovered scalars certified, memory/DP costs reported beside ρ on same group. *(advances LEAD-RHO-cheon-toy-reproduction)*

**Prior-art check:** 6  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor | 6  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models) | 5  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions und

**Plan (abridged; full text in `expanded-plans.md`):** **Construction and provenance.** First locate EXP-AUXIN-25a29a and LEAD-RHO-cheon-toy-reproduction in `isogeny-labs/crypto`, the cryptanalysis materials, and `crypto-autoresearcher`. Record commit hashes, parameters, previous outcomes, and unresolved failures; inspect implementations rather than relying on summaries. Repository contents are unavailable here, so prior results remain unverified. Use the experiment’s exact prime-field curve, point \(P\) of prime order \(r\), and \(d=65536\). Require \(2^{55}\le r<2^{56}\), \(d\mid r-1\), and certified point order. For uniformly sampled nonzero \(...

### 43. **Build + pair TABLE_PHASE_POPC (phase via popc planes) vs 15.88 B/s sigma-table control** — one RTX PRO 6000, identical sorted DP corpora, 300-report re-walk gate. *(advances LEAD-RHO-ecc2k130-gpu-fpga-throughput)*

**Prior-art check:** 14  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks | 10  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 7  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion 

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Implement **TABLE_PHASE_POPC** as an exact alternative encoding of the existing phase/sigma lookup—not a new walk. For the control’s \(N\)-entry phase table \(T\), with \(q\)-bit outputs, construct: \[ P_{k,j}=\sum_{r=0}^{31}\left((T[32j+r]\gg k)\&1\right)2^r, \] padding the final word with zeros. For bucket \(b\), recover: \[ T[b]=\sum_{k=0}^{q-1}2^k\,\operatorname{popc} \left(P_{k,b\gg5}\ \&\ (1_u\ll(b\&31))\right). \] Preserve bucket extraction, point arithmetic, sigma interpretation, distinguished-point predicate, and reporting exactly. Use read-only cached planes initiall...

### 44. **Measure v3 table-walk kernel paired rate vs fused sigma-table control** — 5 alternating pairs A/A drift + planted-log + re-walk gate; price iterations × rate per solve for sigma, SIGMA_SIGN=2, table-v3. *(advances LEAD-RHO-ecc2k130-iteration-function)*

**Prior-art check:** 13  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt) | 10  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 8  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and prior-work gate - Review `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for `LEAD-RHO-ecc2k130-iteration-function`, table-v3, fused sigma-table, `SIGMA_SIGN=2`, and previous timing/correctness reports. Record commits, rejected variants, iteration definitions, and hardware. **Repository access is unavailable here; this review remains a prerequisite, not a completed claim.** - Freeze the existing group, partition function, table generation, distinguished-point predicate, and collision solver. Compare **A:** fused sigma-table control; **B:** table-v3 walk k...

### 45. **Run EXP-GRUMPY-eb8675 (certified exhaustive ladder Z/l 2^10..2^20)** — covered-set counter vs per-target simulation, negation map separate arm; file evidence for EXP-GRUMPY-cd7b82 Stage 1. *(advances LEAD-RHO-grumpy-store-all-schedules)*

**Prior-art check:** 8  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 6  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw) | 6  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)

**Plan (abridged; full text in `expanded-plans.md`):** **EXP-GRUMPY-eb8675 — certified exhaustive ladder** **Construction.** Work in the additive surrogate \(G=\mathbb Z/\ell\mathbb Z\), with \(P=1\), target \(Q=xP\), and \(\ell_k=\operatorname{nextprime}(2^k)\), \(k=10,\ldots,20\). Freeze each candidate’s deterministic, target-independent coefficient schedule \(S=((a_i,b_i))\), representing stored points \(a_iP+b_iQ\). Preserve insertion order, stopping rules, and duplicate-handling policy. For every pair \(i<j\) with \(b_i\ne b_j\), the collision covers exactly \[ x=(a_i-a_j)(b_j-b_i)^{-1}\pmod\ell. \] Maintain an exact bitmap of covered targets...

### 46. **Run EXP-LHW-9adf78 (residue-guess price on W(m,w) with Mersenne/Fermat M)** — or write proof obligation of H-LHW-371a91 as checked derivation. *(advances LEAD-RHO-lhw-modular-filter-price)*

**Prior-art check:** 4  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups | 2  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300 | 2  LEAD-RHO-cheon-aux-acquisition               closed_obstructed  Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourse

**Plan (abridged; full text in `expanded-plans.md`):** **EXP-LHW-9adf78: measure the full price of residue filtering** 1. **Recover definitions and prior results.** Search `isogeny-labs/crypto`, cryptanalysis materials, and `crypto-autoresearcher` for `EXP-LHW-9adf78`, `H-LHW-371a91`, `LEAD-RHO-lhw-modular-filter-price`, and `W(m,w)`. Record commit hashes, tested parameters, negative results, and unresolved assumptions. Repository contents are unavailable here; do not treat the construction below as their verified definition. 2. **Exact construction.** Provisionally define \[ W(m,w)=\{a\in[0,2^m):\operatorname{popcount}(a)=w\}. \] Replace this wit...

### 47. **Re-run EXP-LHW-b49bc6 Stage 1 with checkpointed sumset counts + run length inside claim TTL** — hash-realisable jump sums on frozen (m,w) ladder m∈{20,24}; score E1 vs E2. *(advances LEAD-RHO-lhw-polymem-collision-walks)*

**Prior-art check:** 7  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks | 4  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - First retrieve **EXP-LHW-b49bc6 Stage 1**, **LEAD-RHO-lhw-polymem-collision-walks**, and related tests from `isogeny-labs/crypto` and `crypto-autoresearcher`. These repositories are unavailable here, so prior results and E1/E2 definitions remain unverified. Extract commit IDs, frozen \(w\)-values, jump construction, hash-to-jump mapping, seeds, scoring formulas, and claim TTL; stop if these cannot be recovered. - Reproduce the frozen ladder for \(m\in\{20,24\}\), without parameter retuning. Let \(D_{m,w}\) be its admissible jump-label domain and \(J:D_{m,w}\to E(\mathbb F_p)...

### 48. **Price two incumbent rows of IDEA-20260930-79abd9 at m∈{32,40} in group ops** — Coppersmith-split advice tables + weight-restricted BL table; measure one with planted low-weight logs. *(advances LEAD-RHO-lhw-preprocessing-frontier)*

**Prior-art check:** 19  LEAD-RHO-lhw-preprocessing-frontier          open_unexamined    Low-weight DLP with preprocessing: the (P, S, T, epsilon, U) frontier | 12  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables | 11  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks

**Plan (abridged; full text in `expanded-plans.md`):** 1. **Recover and freeze the incumbents.** Repository contents are unavailable here; do not treat either method as previously verified. In `isogeny-labs/crypto` and `crypto-autoresearcher`, locate `IDEA-20260930-79abd9`, `LEAD-RHO-lhw-preprocessing-frontier`, and related negative results. Record commit hashes, both row definitions, the meaning of \(m\), advice-reuse assumptions, and whether “BL” means Bernstein–Lange. Reproduce their smallest published test before extending it. The construction below assumes \(m\) is the scalar bit length; revise if the records disagree. 2. **Exact construction...

### 49. **Seal ecbench bounds for ρ.negation, ρ.plain, bsgs.negation on prime curves at log2 r 32-48** — ≥24 runs/size, replay certs, section 5a band; fit R(N)=1+c/N^β to toy-to-medium ratio (H-ECDLP-ff38dc). *(advances LEAD-RHO-matched-rho-calibration)*

**Prior-art check:** 10  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw) | 9  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 7  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and prior-work audit - Check out and record commit hashes for `isogeny-labs/crypto`, its cryptanalysis work, and `crypto-autoresearcher`. Search for `H-ECDLP-ff38dc`, `LEAD-RHO-matched-rho-calibration`, `ecbench`, negation walks, replay certificates, and “section 5a.” Build a ledger of tested configurations, failures, counters, and unresolved discrepancies before introducing changes. Repository contents are not available here; this review remains a required execution step. - Freeze three implementations: plain Pollard ρ; negation-quotient ρ with canonical representatives and e...

### 50. **Price Koblitz canonicaliser in field-mul equivalents: EXP-CERTBIN-b4d29c at n=131** — design C (canonicalise every step) vs Bailey sigma (normalise only at DPs) + rotation-invariant polynomial key IDEA-20261015-2d8e5a; callgrind Ir. *(advances LEAD-RHO-native-step-cost)*

**Prior-art check:** 17  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 9  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - Reproduce `EXP-CERTBIN-b4d29c` at \(n=131\). First inspect both repositories for its implementation, parameters, prior results, Design C, Bailey sigma, and `IDEA-20261015-2d8e5a`; record commit hashes and distinguish tested results from proposals. These artifacts are not available in this conversation. - Treat this as a **binary-field Koblitz rho cost experiment**, not prime-field index calculus. Any transfer to the latter requires separate evidence. - On the recorded prime-order subgroup, implement matched walkers using identical arithmetic, partitions, seeds, and distingui...

### 51. **Prove/refute H-EWALK-29cb90 per-step canonicalisation bound** — show for h=|H|>6 on ordinary prime-field curves any canonicaliser costs Ω(log h) group ops/step (charged gain ≤1); search encoding for non-constant H-invariant at h~N^{1/3} on toy curves (exhaustive). *(advances LEAD-RHO-non-automorphism-equivalence)*

**Prior-art check:** 18  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^* | 12  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition | 10  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm

**Plan (abridged; full text in `expanded-plans.md`):** **Target and prior-work check.** Treat H-EWALK-29cb90 as unverified. The repositories are not available here, so no prior-test review can be claimed. Before implementation, search both repos for `H-EWALK-29cb90`, `LEAD-RHO-non-automorphism-equivalence`, canonicalisation, quotient walks, invariant encodings, and preprocessing; record tested constructions, cost conventions, and counterexamples. **Exact construction.** First specify the action of \(H\); cardinality alone does not define canonicalisation. For the concrete translation action, choose ordinary \(E/\mathbb F_p\), \(N=\#E(\mathbb F_p)\...

### 52. **Measure trap rate on real campaign curve at production DP density** — before enabling negation-class walk (ecc-challenges PR #56); test CUDA path on GPU; design Koblitz Frobenius class walk (further √m). *(advances LEAD-RHO-pool-class-quotient)*

**Prior-art check:** 18  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 14  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0 | 12  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) 

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - **Repository gate:** inspect `isogeny-labs/crypto`, `cryptanalysis`, and `crypto-autoresearcher` for negation/Frobenius quotient walks, fruitless-cycle mitigation, GPU benchmarks, and production distinguished-point (DP) settings. Record commit IDs, tested hypotheses, and outcomes before proposing variants. Repository contents were not supplied here; prior-test coverage remains unverified. - Reproduce ecc-challenges PR #56 against its parent commit using the **actual campaign curve, subgroup, jump table, and production DP density** \(\theta\). - Maintain \(X=aP+bQ\). Canonica...

### 53. **Run gpu-match workload on CUDA host with qualified traffic telemetry** — interleaved CPU/GPU repeats with A/A controls, then matched P-256 toy-to-medium ladder in ecbench.gae. *(advances LEAD-RHO-prime-gpu-rho)*

**Prior-art check:** 6  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier | 6  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison | 5  LEAD-RHO-bsgs-family-memory                  closed_known       Baby-step giant-step family (textbook, interleaved, negation, paired, signed-Frobenius claw)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and prior-work gate - Audit `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for `gpu-match`, `ecbench.gae`, and `LEAD-RHO-prime-gpu-rho`: record commits, tested hypotheses, kernels, parameters, negative results, and unresolved telemetry issues. Repository contents are unavailable here; do not claim novelty until this audit is complete. - Freeze the existing `gpu-match` semantics. CPU and GPU receive identical seeded records, table occupancy, duplicate frequency, and hit/miss distributions; compare canonicalized outputs bit-for-bit. - Connect matching to disti...

### 54. **Hybrid FAM-1 + digit-presentation: use digit decomposition to generate FAM-1 seeds** — run digit-presented S_3 at m=2 to produce candidate x-coordinates, filter by FAM-1 membership polynomial; measure yield vs pure FAM-1 at 24/28/32 bits. *(variant of LEAD-ICP-coincidence-harvest-structured-base + LEAD-ICP-digit-presentation-solving-degree; differs: uses digit system as FAM-1 seed generator, not standalone decomposition)*

**Prior-art check:** 15  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks | 10  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit prerequisite:** inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for FAM-1, digit-presented \(S_3\), and both cited leads. Record commit hashes, constructions, tested parameters, negative results, and timings. Repository contents are unavailable here; prior coverage remains unverified. 2. Reuse the audited FAM-1 factor base \(\mathcal F\) and its exact membership polynomial \(M_{\mathcal F}(x)\). Do not modify the family to improve results. 3. For random targets \(R=[a]P+[b]Q\), solve \[ S_3(x_1,x_2,x(R))=0,\qquad x_i=\sum_{j=0}^{k-1}B^jd_{ij}\pmod p, \] wi...

### 55. **Isogeny-transported FAM-1 base: walk volcano to curve where FAM-1 geometry has maximal κ_rel** — use EXP-ECTD-0cf008 crater/floor data to select target curve; transport FAM-1 factor base via isogeny; charge transport cost; measure net κ_rel. *(advances LEAD-ICP-isogeny-transported-relation-yield + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 26  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 23  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 17  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. Audit `EXP-ECTD-0cf008`, FAM-1 implementations, and both named leads in `isogeny-labs/crypto` and `crypto-autoresearcher`. Extract curve parameters, crater/floor paths, relation definitions, timings, and previously rejected variants. Repository contents are unavailable here; novelty and prior results remain unverified. 2. Fix \(E/\mathbb F_p\), prime-order subgroup \(G=\langle P\rangle\) of order \(r\), target \(Q\), and the existing FAM-1 base \(B\). From the recorded volcano, select candidate curves \(E_i\) reached by explicit isogenies \(\phi_i\) of degree coprime to \(r...

### 56. **Lattice-assisted FAM-1 relation generation: use Coppersmith on FAM-1 membership polynomial** — despite Ryan 2025 bound, test if FAM-1's specific algebraic structure (low-degree parameterization) allows beating generic bound at m=3,4; toy primes 16-32 bits with positive controls. *(variant of LEAD-ICP-coppersmith-smallroot-semaev; differs: applies to FAM-1's specific parameterized locus, not generic Semaev)*

**Prior-art check:** 19  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets) | 13  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems | 10  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recogniza

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit before implementation:** inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for FAM-1 definitions, `LEAD-ICP-coppersmith-smallroot-semaev`, lattice configurations, and negative results. Record commit hashes and reproduce the closest baseline. Repository contents are not available here; novelty remains unverified. 2. Use the **actual FAM-1 parameterization**, not an invented surrogate. If its x-coordinate is \(\phi(t)=a(t)/b(t)\), define \[ F_R(\mathbf t)=\operatorname{num}f_{m+1} (\phi(t_1),\ldots,\phi(t_m),x(R))\pmod p, \] for \(m=3,4\), wher...

### 57. **PKM-tower on isogeny volcano: use isogeny chain as tower levels instead of Kummer** — each 2-isogeny step gives new curve; factor base = union of small-x bases across chain; relations from multi-curve Semaev; test at conductor steps 8209/131101. *(variant of LEAD-ICP-pkm-tower-algebraic-oracle; differs: tower = isogeny chain, not Kummer; uses existing volcano census data)*

**Prior-art check:** 26  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 26  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 21  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-le

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Work on an ordinary curve \(E_0/\mathbb F_p\) with prime-order subgroup \(G=\langle P\rangle\), odd order \(r\), and target \(Q\). 1. Select a rational \(2\)-isogeny chain \[ E_0\xrightarrow{\psi_1}E_1\rightarrow\cdots\rightarrow E_L. \] Let \(\Phi_i:E_i\to E_0\) be the reversed dual chain. Its restriction to the order-\(r\) subgroup is invertible. 2. On each \(E_i\), choose a small coordinate set \(S_i\) and signed representatives \[ B_i=\{R\in E_i(\mathbb F_p)[r]:x(R)\in S_i\}/\{\pm1\}. \] Transport them to \(E_0\); deduplicate \(\bigcup_i\Phi_i(B_i)\). These images—not sepa...

### 58. **Special-j digit presentation: j=0/j=1728 automorphisms reduce digit-system variables** — exploit x→ζx symmetry to fold digit equations; measure first-fall degree vs generic j at m=2,3 on matched-order families. *(advances LEAD-ICP-digit-presentation-solving-degree + LEAD-STR-special-j-ic-semaev)*

**Prior-art check:** 16  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks | 9  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 8  LEAD-STR-special-j-ic-semaev              

**Plan (abridged; full text in `expanded-plans.md`):** **Construction.** Work over \(\mathbb F_p\), \(p>3\), with: - \(E_0:y^2=x^3+b\), \(p\equiv1\pmod3\), automorphism \(\phi(x,y)=(\zeta_3x,y)\), invariant \(u=x^3\); - \(E_{1728}:y^2=x^3+ax\), \(p\equiv1\pmod4\), automorphism \(\phi(x,y)=(-x,iy)\), invariant \(u=x^2\). Use a prime-order subgroup stable under \(\phi\); determine \(\lambda\) with \(\phi(P)=[\lambda]P\). Define a factor base by bounded binary-digit presentations \(u=\sum_{j=0}^{t-1}2^jd_j\), \(d_j(d_j-1)=0\), retaining liftable subgroup points and storing orbit representatives. For target \(R\), seek \(m=2,3\) orbit representatives...

### 59. **Miller cocycle + FAM-1: use U(kP) as filter for FAM-1 decompositions** — if U(kP) leaks log-bit info (LEAD-EXO-miller-pairing-cocycle), use as pre-filter before FAM-1 relation search; measure combined yield at toy scale. *(variant of LEAD-ICP-coincidence-harvest-structured-base + LEAD-EXO-miller-pairing-cocycle; differs: Miller cocycle as statistical filter, not standalone transfer)*

**Prior-art check:** 13  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves | 10  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 9  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificat

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Repository contents are unavailable here; first audit the cited leads and both repositories for prior Miller normalizations, FAM-1 implementations, negative results, and benchmarks. Record commit IDs and reuse the existing FAM-1 decomposition predicate unchanged. Let \(E/\mathbb F_p\) contain a prime-order subgroup \(\langle P\rangle\) of order \(r\). Fix auxiliary points \(T_1,\ldots,T_t\). Define \[ U_j(R)=f_{r,R}(T_j), \] using normalized Miller functions with divisor \(r[R]-r[O]\). Reject poles and zeros. Compute features from canonical field encodings: selected bits, mult...

### 60. **Cover-catalog transfer to prime-field IC: pushforward JV weak-class relations to prime field via cover map** — use LEAD-TRF-cover-catalog-jacobian-transfer Mumford arithmetic to transfer genus-3 JV relations from F_{p^6} down to E(F_p); test if transferred relations have usable smoothness. *(advances LEAD-TRF-cover-catalog-jacobian-transfer + LEAD-TRF-jv-sieve-fp6-weak-class)*

**Prior-art check:** 24  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery | 17  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models) | 16  LEAD-ICP-residual-partial-relations          closed_obstructed  Crediting residuals as partial rel

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit before implementation.** Repository access is unavailable here; do not assume prior results. Inspect both repos for the two named leads, cover equations, explicit maps, Mumford-arithmetic tests, weak-class restrictions, failed smoothness experiments, and timings. Record commit hashes and distinguish reproduced results from conjectures. 2. Set \(K=\mathbb F_{p^6}\). Instantiate a catalog genus-3 curve \(C/K\) with an explicit separable map \(f:C\to E_K\) of degree \(\delta\). Verify the induced homomorphism \[ T=\operatorname{Tr}_{K/\mathbb F_p}\circ f_*:J_C(K)\to E(...

### 61. **Odd-char Smith quartic + FAM-1: use Smith isogeny to map FAM-1 base to plane quartic** — if Smith's Props 2/4 work (LEAD-TRF-odd-char-descent-smith-quartic), transport FAM-1 factor base to quartic model; test if decomposition easier on quartic. *(variant of LEAD-TRF-odd-char-descent-smith-quartic + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 25  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 18  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 17  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater 

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and audit - First inspect `LEAD-TRF-odd-char-descent-smith-quartic`, `LEAD-ICP-coincidence-harvest-structured-base`, and FAM-1 implementations/results in `isogeny-labs/crypto`, `cryptanalysis`, and `crypto-autoresearcher`. Record tested parameters, negative results, and relation-cost baselines. **These repositories are not available here; this review remains a prerequisite, not a completed claim.** - Extract Smith’s exact hypotheses and maps from Propositions 2/4. An elliptic curve cannot be isogenous to a genus-3 Jacobian: require an explicit embedding \(\iota:\langle P\rangl...

### 62. **Quantum-classical hybrid: use quantum subroutine for FAM-1 relation generation** — Grover search over FAM-1 parameter space for smooth decompositions; classical linear algebra; cost model: quantum queries + classical ops in S units. *(variant of LEAD-EXO-quantum-ecdlp-resources + LEAD-ICP-coincidence-harvest-structured-base; differs: quantum only for relation search, not full Shor)*

**Prior-art check:** 15  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction) | 14  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 10  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Repository audit gate:** The repositories are not available in this conversation, so prior experiments and FAM-1’s precise definition remain unverified. Before implementation, inspect both repositories’ FAM-1 code, experiment logs, and the two named leads. Record tested parameterizations, negative results, and resource assumptions; do not claim novelty until this comparison is complete. 2. Let \(E/\mathbb F_p\) contain a prime-order subgroup of order \(n\), with \(Q=xP\). Fix factor base \(\mathcal B=\{B_1,\ldots,B_b\}\) using the audited FAM-1 construction. Enumerate its...

### 63. **ML-guided FAM-1 seed selection: train predictor on (curve, target) → κ_rel** — use EXP-ECTD-0cf008 crater/floor data + LEAD-EXO-ml-learned-models pipeline; predict which FAM-1 seeds yield relations; measure speedup vs uniform sampling. *(advances LEAD-ICP-coincidence-harvest-structured-base + LEAD-EXO-ml-learned-models)*

**Prior-art check:** 8  LEAD-ICP-residual-partial-relations          closed_obstructed  Crediting residuals as partial relations (single/double large prime) in prime-field IC | 8  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction / algorithm 1. **Audit before coding:** inspect EXP-ECTD-0cf008, LEAD-EXO-ml-learned-models, and FAM-1 relation-generation code in both repositories; inventory prior predictors, negative results, feature definitions, and timing conventions. Repository contents are unavailable here, so prior coverage and the meaning of logged \(\kappa_{\rm rel}\) remain unverified. 2. Retain the existing FAM-1 seed-to-candidate map and relation verifier unchanged. Build examples \((E,Q,s,x,y,t)\): curve, target, seed, cheap pre-search features, independently verified relation-success indicator,...

### 64. **Tag-tracing FAM-1 walk: use tag-tracing (LEAD-RHO-cheaper-step-primitives) for FAM-1 relation search** — each FAM-1 seed = tag; walk combines tags; measure if in-degree concentration reduces FAM-1 relation cost. *(variant of LEAD-RHO-cheaper-step-primitives + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-RHO-best-of-candidates-indegree         open_next_step     Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree | 10  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 9  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Treat FAM-1 as the existing seeded relation generator; preserve its factor base, acceptance predicate, and relation encoding. 1. Generate \(r\) valid FAM-1 seed increments \(D_i\), each carrying its exact algebraic label. Define the baseline walk \[ X_{t+1}=X_t+D_{h(X_t)},\qquad h:E(\mathbb F_p)\to\{1,\ldots,r\}. \] Accumulate labels exactly; never treat a tag collision as a relation. 2. Implement tag-tracing blocks of length \(b\): a cheap coordinate-derived tag predicts partition choices, while cached aggregate increments defer full point additions. Tags are **not** assumed...

### 65. **Best-of-candidates FAM-1: at each step, evaluate multiple FAM-1 seeds and pick best** — extend LEAD-RHO-best-of-candidates-indegree to FAM-1 parameter space; measure κ_rel improvement at 24/28/32 bits. *(variant of LEAD-RHO-best-of-candidates-indegree + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 10  LEAD-RHO-best-of-candidates-indegree         open_next_step     Step to the better of k candidate images (best of P+R, P-R) to concentrate in-degree | 6  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 6  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - **Repository prerequisite:** I cannot access the named repositories here. Before implementation, inspect both leads, the exact FAM-1 constructor, prior negative results, and existing κ_rel accounting; record commit hashes. Do not substitute a new family for repository-defined FAM-1. - Wrap the existing FAM-1 transition \(T_\theta\). At each canonicalized walk state \(X\), derive \(B\in\{1,2,4,8\}\) admissible parameter seeds deterministically: \[ \theta_j=\mathrm{SeedToFAM1}(H(\text{run salt},X,j)). \] Compute every candidate \(Y_j=T_{\theta_j}(X)\), including its coefficien...

### 66. **Grumpy-giants FAM-1: store-all schedule for FAM-1 relation generation** — apply EXP-GRUMPY-eb8675 exhaustive ladder to FAM-1 seed space; measure if compiled reservoir-guided schedule beats uniform. *(variant of LEAD-RHO-grumpy-store-all-schedules + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 14  LEAD-RHO-grumpy-store-all-schedules          open_next_step     Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks) | 10  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Repository gate:** Before implementation, inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `EXP-GRUMPY-eb8675`, both named parent leads, and FAM-1. Record commit IDs, seed enumeration, relation predicate, timings, and negative results. These repositories are not accessible here; prior-test coverage remains unverified. 2. Freeze the existing FAM-1 generator as a deterministic function \[ G(E,\mathcal B,s)\rightarrow\{\text{verified relation},\bot\}, \] including its original factor base, seed domain, and acceptance rules. Change only scheduling....

### 67. **Low-Hamming-weight FAM-1: restrict FAM-1 seeds to low-HW exponents** — combine LEAD-RHO-lhw-* leads with FAM-1; test if low-HW seeds have higher smoothness probability; price preprocessing frontier. *(variant of LEAD-RHO-lhw-preprocessing-frontier + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 7  LEAD-RHO-lhw-preprocessing-frontier          open_unexamined    Low-weight DLP with preprocessing: the (P, S, T, epsilon, U) frontier | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Repository contents are unavailable here; prior results and FAM-1’s exact implementation remain unverified. First inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for `LEAD-RHO-lhw-*`, `LEAD-RHO-lhw-preprocessing-frontier`, `LEAD-ICP-coincidence-harvest-structured-base`, and FAM-1. Extract code, parameters, negative results, and preprocessing accounting; reproduce the closest baseline before claiming novelty. Use the existing FAM-1 implementation unchanged except for its seed-exponent sampler. For \(E/\mathbb F_p\), subgroup generator \(P\) of prime order \(n\), and \...

### 68. **Non-automorphism equivalence classes for FAM-1: quotient FAM-1 seed space by H⊂(Z/N)^*** — test H-EWALK-29cb90 bound on FAM-1 parameter space; if canonicaliser cheap, measure κ_rel gain. *(variant of LEAD-RHO-non-automorphism-equivalence + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 19  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^* | 14  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant | 9  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and prior-work gate - Review `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` records for **FAM-1**, **H-EWALK-29cb90**, and both named parent leads. Extract the actual seed map, equivalence definition, bound assumptions, failed experiments, and measured costs into a comparison table with commit references. Repository contents are unavailable here; do not assume these definitions or claim novelty before this review. - Let \(S\) be the documented FAM-1 seed space and \(R(s)\) its relation-search output. For prime curve order \(N\), choose small subgroups \(H\le(\...

### 69. **Digit-presentation on isogeny volcano: use digit system at each volcano level, transport relations** — combine LEAD-ICP-digit-presentation-solving-degree with EXP-ECTD-0cf008 data; digit decomposition at crater + floor, charge transport. *(variant of LEAD-ICP-digit-presentation-solving-degree + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 23  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 13  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks | 12  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic mode

**Plan (abridged; full text in `expanded-plans.md`):** **Scope.** The named leads, EXP-ECTD-0cf008, and repositories are unavailable here; prior-test coverage remains unverified. Before implementation, inspect their code, logs, and negative results for digit encodings, solving-degree measurements, transported-factor overlap, and rank accounting. **Construction.** 1. Select ordinary \(E_0/\mathbb F_p\), a prime-order subgroup \(G_0=\langle P\rangle\) of order \(r\), and target \(Q\). Choose a small volcano prime \(\ell\ne r\); construct rational isogeny paths from crater to floor. Record each composite \(\psi_v:E_0\to E_v\), degree \(D_v\), and dua...

### 70. **Lattice IC on isogeny volcano: use volcano structure to build better lattice** — LEAD-ICP-lattice-ic-relation-construction + volcano census; isogeny-adjoint witnesses vary predictably across volcano; exploit for relation construction. *(advances LEAD-ICP-lattice-ic-relation-construction + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 19  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups | 16  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor) | 14  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost ac

**Plan (abridged; full text in `expanded-plans.md`):** **Prior-work gate.** Repository contents are unavailable here; novelty is unverified. Before implementation, inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for both named leads, volcano censuses, adjoint-witness experiments, negative results, and parameter logs. Record tested constructions and reject equivalent variants. **Exact construction.** 1. Choose an ordinary \(E/\mathbb F_p\), prime-order subgroup \(G\) of order \(r\), and small volcano prime \(\ell\ne p,r\). Census a bounded rational \(\ell\)-isogeny neighborhood; select a rooted spanning tree. 2. For each vertex \(v\), def...

### 71. **Shared-coefficient membership for isogeny-chain factor base** — LEAD-ICP-shared-coefficient-membership + isogeny chain; factor base = union across chain; shared Graeffe/quotient circuits across curves in chain. *(advances LEAD-ICP-shared-coefficient-membership + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 18  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for high-degree implicit factor-base membership | 16  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 15  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic 

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Let \(E_0/\mathbb F_p\) contain a prime-order subgroup \(H_0=\langle G\rangle\) of order \(r\). Build a chain of small-degree isogenies \(\phi_i:E_{i-1}\to E_i\), with degrees coprime to \(r\), and set \(T_i=\phi_i\circ\cdots\circ\phi_1\). Choose a common structured set \(S\subset\mathbb F_p\), \(|S|=B\). Define \[ \mathcal B_i=\{P\in H_0:x(T_i(P))\in S\},\qquad \mathcal B=\bigcup_{i=0}^{k}\mathcal B_i. \] Deduplicate transported points; use consistent sign conventions. Write \(x(T_i(P))=N_i(x(P))/D_i(x(P))\). For \(F_S(Z)=\prod_{s\in S}(Z-s)\), membership is \[ M_i(X)=D_i(X)^...

### 72. **x-line symmetry + isogeny transport: j=0/j=1728 symmetry preserved under isogeny?** — test if automorphism folding (LEAD-ICP-xline-symmetry-special-j) survives 2-isogeny transport; measure Macaulay ranks on transported systems. *(variant of LEAD-ICP-xline-symmetry-special-j + LEAD-ICP-isogeny-transported-relation-yield)*

**Prior-art check:** 25  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j | 10  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class | 9  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables

**Plan (abridged; full text in `expanded-plans.md`):** **Hypothesis.** Special-\(j\) automorphism folding reduces relation-solving cost after 2-isogeny transport—not merely relation counts. Repository access is unavailable here; prior-work review remains a prerequisite, not a completed claim. **Prior-work gate.** In `isogeny-labs/crypto` and `crypto-autoresearcher`, locate both named leads and their experiments. Extract curves, factor bases, polynomial generators, saturation rules, term orders, rank measurements, failures, and seeds. Reproduce the closest baseline before adding this variant. **Exact construction.** - Choose primes \(p\equiv1\pmod{...

### 73. **Class-group action + FAM-1: use class-group action to find curve with optimal FAM-1 geometry** — LEAD-STR-class-group-ecdlp-bridge simulation lemma + FAM-1; if simulation lemma holds, class-group action can't help; but test empirically at toy scale. *(variant of LEAD-STR-class-group-ecdlp-bridge + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 8  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition

**Plan (abridged; full text in `expanded-plans.md`):** **Hypothesis.** Searching an ordinary \(\mathbb F_p\)-isogeny class yields curves with better FAM-1 relation geometry, enough to repay search, isogeny evaluation, and linear algebra. The simulation lemma predicts no intrinsic advantage when transported factor bases are allowed; any observed gain must identify a restricted representation or implementation advantage. **Repository gate.** The repositories are unavailable here, so prior experiments cannot be verified. Before implementation, inspect both named repositories for the two cited leads, the exact FAM-1 definition, negative results, param...

### 74. **Matched-order special-j + FAM-1: j=0/j=1728 automorphism-orbit factor base for FAM-1** — LEAD-STR-special-j-ic-semaev matched-order design + FAM-1 geometry; measure κ_rel vs generic-j FAM-1. *(advances LEAD-STR-special-j-ic-semaev + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems | 10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO) | 10  LEAD-ICP-coppersmith-smallroot-semaev        closed_obstructed  Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit before implementation:** inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `LEAD-STR-special-j-ic-semaev`, `LEAD-ICP-coincidence-harvest-structured-base`, FAM-1 definitions, negative results, and automorphism-based bases. Record commit hashes, tested parameters, and failure modes. Repository contents were not provided here; novelty remains unverified. 2. Construct ordinary curves \(E_s/\mathbb F_p\) with \(j=0\) or \(1728\), respectively requiring \(p\equiv1\pmod3\) or \(p\equiv1\pmod4\) for rational extra automorphisms. Find generic-\(j\)...

### 75. **JV sieve + class-representative selection: solve JV weak-class instance on best isomorphic model** — LEAD-TRF-jv-sieve-fp6-weak-class + LEAD-STR-class-representative-ic-selection; calibrate model selection on toy JV instances. *(advances LEAD-TRF-jv-sieve-fp6-weak-class + LEAD-STR-class-representative-ic-selection)*

**Prior-art check:** 16  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 7  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class | 7  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-3

**Plan (abridged; full text in `expanded-plans.md`):** **Hypothesis.** Within a JV weak-class instance over \(\mathbb F_{p^6}\), selecting an isomorphic model before constructing the coordinate-defined factor base reduces relation-generation cost enough to repay selection overhead. This is initially an extension-field experiment—not an attack on prime-field ECDLP without a separate reduction. **Prior-work gate.** Repository contents were not provided, so their tested results cannot be verified here. Before implementation, inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for both lead IDs, JV implementations, model-selection experiments, n...

### 76. **Miller cocycle + class-group bridge: U(kP) as invariant under class-group action** — test if Miller cocycle (LEAD-TRF-miller-cocycle-nonhom-transfer) transforms covariantly under class-group action; if so, could bridge ECDLP to class group. *(variant of LEAD-TRF-miller-cocycle-nonhom-transfer + LEAD-STR-class-group-ecdlp-bridge)*

**Prior-art check:** 18  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class | 11  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves | 7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines

**Plan (abridged; full text in `expanded-plans.md`):** **Construction.** Work with an ordinary \(E/\mathbb F_p\), a prime-order subgroup \(\langle P\rangle\) of order \(\ell\), and an explicitly oriented endomorphism order \(\mathcal O\). Restrict to invertible ideal classes represented by rationally computable isogenies of degree coprime to \(\ell\). Class groups act on oriented curves—not automatically on a fixed ECDLP group. Define \[ \operatorname{div}(f_{m,R})=m[R]-[mR]-(m-1)[O], \qquad U_m(R;D)=f_{m,R}(D), \] for a fixed degree-zero divisor \(D\) with disjoint support. Compute using Miller recursion, testing small \(m\) and \(m=\ell\). For \...

### 77. **Smith quartic + special-j: j=0/j=1728 on plane quartic model** — if Smith isogeny works (LEAD-TRF-odd-char-descent-smith-quartic), test if special-j curves give simpler quartics; measure genus/Diem cost. *(variant of LEAD-TRF-odd-char-descent-smith-quartic + LEAD-STR-special-j-ic-semaev)*

**Prior-art check:** 24  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack | 15  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 10  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and prerequisite audit - First inspect both repositories for `LEAD-TRF-odd-char-descent-smith-quartic` and `LEAD-STR-special-j-ic-semaev`, including failed experiments, scripts, and timing logs. Repository access is unavailable here; prior results must not be presumed. - **Dimension gate:** an elliptic curve cannot be isogenous to a genus-3 Jacobian. Identify Smith’s actual three-dimensional input and every field-extension requirement. In particular, base-changing \(E/\mathbb F_p\) to \(\mathbb F_{p^3}\) does not create a generic Weil-restriction instance. ### Exact experiment...

### 78. **Tower-field DLP recost + FAM-1: use exTNFS cost model to price FAM-1 linear algebra over extension fields** — if FAM-1 relations live in extension field (LEAD-ICP-extension-field-embedding closed but...), use H-PAIR-62e9cc tower-DLP calibration to price LA. *(variant of LEAD-TRF-pairing-target-field-recost + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 20  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged | 14  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 10  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and prior-work gate First inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for FAM-1, `H-PAIR-62e9cc`, `LEAD-ICP-extension-field-embedding`, `LEAD-TRF-pairing-target-field-recost`, and `LEAD-ICP-coincidence-harvest-structured-base`. Extract constructions, parameters, measurements, and closure reasons; these repositories were not available here, so no review is claimed. Reproduce FAM-1’s relation equation before assigning costs. For a prime-order subgroup \(\langle P\rangle\subset E(\mathbb F_p)\) of order \(r\), distinguish: 1. **Extension-field coordi...

### 79. **Teske trapdoor + FAM-1: secret isogeny to curve with optimal FAM-1 geometry** — LEAD-TRF-teske-secret-isogeny-trapdoor + FAM-1; if heavy tail of Semaev meters exists, FAM-1 might amplify it; test at toy scale. *(variant of LEAD-TRF-teske-secret-isogeny-trapdoor + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 34  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness | 17  LEAD-TRF-teske-trapdoor-fp6-weak-class       open_unexamined    Teske-style trapdoor over F_{p^6} built on the Joux-Vitse weak class | 9  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - **Repository review prerequisite:** I cannot access the named repositories here. Before implementation, extract prior Teske-trapdoor, FAM-1, Semaev-tail, and structured-base experiments into a deduplication table: construction, parameters, negative results, and unresolved hypotheses. Reuse their exact FAM-1 definition; do not interpret this plan as a completed review. - Choose ordinary curves \(E/\mathbb F_p\), initially \(p\approx2^{20},2^{24},2^{28}\), with large prime subgroup order \(r\). Generate equal-budget collections of rational low-degree isogeny walks \(\phi:E\to...

### 80. **Weil-restriction Jacobian + FAM-1: FAM-1 on genus-2 Jacobian in Weil class** — LEAD-TRF-weil-restriction-jacobian-class n=2 control + FAM-1 geometry on Jac(C); test if FAM-1 decomposition works on Mumford coordinates. *(variant of LEAD-TRF-weil-restriction-jacobian-class + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 14  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor | 12  LEAD-TRF-weil-restriction-jacobian-class     open_next_step     Genus-n Jacobians in the isogeny class of a Weil-restricted elliptic curve | 11  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - **Repository-review prerequisite:** inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for both named leads, FAM-1 definitions, implementations, and negative results. Record commit hashes and reproduce baselines before claiming novelty. Those repositories were not accessible here; this plan does not claim that review occurred. - Use the **descended \(n=2\) control**: \(E/\mathbb F_p\), quadratic twist \(E^d\), and \[ A=\operatorname{Res}_{\mathbb F_{p^2}/\mathbb F_p}(E_{\mathbb F_{p^2}}). \] Here \(A\) is \(\mathbb F_p\)-isogenous to \(E\times E^d\), n...

### 81. **Coordinate-statistic leakage + FAM-1: digit-character family as FAM-1 membership test** — LEAD-EXO-coordinate-statistic-leakage digit-character (λ, PGL_2-stability) as fast filter for FAM-1 seeds; measure false positive/negative rate. *(variant of LEAD-EXO-coordinate-statistic-leakage + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 6  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets) | 6  LEAD-ICP-shared-coefficient-membership       open_unexamined    Shared divisor-coefficient circuits for high-degree implicit factor-base membership | 5  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply i

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit prerequisite:** I cannot access the named repositories here. Before implementation, inventory prior coordinate-statistic, digit-character, λ, PGL₂-stability, FAM-1, and structured-base experiments; record commit IDs, parameters, negative results, and reusable code. Treat novelty as unverified until this comparison is complete. 2. Freeze the repository’s exact FAM-1 seed generator and membership predicate \(M(s)\). Use exhaustive evaluation on small instances to obtain ground-truth labels; do not redefine membership using coordinate statistics. 3. For each seed’s can...

### 82. **Four-list k-tree + FAM-1: Wagner join on FAM-1 seed space** — LEAD-EXO-four-list-ktree-join O2 agreement kernel on FAM-1 parameter tuples; measure bucket variance W for FAM-1 seeds. *(variant of LEAD-EXO-four-list-ktree-join + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 18  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit before implementation:** locate FAM-1, `LEAD-EXO-four-list-ktree-join`, and `LEAD-ICP-coincidence-harvest-structured-base` in both repositories. Extract exact seed maps, O2 agreement-kernel definitions, previous negative results, and measured costs. Repository contents are unavailable here; this plan does not claim that review is complete. 2. On \(E/\mathbb F_p\), use subgroup order \(n\). Represent each FAM-1 seed as \((R_s,\mathbf c_s)\), where \(\mathbf c_s\) is its verified factor-base decomposition. Preserve any known \(G,Q\) coefficients. 3. Generate four disj...

### 83. **Global lift height + FAM-1: bounded-height sections as FAM-1 relation source** — LEAD-EXO-global-lift-height T_section(d,χ,p) for E1 surfaces; if sections through prescribed fibre exist at low height, use as FAM-1 seeds. *(variant of LEAD-EXO-global-lift-height + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 26  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t) | 21  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces) | 21  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation sourc

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Repository audit first:** inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for global-lift-height, FAM-1, and structured-base experiments. Record commit, parameters, failed assumptions, and measured costs; distinguish reproductions from new tests. Repository contents are unavailable here, so prior results are not presumed reviewed. 2. Fix \(E/\mathbb F_p\), prime-order subgroup \(\langle P\rangle\), and target \(Q\). Construct nonsingular elliptic surfaces \[ \mathcal E:y^2=x^3+A(t)x+B(t),\qquad \deg A\le4\chi,\ \deg B\le6\chi, \] with fibre \(\ma...

### 84. **Hashed factor base + FAM-1: Akshima/Bochum tensor contraction for FAM-1 decomposition counting** — if audit passes (LEAD-EXO-hashed-factor-base-tensor-ecdl), apply to FAM-1 Semaev systems; measure #SAT exponent vs enumeration. *(variant of LEAD-EXO-hashed-factor-base-tensor-ecdl + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 30  LEAD-EXO-hashed-factor-base-tensor-ecdl      open_next_step     Hashed-factor-base ECDL with a compact low-degree Boolean encoding and exact tensor contraction (Akshima et al., Bochum v0.2), conditional on the openai/math #k-SAT result | 20  LEAD-ICP-pkm-tower-algebraic-oracle          open_blocked       PKM tower and APS partitioned factor bases solved algebraically over F_p (summation-polynomial systems with low-degree auxiliary membership; first and last fall degree) | 18  LEAD-STR-specia

**Plan (abridged; full text in `expanded-plans.md`):** **Construction and audit gate.** First inspect `LEAD-EXO-hashed-factor-base-tensor-ecdl`, `LEAD-ICP-coincidence-harvest-structured-base`, FAM-1 definitions, and experiment logs in `isogeny-labs/crypto` and `crypto-autoresearcher`. These repositories were not accessible here; no prior-results review is claimed. Record previously tested constructions, failures, and the exact Akshima/Bochum contraction bound. Proceed only if its tensor representation, coefficient domain, and contraction assumptions apply—not merely its headline exponent. 1. **Exact counting instance.** For \(E/\mathbb F_p\), sele...

### 85. **Invertible hint subset + FAM-1: low-degree poly agreement with FAM-1 log graph** — LEAD-EXO-invertible-hint-subset A(d) measurement on FAM-1 parameter space; if A(d) high, use as FAM-1 seed predictor. *(variant of LEAD-EXO-invertible-hint-subset + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 21  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p) | 8  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines | 6  LEAD-EXO-hashed-factor-base-tensor-ecdl      open_next_step     Hashed-factor-base ECDL with a compact low-degree Boolean encoding and exact tensor contraction (Akshima et al., Bochum v0.2), cond

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit prerequisite:** inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for FAM-1, invertible-hint-subset, and structured-base coincidence experiments. Extract exact parameterizations, failed variants, datasets, and costs; repository contents are unavailable here, so prior results are not assumed. 2. Let \(G\) generate a prime-order subgroup of size \(n\) over \(\mathbb F_p\). Write the actual FAM-1 family as \(P(\theta)\), with graph label \(\ell(\theta)=\log_G P(\theta)\in\mathbb F_n\). Generate ground-truth labels **only for small experimental ins...

### 86. **Lossy object propagation + FAM-1: propagate lossy FAM-1 seed through scalar multiplication** — LEAD-EXO-lossy-object-propagation disjoint projection panel on FAM-1 seed space; test if rigidity theorem leaves probabilistic regime for FAM-1. *(variant of LEAD-EXO-lossy-object-propagation + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 37  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation) | 7  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity) | 6  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/desc

**Plan (abridged; full text in `expanded-plans.md`):** **Construction.** Treat FAM-1 as the existing seed-to-point map \(F:S\to E(\mathbb F_p)\); preserve its actual seed distribution and admissibility constraints. Work in a prime-order subgroup of order \(r\), with target \(Q=xP\). Fix disjoint coordinate-projection panels \(\pi_1,\ldots,\pi_k\) on the **seed representation**, and define lossy states \(L_i(s)=\pi_i(s)\). For scalars \(a\), seek a cheap probabilistic propagator \[ T_{a,i}(L_i(s))\rightsquigarrow L_i(s_a), \qquad F(s_a)=[a]F(s). \] The output may be a bounded candidate list or an explicitly sampled distribution. Count failure to fi...

### 87. **Methodology instruments + FAM-1: planted FAM-1 signals in pipeline** — LEAD-EXO-methodology-instruments 3 planted-signal families specialized to FAM-1 geometry; measure false-negative rate of FAM-1 screens. *(advances LEAD-EXO-methodology-instruments + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 13  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism) | 5  LEAD-ICP-prime-ic-constant-engineering       open_next_step     Constant-factor engineering of the prime-field IC pipeline (native arithmetic, batching, pair-table build, generator, LA filter, planner) | 4  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, b

**Plan (abridged; full text in `expanded-plans.md`):** **Objective.** Measure false negatives in FAM-1 screening—not claim an ECDLP speedup from artificially enriched data. **Repository gate.** Before implementation, audit `isogeny-labs/crypto` and `crypto-autoresearcher`: locate FAM-1’s actual equations, factor-base construction, screening stages, prior planted controls, and negative results. Produce a commit-linked experiment ledger; reuse existing controls. Repository contents were not provided here, so this plan does not claim that review is complete. **Construction.** Let \(E/\mathbb F_p\), factor base \(B\), target \(T\), and relation arity...

### 88. **Quantum FAM-1: Grover on FAM-1 parameter space with quantum oracle for smoothness** — LEAD-EXO-quantum-ecdlp-resources circuit for FAM-1 smoothness test; cost model: quantum queries × classical LA. *(variant of LEAD-EXO-quantum-ecdlp-resources + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction) | 12  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost | 9  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, par

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Repository audit gate:** I cannot access the named repositories here. Before implementation, inventory their FAM-1 definitions, smoothness predicates, structured-base experiments, negative results, and quantum-resource estimates; record commit hashes and identify what this variant changes. 2. Let \(E/\mathbb F_p\) contain a prime-order subgroup \(\langle P\rangle\) of order \(n\), with target \(Q\). Freeze a factor base \(\mathcal B=\{B_1,\ldots,B_B\}\) and the repository’s exact FAM-1 parameter domain \(\Theta\). 3. Implement a reversible oracle computing the existing FA...

### 89. **Advice table variants for FAM-1: batch-reselected FAM-1 seed table** — LEAD-RHO-advice-table-variants T_sel∈{0.65T,0.75T} applied to FAM-1 seed table; grow table from solved FAM-1 relations. *(variant of LEAD-RHO-advice-table-variants + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 23  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables | 8  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7) | 8  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputatio

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - Reuse the repository’s exact FAM-1 family, relation verifier, and seed-table representation. **Repository contents are unavailable here; prior-test overlap must be checked before claiming novelty.** - For \(E/\mathbb F_p\), work in a prime-order subgroup \(\langle P\rangle\) of order \(n\), targeting \(Q=xP\). Preserve coefficient provenance for every stored point and harvested relation. - Operationally define \(T\) as the baseline walk-step budget and \(T_{\rm sel}\in\{0.65T,0.75T\}\) as a **single batch-reselection checkpoint**. - Start with the unchanged FAM-1 seed table...

### 90. **Cheaper step primitives for FAM-1: tag-tracing + halving on FAM-1 seed space** — LEAD-RHO-cheaper-step-primitives ported to FAM-1 parameter walk; measure ns/step vs plain FAM-1 seed enumeration. *(variant of LEAD-RHO-cheaper-step-primitives + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 14  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 13  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 9  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - **Repository audit first:** repository contents are unavailable here; prior testing cannot be verified. Before coding, inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for both named leads, FAM-1 implementations, benchmarks, and negative results. Record commit IDs, duplicate mechanisms, and unresolved assumptions. - Use the existing FAM-1 seed-to-candidate map \(F(s)\) and relation predicate unchanged. Specify its actual seed domain; do not assume seeds are subgroup scalars. - For an odd cyclic seed domain \(\mathbb Z_m\), partition seeds using a che...

### 91. **Cheon auxiliary input for FAM-1: generate [x^d]P via FAM-1 relations** — if FAM-1 gives relations, can we compute [x^d]P cheaper? LEAD-RHO-cheon-deployed-applicability census + FAM-1; test at toy scale. *(variant of LEAD-RHO-cheon-deployed-applicability + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 21  LEAD-RHO-cheon-aux-acquisition               closed_obstructed  Run Cheon's auxiliary-input algorithm on ordinary ECDLP by generating [x^d]P yourself | 16  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply | 14  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit before implementation:** inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for FAM-1, Cheon applicability, and structured-base coincidence experiments. Record exact relation formats, costs, negative results, and commit IDs. These repositories are not available here; prior coverage cannot yet be verified. 2. Work in a prime-order subgroup \(G=\langle P\rangle\) of order \(q\) on \(E(\mathbb F_p)\), with \(Q=[x]P\). Choose \(d>1\) dividing \(q-1\). 3. Instrument FAM-1 to output relations \[ [a_i]P+[b_i]Q+\sum_j[c_{ij}]R_j=O, \] including the complete construct...

### 92. **ECC2K-130 iteration function + FAM-1: sigma walk on FAM-1 seed space** — LEAD-RHO-ecc2k130-iteration-function v3 table walk adapted to FAM-1 seeds; Frobenius action on FAM-1 parameters? Test at binary toy then prime. *(variant of LEAD-RHO-ecc2k130-iteration-function + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 30  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps | 15  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit before implementation.** Search both repositories for `FAM-1`, `LEAD-RHO-ecc2k130-iteration-function`, and `LEAD-ICP-coincidence-harvest-structured-base`; extract the actual seed decoder, v3 transition table, prior negative results, and counting conventions. Repository contents are unavailable here, so novelty and compatibility remain unverified. 2. Let the implemented FAM-1 decoder be \(D:S\to E^k\), with a documented relation predicate \(R(D(s))\). On a binary toy curve defined over \(\mathbb F_2\), construct a seed map \(\sigma\) satisfying \[ D(\sigma s)=\pi^{\t...

### 93. **Grumpy store-all for FAM-1: compiled reservoir-guided FAM-1 schedule** — LEAD-RHO-grumpy-store-all-schedules exhaustive ladder on FAM-1 seed space Z/l 2^10..2^20; measure coverage vs uniform. *(variant of LEAD-RHO-grumpy-store-all-schedules + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 23  LEAD-RHO-grumpy-store-all-schedules          open_next_step     Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks) | 6  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance | 5  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and t

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Treat the existing FAM-1 implementation as a deterministic map \(F(s)=(R_s,a_s,b_s)\), with \(R_s=[a_s]P+[b_s]Q\). Preserve its exact definition; do not introduce a replacement family. 1. **Prior-work audit:** Inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for both named leads, FAM-1 definitions, schedules, collision filters, and negative results. Record commit IDs and distinguish genuinely untested changes. Repository contents are unavailable here, so this review remains a prerequisite. 2. For prime-order subgroups of order \(\ell\), use nested seed d...

### 94. **Low-Hamming-weight modular filter for FAM-1: residue-guess price on FAM-1 seeds** — LEAD-RHO-lhw-modular-filter-price EXP-LHW-9adf78 on FAM-1 parameter space with Mersenne/Fermat M. *(variant of LEAD-RHO-lhw-modular-filter-price + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 13  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups | 4  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters | 3  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)

**Plan (abridged; full text in `expanded-plans.md`):** **Construction.** Preserve FAM-1’s seed map and structured factor base \(\mathcal B=\{B_i\}\). Express each candidate relation as \[ [a(z)]P+[b(z)]Q=\sum_i[c_i(z)]B_i, \] where \(Q=[d]P\), \(B_i=[\beta_i]P\), and \(P\) has prime order \(n\). Use integer lifts of coefficients. Generate FAM-1 seeds from weight-\(w\), \(L\)-bit integers, enumerating fixed-weight supports without replacement. For \(M=2^r-1\) and \(2^r+1\), reduce these integers by folding \(r\)-bit blocks. A valid relation satisfies \[ a+bd-\sum_i c_i\beta_i=kn. \] Test modular compatibility **including the wrap term \(kn\bmod M\)...

### 95. **Low-Hamming-weight collision walks for FAM-1: jump-sum walk on weight-w FAM-1 seeds** — LEAD-RHO-lhw-polymem-collision-walks EXP-LHW-b49bc6 Stage 1 re-run on FAM-1 seed space; checkpointed sumset counts. *(variant of LEAD-RHO-lhw-polymem-collision-walks + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 19  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class | 8  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm | 7  LEAD-RHO-ecc2k130-iteration-function         open_next_step     ECC2K-130 iteration function: sigma walk vs v3 table walk vs class-signed sigma steps

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - **Repository gate:** Before implementation, inspect EXP-LHW-b49bc6, its parent leads, and FAM-1 definitions in both repositories. Record tested parameters, failures, collision conventions, and checkpoint formats. Repository contents are unavailable here; this plan does not claim that review occurred. - Freeze the existing FAM-1 factor base \(B=(P_1,\dots,P_m)\subset E(\mathbb F_p)\). A seed is a weight-\(w\) subset \(S\subset[m]\), with \(\phi(S)=\sum_{i\in S}P_i\). - Walk on seeds: hash the canonical encoding of \(S\) to choose \(i\in S\), \(j\notin S\); set \(S'=(S\setminu...

### 96. **Matched rho calibration for FAM-1: seal FAM-1 ρ baseline at 32-48 bits** — LEAD-RHO-matched-rho-calibration ecbench bounds for FAM-1 relation generation cost; fit R(N)=1+c/N^β. *(variant of LEAD-RHO-matched-rho-calibration + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 17  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier | 13  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo) | 12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny cl

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and prior-work audit Before running experiments, inspect `isogeny-labs/crypto`, cryptanalysis notes, and `crypto-autoresearcher` for FAM-1, `LEAD-RHO-matched-rho-calibration`, and `LEAD-ICP-coincidence-harvest-structured-base`. Record commit hashes, exact relation predicates, factor-base construction, failed variants, and existing benchmarks. Repository contents are unavailable here; this plan does not claim that review is complete. Freeze the canonical FAM-1 implementation and structured-base parameters from that audit. Do not introduce another relation-generation heuristic....

### 97. **Native step cost for FAM-1: price FAM-1 canonicaliser in field-mul equivalents** — LEAD-RHO-native-step-cost EXP-CERTBIN-b4d29c design C vs Bailey for FAM-1 seed canonicalisation; callgrind Ir. *(variant of LEAD-RHO-native-step-cost + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 20  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing | 8  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves | 6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion pa

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction - First inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `FAM-1`, `EXP-CERTBIN-b4d29c`, design C, Bailey, and both cited leads. Extract exact canonicalisation rules, prior benchmarks, rejected variants, and certificate checks into a provenance table. **Repository contents are unavailable here; prior results must be verified, not assumed.** - Implement a native benchmark exposing the existing design-C and Bailey canonicalisers behind identical interfaces: `canon(seed) → (representative, witness)`. Use precisely the FAM-1 equivalence relation establish...

### 98. **Non-automorphism equivalence for FAM-1: quotient FAM-1 seeds by H⊂(Z/N)^*** — LEAD-RHO-non-automorphism-equivalence H-EWALK-29cb90 bound on FAM-1 parameter space; search for cheap H-invariant. *(variant of LEAD-RHO-non-automorphism-equivalence + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 16  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^* | 11  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant | 6  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction Repository contents and definitions of FAM-1/H-EWALK-29cb90 were not provided; prior-test coverage and novelty remain unverified. 1. Extract the exact FAM-1 map \(F:S\to G\), where \(G=\langle P\rangle\) has prime order \(N\) over \(\mathbb F_p\). Audit both repositories for seed symmetries, scalar-orbit canonicalization, invariant searches, and rejected quotient walks. 2. Choose small subgroups \(H\le(\mathbb Z/N)^\times\), initially of orders \(3,4,6,8\) when divisibility permits. Require an explicit seed action \[ F(T_h(s))=[h]F(s). \] Establish closure, action laws, orbit...

### 99. **Pool class quotient for FAM-1: negation + Frobenius classes in distributed FAM-1 search** — LEAD-RHO-pool-class-quotient trap rate measurement on FAM-1 campaign curve; design Koblitz Frobenius class walk for FAM-1 seeds. *(variant of LEAD-RHO-pool-class-quotient + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 28  LEAD-RHO-pool-class-quotient                 open_next_step     Distributed pool v2 walk has no class quotient: add negation (sqrt 2) and Frobenius (sqrt 2m) | 20  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0 | 16  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction 1. **Audit prior work before implementation.** In `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher`, locate `LEAD-RHO-pool-class-quotient`, `LEAD-ICP-coincidence-harvest-structured-base`, and FAM-1 campaign artifacts. Extract curve parameters, subgroup order, seed distributions, walk functions, trap definitions, and measured baselines. Repository contents are unavailable here; prior results remain unverified. 2. **Apply the Frobenius feasibility gate.** For \(E/\mathbb F_p\), every \(P\in E(\mathbb F_p)\) satisfies \(\pi_p(P)=P\): Frobenius supplies **no additi...

### 100. **GPU FAM-1: gpu-match workload for FAM-1 relation generation on CUDA** — LEAD-RHO-prime-gpu-rho interleaved CPU/GPU with A/A controls; matched P-256 toy-to-medium ladder for FAM-1 kernel. *(variant of LEAD-RHO-prime-gpu-rho + LEAD-ICP-coincidence-harvest-structured-base)*

**Prior-art check:** 12  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison | 10  LEAD-RHO-ecc2k130-gpu-fpga-throughput        open_next_step     ECC2K-130 kernel throughput on GPU and FPGA (iterations per second per device and per watt) | 9  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)

**Plan (abridged; full text in `expanded-plans.md`):** ### Construction and repository gate - Audit `isogeny-labs/crypto`, cryptanalysis materials, and `crypto-autoresearcher` for FAM-1, structured-base coincidence harvesting, GPU matching, and interleaved rho experiments. Record commits, exact predicates, failed variants, timings, and controls. **These repositories are not accessible here; novelty and compatibility remain unverified.** - Freeze the existing FAM-1 predicate before optimization. The following is an explicit candidate realization, not an assertion about its existing definition. - On \(E/\mathbb F_p\), work in a prime-order subgroup...

## Critique

_Scope note: the critique stage received the 100 plans as its input, not the repository contents; its caveats about repository access or truncation refer to that prompt. The repository and lead-atlas audit is in **Prior work** above and in `prior-work.md`._

**No repository review is possible from the supplied text.** Prior results, artifact IDs, and novelty remain unverified; many plans are truncated. Below, “flaw” means the principal blocking issue—not necessarily a proof of impossibility. **Within each tier, order is descending expected research value**, not breakthrough probability.

### A — Worth resolving first
50: Elimination may inflate degree.  
96: Undefined FAM-1 prevents replication.  
85: Plants establish sensitivity, not speedup.  
78: Transport preserves relations exactly.  
52: Search overhead may dominate.  
49: Symmetry usually fails kernel descent.  
57: Multivariate small-root guarantees absent.  
83: Digit constraints may dominate.  
77: Orbit closure may destroy structure.  
36: Calibration, not cryptanalysis.  
64: Benchmarking, not index calculus.  
8: Signatures are not canonical forms.

### B — Legitimate experiments; weak breakthrough case
56: Transported membership adds complexity.  
73: Union membership multiplies degrees.  
70: Tail enumeration already costs base-size.  
68: Postfiltering may erase gains.  
89: Quadratic pair enumeration dominates.  
98: Applicable contraction bound unestablished.  
32: Hash circuits obscure exploitable structure.  
6: Prime-field digits aren't Weil descent.  
11: Degree truncation cannot certify regularity.  
61: Elliptic factor survives embedding.  
66: Genus-two embedding lacks demonstrated advantage.  
43: Transfer doesn't supply efficient decomposition.  
44: Section finding hides core difficulty.  
33: CRT needs a common integral instance.  
34: Carry term retains unknown-log dependence.  
71: Efficient evaluation closure unproved.  
65: Predictive signal unestablished.  
72: Nontrivial target homomorphism missing.  
87: Linear operations cannot manufacture powers.  
2: Ideal classes don't canonically act on points.

### C — Mostly scheduling, engineering, or controls
45: Ranking advantage unestablished.  
74: Feature acquisition may consume savings.  
42: Coordinate bias needn't predict relations.  
59: Low-weight seeds may reduce coverage.  
46: Seed equivariance unproved.  
84: Cheap orbit canonicalization missing.  
62: Hashing isn't homomorphic filtering.  
99: Seed walks don't coalesce.  
97: Coverage needn't yield independent relations.  
60: Replay may erase savings.  
76: Endpoint concentration isn't useful rank.  
91: Seed halving supplies no evaluation recurrence.  
92: Unsolved relations aren't free advice.  
93: Wrap classes can annihilate filtering.  
88: Lift ambiguity may explode.  
86: Invertible hints supply no log predictor.  
38: Generalizing scalar-bit prediction unsupported.  
31: Bucket mean double-counts same-bucket pairs.  
30: Scalar/coordinate field comparison is arbitrary.  
22: Shared formulas aren't shared evaluations.  
55: Explicit edge relations add no unknown information.  
79: Upstairs target descent remains missing.  
54: Extension-field scope mismatch.  
67: Full oracle cost unspecified.  
90: Duplicates 67's mechanism.

### D — Off-goal or assumption-dependent
37: Rho engineering only.  
40: Selection distorts collision dynamics.  
41: Advice construction may dominate.  
39: Requires unavailable auxiliary input.  
48: Solves auxiliary-input ECDLP.  
51: Usable residue information missing.  
53: Restricted-secret problem.  
75: Restricted-jump experiment.  
63: Target-independent surrogate limits transfer.  
35: Quantum arithmetic, not IC.  
47: Binary-field rho.  
58: Lookup engineering only.  
80: Kernel benchmark only.  
81: Matching benchmark only.  
82: Rho quotient engineering.  
94: Applicable canonicalizer unspecified.  
95: Binary-field scope mismatch.  
100: Frobenius trivial on rational points.  
69: Translation quotient removes subgroup information.

### E — Reject as written
1: Plants lack known scalar provenance.  
3: Impossible census; false Jacobian assertion.  
4: Summation variety isn't specified curve.  
5: Sampling cannot certify image/kernel.  
7: Rational kernel cannot lie in odd subgroup.  
9: CM doesn't guarantee planted leakage.  
10: PGL₂ doesn't act on curve points.  
12: Number-field sieve lacks ECDLP bridge.  
13: Frobenius basis collapses; cross-prime transfer invalid.  
14: Group law isn't coordinate addition.  
15: Base-size/memory contradiction; wrong modulus.  
16: Forces tiny torsion-only base.  
17: Membership doesn't imply ternary decomposition.  
18: Claimed torsion structure impossible.  
19: Supersingular/ordinary endomorphism theories conflated.  
20: Isogeny collisions don't recover point logs.  
21: Finite-field DLP, not ECDLP.  
23: Static-DH oracle changes problem.  
24: Symmetric powers don't automatically produce covers.  
25: Orbit divisibility condition is vacuous.  
26: Polynomial splitting lacks divisor-class bridge.  
27: Noise claim unsupported; rho isn't subexponential.  
28: Assumes the desired reduction.  
29: Projection fibers supply no decomposition.

**One compute direction: 50.** It is explicit, prime-field, and falsifiable. First audit prior implementations. Then compare orbit-invariant and ordinary digit systems with identical actual bases and targets, charging elimination and verification. **Fastest kill:** increased elimination degree or no reduction in median cost per independent relation on small held-out instances. Stop before a scaling campaign.

## Synthesis

# Research brief: degree-controlled relation generation for prime-field ECDLP

## Recommendation

Prioritize **candidate 50: test whether elimination can make relation generation cheaper without prohibitive degree growth**. It addresses the central index-calculus bottleneck rather than merely improving scheduling or changing representation. This is a hypothesis to resolve, not evidence of a breakthrough.

Use the other high-ranked directions as prerequisites or controls:

- **96:** specify FAM-1 completely before evaluating it.
- **85:** use planted instances to test solver sensitivity—not to claim speedup.
- **78:** treat exact relation transport as an equivalence control unless it demonstrably reduces total cost.
- **36/64:** supply calibration and benchmarking, not cryptanalytic claims.

Do not begin by generating another 100 variants. First determine whether this mechanism survives degree, relation-yield, and rank accounting.

**Evidence limitation:** neither repository is accessible from the supplied material. Previous experiments, artifact IDs, and novelty are therefore unverified. The critique is also truncated at candidate 7. The recommendation is provisional pending an actual repository audit.

## Cost model to beat

Let the prime-order subgroup have order \(\ell\), the factor base contain \(M\) points, and each relation contain approximately \(w\) nonzero coefficients. Measure

\[
T_{\rm IC}
=
T_{\rm setup}
+
N_{\rm trials}C_{\rm trial}
+
T_{\rm dedup/rank}
+
T_{\rm LA}
+
T_{\rm target}.
\]

Here:

- \(C_{\rm trial}\) includes candidate selection, equation construction, elimination, solving, verification, and failed attempts.
- \(N_{\rm trials}\) is the number needed for sufficient **independent** relations—not merely successful decompositions.
- \(T_{\rm LA}\) includes all linear algebra modulo \(\ell\); sparse iterative methods often require roughly \(O(wM^2)\) field operations, subject to matrix structure.
- \(T_{\rm target}\) includes expressing the challenge point in the solved factor base.

Report wall time, peak memory, operation counts, and parallel resources. Compare against both an optimized direct-decomposition baseline and Pollard rho’s approximately \(O(\sqrt{\ell})\) group-operation cost on the same hardware. Report **single-target total cost** separately from amortized multi-target cost. A cheaper polynomial system alone is not an ECDLP improvement.

## First three experiments, in order

### 1. Audit and reproduce before extending

Review `isogeny-labs/crypto`, cryptanalysis materials, and `crypto-autoresearcher`. Build a ledger linking each relevant idea to its definition, commit, parameters, seeds, results, failure modes, and artifacts. Explicitly distinguish implemented, tested, disproved, and merely proposed variants.

Recover candidate 50’s exact elimination construction and define FAM-1. Reproduce the strongest relevant baseline and one prior negative result.

**Deliverable:** a reproducible baseline and a precise statement of what, if anything, is new. If repositories remain unavailable, label this stage blocked; do not claim historical review or novelty.

### 2. Measure degree growth and unbiased relation yield

Across increasing field sizes and factor-base sizes, compare direct decomposition with the proposed elimination. Record intermediate and final degrees, monomial counts, solver time, memory, verified relation yield, and duplicate rate.

Use random ordinary prime-field instances. Keep planted instances separate as correctness controls. Where transport is used, verify that equivalent instances preserve solutions and account for transport overhead.

**Deliverable:** scaling curves for cost per verified relation, including failures, with uncertainty estimates.

### 3. Run end-to-end recovery

On fresh instances with hidden challenge scalars, collect relations, measure rank modulo \(\ell\), solve factor-base logs, and recover challenge logs. Include setup and target decomposition. Compare total cost with direct decomposition and rho at matched resource budgets.

**Deliverable:** independently checkable successful recoveries and a conservative crossover analysis—not a solver-only extrapolation.

## Kill criteria

Stop this direction if:

- The construction remains underspecified or reproduces a previously tested mechanism without a substantive change.
- Elimination’s degree, memory, or solving costs erase its relation-yield advantage.
- Gains appear only on planted, restricted-secret, or otherwise favorable instances.
- Duplicate or dependent relations consume the apparent speedup.
- Target decomposition remains unresolved or dominates total cost.
- Improvements disappear after charging preprocessing, selection, transport, verification, and failed trials.
- Increasing-size experiments show no credible improvement over direct decomposition and no defensible path toward beating rho.

Retain useful benchmarks and engineering results, but label them accordingly—not as new index calculus.

## Next step

Take the highest-ranked direction from the critique, run its first falsifying experiment, and record the result as a new experiment protocol and PR. Directions that the critique closes stay in this document with their obstruction; they are not deleted.

