# EXP-ICEX-153c34 implementation note

Task `TASK-20261001-4862b6` is limited to frozen S0 gates G0-1 through G0-6.
The implementation contains:

* an exact panel generator and an independent Sage byte reproducer;
* independent Bareiss/subset-DP polynomial checks and deterministic smoke,
  power-reproduction, and counter-check workers; G0-3 evaluates the actual
  D-2 implementation and an independent full-slot determinant on all 52,000
  preregistered tuples;
* the D-2 monomial-basis pseudo-resultant, deterministic lex Buchberger,
  recursive gcd/specialisation root extraction, and signed point recovery;
* a fail-closed S0 orchestrator with pinned inputs, C-7 checks, one-worker
  execution, `nice >= 10`, and an 8 GiB address-space ceiling. Before any gate,
  it recomputes the exact 12-file Python-source manifest, compares every file
  with the audited implementation report and its immutable source commit, and
  rejects missing, extra, changed, or commit-unbound sources. Every native
  abnormal path sends TERM and then KILL to the fresh process group, attempts
  to reap the leader, confirms the group is gone, and globally stops later
  gates when that confirmation is unavailable;
* a standalone G0-6 semantic reference which imports neither `g1_s0.py` nor
  its operation-site registry. It independently derives the fixture and all
  20 targets, rebuilds P_setup, implements D-2, Buchberger, recursive roots,
  and signed recovery, and compares setup state, arithmetic outputs, and raw
  primitive totals. Producer events are only an auxiliary site-contract and
  receipt-consistency claim. Offline regressions cover all 60 sites / 63
  site-component pairs and reject a coherent missing-charge forgery that
  preserves arithmetic. P_setup includes coefficient specialization,
  indicator reduction, pair products, and factor-base lift square roots in
  the same C-3 multiplication units; and
* an explicitly selected Modal Sage-verifier backend pinned to the linux/amd64
  manifest
  `sagemath/sagemath@sha256:4562582e9da21605ce1507932effb548d44888ed9e35ec768616049e6776391d`.
  It is the only backend the frozen driver accepts. It sends only a
  hash-manifested per-call bundle, blocks worker networking,
  enforces one CPU/8 GiB/one single-use container/no retries, and returns exact
  stdout and stderr bytes in the receipt. Gate parsing accepts Modal only from
  a confirmed sandbox-termination receipt and never requires the native-only
  process-group field; native gates still require confirmed process-group
  reaping. Modal is never an automatic fallback.

The G1 decision path has no direct Cartesian/grid `V^5` membership substitute
and cannot receive the O5 oracle. The frozen recursive extractor still retains
every `V` candidate when all collected polynomials vanish; such legal branches
can degenerate to `|V|^5` full assignments, are verified against the original
generators, and are charged in `X`. Its only explicit Cartesian product is the
required `2^5` signed-recovery check. S0 retains all verified decompositions,
as required before the frozen D-5 B0-hit-order selection; negative membership
exhausts the algebraic roots.

This static snapshot has not executed Modal or any S0 gate. All six gates remain
blocked pending independent re-audit, committed Coordinator execution
admission, and a Coordinator amendment authorising a repository-volume/TMPDIR
mapping for this host. The pinned `BATCH-454f85` checkpoint has `evidence_id:
null` and says execution is not admitted. The frozen `/Volumes/SSD990/.tmp-agent`
path is absent, no substitute is authorized, and the prior `/workspace` free
space observation is also below C-7's 20-GiB repository-volume minimum. The
earlier non-protocol L=3 development probe
was manually terminated after 34 seconds, emitted no result, and is not gate
evidence. No scientific interpretation is made.
