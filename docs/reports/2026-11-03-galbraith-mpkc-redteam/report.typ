// Some definitions presupposed by pandoc's typst output.
#let blockquote(body) = [
  #set text( size: 0.92em )
  #block(inset: (left: 1.5em, top: 0.2em, bottom: 0.2em))[#body]
]

#let horizontalrule = [
  #line(start: (25%,0%), end: (75%,0%))
]

#let endnote(num, contents) = [
  #stack(dir: ltr, spacing: 3pt, super[#num], contents)
]
#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
      ])
    .join()
}

#let conf(
  title: none,
  authors: none,
  date: none,
  abstract: none,
  cols: 1,
  margin: (x: 1.25in, y: 1.25in),
  paper: "us-letter",
  lang: "en",
  region: "US",
  font: ("Libertinus Serif", "New Computer Modern"),
  fontsize: 11pt,

  doc,
) = {
  set page(
    paper: paper,
    margin: margin,
    numbering: "1",
  )
  set par(justify: true)
  set text(lang: lang,
           region: region,
           font: font,
           size: fontsize)
  set heading(numbering: none)

  if title != none {
    align(center)[#block(inset: 2em)[
      #text(weight: "bold", size: 1.5em)[#title]
    ]]
  }

  if authors != none {
    let count = authors.len()
    let ncols = calc.min(count, 3)
    grid(
      columns: (1fr,) * ncols,
      row-gutter: 1.5em,
      ..authors.map(author =>
          align(center)[
            #author.name \
            #author.affiliation \
            #author.email
          ]
      )
    )
  }

  if date != none {
    align(center)[#block(inset: 1em)[
      #date
    ]]
  }

  if abstract != none {
    block(inset: 2em)[
    #text(weight: "semibold")[Abstract] #h(1em) #abstract
    ]
  }

  if cols == 1 {
    doc
  } else {
    columns(cols, doc)
  }
}
#show emph: it => it.body
#show raw: set text(font: "Libertinus Serif", size: 1em)
#show: doc => conf(
  paper: "a4",
  fontsize: 9pt,
  cols: 1,
  doc,
)


= Red-team of the Galbraith MPKC v2 intake (PR \#2945) and of the book’s
literal statements
<red-team-of-the-galbraith-mpkc-v2-intake-pr-2945-and-of-the-books-literal-statements>
- #strong[Date:] 2026-11-03
- #strong[Kind:] adversarial evidence review. This is a review record,
  not a status change. It edits no PR \#2945 file, catalog row or formal
  target.
- #strong[Subject:] PR \#2945
  (`codex/galbraith-mpkc-formalization-20261101`, head
  `74a0d7f52eb2384f85008eed1e048dbe93539218`), which added
  `KN-LIT-2e5200`, the 1,817-object catalog under
  `inputs/GALBRAITH-MPKC-2018/` and the Lean target
  `galbraith-montgomery-reduction-20261101`. Also the theorem-like rows
  of the source book: Steven D. Galbraith, #emph[Mathematics of Public
  Key Cryptography] v2.0, PDF SHA-256
  `ca75ee62b96daa0d46faaa2d4dc28205683455ad3a2a48586b9b39299c25022d`
  (re-downloaded 2026-11-03; the hash matches), with the official errata
  page snapshot of 2026-11-03.
- #strong[Question:] which of the proofs, lemmas, bounds and theorems
  that this intake brought into the program can be disproved, and which
  survive?

_Figure (kept out of this PDF for the 64 KiB artifact limit): `verdicts.svg` / `verdicts.png` in this report directory._

