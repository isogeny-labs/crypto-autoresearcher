# Review: the hashed-factor-base tensor-contraction ECDL (Akshima et al., Bochum v0.2) for prime fields of 40–80 bits

Date: 2026-10-31. This is the review of the finding the owner named: a sub-exponential factor-base index
calculus that encodes relation finding as a compact low-degree Boolean network and counts/solves it by exact
tensor contraction, using the openai/math ETH-refutation counting backend. It supersedes the scope of
`REVIEW.md` (which covers the adjacent `prime_sat_*` regularity thread).
Sources: Bochum manuscript (pinned 1ee44e56, primary PDF read by a delegated agent, quotes verified there);
`cryptanalysis/experiments/hashed-ecdl-tensor-reference/` (README, TENSOR_IMPLEMENTATION, PORT_STATUS,
prime-development/README); `cryptanalysis/docs/hashed-ecdl-audit-20261029/README.md`;
`crypto/problems/hashed-ecdl-tensor-backend.md`; `LEAD-EXO-hashed-factor-base-tensor-ecdl`;
`LEAD-ICB-decomposition-encoding-and-sat`; `KN-LIT-caa51d`; compile statistics measured this session
(`hashed_tensor_compile_stats.json`, 21 rows, compile-only, nothing contracted or solved).

## 0. Verdict

The algorithm is a real, carefully argued conditional theorem, and the engineering (prime port, ECCp-131
network, 39 correctness tests, OpenSSL cross-checks) is sound. It cannot be extended to 40–80 bits in any
useful sense, for three independent reasons, the first of which is encoding-independent:

1. **Information floor.** The counting cost is 2^(N/√log N) in the number N of Boolean variables, and N is at
   least the number of unknown input bits, mℓ for m slots carrying full ℓ-bit coordinates. Beating rho needs
   N/√log2 N below (1/2 − 1/m)ℓ. With every hidden constant set to 1 this first holds at ℓ about 2^254
   (best case m = 4). That matches the lab's own audit, which finds equality at log2 b = 256. Section F3 shows
   that the three possible re-encodings (full coordinates, index unknowns with one big vertex, index unknowns
   with split vertices) all stay above rho, so no re-encoding changes it.
2. **Measured constants.** The real network has 1,500–3,100 variables per bit per slot. The counting exponent
   is then 1,500–5,500 times rho's at every size from 40 to 131 bits (table in §2).
3. **Size floor in the proofs.** Bochum footnote 4: the saving appears only for networks of size at least
   2^(2^17); below that an internal parameter u0 = floor(b/2^17) is zero and the algorithm "falls back to
   brute force". The two simplified proofs state far larger thresholds (section 5b): at least 2^(3·10^7) for
   Kintali's, and n above about 10^10,000 for Anthropic's. Every compiled network at 40–131 bits has lambda = 19–22 and u0 = 0. So at these sizes the
   "tensor solver" is the exact-summation fallback, and no measurement of it is evidence about the theorem.

So the "path to 40–80 bits" is not an extension of the theorem but a measurement program with a predicted
null, plus a small number of leads that change which quantity is counted (§4).

## 1. The finding, from the primary text

- Prime field only (p > 3, prime order r, b = ceil(log p)); no binary-field version in the manuscript. The
  repository's ECC2K-130 tensor reference is a separate adaptation.
- m points per decomposition (the repository calls it "slots"). Hash-selected factor base per slot:
  F_i = {A : H_i(enc A) < tau}, H_i affine mod a prime s in [2p, 4p], tau about s·max(r^(1/m), 10m)/(r−1).
  Pairwise independence is proved (Lemma 9), not assumed. Coverage >= 2/5 per target (Lemma 10).
- Network per decomposition query: O(mb) edges, maximum degree O(b^(3/4)) (Lemma 11); integer multiplication
  by a two-stage Fourier construction: fewer than 1100(d+1) edges, degree below 136(d+1)^(3/4) (Thm 3).
  Modular reduction is checked (guess quotient, verify xy = theta·q + z, z < q), not computed.
