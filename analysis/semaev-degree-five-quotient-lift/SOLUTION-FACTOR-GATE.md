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
finite check of the factorization, not a sample. A failed comparison now
returns a small explicit kernel polynomial: if `pi4(m)` has quotient bits
`J` and representative monomials `r_j` map to the unit vectors, then
`u = m + sum_(j in J) r_j` lies in `ker(pi4)` but evaluates to one at the
listed solution. The checker rechecks both properties before reporting
the witness. This proves the accepted D4 kernel is not contained in the
solution ideal; it does not prove any statement about `W4` itself.
If the map exposes one
unit-vector image for every quotient coordinate, those rows provide the
basis directly; otherwise basis selection must use exact F2 elimination.
Each claimed solution must also be checked against all 51 independently
exported original generators. A fresh exact count of six must establish
that the list is complete; six individually valid points alone do not.

This is an optional preflight for a future bounded producer attempt. The
current retained count gives six but does not list the six assignments, and
no factorization check has been run. In particular, neither the successful
slice W4 rank nor the original D4 quotient check supplies this gate.

The source-only preparation now includes `enumerate_original_pairs.c`, a
copy of the published exhaustive sum counter that emits each ordered pair
instead of only incrementing its count. The emitter prints two lowercase
hexadecimal field elements per stdout line and the total on stderr. For
this fixed polynomial basis, each element is directly its 26-bit Boolean
coordinate mask. `check_original_solution_factorization.py` requires a
hash-pinned six-line list, a separately hash-pinned count stdout containing
`6`, the accepted D4 seed, and the already independently checked generator
binary. It checks all 51 equations at every listed point, finds a unit-row
basis of the quotient map, and compares the induced evaluation functionals
against every D4 monomial image. It refuses a map without all unit rows;
the pinned blocked-lift source requires unit-surjectivity of its seed.
The checker uses Python 3.10 or newer for integer `bit_count`.

No emitter build, root enumeration, or full-size factorization check has
been performed. Before any bounded run, publish the exact source, command,
input hashes, resource and dollar ceilings, and deadline, then verify live
budget headroom. Keep its result separate from the already frozen V3 D5
attempt and preserve all failures and receipts.

`verify_solution_factor_result.py` is a separate, source-independent
readback checker for either verdict. It parses the original quotient map
and generator binary itself, rechecks the six listed roots, and either
streams every map row for the positive verdict or checks the explicit
kernel polynomial and its nonzero evaluation for the negative verdict.
It verifies the saved pair, count, generator and seed hashes against the
frozen plan and result. Its acceptance of a count stdout containing `6`
assumes the separately pinned exhaustive counter's successful run and
receipt; the reviewer must inspect that receipt as well. The small-map
positive, negative and mutated-witness controls pass, but no full-size
readback has occurred.
