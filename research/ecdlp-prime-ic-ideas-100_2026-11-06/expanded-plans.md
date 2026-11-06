# Expanded delphi plans

## Direction 1

**Research Plan: FAM-1 Growth-Ladder Validation**

**1. Construction & Algorithm (FAM-1 Structured Base)**
*   **Field:** Prime fields $\mathbb{F}_p$ with $p \approx 2^b$, $b \in \{16, 20, 24, 28, 32\}$.
*   **Curve:** $E: y^2 = x^3 + ax + b$ with $j$-invariant 0 (CM by $\sqrt{-3}$) to maximize endomorphism ring structure for relation generation.
*   **Factor Base $\mathcal{F}$:** All points $P \in E(\mathbb{F}_p)$ with $x(P) \in \mathcal{B}$, where $\mathcal{B} \subset \mathbb{F}_p$ is the set of **structured polynomials**: $x = u^2 + c$ (quadratic) or $x = u$ (linear), $u \in \mathbb{F}_p$, $|u| < B_{bound}$. Size $|\mathcal{F}| \approx p^{1/2}$.
*   **Relation Harvest (ICP Coincidence):** For random $R = [r]G + [s]T$, compute $x(R)$. Check if $x(R) = f(u)/g(u)$ where $f,g \in \mathcal{B}[u]$ deg $\le 2$ (FAM-1 geometry). Use **planted positive controls**: Generate 100 relations *artificially* by picking $u \leftarrow \mathbb{F}_p$, computing $x = f(u)/g(u)$, solving for $y$ (50% success), logging $(r,s,u)$. This guarantees $\kappa_{rel}$ measurement isn't bottlenecked by search luck.
*   **Linear Algebra:** Solve $M \vec{v} = \vec{0}$ over $\mathbb{Z}/\ell\mathbb{Z}$ ($\ell = |E|$) via Block Wiedemann. Target: Recover $\log_G T$.

**2. Cost Model & Metric $\kappa_{rel}$**
*   **Relation Cost $C_{rel}$:** CPU cycles per *harvested* relation (including polynomial eval, point addition, factorization check).
*   **LA Cost $C_{LA}$:** Cycles for Block Wiedemann on $|\mathcal{F}| \times |\mathcal{F}|$ matrix (sparsity $\approx 6$).
*   **Total Cost $C_{tot}(b) = C_{rel}(b) \cdot |\mathcal{F}| + C_{LA}(b)$.**
*   **Metric:** $\kappa_{rel}(b) = \frac{\log_2 C_{tot}(b)}{b}$.
*   **Growth Requirement:** $\kappa_{rel}(b_{i+1}) - \kappa_{rel}(b_i) \le \delta^* + \epsilon$ where $\delta^* = 0.125$ (i.e., $2^{8\delta^*} = 2^1 = 2\times$ cost per 4-bit step). Target $\kappa_{rel} \to 0.5$ (sqrt(p) barrier).

**3. Falsification Criteria**
1.  **Growth Violation:** $\exists i: C_{tot}(b_{i+1}) / C_{tot}(b_i) > 2^{1.5}$ (exceeds $2^{8\delta^*}$ by >50%).
2.  **Structured Base Failure:** Planted relation yield $< 90\%$ for $b=32$ (geometry mismatch).
3.  **LA Dominance:** $C_{LA} > 10 \cdot C_{rel} \cdot |\mathcal{F}|$ at $b=32$ (matrix density/sparsity collapse).
4.  **Asymptotic Divergence:** Fitted $\kappa_{rel}(b) > 0.55$ at $b=32$ (extrapolates to $> \sqrt{p}$).

**4. First Experiment (Week 1)**
*   **Implement:** `fam1_harvest.py` using `crypto-autoresearcher` scaffolding (SageMath/FLINT).
*   **Target:** $b=16$ ($p \approx 65537$).
*   **Steps:**
    1.  Generate curve $E/\mathbb{F}_p$ ($j=0$), base $G$, random $T$.
    2.  Build $\mathcal{B} = \{u^2 + c_1, u + c_2\}$ for small $c_i$.
    3.  **Planted Control:** Generate 500 relations via $u \leftarrow [0, 255]$, compute $x = u^2+1$, find $y$, solve DLP for $(r,s)$ via brute-force (feasible at 16-bit).
    4.  **Wild Harvest:** Run random walk for 10k steps, measure $C_{rel}$.
    5.  Construct matrix, run Block Wiedemann (NTL), measure $C_{LA}$.
    6.  Output $\kappa_{rel}(16)$ and planted/wild yield ratio.

## Direction 2

**Construction / Algorithm**  
1. **Ingest & Parse**: Load all 47 PFDR/PATH proposals from `isogeny-labs/crypto` and `crypto-autoresearcher` ledgers. Extract the polynomial system $\mathcal{F} = \{f_1, \dots, f_m\} \subset \mathbb{F}_p[x_1, \dots, x_n]$ defining the relation generation (descent/sieving) step. Normalize coefficient encoding (Montgomery vs. Barrett, limb-size).  
2. **Invariant Signature**: For each system, compute the **Macaulay Matrix** $M_d$ at degree $d = \max(\deg f_i) + 1$ (first fallback degree). Compute the **Hilbert Series** $H_{\mathcal{F}}(t)$ via Gröbner basis (F4, `msolve`/`fgb`) up to degree $d+2$. Extract signature tuple:  
   $\sigma = (\text{dim}, \text{deg}, \text{reg}, \text{Betti}_{0..d}, \text{SymGroup})$  
   where $\text{SymGroup}$ is the automorphism group of the ideal (computed via `Singular`/`Sage` ideal isomorphism check).  
3. **Canonical Form**: For each equivalence class under $\sigma$, select the lexicographically minimal reduced Gröbner basis (grevlex) as the **Canonical Normal Form (CNF)**.  
4. **Deduplication**: Cluster proposals by $\sigma$. Verify isomorphism via ideal transport maps (linear change of vars + scaling). Output $\le 12$ CNFs with provenance mapping.

**Cost Model**  
*   **Time**: $O(N \cdot T_{\text{GB}}(n, m, d, p))$. $N=47$. $T_{\text{GB}}$ dominated by F4 matrix reduction at $d \approx 4..6$. Estimate: 2–8 CPU-hours/proposal on 64-core (AMD EPYC). Total $\le 200$ core-hours.  
*   **Memory**: Peak $O(\binom{n+d}{d}^2)$ for Macaulay matrix. Max expected $n=12, d=6 \implies \sim 50\text{k} \times 50\text{k}$ sparse $\approx 16\text{ GB}$/job.  
*   **Storage**: $\sim 5\text{ GB}$ for intermediate bases + signatures.

**Falsification Criteria**  
1.  **Collision Failure**: $> 12$ distinct $\sigma$ tuples survive after isomorphism verification (implies structural diversity exceeds deduplication hypothesis).  
2.  **Isomorphism Breakdown**: Two proposals share $\sigma$ but *no* invertible linear map $A \in GL_n(\mathbb{F}_p)$ exists s.t. $\mathcal{F}_1(A\mathbf{x}) = \mathcal{F}_2(\mathbf{x})$ (mod ideal), verified by solving the polynomial isomorphism system (degree $\le 2$).  
3.  **Complexity Explosion**: Any single GB computation exceeds $500$ GB RAM or $48$ hrs (indicating $d_{\text{reg}}$ too high for normal-form utility).

**First Experiment**  
Run the pipeline on the **5 "core" PATH proposals** (PATH-001, 004, 007, 012, 019 — highest citation/complexity).  
*   **Step**: Compute $\sigma$ for all 5 using `msolve` (Rust) with `grevlex`, $d_{\text{max}}=8$.  
*   **Success Metric**: $\ge 3$ proposals collapse to $\le 2$ CNFs within $24$ hrs wall-time / $64$ GB RAM.  
*   **Deliverable**: JSON ledger `cnf_sweep_v1.json` mapping `proposal_id -> {cnf_id, sigma, gb_time, isomorphism_map}`.

## Direction 3

**Construction / Algorithm**  
1. **Digit presentation**: For target curve $E/\mathbb{F}_p$, fix $m \in \{2,3\}$. Represent $S_m$ (Semaev’s $m$-th summation polynomial) in the *digit basis* $\{x^{p^i}\}_{i=0}^{m-1}$ over $\mathbb{F}_p$ via repeated Frobenius reduction, yielding a polynomial system $\mathcal{F}_m \subset \mathbb{F}_p[x_1,\dots,x_m]$ of degree $\leq 2^{m-1}$ in each variable.  
2. **Factor base**: Choose $B = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{V}\}$ where $\mathcal{V} \subset \mathbb{F}_p$ is a degree-$g$ subvariety (e.g., $g=2$ for $m=2$, $g=3$ for $m=3$) defined over $\mathbb{F}_p$ with $\#\mathcal{V} \approx p^{1/m}$.  
3. **Independent primes per $s$**: For each relation search degree $s \in [2,8]$, select a distinct auxiliary prime $p_s \approx p^{1/s}$ and lift $\mathcal{F}_m$ to $\mathbb{F}_{p_s}$; solve the lifted system via Gröbner basis (F4) with degree bound $D_s = \lceil 2^{m-1} \cdot s / m \rceil$.  
4. **Certified ladder**: Verify that the maximal degree in the F4 run never exceeds $D_s$ (certificate = degree-bounded Macaulay matrix rank profile). If certificate holds, descend solutions to $\mathbb{F}_p$ via norm equations and check $x$-coordinate membership in $\mathcal{V}$.  
5. **Relation assembly**: Each certified solution yields a relation $\sum_{i=1}^m [P_i] = \mathcal{O}$ with $P_i \in B$. Collect until matrix is square.

**Cost Model**  
- Offline: $s_{\max}=8$ independent Gröbner runs. Cost dominated by $s=8$: $O\left(\binom{D_8 + m}{m}^\omega\right)$ field ops in $\mathbb{F}_{p_8}$, $D_8 \approx 2^{m-1} \cdot 8/m$.  
- Online: Relation search expects $\tilde{O}(p^{1/m})$ trials per relation; linear algebra $O((p^{1/m})^\omega)$.  
- Total heuristic: $\tilde{O}(p^{\max(2/m, \omega/m)})$ for $m=2,3$. Target: beat $p^{1/2}$ for $m=3$.

**Falsification Criteria**  
1. Certificate fails for any $s \in [2,8]$ (degree exceeds $D_s$ in F4).  
2. Norm descent yields $< 1\%$ valid $\mathbb{F}_p$-points in $\mathcal{V}$.  
3. Relation yield $< 0.1 \cdot p^{-1/m}$ per trial.  
4. Wall-clock for $s=8$ certificate $> 10^4$ sec on 64-core.

**First Experiment**  
Run H-PFDR-d5f90f: $p \approx 2^{160}$, $m=3$, $s=2..8$, $p_s$ = next prime $> p^{1/s}$. Use `msolve` with `max_degree=D_s`, `certificate=true`. Controls: block-factored nulls (random $\mathcal{V}$ of same dimension, 10 reps per $s$). Measure: max degree reached, certificate pass/fail, $\mathbb{F}_p$-descent rate, relation yield. Stop if any $s$ fails certificate.

## Direction 4

**Construction/Algorithm: H-GFPN-3366ea (Oracle-Assisted Static DH Source Freeze)**

1.  **Factor Base $\mathcal{F}$:** $x$-coordinates in $\mathbb{F}_p$ with $x < B \approx p^{1/3}$ (standard JV bound).
2.  **Oracle $\mathcal{O}$ (Static DH):** Pre-compute $Q_i = [d]P_i$ for fixed secret $d$ and all $P_i \in \mathcal{F}$. Freeze this dataset. $\mathcal{O}(R) = x([d]R)$ for arbitrary $R$.
3.  **Relation Generation (4-Point Decomposition $\mathcal{D}_4$):** For random $a,b \in [1, n-1]$, compute $R = [a]G + [b]Q_{target}$. Use $\mathcal{O}$ to evaluate Semaev polynomial $f_4(x_1, x_2, x_3, x_4; x_R) = 0$. Solve for $(x_1,x_2,x_3,x_4) \in \mathcal{F}^4$ via Groebner basis (F4) over $\mathbb{F}_p$ using the "Granger" symmetric variable elimination ($s_j = \sigma_j(x_i)$).
4.  **Source Freeze:** The oracle outputs $x([d]R)$ are *static* per $R$. We do not re-solve $f_4$ per query; we pre-compute the decomposition tree structure for the frozen $Q_i$ set. Relation cost $C_{pdp4}$ = cost to solve $f_4=0$ given $x_R$ and frozen symmetric sums of $\mathcal{F}$.

