#set page(paper: "a4", margin: 2cm)
#set text(font: "Libertinus Serif", size: 9.5pt)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show math.equation: set text(font: "Libertinus Serif")
#set par(justify: false)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
= Low-degree query lead, step (b): exact rank of the interpolation matrix
<low-degree-query-lead-step-b-exact-rank-of-the-interpolation-matrix>
Lead: `LEAD-EXO-low-degree-query-lower-bound`. Protocol `protocol.json`, LOWDEG-RANK-20261104, was frozen before data (sha256 `bbcdab319667…`, commit 3edaed22), with the run script, rank routine and analysis pinned by hash. Seeds use the export checker’s own `derive_seed`, and the export passes `check-export` with 0 findings.

#strong[Verdict (frozen rule): HOLDS, with valid controls.] With random multipliers b\_i, the evaluation matrix of degree-≤D monomials in the coordinates of (\[b\_1\]R, …, \[b\_t\]R) has #strong[full rank on every candidate log] once the monomial count is about twice the number of candidates. This held in 39 of 39 decisive cells, at p \= 251, 509, 1021 and 2039. The desk note’s interpolation attack therefore goes through at toy size: each degree-D test can be made to answer "k ∈ S?" for any set S, so H1 of the row (a query bound in terms of D) is false there.

#strong[This is not an attack-cost claim.] Building such a test uses about N^ω local field operations, and the test polynomial has about N/2 or more monomials (see the time-charging note below), so a plain DL table dominates it.

== Design
<design>
- #strong[Instances.] 37 in total. Two prime-order curves (distinct orders) are taken at each of p \= 251, 509, 1021, with D ∈ {2, 3} and t chosen so that C(2t+D, D)/(N−1) is about 0.5, 1 or 2. One instance at p \= 2039 has D \= 3 and ratio about 2.
- #strong[Arms, with 3 replicates each.]
  - rand: random b\_i (the candidate).
  - ap: small b\_i \= 1..t (reference).
  - shift: X\_i \= R + \[i\]P (positive control; rank ≤ 3Dt + 1 by Riemann–Roch).
  - null: uniformly random points of F\_p^(2t) (negative control).
- #strong[Decision rule.] HOLDS iff the full-rank fraction of rand cells with ratio ≥ 1.5 is at least 0.9 at every size. The controls must also hold: null full rank and shift within its bound.

== Results
<results>
#align(center)[#table(
  columns: 3,
  align: (col, row) => (left,right,right,).at(col),
  inset: 6pt,
  [size], [p], [full-rank fraction, rand, ratio ≥ 1.5],
  [L\=8],
  [251],
  [1.00],
  [L\=9],
  [509],
  [1.00],
  [L\=10],
  [1021],
  [1.00],
  [L\=11],
  [2039],
  [1.00],
)
]

- #strong[Controls.] The null is full rank in 100% of its cells, and every shift cell is within 3Dt + 1, far below full rank.
- #strong[Small multipliers (ap).] These are also full rank at ratio ≥ 1.5 in 36 of 39 cells, so large multipliers are not required at this size. With b\_i ≤ 3t, Σ b\_i² is already about 9t³, far above N, so the pulled-back degree Δ is not limiting.

#figure([#image("lowdeg-rank.svg")],
  caption: [
    rank against monomials
  ]
)

== Post-data observations (not preregistered)
<post-data-observations-not-preregistered>
+ #strong[Deficits below ratio 1.5.] Random-multiplier cells fall below the generic expectation min(C, \#mon − t·C(2t+D−3, D−3)) at ratios below 1.5, with a mean deficit of 68 at p \= 1021 in the 0.75–1.5 band. The round-2 derivation check D2 (`docs/reports/leads-round2-20261104/checks/d2.json`) explains the p \= 211 deficits exactly: every deficient triple carries a short relation Σc\_i b\_i ≡ 0 mod N with |c| ≤ 2, and 88–90% of fresh triples are exact. With t up to 31 multipliers, such relations are almost certain to appear, so the frozen design confounds them in the middle band. They do not affect the decisive band, where rank is full regardless.
+ #strong[Time-charging note (memo heuristic HD2c).] A test answering "k ∈ S?" for |S| ≈ N/2 needs a polynomial from a span of dimension greater than N/2. Its description, and the per-target evaluation, cost at least about N/2 field operations. The attack is therefore a preprocessing attack with advice N^(1+o(1)), and a DL table beats it. The row’s model note should charge description length, not only queries.

== Deviations
<deviations>
- #strong[No S3 checkpoint.] There is no upload token. With the owner’s approval (session 2026-11-04), the pushed branch is the resume record.
- #strong[Compression.] Rows and export are stored as `.xz`. Uncompressed hashes are in `data.sha256`.

== Reproduce
<reproduce>
```
xz -dc rows.jsonl.xz > rows.jsonl     # or rerun (about 25 min):
python3 lowdeg_rank.py --protocol-sha bbcdab31966734404349e193614ef75b9b6bc2cdc0495aa63a5ccb2cce737756 --out rows.jsonl
python3 analyze_lowdeg.py rows.jsonl verdict.json
python3 figures.py; ./build_pdf.sh
```
