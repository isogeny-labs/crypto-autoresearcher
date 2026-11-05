# Round-2 prime-field ECDLP lead proposals: synthesis memo (2026-11-04)

Author role: Idea Synthesist (proposal only). This file changes no repo file, ledger record,
status or disposition. It makes no speedup claim and files no ledger record. Every prediction
below is a numbered heuristic until a run tests it.

## 0. Method, and what could not be done

- **Read:** `knowledge/leads/ecdlp/README.md`; every lead row's `title` and `forecloses`
  (173 rows, all families); the full rows of the holant, low-degree, coordinate-statistic, ML,
  character-sum, methodology, coincidence-harvest, Coppersmith and digit-presentation leads;
  `docs/reports/{ecdlp-exotic-scouting-20261101, holant-h1-ggm-lemma-20261103,
  holant-step-b-qtt-20261104, ecdlp-leads-desk-20261104}/README.md`; `lowdeg_rank_check.{py,json}`;
  `ledger/evidence/EV-ECDLP-f83a17.yaml`; the frozen spec
  `ledger/corrections/schema-supersessions/20260808/experiments__EXP-ECDLP-1ed445__specification.v2.yaml`;
  `knowledge/findings/KN-FIND-{9d2f56,4c9e71}.md`; `AGENTS.md`; and `docs/reports/ecdlp-lead-discovery-20261024/AUDIT.md`
  around lines 5453 and 5841. Sibling drafts in this scratchpad (`round2/amendments.md`, `anom_compact.jsonl`)
  were checked to avoid overlap.
- **Not run: `tools/lead_atlas.py --brief` and `--match`.** This session has no shell tool.
  I emulated `--match` by grepping the same fields the tool scores (`forecloses` x3,
  `title` x2, `mechanism` x1, from `tools/lead_atlas.py:609-623`). The hits below are therefore
  ranked by inspection and carry no numeric scores. KR rows were not searched, because
  `knowledge/frontiers/ecdlp/` holds only its README in this sparse clone. Before filing, re-run the
  real gate on the quoted phrasings.
- **Citation provenance (AGENTS.md rule 9):** `internal` = a repo path I read; `recalled` = from
  memory, a pointer only and never support.

## 1. The connection

Three structure instruments ran in the last two weeks: the character-sum ladder (H-PSEUDO), the
digit-QTT rank of the transfer matrix M, and the low-degree evaluation rank. Each produced one
number that its report could not explain:

1. **H-PSEUDO:** R = C_EC/C_null sits at about 1.3, a little above its preregistered band
   (ANOM-001, `EV-ECDLP-f83a17`).
2. **QTT:** the discrete-log labelling of M "still has rank of order sqrt(p)"
   (`holant-step-b-qtt-20261104`, post-data item 2).
3. **Low-degree:** p = 211 shows rank deficits "not explained here" (`ecdlp-leads-desk-20261104`).

I think each anomaly comes from a **nuisance structure the lane's null did not model**:

1. **Negation symmetry of the small-x factor base.** F = -F, so its transform is real, while
   the null was a complex Gaussian.
2. **The entropy of log(FB) alone.** In log order, M is Toeplitz-plus-Hankel in the indicator of
   log(FB), so its QTT rank is that indicator's rank.
3. **Short integer relations among the multipliers b_i mod N.**

A second gap is shared by every lane: **no instrument has been run on a natural weak curve
class.** The only such datum is one anomalous p = 61 curve, and it lies outside the decision rule.

This connection was not visible lane by lane. Each lane built a null matched to its own object
and none shares a calibration panel. The cheapest experiments in the portfolio are therefore
re-nulls and calibrations, not new mechanisms. They decide how to read three recent rows at once,
and they rank first below.

The atlas is close to saturated for new mechanisms. Under the emulated gate, only **three** of the
seven items are new rows (N1-N3). The other four (D1-D4) are **new mechanisms or explanations inside
existing rows**: no row records them, but they would be filed as next-action amendments. I rank
them together by information per hour, as asked.

## 2. Ranked list (information gained per hour of test)

