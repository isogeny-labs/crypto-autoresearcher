---
id: KN-LIT-1bd12c
type: literature
title: "Limits and Constants of OpenAI's Claimed ETH Refutation"
authors:
  - "Fabio Dias"
  - "Yvens Lima"
year: 2026
venue: "arXiv preprint 2611.00517 (v1, 31 Oct 2026)"
identifiers:
  eprint: null
  doi: null
  arxiv: "2611.00517"
  url: "https://arxiv.org/abs/2611.00517"
tags: [sat, eth, counting, constants, crossover, galactic, openai-math]
confidence: reported
citation_verified: read
added: "2026-11-07"
superseded_by: null
---

## Contribution (as reported)
- The paper treats the unstated constant `C` in OpenAI's #k-SAT counting bound as a parameter. The OpenAI preprint "states no constants".
- **Crossover against brute force `2^n`** (abstract): `n ≈ 10^32` for `C = 2`, `10^126` for `C = 3`, and `10^3517` for `C = 10`.
- **Tensor-contraction route.** No speed-up unless `log2(n+m) > 10^9` at bounded density. For random 3-CNF at the threshold it needs `log2 n > 5.3·10^11` (Prop. 4.1, with `C ≈ 6·10^5`).
- The authors do not assess correctness: "We take the preprint's proofs at face value".

## Read here
The arXiv abstract and about the first 40k of 133k characters of the HTML (2026-11-07). The rest is known only from a summary.

## Relevance
- **Corroborates KN-LIT-caa51d.** That entry's galactic verdict rested on our own estimate with `C = 1` against PPSZ. These are published constants against brute force, all far above the size of practical SAT or point-decomposition instances.
- **`LEAD-ICB-decomposition-encoding-and-sat`:** does not meet `revisit_when`.
- Figure: crypto `research/lit_sweep_20261107/figures/crossovers.svg`.

Source sweep: crypto `research/lit_sweep_20261107/` (report and PDF).
