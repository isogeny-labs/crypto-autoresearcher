#set page(paper: "a4", margin: 2cm)
#set text(font: "Libertinus Serif", size: 9.5pt)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show math.equation: set text(font: "Libertinus Serif")
#set par(justify: false)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
= H-PSEUDO re-read against a negation-matched null
<h-pseudo-re-read-against-a-negation-matched-null>
Lead: `LEAD-EXO-dl-character-sum-pseudorandom` (H-PSEUDO). The original run is EXP-ECDLP-1ed445 / RUN-ECDLP-1ed445-001 (EV-ECDLP-f83a17). Protocol `protocol.json`, HPSEUDO-SYMNULL-20261104, was frozen before data (sha256 `cf05250833d8…`, commit f9931a3e).

#strong[Verdict (frozen rule): EXPLAINED, with every control valid.] H-PSEUDO’s recorded constant offset R ≈ 1.28–1.34 is fully accounted for by a null mismatch. The original run keys points by (x, y), so the small-x factor base is closed under negation and its character sums are real. The null was an asymmetric uniform subset. Against a negation-closed null, R is 1 within about 0.04 at every rung.

== Design
<design>
- #strong[EC arm.] The recorded per-curve C\_EC from `stage2.per_curve`, with B \= 512. This study does not re-measure them; it replays a subset instead (below).
- #strong[Decisive (out-of-sample) curves.] At bits 20 and 22, the 12 recorded curves that did not feed R\_mean (curve\_index 8–19). No matched-null ratio had been computed for them before this protocol. #strong[Calibration curves:] the 8 R\_mean curves at each rung. These were already re-read in-sample by the round-2 validator, and the protocol checker rejected them as decisive for that reason.
- #strong[Nulls.] Each curve’s own N gets 20 negation-closed random 512-sets. The original law, uniform 512-subsets with 40 draws at each rung’s representative N, is used as a replication check against the recorded null means.
- #strong[Controls.]
  - Positive: a planted negation-closed arithmetic progression in log space.
  - Replication: the asymmetric null mean against the recorded C\_null\_mean.
  - Replay: C\_EC recomputed with the original code (`run_character_sum_ladder.py`) for 18 curves, including the smallest-N curve at bits 24 and 26.
  - A/A: even- against odd-indexed draws.
- #strong[Rule.] EXPLAINED iff at both decisive rungs the bootstrap CI of mean R\_sym contains 1 and |mean R\_sym − 1| ≤ 0.05.

== Results
<results>
#align(center)[#table(
  columns: 5,
  align: (col, row) => (left,right,left,left,right,).at(col),
  inset: 6pt,
  [rung], [recorded R (asymmetric null)], [R\_sym, calibration (8 curves) \[95% CI\]], [R\_sym, out of sample \[95% CI\]], [mean u\_sym],
  [20],
  [1.334],
  [1.012 \[0.963, 1.061\]],
  [1.040 \[0.999, 1.092\] (n\=12)],
  [0.62],
  [22],
  [1.280],
  [0.987 \[0.954, 1.032\]],
  [0.993 \[0.972, 1.017\] (n\=12)],
  [0.42],
  [24],
  [1.275],
  [0.974 \[0.948, 1.000\]],
  [–],
  [0.35],
  [26],
  [1.342],
  [1.009 \[0.990, 1.036\]],
  [–],
  [0.57],
)
]

#figure([#image("hpseudo-symnull.svg")],
  caption: [
    R against matched null
  ]
)

- #strong[Validity, all passed.]
  - Replication: the asymmetric null reproduces the recorded C\_null\_mean to within 0.9% at every rung.
  - Positive control: the planted AP is 3.5–4.0× the rung’s largest symmetric draw.
  - Replay: all 18 replayed curves reproduce the recorded C\_EC within 1e-5, with negation-closed factor bases.
  - A/A: within 2%.
- #strong[Decisive result.] The out-of-sample rungs give R\_sym \= 1.040 (2^20) and 0.993 (2^22), with CIs containing 1. The 2^20 interval only just reaches 1 (lower end 0.999), so a residual of a few percent at that rung is not excluded. 2^22 is centred on 1.
- #strong[Calibration rungs.] These span 0.974–1.012, matching the round-2 validator’s in-sample recomputation (0.96–1.03).

== Consequence
<consequence>
The H-PSEUDO row’s `best_measured` (R ≈ 1.28–1.34) and its framing "the curve behaves like a random set up to a constant" are corrected. Against a matched null, the small-x factor base #strong[is] a random negation-closed set at 2#super[20–2]26, with no constant offset, within about ±0.04. The disposition `exhausted_at_scale` is unchanged and, if anything, strengthened. The revisit trigger should name the matched null. Any other comparison of a negation-closed factor base against an asymmetric null needs the same correction.

== Deviations
<deviations>
- #strong[Out-of-memory hang (infrastructure).] The memory cgroup killed the three pool workers, at about 5 GB each, on the N ≈ 33.6M prime-length FFTs (`dmesg`). The pool then hung with 36 null tasks lost. `complete_run.py` recomputed exactly those tasks with the frozen `job()` and seeds, in one process, then ran the frozen control and replay stages, whose code is copied verbatim. No design parameter changed. This is the protocol’s infrastructure-only retry.
- #strong[No S3 checkpoint.] There is no upload token. With the owner’s approval, the pushed branch is the resume record.
- #strong[Compression.] Rows are stored as `.xz`. The uncompressed hash is in `data.sha256`.

== Reproduce
<reproduce>
```
xz -dc rows.jsonl.xz > rows.jsonl     # or rerun (needs ~6 GB per worker at the top rung; use --workers 1 or 2):
python3 hpseudo_symnull.py --protocol-sha cf05250833d83b48fa05f8df8e37a0f3f2ff71e0da4d14b15c790d428987b135 --out rows.jsonl --workers 2
python3 analyze_symnull.py rows.jsonl verdict.json
python3 figures.py; ./build_pdf.sh
```
