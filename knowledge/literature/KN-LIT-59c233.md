---
id: KN-LIT-59c233
type: literature
title: "Lowered crossover points of Anthropic's subexponential 3-SAT algorithm"
authors:
  - "Ruhollah Majdoddin"
year: 2026
venue: "arXiv preprint 2610.41622 (v1, 30 Oct 2026; 56 pages)"
identifiers:
  eprint: null
  doi: null
  arxiv: "2610.41622"
  url: "https://arxiv.org/abs/2610.41622"
tags: [sat, eth, counting, crossover, galactic, anthropic, openai-math]
confidence: reported
citation_verified: read
added: "2026-11-07"
superseded_by: null
---

## Contribution (as reported)
- **Anthropic's algorithm.** A #3-SAT counting recursion built on a clique-sum (tensor contraction). Running time `2^{O(km/√log m)}` in clauses, or `2^{O(k² n loglog n/√log n)}` in variables. The paper cites it as "[1]"; the reference list was not read.
- **Lowered crossover points** (abstract):
  - clause density 1: about `2^420` clauses, down from `2^33858` (the body states proved thresholds of `2^417` and `2^10766`);
  - general 3-SAT: `2^(8.6·10^9)` variables, down from `2^(2.2·10^12)`;
  - Sparse Max-3-SAT: about `2^1016` clauses.
- **OpenAI's algorithm for comparison:** about `2^(4.4·10^10)` clauses at density 1 (Appendix D route); the main-text route needs at least `2^(1.09·10^10)` variables.

## Read here
The abstract and the HTML, except its final 68.6k characters. The middle section is known only from a summary.

## Relevance
- A second subexponential #SAT algorithm, with stated crossovers. Every one is far beyond the size of SAT or point-decomposition instances.
- **`LEAD-ICB-decomposition-encoding-and-sat`:** unchanged. Complements KN-LIT-caa51d.

Source sweep: crypto `research/lit_sweep_20261107/` (report and PDF).