== 1. Summary
<summary>
#align(center)[#table(
  columns: 2,
  align: (col, row) => (auto,auto,).at(col),
  inset: 6pt,
  [Object], [Verdict],
  [Lean `montgomery_reduction` (Lemma 2.5.3)],
  [#strong[Survives.] I re-proved the exact proposition independently in
  core Lean 4.35.0 without Mathlib; its axioms are `propext`,
  `Classical.choice` and `Quot.sound`. Exhaustive and box searches found
  no counterexample. Three fidelity findings, all strengthenings (§2).],
  [Theory note of the target],
  [Two inaccuracies. The printed statement does not contain `w < n`;
  only the printed proof does. The inverse form needs only the
  negative-inverse hypothesis, not "odd n, R \= 2^s" (§2).],
  [Catalog: 1,817 objects, kind counts, no gaps or duplicates],
  [#strong[Confirmed], by an independent detector (§3).],
  [Catalog: SHA-256 reproduction],
  [#strong[Holds only under PyMuPDF 1.26.6], which the README does not
  pin. PyMuPDF 2.1 gives a different hash and different class counts
  (§3).],
  [Catalog: 119 `absent_in_book` proofs],
  [#strong[Refuted.] At least 11 of the 119 have proofs; the true count
  is at most 108. At least 10 citation-only proofs are classed
  `present_complete` (§3).],
  [Catalog: 444 exercises with an Appendix B signal],
  [#strong[Refuted.] The count is 486; 42 are missed (§3).],
  [Catalog: errata mapping],
  [#strong[Partly refuted.] ERRATA-041 (the Wiener bound) is attached to
  Lemma 2.3.3 instead of Theorem 24.5.2. There is edition-number drift
  for 5.2.20→5.2.25, 5.3.8→5.3.10 and "7.3.1"→17.3.1 (§3).],
  [Book, Chapter 2 (the planned next formal tranche)],
  [12 rows false as printed, 15 missing a hypothesis or ill-posed, 3
  proof gaps, 4 constant/unit/typo defects, 32 survived. Lemmas 2.5.1
  and 2.5.4, the named next targets, are #strong[not well-formed Lean
  targets as printed] (§4).],
  [Book, Chapters 13–15 (DLP and index-calculus bounds)],
  [7 false as printed, 1 missing hypothesis, 3 proof gaps, 4 constant
  mismatches, about 40 survived. The core constants survived (§5).],
  [Book, Theorem 24.5.2 (Wiener)],
  [The printed bound `N^{1/4}/√3` is a known erratum (`√6`). I found
  #strong[941 concrete failures of the printed proof route] inside the
  printed bound (§6).],
)
]

None of this shows that the book is unreliable in general. It shows that
literal transcription into Lean targets or baseline constants would
encode false statements, which is the risk the PR’s own policy
anticipates.

== 2. The Lean target and its source (verified by the lead)
<the-lean-target-and-its-source-verified-by-the-lead>
Source (PDF p. 52, read from the pinned PDF). Lemma 2.5.3 assumes odd
`n`, `R = 2^s > n`, `n' = −n^{-1} mod R` with `1 ≤ n' < R`, `a` in
Montgomery representation (`0 ≤ a < n`), and `u = a n' mod R`. It
concludes `w = (a+un)/R ∈ Z` and `w ≡ aR^{-1} (mod n)`. The bound
`w < n` appears only in the printed proof.

Checks:

+ #strong[Book statement, exhaustive]
  (`evidence/lead/lemma253_check.py`). All odd `n < R = 2^s` for
  `s ≤ 10` and all `a < n` were tested: 349,525 cases, 0 failures. For
  every case with `s ≤ 8`, `w` is exactly the canonical representative
  of `aR^{-1} mod n`.
+ #strong[PR proposition over a box.] All of `n, R, n', a, u` were taken
  from `[−6, 12]`. No counterexample was found.
+ #strong[Mutation (drop one hypothesis).] Counterexamples exist when
  any of `ha0`, `han`, `hu0`, `huR`, `hnegInv` or `hu` is dropped, so
  each is load-bearing. Dropping #strong[`hnpos` or `hnR` gives no
  counterexample]. Both are redundant: `0 ≤ a < n` gives `n > 0`,
  `0 ≤ u < R` gives `R > 0`, and `R > n` is never used by the integer
  core.
+ #strong[Independent machine check]
  (`lean/MontgomeryReductionCore.lean`). It uses core Lean only, with
  `grind` and `omega` instead of Mathlib’s `ring`/`nlinarith`, and
  compiles with `lean` v4.35.0. It proves:
  - `montgomery_reduction_core`: the PR’s exact proposition;
  - `montgomery_reduction_core_min`: the same without `hnpos` and `hnR`;
  - `montgomery_inverse_form`: `n*n'+1 = k*R` and `n ∣ R*w − a` imply
    `n ∣ w − a*k`. The book’s inverse form `w ≡ aR^{-1}` therefore
    follows from the negative-inverse hypothesis alone, contrary to the
    theory note, which attributes it to "odd n, power-of-two R";
  - a decided control: for Montgomery-multiplication inputs `a < nR`,
    the bound `w < n` fails (`n=3, R=4, a=11, w=5`). The book’s own
    sketch says only `w < 2n` there, and that holds.

  The PR’s Mathlib-based build was not reproduced here: the Mathlib
  cache does not fit in this session’s disk allowance. The core-Lean
  re-proof is independent evidence for the same proposition.

