# A17 source and evidence review before implementation

This implements the ranked [A16 successor](../prime_field_a16_execution_20261107/next-leads.md).
Root read the A16 full-horizon branch, A14 native-case assembly and partial-known
solver/checker, A12 Registry/affine solver and A14 pure geometric cache before
writing this implementation on 2026-11-07. Provenance: internal primary source.

The branch's constructor callbacks populate public affine labels and Registry
equalities. Query outputs populate geometric cache rows and are not fed into
constructor selection or the Registry. Thus both arms can execute the entire
fixed GENERAL horizon24 construction before extra query scheduling. This is a
new implementation boundary, not a measured construction saving.

The partial solver already substitutes supplied native base units and uses the
existing KernelFreeSystem row-space API, with original-row certificate lifting.
Keeping this system alive between query results can identify target coordinates
incrementally. Every new positive must lift through actual base units and
available target rows, and pass the public scalar-point equation before it can
cause a skip. Neither a later certificate nor the reference's answer justifies
an earlier skip.

This safety scope requires all base labels to be paid supplied knowledge.
When base logs remain unknown, a further relation involving a known target may
still reveal base information and help other targets. This first stage does
not transfer its stopping rule to unknown auxiliary pools or norm bases.
Include all paid identity/base/same-target/cross-target Registry equalities;
never silently replace a joint target system with unrelated single-target rows.

A16's fresh4curve/32target census completed1260systems/2520pairedcalls and576
separate diagnostics. Its horizon24 known48 program recovered96/96 dependent
policy slots versus90/96at8; the three horizon8 policies already cover the same
32distinct targets in union. All policy work remains paid, and no adaptive
portfolio was measured. [PCC-20261107-d1bac1](../../pcc/claims/PCC-20261107-d1bac1.json)
remains producer-unverified, not trusted signed scientific replay or calibrated
performance evidence. [pcc:unverified]

Newly merged [A15 independent retained-row review](../prime_field_a15_execution_20261107/runs/a15-batched-pairs-06ab77/reviews/README.md)
at main2aa7407 enumerates all retained signed-triple relation sets with a
separate group law and matches the reported rows and raw phase sums. It leaves
producer-instrumented construction-vector and authenticated execution standing
open, records a source-provenance failure, and performs no new execution.
We do not upgrade A15/A16 PCC standing from that scoped review.
[pcc:unverified]

The carried [A16 literature note](../prime_field_a16_execution_20261107/literature.md)
records the primary PKC2016 section3.2/p8 rough mixed-unit cost warning and its
retained PDF hash. No new paper retrieval, KB search result, corpus-wide absence
or novelty claim is made. Research-kb remains unavailable; direct source review
is the explicit fallback. Fp/Fr primitive calls, logical work and explicit array
traffic remain separate, with Python/hash/pow/OS/checker/calibration gaps.
