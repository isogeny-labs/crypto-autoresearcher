# A15 independent blind algebra review

Date: 2026-11-07 UTC. Administrative archival task: T-1778.

**Overall verdict: holds**, for the field identities with the precise inverse semantics and assumptions stated below. **Breaks** applies to recovering both inverses after dropping either required nonzero assumption, and to interpreting the equal-x finite formula as elliptic-curve addition. Whether an unseen theorem or implementation states and implements this scope is **inconclusive**: neither was inspected.

## Isolation, sources, and method

The sole substantive external source read was:

- `/var/tmp/a15-blind-packet-20261107/blind-input.md`, SHA-256 `940de8dd1b0be02aa7f0e4349b1f1ccf066420d919fdc9ad427ff00a4aff9145`.

I ran `sha256sum` and `cat` on that file; the computed digest exactly matched the assigned digest. The packet supplies definitions and questions; its `[pcc:unverified]` annotations were not treated as evidence of correctness.

Conversation instructions supplied the isolation constraints, administrative identifiers, and output destination. A parent message changed the destination from the original report path to this independent path and disclosed only that another report existed. I did not read that report, its contents, or any sibling review. No repository files, Git history, target YAML, Lean proof text, build or audit receipts, source review, Conductor task contents, memory files, skill files, web pages, or mathematical reference texts were read. I did not run a build, commit, push, contact an external service, or execute a cloud job. The only file created by this review is this report.

All derivations below were made independently from the packet. A short inline Python 3 program used only integer arithmetic and built-in functions to check independently constructed finite-field instances; it imported no modules and read no research inputs or other files. Its complete source is reproduced below. The finite checks support the controls; the symbolic derivations establish the arbitrary-field identities.

## 1. Recovering the two inverses

Let `z = (x*y)^(-1)`. Under `x != 0` and `y != 0`, the product is nonzero and

```
x * (y*z) = (x*y)*z = 1,
y * (x*z) = (x*y)*z = 1.
```

Uniqueness of a multiplicative inverse gives

```
x^(-1) = y * (x*y)^(-1),
y^(-1) = x * (x*y)^(-1).
```

Thus each child is multiplied by the opposite child after inversion of the product. These statements need no characteristic restriction.

If inverse is partial, `x != 0` and `y != 0` are required for both requested target inverses and the product inverse to be defined. If inverse is totalized by `0^(-1) = 0`, as is usual in algebraic field formalizations, the exact truth conditions are slightly more precise:

```
x^(-1) = y*(x*y)^(-1)   iff   (y != 0 or x = 0),
y^(-1) = x*(x*y)^(-1)   iff   (x != 0 or y = 0).
```

To see the first equivalence, if `y != 0`, use the preceding cancellation proof when `x != 0` and check `x = 0` directly. If `y = 0`, the right-hand side is zero, so equality holds exactly when `x^(-1) = 0`, equivalently `x = 0`. Interchanging the variables proves the second equivalence.

Consequently both identities hold exactly when both inputs are nonzero or both are zero. The double-zero equality is a property of totalized formulas; it supplies no multiplicative inverse of zero.

### Dropped-nonzero controls

These examples work in every field:

| Control | Claimed recovered x inverse | Claimed recovered y inverse | Result |
| --- | --- | --- | --- |
| `x=1, y=0` | `0*(0)^(-1)=0`, but `1^(-1)=1` | `1*(0)^(-1)=0=0^(-1)` | x recovery breaks when `y != 0` is dropped |
| `x=0, y=1` | `1*(0)^(-1)=0=0^(-1)` | `0*(0)^(-1)=0`, but `1^(-1)=1` | y recovery breaks when `x != 0` is dropped |
| `x=0, y=0` | `0=0` | `0=0` | both formal identities hold; no zero inverse exists in the multiplicative sense |

In `F_7`, the nontrivial positive control `x=2, y=3` has `(x*y)^(-1)=6`, so the opposite multipliers recover `3*6=4=2^(-1)` and `2*6=5=3^(-1)`. The deliberately wrong same-child multiplier produces `5` as the purported inverse of `2` and is detected.

## 2. Simultaneous y negation

Write

```
d = xk-xj,  u = d^(-1),
s = (yk-yj)*u,
X = s^2-(xj+xk),
Y = s*(xj-X)-yj.
```

After replacing both y inputs by their negatives, the denominator is unchanged and

```
s' = ((-yk)-(-yj))*u = -(yk-yj)*u = -s,
X' = (-s)^2-(xj+xk) = X,
Y' = (-s)*(xj-X)-(-yj) = -s*(xj-X)+yj = -Y.
```

Therefore the new output is exactly `(X,-Y)`.

No division or cancellation by `d` occurred in this derivation. With a totalized inverse, it holds for every quadruple over every field, including `d=0`. With a partial inverse, the formulas are defined only when `d != 0`.

## 3. The four signed candidates

Let `C_{sigma,tau}` mean the packet's formula with y inputs `(sigma*yj, tau*yk)` and the same x inputs. Let

