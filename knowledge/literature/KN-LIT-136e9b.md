---
id: KN-LIT-136e9b
type: literature
title: "Extending the special number field sieve"
authors:
  - "Oliver Schirokauer"
year: 2006
venue: "Talk slides, 20 September 2006 (venue not stated)"
identifiers:
  eprint: null
  arxiv: null
  doi: null
  url: null
tags: [number-field-sieve, snfs, finite-field, dlp, pairing, weight, metrology]
confidence: reported
citation_verified: read
added: "2026-11-20"
superseded_by: null
---

## Contribution

Asks how far the special number field sieve (SNFS) can be pushed when the
characteristic is not of the form `r^e + s` but merely of **small signed binary
weight**, and answers with a two-sided but deliberately pessimistic analysis.
Given `p = sum_{i=1..w} eps_i 2^{c_i}`, the exponents reduced mod `e` split
`[0,e]` into `w-1` gaps; the largest gap `gamma` bounds the coefficients of the
lift polynomial by `2^{e-gamma}`, which fixes the size of the numbers tested for
smoothness and hence the `L_p[1/3; c]` constant.

## Key claims (as reported)

- NFS degree accounting: SNFS tests `M^{d+1} p^{1/d}` and runs in
  `L_p[1/3;(32/9)^{1/3}]`; the general case tests `M^{d+1} p^{2/(d+2)}` and runs
  in `L_p[1/3;(64/9)^{1/3}]`.
- Worked instance: `p = 2^15474 - 2^14954 + 2^14432 + 1` (weight 4) with
  `f = (2^520 - 1)x^14 + 2^547 x^13 + 1` and `p | f(2^1069)`; the tested numbers
  are bounded by `M^15 2^1619`, strictly between the SNFS and GNFS bounds.
- Worst-case gap `e/(w-1)` gives `theta = (2w-3)/(w-1)` and
  `L_p[1/3;(32 theta/9)^{1/3}]`: 1.526, 1.747, 1.810, ..., 1.887 for `w = 2..10`.
- Method-specific lower bound: there are infinitely many weight-`w` integers for
  which this construction cannot beat `(32 tau^2/9)^{1/3}`, with the slides'
  `tau`: 1.526, 1.730, 1.796, ..., 1.881 for `w = 2..10`.
- Average-case counterweight: the mean largest gap (`MESS`) is far above
  `e/(w-1)`, so the worst-case exponent is not a predictor for a particular
  prime. "These results are deceptive. For a given weight w, the asymptotic gain
  over the general NFS is only realized for large p."
- Part II extends the same trick to `F_{p^k}` using the Joux–Lercier–Smart–
  Vercauteren form (a quadratic `f` dividing `g` mod `p`), with two worked
  pairing-relevant examples (`F_{p^2}` and an SNFS `F_{p^18}`) and the
  Barreto–Naehrig `F_{p^12}` case; the `d`-optimality table is explicitly
  asymptotic and flagged as too optimistic at `d = 4`.

## Derived here (not stated on the slides)

- The `e = inf` column of the gap table is exactly the harmonic ratio
  `H_{w-1}/(w-1)`: 0.750, 0.611, 0.521, 0.457, 0.408, 0.370, 0.340, 0.314 for
  `w = 3..10`. So the average largest gap is `H_{w-1}/(w-1) * e`, not
  `e/(w-1)`; the finite-`e` columns converge to it.
- The `tau` column is reproduced exactly by `tau = (sqrt(2)(w-2)+1)/(w-1)`
  (values 1.000, 1.207, 1.276, 1.311, 1.331, ..., with `tau -> sqrt(2)`).
- Consequently both constants tend to `(64/9)^{1/3} ≈ 1.923` as `w -> inf`:
  `theta -> 2`, `tau -> sqrt(2)`. **The weight advantage vanishes with weight**;
  large-`w` SNFS degenerates to the general NFS on those integers.
- The worked example is arithmetically consistent: `2^12 p = 2^520(2^1069)^14 -
  (2^1069)^14 + 2^547(2^1069)^13 + 1` checks, residues are `{0,508,535,1057}`
  (max gap 522), and `2^{1069-522} = 2^547` is exactly the coefficient. The
  `2^1619` exponent is the *product* of the two sides (`2^1069` rational and
  `2^547` algebraic), which is why it sits between `p^{1/14} ≈ 2^1105` and
  `p^{2/16} ≈ 2^1934`.

## Relevance to this program

- **Not an E(F_p) attack.** NFS applies to `F_p^*` and `F_{p^k}`; the scouting
  pass recorded no surviving NFS-on-`E/F_p` mechanism
  (`docs/reports/ecdlp-lead-discovery-20261024/scouting/scout-algorithmic-nt-smoothness.md`,
  K3, plus K17/K18 in the same report).
- **Scope guard for the lift barrier.** SNFS is the canonical case where a
  characteristic-0 *field representation* provably improves the index-calculus
  exponent. `coordination/goals31/drafts/cluster_12_lift_G31-002.md` is about
  *point supply* from a height-bounded Mordell–Weil lattice; the SNFS guard there
  cites this entry so the barrier can never be read as "characteristic 0 is
  useless".
- **Extrapolation calibration for G30-003.** The gap between the worst-case
  `theta` guarantee, the `tau` method lower bound, and the average `MESS` value
  is a historical worked example of why an asymptotic exponent is a poor
  predictor at practical sizes — the discipline G30-003 encodes. The `tau` bound
  is also the rare shape worth imitating: a lower bound on one *construction
  class*, never on DLP hardness.
- **Pairing lane.** Part II's `d`-selection table (bits ranges per `d`) is
  superseded by the later Special-TNFS line already in the corpus
  (`KN-LIT-7084`, `KN-LIT-1624b6`, `KN-LIT-2223`); the owning lead is
  `LEAD-TRF-pairing-target-field-recost`, not a new goal.
- **Instance metrology.** `harness/toycurve.py` now records
  `signed_binary_weight(p)` in the instance block (`instance_metadata`), so a
  prime reused in an `F_p^*`/`F_{p^k}` control is not silently treated as a
  neutral baseline.

## Not verified here

No PDF, publisher page or proceedings record exists in this checkout; the text
was an operator-supplied transcript of slides dated 20 September 2006, with
visible OCR corruption in formulas (see the addendum). The arithmetic checks
above are re-derivations from the transcript's own numbers; they do not
establish that the slides say what the transcript says, and the `tau` formula in
the transcript is garbled and was reconstructed from the table it accompanies.
The 2006 "NFS-security = 13180 bits" figure for the example prime is quoted, not
recomputed.

## Provenance

Transcript: `knowledge/literature/addenda/KN-LIT-136e9b/20261120-136e9b.md`
(operator-supplied, unverified text). Created 2026-11-20 from that transcript as
part of the goals31 scoping pass; no corpus record was modified.
