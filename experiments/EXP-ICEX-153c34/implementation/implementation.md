# EXP-ICEX-153c34 implementation note

Task `TASK-20261001-4862b6` is limited to frozen S0 gates G0-1 through G0-6.
The implementation contains:

* an exact panel generator and an independent Sage byte reproducer;
* independent Bareiss/subset-DP polynomial checks and deterministic smoke,
  power-reproduction, and counter-check workers;
* the D-2 monomial-basis pseudo-resultant, deterministic lex Buchberger,
  recursive gcd/specialisation root extraction, and signed point recovery;
* a fail-closed S0 orchestrator with pinned inputs, C-7 checks, one-worker
  execution, `nice >= 10`, and an 8 GiB address-space ceiling; and
* an explicitly selected Modal Sage-verifier backend pinned to the linux/amd64
  manifest
  `sagemath/sagemath@sha256:4562582e9da21605ce1507932effb548d44888ed9e35ec768616049e6776391d`.
  It sends only a hash-manifested per-call bundle, blocks worker networking,
  enforces one CPU/8 GiB/one single-use container/no retries, and returns exact
  stdout and stderr bytes in the receipt. Modal is never an automatic fallback.

The G1 decision path has no direct Cartesian/grid `V^5` membership substitute
and cannot receive the O5 oracle. The frozen recursive extractor still retains
every `V` candidate when all collected polynomials vanish; such legal branches
can degenerate to `|V|^5` full assignments, are verified against the original
generators, and are charged in `X`. Its only explicit Cartesian product is the
required `2^5` signed-recovery check. S0 retains all verified decompositions,
as required before the frozen D-5 B0-hit-order selection; negative membership
exhausts the algebraic roots.

This static snapshot has not executed Modal or any S0 gate. All six gates remain
blocked pending an immutable implementation commit and an authorized launch
whose local C-7 reading passes. The earlier non-protocol L=3 development probe
was manually terminated after 34 seconds, emitted no result, and is not gate
evidence. No scientific interpretation is made.
