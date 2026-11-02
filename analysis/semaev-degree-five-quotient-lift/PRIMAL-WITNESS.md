# Checkable degree-five primal refutation contract

For a zero-solution Boolean Semaev presentation, the retained D4 certificate
proves `1 not in W4`. A degree-five upper bound additionally needs `1 in W5`.
The [independent checker](verify_primal_witness.py) accepts a derivation of 1
from the named generators using only the defining closure rules. It does not
trust the quotient-lift producer's `projection_kills_one` status.

The witness is a JSON object with schema `semaev.boolean-primal-witness/v1`,
`variables`, `degree`, `generators`, `steps`, and `terminal`. Each generator is a
sorted list of unique integer monomial bitmasks; bit `i` denotes variable `i`,
and mask `0` denotes 1. Every step has one of these forms:

* `{"op":"input","index":i}` copies a defining generator.
* `{"op":"xor","refs":[i,...]}` adds earlier rows over GF(2).
* `{"op":"mul","ref":i,"variable":v}` multiplies an earlier row by variable
  `v` in the Boolean ring, provided that row has degree at most `degree-1`.

The final step must equal the constant polynomial 1. By induction on the
steps, every checked row belongs to `W_degree(F)`. The checker rejects
out-of-range or duplicate monomials, changed generator lists, forward
references, illegal multiplication degrees, and a nonconstant terminal row.

For the exact **n47 random00** input, the checker reconstructs the 47 equations
from the frozen plan using the independent `cert_check.py` descent, then
compares every generator before checking the derivation. Its current pins are:

```
plan SHA-256: 178bec5c09a4645274d8ef5806a3ebdd5681827e14258dd07cfc2b84fc331abd
descent source SHA-256: b6e28168091986b3cb04790f51889723db0ec5838633767bb80a6dc4ac97bd70
canonical system SHA-256: f9ab99aa260c60f4a28758488e363d7d400f4a9c7f2e8537fd572a974f2d5084
variables: 48; generators: 47; total terms: 14,443
```

After a producer emits `witness.json`, check it with:

```bash
python3 analysis/semaev-degree-five-quotient-lift/verify_primal_witness.py witness.json \
  --instance-plan analysis/semaev-degree-five-quotient-lift/rank-check/n47-rand00-plan-002.json \
  --expect-plan-sha256 178bec5c09a4645274d8ef5806a3ebdd5681827e14258dd07cfc2b84fc331abd \
  --expect-descent-source-sha256 b6e28168091986b3cb04790f51889723db0ec5838633767bb80a6dc4ac97bd70 \
  --expect-system-sha256 f9ab99aa260c60f4a28758488e363d7d400f4a9c7f2e8537fd572a974f2d5084
```

No n47 primal witness has been emitted or accepted yet. The terminal n47
quotient-lift snapshots stop before the killed-constant relation. A future
producer needs to retain enough row provenance to express that relation as a
bounded derivation. This checker supplies the independent acceptance gate; it
does not create the missing provenance or make a degree-six lower-bound claim.
