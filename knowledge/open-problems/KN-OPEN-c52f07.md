---
id: KN-OPEN-c52f07
type: open_problem
title: >-
  With D = 2^16 measured for the F_p-rational (Z/2)^4 x| S_5 quotient at
  n = m = 5: how does it compare with the S_5 arm on the same targets, what is
  its per-system solve cost once the change of order is no longer Wiedemann,
  and does the u = x/y polynomial-ring form solve the same cell more cheaply?
tags: [gfpn, ecgfp5, double-odd, summation-polynomial, semaev, 2-torsion,
  symmetrization, fhjrv, pornin, u-coordinate, polynomial-ring-form,
  weil-descent, ideal-degree, groebner, msolve, sparse-fglm, change-of-order,
  hermite-normal-form, block-wiedemann, pdp, index-calculus, extension-field,
  open, ecdlp]
confidence: reported
status: open
source_refs: [KN-OPEN-814b4c, KN-OPEN-9b4a2b, CORR-20261102-7e3a91,
  CORR-20260923-064d0d, EV-GFPN-fc5950, H-GFPN-9a29be, H-GFPN-6cc6aa,
  IDEA-20260905-d0fee4, GOAL-GFPN-380702]
added: 2026-11-02
superseded_by: null
---

## What changed

This entry supersedes `KN-OPEN-814b4c`. It carries that entry's three open
items and their resolution criteria unchanged. It adds one new measurable
item (item 4), and it notes an experiment that is running for item 2.

The new source is a desk audit in the sibling `crypto` repository,
`crypto:research/ecgfp5_representation_audit_20261102/` (branch
`claude/point-decomposition-literature-taddl7`, commit `01205f917`; not yet
merged to crypto main). The correction that scopes the ledger sentence is
`CORR-20261102-7e3a91`.

- **The ring-form sentence is scoped.** `CORR-20260923-064d0d` and
  `KN-OPEN-9b4a2b` say FHJRV's Prop. 8(i) / Prop. 13 polynomial-ring form is
  unavailable for double-odd curves. That holds only for coordinates with
  phi(-P) = phi(P), the Kummer / x class.
- **Two degree-2 classes exist.** On a double-odd curve, degree-2
  coordinates over F_q come in exactly two inequivalent classes: Kummer
  (x, involution P -> -P) and u = x/y (involution P -> N - P), since
  u(P + N) = -u(P) and u(-P) = -u(P).
- **In the u class the quotient is a ring form.** H_R = A(s) + pi B(s) in
  K[s_1, ..., s_{m-1}, pi], with s_k = e_k(u_i^2), pi = prod u_i and the
  two-term quadric s_m - pi^2.
- **Measured at toy size.** D = 2^{(m-1)^2} in every cell, and the planted
  point was recovered each time:

  | m | p | D |
  |---|---|---|
  | 3 | 4111 | 16 |
  | 3 | 262231 | 16 |
  | 4 | 4129 | 512 (re-measured with msolve by the main session) |
  | 4 | 262153 | 512 |

  m = 4 is even. The rescaled lambda construction of `KN-OPEN-9b4a2b` does
  not exist there.
- **The two classes tie, and larger groups are unavailable.** Every
  N-stable subline in either class gives D = 2^{(m-1)^2}. EcGFp5 has no
  rational 4-torsion (b and a^2 - 4b are non-squares), so larger symmetry
  groups are not available. `IDEA-20260905-d0fee4`'s conclusion holds, but
  its step (C2) fails for coordinates that factor through an isogeny.
  "Kummer line optimal" should read "Kummer and u classes tie".

## Statement (what remains open)

1. **The S_5 comparison at m = 5 on the same targets.** (Unchanged from
   `KN-OPEN-814b4c`.) This is criterion 3 of `KN-OPEN-9b4a2b`. The
   S_5-symmetrized arm was measured at m = 3 only. At m = 5 the quotient's
   D = 2^16 has been measured, but not against an S_5 arm on the same
   targets. The orbit non-freeness gap at m = 5 is therefore not reported.
   It must never be reported against the constant 2^20.