- Cost: per attempt 2^O(mb/√log b) (Lemma 1 with s = O(mb)); (N+1) relations with N = sum |F_i| about
  m·r^(1/m); linear algebra O(N^3) over F_r. Total 2^O(b/m + mb/√log b); with m = ceil((log b)^(1/4)) this is
  2^O(b/(log b)^(1/4)). The theorem is stated for b >= 2^16 and is explicitly conditional on "Theorem 2"
  (a simplification of Theorem D.1 of the OpenAI preprint), which the authors did not verify and which is not
  peer reviewed. It states it "does not imply improved concrete attacks" (P-256, Ed25519).
- The constant-locality / preimage-counting corollary of the OpenAI paper is not used. Only the degree <= s^0.9
  tensor-network form (D.1) with polynomial-time predicates is needed. `KN-LIT-caa51d` already says the
  locality corollary does not apply to descended summation polynomials; its actual obstruction is the Tseitin
  variable count N = Theta(l^2) against omega(l sqrt(log l)). Bochum's Fourier encoding escapes that count
  asymptotically (F1), which is the point any extension of the record must address.

## 2. Findings

**F1. The earlier lab obstruction is escaped asymptotically and reinstated by constants.**
`LEAD-ICB-decomposition-encoding-and-sat` and `KN-LIT-caa51d` argue that a Tseitin encoding of field
multiplications has N = Theta(ℓ²) variables, which is omega(ℓ√log ℓ), so the counting bound loses to
enumeration. Bochum's Fourier construction makes N = Theta(mb), so that specific argument does not apply to
this algorithm; `LEAD-EXO` is right to ask whether it does. The answer is that the asymptotic form of the
obstruction is gone but the constant form holds: measured N = 170,440 at ℓ = 40, m = 2.

**F2. Measured network sizes and the corrected exponent comparison.**
Variables N of the compiled prime-field relation network (random prime-order curves from SEA point counting;
statistics from the encoder's own formula, checked against a real compile at ℓ = 40, m = 2: 412,452 edges,
degree 520; ℓ = 131, m = 2 reproduces the recorded 654,523 variables, 1,564,506 edges, degree 1,032).
E = N/√log2 N is the counting exponent with all hidden constants set to 1. rho is ℓ/2.

| ell | m | N | E = N/√log2 N | E / rho | b/m | paper-model unit-constant exponent b/m + mb/√log2 b |
|---|---|---|---|---|---|---|
| 40 | 2 | 170,440 | 40,885 | 2,044 | 20.0 | 55 |
| 40 | 4 | 422,644 | 97,764 | 4,888 | 10.0 | 79 |
| 56 | 2 | 181,988 | 43,536 | 1,555 | 28.0 | 75 |
| 64 | 2 | 199,204 | 47,478 | 1,484 | 32.0 | 84 |
| 64 | 4 | 486,952 | 112,029 | 3,501 | 16.0 | 121 |
| 80 | 2 | 338,352 | 78,947 | 1,974 | 40.0 | 104 |
| 80 | 4 | 839,020 | 189,138 | 4,728 | 20.0 | 147 |
| 131 | 2 | 654,523 | 148,909 | 2,273 | 65.5 | 164 |
| 131 | 4 | 1,622,421 | 357,205 | 5,454 | 32.8 | 231 |

All 21 rows (ℓ = 40..131, m = 2..4) are in the JSON. A delegated measurement agent labelled a column
"log2 of the bound" and concluded the bound sits below rho; that compared a logarithm of the exponent with the
exponent and is wrong. The table above is the corrected comparison.
Scaling: N/m ≈ 715·ℓ^1.24 over ℓ = 40–131 (piecewise, with jumps where the Fourier ring or transform length
changes); cost is affine in m, N(m) = F + m·S with S = 126,102 (ℓ = 40) and 483,949 (ℓ = 131). Multiplications:
10 fixed plus 28 per slot. Max degree 520 for ℓ <= 56 and 1,032 above.