#strong[Recommendation for the target:] record the two redundant
hypotheses and the inverse-form theorem as a dated correction or
follow-up target. Do not edit the frozen spec. Fix the note’s sentence
about the source statement containing `w < n`.

== 3. Catalog claims (catalog audit agent; key rows spot-checked by the
lead)
<catalog-claims-catalog-audit-agent-key-rows-spot-checked-by-the-lead>
Scripts and results are in `evidence/catalog-audit/`. These were
produced by a delegated audit agent. The lead re-read the PDF text for
Theorems 24.2.14 and 24.2.16 ("Proof: (Theorem 24.2.14" and "Proof of
Theorem 24.2.16" on p. 518) and for the ERRATA-041 text.

- #strong[Reproduction.] With PyMuPDF 1.26.6, the catalog SHA-256
  `764d1249…789d`, the summary, the errata JSON and every index are
  byte-identical. With PyMuPDF 2.1, the object count is still 1,817 but
  the hash is `0e473889…e752`. That run also gives absent 122, citation
  52, present\_complete 257 and Appendix B 440, and 381 index lines
  differ. The generator is not reproducible without a pinned PyMuPDF
  version, and the README does not pin it.
- #strong[Completeness.] An independent bold-heading detector found
  1,806 labelled headings, plus 9 Notation blocks and 2 unnumbered
  objects (p. 93, p. 292), for 1,817 in total. It found 0 spurious, 0
  missed, no numbering gaps or duplicates, and every kind count matches.
- #strong[Proof status.]
  - A random sample (seed 20261103) found 2 of 25 `absent_in_book` rows
    wrong.
  - A full scan of all 119 found 11 wrong:
    - 8 have the proof in the statement’s own PDF block: 2.9.1, 9.6.13,
      10.1.14, 14.1.1, 19.3.1, 22.1.5, 24.2.16, and 10.7.4 (really
      citation-only).
    - 3 have the proof displaced after another object: 7.7.11, 11.1.4
      and 24.2.14.
  - At least 10 rows whose proof is only a literature pointer are
    classed `present_complete`: 8.7.2, 9.10.12, 9.11.2, 10.2.6, 10.2.11,
    10.9.5, 19.2.1, A.6.7, A.7.2 and A.10.8.
  - The problem record’s "119 theorem-like rows have no detected in-book
    proof" therefore overstates the queue by about 9%.
- #strong[Appendix B.] An independent scan of pp. 605–642 found 486
  exercise entries. All 444 catalog rows are among them; 42 are missed
  (for example 2.15.1, 10.2.4, 13.3.3 and 24.6.3) because
  `get_text(sort=True)` merges lines.
- #strong[Errata.]
  - The 47 items are confirmed.
  - The 31 exact matches cover 31 objects but 33 errata ids.
  - #strong[ERRATA-041] ("correct bound … `0 < d < N^{1/4}/√6`") is
    attached to Lemma 2.3.3, which it only cites. It is missing from v2
    #strong[Theorem 24.5.2] (p. 528), which still prints `√3`.
  - 2012-to-v2 drift: Lemma 5.2.20 is v2 Lemma 5.2.25, Theorem 5.3.8 is
    v2 Theorem 5.3.10, and the erratum’s "Definition 7.3.1" means v2
    Definition 17.3.1.
  - No erratum touches §2.5 or Montgomery reduction, as the PR claims.

== 4. Chapter 2 literal statements (Chapter 2 agent; spot-checked by the
lead)
<chapter-2-literal-statements-chapter-2-agent-spot-checked-by-the-lead>
Scripts and outputs are in `evidence/ch2/`. The scripts read page text
they extract from the pinned PDF; the book text itself is not committed.
The lead re-read three rows against the PDF:

- Lemma 2.3.3(1): the book’s own Example 2.3.4 has `s₁ = 1, s₂ = −1`,
  which contradicts `|s_i| < |s_{i+1}|` for `i ≥ 1`.
- Lemma 2.14.8: the statement omits `Tr(α) = 0`, which appears only in
  the preceding Exercise 2.14.7.
- Lemma 2.5.4: as printed, it carries no bound on `s`.

#align(center)[#table(
  columns: 3,
  align: (col, row) => (auto,auto,auto,).at(col),
  inset: 6pt,
  [Row], [Defect], [Evidence],
  [#strong[Lemma 2.5.1(4)]],
  [Ill-posed: the bound `O(log n (log a − log n + 1))` is negative for
  `a < n/e` and undefined for `a ≤ 0`. The book’s `log` is natural
  (p. 15) and Def. 2.1.2 requires `g > 0`.],
  [`(a,n) = (1,100)` gives −16.6],
  [Lemma 2.5.1(1–3)],
  [The bound is 0 at `n = 1`. Item 3 needs `gcd(a,n) = 1`.],
  [`a = 2, n = 6`],
  [#strong[Lemma 2.5.4]],
  [Missing `s = O(log n)`: nothing bounds `R = 2^s`, so the cost is
  `O(M(s))`. It is also unstated whether the cost of `n'` is charged.],
  [argument],
  [p. 53, Newton/Barrett text],
  [`a` and `n` are swapped. Even after the fix, `⌊ab/2^e⌋ ≠ ⌊a/n⌋` in
  2,418,140 of 21,253,395 cases (off by 1), so a correction step is
  needed.],
  [`t1.out`],
  [p. 53, CRT formula],
  [The result is not reduced into `[0, m₁m₂)`: 87% of cases are out of
  range.],
  [`(2,3,1,0)` gives −3],
  [Algorithm 1 (symmetric remainders)],
  [Returns a negative "gcd".],
  [`(2,3)` gives `d = −1`; 1,442 pairs],
  [Lemma 2.3.3(1), (6)],
  [False at `i = 1`, including on the book’s own example.],
  [Example 2.3.4],
  [Lemma 2.3.3(7), (8)],
  [Missing `gcd(s,t) = 1`, and missing `s, r ≠ 0`.],
  [`(1,1,2,−2)`],
  [Thm 2.3.1 (proof)],
  [`2|r_i| ≤ |r_{i−1}|` does not imply `1 + ln r_i ≤ ln r_{i−1}`.],
  [`(12,5,2)`],
  [Lemma 2.9.2, Ex. 2.9.10],
  [Missing `p` odd, `p ∤ a`, and `(a/p) = 1`.],
  [`p = 3, a = 2`],
  [p. 60, Cornacchia (2p variant)],
  [Misses 2,078 of 2,918 solvable cases.],
  [`7 = 2² + 3·1²`],
  [p. 57, Stolarsky],
  [States a lower-bound conjecture as an upper bound.],
  [`m = 127` needs 10 \> 9.80],
  [Thm 2.14.2],
  [`q − m(m−1)` should read "at least".],
  [`q = 7, m = 3`],
  [#strong[Lemma 2.14.8] (half trace)],
  [Missing `Tr(α) = 0`: fails on exactly the trace-1 half.],
  [`m = 3, 5, 7`],
  [p. 69, order],
  ["smallest f" should be "largest f".],
  [`f = 0` always qualifies],
  [Lemma 2.15.7],
  [The count fails with natural log, and `m = 1` is undefined.],
  [`m = 2` gives 35 \> 27.7],
  [p. 71, φ bound],
  [Fails at `q = 3`.],
  [0.5 \< 1.77],
  [Ex. 2.6.4],
  [The claims `2z ∉ Z` and that `x` exists both fail.],
  [all `c_i = 0`],
)
]

The full table, with all survivors, is in `evidence/ch2/` (`t*.out`).
The items here are agent-computed except the three rows above.

#strong[Consequence for the campaign.] The problem record’s next step is
to formalize "Lemmas 2.5.1 and 2.5.4". Neither can be transcribed
faithfully: each needs a declared cost model first (bit lengths instead
of logs, a rule for the case `a < n`, a bound on `R`, and which
precomputation is charged). That is the "unmodelled complexity
convention" stop condition the record already names.

== 5. DLP and index-calculus bounds, Chapters 13–15 (DLP agent; one row
re-derived by the lead)
<dlp-and-index-calculus-bounds-chapters-1315-dlp-agent-one-row-re-derived-by-the-lead>
Scripts and outputs are in `evidence/dlp/`. "C" means exact computation
or seeded Monte Carlo with 95% intervals; "A" means argument only.

#align(center)[#table(
  columns: 3,
  align: (col, row) => (auto,auto,auto,).at(col),
  inset: 6pt,
  [Row], [Verdict], [Evidence],
  [#strong[Thm 15.8.2] (summation polynomials)],
  [#strong[False over `F_q` as printed.] It holds over the algebraic
  closure; F\_q-roots can come from the quadratic twist.],
  [C. The lead re-derived this independently
  (`evidence/lead/semaev_s3_fp.py`): on `y² = x³+2x+3/F₃₁`, 462 of 930
  F\_p-roots of S₃ come from no E(F\_p) points; on `y² = x³+x+5/F₃₇`,
  666 of 1332. Every point triple is a root.],
  [Thm 14.5.5 and Pollard kangaroo data],
  [The book quotes `C(n_S)` between 1 and 1.06 for `n_S ≥ 12`. The
  book’s own recursions give `C(12) = 1.118` and `C(13) = 1.110`
  (simulation 1.115 ± 0.011). A full kangaroo with `2^j` jumps gives
  2.107 ± 0.046 (`n_S = 10`) and 2.140 ± 0.046 (`n_S = 12`). The
  asymptotic `2 + o(1)` is not refuted.],
  [C, `t3_kangaroo.py`],
  [Ex. 14.4.8 (Koblitz)],
  [`√(π2^m/(4m))` uses `2^m` instead of `r = 2^m/h`, which overstates by
  `√h`.],
  [A],
  [p. 297, Brent–Pollard],
  [`c = n_S/(n_S−1)` is not the in-degree variance; the variance is the
  inverse. The constant fails for small `n_S` (`n_S = 3`: 2.04 against
  1.22).],
  [C],
  [Lemma 13.5.6],
  [The lower bound `Ω(#S₁^{l/2})` needs `∏#S_j ≈ r`.],
  [A],
  [p. 286, Wiener birthday bound],
  [Fails in the printed range `l ≤ 2N log N` (first at `l = 181`,
  `N = 1000`).],
  [C],
  [p. 287, Kuhn–Struik],
  [`√(2kN)` is 6.4% high at `k = 2`.],
  [C],
  [Thm (p. 292) Floyd failure probability, proof],
  [Assumes `b_{i+lh} − b_i` is constant, which is false for the squaring
  walk (190 of 197 cycles). The 3.093 constant survives.],
  [C],
  [Lemma 14.6.5 (proof)],
  [The colliding-pair formula has a sign error (3,689 of 4,000 cases).],
  [C],
  [Alg. 14 (BSGS)],
  [Claimed to solve the decision problem, but has no loop bound, so it
  does not halt when `h ∉ ⟨g⟩`.],
  [C],
  [Thm 13.6.9],
  ["WLOG `n, w` even" breaks Algorithm 15.],
  [C],
  [§15.5.1, Ex. 15.5.7],
  ["Rigorous" `L(1/2, 2)` omits the full-rank argument.],
  [A],
  [Conj. 15.5.21],
  [The optimisation text and the numeric value: 2^68.9, not 2^67. Partly
  KNOWN.],
  [C],
  [§15.8.2 Gaudry degree],
  [The eliminant degree is `n!·2^{n(n−1)}` in the x-variables.],
  [C],
  [Lemma 15.1.6(8)],
  [`=` should be `≤`.],
  [A, `F ≡ 1`],
)
]

#strong[Survived (C):] - Thm 14.1.1; - birthday examples; - epact
constant 0.8226; - Floyd 3.0929; - tail/cycle `√(πN/8)`; - #strong[rho
`√(πr/2)`]; - #strong[Gaudry–Schost 2.43284] (exact lattice sum); - BSGS
and Algorithm 13; - Lemmas 13.4.4, 13.6.6 and 13.6.7; - the Certicom
ratios; - the stated L-values.

