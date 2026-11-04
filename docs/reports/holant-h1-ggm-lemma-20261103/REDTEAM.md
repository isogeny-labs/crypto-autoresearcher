# Red-team review: Holant lead step (a) note (H1 lemma and transfer-matrix correction)

Reviewer: Red Team, Claude Opus 5.5, 2026-11-03. This review challenges the note. It decides nothing:
the Coordinator and the Validator decide and record. Nothing in the note, the scripts or the repo
was edited.

## 0. What was reviewed, and its status

These files were reviewed by content hash. They are scratch files, not committed evidence:

| file | sha256 |
|:--|:--|
| README.md | cd8ad7e5cbdce74f7b36639e99871687fd574925edb028fd7f36048d660e6bad |
| check_transfer.py | 605409fb4dfad700ff8675d6eba2614faca02e8e4192ca2ec3d19320c264993f |
| check_O.py | bc37e0936ed197223dfacf33440e603d67b4adaedb9fea64f5f2f19acfa3be5c |
| transfer_spectrum.json | e4484c78cbb53b7990894aca351e5caccdcea01a5e45b2eb4cc57a1559240c00 |
| o_vertex_control.json | c49c34758fbef08e2f6b55d5d5e0d7e42675bbd3b8b6c46e0b64b7f699441c66 |

* Repo context: `/home/user/crypto-autoresearcher`, sparse clone, main @ 9b721d74.
* Out of scope: four files appeared in this directory at 16:59, after the dispatch. They are
  `figures.py`, `preview.png`, `preview.typ` and `spectrum-interlacing.svg`, and were not
  reviewed. `figures.py` plots the p=101 curve only, and its title states the odd-n interlacing
  claim.
* Durability: none of these files is committed, so none is durable evidence yet. The note can
  land only as a commit containing these exact bytes.
* Reproduction: both producer scripts were rerun from a copy. They reproduce
  `transfer_spectrum.json` and `o_vertex_control.json` byte for byte; the hashes match the table.

## 1. Verdicts

| item | verdict | one line |
|:--|:--|:--|
| 1. Lemma 3 | **holds-with-restatement** | The reduction is sound, but the lemma is much weaker than the truth. The quantifier invites the wrong reading, the anomalous detour is unnecessary, and the sign step is miscounted. |
| 2. Lemmas 1–2 / H1 | **holds-with-restatement** | Lemma 1 is right as a count of oracle queries but leaves the time cost unpriced. Lemma 2's "only way" is wrong: under a label-indexed reading H1 is literally true (verified, ≤ 4 queries per entry) and gives a real but narrow bound. The repo's "structured GGM" reading gives no bound at all. |
| 3. Transfer matrix | **holds-with-restatement for odd n; fails for even n; fails for degenerate spectra** | Exact for odd n (21/21 extra configurations). It fails for even n (3/3 curves, interlacing violated). "Not equal / eigenvectors not characters" is false for j=0 with a ζ-stable FB (11/11 curves: 2/3 of the spectrum equals character sums exactly). |
| 4. Wider implication | **holds; understated and under-cited** | The row's x-oracle closure rests on Shoup through a simulability premise that fails, and nothing in the row scopes it to survive. The row is already contradicted by records it cites itself (KN-FIND-194294, and EV-GGM-002, which supersedes EV-GGM-001). The note should flag it and cite those records, not present Lemma 3 as the discovery. |

## 2. Findings, ordered by severity

Each finding is tagged as **wrong**, **unsupported** or **unpriced**.

### F1 (high; unsupported, in the row, flagged too weakly by the note): the augmented-oracle row contradicts its own citations

* **Evidence.** `knowledge/leads/ecdlp/exotic/LEAD-EXO-augmented-oracle-ggm.yaml`, lines 13–15
  and 19–21, verbatim:
  > 13–15: "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving
  > equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at
  > exponent 1/2 (KN-FIND-002, KN-FIND-b7e091, KN-FIND-194294; EV-GGM-001 strong)."

  > 19–21: revisit_when "A publicly computable oracle that is NOT GGM-simulable is exhibited
  > (the threshold oracle is the minimal non-simulable identifier, KN-FIND-982fdf, but needs
  > private data)."

