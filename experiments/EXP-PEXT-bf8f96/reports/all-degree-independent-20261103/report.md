# EXP-PEXT-bf8f96: independent all-pattern collision replay

An independent polynomial-basis checker now replays the fixed F27 all-degree collision certificate. It validates the complete 1,638-row joined software fixture, reconstructs all 819 distinct left-coset cocycles and their projective norm identities, and uses each joined matrix as an explicit Lang witness for its cocycle. For seven bound quartics it checks the monic irreducible factor product, the complete distinct root set and each K-Frobenius factor orbit in a symbolic extension. It then solves the collision kernels in Python, maps them through the independently rebuilt cocycle index, and compares rational, nonrational and union candidate sets with literal transformed-quartic support gcds. The checker uses polynomial-basis arithmetic rather than the Rust producer's logarithm arithmetic.

| Bound quartic | Factor pattern | Rational | Nonrational | Shared | Exceptional union |
|---|---:|---:|---:|---:|---:|
| Fixed split form | 1+1+1+1 | 590 | 0 | 0 | 590 |
| Fixed mixed form | 1+1+2 | 273 | 7 | 1 | 279 |
| Fixed mixed form | 1+3 | 117 | 0 | 0 | 117 |
| Fixed quadratic pair | 2+2 | 0 | 20 | 0 | 20 |
| Fixed irreducible form | 4 | 0 | 1 | 0 | 1 |
| Actual T block 0 | 1+1+2, including infinity | 273 | 7 | 1 | 279 |
| Actual T block 1 | 4 | 0 | 1 | 0 | 1 |

The independent test rejects a deleted nonrational index, an inserted union index, a root moved off the quartic and a broken factor. Source hashes, exact commands and outputs are in [software-tests.json](software-tests.json): 17 core and 19 join native tests plus one independent Python mutation test pass. These are fixed software fixtures, not the P1–P4 scientific cohorts.

The algorithmic candidate-set gate is now replayed independently at every squarefree quartic factor pattern. Before approval, production shards still need source-bound candidate receipts, literal support checks and independent nonce-sampled replay, plus a measured fit within the proposed 4 GB and 24 CPU-hour ceilings. The original cohort controls, coefficient-aware descent, Type2, H1 analysis, runbook and frozen execution packet remain to complete. EXP-PEXT-bf8f96 stays `review_required`; no scientific trial was launched.
