#set page(paper: "a4", margin: 16mm, numbering: "1")
#set text(size: 9pt)
= Range compiler: independent review
DEC-20261031-63eb44 · TASK-20261031-7bf80e

#image("diagram.svg", width: 100%)

Observation. The independent checks validate canonical source binding, the derived Boolean expansions, compressed range semantics, and literal transcript completion through the unchanged verifier. Four assigned review joints hold. Two joints break at precise API requirements: omitted decoding phase costs and acceptance of an empty equation label by the low-level substitution helper. Decision: refine these two interfaces while preserving the checked components.

Both test attempts are retained. Attempt 1 passed 18 group functions and exited 0. Attempt 2 added explicit assertions for the two observed defects: 16 groups passed and two failed, exit 1. This is a strengthened test suite against unchanged source, not a performance comparison or a regression caused by a source change. Both stderr streams are empty, both native checkpoints succeeded, and all 21 permitted input hashes stayed unchanged. Each invocation used a 240-second watchdog and 2 GiB memory limit; no solver, census, benchmark or remote job ran.

F1, production accounting. On the F5 curve y^2=x^3+1, the constant-block descriptor with projection b0 and witness b0=2,z=3 encodes as 26. Decoding reconstructs the correct assignment, but independent instrumentation observes two canonical source builds. The returned costs contain only six value-bit reads and zero state-bit checks. Authentication, compilation and typed-comparison receipts are discarded, including those from the nested encoder. Preserve all executed phases, or remove the redundant authentication and count the remaining work. This defect matters directly to the requested charged comparison.

F2, low-level input validation. Substituting one zero equation whose label is the empty string is accepted at p=5,n=0, although the frozen source format requires nonempty labels. Add that missing predicate. The authenticated production builder supplies nonempty labels, so this is a generic-helper parsing failure; it does not establish an incorrect authenticated production polynomial. Independent square, product, repeated-variable, zero, constant and cancellation expansions agree with the compiler.

Certificate component. For F7, e=s-x2\*x1 and g=s\*x0. At prefix x0=x1=x2=1, the explicit identity is 6\*(s-1)+s=1. The unchanged verifier accepts its serialized multipliers [6,1]. Models [0,1,2,3,4,5,14] cover projections 0 through 6, and the certified prefix excludes 7. Interleaved and projection-crossing certificates also pass. Missing valid projections, incorrect recurrence states, malformed original learned records and duplicate projections reject; censored status is preserved. Value-only comparator CNF is never treated as the final proof.

The F7 completion receipt records 21 insertion-bit visits, 15 trie visits, 14 minimum updates, one certificate with two nonzero multipliers and 74 serialized bytes. Its final checker records three identity multiplications, 21 model-term visits, and eight covering prefixes. These are separate operation units, not time estimates. They remain valid fixed-fixture counters; F1 identifies missing phases in the different encoding/decoding path.

Evidence review. Root matched the four sealed output hashes, verified both test snapshots, recomputed group totals from raw stdout, and checked all frozen input hashes without rerunning the suites. The native review-plan/attestation consistency check passed. The fresh reviewer was source-aware and blind to producer tests, results and interpretations. Requested effort was xhigh; actual serving identity and effective effort remain unauthenticated under the prospective amendment. The raw records retain exact commands, outputs, interpreter identity, source snapshots and checkpoint receipts.

Next implementation. Preserve this source and both attempts; admit additive corrections for F1 and F2. Require exact accounting and the retained parser negative before treating the full compiler contract as accepted. Then integrate complete chart handling and compare quartic, membership-augmented and quadratic-lift encodings on the same complete projected model sets, including witness reconstruction and certificate checking. Continue partial-assignment pruning through checked certificates. Unchanged partial-matrix and two-bit-backdoor configurations remain unscaled.

Scope. These are fixed compiler and certificate results, not a full chart solve or regularity measurement. Trusted public descriptors, caller-assumed primality and canonical-builder semantics remain explicit dependencies. No canonical frontier graph changes: the frontier references and prior authenticated-interface report were checked; neither asserts this compiler's acceptance. The new diagram records this review's scoped outcomes.

Review publication: 5c6a3cca2d8d5946182fc515fd9cee9c90c38692. Exact sources: report-inputs.json.
