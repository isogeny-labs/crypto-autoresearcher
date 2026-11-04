#set page(paper: "a4", margin: 2cm)
#set text(font: "Libertinus Serif", size: 9.5pt)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show math.equation: set text(font: "Libertinus Serif")
#set par(justify: false)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
= Quadratic-phase leakage of the small-x factor base (lead N2)
<quadratic-phase-leakage-of-the-small-x-factor-base-lead-n2>
Lead: `LEAD-EXO-quadratic-phase-small-x-leakage`. Protocol `protocol.json`, QUADPHASE-20261104, was frozen before data (sha256 `6a44309417a9…`, commit 2d6c661a), with the run and analysis scripts pinned by hash.

#strong[Verdict (frozen rule): NULL, with valid controls.] At N ≈ 2#super[12–2]14, the small-x factor base’s discrete logs correlate with quadratic phases e((αl² + βl)/N) no more than negation-closed random sets of the same size do. The test detects #strong[coherent single-phase leakage of about 0.3 or more of the set] (validator’s probe). The planted control is full-coherence only, and weaker or multi-peak quadratic structure is untested. The result sits beside H-PSEUDO’s linear phases and carries the same scale caveat: a toy size cannot see a correlation of order 1/polylog. (Wording corrected after validation, `VALIDATION.md`.)

== Design
<design>
- #strong[Statistic.] Q(S) \= max over α ∈ \[1, N−1\] and β ∈ \[0, N−1\] of |Σ\_{l∈S} e((αl² + βl)/N)| / √|S|, computed with one length-N FFT per α.
- #strong[Curves.] Each has prime order N ≠ p, with p the largest prime below 2^L. There are 3 curves at each decisive size L \= 12, 13, 14, and 1 descriptive curve at L \= 16.
- #strong[Arms.]
  - EC: the discrete logs of the first 512 points sorted by (x, y), the H-PSEUDO small-x rule.
  - Null: 40 negation-closed random 512-sets per curve (5 at L \= 16), applying the D1 lesson.
  - Planted: the negation-closed set {l : α₀l² mod N \< 512} (size ≈ 512), which must spike at α₀.
- #strong[Rule.]
  - SIGNAL iff Q\_EC exceeds every null draw on 2 of 3 curves at 2 of the 3 decisive sizes.
  - NULL iff Q\_EC’s percentile lies in \[0.05, 0.95\] on ≥ 8 of 9 decisive curves.
  - Validity requires planted Q ≥ 3 × null max with the argmax at α₀, and A/A within 3%.
- #strong[Sizes.] These were reduced from the memo’s 2^14 and 2^16, because one Q evaluation costs about 400 s at 2^16 here. That reduction is recorded in the protocol.

== Results
<results>
#align(center)[#table(
  columns: 6,
  align: (col, row) => (left,right,right,left,right,right,).at(col),
  inset: 6pt,
  [size], [N], [Q\_EC], [null mean / max], [u], [planted / null max],
  [2^12],
  [4133],
  [4.102],
  [4.028 / 4.512],
  [0.650],
  [4.9×],
  [2^12],
  [3989],
  [4.144],
  [3.990 / 4.642],
  [0.700],
  [4.7×],
  [2^12],
  [4007],
  [4.268],
  [4.036 / 4.787],
  [0.850],
  [4.8×],
  [2^13],
  [8231],
  [4.152],
  [4.224 / 4.658],
  [0.375],
  [5.2×],
  [2^13],
  [8081],
  [4.151],
  [4.257 / 4.995],
  [0.375],
  [4.4×],
  [2^13],
  [8167],
  [3.997],
  [4.187 / 4.928],
  [0.175],
  [4.6×],
  [2^14],
  [16417],
  [4.303],
  [4.415 / 5.400],
  [0.350],
  [4.0×],
  [2^14],
  [16273],
  [4.579],
  [4.524 / 5.678],
  [0.625],
  [3.8×],
  [2^14],
  [16427],
  [4.201],
  [4.405 / 4.894],
  [0.125],
  [4.5×],
  [2^16],
  [65167],
  [4.725],
  [4.609 / 4.708],
  [1.000],
  [4.8×],
)
]

#figure([#image("quadphase.svg")],
  caption: [
    Q per curve
  ]
)

- #strong[All decisive curves are inside the null’s band.] 9 of 9 decisive curves fall inside it (u from 0.125 to 0.85), and no size has a curve above the null maximum.
- #strong[The controls are valid.] The planted control is 3.8–5.2× the null maximum on every curve, always at the planted α₀, and the A/A even/odd difference, pooled per size, is at most 2.3% (per curve up to 4.0%).
- #strong[2^16 is descriptive only.] That one curve sits above all 5 of its null draws (Q 4.725 against max 4.708). With 5 draws this happens with probability 1/6 under the null. It is recorded, not interpreted. A 2^16 rerun with 40 draws would settle it, at about 4.5 core-hours here.

== Consequence
<consequence>
The lead’s amended discriminator (8 of 9 decisive curves inside the band) is met on the NULL side at toy scale. Linear (H-PSEUDO) and coherent quadratic phases of the small-x predicate in log order both look like those of a random negation-closed set at these sizes. The exploitation path in the lead (sparse Fourier recovery of k²) has nothing to act on there.

== Deviations
<deviations>
- No S3 checkpoint (no upload token). With the owner’s approval, the pushed branch is the resume record.
- The run shared the cores with three other runs. Values are exact, so only wall time was affected.
- Environment: Python 3.13.18 and NumPy 2.5.3 (session container). No experiment.export/v1 bundle was written. The independent validation recomputed all 385 rows with a separate, FFT-free implementation and matched to within 7e-15.

== Reproduce
<reproduce>
```
xz -dc rows.jsonl.xz > rows.jsonl     # or rerun:
python3 quadphase.py --protocol-sha 6a44309417a905167606a10754a6fad66de617a16c81feed73cd9cace0a02efb --out rows.jsonl --workers 3
python3 analyze_quadphase.py rows.jsonl verdict.json
python3 figures.py; ./build_pdf.sh
```
