# J1 blind review: raw-coordinate algebra and finite controls

**Task:** TASK-20261109-e30670  
**Joint:** J1 blind raw-coordinate algebra and finite controls  
**Verdict:** holds, at the typed-pair mathematical scope stated in the blind card.

## Blind input and method

The only source read was `/var/tmp/semaev-raw-coordinate-fidelity-20261109/docs/reports/2026-11-09-semaev-raw-coordinate-fidelity/blind-card.md`, whose SHA-256 I verified as `82114d64bf957cf255cc6c451cd961026f58814be4ec813719899f0902398d90`. I did not inspect producer code, a theorem or proof, target, review plan, Git history, earlier reports, or sibling output. I independently derived the equivalence and used a standalone Python 3 arithmetic enumerator over F5. No Lean run or repository edit was performed. The `python` command was unavailable; rerunning the same standalone check with `python3` succeeded.

## Derivation

Write `A_i := Equation(x_i,y_i)`, `B_i := Span(x_i)`, and `S := (sum_i pointOfRaw(x_i,y_i) = R)`. By the card's definition,

`ValidRaw(xy;R) := (forall i, A_i and B_i) and S`.

The proposed right-hand statement is exactly `(forall i, A_i and B_i) and S`. The two implications follow by conjunction elimination and introduction; no group cancellation or assumption that `pointOfRaw` is injective is needed. When all `A_i` hold, each `pointOfRaw(x_i,y_i)` is the typed curve point with those coordinates, so `S` is also equality of the sum of those constructed points with `R`. That last replacement is conditional on the equation witnesses. The definition maps a failed equation to the identity, so `S` alone cannot imply any `A_i`.

This is a mathematical statement about typed `K × K` pairs, the declared `F`-span, and a typed target `R : W.Point`. The finite-field and nonsingularity hypotheses provide the intended group setting; the equivalence itself is direct from the stated definition.

## Explicit F5 controls

For `y² = x³ + x + 1` over F5, `-16(4a³+27b²) = -496 = 4 (mod 5)`, so the curve is nonsingular. Its affine points are `(0,1)`, `(0,4)`, `(2,1)`, `(2,4)`, `(3,1)`, `(3,4)`, `(4,2)`, and `(4,3)`, plus identity `O`. Let `P=(0,1)`, `-P=(0,4)`, and `Q=(2,1)`. Direct group arithmetic gives `P+(-P)=O`, `2P=(4,2)`, and `P+Q=(3,4)`. The enumerator reproduced these values.

| Declared span and tuple | Target | Equation/span/sum check | `ValidRaw` |
| --- | --- | --- | --- |
| `b=1`, basis `(1)`; `(Q)` | `Q` | Equation holds; `2·1=2` witnesses span; sum is `Q`. | true |
| `b=0`; `(P)` | `P` | Empty basis spans only `0`; `x(P)=0`; sum is `P`. | true |
| `b=0`; `(P,-P)` | `O` | Both x-coordinates are `0`; sum is `O`. | true |
| `b=0`; `(P)` | `O` | Equation and span hold, but sum is `P`, not `O`. | false |
| `b=0`; `((0,0))` | `O` | `0² != 0³+0+1`; span holds; `pointOfRaw(0,0)=O`, so the sum equality nevertheless holds. | false |
| `b=1`, basis `(1)`; `((1,0))` | `O` | Span holds, but RHS at `x=1` is `3` and `0² != 3`; reification gives `O`. | false |
| `b=0`; `(P,(0,0))` | `P` | Sum equality holds because invalid `(0,0)` maps to `O`; its equation fails. | false |
| any `b`; empty tuple `m=0` | `O` | Universal coordinate condition is vacuous; empty group sum is `O`. | true |
| any `b`; empty tuple `m=0` | `P` | Universal coordinate condition is vacuous; empty group sum is `O != P`. | false |

With `b=0`, the coefficient family has one empty choice and its sum is zero, so `Span(x)` iff `x=0`. This includes the `b=0,m=0` case. An off-curve pair mapping to identity supplies a counterexample to the weakened statement that sum equality implies validity; it does not break the stated iff, because the equation conjunct rejects that pair. I found no counterexample to the stated iff.

## Scope boundary

The equivalence does not authenticate an untrusted serialized record. A parser, encoding, field and curve identifiers, declared basis, target, and relation of bytes to the typed values need their own checks. This blind card supplies no evidence about a producer's actual field or curve, its implementation of `pointOfRaw`, or execution of a theorem prover. The existential span condition and group sum also specify no algorithm, operation count, memory usage, or runtime cost.
