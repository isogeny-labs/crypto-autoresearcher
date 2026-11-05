# J1 blind mathematical review

Task: `TASK-20261103-a1d701` (conductor task `T-1530`)

Joint owned: **J1 blind mathematical rederivation and countermodels**

Verdict: **holds**.

Both requested conclusions follow from the stated assumptions on a commutative
monoid. The proof uses no cancellation, ambient group structure, finite size,
minimal order of `P`, or assumption that `r` annihilates every element.

## Statement reviewed

Let `A` have an associative, commutative operation `+` with two-sided identity
`0`. Define natural scalar multiplication by `0·a = 0` and
`(n+1)·a = (n·a)+a`. Suppose that `r = k+k+1` for a natural number `k`,
`r·P = 0`, `T+T = 0`, and `T != 0`. The requested conclusions are
`r·(P+T) = T` and `r·(P+T) != 0`.

## Independent derivation

The recursive definition and the monoid laws give the following identities
for all natural `m,n` and elements `a,b`:

1. `(m+n)·a = (m·a)+(n·a)`.
2. `n·(a+b) = (n·a)+(n·b)`.
3. `n·0 = 0`.

For identity 1, induct on `n`: the zero case is the right identity law; the
successor case follows by the recursive definition and associativity. For
identity 2, induct on `n`: the zero case is `0 = 0+0`; in the successor case,
reassociate and commute the four summands to move the final `a` next to
`n·a` and the final `b` next to `n·b`. Identity 3 follows directly by induction
and the identity law.

Applying identities 1 and 2 at the same scalar `k` gives

```text
(k+k)·T = (k·T)+(k·T) = k·(T+T) = k·0 = 0.
```

Consequently, the supplied oddness witness gives

```text
r·T = (k+k+1)·T = ((k+k)·T)+T = 0+T = T.
```

Distributing the scalar across `P+T` now proves

```text
r·(P+T) = (r·P)+(r·T) = 0+T = T.
```

If the left side were zero, this equality would give `T = 0`, contradicting
the final hypothesis. Thus `r·(P+T) != 0` as well.

## Explicit nonvacuous model and isolated controls

Use the commutative group `A = Z/6Z`, regarded only as a commutative monoid,
with addition and natural scalar multiplication modulo 6. All entries in
the following table are residues modulo 6.

| Case | `r` | `P` | `T` | `r·P` | `T+T` | `r·(P+T)` | Equality to `T` | Nonzero output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Positive odd case | 3 | 2 | 3 | 0 | 0 | 3 | true | true |
| Even control | 6 | 2 | 3 | 0 | 0 | 0 | false | false |
| Zero-`T` control | 3 | 2 | 0 | 0 | 0 | 0 | true | false |

For the positive case the witness is `k=1`; both `P=2` and `T=3` are
nonzero, distinct, and their sum is `5`. Directly,
`3·2 = 6 = 0`, `3+3 = 6 = 0`, and `3·5 = 15 = 3` modulo 6.
In this example `P` has exact order 3 and `T` has exact order 2.

The even control changes only `r` from 3 to 6. It retains `r·P=0`,
`T+T=0`, and `T != 0`, but `6·5 = 30 = 0` modulo 6. Hence removing
oddness can invalidate each conclusion, even with positive `r`, nonzero
and distinct `P,T`, and nonzero `P+T`.

The zero-`T` control changes only `T` from 3 to 0 in the positive case.
It retains oddness, `r·P=0`, and `T+T=0`. The equality to `T` still holds,
while the output is zero. Therefore `T != 0` is needed for the requested
nonzero conclusion; it is not needed for the equality conclusion.

## Assumption challenges and boundary cases

- `r·P=0` concerns the particular element `P`. Replacing it with a claim
  about an ambient modulus or group size would need a separate argument;
  this proof does not make that replacement.
- The displayed oddness witness is sufficient. No primality assumption on
  `r` is used. For `k=0`, `r=1` forces `P=0`, and the conclusion still
  follows from `1·(0+T)=T`.
- The hypothesis `T+T=0` permits `T=0`; the explicit inequality rules this
  out for the second conclusion. Together these hypotheses make `T` a
  nonzero element of exact additive order 2, although the proof does not
  require order terminology or an ambient group.
- Commutativity is used to distribute the natural scalar over `P+T` and
  to regroup the paired copies of `T`. The derivation therefore applies
  to the stated commutative monoid without adding cancellation or additive
  inverses as hidden hypotheses.
- The positive model contains nonzero `P`; the result is not supported only
  by the special case `P=0`.

## Blind compliance and freeze

This report was derived solely from the blind statement. Before this report
and its attestation were frozen, I did not read the producer source note,
producer proof or Lean code, machine receipts, plan attack details, or any
sibling review output. No build, trial, experiment, or producer-code check
was run. The controls above are explicit hand computations.

Exact source read:

`/var/tmp/autoresearcher-odd-torsion-review-20261103/docs/reports/2026-11-03-odd-torsion-review/blind-statement.md`

Source SHA256:
`5554057db02416a2cad679903b79e1a131b6d11ba72e4a035d927c82db65936a`.

The parent supplied frozen plan commit `b806841cef` as task context; no plan
contents were read. The report SHA256 is recorded in the companion
`review_attestation.yaml`, and both final file digests are sent to the
coordinator as the freeze record.
