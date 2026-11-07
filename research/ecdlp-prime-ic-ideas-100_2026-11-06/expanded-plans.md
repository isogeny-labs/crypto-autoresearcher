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

## Direction 34

### Construction and repository audit
- Freeze commits of `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher`. Locate IDEA-20260807-efc8de, IDEA-20260815-bc26a3, and LEAD-EXO-methodology-instruments; extract the **actual three signal generators**, prior results, rejected variants, screening thresholds, and configurations. Repository contents are not available here; do not assume the families’ definitions.
- Inventory every ECDLP mechanism screen, including abandoned implementations. Map each to its input stage, claimed detectable signal, acceptance threshold, and smallest previously tested effect. Deduplicate equivalent tests while retaining configuration history.

### Exact replay algorithm
For each screen \(S\), family \(F\), curve size, and injection strength \(\alpha\):
1. Generate a matched null instance and positive instance using identical curve parameters, factor-base size, budgets, and coupled randomness.
2. Invoke the recovered generator \(F(\alpha)\) at its documented pipeline boundary. Record injected witnesses and labels separately; prohibit screen access to them.
3. Run the **unchanged production pipeline**, including preprocessing, filtering, relation collection, rank tests, and stopping rules—not merely the final statistic.
4. Independently verify that the signal survives to the intended detection boundary. For genuine elliptic-curve relations, check  
   \[
   aQ+bP+\sum_i c_iR_i=\mathcal O
   \]
   directly. Label artificial algebraic surrogates explicitly; never count them as genuine relations.
5. Report detection probability, false-negative rate, false-positive rate, confidence intervals, and cost per detected positive.

Use \(\alpha=0\), a strong positive, and a logarithmic dose ladder around each screen’s historical threshold. Define detection before replay; distinguish “statistically detected” from “produces useful relations.”

### Cost model
Measure field/group operations, relation yield, matrix dimensions/nonzeros/rank, peak memory, and wall time. Separate injection/oracle construction cost from screening cost. A detectable synthetic signal does **not** establish an ECDLP speedup; charge all non-oracular construction costs before comparing against Pollard rho’s \(O(\sqrt{\ell})\) group operations.

### Falsification
The methodological claim fails for a screen if validated strong positives remain undetected, or sensitivity appears only after threshold retuning that inflates null acceptance. Invalid witnesses, label leakage, or unmatched distributions invalidate the experiment rather than indicting the screen.

### First experiment
Replay the cheapest archived screen against all three recovered families: 100 strong-positive and 100 matched-null seeds per family. Publish immutable manifests, stagewise signal-retention checks, confusion matrices, and every failure trace before expanding the sweep.

## Direction 35

1. **Audit prior work before claiming novelty.** Inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for `LEAD-EXO-miller-pairing-cocycle`, Weil reciprocity, Miller functions, carry terms, and character extraction. Record commit/file references, tested identities, charged costs, and negative results. Repository contents were not provided here; this review remains a prerequisite.

2. **Exact construction.** Choose \(E/\mathbb F_p\), \(P\) of prime order \(N\), with \(\gcd(N,p-1)=1\). Let
   \[
   \operatorname{div}(f_m)=m[P]-[mP]-(m-1)[O],
   \qquad d=N^{-1}\pmod{p-1}.
   \]
   For an auxiliary \(T\), define
   \[
   F(Q)=\frac{f_N(Q+T)}{f_N(T)},\qquad U(Q)=F(Q)^d.
   \]
   Use only evaluations with disjoint supports and nonzero finite values; switch shifts for exceptions.

   **K1:** Verify Miller’s cocycle identity
   \[
   f_{a+b}=f_af_b\,g_{aP,bP}
   \]
   up to normalization, where \(\operatorname{div}(g_{A,B})=[A]+[B]-[A+B]-[O]\). Independently verify Weil reciprocity on disjoint supports.

   **K2:** Reciprocity predicts, for \(Q=kP\),
   \[
   U(Q)=r_kC^{kd},\quad
   r_k=\frac{f_k(-T)}{f_k(P-T)},\quad C=F(P).
   \]
   Thus \(c=1\). Check this identity exhaustively on tiny curves.

3. **Recovery algorithm and cost model.** Given only \(P,Q\), compute \(U(Q)\); attempt recovery using any proposed recurrence, elimination, or compression of \(r_k\). Treat computing \(r_k\) from the unknown \(k\) as the central obstacle—not free advice. Charge preprocessing, storage, group operations, field arithmetic, Miller evaluations, exceptional-point handling, and any multiplicative discrete logarithms. Report total and amortized costs separately. Measure \(\operatorname{ord}(C)\), since the multiplicative component may distinguish few indices.

4. **Falsification.** Reject the identities if exact-arithmetic checks fail after normalization/support checks. Reject the cryptanalytic lead if recovery requires known-\(k\) Miller chains, exhaustive carry tables, or total work scaling at least as \(\sqrt N\). Identity verification alone is not an attack.

5. **First experiment.** Implement Sage checks on several \(N\approx2^{10}\) prime-order curves; enumerate admissible \(k,T\), verify both identities, and test whether \(r_k\) has any independently computable low-complexity structure.

## Direction 36

**Hypothesis.** Coordinate-based models predict a balanced scalar-log bit on unseen points more efficiently than generic discrete-log recovery; planted leakage and random relabelling distinguish genuine signal from pipeline artifacts.

**Phase 0 — prior-work audit.** Inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `ec_hardness_predictor`, `LEAD-EXO-ml-learned-models`, coordinate classifiers, leakage controls, and failed runs. Record commit, construction, splits, seeds, compute, and outcome in a deduplication table. Repository contents are unavailable here; this audit is a prerequisite, not a completed review.

**Phase 1 — exact construction and controls.**
- Select curves \(E/\mathbb F_p\) with prime-order group \(q\), spanning \(q\approx2^{12},2^{16},2^{20},2^{24}\). Publish parameters.
- Sample \(k\) uniformly from \(1,\ldots,q-1\); form \(P=[k]G=(X,Y)\). Label \(b(k)=\mathbf1[k>q/2]\), exactly balanced.
- **Real task:** predict \(b\) from fixed-width coordinate bits, normalized coordinates, and separately preregistered algebraic features.
- **Positive control:** append \(h(P)=k\in\mathbb F_q\), normalized by \(q\). This is a deliberately planted additive homomorphic coordinate; a threshold recovers the label. A prime-order group has no nontrivial homomorphism to a single binary bit.
- **Null:** replace points with independent random injective identifiers of matching length; retain labels and sample counts. Expose no group-operation oracle.

Split by unordered pairs \(\{P,-P\}\), preventing signed-pair overlap. Shuffle generation order; exclude scalar indices and timing metadata.

**Phase 2 — learning and cost.** Compare logistic regression, boosted trees, and small MLPs at matched sample budgets. Track generation time, group operations, feature extraction, training FLOPs, memory, inference, and amortization across queries. Compare with exhaustive lookup and generic BSGS/Pollard-rho costs. Count label acquisition; free labelled logs are not a cryptanalytic speedup.

**Phase 3 — falsification and index-calculus relevance.** Require positive-control success, null chance performance, corrected significance across configurations, and replication across generators, curves, and held-out sizes. Failure to scale beyond toy groups falsifies extrapolation. Bit prediction alone is not index calculus: require a subsequent demonstrated improvement in relation yield or total log-solving cost.

**First experiment.** At \(q\approx2^{16}\), run all three arms with identical splits across ten seeds; investigate nothing further until controls pass.

## Direction 37

### Construction

