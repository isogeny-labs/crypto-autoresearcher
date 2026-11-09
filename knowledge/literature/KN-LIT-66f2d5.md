---
id: KN-LIT-66f2d5
type: literature
title: "Polynomial Separation of a Shared Tensor Leg and Matrix Multiplication in Arbitrary Characteristic"
authors:
  - "Houxi Lü"
year: 2026
venue: "arXiv preprint 2610.18914 (v1, 12 Oct 2026; cs.CC)"
identifiers:
  eprint: null
  doi: null
  arxiv: "2610.18914"
  url: "https://arxiv.org/abs/2610.18914"
tags: [matrix-multiplication, omega, characteristic-2, separation, openai-math]
confidence: reported
citation_verified: read
added: "2026-11-07"
superseded_by: null
---

## Contribution (as reported)
- **Cheaper shared-leg separation.** Improves Proposition 3.1 of OpenAI's 9/4 preprint: copies drop from `5M` to `2M-1` (with `n = M`). It works over any field with at least `M+n-1` elements and needs no roots of unity or factorial denominators.
- **Corollary 4.1**, quoted: "For every algebraically closed field K, the matrix multiplication exponent satisfies ωK≤9/4." The paper adds: "no characteristic needs to be excluded."
- It does not improve on `9/4`: "By itself it does not give a strict improvement below 9/4."

## Read here
The abstract and the HTML v1.

## Relevance
- **A third reported route to `ω ≤ 9/4` in characteristic 2,** besides KN-LIT-eef882 and KN-LIT-d4aa5d. Corollary 4.1 covers every algebraically closed field; since `ω` depends only on the characteristic (a standard fact), this covers `GF(2^k)`. That last step is derived here, not stated in the paper.
- Adds evidence to KN-LIT-58d42d without changing it. No cost-model number changes.

Source sweep: crypto `research/lit_sweep_20261107/` (report and PDF).