2. **The per-system cost with a sub-Wiedemann change of order.** (Unchanged
   from `KN-OPEN-814b4c`.) Under the G1 rule of
   `crypto:research/ecgfp5_lead_evaluation_20261031`, the measured
   whole-solve c sits 0.30–0.63 bits above the CLOSE threshold (2^46). F4
   alone would sit in the not_measured band.
   - Berthomieu–Neiger–Safey El Din (ISSAC 2022, arXiv 2202.09226) change
     of order via the Hermite normal form of a t×t polynomial matrix costs
     O~(t^{ω-1} D), against O~(t D^2) for Wiedemann.
   - Their Table 2 reports about 5× at D = 65,536, at t = 8,092 and 12,870.
   - At t = 4,920 that model predicts the finish dropping from about 20,700
     to about 3,000 CPU-s. That would move c to about 2^45.1–2^45.6, which
     is G1 not_measured, not CLOSE. This is a prediction, not a measurement.
3. **The degree-4 Macaulay rank (H-GFPN-6cc6aa).** (Unchanged.) It remains
   untested.
4. **The u = x/y ring form at m = 5 (new).** At m = 5 the u system has 6
   unknowns of degrees (8,8,8,8,8,2), the same supports as the current
   quotient (1287 and 792 terms), and the two-term quadric s_5 - pi^2 in
   place of the dense w^2 - Q(s). Does it solve the same cell more cheaply
   than the current quotient under the same solver? No m = 5 u cell has been
   run. The audit expects D = 65,536 and no degree fall, so any gain would
   be a constant factor. That is an expectation, not a result.

## Work in progress (no result)

- **Block-Wiedemann finish, for item 2.** An experiment is running under
  `crypto:research/ecgfp5_quotient_bw_finish_20261102/`. Its protocol was
  frozen on 2026-11-02 before any cell. It replaces W0's change of order with
  a block-Wiedemann finish on the BNS22 chain matrix, on W0's three merged
  m = 5 planted systems. **No result exists yet.** Nothing in this entry
  reports one. Whether its finish meets item 2's criterion ("an HNF/PML
  change of order or equivalent") is decided when its result is reviewed.

## Resolution criterion

- Item 1 is resolved by an S_5 arm solved at m = 5 on the quotient's own
  targets. It needs at least three primes spanning 12 or more bits, a
  recorded envelope, and its D and gap reported. A memory or time stop is
  not_measured. (Unchanged.)
- Item 2 is resolved by a complete solve whose finish is not Wiedemann
  sparse-FGLM: an HNF/PML change of order or equivalent. It runs on the same
  quotient systems, recovers the planted point, uses a frozen protocol, and
  reports whole-solve c at all three primes. (Unchanged.)
- Item 4 is resolved by one m = 5 u-ring cell at p' = 4111, compared
  against W0 on the same protocol shape:
  - the protocol is frozen before the cell;
  - the solver, threads, host class and envelope are W0's (msolve 0.6.5,
    4 threads, 12 GiB / 4 h);
  - D is reported, and the planted point is recovered;
  - F4 CPU and whole-solve CPU are reported against W0. W0's bars are an F4
    CPU of 6,900 s (W0_F4_CPU / 1.5) and a whole-solve CPU of 31,004 s.
  A memory or time stop is not_measured. One cell decides only whether the
  form is worth a three-prime run. It is not a three-prime verdict. The
  audit suggests folding subline choice within a family into the same cell
  (two mu' values).

## What must NOT be said

- **Not** "EcGFp5 is below 142 (or 128) bits", nor that it is safe. c is a
  per-system stage cost at toy primes, not an end-to-end attack cost, and
  no matched rho reference exists for it.
- **Not** "the symmetrization does not help". D fell from 2^20 (S_5,
  model) to 2^16 (measured). What remains open is the cost per system at
  that D.
- **Not** "the quotient is closed". Its lead in the atlas
  (`LEAD-ICP-gfp5-symmetrized-gaudry`) is `closed_dominated`. It stays in
  the pursuit queue with explicit revisit conditions, and items 2 and 4 are
  among them.
- **Not** "FHJRV's ring form is unavailable for double-odd curves" without
  the scope. It is unavailable only for coordinates with phi(-P) = phi(P)
  (`CORR-20261102-7e3a91`).
- **Not** "the Kummer line is the unique optimal coordinate". The Kummer
  and u classes tie at D = 2^{(m-1)^2}.
- **Not** "the u ring form is faster", and not "it lowers D at m = 5". Both
  are unmeasured. The m = 5 u cell has not been run.
- **Not** any block-Wiedemann finish number. That experiment has no
  result.