* **Which oracles "named" covers.** The named oracles include the x-oracle. The title (line 4)
  is "Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence)". The
  mechanism (line 6) begins "x-coordinate, y-coordinate, full point, …". The row's `forecloses`
  list includes "x-coordinate oracle meet in the middle", "y-coordinate oracle guided
  decomposition" and "full-point oracle".
* **The records the row cites already break it:**
  * `knowledge/findings/KN-FIND-194294.md` (cited on line 15), lines 25–26: "O_D inherits the
    classification of O_x: it is NON-SIMULABLE (Tier 3) in the GGM sense." Lines 40–42: "The
    x-oracle-alone sub-rho question is OPEN". It defines O_x : Q ↦ x(Q) (line 19), which is the
    note's X. So the row cites a record saying x and halving are non-simulable, inside a sentence
    asserting that each named oracle is simulable.
  * `ledger/evidence/EV-GGM-002.yaml` supersedes EV-GGM-001 (line 3). It declares the run set
    "EVIDENTIALLY VOID with respect to H-GGM-001" and states: "THE CLOSURE LANGUAGE OF EV-GGM-001
    IS NOT CARRIED FORWARD. 'Closure at exponent 1/2' … appear nowhere in this record and are not
    supported by it." The row still cites "EV-GGM-001 strong".
  * `ledger/evidence/EV-ECDLP-048824.yaml`, CC-3, says KN-FIND-002 closes jet and endomorphism
    at 1/2 "WHILE declaring the structured GGM as its model … no lower bound can be certified in
    the structured GGM because Shoup theorem does not hold there, and the producer own
    anomalous-curve control demonstrates it." So the anomalous-curve witness behind Lemma 3 is
    already on record in the repo.
  * `knowledge/findings/KN-FIND-002.md`, lines 81–84: "The classification uses the structured
    GGM (curve equation is public) … Under the strictest GGM, jet and endomorphism would be
    NON-SIMULABLE because they require coordinate access." Coordinate access is therefore what
    "structured" adds, so the note's "*If* coordinates of instance points are available in that
    model" can drop the "if".
  * `knowledge/findings/KN-FIND-982fdf.md`, line 29: C_t "is not GGM-simulable; it is
    encoding-dependent and publicly computable". KN-FIND-194294 likewise has O_x non-simulable,
    and O_x is publicly computable in the concrete model. The row's revisit_when trigger has
    therefore already fired by its own references, and its "but needs private data" contradicts
    KN-FIND-982fdf.
* **Does any scoping save the closure? No.**
  * "Scope: oracles, not resources" does not change the oracle definition.
  * The measured items cover one exploitation strategy at 7–8 field bits: Y_A = Y_B
    (EV-ECDLP-fd61e4), "oracle increases candidates" (EV-ECDLP-284817) and "MITM saving
    attributable to the split" (EV-ECDLP-7367e2). They are not a lower bound and cannot carry
    "closes … at exponent 1/2".
  * A sanity check: in the concrete model a full-point oracle *is* the group representation.
    Closing the full-point or x-oracle family at exponent 1/2 by Shoup would prove Ω(√n) for
    concrete ECDLP on every curve, which anomalous curves refute.
* **What survives in Shoup's model.**
  * Endomorphism: simulable with Θ(log N) overhead. φ acts as a public scalar λ; this is the
    reviewer derivation attributed in EV-GGM-002, not O(1)/C=0.
  * Incidence: O(m) once FB labels are supplied.
  * x, y, full-point, halving and field-valued jet/net: not simulable.
