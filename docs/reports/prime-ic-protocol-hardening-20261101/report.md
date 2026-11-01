# Prime-field arity-three protocol hardening

**Decision:** `DEC-20261101-26f1fa`

**Status:** additive correction plus bounded development-fixture validation; no scientific run.

![Evidence and complete-cost gates](diagram.pdf)

The review keeps the arity correction from `DEC-20261031-b51282` and fixes its
execution contract without changing immutable history. `DEC-20261031-cd6460`
remains the separate checker-defect decision.

## Corrections

1. Cold relation collection is `2^(a s)+2^((e+1)s)` up to polynomial factors.
   At `m=3`, reusable setup needs `a<1.5` and natural queries need `e<0.5`.
2. The primary query slope uses every preregistered natural row and actual
   `log2(p)/3`. Any natural censoring is inconclusive.
3. Planted and exact-UNSAT rows are separately reported controls, never slope
   samples.
4. Sinz sequential exactly-one is selected. At `s=27`, the three windows have
   805,306,365 Boolean variables and 1,207,959,543 exactly-one clauses before
   theory auxiliaries, so one-hot `s=15..27` is not admitted.
5. `Theta((log p)^2)` describes only the selected schoolbook CNF control; it is
   not a universal multiplication lower bound.
6. Each abscissa is bound to a rational-lift sign and the signed group relation
   is replayed. Chained `S3` alone is sign-blind.
7. At inspected cvc5 source `02f77af...`, finite fields expose no proof checker.
   QF_FF is therefore a SAT/model diagnostic unless a later prospective
   amendment binds independently checked finite-field UNSAT evidence.
8. Field/index membership is a compact unsigned range predicate. Per-word
   clauses are allowed only under an explicit complete-enumeration cap.
9. Provenance is additive: checker defect `cd6460`, arity correction `b51282`,
   hardening `26f1fa`.

## Implemented and still open

Merged `cryptanalysis#1347` validates the rational-lift discriminant
`16t^2 f(x)`, the `t=0` branch, signed replay, guarded three-summand
rationality, chained `S3`, compact ranges, Sinz exactly-one and exact
full-versus-two-window model sets on a disclosed `F_7` fixture. It contains no
held-out row, production trail theory or exponent estimate.

The next technical lead is the source-bound `F_p` trail theory with exhaustive
partial-assignment and explanation/proof replay. In parallel, a compact/lazy
selector must match the complete projected signed model set at small cells and
pass setup/bytes/RSS preflights before any 40–80-bit continuation proposal.

No new hypothesis, experiment, evidence or goal status was promoted.