#strong[Survived (A):] the negation-map `√(πr/4)` heuristic, the three-
and four-kangaroo constants, and Theorems 13.2.5, 13.3.1, 14.2.16,
14.3.2, 14.6.2, 14.6.6, 14.9.2, 15.2.7 and 15.3.2. Cited external
results (CEP, Diem, Enge–Stein and others) were not re-proved.

#strong[Leaderboard relevance (interpretation).] - The matched-rho
references the program uses (`√(πr/2)`, and `√(πr/4)` with negation)
survived. - Any kangaroo reference built on "`C(n_S)` ≤ 1.06" or a flat
`2√w` at practical `n_S` is low by about 5–7%. - Any Koblitz reference
computed from Ex. 14.4.8 is high by `√h`. - Any summation-polynomial
decomposition test that accepts F\_q-roots of `Summ_n` as relations
without lifting the `y` coordinates over F\_q over-counts by about half
for S₃ in these instances.

I did not audit whether any existing row uses these formulas. That is
the next check.

== 6. Theorem 24.5.2 (Wiener): a concrete failure of the printed proof
(verified by the lead)
<theorem-24.5.2-wiener-a-concrete-failure-of-the-printed-proof-verified-by-the-lead>
v2 prints `0 < d < N^{1/4}/√3`; the official erratum (ERRATA-041)
corrects this to `√6`. `evidence/lead/wiener_window.py` takes all
`p < q < 2p` with `p, q < 2000` and every `d` in the window
`[N^{1/4}/√6, N^{1/4}/√3)` with `gcd(d, φ) = 1`.

