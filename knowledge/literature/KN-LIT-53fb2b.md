---
id: KN-LIT-53fb2b
type: literature
title: "Faster Polynomial Factorization over Finite Fields via Batched Modular Composition"
authors:
  - "Zhenyu Xiong"
  - "Mingsheng Wang"
year: 2026
venue: "IACR ePrint 2026/2625 (Oct 2026)"
identifiers:
  eprint: "iacr:2026/2625"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/2625"
tags: [polynomial-factorization, finite-fields, modular-composition, root-finding, cost-model]
confidence: reported
citation_verified: abstract
added: "2026-11-07"
superseded_by: null
---

## Contribution (as reported)
- **Factoring degree-`n` polynomials over `F_q`:** `n^{1.5532+o(1)} log q` operations in the algebraic model, against the previous `n^{1.80535+o(1)} log q` (Kaltofen–Shoup with Huang–Pan). It would be `n^{3/2+o(1)} log q` if `ω = 2`.
- **For large `q`:** `O(n^{1.5983}) + n^{1+o(1)} log q`.
- A single modular composition, Las Vegas, costs `(ω+3)/4 < 1.3429`, or 1.3309 with a fourth level.

## Read here
The abstract only (2026-11-07). The abstract does not discuss root finding.

## Relevance
- It touches the root-finding step of point decomposition (`S_{m+1}` roots over `F_{2^n}`) only asymptotically.
- Decomposition root finding needs roots, not full factorization, and runs at small degree. No cost row changes.
- A candidate only if a future cost model is dominated by high-degree univariate factorization.

Source sweep: crypto `research/lit_sweep_20261107/` (report and PDF).
