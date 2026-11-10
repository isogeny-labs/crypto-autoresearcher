# Affine STARK transition: technical proof composition — 2026-11-08

**Technical result.** The seven stated propositions about the ring expression
`a*x + b*y + c` have passing Lean machine evidence and two independent
mathematical/source-fidelity reviews that hold at that exact scope. The third
review holds for the native type, axiom, and negative-control subchecks but was
inconclusive for installed-dependency cleanliness and an independent kernel
recheck. A later hosted run supplies clean pre/post dependency revisions for
unchanged theorem bytes. No independent kernel rechecker was available. This
packet records **passing machine evidence and independently supported scoped
ring-expression fidelity**. The complete technical-review outcome remains
**inconclusive** until J3's remaining trust boundary is independently closed;
the Rust execution and STARK protocol bridges remain open. It does not change
the frozen target or any scientific ledger decision.

## Bound inputs and review sequence

- Producer claim: [`CLAIMS.md`](../../CLAIMS.md), seven numbered propositions.
  The source labels its seventh-declaration validation as pending; this
  composition is an additive later assessment, not an edit of that record.
- Theorem module: `formal/CryptoResearch/Stark/AffineTransition.lean`, SHA-256
  `3311451f0dfa19c9c696b872bb3b85d0ed60e68a75c89c871052cbd39dadfa0d`.
  The registered target is `three_probe_extensionality`; the other six named
  theorems were checked through the source-module build and printed axioms.
- The precommitted [review plan](../review-plan.json) has SHA-256
  `a94fcf87975f2998e3600135984f8b50c25d5873b97b02ee8b3915e2c79320cc`.
  The three original reports remain in their separate `reviews/TASK-*`
  directories. The normalized independence check records `PASS: 3 report(s),
  every joint owned and attested, blindness respected, controls declared`.
- J1 blind derivation (`TASK-20261030-44bc06`, SHA-256 `a57c555b5989c577372773d612ede4dc73ccb4455c8dee32f10501ac5758f938`)
  holds the seven ring statements, including missing-probe and zero-ring
  countermodels. J2 source/type review (`TASK-20261030-2fb4bd`, SHA-256
  `bc153e5e06a0b1a2e2a1ced46d48adab9907e2f41c28d65943e43ded14f4bd34`)
  holds exact claim fidelity. J3 native-boundary review (`TASK-20261030-2b2947`,
  SHA-256 `7bd02a7f7c7f39836e77fd323b0372063b1c7539d138f10b4a4f3c281c658bd6`)
  confirms seven built declarations, actual types/axioms, and both nontriviality
  rejection controls; its complete-boundary verdict was inconclusive.

The fresh hosted source-module run 41109712394 supplied the seven elaborated
types, axiom prints and controls to the reviewers. Later [hosted run
42423957020](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42423957020)
completed the full workspace build and axiom audit. Its registered target
receipt (SHA-256 `1a7b2c3ec250bb046dd3dbce86d44c8af30f79fdd38507c458e80cf12deb75bb`)
reports `machine_verified`, the exact theorem-source SHA above, a named target
axiom-audit pass, and semantic-review status `pending`. Its pre/post dependency
pin receipts are byte-identical (each SHA-256
`bfff6e66739c2f8e745910110cc91ff90d7162871492b0a46fc67a40320b2221`)
and report clean installed source revisions. The artifact-wide audit on
[PR #3170](https://github.com/isogeny-labs/crypto-autoresearcher/pull/3170)
matched these formal and verifier inputs to current `main` at
`4239648a889fe97d976a99862d178ba50324dc6e`; that PR is separate and
its merge state is not evidence for this result.

## Per-claim composition

| Claim | Lean declaration | Mathematical and fidelity evidence | Machine evidence |
| --- | --- | --- | --- |
| Coefficients recover from three probes | `recover_coefficients` | J1 holds; J2 exact tuple and probe order | Built; type and axioms printed |
| Equal probes imply equal triples | `coefficients_eq_of_probes` | J1/J2 hold over any commutative ring | Built; type and axioms printed |
| Equal probes imply equal values everywhere | `three_probe_extensionality` | J1/J2 hold, no field or nontriviality assumption | Registered target machine verified |
| Multiplication is not globally affine | `multiplication_not_affine` | J1/J2 hold with nontriviality | Built; zero-ring application rejected |
| Two probes can be insufficient | `two_probes_insufficient` | J1/J2 hold with explicit witnesses | Built; type and axioms printed |
| Zero-ring exception | `zero_ring_product_control` | J1/J2 hold for `ZMod 1` | Built; type and axioms printed |
| Four designated probes obstruct multiplication | `multiplication_not_affine_on_four_probes` | J1/J2 hold with nontriviality and exact four-point conjunction | Built; zero-ring application rejected |

The seven mathematical propositions have independent **faithful_scoped**
support and passing named/source-module machine evidence. The technical-review
outcome is **inconclusive** for J3's complete verification boundary; the
Rust implementation, fingerprint, and security claim is also **inconclusive**
on this packet. The latest `crypto` main was
`73d046ea68df459af9fa02c132cb0172024aa73d`; its 1,035-byte
`AffineTransition` definition/evaluation block is byte-identical to the
producer's cited `8ce2800fbe3d265027e2341ec193ad69b946a8bd` source
(SHA-256 `ec1035ff7980da46be06338239144e62a27885623a8d20b23a79b426f6060bcc`).
Other parts of `stark_v2.rs` changed, so this check does not extend the proof
to the current full protocol implementation.

## Open bridges and controls

The theorem models ring operations, not Rust `BigUint` arithmetic, modular
reduction, byte serialization, AIR fingerprint injectivity, transcript
binding, FRI soundness, zero knowledge, or end-to-end STARK security. The
four-point and zero-ring controls establish the precise algebraic boundary.
No local `lean4checker` or `nanoda` was installed, so an independent kernel
recheck remains open; dependency binaries still carry ordinary Lean/Lake
trust. The source document and frozen target retain their historical labels.

No performance result was added. The dashboard and performance graph inputs
were checked for this composition's scope and require no value change. The
diagram below shows the proved path and the unproved implementation bridge.

![Proof boundary](boundary.svg)

The companion `report.pdf` was rendered from `report.typ` and inspected.