- In #strong[941 of 34,211] cases, `d` is not an `e`-cofactor of the
  Euclidean algorithm on `(e, N)`, which is the route the printed proof
  uses.
- Smallest example: `N = 137·167 = 22879`, `e = 19351`, `d = 7 < 7.10`.
  The XGCD cofactors are 1, 1, 6, 13, 214 and 1511.
- Positive control: below the corrected `√6` bound there are #strong[0
  failures in 18,597] cases.

This refutes the printed proof, not the existence claim. Polynomial-time
extensions beyond `N^{1/4}` exist in the literature (recalled, not
verified here). The catalog should carry this erratum on 24.5.2.

== 7. Recommended follow-ups (none executed here)
<recommended-follow-ups-none-executed-here>
+ #strong[PR \#2945 catalog:]
  - pin `pymupdf==1.26.6` in the README and record it in
    `provenance.json`;
  - extend the proof classifier to proofs in the same block and
    displaced proofs (11 rows), and to "Proof: see/This is …" citations
    (at least 10 rows);
  - parse Appendix B without `sort=True` (42 rows);
  - move ERRATA-041 to Theorem 24.5.2 and record the three edition-drift
    maps.
+ #strong[Formal lane:]
  - file a correction or follow-up target for the minimal Montgomery
    statement and the inverse form;
  - before any Chapter 2 complexity target, write a cost-model note. The
    Chapter 2 table above is a ready-made counterexample corpus: each
    row is a `formal_counterexample` candidate.
+ #strong[Baselines:] audit leaderboard and ecbench references for the
  kangaroo `C(n_S)`, the Koblitz `√h` factor, and summation-polynomial
  relation acceptance over F\_q (Thm 15.8.2).

== Provenance and limits
<provenance-and-limits>
- #strong[Verified by the lead in this session] (code in
  `evidence/lead/` and `lean/`):
  - Lemma 2.5.3 and the Lean statement;
  - Thm 15.8.2, re-derived independently;
  - the Wiener window;
  - three Chapter 2 rows and two catalog rows, re-read against the PDF.
- #strong[Computed by delegated agents] (Sonnet: catalog; Opus: Chapter
  2, Chapters 13–15), with their scripts and outputs committed
  unchanged. These are not independently re-run unless listed above.
- #strong[Not covered:]
  - Chapters 1, 3–12 and 16–26, apart from Thm 24.5.2;
  - unlabelled prose beyond the rows listed;
  - re-proving cited external theorems;
  - a Mathlib build of the PR file.
- #strong[Copyright:] no book text, page images or the full catalog
  JSONL are committed. Scripts regenerate what they need from the pinned
  PDF URL and hash.
