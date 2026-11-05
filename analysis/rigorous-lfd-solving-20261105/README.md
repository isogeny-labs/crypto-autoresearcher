# Rigorous last-fall and solving-degree bounds

2026-11-05. Follow-up to the owner's request for full binary formalization and
fixed-degree growing-family lower bounds. The prime digit growth theorem is
proved here in writing and has a fresh independent mathematical review;
formal coverage is stated separately. No official scientific status changed.

- [The exact prime theorem and full proof](THEOREM.md): for two s-bit blocks,
  s>=2, prime p>=2^s, nonsingular short Weierstrass curve and any target,
  `4+floor(s/2)<=d_F<=sd_sigma(F)<=2s+1` for degree-compatible sigma.
  Raw and normalized S3 are both covered with explicit bit equations.
  There are actual rational-target SAT and UNSAT families for every width.
- [General and binary bounds](BOUNDS.md): generic Boolean N+1 upper bound,
  full normalization bridge in writing, and support-aware proof of binary
  UNSAT `d_F=sd<=3ell+1` for the exact two-S3 chain presentation.
- [Independent prime review](prime-independent-review.md): blind derivation,
  elementary inclusion-rank induction, five false-claim controls, frozen
  proof audit and declared supplemental consistency check.
- [Formal coverage and verification](formal-status.md): exact new Lean
  statements, pins, builds, axiom audits and target receipts.
- [Report PDF](report.pdf), [editable report](report.typ), [diagram source](diagram.dot)
  and [vector diagram](diagram.svg).
- [Remaining binary obligations](problems/remaining-binary-obligations.md):
  complete instantiated support/localization formalization and unbounded
  characteristic-two lower bound. Neither is claimed completed.

The non-bit input degree stays four as s grows. The lower bound is a full
iterated-closure bound, including SAT missing consequences, not a first-fall
measurement. It covers this exact F_p-coefficient digit presentation, not a
GF(2) carry circuit or a presentation with extra chain/membership constraints.

Lean: `formal/CryptoResearch/FallDegree/{BooleanNormalization,BinarySemaevShape}.lean`.
All failed and successful proof-construction logs remain in this directory
and `validation/`. Run the scoped builds from `formal/`:

```sh
lake build +CryptoResearch.FallDegree.BooleanNormalization
lake build +CryptoResearch.FallDegree.BinarySemaevShape
```

Frozen target specs are `formal/targets/{boolean-normalization-repair,
boolean-lastfall-upper,binary-semaev-repair}-20261105.yaml`. Their exact
receipts are in `validation/`. The generic normalizer and last-fall upper
bound are not a Lean formalization of the prime growth or solving-degree
sandwich. The binary S3-shape module is not the full binary 3ell+1 theorem.

Historical input `PRIME-PROOF.md` and `CLAIM.md` retain their candidate
wording because they were frozen before independent review. THEOREM.md is
the consolidated proof; review bindings retain the original input hashes.
