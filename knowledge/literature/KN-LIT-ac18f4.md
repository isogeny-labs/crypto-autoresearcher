---
id: KN-LIT-ac18f4
type: literature
title: "Matrix Multiplication from Polynomial Packings: A Constructive and Elementary Proof of omega <= 9/4 (integers / characteristic 0)"
authors:
  - "Rafael Pass"
year: 2026
venue: "arXiv preprint 2610.28627 (v1 20 Oct 2026; v2 30 Oct 2026)"
identifiers:
  eprint: null
  doi: null
  arxiv: "2610.28627"
  url: "https://arxiv.org/abs/2610.28627"
tags: [matrix-multiplication, omega, constructive, galactic, characteristic-0, openai-math]
confidence: reported
citation_verified: abstract
added: "2026-11-07"
superseded_by: null
---

## Contribution (as reported)
- **Theorem 1.1** (quoted): "For every γ>0, there is an explicit recursive algorithm that, for every positive integer n, multiplies two n×n integer matrices with O(n^{9/4+γ}) integer arithmetic operations. In particular, ω≤9/4."
- **Method**: it constructs an explicit Strassen-style identity from polynomial packings and applies ordinary block recursion.
- **Field coverage**: characteristic 0 only. Section 2 says it works "over a fixed field of characteristic zero" (integers, rationals, clearing denominators).
  - The paper does not address positive characteristic or GF(2^k).
- **Practicality**: the author calls the algorithm "galactic": the constants in O(·) are enormous. The exponent `9/4` is reached only as a limit over an integer parameter.

## Relevance to this program
- It is the first **constructive** route to `ω ≤ 9/4`.
- For binary-field index calculus it adds nothing beyond KN-LIT-eef882: it does not cover characteristic 2, and its constants rule out any practical crossover.
- It does not change any cost-model row.

## Limits
- Read here: the arXiv abstract and about the first 40k characters of the v2 HTML; Section 4 is known only from a summary.
- Not peer reviewed; the proof was not checked here.