| rank | id | type | one line | field | cost (local CPU) | prior that the predicted outcome holds |
|--:|:--|:--|:--|:--|:--|:--|
| 1 | D1 | amendment (H-PSEUDO) | R ~ 1.3 is the max of a real vs a complex Gaussian (negation symmetry); a symmetric null gives R ~ 1.00 | extreme-value statistics | 20-30 min | ~85% |
| 2 | D2 | amendment (low-degree) | p = 211 rank deficits come from short relations c.b = 0 mod N among multipliers; time-charging lemma for interpolation tests | lattices / complexity | 15 min + 1 h desk | ~65% |
| 3 | D3 | amendment (holant) | QTT rank of M in log order is fixed by the QTT rank of 1_{log FB}; a log-AP factor base collapses it to O(1) | tensor networks | 30-45 min | ~80% |
| 4 | D4 | amendment (ML) | the ML lead's "planted homomorphic leak" control is predicted to read chance unless its multiplicative height is small, so a curve-arm null would be uninterpretable | learning theory (SQ) | ~1 h | ~70% |
| 5 | N1 | **new** | natural weak classes (anomalous, MNT k = 3/4/6, j = 0 with a zeta-stable FB) as positive controls for every numeric instrument | methodology / statistics | 3-4 h | ~85% blind |
| 6 | N2 | **new** | quadratic-phase (U^3) correlation of the small-x predicate in log order; exploitable by a u = r^2 reduction to a linear hidden-number problem | additive combinatorics / HNP | 2-3 h | ~99% null |
| 7 | N3 | **new** | Farey (small-height rational x = u/v) factor base: yield census and lattice reach of the non-x-variable presentation | lattice / NFS transfer | 1.5-2 h | ~97% no gain |

Each test uses local CPU only: no cloud, no GPU, under 8 GB RAM. All of them fit in about 9-12 CPU
hours. D1-D3 together take under 2 hours and would settle three open anomalies.

---

## 3. Records

### D1. Negation symmetry explains R ~ 1.3 in the H-PSEUDO ladder (amends `LEAD-EXO-dl-character-sum-pseudorandom`)

- **Mechanism.** The small-x factor base is closed under negation: F = -F, and the spec's tau rule
  takes points in (x, then y) order, so both +-P are present. Its additive-character transform
  sum_{P in F} e(k log P / N) is therefore **real**. Each value is a sum of B/2 terms
  2 cos(theta) with variance B, so |.|^2/B ~ chi^2_1 rather than Exp(1). The frozen null
  (`EXP-ECDLP-1ed445` spec, ARM-NULL) is a uniform, non-symmetric B-subset with forced value
  sqrt(ln M + gamma), where M = (N-1)/2. Its maximum is that of complex Gaussians.
- **Claim (derived here; numbered heuristic HD1).** Over M independent frequencies, the expected
  maximum of chi^2_1 is a_M + 2 gamma, where a_M solves sqrt(2/(pi a)) e^(-a/2) = 1/M (Gumbel scale 2).
  Hence C_sym ~ sqrt(a_M + 2 gamma), and the predicted ratio is:

  | N | C_null (spec formula) | predicted C_sym | predicted R = C_sym/C_null | recorded R (EV-ECDLP-f83a17) |
  |:--|--:|--:|--:|--:|
  | 2^17 | 3.42 | 4.47 | 1.31 | - |
  | 2^20 | 3.71 | 4.89 | 1.32 | 1.334 |
  | 2^22 | 3.89 | 5.16 | 1.33 | 1.280 |
  | 2^24 | 4.07 | 5.41 | 1.33 | 1.275 |
  | 2^26 | 4.23 | 5.65 | 1.34 | 1.342 |

  As N grows the ratio tends slowly to sqrt 2. HD1 also predicts ANOM-001 (R slightly above
  1.32), which the record left unexplained. The Jensen correction for E[sqrt max] is under 0.3%.
- **Assumption to check first.** The DL table is keyed by x on first occurrence. If the EC arm
  placed both +-P at the same index (logs collapsed into [1,(N-1)/2]), the set would carry a
  half-range bias at k = +-1, and R would be about 2 or more, which was not observed. HD1
  assumes signed logs. Confirm this in the run code before reading the result.
