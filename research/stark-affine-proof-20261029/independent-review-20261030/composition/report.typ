#set page(paper: "a4", margin: 17mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.55em)

= Affine STARK transition: technical proof composition

*Pinned review:* 2026-11-08. *Producer source:* `CLAIMS.md` and Lean module
`formal/CryptoResearch/Stark/AffineTransition.lean` (SHA-256
`3311451f0dfa19c9c696b872bb3b85d0ed60e68a75c89c871052cbd39dadfa0d`).

*Scoped result:* Seven ring-expression propositions are supported by passing
Lean machine evidence, independent blind derivation, and independent
source/type review. The native reviewer confirmed seven built declarations,
their types and axioms, and two nontriviality controls. The complete technical
outcome remains `inconclusive` pending independent closure of J3's trust
boundary. The Rust implementation and STARK protocol bridges remain open.

#figure(image("boundary.svg", width: 100%), caption: [Solid arrow: the
reviewed ring-expression proof. Dashed arrow: unproved implementation and
security bridges.])

== Review and machine evidence

The precommitted plan assigned J1 blind algebra, J2 source/type fidelity, and
J3 machine-boundary review to three separate reviewers. The normalized
independence check passed for all three reports and attestations. J1 and J2
hold all seven numbered claims. J3 holds the type, axiom, and boundary-control
subchecks; its full-boundary verdict was inconclusive because the older run
did not prove installed dependency cleanliness or supply an independent
kernel recheck.

Hosted run 41109712394 built the seven-declaration module and retained types,
axiom prints and zero-ring rejection controls. Hosted run 42423957020 later
built the same theorem bytes within the full workspace and gave a
`machine_verified` receipt for the registered `three_probe_extensionality`
target. Its identical pre/post dependency-pin receipts report clean installed
revisions. An artifact-wide audit matched formal and verifier input bytes to
crypto-autoresearcher main `4239648a889fe97d976a99862d178ba50324dc6e`.
No independent `lean4checker` or `nanoda` result is claimed.

== Claim map

1. `recover_coefficients`: three evaluations recover the tuple `(a,b,c)`.
2. `coefficients_eq_of_probes`: equal values at the three probes force equal coefficients.
3. `three_probe_extensionality`: equal probes force equal values at all pairs.
4. `multiplication_not_affine`: in a nontrivial ring, multiplication is not globally affine.
5. `two_probes_insufficient`: omitting the third probe admits distinct transitions.
6. `zero_ring_product_control`: the zero ring is the required exception.
7. `multiplication_not_affine_on_four_probes`: in a nontrivial ring, the four designated product equalities cannot all hold.

Claims 1–3 need only a commutative ring; claims 4, 5 and 7 add
nontriviality. Claim 6 uses `ZMod 1`. The explicit four-point control avoids
mistaking global nonagreement for a finite-point statement.

== Current source and limits

The current crypto main at `73d046ea68df459af9fa02c132cb0172024aa73d`
retains the exact 1,035-byte `AffineTransition` definition/evaluation block
from producer revision `8ce2800fbe3d265027e2341ec193ad69b946a8bd`:
SHA-256 `ec1035ff7980da46be06338239144e62a27885623a8d20b23a79b426f6060bcc`.
Other parts of `stark_v2.rs` changed. The proof does not certify Rust BigUint
arithmetic, modular reduction, serialization, AIR fingerprint injectivity,
Fiat–Shamir binding, FRI soundness, zero knowledge, or end-to-end security.
The frozen target and scientific ledger are not changed. No new measurement
or dashboard value follows from this composition.

The complete source-linked evidence table, reviewer SHA-256 values, receipt
hashes and remaining obligations are in the sibling `report.md`.