**F3. The information floor is encoding-independent (new, closed form).**
Let m slots carry full ℓ-bit coordinates, so N >= mℓ. Beating rho needs total exponent below ℓ/2. Relations
cost about 2^(ℓ/m) attempts, so the per-attempt exponent must be below (1/2 − 1/m)ℓ. Therefore

    mℓ/√log2(mℓ) <= N/√log2 N < (1/2 − 1/m)ℓ   ==>   √log2(mℓ) > 2m²/(m−2).

The right side is minimised at m = 4 (value 16), requiring log2(4ℓ) > 256, ℓ > 2^254. This is the rigorous
form of the lab audit's "equality at L = 256". It is a necessary condition for networks whose unknowns are the
mℓ coordinate bits. Three encodings must be ruled out for it to cover "any re-encoding":

- **(a) Full coordinates (the Bochum design).** N >= mℓ, as above.
- **(b) Index unknowns, one vertex for the group law.** Take the unknowns to be the indices j_i into the explicit
  hashed lists (about ℓ/m bits each, about ℓ in total), with the predicate "point j of F_i" computed by
  inverse-hash enumeration, and one vertex of fan-in about ℓ checking the sum. Two obstructions.
  First, the degree hypothesis (<= s^0.9) forces padding to s about ℓ^(10/9) edges, so E = s/√log2 s is about
  0.6–0.65ℓ for ℓ = 40..80, which must sit below (1/2 − 1/m)ℓ < ℓ/2. It fails for every m, not marginally.
  Second, unpadded, the counter reaches this vertex's tensor only through entry evaluations (the manuscript's
  hypothesis is "polynomial description size and predicate evaluation time"; to be confirmed against the text of
  Theorem D.1). Exactly counting a predicate known only by evaluation needs 2^ℓ evaluations in the worst case,
  worse than meet-in-the-middle at 2^(ℓ/2). So unit constants are not a favourable assumption in this regime,
  they are an impossible one.
- **(c) Index unknowns, split vertices.** Breaking the group law into bounded fan-in vertices forces
  intermediate ℓ-bit partial sums onto edges, so N >= roughly mℓ again and (a) applies.

With (a)–(c) written out, the closure "no re-encoding of this algorithm beats rho below ℓ about 2^254 at unit
constants" is defensible. It is a necessary-condition argument for this algorithm family, not a proof that no
other mechanism works.