- **Why not covered (emulated match).**
  - "negation-symmetric null for the character-sum ladder": top hits
    `LEAD-EXO-dl-character-sum-pseudorandom` (forecloses "H-PSEUDO bias", "Fourier bias of
    x-coordinate sets in log order"), `LEAD-EXO-methodology-instruments` ("label-permutation
    null"), `LEAD-RHO-negation-map-fruitless-cycles` (title token "negation").
  - "small-x factor base Fourier maximum real-valued extreme value": `dl-character-sum`,
    `coordinate-statistic-leakage`.
  - "Gumbel chi-square constant offset of the character-sum ratio": `dl-character-sum` only.
  - Why they differ: no row, finding or evidence record mentions the symmetry. A repo grep for
    "negation-symmetr", "symmetric null" and "Gumbel" in `knowledge/` and `ledger/evidence/` finds
    only the spec's complex-Gaussian derivation.
- **Test.** Re-run only the null with negation-closed random sets: B/2 random pairs {l, N-l}, at the
  four recorded N (or the per-curve N, which also fixes ANOM-002), 200 draws each. No EC arm
  is needed, because the EC values are on record. Optionally re-run the EC arm at bits = 20
  (8 curves, a few minutes) to check the signed-log assumption.
- **Pre-registered prediction.** C_symnull is within 3% of the table at every rung, and
  R_sym = C_EC/C_symnull lies in [0.96, 1.04] at every rung.
- **Falsifier.** R_sym > 1.05 at 2 or more rungs means a residual EC-specific excess beyond
  symmetry, which should be reported as such. C_symnull more than 3% off the table means HD1 is wrong.
- **What each outcome changes.** If confirmed, the "constant offset" in the record is fully
  accounted for. The row's revisit trigger ("R trends upward") must then be read against a
  symmetric null. The p^0.079 growth in `KN-FIND-4c9e71` is consistent with the extreme-value
  growth of the symmetric max (predicted effective exponent about 0.065 over p = 1009 to 50021).
  The follow-up is to audit every factor-base-versus-null comparison whose factor base is
  negation-closed and whose null is not. x-keyed statistics (QTT, kappa) are already quotiented and
  are probably safe. If falsified, a real constant excess remains, the first positive H-PSEUDO
  residual, and it goes to `review-breakthrough`.
- **Cost.** About 800 FFTs of length up to 2^26 (about 3 s each at the top rung), so 20-30 min on
  one core, 8 GB peak. Desk work is done here.

### D2. Short multiplier relations explain the p = 211 rank deficits, and interpolation tests cost at least N/2 per target (amends `LEAD-EXO-low-degree-query-lower-bound`)

- **Observation (internal, `lowdeg_rank_check.json`, `lowdeg_rank_check.py`).** The
  expected rank is #monomials minus the Weierstrass multiples: t (D = 3) or 7t (D = 4) for t points.
  This holds exactly in every cell except the two t = 3 cells at p = 211:

  | cell | measured | expected | deficit |
  |:--|--:|--:|--:|
  | (t,D) = (3,3) | 77 | 81 | 4 |
  | (t,D) = (3,4) | 162 | 189 | 27 |

  The t = 4 cell at p = 211 is exact (161 = 165 - 4). The two t = 3 cells draw their b_i from
  different seeds (20261104+33 and +34).
- **Mechanism (HD2a).** A relation c1 b1 + c2 b2 + c3 b3 = 0 (mod N) with small c turns into a
  polynomial relation among the t points. For example, c in {+-1}^3 makes the three points
  collinear, which is the degree-2 determinant g. g and its multiples, net of their syzygies with
  the Weierstrass relations, give deficits that grow with D in the observed way (degree-2 multiples:
  7 at D = 3 and 28 at D = 4, against 4 and 27 measured).
- **Alternative (HD2b).** The deficit is structural at that curve or prime.
- **Test (10-15 min).** At p = 211 and at a second p near 227, take 50 fresh random b-triples and
  record the rank at D = 3 and D = 4. For each triple, record the shortest nonzero vector of the
  lattice {c : c.b = 0 mod N} (a 3-dim LLL). Then print the two original seeds' b-triples.
- **Prediction.** At least 80% of triples are exact. Every deficient triple has a relation with
  |c|_inf <= 2. Rank deficits occur only where such a relation exists.
- **Falsifier.** More than 20% of triples are deficient, or any deficient triple has no relation
  with |c|_inf <= 2. Then HD2b holds, and the full-rank heuristic behind the row's attack needs a
  structural correction at small p.
- **Desk companion (time-charging lemma, HD2c; about 1 h).** A test answers "k in S?" only if some
  f in the evaluation span V vanishes exactly on S among the N candidates. For |S| about N/2 and V
  in general position, that needs dim V > N/2. So f has at least about N/2 monomials, and evaluating
  it costs at least about N/2 field operations per target. Short (SLP-compact) tests with large zero
  sets do exist, for example the Legendre symbol of x, but their zero sets in log space are
  pseudo-random. Interpreting them needs enumeration (Kohel-Shparlinski covers the t = 1 case;
  `internal`, desk note). Consequence: the row's attack is a preprocessing attack with advice of
  N^(1+o(1)) and per-target time of N^(1+o(1)). It is dominated by a plain DL table. The
  "restrict local work" model note the row anticipates should charge f's description length.
- **Why not covered (emulated match).**
  - "rank deficit of low-degree evaluation matrix from multiplier relations":
    `LEAD-EXO-low-degree-query-lower-bound` ("low-degree polynomial test on coordinates..."),
    `LEAD-EXO-invertible-hint-subset` ("low-degree polynomial agreeing with the discrete log"),
    `LEAD-ICE-relation-graph-rank-large-prime` (token "rank").
  - "time-charged interpolation coordinate tests": low-degree lead only (mechanism "free local work").
  - "short relation lattice of the multipliers b_i": `LEAD-STR-endo-scalar-action-generic`
    ("eigenvalue lattice reduction recovers k"), `LEAD-ICP-lattice-ic-relation-construction`.
  - Why they differ: the row records the deficit as unexplained and plans a rank sweep with random
    b_i. It neither controls for relations among the b_i nor charges description length.
- **Outcome value.** If HD2a holds, the planned 2^8-2^14 sweep must draw b_i with no short relation
  (reject b with ||c||_inf <= 3) or log the shortest relation as a covariate. Otherwise the sweep
  conflates two effects.

### D3. In log order, QTT rank of M equals the QTT rank of the log-set symbol (amends `LEAD-EXO-holant-decomposition-count-network`)

- **Mechanism.** In the LOG arm, row i stands for +-[i]G. Then
  M[i,j] = c(i+j) + c(i-j), where c = 1_{+-log FB}: M is Toeplitz plus Hankel in the symbol c.
  The QTT ranks of Toeplitz and Hankel matrices with interleaved digits are bounded by a small
  constant times the QTT ranks of their generating vector (Kazeev-Khoromskij-Tyrtyshnikov,
  multilevel Toeplitz in TT format; `recalled`). The QTT rank of any length-2^L vector is at most
  2^(L/2) at the middle cut. This ceiling alone predicts "LOG r_max ~ 2-4 sqrt(p), saturating as |FB|
  grows", which is what the report observed (post-data item 2). So the positive control measures
  how random log(FB) is. It does not measure the elliptic-curve group law.
- **Claim (HD3).**
  - (i) r_max(M_LOG) <= kappa r_max(c), with kappa <= 4.
  - (ii) The small-x FB and a random-log FB of the same size give the same r_max(M_LOG), within
    the null spread.
  - (iii) A log-AP factor base {+-[i]G : 1 <= i <= s} gives r_max(M_LOG) <= 12 at every L, because
    an interval indicator has QTT rank at most 3.
- **Why not covered (emulated match).**
  - "QTT rank of the transfer matrix in discrete-log order": `holant-decomposition-count-network`
    (forecloses "transfer matrix of decomposition counts...", "low tensor rank of the S_3 incidence
    tensor"), `LEAD-EXO-hashed-factor-base-tensor-ecdl` ("tensor contraction counting").
  - "tensor-train rank of the factor base's log indicator": `dl-character-sum-pseudorandom`
    ("Fourier bias of x-coordinate sets in log order"), holant.
  - "log-space description complexity of the factor base": `coincidence-harvest-structured-base`
    ("log-GAP bases"), `dl-character-sum`.
  - Why they differ: the holant row's reopen bar ("a labelling ... with QTT rank below sqrt(p)")
    treats sqrt(p) as a property of M. HD3 says it is the vector ceiling, set by log(FB).
- **Test.** Add three arms to the frozen `qtt_rank.py` at L = 6..10 (3 curves per L):
  1. LOG with the small-x FB (existing);
  2. LOG with a random-log FB of equal size (20 draws);
  3. LOG with the log-AP FB.

  Also compute r_max(c) directly for each arm.
- **Prediction.** (ii) holds on at least 7 of 9 curves with L >= 8. (iii) gives r_max <= 12. The
  ratio r_max(M_LOG)/r_max(c) lies in [1, 4] for every arm.
- **Falsifier.** The small-x FB falls below the random-log arm's 5th percentile on at least 7 of 9
  curves: digit structure in the small-x log set, the first QTT-visible deviation. Or the log-AP
  arm stays near sqrt(p): then sqrt(p) is intrinsic to the negation-quotient Cayley structure, and
  HD3 is wrong.
- **What it changes.** If confirmed, the holant row's QTT branch is a restatement of the H-PSEUDO
  object, the digit complexity of log(FB). Its reopen condition becomes "an x-describable FB whose
  log set has low QTT rank", which means a factor base with cheaply known logs, which means generic
  (BSGS-like). The QTT branch could then be filed as `closed_dominated` by the character-sum row for
  that scope. This is a Coordinator call.
- **Note for the anomalous follow-up (not a new arm here).** One curve below the 5th percentile
  among the 6 curves at L <= 7 has chance probability 1 - 0.95^6 ~ 0.26 under the null. A
  decisive control on #E = p curves is the psi-labelling, by Smart's p-adic log, which equals LOG
  up to scaling: HD3 predicts it matches LOG, and the X arm sits at the null.
- **Cost.** About 30-45 min on one core (the original run took 18 min for 1530 matrices).

### D4. The ML lead's positive control is predicted to be blind; calibrate its multiplicative height first (amends `LEAD-EXO-ml-learned-models`)

- **Mechanism.** The row plans to "train a model to predict a log bit from coordinates, with a
  planted-structure positive control (a known homomorphic leak) ... at N up to 2^24". A natural
  homomorphic leak exposes u = c.l mod n for an unknown or known c. Two examples: Smart's psi on an
  anomalous curve, and a planted feature. The label is then lsb(l) = lsb(c^-1 u mod n), which for
  odd n is a half-interval predicate of (c^-1/2) u mod n. The functions {u -> half(a u mod n)}
  are pairwise nearly uncorrelated unless a1/a2 has a small-height rational representative mod n. That is
  a high statistical-query dimension, so SQ-style learners and large-batch gradient descent are
  predicted to need super-polynomially many queries (Kearns 1998; Blum et al. 1994;
  Shalev-Shwartz-Shamir-Shammah 2017; all `recalled`). Abbe-Sandon 2020 (`recalled`) shows that
  small-batch SGD can escape SQ, so the prediction is empirical, not a theorem, for real training.
- **Claim (HD4).** An MLP trained by gradient descent on binary-encoded u reaches about 0.9 held-out
  accuracy for small-height c (c = 1, 2, 3, or u/v with |u|,|v| <= 4). It stays at chance
  (accuracy within 0.02 of 0.5) for random c at n >= 2^16, with up to 10^6 examples.
- **Why not covered (emulated match).**
  - "neural network learns modular multiplication as a positive control":
    `LEAD-EXO-ml-learned-models` ("neural network predicts discrete log bits"),
    `LEAD-EXO-methodology-instruments` ("planted-signal positive control").
  - "statistical-query hardness of learning discrete-log bits": `LEAD-EXO-hnp-advice-leakage`
    ("bit security of the elliptic discrete log"), ML lead.
  - "gradient descent cannot learn a planted homomorphic leak": ML lead, methodology lead.
  - Why they differ: no row or audit note discusses the learnability of the control itself. A
    repo grep for "statistical query", "SQ dimension" and "learnab" finds only the ML row's own
    step.
- **Test.** For n in {2^12, 2^14, 2^16}, take c in {1, 2, 3, 5/3 mod n, 10 random}. Use inputs u in
  binary (and one-hot at n = 2^12) with an 80/20 split, a 2-layer MLP (numpy or sklearn), and a fixed
  budget per cell. Report accuracy against the multiplicative height of c.
- **Falsifier.** Random-c accuracy of at least 0.9 at n = 2^16. The planned control is then valid
  as designed, and the row proceeds unchanged.
- **What it changes.** If HD4 holds, the row's 2^24 run cannot tell "no leak on the curve" from "a
  leak the learner cannot represent". The control should be replaced by a height ladder, and any
  curve-arm null scoped to "no leak of multiplicative height below h*". The cost is about 1 h
  against the row's planned training budget. This is the same blindness that N1 tests across
  instruments.
- **Prior.** About 70% that random c fails. Grokking results (`recalled`) show modular arithmetic
  learned at p about 97 from nearly full tables, so small n may pass.

### N1. Natural weak curve classes as positive controls for the numeric instruments (NEW)

- **Mechanism.** Every exhausted or null structure row rests on an instrument that has never seen a
  curve whose DLP is known to be easy. The audit has proposed known-positive replays for the
  screen's Gate A/B sheets and for the GGM-simulability classifier (`AUDIT.md` lines 5453 and 5841,
  `internal`), but not for the measured statistics. This lead runs a panel of natural weak classes
  through each numeric instrument. The result is a detect-or-blind table, which scopes what every
  null means.
- **Panel (toy p in [2^10, 2^14]; 3 curves per class per size).**
  - (A) Anomalous, #E = p. DLP is polynomial-time. Found by random search with naive point counting:
    about 4 sqrt(p) curves per hit, seconds at 2^14.
  - (B) Prime-order MNT-type curves with embedding degree k in {3, 4, 6}. DLP is subexponential
    through MOV. Found by searching for traces with p^k = 1 mod n.
  - (C) j = 0 with a zeta-stable factor base. The constant-factor class, and the only one with a
    known spectral signature (2/3 of M's eigenvalues are exact character sums, per the H1 report).
  - (D) Ordinary prime-order curves.
- **Instruments.**
  - (i) The frozen QTT r_max (odd-prime #E only, so A and D);
  - (ii) the character-sum C against the **symmetric** null from D1;
  - (iii) the low-degree rank r(t,D,b) with b drawn to have no short relation (D2);
  - (iv) the m = 2 x-keyed decomposition yield kappa against a random factor base.
- **Prediction.** Instruments (i), (ii) and (iv) are blind to A and B: each class falls inside its
  null's 5-95% band at 2 or more of 3 sizes. (iii) is curve-independent at full rank. C is detected
  by (ii) only as a small downward shift (fewer independent frequencies).
- **Falsifier.** Any instrument separates A or B from D at 2 or more sizes, beyond the null band, in
  the same direction.
- **What each outcome changes.** If blind, every `exhausted_at_scale` row resting on (i), (ii) or
  (iv) gets a scope note: "blind to Smart- and MOV-weak classes; a null excludes only structure of
  this statistic's type". That is honest scoping, not closure. If an instrument detects a weak
  class, it is the first with natural dynamic range. Its signal on A or B then becomes the object to
  explain, starting with the p = 61 QTT dip, before any ordinary-curve null from it is read.
- **Why not covered (emulated match).**
  - "anomalous and MNT curves as positive controls for structure instruments":
    `LEAD-EXO-methodology-instruments` ("planted-signal positive control", "instrument detection
    floor"), `LEAD-TRF-anomalous-padic-lift` ("anomalous curve attack"),
    `LEAD-TRF-mov-small-embedding-degree` ("small embedding degree attack").
  - "natural weak-curve panel for instrument calibration": methodology lead,
    `LEAD-TRF-curve-parameter-transfer-audits` ("anomalous standard curve").
  - "known weak-class detection by QTT, character sum and low-degree rank": holant row (p = 61
    remark), `dl-character-sum`, `low-degree-query-lower-bound`.
  - Why they differ: the methodology row injects **synthetic** planted signals (IDEA-20260807-efc8de),
    the audit proposals calibrate classifiers rather than statistics, and the in-flight anomalous
    follow-up (`anom_compact.jsonl`) is QTT-only on class A. Hand the QTT x A cell to that
    follow-up and run the rest here.
- **Prior and why worth it.** About 85% that all instruments are blind. The value is in the scope
  notes for roughly ten rows. Detection would be the more valuable outcome.
- **Cost.** 3-4 h in total: about 1 h coding, under 5 min of curve search, about 1-2 h of instrument
  runs (the low-degree rank at N about 10^3 is the bottleneck, around 1 min per cell with numpy
  int64 elimination).

### N2. Quadratic-phase (U^3) leakage of the small-x predicate in log order (NEW)

- **Mechanism.** H-PSEUDO tests linear phases e(k l/N). Additive combinatorics separates linear
  (U^2) from quadratic (U^3) structure. A set can be Fourier-flat yet correlate with e(alpha l^2/N).
  Relation yield is a complexity-1 count and so is governed by U^2 alone (generalized von Neumann,
  `recalled`). So N2 is **not** a yield lead. It is a direct leakage lead with an explicit
  exploitation path, sketched below.
- **Exploitation path (derived here).** Let g(r) = 1_S([r]Q), so g(r) = f(rk). If f has a heavy
  coefficient at (alpha*, 0), then g has one at alpha* k^2. The factor base is negation-closed, so g
  is even. Set h(u) = g(sqrt u) on quadratic residues (sqrt mod n is cheap, and [sqrt u]Q costs
  O(log n) group operations). Then h correlates with the **linear** phase e(alpha* k^2 u / N).
  Akavia-Goldwasser-Safra / Kushilevitz-Mansour sparse Fourier search with chosen queries
  (`recalled`) recovers k^2 in poly(log n, 1/tau), and hence k up to sign. A heavy coefficient with
  beta* != 0 already shows up as linear H-PSEUDO bias.
- **Why worth testing.** Linear phases have a rigorous, if weak, bound by completion through group
  characters (Kohel-Shparlinski type, `internal` desk note; KN-FIND-e7a3b1 records the
  O(p^(3/4))-type route). Quadratic phases in log l are not group characters, so no completion
  argument applies, and to my knowledge no bound exists. The instrument already exists: it is
  EXP-ECDLP-1ed445 with one extra loop.
- **Test.** n in {2^14, 2^16} (and 2^17 if time allows), 3 curves each, B = 512 (the frozen B rule).
  f = 1_F - B/n. For each alpha in [1, n-1], FFT f(l) e(alpha l^2/n) over l, and take
  Q = max_{alpha,beta} |.|/sqrt(B). Nulls: 30 negation-closed random sets per size (the D1 lesson).
  Positive control: a planted set {l : alpha0 l^2 mod n in [0, B)}, which is negation-closed and
  has size about B, and must spike at alpha0.
- **Prediction.** Q_EC lies within the symmetric null's 5-95% band on at least 5 of 6 curves. The
  planted control exceeds the null max by at least 3x.
- **Falsifier.** Q_EC is above the symmetric-null maximum on at least 2 of 3 curves at both sizes, at
  a stable alpha* across curves of one size.
- **What it changes.** A null closes degree-2 phase leakage of the small-x predicate at toy scale.
  It sits beside H-PSEUDO, and the same scale caveat applies (toy cannot see tau ~ 1/polylog). A
  signal would be the first non-linear Fourier bias on record and goes to `review-breakthrough`.
- **Why not covered (emulated match).**
  - "quadratic phase correlation of the x-coordinate predicate in log order": `dl-character-sum`
    ("Fourier bias of x-coordinate sets in log order"), `coordinate-statistic-leakage`
    ("x-coordinate statistic census").
  - "Gowers U3 norm of the small-x factor base": no lexical hit beyond those two. A grep for "Gowers",
    "U^3", "quadratic phase", "nilsequence" and "polynomial hidden number" in `knowledge/leads/ecdlp/`
    finds nothing.
  - "polynomial hidden number problem from quadratic Fourier bias": `LEAD-EXO-hnp-advice-leakage`
    ("hidden number problem from coordinate bias", "convert a statistical distinguisher into key
    recovery").
  - Why they differ: every covered statistic is linear in log or local in coordinates. The
    conversion step is shared with hnp-advice, and N2 would feed it.
- **Cost.** n FFTs of length n per function: about 1.5 min per function at 2^16, so about 1.5-2.5 h
  for 3 curves plus 30 nulls plus controls at two sizes, on one core, under 2 GB.

### N3. Farey (small-height rational) factor base (NEW; lowest rank)

- **Mechanism.** This is the F_p^* NFS rational-reconstruction idea (Joux-Lercier, `recalled`)
  transferred to the factor base: FB = {P : x(P) = u/v mod p, |u|,|v| <= B}, of size about (12/pi^2) B^2.
  Membership costs one half-gcd. The Semaev block becomes trihomogeneous of tridegree (2,2,2) in
  six small unknowns, a **non-x-variable presentation**. The Coppersmith row's `revisit_when` lists
  "a non-convex monomial set or an unequal-bound allocation", and its evidence lists "e-form unequal
  bounds, non-convex and multi-ideal lattices stay open".
- **Claim (HN3).** The m = 2 yield equals that of an interval factor base of equal size, by
  equidistribution of Farey fractions mod p. The lattice reach per block, in units of log|FB|, does
  not exceed the interval reach (0.3536 for two unknowns per block). A volume argument suggests why:
  the box volume u1 v1 u2 v2 equals x1 x2 at equal |FB|.
- **Test.**
  - (a) Census of per-target m = 2 decompositions at p ~ 2^16 and 2^20, Farey against interval at
    equal |FB|, 10^4 targets.
  - (b) Planted-solution LLL recovery at 32-40 bits for the dehomogenized S_3 block in (u,v)
    unknowns with Jochemsz-May-style shifts. Use `tools/smallroot_reach.py` calibration where it
    applies; the polytope is degenerate (homogeneous), so the volume formula needs the
    dehomogenized form.
- **Falsifier.** Planted recovery succeeds at a |FB| exponent above the interval's by at least 0.05
  per block, or the census yield ratio leaves [0.95, 1.05].
- **What it changes.** A null closes the "non-x-variable small-height" branch of the Coppersmith
  revisit list. A gain would reopen the Coppersmith row with a concrete block polynomial.
- **Why not covered (emulated match).**
  - "Farey small-height rational factor base x = u/v": `LEAD-ICP-coppersmith-smallroot-semaev`
    ("small-x factor base solved by LLL"), `LEAD-TRF-global-lift-small-height` (token "small
    height", but it concerns characteristic-0 lifts).
  - "rational reconstruction factor base for prime-field index calculus":
    `LEAD-ICP-algebraic-membership-factor-base` ("algebraic factor base ..."),
    `LEAD-ICP-lattice-ic-relation-construction`.
  - "projective small-height Coppersmith lattice for summation polynomials": Coppersmith row.
  - A grep for "Farey", "rational reconstruction", "u/v" and "half-gcd" finds nothing.
- **Prior.** About 97% no gain. It ranks last on information per hour, but it is cheap and it closes
  a named open branch.
- **Cost.** 1.5-2 h (census about 20 min; LLL probes about 1 h at dimension 30 or below).

---

## 4. Considered and dropped

| idea | field | reason dropped |
|:--|:--|:--|
| Prange or Stern information-set decoding on C_L(FB, kO) | coding theory | Prange is (k-1)-subset enumeration and Stern is the 4-list join. Already foreclosed ("information set decoding on elliptic codes", `LEAD-ICP-elliptic-code-list-decoding`; `LEAD-EXO-four-list-ktree-join`). |
| Gowers U^3 excess of the factor base as a relation-yield source | additive combinatorics | Relation counts are complexity-1 systems, controlled by U^2 = Fourier (generalized von Neumann, `recalled`). That is H-PSEUDO. Kept only as a leakage statistic (N2). |
| Approximate-homomorphism (BLR / Hyers-Ulam / BSG) transfer to F_p^+ or F_p^* | additive combinatorics | Coprime orders leave no nontrivial homomorphism. BLR acceptance above 1/\|H\| forces a Fourier correlation of chi o phi with a group character, which is a linear DL leak already owned by hnp-advice and H-PSEUDO. |
| GF(2)- or F_p-linear complexity of coordinate sequences such as lsb x([k]G) | coding / sequences | With prime period n, a non-constant sequence has linear complexity at least ord_n(q) (Blahut / cyclotomic cosets). For q = 2 the state DL lives in F_{2^ord_n(2)} (astronomical). For q = p it lives in mu_n of F_{p^k}, which is MOV in disguise. Lower bounds for EC generators are known (Hess-Shparlinski, `recalled`). |
| F_p^*-log or CRT relabelling of the alphabet for QTT | tensor networks | Symmetries (j = 0) give only constant-factor rank drops, while the reopen bar is sqrt(p). D3 shows the LOG-labelling bound is set by log(FB) anyway. |
| Bipartition or tree tensor networks over digits | tensor networks | Cut ranks are a permutation family of the QTT unfoldings, so the D3 logic applies unchanged. Enumerating all C(16,8) cuts at L = 8 is cheap but has no predicted signal. |
| Top-eigenvector (Green-function) DL from the public M | physics / spectral | M is p x p, and entries of a global eigenvector need global normalization. Power iteration costs Theta(p\|FB\|), above rho. Owned by holant ("Cayley graph spectrum ... reveals discrete logs"). |
| Classical dequantization (Tang-style) of Shor's f(a,b) = h(aP+bQ) | quantum-inspired | The matrix is circulant-like, and its rank is the Fourier support of h, so low rank means H-PSEUDO bias. |
| Kushilevitz-Mansour sparse Fourier search on 1_{small-x}([l]G) by membership queries | learning | Heavy coefficients sit at the random level, so 1/tau ~ n/log n queries. Covered by H-PSEUDO and hnp-advice. |
| Simulated annealing or QUBO for prime-field point decomposition | physics | No mechanism makes carry-circuit landscapes smoother than CDCL search. The SAT, XOR and CDCL(T) rows dominate the encoding family. |
| Minimal circuit size, OBDD size or compressor MDL of the toy DL table | complexity | The natural positive control (anomalous curve: Smart's attack is short) fails at reachable n. Structured circuits exceed the Shannon bound 2^n/n until n is around 30 or more. The instrument is invalid by construction (cf. N1). |
| Vieta jumping on the S_3 = 0 surface as a new x-only walk | number theory | The Vieta involution x1' = (sum of roots) - x1 is exactly Montgomery differential addition. Owned by x-only and negation-map walks. |
| Mixed E / quadratic-twist relations through F_{p^2} | algebraic geometry | E(F_p) and E^t(F_p) are distinct Frobenius eigenspaces. A mixed sum is not F_p-rational, so F_p-rational S_3 zeros are E-E-E or T-T-T. This is consistent with the H1 report's zero cross mass. |
| Points-in-small-boxes or incidence bounds (Stevens-de Zeeuw, Cilleruelo-Shparlinski) as a worst-case per-target yield cap | additive combinatorics | Useful only for \|FB\| much smaller than p^(1/2), where the expected count is already below 1. The empirical side is owned by `LEAD-ICE-decomposition-probability-audit`. |
| Algebraic decision-tree lower bounds with equality tests | complexity | Gives only log N (Strassen degree), and IC's power comes from the non-algebraic integer order of F_p. Lesson (iv) already shows the free-local-work escape. |
| SQ-dimension closure of the ML row as a stand-alone lead | learning | SQ hardness of {lsb(c l)} holds for any encoding, including the trivial Z/n and F_p^* (subexponential DL), so it cannot separate easy from hard groups. Kept only as the instrument-validity test D4. |

## 5. Sources

- **Internal (read this session):** paths listed in section 0, plus `tools/lead_atlas.py:599-629`,
  `knowledge/leads/ecdlp/**/LEAD-*.yaml` (forecloses and titles), and
  `knowledge/findings/KN-FIND-e7a3b1.md` (grep).
- **Recalled (pointers only, unverified this session):**
  - Kearns, "Efficient noise-tolerant learning from statistical queries" (JACM 1998);
  - Blum, Furst, Jackson, Kearns, Mansour, Rudich (STOC 1994), SQ dimension;
  - Shalev-Shwartz, Shamir, Shammah, "Failures of gradient-based deep learning" (ICML 2017);
  - Abbe, Sandon (2020), SGD beyond SQ;
  - Power et al., grokking (2022);
  - Akavia, Goldwasser, Safra (FOCS 2003);
  - Kushilevitz, Mansour (1993);
  - Green-Tao, generalized von Neumann / true complexity;
  - Kazeev, Khoromskij, Tyrtyshnikov, multilevel Toeplitz matrices in TT format (SIAM J. Sci.
    Comput. 2013);
  - Hess, Shparlinski, linear complexity of EC congruential generators (2005);
  - Joux-Lercier rational reconstruction;
  - Miyaji-Nakabayashi-Takano curves (2001).
