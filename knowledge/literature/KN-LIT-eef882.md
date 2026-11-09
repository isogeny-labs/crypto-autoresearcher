---
id: KN-LIT-eef882
type: literature
title: "Multiplying matrices via polynomials: exposition and barriers (omega_F <= 9/4 over every field; operational barrier)"
authors:
  - "Alimzhan Amanov"
  - "Maxim van den Berg"
  - "Jeroen Zuiddam"
year: 2026
venue: "arXiv preprint 2610.30054 (v1, 21 Oct 2026; cs.CC, math.RA, math.RT)"
identifiers:
  eprint: null
  doi: null
  arxiv: "2610.30054"
  url: "https://arxiv.org/abs/2610.30054"
tags: [matrix-multiplication, omega, characteristic-2, asymptotic-spectrum, barrier, groebner, cost-model, openai-math]
confidence: reported
citation_verified: abstract
added: "2026-11-07"
superseded_by: null
---

## Contribution (as reported)
- **Theorem 1.1** (quoted from the HTML introduction): "For every field 𝔽, ω𝔽≤9/4."
  - The abstract says: "Our version of the proof gives ω𝔽≤9/4 over every field 𝔽."
  - The paper is an exposition of the openai/math family-107 argument (`ω(ℂ) ≤ 9/4`), reworked so that it holds in every characteristic.
- **Theorem 1.2**: rectangular bounds over every field: `ω(1,k,1) = 2` for `0 ≤ k ≤ 1/2`, and a closed form for `ω(a,b,c)`.
- **Operational barrier** (Theorem 5.4). The abstract says it shows that "the current degeneration ingredients cannot improve the bounds".
- **Method**: existential, through Strassen's asymptotic-spectrum duality. A secondary summary reports a positive-characteristic workaround (subspace/quotient, because Clebsch–Gordan fails there) and a field-size case split in Lemma 3.3.

## What was read
- **Read here**: the arXiv abstract page and about the first 40k characters of the v1 HTML (2026-11-07).
- **Not read**: Theorem 5.4 and the positive-characteristic sections (the middle and end of the HTML). They are known here only from a summary.
- No proof was checked here.

## Relevance to this program
- **Answers KN-OPEN-57907f** (does ω ≤ 9/4 hold over GF(2^k)?): yes, as reported. KN-OPEN-57907f is superseded by this entry.
- **Cost model.** The characteristic-2 summation-polynomial rows at `ω = 9/4` were "conditional" in crypto's `matmul_exponent.rs` and in the 2026-10-07 and 2026-10-26 literature-note addenda. They now rest on a published-preprint claim. They are still existence-only (galactic), and they still assume the contested first-fall-degree model:
  - `2^68.96` at `n = 131`, above both rho (`2^60.8`) and generic (`2^65.5`);
  - turning point `n = 227`.
- **Barrier.** Under these ingredients, 9/4 is the floor of this line of improvement. A cost model must not extrapolate a further drop in `ω` from it.
- **Missed earlier.** This preprint (21 Oct) predates the 2026-10-26 review, which missed it.

## Limits
- Not peer reviewed; the proof was not checked here.
- Asymptotic arithmetic complexity only: no explicit identity, no constants, no crossover point.
