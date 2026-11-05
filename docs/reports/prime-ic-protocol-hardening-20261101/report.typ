#set page(width: 210mm, height: 297mm, margin: 16mm)
#set text(font: "DejaVu Sans", size: 9.5pt)
= Prime-field arity-three protocol hardening

#text(size: 8.5pt)[Decision `DEC-20261101-26f1fa` · 2026-11-01 · no scientific run]

#image("diagram.svg", width: 100%)

== Corrected contract

- Cold collection is $2^(a s)+2^((e+1)s)$ up to polynomial factors. At $m=3$, both $a<1.5$ and $e<0.5$ are necessary.
- Fit $e$ only on every preregistered natural row at actual $log_2(p)/3$. Any natural censoring is inconclusive; planted and exact-UNSAT rows are separate controls.
- Bind each selected abscissa to a rational-lift sign and replay the signed group relation. Chained $S_3$ alone is sign-blind.
- Freeze Sinz sequential exactly-one and a compact unsigned range predicate. Per-forbidden-word clauses require an explicit complete-enumeration cap.
- Scope $Theta((log p)^2)$ to the selected schoolbook CNF control. At inspected cvc5 source, QF_FF is a SAT/model diagnostic because finite fields expose no proof checker.
- One-hot $s=27$ has 805,306,365 Boolean variables and 1,207,959,543 exactly-one clauses before theory auxiliaries. The $s=15..27$ continuation is not admitted.

== Evidence boundary and next lead

Merged `cryptanalysis#1347` supplies a passing disclosed $F_7$ development oracle for the lift identity, complete $t=0$ branch, signed replay, guarded rationality, chained $S_3$, compact range semantics, Sinz exactly-one and exact enumeration agreement. It supplies no production $F_p$ trail theory, checked UNSAT route, held-out row or exponent.

Next, drive actual Boolean trail assignments through a source-bound $F_p$ theory and exhaustively check every response and explanation/proof step. Separately establish complete small-cell signed-model-set equivalence for a compact/lazy selector before proposing any continuation.

Decision provenance is additive: `DEC-20261031-cd6460` remains the checker defect; `DEC-20261031-b51282` is the arity correction; this hardening is `DEC-20261101-26f1fa`.
