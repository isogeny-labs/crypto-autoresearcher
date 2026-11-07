# A solution-factorization gate for the original n51 D4 seed

Let `pi4: B_<=4 -> Q` be the accepted original polynomial-00 D4 quotient
map and `U = ker(pi4)`. Its checker proves `W4(F) subset U`; it does not
prove that `U` vanishes at the six Boolean solutions. The latter property
can be checked directly without computing the exact rank of `W4(F)`.

For a Boolean solution `s`, write `ev_s` for evaluation on `B_<=4`. Since
`pi4` is onto, the following statements are equivalent:

1. Every polynomial in `U` evaluates to zero at `s`.
2. There is a unique linear functional `lambda_s: Q -> F2` satisfying
   `ev_s = lambda_s composed with pi4`.

Indeed, the first condition says that `ev_s` is constant on fibers of
`pi4`, so it descends to the quotient. Conversely, a factorization kills
the kernel. The equivalence applies separately to every solution; checking
all six establishes `U subset I(S)`. Lemma 1.7 of the theorem dossier then
gives `C5(U) subset I(S)`, `1 not in C5(U)`, and quotient dimension at least
six. It does **not** give dimension seven or LFD at least six. A separately
checked D5 quotient of dimension at least seven remains necessary for the
desired lower bound (Proposition 1.4).

The accepted binary map stores the image of every degree-at-most-four
monomial as a 45,615-bit row. A check can select 45,615 monomials whose
images form a basis of `Q`, solve the value of `lambda_s` on that basis
from their evaluations, then stream through *all* 294,204 monomial rows.
For every row `m`, compare `lambda_s(pi4(m))` with `m(s)`. This is a complete
finite check of the factorization, not a sample. If the map exposes one
unit-vector image for every quotient coordinate, those rows provide the
basis directly; otherwise basis selection must use exact F2 elimination.
Each claimed solution must also be checked against all 51 independently
exported original generators. A fresh exact count of six must establish
that the list is complete; six individually valid points alone do not.

This is an optional preflight for a future bounded producer attempt. The
current retained count gives six but does not list the six assignments, and
no factorization check has been run. In particular, neither the successful
slice W4 rank nor the original D4 quotient check supplies this gate.
