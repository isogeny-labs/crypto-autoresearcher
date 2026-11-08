# n47 random00: exactness conditions for the queued D5 lift

The queued `n47-rand00-d5-local-002` attempt uses
`quotient_lift_checkpoint.cpp` with checkpoint environment variables removed by
`run_n47_rand00_d5_local.py`. This is a source audit of the mathematical
algorithm, not a claim that the queued attempt has run or that its future
output is a certificate. The output root is write-once and remains absent at
this audit.

The committed C++ source SHA-256 is
`ce6424270a807bdb47ca7e391fd74467fedb6d5a6759a8a71655b99e7d96f7d6`;
the included `quotient_checkpoint.hpp` SHA-256 is
`553e26f10907206d622684bec776d1e65ee1b91f096b8f0b271b378b9d27816e`.
The retained binary SHA-256 is
`fc0911db6560fe10b49d88d6206f89f8de6494616020a864c82d8be552749613`,
matching the frozen plan. The source audit assumes that binary implements
these committed sources; it is not an independent reproducible-build proof.

The current source's admission expression can be recomputed from the frozen
dimensions (`next_columns=1,925,357`, `old=213,053`, `nq=61,196`,
`work=187,583`, `chunk=4,096`). It gives `stride=23,464`,
`seedstride=7,672`, payload 62,509,841,968 bytes, and the source's
`payload*135/100+64 MiB` envelope **84,455,395,520 bytes**. The frozen plan
reserves 86,599,881,493 bytes, exceeding that source expression by
2,144,485,973 bytes; both are below its 96-GiB child address-space cap
(103,079,215,104 bytes). The source accepts that cap exactly. This
arithmetic checks the current source and frozen plan for an immediate
resource-argument refusal, but neither expression measures peak RSS or
guarantees host admission. The runner removes `SEMAEV_CHECKPOINT_*` variables,
so this attempt has no checkpoint writing or restoration despite the reused
binary's optional capability.

Proposition 1.9 in `../semaev-m2-last-fall-degree/theorem-dossier.md` gives
the exactness criterion. The source implements its steps as follows:

| Proposition 1.9 object | Source operation |
| --- | --- |
| Unit monomial representatives of the D4 quotient | `rep` and `repq` require one unit row for every seed coordinate; the descending `allowed` check rejects nontriangular representatives. |
| Acyclic high-monomial rewrite | `divisor` selects a nonrepresentative D4 divisor; the reverse high-column loop requires every rewrite target to have a later column. |
| Initial relations `phi(x_i u_m)` | Each seed row is multiplied through `action(x)`, then the provisional image of `x_i m` is xor-ed before echelon insertion. This is done for every seed monomial and variable. |
| Closure of `A cap Q` | Echelon rows with leading column at least `nhigh` form a basis of the low-coordinate intersection. Every such row is multiplied by every variable, and rounds continue until the rank is unchanged. |
| Quotient export | The terminal relation pivots are eliminated from the provisional map; the remaining coordinates are written in the standard certificate format. |

All inserted relations are images of legal degree-five multiples of the D4
kernel or of previously found low-degree relations. Conversely, at a
completed fixed point the final relation space is closed in the sense of
Proposition 1.9. Thus, **if the D4 seed kernel is exactly `W_4(F)`**, a
completed candidate export has kernel exactly `W_5(F)` at the source-algorithm
level. The n47 D4 exactness premise is the conditional source-and-execution
audit in `N47-D4-EXACT-LIFT-AUDIT.md`; it is stronger than the independent
checker result, which only proves `W_4(F)` is contained in the seed kernel.

The producer can return `projection_kills_one`, fail, time out, or write an
unchecked candidate. None proves `1 not in W_5(F)`. A positive degree-six
lower bound requires the independent D5 checker to accept a nonzero image of
one and the independent exact zero count to accept the same named instance.
The checker establishes the lower bound even if the stronger source-level
exactness premise is later withdrawn. The queued runner's one-attempt budget
and publication gates are unchanged by this audit.
