# Cluster 11 — SECANT: Goal Draft G31-001

Theme: a geometric, second instrument for the D2 quasirandom-relation-rate barrier.
Claim tier: toy. Nothing here asserts a crypto-scale fact, and no cell is a
performance claim. The goal measures a dimension statistic, not a relation engine,
so the G30-001 GOE ruler is not consumed and no rho-relative ratio is published.

Non-duplication rules honored:

- `LEAD-ICP-split-graph-secant-presentation` uses secant-line *coordinates* as a
  decomposition presentation for prime-field relation finding. This goal never
  measures that lead's bases, never re-sorts its saved panels, and never shares a
  frozen selector with it. The two touch the same word `secant` and no common
  object.
- G30-007/008 (arithmetic monodromy) and G30-022 (D1 log-space additive energy)
  are consumed only as comparison covariates on identical cells, and only if
  their numbers are already committed in-tree; otherwise the comparison arm is
  omitted and recorded as omitted.
- No existing certificate pool is re-sorted; all cells are fresh and frozen
  before any run.

## G31-001: Secant-defectivity (tangent/Jacobian rank) census — an independent geometric instrument for D2

- **Cluster:** 11 SECANT
- **Type:** measurement
- **Long-term chain:** D2 (quasirandom relation rates) is the program's flagship
  barrier and currently has one instrument family, the arithmetic monodromy line
  (G30-007 Chebotarev census, G30-008 imprimitive-resolvent test, G30-009 wreath
  barrier theorem). A barrier promoted on arithmetically computed densities alone
  is only as strong as one instrument. This goal builds a geometrically
  independent second instrument — the classical tangent/tangent-span (Terracini)
  rank test for secant defectivity — at one elimination pass per cell instead of a
  Chebotarev/resultant computation, and pre-registers the agreement test between
  the two. The outcome gates whether a D2 promotion may cite two independent
  instruments, and whether secant geometry can screen a structured factor base
  before a relation engine is built (the D1 interface).
- **Mechanism:** Fix a degree-d model embedding φ_d: E → P^(d−1) by the complete
  linear system |d·O| (d ∈ {6,7,8}; d ≥ 6 is required for the informative cells),
  over toy curves at p ∈ {127, 257, 1024, 4096}. For N points P_1..P_N and the
  join parameterization Φ(P_1..P_N, λ) = Σ λ_i φ_d(P_i), the join Jacobian at a
  generic point is the (d−1) × 2N matrix

      J = [ v_1 … v_N | t_1 … t_N ],   v_i = affine φ_d(P_i),  t_i = affine
      tangent direction at φ_d(P_i),

  and defectivity is rank(J) < min(2N, d−1), i.e. the Terracini-type
  tangent/tangent-span test (the affine form of the classical statement that the
  tangent space of the secant variety is spanned by the tangents at the contact
  points). All conventions — embedding basis, affine chart, rank normalization,
  sign-branch ordering — are frozen in the pre-registration before the first run.
  Two arms:
  (i) **model arm** — N general points, informative cells where 2N < d−1
      ((d,N) = (6,2), (7,2), (8,2), (8,3)); the classical expected-dimension rule
      for elliptic normal curves predicts no defect, and this arm is a
      calibration/null, not a discovery arm;
  (ii) **branch arm** — the object every relation engine actually faces: the
      x-line model, where each base x-coordinate carries two points ±P. The base
      fixes x_1..x_N and the signs are free; the statistic is
      max over the 2^(N−1) sign patterns of rank(J^σ), since a relation needs one
      branch at expected rank. Relation-relevant cells use subgroup bases of order
      ~p^(1/3), x-interval bases, and seeded uniform bases, paired per instance.
  The rank statistic is validated against exhaustive secant enumeration at
  p ≤ 128: enumerate all N-tuples, compute the exact rank of every join matrix,
  and compare rank laws, not just the maximum.
- **Quantified prediction:** model arm: rank deficit 0 in 100% of informative cells
  (≥ 3 curves × 3 seeds × 4 p-values), consistent with the classical
  expected dimension for elliptic normal curves. Branch arm: deficit 0 in ≥ 95% of
  cells; any deficit is monotone in the base's log-space additive energy
  (Spearman ρ ≥ 0.5 over ≥ 24 cells) rather than in p, and reproduces at a second
  seed. Bridge test (pre-registered, not confirmatory): the branch-arm deficit and
  the measured relation-rate residual on the identical instance agree in sign in
  ≥ 90% of cells; otherwise the bridge is recorded as unestablished, and only the
  instrument, not D2, is reported.
