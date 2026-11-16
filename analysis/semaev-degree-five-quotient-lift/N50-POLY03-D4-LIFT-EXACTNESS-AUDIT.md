# n50 polynomial03: source and execution audit of the D3-to-D4 lift

The original-system `fresh-n50-poly-03` D3 seed is now independently exact W3 (`N50-POLY03-W3-EXACTNESS.md`). This note checks the retained D4 lift against Proposition 1.9 of the theorem dossier. The [machine-readable readback](validation/n50-poly03-d4-lift-source-audit-001.json) has SHA-256 `b288845ef5cb7acbe79465e58aef7d20e662b830077c55fd77c0ca3f2385f84d`.

The frozen `n50n51-bounded-d4-concurrent-plan-001.json` pins `quotient_lift_checkpoint.cpp` SHA-256 `ce6424270a807bdb47ca7e391fd74467fedb6d5a6759a8a71655b99e7d96f7d6` and invoked binary SHA-256 `fc0911db6560fe10b49d88d6206f89f8de6494616020a864c82d8be552749613`. Both retained files rehash to those values. The seed SHA-256 is `d5e27dbe345b6a5f3100f41d6be1df4702be2de0a52b07dbfec3907d5425a94d`, and the exported D4 map SHA-256 is `6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719`. The terminal `result.json`, producer stdout/stderr and independent D4 checker stdout rehash to their recorded artifact values; the producer and checker both exited zero.

The source implements the Proposition 1.9 objects as follows:

| Source construction | Mathematical object |
| --- | --- |
| `rep[q]` from literal unit seed rows | monomial representatives `b_q` |
| `standard` high monomials and acyclic reverse `divisor` rewrite | onto provisional map `phi:B_<=4 -> P` |
| initial `seed variable` products `seed*T_x + map[xm]` | images `phi(x_i u_m)` for the seed-kernel basis relations |
| low-block echelon rows, then `action(x)` multiplication | closure of `A cap Q` under `T_i` |
| `export_map` after stable rank | quotient by terminal relation space `A` |

The saved stderr reports every seed variable 1–50. It then records closure-round ranks `42,646`, `51,955`, `58,955`, `58,955`: the fourth round adds no relation. The saved stdout is `candidate_certificate`, with 97,584 provisional coordinates, codimension 38,629 and four rounds. The arithmetic `97,584 - 58,955 = 38,629` matches the independently accepted D4 map. The D4 checker confirms an onto quotient that kills the 50 generators, has a closed kernel, and keeps one nonzero.

**Conditional exactness reading.** Proposition 1.9 says that a completed lift from exact W3 presents W4 exactly. The source and terminal receipts satisfy its structural and fixed-point premises. If the invoked binary executed that audited source and its reported rank correctly, the D4 kernel equals W4 and `dim W4 = 251,176 - 38,629 = 212,547`. The saved result is a source-and-execution audit, not an independent primal relation transcript or direct W4 rank calculation. The source and binary hashes are pinned separately, but no bit-for-bit rebuild or independent full-size rank replay is supplied by this audit. The separately checked D4 map already proves `W4` is contained in its kernel; an independent rank of 212,547 would supply the missing two-sided dimension check without relying on the producer's rank.

This conditional W4 reading makes the n50 same-seed sliced D5 producer result scientifically relevant. It does not turn that producer's killed-projection status into a checked W5 membership relation; a separate D5 transcript remains necessary. It also does not produce an LFD-six lower bound.
