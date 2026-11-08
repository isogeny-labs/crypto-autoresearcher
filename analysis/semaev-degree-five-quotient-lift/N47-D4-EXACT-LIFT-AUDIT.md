# n47 random00: source audit of the batched D4 quotient lift

Proposition 1.9 in the theorem dossier proves that a completed quotient lift
from an exact degree-three seed presents exactly $C_4(W_3(F))=W_4(F)$.
This note maps that construction to the retained n47 random00 attempt.
The original lift account below is a source-and-execution audit. A later
independent direct $W_4$ rank replay now supplies the missing two-sided
dimension evidence; the D4 map's separate checker supplies containment.

The seed's exactness premise is now independently reproduced in
`N47-D3-EXACT-CLOSURE-AUDIT.md`: a separate Python derivation matches every
row of the retained `input.sys` and computes the full D3 fixed point at rank
5,546 in 18,473 columns, leaving 12,927 quotient coordinates. This removes
the direct D3 producer's source-to-executable assumption from the seed
exactness claim. The high-memory
attempt rechecked that exact seed hash before invoking
`quotient_lift_batched`.

In `quotient_lift_batched.cpp`, the named mathematical objects are:

| Source operation | Proposition 1.9 object |
| --- | --- |
| `rep[q]` records a monomial whose seed row is the unit vector $e_q$ | $b_q$ |
| `standard` retains high monomials with no non-unit degree-three divisor | $H$ |
| `map` rows for low monomials copy the seed quotient rows | $\phi|_{B_{\le3}}=\beta$ |
| reverse rewrite of each nonstandard high monomial using `divisor` and `missing`, with `target>i` | acyclic $\phi(xm)=\sum_q\beta(m)_q\phi(xb_q)$ |
| each `seed variable` relation `seed[m]*T_x + map[xm]` | $\phi(xu_m)$ |
| echelon rows whose leading coordinate is in the low seed block, then multiplication by each `T_x` | $A\cap Q$ and its closure |
| `export_map` projects `map` modulo the terminal relation row space | $B_{\le4}\to P/A$ |

The producer wrote `provisional map constructed`, completed all 48 seed
variables, and reported relation rank 11,359 before closure. Its four
closure rounds reached ranks 34,013, 40,969, 47,549 and 47,549. The
last equal-rank round is the fixed-point condition in Proposition 1.9.
Its terminal record is

```
{"status":"candidate_certificate","working_coordinates":108745,
 "codimension":61196,"closure_rounds":4}
```

The arithmetic agrees: `108745 - 47549 = 61196`; the exported original-system
map is degree four on 48 Boolean variables with 213,053 monomial columns.
The independent checker
accepted its surjectivity, generators, closure, and nonzero image of one.
As a small implementation control, the retained n=6/n=8 cascade fixtures
have direct degree-four fixed-point quotient dimensions 3, 1 and 1;
their batched lifts report the same three dimensions. This checks the
source correspondence on those fixtures, not at n47 scale.

| Retained item | SHA-256 |
| --- | --- |
| named `input.sys` | `b8ee56830e9b7f064c4cfe17579b512dd3f7b01e62fd0575b6632a37f2ec936c` |
| D3 seed map | `ee92818caa402f34b9ffe8f61d00db95f1ab73d74b8bed120fbfb08d353a5bb1` |
| accepted D4 map | `3bdad807113e43ec41ac6e9edcb2a282ffa486c7a694eba0dd3e0e9b0fa5162f` |
| `quotient_lift_batched.cpp` at recorded source commit `0fe0e3ac` | `5fb060678c462894fef27e7fe2afd009b6268d03d8c6f08b82e343e1b188845d` |
| invoked `quotient_lift_batched` binary | `ba0fe8d4986063634381908da1257cb3e24303fb88a251e13e74270f55caeb08` |
| `produce4.stdout.txt` | `3f73e21fadc69bb50ab9690e6787e77145fd7d8fc25ee7516d4e18f0c0f5d48d` |
| `produce4.stderr.txt` | `ad4a49b262a09278c432aa8f2ea9ed38c3c4b5dc61ae785ffe9114fbce191fed` |
| terminal `result.json` | `0e9281892d213c5736f9be336571408c2399190b367980c32f80f6b611ca96f1` |

The committed `highmem-plan.json` pins the source and binary hashes.
The retained result records that binary's invocation and terminal status.
The original lift audit does not establish a bit-for-bit rebuild of the
native binary or an independent derivation basis for every D4 relation.
Proposition 1.9 and the independently exact D3 seed gave the conditional
dimension reading

```
dim W_4(F_original) = 213053 - 61196 = 151857.
dim W_4(F_sliced)   = 195709 - 61196 = 134513.
```

where the sliced equality uses the checked affine witness and Proposition
2.5b. The planned projected D4 map has not yet been produced or checked.
Those dimensions are now supported independently. The frozen
`rank-check/n47-rand00-plan-002.json` ran the unchanged independent
`verify/indep_verify.py` on the same named record with `NOCOUNT=1` and a
16-GiB child address-space cap. It reconstructed the S3 equations by field
evaluation and Boolean interpolation, then built the degree-four Macaulay
space and repeatedly multiplied every newly found degree-at-most-three
pivot row until no such row remained. Its single completed output was
`W4 dims [0, 1, 141, 6909, 151857] contains_one 0 rank 151857 cols 213053`
in 12,535 seconds. The terminal `rank_match` receipt has SHA-256
`9543233d947e9ede88776a7c2a8e10c53af0d27bb408c0429b4d3c8c28c5f502`;
its pinned verifier, runner, request, D4 seed, accepted-checker transcript,
stdout and stderr hashes all match the retained files. The run exited zero
without timeout. Since the independently checked D4 map proves
$W_4(F)\subseteq U_4=\ker\pi_4$ and
$\dim U_4=213053-61196=151857$, the independently computed rank gives
**$U_4=W_4(F)$** for this named original input. Proposition 2.5b then gives
the displayed sliced dimension. This equality rests on the correctness and
recorded execution of the independent rank program; it is not a compact
primal row certificate and does not certify any degree-five claim.

The established seed equality is useful if a later D5 quotient lift kills
one: Lemma 1.6 identifies a completed exact lift's terminal closure with
$W_5(F)$, provided that D5 execution is source-audited or primal-certified.
A positive independently checked D5 nonmembership map needs only the D4
kernel inclusion and remains the direct route to the degree-six lower bound.
