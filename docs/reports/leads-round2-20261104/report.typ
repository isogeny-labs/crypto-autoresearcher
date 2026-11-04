#set page(paper: "a4", margin: 2cm)
#set text(font: "Libertinus Serif", size: 9.5pt)
#show raw: set text(font: "Libertinus Serif", size: 9pt)
#show math.equation: set text(font: "Libertinus Serif")
#set par(justify: false)
#show heading.where(level: 1): set text(size: 14pt)
#show heading.where(level: 2): set text(size: 12pt)
= ECDLP leads, round 2 (2026-11-04)
<ecdlp-leads-round-2-2026-11-04>
Two frozen experiments have their own reports: `../anomalous-qtt-20261104` (NULL) and `../lowdeg-rank-20261104` (HOLDS). This report covers everything else from the round:

- three derivation checks;
- an adversarial review of a closed row;
- two literature amendments;
- new-lead synthesis, with the real novelty gate.

None of it is a measurement of attack cost. No disposition is changed. Proposals for the Coordinator are marked.

== Derivation checks (`checks/`, each runs in seconds to minutes)
<derivation-checks-checks-each-runs-in-seconds-to-minutes>
#align(center)[#table(
  columns: 3,
  align: (col, row) => (left,left,left,).at(col),
  inset: 6pt,
  [check], [claim tested], [result],
  [#strong[D1] `d1_symnull.py`],
  [H-PSEUDO’s recorded R ≈ 1.28–1.34 is the effect of a negation-closed factor base against an asymmetric null],
  [#strong[Supported.] Random negation-closed sets, with no curve structure, give R \= 1.29 (N ≈ 2^17) and 1.31 (N ≈ 2^20) against the same null. The H-PSEUDO run code keys points by (x, y), so its factor base is ±-closed with signed logs. Against a symmetric null the recorded 2^20 value is R ≈ 1.02.],
  [#strong[D2] `d2_relations.py`],
  [low-degree rank deficits come from short multiplier relations Σc\_i b\_i ≡ 0 mod N],
  [#strong[Supported.] At p \= 211 and 227, 88–90% of fresh random triples are exact. Every deficient triple has a relation with |c| ≤ 2, and both original p \= 211 triples do (b₂ ≡ −2b₃ and b₂ ≡ 2b₃).],
  [#strong[D3] `d3_logfb.py`],
  [the discrete-log labelling’s √p-scale QTT rank comes from the factor base’s log set, not from the group law],
  [#strong[Supported in mechanism, two numeric predictions missed.] A log-AP factor base gives rank 12, 18 and 16 at p \= 251, 509 and 1021, against 55–120 for small-x and random-log factor bases. The predicted ≤ 12 at every size and the ratio range \[1, 4\] were missed (observed 18 at L \= 9, ratio 4.3–6.1).],
)
]

#figure([#image("d1-symmetry.svg")],
  caption: [
    D1
  ]
)

These three checks went into rows as follows:

- #strong[D1:] a note on the H-PSEUDO row, with no disposition change. Its revisit trigger now names a negation-matched null.
- #strong[D2:] a note on the low-degree row.
- #strong[D3:] a note on the holant row. The QTT branch reduces to the digit complexity of log(FB).

#strong[Proposed for the Coordinator:]

- rerun the full H-PSEUDO ladder against a negation-closed null;
- consider filing the holant QTT branch `closed_dominated` by the character-sum row.

== Review: `LEAD-EXO-augmented-oracle-ggm` (`augmented-oracle-review.md`; red-team, Opus)
<review-lead-exo-augmented-oracle-ggm-augmented-oracle-review.md-red-team-opus>
The closure holds only for oracles computable from labels alone: endomorphism image as a label, label halving, incidence over a label factor base, and label-valued net. It fails for every coordinate-revealing oracle: x, y, full point, x-valued halving, field-valued jet and field-valued net. Two x-queries plus free local work give the logarithm. The row also states "jet O(1)", which CORR-20260727-003 withdrew ("No theorem exists", verified here). Its claim that the threshold oracle "needs private data" contradicts KN-FIND-982fdf, which says it is publicly computable (verified here). Its `revisit_when` has fired.

#strong[Proposed for the Coordinator:] split the row. Keep it closed for label oracles, and open `LEAD-EXO-coordinate-revealing-oracles`, which states that the GGM gives no bound there and that the open question is index calculus itself. The row is #strong[not edited] in this round.

== Amendments from the 2026-11-01 scouting report (`amendments-literature.md`)
<amendments-from-the-2026-11-01-scouting-report-amendments-literature.md>
- #strong[A1, applied as a scoped note to `LEAD-ICE-generic-oracle-arity-cost-floor`.] 3SUM-Indexing bounds (Golovnev et al., STOC 2020) assume preprocessing, an explicit list and |G| ≤ N^c. They give context only and do not extend the wall. 3SUM-Indexing is Goldstein et al. (WADS 2017), not the ESA 2016 paper.
- #strong[A2, applied as a scoped note to `LEAD-EXO-invertible-hint-subset`.] Lange–Winterhof (COCOON 2002, AAECC 2003) and Kiltz–Winterhof (2004) are verified at abstract level only, because the theorems are behind publisher logins. The row’s next step now begins by reading them.

== New leads (`new-leads-memo.md`; synthesist, Opus) and the real novelty gate
<new-leads-new-leads-memo.md-synthesist-opus-and-the-real-novelty-gate>
The synthesist could not run `lead_atlas.py`, so its matches were emulated. Here the real gate (`--match`, several phrasings) was run:

#align(center)[#table(
  columns: 3,
  align: (col, row) => (left,left,left,).at(col),
  inset: 6pt,
  [proposal], [top atlas hits (score)], [decision],
  [N1, weak curve classes as positive controls for the numeric instruments],
  [SafeCurves audit (11), H-PSEUDO (10), kernel-of-reduction (10)],
  [#strong[filed] as `LEAD-EXO-weak-class-instrument-calibration`],
  [N2, quadratic-phase (U³) leakage of the small-x predicate],
  [H-PSEUDO (12, linear phases only), invertible-hint (8)],
  [#strong[filed] as `LEAD-EXO-quadratic-phase-small-x-leakage`],
  [N3, small-height rational (Farey) factor base],
  [Coppersmith small-root (15), global-lift small height (12), cofactor ladder (12)],
  [#strong[not filed]: collides with existing rows],
)
]

Items D1–D3 of the memo are the checks above. D4 predicts that the ML lead’s planted homomorphic-leak control would train at chance. It is recorded here for that row’s owner and was not tested in this round.

== Not done
<not-done>
- Zhang–Liu (ePrint 2018/795) is still unread. eprint.iacr.org blocks this session, and no bypass was used.
- The Lange–Winterhof and Kiltz–Winterhof theorem statements are behind publisher logins.
- Conductor task T-5751 can only be closed from the owner’s machine.