**F4. Why m = 2 is structurally dead, and what the lab's threshold means.**
Per-attempt cost A, N_rel about m·r^(1/m) relations, constant success probability per attempt:
relation phase about m·2^(ℓ/m)·A, beating rho (2^(ℓ/2)) iff A < 2^((1/2 − 1/m)ℓ)/m. In the lab's per-unit
language (field 2^(mλ) with factor base 2^λ per slot, ℓ = mλ) this is exactly alpha < m/2 − 1, the threshold in
`LEAD-ICB-decomposition-encoding-and-sat`. m = 2 gives A < 1/2: impossible. Linear algebra also constrains m:
dense elimination O(N_rel^3) = 2^(3ℓ/m) needs m > 6; sparse (Wiedemann) 2^(2ℓ/m) needs m > 4. Bochum's text
says the elimination term is "dominated" by b/m; that holds only inside the O() with m growing.
(Reconciliation with the sibling sweep's Lean-proved `rho_floor` is in §3.)

**F5. What exists to measure is tiny, and the exact-leaf algorithm is plain enumeration.**
- Python reference, ECCp-131, 2 slots: 654,523 variables, default u0 = 0, exact summation exceeds the
  2,000,000-operation budget, no relation found. Hashed-factor-base enumeration at 131 bits needs
  157,481,772,803,551,985,380 candidates, over the 200,000 preflight limit.
- Native Rust crate (about 12,000 lines, any size via BigUint, no u128 limit): a 40–80-bit prime curve is
  runnable in principle (`hashed-ecdl solve` then `verify`, with a certified full group order), but is not
  feasible today. A 3-bit curve (p = 7) takes 90–290 s and p = 17 exhausts its resource limits after about 700 s.
- The u0 = 0 exact leaf is odometer enumeration over the free input bits of the built-in program, worst case
  2^(#free inputs) program evaluations with conservative dependency-based block skipping. It is not variable
  elimination or dynamic programming. So any "exact summation" number at 40–80 bits is brute force on the
  free bits, and the recursive kernel is inactive (lambda <= 64, u0 = 0).
- The frozen 84-case panel is not a 40–80-bit panel. It covers three curves of 3–5 bits (p = 5, 7, 17), 2 slots,
  and its two arms are two builds of the same native crate (baseline d188c5a vs a candidate with bounded u64
  primality and single-pass witness search), not two index-calculus backends. No matched rho in ecbench's counted
  unit exists: the s/rho, s/applicable-floor and common-operation ratios are null. Blockers: checkpoint push and
  gate fail (no AWS profile or upload token), no digest-pinned native image, a missing `gawk`, and a frozen
  1800 s deadline against a sizing estimate of about 179 hours.
- Measured data: only contended diagnostics, for example one p = 7 row with 738,715,758 charged steps over
  308,775 functional assignments. No free-bit counts per leaf and no scaling in variable count.

**F6. Correctness status of the implementation.** Scalar (ell = 1) contraction only; the general truncated
V-polynomial case is not implemented, which is all Theorem 2 needs. Independent audit of packet packing, mode
orientation, precision loss, degree/shrink invariants and construction-cost accounting is open
(`crypto/problems/hashed-ecdl-tensor-backend.md`). Tests are correctness diagnostics with no performance
claim. The producer and certificate verifier share curve arithmetic; OpenSSL gives an independent arithmetic
check only.

## 3. Reconciliation of thresholds across the lab

| Source | Statement | Same threshold? |
|---|---|---|
| `LEAD-ICB-...` | per-attempt exponent alpha < m/2 − 1 per unit lambda, field 2^(mλ) | Yes, derived in F4 |
| Bochum audit doc | unit-constant exponent 2b/L^(1/4) vs b/2 equal at L = 256 | Yes, F3 reproduces it from N >= mℓ |
| Sibling sweep Lean `rho_floor` | oracle must be m√p times cheaper than enumeration of its own candidate set | To be reconciled; see below |

Reconciliation of `rho_floor` (PrimePdpEncoding.lean lines 153–159, docstring 20–28, read by a delegated agent):
m summands, p field size, l = log2 |F|, c the per-target oracle cost, s with s·s <= p. Product law: success per
target 2^(ml)/(m!·p), 2^l relations, total W = m!·p·c/2^((m−1)l). Theorem: 2^((m−1)l) <= c·m·s implies W >= s.
Its "enumeration of its own candidate set" T_enum is exhaustive probes per target with the last summand found by
lookup, so it enumerates (m−1)-tuples (cost about p/B), which is the reading I inferred from the pilot scale.
Under that reading the theorem and the lab's alpha < m/2 − 1 are the same relation-phase threshold:
with p = 2^(ml), the sufficient condition c >= 2^((m/2−1)l)/m. Caveats from the check:

- Exact threshold is c < 2^((m−1)l)/(m!·√p). The theorem uses m where it should carry m!, so it is sound but loose;
  the docstring's "m√p cheaper" omits a 1/(m−1)! factor.
- "Independent of l" holds for the T_enum-relative form at fixed p; the absolute budget scales as 2^((m/2−1)l).
  The product law needs 2^(ml) <= p. At m = 2 the budget is below one operation.
- The lab's measured alpha about m (WDSat "reproducing 2^(3l)/3!") is full m-tuple enumeration without lookup;
  the sweep and the Lean T_enum use lookup, alpha = m−1. Name the baseline when comparing: measured SAT is a
  further factor 2^l worse than T_enum.
- Neither threshold includes linear algebra. Sparse elimination is about m·2^(2l) against rho 2^(ml/2): it ties
  at m = 4 and fails at m = 3, so alpha < m/2 − 1 is necessary but not sufficient for m = 3, 4. (This agrees with
  my F4 statement that sparse elimination needs m > 4.)
- Also ignored: rho's √(πn/4) constant and the Hasse correction.

## 3b. What a 40-bit solve costs today through the existing hashed backend

The compile statistics record `relation_backend: meet_in_middle` and, at ℓ = 40, m = 2, factor-base size
803,464 per slot with 803,464 table entries and 803,464 query entries; generic rho is 2^19.94 group additions.
Collecting N+1 about 1.6 million relations at constant success probability (expected about 5 attempts each) costs
about 8·10^6 attempts × 8·10^5 lookups ≈ 6·10^12 lookups ≈ 2^42.5, against rho's 2^20. That is feasible in a few
core-hours and structurally about 2^22 times slower than rho, with the tensor backend contributing nothing at
this size. This is a derivation from the recorded table sizes and the manuscript's success probabilities, not a
measurement; the frozen panel is what would measure it. At ℓ = 80 the same formula gives about 2^83 against
rho's 2^40, out of reach.

## 4. Path to 40–80-bit prime fields

The code already compiles networks at any prime size (the work is in building the instance and running the
contraction). What is missing is not size support but a regime where the theorem's algorithm is active. So the
plan is a measurement program.

**P0. Close the question in writing (no compute).** File F3, with cases (a)–(c), as a negative extending
`LEAD-ICB-decomposition-encoding-and-sat` and `KN-LIT-caa51d` (units: unit-constant crossover ℓ about 2^254,
real-constant ratio 1,500–5,500 at 40–131 bits). It adds what those records lack: the obstruction survives the
Fourier encoding that escapes the Tseitin-count argument. Draft in `KR_DRAFTS.md`; this replaces the withdrawn
draft KR-2.

**P1. One audit that closes F3(b).** Read Theorem D.1's degree and description-size hypotheses in the OpenAI
paper and confirm that vertex tensors are accessed only through entry evaluation. If so, F3(b) is closed.
If vertex tensors may be supplied in a structured form (for example as products), rerun the estimate.

**P2. Measure the exact-summation fallback honestly at 40–80 bits.** Compile at ℓ = 40, 48, 56, 64, 72, 80
with m = 2, 3, 4 (m >= 5 needs encoder support). The native leaf is plain enumeration over free bits, so
"budget exhausted" carries no information about structure. Replace it by structural estimates:
(i) greedy-ordering contraction width of the compiled network, (ii) a model-counter run (d4/sharpSAT-class) on
the CNF export of the ℓ = 40 network, (iii) the free-input-bit count per leaf, which the native crate does not
record today and is the quantity the enumeration cost is 2 to the power of.
Pre-register that the result is compared in ecbench's counted unit against matched rho and against hashed
factor base with meet-in-the-middle over explicit lists (`LEAD-ICP-generic-table-decomposition`).
Prediction: all three exceed rho by orders of magnitude; the measurement fixes constants.

**P3. Forced-small recursion constants ladder.** The native crate and the Python reference can run the
recursive kernel with marked experimental parameters. Sweep (r, epsilon) on synthetic bounded-fan-in arithmetic
networks of growing size and record the smallest n at which recursion beats direct summation. Extrapolate to
n = 2·10^5–10^6. The result is an empirical "effective 2^17" for the algorithm as implemented.

**P4. Build the 40–80-bit panel; the frozen one does not cover it.** The frozen 84-case panel is 3–5-bit curves
comparing two builds of one crate. A 40–80-bit panel (ℓ in {40..80}, m in {2,3,4}) with matched rho in ecbench's
counted unit and the two baselines above is new work, and needs the checkpoint transport that is currently
unavailable. Do not launch from this study; it needs the Coordinator's approval, the RESUME/S3
checkpoint and the native launch receipt per AGENTS.md.

**P5. Do not duplicate the sibling sweep.** The prime-field PDP SAT sweep in
`crypto-worktrees/prime-pdp-sat-sweep-20261031` already covers CDCL on direct digit windows. Its pilot is the
pure-CNF baseline for P2.

## 5. Leads connecting the ETH refutation to a generalized solver or speed-up for index calculus

Stated against the primary facts: OpenAI Theorem 1.1 (deterministic exact #k-CNF in
(n+m)^O(1)·2^O(n log log n/√log n); m <= Dn gives n/√log n), proved by tensor contraction with replacement
linear forms, group-factorised cube sums and Hermite recovery; the Lean statement is weaker; the Bochum use
needs only Theorem D.1.

1. **Index-valued unknowns (F3(b)).** Reduces N to about ℓ and removes arithmetic from the network, but fails
   twice: the degree hypothesis forces padding to about 0.6ℓ against a requirement below 0.5ℓ, and unpadded the
   counter needs 2^ℓ evaluations. Recorded as closed pending the P1 reading.
2. **Shrink the arithmetic.** Fourier arithmetic costs 2,000–3,000 variables per bit per slot. A Semaev-style
   x-only constraint replaces point addition by one polynomial; chained S3 needs about 7 multiplications per slot
   instead of 28. That is a constant of about 4 against a requirement of 1,500+, and F3(a) says N >= mℓ anyway.
   At 40–80 bits the Fourier network is also no smaller than schoolbook Tseitin would be: about 250,000
   variables per extra slot at ℓ = 80 against about 28·ℓ² ≈ 179,000.
3. **Treat the counting backend as a library and measure its crossover (P3).** If the effective floor is orders
   of magnitude below 2^(2^17), the algorithm is a practical tool for CNFs of a few hundred thousand variables
   with no ECDLP link. If it is not, the Bochum result is permanently galactic. This is the experiment that
   decides whether "ETH is false" has any engineering consequence for index calculus.
4. **Amortisation over targets.** One transform shared by all targets would help, but the relation count as a
   function of the target is a group-ring convolution whose Fourier transform needs the discrete logarithm.
   Closed; recorded so it is not re-proposed.
5. **Sparse-permanent view (O'Donnell).** The algorithm is a permanent algorithm for matrices with O(1)
   nonzeros per row and column. The index calculus linear algebra step is a sparse determinant-style solve mod r,
   already polynomial. No gain.
6. **Locality-bounded steps.** The bounded-locality preimage-counting corollary applies to maps whose output bits
   read O(1) input bits. Descended summation polynomials are dense in the unknown bits (`LEAD-ICB`). A concrete
   measurement: monomials per equation of descended S_(m+1) as a function of (m, ℓ, basis). Only a basis giving
   polylog monomials would reopen it. Cheap, symbolic, no compute budget.
7. **What ETH-falsity does change.** No 2^Omega(n) lower bound can be assumed for any SAT step in a cost model
   (already recorded in `KN-LIT-caa51d`). It removes a barrier, not a mechanism. F3 shows the barrier was not the
   binding one.

## 5b. Remaining sources, read 2026-10-31 (late), including both PDFs

Primary texts were extracted with `pdftotext` and read by a delegated agent; figures below are its extraction.

- **Kintali, "A simplified proof of ETH is false" (26 Oct).** Theorem 1.1: for every fixed ε > 0 a deterministic
  algorithm decides 3-SAT in C_ε (n+m+1)^(c_ε) 2^(εn) bit operations. It is built from Proposition 1.4 (s >= 64,
  exact counting for 3-CNFs with at most 3 occurrences per variable) with rate
  a_s = H2(3/s) + 5/s + 2 s^(-6) log2(2 s^(2^(s^4)) + 1). Parameters (4.1): r = s groups, Q = s^4 nodes, R = s^3,
  τ = s^(-6), D = s·2^(Q). **The construction is valid only for N >= N0(s) = max{12 D², 2 Q r²}, which is
  12 s² 2^(2 s⁴) for s >= 64, already above 2^(3·10^7)**; below that it does exhaustive search, absorbed into
  C_ε. Since a_s > 5/s, s > 10·B/ε, so the threshold is 2^(Θ(s⁴)) = 2^(poly(1/ε)). The paper says only "All
  constants depending on s may be large." It declares AI assistance and claims only the decision theorem.
- **Anthropic, "A 2^o(n) time algorithm for 3-SAT" (26 Oct; Hexagon v1 27 Oct).** Theorem 1: deterministic #k-SAT in
  2^O(min{k·m/√log m, k²·n·log log n/√log n}) on a word RAM, k part of the input, absolute O-constant not given.
  Method is an eight-square-identity recursion over levels (K_{l+1} = 9 K_l^16, K_1 >= 9·2^96), unrelated to
  OpenAI's interpolation. **The paper states the result is purely asymptotic: for m = 5n it beats 2^n only when
  n > 10^10,000, and for the n-only bound only when n > 10^(10^8)** (Appendix D: log n > 8.5·10^9). Below
  thresholds such as n < K_0^17 it tries all assignments. Appendix E: the Lean statements are `ETHIsFalse` and
  `MainTheorem` on Mathlib's multi-stack Turing machine (Lean 4.33.1), the time-bound constant is named but not
  valued, the input encoding is fixed, RAM simulation is not in Lean, and the Lean proof is "a different proof of
  the same statement" (1,050 modules, three standard axioms, Comparator/nanoda). "At the time of writing no person
  is known to have checked it." The two proofs are different methods that reach the same shape of bound.
- **Reconciliation with the Bochum footnote.** Bochum cites 2^(2^17) for the OpenAI proof's internal parameter
  u0 = floor(b/2^17). Those two PDFs give far larger sizes for the regimes where the saving is real: at least
  2^(3·10^7) for the simplified proof and about 10^10,000 for Anthropic's. The OpenAI paper's own threshold was not
  re-read here; the point stands either way, because every compiled network at 40–131 bits has 1.7·10^5 to 3·10^6
  variables, below every one of these.
- **Fortnow (blog, 10/29 update).** Has not verified; "safe to assume ... toast". Lean bound "slightly weaker". No
  bug named. A commenter reports an exponential-time subroutine below a huge threshold, consistent with the above.
- **Review status.** Impagliazzo, Paturi and Williams are examining OpenAI's claim; their statement says this is
  not certification. No public bug or gap by 2026-10-31. Anthropic repository issue #36 asks whether the Lean
  `ETHIsFalse` statement means ETH; it reports no technical defect.
- **Press.** Scientific American gives no bound and quotes no complexity-theorist skepticism. Science returned 403.
- **Still not read:** Williams's own posts, aiweekly, cellcog.

Effect on this review: the conclusions harden. Every source describes the saving as asymptotic and size-thresholded,
with thresholds from 2^(2^17) up to 10^(10^8), against networks of at most a few million variables.

## 6. Reliability of this review

- Primary text of the Bochum manuscript was read by a delegated agent from the pinned PDF; the quotes are its
  verbatim extraction and I have not re-read the PDF myself.
- The OpenAI paper is conditional and unverified by the community as of 2026-10-31 (reviewers Impagliazzo,
  Paturi, Williams).
- All exponent comparisons set hidden constants to 1, which favours the algorithm. The measured variable
  counts are formula output from the encoder, cross-checked by one real compile.
- F3 is a clean necessary condition; it is not a proof that no other mechanism works.
- Nothing here was executed against the sibling sweep or the frozen panel.
