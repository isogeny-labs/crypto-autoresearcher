# Endosweep batch 7 primality and named-curve bridge

- **Status:** `open`
- **Kind:** proof gap, historical evidence-custody gap, and source-input enforcement gap
- **Affected work:** [batch 7 target](../formal/targets/endosweep-dk-exact-batch7-discriminants.yaml), [Lean certificate](../formal/CryptoResearch/Endosweep/DkExactBatch7.lean), [source results](../research/endosweep_dk_exact_batch7_20261106/README.md), [independent technical review](../docs/reports/2026-11-07-endosweep-b7-fidelity/README.md), archival task T-1739
- **Next action owner:** formal research lane for certificates and curve bridge; Endosweep source maintainer for pin enforcement; Coordinator for additive target wording correction
- **Last updated:** 2026-11-07

## Problem

For brainpool/brainpoolP512r1, the named Lean theorem proves exact identities for recorded integers and makes the fundamental-discriminant result conditional on two large factors being prime. It does not discharge that premise or prove that the recorded `t` is the curve's actual Frobenius trace, that its endomorphism ring is the asserted quadratic order, or that endomorphism degree equals the arithmetic norm. Those missing links prevent the recorded-integer certificate from being an end-to-end theorem about the named curve.

## Evidence and uncertainty

- **Observed:** Hosted [run 42260198392](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42260198392) gives a named machine receipt and axiom audit; exact target/source hashes match the 2026-11-07 review base. The [blind review](../docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/report.md) independently reproduces the arithmetic and demonstrates by a composite-base counterexample that factor multiplication does not imply fundamentality.
- **Observed:** The [source review](../docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/source/report.md) passes 53 source checks and all 13 data hashes, confirms byte-identical Lean generation and upstream parameter matching, but finds no retained certificate or authenticated receipt for the archived PARI primality assertion. `build_dk_exact.py` records the std-curves revision without enforcing the pin or clean input bytes; the particular saved numbers match a fresh immutable upstream read.
- **Derived or proved:** The Lean statement's implication is correctly conditional on `IsPrimeNat` for the two large bases. The recorded integer equalities and degree bound hold at their explicit numeric scope. The target notes' unconditional “squarefree part” phrase overstates that scope; the target claim and Lean header are conditional.
- **Suspected explanation:** No assertion of false primality or wrong curve data is made. The missing historical proof receipt may be a custody omission; the curve bridge is an unformalized dependency.
- **Missing capability:** A retained, independently checkable primality certificate for each large factor, enforced source input pinning for future generation, and a theorem or checkable derivation binding actual named-curve trace, order and degree to the numeric certificate.
- **What this evidence does not establish:** Neither a broken factorization nor an invalid named curve has been shown. A lack of local PARI replay is an evidence limit, not a compositeness result.

## What would unblock it

- [ ] Obtain independent, checkable prime certificates for the two exact large factors in the target and verify both against their decimal integers; retain source/tool/pin and verification receipts. A Lean proof of the exact `IsPrimeNat` premises would discharge the theorem's conditional hypothesis.
- [ ] Bind brainpoolP512r1 parameters to an immutable curve definition and prove or independently certify its field/order/trace facts, including the assumptions used by the trace check.
- [ ] Formalize or cite with an exact instantiation the bridge from the curve's Frobenius/order to `End(E)` and from endomorphism degree to the quadratic norm; compare the instantiated discriminant and conductor to the recorded integers.
- [ ] For future generated records, enforce the declared std-curves revision and clean/content-hashed input bytes; create an additive corrected target for the unconditional squarefree wording and rerun its named proof gate.

The first condition would establish fundamental discriminant for the recorded integers, not the named curve's trace. The later curve and order conditions are needed for the end-to-end named-curve conclusion.

## Next discriminating step

- **Action or proof obligation:** Produce and independently verify a certificate for the 54-digit factor first, using its exact integer from the target; then apply the same method to the 98-digit factor. Keep prime certification separate from the curve bridge.
- **Inputs and controls:** Exact factor integers and product from the pinned target; known prime 557 as positive control and a same-size composite obtained by multiplying a small known factor as negative control. Require exact identity checks and a checker that rejects altered certificates.
- **Execution limits and stop condition:** No new cloud experiment is authorized by this record. Any substantial computation needs its own finite budget, exclusive ownership and published inputs under the existing cost policy. Stop on an unverified factor, missing certificate, or resource gate.
- **Outcomes and next actions:** Valid certificates discharge the numeric primality premise; a composite factor requires an additive factorization/source correction and fresh Lean target; an inconclusive or resource-limited attempt leaves the premise open. None of these alone proves the curve bridge.
- **Recheck trigger:** A new prime certificate, a revised source builder, or a concrete curve-to-order theorem and review packet.

A planned step is not a completed experiment. Apply the existing execution, review, budget, and archival rules before acting on it.