**Cost Model (Projected to $p=2^{64}$)**
*   $C_{pdp4}(p') = T_{gb}(p') + T_{solve}(p')$ measured at $p' \in [2^{16}, 2^{20}]$.
*   $T_{gb}$: F4 Groebner basis time for $f_4$ system (deg $\approx 8$, 4 vars $\to$ 3 sym vars).
*   $T_{solve}$: Root finding / back-substitution.
*   **Projection:** $C_{pdp4}(2^{64}) \approx C_{pdp4}(p') \cdot (\log_2 p / \log_2 p')^2 \cdot (D_{reg}(64)/D_{reg}(p'))^\omega$.
    *   $\omega \approx 2.37$ (matrix mult).
    *   $D_{reg}$: Degree of regularity (expected $\approx 5-6$ for $m=4$).
    *   Error budget: $\pm 30\%$ on $\omega$, $\pm 1$ on $D_{reg}$, $\times 2$ constant factor for $\mathbb{F}_{2^{64}}$ arithmetic vs $\mathbb{F}_{p'}$.
*   Total IC Cost: $L_p[1/2, c] \approx \#\mathcal{F} \cdot C_{pdp4}(2^{64}) / P_{smooth}$. Target $c < 1.0$ (vs $\sqrt{p} \approx 2^{32}$).

**Falsification Criteria**
1.  $D_{reg} > 7$ at $p'=2^{20}$ (implies exponential blowup at $2^{64}$).
2.  Measured $C_{pdp4}(p')$ scales as $p'^\epsilon, \epsilon > 0.5$ (polynomial, not quasi-poly).
3.  Projected $C_{total}(2^{64}) > 2^{40}$ ops (fails to beat Pollard Rho $2^{32}$).
4.  Oracle $\mathcal{O}$ storage $> 2^{20}$ elements (breaks "Static DH" feasibility).

**First Experiment (Week 1-2)**
*   **Repo:** `isogeny-labs/crypto` -> `experiments/icp/gfp5_oa_sdhp_jv/`.
*   **Params:** $p' = 2^{16} - 17$ (NTT friendly), Curve: $y^2 = x^3 + x$ (j=1728, efficient $f_4$). $B = \lfloor p'^{1/3} \rfloor \approx 40$. $\mathcal{F} = \{x < B\}$.
*   **Action:**
    1.  Generate frozen Static DH oracle: Pick random $d$, compute $Q_i = [d]P_i$ for all $P_i \in \mathcal{F}$.
    2.  Implement $f_4$ symmetric system (Granger vars $s_1,s_2,s_3$) in SageMath/F4 (Singular/msolve).
    3.  Benchmark 100 random $R = [a]G + [b]Q_{target}$: Measure $T_{gb}$, $T_{solve}$, success rate ($\mathcal{D}_4$ existence).
    4.  Log: $D_{reg}$ (max degree in F4), matrix dims, wall time.
*   **Deliverable:** `measure_pdp4_p16.json` with raw timings, $D_{reg}$, matrix density. Decision gate: Proceed to $p'=2^{20}$ iff $D_{reg} \le 6$ and $T_{gb} < 10$ms.

## Direction 5

**Research Plan: Odd-Characteristic Cover Genus Certification for EcGFp5/EcMasFp5**

**1. Exact Construction & Algorithm**
*   **Target Curves**: `EcGFp5` (generator curve for GF(p^5) DLP via Weil descent) and `EcMasFp5` (Masser curve, typically higher genus model). Both defined over `F_p` with prime `p ~ 2^64` (or current lab standard).
*   **Isogeny Class Sampling**: Compute the isogeny volcano for the conductor `N` (trace `t = p+1-#E`). Use `isogeny-labs/crypto` volcano traversal to sample a *random* curve `E_rand` in the same isogeny class (same `End(E) ⊗ Q`), distinct from the two targets.
*   **Cover Construction (Diem/Gaudry)**: For each curve `E ∈ {EcGFp5, EcMasFp5, E_rand}`, construct the summation variety `V_m ⊂ (P^1)^m` (or affine `x`-coordinate model) for `m=3,4,5`. Define the covering curve `C_f` as the fiber product of `V_m` under the `x`-coordinate map `x: E → P^1`.
*   **Genus Computation**: Compute the geometric genus `g(C_f)` via Riemann-Hurwitz on the projection `π: C_f → E` (degree `d = m!` or `2^m` depending on model).
    *   Ramification locus: Points where `V_m` is singular or `x` ramifies (2-torsion, points at infinity).
    *   Formula: `2g(C_f) - 2 = d(2g(E)-2) + ∑(e_P - 1)`. Since `g(E)=1`, `2g(C_f) - 2 = ∑(e_P - 1)`.
    *   Implementation: Symbolic computation of ramification indices `e_P` using Gröbner bases / resultants on the defining equations of `V_m ∩ (x^{-1}(t))^m` over `F_p(t)`, certified by `magma`/`singular` via `crypto-autoresearcher` algebraic geometry pipeline.

**2. Cost Model**
*   **Offline (Precomputation)**:
    *   Volcano walk: `O(p^{1/4})` ~ negligible for `p~2^64`.
    *   Summation polynomial `S_m` computation: `O(m^2 2^m)` ops in `F_p[x]` (precomputed in repos).
    *   Ramification analysis (Gröbner basis for `m=4,5`): Dominant cost. Estimated `O((deg S_m)^ω)` ~ hours on 64-core for `m=5`.
*   **Online (Per Curve)**: Evaluation of Riemann-Hurwitz formula using precomputed ramification structure: `< 1 sec`.
*   **Index Calculus Relevance**: Factor base size `~ p`. Relation search cost `L_p(1/2, c)` where `c ∝ sqrt(g)`. Target `g ≥ 9` implies `c ≥ 3`, confirming exponential hardness vs `g=3` (Gaudry) or `g=6` (Diem `m=3`).

**3. Falsification Criteria**
*   **Hard Falsify**: Any curve `E ∈ {EcGFp5, EcMasFp5, E_rand}` yields `g(C_f) < 9` for the optimal `m` (likely `m=4` or `5`).
*   **Soft Falsify**: `g ≥ 9` but the *degree* of the cover `d` is so large (`d > p^{1/2}`) that the factor base representation becomes inefficient (relation probability `1/g!` too low), making the attack complexity `> p`.
*   **Structural Falsify**: `E_rand` genus distribution has variance `> 2`, implying isogeny class does not control genus (invalidating "class control" hypothesis).

**4. First Experiment**
Run `crypto-autoresearcher` pipeline `compute_diem_genus.py` on `EcGFp5` with `m=4`:
1.  Load `EcGFp5` parameters from `isogeny-labs/crypto/curves/gfp5.py`.
2.  Compute `S_4(x_1,x_2,x_3,x_4)` (already cached).
3.  Construct fiber `C_f: S_4(x_1..x_4)=0, x_i = x(P_i), ∑ P_i = O`.
4.  Compute ramification divisor via discriminant of projection `(x_1..x_4) → x_1`.
5.  Output certified genus `g`.
**Success Metric**: `g ≥ 9` certified in `< 4 hrs` wall time. If `g < 9`, immediately test `m=5`.

## Direction 6

**Construction / Algorithm**  
1. **Curve & Quotient**: For a toy prime `p' ≈ 2^40`, select a *double‑odd* curve `E/𝔽_p'` (i.e. `#E = 4·ℓ`, `ℓ` prime). Let `G = E[2] ≅ (ℤ/2)²`. The *double‑odd 2‑torsion quotient* is the set of `x`‑coordinates of `G \ {O}` modulo the involution `x ↦ x` (trivial here) — effectively the three roots of the 2‑division polynomial `ψ₂(x)`.  
2. **Polynomial System**: For the symmetrized Gaudry index‑calculus (LEAD‑ICP‑gfp5), the relation search uses the `x`‑coordinates of factor‑base points. At degree 4, build the Macaulay matrix `M₄` from the Semaev polynomial `s₅(x₁,…,x₅)` specialized to the factor base, then quotient by the ideal generated by `ψ₂(x_i)` for each variable.  
3. **Rank Computation**: Compute `rank(M₄)` over `𝔽_p'` using sparse Gaussian elimination (Wiedemann). The *generic rank* is the number of monomials of degree ≤4 in 5 variables minus the number of independent syzygies expected from the symmetrization.  

**Cost Model**  
- Matrix dimension: `D = binom(5+4,4) = 126` rows/cols before quotient; quotient by `ψ₂` reduces each variable’s degree by 2 → effective dimension `D_eff ≈ 70`.  
- Construction: `O(D_eff²·|F|)` field ops, `|F| = O(p'^{1/2})` (factor‑base size).  
- Rank: `O(D_eff²·nnz)` with `nnz ≈ 5·D_eff`.  
- Memory: `O(D_eff·nnz)` ≈ 25 kB for `p' ≈ 2^40`.  

**Falsification Criteria**  
- If `rank(M₄) ≥ generic_rank - 2` for **all** three test primes `p₁,p₂,p₃` (each ≥12‑bit larger than previous, cofactor‑1), the degree‑4 Macaulay matrix does **not** exhibit a structural rank deficiency → the double‑odd quotient yields no new linear relations at this degree.  
- If memory envelope exceeds `2×` the predicted sparse footprint during any run, the cost model is invalid.  

**First Experiment**  
Run `H-GFPN-6cc6aa --cofactor 1 --null` on the smallest toy prime `p' = 2^40 - 87` (double‑odd curve `y² = x³ + x + 1`). Log `rank(M₄)`, `generic_rank`, wall time, and peak RSS. If `rank < generic_rank - 2`, proceed to the 3‑prime C1 ladder; else terminate.

## Direction 7

**Construction/Algorithm**  
1. **Ground truth generation**: For each l∈{5,6}, enumerate all factor-base elements (x-coordinates) and precompute exhaustive side-classified relation tables: for every target point T, list all decompositions T = Σ P_i with P_i in factor base, tagged by sign-pattern (side) of y-coordinates. Store as CSV: `target_x, decomposition_id, [fb_indices], side_mask`.  
2. **Binary PDP formulation**: Encode each decomposition as a Boolean polynomial system over GF(2): variables `z_i ∈ {0,1}` indicate factor-base membership; equations enforce `Σ z_i·x_i = x_T` (via lookup-table ANF) and side-consistency `Σ z_i·side_i = 0`. Degree ≤ 3 after ANF conversion.  
3. **BRiAl solver**: Use BRiAl’s `groebner_basis` with `deg_bound` instrumentation. Emit parseable `d_solv` (max degree reached) and `t_solve` per instance. Wrap in RSS watchdog (poll `/proc/self/status` every 100 ms; kill if RSS > 4 GB).  
4. **WDSat baseline**: Translate same ANF to CNF via `anf2cnf` (XOR→Tseitin), feed to CaDiCaL with `—no-binary-clauses`. Record `t_sat`, `conflicts`, `decisions`.

**Cost Model**  
- **Time**: `t_solve` (BRiAl) vs `t_sat` (WDSat) per instance; median over 1000 targets.  
- **Memory**: peak RSS (BRiAl) vs peak RSS (CaDiCaL).  
- **Algebraic complexity**: `d_solv` distribution; correlation with `log₂(#solutions)`.  
- **Scaling proxy**: fit `log(t) ~ α·l + β·d_solv` for l=5→6 extrapolation.

**Falsification Criteria**  
- BRiAl median `t_solve` > 2× WDSat median `t_sat` on l=6.  
- `d_solv` ≥ 8 for >10% of l=6 instances (degree explosion).  
- RSS watchdog triggers on >5% of l=6 runs (memory wall).  
- No statistically significant correlation (p>0.05) between `d_solv` and solution-count entropy.

**First Experiment**  
Generate l=5 exhaustive table (≈ 2^15 targets). Run BRiAl + WDSat on first 200 targets with `deg_bound=6`, RSS limit 2 GB. Collect `d_solv`, `t_solve`, `t_sat`, RSS. Plot `d_solv` histogram vs solution-count bins. If BRiAl wins on median time and `d_solv` ≤ 5, proceed to full l=5/l=6 sweep.

## Direction 8

**Research Plan: EXP-ECTD-0cf008 Completion (17 Missing Arms)**

**1. Exact Construction / Algorithm**
*   **Target Set:** 32,768 random ECDLP instances $(P, Q=[k]P)$ on $E/\mathbb{F}_p$ ($p \approx 2^{128}$).
*   **Factor Bases (FB):**
    *   *Native:* $\mathcal{F}_{nat} = \{R \in E(\mathbb{F}_p) : x(R) \in \mathcal{B}\}$ where $\mathcal{B}$ is the set of $x$-coordinates of $\mathbb{F}_p$-rational points on the 17 specific isogenous curves $E_i$ reached via $\ell=8209$ and $\ell=131101$ isogeny walks (crater/floor pairs) from $E$.
    *   *Random:* $\mathcal{F}_{rand} \subset E(\mathbb{F}_p)$, $|\mathcal{F}_{rand}| = |\mathcal{F}_{nat}|$, uniform random $x$-coordinates.
*   **Relation Search:** For each target $Q$, decompress $Q + [r]P$ ($r \leftarrow \mathbb{Z}_n$). Check if $x$-coordinate lands in $\mathcal{B}$ (Native) or $\mathcal{F}_{rand}$ (Random).
*   **Arity-3 Enforcement:** Only accept relations where the decomposition yields exactly 3 factor base elements (verified via Vélu's formulas on the isogenous neighbors). Discard arity $\neq 3$.
*   **Transport:** Map valid relations back to $E$ via dual isogenies to form linear equations in $k$.
*   **Arms:** 17 Arms = (Conductor $\ell \in \{8209, 131101\}$) $\times$ (Level: Crater/Floor) $\times$ (FB Type: Native/Random) $\times$ (Direction: Ascending/Descending) minus 1 already completed baseline.

**2. Cost Model**
*   **Isogeny Setup (Amortized):** $O(\ell \log^2 p)$ per curve for Vélu; $\approx 2 \times 10^6$ $\mathbb{F}_p$-ops per conductor. Total setup $\approx 3.4 \times 10^7$ ops (negligible).
*   **Relation Search (Dominant):** Cost per trial = 1 scalar mult ($128$ doubles + $64$ adds $\approx 10^4$ $\mathbb{F}_p$-muls) + 1 $x$-coordinate lookup (Hash table: $O(1)$).
*   **Expected Trials:** Heuristic probability $\rho \approx |\mathcal{F}| / p$. Target $|\mathcal{F}| \approx 2^{20}$. $\rho \approx 2^{-108}$.
*   **Total Cost/Arm:** $32,768 \times 2^{108} \times 10^4$ $\mathbb{F}_p$-muls $\approx 2^{128}$ ops (Infeasible for full run).
*   **Experimental Mode:** Reduce $p$ to 64-bit ($p \approx 2^{64}$), $|\mathcal{F}| \approx 2^{16}$. Cost/Arm $\approx 2^{54}$ ops $\approx 4$ GPU-days. 17 Arms $\approx 68$ GPU-days.

**3. Falsification Criteria**
1.  **Coverage Null:** Native FB coverage (relations found / 32,768 targets) $\leq$ Random FB coverage $+ 2\sigma$ (variance across arms).
2.  **Arity Collapse:** Verified arity-3 relations $< 0.1\%$ of total raw hits for Native FB (indicating transport failure).
3.  **Conductor Parity:** No statistically significant difference ($p < 0.01$, Welch's t-test) in yield between $\ell=8209$ and $\ell=131101$ arms.
4.  **Topology Invariance:** Crater vs Floor yield difference $< 1\%$ (invalidating volcano structure hypothesis).

**4. First Experiment (Week 1)**
*   **Scope:** Single Arm: $\ell=8209$, Crater, Ascending, Native FB.
*   **Parameters:** $p \approx 2^{64}$ (Curve `secp64k1` or generated), $|\mathcal{F}_{nat}| \approx 65,536$.
*   **Execution:** Launch 32,768 independent walkers (1 per target) on 8x A100 GPUs. Kernel: Fixed-window scalar mult + hash probe.
*   **Metrics:** Relations found, Arity-3 verification rate, Time/Relation.
*   **Go/No-Go:** If Arity-3 rate $> 5\%$ and Native yield $> 1.5\times$ Random baseline (run concurrently on CPU), scale to full 17-arm matrix.

## Direction 9

**Construction (Admitted-Polynomial Lattice IC Pipeline)**
1. **Factor Base**: $\mathcal{F} = \{ (x - \alpha_i) \mid \alpha_i \in S \}$ where $S \subset \mathbb{F}_p$ is a structured set (e.g., subgroup coset, trace-zero variety intersection, or low-height rational points). Target $|\mathcal{F}| \approx p^{1/2}$.
2. **Admitted Polynomial Successor**: Define $f_{k+1}(x) = f_k(x) \cdot g_k(x) + h_k(x) \mod (x^p - x, E_{a,b})$. $g_k$ is chosen from a lattice $\Lambda_k \subset \mathbb{F}_p[x]_{<d}$ to force $f_{k+1}$ to split over $\mathcal{F}$ with probability $\rho$. $h_k$ corrects the curve equation residue.
3. **Lattice Construction**: For target relation $f(x) \equiv \prod (x-\alpha_i)^{e_i}$, build lattice $\mathcal{L}$ with rows: coefficient vectors of $x^j f(x) \bmod \psi_E(x)$ (division poly) and $x^j \psi_E(x)$. Short vectors $v \in \mathcal{L}$ yield $g(x)$ s.t. $f \cdot g \equiv \text{smooth}$.
4. **Rank-2 Control ($\mathbb{F}_{25}$)**: Embed $\mathbb{F}_{25} \cong \mathbb{F}_5[\zeta]$. Run identical pipeline on $E/\mathbb{F}_{25}$ (trace 0, rank 2). Verify relation independence via $\text{Gal}(\mathbb{F}_{25}/\mathbb{F}_5)$-action on factor base orbits. Certify rank via matrix rank over $\mathbb{Z}/\ell\mathbb{Z}$.

**Certification Metrics (Explicit Primes)**
- **Density**: $\rho = \frac{\#\{ \text{smooth } f_{k+1} \}}{\# \text{trials}}$ on $p \in \{43, 97, 101\}$. Target $\rho > p^{-0.4}$.
- **Valid Roots**: 100% of reported relations satisfy $f(x) \equiv \prod (x-\alpha_i)^{e_i} \pmod{E}$ via resultant check.
- **Independent Rank**: Relation matrix $M \in \mathbb{Z}^{|\mathcal{F}| \times N}$ has $\text{rank}(M) = |\mathcal{F}| - 1$ (kernel = discrete log).
- **Complete Relation Cost**: $C = T_{\text{LLL}} + T_{\text{sieve}} + T_{\text{lin}}$. Report $\log_2 C$ per prime.

**Cost Model**
$T_{\text{LLL}} \approx O(d^4 \log^3 p)$ for dim $d \approx p^{1/2}$. $T_{\text{sieve}} \approx O(\rho^{-1} d^2)$. $T_{\text{lin}} \approx O(|\mathcal{F}|^\omega)$. Total heuristic: $L_p[1/2, c]$ with $c \approx 1.0$ if $\rho \approx p^{-1/2}$.

**Falsification Criteria**
1. $\rho < p^{-0.6}$ for $p=101$ (density collapse).
2. $\text{rank}(M) < |\mathcal{F}| - 5$ after $2|\mathcal{F}|$ relations (dependency failure).
3. $T_{\text{LLL}} > 2^{20}$ ops for $p=101$ (lattice dim explosion).
4. $\mathbb{F}_{25}$ control yields rank deficit $> 2$ vs prediction (structural flaw).

**First Experiment**
Implement pipeline for $p=43$, $E: y^2 = x^3 + x + 1$, $\mathcal{F} = \{x - \alpha \mid \alpha \in \mathbb{F}_{43}^*\}$ (size 42).
1. Construct $\mathcal{L}$ targeting deg $f=5$, lattice dim $d=21$.
2. Run LLL (fpLLL) to find short $g(x)$.
3. Check smoothness of $f \cdot g \bmod \psi_E$ over $\mathcal{F}$.
4. Repeat 5000x. Measure $\rho$, avg $||g||$, relation validity.
5. Parallel run on $E/\mathbb{F}_{25}$ (same $j$-inv) for rank-2 control.
6. Output: $\rho_{43}$, rank($M_{43}$), $\rho_{25}$, rank($M_{25}$), $T_{\text{LLL}}$.

**Four-Track Review**
1. **Crypto-autoresearcher**: Reproduce $p=43$ density vs heuristic $L_p[1/2, 1.0]$; flag lattice dimension vs smoothness bound tradeoff.
2. **Isogeny-labs/crypto**: Cross-check relation validity using Vélu/Isogeny walk verification; test if admitted poly structure leaks torsion info.
3. **Prior Art (Joux-Vitse, Diem, Nagao)**: Compare lattice dim $d$ vs Function Field Sieve basis size; verify "admitted successor" isn't re-deriving Harper's lattice descent.
4. **Hardware/Impl**: Profile fpLLL vs custom BKZ on relation lattice; assess $T_{\text{LLL}}$ scaling to $p=97$.

## Direction 10

**Construction / Algorithm**  
Implement a staged Gröbner basis / XL fall-degree pipeline targeting the Semaev polynomial system for ECDLP over prime fields $\mathbb{F}_p$, using the PKM tower representation ($m=2$ Kummer surface) to reduce variable count.  
Stages:  
- **g4**: Generate Macaulay matrix at degree $D=4$ for the $m=2$ summation polynomial $S_3$ on the Kummer $x$-coordinates.  
- **hky-A / d-A / cap-A**: Apply hybrid F4 (hky), sparse $F_5$ (d), and Cap-optimized (cap) linear algebra at degree $D$ to compute the degree of regularity $d_{reg}$ and fall-degree $d_F$ median over 100 random instances.  
- **hky-C / hky-B / d-B**: Repeat at $D=5,6$ with column/row pruning (C), block-Wiedemann (B), and dense $F_4$ (d) variants.  
All stages run on a dedicated GPU node (A100 80GB); multiply-add counters instrumented via `cusparse`/`cublasLt` hooks.

**Cost Model**  
$C = \sum_{stage} (M_{stage} \cdot \tau_{MADD} + M_{stage} \cdot \tau_{mem} + \log_2(\text{rows}) \cdot \tau_{sync})$, where $M_{stage}$ = recorded multiply-adds, $\tau_{MADD}=0.3$ ns, $\tau_{mem}=1.2$ ns, $\tau_{sync}=5 \mu s$. Wall-clock budget: 72 h.

**Falsification Criteria**  
1. Stage A (hky-A/d-A/cap-A at $t=1$, $D=4$) fails to reproduce the preregistered Kummer $m=2$ fall-degree medians $[3,4,4,4,4,5,5,5,5,6]$ (exact match, 100 seeds).  
2. Any stage exceeds $2\times$ predicted $M_{stage}$ from the $D=4$ scaling law $M_D \approx M_4 \cdot \binom{n+D}{D}/\binom{n+4}{4}$.  
3. Memory footprint $> 70$ GB at any stage.

**First Experiment**  
Run **Stage g4 → hky-A** for 100 random curves over a 64-bit prime $p$, $m=2$ Kummer $S_3$ system ($n=8$ vars after symmetrization). Instrument multiply-adds in the F4 reduction kernel. Verify median $d_F$ sequence matches $[3,4,4,4,4,5,5,5,5,6]$. Log $M_{hky-A}$, wall time, peak VRAM. If median mismatches or $M_{hky-A} > 1.2 \times 10^{12}$, abort and re-parameterize $D$ or variable ordering.

## Direction 11

**Construction / Algorithm**  
Reproduce the *constant-engineering recipe* from Section 13 (isogeny-labs/crypto#IC-constant-engineering) for prime-field index calculus targeting the 20-bit holdout set (1,008 curves, N=46…50). The recipe fixes:  
1. **Polynomial selection**: `f(x) = x^N + c_{N-1}x^{N-1} + … + c_0` where coefficients `c_i` are drawn from the pre-computed “leaderboard” distribution (Pareto-optimal for `log2(p) ≈ 20`, `N>45`).  
2. **Factor base**: Degree-1 primes `π` with `Norm(π) < B = 2^{12.3}`.  
3. **Relation search**: Structured sieving on `a + b·x` with `|a|,|b| ≤ 2^7`, using the constant-engineered `f(x)` to maximize smoothness probability.  
4. **Linear algebra**: Block-Lanczos over `GF(2)` on the resulting `≈1.2B` relations.  

**Cost Model**  
`T_total = T_poly + T_sieve + T_LA`.  
- `T_poly`: Negligible (constants pre-computed).  
- `T_sieve`: `O(B · 2^{14} · M(N))` where `M(N)` is poly-mul cost. For 20-bit: `≈ 2^{28}` ops.  
- `T_LA`: `O(B^2)` bit-ops. For 20-bit: `≈ 2^{24.6}`.  
**24-bit projection**: `B' = 2^{14.8}`, `T_sieve' ≈ 2^{33}`, `T_LA' ≈ 2^{29.6}`. Target wall-time < 72 h on isolab-eks (c6i.32xlarge × 8).

**Falsification Criteria**  
1. **Reproducibility break**: Any of the 1,008 20-bit records fails verification on isolab-eks (hash mismatch on relation set or log).  
2. **Scaling collapse**: 24-bit smoothness yield drops > 3× vs. model prediction (i.e. `yield_24 < yield_20 / 3`).  
3. **Constant decay**: Leaderboard constants for N>45 produce `>5%` more relations than the fixed recipe on 24-bit curves (recipe not transferable).

**First Experiment**  
Run the *exact* 20-bit pipeline (fixed constants, same sieving bounds, same LA parameters) on **one** previously unseen 24-bit curve (`p ≈ 2^24`, N=46) using the promoted leaderboard constants. Measure:  
- Relations found per CPU-hour vs. 20-bit baseline.  
- Smoothness probability `Pr[smooth]` for `Norm(a+bx)`.  
- Matrix density and Lanczos iteration count.  
Pass gate: `Pr[smooth]_24 ≥ 0.3 × Pr[smooth]_20` and matrix builds in < 4 h.

## Direction 12

**Construction / Algorithm**
1.  **Input:** Prime $p$, factor base $\mathcal{F}$ (deg $k=3,4$), $N \ge 5$ distinct usable $x_i \in \mathbb{F}_p$ yielding split polynomials $f_{x_i}(t) = \prod_{j=1}^k (t - r_{ij})$.
2.  **Circuit Construction per $x_i$:** For each root set $\{r_{ij}\}$, build four arithmetic circuits computing the divisor coefficient vector $\mathbf{c} \in \mathbb{F}_p^m$ (targeting symmetric sums or PKM basis):
    *   **PKM:** Direct power-sum $p_\ell = \sum_j r_{ij}^\ell$ via Horner, Newton identities to $\mathbf{c}$.
    *   **Symmetric:** Elementary symmetric polynomials $e_\ell$ via Vieta’s formulas (subproduct tree).
    *   **Quotient:** Compute $f_{x_i}(t) / (t - r_{ij})$ for each $j$ via synthetic division; derive $\mathbf{c}$ from quotient coefficients.
    *   **Graeffe:** Iterate $f^{(s+1)}(t) = (-1)^k f^{(s)}(\sqrt{t}) f^{(s)}(-\sqrt{t})$ to isolate power sums $p_{2^s}$; reconstruct $\mathbf{c}$.
3.  **Shared-Coefficient Extraction:** For each circuit type, identify the sub-circuit DAG nodes computing the *final* coefficients $c_1, \dots, c_m$. Hash the normalized (commutative/associative canonicalized) DAG structure of each coefficient node across all $N$ inputs.
4.  **Chart Census:** Construct the "Chart" $C_k$: a map from Coefficient Index $\to$ Equivalence Class of Shared Sub-Circuit DAGs. Freeze census when $N \ge 5$ distinct $x$ yield stable equivalence classes (no new DAG hashes appear for 3 consecutive $x$).
5.  **Negative Control ($k=2$):** Execute steps 1–4. Verify Chart $C_2$ is empty (no shared sub-circuits beyond trivial constants) for squarefree $f_x$.

**Cost Model**
*   **Metric:** *Shared Circuit Complexity (SCC)* = $\sum_{\text{class} \in C_k} (\text{Size}(\text{DAG}_{\text{class}}) \times \text{Frequency}(\text{class}))$.
*   **Baseline:** Naive per-root evaluation cost $O(k^2)$ or $O(M(k)\log k)$ per $x$.
*   **Target:** Prove $SCC(C_k) < N \times \text{Cost}_{\text{naive}}$ for $k=3,4$ implying amortized sub-linear cost per relation.
*   **Overhead:** Canonicalization cost $O(|V| \log |V|)$ per node.

**Falsification Criteria**
1.  **Instability:** Census for $k=3$ or $k=4$ fails to freeze after $N=20$ distinct usable $x$ (new DAG classes keep appearing).
2.  **Negative Control Failure:** $C_2$ contains non-trivial shared sub-circuits (size $> 1$ node) for squarefree inputs.
3.  **No Compression:** $\text{SCC}(C_k) \ge N \times \text{Cost}_{\text{naive}}$ for frozen $C_3, C_4$.
4.  **Isomorphism Gap:** PKM, Symmetric, Quotient, Graeffe charts $C_k^{\text{type}}$ are not pairwise isomorphic (DAG hash mismatch) for same $k$, implying representation-dependent structure, not intrinsic divisor structure.

**First Experiment**
Implement the circuit builder in Rust (using `ark-ff` for $\mathbb{F}_p$ arithmetic, $p \approx 2^{61}-1$). Target $k=3$. Generate 10 random $x$ yielding split cubics. Construct 4 circuit types per $x$. Canonicalize DAGs (sort children by hash, deduplicate). Compute $C_3^{\text{type}}$ for each type. Verify: (a) $C_3^{\text{PKM}} \cong C_3^{\text{Sym}} \cong C_3^{\text{Quot}} \cong C_3^{\text{Graeffe}}$; (b) $C_2 = \emptyset$ for 10 split quadratics. Output: DAG hash tables, SCC values, isomorphism proof logs.

## Direction 13

**Research Plan: Direction 13 — Macaulay Ranks of Chained S₄ at Special j**

**1. Exact Construction / Algorithm**
*   **Polynomial System:** Construct the *chained S₄* summation polynomial system for relation search: $S_4(x_1, x_2, x_3, x_4) = 0$ where $x_i = f_i(u_i)$ are rational functions (degree $\delta$) mapping factor base variable $u_i \in \mathbb{F}_p$ to $x$-coordinates. Use "digit" decomposition: $u_i = \sum_{k=0}^{D-1} u_{i,k} B^k$ for base $B \approx p^{1/D}$.
*   **Specialization:** Instantiate curve $E/\mathbb{F}_p$ at $j=0$ ($y^2 = x^3 + b$) and $j=1728$ ($y^2 = x^3 + ax$). Compare against generic $j \notin \{0, 1728\}$.
*   **Macaulay Matrix $M_d$:** For degree $d \in [2, 6]$, build the Macaulay matrix over $\mathbb{F}_p$ using monomials in $\{u_{i,k}\}$ up to total degree $d$. Rows: polynomial multiples of the system equations (Weil descent of $S_4$ + field equations $u_{i,k}^p - u_{i,k}$). Columns: monomials.
*   **Coefficient-Block Vanishing:** Identify column blocks corresponding to monomials containing $u_{i,k}^e$ where $e$ triggers automorphism-induced symmetries (e.g., $e \equiv 0 \mod 3$ for $j=0$, $e \equiv 0 \mod 2$ for $j=1728$). Compute rank $r_d = \text{rank}(M_d)$ and nullity $\nu_d = \text{cols}(M_d) - r_d$. Track $\nu_d$ restricted to symmetry blocks.

**2. Cost Model**
*   **Matrix Size:** $N_d \approx \binom{4D + d}{d}$. Target $D=2,3$ (so $4D=8,12$ vars). For $d=6, D=3$: $N_6 \approx \binom{18}{6} \approx 18k$ cols.
*   **Complexity:** Dense Gaussian elimination $O(N_d^\omega)$, $\omega \approx 2.8$. Sparse Wiedemann $O(N_d^2)$.
*   **Metric:** Rank deficit $\Delta_d = \nu_d^{\text{special}} - \nu_d^{\text{generic}}$. Speedup factor $\approx (N_d / (N_d - \Delta_d))^\omega$ for F5/Gröbner basis.

**3. Falsification Criteria**
*   **Hard Falsify:** For all three toy primes ($p \approx 2^{16}, 2^{24}, 2^{32}$) and $d=2..6$, $\Delta_d \le 1$ (statistical noise).
*   **Soft Falsify:** $\Delta_d > 0$ but $\Delta_d / N_d < 10^{-3}$ (asymptotically negligible block sparsity).
*   **Structural Falsify:** Null vectors in symmetry blocks do *not* correspond to valid factor base relations (i.e., they are parasitic syzygies from field equations, not $S_4$ structure).

**4. First Experiment (Week 1)**
*   **Code:** Extend `H-PFDR-df0127` (Macaulay builder) and `H-PFDR-6b9f1a` (symmetry detector).
*   **Parameters:** $p_1 = 65521$ ($2^{16}-15$), $D=2$ ($B=256$), $d=3,4$.
*   **Curves:** $E_0: y^2=x^3+1$ ($j=0$), $E_{1728}: y^2=x^3+x$ ($j=1728$), $E_{\text{gen}}: y^2=x^3+x+1$.
*   **Action:** Build $M_3, M_4$ for all 3 curves. Compute dense rank (Sage `rank()`). Log $\nu_d$ per curve. Extract nullspace basis vectors for $j=0, 1728$; verify if support lies strictly in predicted symmetry blocks (e.g., $u_{i,k}^3$ terms for $j=0$).
*   **Deliverable:** Table of $(p, d, j, \text{rows}, \text{cols}, r_d, \nu_d, \Delta_d)$ + nullspace support heatmaps.

## Direction 14

**Research Plan: Simulation Lemma for Class-Group Action in Curve-Aware GGM (H-CLGP-63f471)**

**1. Construction / Algorithm: The Simulator $\mathcal{S}$**
Define the **Curve-Aware Generic Group Model (CA-GGM)**. The adversary $\mathcal{A}$ receives:
*   Standard group oracles: `Add`, `Neg`, `Eq` for an unknown target curve $E_0/\mathbb{F}_p$ (order $N \approx p$).
*   **Class-Group Action Oracle $\mathcal{O}_{\text{cl}}$**: On query $(\mathfrak{a}, [P])$ where $\mathfrak{a} \in \text{Cl}(\mathcal{O})$ (represented as reduced ideal) and $[P] \in E/\mathbb{F}_p$ (handle), returns handle for $[\mathfrak{a}] \cdot P$ on curve $E' = [\mathfrak{a}] \cdot E$. $\mathcal{A}$ can request action on *any* curve handle it holds.

**Simulator $\mathcal{S}$ Strategy (Lazy Sampling with Isogeny Graph Consistency):**
1.  Maintain a dynamic graph $G = (V, E)$ where vertices $v \in V$ are curve isomorphism classes (represented by random handles $h_v$) and edges are $\ell_i$-isogenies for small primes $\ell_i | \Delta_{\mathcal{O}}$.
2.  Maintain a relation lattice $\Lambda \subset \mathbb{Z}^k$ tracking known ideal-class relations among queried ideals.
3.  **On $\mathcal{O}_{\text{cl}}(\mathfrak{a}, h_v)$ query:**
    *   Decompose $\mathfrak{a} = \prod \mathfrak{l}_i^{e_i}$.
    *   Walk $G$ from $v$ via edges $\mathfrak{l}_i^{e_i}$. If path missing, sample new vertices $h_{v'}$ uniformly from unused handles, add edges, ensure no collisions in $V$ (birthday bound on $h \approx p^{1/2}$).
    *   Return handle for endpoint vertex $v'$.
4.  **On Group Op query:** Standard GGM lazy sampling on the *current* curve's group (handles scoped by vertex $v$).
5.  **Consistency Check:** If $\mathcal{A}$ finds a collision $h_{v_1} = h_{v_2}$ for $v_1 \neq v_2$ (implying a relation in $\text{Cl}(\mathcal{O})$ shorter than expected), $\mathcal{S}$ aborts (fails simulation).

**2. Cost Model**
*   **Adversary Cost:** $Q_G$ group ops + $Q_C$ class-group queries (each counted as 1 op).
*   **Simulator Overhead:** $O((Q_C + Q_G) \log p)$ time (graph traversal, lattice reduction for relation detection).
*   **Security Parameter:** $p$ prime, $N \approx p$, Class number $h \approx \sqrt{p}$ (CM discriminant $\Delta \approx -p$).
*   **Target Bound:** Prove $\Pr[\mathcal{A} \text{ solves ECDLP}] \leq \frac{(Q_G + Q_C)^2}{N} + \frac{Q_C^2}{h} + \text{negl}$. The $Q_C^2/h$ term is the "size-gap" penalty: exploiting class-group structure requires collisions in a space of size $h \approx \sqrt{N}$, costing $\Omega(\sqrt{h}) = \Omega(N^{1/4})$ queries, but the *ECDLP solution* still requires a group collision in size $N$.

**3. Falsification Criteria**
The lemma is **falsified** if:
*   An adversary $\mathcal{A}$ solves ECDLP with $Q_G + Q_C = o(\sqrt{N})$ queries in the CA-GGM.
*   Specifically, if $\mathcal{A}$ constructs a "short-cut" isogeny path (length $o(\sqrt{h})$) between two random curves using only $Q_C$ queries, violating the expander mixing time of the $\ell$-isogeny graph, *or* uses the class-group action to induce a non-trivial relation in the target group $E_0$ faster than $\sqrt{N}$ (e.g., via anomalous torsion point transport).
*   Simulator $\mathcal{S}$ aborts with non-negligible probability ($\gg Q_C^2/h$) for a *generic* adversary (implying the graph model is inconsistent).

**4. First Experiment: Graph Diameter vs. Query Complexity**
*   **Setup:** Implement the $\ell$-isogeny graph for $\mathcal{O} = \mathbb{Z}[\sqrt{-p}]$ (or maximal order) for $p \approx 2^{20}, 2^{24}, 2^{28}$. Compute $h$ exactly.
*   **Adversary $\mathcal{A}_{\text{walk}}$:** Performs random walk of length $L$ from $E_0$ via $\mathcal{O}_{\text{cl}}$, stores all visited curve handles. Attempts to find collision (cycle) or reach a curve with known DL (simulated by tagging one random curve with "solution").
*   **Metrics:** Plot success probability vs $Q_C = L$ for $L \in [1, 2\sqrt{h}]$. Verify sharp threshold at $L \approx \sqrt{h}$.
*   **Simulator Check:** Run $\mathcal{S}$ against $\mathcal{A}_{\text{walk}}$. Verify $\mathcal{S}$ abort rate matches $Q_C^2/h$ prediction. Confirm no "free" group relations leak across curves (check group handles remain independent per vertex).
*   **Deliverable:** Empirical validation of the $Q_C^2/h$ term dominance for $Q_C < N^{1/4}$.

## Direction 15

**Research Plan: Preregistered ecbench IC Study (Three Arms)**

**1. Construction / Algorithm**
*   **Target:** Prime field $\mathbb{F}_p$, $p \approx 2^{128}$ (scaled to $2^{60}$–$2^{80}$ for experiment). Curve $E_0/\mathbb{F}_p$ with $N = \#E_0 = h \cdot r$ ($r$ prime).
*   **Factor Base $\mathcal{F}$:** $x$-coordinates of points with $x \in [0, B]$ (or $y^2 = x^3+ax+b$ smoothness bound $B$). Size $|\mathcal{F}| \approx \pi(B)$.
*   **Arm A (Floor-on-Floor):** Standard $x$-only Gaudry–Diem IC on $E_0$. Decompose random $R = [a]G + [b]Q$ via summation polynomials $S_{m+1}(x_1,\dots,x_m, x_R)$. Solve system via Gröbner/Resultant over $\mathbb{F}_p$. Collect $|\mathcal{F}| + \delta$ relations. Linear algebra on $\mathbb{F}_r$-matrix.
*   **Arm B (Floor→Crater via 2-Isogeny):** Compute 2-isogeny $\phi: E_0 \to E_1$ (Vélu, kernel $E_0[2] \cap \langle G \rangle$ if rational, else quadratic extension descent). Map factor base: $\mathcal{F}_1 = \phi(\mathcal{F}) \cup \phi(-\mathcal{F})$. Search relations on $E_1$ using $S_{m+1}^{(E_1)}$. Lift relations to $E_0$ via $\hat{\phi}$ (dual isogeny) for linear algebra on original $G, Q$.
*   **Arm C (Crater-on-Best-Model):** Walk 2-isogeny volcano from $E_1$ to crater curve $E_c$ (endomorphism ring $\mathcal{O}_K$). Select $E_c$ minimizing estimated relation search cost $C(E) = \frac{\text{deg}(S_m)}{\rho(\log p / \log B)}$ (model selection via pilot $B=2^{16}$). Run full IC on $E_c$ with optimal $B^*, m^*$. Map solution to $E_0$ via isogeny chain.

**2. Cost Model**
Total cost $T = T_{\text{rel}} + T_{\text{LA}}$.
*   $T_{\text{rel}} = \frac{|\mathcal{F}|}{\text{Prob(smooth)}} \cdot C_{\text{poly}}(m, \text{deg})$. Measured in CPU-cycles/relation (ecbench `relation_search` harness).
*   $T_{\text{LA}} = O(|\mathcal{F}|^{\omega})$ ($\omega \approx 2.8$). Measured via `sage.matrix` benchmark on relation matrix.
*   **Transport Cost:** Arm B adds $C_{\text{iso}} = \text{cost}(\phi) + \text{cost}(\hat{\phi})$ per relation lift. Arm C adds $C_{\text{chain}}$ (volcano walk + composition). Charged to $T_{\text{rel}}$ overhead.

**3. Falsification Criteria**
Study is falsified if **no arm** achieves $T_{\text{total}} < T_{\text{Pollard-Rho}}(r)$ at $p \approx 2^{80}$ (extrapolated via $L_p[1/2, c]$ fit), OR if Arm B/C transport overhead $> 50\%$ of $T_{\text{rel}}$ at held-out $p \approx 2^{85}$, OR if model selection (Arm C) picks $E_c$ with $T_{\text{total}} > 1.2 \times T_{\text{Arm A}}$ on held-out primes.

**4. First Experiment (Week 1)**
*   **Setup:** `ecbench` harness, $p \approx 2^{60}$ (10 random primes), $B=2^{14}$, $m=3$.
*   **Run:** Execute Arm A on all 10 primes. Measure $T_{\text{rel}}, T_{\text{LA}}, \text{Prob(smooth)}$.
*   **Calibration:** Fit $c$ in $L_p[1/2, c]$ for Arm A. Compute volcanoes for all 10 primes; verify 2-isogeny availability (Arm B feasibility). Select $E_c$ for Arm C via pilot search ($B=2^{12}$).
*   **Gate:** Proceed to full 3-arm preregistration only if Arm A $c < 1.8$ and $\ge 7/10$ primes have rational 2-torsion or efficient $\mathbb{F}_{p^2}$ descent.

## Direction 16

**Construction / Algorithm**
1. **Factor Base**: For target curve $E/\mathbb{F}_p$ with $j(E) \in \{0, 1728\}$, define factor base $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{X}\}$ where $\mathcal{X} \subset \mathbb{F}_p$ is the set of $x$-coordinates of points whose automorphism orbit size divides $|\text{Aut}(E)|$ (3 for $j=0$, 2 for $j=1728$). For generic $j$, $\mathcal{X}$ is random subset of same cardinality $N = \#\mathcal{F} \approx p^{1/2}$.
2. **Relation Generation**: Use Semaev's summation polynomials $f_m$. For $j=0,1728$, exploit symmetry: $f_m(x_1,\dots,x_m) = 0$ implies $f_m(\sigma(x_1),\dots,\sigma(x_m))=0$ for $\sigma \in \text{Aut}(E)$. Generate relations by solving $f_{m+1}(x_1,\dots,x_m, x_Q)=0$ for $x_i \in \mathcal{X}$ via Gröbner basis (F4).
3. **Sham-Curve Null**: For each relation found on $E$, construct isogenous "sham" curve $E'/\mathbb{F}_p$ with same $j$-invariant but different twist/order structure. Verify if relation lifts to $E'$ (null test). Discard relations failing lift.

**Cost Model**
$C_{\text{total}} = C_{\text{rel}} + C_{\text{la}}$.
$C_{\text{rel}} = \frac{N}{\rho \cdot \epsilon} \cdot T_{\text{F4}}(m, d_{\text{ff}}, \mathbb{F}_p)$.
- $\rho$: Probability random $m$-tuple sums to $Q$ (Heuristic: $1/m!$).
- $\epsilon$: Automorphism gain factor. $\epsilon = |\text{Aut}(E)|^{m-1}$ for $j=0,1728$ vs $\epsilon=1$ generic.
- $T_{\text{F4}}$: F4 runtime. Modeled as $O(\binom{m+d_{\text{ff}}}{d_{\text{ff}}}^\omega)$.
- $d_{\text{ff}}$: First-fall degree. Hypothesis: $d_{\text{ff}}^{\text{special}} \le d_{\text{ff}}^{\text{generic}} - \Delta$ due to symmetry-induced degree drops.
$C_{\text{la}} = O(N^2)$ (sparse linear algebra).

**Falsification Criteria**
1. Measured $d_{\text{ff}}$ for $m=3,4$ on $j=0,1728$ equals generic $d_{\text{ff}}$ (no degree drop).
2. $\epsilon_{\text{empirical}} < 1.5$ for $j=1728$ or $< 2.5$ for $j=0$ at $m=3$ (theoretical max 2, 3).
3. Sham-curve null rate $> 50\%$ (symmetry breaks under isogeny).
4. Wall-clock $T_{\text{F4}}$ per relation for special $j$ exceeds generic $j$ at matched $N$.

**First Experiment**
Implement F4 in `msolve`/`FGb` for $m=3$ (Semaev $f_4$). Target $p \approx 2^{31}-1$.
1. Fix $N=2000$. Select $\mathcal{X}_{\text{spec}}$ (orbits size 3 for $j=0$, 2 for $j=1728$) and $\mathcal{X}_{\text{gen}}$ (random).
2. For 100 random $Q \in E(\mathbb{F}_p)$, solve $f_4(x_1,x_2,x_3, x_Q)=0$ for $x_i \in \mathcal{X}$.
3. Measure: (a) $d_{\text{ff}}$ (max degree in F4), (b) $T_{\text{F4}}$ per system, (c) Solutions found / 100 trials.
4. Repeat for generic $j$ curve with matched $N$.
5. Compute empirical $\epsilon = (\text{Sol}_{\text{spec}} / T_{\text{spec}}) / (\text{Sol}_{\text{gen}} / T_{\text{gen}})$.

## Direction 17

**Construction / Algorithm**  
1. **Input**: The 2,100 precomputed pullback bindings (1,940 prime-quadratic, 160 binary-cubic) from `LEAD-TRF-cover-catalog-jacobian-transfer`. Each binding defines a degree-`d` cover `φ: H → E` with `H` genus-2, `E` elliptic, `d ∈ {2,3}`.  
2. **Mumford Representation**: For each `H`, implement even-degree (`d=2`) Cantor addition/doubling in projective Mumford coordinates `(U, V, W)` avoiding inversions. For `d=3` bindings, derive explicit `φ_*` via resultant-based norm: `φ_*(D) = Norm_{K_H/K_E}(D - ∞)` computed as polynomial resultant `Res_U(u_H, u_E)` evaluated at divisor Mumford polynomials.  
3. **Certification Loop**: For each binding:  
   a. Compute `G = φ_*(Jac(H)) ⊆ E(𝔽_p)` by evaluating `φ_*` on 200 random Mumford divisors.  
   b. Determine `#G` via baby-step-giant-step on `E` (bound `≤ 2√p`).  
   c. Compute kernel `K = ker(φ_*) ∩ Jac(H)[ℓ]` for `ℓ | #E` by solving `φ_*(D) = O_E` as polynomial system in Mumford coords (Gröbner basis over `𝔽_p`, deg ≤ 6).  
   d. Verify exact sequence `0 → K → Jac(H) → G → 0` and record `(binding_id, #G, K_structure, φ_*_explicit_formula)`.  

**Cost Model**  
- Mumford `d=2` add: 12M + 4S (projective); `d=3` norm: 1 resultant (≈ 200M via subresultant PRS).  
- BSGS per binding: `O(√p)` group ops (`p ~ 2^256` → infeasible full; use `p ~ 2^64` for certification, extrapolate).  
- Kernel solve: `O(ℓ^3 ω)` field ops per `ℓ` (ω=2.37).  
- Total estimate: 2,100 × (5k M + 1 BSGS_64 + 3 kernel solves) ≈ 4 GPU-hours on H100 for `p_64`; `p_256` requires heuristic sampling only.

**Falsification Criteria**  
1. Any binding yields `#G ∤ #E(𝔽_p)` or `#G ≠ #Jac(H)/#K`.  
2. Kernel dimension > 1 for prime `ℓ` (implies non-cyclic `K`, contradicts Richelot structure).  
3. `φ_*` formula degree in Mumford coords exceeds `2d` (violates functoriality bound).  
4. >5% bindings fail resultant computation due to non-generic `H` (singular fibers).

**First Experiment**  
Run certification on the 160 binary-cubic bindings at `p = 2^61-1` (Mersenne, fast reduction). Implement Mumford `d=3` norm via Flint `fmpz_mod_poly_resultant`. Output CSV: `binding_id, p, #E, #Jac(H), #G, K_invariants, resultant_time_ms`. Success = all 160 pass sequence check in < 30 min.

## Direction 18

**Construction/Algorithm**  
1. **JV Sieve (R0 S)**: Factor base ℬ = {E : j(E) ∈ S₀} where S₀ = {j ∈ 𝔽ₚ : ∃E/𝔽ₚ, #E = p+1−t, |t|≤2√p}. Relations from split-curve walks: start at random E, take ℓ-isogeny steps (ℓ∈ℒ={2,3,5,7,11,13}) until j(E)∈S₀. Record relation when path length ≤ L_max=12. Use corrected hash accounting: each relation weighted by 2⁻ˡ where l = path length.  
2. **Strong-Rho (A/A rule)**: Parallel distinguished-point walk on isogeny graph with step function φ(E) = [x(E) mod 3] selecting ℓ∈ℒ. Charge rule: each step costs log₂(ℓ) + 0.5 (F4/LA overhead). Collision when j(E₁)=j(E₂) and both marked A (endomorphism ring ℤ[√−p]).  
3. **Charged Isogeny Walk**: For each step, compute ℓ-isogeny via Vélu, then apply F4 reduction (2M+5S) and linear-algebra precomputation (LA) for kernel polynomial reuse. Charge = 1.0 + 0.15·deg(ℓ).  

**Cost Model**  
- Sieve: C_sieve = |ℬ|·(μ·C_step + C_LA) where μ = avg steps to hit ℬ (target μ≤8), C_step = Σ_{ℓ∈ℒ} p_ℓ·charge(ℓ), C_LA = 0.08·|ℬ| F4 ops.  
- Rho: C_rho = √(π|ℬ|/2) · C_step · (1 + ε_charge) with ε_charge = 0.12 from F4/LA.  
- Target: C_sieve / C_rho ≤ 0.7 at p=1823.  

**Falsification Criteria**  
- μ > 10 at any p ∈ {1009,1511,1823} (sieve too sparse).  
- Hash-weighted relation rate < 0.03/step (insufficient yield).  
- C_sieve / C_rho > 1.0 at p=1823 (rho wins).  
- A/A collision rate deviates >25% from √(π|ℬ|/2) prediction (walk bias).  

**First Experiment**  
Run JV sieve at p=1009 with frozen tolerances: L_max=12, ℒ={2,3,5,7,11,13}, charge(ℓ)=1+0.15ℓ, hash weight=2⁻ˡ. Collect 5000 relations. Measure μ, relation rate, and linear-algebra matrix density. Compare wall-clock against strong-rho (10⁶ steps, 32 DP threads) on same hardware. Log all charges per step for cost-model validation.

## Direction 19

**Research Plan: Direction 19 — Toy-Size Test of H1 (Miller Cocycle Transfer)**

**1. Exact Construction & Algorithm**
*   **Curve & Field:** Select a 64-bit prime `p` (toy) and `p' ≈ p` (matched random control). Generate `E/F_p` with `N = #E(F_p) = h·r` (`r` prime, `h` small). Fix generator `P ∈ E[r]`, `g ∈ F_p^*` generator.
*   **Planted Positive Control:** Construct `E_planted` via CM method or `r`-torsion polynomial solving such that `∃ φ: E → E'` (deg `ℓ` small) where `U = x ∘ φ` (or `f_{ℓ,P}` Miller function) yields `log_g U(kP)` with known bias (e.g., image lies in subgroup of `F_p^*` of index `M`).
*   **Map `U`:** Use `x`-coordinate of `kP` (standard) and `f_{m,P}(Q)` (Miller function for `m|r`, `Q` independent point) as `U_candidate`.
*   **Sampling:** For `k ∈ [1, K]` (`K = 2^16`), compute `y_k = log_g(U(kP)) mod (p-1)` via BSGS (precomputed `g^i` table).
*   **Statistics:**
    *   **Equidistribution:** `χ²` test on `y_k mod M` for `M ∈ {2, 4, 8, 16, r, h}`.
    *   **Smart Ratio:** Compute `S = (1/K) Σ exp(2πi y_k / N)`. Track `|S|`.
    *   **Character Correlation:** For additive chars `ψ_a(y) = exp(2πi a y / (p-1))` and multiplicative `χ_b(y) = exp(2πi b log_g(y) / r)`, compute `C(a,b) = |Σ ψ_a(y_k) χ_b(k)| / K`.

**2. Cost Model**
*   **Precomputation:** `O(√p)` ≈ `2^32` ops (BSGS table for `log_g`), done once per `p`.
*   **Per Curve:** `K` scalar mults (`O(K log p)`), `K` evals of `U`, `K` table lookups.
*   **Total Toy Run:** < 1 GPU-hour per curve (special, random, planted).

**3. Falsification Criteria (H1 False If)**
*   **Equidistribution:** `p-value > 0.01` for `y_k mod r` and `y_k mod h` on *Special* curves (no bias detected where theory predicts).
*   **Smart Ratio:** `|S| < 1.5 / √K` for Special curves (no anomalous concentration).
*   **Character Correlation:** `max_{a,b≠0} |C(a,b)| < 3σ` (Gaussian noise floor) for Special curves.
*   **Control Failure:** Planted curve *fails* to show `p-value < 10^{-6}` or `|S| > 5/√K` (experimental setup broken).

**4. First Experiment (Week 1)**
Implement `test_toy_equidistribution.py`:
1.  Generate `p=2^61-1` (Mersenne, fast mod), find `E_special` (CM disc -4, `j=1728`, `p≡1 mod 4`), `E_random` (random `a,b`), `E_planted` (force `r|p-1`, embed `μ_r ⊂ F_p^*` via `x`-map).
2.  Build `log_g` table for `F_p^*`.
3.  Run `K=65536` walks for all 3 curves using `U(kP) = x(kP)`.
4.  Output: `χ²` histograms for `mod r`, `mod h`, `mod 16`; Smart Ratio `|S|`; Top-10 Character Correlations.
5.  **Go/No-Go:** Proceed iff `E_planted` shows extreme bias (`χ²/r > 5`) AND `E_smart` shows `χ²/r > 1.5` AND `E_random` shows `χ²/r ∈ [0.8, 1.2]`.

## Direction 20

**Construction / Algorithm**
1. **Input:** Odd-char prime field $\mathbb{F}_q$, target elliptic curve $E/\mathbb{F}_q$, factor base $\mathcal{F} \subset E(\mathbb{F}_q)$ of smoothness bound $B \approx q^{1/3}$.
2. **Descent Enumeration:** For each $R \in \mathcal{F}$, compute the fiber $S \in \mathrm{Sym}^3(E)$ mapping to $R$ under $x$-coordinate summation (Diem’s $G_3$ descent). Filter fibers where the Mumford representation $(u(x), v(x))$ has $\deg u = 3$ and $\deg v \leq 2$.
3. **Trigonal Check (Prop 2):** For each fiber, test if the associated genus-3 curve $C: y^3 = f(x)$ (or trigonal model $y^3 + h(x)y = f(x)$ via Prop 4 reduction) admits a degree-3 map $\pi: C \to \mathbb{P}^1$ defined over $\mathbb{F}_q$. Verify $\mathbb{F}_q$-rationality of the $g^1_3$ by checking if the invariant differentials pull back to $\mathbb{F}_q$-rational sections.
4. **Non-degeneracy (Prop 4):** Compute the Maroni invariant via the Hilbert series of the canonical ring. Reject curves where the trigonal linear system is composite with an involution (hyperelliptic locus) or has a base point (degenerate).
5. **Relation Generation:** For valid $C$, compute $\mathrm{Jac}(C)(\mathbb{F}_q)$ via group law (Cantor/Kharitonov). Decompose random $D \in \mathrm{Jac}(C)$ over factor base $\mathcal{F}_C$ (degree-1 places) using $L_{q}(1/2)$ index calculus on $\mathrm{Jac}(C)$. Lift relations to $E(\mathbb{F}_q)$ via norm map $\mathrm{Nm}: \mathrm{Jac}(C) \to E$.

**Cost Model**
*   Descent probability: $q^{-1/3}$ per $R$.
*   Trigonal filter survival rate: Heuristic $q^{-\epsilon}$ ($\epsilon \approx 0.05$).
*   Relation search on $\mathrm{Jac}(C)$: $L_{q^3}(1/2, c) \approx \exp((c+o(1))(\log q)^{1/2}(\log \log q)^{1/2})$.
*   Total expected complexity: $\tilde{O}(q^{1/3} \cdot L_{q^3}(1/2))$. Target: beat Diem’s $O(q^{4/3})$ if $L_{q^3}(1/2) < q^{1/3}$ (holds for $q > 2^{100}$).

**Falsification Criteria**
1.  **Zero Survival:** Zero enumerated descents pass the $\mathbb{F}_q$-rational trigonal test (Prop 2) + non-degeneracy (Prop 4) for $q < 2^{60}$.
2.  **Maroni Obstruction:** All surviving curves have Maroni invariant $>0$ (non-trigonal generic) or map to hyperelliptic curves, preventing efficient index calculus on $\mathrm{Jac}(C)$.
3.  **Lift Failure:** Norm map $\mathrm{Nm}$ fails to land in $\mathcal{F}$ with probability $> 1 - q^{-1/3}$, breaking descent closure.

**First Experiment**
Implement descent enumeration (Step 2) for $q \approx 2^{40}$ (prime). Use Magma/Sage to enumerate $10^5$ fibers $S$. Apply rigorous $\mathbb{F}_q$-rational trigonal test (Step 3: compute canonical model, check for $g^1_3$ defined over $\mathbb{F}_q$ via automorphism group of canonical embedding). Output: Count of valid genus-3 trigonal curves per $10^5$ descents. If count $= 0$, direction is falsified for cryptographic sizes.

## Direction 21

**Construction/Algorithm**  
Implement the n=7 placement-exhaustion engine for odd-prime-degree ℓ-isogeny graphs over 𝔽_p (p ≈ 2^212). For each rational point placement P ∈ E(𝔽_p)[ℓ] (ℓ ∈ {3,5,7}), compute the full ℓ-isogeny volcano walk to the floor, recording: (a) 2-torsion subgroup structure at each level, (b) endomorphism ring discriminant Δ, (c) relation density ρ = #{smooth norms}/#{total norms}. Use Lean 4 to formally verify: (i) every walk terminates at a unique floor, (ii) floor 2-torsion is isomorphic to (ℤ/2ℤ)² × (ℤ/2^kℤ) with k ≥ 2, (iii) the cover map φ: E → E' induced by the walk has degree ℓ^n and its kernel is rational. Stratify by ℓ: for each ℓ ∈ {3,5,7}, census all 3^7, 5^7, 7^7 placement sequences, pruning isomorphic walks via j-invariant equivalence.

**Cost Model**  
C_total = Σ_ℓ [C_walk(ℓ) + C_smooth(ℓ) + C_linear(ℓ)] where  
C_walk(ℓ) = N_placements(ℓ) × (ℓ^n × M_p + log p × I_p)  // M_p = 𝔽_p mul, I_p = 𝔽_p inv  
C_smooth(ℓ) = N_relations(ℓ) × L_p[1/2, c]  // ECM smoothness test  
C_linear(ℓ) = (N_relations(ℓ))^ω  // sparse linear algebra, ω ≈ 2.37  
Target: C_total < 2^128 for p ≈ 2^212. Baseline: ρ ≥ 2^{-40} for ℓ=3, ρ ≥ 2^{-45} for ℓ=5, ρ ≥ 2^{-50} for ℓ=7.

**Falsification Criteria**  
(1) Any placement walk fails to reach a floor within ℓ^n steps.  
(2) Floor 2-torsion lacks (ℤ/2ℤ)² factor for >0.1% of walks.  
(3) Measured ρ_ℓ < 0.5 × predicted ρ_ℓ for any ℓ ∈ {3,5,7}.  
(4) Lean proof of (i)-(iii) fails for >0 placements.  
(5) C_total > 2^130 after census completion.

**First Experiment**  
Run ℓ=3 census on p = 2^212 - 123 (fixed prime from isogeny-labs/crypto). Generate all 3^7 = 2187 placement sequences. For each: compute 3-isogeny walk via Vélu (Lean-verified), record floor j-invariant, 2-torsion structure, and 1000 random norm samples for ρ_3 estimate. Parallelize over 64 cores. Output: CSV with columns [placement_id, floor_j, torsion_type, smooth_count]. Expected runtime: <4 hours. This validates the engine and gives first ρ_3 measurement before ℓ=5,7.

## Direction 22

**Construction / Algorithm**

1. **Tower definition**: For each n ∈ {4,5,6,8,12} build a coprime tower  
   `F_p ⊂ F_{p^a} ⊂ F_{p^{ab}} = F_{p^n}` with a,b > 1, gcd(a,b)=1.  
   Use Conway polynomials (or minimal-weight irreducibles) for each step; store the explicit embeddings.

2. **JLSV-style descent** (Joux–Lercier–Smart–Vercauteren) inside the tower:  
   - Factor base: all degree-1 elements in the top field represented in the *bottom* basis.  
   - Relation generation: random linear combinations of basis elements → smoothness test in the subfield `F_{p^a}` (for a|n) via norm map to `F_p`.  
   - Individual logarithm: same descent, but target is a fixed generator `g` of `F_{p^n}^*`.

3. **Certified log in F_121**:  
   - `p=11, n=2` (trivial tower). Run full index-calculus (Gaussian elimination over `F_2`) to obtain `log_g(h)` for a NIST-recommended generator `g` and random `h`.  
   - Verify by exponentiation; publish the log as a reproducible artifact.

4. **Same-shape GF(p^12) calibration**:  
   - Choose `p ≈ 2^20` (so `p^12 ≈ 2^240`), matching the *shape* (tower splits 3·4) of the current pairing-friendly record (Barbulescu–Gaudeau–Guillevic–Morain, 2014, 239-bit).  
   - Run the *exact same code path* (same smoothness bound, same linear algebra) on this field.  
   - Compare wall-clock time, relation yield, and matrix density against the published 239-bit run.

**Cost Model**

- `C_rel = (smoothness_prob)^{-1} · (cost_per_trial)`  
  `smoothness_prob ≈ ρ(log(p^n)/B) / ρ(log(p^a)/B)` with `B = L_{p^n}[1/3, c]`.  
- `C_LA = O(M^2)` for matrix dimension `M = #factor_base ≈ p^a`.  
- Total `C_total = C_rel + C_LA`.  
- Parameter `c` fitted from the `F_{p^12}` calibration; then extrapolate to cryptographic sizes (e.g., BLS12-381 target field `p^12 ≈ 2^4600`).

**Falsification Criteria**

1. The certified `F_121` log cannot be reproduced by an independent script within 2× the reported time.  
2. The `GF(p^12)` calibration run yields >2× the published relation count *or* matrix density for the same `B`.  
3. Fitted `c` deviates >15 % from the asymptotic `c = (64/9)^{1/3} ≈ 1.92`.  
4. Any tower split produces a norm-map collision rate > `1/p^{min(a,b)}` (breaks independence heuristic).

**First Experiment**

Implement the `F_121` certified log *today* in SageMath/FLINT:  
- Define `F_11`, `F_121 = F_11[x]/(x^2+1)`, generator `g = x+2`.  
- Factor base = all `a + b·x` with `a,b ∈ [0,10]`.  
- Collect 200 relations via random `g^k · h^j`, smoothness = splits completely in `F_11`.  
- Solve 121×121 system over `Z/120Z`, output `log_g(h)` for `h = x+3`.  
- Push script + log + verification to `isogeny-labs/crypto/certified_logs/F_121/`.

## Direction 23

**Construction / Algorithm**  
1. **Volcano Setup**: For each of the 20 arms, instantiate the ℓ-isogeny volcano (ℓ=3) over 𝔽ₚ with p ≈ 2²⁵⁶, target conductor `f ∈ {8209, 131101}`. Compute crater (cyclic) and floor (depth-1) curves via `isogeny_volcano` module.  
2. **Factor Bases**:  
   - *Native*: All 𝔽ₚ-rational points on crater curves (size ≈ p).  
   - *Random*: Uniformly sampled subsets of same cardinality.  
3. **Relation Collection**: Walk arity-3 graphs from random floor curves; record (crater, floor) pairs where discrete log of target point factors over the active factor base. Use Teske’s `radding` walk with distinguished points (DP threshold 2⁻²⁰).  
4. **Linear Algebra**: Sparse matrix over ℤ/(p−1); solve via block Wiedemann.  
5. **Trapdoor Check**: Verify secret isogeny path (crater→floor) reduces relation count by factor ≥ √(deg φ).

**Cost Model**  
- **Relation cost**: C_rel = (walks_per_arm) × (avg_steps) × (ℓ-iso eval). Target: 2⁴⁰ ops/arm.  
- **Memory**: O(|FB|) ≈ 2²⁰ rows × 64 bytes.  
- **LA cost**: O(|FB|²) bit-ops; parallelized over 20 arms.  
- **Speedup metric**: σ = (relations_native / relations_random). Success if σ ≥ 1.8 ± 0.1.

**Falsification Criteria**  
- σ < 1.3 after 2× budget (rules out native FB advantage).  
- Arity-3 occupancy < 0.85 (graph expansion failure).  
- Conductor 131101 yields same σ as 8209 (conductor independence).  
- Secret isogeny path does not reduce relation count (trapdoor invalid).

**First Experiment**  
Patch `psutil` import in `exp_ectd_0cf008.py`; launch single-arm pilot (conductor 8209, native FB) for 2¹⁸ relations. Log: steps/walk, DP hit rate, matrix density, wall-clock. Compare occupancy histogram vs. prior verified arity-3 baseline (target: KS-test p > 0.05).

## Direction 24

**Construction / Algorithm**
1. **Parameter selection**: Fix a 256-bit prime `p ≡ 3 mod 4` (e.g., `p = 2^256 − 189`). Work in `F_{p^6} = F_p[u]/(u^6 − ξ)` with `ξ` a quadratic non-residue in `F_{p^2}`. Use the `l = 2`-isogeny graph on supersingular `j`-invariants (or `(a,b)`-models for Montgomery curves).
2. **JV-weak class definition**: A curve `E/F_{p^6}` is *JV-weak* iff its endomorphism ring contains an order `O` with `disc(O) = disc(End(E)) / D^2` where `D` is `B`-smooth (`B = 2^16`) and `O` admits an explicit `B`-smooth isogeny to a curve with known endomorphism ring (e.g., `j = 0` or `1728`). Precompute the set `W` of all such `j`-invariants by enumerating `B`-smooth ideals in `O_{K}` (`K = Q(√−p)`) via KLPT and translating to `j`-invariants.
3. **Public ISO-1 walk**: From a random start `j_0 ∈ F_{p^6} \ F_{p^3}`, perform a deterministic *non-backtracking* 2-isogeny walk using the Vélu-formula successor function `succ(j) = next 2-isogenous neighbour` ordered by `x`-coordinate. This is the "public" walk (no secret seed).
4. **Distance measurement**: For each of `N = 1000` random seeds `j_0`, walk until hitting `W` or reaching step limit `L_max = 2·10^10`. Record hitting time `T(j_0)`. Compute median `T_med` and max `T_max`.

**Cost Model**
- One 2-isogeny step (Vélu + field ops in `F_{p^6}`) ≈ 12,000 `F_p` multiplications.
- `10^10` steps ≈ `1.2·10^14` `F_p` muls ≈ `2^47` bit-ops.
- Target threshold: `T_max > 10^10` steps (i.e., at least one class places the nearest weak curve beyond the public walk budget).

**Falsification Criteria**
- If `T_max ≤ 10^9` for all 1000 seeds (weak curves are too dense).
- If `T_med > 10^10` (walk cost exceeds budget for typical instances, breaking the trapdoor assumption).
- If `|W| / |V| > 2^{-30}` (density heuristic violated; `V` = supersingular vertices in `F_{p^6}`).

**First Experiment**
Implement the walk in SageMath/C with `p = 2^61−1` (toy prime) and `F_{p^6}` tower `F_p → F_{p^2} → F_{p^6}`. Enumerate `W` for `B = 2^8`. Run 100 walks with `L_max = 10^6`. Verify median hitting time matches `O(√(|V|/|W|))` prediction. If toy scaling holds, promote to 256-bit `p` with `B = 2^16` and `N = 1000`.

## Direction 25

**Research Plan: Direction 25 — Weil Restriction Census & Isogeny-Gated Index Calculus**

**Construction / Algorithm**
1. **Base setup**: Fix prime `p ≈ 2^64` (large enough for non-trivial DLP, small enough for exhaustive census). Work over `F_{p^2}` and `F_{p^3}`.
2. **Weil restriction**: For every elliptic curve `E/F_{p^n}` (`n=2,3`), compute `Res_{F_{p^n}/F_p}(E)` — an abelian variety of dimension `n` over `F_p`. For `n=2`, this is a genus-2 Jacobian (or product of elliptic curves); for `n=3`, dimension-3 abelian variety.
3. **Exhaustive n=2 control**: Enumerate all `E/F_{p^2}` up to `F_p`-isomorphism (via `j`-invariant in `F_{p^2}`). For each, compute `Res(E)` and test if it splits over `F_p` as `Jac(C)` for genus-2 curve `C`. Record `(j, #E(F_{p^2}), split_type, C)`.
4. **Exhaustive n=3 point-count census**: For `q=2,3` (i.e., `p=2,3`), enumerate all `E/F_{q^3}`. Compute `Res(E)` and count `F_q`-rational points on the resulting dimension-3 variety. Full census feasible: `~q^3` curves.
5. **Isogeny gate**: Before pricing any DLP route, require an explicit `F_q`-isogeny `φ: Res(E) → Jac(C)` of degree `≤ D_max` (start `D_max = 2^10`). Compute via Kedlaya-style or explicit Vélu on Jacobians. Discard curves without such `φ`.
6. **Index calculus pricing**: For survivors, run genus-2/3 index calculus (Gaudry-Schost / Diem-Kochinke) on `Jac(C)(F_q)` to solve DLP transported via `φ`. Cost model: `L_q(1/2, c)` for genus 2, `L_q(1/2, c')` for genus 3, plus `deg(φ)` overhead.

**Cost Model**
- Census: `O(p^2)` curves for `n=2`, `O(p^3)` for `n=3` (trivial for `p=2,3`; sampled for larger `p`).
- Isogeny search: `O(D_max^{n})` per curve using `l`-isogeny graphs (`l` small primes).
- Index calculus: `exp((c+o(1))√(g log q log log q))` for genus `g` Jacobian over `F_q`.
- Total projected cost for `p≈2^64`, `n=3`: dominated by index calculus on genus-3 over `F_p` → `L_p(1/2, ~1.5)` vs. generic `O(p^{3/2})`.

**Falsification Criteria**
1. **Split rate < 1%**: <1% of `E/F_{p^n}` have `Res(E)` isogenous to a Jacobian over `F_p` of controlled degree.
2. **Isogeny degree explosion**: Minimal `deg(φ)` for survivors grows as `p^{Ω(1)}`, making transport cost exceed generic DLP.
3. **Index calculus constant `c` ≥ 2.0**: Measured `c` for genus-3 over `F_p` makes `L_p(1/2,c)` slower than Pollard rho on `E(F_{p^3})`.

**First Experiment**
- **Target**: `p=2,3`; `n=3` exhaustive census.
- **Code**: Extend `isogeny-labs/crypto` `weil_restriction.py` to enumerate all `E/F_{q^3}` (`q=2,3`), compute `Res(E)` as dimension-3 `p.p.av`, test for `F_q`-isogeny to genus-3 Jacobian via `l`-isogeny graph walk (`l=2,3,5`), bound `deg ≤ 1000`.
- **Output**: CSV of `(j, #E, split?, min_deg_φ, C_eqn)`. Runtime target: <1 hour on 32 cores.
- **Decision gate**: If ≥5 curves survive with `deg(φ) ≤ 500`, proceed to `p≈2^20` sampled census + genus-3 index calculus prototype.

## Direction 26

**Construction & Algorithm**  
Define the *digit-character family* $\chi_{b,k}: \mathbb{F}_p \to \mathbb{C}^\times$ by $\chi_{b,k}(x) = \exp(2\pi i \cdot \text{digit}_b(x; k) / b)$, where $\text{digit}_b(x; k)$ extracts the $k$-th base-$b$ digit of the canonical integer representative of $x \in [0, p-1]$. For a target curve $E/\mathbb{F}_p$ and factor base $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{I}\}$ (interval $\mathcal{I}$ of size $\approx p^{1/3}$), compute the **stability statistic** for parameter $\lambda$ (Möbius transform $x \mapsto (ax+b)/(cx+d)$):  
$$S(\lambda) = \frac{1}{|\mathcal{F}|} \sum_{P \in \mathcal{F}} \chi_{b,k}(x(\lambda \cdot P)) \cdot \overline{\chi_{b,k}(x(P))}.$$  
Test $\lambda \in \Lambda \subset \text{PGL}_2(\mathbb{F}_p)$ (size $|\Lambda| \approx 2^{16}$) against a **PGL₂-orbit-matched null**: for each $\lambda$, generate 100 random $\mu \in \text{PGL}_2(\mathbb{F}_p)$ with identical cycle-type/discrepancy profile on $\mathbb{P}^1(\mathbb{F}_p)$, compute $S(\mu)$, build empirical null CDF. Flag $\lambda$ where $S(\lambda)$ exceeds 99.9th percentile.

**Cost Model**  
- Census size $N = |\mathcal{F}| \in \{2^{20}, 2^{22}, 2^{24}, 2^{26}\}$.  
- Per $\lambda$: $O(N)$ field ops + digit extraction (table lookup).  
- Total: $|\Lambda| \cdot N \cdot (1 + 100) \approx 2^{16} \cdot N \cdot 101$.  
- At $N=2^{26}$: $\approx 2^{42}$ ops ($\sim$1 GPU-week). Memory: $O(N)$ for $x$-coordinates.

**Falsification Criteria**  
1. No $\lambda \in \Lambda$ survives Bonferroni correction ($p < 0.01 / |\Lambda|$) at any $N$.  
2. Effect size $|S(\lambda)|$ decays as $N^{-1/2}$ (consistent with CLT noise).  
3. Surviving $\lambda$ correlate with trivial symmetries (e.g., $x \mapsto -x$, Frobenius).

**First Experiment**  
Run $N=2^{20}$ census on secp256k1. $\mathcal{I} = [0, 2^{20})$. $b=2, k=10$ (mid-bit). $\Lambda$ = all $\lambda = \begin{pmatrix} 1 & t \\ 0 & 1 \end{pmatrix}$ (translations, $t \in \mathbb{F}_p$ sample $2^{16}$). Compute $S(\lambda)$ vs. 100 matched null $\mu$ per $\lambda$. Output: histogram of max-zscores, runtime, memory.

## Direction 27

**Research Plan: Relative Bucket Variance W of O2 Agreement Kernel**

**1. Exact Construction / Algorithm**
*   **O2 Agreement Kernel ($K_{O2}$):** For a fixed factor base $\mathcal{F}$ of size $N$, define the $O2$ relation set $\mathcal{R} = \{(u,v) \in \mathcal{F}^2 : u+v \in \mathcal{F} \}$. Partition $\mathcal{F}$ into $B = \lceil \sqrt{N} \rceil$ buckets $\mathcal{B}_i$ via $x$-coordinate interval hashing (width $\approx p/N$).
*   **Bucket Weight ($w_i$):** For bucket $\mathcal{B}_i$, compute $w_i = |\{(u,v) \in \mathcal{R} : u \in \mathcal{B}_i \lor v \in \mathcal{B}_i \}|$.
*   **Relative Variance ($W$):** $W(N) = \frac{1}{B} \sum_{i=1}^B \left( \frac{w_i - \mu}{\mu} \right)^2$ where $\mu = \frac{1}{B}\sum w_i = 2|\mathcal{R}|/B$.
*   **Scaling Sweep:** Compute $W(N)$ for $N \in \{2^{10}, 2^{11}, \dots, 2^{18}\}$ over 10 random curves/seeds per $N$. Fit model $W(N) = \alpha N^{-\beta} + \epsilon$ via log-log OLS. Target: confirm $\beta \approx 0.5$ ($W \propto 1/\sqrt{N}$).

**2. Cost Model**
*   **Relation Generation:** $O(N^{3/2})$ group ops (standard $O2$ enumeration).
*   **Bucket Assignment:** $O(N)$ hash/insert.
*   **Variance Calculation:** $O(B) \approx O(\sqrt{N})$.
*   **Total per $N$:** $\approx 2 N^{3/2}$ ECADD. For $N=2^{18}$: $\sim 2^{28}$ ops ($\approx$ 1 GPU-hour on RTX 4090 using `ecgpu` batch arithmetic).
*   **Memory:** $O(N)$ for factor base + $O(|\mathcal{R}|) \approx O(N^{3/2})$ for relation buffer (streamed to disk).

**3. Falsification Criteria**
1.  **Scaling Violation:** Fitted $\beta < 0.4$ or $\beta > 0.6$ ($p < 0.01$).
2.  **Plateau:** $W(N)$ plateaus above $10^{-3}$ for $N > 2^{16}$, implying structural bias (e.g., anomalous clustering from $x$-hash) preventing $ktree$-join load balancing.
3.  **Class Mismatch:** $W(N)$ distribution for $N=2^{16}$ fails KS-test ($p<0.05$) against the Gaussian mixture model assumed in `EXP-ECDLP-5cad48` (which assumed uniform $W$ class).

**4. First Experiment**
*   **Target:** $N=2^{14}$ ($B=128$), single curve `secp128r1` (prime field), 5 seeds.
*   **Implementation:** Modify `isogeny-labs/crypto/cryptanalysis/ecdlp/o2_kernel.py` → add `BucketVarianceTracker` class. Use `x % B` for bucketing (fast, deterministic).
*   **Output:** CSV `N, seed, W, mu, max_bucket_load`. Plot `log(W)` vs `log(N)`.
*   **Success Gate:** $\beta \in [0.45, 0.55]$ and max load $< 3\mu$. If passed, launch full sweep on H100 cluster (SLURM array job).

## Direction 28

**Research Plan: Bounded-Height Section Timing on E1 Surfaces (Dir. 28)**

**1. Construction / Algorithm**
Target: Compute a section $s: \mathbb{P}^1 \to \mathcal{E}$ of an elliptic surface $\mathcal{E}/\mathbb{F}_p$ (E1: $j$-map degree 1) passing through a prescribed fibre $E_t$, with logarithmic height $h(s) \leq B$. 
*   **Model:** $\mathcal{E}: y^2 = x^3 + A(t)x + B(t)$, $\deg A \leq 4, \deg B \leq 6$. Section $s(t) = (x(t), y(t))$, $\deg x \leq 2, \deg y \leq 3$.
*   **Constraint System:** Enforce $s(t_0) = P_{target} \in E_{t_0}$ and $y(t)^2 \equiv x(t)^3 + A(t)x(t) + B(t) \pmod{p}$.
*   **Gröbner Control:** Solve for coefficients of $x(t), y(t)$ over $\mathbb{F}_p$ using F4/F5 with **Graded Reverse Lex (grevlex)** ordering. Introduce **random linear combinations** of the defining polynomials (Macaulay matrix row randomization) before elimination to control degree fall and matrix density, mimicking `crypto-autoresearcher`’s `groebner_randomized_projection` heuristic.
*   **Multi-Prime Lift:** Execute in parallel for $p_1, p_2, p_3 \approx 2^{60}$. Reconstruct rational section via CRT/Rational Reconstruction if heights align.

**2. Cost Model**
$T_{section}(d, \chi, p) \approx O\left( \binom{d_{reg} + n}{n}^{\omega} \right)$ where:
*   $n = 12$ (coeffs of $x,y$).
*   $d_{reg} \approx 5$ (expected degree of regularity for semi-regular sequence after randomization).
*   $\omega \approx 2.37$ (matrix mult).
*   **Dominant Term:** Macaulay matrix size at $d_{reg}$. Randomization targets reducing $d_{reg}$ by 1 vs standard F4 (observed in `isogeny-labs/crypto` ECDLP-IC experiments on decomposition polynomials).
*   **Overhead:** 3x CPU for multi-prime; negligible comms.

**3. Falsification Criteria**
The approach is falsified if **ANY** hold:
1.  $d_{reg} \geq 7$ for $>90\%$ of random $p, \mathcal{E}, P_{target}$ (implies $T > 10^4$s, non-competitive with Pollard Rho).
2.  No solution exists for $B=3$ (height bound) in $>50\%$ of trials (geometric obstruction).
3.  Randomization fails to reduce average $d_{reg}$ vs deterministic F4 (measured in `crypto-autoresearcher` bench suite `groebner_ecdlp_bench`).
4.  CRT reconstruction fails due to height explosion ($h(s) \gg B$) in $>10\%$ of successful local solves.

**4. First Experiment (Week 1)**
**Script:** `exp_dir28_section_timing.py`
**Parameters:** 100 random triples $(p_i, \mathcal{E}_i, P_i)$ with $p_i \approx 2^{31}$ (fit 64-bit ints, fast turnaround).
**Metrics:** 
1.  `d_reg_achieved` (max degree in F4).
2.  `matrix_dim` at $d_{reg}$.
3.  `wall_time` per prime.
4.  `solution_exists` (bool).
**Control:** Run identical systems with `sage.groebner_basis(protocol='f4')` (deterministic) vs custom randomized F4 wrapper.
**Success Gate:** Median `wall_time` < 5s/prime AND `d_reg_achieved` <= 5 for randomized vs >= 6 for deterministic.

## Direction 29

**Research Plan: Audit of Hashed Factor Base ECDL via Akshima/Bochum SAT Encoding**

**1. Construction / Algorithm**
Target curve: $E/\mathbb{F}_p$, $p \approx 2^n$. Factor base $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{H}\}$ where $\mathcal{H} \subset \mathbb{F}_p$ is a hash-defined set $|\mathcal{H}| = p^\alpha$, $\alpha \in (0,1)$. Relation search: find $a,b$ such that $aG + bT = \sum_{i=1}^m P_i$, $P_i \in \mathcal{F}$. Decomposition problem: given $R \in E(\mathbb{F}_p)$, find $m$-tuple $(P_1,\dots,P_m) \in \mathcal{F}^m$ summing to $R$. Encode as SAT via **Akshima/Bochum**: variables for $x$-coordinates $x_i \in \mathcal{H}$, $y_i^2 = x_i^3+Ax_i+B$, and group law constraints $\sum P_i = R$ using division polynomials $\psi_m$ or iterative addition formulas. Hash constraint $x_i \in \mathcal{H}$ encoded via boolean circuit for $H(x_i)=1$ (e.g., Keccak or algebraic hash).

**2. Cost Model**
- SAT variables: $V \approx m \cdot (\log_2 p + C_H)$ where $C_H$ = hash circuit complexity.
- Clauses: $C \approx m \cdot (C_{\text{curve}} + C_{\text{group}} + C_H)$.
- Solving time: $T_{\text{SAT}} \approx 2^{\beta V}$ for CDCL ($\beta \sim 0.01$–$0.1$ empirical) or $2^{\gamma V}$ for #SAT ($\gamma \sim 0.2$–$0.3$).
- Classical enumeration: $T_{\text{enum}} \approx |\mathcal{F}|^m / m! \approx p^{\alpha m}$.
- Total index calculus: $L_p[1/2, c]$ with $c = \sqrt{2\alpha + 1/\alpha}$ (heuristic) if SAT solves in poly($V$); else dominated by $T_{\text{SAT}}$.

**3. Falsification Criteria**
- **Obstruction confirmed**: For $n \geq 160$, $\alpha \in \{0.3, 0.4, 0.5\}$, $m \in \{2,3,4\}$, SAT solving time $T_{\text{SAT}} > T_{\text{enum}}$ for all instances, or $T_{\text{SAT}}$ scales as $2^{\Omega(V)}$ with $\beta > 0.05$ making $c > 1.5$.
- **Encoding blowup**: $C_H > 10^4$ clauses/bit forces $V > 10^5$ for $p \approx 2^{160}$, exceeding solver capacity.
- **Structural weakness**: Solutions found do not correspond to valid $\mathcal{F}$-decompositions (spurious SAT models from incomplete group law encoding).

**4. First Experiment**
Implement Akshima/Bochum encoding in **CaDiCaL**/**Kissat** via **PySAT** for $p \approx 2^{61}$ (Mersenne), $\alpha=0.5$, $m=3$. Hash $\mathcal{H} = \{x : \text{LSB}_{30}(\text{SHA256}(x)) = 0\}$. Generate 100 random targets $R$. Measure: (a) SAT vars/clauses, (b) solve time vs $T_{\text{enum}} \approx 2^{91}$, (c) solution validity rate. Parallel: implement #SAT counter (**sharpSAT**) on same instances to estimate $\gamma$. Threshold: if median solve time $> 1$ hour or $\beta_{\text{est}} > 0.08$, obstruction holds; proceed to structural analysis of conflict clauses.

## Direction 30

**Research Plan: Price Thue-Morse/Rudin-Shapiro Conversion for HNP Advantage Amplification**

**1. Exact Construction / Algorithm**
*Target*: Given an ECDLP instance $Q = [k]P$ over $\mathbb{F}_p$, and an oracle $\mathcal{O}$ returning MSB$_k$ (or LSB$_k$) with advantage $\epsilon = 2^{-\beta}$ ($\beta < \log_2 p$), recover $k$ in subexponential time $L_p[1/2, c]$ beating Pollard's Rho ($L_p[1/2, 1/2]$).

*Algorithm (Price Sequence Sieve)*:
1.  **Basis Generation**: Construct $m \approx p^{1/2}$ linear relations $k \equiv \sum_{i=1}^n a_i x_i \pmod p$ using a **Thue-Morse (TM)** sequence for coefficients $a_i \in \{\pm1\}$ to minimize correlation, or **Rudin-Shapiro (RS)** sequence for bounded flatness (low $L_\infty$ norm of Fourier transform).
2.  **Advice Injection**: For each relation, query $\mathcal{O}$ on $x_i$ to get noisy bits $b_i = \text{MSB}(x_i) \oplus e_i$. The TM/RS structure ensures the noise vector $\mathbf{e}$ has low discrepancy / bounded spectral norm.
3.  **Decoding via Price's Method**: Treat the system as a Bounded Distance Decoding (BDD) problem in a lattice $\Lambda$ generated by the relation matrix $A$. Use the **Price sequence** (iterated TM/RS) to construct a decoding basis $B$ where the Gram-Schmidt norms decay as $\|b_i^*\| \approx p^{1/2} \cdot 2^{-i\beta/n}$.
4.  **Recursive Lifting**: Apply Babai's Nearest Plane on $B$. The flatness of RS/TM guarantees the effective noise rate per level is $\epsilon_{eff} \approx \epsilon \cdot \sqrt{n}$. If $n \approx p^\delta$, total cost $T \approx 2^{n} \cdot \text{poly}(p)$.
5.  **Optimization**: Tune $\delta$ to balance $2^n$ (enumeration) vs $p^{1/2-\delta}$ (lattice dimension reduction). Target exponent $2\beta$ vs $1/2$: achieve $T \approx p^{\max(2\beta, 1/2 - \delta)}$.

**2. Cost Model**
*   **Time**: $T = \min_{n} \left( 2^{n H(\epsilon_{eff})} + \text{poly}(p) \cdot p^{1/2 - n/\log p} \right)$.
*   **Memory**: $M = \max(2^n, p^{1/2})$ (storing relations / lattice basis).
*   **Advantage Threshold**: Requires $\beta < 1/4$ for exponent $2\beta < 1/2$. If $\beta \ge 1/4$, falls back to $L_p[1/2, 1/2]$.
*   **Table (Target)**:
    | $\beta$ | Target Exponent | Memory |
    | :--- | :--- | :--- |
    | 0.10 | 0.20 | $p^{0.4}$ |
    | 0.20 | 0.40 | $p^{0.3}$ |
    | 0.25 | 0.50 | $p^{0.25}$ |

**3. Falsification Criteria**
1.  **Spectral Collapse**: The RS/TM correlation matrix $A^T A$ has minimum eigenvalue $\lambda_{min} < p^{1/2 - \delta} / \text{poly}(\log p)$, causing noise amplification $\epsilon_{eff} \to 1/2$ during lifting.
2.  **Price Decoding Failure**: The decoding radius of the Price basis $B$ is $< \|\mathbf{e}\|_2$ for all $n < p^{1/2}$, proven via transference theorems on the dual lattice $\Lambda^*$.
3.  **Memory Wall**: Required $M > 2^{80}$ for $p \approx 2^{256}$ at $\beta=0.2$, making it practically inferior to Rho.

**4. First Experiment**
*   **Setup**: SageMath/Python. $p \approx 2^{40}$ (toy), $p \approx 2^{80}$ (medium). Secret $k \xleftarrow{\$} [1, p-1]$.
*   **Oracle**: Simulate $\mathcal{O}(x) = \text{MSB}_{\lfloor \log_2 p \rfloor - \beta}(x) \oplus \text{Ber}(\epsilon)$ with $\beta \in \{0.1, 0.15, 0.2\}$.
*   **Implementation**:
    1.  Generate $n=2000$ relations using RS sequence (length $N=2^m \ge n$).
    2.  Construct lattice basis $B$ via LLL on relation matrix + Price orthogonalization step.
    3.  Run Babai NPP on target vector derived from oracle outputs.
*   **Metric**: Success rate vs $\beta$; measured decoding radius vs $\|\mathbf{e}\|_2$; runtime scaling vs $n$.
*   **Go/No-Go**: Success rate $> 50\%$ at $\beta=0.15$ with $n < 5000$ for $p \approx 2^{80}$ proceeds to $p \approx 2^{120}$ GPU implementation.

## Direction 31

**Research Plan: IDEA-012 Finite-Deck Weighted Endpoint (REVISE_SCOPED_REDUCTION)**

**1. Named Constructor & Theorem**  
Define `FiniteDeckWeightedEndpoint(𝔽_p, E, 𝒟, w, ℛ)` where:  
- `𝒟 = {D_1,…,D_m} ⊂ E(𝔽_p)` is a fixed “deck” of divisor representatives.  
- `w: 𝒟 → ℝ_{>0}` assigns a cost weight (e.g., `w(D) = log ‖ψ(D)‖` for a chosen isogeny `ψ`).  
- `ℛ: Div^0(E) → 𝒟^*` is a *scoped reduction* mapping any degree‑0 divisor to a multiset of deck elements, satisfying:  
  (i) `supp(ℛ(D)) ⊆ 𝒟`,  
  (ii) `∑_{D_i∈ℛ(D)} n_i D_i ∼ D` (linear equivalence),  
  (iii) `cost(ℛ(D)) = ∑ n_i w(D_i) ≤ C·h(D)` for explicit constant `C` and naive height `h`.  

**Theorem (Reduction Soundness)**: For any `D ∈ Div^0(E)`, `ℛ(D)` yields a relation in the factor base `𝒟` with probability `≥ 1/|𝒟|^δ` (`δ<1`), and the expected weight per relation is `O(log p)`.

**2. Cost Model**  
- **Precomputation**: `O(m·M(p))` to build `𝒟` and `w` (one-time).  
- **Relation search**: Sample random `R ∈ E(𝔽_p)`, compute `D = (R) - (O)`, reduce via `ℛ`. Cost per trial: `O(M(p)·log p)` for scalar mult + `O(m·log m)` for reduction.  
- **Linear algebra**: `m = L_p(1/2, c)` relations → `O(m^ω)` field ops.  
Total expected: `L_p(1/2, √2 + o(1))` if `C·δ < 1`.

**3. Falsification Criteria**  
- No deck `𝒟` of size `m = L_p(1/2, c)` admits a reduction `ℛ` with `C·δ < 1` for `p > 2^200`.  
- Empirical weight per relation exceeds `2·log p` on 1000 random curves.  
- Reduction fails to preserve linear equivalence for >0.1% of random divisors.

**4. First Experiment (Zero-Compute Preflight)**  
Implement a *contract test* in Python/Sage:  
- Input: prime `p ≈ 2^127`, curve `E/𝔽_p`, deck size `m = 500`.  
- Construct `𝒟` as `x`-coordinates of points from a short random walk.  
- Define `ℛ` via Baby-Step Giant-Step on `𝒟` (bounded depth 4).  
- Verify: (a) `ℛ(D) ∼ D` for 10k random `D`; (b) mean weight `≤ 1.5·log p`; (c) success rate `≥ 1/m^0.8`.  
Output: JSON report with `C, δ, success_rate`. If any check fails, IDEA-012 is rejected before any HPC run.

## Direction 32

**Research Plan: Direction 32 — Measure A(1) and A(d) on Toy Ladder**

**1. Exact Construction / Algorithm**
*   **Toy Ladder Setup:** Fix a small prime `p` (e.g., `p ≈ 2^16`) and an elliptic curve `E/F_p` with smooth order `#E = ∏ q_i^{e_i}`. Construct the "ladder" graph `G`: vertices `V = E(F_p)`, edges `(P, Q)` iff `Q = P ± R_j` for a fixed small basis `R_j` (e.g., `j=1..k`, `k=4`).
*   **Log-Graph `Γ_E`:** Assign discrete log labels `ℓ(P) ∈ Z/#E` relative to a generator `G`. Target function `f: V → Z/#E`, `f(P) = ℓ(P)`.
*   **Agreement Metric `A(d)`**: For degree `d ∈ {1, 2, 3}`, define the hypothesis class `H_d` as all polynomials `P(x, y) ∈ F_p[x, y]` of total degree `≤ d`, evaluated at affine coordinates `(x, y)` of `P ∈ V` (point at infinity mapped to fixed sentinel). 
    *   `A(d) = max_{h ∈ H_d} (1/|V|) ∑_{v∈V} 1[h(v) = f(v)]`.
*   **Optimization:** Solve `max_{h∈H_d} Agreement` via Integer Linear Programming (ILP) or MaxSAT encoding (variables = polynomial coefficients in `F_p`, constraints = equality checks). For `d=1`, brute-force search over `p^3` coefficients is feasible for `p<1000`; for `d>1`, use greedy coordinate descent + local search (flip coeffs) with random restarts.
*   **Null Model:** Generate `N=1000` random permutations `π: V → Z/#E`. Compute `A_null(d) = max_{h∈H_d} Agreement(h, π)`. Estimate `μ_d, σ_d`.

**2. Cost Model**
*   **Graph Construction:** `O(k * p)` group ops.
*   **ILP/MaxSAT (d=1):** `O(p^3)` variables/constraints → ~minutes for `p≈500` on standard solver (Gurobi/OR-Tools).
*   **Local Search (d=2,3):** `O(restarts * steps * |V| * dim(H_d))`. `dim(H_2) ≈ p^3`, `dim(H_3) ≈ p^6`. Cost dominated by evaluation `O(|V| * dim)`.
*   **Null Sampling:** `N * Cost(Optimization)`. Total budget: **< 48 CPU-hours** for `p ≤ 1000`.

**3. Falsification Criteria**
The hypothesis *"Low-degree polynomials correlate non-trivially with the discrete log on the ladder graph"* is **falsified** if:
*   `A(1) ≤ μ_1 + 3σ_1` AND `A(2) ≤ μ_2 + 3σ_2` AND `A(3) ≤ μ_3 + 3σ_3`.
*   Equivalently: `p-value > 0.001` for all `d ∈ {1,2,3}` against the random labelling null.
*   *Secondary:* If `A(d)` scales as `O(1/p)` (random guessing baseline) rather than `Ω(1)`.

**4. First Experiment (Week 1)**
*   **Parameters:** `p = 521` (NIST prime), `E: y^2 = x^3 + 2x + 3` (smooth order check required; fallback to `p=509`, random curve until `#E` is `B`-smooth, `B=50`). Basis `R_j`: 4 random points.
*   **Action:** Implement `d=1` brute-force search (coeffs `a,b,c` for `ax+by+c`) and `d=2` greedy search (100 restarts, 1000 steps). Compute `A(1), A(2)`. Generate `N=100` null permutations, compute `μ_1, σ_1, μ_2, σ_2`.
*   **Deliverable:** Table: `d | A(d) | μ_d | σ_d | Z-score | p-value`. Decision: Proceed to `d=3`/larger `p` iff `Z-score > 3` for any `d`.

## Direction 33

**Research Plan: Disjoint Projection Panel in Probabilistic Regime (IDEA-20260817-84755b)**

**1. Construction / Algorithm**
*   **Factor Base:** Define $\mathcal{F} = \{P \in E(\mathbb{F}_p) : x(P) \in \mathcal{V}\}$ where $\mathcal{V} \subset \mathbb{F}_p$ splits completely under $m$ disjoint rational projection maps $\pi_i: E \dashrightarrow \mathbb{P}^1$ (e.g., $x$-coordinate, $x+\lambda$, isogenous $x$-maps from low-degree $\phi_i$).
*   **Relation Generation (Probabilistic Regime):** For random $a,b \in \mathbb{Z}$, compute $R = aG + bT$. Decompose $R = \sum_{j=1}^k P_j$ using Semaev’s $m$-th summation polynomial $S_m$ evaluated over the fibre product $\prod_{i=1}^m \pi_i^{-1}(\pi_i(R))$.
*   **Exact-Arithmetic Fibre Test:** Solve $S_m(x_1,...,x_m, x(R))=0$ over $\mathbb{F}_p$ using exact rational reconstruction (FLINT/NTL) on the resultant variety. Reject relations where the fibre dimension $>0$ (positive-dimensional components indicate KN-FIND-7d098b "trap" subvarieties).
*   **Disjoint Panel Filter:** Retain relation iff the decomposition sets $\{P_j\}$ are disjoint across all $m$ projection panels (i.e., $\pi_i(P_j) \neq \pi_i(P_{j'})$ for all $i,j \neq j'$).
*   **Random-Relabelling Null Check:** Apply random $\mathbb{F}_p^*$-scaling to $x$-coordinates (inducing $\psi: E \to E^{(d)}$ twist) and recompute linear algebra dependencies. A valid relation must persist in the nullspace of the relabelled matrix $M^{(\psi)}$ with probability $\geq 1 - \epsilon$.

**2. Cost Model**
*   **Relation Search:** $O(m \cdot p^{1 - 1/m} \cdot \mathsf{poly}(\log p))$ per relation (Gröbner/Resultant on fibre product).
*   **Exact Arithmetic:** Multiplicative overhead $C_{exact} \approx 10^2$–$10^3\times$ floating point (modular resultants + rational reconstruction).
*   **Linear Algebra:** $O(|\mathcal{F}|^2)$ sparse matrix ops $\times$ $N_{relabel}$ (e.g., 10 twists).
*   **Total Target:** $L_p[1/2, c]$ with $c < \sqrt{2}$ (standard IC) if disjointness probability $P_{disj} \approx 1/m!$ and fibre traps are rare.

**3. Falsification Criteria**
1.  **Fibre Trap Density:** $> 5\%$ of candidate relations lie on positive-dimensional fibres (KN-FIND-7d098b caveat confirmed dominant).
2.  **Disjointness Collapse:** $P_{disj} < p^{-0.1}$ for $m \geq 3$, making relation yield sub-exponential.
3.  **Nullspace Instability:** $> 50\%$ of exact relations vanish under random relabelling (indicating "lossy object propagation" — structural aliasing in the factor base graph, not true dependencies).
4.  **Complexity Crossover:** Wall-clock time for $p \approx 2^{80}$ exceeds Pollard's Rho on same hardware.

**4. First Experiment (Week 1–2)**
*   **Target:** Curve `secp112r1` ($p \approx 2^{112}$), $m=3$ projections ($x, x+1, x_{\phi}$ for 2-isogeny $\phi$).
*   **Code:** Extend `crypto-autoresearcher/sage/ic_fibre.py` with FLINT exact resultant backend.
*   **Metric:** Generate 10,000 candidate $R$. Measure: (a) % passing exact fibre test (dim 0), (b) % of those passing disjoint panel filter, (c) Nullspace survival rate over 20 random quadratic twists.
*   **Go/No-Go:** Proceed to $m=4$ / larger $p$ only if (a) $> 10\%$, (b) $> 1\%$, (c) $> 90\%$.

