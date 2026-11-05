> **SCOPE CORRECTION (2026-10-31, later).** This file reviews the adjacent `prime_sat_*` regularity thread.
> The finding the owner named ("sub-exponential factor base tensor Boolean SAT solver for ECDLP index
> calculus") is the Akshima et al. (Bochum v0.2) hashed-factor-base ECDL with exact tensor contraction using
> the openai/math ETH counting backend, implemented as `cryptanalysis/experiments/hashed-ecdl-tensor-reference/`
> (binary ECC2K-130 and prime-field ECCp-131 via `tensor_prime.py`), with lead
> `LEAD-EXO-hashed-factor-base-tensor-ecdl`. The 40-80-bit path and ETH leads for THAT finding are in
> `HASHED_TENSOR_REVIEW.md` in this directory. Sections 3-4 and addendum A1/A3 below are secondary;
> **draft KR-2 (A1) is withdrawn as written**: `LEAD-ICB-decomposition-encoding-and-sat` and `KN-LIT-caa51d`
> already record a Tseitin-variable-count obstruction of the same kind, so any KR must extend those.

# Review: the tensor-regularity / Boolean-SAT finding for prime-field ECDLP index calculus

Date: 2026-10-31. Reviewer: Claude (session on SSD990-2). Scope: the `prime_sat_*`
thread in `crypto-autoresearcher/research/` (Oct 29–31, 2026), its reviews
(DEC-20261029-ce5c57, DEC-20261029-0857a9, DEC-20261029-266f95, DEC-20261029-76b793,
DEC-20261030-676356, DEC-20261031-430815, DEC-20261031-cd6460) and the measured
SAT follow-up EXP-PNEXT-624f41. Sources are cited by repository path.

## 0. One-paragraph verdict

The finding is real but much narrower than "sub-exponential factor base". What was
proved is a tensor-product Hilbert-series calculation of the *leading-form degree of
regularity* (Caminata–Gorla Def. 1.4 convention) of the two-summand Boolean-digit
Semaev system over F_p, plus two generator-presentation tricks that lower that number
(membership predicates: minus 1; one-hot pair grouping: s+1 instead of 1+3s/2). Nothing
in the thread is sub-exponential in anything: the local Boolean quotient keeps dimension
4^s in both presentations (`prime_sat_costbridge_20261029/cost-bridge.md` §1), the
producer's own Section D proves the grouped regularity G+1 is *independent of the
problem*, and the only SAT measurements (p=17, 97; s=2,3) show membership augmentation
*increasing* search work 2.7x. The thread's actual value is a correct, certified
encoding/checker stack for prime-field PDP and a clean statement of what would have to
be measured. The path to 40–80-bit prime fields is a measurement program for the
*exponent* of SAT-based PDP at arity 3–4, not a scaling of this theorem.

## 1. What the finding actually says (and what the reviews accepted)

| Object | Statement | Status |
|---|---|---|
| Baseline bit presentation F0 (2s Boolean vars, raw S3 quartic) | d_reg = s + ceil((s+2)/2) exactly, for p > s, nonzero weights; uses strong Lefschetz on k[z]/(z_i^2) (Phuong–Tran Thm 2.7) blockwise, then tensor ranks | accepted, DEC-ce5c57 |
| Membership predicates M_i (full 2^s truth table of "f(x_i) nonsquare") | d_reg(F1) <= d_reg(F0) - 1; same affine ideal | accepted, DEC-ce5c57; costs O(2^s log p) per domain |
| Single forbidden word D_i (one known nonsquare x in the window) | same -1, cost O(s), one length-s clause in CNF | unreviewed corollary (next-leads §C) |
| Grouped one-hot pairs Fg (3s vars, 6s local quadratics, raw S3) | d_reg(Fg) = s+1 exactly for even s; general upper bound G+1 | accepted, DEC-0857a9 |
| Solving-degree transfer | sd_sigma(Fg) <= s+2 in Salizzoni's mutant-closure convention | accepted as an *upper bound only* |
| Section D (producer's own warning) | for *any* Boolean system, raw one-hot grouping into G groups gives d_reg exactly G+1 | unreviewed, but elementary and correct |
| Three summands, disjoint domains, no rational 2-torsion | all lifts rational; d_reg(baseline) = 2s + ceil((s+4)/2), augmented -2 | unreviewed (next-leads §B) |
| Measured SAT (EXP-PNEXT-624f41) | quartic arm 69k field mults / 3,599 SAT candidates; membership arm 190k / 1,149; quadratic lift 5.4M; grouped arm **not run** | native checker failed (`invalid_output`), replay only |
| Fall-degree ladder (EV-PFDR-1394a4, EV-PFDR-99c699) | d_ff = m 2^{m-1} + floor((s-2^{m-1})/2) + 1, reproduced by a *curve-free* null; d_lf rises with s; sigma > 1 | replicated, toy tier |

All review joints "hold" within scope, and the custody is unusually clean. The reviews
are also honest that one reviewer per package is not a quorum and no novelty audit ran.

## 2. Review findings

### 2.1 The invariant is presentation-dependent, and Section D proves it measures nothing about hardness
The leading-form d_reg of a *listed generator set* can be driven to any value G+1 by
re-encoding Boolean variables as one-hot groups of width w (G = n/w groups), at the
price of 2^w - 1 variables per group. At w = s (one group per coordinate) you get
d_reg = 3 with 2^{s+1} variables, which is just the truth table. The grouped result
(w = 2) is the first step on exactly this curve. The accepted theorem is therefore a
correct computation of a quantity that trades degree for width at constant information:
(1+T)^{2s} and (1+3T)^s both have total dimension 4^s (cost-bridge §1). The
conclusion "lower regularity" should be read as "same object, different grading".
*Recommendation:* retire d_reg (generator convention) as a progress metric for this
thread. The presentation-independent quantities the lab already has are the last fall
degree (EV-PFDR-99c699: grows with s) and measured solver work.

### 2.2 Arity two can never matter, by the lab's own reference
Cost-bridge §2 gives the complete two-summand reference: enumerate D1, two square roots
and one group subtraction per x, K <= 2|D1| outputs, i.e. O(2^s log^2 p). Every
arity-2 SAT/Gröbner arm must be compared against that and cannot beat it by more than
polynomial factors, because the *output* can be 2^s points. Independently, index
calculus at arity 2 needs PDP cost below p^{1/2-1/2}/2! = O(1) to beat rho (see §3.1),
so arity 2 is structurally irrelevant to ECDLP. The thread knows this ("a two-summand
decomposition routine supplies no unknown scalar"), but the choice of arity 2 for every
accepted theorem means none of the accepted results touches the regime that matters.

### 2.3 The measured direction is negative, and the headline candidate is unmeasured
PNEXT: membership augmentation cut SAT candidates 3.1x but raised search field
multiplications 2.7x and added 8,480 field powers of construction; the degree-2 lambda
lift was 78x worse than the quartic. The grouped (one-hot) arm, the only one with an
accepted *larger* regularity drop, has never been run through a solver. Note also that
one-hot vs. binary ("direct vs. log") encodings are a 25-year-old SAT/CSP trade-off
(the next-leads file cites ICALP 2026 for the One-hot subsection); the prior is that
direct encodings propagate better for CDCL but do not change asymptotics.

### 2.4 Prime-field specific obstruction the thread sidesteps but does not solve
The theorems live in F_p[z]/(z^2-z): Boolean variables, field coefficients, no carries.
That is a strength (no bit-blasted modular multipliers), but it means the "Boolean SAT
solver" is necessarily a hybrid CDCL(T) with an F_p theory (the PC-certified MiniSat /
CaDiCaL external-propagator loop in `prime_sat_followup_20261029`,
`prime_sat_prefix_search_20261030`, or cvc5-ff / Yices MCSat from
`prime_sat_five_tests_20261029`). A pure CNF route needs log^2 p gates per field
multiplication; S3 chained at arity 3–4 needs tens of multiplications, so n grows to
thousands of auxiliaries and CDCL on multipliers is the classic worst case. The thread
should state which route it is on; today it is implicitly on the hybrid route, which
is the right one.

### 2.5 Things that are correct and worth keeping
- Rational-lift identity S3 = N^2 - 4t^2(x1+x2+r) and the complete enumeration formula
  with discriminant 16 t^2 f(x). This is the right certified reference and removes the
  algebraic-closure ambiguity in Kosters–Yeo for m = 2.
- Three-summand rationality via the "Frobenius sends non-rational lifts to negatives"
  argument with disjoint windows and no rational 2-torsion (next-leads §B). It is the
  correct way to make arity-3 relation certificates cheap and should be reviewed.
- The rationality circuits (`prime_sat_rationality_*_20261031`): nilpotent-square /
  slack / guard quadratic encodings of "f(x) is a square or zero" with 0,3,9,15,21,36
  auxiliaries for k = 0..5. These are what an arity >= 4 encoding needs (where
  non-rational pairs can cancel), and DEC-cd6460's F5 arity counterexample must be
  fixed before SAT integration.
- Forbidden-word clause (§C): the O(s) way to get the same -1 as the 2^s table.

### 2.6 Small gaps
- next-leads §A asserts exactness for the grouped list only for even s and raw S3;
  the reviewers derived odd s but it is outside accepted scope. For a sweep you need
  odd s; adopt the reviewer derivations formally.
- The p > s Lefschetz hypothesis is harmless for 40–80-bit fields but the proofs
  should say "characteristic p > s" rather than relying on 2^s <= p.
- No ledger hypothesis yet states the discriminating prediction for the grouped SAT
  arm. Without a pre-registered slope prediction the next run will be another
  "observations only" report.

## 3. Path to prime fields of 40–80 bits

### 3.1 First fix the target: what "works" means at 40–80 bits
Pollard rho on an 80-bit prime-order curve is 2^40 group operations, minutes on one
GPU. No index-calculus implementation will beat rho in wall clock at these sizes; the
purpose of 40–80 bits is to *measure the exponent* of SAT-based point decomposition
where instances are large enough to be non-toy and small enough to run ladders.

Accounting (prime field, factor base = x-window of 2^s values, arity m, s = log2(p)/m):
- relations needed ~ p^{1/m}; success probability per random target ~ 1/m!;
- if one PDP attempt costs 2^{e s} = p^{e/m}, the relation phase costs
  m! · p^{(1+e)/m}; linear algebra ~ p^{2/m} (sparse);
- beats rho iff (1+e)/m < 1/2, i.e. **e < m/2 - 1** (and m >= 5 for the linear algebra
  to fit under p^{1/2} without extra tricks).
- enumeration/MITM baselines give e = m-1 (naive) or e = ceil((m-1)/2)·... with memory.

So: m = 2 needs e < 0 (impossible); m = 3 needs e < 0.5; m = 4 needs e < 1; m = 5
needs e < 1.5. The measurable question is the slope e of log2(SAT work) against s at
fixed m, with primes drawn fresh per s. Nothing in the accepted theorems bounds e;
the Boolean quotient dimension 4^s per block pair corresponds to e = 2 at m = 2 and
suggests e = m - 1 for Gröbner-type closure, i.e. no better than enumeration.

### 3.2 Concrete parameter grid
| p bits | m = 3: s, |F| | m = 4: s, |F| | enumeration baseline per PDP (m=3 / m=4) |
|---|---|---|---|
| 40 | 13–14, 2^13 | 10, 2^10 | 2^27 / 2^30 |
| 56 | 18–19, 2^18 | 14, 2^14 | 2^37 / 2^42 |
| 64 | 21–22, 2^21 | 16, 2^16 | 2^43 / 2^48 |
| 80 | 26–27, 2^26 | 20, 2^20 | 2^53 / 2^60 |

A SAT arm is interesting only if its per-instance work at s = 14..20 extrapolates to a
slope e below the §3.1 threshold. Fit e on s = 6..14 first (p from 2^18 to 2^42 at
m = 3); that is already decisive and runs on one box.

### 3.3 Encoding to use (hybrid CDCL(T) over F_p)
1. Boolean skeleton: one-hot pairs (accepted grouped encoding) for each of the m
   windows: 3 indicators per 2 bits, three pairwise negative clauses per group, zero
   word allowed. Optionally the forbidden-word clause per window (O(s)).
2. Arithmetic: do **not** expand S_{m+1}. Chain S3 with intermediate x-coordinates and
   the quadratic lambda lift: for m = 3, variables t (= x(P1+P2)), lambda_1, lambda_2
   with lambda_1^2 = x1 + x2 + t, 2 y_t lambda_1 = N(x1,x2,t), and S3(t, x3, r) = 0
   via the same lift. All constraints are degree <= 2 over F_p; the field variables
   t, lambda, y_t are theory variables, not bits.
3. Rationality: at m = 3 use the disjoint-window + no-2-torsion theorem (next-leads §B)
   so no membership circuit is needed; at m = 4 add the reviewed guard/slack circuits
   for the two inner points (where non-rational pairs can cancel).
4. Solver: CaDiCaL external propagator with the PC-certified lemma learner already
   in `prime_sat_prefix_search_20261030`, or cvc5 finite-field theory, both with the
   exact-checker contract already written. Keep the complementary-point reference
   (cost-bridge §2 generalized to m-1 enumerated windows) as the control arm.
5. Certificate: the same projected-model + arithmetic-refutation transcript format;
   it already covers LSB-prefix cylinders. Arbitrary-literal learned clauses need the
   separate proof interface the prefix-adapter review flagged.

### 3.4 Experiment design (pre-register before running)
- Hypothesis: "On the hybrid grouped encoding at m = 3, log2(search field
  multiplications + theory calls) grows with slope e < 0.5 in s over s = 6..14." Null:
  e >= 1 (enumeration-like). Blocking controls: bit encoding without grouping;
  grouping with the S3 constraint replaced by a random quartic of the same shape
  (curve-free null, as in EV-PFDR-1394a4); forbidden-word on/off.
- Fresh primes per s (fix the pseudoreplication noted in EV-PFDR-99c699), 3 curves
  per prime, 32 targets per curve, success and UNSAT cells both counted; report UNSAT
  cells separately because 1 - 1/m! of targets have no decomposition and UNSAT proofs
  dominate relation-phase cost.
- Decision rule: slope with bootstrap CI entirely below the §3.1 threshold reopens
  the cost table; CI containing e = m-1 closes the SAT lane for prime fields at this
  encoding, in line with the existing LEAD-ICP-digit-presentation-solving-degree
  foreclosures.

### 3.5 What to stop doing
- No more arity-2 theorems or arity-2 SAT arms except as controls.
- No more leading-form d_reg comparisons as evidence; track last fall degree and work.
- Do not scale membership tables (2^s per window): the forbidden-word clause gives the
  same algebraic effect at O(s).

## 4. Leads connecting the (claimed) ETH refutation to index calculus

Status of the external result as of 2026-10-31: OpenAI (paper "The Exponential Time
Hypothesis is false", natural-language proof 16 Oct, Lean formalization 17 Oct) and,
per secondary reports, an Anthropic paper dated 26 Oct, claim a **deterministic**
algorithm counting satisfying assignments of any k-CNF in time
(n+m)^{O_k(1)} · 2^{n/(log n)^{1/2+o(1)}} and polynomial space; for m <= Dn the exponent
is O_{k,D}(n/sqrt(log n)). Technique per the abstract/overview: polynomial method
(clause -> polynomial equal to 1 on satisfying inputs), variable occurrences replaced by
parameter-dependent linear forms so the cube sum factorizes across variable groups once
shared integer measurements are fixed, the sum becomes a univariate H(T) recovered by
Hermite interpolation, inclusion–exclusion over coordinate sets, F2 parity tests with
expander codes and greedy test selection; Kintali's simplification lists
"sparsification, bounded occurrences, spectral replacement, rational interpolation".
Review by Impagliazzo, Paturi and Williams is in progress; one secondary source says the
Lean statement is slightly weaker than the paper's. **Treat as unverified.** Everything
below is conditional on it standing.

### 4.1 Direct use is dead on arrival (quantified)
The gain is a factor sqrt(log n) in the exponent denominator, and the exponent is in the
*total* variable count n of a fixed-width CNF. Bit-blasting the m = 3 chained system at
p = 2^42 needs field multipliers, so n is in the thousands; 2^{n/sqrt(log n)} with
n = 3000 is 2^{~900}, against an enumeration baseline of 2^28. For any n reachable at
40–80 bits, n/sqrt(log n) is n/3.3, a constant factor. No algorithm of this shape is a
PDP solver at cryptographic or even toy sizes.

### 4.2 Structural lead: the proof's "linear forms + group factorization" is the finding's tensor structure
The ETH algorithm's core move, replace each variable occurrence by a linear form in
shared parameters so the cube sum splits as a product over variable groups, is the same
move as the finding's L_i = sum_j a_ij z_ij with the quotient a tensor product over
blocks. The finding uses it to compute a Hilbert series; the ETH proof uses it to count.
Lead: **count** decompositions instead of deciding them. #PDP over the Boolean cube is
sum_z (1 - S3(L1(z), L2(z), r)^{p-1}) by Fermat; this is exactly identity (10) in
`proof.md`. The obstruction is explicit: the clause polynomials in k-SAT have degree k,
the Fermat indicator over F_p has degree 4(p-1). The polynomial method needs low degree
in the Boolean variables, and F_p arithmetic constraints are not low-degree Boolean
functions. This is the precise reason the technique does not transfer to prime-field
PDP, and it is worth recording as a known result in the ledger so it is not re-proposed.

### 4.3 Where it *does* transfer: the character-sum / histogram form, i.e. batch PDP
Replace the Fermat indicator by the additive character 1[S=0] = (1/p) sum_c omega^{cS}.
For injective windows, N_i(a) = #{z : L_i(z) = a} is 0/1, so the count collapses to
#{(a,b) in D1 x D2 : Q(a,b) = 0} with Q the quartic in the window values, which is the
cost-bridge enumeration again at m = 2. At m >= 3 the same rewriting gives the
convolution structure: let h(t) = #{(P1,P2) in F^2 : x(P1+P2) = t}; then relation counts
for all targets are convolutions of h with itself. That is the x-coordinate
meet-in-the-middle: a p^{2/m} table shared by all p^{1/m} targets. Asymptotically this
is p^{3/m} for the relation phase, below rho for m >= 7 but with p^{2/m} memory and the
m! yield constant; the lab already tracks it as LEAD-ICP-generic-table-decomposition.
The *new* angle from the ETH proof is deterministic interpolation of the whole count
polynomial H(T) in a target parameter: if the family of targets is parametrized as
R = R0 + [T]G, the number of decompositions as a function of T is what IC needs, and
amortizing one algebraic transform over all targets (as the finding already does for
the membership table M_i, O(s 2^s) per window shared across targets) is the only known
way to push work below per-target enumeration. Concrete sub-lead: a retained-setup
arm (LEAD-ICP-retained-setup-online) where the per-window transforms are the one-hot
group tables and the online per-target cost is measured separately.

### 4.4 Complexity-theoretic lead: the hardness floor is gone, not the cost
Kosters–Yeo show deciding whether S_r vanishes on inputs of the relevant shape is
NP-complete for large r; the lab's digit-presentation lane carried an implicit "Boolean
PDP is a SAT instance, so expect 2^{Omega(n)}" prior. If ETH is false, there is no
complexity barrier to 2^{o(s)} Boolean PDP in principle. The honest reading is that
this removes a reason for pessimism without providing a mechanism; the measured
negatives (last fall degree growing with s; curve-free null reproducing d_ff) stand.
Also note: the ETH refutation is for *fixed* clause width k; PDP as a Boolean function
of the bits has width 2s (every bit appears in L_i), and width-reduction via Tseitin is
exactly the variable blow-up of §4.1. "Fixed width" is the restriction that excludes
arithmetic constraints.

### 4.5 Sparsification + bounded occurrence vs. dense Semaev structure
The ETH proof first reduces to sparse 3-CNF with each variable in <= 3 clauses. Semaev
digit systems are maximally dense in the bits but depend on them only through m linear
forms. The analogous "bounded occurrence" normal form for F_p PDP is: m field unknowns
x_i, m interval constraints x_i in D_i, one polynomial S_{m+1}. The interval constraints
are where the Boolean structure lives; the polynomial is where the field lives. This
separation suggests the known small-roots framing (Coppersmith on S3 or chained S3 in a
box), already LEAD-ICP-coppersmith-smallroot-semaev; the known bound is that box sizes
near p^{1/m} per variable far exceed what lattice methods tolerate for degree-4
bivariate polynomials. No new mechanism; record as checked.

### 4.6 Parity and self-reducibility (minor)
#ETH false gives ⊕ETH false, so parity of the number of decompositions is cheap in the
same model; search reduces to decision with s·m oracle calls by fixing bits. This does
not change any exponent and is noted only so it is not proposed as a separate lead.

### 4.7 One genuinely open question the two threads share
Both the ETH proof (expander-code parity tests, greedy deterministic test selection)
and the grouped encoding (local one-hot replacement giving d_reg = G+1 regardless of the
problem) are *local replacement* schemes that change grading without changing the
solution set. Whether a local replacement can lower the *last fall degree* of the
Boolean-digit Semaev system, not just the leading-form regularity, is the one algebraic
question not yet measured. The ladder in §3.4 with d_lf instrumented on the grouped
system answers it at toy scale; EV-PFDR-99c699's framework applies unchanged.

## 5. Recommended next actions, in order
1. Pre-register the §3.4 hypothesis with slope thresholds e < 0.5 (m = 3) and run the
   s = 6..14 ladder on the hybrid grouped encoding with the curve-free null and the
   enumeration reference. This is the single discriminating experiment.
2. Promote the three-summand rationality derivation (next-leads §B) and the
   forbidden-word corollary (§C) through blind review; both are cheap and are
   prerequisites for step 1 at m = 3.
3. Fix the arity bug flagged in DEC-20261031-cd6460 before any m >= 4 SAT integration.
4. Record two known results: (a) leading-form d_reg is presentation-dependent and
   one-hot grouping makes it G+1 for any Boolean system (Section D); (b) the k-SAT
   polynomial method does not transfer to F_p PDP because the Fermat indicator has
   degree ~p (§4.2). Both prevent re-proposal.
5. Retire arity-2 arms except as controls; retire d_reg comparisons as evidence.

## Sources
- Repo: `crypto-autoresearcher/research/prime_sat_regularity_20261029/{proof,grouped-proof,next-leads,review-summary,grouped-review-summary}.md`;
  `prime_sat_costbridge_20261029/cost-bridge.md`; `prime_sat_followup_20261029/README.md`;
  `experiments/EXP-PNEXT-624f41/reports/run-20261029T1601Z/report.md`;
  `knowledge/leads/ecdlp/ic-prime/LEAD-ICP-digit-presentation-solving-degree.yaml`;
  `ledger/evidence/EV-PFDR-{1394a4,99c699}.yaml`; `ledger/decisions/DEC-20261031-{430815,cd6460}.yaml`.
- Caminata–Gorla, arXiv:2112.05579; Phuong–Tran, arXiv:2211.13548; Salizzoni, arXiv:2304.13485;
  Kosters–Yeo, arXiv:1503.08001; Petit–Kosters–Messeng PKC 2016.
- ETH claim coverage (secondary, unverified): alphaxiv abstract page for "The Exponential Time
  Hypothesis Is False"; johndcook.com/blog/2026/10/27/eth-false (Kintali simplification);
  Yahoo/BeInCrypto and FourWeekMBA reports naming Impagliazzo, Paturi, Williams as reviewers.

---

# Addendum (2026-10-31, later): results of four delegated Sonnet audits

## A1. Ledger audit: neither proposed known result is recorded
- There is no `ledger/known_results/`; KRs live in `knowledge/frontiers/ecdlp/<area>/KR-<AREA>-<6hex>.yaml`
  (fields: id, area, kind ∈ {known_bound, known_negative, known_mechanism, dispute, textbook_fact},
  title, claim, status ∈ {proven, heuristic, disputed, reported}, setting, sources[{ref, locator,
  verification_state}], forecloses[], internal[{ref, relation, note}], open[], dominated_by,
  added, superseded_by). Leads reference them via `known_results:`.
- KR-1 (d_reg presentation-dependence, G+1 for any Boolean system): **partially recorded**. Only the
  weaker `d_reg(full grouped list) <= G+1` is in DEC-20261029-0857a9 (`scoped_claim.general_full_upper_bound`);
  the universal-equality statement exists only as unreviewed next-leads §D, and the conclusion
  "d_reg in this convention is not a hardness measure" appears nowhere in knowledge/ or ledger/.
- KR-2 (k-SAT polynomial method does not transfer to F_p PDP; Fermat indicator degree ~p; character-sum
  form collapses to x-enumeration/MITM): **not recorded**. Nearest neighbours are binary-field only
  (LEAD-ICB-decomposition-encoding-and-sat, LEAD-EXO-hashed-factor-base-tensor-ecdl with KN-LIT-caa51d)
  and LEAD-ICP-generic-table-decomposition for the MITM half.
- Draft KR entries (not written to the repo; owner to place under `knowledge/frontiers/ecdlp/index-calculus/`):

```yaml
# KR-IC-<new>.yaml
kind: known_negative
status: proven
title: Leading-form degree of regularity is presentation-dependent; one-hot grouping forces G+1
claim: >-
  For any Boolean polynomial system over a field with no nonzero constant generator, replacing
  each width-w group of bits (w>=2) by 2^w-1 mutually exclusive indicators and substituting the
  bit projections into every original polynomial (no local reduction) gives a raw generator list
  whose Caminata-Gorla Definition 1.4 degree of regularity is exactly G+1, G = number of groups.
  The local quotient keeps dimension 2^n. Hence a lower d_reg in this convention is a regrading,
  not evidence of lower solving cost; the elliptic S3 case (1+3s/2 -> s+1) is an instance.
setting: {field: any}
forecloses:
  - leading-form d_reg reduction by variable re-encoding presented as a hardness reduction
  - one-hot / indicator encodings of Boolean Semaev systems as a complexity improvement per se
internal:
  - {ref: DEC-20261029-0857a9, relation: extends, note: accepted <=G+1 and exact S3 case}
  - {ref: research/prime_sat_regularity_20261029/next-leads.md#D, relation: rederived}
```
```yaml
# KR-IC-<new>.yaml
kind: known_negative
status: proven
title: The k-CNF polynomial-method counter does not transfer to prime-field point decomposition
claim: >-
  Subexponential #k-SAT via the polynomial method (clause -> degree-O(1) polynomial, cube sum
  factorized across variable groups, univariate Hermite interpolation) requires the product
  polynomial to have degree linear in n. The Boolean indicator of S(x_1..x_m)=0 over F_p is
  1 - S^(p-1), of degree ~deg(S)*(p-1) in the field, so the interpolation degree and point count
  scale with p. The additive-character rewriting 1[S=0] = (1/p) sum_c w^{cS} removes the degree
  but, for injective digit windows, reduces the count to #{a in D_1 x ... x D_m : S(a)=0}, i.e.
  window enumeration / x-coordinate meet-in-the-middle. Tseitin width reduction of F_p arithmetic
  inflates n by the multiplier circuit size, so the fixed-width theorem gives no 2^{o(s)} PDP.
setting: {field: prime}
forecloses:
  - direct application of the ETH-refutation counting algorithm to Semaev point decomposition over F_p
  - Fermat-indicator polynomial-method counting of Boolean-digit decompositions
internal:
  - {ref: research/prime_sat_regularity_20261029/proof.md#5 eq (10), relation: extends}
  - {ref: LEAD-ICP-generic-table-decomposition, relation: extends, note: MITM half}
```

## A2. Odd s: the grouped theorem holds at every s (reviewer-derived, hand-checked at s=3)
Both blind reviewers (TASK-f78b3b, TASK-9c92f8) derived, with no disagreement on values:
- s odd, a = (s+1)/2, G = 2a (one singleton group per coordinate): d_reg(F_grouped, raw) = 2a+1 = s+2
  exactly; baseline d_reg(F_bit) = s+a+1; gap floor(s/2). Counts: 3s−1 variables, 6s−4 local quadratics.
- Local Hilbert series (1+3T)^{s−1}(1+T)^2. Lower bound: kill X_g in each width-2 group (functional
  or quotient); every X-pair involves a width-2 group, so X²Y² vanishes while degree G survives.
- Locally reduced S3 list: equality survives for s >= 3 (normal form keeps 4(ΣX_gX_h)(ΣY_gY_h) ≠ 0
  since p > 3). Control: {u²−u, v²−v, u²v²} vs {…, uv} share an affine ideal but have thresholds 3 vs 2.
- s = 2: raw d_reg = 3 (below input degree 4, so Salizzoni Prop. 3.13 does not apply; Prop. 3.10 gives sd <= 4).
- General width w: only the upper bound G+1 is in the sources. The reviewer-side agent observed the
  lower-bound argument seems to extend to any w >= 2 (dim V_g >= 3 >= 2); unreviewed.
- Hand check s = 3: per block (1+3T)(1+T); total 1+8T+22T²+24T³+9T⁴; X²Y² is one nonzero element of
  A_4 (dim 9) so quotient has dim 8 in degree 4 and 0 in degree 5: d_reg = 5 = s+2. Baseline bidegree
  (2,3) survives, (3,3) dies: d_reg = 6 = s+a+1. Matches.
Consequence for §3.4: the ladder can use every s = 6..14; no even-s restriction. The odd-s statement
above is ledger-ready modulo one check: the producer `grouped-proof.md` was not re-read against it.

## A3. ETH refutation: primary-source facts (replaces the secondary-source framing of §4)
Read directly: OpenAI paper PDF (github.com/openai/math, dated 17 Oct, revised 25 Oct), the Lean
doc `lean/docs/378.md`, O'Donnell's CMU exposition (30 Oct). Anthropic's paper (hexagonmath.org/2610.00577v1,
Lean at github.com/anthropics/formal-math …/eth) and Kintali's simplification were reachable only as abstracts/aggregators.
- **Theorem 1.1 (OpenAI).** Deterministic exact #k-CNF, fixed k >= 2: (n+m)^{O_k(1)} · 2^{O_k(n log log n/√log n)}
  bit operations, poly space; for m <= Dn: 2^{O_{k,D}(n/√log n)}. Appendix D proves both via
  **tensor contraction**; the rational-interpolation route (§6.4) gives only n(log log n)²/√log n.
- **Lean statement is weaker**: stated in encoding length L, exponent (log log n)², and the m <= Dn
  refinement is not formalized. Fortnow confirms.
- **Technique.** Bounded-occurrence 3-CNF core (each variable in <= 3 clauses) so the clause-product
  polynomial has degree <= 3n (linear degree is what interpolation needs). Each occurrence of X_v is
  replaced by a linear form ⟨P_{e,v}(T), X⟩ with deg P <= R; H(T) = Σ_x Π_e Φ_e, H(0) = #F,
  deg H <= 3nR. At Q evaluation points, variables are split into r groups and clauses see other groups
  only through shared integer measurements y_g = C_g x_g; fixing y factorizes the cube sum into
  per-group sums, so H(t) = Σ_y Π_g B_g(y_g). Taylor data of H(t+z) is obtained by inclusion–exclusion
  and H recovered by Hermite interpolation. The measurement matrices come from an eigenbasis
  construction M0 = V0 f(W0) on commuting cube involutions (the "spectral replacement"); parameters
  r ~ √log n/(log log n)², Q ~ log n/log log n, R ~ √log n. Derandomized by conditional expectations.
  The better exponent avoids variable copying by turning a leaf formula into O(n) sparse F2 parity
  tests (Tanner/expander code on the clause-violation vector + greedy tests), then Beigel–Tarui
  polynomials mod 2^l. O'Donnell reframes the whole thing as a sparse-permanent algorithm
  (O(1) nonzeros per row/column, Hermite interpolation of per(A(t)) at Θ(log n/log log n) points).
- **Transfer (authors' words).** "we need a reduction in the other direction, from that problem to
  fixed-width SAT, that controls the number of variables." 2^{o(n)} does not survive general
  polynomial-time reductions; unrestricted-width CNF-SAT and OVC-based lower bounds are not refuted.
- **Status.** Williams (27 Oct): "claimed refutation", independent examination with Impagliazzo and
  Paturi, "not certification". Fortnow: "safe to assume ETH is toast" without having checked. No bug
  reported as of 31 Oct. Anthropic's bound as reported: deterministic 2^{O(n log log n/√log n)} for
  #3-SAT, same shape as OpenAI's general bound.

**Effect on the leads in §4.** All six leads stand; two sharpen.
- §4.2 is strengthened: the algorithm's hard requirement is a clause-product polynomial of degree
  O(n) over a *bounded-occurrence* formula. F_p constraints violate both: the Fermat indicator has
  degree ~p, and every window bit occurs in the linear form of every S3 it feeds. This is the content
  of draft KR-2 above.
- §4.3 is sharpened: the actual engine is tensor contraction over a group-factorized sum, with the
  cross-group coupling pushed into low-rank "measurements". The finding's block-tensor structure is
  the same shape with *zero* cross-group coupling except through S3. The one place IC could borrow
  the idea is amortization over a target family R(T) = R0 + [T]G: interpolate the relation-count
  polynomial in T once per window transform instead of deciding per target. Cost model unknown; it
  belongs behind the §3.4 ladder, not ahead of it.
- O'Donnell's permanent view suggests a cleaner negative: #PDP over digit windows is a permanent-like
  sum only if the constraint factorizes per variable, which S3 does not (it couples L1, L2 quartically).

## A4. Solver inventory: what exists, what the m=3 ladder needs (with one correction)
Existing code (lines): prefix_search/engine.py 359, driver.py 284, check.py 218; followup/encoding.py 354,
coefficients.py 512, driver.py 128; five_tests/core.py 195, sat/solver.py 301; costbridge/reference.py 213,
check_reference.py 167; rationality_software/circuits.py 90, rationality.py 209; prefix_adapter/adapter.py 254.
- Backends: CaDiCaL195 via PySAT IPASIR-UP external propagator (prefix_search), MiniSat22 learner loop
  (followup, five_tests), cvc5 QF_FF and Z3 as tiny-p oracles only. Theory lemmas are polynomial-calculus
  refutations with multiplier certificates, rechecked online and offline; UNKNOWN emits no clause.
- Encodings today: quartic, membership, quadratic lambda lift, reversed quadratic. **All arity 2, all
  binary digits.** No module emits the grouped one-hot encoding; no module implements arity 3 or S4.
- Hard limits that break at 2^18..2^42: `driver.select_cells` scans O(p²) for targets; `encoding.census`
  and `verify_search` are 2^n exhaustive (legacy verify path); `membership.from_values` is a 2^n truth
  table; `coefficients.py` loops over p³. `reference.solve` is O(|D1| log p) and fine. Arithmetic is
  pure-Python big-int everywhere (correct at 42 bits, slow). PC refuter is O(n) per row.
- **Correction to the agent's sizing.** It modelled "one-hot" as one indicator per window *value*
  (3·2^s variables, ~49k at s=14) and called the refuter's O(n)-per-row scaling the biggest risk. The
  accepted grouped encoding is one-hot over *bit pairs*: 3 indicators per pair, 3s/2 variables per
  window, so n ≈ 3·(3s/2) + log p (for t) + 2 log p (lambdas) ≈ 63 + 126 ≈ 190 at s = 14, p = 2^42.
  The refuter scaling concern is minor; the real cost centre is the field-variable blocks t, lambda_1,
  lambda_2 (binary, log p bits each, with `< p` domain CNF), as in the existing quadratic arm.
- New components for the m = 3 ladder (agent estimate, adjusted): grouped emitter ~100 lines;
  chained-S3 builder (two lambda lifts plus intermediate t, non-2-torsion checks at both steps) ~150–200;
  two-window enumeration reference + checker ~200 (2^{2s} pow calls: feasible in pure Python only to
  s ≈ 10–11; needs a C/Rust or numpy path for s = 12–14); transcript/adapter generalization (prefix
  cylinders over indicator groups; multi-block aux domain) ~150–250; target selection via Tonelli
  instead of the O(p²) scan plus per-cell resource caps ~80–120. Total ~700–900 lines on a 3,030-line base.
- Admission chain (from AGENTS.md and READMEs): frozen `experiment.protocol/v1` with controls and
  variable ledger; new EXP-* contract (EXP-PSEARCH-3ea9fe is the precedent; its README says the curve
  run "is a separate admission"); `tools/experiment_preapproval.py --packet` must report `approvable: true`
  and `tools/newest_experiments.py` must show `execution_state: ready`; drivers require `launch.json`
  and `environment.json` and refuse overwrite; `.resume/RESUME.md` fully filled and pushed to
  `s3://setec-astronomy-artifacts/checkpoints/...` via `scripts/checkpoint.sh` before any launcher runs.

## A5. Updated next actions
1. File the two KRs above (A1) and the odd-s statement (A2) through the normal review route.
2. Write the m = 3 hybrid ladder spec against the A4 component list, with the one-hot-over-pairs
   encoding and binary t/lambda blocks; pre-register slope threshold e < 0.5 and the curve-free null.
3. Replace `select_cells` and add the two-window reference first; they gate everything else.
4. Keep the ETH material as context only until the Impagliazzo–Paturi–Williams examination reports.
