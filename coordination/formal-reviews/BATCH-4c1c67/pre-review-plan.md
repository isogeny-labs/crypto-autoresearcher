# Nagao 2015/984 Lemma 4 formal statement review plan (prepared, not dispatched)

Review base: `main` at `3102f9c04ab686e301dd5c61a2fc0441fa946203`. Lean
`leanprover/lean4:v4.35.0`, Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`
(the pins on `main` at packet time; the five modules were last verified on the
hosted gate under these pins in run 41280794617). This plan records the prior
before independent review. No verdict is assigned.

## Claims under review

Let `F = {f_1, f_2}` over `F_2`, `S_fe = {X_i^2 + X_i}`. Equality reading of
condition (1) of Definitions 5 and 6 of Nagao 2015/984: a fall at degree `D` is a
cofactor tuple with every product of degree `<= D`, one of degree exactly `D`, and
a nonzero sum of degree `< D`; the fake version takes products and sum modulo
`S_fe`.

- **C1 (inside form).** For witness A (`X^2 Y`, `X Y + X` in `F_2[X,Y]`) and
  witness B (`X_1X_2 + X_3`, `X_1X_3 + X_2` in `F_2[X_1,X_2,X_3]`),
  `d_F(F u S_fe) = 3` and `d'_F(F u S_fe) = 2`.
- **C2 (printed form).** For both witnesses, `d_F(F) = 3` and `d'_F = 2`, with the
  fake side computed from `F` or from `F u S_fe`.
- **C3 (recovery).** If `S = F u S_fe` and a fake fall at degree `v` for the
  generators in `F` has every unreduced product of degree `<= v`, then `S` has a
  true fall at degree `v`.
- **C4 (unrestricted cofactors).** C1 and C2 hold in `F_2[X_1..X_n]` with
  arbitrary polynomial cofactors, and the list-model witness data maps to the
  stated polynomials.

Source: `knowledge/findings/KN-FIND-936151.md` (C1, C2, C3 as the recovery rule of
section 4); `papers/first-fall-lean/paper.tex` Theorem 5 and Proposition 6.

## Prior (recorded before any reviewer)

The producer expects all five declarations to state C1 to C4 faithfully at the
scope above. Kernel evidence exists for each (table in `README.md`); a fresh
pinned rebuild by a reviewer has not been done. The producer has not compared
the Lean definitions with the text of Nagao 2015/984 directly; the comparison
in KN-FIND-936151 and its source reads is the producer's only route to the
primary text. The producer's own uncertainty is concentrated in the deltas
D1, D3, D5 and D6 below.

## Hypothesis deltas (producer's list; reviewers must extend, not trust, it)

Each delta is a Lean hypothesis or definitional choice the human claim does not
state, marked `implied`, `scoping` or `unjustified` by the producer. Reviewers
re-mark each one.

- **D1 equality reading (all; scoping).** Lean fixes condition (1) as
  "all products `<= D`, one exactly `D`". The PDF prints `>=`. Under `>=` the
  lemma holds trivially (KN-FIND-936151 section 3). Check that the elaborated
  `IsFall` / `Cond` / `FallAt` really encode equality and not `>=`.
- **D2 list model (T1, T2; scoping).** Polynomials are duplicate-free lists of
  exponent vectors over `F_2`; `norm` keeps odd-count monomials. Check that `mul`,
  `reduceFe`, `norm` and `prep` implement `F_2[X]` arithmetic and reduction mod
  `S_fe` on these inputs.
- **D3 cofactor domain (T1, T2; scoping, discharged by T4/T5).** The list model
  restricts cofactors to monomials of degree `<= D` (multilinear on the fake side).
  T4 and T5 remove this for the true side. Check that the no-fall theorems in T4
  and T5 quantify over all cofactors.
- **D4 dropped fake generators (T1, T2, T4, T5; implied?).** The list model drops
  fake-side generators that reduce to zero. T4/T5 instead give field equations the
  zero cofactor on the fake side. Check this matches Definition 6.
- **D5 fake sum (T3, T4, T5; implied via red_sum_red).** `IsFakeFall` takes
  `red (sum of unreduced products)`; the list model takes the reduction of the sum
  of reduced products. `Bridge.red_sum_red` proves these equal. Check the
  statement of `red_sum_red` covers the case used.
