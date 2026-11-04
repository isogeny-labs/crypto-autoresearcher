#set page(paper: "a4", margin: 2cm)
#set text(font: "Libertinus Serif", size: 9.5pt)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show math.equation: set text(font: "Libertinus Serif")
#set par(justify: false)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
= Anomalous-curve follow-up: QTT structure of the transfer matrix
<anomalous-curve-follow-up-qtt-structure-of-the-transfer-matrix>
This is a follow-up to holant step (b) (`docs/reports/holant-step-b-qtt-20261104`). In that run the single curve whose x-labelling scored below its random-relabelling null was p \= 61, a \= 21, b \= 57. It has \#E \= p, so it is #strong[anomalous], the class where Smart’s attack makes the DLP easy. This study tests whether that was a property of anomalous curves or chance.

Protocol `protocol.json`, ANOMALOUS-QTT-20261104, was frozen before data (sha256 `82703e7f25ed…`, commit ef35b300). The run script, the core (a byte copy of step (b)’s frozen `qtt_rank.py`) and the analysis script are all pinned by hash.

#strong[Verdict (frozen rule): NULL, with valid controls.] Anomalous curves show no QTT structure beyond ordinary prime-order curves at p ≤ 127. The p \= 61 observation was chance. This is a structure statistic, not a cost claim.

== Design
<design>
- #strong[Curves.] All 20 primes 37 ≤ p ≤ 127, where QTT ranks are not saturated. For each prime, up to 4 anomalous isomorphism classes ((a u⁴, b u⁶) orbits) are drawn by a protocol-hash-seeded stream, together with an equal number of ordinary prime-order classes. That gives 63 + 63 curves. The motivating curve’s class is #strong[excluded] from the test and reported separately.
- #strong[Per curve:]
  - X, M in natural x-labelling;
  - LOG, the discrete-log orbit labelling (positive control);
  - 99 random relabellings (the null). Draw 0 scored against draws 1–98 is the A/A check.

  FB is the ⌊√p⌋ smallest x-coordinates on E.
- #strong[Primary metric.] u\_X is the mid-rank percentile of X’s interleaved QTT parameter count (Σ log₂ rank) within that curve’s own null, so each curve is compared with itself. The secondary metric is the same with r\_max.
- #strong[Test.] Mean u\_X(ordinary) − mean u\_X(anomalous), with a one-sided label permutation stratified by prime (9999 resamples).
- #strong[Rule.]
  - EFFECT iff p \< 0.01 and mean u\_X(anomalous) \< 0.25.
  - NULL iff p ≥ 0.05.
  - Validity requires mean u\_LOG \< 0.05 in each group and A/A in \[0.35, 0.65\].

== Results
<results>
#align(center)[#table(
  columns: 7,
  align: (col, row) => (left,left,right,right,right,left,right,).at(col),
  inset: 6pt,
  [metric], [verdict], [p (perm.)], [mean u\_X anomalous], [mean u\_X ordinary], [u\_LOG (anom, ord)], [A/A],
  [Σ log₂ rank (primary)],
  [#strong[NULL]],
  [0.831],
  [0.534],
  [0.483],
  [0.00, 0.00],
  [0.506],
  [r\_max (secondary)],
  [NULL],
  [0.620],
  [0.493],
  [0.478],
  [0.00, 0.00],
  [0.499],
)
]

#figure([#image("anomalous-ecdf.svg")],
  caption: [
    ECDF of within-null percentiles
  ]
)

- The anomalous curves sit slightly #strong[above] the ordinary ones, the opposite of the hypothesised direction. Both ECDFs follow the uniform line.
- 1 of 63 anomalous curves (1.6%) fell below the 5th percentile, against 6 of 63 ordinary curves (9.5%).
- The motivating curve, rerun under this protocol’s seeds, again sits low (u\_X \= 0.025). At u ≤ 0.025 there are 4 ordinary curves and 0 anomalous ones among the 126, which is 4 against 3.2 expected under the null. So it is a tail draw, and the tail is not anomalous-specific. (Wording corrected after independent validation.)
- Both controls behave as designed. LOG is below every null draw on every curve (u \= 0), and the A/A mean is 0.51.

== Consequence
<consequence>
The pointer recorded in the holant step-(b) report and in the lead row is closed: at p ≤ 127, anomalous curves show no anomaly-specific digit structure in the x-labelled decomposition network. Smart’s attack exploits the p-adic formal group, not anything this network or its digit labelling sees.

== Deviations and notes
<deviations-and-notes>
- #strong[Export checker mismatch.] The export (`export.json.xz`) fails `check-export` for the same encoding mismatch as step (b) (amendment A1 there). The null draws are not encoded as replicates, the script’s seed formula is not the checker’s, and the motivating curve’s arm is reported outside the export’s arm list. The counts in the export match the rows.
- #strong[Compression.] Rows and export are stored as `.xz` to stay under the 64 KiB in-Git threshold. Uncompressed hashes are in `data.sha256`.
- #strong[No S3 checkpoint.] The container has no upload token. With the owner’s approval (session 2026-11-04), the pushed branch is the resume record. The run took about 2 minutes, with exact counts and no clock.

== Reproduce
<reproduce>
```
xz -dc rows.jsonl.xz > rows.jsonl     # or rerun:
python3 anomalous_qtt.py --protocol-sha 82703e7f25eda9775ec61e7d25dcbc53aeced794f26f740707c5a046a4ec3f84 --out rows.jsonl --include-excluded
python3 analyze_anomalous.py rows.jsonl verdict.json log2_params
python3 analyze_anomalous.py rows.jsonl verdict_rmax.json r_max
python3 figures.py; ./build_pdf.sh
```
