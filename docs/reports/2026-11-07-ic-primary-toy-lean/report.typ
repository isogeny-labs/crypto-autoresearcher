#set page(paper: "a4", margin: (x: 17mm, y: 17mm))
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.5em)
#set heading(numbering: none)

= Primary n=13 IC toy-curve certificate
Technical review · 2026-11-07 UTC · Claim IC-PRIMARY-N13-ENCODED-SCALARS-20261107

The exact Lean 4.35.0 declaration checks three archived scalar-to-point
equalities in a separately defined 13-bit arithmetic model. The source-fidelity
review and independent arithmetic calculation agree with those finite values.

#table(
  columns: (1fr, 1.5fr, 1.5fr),
  inset: 6pt,
  [Scalar], [Computed encoded point], [Workload],
  [1046], [(2659, 1282)], [`026858681e66`],
  [606], [(6749, 6034)], [`398002869ca3`],
  [861], [(4412, 6211)], [`aa4b90819f2f`],
)

The theorem also checks the modulus mask 8231, generator curve membership,
`scale 2003 G = none`, three adjacent-scalar inequalities, and an altered
coordinate that fails the encoded curve equation. The exact direct Lean run
exited 0; axiom printing for the certificate and its helpers lists only the
standard Lean axiom `propext`. The hosted full workspace gate remains a merge
requirement.

#image("proof-flow.svg", width: 100%)

Source: cryptanalysis commit `612427ead3d47565b92da3e663739d5c17ce71ed`,
archived primary JSONL SHA-256 `3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973`.
Proof-input commit `83d750c7a0`; exact source-to-theorem mapping and workload
hashes are in `source.md` and `reviews/fidelity.md`.

#pagebreak()
= Review and claim boundary

The independent source-fidelity report found the statement faithful to the
fixed encoded computation. The independently coded algebra report reproduced
the points and controls; it also checked all nonzero field encodings against
the inversion exponent. The first algebra reviewer read more of the original
Markdown plan than its intended allowance, including a favorable prior.
`blind_addendum.md` records that protocol deviation and freezes a new input
without target outputs for a further result-blind computation. That third
review independently computed all ten requested multiples by repeated
addition and binary double-and-add; after its report was frozen, comparison
found agreement on all three targets and adjacent controls. The altered
point residual was 2658. Its file is `reviews/strict-blind.md`, SHA-256
`3e64d272a1106128872ec657e6b5350223fb00a18e39cc2295f3bc717c5a3833`.
Conductor T-1868 later displayed `cancelled` after claim release; its
frozen report remains the technical record.

The precommitted plan and reports are Markdown. The repository independence
checker expects YAML plan and attestation blocks with `TASK-*` IDs, whereas
the actual Conductor IDs are `T-*`; its run returned exit 2 with
`no review_plan block`. This round retains the original files and read lists
for manual inspection and does not claim a passing machine independence check.

*Verified finite statement:* fixed encoded arithmetic equalities and negative
controls, with pinned Lean compilation, source-fidelity review and a
result-blind independent computation. Machine status is `passed` locally;
fidelity is `faithful_scoped`; review outcome is `validated_scoped` for the
finite computation. Hosted workspace CI is still a publication gate.

*Separate obligations:* a Lean proof of field irreducibility and generic point
group law, exact order, equivalence to the cryptanalysis implementation, and
independent authentication of historical execution and timing. None follows
from the finite certificate.

Detailed commands, hashes, receipts and review attestations are in
`machine-check.json`, `source.md`, `review_plan.md`, `blind_addendum.md`,
and `reviews/` beside this PDF.
