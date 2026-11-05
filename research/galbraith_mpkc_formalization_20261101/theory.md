# Galbraith MPKC v2 formalization tranche 1

- **Source:** Steven D. Galbraith, *Mathematics of Public Key Cryptography*,
  version 2.0 (2018 PDF), Chapter 2, §2.5, Lemma 2.5.3.
- **Pinned source:** `SRC-GALBRAITH-MPKC-V2-2018`, PDF SHA-256
  `ca75ee62b96daa0d46faaa2d4dc28205683455ad3a2a48586b9b39299c25022d`.
- **Catalog object:** `book:galbraith-mpkc-v2-2018:lemma:2.5.3`, physical PDF
  page 52.
- **Status of this note:** source-aware formal target; not an independent
  semantic review.

## Source claim

The lemma takes odd `n`, `R = 2^s > n`, a negative inverse `n'` modulo `R`, a
Montgomery representative `0 <= a < n`, and `u = a n' (mod R)`. It states that
`a + u n` is divisible by `R`; for `w = (a + u n) / R`, one has `w < n` and
`w = a R^{-1} (mod n)`. The printed proof uses the two modular congruences,
the canonical bounds on `a` and `u`, and the estimate
`a + u n <= (n - 1) + (R - 1)n = Rn - 1`.

## Formal claim

For integers `n`, `R`, `n'`, `a`, and `u`, assume:

1. `0 < n < R`, `0 <= a < n`, and `0 <= u < R`;
2. there is an integer `k` with `n*n' + 1 = k*R` (that is,
   `n*n' = -1 (mod R)`);
3. there is an integer `ell` with `u = a*n' + ell*R` (that is,
   `u = a*n' (mod R)`).

Then there is an integer `w` such that

`a + u*n = R*w`, `0 <= w < n`, and `n` divides `R*w - a`.

The last clause is `R*w = a (mod n)`. Under the book's original hypotheses,
`R` is invertible modulo odd `n`, so it is equivalent to the displayed
conclusion `w = a*R^{-1} (mod n)`.

## Hypothesis and conclusion delta

- The Lean theorem works over `Int` and writes congruences as explicit integer
  witnesses. This changes representation, not mathematical content.
- It omits “`n` odd” and “`R` is a power of two” after taking the negative
  inverse congruence as a hypothesis. Those structural assumptions are used to
  obtain the inverse and efficient machine operations; they are not needed for
  the integer argument. The resulting arithmetic claim is stronger.
- Bounds on `a` and `u` are explicit. They are already part of the book's
  representative conventions and are load-bearing for `w < n`.
- Lean proves existence of `w` and the exact division equation instead of
  presupposing that the quotient denotes an integer.
- Lean states the modular conclusion in multiplication form. It does not
  formalize modular-inverse existence or the equivalence obtained by
  multiplying by that inverse.

## What this target does not prove

It does not verify Montgomery multiplication code, constant-time behavior,
word-size assumptions, or any bit-complexity claim. It does not review or
formalize any of the other 1,816 catalog rows. A clean Lean build would establish
only the formal claim above and would still require independent
statement-fidelity review.

## Sources checked

- The pinned v2 PDF, Lemma 2.5.3 and its complete printed proof.
- The author's official errata page retrieved 2026-11-01; no exact or §2.5
  erratum was detected for this lemma.
- The repository's earlier source-read receipt, which covers only §§25.4 and
  26.3--26.4 and therefore supplies no review evidence for this lemma.