```
a = (yk-yj)*u,
b = (yk+yj)*u,
A = a^2-(xj+xk),
B = b^2-(xj+xk),
H = a*(xj-A)-yj,
K = b*(xj-B)+yj.
```

Direct substitution gives:

| Candidate | Slope | X coordinate | Y coordinate |
| --- | --- | --- | --- |
| `(+,+)` | `a` | `A` | `H` |
| `(-,-)` | `-a` | `A` | `-H` |
| `(-,+)` | `b` | `B` | `K` |
| `(+,-)` | `-b` | `B` | `-K` |

In particular,

```
C_{-,-} = (X_{+,+}, -Y_{+,+}),
C_{-,+} = (X_{+,-}, -Y_{+,-}).
```

Each pair shares its X coordinate and has opposite Y coordinates. This does not assert that all four candidates are distinct. In characteristic two, negation is the identity and all four signed input choices coincide. In other characteristics, zero y coordinates or zero output Y coordinates can also collapse some sign choices.

The cross-pair comparison is not a statement that `A=B` universally. When `d != 0`, their difference is

```
B-A = ((yk+yj)^2-(yk-yj)^2)*u^2 = 4*yj*yk*u^2.
```

This additional identity explains why the two pairs can have different X coordinates.

### Sign and mutation controls

Over `F_7`, with `(xj,yj,xk,yk)=(1,2,3,4)`, direct calculation yields

```
C_{+,+} = (4,2),   C_{-,-} = (4,5),
C_{-,+} = (5,4),   C_{+,-} = (5,3).
```

Both required pair relations hold and the two pairs have different X coordinates. Deliberately negating the slope while incorrectly retaining the original `-yj` term gives Y coordinate `1` in the `(-,-)` calculation, instead of the required `5`. This control detects failure to negate the intercept contribution.

## 4. Equal-x attack and geometric scope

Under totalized inverse and `xk=xj`, one has `u=0` and every candidate slope is zero, regardless of the y inputs. In particular,

```
C_{+,+} = (-2*xj,-yj),
C_{-,-} = (-2*xj, yj),
C_{-,+} = (-2*xj, yj),
C_{+,-} = (-2*xj,-yj).
```

The sign identities still hold. The finite formula ignores `yk` entirely at this boundary. This is an explicit example of an algebraic identity surviving at inputs where its point-addition interpretation fails.

For a concrete on-curve control, take the nonsingular curve

```
E/F_5: y^2 = x^3+x+1.
```

Here `4*A^3+27*B^2 = 31 = 1 mod 5`, so the discriminant is nonzero. The points `P=(0,1)` and `-P=(0,4)` are on E.

- For inputs `P` and `-P`, the group sum is the point at infinity, but the totalized distinct-point formula returns the finite point `(0,4)`.
- For inputs `P` and `P`, the correct tangent slope is `(3*0^2+1)/(2*1)=3 mod 5`. Thus `2P=(4,2)`. The equal-x substitution in the packet's secant formula again returns `(0,4)`.

Both attacks use actual points on the same nonsingular curve. The incorrect finite outputs in these controls are themselves on the curve, so merely checking the curve equation would not detect the wrong sum.

For the usual nonsingular short Weierstrass model `y^2=x^3+A*x+B` in characteristic other than two, with both inputs on that curve and `xj != xk`, the packet's secant formulas do compute the group sum, and y negation is point negation. Characteristic three need not be excluded for these secant formulas when the curve is nonsingular. Signed inputs retain the same distinct x coordinates, so the same domain condition applies to all four candidates. In this setting their relations agree with `(-P)+(-Q)=-(P+Q)` and `(-P)+Q=-(P+(-Q))`.

At equal x, one must use the appropriate doubling or inverse-point case and represent the point at infinity. At a point of order two, doubling also reaches infinity. The field identities alone provide none of these case distinctions.

The packet specifies no curve model or on-curve assumptions. On a generalized Weierstrass model, point negation generally has the form `(x,-y-a1*x-a3)`; raw y negation need not be geometric negation. Thus geometric assertions require a model and domain beyond the arbitrary-field formulas.

## 5. Exhaustive finite-field checks and limits

The independent inline program checked the fields `F_2`, `F_3`, `F_5`, `F_7`, and `F_11` using totalized inversion. It exited with status zero and all assertions passed.

| Prime | Recovery input pairs | Both nonzero | Formula quadruples | Equal-x quadruples |
| --- | ---: | ---: | ---: | ---: |
| 2 | 4 | 1 | 16 | 8 |
| 3 | 9 | 4 | 81 | 27 |
| 5 | 25 | 16 | 625 | 125 |
| 7 | 49 | 36 | 2,401 | 343 |
| 11 | 121 | 100 | 14,641 | 1,331 |
| Total | 208 | 157 | 17,764 | 1,834 |

