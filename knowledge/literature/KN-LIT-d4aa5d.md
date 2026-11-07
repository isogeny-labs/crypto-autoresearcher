---
id: KN-LIT-d4aa5d
type: literature
title: "matrix-multiplication-all-fields: Lean extension of openai/math's omega <= 9/4 proof to every field (Navot)"
authors:
  - "Sela Navot (repository owner; README credits AI models working under his direction)"
year: 2026
venue: "GitHub repository selanavot/matrix-multiplication-all-fields (Zenodo 10.5281/zenodo.23219128, v1.0.0)"
identifiers:
  eprint: null
  doi: "10.5281/zenodo.23219128"
  arxiv: null
  url: "https://github.com/selanavot/matrix-multiplication-all-fields"
tags: [matrix-multiplication, omega, lean, formal, characteristic-2, openai-math, unverified-proof]
confidence: reported
citation_verified: read
added: "2026-11-07"
superseded_by: null
---

## Contribution (as reported in the README; nothing built here)
- **What it is.** A fork of the openai/math MatrixMultiplication subtree, taken at commit `adc7f12`.
- **The main theorem is generalized:**
  - from `theorem omega_le_nine_quarters : Arithmetic.omega ℂ ≤ (9 : ℝ) / 4`
  - to `theorem omega_le_nine_quarters (F : Type*) [Field F] : Arithmetic.omega F ≤ (9 : ℝ) / 4`.
- **Also stated**:
  - `exactRankExponent_le_nine_quarters_allFields`;
  - a cost theorem `matrix_multiplication_cost_le` (for every ε > 0, `C·n^{9/4+ε}`).
- **Scope.** The README says the field "may be finite or infinite, of any characteristic", so characteristic 2 is included.
- **Method.** It works over the algebraic closure and descends, using "Fourier separation in every characteristic" with period `5M` or `5M+1`.
- **Axioms.** The README says the audit admits only `propext`, `Classical.choice` and `Quot.sound`, with no `sorry`. It reports that Palomar verification passed on 2026-10-07.
- **Toolchain.** Lean v4.35.0-rc2; Mathlib commit `065356127b1d`.

## Caveats
- Over finite fields, the cost theorem's `P.Correct` is functional equality, which is weaker than polynomial identity (for example `x² = x` on F₂). The separate exact-rank theorem is the algebraic certificate.
- Non-effective: no constants and no procedure that generates the programs.
- Mostly AI-produced, per the README. It makes no priority claim.
- **Not built or audited here.** The statement-fidelity check (Comparator statement against the claim) is still open.

## Relevance
- An independent, machine-checked (as reported) route to the KN-OPEN-57907f answer, separate from the expository proof in KN-LIT-eef882.
- Checking this statement would let crypto's `matmul_exponent.rs` mark `9/4` in characteristic 2 as formalized.