- **Test boundary / scope:** toy only (p ≤ 4096); d ≤ 8; N ∈ {2,3}; prime-order
  subgroup instances only; no Gröbner computation and no monodromy computation in
  this goal; 2^(N−1) ≤ 4 sign branches, all charged. Nothing here extrapolates to
  cryptographic p, and no cell says anything about a deployed curve.
- **Primary metric:** measured rank deficit r_exp − r_meas per frozen cell, with
  r_exp = min(2N, d−1) / **Secondary metrics:** the full rank distribution per
  cell, the max-branch statistic, the base's log-space additive energy, the
  measured relation-rate residual on the identical instance, field operations per
  cell (the instrument's cost claim is exactly this number, not wall time), and
  peak RSS.
- **Controls:** exhaustive enumeration at p ≤ 128 as ground truth for the rank law;
  a rational-normal-curve null (degree-d embedding of P^1), where no secant
  defectivity is possible, must show deficit 0 in every cell — a defect there is
  an implementation bug by construction; paired bases of identical size (uniform
  random vs subgroup vs x-interval) on the same curve and the same targets;
  a second, independently written rank routine (exact rational / Sage path through
  G30-025's environment capture where available) on ≥ 10% of cells; frozen cell
  list opened only once.
- **Falsification criteria:** (i) exhaustive validation disagrees with the rank
  statistic in any cell → instrument defect, every affected cell is
  `invalid_measurement` and carries no evidential weight; (ii) the model arm shows
  a reproducible deficit ≥ 1 at two seeds and two curves at p ≥ 1024 — this would
  contradict the classical expected dimension for elliptic normal curves, so
  before any claim it requires an independent derivation artifact per
  `docs/claims-and-verification.md`; (iii) the branch arm shows deficit 0 in every
  cell *and* |Spearman ρ| < 0.2 against both the additive energy and the
  relation-rate residual over ≥ 24 cells → the instrument has no discriminating
  power for D2; it is scoped down to a calibration artifact and the negative is
  recorded as "D2's content is invisible to this secant statistic", never as
  support for D2.
- **Negative-outcome value:** outcome (iii) is the expected, publishable result if
  the classical picture survives: it says D2's quasirandomness is an arithmetic
  phenomenon, not a classical secant-dimension phenomenon, which forecloses any
  future "the secant variety says so" argument and replaces repeated Chebotarev
  spend at m=2 (one rank elimination vs a density computation). A positive
  (correlated deficit) gives D1 a geometric witness and D2 a genuinely independent
  instrument. Outcomes (i)/(ii) are instrument or mathematics events and are
  reported as such, never as theory evidence.
- **Budget:** wall_clock 12h, memory 4 GiB, max_runs 96
- **Stopping rule:** stop when every frozen (d, N, p, base) cell has a completed
  rank result with its validation and control pairs, OR at 12h wall clock, OR when
  the p ≤ 128 validation fails twice (early stop; reported as instrument defect,
  not as a negative result). Censored and invalid cells are listed explicitly.
- **Harness dependency:** existing `harness/toycurve.py` (curves, group law,
  deterministic instance generation); commissions one module,
  `harness/secant_tangent.py`: |d·O| Riemann–Roch basis coordinates over F_p,
  join-Jacobian assembly, exact rank, exhaustive secant enumeration at tiny p, and
  the x-line sign-branch enumeration. Pure Python/sympy; an optional Sage
  cross-check goes through G30-025's environment-capture registry. No dependency
  on the GOE cost ruler; no rho baseline is needed because no performance claim is
  made.
- **Claim tier:** toy
- **Dependencies:** none hard. Soft interfaces only: G30-007/008 comparison numbers
  and G30-010/013/015 relation-rate residuals are consumed only if already
  committed, on identical cells, with no re-sorting and no re-selection.
- **Novelty screen (2026-11-20):** corpus grep for `terracini|castelnuovo|secant
  variet` finds only the secant-rank digest `KN-LIT-1861` and `KN-LIT-1576`;
  Castelnuovo–**Mumford** regularity in the lead-discovery report is a different
  theorem that a naive regex conflates, and no goal or experiment measures secant
  defectivity. The only `secant` lead is a decomposition presentation (above).
  No novelty is claimed beyond "absent from this program".
