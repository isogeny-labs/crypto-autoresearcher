---
id: KN-OPEN-814b4c
type: open_problem
title: >-
  With D = 2^16 now measured for the F_p-rational (Z/2)^4 x| S_5 quotient at
  n = m = 5, how does it compare with the S_5 arm on the same targets, and what
  is its per-system solve cost once the change of order is no longer Wiedemann?
tags: [gfpn, ecgfp5, double-odd, summation-polynomial, semaev, 2-torsion,
  symmetrization, weil-descent, ideal-degree, groebner, msolve, sparse-fglm,
  change-of-order, hermite-normal-form, pdp, index-calculus, extension-field,
  open, ecdlp]
confidence: reported
status: open
source_refs: [KN-OPEN-9b4a2b, EV-GFPN-fc5950, H-GFPN-9a29be, H-GFPN-6cc6aa,
  GOAL-GFPN-380702]
added: 2026-11-02
superseded_by: null
---

## What changed

This entry supersedes `KN-OPEN-9b4a2b`. It narrows that entry's question,
because part of it is now measured. Its source is one experiment in the
sibling `crypto` repository, `crypto:research/ecgfp5_quotient_solve_20261101/`
(merged in crypto PR #3267). The protocol was frozen before the first run and
amended five times (A1–A5).

Measured there (msolve 0.6.5, 4 threads, one shared cloud host, tier L):

- **m = 3 validation (resolution criterion 1 of `KN-OPEN-9b4a2b`).** There
  were 30 solves at the primes 4111, 262231 and 33554371, each with a
  planted and a random target. Every arm gave its predicted D: raw 384,
  S_3 64, quotient 16. The planted point was recovered. The identity control
  mapped every rational raw solution onto a quotient solution.
- **m = 5 (resolution criterion 2).** The quotient (6 unknowns, degrees
  8,8,8,8,8,2) was solved completely at p' = 4111, 262231 and 33554371, three
  primes spanning 13 bits. D = 65,536 = 2^16 = 2^{(m-1)^2} in every cell, and
  the planted point was recovered every time. Peak RSS was 4.68, 6.47 and
  6.41 GiB, under a 12 GiB / 4 h envelope that no cell reached.
- **Per-system cost.** Whole-solve c_cyc (CPU-s × 2.8 GHz) was 2^46.30,
  2^46.56 and 2^46.63. F4 alone was 2^44.72, 2^45.05 and 2^45.29. About
  two-thirds of c is msolve's Wiedemann-based sparse-FGLM sequence: the
  multiplication matrix has 4,920 dense columns (89% dense). The eliminant
  itself takes about 1 s.
- **Solver probes at 4111, none of which improved on grevlex F4.** Three
  weighted orders (FSV 2016) and two Singular `sba` runs were tried.
  Grevlex shows no degree fall on this system.

So the m = 5 law D = 2^16, and solvability within a stated envelope, are
measured at toy primes. They are no longer open.

## Statement (what remains open)

1. **The S_5 comparison at m = 5 on the same targets.** This is criterion 3
   of `KN-OPEN-9b4a2b`. The S_5-symmetrized arm was measured at m = 3 only.
   At m = 5 the quotient's D = 2^16 has been measured, but not against an
   S_5 arm on the same targets. The orbit non-freeness gap at m = 5 is
   therefore not reported. It must never be reported against the constant
   2^20.
2. **The per-system cost with a sub-Wiedemann change of order.** Under the
   G1 rule of `crypto:research/ecgfp5_lead_evaluation_20261031`, the
   measured whole-solve c sits 0.30–0.63 bits above the CLOSE threshold
   (2^46). F4 alone would sit in the not_measured band.
   - Berthomieu–Neiger–Safey El Din (ISSAC 2022, arXiv 2202.09226) change
     of order via the Hermite normal form of a t×t polynomial matrix costs
     O~(t^{ω-1} D), against O~(t D^2) for Wiedemann.
   - Their Table 2 reports about 5× at D = 65,536, at t = 8,092 and 12,870.
   - At t = 4,920 that model predicts the finish dropping from about 20,700
     to about 3,000 CPU-s. That would move c to about 2^45.1–2^45.6, which
     is G1 not_measured, not CLOSE. This is a prediction, not a measurement.
3. **The degree-4 Macaulay rank (H-GFPN-6cc6aa).** It remains untested.

## Resolution criterion

- Item 1 is resolved by an S_5 arm solved at m = 5 on the quotient's own
  targets. It needs at least three primes spanning 12 or more bits, a
  recorded envelope, and its D and gap reported. A memory or time stop is
  not_measured.
- Item 2 is resolved by a complete solve whose finish is not Wiedemann
  sparse-FGLM: an HNF/PML change of order or equivalent. It runs on the same
  quotient systems, recovers the planted point, uses a frozen protocol, and
  reports whole-solve c at all three primes.

## What must NOT be said

- **Not** "EcGFp5 is below 142 (or 128) bits", nor that it is safe. c is a
  per-system stage cost at toy primes, not an end-to-end attack cost, and
  no matched rho reference exists for it.
- **Not** "the symmetrization does not help". D fell from 2^20 (S_5,
  model) to 2^16 (measured). What remains open is the cost per system at
  that D.
- **Not** "the quotient is closed". Its lead in the atlas
  (`LEAD-ICP-gfp5-symmetrized-gaudry`) is `closed_dominated`. It stays in
  the pursuit queue with explicit revisit conditions, and item 2 is one of
  them.