Implement coherent, fixed-schedule **batched divsteps** for inversion modulo an odd prime \(p\), with \(n=\lceil\log_2p\rceil\). Initialize \((\delta,f,g)=(1,p,x)\). Each divstep uses
\[
(\delta',f',g')=
\begin{cases}
(1-\delta,g,(g-f)/2),&\delta>0,\ g\text{ odd},\\
(1+\delta,f,(g+(g\bmod2)f)/2),&\text{otherwise}.
\end{cases}
\]

For blocks of \(b\) steps, reversibly derive the integer transition matrix \(M\) from \(\delta\) and the low \(b+1\) bits of \(f,g\); apply
\[
(f',g')^T=2^{-b}M(f,g)^T
\]
once to full-width registers. Track coefficients \(a,c\) satisfying \(f\equiv ax,\ g\equiv cx\pmod p\), applying \(2^{-b}M\bmod p\). At termination, return \(fa\bmod p\) when \(f=\pm1\). Define \(0^{-1}=0\), using a coherent zero flag.

Use a published termination bound **verified for this exact recurrence**, never input-dependent stopping. Retain sufficient signed width; explicitly reverse block histories and ancillas. Integrate the inverter into the existing narrow-apply, in-place-multiplication, and quotient phases.

### Prior-work gate

Repository contents are unavailable here. Before implementation, inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for divstep, safegcd, jump-GCD, cswap, inversion, ipmul, and quotient experiments. Record commit, construction, tested domain, costs, and failure mode; distinguish genuinely new batching from previously rejected variants.

### Cost model

Compare identical clean reversible interfaces and arithmetic backends. Report logical qubits, Toffoli count/depth, Clifford operations, and qubit–Toffoli-depth product, both per inversion and end-to-end.

Charge for matrix synthesis, **quantum-variable** coefficient multiplication, modular halving, sign handling, quotient bookkeeping, history storage, and uncomputation. Sweep \(b\in\{1,2,4,8,16,32\}\); do not treat matrix entries as classical constants.

### Falsification

Reject if any input violates correctness or ancilla cleanup; if low-bit prediction fails; or if no batching choice improves the baseline resource frontier after integration. Savings confined to a Fiat–Shamir-selected subset do not qualify.

### First experiment

For every odd prime \(p<256\), exhaustively test all \(x\in[0,p-1]\), including zero, against classical inversion. Check each block against scalar divsteps, then reverse the complete computation. Collect exact reversible-gate counts before attempting cryptographic-size synthesis.

## Direction 38

### Construction and replication gate
- Obtain **EV-ECDLP-f6b3f5**, **EV-ECDLP-31e91c**, `fixture_gate_v2`, and **LEAD-RHO-advice-table-variants** from `isogeny-labs/crypto` and `crypto-autoresearcher`. Review linked experiments, failed controls, selection rules, and accounting conventions; produce an overlap matrix before coding. Repository contents are unavailable here, so prior findings remain unverified.
- Freeze the original definitions of \(T\), \(T_{\rm sel}\), “support,” and “basin.” Independently implement the recorded walk and advice construction, without importing experimental code. Replicate \(T_{\rm sel}/T=0.65,0.75\); include full-support and uniformly subsampled, matched-size controls.
- Use an elliptic curve over a prime field with a verified prime-order subgroup \(r\approx2^{30}\), not an asserted prime-order subgroup of order exactly \(2^{30}\). Sample \(Q=xP\) uniformly. Track walk states as \(R=aP+bQ\); recover \(x=(a-a')(b'-b)^{-1}\bmod r\) from usable collisions.
- Freeze advice before held-out targets. Charge every target-dependent construction step online; exclude any use of known \(x\) outside verification.

### Repair `fixture_gate_v2`
For small exhaustive instances, compare instrumented basin assignments against an independently written reference enumerator. Assert deterministic transitions, correct entry/merge attribution, complete state accounting, correct cycle handling, and no instrumentation-induced transition changes. Include deliberately corrupted fixtures that **must fail**. Separate logical correctness from measured basin enrichment; repair acceptance must not depend on observing speedup.

### Cost model
Report offline group operations \(C_{\rm off}\), online operations \(C_{\rm on}\), advice bytes, lookups, wall time, and success probability. For \(K\) targets, compare
\[
C_{\rm amort}=C_{\rm off}/K+\mathbb E[C_{\rm on}]
\]
against identically optimized rho and matched-memory controls. Include failed walks, restarts, and table construction. Report break-even \(K\), not merely online acceleration.

### Falsification
Reject the claimed mechanism if basin enrichment disappears on held-out targets/seeds, matched-size random support performs equivalently, instrumentation changes trajectories, or gains vanish under complete accounting. A constant-factor improvement does not establish index-calculus scaling.

### First experiment
After exhaustive fixture validation, run 256 paired targets at \(r\approx2^{30}\), sharing targets across baseline, full support, both selected supports, and random-support controls. Pre-register stopping rules and paired confidence intervals for operation counts; use independent selection/evaluation seeds. Scale only after correctness and an accounting-complete benefit survive replication.

## Direction 39

### Construction
- First audit `isogeny-labs/crypto`, its cryptanalysis work, and `crypto-autoresearcher` for best-of-candidate, indegree, batching, cycle-escape, and DP-replay experiments. Record commits, parameters, negative results, and reproducibility; repository access is required before claiming novelty.
- Target P-256’s prime-order subgroup, with \(Q=dG\). Track \(P=aG+bQ\).
- Define one globally shared, deterministic transition. Set \(j=h_0(P)\bmod m\), with precomputed \(R_j=u_jG+v_jQ\). Form \(C_\pm=P\pm R_j\), score both using an independently seeded point hash, and choose the lower score. Update coefficients with the corresponding sign; specify deterministic tie-breaking.
- Implement in `gpu/nist`, preserving the shipping kernel’s coordinate representation where practical. For affine updates, both candidates share denominator \(x(R_j)-x(P)\): batch these denominators across \(W=16,24,32\) walks/thread using the kernel’s own inversion routine. Handle exceptional additions explicitly.
- Detect short fruitless cycles locally and **restart** affected walks with fresh coefficient pairs. Never introduce history-dependent successor choices: these can destroy coalescence. Measure detector overhead and discarded work.

### Cost model
Measure
\[
T_{\rm useful}=T_{\rm step}\times E[\text{aggregate steps to recover }d].
\]
Include two candidate constructions, scoring, coefficient updates, batch inversion, register pressure/spills, occupancy, DP handling, and restart losses. A batch of \(W\) nonzero denominators costs approximately one inversion plus \(3(W-1)\) multiplications, excluding candidate arithmetic.

Report paired candidate throughput **and accepted transitions/second**. Model collision work as \(c\sqrt n\), estimating \(c\) experimentally; increased indegree is not automatically beneficial. This is a rho improvement, not an index-calculus algorithm.

### Falsification
Reject if:
- end-to-end collision time does not improve over shipping at matched resources;
- gains disappear after DP traffic, cycle handling, or spills;
- score correlations create excessive cycles, biased coverage, or DP starvation;
- DP replay gains fail on fresh walks.

Predeclare confidence intervals and a practically meaningful speedup threshold.

### First experiment
Run an instrumented A/B sweep on P-256 using identical starts, tables, DP predicate, and paired seeds: shipping versus best-of-\(\pm R\), across all three \(W\) values. Replay the existing DP corpus for regression and throughput—not proof of collision improvement. Estimate steps-to-collision separately on tractable prime-order test curves, then validate fresh P-256 transition/DP statistics.

## Direction 40

**Construction.** First audit `isogeny-labs/crypto` and `crypto-autoresearcher` for tag-tracing, paired affine addition, batch inversion, DP replay, and point-halving experiments. Record commit IDs, parameters, negative results, and reusable code; repository contents are unavailable here, so novelty remains unverified.

Use a nonsingular short-Weierstrass curve over a 64-bit prime, with a verified large prime-order subgroup. Implement in `rho_walk_leads`:
- Plain \(r=16\) adding walk: \(P\leftarrow P+R_{h(P)}\), with canonical-coordinate hashing and coefficient tracking \(P=aG+bQ\).
- Speculative paired walk: predict the next bucket from a cheap tag; calculate two additions sharing one inversion, then validate the prediction. A mismatch commits only the first addition. Never substitute an unchecked tag transition for the canonical walk.

For \(P=(x,y)\), first addend \((u,v)\), define
\[
d=u-x,\quad n=v-y,\quad A=n^2-(x+u)d^2,\quad
B=n(xd^2-A)-yd^3.
\]
The intermediate point is \((A/d^2,B/d^3)\). For predicted second addend \((w,z)\), set \(e=wd^2-A,\ f=zd^3-B\). One inverse of \(de\) recovers both \(d^{-1}\) and the second slope \(f/(de)\). Handle zero denominators explicitly.

**Cost model.** Batch inversions across \(W=8,16,\ldots,1024\) walks. Measure complete ns/committed logical step, including hashing, prediction, coefficient updates, batching, exceptional cases, and DP bookkeeping. If prediction accuracy is \(q\), each pair attempt commits \(1+q\) steps; compare its measured cost against \((1+q)\) plain steps. Report field-operation counts and cache effects.

**Correctness and falsification.** Require bit-exact agreement with plain trajectories and replayable DP collisions. Reject if prediction accuracy fails the measured break-even threshold, end-to-end speedup disappears, or steps/collision increase beyond statistical uncertainty.

**First experiment.** Freeze curve, seeds, and DP density; sweep batch widths with plain, measured predictor, random predictor, and oracle predictor. The oracle isolates the maximum possible pairing benefit before investing in tag design.

**Binary follow-up.** Separately benchmark subgroup-correct point halving on sect113r1, charging quadratic solving, root selection, coefficient updates, and replay. Do not conflate cheaper rho steps with index-calculus progress.

## Direction 41

### Construction / approval gate
Treat **H-AUXIN-6db354** as a conditional protocol approval, not a validated speedup. Repository contents were not supplied; reviewing the named artifacts and prior experiments is a prerequisite.

1. Inspect `isogeny-labs/crypto` cryptanalysis records and `crypto-autoresearcher` for RUN-AUXIN-fd1edc, IDEA-20260930-68326c, and prior Cheon/auxiliary-input tests. Record commit hashes, configurations, negative results, and duplicate hypotheses.
2. Normalize census and roster into typed records: curve, prime subgroup order \(\ell\), generator \(P\), target \(Q=[x]P\), auxiliary-point provenance, exponent, instance count, acquisition cost, and reuse permissions.
3. For each branch \(r\mid(\ell-1)\), admit a target only when an authenticated auxiliary point \(A=[x^r]P\) is available for the **same scalar and generator**. Ordinary scalar multiples \([r]Q\) do not qualify. Quarantine unsupported branches.
4. Join on these compatibility fields, deduplicate targets and auxiliary assets, and enforce roster multiplicity and reuse constraints. Never extrapolate a tested auxiliary source into unlimited supply.

### Algorithm and cost model
For each admitted target, run the corresponding Cheon auxiliary-input attack; use Pollard rho otherwise.

Model branch cost as
\[
C_r=c_1\sqrt{\ell/r}+c_2\sqrt r+C_{\rm acquire}+C_{\rm verify},
\]
with constants, memory, and preprocessing measured separately. Compare against a measured rho baseline under identical hardware and parallelism.

Define the supply-capped branch quantity
\[
E(r)=\sum_{t\in S_r}\max(0,C_{\rho,t}-C_{r,t}),
\]
where feasible allocations \(S_r\) obey demand, inventory, and reuse limits. Select allocations jointly across branches to prevent double-counting targets or shared assets. Report field-operation costs, wall time, memory, and uncertainty—not just asymptotic savings.

### Falsification
Reject deployment applicability if provenance cannot establish same-secret auxiliary input, compatible supply is zero, acquisition erases savings, or measured total cost fails to beat rho. This tests an auxiliary-input opportunity, **not** generic prime-field ECDLP index calculus.

### First experiment
Freeze both artifacts and produce the capped compatibility join. Then benchmark its highest-predicted-savings branch on reproducible toy prime-order groups, including incompatible-scalar and ordinary-multiple negative controls. Publish the complete allocation ledger and benchmark results before approving larger runs.

## Direction 42

**Construction and provenance.** First locate EXP-AUXIN-25a29a and LEAD-RHO-cheon-toy-reproduction in `isogeny-labs/crypto`, the cryptanalysis materials, and `crypto-autoresearcher`. Record commit hashes, parameters, previous outcomes, and unresolved failures; inspect implementations rather than relying on summaries. Repository contents are unavailable here, so prior results remain unverified.

Use the experiment’s exact prime-field curve, point \(P\) of prime order \(r\), and \(d=65536\). Require \(2^{55}\le r<2^{56}\), \(d\mid r-1\), and certified point order. For uniformly sampled nonzero \(x\), provide \(Q=[x]P\) and auxiliary point \(A=[x^d\bmod r]P\). Explicitly distinguish this auxiliary-input attack from ordinary ECDLP.

**Exact recovery algorithm.** Let \(g\) generate \(\mathbb F_r^\*\), \(m=(r-1)/d\), and \(h=g^d\bmod r\).

1. Recover \(i\in[0,m)\) satisfying \(A=[h^i]P\) using multiplicative-action BSGS: store \([h^j]P\), \(0\le j<B=\lceil\sqrt m\rceil\); probe \([h^{-kB}]A\). A match yields \(i=j+kB\bmod m\).
2. Set \(R=[g^i]P\), \(z=g^m\bmod r\). Apply the same procedure with order \(d\) to solve \(Q=[z^t]R\).
3. Return \(x=g^{i+mt}\bmod r\); certify \([x]P=Q\) and \([x^d]P=A\).

**Cost model and reporting.** Report both stages separately: table entries, probes, scalar multiplications, underlying additions/doublings, elapsed time, peak RSS, and certificate checks. Expected scale is \(O(\sqrt{r/d}+\sqrt d)\) **scalar multiplications**, not additions. Benchmark Pollard rho on the identical subgroup and hardware; report measured and projected rho costs separately. Include distinguished-point density, storage, communication, and walk overhead. Report gains \(T_\rho/T_{\rm aux}\) and fractions \(1-T_{\rm aux}/T_\rho\), likewise for memory. Separate auxiliary-input generation from attack cost.

**Falsification.** Reject correctness on any failed certificate; reject practical advantage if full-cost runtime does not beat rho. Missing auxiliary-input justification invalidates any ordinary-ECDLP claim.

**First experiment.** Freeze one manifest and seed; run both stages at 56 bits, certify recovery, then run matched rho before expanding to multiple seeds.

## Direction 43

### Construction
Implement **TABLE_PHASE_POPC** as an exact alternative encoding of the existing phase/sigma lookup—not a new walk.

For the control’s \(N\)-entry phase table \(T\), with \(q\)-bit outputs, construct:
\[
P_{k,j}=\sum_{r=0}^{31}\left((T[32j+r]\gg k)\&1\right)2^r,
\]
padding the final word with zeros. For bucket \(b\), recover:
\[
T[b]=\sum_{k=0}^{q-1}2^k\,\operatorname{popc}
\left(P_{k,b\gg5}\ \&\ (1_u\ll(b\&31))\right).
\]
Preserve bucket extraction, point arithmetic, sigma interpretation, distinguished-point predicate, and reporting exactly. Use read-only cached planes initially; test shared-memory placement only as a subsequent variant.

### Prior-work gate
Repository contents are unavailable here, so prior review remains mandatory, not claimed completed. Before implementation, inspect `isogeny-labs/crypto` cryptanalysis materials and `crypto-autoresearcher` for `TABLE_PHASE_POPC`, phase encodings, bit planes, POPC, sigma-table benchmarks, and `LEAD-RHO-ecc2k130-gpu-fpga-throughput`. Record commit IDs, tested configurations, failures, and the precise conditions/units behind **15.88 B/s**. Skip already-falsified configurations unless identifying a changed assumption.

This is a rho-throughput experiment, **not evidence of prime-field ECDLP index-calculus progress**.

### Cost model
Control: measure actual lookup loads, cache misses, dependency latency, registers, and occupancy.

Candidate: \(q\) plane-word loads, \(q\) POPCs, masks/shifts, and output assembly per lookup; storage \(4q\lceil N/32\rceil\) bytes. Compare against the control’s *actual* representation, not an assumed unpacked table. Estimate total speedup from measured lookup fraction \(f\):
\[
S=[(1-f)+fS_{\rm lookup}^{-1}]^{-1}.
\]
Include initialization and reporting in end-to-end results.

### Falsification
Reject for any reconstructed-table mismatch, divergent walk state, or failed **300-report re-walk gate**. Reject the throughput hypothesis if paired full-walk runs show no statistically credible improvement over the contemporaneous control; historical 15.88 B/s alone is insufficient.

### First experiment
On one RTX PRO 6000, exhaustively validate table reconstruction, then alternate control/candidate runs using identical seeds and identical sorted DP corpora. Fix clocks, compiler, launch parameters, and reporting. Re-walk all 300 reports; collect wall-clock throughput, lookup-sector traffic, POPC utilization, registers, and occupancy across repeated paired runs.

## Direction 44

### Construction and prior-work gate
- Review `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for `LEAD-RHO-ecc2k130-iteration-function`, table-v3, fused sigma-table, `SIGMA_SIGN=2`, and previous timing/correctness reports. Record commits, rejected variants, iteration definitions, and hardware. **Repository access is unavailable here; this review remains a prerequisite, not a completed claim.**
- Freeze the existing group, partition function, table generation, distinguished-point predicate, and collision solver. Compare **A:** fused sigma-table control; **B:** table-v3 walk kernel. Test all three configurations: sigma, `SIGMA_SIGN=2`, and table-v3, explicitly recording which implementation/configuration combinations exist.
- Maintain \(X=aP+bQ\). Each transition must update the point and coefficients consistently, including canonicalization/sign handling. Do not introduce a new walk while measuring the kernel change.

### Measurement protocol
For each valid comparison, run five paired blocks with order **AB, BA, AB, BA, AB**. Match starting states, tables, seeds, walk budgets, and distinguished-point settings within each pair. Pin workers; fix compiler flags, clocks, thread count, and memory placement; exclude warm-up and compilation.
- Bracket the campaign with matched **A/A** measurements; reject timing results if control drift exceeds a predeclared 2%.
- **Planted-log gate:** choose random \(x\), set \(Q=xP\), and require recovered logs to satisfy \(x'P=Q\).
- **Re-walk gate:** replay collision-producing walks and independently check checkpoint states, coefficient invariants, and the final collision equation. Require bit-identical A/B traces only where transition semantics are intended to match.

### Cost model
Measure completed logical transitions per second \(R\), transitions per successful solve \(I\), and non-walk overhead \(H\):
\[
T_{\rm solve}=I/R+H.
\]
Report failed/degenerate collisions, retries, table construction, distinguished-point traffic, memory, and energy separately. Estimate paired solve-time ratios with uncertainty; five timing pairs alone do not establish unchanged collision efficiency. This tests rho engineering, not an index-calculus breakthrough.

### Falsification
Reject correctness on any invariant, replay, or planted-log failure. Reject the performance lead if throughput gains disappear after drift correction, are offset by increased \(I\) or overhead, or remain statistically unresolved.

### First experiment
Run the correctness gates on a tractable prime-field instance, then the five paired target-hardware kernel blocks. Advance only surviving variants to independently seeded end-to-end solves.

## Direction 45

**EXP-GRUMPY-eb8675 — certified exhaustive ladder**

**Construction.** Work in the additive surrogate \(G=\mathbb Z/\ell\mathbb Z\), with \(P=1\), target \(Q=xP\), and \(\ell_k=\operatorname{nextprime}(2^k)\), \(k=10,\ldots,20\). Freeze each candidate’s deterministic, target-independent coefficient schedule \(S=((a_i,b_i))\), representing stored points \(a_iP+b_iQ\). Preserve insertion order, stopping rules, and duplicate-handling policy.

For every pair \(i<j\) with \(b_i\ne b_j\), the collision covers exactly
\[
x=(a_i-a_j)(b_j-b_i)^{-1}\pmod\ell.
\]
Maintain an exact bitmap of covered targets and record coverage after every insertion. Equal coefficient pairs are uninformative; equal \(b\), unequal \(a\) pairs cover nothing.

Run **negation as a separate arm**: additionally cover solutions of
\[
(a_i+a_j)+(b_i+b_j)x=0.
\]
Handle zero denominators explicitly; do not credit universal, uninformative identities as solved targets.

**Controls and independent certification.** Include sequential baby-step/giant-step: babies \(iP\), \(0\le i<m\); giants \(Q-jmP\), \(0\le j<\lceil\ell/m\rceil\), with \(m=\lceil\sqrt\ell\rceil\). Independently simulate every \(x\in\mathbb Z/\ell\mathbb Z\), storing actual residues and detecting collisions. Verify that each collision yields a valid recovered \(x\), and compare first-solution insertion against the bitmap prediction. Adaptive schedules require per-target execution; a single fixed covered-set certificate cannot certify them.

**Cost model.** Report group additions, initializations, stored points, lookups, canonicalizations, peak bytes, and empirical stopping-time distribution over all targets. Charge negation/canonicalization explicitly. Separate pair-enumeration and certification overhead from attack cost. Report mean, median, worst case, and fixed-budget success against identical-memory controls.

**Falsification.** Any bitmap/simulator discrepancy invalidates certification. Reject a claimed improvement if it disappears after duplicate accounting, equal-memory comparison, or negation costs. Surrogate improvement alone does not establish an ECDLP index-calculus advance.

**First experiment and evidence.** Start at \(\ell=\operatorname{nextprime}(2^{10})\): certify controls, then frozen candidate schedules, before extending the ladder. File source, schedule hashes, manifests, coverage bitmaps, mismatch logs, and cost tables under `EXP-GRUMPY-eb8675`, cross-referenced to `EXP-GRUMPY-cd7b82` Stage 1.

Repository contents are unavailable here: first inventory prior experiments in both named repositories, linking duplicates and negative results before claiming novelty.

## Direction 46

**EXP-LHW-9adf78: measure the full price of residue filtering**

1. **Recover definitions and prior results.** Search `isogeny-labs/crypto`, cryptanalysis materials, and `crypto-autoresearcher` for `EXP-LHW-9adf78`, `H-LHW-371a91`, `LEAD-RHO-lhw-modular-filter-price`, and `W(m,w)`. Record commit hashes, tested parameters, negative results, and unresolved assumptions. Repository contents are unavailable here; do not treat the construction below as their verified definition.

2. **Exact construction.** Provisionally define
   \[
   W(m,w)=\{a\in[0,2^m):\operatorname{popcount}(a)=w\}.
   \]
   Replace this with the repository definition before execution. For \(M=2^k-1\) and \(2^k+1\), count
   \[
   B_r=\#\{a\in W(m,w):a\bmod M=r\}
   \]
   using dynamic programming over bit position, weight, and residue. Exploit \(2^k\equiv1\) or \(-1\pmod M\), but charge all preprocessing. Implement bucket sampling with counted DP transitions. Integrate it into the existing relation generator without assuming that the unknown discrete logarithm’s residue is available.

3. **Cost model.** Record preprocessing, memory, bucket draws, rejected candidates, residue guesses, group operations, relation yield, and linear algebra. Report
   \[
   T_{\rm total}=T_{\rm setup}+T_{\rm guesses}+T_{\rm generation}
   +T_{\rm relations}+T_{\rm LA}.
   \]
   Measure effective work per independent usable relation, not merely bucket shrinkage. Compare complete-solve cost against both the unfiltered pipeline and matched Pollard rho. Explicitly distinguish integer residues modulo \(M\) from scalar arithmetic modulo the subgroup order \(n\).

4. **Proof obligation / falsification.** Derive the joint distribution of bucket choice, target compatibility, and relation success. Every conditioning step must specify an implementable sampler and its cost. Falsify the proposed gain if it requires an unavailable target-residue oracle, loses correctness through reduction modulo \(n\), or has residue-search/sampling costs that cancel its relation-yield improvement. Any asymptotic claim must survive charging preprocessing and unsuccessful guesses.

5. **First experiment.** Exhaustively enumerate \(W(24,8)\) for \(M\in\{31,33,127,129\}\); verify DP counts and sampler frequencies. On a small prime-field curve with a known prime-order subgroup, exhaust all target scalars and compare oracle-assisted, honestly guessed, and unfiltered variants. Publish operation counts, failure rates, and reproducible seeds.

## Direction 47

### Construction
- First retrieve **EXP-LHW-b49bc6 Stage 1**, **LEAD-RHO-lhw-polymem-collision-walks**, and related tests from `isogeny-labs/crypto` and `crypto-autoresearcher`. These repositories are unavailable here, so prior results and E1/E2 definitions remain unverified. Extract commit IDs, frozen \(w\)-values, jump construction, hash-to-jump mapping, seeds, scoring formulas, and claim TTL; stop if these cannot be recovered.
- Reproduce the frozen ladder for \(m\in\{20,24\}\), without parameter retuning. Let \(D_{m,w}\) be its admissible jump-label domain and \(J:D_{m,w}\to E(\mathbb F_p)\) its original jump map.
- Enumerate **hash-realisable** labels only. Establish reachability from the selector’s specification; finite sampling cannot certify it. Stream canonical point encodings into an exact multiplicity table:
  \[
  c(P)=|\{d\in D_{m,w}:J(d)=P\}|.
  \]
  Preserve selector probabilities separately if labels are nonuniform.
- Checkpoint enumeration cursor, multiplicities, completed blocks, configuration digest, RNG state, and checksums. Restart by loading the latest committed checkpoint; never count a block twice.
- Run the original collision walk with checkpointed position, coefficient state, step count, collision records, and RNG state. Renew claims before expiry and terminate cleanly before the TTL safety margin.

### Cost model
For each cell, report enumeration time, group additions, hashing, peak RAM, checkpoint bytes, I/O time, restart overhead, and walk steps. Compute support size, multiplicity histogram, and jump collision probability \(\sum_P q(P)^2\). Do not equate this one-step statistic with full-walk collision probability. Score **E1 versus E2 using their recovered definitions**, including preprocessing and checkpoint costs.

### Falsification
Reject the claimed advantage if exact counts contradict its assumed sumset size or multiplicities; E2 loses to E1 after equal-budget accounting; benefits disappear across held-out seeds; or resumable runs produce different counts or trajectories from uninterrupted runs.

### First experiment
Use the smallest frozen \(m=20\) cell. Run uninterrupted and deliberately interrupted/resumed copies with identical seeds and total work. Require identical final tables and trajectories. Then compare E1/E2 predictions with observed collision statistics across preregistered independent seeds before advancing to \(m=24\).

## Direction 48

1. **Recover and freeze the incumbents.** Repository contents are unavailable here; do not treat either method as previously verified. In `isogeny-labs/crypto` and `crypto-autoresearcher`, locate `IDEA-20260930-79abd9`, `LEAD-RHO-lhw-preprocessing-frontier`, and related negative results. Record commit hashes, both row definitions, the meaning of \(m\), advice-reuse assumptions, and whether “BL” means Bernstein–Lange. Reproduce their smallest published test before extending it. The construction below assumes \(m\) is the scalar bit length; revise if the records disagree.

2. **Exact construction.** Use a prime-order subgroup \(\langle P\rangle\) of an elliptic curve over a prime field, with \(n>2^{40}\). Targets satisfy \(Q=xP\), \(0\le x<2^m\), for \(m\in\{32,40\}\).
   - **Split-advice baseline:** partition bit positions into balanced sets \(I,J\). Precompute \(P_i=2^iP\). For each weight allocation \(a+b\le w\), store
     \[
     A_a=\{(\sum_{i\in S}P_i,S):S\subseteq I,\ |S|=a\}.
     \]
     Enumerate \(T\subseteq J\), \(|T|=b\), and look up \(Q-\sum_{j\in T}P_j\). Verify recovered scalars.
   - **Weight-restricted BL incumbent:** reproduce the repository’s actual advice generation, walk, and lookup rules, restricting scalar support only where justified by that construction. Do not relabel ordinary meet-in-the-middle as BL.

3. **Price both rows.** Count additions, doublings, negations, inversions, table probes, bytes, and peak RAM separately. Report group-operation totals using an explicit conversion convention, plus unconverted counts. Include advice construction, failures, verification, and expected online cost. Report amortized cost \(C_{\rm pre}/K+C_{\rm online}\) for \(K=1,10^2,10^4\). Compare with memory-matched low-weight search and unrestricted Pollard rho. For uniform scalars, charge the actual covered probability; planted success is not general ECDLP progress.

4. **Falsification.** Reject any claimed advantage erased by preprocessing, memory matching, missed weight allocations, or honest coverage accounting. Reject independence or walk-mixing assumptions contradicted by measurements.

5. **First experiment.** At both \(m\), plant 100 independently sampled exact-weight-six logs; freeze advice before sampling targets. Sweep feasible advice budgets, measure both rows, then repeat with uniform scalars as a coverage control. Publish seeds, operation counters, and break-even \(K\).

## Direction 49

### Construction and prior-work audit
- Check out and record commit hashes for `isogeny-labs/crypto`, its cryptanalysis work, and `crypto-autoresearcher`. Search for `H-ECDLP-ff38dc`, `LEAD-RHO-matched-rho-calibration`, `ecbench`, negation walks, replay certificates, and “section 5a.” Build a ledger of tested configurations, failures, counters, and unresolved discrepancies before introducing changes. Repository contents are not available here; this review remains a required execution step.
- Freeze three implementations: plain Pollard ρ; negation-quotient ρ with canonical representatives and explicit fruitless-cycle handling; negation BSGS.
- For BSGS, store canonical representatives of \(jP\), \(0\le j\le m\). Probe \(Q-(2i+1)mP\); a signed match yields \(k=(2i+1)m\pm j\bmod r\). Choose \(m\approx\sqrt r/2\), verify every recovered logarithm, and handle endpoint coverage explicitly.

### Experimental design and certificates
For every integer subgroup size \(\lceil\log_2r\rceil=32,\ldots,48\), run each algorithm on **24 independently seeded instances**, balanced across at least four prime-field curves. Share curve/target instances across algorithms; distinguish field size from subgroup order.

Archive curve parameters, subgroup-order evidence, generators, seed derivation, targets, walk rules, restart policy, counters, environment, and recovered-log verification. Supply deterministic replay and an independently implemented verifier. Apply section 5a’s actual band only after retrieving its definition.

### Cost model and fit
Count additions, doublings, field operations, canonicalizations, hash probes, memory, restarts, and elapsed time separately; publish raw and weighted totals.

Set \(N=\sqrt r\). Define
\[
R_A(N)=\frac{\text{measured mean work for }A}
{\text{matched finite-size reference expectation for }A}.
\]
Freeze reference expectations before medium-size measurements, including stopping rules and restart overhead. Fit \(R_A(N)=1+c_A/N^{\beta_A}\), with curve-clustered uncertainty and held-out sizes. Compare against a free-asymptote model; do not force convergence to one.

### Falsification
Reject the proposed sealing claim if held-out intervals breach section 5a’s band, replay fails, negation-cycle overhead remains unexplained, curve effects dominate uncertainty, or the free-asymptote model materially outperforms the prescribed fit. Add runs when 24 cannot resolve the band.

### First experiment
At 32 bits, execute 24 matched instances per algorithm, replay all certificates, and independently validate counters and BSGS boundary coverage before launching larger sizes.

## Direction 50

### Construction

- Reproduce `EXP-CERTBIN-b4d29c` at \(n=131\). First inspect both repositories for its implementation, parameters, prior results, Design C, Bailey sigma, and `IDEA-20261015-2d8e5a`; record commit hashes and distinguish tested results from proposals. These artifacts are not available in this conversation.
- Treat this as a **binary-field Koblitz rho cost experiment**, not prime-field index calculus. Any transfer to the latter requires separate evidence.
- On the recorded prime-order subgroup, implement matched walkers using identical arithmetic, partitions, seeds, and distinguished-point (DP) density:
  1. **C:** canonicalise under \(P\mapsto\pm\tau^jP\) after every step.
  2. **Sigma:** reproduce Bailey’s actual transition rule, normalising only at DPs.
  3. **Polynomial-key variant:** reproduce the cited rotation-invariant key exactly. If unspecified, test the explicitly labelled fallback
     \[
     K(P)=\prod_{j=0}^{130}(T-x(P)^{2^j})\in\mathbf F_2[T].
     \]
     This identifies Frobenius orbits of \(x\), hence point orbits modulo sign. Handle infinity separately.
- Maintain \(P=aG+bQ\). Applying \(\pm\tau^j\) must multiply both coefficients by \(\pm\lambda^j\bmod r\). Verify reconstructed states and recovered logarithms.
- Test whether each transition actually respects the proposed orbit equivalence; an invariant endpoint key alone does **not** establish quotient-walk speedup.

### Cost model

Use Callgrind `Ir` as the primary deterministic proxy, reporting
\[
C_{\rm step}=\frac{Ir_{\rm walk}}{N_{\rm steps}\,Ir_{\rm field\ multiply}}.
\]
Measure squaring, multiplication, inversion, canonicalisation, key construction, coefficient updates, DP tests, and table operations separately. Also report wall time, memory, effective orbit size, fruitless cycles, and total cost per successful solve. DP-only normalisation contributes approximately \(p_{\rm DP}C_{\rm norm}\), but collision efficiency must be measured independently.

### Falsification

Reject an advantage if canonicalisation overhead exceeds measured collision savings; quotient transitions fail; short cycles erase gains; keys merge inequivalent orbits; or coefficient bookkeeping produces invalid collisions.

### First experiment

Run a fixed-seed, million-step microbenchmark at \(n=131\), with representative DP densities and instrumentation checks disabled during timing. Then validate collision behaviour on tractable smaller instances before extrapolating full-solve costs.

## Direction 51

**Target and prior-work check.** Treat H-EWALK-29cb90 as unverified. The repositories are not available here, so no prior-test review can be claimed. Before implementation, search both repos for `H-EWALK-29cb90`, `LEAD-RHO-non-automorphism-equivalence`, canonicalisation, quotient walks, invariant encodings, and preprocessing; record tested constructions, cost conventions, and counterexamples.

**Exact construction.** First specify the action of \(H\); cardinality alone does not define canonicalisation. For the concrete translation action, choose ordinary \(E/\mathbb F_p\), \(N=\#E(\mathbb F_p)\), and rational \(H\le E(\mathbb F_p)\) with \(h>6\), \(h\mid N\), and \(h\approx N^{1/3}\). Construct
\[
C(P)=\min_{\rm lex}\{\operatorname{enc}(P+T):T\in H\}.
\]
Exhaustively verify \(C(P)=C(Q)\iff P-Q\in H\).

Test three implementations: orbit enumeration; a precomputed dictionary \(P\mapsto C(P)\); and the quotient-isogeny encoding \(\operatorname{enc}(\phi(P))\), where \(\ker\phi=H\). The last is a complete orbit invariant, not necessarily a representative on \(E\); determine whether the proposed walk accepts it and supports transitions without costly lifting. Ordinary-curve automorphism bounds do not themselves constrain translation actions.

**Cost model.** Report group additions/doublings, field operations, bit operations, memory, preprocessing, and amortised online cost separately. Fix \(T\), the number of walk steps, and charge
\[
C_{\rm total}=C_{\rm setup}+T C_{\rm step}.
\]
State allowed advice, lookup costs, and encoding access. A universal group-operation-only lower bound is false with unrestricted preprocessing: the dictionary uses zero online group operations.

**Falsification criteria.** Distinguish refuting the literal claim from improving cryptanalysis. An asymptotic canonicaliser family with \(o(\log h)\) online group operations refutes the literal bound. A useful attack additionally needs charged speedup exceeding one against an equally optimised rho baseline, including setup, transition generation, collision handling, and logarithm recovery. Small-instance timings cannot prove an asymptotic bound.

**First experiment.** Exhaustively enumerate several small ordinary prime-field curves with eligible \(h\); build the dictionary and quotient invariant, verify every fibre, and run identical collision walks under both encodings. Publish operation counts and amortisation break-even points before pursuing a lower-bound proof.

## Direction 52

### Construction
- **Repository gate:** inspect `isogeny-labs/crypto`, `cryptanalysis`, and `crypto-autoresearcher` for negation/Frobenius quotient walks, fruitless-cycle mitigation, GPU benchmarks, and production distinguished-point (DP) settings. Record commit IDs, tested hypotheses, and outcomes before proposing variants. Repository contents were not supplied here; prior-test coverage remains unverified.
- Reproduce ecc-challenges PR #56 against its parent commit using the **actual campaign curve, subgroup, jump table, and production DP density** \(\theta\).
- Maintain \(X=aP+bQ\). Canonicalize the negation class using a deterministic encoding:
  \[
  C(X)=\min(\operatorname{enc}(X),\operatorname{enc}(-X)).
  \]
  Whenever canonicalization negates \(X\), replace \((a,b)\) by \((-a,-b)\bmod n\). Derive jump selection and DP predicates from the canonical encoding.
- Instrument repeated states, short cycles, escape attempts, endpoint duplicates, coefficient consistency, and usable collisions. Test the existing escape rule against deterministic, domain-separated alternate jumps that preserve coefficient tracking.

### Cost model
For subgroup order \(n\), an ideal negation quotient reduces expected collision work from approximately \(\sqrt{\pi n/2}\) to \(\sqrt{\pi n/4}\).

Measure
\[
S\approx\sqrt2\,
\frac{c_{\rm base}}{c_{\rm quotient}}\,
\frac{1-w_{\rm quotient}}{1-w_{\rm base}},
\]
where \(c\) includes canonicalization, GPU divergence, DP handling, and communication; \(w\) is the measured fraction of updates wasted on traps or duplicates. Validate this approximation with end-to-end collision experiments. Expected DP spacing is \(1/\theta\); short high-density tests cannot substitute for production-density runs.

### Falsification
Reject deployment if coefficient invariants fail, traps produce unresolved tails, DP bias materially reduces usable collision yield, or measured wall-clock improvement is absent with confidence intervals. Specifically, overhead and wasted work exceeding the ideal \(\sqrt2\) advantage falsify the practical benefit.

### First experiment
Run matched baseline/quotient CUDA batches on the campaign curve, identical hardware and production \(\theta\), until each arm produces at least \(10^4\) DP arrivals. Report throughput, trap incidence, walk-length tails, and DP-server load; independently verify sampled trajectories on CPU.

### Frobenius extension
Separately prototype binary-field Koblitz curves: quotient by \(\{\pm\tau^i\}_{i=0}^{m-1}\), tracking coefficients through the subgroup eigenvalue of \(\tau\). Test canonicalization cost against the additional ideal \(\sqrt m\) gain. **This is not a prime-field improvement:** prime-field Frobenius acts trivially on rational points.

## Direction 53

### Construction and prior-work gate
- Audit `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for `gpu-match`, `ecbench.gae`, and `LEAD-RHO-prime-gpu-rho`: record commits, tested hypotheses, kernels, parameters, negative results, and unresolved telemetry issues. Repository contents are unavailable here; do not claim novelty until this audit is complete.
- Freeze the existing `gpu-match` semantics. CPU and GPU receive identical seeded records, table occupancy, duplicate frequency, and hit/miss distributions; compare canonicalized outputs bit-for-bit.
- Connect matching to distinguished-point Pollard rho: records contain endpoint, walk identifier, and coefficients \(a,b\), with endpoint \(aG+bQ\). Equal endpoints yield
  \[
  k=(a_1-a_2)(b_2-b_1)^{-1}\pmod n,
  \]
  when the denominator is nonzero; verify \(kG=Q\). This advances the rho implementation, not index calculus.

### Qualified measurement
On one CUDA host, pin CPU threads and NUMA placement; record GPU model, driver, clocks, power, temperatures, throttling, and ECC status. Preallocate buffers and separate cold-start from steady-state measurements.

Run randomized, interleaved CPU/GPU pairs plus CPU/CPU and GPU/GPU A/A controls, at least 30 repeats per workload. Measure wall-clock latency, kernel time, transfers, actual DRAM bytes, cache behavior, occupancy, and matching correctness. Collect intrusive profiler traces separately and quantify profiler overhead.

### Cost model
For \(R\) distinguished-point records:
\[
T_{\rm total}=T_{\rm walk}+T_{\rm pack}+T_{\rm transfer}
+T_{\rm match}+T_{\rm verify}.
\]
Estimate \(T_{\rm match}\ge\max(B_{\rm actual}/BW_{\rm sustained},I/P_{\rm sustained})\); include allocation, synchronization, and amortization explicitly. With distinguished-point probability \(\theta\), expect \(R\approx\theta W\), where rho requires \(W=O(\sqrt n)\) group operations. Report end-to-end speedup, not kernel-only acceleration.

### Falsification
Reject the acceleration claim if correctness differs, A/A variation explains the gain, transfers eliminate it, or measured traffic contradicts the proposed bottleneck. Reject cryptanalytic extrapolation if matching improvements do not materially reduce total rho cost.

### First experiment
Replay identical 1-million-record workloads across cache-resident and DRAM-resident table sizes. Require reproducible end-to-end improvement before integration into `ecbench.gae`. Then run matched toy-curve solves and increasing-budget P-256 walks with planted endpoint collisions; label these separately—short P-256 walks are not reduced-order DLP solves.

## Direction 54

### Construction
1. **Audit prerequisite:** inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for FAM-1, digit-presented \(S_3\), and both cited leads. Record commit hashes, constructions, tested parameters, negative results, and timings. Repository contents are unavailable here; prior coverage remains unverified.
2. Reuse the audited FAM-1 factor base \(\mathcal F\) and its exact membership polynomial \(M_{\mathcal F}(x)\). Do not modify the family to improve results.
3. For random targets \(R=[a]P+[b]Q\), solve
   \[
   S_3(x_1,x_2,x(R))=0,\qquad
   x_i=\sum_{j=0}^{k-1}B^jd_{ij}\pmod p,
   \]
   with \(d_{ij}\in D_{ij}\), encoded by \(\prod_{u\in D_{ij}}(d_{ij}-u)=0\). Use the previously tested digit solver and box-selection rule; rotate boxes independently of FAM-1 membership. Deduplicate representations and outputs.
4. **Only after solving**, filter candidates by \(M_{\mathcal F}(x_1)=M_{\mathcal F}(x_2)=0\). Lift coordinates and verify signs satisfying \(P_1+P_2=R\). Reject non-liftable, exceptional, and duplicate relations. This is seed generation followed by filtering—not a joint FAM-constrained solver.

### Cost model
Compare against audited pure FAM-1 relation generation using identical curves, factor bases, targets, hardware, and verification.

Measure
\[
C_{\rm rel}=
\frac{T_{\rm setup}/N+T_{\rm digit}+T_{\rm filter}+T_{\rm lift}}
{\text{new verified relations per target}}.
\]
Report peak memory, failures, digit-box coverage, solver degree, and unique relation yield. Include all unsuccessful solves.

For context, if candidates were independent uniform field elements, double membership would occur with probability approximately \((|\mathcal F|/p)^2\). Measure actual enrichment; do not assume independence. Estimate downstream matrix cost and rank growth to distinguish useful relations from redundant output.

### Falsification
Reject the direction if filtering enrichment cannot repay digit-solving overhead; if improvements disappear after deduplication or setup accounting; or if cost-per-independent-relation scaling is worse than pure FAM-1. Toy-size wins alone do not establish asymptotic improvement.

### First experiment
Run a bounded 24-bit pilot: three curve instances, 100 shared random targets each, fixed resource limits, pure FAM-1 versus digit-seeded filtering, plus uniform-coordinate controls. Freeze parameters before extending to 28/32 bits. Report paired timings and bootstrap confidence intervals; treat zero-yield runs as failures, not missing data.

## Direction 55

### Construction
1. Audit `EXP-ECTD-0cf008`, FAM-1 implementations, and both named leads in `isogeny-labs/crypto` and `crypto-autoresearcher`. Extract curve parameters, crater/floor paths, relation definitions, timings, and previously rejected variants. Repository contents are unavailable here; novelty and prior results remain unverified.
2. Fix \(E/\mathbb F_p\), prime-order subgroup \(G=\langle P\rangle\) of order \(r\), target \(Q\), and the existing FAM-1 base \(B\). From the recorded volcano, select candidate curves \(E_i\) reached by explicit isogenies \(\phi_i\) of degree coprime to \(r\). Transport \(P,Q,B\), retaining every base element’s original subgroup label.
3. Run two distinct arms:
   - **Literal transport:** use \(B_i=\phi_i(B)\) and transport the relation predicate exactly.
   - **Geometry-adapted transport:** retain \(B_i\), but apply the target curve’s native FAM-1 geometric relation-search procedure. Count only identities verified in \(G_i\); deduplicate coefficient rows and measure rank.

**Critical invariant:** literal transport preserves every subgroup relation because \(\phi_i|_G\) is an isomorphism. Any gain must come from cheaper discovery, representation, or verification—not more underlying relations. If rebuilding the base is necessary, report that separately, not as transported-base evidence.

### Cost model
Define
\[
\kappa_{\rm rel}=\frac{\text{independent usable relations}}{\text{total measured work}}.
\]
Charge curve selection, isogeny construction, transport, preprocessing, failed searches, verification, and deduplication. Report cold-start and explicitly amortized results separately. Estimate full DLP cost, including sparse linear algebra and individual-log recovery; report memory and wall-clock alongside operation counts.

### Falsification
Reject if literal transport changes exhaustive relation counts, if apparent gains disappear after duplicate/rank filtering, or if net \(\kappa_{\rm rel}\) fails to beat same-curve FAM-1 after transport costs. Reject a broader speedup claim if relation savings are outweighed by linear-algebra or recovery costs.

### First experiment
On one exhaustively tractable prime-field instance from `EXP-ECTD-0cf008`, compare the source, one crater curve, and one floor curve using identical base sizes, relation arities, and paired seeds. Exhaustively verify literal-transport invariance, then benchmark geometry-adapted discovery under equal total budgets. Select the target on training seeds and confirm on held-out seeds; scale only after a reproducible net gain.

## Direction 56

### Construction
1. **Audit before implementation:** inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for FAM-1 definitions, `LEAD-ICP-coppersmith-smallroot-semaev`, lattice configurations, and negative results. Record commit hashes and reproduce the closest baseline. Repository contents are not available here; novelty remains unverified.
2. Use the **actual FAM-1 parameterization**, not an invented surrogate. If its x-coordinate is \(\phi(t)=a(t)/b(t)\), define
   \[
   F_R(\mathbf t)=\operatorname{num}f_{m+1}
   (\phi(t_1),\ldots,\phi(t_m),x(R))\pmod p,
   \]
   for \(m=3,4\), where \(f_{m+1}\) is the Semaev summation polynomial. Restrict \(0\le t_i<B\); reject poles, invalid lifts, and duplicate points. Verify every candidate by signed elliptic-curve addition. If FAM-1 requires additional membership constraints, retain them explicitly.
3. Build modular-small-root lattices from shifts
   \[
   p^{k-j}\mathbf t^{\mathbf e}F_R^j,\qquad 0\le j\le k,
   \]
   with bounded total shift degree. Scale monomials by \(B^{|\mathbf e|}\), apply LLL/BKZ, and attempt elimination of short-vector polynomials. Sweep predetermined degree, multiplicity, and reduction-budget grids. Treat multivariate root recovery as heuristic.
4. Read Ryan’s 2025 bound precisely; identify which assumptions FAM-1 might evade. Low-degree parameterization alone is not evidence.

### Cost model
Measure preprocessing, lattice dimension/coefficient bits, reduction time, elimination time, failures, and verified relations per CPU-hour. Compare against exhaustive search and optimized meet-in-the-middle using identical factor bases. For effective signed-base size \(N\) and subgroup order \(n\), use \(N^m/(m!n)\) only as a heuristic expected representation count. Include target retries, relation-matrix rank, and eventual linear-algebra cost.

### Falsification
Reject the tested configuration if apparent gains disappear after full accounting, occur only on planted instances, fail to scale, or yield insufficient independent relations. Finite negative results do not exclude every lattice construction.

### First experiment
At 16-bit primes, exhaustively catalogue roots for random targets and both \(m\), then benchmark lattice recovery against that ground truth. Include planted FAM-1 roots, standard univariate Coppersmith positive controls, and degree/support-matched random-polynomial controls. Advance to 24–32 bits only after reproducible wins.

## Direction 57

### Construction
Work on an ordinary curve \(E_0/\mathbb F_p\) with prime-order subgroup \(G=\langle P\rangle\), odd order \(r\), and target \(Q\).

1. Select a rational \(2\)-isogeny chain
   \[
   E_0\xrightarrow{\psi_1}E_1\rightarrow\cdots\rightarrow E_L.
   \]
   Let \(\Phi_i:E_i\to E_0\) be the reversed dual chain. Its restriction to the order-\(r\) subgroup is invertible.
2. On each \(E_i\), choose a small coordinate set \(S_i\) and signed representatives
   \[
   B_i=\{R\in E_i(\mathbb F_p)[r]:x(R)\in S_i\}/\{\pm1\}.
   \]
   Transport them to \(E_0\); deduplicate \(\bigcup_i\Phi_i(B_i)\). These images—not separate curve-local logarithms—define the factor-base unknowns.
3. For random \(T=aP+bQ\), seek
   \[
   T=\sum_{j=1}^{m}\epsilon_j\Phi_{i_j}(R_j),\qquad R_j\in B_{i_j}.
   \]
   Encode this using \(E_0\)’s \(f_{m+1}\) Semaev polynomial, with transported coordinates supplied by bounded-degree isogeny graph equations. Retain intermediate variables rather than expanding degree-\(2^i\) rational maps. Exclude poles, enforce rationality and subgroup membership, recover signs, and verify every relation by group arithmetic.
4. Solve the resulting sparse linear system modulo \(r\).

### Prior-work audit
Repository contents are unavailable here; no prior-test review is claimed. Before implementation, inspect **isogeny-labs/crypto cryptanalysis** and **crypto-autoresearcher** for `LEAD-ICP-pkm-tower-algebraic-oracle`, volcano census records, transported-base experiments, and elimination benchmarks. Record tested parameters and failures; distinguish this proposal from merely relabeling one transported factor base.

### Cost model
Let \(N\) be the deduplicated base size. Measure
\[
C=C_{\rm setup}+A C_{\rm solve}+C_{\rm LA},
\]
where \(A\) is attempts needed for sufficient independent relations. Track solver memory, intermediate-variable count, solving degree, successful relations/second, and matrix rank. Generic decomposition probability is approximately \(N^m/(m!r)\), with sign conventions accounted for consistently. Thus any advantage must come from cheaper structured solving, not additional representations alone.

### Falsification
Reject practical advantage if transport causes degree/memory explosion, conductor depth provides no reproducible solving benefit, or equal-\(N\) single-curve baselines outperform the tower end-to-end.

### First experiment
On the census instances labelled **8209/131101**, verify conductor interpretation and rational edges. Sweep \(L=0,1,2,3\), initially \(m=3\), holding \(N\) fixed. Compare identical targets against direct transported-base and single-curve controls; report setup-inclusive cost per independent relation.

## Direction 58

**Construction.** Work over \(\mathbb F_p\), \(p>3\), with:
- \(E_0:y^2=x^3+b\), \(p\equiv1\pmod3\), automorphism \(\phi(x,y)=(\zeta_3x,y)\), invariant \(u=x^3\);
- \(E_{1728}:y^2=x^3+ax\), \(p\equiv1\pmod4\), automorphism \(\phi(x,y)=(-x,iy)\), invariant \(u=x^2\).

Use a prime-order subgroup stable under \(\phi\); determine \(\lambda\) with \(\phi(P)=[\lambda]P\). Define a factor base by bounded binary-digit presentations \(u=\sum_{j=0}^{t-1}2^jd_j\), \(d_j(d_j-1)=0\), retaining liftable subgroup points and storing orbit representatives.

For target \(R\), seek \(m=2,3\) orbit representatives and automorphism labels satisfying \(\sum_i\phi^{e_i}(P_i)=R\), allowing signs. Construct the elimination ideal
\[
\left\langle f_{m+1}(x_1,\ldots,x_m,x_R),\ u_i-x_i^k\right\rangle
\cap\mathbb F_p[u_1,\ldots,u_m],
\]
with \(k=3,2\). Add digit constraints. Precompute symbolic templates where feasible; solve specialized systems and verify every candidate on the curve. Record automorphism labels as coefficients \(\pm\lambda^{e_i}\) in relations. Elimination may increase degree: variable reduction alone is not evidence.

**Prior-work audit.** Repository contents are unavailable here; no review is claimed. Before experimentation, inspect both named repositories for the two referenced leads, digit encodings, Semaev elimination, special-\(j\) experiments, and negative results. Produce a tested-versus-new checklist with commit/run identifiers.

**Cost model.** Compare conventional \(x\)-digits, invariant digits, and generic-\(j\) controls using both encodings. Match field size, subgroup-order size, cofactor, and *realized factor-base cardinality*; require identical subgroup order only where available. Measure template cost, equation size, first-fall degree, solving degree, peak memory, branch/lift overhead, verified relations/second, and projected collection-plus-linear-algebra cost.

**Falsification.** Reject the advantage if lower first-fall degree does not yield lower amortized total cost, if elimination/branching erases savings, or if equivalent generic-\(j\) encodings explain the improvement.

**First experiment.** Over 20–24-bit primes, benchmark \(m=2\), then \(3\), across several curves and 100 fixed-seed targets per configuration. Independently enumerate decompositions to verify completeness and identify spurious solutions.

## Direction 59

### Construction
Repository contents are unavailable here; first audit the cited leads and both repositories for prior Miller normalizations, FAM-1 implementations, negative results, and benchmarks. Record commit IDs and reuse the existing FAM-1 decomposition predicate unchanged.

Let \(E/\mathbb F_p\) contain a prime-order subgroup \(\langle P\rangle\) of order \(r\). Fix auxiliary points \(T_1,\ldots,T_t\). Define
\[
U_j(R)=f_{r,R}(T_j),
\]
using normalized Miller functions with divisor \(r[R]-r[O]\). Reject poles and zeros. Compute features from canonical field encodings: selected bits, multiplicative characters, and cross-evaluation ratios. Freeze feature choices before testing.

Verify the normalization-dependent cocycle identity
\[
U_j(A)U_j(B)/U_j(A+B)=g_{A,B}(T_j)^r.
\]
Do not assume pairing nondegeneracy or discrete-log leakage.

Generate training points \(R=kP\), recording both selected bits of \(k\) and whether the existing FAM-1 search finds a valid decomposition within fixed budget \(B\). Train:
1. a log-bit predictor, testing the proposed mechanism;
2. a decomposition-success predictor, testing operational usefulness.

At deployment, score \(R=aP+bQ\) using **point-derived features only**, never its unknown logarithm. Search only accepted points.

### Cost model
Measure feature cost \(C_U\), baseline search cost \(C_F\), acceptance fraction \(\alpha\), baseline success probability \(s\), and accepted-point success probability \(s_A\). Compare
\[
\frac{C_U+\alpha C_F}{\alpha s_A}
\quad\text{against}\quad
\frac{C_F}{s}.
\]
Include preprocessing, amortized training, rejected-point generation, and independent-relation rank—not merely raw decomposition counts.

### Falsification
Reject practical utility if held-out total cost per independent relation does not improve. Reject the proposed leakage mechanism if log-bit prediction matches permutation controls. Also reject gains caused by scalar-encoding leakage, curve-specific overfitting, unequal search budgets, or changed factor bases. With \(\gcd(r,p-1)=1\), the rational-field Tate quotient is trivial; cocycle structure alone supplies no transfer.

### First experiment
On three small ordinary prime-field curves with nontrivial baseline FAM-1 yield, collect \(10^4\) training and \(10^4\) untouched test points each. Start with \(t=1\), a shallow classifier, and acceptance thresholds fixed on validation data. Compare against random thinning and equally costly coordinate-only filters; report bootstrap confidence intervals for end-to-end speedup.

## Direction 60

### Construction
1. **Audit before implementation.** Repository access is unavailable here; do not assume prior results. Inspect both repos for the two named leads, cover equations, explicit maps, Mumford-arithmetic tests, weak-class restrictions, failed smoothness experiments, and timings. Record commit hashes and distinguish reproduced results from conjectures.
2. Set \(K=\mathbb F_{p^6}\). Instantiate a catalog genus-3 curve \(C/K\) with an explicit separable map \(f:C\to E_K\) of degree \(\delta\). Verify the induced homomorphism
   \[
   T=\operatorname{Tr}_{K/\mathbb F_p}\circ f_*:J_C(K)\to E(\mathbb F_p).
   \]
   Evaluate \(T\) on reduced Mumford divisors by mapping support points, including multiplicities and pole corrections, then tracing.
3. Transfer each verified JV relation \(\sum_i n_iD_i=0\) to \(\sum_i n_iT(D_i)=0\). Canonicalize projected factor-base elements and measure collisions and relation rank. **Smoothness must occur upstairs:** projection alone does not create a useful small factor base.
4. For \(Q=xP\) in a prime-order subgroup of order \(r\), target relations must also connect to \(Q\). Since
   \[
   T(f^*(Q-O))=[6\delta]Q,
   \]
   require \(r\nmid6\delta\). Randomize lifted target divisors using the JV machinery; measure their smoothness separately from ordinary weak-class relations.

### Cost model
Let \(B'\) be the number of distinct projected unknowns, \(s\) relation success probability, \(c\) trial cost, and \(w\) average row weight. Estimate
\[
C_{\rm total}=C_{\rm setup}+\Theta(B'c/s)+C_{\rm transfer}
+\widetilde O(wB'^2)+C_{\rm target}.
\]
Charge extension-field arithmetic, divisor reduction, support-field evaluation, six-term traces, memory, and rejected relations explicitly. Compare against \(\Theta(\sqrt r)\) Pollard-rho work using measured operation costs.

### Falsification
Reject if the catalog lacks the required map; transfer is trivial on the target subgroup; projected equations lack sufficient rank; target lifts lose weak-class smoothness; or extrapolated total work exceeds rho. Easier relation collection alone is insufficient.

### First experiment
Choose the smallest catalog instance with feasible exhaustive checking. Verify transfer homomorphism and \(T\circ f^*=[6\delta]\); collect \(10^4\) ordinary and target-lift trials. Measure both smoothness rates, projected collisions, sparse rank modulo \(r\), and timings; attempt one complete toy DLP.

## Direction 61

### Construction and audit
- First inspect `LEAD-TRF-odd-char-descent-smith-quartic`, `LEAD-ICP-coincidence-harvest-structured-base`, and FAM-1 implementations/results in `isogeny-labs/crypto`, `cryptanalysis`, and `crypto-autoresearcher`. Record tested parameters, negative results, and relation-cost baselines. **These repositories are not available here; this review remains a prerequisite, not a completed claim.**
- Extract Smith’s exact hypotheses and maps from Propositions 2/4. An elliptic curve cannot be isogenous to a genus-3 Jacobian: require an explicit embedding \(\iota:\langle P\rangle\hookrightarrow A(\mathbb F_p)\) into the source abelian variety and an isogeny \(\phi:A\to J(C)\), where \(C\) is a smooth plane quartic.
- For subgroup order \(r\), verify injectivity on the target subgroup, preferably via \(r\nmid\deg\phi\). Let \(\Psi=\phi\circ\iota\). Transport the **actual** FAM-1 base \(B=\{B_i\}_{i=1}^{M}\) as divisor classes \(\widehat B_i=\Psi(B_i)\), not as presumed quartic points.

### Algorithm
For \(Q=xP\), sample known \(a,b\) and seek
\[
a\Psi(P)+b\Psi(Q)=\sum_{j=1}^{k}\epsilon_j\widehat B_{i_j}.
\]
Build a quartic-specific decomposition solver using divisor arithmetic and Riemann–Roch membership tests; use line/conic intersections only when their induced divisor-class identities are proved. Pull every relation back to the original subgroup and verify it before sparse linear algebra. Benchmark against the unchanged FAM-1 solver using identical targets, base size, and relation length.

### Cost model
Measure
\[
T=T_{\rm construction}+T_{\rm transport}
 +R\,c_{\rm attempt}/s+T_{\rm LA}+T_{\rm recovery},
\]
with success probability \(s\), rank-sufficient relation count \(R\), memory, and amortization stated separately. Compare against original-model FAM-1 and generic square-root attacks. Transport alone preserves decomposition existence; improvement must come from cheaper search or exploitable quartic structure.

### Falsification
Stop if hypotheses fail, subgroup transport is not injective, or useful quartic decompositions require an uncontrolled enlarged base. Reject the acceleration hypothesis if matched benchmarks show no improving relation-yield-per-cost trend, or rank deficiency eliminates apparent gains.

### First experiment
Choose one small admissible odd-characteristic instance permitting exhaustive checks. Certify maps and subgroup transport; transport FAM-1; compare exhaustive short-decomposition sets and measured solver costs on both models before scaling.

## Direction 62

### Construction
1. **Repository audit gate:** The repositories are not available in this conversation, so prior experiments and FAM-1’s precise definition remain unverified. Before implementation, inspect both repositories’ FAM-1 code, experiment logs, and the two named leads. Record tested parameterizations, negative results, and resource assumptions; do not claim novelty until this comparison is complete.
2. Let \(E/\mathbb F_p\) contain a prime-order subgroup of order \(n\), with \(Q=xP\). Fix factor base \(\mathcal B=\{B_1,\ldots,B_b\}\) using the audited FAM-1 construction. Enumerate its parameter domain \(U\), \(|U|=N\).
3. Reversibly implement the **actual FAM-1 relation predicate**:
   \[
   u\mapsto(a_u,c_u,\mathbf e_u),\qquad
   a_uP+c_uQ=\sum_i e_{u,i}B_i.
   \]
   Mark only valid, fully verified decompositions. Include decomposition finding—not merely verification—in the oracle cost. Uncompute workspace after phase marking.
4. Use amplitude amplification to harvest relations, measuring accepted parameters. Collect enough independent rows to find \(\boldsymbol\lambda^\top E=0\), with \(\boldsymbol\lambda^\top\mathbf c\ne0\), then recover
   \[
   x=-\frac{\boldsymbol\lambda^\top\mathbf a}
            {\boldsymbol\lambda^\top\mathbf c}\pmod n.
   \]
   Account explicitly for duplicate suppression and failed-rank batches.

### Cost model
Define \(S\) as one classical subgroup scalar multiplication. Report separately quantum queries, logical gates/depth, qubits, and classical \(S\)-cost; any combined \(S\)-equivalent total requires an explicit conversion assumption.

For \(R\) required distinct relations and remaining marked counts \(M_j\), estimate
\[
Q_{\rm search}\approx\sum_{j=0}^{R-1}\frac{\pi}{4}\sqrt{N/M_j}.
\]
Charge oracle arithmetic, coherent factor-base access, exclusion bookkeeping, verification, preprocessing, and sparse linear algebra. Assume no free QRAM. Compare with classical FAM-1 and Pollard rho under matched resource conventions.

### Falsification
Reject the advantage if reversible decomposition dominates search savings; usable relations are too rare or rank-deficient; memory/access costs erase savings; or optimized end-to-end scaling fails to improve the relevant classical baseline.

### First experiment
On several small prime-field curves, exhaustively enumerate the audited FAM-1 domain. Measure acceptance density, collisions, row rank, and classical predicate cost. Compile one reversible oracle and estimate its resources. Extrapolate only after these measurements; a quantum device is unnecessary initially.

## Direction 63

### Construction / algorithm
1. **Audit before coding:** inspect EXP-ECTD-0cf008, LEAD-EXO-ml-learned-models, and FAM-1 relation-generation code in both repositories; inventory prior predictors, negative results, feature definitions, and timing conventions. Repository contents are unavailable here, so prior coverage and the meaning of logged \(\kappa_{\rm rel}\) remain unverified.
2. Retain the existing FAM-1 seed-to-candidate map and relation verifier unchanged. Build examples \((E,Q,s,x,y,t)\): curve, target, seed, cheap pre-search features, independently verified relation-success indicator, and measured generation/verification time. Include failed seeds and crater/floor metadata.
3. Resolve an identification issue: **\((E,Q)\) alone cannot rank seeds for the same target.** Train \(f(E,Q,s,x)\) to estimate success probability and expected evaluation cost. Treat logged \(\kappa_{\rm rel}\) as an auxiliary target only after confirming its definition.
4. Start with gradient-boosted trees. Permit only features computable before candidate evaluation; exclude known target scalars, post-search statistics, and crater/floor labels unavailable in deployment.
5. Generate seed batches, score them, and evaluate candidates in descending predicted success-per-cost order. Reserve 10% of evaluations for uniform exploration. Verify and deduplicate every relation.

### Cost model
For \(R\) usable, independent relations, measure
\[
T_{\rm ML}=T_{\rm data}+T_{\rm train}
+M(c_{\rm feature}+c_{\rm score})+Kc_{\rm evaluate}+T_{\rm LA},
\]
where \(M\) seeds are scored and \(K\) evaluated. Compare with uniform sampling through the **same** generator, verifier, and linear-algebra pipeline. Report cold-start and amortized costs separately. Count duplicate/dependent relations, memory, and feature extraction—not merely classifier accuracy. Explicitly calculate the number of future targets required to recover training cost.

### Falsification
Reject practical usefulness if gains disappear with curve-family/target-grouped splits, depend on unavailable labels, or fail to reduce held-out wall-clock time at equal relation rank and solve success. Reject a scaling claim if gains vanish as field size increases.

### First experiment
On audited EXP-ECTD-0cf008 data, use curve-grouped training/validation/test splits and a prospective, untouched seed pool. Compare uniform sampling, a cheap handcrafted ranking, and learned ranking under identical budgets across crater/floor strata. Pre-register a ≥20% end-to-end speedup threshold, paired confidence intervals, and replication on unseen larger-field curves before expanding the search.

## Direction 64

### Construction
Treat FAM-1 as the existing seeded relation generator; preserve its factor base, acceptance predicate, and relation encoding.

1. Generate \(r\) valid FAM-1 seed increments \(D_i\), each carrying its exact algebraic label. Define the baseline walk
   \[
   X_{t+1}=X_t+D_{h(X_t)},\qquad h:E(\mathbb F_p)\to\{1,\ldots,r\}.
   \]
   Accumulate labels exactly; never treat a tag collision as a relation.
2. Implement tag-tracing blocks of length \(b\): a cheap coordinate-derived tag predicts partition choices, while cached aggregate increments defer full point additions. Tags are **not** assumed homomorphic. Reconstruct and verify every predicted partition choice before accepting a block; replay from its starting point after any mismatch.
3. Apply the unchanged FAM-1 acceptance test to verified candidates. If intermediate candidates must be inspected, charge their reconstruction explicitly. Deduplicate relations and measure their incremental rank.
4. Compare uniform partitioning with deliberately concentrated partitioning, holding seed sets and restart policy fixed. Measure empirical successor frequencies, collision rates, cycle lengths, and useful-relation yield. Partition imbalance alone is not evidence of beneficial in-degree concentration.

### Prior-work audit
The repositories are not available in this conversation, so prior results cannot be claimed reviewed. Before implementation, inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for FAM-1, both named LEAD directions, tag tracing, caching, and failed concentration experiments. Record commit IDs, configurations, negative results, and which mechanisms this experiment actually changes.

### Cost model
Primary metric:
\[
C_{\rm useful}=
\frac{\text{setup+tagging+table lookup+EC arithmetic+verification+replay+deduplication time}}
{\text{new independent accepted relations}}.
\]
Also report memory, field operations, prediction accuracy, block survival probability, and total projected relation-collection plus linear-algebra cost. Compare against optimized untraced FAM-1 and conventional rho; faster collisions alone do not establish index-calculus progress.

### Falsification
Reject the direction if replay or intermediate inspection eliminates arithmetic savings; concentration mostly produces cycles or dependent relations; gains disappear after setup/memory accounting; or speedup deteriorates across increasing field sizes.

### First experiment
On three toy prime-field curves permitting independent correctness checks, run paired-seed trials for baseline, tracing-only, concentration-only, and combined variants. Sweep \(r\in\{8,16,32\}\), \(b\in\{2,4,8\}\). Require identical verified walk semantics and report confidence intervals for cost per independent relation before scaling.

## Direction 65

### Construction
- **Repository prerequisite:** I cannot access the named repositories here. Before implementation, inspect both leads, the exact FAM-1 constructor, prior negative results, and existing κ_rel accounting; record commit hashes. Do not substitute a new family for repository-defined FAM-1.
- Wrap the existing FAM-1 transition \(T_\theta\). At each canonicalized walk state \(X\), derive \(B\in\{1,2,4,8\}\) admissible parameter seeds deterministically:
  \[
  \theta_j=\mathrm{SeedToFAM1}(H(\text{run salt},X,j)).
  \]
  Compute every candidate \(Y_j=T_{\theta_j}(X)\), including its coefficient/representation update.
- Construct a **frozen indegree-sketch scorer** from an independent pilot set: sample states, enumerate their candidates, and count candidate endpoints in hash buckets. Score \(Y_j\) by its bucket count; select the highest score, breaking ties by \(j\). Freeze scoring before production so the transition remains deterministic.
- Preserve the existing structured-base coincidence harvester and relation verification. Reject trivial relations and count only independent, verified relations.
- Controls: original FAM-1; random selection among the same \(B\) candidates; best-of-\(B\) with shuffled sketch scores. These separate selection benefit from extra sampling and sketch artifacts.

### Cost model
Report repository-defined κ_rel unchanged, plus
\[
C_{\rm rel}=
\frac{C_{\rm pilot}+C_{\rm candidate\ evaluations}+C_{\rm scoring}
+C_{\rm harvesting}+C_{\rm verification}}
{\#\text{ independent verified relations}}.
\]
Include rejected candidates, hash operations, memory, wall-clock time, and amortization assumptions. Report both transition-count and full-cost κ_rel ratios; fewer selected steps alone is not improvement. Separately measure cycle lengths, walk merging, and relation-rank yield.

### Falsification
Reject the direction if full-cost κ_rel fails to improve over baseline with paired confidence intervals; gains vanish under independent pilot/production salts; shuffled scoring performs equally well; or increased collisions predominantly produce short cycles, duplicate relations, or rank deficiency. Indegree concentration is not evidence of useful relation yield by itself.

### First experiment
At 24 bits, run 30 paired salts with identical curves, bases, starting states, and total budgets across all controls and \(B\) values. Sweep pilot expenditure over 1%, 5%, and 10% of baseline budget. Predeclare full-cost κ_rel as primary. Advance only surviving configurations to held-out 28- and 32-bit instances, without retuning.

## Direction 66

### Construction
1. **Repository gate:** Before implementation, inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `EXP-GRUMPY-eb8675`, both named parent leads, and FAM-1. Record commit IDs, seed enumeration, relation predicate, timings, and negative results. These repositories are not accessible here; prior-test coverage remains unverified.
2. Freeze the existing FAM-1 generator as a deterministic function
   \[
   G(E,\mathcal B,s)\rightarrow\{\text{verified relation},\bot\},
   \]
   including its original factor base, seed domain, and acceptance rules. Change only scheduling.
3. Implement the referenced exhaustive ladder **exactly as recovered**, storing every seed’s outcome, relation fingerprint, runtime, and pre-evaluation features. Features must be available before relation generation: seed coordinates, ladder position, and existing FAM-1 structural descriptors.
4. On training instances, use a fixed-capacity, uniformly sampled reservoir of these records to fit a deterministic success-probability estimate \(\hat p(s)\) and cost estimate \(\hat c(s)\). Compile a complete permutation of the seed domain ordered by \(\hat p(s)/\hat c(s)\), with seeded tie-breaking. Never discard seeds.
5. Evaluate this frozen schedule on unseen instances against uniform random permutations and the unmodified exhaustive ladder. Deduplicate and algebraically verify all relations.

### Cost model
For a target of \(R\) usable relations, measure
\[
T_R=T_{\rm offline}/A+T_{\rm features}+T_{\rm scheduling}
+\sum_{i\leq N_R}T_G(s_i)+T_{\rm verification},
\]
where \(A\) is the explicitly justified number of instances sharing the compiled schedule. Report cold-start \(A=1\), plausible amortization, peak RAM, stored bytes, field operations, and wall time. Also measure matrix rank and eventual solve cost: more duplicate or dependent relations do not count as progress.

### Falsification
Reject the practical hypothesis if held-out end-to-end speedup disappears after compilation/storage costs, confidence intervals include parity, or improvement requires same-instance outcome leakage. Reject transferability if gains vanish across curves or field sizes. Exhaustive completion visits the same seeds; any gain must concern time-to-target, not total relation yield.

### First experiment
Choose the smallest archived FAM-1 regime permitting full enumeration and a nontrivial relation yield. Split independent instances into training, validation, and untouched test sets. Compare paired time-to-\(R\) curves across at least 30 test instances; report bootstrap confidence intervals and cold-start break-even.

## Direction 67

### Construction
Repository contents are unavailable here; prior results and FAM-1’s exact implementation remain unverified. First inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for `LEAD-RHO-lhw-*`, `LEAD-RHO-lhw-preprocessing-frontier`, `LEAD-ICP-coincidence-harvest-structured-base`, and FAM-1. Extract code, parameters, negative results, and preprocessing accounting; reproduce the closest baseline before claiming novelty.

Use the existing FAM-1 implementation unchanged except for its seed-exponent sampler. For \(E/\mathbb F_p\), subgroup generator \(P\) of prime order \(n\), and \(L=\lceil\log_2 n\rceil\), sample uniformly from
\[
S_h=\{e:1\le e<n,\ \operatorname{HW}(e)=h\}.
\]
Implement by uniformly selecting \(h\) distinct positions among \(L\) bits and rejecting integers \(\ge n\). Deduplicate exponents. Sweep \(h\in\{2,3,4,6,8\}\), plus uniform seeds and bit-length-matched controls.

Feed \(e\) into the original FAM-1 seed interface, retaining its factor base, smoothness criterion, and relation verification. Do not substitute a new meaning for “FAM-1.” Record seed-point construction costs separately; optionally reuse precomputed \([2^i]P\). Count verified, linearly independent relations—not merely smooth candidates.

### Cost model
For each sampler measure
\[
T_{\rm solve}=T_{\rm pre}+N_{\rm trials}t_{\rm trial}
+T_{\rm rank}+T_{\rm LA}+T_{\rm descent}.
\]
Include seed generation, rejection, deduplication, point arithmetic, smoothness testing, memory, and failed trials. Estimate usable yield \(q_{\rm ind}\); report time per independent relation and finite-pool exhaustion. Price preprocessing both cold-start and amortized across explicitly stated numbers of targets sharing the curve and factor base. Plot the time–memory–reuse Pareto frontier.

### Falsification
Reject the direction if any apparent smoothness advantage disappears under matched controls, produces dependent relations, vanishes across curves, or cannot repay preprocessing before exhausting \(S_h\). Faster sparse scalar multiplication alone is not evidence of higher smoothness. Treat small-field gains as provisional unless scaling supports them.

### First experiment
On three reproducible, tractable prime-field instances, freeze FAM-1 parameters and compare every sampler using up to \(10^5\) distinct seeds each, capped by pool size. Randomize execution order; publish confidence intervals for smoothness and independent-relation yield, alongside cold-start wall time. Advance only variants improving total projected solve cost.

## Direction 68

### Construction and prior-work gate
- Review `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` records for **FAM-1**, **H-EWALK-29cb90**, and both named parent leads. Extract the actual seed map, equivalence definition, bound assumptions, failed experiments, and measured costs into a comparison table with commit references. Repository contents are unavailable here; do not assume these definitions or claim novelty before this review.
- Let \(S\) be the documented FAM-1 seed space and \(R(s)\) its relation-search output. For prime curve order \(N\), choose small subgroups \(H\le(\mathbb Z/N)^\*\), initially of orders \(2,4,8,16\) where available.
- Specify and verify a seed action \(T_h\), satisfying \(T_aT_b=T_{ab}\). Multiplication \(s\mapsto hs\bmod N\) is permissible only if it preserves valid FAM-1 seeds.
- Define \(c(s)=\min_{h\in H}\operatorname{encode}(T_hs)\). Establish exactly how relations transport between orbit members, including coefficient changes. Seed equivalence alone is insufficient: prove it preserves the relation event, or quantify its failure.
- Implement exhaustive canonicalisation first; optimise only after correctness. Sample distinct canonical representatives, preserving the intended orbit distribution. Account for stabilisers and nonuniform orbit sizes.

### Cost model
Measure seed generation, canonicalisation, relation testing, duplicate detection, memory, and linear algebra separately. Use
\[
\kappa_{\rm rel}=
\frac{\text{independent usable relations per second, quotient}}
{\text{independent usable relations per second, baseline}}.
\]
Also report total time to a fixed relation-matrix rank. An \(h\)-fold reduction in seed count is **not** an \(h\)-fold speedup: relation multiplicity, canonicalisation, and sampling overhead must enter the estimate. Substitute measured quantities into H-EWALK-29cb90 only after checking every assumption.

### Falsification
Reject the proposed equivalence if transport fails. Reject practical benefit if quotienting removes distinct useful relations, biases sampling adversely, or gives \(\kappa_{\rm rel}\le1\) within uncertainty. Reject extrapolation if predicted gain disappears with increasing field size.

### First experiment
On the smallest nontrivial, exhaustively enumerable FAM-1 instance, enumerate seeds and \(H\)-orbits; record stabilisers, relation outcomes, transported coefficients, and matrix rank. Compare baseline versus quotient under equal wall-clock budgets and repeated runs, before attempting larger fields.

## Direction 69

**Scope.** The named leads, EXP-ECTD-0cf008, and repositories are unavailable here; prior-test coverage remains unverified. Before implementation, inspect their code, logs, and negative results for digit encodings, solving-degree measurements, transported-factor overlap, and rank accounting.

**Construction.**
1. Select ordinary \(E_0/\mathbb F_p\), a prime-order subgroup \(G_0=\langle P\rangle\) of order \(r\), and target \(Q\). Choose a small volcano prime \(\ell\ne r\); construct rational isogeny paths from crater to floor. Record each composite \(\psi_v:E_0\to E_v\), degree \(D_v\), and dual.
2. At every selected level define digit factor bases
   \[
   B_v=\{R\in G_v:x(R)=c_v+\sum_{j\in J_v}2^jd_j,\ d_j\in\{0,1\}\}.
   \]
   Require canonical integer coordinates below \(p\). Enumerate candidates, lift square roots, and test subgroup membership. Tune \(|J_v|\) for comparable base sizes.
3. For random \(T=aP+bQ\), solve
   \[
   R_1+\cdots+R_m=\psi_v(T),\quad R_i\in B_v,
   \]
   using digit-augmented summation-polynomial systems. Saturate denominators, validate every solution by group arithmetic, and record exceptional-case exclusions.
4. Normalize factors into \(G_0\) using
   \[
   N_v(R)=[D_v^{-1}\bmod r]\widehat\psi_v(R).
   \]
   Then \(\sum_iN_v(R_i)=aP+bQ\). Deduplicate normalized factors globally. “Transport charge” means explicitly counting each new column, normalization operation, and dependent row—not treating transported relations as free information.

**Cost model.** Measure total digit-base enumeration, isogeny construction, polynomial solving, normalization, storage, and sparse linear algebra. Report solving degree, peak memory, validated relations/second, distinct normalized columns, and incremental rank over \(\mathbb F_r\). Estimate completion cost from rank growth and matrix dimensions; compare against single-level digit bases, identical-budget multibase sampling without isogenies, and Pollard rho.

**Falsification.** Reject the advantage if matched-budget trials show no lower projected end-to-end cost: solving degree does not improve, transport produces mostly duplicate/dependent rows, or extra columns and linear algebra erase relation-generation gains. Any asymptotic claim requires scaling evidence.

**First experiment.** After auditing prior artifacts, use several small ordinary prime-field curves with verified rational crater-to-floor paths. Hold \(m\), total base size, hardware, and solver budget fixed; compare crater-only, floor-only, and combined-level collection. Measure rank gained per CPU-second and projected completion cost before attempting larger fields.

## Direction 70

**Prior-work gate.** Repository contents are unavailable here; novelty is unverified. Before implementation, inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for both named leads, volcano censuses, adjoint-witness experiments, negative results, and parameter logs. Record tested constructions and reject equivalent variants.

**Exact construction.**
1. Choose an ordinary \(E/\mathbb F_p\), prime-order subgroup \(G\) of order \(r\), and small volcano prime \(\ell\ne p,r\). Census a bounded rational \(\ell\)-isogeny neighborhood; select a rooted spanning tree.
2. For each vertex \(v\), define \(\tau_v:E_v\to E\) by composing dual tree isogenies. Select factor-base points in the \(r\)-torsion subgroup, deliberately including edge-matched pairs \(B_u=\phi(B_v)\).
3. For each tree edge \(\phi:E_v\to E_u\),
   \[
   \tau_u(B_u)=[\ell]\tau_v(B_v).
   \]
   Thus \(e_{u,B_u}-\ell e_{v,B_v}\) is an explicit integer relation. Form their lattice \(L_0\); verify every generator by group arithmetic. Do not assume non-tree edges satisfy this identity.
4. Define \(F(a)=\sum a_{v,B}\tau_v(B)\). Reduce coefficient vectors modulo \(L_0\), then enumerate bounded-weight quotient representatives. Hash \(F(a)\); collisions yield relations \(a-b\) outside the known lattice. Add columns \(P,Q\), where \(Q=[x]P\), and collect enough independent relations modulo \(r\) to recover \(x\).
5. Compare ordinary enumeration against HNF quotient reduction and LLL/BKZ-assisted enumeration under identical memory budgets.

**Cost model.** Measure census/isogeny costs, factor-base size \(M\), lattice preprocessing, coefficient growth, group operations, memory, and independent—not total—relations. With \(N\) approximately uniform evaluated representatives, expect roughly \(N^2/(2r)\) collisions. Volcano relations alone cannot improve this birthday exponent; any benefit must improve usable-relation throughput or solve cost.

**Falsification.** Reject if gains disappear after deduplicating transported points; relations add no rank beyond \(L_0\); reduction overhead exceeds savings; or matched controls show no reproducible end-to-end improvement.

**First experiment.** Use several ordinary curves with 28–36-bit subgroup orders and nontrivial \(2\)- or \(3\)-volcano neighborhoods. Compare matched-point, random-point, and single-curve controls with equal effective column counts. Plot independent relations per second and total recovery time, charging preprocessing fully.

## Direction 71

### Construction
Let \(E_0/\mathbb F_p\) contain a prime-order subgroup \(H_0=\langle G\rangle\) of order \(r\). Build a chain of small-degree isogenies \(\phi_i:E_{i-1}\to E_i\), with degrees coprime to \(r\), and set \(T_i=\phi_i\circ\cdots\circ\phi_1\).

Choose a common structured set \(S\subset\mathbb F_p\), \(|S|=B\). Define
\[
\mathcal B_i=\{P\in H_0:x(T_i(P))\in S\},\qquad
\mathcal B=\bigcup_{i=0}^{k}\mathcal B_i.
\]
Deduplicate transported points; use consistent sign conventions.

Write \(x(T_i(P))=N_i(x(P))/D_i(x(P))\). For
\(F_S(Z)=\prod_{s\in S}(Z-s)\), membership is
\[
M_i(X)=D_i(X)^B F_S(N_i(X)/D_i(X))=0,
\]
excluding poles. Union membership is \(\prod_iM_i(X)=0\).

Seek relations \(aG+bQ=\sum_{j=1}^{m}P_j\), with each \(P_j\in\mathcal B\). Compare explicit curve-label enumeration against product-polynomial membership. Compile shared \(F_S\) coefficients, quotient/remainder computations, and Graeffe stages where algebraically reusable. Identical coefficients at different inputs **do not automatically imply reusable intermediate values**.

### Prior-work gate
Repository contents are unavailable here. Before implementation, inspect both named repositories for the two cited leads, isogeny-transport experiments, negative results, and benchmark code. Record commit-linked overlap and distinguish genuinely new optimizations from previously rejected ones.

### Cost model
Measure
\[
C_{\rm total}=C_{\rm setup}+R\,C_{\rm relation}+C_{\rm linear\ algebra},
\]
where \(R\) is the relations required by the **expanded** factor base. Track effective union size, overlap, relation yield, solver degree, monomial count, peak memory, and matrix sparsity. Include isogeny evaluation and factor-coordinate recovery. Naively, \(\deg M_i\) grows like \(B\deg T_i\).

Baseline against single-curve constructions at both equal factor-base size and equal memory—not merely equal \(B\).

### Falsification
Reject if sharing provides no amortized savings, transported bases overlap excessively, degree growth overwhelms yield, or increased matrix dimension eliminates relation-generation gains.

### First experiment
On small prime fields with enumerable subgroups, test chains of lengths \(0,1,2,4\) using degree-\(2\) or degree-\(3\) isogenies. Compare independent membership circuits, shared compilation, and union circuits. Exhaustively verify membership and relations; measure end-to-end time across increasing field sizes before extrapolating.

## Direction 72

**Hypothesis.** Special-\(j\) automorphism folding reduces relation-solving cost after 2-isogeny transport—not merely relation counts. Repository access is unavailable here; prior-work review remains a prerequisite, not a completed claim.

**Prior-work gate.** In `isogeny-labs/crypto` and `crypto-autoresearcher`, locate both named leads and their experiments. Extract curves, factor bases, polynomial generators, saturation rules, term orders, rank measurements, failures, and seeds. Reproduce the closest baseline before adding this variant.

**Exact construction.**
- Choose primes \(p\equiv1\pmod{12}\), excluding bad characteristics. Use \(E_0:y^2=x^3+1\) and \(E_{1728}:y^2=x^3-x\); enumerate their rational order-two kernels \(K\) and construct Vélu maps \(\phi:E\to E'=E/K\).
- Explicitly test descent: an automorphism \(\alpha\) induces \(\alpha'\) with \(\phi\alpha=\alpha'\phi\) exactly when \(\alpha(K)=K\). The order-three \(j=0\) symmetry permutes the three kernels; the order-four \(j=1728\) symmetry fixes one. These provide negative and positive controls.
- Build three-point summation-polynomial systems \(f_3(x_1,x_2,x_3)=0\), with identical factor-base constraints across comparisons. Transport using equations \(u_i=\phi_x(x_i)\), clear denominators, and saturate away poles. Retain lift variables initially; separately measure elimination cost.
- Compare ordinary systems, source-folded systems, transported systems, and transported systems folded only by verified descended automorphisms. For non-descending symmetry, test a correspondence across the three quotient curves, explicitly charging branch overhead.
- Verify every recovered relation by elliptic-curve group arithmetic; record sign/lift ambiguities and multiplicities.

**Cost model.** Measure relation yield per trial, distinct relations, Macaulay rows/columns/rank/nullity at each degree, degree of regularity, nonzeros, field operations, wall time, and peak memory. Include transport, saturation, elimination, unfolding, and final sparse linear algebra. Compare estimated total work per solved logarithm, not rank alone.

**Falsification.** Reject the advantage if folding loses valid relations, rank reductions merely reflect fewer variables/equations, or transport and branch overhead erase any solving gain across increasing sizes.

**First experiment.** At \(p=1009\), enumerate all six kernels; symbolically verify descent, then compute matched degree-by-degree Macaulay profiles for three-point systems using fixed-seed, automorphism-stable factor bases. Repeat across seeds before scaling.

## Direction 73

**Hypothesis.** Searching an ordinary \(\mathbb F_p\)-isogeny class yields curves with better FAM-1 relation geometry, enough to repay search, isogeny evaluation, and linear algebra. The simulation lemma predicts no intrinsic advantage when transported factor bases are allowed; any observed gain must identify a restricted representation or implementation advantage.

**Repository gate.** The repositories are unavailable here, so prior experiments cannot be verified. Before implementation, inspect both named repositories for the two cited leads, the exact FAM-1 definition, negative results, parameters, and timings. Record commit/file references; reuse their predicate and baseline rather than silently redefining FAM-1.

**Construction.**
1. Choose an ordinary curve \(E/\mathbb F_p\), prime-order subgroup \(G=\langle P\rangle\) of order \(r\), and \(Q=zP\).
2. Sample bounded class-group walks using invertible ideals of small split-prime norm, with explicit orientation and \(\mathbb F_p\)-rational isogenies. Require every degree coprime to \(r\). Record composite \(\phi:E\to E'\), degree \(d\), construction time, and evaluation cost.
3. On each \(E'\), construct its native FAM-1 factor base \(B'\subseteq\phi(G)\) under identical size and construction budgets. Score using held-out relation throughput, not geometry alone.
4. Control: pull \(B'\) back as \(B=[d^{-1}]\hat\phi(B')\). Compare native-source, native-destination, and transported-source bases with matched relation-generation code.
5. Collect relations \(\sum c_iB'_i=a\phi(P)+b\phi(Q)\); solve the resulting sparse system, including the unknown \(z\), modulo \(r\). Verify \(Q=zP\).

**Cost model.**
\[
T=T_{\rm search}+T_{\rm maps}+T_{\rm bases}+T_{\rm relations}+T_{\rm LA}.
\]
Measure wall time, field operations, peak memory, relation independence, and matrix fill-in. Charge all rejected candidates. Report single-target and explicitly amortized multi-target costs; compare against source-only FAM-1 and Pollard rho.

**Falsification.** Reject the practical advantage if held-out end-to-end gains disappear after overhead, degree growth, or rank deficiency. Equality with transported controls supports simulation; it does not establish an asymptotic theorem. Reject an asymptotic claim if improvement remains constant-factor.

**First experiment.** At \(r\approx2^{20}\), test 30 independent ordinary instances, 32 bounded walks each, fixed factor-base size, and preregistered budgets. Exhaustively recover ground-truth logs to audit every relation. Select curves on training samples; evaluate relation throughput and complete solves on fresh samples.

## Direction 74

### Construction
1. **Audit before implementation:** inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `LEAD-STR-special-j-ic-semaev`, `LEAD-ICP-coincidence-harvest-structured-base`, FAM-1 definitions, negative results, and automorphism-based bases. Record commit hashes, tested parameters, and failure modes. Repository contents were not provided here; novelty remains unverified.
2. Construct ordinary curves \(E_s/\mathbb F_p\) with \(j=0\) or \(1728\), respectively requiring \(p\equiv1\pmod3\) or \(p\equiv1\pmod4\) for rational extra automorphisms. Find generic-\(j\) curves **over the same field with exactly the same group order**, retaining a large prime subgroup of order \(r\). Verify subgroup stability under the automorphisms.
3. Freeze the audited FAM-1 family, decomposition length, and solver settings. Select seed points through its existing geometry, then close their union under the special curve’s automorphism group. Measure whether this union preserves FAM-1’s exploitable structure; do not assume it does.
4. Use one factor-base column per automorphism orbit. Compute and verify each automorphism’s subgroup scalar \(\lambda_\phi\); translate \(P=\phi(R)\) into coefficient \(\lambda_\phi\) on representative \(R\). Generate FAM-1/Semaev relations and deduplicate symmetry-equivalent equations. Relative to an existing \(\{\pm1\}\) quotient, extra orbit expansion is at most \(3\) or \(2\), not \(6\) or \(4\).

### Cost model
Define
\[
\kappa_{\rm rel}=
\frac{\text{verified relations increasing matrix rank}}
{\text{core-seconds collecting and validating relations}}.
\]
Also report attempts, decomposition probability, polynomial-system size, solving time, orbit overhead, rank saturation, memory, and sparse-linear-algebra cost. Estimate total attack cost, including setup and individual logarithms.

Compare special-\(j\) orbit FAM-1 against generic-\(j\) FAM-1 **both at equal expanded base cardinality and at equal column count**; include special-\(j\) without extra automorphisms.

### Falsification
Reject the mechanism if gains disappear after orbit deduplication, yield dependent relations, require disproportionately harder polynomial systems, or fail to reduce projected total cost. An uncharged enlargement of the factor base is not evidence of improvement.

### First experiment
After the audit, benchmark several matched-order pairs at approximately 24–32-bit fields, with identical FAM-1 settings and multiple independent seeds. Collect through rank saturation. Bootstrap paired runtime differences; proceed to larger fields only if useful-relation throughput improves reproducibly without worse matrix cost.

## Direction 75

**Hypothesis.** Within a JV weak-class instance over \(\mathbb F_{p^6}\), selecting an isomorphic model before constructing the coordinate-defined factor base reduces relation-generation cost enough to repay selection overhead. This is initially an extension-field experiment—not an attack on prime-field ECDLP without a separate reduction.

**Prior-work gate.** Repository contents were not provided, so their tested results cannot be verified here. Before implementation, inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for both lead IDs, JV implementations, model-selection experiments, negative results, and timing logs. Record commits and distinguish new factor-base choices from previously tested coordinate changes.

**Construction.**
1. Reproduce one toy weak-class instance and its existing JV sieve unchanged, including subgroup, relation arity, factor-base rule, and linear algebra.
2. For characteristic \(p>3\), enumerate admissible short-Weierstrass scalings
   \[
   E_u:y'^2=x'^3+(a/u^4)x'+b/u^6,\qquad
   (x,y)=(u^2x',u^3y').
   \]
   Include the original model; deduplicate identical induced factor bases.
3. For the baseline’s fixed subspace \(V\subset\mathbb F_{p^6}\), construct
   \(B_u=\{P'\in E_u:x(P')\in V\}\).
   Map relations back to the original subgroup. Reject models violating the JV weak-class prerequisites.
4. Pilot each candidate with identical budgets and target distributions. Rank by **verified, rank-increasing relations per second**, accounting for factor-base size. Validate the winner on fresh targets.
5. Control: transport the original factor base through each isomorphism instead of rebuilding it. This isolates coordinate-arithmetic gains from genuinely different relation sets.

**Cost model.**
\[
T_{\rm total}=T_{\rm selection}+T_{\rm setup}
+\frac{R_{\rm required}}{\rho_{\rm independent}}+T_{\rm LA}+T_{\rm descent}.
\]
Measure sieve work, elimination time, relation verification, memory, matrix dimensions/density, and descent success. Report amortization over one versus many logarithms; include unsuccessful candidates in selection cost.

**Falsification.** Reject the direction if held-out end-to-end savings disappear after selection overhead, arise solely from smaller factor bases, reproduce the transported-base control, or reflect weak-class invalidation. No prime-field claim survives without a demonstrated bridge.

**First experiment.** On one reproducible toy instance, compare 32 admissible models plus both controls across five seeds; advance only if held-out total runtime improves with uncertainty bounds excluding parity.

## Direction 76

**Construction.** Work with an ordinary \(E/\mathbb F_p\), a prime-order subgroup \(\langle P\rangle\) of order \(\ell\), and an explicitly oriented endomorphism order \(\mathcal O\). Restrict to invertible ideal classes represented by rationally computable isogenies of degree coprime to \(\ell\). Class groups act on oriented curves—not automatically on a fixed ECDLP group.

Define
\[
\operatorname{div}(f_{m,R})=m[R]-[mR]-(m-1)[O],
\qquad U_m(R;D)=f_{m,R}(D),
\]
for a fixed degree-zero divisor \(D\) with disjoint support. Compute using Miller recursion, testing small \(m\) and \(m=\ell\).

For \(\phi:E\to E'\), transport \(R\mapsto\phi R\), \(D\mapsto\phi_*D\). The function-norm identity predicts
\[
U_m(\phi R;\phi_*D)
=\prod_{T\in\ker\phi}f_{m,R}(\tau_TD),
\]
with translations taken over geometric kernel points. This is a baseline identity, **not** a class-group bridge.

Test whether the product closes efficiently:
\[
U_m(\phi R;\phi_*D)=c_{\phi,D}\,U_m(R;D)^{a_\phi},
\]
or closes on a bounded-dimensional vector of translated evaluations. Require coefficients independent of \(R\), compatible with class-group relations, and computable without ECDLP. Then test whether the resulting invariant actually distinguishes \(R=[k]P\) and yields recoverable information about \(k\).

**Prior-work audit.** Repository contents are unavailable here; no novelty or completed-review claim is justified. Before implementation, inspect both named repositories for the two lead IDs, Miller transfer defects, norm identities, orientation assumptions, and failed covariance tests. Record exact files, commits, and eliminated hypotheses.

**Cost model.** Miller evaluation costs \(O(\log m)\) extension-field operations per evaluation. Direct degree-\(d\) kernel products cost \(O(d\log m)\), plus isogeny, orientation, and extension-field overhead. Track invariant dimension, class-relation collection, linear algebra, and extraction costs. Demand an end-to-end advantage over \(O(\sqrt\ell)\) generic attacks.

**Falsification.** Reject scalar covariance if held-out points violate it; reject bounded closure if dimension grows with accumulated kernel size. Reject the bridge if outputs collapse to known pairing behavior, require unknown discrete logs, or lose all \(k\)-dependence.

**First experiment.** On small ordinary curves with nontrivial class groups, enumerate subgroup points and several low-degree ideal isogenies. Fit exponents using exhaustive toy-field logarithms, validate on held-out points, and test class-relation loops. Treat fitting solely as diagnosis—not an algorithmic ingredient.

## Direction 77

### Construction and prerequisite audit
- First inspect both repositories for `LEAD-TRF-odd-char-descent-smith-quartic` and `LEAD-STR-special-j-ic-semaev`, including failed experiments, scripts, and timing logs. Repository access is unavailable here; prior results must not be presumed.
- **Dimension gate:** an elliptic curve cannot be isogenous to a genus-3 Jacobian. Identify Smith’s actual three-dimensional input and every field-extension requirement. In particular, base-changing \(E/\mathbb F_p\) to \(\mathbb F_{p^3}\) does not create a generic Weil-restriction instance.

### Exact experiment
For odd \(p>3\), test
\[
E_0:y^2=x^3+b,\qquad E_{1728}:y^2=x^3+ax,
\]
with nonsingular parameters, alongside ordinary generic-\(j\) controls matched by field size and subgroup size.

If compatible with the audited Smith implementation:
1. Form \(A=E^3\) with its product polarization.
2. Enumerate the **135 geometric maximal isotropic subgroups** \(K\subset A[2]\); retain Frobenius-stable ones.
3. Construct the principally polarized quotient \(A/K\). Reject decomposable quotients; distinguish hyperelliptic Jacobians from smooth plane-quartic Jacobians.
4. For each quartic \(C\), explicitly verify the quotient map and transport
   \[
   P\mapsto\phi(P,O,O),\quad Q\mapsto\phi(Q,O,O).
   \]
   Verify preservation of an odd prime-order subgroup.
5. Measure quartic sparsity, coefficient arithmetic, rational automorphisms, divisor reduction, and Diem-style relation collection. Compare identical implementations and factor-base policies across curve classes.

If Smith requires different input, implement that input explicitly rather than silently substituting this construction.

### Cost model
Record
\[
T=T_{\rm construction}+N_{\rm trials}c_{\rm trial}
 +T_{\rm filtering}+T_{\rm linear\ algebra}+T_{\rm descent},
\]
plus memory and success probability. Measure relation rank **modulo the target subgroup order**, not merely relation count. Compare against Pollard rho, including special-\(j\) automorphism speedups. Generic genus-3 index-calculus estimates around \(\widetilde O(p^{4/3})\) already lose to \(\widetilde O(\sqrt{\ell})\) when \(\ell\asymp p\); demand a quantified structural improvement.

### Falsification and first run
Falsify if the construction fails, special-\(j\) yields only constant-factor simplifications, relations lack rank, or complete projected cost exceeds rho.

**First run:** enumerate all 135 kernels over several small primes, recording quotient type, map correctness, and quartic sparsity before implementing relation collection.

## Direction 78

### Construction and prior-work gate
First inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for FAM-1, `H-PAIR-62e9cc`, `LEAD-ICP-extension-field-embedding`, `LEAD-TRF-pairing-target-field-recost`, and `LEAD-ICP-coincidence-harvest-structured-base`. Extract constructions, parameters, measurements, and closure reasons; these repositories were not available here, so no review is claimed.

Reproduce FAM-1’s relation equation before assigning costs. For a prime-order subgroup \(\langle P\rangle\subset E(\mathbb F_p)\) of order \(r\), distinguish:

1. **Extension-field coordinates:** factor-base points or relation generation use \(\mathbb F_{p^k}\), but equations  
   \[
   a_i+b_ix+\sum_j c_{ij}\log_P(B_j)=0\pmod r
   \]
   still require linear algebra over \(\mathbb F_r\). Verify every \(B_j\in\langle P\rangle\); otherwise these logarithms are undefined.
2. **Multiplicative-target reduction:** construct an explicit efficiently computable homomorphism into \(\mathbb F_{p^k}^{*}\), nontrivial on \(P\), yielding \(h(Q)=h(P)^x\). For a pairing construction, provide the auxiliary torsion point and prove nondegeneracy. Require \(r\mid p^k-1\); merely extending coordinates supplies no reduction.

### Cost model
Measure
\[
T=T_{\rm setup}+T_{\rm relations}+T_{\rm filtering}
 +T_{\rm LA}+T_{\rm descent}.
\]
For \(N\) filtered unknowns and average row weight \(w\), budget sparse Wiedemann/Lanczos at approximately \(O(N^2w)\) coefficient-field operations, explicitly pricing modular arithmetic, memory traffic, and parallelism.

Apply exTNFS **only** to a justified multiplicative-target DLP. Reuse `H-PAIR-62e9cc` calibration only after matching characteristic, extension degree, tower representation, subgroup size, and special polynomial structure. Separate reusable precomputation from per-target descent. Compare total and amortized costs against Pollard rho and existing FAM-1 estimates.

### Falsification
Reject if the embedding is absent or degenerate; relations introduce unavailable logarithms; rank deficiencies prevent recovery; extension-field arithmetic was incorrectly charged as the LA coefficient field; or calibrated total cost exceeds the baseline.

### First experiment
On a toy curve with known \(x\), reproduce one complete FAM-1 recovery. Record relation yield, matrix dimensions, rank, coefficient modulus, memory, and timings. If a multiplicative reduction exists, independently solve its target DLP and compare measured cost with the tower calibration before extrapolating.

## Direction 79

### Construction
- **Repository review prerequisite:** I cannot access the named repositories here. Before implementation, extract prior Teske-trapdoor, FAM-1, Semaev-tail, and structured-base experiments into a deduplication table: construction, parameters, negative results, and unresolved hypotheses. Reuse their exact FAM-1 definition; do not interpret this plan as a completed review.
- Choose ordinary curves \(E/\mathbb F_p\), initially \(p\approx2^{20},2^{24},2^{28}\), with large prime subgroup order \(r\). Generate equal-budget collections of rational low-degree isogeny walks \(\phi:E\to E'\), with degrees coprime to \(r\).
- On each \(E'\), construct the prescribed FAM-1 factor base \(F=\{P_i\}\), size \(B\), using identical parameter-selection budgets. Controls: random bases, interval-\(x\) bases, and FAM-1 on the original curve.
- For random \(R=a\phi(P)+b\phi(Q)\), enumerate factor-base \(x_1\); solve
  \[
  f_3(x_1,x_2,x(R))=0
  \]
  for \(x_2\). Require \(x_2\) in the base, lift points, and verify signs and the group equation. Record relations
  \[
  aP+bQ=\sum_i c_iP_i'
  \]
  in target-curve coordinates, then solve the sparse system modulo \(r\).
- Select promising targets using training relations only; evaluate on fresh relations and fresh DLP instances. Retain the isogeny as the proposed trapdoor.

### Cost model
Measure
\[
C_{\rm total}=C_{\rm search}+C_\phi+N_{\rm trials}C_{\rm trial}
+C_{\rm filtering}+C_{\rm LA}.
\]
Include failed walks, factor-base construction, rank deficiency, memory, and map evaluation. Report single-instance and explicitly amortized costs. The enumerative decomposition kernel costs \(O(B)\) field operations per trial; measured success probability \(s\) gives approximately \(B/s\) work per usable relation. Compare complete recovery against optimized Pollard rho, not just relation yield.

### Falsification
Reject if held-out gains disappear; FAM-1 fails to outperform matched controls; heavy tails reflect duplicates or low-rank relations; or search/setup costs erase end-to-end savings. A secret isogeny alone provides no hardness gap: an efficient known isogeny transports the DLP.

### First experiment
At \(p\approx2^{20}\), test 256 walks, three base sizes, and fixed training/validation budgets. Measure decomposition-rate tails, distinct-relation rank, and total recovery time before scaling.

## Direction 80

### Construction
- **Repository-review prerequisite:** inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for both named leads, FAM-1 definitions, implementations, and negative results. Record commit hashes and reproduce baselines before claiming novelty. Those repositories were not accessible here; this plan does not claim that review occurred.
- Use the **descended \(n=2\) control**: \(E/\mathbb F_p\), quadratic twist \(E^d\), and
  \[
  A=\operatorname{Res}_{\mathbb F_{p^2}/\mathbb F_p}(E_{\mathbb F_{p^2}}).
  \]
  Here \(A\) is \(\mathbb F_p\)-isogenous to \(E\times E^d\), not a generic simple abelian surface.
- Initially choose \(E\) with full rational 2-torsion. Glue \(E\) and \(E^d\) along a nondegenerate anti-isometry of their 2-torsion to construct a \((2,2)\)-isogeny \(\psi:E\times E^d\to J(C)\). Verify smoothness, maps, and Frobenius polynomial.
- Transfer an odd-prime-order challenge \(Q=[s]P\) using \(R\mapsto\psi(R,0)\); verify order preservation.
- Unless repository FAM-1 specifies otherwise, test this explicit one-parameter family: choose \(P_0\in C(\mathbb F_p)\), set \(D(t)=[P_t-P_0]\), and retain points whose \(x(P_t)\) lies in a predetermined set \(S\). Store generalized Mumford coordinates.
- For randomized \(T=[a]\psi(P,0)+[b]\psi(Q,0)\), solve
  \[
  T=D(t_1)+D(t_2)
  \]
  using Mumford addition equations, elimination, and rational-root filtering. Collect relations; solve modulo the subgroup order.

### Cost model
For \(B\approx |S|\), record factor-base generation, elimination, root finding, membership tests, relation yield, memory, and sparse linear algebra. The generic-surface heuristic gives yield \(B^2/p^2\); **measure rather than assume it**, because targets lie in an elliptic subvariety. Include twist-component cancellation constraints. Compare total cost with Pollard rho, \(\widetilde O(\sqrt r)\).

### Falsification
Reject if decomposition multiplicities remain bounded and yield is generic or worse; twist cancellation destroys usable rank; elimination dominates; or measured scaling offers no advantage over rho. This falsifies the tested construction, not every FAM-1 variant.

### First experiment
At several 16–24-bit primes, exhaustively enumerate decompositions for small \(S\). Compare random Jacobian targets against transferred elliptic-subgroup targets, measuring yield, collisions, rank, and runtime before larger searches.

## Direction 81

### Construction

1. **Audit prerequisite:** I cannot access the named repositories here. Before implementation, inventory prior coordinate-statistic, digit-character, λ, PGL₂-stability, FAM-1, and structured-base experiments; record commit IDs, parameters, negative results, and reusable code. Treat novelty as unverified until this comparison is complete.
2. Freeze the repository’s exact FAM-1 seed generator and membership predicate \(M(s)\). Use exhaustive evaluation on small instances to obtain ground-truth labels; do not redefine membership using coordinate statistics.
3. For each seed’s candidate points \(P_i\), normalize \(x_i=x(P_i)\in\{0,\ldots,p-1\}\). Define
   \[
   d_{B,j}(x)=\lfloor B^j x/p\rfloor\bmod B,\qquad
   \chi_{B,j,k}(x)=e^{2\pi i k d_{B,j}(x)/B}.
   \]
   Start with \(B\in\{2,4,16\}\), \(j\in\{1,2,3\}\), and \(1\le k<B\).
4. Form features from empirical character means and selected pairwise correlations. Repeat after 16 fixed, publicly seeded Möbius maps \(g(x)=(ax+b)/(cx+d)\); handle poles explicitly. These are coordinate encodings, not assumed elliptic-curve automorphisms.
5. Fit a regularized linear score \(S_\lambda=\lambda^\top f(s)\). Accept seeds above threshold \(\tau\); run exact membership only on accepted seeds. Measure stability across held-out maps—not invariance under all PGL₂, whose transitivity can erase coordinate information.

### Cost model

Let positive prevalence be \(\pi\), true-positive rate \(r\), false-positive rate \(q\), exact-test cost \(C_M\), and feature cost \(C_F\). Accepted fraction is
\[
a=\pi r+(1-\pi)q.
\]
Cost per retained true member is \((C_F+aC_M)/(\pi r)\), versus \(C_M/\pi\) without filtering. Include seed generation, inversions, training amortization, and downstream relation yield; classification alone does not establish an ECDLP speedup.

### Falsification

Reject if held-out savings vanish, useful-relation recall falls, performance disappears under matched sampling controls, or gains fail across curves, primes, or held-out maps. Compare against cheaper coordinate summaries and shuffled-label controls.

### First experiment

Use three small prime-field curves with exhaustively labeled seed pools. Split by seed lineage, train on two curves, test once on the third. Report confidence intervals for false-positive/negative rates, wall-clock cost per useful relation, and transform stability.

## Direction 82

### Construction
1. **Audit before implementation:** locate FAM-1, `LEAD-EXO-four-list-ktree-join`, and `LEAD-ICP-coincidence-harvest-structured-base` in both repositories. Extract exact seed maps, O2 agreement-kernel definitions, previous negative results, and measured costs. Repository contents are unavailable here; this plan does not claim that review is complete.
2. On \(E/\mathbb F_p\), use subgroup order \(n\). Represent each FAM-1 seed as \((R_s,\mathbf c_s)\), where \(\mathbf c_s\) is its verified factor-base decomposition. Preserve any known \(G,Q\) coefficients.
3. Generate four disjoint seed lists of size \(N\). Seek
   \[
   R_a+R_b+R_c+R_d=T,
   \]
   yielding a verified relation after subtracting \(T\)’s symbolic representation.
4. Apply the audited O2 kernel to generate restricted pair lists \(P_{12}\) and \(P_{34}\). Store exact pair sums and provenance. Bucket left sums \(X\) and right complements \(T-Y\) using the same \(b\)-bit label; compare full points within matching buckets.
5. **Critical constraint:** coordinate truncation is not a group homomorphism. Any Wagner-style speedup requires a demonstrated, inexpensive seed-space agreement rule—not merely hashing elliptic-curve sums.

### Cost model
Let \(A(N)\) be pair-generation work and \(M_L,M_R\) retained pair counts. Define
\[
W=2^b\sum_z p_L(z)p_R(z).
\]
Expected bucket comparisons are \(C=M_LM_RW/2^b\). Measure conditional exact-match probability \(\rho\); expected verified relations are \(C\rho\).

Total cost includes seed generation, \(A(N)\), point arithmetic, sorting, comparisons, memory traffic, and downstream relation-rank contribution. Count dependent relations separately. Compare against unrestricted four-list meet-in-the-middle, matched random-seed filtering, and previously tested repository methods at equal memory.

### Falsification
Reject the direction if:
- implementing the kernel still enumerates \(\Theta(N^2)\) pairs without compensating relation yield;
- bucket agreement provides no exact-match enrichment beyond matched controls;
- heavy buckets, repeated seeds, or dependent relations erase savings;
- measured scaling fails to beat the best audited baseline.

### First experiment
After reproducing the repository kernel, run a preregistered sweep on small prime-field curves with exhaustively checkable subgroup sizes. Vary \(N,b\), kernel thresholds, and independent seed batches. Record pair-generation work, \(W\), maximum bucket occupancy, \(\rho\), relation independence, and cost per usable relation. Exhaustive enumeration must quantify kernel recall and missed solutions.

## Direction 83

### Construction
1. **Repository audit first:** inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for global-lift-height, FAM-1, and structured-base experiments. Record commit, parameters, failed assumptions, and measured costs; distinguish reproductions from new tests. Repository contents are unavailable here, so prior results are not presumed reviewed.
2. Fix \(E/\mathbb F_p\), prime-order subgroup \(\langle P\rangle\), and target \(Q\). Construct nonsingular elliptic surfaces
   \[
   \mathcal E:y^2=x^3+A(t)x+B(t),\qquad \deg A\le4\chi,\ \deg B\le6\chi,
   \]
   with fibre \(\mathcal E_{t_0}=E\). Freeze each surface **before** selecting target points.
3. Define \(T_{\rm section}(d,\chi,p;R)\) as the measured cost of finding a section specializing to \(R\). Search
   \[
   x=U/W^2,\quad y=V/W^3,\quad
   V^2=U^3+AUW^4+BW^6,
   \]
   with \(\deg W\le d,\deg U\le2(d+\chi),\deg V\le3(d+\chi)\), normalized coprime coordinates and \(W(t_0)\ne0\). Impose specialization to randomly labelled \(R=aP+bQ\). Use coefficient elimination/Gröbner solving; count failures and timeouts.
4. Feed successful sections into the repository’s frozen FAM-1 relation extractor. Specify its algebraic identity and factor-base acceptance test explicitly before testing. Accept only verified relations
   \[
   aP+bQ=\sum_i c_iF_i.
   \]
   Merely lifting \(R\), or obtaining relations solely among known scalar multiples, is not progress.

### Cost model
For factor-base size \(m\), measure
\[
C_{\rm total}=C_{\rm surface}+C_{\rm precompute}
+\frac{m+s}{\rho}(T_{\rm section}+C_{\rm extract}+C_{\rm verify})
+C_{\rm linear\ algebra},
\]
where \(\rho\) counts **independent, useful relations per attempted target**, including lift failures. Report memory, preprocessing amortization, rank, and comparison with identical FAM-1 without sections and generic square-root attacks.

### Falsification
Reject the tested regime if lift solving approaches generic DLP cost; sections cover only a biased, unusable subset; extraction gives no end-to-end gain; or relations are dependent/tautological. Target-dependent surface construction must be charged, not hidden as preprocessing.

### First experiment
Use subgroup primes of approximately 20, 24, and 28 bits, \(\chi=1\), and \(d=0,1,2\). Test 100 random targets per frozen surface, with matched time budgets and baseline extraction. Measure lift probability, runtime tails, relation yield, and rank before scaling.

## Direction 84

**Construction and audit gate.** First inspect `LEAD-EXO-hashed-factor-base-tensor-ecdl`, `LEAD-ICP-coincidence-harvest-structured-base`, FAM-1 definitions, and experiment logs in `isogeny-labs/crypto` and `crypto-autoresearcher`. These repositories were not accessible here; no prior-results review is claimed. Record previously tested constructions, failures, and the exact Akshima/Bochum contraction bound. Proceed only if its tensor representation, coefficient domain, and contraction assumptions apply—not merely its headline exponent.

1. **Exact counting instance.** For \(E/\mathbb F_p\), select factor-base abscissae
   \[
   X_B=\{x:\exists y\in\mathbb F_p,\ (x,y)\in E,\ h_s(x)<\tau\}.
   \]
   Set \(\tau\) for expected size \(B\); retain both point signs. Instantiate the repository’s *actual* FAM-1 Semaev system for target \(R\), with \(x_i\in X_B\). Do not invent a replacement FAM-1 definition. Add canonical ordering to remove permutation duplicates. Include a deterministic finite-field/group-law verification circuit checking that signed points sum to \(R\), eliminating resultant artifacts and exceptional-case errors.

2. **Tensor algorithm.** Compile arithmetic, hash membership, and verification into bounded-arity constraints. Represent each constraint by its Boolean indicator tensor; contract over all variable indices using exact integer arithmetic. Require unique auxiliary witnesses per accepted decomposition so the scalar equals the decomposition count. Recover relations by conditioning variables and repeating contractions; separately measure this extraction overhead. Compare optimized elimination orders with brute-force and meet-in-the-middle baselines.

**Cost model.** Measure
\[
T_{\rm total}=T_{\rm base}+T_{\rm compile}+T_{\rm contract}+T_{\rm extract}+T_{\rm linear\ algebra}.
\]
Report peak memory, tensor entries processed, integer bit complexity, and empirical exponent versus \(\log_2p\). Charge hash-circuit complexity and base-generation costs explicitly. Estimate relation supply using the measured count distribution, not just its mean. Counting alone is not an ECDLP speedup.

**Falsification.** Reject the direction if the audit invalidates theorem applicability; counts disagree with exhaustive enumeration; contraction width or hash constraints erase the predicted advantage; extraction costs dominate; or insufficient independent relations negate end-to-end gains.

**First experiment.** On several 16–24-bit prime-field curves, use FAM-1’s smallest supported arity and three base densities. For 100 targets per setting, compare exhaustive counts against tensor counts, then benchmark relation extraction and width scaling using identical instances and preprocessing budgets.

## Direction 85

### Construction
1. **Audit prerequisite:** inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for FAM-1, invertible-hint-subset, and structured-base coincidence experiments. Extract exact parameterizations, failed variants, datasets, and costs; repository contents are unavailable here, so prior results are not assumed.
2. Let \(G\) generate a prime-order subgroup of size \(n\) over \(\mathbb F_p\). Write the actual FAM-1 family as \(P(\theta)\), with graph label \(\ell(\theta)=\log_G P(\theta)\in\mathbb F_n\). Generate ground-truth labels **only for small experimental instances**.
3. Enumerate cheap hint maps \(H\) and predicates defining subsets \(S\), requiring \(H|_S\) to have an explicit efficient inverse—not a lookup table or discrete-log oracle. Specify how hints become elements of \(\mathbb F_n^r\); do not conflate coordinate and scalar fields.
4. Fit total-degree-\(d\) polynomials \(f\) predicting \(\ell(\theta)\) from \(H(\theta)\). Measure
\[
\rho=\Pr[\theta\in S],\qquad
A(d)=\Pr[f(H(\theta))=\ell(\theta)\mid\theta\in S].
\]
Freeze subset selection and fitting before testing. Exclude families whose construction already reveals their logs.
5. Feed verified predictions into the existing FAM-1 relation-generation pipeline; test whether they increase **independent usable relations**, not merely labeled points.

### Cost model
With \(r\) hint coordinates, \(M=\binom{r+d}{d}\) coefficients. Report training labels, fitting time, storage, hint inversion, evaluation, and verification separately. Dense fitting is roughly \(O(NM^2+M^3)\) field operations.

Expected online cost per correct prediction:
\[
\frac{C_{\rm family}+C_H+C_f}{\rho A(d)}+C_{\rm verify}.
\]
Then charge relation construction, filtering, rank losses, and sparse linear algebra. Training-label acquisition must remain in the full attack cost.

### Falsification
Reject if agreement vanishes on untouched tests; depends on hidden log leakage; requires exponential subset search; yields dependent/unusable relations; or total amortized work fails to beat relevant baselines. High \(A(d)\) alone is insufficient if \(\rho\) collapses.

### First experiment
Use three increasing toy subgroup sizes and the audited FAM-1 construction. Exhaustively label each, then split by parameter blocks into training/validation/test. Scan small \(d\) and a preregistered hint library. Compare against shuffled-label, random-subset, and constant-predictor controls; repeat on fresh curves and generators. Advance only reproducible held-out gains with favorable density and end-to-end relation throughput.

## Direction 86

**Construction.** Treat FAM-1 as the existing seed-to-point map \(F:S\to E(\mathbb F_p)\); preserve its actual seed distribution and admissibility constraints. Work in a prime-order subgroup of order \(r\), with target \(Q=xP\). Fix disjoint coordinate-projection panels \(\pi_1,\ldots,\pi_k\) on the **seed representation**, and define lossy states \(L_i(s)=\pi_i(s)\).

For scalars \(a\), seek a cheap probabilistic propagator
\[
T_{a,i}(L_i(s))\rightsquigarrow L_i(s_a),
\qquad F(s_a)=[a]F(s).
\]
The output may be a bounded candidate list or an explicitly sampled distribution. Count failure to find an admissible \(s_a\); do not condition it away. Test successive doubling first, then addition chains. Determine whether any rigidity theorem excludes only exact deterministic propagation, or also this probabilistic/list-valued interface.

Use propagated states to nominate structured-base coincidences for relation harvesting. Every nomination must be lifted to full points and verified. Lossy-state collisions alone are not relations.

**Cost model.** Measure setup, propagation, candidate-list growth, lift/verification, memory, relation yield, and linear algebra. If each nomination costs \(C\) and produces a verified independent relation with probability \(\rho\), charge at least \(C/\rho\) per relation. Include seed search, rejected lifts, duplicate relations, and preprocessing. Estimate total discrete-log cost and compare with both the unchanged relation-harvesting pipeline and generic \(O(\sqrt r)\) attacks. Reduced projection entropy is not itself a speedup.

**Falsification.**
- Propagation predicts no better than a seed-distribution-matched baseline.
- Candidate lists or lifting costs erase the filtering advantage.
- Accuracy collapses under repeated scalar steps.
- Verified relations lack independence or sufficient yield.
- The applicable rigidity theorem already forbids the proposed probabilistic interface under its actual assumptions.

**First experiment.** On several small prime-field curves, enumerate FAM-1 seeds and admissible doubling lifts. For equal-sized disjoint panels, measure \(H(L_i(s_2)\mid L_i(s))\), top-\(K\) prediction accuracy, lift multiplicity, and end-to-end cost on held-out seeds and curves. Compare against shuffled labels, marginal sampling, and direct doubling.

**Prior-work gate.** Repository contents were not supplied, so no review is claimed. Before implementation, inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for both named leads, FAM-1 definitions, rigidity proofs, tested panels, and negative results; record exact files/commits and reject duplicate experiments.

## Direction 87

**Objective.** Measure false negatives in FAM-1 screening—not claim an ECDLP speedup from artificially enriched data.

**Repository gate.** Before implementation, audit `isogeny-labs/crypto` and `crypto-autoresearcher`: locate FAM-1’s actual equations, factor-base construction, screening stages, prior planted controls, and negative results. Produce a commit-linked experiment ledger; reuse existing controls. Repository contents were not provided here, so this plan does not claim that review is complete.

**Construction.** Let \(E/\mathbb F_p\), factor base \(B\), target \(T\), and relation arity \(k\) match the audited configuration. Denote the independently evaluated FAM-1 geometric conditions by \(G\). Build three positive-control families:

1. **Unconditioned algebraic plants.** Sample \(P_1,\ldots,P_{k-1}\in B\); set \(P_k=T-\sum_{i<k}P_i\). Retain only \(P_k\in B\) and \(G(P_1,\ldots,P_k)\). Record all rejection rates; never silently enlarge \(B\).
2. **Structured coincidence plants.** Enumerate disjoint tuple pools, hash their group sums, and join complementary sums totaling \(T\). Retain independently verified \(G\)-valid relations. Stratify by repeated coordinates, orbit membership, and sum multiplicity where these are relevant to the audited geometry.
3. **Geometric stress plants.** From verified relations, enumerate only transformations proven to preserve both the relation and FAM-1 admissibility. Oversample strata near implemented screening thresholds and exceptional geometric loci. Count independent seeds separately from transformed descendants.

Validate positives using curve arithmetic and direct geometric equations—not the screening implementation. Inject blinded records at each compatible pipeline boundary. Add matched invalid controls to detect indiscriminate acceptance. Log each record’s first rejection stage.

**Cost model.** Family 1 costs approximately \(1/(\Pr[P_k\in B]\Pr[G\mid P_k\in B])\) trials per retained plant. Meet-in-the-middle enumeration costs \(O(|B|^{\lceil k/2\rceil})\) group operations and comparable worst-case storage. Report planting, oracle, and screening costs separately; include symmetry-induced effective sample-size loss.

**Falsification.** The instrumentation fails if independent verification rejects plants, injection changes pipeline behavior, or claimed coverage excludes legitimate FAM-1 strata. A claimed false-negative rate below 1% is unsupported unless its confidence bound establishes that threshold.

**First experiment.** Exhaustively enumerate a tractable toy-field instance, establish ground truth, then blindly inject 300 independent positives per family plus matched negatives. Compare stagewise rejection rates with exhaustive truth before scaling.

## Direction 88

### Construction
1. **Repository audit gate:** I cannot access the named repositories here. Before implementation, inventory their FAM-1 definitions, smoothness predicates, structured-base experiments, negative results, and quantum-resource estimates; record commit hashes and identify what this variant changes.
2. Let \(E/\mathbb F_p\) contain a prime-order subgroup \(\langle P\rangle\) of order \(n\), with target \(Q\). Freeze a factor base \(\mathcal B=\{B_1,\ldots,B_B\}\) and the repository’s exact FAM-1 parameter domain \(\Theta\).
3. Implement a reversible oracle computing the existing FAM-1 candidate \(R_\theta=a_\theta P+b_\theta Q\), then deciding whether it admits the prescribed bounded-weight decomposition
   \[
   R_\theta=\sum_i c_{\theta,i}B_i.
   \]
   Mark successful parameters, copy out the relation, and uncompute workspace. “Smoothness” means this group decomposition—not smoothness of an integer coordinate.
4. Charge the **entire decomposition procedure** to the oracle. If FAM-1 instead outputs witnesses directly, include their parameter-space size; do not assume a free existential smoothness oracle.
5. Use amplitude amplification to collect distinct relations, then classical sparse elimination modulo \(n\). Seek a row combination eliminating factor-base coefficients and yielding \(AP+BQ=0\), \(B\ne0\); return \(-A/B\bmod n\).

### Cost model
Measure fresh-relation probability \(\rho_j\) after \(j\) accepted relations. For \(R\) relations sufficient for elimination,
\[
T_Q\approx\sum_{j=0}^{R-1}\frac{C_{\mathrm{oracle}}}{\sqrt{\rho_j}}
+C_{\mathrm{readout}}+C_{\mathrm{LA}}.
\]
Report logical qubits, Toffoli count/depth, memory-access assumptions, classical storage, and rank yield. Oracle cost includes arithmetic, membership, decomposition, duplicate rejection, and uncomputation. Quantum search and LA costs are **additive**, not multiplied. Compare with classical FAM-1 and Shor under identical fault-tolerance assumptions.

### Falsification
Reject the proposed advantage if decomposition dominates the quadratic search saving; valid parameters concentrate into duplicate/dependent relations; reversible memory costs erase gains; or optimized total resources fail to beat classical FAM-1. Treat Shor competitiveness separately.

### First experiment
On several toy curves over 20–32-bit prime fields, exhaustively enumerate a bounded FAM-1 domain. Measure success density, multiplicities, decomposition runtime, and relation rank. Compile the dominant predicate into a reversible circuit and extrapolate only from measured gate counts. Stop before larger searches if oracle costs already eliminate the advantage.

## Direction 89

### Construction
- Reuse the repository’s exact FAM-1 family, relation verifier, and seed-table representation. **Repository contents are unavailable here; prior-test overlap must be checked before claiming novelty.**
- For \(E/\mathbb F_p\), work in a prime-order subgroup \(\langle P\rangle\) of order \(n\), targeting \(Q=xP\). Preserve coefficient provenance for every stored point and harvested relation.
- Operationally define \(T\) as the baseline walk-step budget and \(T_{\rm sel}\in\{0.65T,0.75T\}\) as a **single batch-reselection checkpoint**.
- Start with the unchanged FAM-1 seed table of size \(M\). During exploration, retain verified FAM-1 relations and candidate seeds derived from them. Admit a candidate only when its required coefficients/logarithms are actually known; an unsolved relation does not supply free advice.
- At the checkpoint, select \(M\) seeds from the original-plus-grown pool. Rank candidates by estimated **distinct, useful verified relations per charged evaluation**, using exploration statistics with duplicate and occupancy penalties. Freeze the table for the remaining budget.
- Use exact group equality and the original relation verifier, never advice-label coincidence alone.

### Cost model
Measure
\[
C=C_{\rm seed}+C_{\rm walk}+C_{\rm verify}+C_{\rm select}
 +C_{\rm update}+C_{\rm linear\ algebra}.
\]
Report field-operation equivalents, wall time, peak memory, distinct-relation yield, rank gain, and end-to-end successful solves. Charge all candidate construction, failed verification, scoring, sorting, and table rebuilding. Report amortized results separately, explicitly stating how many targets share preprocessing.

### Prior-test review
Search both named repositories for FAM-1, advice-table variants, coincidence harvesting, adaptive reseeding, and negative results. Record commit, configuration, seed provenance, charged costs, and outcome. Determine whether this experiment differs in checkpoint timing, candidate generation, selection rule, or accounting.

### Falsification
Reject the direction if apparent gains disappear after preprocessing/reselection costs; increased collisions do not increase independent useful relations; growth requires unknown logarithms; or selected seeds overfit exploration and fail on held-out runs. A small-instance gain alone does not establish asymptotic improvement.

### First experiment
Run paired random seeds at three feasible subgroup sizes with identical memory and total budgets: fixed table, random batch reselection, and scored reselection at both checkpoints. Use at least 30 pairs per size. Advance only if scored reselection lowers total solve cost with confidence intervals excluding no improvement and shows no worsening size trend.

## Direction 90

### Construction
- **Repository audit first:** repository contents are unavailable here; prior testing cannot be verified. Before coding, inspect `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher` for both named leads, FAM-1 implementations, benchmarks, and negative results. Record commit IDs, duplicate mechanisms, and unresolved assumptions.
- Use the existing FAM-1 seed-to-candidate map \(F(s)\) and relation predicate unchanged. Specify its actual seed domain; do not assume seeds are subgroup scalars.
- For an odd cyclic seed domain \(\mathbb Z_m\), partition seeds using a cheap reproducible tag \(j=h(s)\bmod r\), then walk
  \[
  s_{i+1}=2^{-1}(s_i+c_j)\pmod m,
  \]
  with fixed offsets \(c_j\). Maintain the exact affine trace \(s_i=A_i s_0+B_i\pmod m\). For other seed domains, require a proven domain-preserving analogue before proceeding.
- Evaluate \(F(s_i)\) normally initially. Separately implement incremental evaluation **only if the actual FAM-1 formulas imply an exact recurrence**. Seed halving does not imply cheap elliptic-curve halving.
- Deduplicate candidates and validate relations identically to baseline; use independent restarts to expose short cycles.

### Cost model
Measure
\[
T_{\rm useful}=
\frac{T_{\rm tags}+T_{\rm seed}+T_F+T_{\rm predicate}+T_{\rm dedup}+T_{\rm restart}}
{\#\text{distinct accepted relations}}.
\]
Report ns/step, ns/distinct candidate, relation yield, memory, and relation-matrix rank growth. Compare with sequential and pseudorandom plain FAM-1 enumeration under identical arithmetic, threading, and validation. Charge deferred trace materialization and batch operations fully.

A cheaper seed transition matters only if it reduces total candidate-generation cost without losing useful relation yield.

### Falsification
Reject the direction if:
- No exact, cheaper FAM-1 evaluation recurrence exists and seed arithmetic is negligible.
- Walk collisions, bias, or cycles erase transition savings.
- Accepted relations are disproportionately dependent.
- End-to-end time per useful relation fails to beat enumeration across multiple instances and seeds.

### First experiment
On a small prime-field instance where relation collection is measurable, run paired baseline/tagged-halving benchmarks with identical candidate budgets and at least ten restarts. Profile components separately; first test the unchanged evaluator to isolate traversal effects, then test any proven incremental evaluator. Publish traces and confidence intervals, including negative results.

## Direction 91

### Construction
1. **Audit before implementation:** inspect `isogeny-labs/crypto` and `crypto-autoresearcher` for FAM-1, Cheon applicability, and structured-base coincidence experiments. Record exact relation formats, costs, negative results, and commit IDs. These repositories are not available here; prior coverage cannot yet be verified.
2. Work in a prime-order subgroup \(G=\langle P\rangle\) of order \(q\) on \(E(\mathbb F_p)\), with \(Q=[x]P\). Choose \(d>1\) dividing \(q-1\).
3. Instrument FAM-1 to output relations
   \[
   [a_i]P+[b_i]Q+\sum_j[c_{ij}]R_j=O,
   \]
   including the complete construction provenance of every \(R_j\).
4. Seek known coefficients satisfying
   \[
   [x^d]P=[u]P+[v]Q+\sum_j[w_j]R_j.
   \]
   Require a derivation from FAM-1’s actual defining equations—not merely a fit at the sampled secret. Attempt sparse elimination on those equations; record every nonlinear operation, scalar disclosure, and assumed oracle.
5. If extraction succeeds, feed the auxiliary point to Cheon’s algorithm. If all available points arise solely through known-scalar linear combinations of \(P,Q\), establish the obstruction: their formal coefficients remain affine in \(x\), so generic generation of \(x^dP\) requires additional information.

### Cost model
Measure
\[
T_{\rm total}=T_{\rm relations}+T_{\rm elimination}+T_{\rm extraction}
+\widetilde O(\sqrt{q/d}+\sqrt d).
\]
Include failed relation searches, field operations, memory, preprocessing, and amortization assumptions. Compare against optimized Pollard rho, \(\Theta(\sqrt q)\), and direct DLP recovery from the same relations. Audit whether deployed subgroup orders admit useful divisors \(d\).

### Falsification
Reject the proposed advantage if extraction requires knowing \(x\), an unavailable multiplication oracle, or work comparable to rho; if relations yield only affine closure; or if auxiliary extraction is no cheaper than recovering \(x\) directly. Toy correctness alone does not establish asymptotic improvement.

### First experiment
Choose toy curves with 24–32-bit prime subgroup orders and several useful divisors \(d\mid(q-1)\). For 100 random secrets per setting, isolate a **blind extractor** receiving only public inputs and FAM-1 outputs. A separate verifier checks its output against \([x^d]P\). Log correctness, provenance, total cost, and scaling; include affine-only and random-relation controls.

## Direction 92

### Construction
1. **Audit before implementation.** Search both repositories for `FAM-1`, `LEAD-RHO-ecc2k130-iteration-function`, and `LEAD-ICP-coincidence-harvest-structured-base`; extract the actual seed decoder, v3 transition table, prior negative results, and counting conventions. Repository contents are unavailable here, so novelty and compatibility remain unverified.
2. Let the implemented FAM-1 decoder be \(D:S\to E^k\), with a documented relation predicate \(R(D(s))\). On a binary toy curve defined over \(\mathbb F_2\), construct a seed map \(\sigma\) satisfying
   \[
   D(\sigma s)=\pi^{\times k}D(s),\qquad \pi(x,y)=(x^2,y^2).
   \]
   Derive this from the decoder equations; do not assume squaring parameters suffices. Include coefficient transformations if the family is not defined over \(\mathbb F_2\).
3. Adapt the **actual v3 table walk** to valid FAM-1 seed transformations. Each table entry must specify its seed update, decoded-point effect, inverse when available, and cost. Reject updates requiring expensive inversion of \(D\).
4. Canonicalize seeds under valid \(\sigma\)-orbits; use distinguished points to find merges. Harvest only merges yielding independently checkable, nonduplicate relations over the chosen factor base—not merely equal seeds or Frobenius conjugates.

### Cost model
Measure total seed operations, field operations, decoding, canonicalization, storage, and communication. Primary metric:
\[
\frac{\text{total measured work}}{\text{rank increase of the relation matrix}}.
\]
Report orbit sizes, walk-cycle statistics, relation yield, and linear-algebra cost. Compare against identical FAM-1 harvesting without quotienting and the original table walk. A collision speedup alone is not an index-calculus improvement.

### Falsification
Reject if equivariance or closure fails; canonicalization erases orbit savings; quotienting creates short cycles; harvested relations are algebraically redundant; or end-to-end cost fails to improve.

For \(E/\mathbb F_p\), coordinate \(p\)-Frobenius is identity on rational points. Prime-field transfer therefore requires a separately demonstrated nontrivial endomorphism or seed symmetry; binary success alone does not support it.

### First experiment
On a small binary instance permitting exhaustive enumeration, verify equivariance and orbit structure, then run matched-budget baseline/quotient ablations with identical seeds. Compare **independent relations per field operation**, including all overhead, before attempting prime-field transfer.

## Direction 93

### Construction
Treat the existing FAM-1 implementation as a deterministic map \(F(s)=(R_s,a_s,b_s)\), with \(R_s=[a_s]P+[b_s]Q\). Preserve its exact definition; do not introduce a replacement family.

1. **Prior-work audit:** Inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for both named leads, FAM-1 definitions, schedules, collision filters, and negative results. Record commit IDs and distinguish genuinely untested changes. Repository contents are unavailable here, so this review remains a prerequisite.
2. For prime-order subgroups of order \(\ell\), use nested seed domains \(S_k=\{0,\ldots,2^k-1\}\subset\mathbb Z/\ell\), \(k=10,\ldots,20\), with \(\ell>2^{20}\).
3. On independent training instances, exhaustively enumerate FAM-1 outputs. Build a reservoir of output classes, multiplicities, seed features, and marginal coverage gains. Canonicalize \(R\sim-R\), adjusting coefficients accordingly.
4. Compile a deterministic seed ordering using only inexpensive, preregistered seed features. Rank feature buckets by training-estimated new canonical points per evaluation; interleave buckets greedily. No held-out group outputs may influence compilation.
5. On fresh instances, execute the compiled ordering, storing every canonical output and coefficient pair. A matching pair yields
\[
x=-(a-a')(b-b')^{-1}\pmod\ell
\]
when \(b\ne b'\); verify \([x]P=Q\).

### Cost model
Report compilation time, training evaluations, online group operations, feature overhead, hash-table probes, peak bytes, and verified-log success. Give both cold-start cost and explicitly amortized cost across instances.

Primary statistic: distinct canonical outputs versus **total charged work**. Secondary statistics: coverage-curve area, useful-collision yield, and time-to-log. Compare natural order, uniform random permutations without replacement, uniform sampling with replacement, and existing grumpy schedules.

Exhaustive endpoint coverage must match: ordering alone cannot change it.

### Falsification
Reject the direction if gains disappear on independent instances, require near-exhaustive instance-specific preprocessing, fail against uniform permutations, or vanish after charging compilation and memory. Improved coverage without increased useful-collision yield is insufficient evidence of cryptanalytic benefit.

### First experiment
At \(k=10,\ldots,16\), train on 16 instances and test on 32 fresh instances per subgroup size. Sweep prefixes \(1/64,\ldots,1\); bootstrap paired coverage and cost differences. Advance to \(2^{20}\) only after reproducible end-to-end improvement.

## Direction 94

**Construction.** Preserve FAM-1’s seed map and structured factor base \(\mathcal B=\{B_i\}\). Express each candidate relation as
\[
[a(z)]P+[b(z)]Q=\sum_i[c_i(z)]B_i,
\]
where \(Q=[d]P\), \(B_i=[\beta_i]P\), and \(P\) has prime order \(n\). Use integer lifts of coefficients. Generate FAM-1 seeds from weight-\(w\), \(L\)-bit integers, enumerating fixed-weight supports without replacement.

For \(M=2^r-1\) and \(2^r+1\), reduce these integers by folding \(r\)-bit blocks. A valid relation satisfies
\[
a+bd-\sum_i c_i\beta_i=kn.
\]
Test modular compatibility **including the wrap term \(kn\bmod M\)**. Guess only residues unavailable from public data; price every guess and every admissible wrap class. If wrap classes exhaust all residues, declare the filter vacuous. Never assume reduction modulo \(M\) is a homomorphism from the order-\(n\) group.

**Prior-work gate.** Repository contents are unavailable here, so no prior experiments have been reviewed. Before implementation, inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for both named leads, `EXP-LHW-9adf78`, FAM-1 definitions, negative results, and seed distributions; record exact commits and distinguish genuine variants from repeats.

**Cost model.** Measure seed-generation, modular-filter, group-operation, relation-verification, memory, and sparse-linear-algebra costs. Report
\[
C_{\rm useful}=
\frac{C_{\rm enumeration}+C_{\rm guesses}+C_{\rm filtering}
+C_{\rm verification}+C_{\rm linear\ algebra}}
{\text{independent useful relations}}.
\]
Charge residue hypotheses, wrap enumeration, repeated seeds, correlations, and parameter tuning. Compare against unfiltered FAM-1, structured-base coincidence harvesting, and generic rho on identical instances. Oracle residue knowledge is diagnostic only, never a deployable speedup.

**Falsification.** Reject if correct wrap accounting removes selectivity; unknown-residue search cancels savings; genuine-relation recall falls enough to erase gains; relation rank stagnates; or measured gains are explained solely by cheap seed generation rather than reduced total attack cost.

**First experiment.** On small prime-order curves allowing exhaustive ground truth, compare unfiltered, oracle-residue, and fully charged guessed-residue runs using identical seed streams. Sweep \(w,r\), and Mersenne/Fermat moduli. Record true/false survival, wrap coverage, independent relations per second, and total solution time. Continue only if charged gains persist across increasing group sizes.

## Direction 95

### Construction
- **Repository gate:** Before implementation, inspect EXP-LHW-b49bc6, its parent leads, and FAM-1 definitions in both repositories. Record tested parameters, failures, collision conventions, and checkpoint formats. Repository contents are unavailable here; this plan does not claim that review occurred.
- Freeze the existing FAM-1 factor base \(B=(P_1,\dots,P_m)\subset E(\mathbb F_p)\). A seed is a weight-\(w\) subset \(S\subset[m]\), with \(\phi(S)=\sum_{i\in S}P_i\).
- Walk on seeds: hash the canonical encoding of \(S\) to choose \(i\in S\), \(j\notin S\); set \(S'=(S\setminus\{i\})\cup\{j\}\), updating \(\phi(S')=\phi(S)-P_i+P_j\). Use independently salted walks and restart upon repeated seeds.
- Store checkpointed mappings \(\phi(S)\mapsto S\). Distinct seeds with equal images yield the verified relation \(\mathbf1_S-\mathbf1_T\). Cancel overlaps and deduplicate up to sign.
- **Do not assume rho coalescence:** equal images need not produce equal successors because transitions depend on seeds. Distinguished-point endpoints alone cannot detect arbitrary intermediate image collisions.

### Cost model
Let \(N=\binom mw\), \(q=|E(\mathbb F_p)|\), and \(\pi_x=\Pr[\phi(S)=x]\) for uniform seeds. Define \(Q_{\rm eff}=1/\sum_x\pi_x^2\).

Each step costs two group additions plus hashing/storage. Independent samples give approximately \(\binom t2/Q_{\rm eff}\) image coincidences, **before subtracting identical-seed coincidences**. Measure walk autocorrelation and distinct-seed coverage rather than assuming independent sampling.

For small exhaustive instances, checkpoint support size and multiplicities; compute \(\sum_x\binom{n_x}{2}\), the exact distinct-seed collision count. Report useful relations and incremental rank per group operation, memory byte, and wall-clock second. Include target descent costs: internal relations alone do not solve ECDLP.

### Falsification
Reject the lead if apparent gains disappear after removing repeated seeds, correlated samples, trivial/duplicate relations, or rank redundancy; if matched-memory independent sampling wins; or if relation collection plus descent cannot improve the generic square-root baseline.

### First experiment
Re-run Stage 1 on one exhaustively enumerable FAM-1 instance. Compare jump walks against uniform weight-\(w\) sampling at identical operation and memory budgets. Checkpoint coverage, exact collision counts, relation rank, and restart statistics across 20 salts; then repeat at the next larger instance.

## Direction 96

### Construction and prior-work audit
Before running experiments, inspect `isogeny-labs/crypto`, cryptanalysis notes, and `crypto-autoresearcher` for FAM-1, `LEAD-RHO-matched-rho-calibration`, and `LEAD-ICP-coincidence-harvest-structured-base`. Record commit hashes, exact relation predicates, factor-base construction, failed variants, and existing benchmarks. Repository contents are unavailable here; this plan does not claim that review is complete.

Freeze the canonical FAM-1 implementation and structured-base parameters from that audit. Do not introduce another relation-generation heuristic.

For prime-field curves with prime-order subgroups of **32, 36, 40, 44, and 48 order bits**, sample independent targets \(Q=xP\). Compare:
1. FAM-1, including structured-base setup, coincidence harvesting, relation verification, linear algebra, and target recovery.
2. A tuned Pollard-rho solver using the same arithmetic backend, hardware, threading, and equivalent engineering effort.

Use identical instances and paired seeds where meaningful. Validate every recovered scalar independently. If FAM-1 amortizes preprocessing, report both single-target and explicitly specified batch-target results.

### Cost model
Define \(N=\operatorname{ord}(P)\), not field size. Measure total cycles, wall time, peak memory, group operations, field operations, and failed/redundant relations.

For \(k\) targets, use
\[
T_F(N,k)=T_{\rm setup}+T_{\rm relations}+T_{\rm LA}
+\sum_{i=1}^{k}T_{{\rm descent},i},
\qquad
R_k(N)=\frac{T_F(N,k)}{\sum_{i=1}^{k}T_{\rho,i}}.
\]
Also report relation-generation cost separately; do not equate relations produced with discrete logarithms solved.

Fit the prespecified hypothesis \(R_k(N)=1+c/N^\beta\), with \(c,\beta>0\), using instance-level bootstrap intervals. Compare against constant-ratio and unconstrained power-law alternatives. Report rho’s observed coefficient relative to \(\sqrt N\); account explicitly for negation and parallel collision handling.

### Falsification
Reject the calibration model if held-out sizes contradict its prediction intervals, \(\beta\) is unidentifiable or nonpositive, or alternatives predict materially better. Treat incomplete solves, omitted preprocessing, unmatched rho optimizations, and memory exhaustion as failures—not speedups. A fit approaching one is **not** evidence of asymptotic improvement over rho.

### First experiment
At 32 bits, run 30 independent instances, ten targets each, with separately reported cold-start and amortized costs. Establish correctness, complete cost accounting, and paired uncertainty before extending to larger sizes.

## Direction 97

### Construction
- First inspect `isogeny-labs/crypto` cryptanalysis and `crypto-autoresearcher` for `FAM-1`, `EXP-CERTBIN-b4d29c`, design C, Bailey, and both cited leads. Extract exact canonicalisation rules, prior benchmarks, rejected variants, and certificate checks into a provenance table. **Repository contents are unavailable here; prior results must be verified, not assumed.**
- Implement a native benchmark exposing the existing design-C and Bailey canonicalisers behind identical interfaces: `canon(seed) → (representative, witness)`. Use precisely the FAM-1 equivalence relation established by the repository—not a newly assumed symmetry.
- Require independent witness verification, idempotence, and equivalent seeds mapping to the same representative. Require cross-implementation equality where the specification defines a unique representative.

### Cost model
Measure release builds with identical compiler flags, field representation, CPU affinity, and input corpus. Exclude parsing, allocation, and corpus generation from timed regions; report those separately.

For algorithm \(A\), define
\[
E_A^{Ir}=\frac{Ir_A-Ir_{\rm harness}}{Ir_{\rm fieldmul}},
\qquad
E_A^{cycles}=\frac{cycles_A-cycles_{\rm harness}}
{cycles_{\rm fieldmul}}.
\]
Benchmark field multiplication in both dependency-chain and independent-throughput modes. Callgrind instruction ratios are **instruction-equivalent costs**, not automatically cycle-equivalent costs. Also count multiplications, squarings, inversions, branches, and memory accesses.

Separate canonicalisation frequency explicitly:
\[
C_{\rm step}=C_{\rm walk}+qC_{\rm canon}+C_{\rm bookkeeping}.
\]
For seed-only canonicalisation, \(q=1/L\), where \(L\) is average walk length; for per-step canonicalisation, \(q=1\). Include witness construction and checking at their actual frequencies.

For coincidence harvesting, report total native cost per **accepted, nonduplicate relation**, including rejection and deduplication—not merely cost per seed.

### Falsification
Reject correctness upon any invalid witness, inconsistent representative, or lost required seed coverage. Reject the performance hypothesis if design C’s cycle advantage disappears on held-out seeds, or canonicalisation overhead exceeds measured downstream savings. Cheaper canonicalisation alone does not establish an ECDLP improvement.

### First experiment
At one repository-standard prime and FAM-1 parameter set, benchmark both implementations on \(2^{16}\) reproducibly generated seeds plus adversarial boundary cases. Collect paired Callgrind counts and repeated native timings, publish confidence intervals and mismatch logs, then replay identical seeds through the existing relation-harvesting pipeline to test end-to-end cost per accepted relation.

## Direction 98

### Construction
Repository contents and definitions of FAM-1/H-EWALK-29cb90 were not provided; prior-test coverage and novelty remain unverified.

1. Extract the exact FAM-1 map \(F:S\to G\), where \(G=\langle P\rangle\) has prime order \(N\) over \(\mathbb F_p\). Audit both repositories for seed symmetries, scalar-orbit canonicalization, invariant searches, and rejected quotient walks.
2. Choose small subgroups \(H\le(\mathbb Z/N)^\times\), initially of orders \(3,4,6,8\) when divisibility permits. Require an explicit seed action
   \[
   F(T_h(s))=[h]F(s).
   \]
   Establish closure, action laws, orbit sizes, and transformation costs. Scalar multiplication alone does **not** establish a cheap seed action.
3. Build the expensive correctness oracle
   \[
   c(s)=\min_{h\in H}\operatorname{encode}([h]F(s)),
   \]
   retaining the minimizing multiplier. Search for a cheaper canonicalizer using FAM-1 parameter permutations, rational expressions, or elimination invariants. An invariant alone is insufficient: its fibers must distinguish \(H\)-orbits, or false matches must be charged.
4. Run a quotient walk retaining \(X=[a]P+[b]Q\) and its canonicalizing multiplier. For a verified collision \(X_i=[h]X_j\), solve
   \[
   x=(ha_j-a_i)(b_i-hb_j)^{-1}\pmod N.
   \]
   Reject zero denominators. Test mixing and short cycles explicitly.

### Cost model
For a full-group, well-mixing quotient walk, model
\[
W_H\approx(C_{\rm step}+C_{\rm can})\sqrt{N/|H|}+C_{\rm lift}.
\]
Compare with measured baseline rho, including existing automorphism quotients. For restricted FAM-1 walks, **measure** reachable states and collision entropy; do not substitute seed count for \(N\).

For index-calculus relevance, separately measure useful relations per second, duplicate relations, and matrix rank. Rho acceleration alone is not an index-calculus improvement.

### Falsification
Reject if closure fails; canonicalization costs exceed the square-root gain; invariant fibers are excessively larger than orbits; quotient walks develop trapping cycles; or apparent relation savings vanish after deduplication and rank testing.

### First experiment
On several toy curves with \(N\approx2^{24}\)–\(2^{32}\), implement the actual FAM-1 action and exhaustive canonicalization oracle. Compare baseline and quotient walks over 100 independent trials, recording wall time, orbit sizes, collision validity, and cycle frequency. First require a reproducible net gain before optimizing invariants.

## Direction 99

### Construction
1. **Audit prior work before implementation.** In `isogeny-labs/crypto`, cryptanalysis, and `crypto-autoresearcher`, locate `LEAD-RHO-pool-class-quotient`, `LEAD-ICP-coincidence-harvest-structured-base`, and FAM-1 campaign artifacts. Extract curve parameters, subgroup order, seed distributions, walk functions, trap definitions, and measured baselines. Repository contents are unavailable here; prior results remain unverified.
2. **Apply the Frobenius feasibility gate.** For \(E/\mathbb F_p\), every \(P\in E(\mathbb F_p)\) satisfies \(\pi_p(P)=P\): Frobenius supplies **no additional quotient**. A Koblitz Frobenius walk requires a suitable extension-field setting, changing the campaign. Permit it only as a separately labeled control, never as a prime-field speedup.
3. **Implement the valid prime-field quotient.** For odd-order subgroup points \(R=aP+bQ\), canonically represent \(\{R,-R\}\), choosing the smaller encoded point and negating \((a,b)\) whenever required. Partition using the canonical encoding; add a precomputed \(u_iP+v_iQ\), update coefficients, and canonicalize again. Handle infinity explicitly.
4. Deduplicate seed classes globally; record duplicate-class frequency separately from walk collisions. Use identical distinguished-point criteria and storage budgets across runs. On collision, solve
\[
(b-b')x=a'-a\pmod n,
\]
rejecting zero denominators and verifying \(xP=Q\). Instrument short cycles; evaluate deterministic escape rules separately.

### Cost model
Measure additions, canonicalizations, hashes, network bytes, distinguished-point storage, and wall-clock time. Ideal negation quotient reduces rho collision work from approximately \(\sqrt{\pi n/2}\) to \(\sqrt{\pi n/4}\); overhead, correlations, and traps may erase that \(\sqrt2\) benefit. Seed deduplication saves redundant starts, not necessarily collision work. Report useful collisions per core-second and full recovery cost. This is a rho optimization, **not an index-calculus breakthrough** absent demonstrated relation-generation savings.

### Falsification
Reject the Frobenius claim immediately for rational prime-field points. Reject the practical quotient benefit if matched-budget trials show no statistically supported throughput improvement, or trap mitigation consumes the gain. Reject structured-seed harvesting if improvements disappear against uniformly sampled, class-deduplicated seeds.

### First experiment
On tractable subgroups matching the campaign’s field and curve structure, run paired ordinary-rho, negation-quotient, and quotient-plus-escape trials across at least 100 independent targets. Log cycle lengths, repeated classes, recoveries, and component timings; estimate variance before scaling to campaign parameters.

## Direction 100

### Construction and repository gate
- Audit `isogeny-labs/crypto`, cryptanalysis materials, and `crypto-autoresearcher` for FAM-1, structured-base coincidence harvesting, GPU matching, and interleaved rho experiments. Record commits, exact predicates, failed variants, timings, and controls. **These repositories are not accessible here; novelty and compatibility remain unverified.**
- Freeze the existing FAM-1 predicate before optimization. The following is an explicit candidate realization, not an assertion about its existing definition.
- On \(E/\mathbb F_p\), work in a prime-order subgroup of order \(n\), with \(Q=xP\). Choose a deterministic factor base \(B=\{B_i\}_{i=1}^m\) using the audited structured-base rule.
- Sample \(T_t=a_tP+b_tQ\). Enumerate \(S_{tij}=T_t+B_i+B_j\), \(i\le j\). Match against a GPU-resident table of complete, canonical factor-base point encodings. Each verified match \(S_{tij}=B_k\) yields
  \[
  a_t+b_tx+\ell_i+\ell_j-\ell_k=0\pmod n,
  \]
  where \(\ell_i=\log_P B_i\).
- CUDA tiles reuse \(T_t+B_i\); batch-normalize projective points, hash, and verify full-point equality. CPU independently verifies hits and assembles sparse equations. Solve only after measuring rank; verify recovered \(x\).

### Cost model
Let \(q\) be measured match probability per candidate; the uniform baseline is \(q\approx m/n\). Collecting \(R\) relations costs approximately \(R/q\) candidates. At \(R=\Theta(m)\), this is \(\Theta(n)\), **not an asymptotic improvement over rho**.

Measure total time:
\[
T=T_{\rm setup}+C/G+T_{\rm transfer}+T_{\rm verification}+T_{\rm linear\ algebra},
\]
with \(C\) actual candidates and \(G\) sustained candidate throughput. Include rank deficiency, memory, energy, and failed batches.

### Falsification
Reject advantage if structured bases provide no reproducible yield/rank improvement, GPU gains disappear end-to-end, or matched-budget rho wins. Reject this implementation immediately if it does not preserve the audited FAM-1 predicate.

### First experiment
Run randomized, interleaved CPU-FAM/GPU-FAM/CPU-rho/GPU-rho trials, including GPU A/A controls. Start with 24–40-bit prime-order toy curves, then advance a matched prime-field ladder toward P-256; smaller fields are not P-256 itself. Use identical instances, seeds, budgets, and correctness checks. Report confidence intervals for verified independent relations/second and time-to-solution before scaling.

