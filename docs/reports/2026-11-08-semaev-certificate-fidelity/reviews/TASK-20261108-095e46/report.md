# Blind derivation of the decomposition certificate predicate

Review task: TASK-20261108-095e46 / Conductor T-1935. Joint owned: J1.

Verdict: **holds**, for the mathematical decision rule below under the card's
assumptions and the explicit typing conditions stated here. This verdict is an
independent specification derivation. No producer implementation or Lean
statement was read or assessed.

## Source boundary

The only pre-existing mathematical input read was
`/var/tmp/semaev-blind-input-20261108/blind-card.md`, whose SHA256 was verified as
`16aea5ff762f1c4436da2321a3cd9f8942a166c3e858d50aad6535370744e800`.
No repository, producer source, Lean proof, plan, prior report, receipt, Git
history, sibling report, or prior mathematical conversation was consulted.
CLI help and this task's Conductor claim were read for administration only.
The scratch program and result in this directory were created by this reviewer.
There was no departure from the mathematical source boundary.

## Exact finite span test

Let `iota : F -> K` be the algebra map. Write

```
comb(c) = sum(j : Fin b, iota(c(j)) * basis(j))
spanTest(x) = exists c : Fin b -> F, comb(c) = x.
```

The set of such coefficient tuples is finite. Enumerate it, compute `comb(c)`,
and compare with `x` using equality in `K`. This gives

```
spanTest(x) = true  iff  x belongs to V.
```

Every enumerated combination lies in the span. Conversely, the image of the
linear map `c -> comb(c)` is a submodule containing every generator and hence
contains the span; equivalently, any finite linear combination can be collected
by generator index. This also covers repetitions, zero generators, and linear
dependence. No independence or injectivity of the listed family is needed.
The notation `basis` does not supply such an assumption.

The algebra/module operations implicit in an `F`-span must of course exist.
The argument uses finite enumeration of `F`, not an additional field hypothesis
on `F`. For an executable implementation, a finite enumeration (for example a
`Fintype` structure) must be available; a purely propositional assertion of
finiteness may first need a choice of enumeration. `K` itself need not be finite.

When `b = 0`, there is exactly one coefficient tuple and its combination is
zero, so `V = {0}`. An empty generator list is not an empty set of admissible
x-coordinates. When `b = 1`, the test is `exists c : F, iota(c)*basis(0) = x`.

## Exact predicate for typed curve points

Let `Aff(p)` mean that `p` is an affine point, so it has coordinates `(x,y)`
and is distinct from the group identity `O`. Define the per-point check by
matching on the point:

```
pointTest(O) = false
pointTest(affine(x,y)) = spanTest(x)
decide(P,R) = (forall i : Fin m, pointTest(P(i)))
              and (sum(i : Fin m, P(i)) = R).
```

Then the exact statement is

```
decide(P,R) = true
  iff
    (forall i, exists x y,
       P(i) = affine(x,y)
       and curveEquation(x,y)
       and x belongs to V)
    and sum(i : Fin m, P(i)) = R.
```

Here `P(i) = affine(x,y)` denotes the actual affine representation of the
nonsingular curve point; its constructor already supplies the curve equation
and nonsingularity. The extra written curve equation exposes the intended
certificate claim even though it is redundant for typed points. It does not
justify accepting arbitrary unchecked coordinates.

For the forward direction, each successful point match supplies the affine
coordinates, their constructor evidence supplies the curve equation, and
`spanTest` supplies span membership. The final comparison supplies the sum
equality. For the reverse direction, the affine witnesses force the affine
branch, the finite span equivalence makes every point test true, and the given
sum equality passes the final comparison. Thus no extra hypothesis such as
`m > 0` or `b > 0` belongs in this iff.

The sum is a finite group sum. For `m = 0` all point checks are vacuous and the
sum is `O`; acceptance is exactly `R = O`. For `m = 1` it is exactly affinity,
span membership, and `P(0) = R`. In particular `[O]` fails even when `R = O`.

## Raw coordinates and conversion

For a general Weierstrass equation set