For every recovery pair, the checks verified both exact truth conditions and the combined truth condition, including failures after dropping an assumption. For every quadruple, the checks verified both requested sign-pair identities. Equal-x tuples were additionally checked against their degenerate closed forms. The two deliberately incorrect formulas were confirmed to disagree with their intended outputs. The on-curve equal-x arithmetic was also checked explicitly.

These finite tests are not a proof for arbitrary fields; the preceding symbolic arguments supply that proof. The review establishes formula identities, their required inverse semantics, and concrete domain failures. It cannot establish the contents or correctness of an unseen Lean statement or proof, implementation behavior, build status, batch-tree invariants, source custody, execution cost, or performance. No such claim was inspected or inferred.

## Reproducible control program

Executed inline as `python3 - <<'PY'` with the following body; no input files other than the packet were consulted in preparing it:

```python
primes = (2, 3, 5, 7, 11)
totals = {'recovery_pairs': 0, 'nonzero_recovery_pairs': 0, 'formula_tuples': 0, 'equal_x_tuples': 0}
for p in primes:
    inv = lambda a: pow(a % p, p - 2, p) if a % p else 0
    recovery_pairs = 0
    nonzero_pairs = 0
    formula_tuples = 0
    equal_x_tuples = 0
    for x in range(p):
        for y in range(p):
            rx = y * inv(x*y) % p
            ry = x * inv(x*y) % p
            assert (rx == inv(x)) == (y != 0 or x == 0)
            assert (ry == inv(y)) == (x != 0 or y == 0)
            assert ((rx == inv(x)) and (ry == inv(y))) == ((x == 0 and y == 0) or (x != 0 and y != 0))
            recovery_pairs += 1
            nonzero_pairs += int(x != 0 and y != 0)
    def candidate(xj, yj, xk, yk):
        s = (yk-yj) * inv(xk-xj) % p
        X = (s*s-xj-xk) % p
        Y = (s*(xj-X)-yj) % p
        return X, Y
    def neg(pair):
        return pair[0], (-pair[1]) % p
    for xj in range(p):
        for yj in range(p):
            for xk in range(p):
                for yk in range(p):
                    pp = candidate(xj, yj, xk, yk)
                    mm = candidate(xj, -yj, xk, -yk)
                    mp = candidate(xj, -yj, xk, yk)
                    pm = candidate(xj, yj, xk, -yk)
                    assert mm == neg(pp)
                    assert mp == neg(pm)
                    if xj == xk:
                        assert pp == ((-2*xj) % p, (-yj) % p)
                        assert mm == ((-2*xj) % p, yj)
                        equal_x_tuples += 1
                    formula_tuples += 1
    totals['recovery_pairs'] += recovery_pairs
    totals['nonzero_recovery_pairs'] += nonzero_pairs
    totals['formula_tuples'] += formula_tuples
    totals['equal_x_tuples'] += equal_x_tuples
    print({'p': p, 'recovery_pairs': recovery_pairs, 'nonzero_recovery_pairs': nonzero_pairs, 'formula_tuples': formula_tuples, 'equal_x_tuples': equal_x_tuples})
print({'totals': totals})
p = 7
inv = lambda a: pow(a % p, p-2, p) if a % p else 0
assert 3*inv(2*3)%p == inv(2) == 4
assert 2*inv(2*3)%p == inv(3) == 5
assert 2*inv(2*3)%p != inv(2)
xj, yj, xk, yk = 1, 2, 3, 4
s = (yk-yj)*inv(xk-xj)%p
X = (s*s-xj-xk)%p
Y = (s*(xj-X)-yj)%p
mutant_Y = ((-s)*(xj-X)-yj)%p
assert (X, Y) == (4, 2)
assert mutant_Y == 1 and (-Y)%p == 5
print({'mutation_controls': 'same-child recovery and omitted intercept sign are detected', 'sign_example': {'pp': (4, 2), 'mm': (4, 5), 'mp': (5, 4), 'pm': (5, 3)}})
p = 5
inv = lambda a: pow(a % p, p-2, p) if a % p else 0
P = (0, 1)
minusP = (0, 4)
assert (4*1**3+27*1**2)%p != 0
assert (P[1]**2 - (P[0]**3+P[0]+1))%p == 0
assert (minusP[1]**2 - (minusP[0]**3+minusP[0]+1))%p == 0
m = (3*P[0]**2+1)*inv(2*P[1])%p
X2 = (m*m-2*P[0])%p
Y2 = (m*(P[0]-X2)-P[1])%p
assert (X2,Y2)==(4,2)
assert (Y2**2 - (X2**3+X2+1))%p == 0
print({'equal_x_geometric_control': {'field': 5, 'curve': 'y^2=x^3+x+1', 'P': P, 'minusP': minusP, 'degenerate_formula': (0,4), 'actual_double': (X2,Y2), 'P_plus_minusP': 'point at infinity'}})
```

## Final attestation

I independently derived the identities from the single hash-verified blind packet before filing this report. I preserved the assigned information barrier and did not inspect any prohibited source or report. The only prior-review information disclosed to me was that an earlier report file existed; its content played no part in this review. This attestation applies to this reviewer session and this report.