* **Required restatement** of the note's "Wider implication" paragraph:
  > "LEAD-EXO-augmented-oracle-ggm states (lines 13–15): '[full quote above]'. The named oracles
  > include the x-, y- and full-point oracles (title, mechanism, forecloses). For these, and for
  > the halving oracle and the field-valued jet, the premise fails in Shoup's model: Lemma 3, and
  > already KN-FIND-194294 (cited by the row), which classifies O_x and O_D as NON-SIMULABLE. In
  > the structured GGM of KN-FIND-002 the premise holds trivially, but Shoup's theorem does not
  > apply (EV-ECDLP-048824 CC-3). The row's 'EV-GGM-001 strong' is superseded by EV-GGM-002,
  > which does not carry the exponent-1/2 closure language forward. The row's revisit_when
  > condition is met by KN-FIND-194294 and KN-FIND-982fdf. The endomorphism (Θ(log N)) and
  > incidence (O(m), given FB labels) closures are unaffected in Shoup's model. The measured
  > toy-tier results stand as measurements of one strategy and are not a lower bound. Not changed
  > here; routed for review."
* **Cheapest test that settles it:** open the six records above at main @ 9b721d74. That is a
  read, with no runs; the quotes here were taken from those bytes.

### F2 (high; wrong): Lemma 2's "the only way to give the network its boundary is to add an oracle X"; H1's verdict depends on the reading

* **Evidence.** README lines 47–48 and Summary row H1 ("False as stated in Shoup's model").
* **A second way exists: a label-indexed entry oracle.** Define
  I(σ(R1), σ(R2), σ(R3)) = T[x(R1), x(R2), x(R3)]. Over F̄_p the points with abscissa x(Ri) are
  ±Ri, so S_3 = 0 iff R1 ± R2 ± R3 = O for some signs. The predicate is answered by:
  * 4 subtraction-oracle queries: −R2, −R3, R1−R2, R1+R2;
  * 4 label comparisons against ±R3;
  * plus 1 one-time query for σ(O).
* **Verified.** `rt_h1_paths.py` checks this against S_3 at p=61, a=4, n=67 under a random
  labelling. Result: 0 mismatches over all 287,496 ordered affine triples, max 4 queries per
  entry.
* **The three readings of H1 ("an algorithm that only reads entries of T"):**

