# Review plan: Endosweep batch 7 discriminant certificate

Status: prereview plan, recorded before independent reviewer work. Base Git commit: `23c5aeca09f8f512d90755193660c1b2aa509714`. Target: `formal/targets/endosweep-dk-exact-batch7-discriminants.yaml`; declaration: `CryptoResearch.Endosweep.DkExactBatch7.exact_discriminants` in `formal/CryptoResearch/Endosweep/DkExactBatch7.lean`. Producer claim: the target's `claim` field, with its one named brainpool curve, exact integer equalities, degree bound, and conditional fundamentality. Source: `research/endosweep_dk_exact_batch7_20261106/README.md`, `dk_exact.json`, `factorizations.jsonl`, and the generator named in the target.

## Prior and boundaries

Prior: the integer identities likely hold because the checked source and Lean constants were generator linked, but that shared generator is not independent evidence. The theorem may faithfully state an arithmetic certificate while the link to the named elliptic curve's trace and endomorphism ring remains external. The large-factor primality and source identity require separate checks. No verdict is assigned by this plan.

## Joints and adversarial checks

| Joint | Owner | Worked attack or countercheck |
| --- | --- | --- |
| Source custody and code-to-record mapping | Source reviewer | Compare committed `dk_exact.json`, `factorizations.jsonl`, `SHA256SUMS`, snapshot, generator, and Lean constants. Look for a swapped curve, copied `t`, stale source revision, or a factor record that multiplies back but has no trustworthy primality evidence. |
| Independent integer derivation | Blind reviewer | From the raw integers and definitions in `blind-input.md` alone, recompute `q+1-t`, `4q-t²`, factor product, squarefree candidate, `D_K`, and degree floor/bounds. Try a one-digit factor mutation and a composite-in-place-of-prime counterexample to distinguish an identity from a primality proof. |
| Formal statement and proof gate | Coordinator | Expand `DkCert.Statement` and imports; compare every conjunct, conditional hypothesis and quantifier with the target. Bind the exact hosted run and verify that it compiles this named module and audits its named theorem. Probe a wrong declaration name or changed input through a fresh isolated control when capacity permits. |
| Curve and endomorphism interpretation | Coordinator | Identify a theorem or record proving the stated `t` is the named curve's actual Frobenius trace and that the arithmetic order is `End(E)` with degree equal to norm. If absent, mark the bridge open rather than granting it from integer arithmetic. |

The known-false nearby case is a list containing a composite odd-exponent factor while retaining the same product. The factor-product identity can still hold; unconditional fundamentality should not follow. The empty curve list is another proves-too-much case: a universal statement over it is vacuous, so the named list length and member identity must be checked.

## Isolation and handoffs

The source reviewer may read the producer files, target, Lean source, and generator, but must not read the blind report before filing its own. The blind reviewer may read only `blind-input.md` and standard mathematical references or scratch calculations; it must not read the producer README, target, Lean source, generator, receipts, sibling report, or this plan's expected-boundary paragraph. Each reviewer records all paths read, a `holds | breaks | inconclusive` result for its owned joints, and any deviations. The Coordinator reads both only after they are filed and checks source/claim fidelity, machine evidence and independence separately. Any scientific decision or claim promotion requires the repository's additional Coordinator route; this technical packet changes no hypothesis status.