```
H(x,y) = y^2 + a1*x*y + a3*y
         - x^3 - a2*x^2 - a4*x - a6
Hx(x,y) = a1*y - 3*x^2 - 2*a2*x - a4
Hy(x,y) = 2*y + a1*x + a3.
```

A raw pair can be lifted to the affine nonsingular point type precisely when
`H(x,y) = 0` and `Hx(x,y) != 0 or Hy(x,y) != 0`. Check these equalities before
constructing a point. If `W` is known to be nonsingular as a curve, the second
check follows from that global hypothesis. Without that hypothesis it must
be retained or proved separately; a Weierstrass equation alone need not be
smooth. The derivative formulas apply in arbitrary characteristic, with
integers interpreted in `K`.

For raw tuples `Q(i) = (x_i,y_i)`, reject a failed conversion. Otherwise form
the resulting points `P(i)` and apply the typed decision rule. Its exact iff,
without a partially defined sum, is

```
rawDecide(Q,R) = true
  iff
    exists P : Fin m -> W.Point,
      (forall i, P(i) has affine coordinates (x_i,y_i))
      and (forall i, x_i belongs to V)
      and sum(i : Fin m, P(i)) = R.
```

Equivalently, all raw pairs pass the equation and nonsingularity checks, all
x-coordinates pass the finite span test, and the sum of their unique lifts is
`R`. No arbitrary group point is substituted for a failed conversion.

These decision procedures use the point representation and group operations
of `W.Point`, the field/algebra operations, finite index enumeration, a finite
enumeration of `F`, and decidable equality in `K`. They decide certificate
validity; they do not require searching over the possibly infinite field `K`.

## Independent controls over F_5

For `y^2 = x^3+x+1`, the discriminant is
`-16*(4+27) = 4 mod 5`, so the curve is nonsingular. Its affine points are

```
(0,1), (0,4), (2,1), (2,4), (3,1), (3,4), (4,2), (4,3).
```

There are nine group points after adjoining `O`. Let `A=(0,1)` and `B=(2,1)`.
The empty family and the one-element family `[0]` both span `{0}`. The family
`[1]` spans all of `F_5`. Any one-element family `[u]` with `u != 0` does so
because multiplication by `u` is a bijection of `F_5`.

The pair `(0,0)` is off the curve because `0 != 1`; it must be rejected before
conversion. The two points `A` and `B` satisfy the equation because their
right-hand sides are respectively `1` and `11 = 1 mod 5`. Their y derivative
is `2 != 0`, which separately confirms nonsingularity at each point.

In the table, the entry lists all accepted targets among `{O,A,B}`; a dash
means none of those targets is accepted.

| Certificate | Empty family `[]` | Family `[0]` | Family `[1]` |
|---|---|---|---|
| Empty tuple | `O` | `O` | `O` |
| Raw singleton `[(0,0)]` | - | - | - |
| Affine singleton `[A]`, typed or raw | `A` | `A` | `A` |
| Affine singleton `[B]`, typed or raw | - | - | `B` |
| Typed singleton `[O]` | - | - | - |

The empty tuple row isolates the empty group sum and vacuity; it uses no
coordinate or generator hypothesis. The `[(0,0)]` row isolates the equation
check, even though its x-coordinate is in every displayed span. The `[A]`
row establishes that zero x-coordinates remain admissible with no generators.
The `[B]` row establishes that affinity, the curve equation, and a matching
target are insufficient without span membership. The `[O]` row establishes
that the affine requirement is necessary even if the target and sum match.
Finally, each affine singleton fails with target `O`, and switching its target
to the other affine point also fails; these isolate the sum-equality check.

The scratch computation enumerates the 25 raw coordinate pairs and executes
72 stated controls: 36 raw cases and 36 typed cases, across the three families,
four input tuples per representation, and three targets. It expects 14 accepts
and 58 rejections. No group law beyond the empty and singleton sum laws is used
by this finite panel. General tuple lengths are covered by the proof above.

## Scope of the verdict

J1 holds for the derived iff and these controls. The typed and raw predicates
have been kept distinct, and the possible nonsingularity obligation on a raw
pair is explicit. This review provides no conclusion about whether an unseen
producer theorem or implementation matches this predicate; that comparison
requires a separately authorized source review after the blind derivation
is sealed.