| reading | queries per entry | H1 | lower bound obtained | what it covers |
|:--|:--|:--|:--|:--|
| A. public indices (x,y,z) ∈ F_p³ | 0 | true, vacuous | Shoup's Ω(√n'): T is σ-independent, so it is useless to the generic algorithm | no index calculus (never touches the instance through T) |
| B. label-indexed entries I(σ1,σ2,σ3), FB supplied as labels | ≤ 4 (+1 once) | **true** | Shoup: success ≤ O((4q_T + q_G)²/n') | generic decomposition search, including MITM on hashed **labels**; excludes every algorithm that treats bond values as **field elements** (sorting/hashing x, Fourier/multiplicative/Legendre bases on F_p, Gröbner on S_{m+1}) |
| C. coordinate access (algorithm learns x(R), then reads T rows) | Θ(√n') (F3) | **false** | none | all Semaev-style index calculus, every F_p-basis change |
| C′. repo's "structured GGM" (coordinates of all group elements visible) | 0 | true, vacuous | **none**: the model is the concrete representation, where anomalous (Smart), pairing-friendly (MOV/FR) and, over F_{q^n}, Gaudry–Diem decomposition attacks all beat √n | everything |

* **Consequence.** The note's conclusion, that step (a) removes no basis family from scope, is
  right under every reading, but for a reason it does not state:
  * Under B the bound holds but cannot see any F_p-basis change, because the bonds carry labels,
    not field elements.
  * Under C and C′ there is no bound.
  * The lead's sentence ("only bases that use the algebraic form of S_3 remain in scope") draws
    the line in the wrong place. The line is "uses coordinates of instance points as field
    elements", not "manipulates the polynomial S_3".
* **Required restatement** of Summary row H1 and Lemma 2:
  > "H1 is ambiguous. Read as label-indexed entry access (I(σ1,σ2,σ3) = T[x(R1),x(R2),x(R3)]),
  > it is true with ≤ 4 group queries per entry, and Shoup's bound applies to that class; but
  > that class cannot apply any basis change to the F_p bond alphabet. Read as the lead intends
  > (entry reads at x(R), 'as the x-oracle is'), it is false: the boundary vector e_{x(R)} needs
  > coordinate access, which is not GGM-simulable (Lemma 3). In the repo's structured GGM it is
  > trivially true and yields no lower bound. Under every reading, step (a) removes no
  > F_p-basis family from scope."

  Replace "the only way to give the network its boundary is to add an oracle X" with "the only
  way to evaluate the boundary in the F_p alphabet, which is where a holographic basis change
  acts, is coordinate access".
* **Cheapest test:** done, `rt_h1_paths.py` part (a), 2 s.

### F3 (medium-high; the reduction is right, the quantifier is weaker than the truth): Lemma 3

* **Evidence.** README lines 52–65.
* **The reduction is sound:**
  * Smart's attack works from x-only data. Choosing either square root for each of P and Q
    returns ε_P·ε_Q·k mod p.
  * A random (non-canonical) lift is needed; the canonical lift makes the map degenerate.
  * This is Las Vegas polynomial time.
* **The truth is much stronger.**
  * Shoup's bound counts oracle queries only; local computation is free. On **any** curve, two
    X-queries give x(P) and x(Q). Local computation (brute force, or concrete rho at zero oracle
    cost) then returns k up to sign, and O(log n) subtraction queries for σ([k]P) plus one label
    comparison resolve the sign.
  * So a simulator with s queries per X-query yields a generic algorithm with
    2s + O(log n) queries. Shoup then gives **s = Ω(√n')** on **every** curve family with
    n' → ∞, not just uniformly. The anomalous case adds only that the local work can be
    polynomial time.
  * The matching upper bound: answer each X-query by BSGS on the queried label, which takes
    O(√n) queries, then evaluate x([r]P) locally. So X's simulation overhead is **Θ(√n')**, and
    X is GGM-equivalent to a DLP oracle up to O(log n) group operations. EV-GGM-79e710 uses the
    same "equivalent to the DLP oracle" language for the jet.
* **On the dispatcher's question.** "Simulability is curve-specific, and on prime-order
  non-anomalous curves the question is open" is not the right restatement. Simulability fails on
  every curve, information-theoretically. What is open is computational: whether x-access lets a
  time-bounded attacker beat rho on a given curve. That is ECDLP itself, and no GGM argument can
  express or decide it.
* **Minor errors in the proof text:**
  * "One group query … resolves the sign" should read: O(log p) group queries to form σ([k]P),
    then one label comparison.
  * "poly(log p) X-queries" should be 2 X-queries, giving s = Ω(√p), not
    Ω(√p / poly(log p)).
  * Semaev's (1998) and Satoh–Araki's attacks are not p-adic-lift attacks (one uses functions /
    an additive map, the other Fermat quotients). Cite Smart, with the non-canonical-lift
    condition.
* **Overreach in the closing paragraph (lines 63–65).** "For any oracle that reveals coordinates
  of instance points" should be narrowed to "for any oracle whose answers on O(1) instance points
  determine log_P Q up to poly(log n) candidates". A one-bit coordinate oracle such as C_t is
  non-simulable by a different argument (KN-FIND-982fdf), and Lemma 3 does not set its overhead.
* **Required restatement of Lemma 3:**
  > "For every family of curves with largest prime n' | #E → ∞, any simulator of
  > X: σ(R) ↦ x(R) from the generic group oracle needs Ω(√n') group queries per X-query, and
  > O(√n') suffice (BSGS). Proof: two X-queries determine log_P Q up to sign
  > information-theoretically; Shoup's bound counts only oracle queries. Remark: on anomalous
  > curves the local work is even polynomial (Smart, random lift). Nothing here says whether
  > coordinate access helps a time-bounded attacker on any given curve."
* **Cheapest test:** none needed; the 3-line proof above replaces the anomalous witness. A toy
  demonstration cannot discriminate, because Shoup's bound is vacuous at toy n.

### F4 (medium; unpriced): Lemma 1 and "the bulk … (it is 0)"

* **Evidence.** README lines 31–39: "uses 0 oracle queries" (correct), and then "H1's 'O(1)
  group operations per entry' overstates the cost of the bulk (it is 0)" (a cost statement).
* **The fault.** Zero oracle queries is GGM accounting, not cost.
  * Building M over the F_p alphabet takes |FB|·p² S_3 evaluations, and T has p³ entries.
  * At the note's own largest curve (p=307, |FB|=17, n=313): 17·307² ≈ 1.60·10⁶ evaluations,
    against √n ≈ 17.7, so S ≈ 9.1·10⁴ for building M alone, before any boundary evaluation.
  * The crypto program's (aburan28/crypto) AGENTS.md "The rule: boundary, table, ratio" requires
    "Every cost the method incurs belongs in S: precomputation, table setup, …".
* **Why it matters.** Whether a basis change makes the bulk *cheap* is exactly the lead's
  question in step (b). Calling it 0 assumes the answer.
* **Required restatement:**
  > "The bulk costs 0 oracle queries. Its time cost (Θ(|FB|·p²) to build M, p³ entries in T) is
  > unpriced here and is the subject of step (b)."
* **Cheapest test:** none; the arithmetic is above.

### F5 (medium; wrong as an unconditional claim): even n, so the Summary row needs "odd n"

* **Evidence.** The Summary row "Transfer matrix" states the O-deletion identity without the
  odd-n condition. The body (line 84) has "For odd n"; the table does not.
* **Mechanism.** For a 2-torsion point T, P+F and P−F lie in the same ±-orbit. So B[T,o'] = 2 for
  every non-2-torsion o' with o' ∈ ±(T±F) (a single FB hit), while M[T,o'] = 1, because S_3
  counts each x_F at most once.
* **Observed** (`rt_edge.json`, p=67, b=3, a ∈ {2,3,5}, n ∈ {56,66,82}):
  * M ≠ B[1:,1:] at exactly the 2-torsion rows/columns, with ratio B/M = 2 on every mismatched
    entry (24, 8, 8 entries).
  * Cauchy interlacing against spec(B) is violated at 16, 7 and 4 indices, for M of dimension
    29, 33 and 41.
  * First violation (n=56): λ_1 = −4.4058 and λ_2 = −4.2470, but μ_1 = −4.1994 > λ_2.
* **Exact even-n form (verified 3/3).** M equals the O-deleted symmetrised quotient with every
  coupling between a 2-torsion vertex and a non-2-torsion vertex divided by √2. This is a
  congruence, not a similarity, so it gives no interlacing with the character sums.
* **Required restatement:** the Summary row should read "For odd #E: M is the symmetrised Cayley
  quotient with the O vertex deleted …", with the even-n correction above stated as such.
* **Cheapest test:** done, `rt_edge.py` part (i), < 1 s.

### F6 (medium; wrong as a universal claim): degenerate spectra. "Interlacing not equality" and "M's eigenvectors are not characters" both fail for j=0 with an automorphism-stable FB

* **Evidence.** README Summary row ("its spectrum interlaces the character sums but is not equal
  to them") and line 87 ("M's eigenvectors are not characters").
* **Mechanism.** On y² = x³ + b with p ≡ 1 (mod 3), take a FB closed under x ↦ ζx. Then S is
  stable under [μ] (μ² + μ + 1 ≡ 0 mod n), so λ_j = λ_{μj}. Each eigenvalue of B then has
  multiplicity 3, and the O-deleted M keeps it with multiplicity ≥ 2. The eigenvectors are
  cos(2πj·log/n) − cos(2πμj·log/n), which vanish at O.
* **Observed** (`rt_edge.json` part (ii)): 11/11 curves (p ∈ {67,…,199}, prime n).
  * Exactly 2/3 of M's eigenvalues equal character sums: 24/36, 22/33, 32/48, …, 70/105.
  * The character difference is an exact eigenvector: residual ≤ 6.1·10⁻¹⁴.
  * A single character is not: residual 0.47–0.68.
* **Relevance.** secp256k1 is j=0, and an automorphism-stable FB is the standard way to use the
  order-6 automorphism in index calculus. So this is not an exotic edge case.
* **Exact replacement** (verified at all 5 producer curves, `rt_secular.json`):
  * Eigenvalues: for cyclic odd n, μ is an eigenvalue of M exactly when Σ_{j∈Z/n} 1/(λ_j − μ) = 0
    (the trace of the Cayley resolvent), or when μ = λ_j for some λ_j of multiplicity m ≥ 2 (then
    with multiplicity ≥ m − 1). Max relative secular residual is ≤ 1.9·10⁻¹⁰.
  * Eigenvectors: for the non-degenerate μ, the eigenvector is the Green function
    G_μ(P) = Σ_j cos(2πj·log P/n)/(λ_j − μ). Cosine with the numerical eigenvector is ≥ 1 − 4·10⁻¹⁶
    in every case.
* **This partly restores the lead's sentence.** M's eigenvectors are still explicit functions of
  log P (resolvent-weighted character sums). "A basis that diagonalises M encodes the discrete
  log" survives in that form, and the note's correction should not be read as removing it.
* **Required restatement:**
  > "For odd #E, M is the O-deleted symmetrised Cayley quotient. Its spectrum is the degenerate
  > character sums (multiplicity reduced by one) together with the zeros of
  > Σ_j 1/(λ_j − μ). The remaining eigenvectors are the Green functions G_μ(P), not single
  > characters. Strict interlacing and 'no character eigenvectors' hold only when the character
  > sums are simple, as at the five tested curves (smallest-x FB, a ≠ 0)."
* **Cheapest test:** done, `rt_edge.py` part (ii) and `rt_secular.py`, under 3 s.

### F7 (low; incomplete proof sketch): line 84, "both cannot hold at once"

* **The fault.** The sketch pairs the wrong events. B counts, per x_F, the four equalities
  P' = ±(P ± F) separately. M = B[1:,1:] needs "at most one of the four holds", which is true
  iff 2P, 2P' and 2F are all ≠ O. That is exactly why the identity is odd-n only (F5).
* **Restatement:** state the four-equality condition. The conclusion is right for odd n.

### F8 (low; scope of N_m): the chain count is a count of bond paths, not of decompositions

* **The fault.** For m=3, a FB tuple can reach the target by two internal-bond paths
  (y = x(F1+F2) and y = x(F1−F2)).
* **Observed** (`rt_h1_paths.json` part (b)): at p ∈ {61, 101, 163},
  * chain count exceeds tuple count by 84, 180 and 264, at exactly |FB| targets (7, 10, 12);
  * that is 2(|FB|−1) cancelling tuples (z, w, w) per FB target z, with max 2 paths.
* **Impact.** For instance-derived R ∉ ±FB the two counts agreed at all three curves. Separately,
  a relation also needs one sign bit per relation, which comes from y(R) or a group-side check.
  The instance therefore enters through x(R) *and* that bit, which Lemma 2 omits.
* **Restatement:** add one sentence to Lemma 2 covering both points.

### F9 (low; scope): the evidence base and the λ_j formula

* **Evidence base.** "5/5 primes" is 5 curves, b = 1, one FB rule. The identity is a 3-line
  algebraic fact for odd n, so present it as proved, with the numerics as a check.
* **Extension run here (`rt_transfer.json`):** 21/21 odd-n configurations hold exactly (integer
  equality M = B[1:,1:], coupling √2·1_FB, bordered spectrum = spec(B) to ≤ 6.8·10⁻¹⁴,
  interlacing). The 21 are:
  * 6 prime-n curves with b ∈ {2,3};
  * 3 odd composite n (65, 69, 65);
  * 6 twist-side FB;
  * 6 mixed FB;
  * the producer's 5 come on top of these.
* **The λ_j formula.** It is written with "log s", so it assumes E(F_p) is cyclic. For odd
  non-cyclic groups (possible when 3 | gcd(n, p−1)), use the group's characters. The identity
  itself is group-agnostic (my check compares against spec(B) directly).

### F10 (informational; the twist claim is stronger than stated)

* **It is a theorem.** For FB ⊂ X(E) containing no root of x³+ax+b (automatic for odd #E),
  M[E×twist] = M[twist×twist] = 0. The Frobenius argument: π(F ± P) = F ∓ P ≠ ±(F ± P).
* **Twist-side FB.** The twist block equals the O-deleted Cayley quotient of E^t(F_p), exactly:
  6/6 primes, integer equality.
* **Mixed FB.** M = M_E(FB ∩ X(E)) ⊕ M_{E^t}(FB ∩ X(E^t)) with zero cross mass, in all 27
  configurations including even n.
* **When the twist block is non-zero.** For even n with a 2-torsion x in FB, the twist block is
  non-zero (mass 114, 34, 26) even though FB ⊂ X(E). So the note's "odd #E" qualifier is
  necessary and should stay.

## 3. Commands and outputs

All runs are local, pure Python + NumPy 2.5.3, p < 320, and each takes seconds. They are
derivation checks, not experiments. Scripts live in a separate directory and do not import or
modify the frozen files.

```
cd /tmp/claude-0/-home-user/cbe54866-0ec9-5df8-a9c8-3139bd6e12e8/scratchpad/rt_rerun
cp ../holant/check_transfer.py ../holant/check_O.py .
python3 check_transfer.py > t.json   # 1.7 s; cmp == ../holant/transfer_spectrum.json
python3 check_O.py > o.json          # 1.0 s; cmp == ../holant/o_vertex_control.json
python3 rt_transfer.py > rt_transfer.json   # 0.6 s; 27 configs: 21 odd-n pass, 6 even-n fail (F5, F9, F10)
python3 rt_edge.py     > rt_edge.json       # 0.4 s; even-n localisation + correction; j=0 degeneracy (F5, F6)
python3 rt_secular.py  > rt_secular.json    # 2.5 s; secular equation + Green-function eigenvectors (F6)
python3 rt_h1_paths.py > rt_h1_paths.json   # 2.2 s; label-indexed entry oracle; m=3 path multiplicity (F2, F8)
```

| artifact | sha256 |
|:--|:--|
| rt_transfer.py | db0600f2231486cc0e27cdcc81c4373bde0e59f30d08852c3165f7ae5bcc867b |
| rt_transfer.json | 90eaada72a5a49570e17cc6e8b9f8e3b89629e190e10e369920dc74a2498b5dd |
| rt_edge.py | 1dcd60e2a5c689093f4539d5f0d180baf7ab3dfae0051b745295be871c209d4c |
| rt_edge.json | 78e0980fa6ae5b29f41ba7c07a28812bf6fe0942d246c127cfa4bd65ff936de9 |
| rt_secular.py | c42d598264b56594ce0a2038f09131e572345f14302dd6f16739bba586762fe2 |
| rt_secular.json | 92a76193dbcfd8b2e8497f75e84e474c78aa1de51373f2cca1174f328bf30acd |
| rt_h1_paths.py | 4292f713011657b90be8800b0951f115616e224532c092d2f7b544ddbcffeccb |
| rt_h1_paths.json | e66c2ed8520f034deab501c563a02a1fe9253669d42c3ffad16c73032464fdf6 |

These artifacts are scratch, not evidence. If the Coordinator wants them durable, they must be
committed alongside the note.

## 4. What this review did not do

* It did not edit the README, the scripts, the repo or any status.
* It did not run any experiment, and did not touch EKS or the resume checkpoints. The runs above
  are seconds-long derivation checks the dispatch asked for.
* It did not review the four post-dispatch files.
* It did not assess H2 (Cai–Chen); the note leaves it untouched and so does this review.
