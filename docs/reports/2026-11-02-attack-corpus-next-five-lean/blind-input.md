# Blind mathematical input: five cryptographic assumption boundaries

This document supplies definitions and questions only.  Do not assume that a
requested implication is true, that a proposed repair is sufficient, or that
any of these finite models establishes or refutes a computational security
theorem.  Derive each answer independently and identify every load-bearing
hypothesis.

## 1. One-shot counts versus repeated history

Let the outcome space be the two-element uniform set `{false, true}`.  A
two-trial process assigns a success predicate to each trial and outcome.

1. Construct two processes for which each individual trial succeeds on
   exactly one outcome, but whose sets of outcomes failing both trials have
   different cardinalities.
2. Determine whether identical one-trial success counts can rule out an
   outcome that fails forever when trials are indexed by the natural numbers.
3. Let `S : N -> R`, `S 0 = 1`, `0 <= epsilon <= 1`, and `S n >= 0`.  Determine
   what follows from the recurrence

       (1 - epsilon) S(n) <= S(n+1).

   In particular, derive the sharp geometric pointwise consequence and a
   finite, division-free tail-sum inequality.  Say why a marginal one-shot
   count alone does or does not supply this recurrence.

## 2. Rank of cubic evaluation

Use the ten homogeneous degree-three monomials in three variables as a basis.
For ten distinct rational coordinate triples, form the square matrix whose
rows evaluate those monomials.

1. Decide whether distinctness of the ten triples implies that this matrix is
   invertible.  Give an explicit proof or counterexample.
2. State and prove the minimal determinant-based repair for a coefficient
   vector whose cubic vanishes on all ten triples.
3. Keep projective quotienting, nonsingularity of the cubic, and any
   rank-tested family of fewer than ten rows outside the conclusion unless
   independently established.

## 3. Scalar clearing and exact pushforwards

For finite additive groups `K` and `S`, consider scalar multiplication by a
natural number `h` on `K x S`, and regard `{0} x S` as the intended target.

1. Give a small finite example in which a proposed clearing scalar collapses
   more than the unwanted factor.
2. Give a small finite example in which it kills `K`, permutes `S`, has image
   exactly `{0} x S`, and has a constant number of preimages above every target
   point.
3. Derive the corresponding generic image and exact fibre-cardinality theorem
   from explicit hypotheses.  Explain why equal fibres for uniform ambient
   input are not a theorem about an unspecified hash encoder.

## 4. Constant challenges in a Schnorr-style equation

Let `F` be a field, `A` an additive `F`-module, and define acceptance by

    s * G = R + H(m,R) * X.

1. Analyze the cases where `H` is the constant zero function and, more
   generally, a known constant chosen before `R`.
2. Give a concrete finite example in which one fixed zero-challenge transcript
   accepts two distinct public keys.
3. For a fixed transcript and a nonzero challenge, determine whether two
   accepting public group elements must coincide.  Separate this fixed
   equation from random-oracle, replay, forking, and extraction claims.

## 5. The relation kernel of a two-generator commitment

Let `F` be a field, `V` an additive `F`-module, and

    Com(m,r) = m * G + r * H.

Assume `H = alpha * G`, `alpha != 0`, and that `a |-> a * G` is injective.

1. Characterize the full kernel of `(m,r) |-> Com(m,r)` and exhibit a nonzero
   relation.
2. Given an opening `(m,r)` and a requested message `m'`, derive an alternate
   blinder and check the sign.
3. From two colliding openings with different messages, prove what can be
   recovered and which denominator is nonzero.
4. Give a concrete finite-field collision.  Explain why the algebraic
   existence of `alpha` is not the same statement as an outsider's ability to
   compute it.

## Required controls

For every item, test at least one weakened or removed premise and record how
the conclusion changes.  Reject any conclusion that silently upgrades a
finite algebraic countermodel into a ROM/QROM attack, a hash-to-curve theorem,
a computational binding theorem, an ECDLP algorithm, or a claim about a paper
whose actual hypotheses were not modeled.
