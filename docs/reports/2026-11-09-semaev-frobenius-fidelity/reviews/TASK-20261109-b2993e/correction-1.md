# J1 additive correction 1

Task: `TASK-20261109-b2993e`  
Joint: `J1 blind algebra and finite controls`  
Source: `/var/tmp/semaev-frobenius-blind-input-20261109/blind-card.md` (SHA-256 `b530095988cf497d34f884d813f79f67592f52572480e21e8ac8b1c41b107a0b`)

This corrects only the finite witness in control 2 of the original sealed J1 report. The original report asserted that `x -> a`, `y -> 1` into `F_4` annihilates `x^3-x`. That assertion is false: `a^3=1`, so `a^3-a=1-a` is nonzero. The `F_4` evaluation must not be used as evidence of ideal nonmembership.

## Correct finite witness

The residue calculation itself is unchanged:

`(x+y)^3 - (x+y) = (x^3-x) + (y^3-y) + x^2 y + x y^2`

in `F_2[x,y]`. Let `A = F_2[u]/(u^2)`, a four-element ring, and evaluate `x -> 1+u`, `y -> 1`. Both generators of `I = (x^3-x, y^3-y)` vanish in `A`:

- `(1+u)^3-(1+u) = (1+u+u^2+u^3)-(1+u) = 0`, since `u^2=0`;
- `1^3-1 = 0`.

The residue maps to

`(1+u)^2*1 + (1+u)*1^2 = 1+(1+u) = u`,

and `u` is nonzero in `A`. Thus the evaluation factors through `F_2[x,y]/I` and detects a nonzero class. Hence `x^2 y + x y^2` is not in `I`.

Independently, the monic relations `x^3-x` and `y^3-y` yield a unique normal form with monomials `x^i y^j`, `0 <= i,j < 3`: reduce powers of `x` and `y` independently, and use division by a monic polynomial in one variable to establish uniqueness at each step. The residue `x^2 y + x y^2` is already such a form, with two distinct nonzero coefficients.

## Verdict and scope

The J1 mathematical verdict remains **holds** for `q=p^e`: the Frobenius congruence follows term by term in the quotient, including `M=0` and `e=0`. The nearby `q=3` claim in characteristic 2 still **breaks**. This correction concerns a blind mathematical derivation and controls only; it makes no assertion about producer Lean code, repository state, archived runs, or sibling reviews. The original sealed packet remains unchanged and should be read together with this correction.