- **D6 fake cofactors in MvPolynomial (T3, T4, T5; scoping).** `IsFakeFall`
  allows arbitrary cofactors, not only multilinear ones. The exhibited fake
  cofactors (`(1,1)` for A, `(1, X_1+1)` for B) are multilinear, so the
  counterexample should survive the restriction. Check whether Definition 6
  restricts cofactors and whether any theorem relies on the permissive form.
- **D7 minimum on the fake side (T4, T5; implied).** `Lemma4Mv` states
  `d_F <= D` for every `D` with a fake fall instead of `d_F <= d'_F`. These are
  equivalent when `d'_F` exists, since `d'_F` is the least such `D`. Check the
  equivalence, including `D = 0`.
- **D8 first fall degree range (all; implied).** `FirstFall` / `FirstFallIs`
  quantify over `1 <= D' < d`. Check against "minimal d" in Definition 5.
- **D9 field equations (T3; scoping).** `fe j = X_j^2 - X_j` over any commutative
  ring; Nagao's field equations over `F_p` are `X_i^p - X_i`. C3 is only claimed
  for `p = 2`. Check the theorem is not cited beyond `p = 2`.
- **D10 U-3 and U-4 (T3; implied).** U-3 is built into `withFe` (field equations
  among the true generators); U-4 is the hypothesis `hU4`. Check no other
  hypothesis is hidden in `IsFakeFall` or `withFe`.

## Independent joints and attacks

1. **J1 primary-source correspondence.** Read Definitions 5 and 6 and Lemma 4 of
   ePrint 2015/984 (and Definition 1 of 2013/549) directly. For each of D1, D4,
   D6, D8, state what the source says and whether the Lean choice matches,
   narrows, or departs from it. Breaking artifact: a quoted source clause that
   no reading of the Lean definitions satisfies.
2. **J2 blind re-derivation.** From `blind-input.yaml` only, compute the true and
   fake first fall degrees of both witnesses in both placements, with arbitrary
   cofactors, and prove or refute the recovery statement. Freeze the derivation
   before seeing any Lean source, the finding, the paper or a sibling report.
   Breaking artifact: a different first fall degree, or a counterexample to
   recovery under its stated hypotheses.
3. **J3 Lean statement and machine gate.** In an isolated checkout at the review
   base, build the five modules on the pinned toolchain, print the elaborated
   types of the named theorems and of `IsFall`, `IsFakeFall`, `withFe`, `red`,
   `FirstFall`, `Lemma4Inside`, `Lemma4Outside(Fe)`, `Lemma4Mv`, `Lemma4Mv'`,
   and `#print axioms` for each named theorem. Compare each clause with C1 to C4
   and D1 to D10. Attack: wrong theorem name, omitted module, an axiom beyond
   `propext`, `Classical.choice`, `Quot.sound`, a definition that makes a
   statement vacuous. Breaking artifact: a clause of C1 to C4 not implied by the
   elaborated statement, or a vacuity.
4. **J4 claim scope (Coordinator).** Compare J1 to J3 with KN-FIND-936151 and
   the paper's Theorem 5 and Proposition 6, and decide what may be cited. The
   derived claim that a published bound rests on Lemma 4 stays un-promoted
   (`IMP-SEMBIN-FCB7A2-LEMMA4-TIER`) unless separately reviewed.

## Proves-too-much controls

- **Recovery without U-4.** Witness A inside: `g = (1, 1)` is a fake fall at
  degree 2, and `deg(1 * X^2 Y) = 3 > 2`. If C3 were claimed without U-4 it would
  give a true fall at degree 2, contradicting `Bridge.in_no_fall_two`. A review
  that accepts a U-4-free reading of `recovery` proves too much.
- **The `>=` reading.** Under `>=`, Lemma 4 holds for every nonzero system
  (KN-FIND-936151 section 3). A review that finds the counterexample also holds
  under `>=` has misread D1.
- **Vacuous first fall.** "First fall degree 3" must require an actual fall at
  degree 3, not only the absence of falls below 3. Reviewers check that
  `FirstFall` and `FirstFallIs` contain the positive clause, and that the fall
  certificates (`gA_true`, `gA_out`, `Gout`, `Gin`, `GoutB`, `GinB`) are real falls:
  products of degree at most 3, one of degree exactly 3, nonzero sum of degree
  below 3.

## Dispatch and completion gates

Before dispatch, the Coordinator archives this plan with its hash under a review
task, assigns J1 to J3 to three distinct sessions that did not produce the
modules, and requires read attestations. Completion needs fresh machine output,
three independent reports, a passing `tools/check_review_independence.py`, the
controls above, and a Coordinator decision. None of those gates is claimed here.
