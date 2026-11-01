# Open-idea experiment designs (2026-10-31)

Design pass for every open idea in the ledger under the `design-experiment`
skill. An idea is **open** when its proposal record has `status: proposed`,
no `dominated_by`, and its `IDEA-*` id appears in no hypothesis or experiment
index. That query returned 11 ideas, all designed below.

Each design fixes: the sentence under test and its class, the arms and the
A/A / positive / negative controls, the variable ledger, seeds and blinding,
the primary metrics and their units, the stopping and invalidation rules, the
decision rule with its verdict vocabulary, and the falsifier. Machine-readable
records are in `protocols/`; validate with
`python3 tools/experiment_protocol.py validate <file>`.

**Status: designed, not approved, not run.** No data was taken; every protocol
records `filed_before_affected_data: true`.

## Index

| area | idea | design | protocol |
|:--|:--|:--|:--|
| WESO | `IDEA-20261016-397ac9` | Delgado 2^80 n^4 factor at n=256: does it enter the Theorem 5.3 runtime product? | `protocols/IDEA-20261016-397ac9.json` |
| WESO | `IDEA-20261016-cdb5e4` | Mixing citation vs total variation 2^-15 on the NIST-I row | `protocols/IDEA-20261016-cdb5e4.json` |
| WESO | `IDEA-20261016-fb1656` | Per-entry modular-polynomial cost against the NIST-I Delfs-Galbraith gap | `protocols/IDEA-20261016-fb1656.json` |
| SEMBIN | `IDEA-20261017-0e2dab` | Replicate the n=40, t=2, k=20 cell at 20x the z, sparse-f versus dense-f | `protocols/IDEA-20261017-0e2dab.json` |
| SEMBIN | `IDEA-20261017-3079bc` | Zero-background detector for intrinsic solution clustering at t=4..12 | `protocols/IDEA-20261017-3079bc.json` |
| SEMBIN | `IDEA-20261017-3db2a8` | Semaev yield is an exact first moment; Poisson link is second order | `protocols/IDEA-20261017-3db2a8.json` |
| SEMBIN | `IDEA-20261017-e9f824` | Does the 18-22% t=2 yield deficit transfer to the cost-relevant linear regime? | `protocols/IDEA-20261017-e9f824.json` |
| KIC | `IDEA-20261018-329d0a` | Frobenius-stable multiplicative-subgroup bases x^d=1 at prime degrees | `protocols/IDEA-20261018-329d0a.json` |
| KIC | `IDEA-20261018-5f37a1` | Log-blind golden bases: coverage is an order statistic of orbit-class occupancy | `protocols/IDEA-20261018-5f37a1.json` |
| KIC | `IDEA-20261018-d4cef4` | Universal Frobenius relations: the relation module is (delta) in Z[tau] | `protocols/IDEA-20261018-d4cef4.json` |
| KIC | `IDEA-20261018-f2cd4d` | Is the tau-Horner m! the symmetry-breaking m! in disguise? | `protocols/IDEA-20261018-f2cd4d.json` |

## IDEA-20261016-397ac9 — Delgado 2^80 n^4 factor at n=256: does it enter the Theorem 5.3 runtime product?

**Area:** WESO  
**Question:** At n=256, does the quoted 2^80 n^4 trial factor multiply the Theorem 5.3 expected-time product, or is it cancelled by a displayed identity?

**Hypothesis H1.** The 2^80 factor in Theorem 4.4 enters the Theorem 5.3 expected-time product at n=256.

*Mechanism.* 2^80 n^4 counts objects examined; substituting n=256 makes the trial factor 2^112, and one p^(1/3) pass multiplies it by about 2^85.

**Claims.**

- `C1` (exact computation): Two readers locate the introduction and cancellation of 2^80 from arXiv:2609.22018v1 Theorem 4.4 (p.16), Eq. 55 and the proof of Theorem 5.3 (p.22), and agree on the line and exponent.
- `C2` (comparative, decided by `C-present`): The 2^80 trial factor is present (not cancelled), so the n=256 product is >=2^197 and Heuristic 1 stays load-bearing below 2^128.

**Predictions.**

- `P1` `indicator` (2^80 present (1) or cancelled (0)): higher, minimum effect 1
- `P2` `log2_product` (log2 of the trial product at n=256): higher, minimum effect >=197
- `P3` `sheet_agreement` (reader agreement on page and cancellation line): equal_within, minimum effect 0 mismatches

**Arms.**

