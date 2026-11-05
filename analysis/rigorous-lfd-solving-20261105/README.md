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
- [Complete raw binary formalization](BINARY-FORMAL.md): the actual raw
  coefficient projections of the two-S3 chain and optional guard satisfy
  LFD<=3ell+1 on Boolean UNSAT, without supplied localized rows or refutations.
  [Generic core review](binary-localization/review.md) and
  [raw-instantiation review](coefficient-descent/review.md) have separate joints.
- [Formal coverage and verification](formal-status.md): exact new Lean
  statements, pins, builds, axiom audits and target receipts.
- [Report PDF](report.pdf), [editable report](report.typ), [diagram source](diagram.dot)
  and [vector diagram](diagram.svg).
- [Remaining binary obligations](problems/remaining-binary-obligations.md):
  unbounded characteristic-two lower bound and full prime growth Lean proof.
  These remain open.

The non-bit input degree stays four as s grows. The lower bound is a full
iterated-closure bound, including SAT missing consequences, not a first-fall
measurement. It covers this exact F_p-coefficient digit presentation, not a
GF(2) carry circuit or a presentation with extra chain/membership constraints.

Lean modules live in `formal/CryptoResearch/FallDegree/`; see formal-status.md.
All failed and successful proof-construction logs remain in this directory
and `validation/`. Run the scoped builds from `formal/`:

```sh
lake build +CryptoResearch.FallDegree.BooleanNormalization
lake build +CryptoResearch.FallDegree.BinaryCoefficientDescent
```

Frozen target specs under formal/targets/ include the original repair/upper
and S3-shape targets plus binary-supported-affine-lastfall-20261105.yaml and
binary-raw-chain-lastfall-20261105.yaml. Standard broader receipts and scoped
check evidence are in validation/; their different outcomes are explicit. The prime growth and solving-degree comparison remain written mathematics.
The final binary raw-chain LFD theorem is instantiated in
BinaryCoefficientDescent.lean; the separate shape module is only one component.
Full-workspace standard verification did not pass because an old rank
certificate was killed by OOM (16GiB, exit137); this is preserved in
validation/workspace-resource-failure.json. Scoped proof checks pass.

Historical input `PRIME-PROOF.md` and `CLAIM.md` retain their candidate
wording because they were frozen before independent review. THEOREM.md is
the consolidated proof; review bindings retain the original input hashes.
