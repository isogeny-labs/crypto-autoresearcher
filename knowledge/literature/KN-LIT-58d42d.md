---
id: KN-LIT-58d42d
type: literature
title: "Matrix multiplication exponent bounds in openai/math family 107, with follow-ups: omega <= 9/4 now reported over every field"
authors:
  - "OpenAI (unnamed internal model; no human author listed)"
year: 2026
venue: "openai/math family 107 (since commit adc7f12, 2026-10-06; unchanged through 4eaee87, 2026-10-29), with follow-ups KN-LIT-eef882, KN-LIT-ac18f4, KN-LIT-d4aa5d"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://github.com/openai/math/blob/main/lean/docs/107.md"
tags: [matrix-multiplication, omega, linear-algebra, groebner, f4, characteristic-2, first-fall-degree, galactic, openai-math, unverified-proof]
confidence: reported
citation_verified: read
added: "2026-11-07"
superseded_by: null
---

This entry supersedes KN-LIT-0b036e. Only the characteristic-2 status of `9/4` changed. Everything else in that entry carries over, including its correction of an internal record.

## Bounds (as reported)
- **`ω(ℂ) ≤ 9/4`**: openai/math family 107. Lean: `complex_omega_le_nine_quarters`.
- **`ω < 2.258`**: characteristic 0, and every positive characteristic outside a finite, uncomputed set.
- **`ω(F) < 2.371054886…` for every field**: openai/math. Lean: `omega_lt_source_constant`.
- **`ω(F) ≤ 9/4` for every field, characteristic 2 included.** Two independent reports:
  - Amanov, van den Berg and Zuiddam, arXiv 2610.30054 (KN-LIT-eef882), Theorem 1.1. The paper also proves an operational barrier: the current ingredients cannot improve on `9/4`.
  - Navot, `matrix-multiplication-all-fields` (KN-LIT-d4aa5d): a Lean statement `omega_le_nine_quarters (F : Type*) [Field F]`. The README reports only the standard axioms.
- **Constructive `ω ≤ 9/4`, characteristic 0 only**: Pass, arXiv 2610.28627 (KN-LIT-ac18f4). It does not cover GF(2^k).

## Characteristic 2 (what binary-field index calculus needs)
`9/4` changes from **conditional** (KN-OPEN-57907f) to **reported** for every field. The 2026-10-07 transfer argument agrees with both reports:
- the root-of-unity step transfers;
- Appendix A's tools do not depend on the field.

What has been done here:
- Nobody here has checked either proof.
- Neither Lean artefact has been built.
- The Navot statement has not been compared with its claim.

## Relevance
- **Model only.** Under the contested first-fall-degree model:
  - `2^68.96` at `n = 131`, above both generic (`2^65.5`) and rho (`2^60.8`);
  - turning point `n = 227`, against `n = 357` at the published `ω`.

  These rows now rest on a reported every-field result, not a conditional transfer. They are still existence-only and galactic.
- **The barrier (KN-LIT-eef882).** It bounds this line of improvement at `9/4`. Do not extrapolate below it.

## Limits
- All the bounds are unverified here and asymptotic.
- No explicit identity exists over GF(2^k).
