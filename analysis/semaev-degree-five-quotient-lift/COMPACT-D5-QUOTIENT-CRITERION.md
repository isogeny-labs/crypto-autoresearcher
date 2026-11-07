# A compressed degree-five nonmembership certificate

This is a proved certificate criterion for a future independent checker, not
an n47 certificate or an executed frontier run. It specializes the
provisional-map construction in Proposition 1.9 of
`../semaev-m2-last-fall-degree/theorem-dossier.md` and does **not** assume
that the checked degree-four seed is exact.

Let `beta:B_<=4 -> Q` be an onto, independently checked degree-four quotient
map satisfying Proposition 1.5 for `F`. Put `U=ker beta`. Require unit
monomial representatives `b_q` and the acyclic degree-five rewrite described
in Proposition 1.9. That construction gives an onto linear map

`phi:B_<=5 -> P=H_high direct_sum Q`

whose restriction to degree at most four is `beta` in the `Q` block. Let
`h:P -> Z` be any linear map. For every low monomial `m`, set
`u_m=m+sum_q beta(m)_q*b_q`; these `u_m` span `U`. For a variable `x_i`,
write `T_i(q)=phi(x_i*sum_q q_q*b_q)`. The following are finite checks:

1. `h(phi(1)) != 0`.
2. `h(phi(x_i*u_m)) = 0` for every variable `i` and low monomial `m`.
3. For every `i`, `ker(h|_Q) <= ker(h*T_i)`. Paired elimination of the
   `dim Q` columns `(h(e_q), h(T_i(e_q)))` checks this without constructing
   a basis of the kernel.

**Claim.** If these checks pass, `1 not in W_5(F)`. If `h` has rank `r`,
they also give `codim W_5(F) >= r`. No exactness of `U=W_4(F)` is needed.

*Proof.* Put `S=ker(h*phi)`. Every generator has degree at most four and
lies in `U`, because `beta` is checked; hence `F <= S`. Let `g` lie in
`S cap B_<=4`, and set `q=beta(g)`. Since `phi(g)=q`, we have
`q in ker(h|_Q)`. The difference
`g+sum_q q_q*b_q` lies in `U` and is a linear combination of the `u_m`.
Condition 2 therefore kills its product with every `x_i`. Condition 3 kills
`h(T_i(q))`, the image of the representative's product. Consequently
`h(phi(x_i*g))=0` for every variable. Thus `S` contains the generators and
is closed under every allowed degree-five multiplication. By the definition
of `W_5`, `W_5(F) <= S`; condition 1 separates the constant. As `phi` is
onto, `rank(h*phi)=rank(h)=r`, giving the codimension statement. QED.

For the n47 affine slice, `B_<=5` has 1,729,648 monomials. The retained D4
seed has `dim Q=61,196`, and its provisional lift has 187,583 coordinates.
A row-major `h` matrix of rank `r` therefore needs about 9.23 times fewer
row bytes than a full degree-five quotient map of the same rank. At
`r=61,196`, the conceptual 32-byte-header plus padded-row format is
1,436,135,480 bytes (1.338 GiB), versus 13,256,022,304 bytes for the full
map. This comparison concerns certificate storage only; the checker still
must derive or stream the seed rewrite and check all initial relations.

The current producer computes a `projection` matrix from the provisional
coordinates to the terminal quotient before multiplying it into every
degree-five monomial row. That matrix is a candidate `h`, but it must be
exported with seed, provisional-map, rank, and source bindings and checked
independently under the three conditions above. The frozen D5 attempt and
its output contract are unchanged; a compact-output producer/checker would
need its own frozen protocol and budget admission.

`compact_quotient_reference.py` implements the three checks for at most ten
variables and rechecks the seed closure. Its retained n6 test extracts `h`
from an existing D5 map, independently descends the n6 generators, checks the
compact criterion, and verifies that
`h*phi` reproduces every full-map monomial image; a synthetic two-point
quotient exercises recursive high-monomial rewriting. This is a correctness
oracle for a future bounded frontier checker, not a checker for n47 files.
