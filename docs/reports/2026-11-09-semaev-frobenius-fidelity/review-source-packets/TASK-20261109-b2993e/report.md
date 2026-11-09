# J1 blind algebra and finite controls

Task: `TASK-20261109-b2993e`  
Source: `/var/tmp/semaev-frobenius-blind-input-20261109/blind-card.md` (SHA-256 `b530095988cf497d34f884d813f79f67592f52572480e21e8ac8b1c41b107a0b`)

## Verdict

**Holds:** for every commutative ring `K` of characteristic `p`, every natural `e`, every finite number `M` of variables, and every `g` in `R`,

`g^q - g^phi` belongs to `I_q`, where `q = p^e`.

This is a blind mathematical verdict about the card's polynomial congruence only.

## Derivation

Write `g = sum_alpha c_alpha x^alpha`, with finite support. Because `q` is a power of the characteristic prime, iterating the Frobenius endomorphism gives

`g^q = sum_alpha c_alpha^q x^(q alpha)`.

By the coefficientwise definition, `g^phi = sum_alpha c_alpha^q x^alpha`. In `R/I_q`, each `x_i^q = x_i`, hence `x^(q alpha) = x^alpha` for every multi-index `alpha`. Their difference is therefore zero in the quotient, proving ideal membership. This uses neither `c_alpha^q = c_alpha` nor any field assumption on `K`.

## Finite controls

1. **The ideal is essential for literal equality.** In `F_2[x]`, with `q = 2` and `g = x`, `g^2 - g^phi = x^2 - x`. This is a nonzero polynomial (its degree is 2), although it is the generator of `I_2`. It evaluates to zero at both elements of `F_2`; those evaluations do not make it the zero polynomial.

2. **The exponent must be a characteristic power.** In `F_2[x,y]`, set `q = 3` and `g = x+y`. Coefficientwise cubing fixes the coefficients, so `g^phi = x+y`. Characteristic 2 gives

   `(x+y)^3 - (x+y) = (x^3-x) + (y^3-y) + x^2 y + x y^2`.

   Thus the residue modulo `(x^3-x, y^3-y)` is `x^2 y + x y^2`, which is **nonzero**. For a finite witness, map `F_2[x,y]` to `F_4 = F_2[a]/(a^2+a+1)` by `x -> a`, `y -> 1`. Both ideal generators map to zero, since `a^3 = 1` and `1^3 = 1`, while the residue maps to `a^2+a = 1`. Consequently the difference is not in this ideal. In particular, testing only `F_2`-valued points would miss this failure.

3. **Non-prime-field coefficient.** In `K = F_4`, `a^2 = a+1`. For `q = 2`, `g = a x+1` gives `g^2 = a^2 x^2+1` and `g^phi = a^2 x+1`. Thus `g^2-g^phi = a^2(x^2-x)` lies in `I_2`, and it is not the zero polynomial. The coefficientwise twist by `phi` is necessary: replacing `g^phi` by `g` would leave coefficient `a^2-a = 1` at `x` after reduction.

4. **Empty variables.** For `M = 0`, `R = K` and `I_q = (0)` because there are no generators. For any `g = c` in `K`, `g^q = c^q = g^phi`, so the difference is literally zero. This remains true even when `K` is not a field.

5. **Zero exponent.** For `e = 0`, `q = p^0 = 1`, `phi` is the identity, and every generator `x_i^1-x_i` is zero. Hence `I_1 = (0)` and `g^1-g^phi = g-g = 0` as a literal polynomial equality for every `M`, including `M = 0`.

## Scope

The proof covers finite polynomial expressions over a commutative ring of characteristic `p`. The `q = 3` example is an intentional counterexample to a nearby claim outside `q = p^e`. No producer code, repository state, archived run, or sibling review was examined.
