# J1 blind mathematical review: decomposition certificate

## Decision procedure and exact predicate

Write `O` for the group identity and `Aff(Q)` for the assertion that `Q` is an affine (rather than infinity) point. For an affine point write `x(Q)` and `y(Q)`. Define

`InV(x) := exists c : Fin b -> F, x = sum (i : Fin b), algebraMap F K (c i) * basis i`.

This is exactly membership in the `F`-span of the basis range, even when the family is empty, dependent, or contains zero. A finite decision procedure enumerates all `|F|^b` coefficient vectors once, computes their sums in `K`, and stores or compares them. For each tuple entry, decide `Aff(P i)`, decide its curve equation (and nonsingularity where a raw pair must be converted to a point), and decide `InV(x(P i))`. Finally compute the finite group sum and compare it with `R`. Return true precisely when all checks pass. Equality in `K`, finiteness of `F` and `Fin b`, and the point/group operations make these checks finite. No independence or spanning hypothesis on `basis` is needed.

The exact iff, for an already typed tuple of nonsingular curve points, is

`decide(P,R,basis) = true  <->  (forall i : Fin m, Aff(P i) and curveEquation(x(P i), y(P i)) and InV(x(P i))) and (sum (i : Fin m), P i) = R`.

The equation conjunct may be redundant for a point type that already certifies it, but keeping it states the certificate contract explicitly. For raw pairs `(x_i,y_i)`, check the equation and any nonsingularity condition required by the point constructor before forming `P i`; an invalid raw pair returns false. If those checks pass, the raw predicate is the same conjunction with `InV(x_i)` and the sum of the constructed points equal to `R`. Merely satisfying the equation does not justify conversion on a possibly singular Weierstrass model. An identity summand is rejected by `Aff` even though it is a group point. For `m=0`, every per-entry condition is vacuous and the sum is `O`, so the answer is true exactly when `R=O`, independently of `basis`.

Soundness follows because every accepted entry passed the affine, curve, and span tests and the computed sum equals `R`. Completeness follows because a witness coefficient vector for each `x(P i) in V` appears in the exhaustive finite enumeration; all other true conjuncts pass their decidable checks. The enumeration witnesses are independent across tuple entries.

## F5 controls

For `F=K=F_5`, `y^2=x^3+x+1` is nonsingular: `4*1^3+27*1^2 = 31 = 1 (mod 5)`, so its short-Weierstrass discriminant is nonzero. Denote `A=(0,1)` and `B=(2,1)`. Both satisfy the equation: at `x=0`, right side is `1`; at `x=2`, it is `8+2+1=11=1 (mod 5)`. `(0,0)` fails since its left side is `0` and right side `1`. Both `A` and `B` are nonidentity affine points and are distinct.

| Basis family | Tuple / raw input | Target | Decision and reason |
| --- | --- | --- | --- |
| empty (`V={0}`) | empty | `O` | true: vacuous entry checks, empty sum `O` |
| empty | empty | `A` | false: sum `O != A` |
| empty | `[A]` | `A` | true: affine, on curve, `x=0 in V`, correct sum |
| empty | `[A]` | `O` or `B` | false: wrong sum |
| empty | `[B]` | `B` | false: `x=2 notin V`, despite correct sum |
| singleton `[1]` (`V=F_5`) | `[B]` | `B` | true: coefficient `2` witnesses `x=2` |
| singleton `[1]` | `[B]` | `A` or `O` | false: wrong sum, while all entry checks pass |
| empty or singleton `[1]` | raw `[(0,0)]` | `O`, `A`, or `B` | false: curve equation fails before conversion |
| empty or singleton `[1]` | raw `[(0,1)]` | `A` | true: valid affine point, `x=0`, correct sum |
| singleton `[0]` (`V={0}`) | `[B]` | `B` | false: one-element family alone does not imply full span |
| any | `[O]` as point input | `O` | false: summand is not affine |

The empty-basis `B` row isolates the span test; the `[1]` wrong-target row isolates the sum test; `(0,0)` isolates the raw curve test; `[O]` isolates the affine requirement. The zero-length rows establish the exact empty-sum boundary. These field examples use only finite-field arithmetic and group identity/distinctness; the general procedure additionally uses the finite enumeration of `F` and decidable equality in `K`.

## Scope and verdict

**Holds** for the mathematical predicate stated on the blind card. This is a source-blind derivation and control analysis, not an inspection of any implementation or proof artifact. It establishes no claim about a producer's code, Lean theorem, runtime, or certificate serialization. I read only the specified blind card; its SHA-256 matched the supplied digest.