- `read-a` (reference): first independent reader, frozen reading sheet
- `read-b` (candidate): second independent reader, same sheet, same source tokens
- `quoted-2-50` (control_aa): second quoted constant (2^50 n^2) on the same sheet
- `pdf-tokens` (control_positive): PDF token check: the quoted 2^80 must be found verbatim
- `toy-smoothness` (control_negative): toy smoothness sample, which cannot decide a quoted constant

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `pdf-tokens` — the quoted 2^80 is located verbatim in the PDF tokens.
- Negative: `toy-smoothness` — null population {'description': 'toy smoothness samples that carry no information about a proof constant', 'generator': 'toy smoothness samples that carry no information about a proof constant', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `reader`: crossed — two independent readers on the same frozen PDF tokens
- `source`: fixed — one frozen PDF and its token extract
- `evidence`: crossed — varied by comparison C-present
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `indicator` (exact, 0/1): 1 if 2^80 multiplies the Theorem 5.3 product, 0 if cancelled by a displayed identity
- `log2_product` (derived, bits): 85.3 + 112 if the factor is present; else the exponent of the surviving product
- `sheet_agreement` (exact, count): page and cancellation line mismatches between the two independent sheets

**Sample size and stopping.**
- Instances 2, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: two readers x one sheet, plus the verbatim token check, then stop.

**Decision rule.**

C-present is supported when both readers place 2^80 inside the Theorem 5.3 product (indicator=1) with no sheet disagreement and log2_product>=197; if the proof cancels 2^80 by a displayed identity, indicator=0 and Heuristic 1 is not necessary for that write-up.

**Inadmissible.**

- substituting n=256 before locating the factor
- reading a secondary summary instead of the PDF tokens
- treating a cancelled factor as a proof of the unconditional algorithm

## IDEA-20261016-cdb5e4 — Mixing citation vs total variation 2^-15 on the NIST-I row

**Area:** WESO  
**Question:** Does the frozen proof display a walk length n with total-variation distance eps(n) < 2^-15 for the non-backtracking walk, or only n=O(log p)?

**Hypothesis H1.** The cited mixing results give no n with eps(n) < 2^-15 for the non-backtracking walk used by Algorithm 3.

*Mechanism.* A transferred success lower bound must keep at least half the uniform bound; the budget 2^-15 is half the reciprocal of the printed NIST-I ratio 2^14.

**Claims.**

- `C1` (exact computation): Every explicit (n, eps) pair is extracted from EUROCRYPT 2023 Lemma 14 and the Pizer/[37] citation, labelled by walk type and distance, with the minimum eps recorded.
- `C2` (comparative, decided by `C-budget`): No cited n displays eps(n) < 2^-15, so Lemma 3.5's uniform-curve probability is not yet attached to Algorithm 3 at the NIST-I row.

**Predictions.**

- `P1` `min_eps_log2` (minimum cited total-variation eps): lower, minimum effect >=2^-15
- `P2` `explicit_n` (number of explicit (n,eps) pairs with eps<2^-15): lower, minimum effect 0
- `P3` `separation` (simple vs non-backtracking rows kept separate): equal_within, minimum effect 0 mixed rows

**Arms.**

- `proof-read` (reference): frozen proof use of Lemma 14 and the Pizer citation
- `primary-cite` (candidate): EUROCRYPT 2023 Lemma 14 read from the primary source
- `citation-37` (control_aa): second citation [37] read on the same sheet
- `planted-eps` (control_positive): a displayed pair with eps=2^-16 must be detected
- `simple-walk` (control_negative): simple-random-walk bound, which does not bound Algorithm 3

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `planted-eps` — a planted (n, 2^-16) pair is recorded and classified.
- Negative: `simple-walk` — null population {'description': 'simple-random-walk mixing bounds, which are not bounds on the non-backtracking walk', 'generator': 'simple-random-walk mixing bounds, which are not bounds on the non-backtracking walk', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `source`: fixed — one frozen token extract
- `walk_type`: crossed — simple and non-backtracking on separate rows
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `min_eps_log2` (exact, bits): minimum over cited pairs of log2 eps on the non-backtracking row
- `explicit_n` (exact, count): cited n with eps(n)<2^-15 on the non-backtracking row
- `separation` (exact, count): rows where total variation, statistical distance or l2 are conflated, or walk types mixed

**Sample size and stopping.**
- Instances 2, replicates 1, warmups 0; family of 2 tests with holm correction.
- fixed: one extraction sheet per source, plus the planted pair, then stop.

**Decision rule.**

C-budget is supported when no non-backtracking pair reaches eps<2^-15 and the rows stay separated; a displayed pair with eps<2^-15 refutes it and the coupling keeps Lemma 3.5's bound positive.

**Inadmissible.**

- using a simple-random-walk bound as a bound on the non-backtracking walk
- conflating statistical distance, total variation and l2
- spectral computations (belong to IDEA-20260815-1cc763)

## IDEA-20261016-fb1656 — Per-entry modular-polynomial cost against the NIST-I Delfs-Galbraith gap

**Area:** WESO  
**Question:** At p=5*2^248-1 with B* from the Section 4.1 formulas, is the entry-weighted F_{p^2}-multiplication count c at least 2^Delta, where Delta is the recomputed gap to the Delfs-Galbraith line?

**Hypothesis H1.** The per-entry cost of the two named listing algorithms is at least the recomputed Delfs-Galbraith gap at p=5*2^248-1.

*Mechanism.* The print's rounding hides 21.5 bits at the exact prime; charging Phi_l once over Z and per batch decides whether the batched listing closes that gap.

**Claims.**

- `C1` (exact computation): c_direct and c_batched are counted with the schoolbook F_{p^2} multiplication unit on one frozen j-list, and Delta is recomputed at the exact prime, not read from the rounded row.
- `C2` (comparative, decided by `C-gap`): c >= 2^Delta, so the listing correction lifts the NIST-I time lower bound to at least the Delfs-Galbraith line under the Section 4.1 model.

**Predictions.**

- `P1` `log2_c` (log2 entry-weighted F_p^2 multiplications per new entry): higher, minimum effect >=Delta
- `P2` `delta` (recomputed gap in bits): higher, minimum effect 21.5 on the printed row
- `P3` `algorithm_split` (log2 split between direct and batched): different, minimum effect reported

**Arms.**

- `direct` (reference): direct: reduce Phi_l and find roots at one supersingular j
- `batched` (candidate): one batched multipoint evaluation of Phi_l, written down before timing
- `batch-aa` (control_aa): the direct arm repeated on a second j-subset
- `known-phi` (control_positive): a low-degree Phi_l whose root count is known by hand
- `toy-l` (control_negative): toy prime l whose entry cost cannot be 2^21.5, to prove the counter is not inflating

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `known-phi` — the counted root count matches the hand value.
- Negative: `toy-l` — null population {'description': 'a small prime l where the gap cannot be reached', 'generator': 'a small prime l where the gap cannot be reached', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `algorithm`: crossed — direct and batched on the same j-list
- `j_list`: fixed — frozen before counting
- `prime_size`: crossed — varied by comparison C-gap
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `log2_c` (counted, bits): entry-weighted F_p^2 multiplications of the better of the two named algorithms
- `delta` (derived, bits): log2(printed Delfs-Galbraith line) - log2(M/P0) at p=5*2^248-1
- `algorithm_split` (derived, bits): ratio of the two counted costs on the same j-list

**Sample size and stopping.**
- Instances 20, replicates 1, warmups 0; family of 1 tests with none correction.
- fixed: 20 j values x both algorithms, batched routine written before the count, then stop.

**Decision rule.**

C-gap is supported when log2_c>=delta at the recomputed prime; c<2^Delta falsifies the lift, and a 2^Delta split between the algorithms falsifies the one-sided label.

**Inadmissible.**

- timing before writing the batched algorithm down
- charging Phi_l per batch only
- using the printed 21.5 instead of the recomputed Delta

## IDEA-20261017-0e2dab — Replicate the n=40, t=2, k=20 cell at 20x the z, sparse-f versus dense-f

**Area:** SEMBIN  
**Question:** At n=40, k=20, does the sparse-f parity mixture give P=.316 (not .393) at 2000 z, with zero solutions whenever Tr(b/z)=1?

**Hypothesis H1.** At |V|=2^20 the parity confinement makes the n=40 success probability .316 on sparse f, not .393.

*Mechanism.* If f has second exponent s<=20 then Tr(alpha^j)=0 for j<n-s, so N(z)=0 for every z with Tr(b/z)=1; the surviving mass gives (1-e^{-2mu})/2=.316 at mu=.5.

**Claims.**

- `C1` (exact computation): N(z) is counted exactly for every z by exhaustive pushforward of V^2, split by Tr(b/z), and every table cell's instance band is recomputed from a(V).
- `C2` (comparative, decided by `C-window`): Sparse-f P lies in [.30,.33] and differs from the dense-f .393 arm by more than the exact-count interval.

**Predictions.**

- `P1` `p_sparse` (P on sparse f at k=20): lower, minimum effect .316+-.015
- `P2` `p_dense` (P on dense f (Tr(alpha)=1)): different, minimum effect .393+-.015
- `P3` `pi1_hits` (solutions at Tr(b/z)=1 with sparse f): lower, minimum effect exactly 0
- `P4` `band_violations` (Tables 1-2 cells outside their instance band): lower, minimum effect <=2 of 33 at 95%

**Arms.**

- `sparse-f` (candidate): n=40, k=20, sparse f with s<=20, 2000 uniform z
- `dense-f` (reference): n=40, k=20, dense f with Tr(alpha)=1, same 2000 z
- `sparse-aa` (control_aa): sparse-f rerun on a fresh z stream
- `n20-exhaustive` (control_positive): n=20, k=10 exhaustive pushforward already measured at RUN-SEMBIN-8be036
- `curve-free` (control_negative): curve-free random map at |V|=2^20 through the same z-loop; P=.393

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `n20-exhaustive` — the exhaustive n=20 pushforward reproduces its recorded hit profile.
- Negative: `curve-free` — null population {'description': 'curve-free random map with P=.393 at |V|=2^20', 'generator': 'curve-free random map with P=.393 at |V|=2^20', 'n': 1000, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `f_representation`: crossed — sparse and dense f on the same z stream
- `z_stream`: fixed — frozen before the count
- `tr_split`: measured — Tr(b/z) recorded per z
- `map`: crossed — varied by comparison C-window
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `p_sparse` (rate, probability): hits/2000 on the sparse-f arm with Wilson interval
- `p_dense` (rate, probability): hits/2000 on the dense-f arm with Wilson interval
- `pi1_hits` (exact, count): solutions at z with Tr(b/z)=1 under sparse f
- `band_violations` (exact, count): of the 33 Tables 1-2 cells, how many exp_prob falls outside the 95% instance band

**Sample size and stopping.**
- Instances 2000, replicates 1, warmups 0; family of 4 tests with holm correction.
- fixed: 2000 z per arm x two f representations, plus the n=20 and curve-free controls, then stop.

**Decision rule.**

C-f is supported when p_sparse in [.30,.33], p_dense in [.38,.41], pi1_hits=0 and <=4 band violations; sparse P outside [.30,.33] falsifies the parity mixture at |V|=2^20.

**Inadmissible.**

- matching MAGMA's unknown default f instead of bracketing both representations
- reading the result as a statement about Assumption 1 or any curve's security

## IDEA-20261017-3079bc — Zero-background detector for intrinsic solution clustering at t=4..12

**Area:** SEMBIN  
**Question:** With Poisson background <=1e-5, does the conditional extra-solution rate nu_t exceed the null at any cell t=4..12, and does the planted 2-torsion flip recover exactly 2^{t-1}-1?

**Hypothesis H1.** At |V|<=2^8 and t<=12 there is no intrinsic solution clustering beyond the stated multiset null.

*Mechanism.* Size-biased sampling makes the expected number of other solutions exactly nu_t=E[c(c-1)]/E[c]; with mu_class<=1e-5 any extra solution is far outside the Poisson background.

**Claims.**

- `C1` (exact computation): Extra-solution events are recounted by meet-in-the-middle over canonical multisets for 2e4 sampled targets per cell, so a single event is structure, not noise.
- `C2` (comparative, decided by `C-null`): nu_t stays within the null bound in every cell while the planted flip recovers 2^{t-1}-1, so no intrinsic clustering is detected in the tested box.

**Predictions.**

- `P1` `extra` (extra solutions per target minus null): equal_within, minimum effect 0 within the Poisson bound
- `P2` `planted` (planted flip nu): higher, minimum effect 2^{t-1}-1
- `P3` `nonrational` (non-rational share at t=4): lower, minimum effect <1% at |V|>=2^6

**Arms.**

- `window` (reference): Semaev window family, B=1 and random
- `random-subspace` (candidate): random subspace and random subspace inside ker Tr, same cells
- `window-aa` (control_aa): window family rerun on a fresh target stream
- `planted-flip` (control_positive): base V u b/V; nu must equal 2^{t-1}-1
- `curve-free` (control_negative): relabelled Z/N through the same pipeline; zero events expected

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `planted-flip` — nu equals 2^{t-1}-1 exactly.
- Negative: `curve-free` — null population {'description': 'relabelled Z/N group, where no curve coincidence exists', 'generator': 'relabelled Z/N group, where no curve coincidence exists', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `family`: crossed — window, random subspace, ker Tr subspace
- `t`: crossed — t in {4,6,8,10,12}
- `target_stream`: fixed — protocol-hash seeds, canonical multisets
- `group`: crossed — varied by comparison C-null
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `extra` (exact, count): recounted other x-multisets summing to +-R minus the null bound
- `planted` (exact, count): extra solutions on the planted 2-torsion flip arm
- `nonrational` (rate, fraction): share of single-polynomial solutions not rational at t=4

**Sample size and stopping.**
- Instances 5, replicates 1, warmups 0; family of 5 tests with holm correction.
- fixed: five (t,k) cells x four families x 2e4 targets, then stop.

**Decision rule.**

C-null is supported when the planted control is recovered, the curve-free control is empty, and no cell exceeds the null bound; a missed planted control voids every clean cell, and events above the null at >=2 cells with a common pattern establish clustering.

**Inadmissible.**

- calling a cell clean when the planted control was missed
- deduping repeated entries and P,-P pairs together
- extrapolating to |V|=2^38

## IDEA-20261017-3db2a8 — Semaev yield is an exact first moment; Poisson link is second order

**Area:** SEMBIN  
**Question:** Does the per-class mean equal d(V)*C(|W|+t-1,t)/N in toy cells, and does the crossover sensitivity read 2.9+-0.3 n per bit?

**Hypothesis H1.** The Semaev yield is the exact first moment d(V)*C(|W|+t-1,t)/N, and each yield constant is an additive theta bits in stage 1.

*Mechanism.* x-multiset decompositions of R_X correspond to point multisets of W summing to R up to O(1/N) coincidences; d(V)=h/|<cl(W)>| carries the class factor.

**Claims.**

- `C1` (exact computation): Stage 0 recomputes n_cross sensitivity from the frozen tables formulas; Stage 2 verifies by group enumeration that P in 4E iff Tr(u)=0 and counts d(V) on h=4 and h=2 curves.
- `C2` (comparative, decided by `C-exact`): The measured class mean matches the exact first moment within O(c/N) and the crossover sensitivity is 2.9+-0.3 n per bit.

**Predictions.**

- `P1` `class_mean_ratio` (class mean / exact first moment): equal_within, minimum effect 1 within O(c/N)
- `P2` `ncross_shift` (n_cross shift per bit of theta): equal_within, minimum effect 2.9+-0.3 n
- `P3` `gap` (relative gap P(A_t)-P(eq.5)): lower, minimum effect <=t/|V|

**Arms.**

- `frozen-counts` (reference): RUN-SEMBIN-8be036 per-R counts, read-only
- `class-mean` (candidate): pi=0 class mean against the exact first moment
- `counts-aa` (control_aa): frozen counts re-read under the second convention
- `h4-enumeration` (control_positive): n=11,13 h=4 curve: P in 4E iff Tr(u)=0 by group enumeration
- `h2-curve` (control_negative): h=2 curve (Tr(a)=1): d=1 for every V

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `h4-enumeration` — the Tr(u)=0 criterion reproduces the h=4 class split.
- Negative: `h2-curve` — null population {'description': 'h=2 curve where the class factor d is 1 for every V', 'generator': 'h=2 curve where the class factor d is 1 for every V', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `estimator`: crossed — overall mean, class mean, exact first moment
- `curve_h`: fixed — frozen fixtures
- `method`: crossed — varied by comparison C-exact
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `class_mean_ratio` (derived, ratio): measured pi=0 class mean divided by d(V)*C(|W|+t-1,t)/N
- `ncross_shift` (derived, n per bit): recomputed from the frozen tables.yaml formulas
- `gap` (derived, fraction): P(A_t)-P(eq.5) divided by P(A_t)

**Sample size and stopping.**
- Instances 2, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: Stage 0 arithmetic, Stage 1 frozen counts, Stage 2 two toy curves, then stop.

**Decision rule.**

C-exact is supported when the class mean matches the exact first moment within O(c/N), the h=2 control gives d=1, and the sensitivity is 2.9+-0.3 n per bit; a class mean outside O(c/N) falsifies C1.

**Inadmissible.**

- editing H-RELN-96e3ba or EXP-RELN-164ad3 instead of filing an additive amendment
- reading constants as a security claim

## IDEA-20261017-e9f824 — Does the 18-22% t=2 yield deficit transfer to the cost-relevant linear regime?

**Area:** SEMBIN  
**Question:** At fixed |V|=1024 and t=2, does the confinement dispersion factor f_disp track (1+e^{-mu})/2 from mu=.5 down to .0078, while the unconfined arm stays 1.000+-.005?

**Hypothesis H1.** The t=2 yield deficit is trace-parity confinement, and it vanishes as mu drops into the cost-relevant linear regime.

*Mechanism.* For V in ker Tr the per-target count is a 50/50 mixture of 0 and Poisson(2mu), giving f_disp=(1+e^{-mu})/2; intrinsic clustering would instead be flat at 1/kappa.

**Claims.**

- `C1` (exact computation): c(R) is exact for all targets by one exhaustive pushforward of V^2 into a 2^n count array, and f_disp is scored against the measured mu-hat, not the nominal rate.
- `C2` (comparative, decided by `C-form`): Confined f_disp tracks the closed form within .005 while the unconfined arm is flat at 1, so the 18-22% deficit is a saturation artifact and the clustering reading loses.

**Predictions.**

- `P1` `f_disp` (confined f_disp(mu-hat)): higher, minimum effect (1+e^{-mu})/2 within .005
- `P2` `f_disp_unconf` (unconfined f_disp): different, minimum effect 1.000+-.005
- `P3` `pi1` (pi=1 hit fraction, confined): lower, minimum effect exactly 0
- `P4` `vmr` (inside-class variance/mean): equal_within, minimum effect 1.00+-.03

**Arms.**

- `confined` (candidate): V random inside ker Tr, k=10, t=2
- `unconfined` (reference): unconfined random V, same n and t
- `confined-aa` (control_aa): confined arm rerun on a fresh V draw
- `mu-half` (control_positive): reproduce the recorded mu~.5 cells at .80 before any low-mu cell
- `curve-free` (control_negative): curve-free symmetric random map through the same pushforward; f_disp=1

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `mu-half` — the recorded mu~.5 f_disp .80 is reproduced.
- Negative: `curve-free` — null population {'description': 'curve-free symmetric random map with f_disp=1 at every mu', 'generator': 'curve-free symmetric random map with f_disp=1 at every mu', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `confinement`: crossed — ker Tr and unconfined V
- `n`: crossed — n=20..29 including prime n=23,29
- `mu_hat`: measured — measured mean per cell, not nominal
- `map`: crossed — varied by comparison C-form
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `f_disp` (derived, ratio): P/(1-e^{-mu-hat}) on the confined arm
- `f_disp_unconf` (derived, ratio): same ratio on the unconfined arm
- `pi1` (exact, fraction): hits in the Tr=1 class divided by all z
- `vmr` (derived, ratio): inside-class variance over mean at each mu-hat

**Sample size and stopping.**
- Instances 10, replicates 1, warmups 0; family of 4 tests with holm correction.
- fixed: n=20..29 x two confinement arms x two B values, plus the mu~.5 and curve-free controls, then stop.

**Decision rule.**

C-form is supported when confined f_disp tracks the closed form within .005, pi1=0, the unconfined arm is 1.000+-.005 and the mu~.5 control is reproduced; confined f_disp below .95 at mu<=.04 in >=2 cells establishes clustering.

**Inadmissible.**

- scoring against the nominal rate instead of mu-hat
- reading toy mu as a degree or security statement

## IDEA-20261018-329d0a — Frobenius-stable multiplicative-subgroup bases x^d=1 at prime degrees

**Area:** KIC  
**Question:** At n=23 and n=29, does B_d have coverage within 2 sd of the orbit-class null and a random stable union, with an O(n)-byte stable description at no more than 2x a random orbit seed's construction cost?

**Hypothesis H1.** Multiplicative-subgroup bases are a Frobenius-stable base lane at prime degrees where the stable-subspace lane is empty, with no coverage bias.

*Mechanism.* S_d is closed under squaring and, for b=1, under x->1/x; every non-identity orbit of <2,-1> on Z/d has size 2n, so the base has an O(1) description (n, modulus, d) and one exponentiation test.

**Claims.**

- `C1` (exact computation): The census (n<=200) is checked by multiplication and primality; S_d is generated by powers of a generator at one multiplication per element.
- `C2` (comparative, decided by `C-null`): B_d coverage matches the orbit-class null within 2 sd and construction cost stays within 2x a random orbit seed, so the multiplicative lane is a usable stable base.

**Predictions.**

- `P1` `coverage_z` (coverage z vs orbit-class null): different, minimum effect |z|<=2
- `P2` `gap_stable` (coverage gap to a random stable union): lower, minimum effect within 2 sd
- `P3` `cost_ratio` (construction cost vs random orbit seed): lower, minimum effect <=2x

**Arms.**

- `explicit-list` (reference): explicit list of equal class count
- `b-d` (candidate): B_d from S_d at n=23 (d=47,178481) and n=29 (d=2089,1103)
- `list-aa` (control_aa): second explicit list of equal class count
- `subspace-lane` (control_positive): the subspace lane at n=23, known to exist
- `relabelled` (control_negative): relabelled Z/r group with no multiplicative structure

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `subspace-lane` — the known n=23 subspace lane is enumerated and counted.
- Negative: `relabelled` — null population {'description': 'relabelled Z/r with no multiplicative structure', 'generator': 'relabelled Z/r with no multiplicative structure', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `base`: crossed — explicit-list, B_d, random stable union
- `n`: crossed — n=23 and n=29
- `m`: crossed — m=2 at n=23, m=3 at n=29
- `group`: crossed — varied by comparison C-null
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `coverage_z` (derived, sd): (observed coverage - null mean)/null sd
- `gap_stable` (derived, fraction): coverage difference from an equal-class-count random stable union
- `cost_ratio` (counted, ratio): charged field multiplications per accepted point over a random orbit seed

**Sample size and stopping.**
- Instances 4, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: census n<=200, then n=23 and n=29 enumeration, then stop.

**Decision rule.**

C-null is supported when |coverage_z|<=2, the stable-union gap is within 2 sd and cost_ratio<=2; coverage z beyond 3 for B_d but not for random stable unions means multiplicative closure biases S_3 solutions.

**Inadmissible.**

- large n=11 saturation cells as evidence
- claiming a SAT or attack result
- editing the balanced-base census by hand

## IDEA-20261018-5f37a1 — Log-blind golden bases: coverage is an order statistic of orbit-class occupancy

**Area:** KIC  
**Question:** On the frozen N19 pool of 66045 four-orbit bases, is the score sd 0.8-1.25 times the exact occupancy-null sd, and are the pool and plane winners within 1 sd of the selection-matched expected maximum?

**Hypothesis H1.** Coverage gained without discrete logarithms is an order statistic of the exact orbit-class occupancy null and carries no exploitable structure.

*Mechanism.* M_c m-sum classes thrown into N_c target classes give occupancy variance about N_c e^-lam(1-(1+lam)e^-lam); a log-blind pool search reaches mean + z(K_eff) sd, whereas the log-aware headroom min(1,lam) needs logs.

**Claims.**

- `C1` (exact computation): Stage 0 reads base_scores.json of RUN-KIC-234d11 and computes mean, sd, skew, max, min and the exact occupancy null under both counting conventions.
- `C2` (comparative, decided by `C-null`): The log-blind pool reaches at most 0.1 of the log-aware headroom while the log-aware greedy control sits at least 5 null sd above the mean.

**Predictions.**

- `P1` `sd_ratio` (score sd over null sd): different, minimum effect 0.8 to 1.25
- `P2` `winner_z` (winner z minus E[max of K_eff]): lower, minimum effect |z|<=1
- `P3` `headroom_share` (log-blind share of log-aware headroom): lower, minimum effect <=0.1

**Arms.**

- `frozen-null` (reference): exact occupancy null under the frozen counting convention
- `pool-scores` (candidate): 66045 N19 log-blind pool scores
- `null-aa` (control_aa): exact null under the second counting convention
- `log-aware` (control_positive): dlog-guided greedy base, expected 5 null sd above the mean
- `relabelled` (control_negative): 200 random 37-column pools in relabelled Z/r with scalar lambda

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `log-aware` — log-aware greedy reaches at least 5 null sd above the mean.
- Negative: `relabelled` — null population {'description': 'relabelled Z/r pools with the same exhaustive 4-of-37 search', 'generator': 'relabelled Z/r pools with the same exhaustive 4-of-37 search', 'n': 1000, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `base_selection`: crossed — frozen pool, random pools, log-aware greedy
- `counting_convention`: crossed — both conventions reported
- `n`: crossed — n=19 primary; n=17 and n=11 replication
- `group`: crossed — varied by comparison C-null
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `sd_ratio` (derived, ratio): sd of the 66045 N19 scores over the exact occupancy-null sd
- `winner_z` (derived, sd): winner z minus the selection-matched expected maximum
- `headroom_share` (derived, fraction): log-blind coverage gain over the log-aware headroom

**Sample size and stopping.**
- Instances 66045, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: Stage 0 the frozen 66045 scores, Stage 1 200 random pools, Stage 2 one log-aware greedy, then stop.

**Decision rule.**

C-null is supported when sd_ratio in [0.8,1.25], |winner_z|<=1 and headroom_share<=0.1; sd_ratio>=1.5 flags real structure whose source is then the finding.

**Inadmissible.**

- using an element-level null that treats the 2n images as independent
- reading coverage as yield (mean yield is conserved, KN-FIND-007)

## IDEA-20261018-d4cef4 — Universal Frobenius relations: the relation module is (delta) in Z[tau]

**Area:** KIC  
**Question:** At n<=23, does every found relation lie in (delta), and is the exact N_w within a factor 3 of the random-lattice count at every cell and weight w<=8?

**Hypothesis H1.** The relation module of a Koblitz orbit is the principal ideal (delta), and w_min marks where toy tau-stable cells become dimension-forced.

*Mechanism.* delta=sum_{j<n} tau^j has norm equal to the point-count ratio; Ann(G)=(delta), so every column relation is a multiple of delta and the minimum tau-adic weight controls duplicate class-sums.

**Claims.**

- `C1` (exact computation): N_w (w<=8) is enumerated by meet-in-the-middle and membership in (delta) is checked exactly in Z[tau]; the tau-NAF of delta is a planted positive at its predicted weight.
- `C2` (comparative, decided by `C-ideal`): The exact N_w is within a factor 3 of the random-lattice count and duplicate class-sums stay within floor+2 sd of the class null.

**Predictions.**

- `P1` `nw_ratio` (exact N_w over random-lattice count): equal_within, minimum effect factor 3
- `P2` `membership` (share of relations in (delta)): higher, minimum effect 1.0
- `P3` `dup_excess` (duplicate class-sums beyond class null): lower, minimum effect <=floor+2 sd

**Arms.**

- `random-lattice` (reference): random-lattice count for N_w
- `exact-mitm` (candidate): exact N_w by meet-in-the-middle from lambda
- `lambda-aa` (control_aa): random lambda' of order n mod r
- `tau-naf` (control_positive): tau-NAF(delta) must appear at its predicted weight
- `distinct-point` (control_negative): multiset convention, whose extra coincidences are not relations

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `tau-naf` — tau-NAF(delta) appears at its predicted weight.
- Negative: `distinct-point` — null population {'description': 'multiset convention whose coincidences are not algebraic relations', 'generator': 'multiset convention whose coincidences are not algebraic relations', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `method`: crossed — exact meet-in-the-middle vs random-lattice estimate
- `n`: crossed — K1 n=7,11,17,19,23; K0 n=7,13
- `weight`: crossed — w<=8
- `planted_relation`: crossed — varied by comparison C-ideal
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `nw_ratio` (counted, ratio): exact weight-w pattern count over the random-lattice estimate
- `membership` (exact, fraction): relations whose coefficient vector lies in (delta)
- `dup_excess` (derived, count): duplicate class-sums minus floor, in class-null sd

**Sample size and stopping.**
- Instances 8, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: eight cells x weights 1..8, then the two table duplicate counts, then stop.

**Decision rule.**

C-ideal is supported when membership=1, nw_ratio within factor 3 at every cell and weight, and dup_excess<=2 sd; a relation outside (delta) is an instrument error or a false Ann(G)=(delta).

**Inadmissible.**

- claiming anything at deployed n (w_min about 33-44 by hand estimate)
- mixing multiset and distinct-point conventions

## IDEA-20261018-f2cd4d — Is the tau-Horner m! the symmetry-breaking m! in disguise?

**Area:** KIC  
**Question:** At (n,m,l)=(17,2,8),(19,2,9),(17,3,6),(19,3,6), is conflicts per distinct relation for Horner over plain+lex-SB in [0.8,1.25], while plain+SB is about 1/m! of plain?

**Hypothesis H1.** In the exhaustive-core regime the tau-Horner chain's per-relation m! is the same m! that lex symmetry breaking already removes.

*Mechanism.* Plain+SB searches 2^(ml)/m! with B^m/(m! r) unordered solutions; Horner searches 2^(ml) with B^m/r ordered ones; both cost c 2^(ml) r/B^m per relation.

**Claims.**

- `C1` (exact computation): Distinct relations of plain (unordered) and Horner (ordered) are enumerated exactly per cell; MITM table sizes and probe counts come from the same enumeration.
- `C2` (comparative, decided by `C-sb`): Horner costs the same per distinct relation as plain+SB, so the tau-Horner m! is the symmetry-breaking m! and the two do not compose.

**Predictions.**

- `P1` `horner_ratio` (conflicts per distinct relation, Horner/plain+SB): equal_within, minimum effect 0.8 to 1.25
- `P2` `sb_gain` (conflicts per target, plain+SB/plain): lower, minimum effect about 1/m!
- `P3` `mitm_ratio` (ordered/unordered table size times probes): equal_within, minimum effect 1.0 within 10%

**Arms.**

- `plain` (reference): plain chain, no symmetry breaking
- `plain-sb` (baseline): plain chain with lex symmetry breaking
- `horner` (candidate): tau-Horner chain of IDEA-20260926-197ecf
- `plain-aa` (control_aa): plain rerun on a second recorded seed
- `sb-count` (control_positive): SB model count against the binomial count
- `relabelled` (control_negative): Z/NZ relabelled group with scalar of order n

**Controls.**
- A/A: comparison `C-aa`.
- Positive: `sb-count` — SB model count equals the binomial count.
- Negative: `relabelled` — null population {'description': 'relabelled Z/N group with a scalar of order n, where curve structure is absent', 'generator': 'relabelled Z/N group with a scalar of order n, where curve structure is absent', 'n': 100, 'why_n': 'enough independent null draws to resolve the stated alpha under the family correction; the null is exact where the proposal states an exact count, and sampled otherwise', 'matched_on': ['size', 'field and curve shape', 'instrument', 'seed law']}.

**Variable ledger.**

- `chain`: crossed — plain, plain+SB, Horner
- `solver`: crossed — CaDiCaL and WDSat default
- `cell`: crossed — four (n,m,l) cells
- `symmetry_breaking`: crossed — varied by comparison C-sb
- Instrument: fixed (one commit, flags and thread count per arm).
- Arm order: interleaved; seeds from the frozen protocol hash; analyst blinded.

**Metrics (primary).**

- `horner_ratio` (counted, ratio): pooled conflicts over pooled distinct relations, Horner over plain+SB
- `sb_gain` (counted, ratio): conflicts per target, plain over plain+SB
- `mitm_ratio` (derived, ratio): table size times probes per relation, ordered over unordered

**Sample size and stopping.**
- Instances 4, replicates 1, warmups 0; family of 3 tests with holm correction.
- fixed: four cells x three chain arms x two solvers, 200 targets per cell from a recorded seed, then stop.

**Decision rule.**

C-horner is supported when horner_ratio in [0.8,1.25], sb_gain about 1/m!, and mitm_ratio 1.0 within 10%; horner_ratio<=0.67 at two cells is a genuine structural gain.

**Inadmissible.**

- treating conflicts as a bound rather than search work
- changing the cells after seeing results
- reading the result as an exponent claim

