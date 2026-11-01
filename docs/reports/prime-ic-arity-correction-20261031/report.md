# Prime-field index calculus: arity and solver correction

DEC-20261031-b51282

The programme now treats every accepted arity-two theorem cell as component evidence, not as
an exponent-changing ECDLP result. If `s=log2(p)/m`, a PDP call costs `2^(e s)`, and relation
collection needs `Theta(2^s)` calls, the collection exponent is `(e+1)/m` in `p`. Strictly
beating rho therefore requires

```text
e < m/2 - 1.
```

At `m=2` this requires `e<0` and is impossible for nonnegative work. Exact enumeration is
already optimal up to polynomial factors in the stated reference model. At `m=3`, the first
relevant PDP screen, the necessary threshold is `e<0.5`. This is not sufficient for a complete
index-calculus win: the existing complete PKM cost bridge still places its linear-algebra
crossover at `m>=4`.

## Correction boundaries

| Requirement | Decision | Evidence status |
| --- | --- | --- |
| Fix the earlier outer-arity software defect first | Preserve DEC-20261031-cd6460; DEC-20261031-ca1521 already rejects R1 in its fixed F5/F7 authenticated suite | Verified software scope; not a complexity result |
| Remove arity two from exponent-bearing experiment selection | Use the strict gate `e<m/2-1`; move the PDP slope screen to fixed `m=3` | Arithmetic cost identity; no new run |
| Name the actual prime-field solver | CaDiCaL CDCL(T) with an external `F_p` theory; cvc5 `QF_FF` independently | Specified, not implemented or benchmarked |
| Account for pure CNF honestly | Treat it as an encoding-cost control; general `F_p` multiplication costs `Theta(log^2 p)` Boolean gates | Cost boundary, not a solver result |
| Preserve useful algebra | Keep the lambda lift, discriminant, guarded three-summand rationality, higher-arity rationality circuits and forbidden-word clauses | Retained at their stated scopes |

The historical decisions are immutable and retain their original meaning. DEC-20261031-cd6460
records a metadata/checker defect: changing the purported outer arity could be accepted.
DEC-20261031-ca1521 records the independent fixed-interface rejection of that mutation. This
new decision does not reopen either suite. It corrects the later experiment-selection
inference: fixing a software arity check does not turn an `m=2` component theorem into an
ECDLP exponent result.

## Retained predicate and solver model

The corrected `m=3` predicate uses three disjoint one-hot windows and two chained `S3`
relations. It does not expand `S4`. The nonexceptional rational lift is

```text
(2 t lambda - s0)^2 = f(x),
```

with discriminant `16 t^2 f(x)`; `t=0` remains an explicit exceptional branch. Under a
rational non-2-torsion target, odd prime whole-group order and disjoint windows, the
three-summand Frobenius argument gives rationality without another circuit. At arity four or
higher that shortcut is not automatic, so explicit rationality circuits remain mandatory.
Every field or index word outside its declared domain receives a forbidden-word clause.

Boolean equations `z^2-z` avoid carry semantics in the quotient model, but they do not remove
the gate cost of prime-field multiplication after bit blasting. The primary candidate is
therefore CaDiCaL with a source-bound external `F_p` theory and independently replayed Boolean
explanations. The independent candidate is a pinned cvc5 `QF_FF` export of the same canonical
predicate. Pure CNF reports gates, variables, clauses and bytes only.

The existing Q1421 CaDiCaL loop is bound to source SHA-256
`0a0d2c673e9484f4b217917ee306e7663140e4d4618d8bb0ed8dc91947d08bc6`.
It demonstrates external-propagator lifecycle and counted theory calls over `F_{2^n}`. It is
not an `F_p` theory implementation and is not reported as one.

## Fixed next measurement

The owned execution design merged as
[cryptanalysis PR #1343](https://github.com/isogeny-labs/cryptanalysis/pull/1343), source head
`aa98e66beeaa2d8ef953e4fe01d73f41a267402e`. It fixes `m=3`, an initial ladder containing
every integer `s=6..14`, and a strict Holm-corrected upper-interval gate `e<0.5`. Controls are
the exact two-window enumeration reference (`e=2`), a curve-free support-matched null,
planted and exact-UNSAT classes, a fresh-process A/A arm and pure-CNF size accounting. Complete
work starts at target-dependent IR construction and ends after explanation replay and
independent group-law verification.

The 40--80-bit path is the same fixed arity with `s=13..27`, corresponding to roughly 39--81
field bits. The initial ladder reaches `s=13,14`; `s=15..27` is a separately frozen continuation
and cannot be appended after observing favorable data. At 80 bits, rho is about `2^40` group
operations, so this programme measures the PDP exponent rather than predicting a wall-clock win.

No `F_p` propagator, held-out instance, cvc5 benchmark, field census or exponent fit exists in
this correction. Scientific runs: zero. Performance claims: zero. The next action is
implementation plus exhaustive tiny-cell replay, not execution of the ladder.

Primary-source context: Petit, Kosters and Messeng, *Algebraic approaches for the elliptic
curve discrete logarithm problem over prime fields*, PKC 2016,
DOI `10.1007/978-3-662-49387-8_1` (KN-LIT-10b0fa). Exact internal and cross-repository identities
are recorded in `report-inputs.json`.
