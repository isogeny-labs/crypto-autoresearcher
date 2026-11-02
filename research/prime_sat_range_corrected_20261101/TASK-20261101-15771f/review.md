**Independent source-aware review — TASK-20261101-15771f**

The additive compiler corrects the retained F1 and F2 counterexamples in this fixed review. Counted encoding and decoding each authenticate through exactly one canonical source build and return the independently derived successful-operation phase receipts. The exposed substitution helper rejects the empty equation label. All 24 frozen obligation groups passed in the first bounded suite: 604 checks, exit status 0, empty stderr. No new counterexample was found within these assigned checks.

The target is `research/prime_sat_range_corrected_20261101/compiler.py`, SHA-256 `8501e320de27169cebc35f678759b5e33a3d7c76c86dc4bb5caf329a2e12fdd7`. Every one of the 24 bound input hashes agreed before and after execution. The exact test source, expected values, inputs, observed values, complete stdout/stderr, commands, gate receipt and runtime metadata are retained in `independent-results.json`. Its `attempts[0].stdout` is the exact JSON emitted by the suite; parsing that string recovers every structured check. A compact group index is a derived navigation aid, not a replacement for that raw record.

| Assigned joint | Verdict | Evidence and scope |
|---|---|---|
| `source_binding` | holds | Trusted public descriptors rebuild the canonical field source; typed document and descriptor mutations reject. Witnesses leave the symbolic document unchanged. |
| `bit_substitution` | holds | Independently specified squares, products, diagonal terms, modular cancellation and zero/constant polynomials match. F2's empty label rejects; nonempty zero equations remain accepted. |
| `range_exactness` | holds | Literal generators and comparator clauses match the threshold construction. Interleaved and crossing layouts, state reconstruction, malformed inputs and fixed wrong-state controls behave as derived. |
| `certificate_completion` | holds | Literal serialized identities pass the unchanged adapter. False completeness, bad original records, duplicate projections and wrong states reject; gaps remain gaps and censored status is preserved. |
| `fixed_execution` | holds | One of four allowed attempts, after successful native checkpoint, under the 240-second and 2-GiB address-space limits. No solver, census, sweep, benchmark or remote job ran. |
| `claim_boundary` | holds | Whole successful-operation phase dictionaries match independently derived counts; separate interception records one canonical build per counted encode/decode. Receipt mutation does not affect the document or later calls. Failure-cost and workload boundaries remain explicit. |

These are verdicts on the six assigned joints. The Coordinator owns composition, official decisions, publication and rendering.

**F1: complete phase receipts and one authentication.** The exact F5 public descriptor is `{"p":5,"curve":{"a":0,"b":1},"kind":"constant","k":null,"projection":["b0"]}`. Its symbolic source is `b0*z-1=0`. The fixed assignment `{"b0":2,"z":3}` encodes to 26 and decodes to the same two named values. A transparent wrapper around the frozen `canonical_circuit` function captured precisely one call, with that exact trusted descriptor, for each counted public encode and decode invocation. The wrapper called through to the original function and was restored after each check.

The authentication receipt was derived independently from the literal constant circuit and the document's typed tree. The actual receipt agrees with that derivation and with `authenticate`: 184 typed comparison nodes; one canonical builder call; one equation; 382 canonical source bytes; two source terms; 12 substitution products; 10 coefficient merges; zero cancelled output terms; two range blocks; four generators; four clauses; eight literals. These are separate units. The reconstruction phase records three threshold-bit visits, two canonical-value checks, six value-bit writes and two initial-state reads. No recurrence or state-write event occurs for F5, so those zero-event fields are absent. Decode additionally records six value-bit reads and zero state-bit checks. Authentication, decoding and reconstruction remain distinct dictionaries.

For the F7 descriptor with value positions `[0,2,4]`, state position `[5]`, `n=6`, `m=3`, assignment `x=6` encodes to 52. The complete reconstruction receipt records three threshold visits, one canonical-value check, three value writes, one initial-state read, one recurrence product and one state write. Decode records three value reads and one state check. The fixed values 20 (same value bits, wrong state) and 53 (noncanonical field value seven), as well as malformed bit integers, reject. Mutation of returned authentication, reconstruction, decoding and assignment objects leaves both the source document and later results intact. The integer compatibility encoder agrees on bits and remains an integer-only API, not a cost receipt. The helper `_encode_authenticated` is private, documents its authenticated caller requirement, and is invoked only after authentication by the inspected public wrappers; there is no cached trust token.

**F2: strict nonempty equation labels.** The predecessor counterexample is retained verbatim:

```python
substitute_equations([{"label": "", "terms": []}], {}, 5, 0)
```

It now raises `ValueError`. The corresponding nonempty label `zero` still returns a zero polynomial, while duplicate labels reject. Canonical-source controls also reject zero/noncanonical/bool coefficients, unknown variables, a cubic term, unsorted variables, unsorted terms and duplicate monomials. The predecessor source and review remain unchanged.

**Independent symbolic and field checks.** For F5, write `x=b0+2*b1+4*b2`. Boolean reduction gives

```text
x^2 = b0 + 4*b1 + b2 + 4*b0*b1 + 3*b0*b2 + b1*b2,
x^2-x = 2*b1 + 2*b2 + 4*b0*b1 + 3*b0*b2 + b1*b2.
```

The suite specifies the nine cross-block `x*y` coefficients independently, along with a literal zero and constant three. The five-equation fixture gives 39 substitution products, 31 coefficient merges, nine colliding masks, five source terms and one cancelled output term. Repeated-variable squares use mask union and retain their linear diagonal terms.

The retained 18 public descriptors comprise nilpotent degrees 0 through 5 and guard/slack/constant blocks over each of the two fixed nonsingular curves `p=5,a=0,b=1` and `p=7,a=0,b=1`. The review independently expands every source term, compares arithmetic equation ordering and exact projection/layout, and checks degree at most two. This is the prescribed descriptor cohort, not an assignment search.

The roundtrip group contains 43 explicitly constructed field assignments: 36 satisfying assignments and seven canonical assignments with nonzero residuals, plus six malformed-assignment rejection controls. It includes every frozen nilpotent fixture and all eight frozen guard fixtures, both common-root beta signs, fixed coprime guards/slack witnesses, constant inverses, and the fixed `U=X^k,C=1` nilpotent witnesses. Auxiliary values are constructed by the review's own ordinary coefficient arithmetic; the independent original-equation evaluator multiplies the supplied named values directly. Every source residual equals the corresponding compiled bit-polynomial residual, and every canonical assignment has zero range residuals. A canonical invalid witness still encodes and decodes as a field assignment; its nonzero arithmetic residual remains visible. No failed witness is interpreted as unsatisfiability.

**Range exactness and certificates.** If the one positions of `p-1` are `j1>...>jh`, the equations force `s_r` to the product of the value bits at `j1,...,jr`, starting with the alias `s1=x[j1]`. Thus every value-bit assignment has one recurrence extension. If its integer value exceeds `p-1`, its highest differing threshold-zero position and all higher threshold-one positions are one, violating the associated forbidden generator. Conversely, a nonzero forbidden generator implies that the integer exceeds the threshold. This proves the canonical-range projection statement under the stated prime-field/Boolean-quotient premises. The implementation checks here cover fixed literals and layouts, rather than enumerating assignments to establish that statement.

For F7 the two polynomials are `e=s-x2*x1`, `g=s*x0`. At prefix `x0=x1=x2=1`, restriction gives `e=s-1` and `g=s`, so `6*(s-1)+s=1` in F7. The exact multiplier vector is `[{"0":6},{"0":1}]`. The same vector verifies at full-depth prefixes 7 and 15 with the state fixed to either value. The supplied models `[0,1,2,3,4,5,14]` project to `[0,1,2,3,4,5,6]`; completion appends the exact certified prefix seven. An independent mask evaluator and the unchanged adapter both verify the identities.

The direct F5 certificate uses its forbidden generator alone. Two interleaved F5 blocks verify both one-invalid-block cases and the declaration-order tie when both blocks are invalid. The projection-crossing case distinguishes existential projection from a chosen field value: in the range-only system, 52 and 4 can share a projection while representing different canonical field values. Adding the explicit arithmetic polynomial `bit4-1` makes 52 a valid witness and 4 invalid, checking that a zero auxiliary suffix cannot replace the required witness. Literal F11 and F17 threshold examples check additional state/alias and clause layouts without a parameter or assignment census.

The unchanged final adapter was intercepted transparently and received exactly the authenticated polynomial list, `domain_cnf=[]`, the augmented transcript and `aux_bound=None`. The actual comparator CNF remains separately retained. Directly supplying nonempty comparator CNF to the full-cube interface rejects. Missing certificates or a valid projection, wrong multiplier sign, wrong recurrence state, a malformed learned record shadowed by a model terminal, and duplicate model projections reject. Every original learned record remains an unchanged prefix of the augmented list; every raw model and status is retained. Censored transcripts with either complete or incomplete incidental coverage remain censored. Empty or missing domain-valid branches retain gaps with `arithmetic_root_asserted=false`. The value-zero/state-one assignment satisfies the comparator but fails the recurrence, and range completion does not fabricate a certificate for it.

**Literal F7 accounting.** Independent counts agree with the complete receipt, including serialization. Construction performs two coefficient merges and creates one block, two generators, one clause and three literals. Authentication visits 62 typed nodes; comparator comparison visits five. The following values remain separate units:

| Phase | Named unit | Count |
|---|---|---:|
| Completion | insertion bit visits | 21 |
| Completion | trie visits | 15 |
| Completion | minimum updates | 14 |
| Completion | emitted certificates | 1 |
| Completion | multiplier entries / nonzero entries | 2 / 2 |
| Completion | serialized certificate bytes | 74 |
| Restriction | term visits / coefficient additions | 3 / 3 |
| Identity check | coefficient multiplications / additions | 3 / 3 |
| Model evaluation | term visits / coefficient additions | 21 / 2 |
| Coverage | prefixes / summed depths / trie nodes | 8 / 24 / 15 |
| Serialization | raw / augmented / bootstrap bytes | 60 / 134 / 12 |

**Frozen obligation inventory.** All rows passed in attempt 1. Counts below count assertions and explicit observed-value records in this review suite, not solver instances.

| Group | Checks | Group | Checks |
|---|---:|---|---:|
| literal_f7 | 7 | literal_f7_negatives | 5 |
| direct_f5 | 4 | f7_fixed_states | 6 |
| interleaving | 10 | cross_projection | 9 |
| zero_projection | 5 | censored | 6 |
| shadowed_bad_record | 4 | domain_gap | 13 |
| bootstrap | 14 | layout_mutations | 26 |
| content_mutations | 17 | bit_substitution | 3 |
| accepted_blocks | 144 | fixed_root_roundtrip | 264 |
| fidelity | 8 | accounting | 2 |
| nonempty_labels | 11 | counted_encode | 5 |
| single_decode_authentication | 4 | nonzero_recurrence | 8 |
| canonical_binding | 22 | cost_receipt_isolation | 7 |

**Execution custody and scope.** The successful native gate ran from `2026-11-01T18:01:15.931839Z` to `2026-11-01T18:08:31.085371Z`, retaining its complete S3 checkpoint receipt. Attempt 1 began at `2026-11-01T18:08:31.110979Z` and ended at `2026-11-01T18:08:32.033787Z`. Its orchestrator-observed elapsed interval was 0.902521894997335 seconds; this is custody telemetry, not a performance comparison. Peak memory and CPU time were not measured. The enforced address-space limit was 2,147,483,648 bytes. Python was 3.12.8 at `/home/ec2-user/prime-sat-research-venv/bin/python`. The exact command was:

```sh
timeout --signal=TERM --kill-after=5s 240s bash -c 'ulimit -v 2097152; export PYTHONDONTWRITEBYTECODE=1; exec /home/ec2-user/prime-sat-research-venv/bin/python research/prime_sat_range_corrected_20261101/TASK-20261101-15771f/test_independent.py'
```

The test-source SHA-256 is `71c8fca3e7195dbb7f31990ebe3f3457485c3e455452b6bc54907479635fa590`. The recorded repository revision is `debd176b5a13a8a9c75127a55e88c06b9df62f0c`. Read-only tracked-path status reported three dirty generated ledger index files; the reviewer did not edit them. The bound research inputs all remained unchanged. The checkpoint was preserved during its seven-minute execution, and no duplicate gate or suite was launched. Only one software suite invocation was needed; there are no failed or discarded suite attempts.

The source review used the exact source/API contracts, fixed fixtures, range and completion derivations, and predecessor F1/F2 review allowed by the handoff. These are internal primary sources, retrieved in this session; no novelty or external-literature claim is made. All current producer tests, software results, README, snapshot receipt and interpretations outside the frozen brief remained unread. `attestation.yaml` contains the native `review_attestation`, exact read inventory, actual attempt metadata and unknown runtime properties. Requested inference was `review-adversarial` at `xhigh`; actual model, provider, tier, effective effort and context/output capacities remain unauthenticated under the approved amendment.

The reviewed successful-operation counts do not quantify rejected operations. The later workload harness must separately retain and charge failures and rejected witnesses before making a full workload cost comparison. The accepted field-circuit builder is the production semantic dependency; generic caller-supplied arithmetic retains its caller-defined meaning, and primality remains a premise. This review checks compiler/certificate behavior and declared operation units. Full chart integration and its projected SAT comparison remain the next separately contracted work. Root owns Git, claims, queue, archives and report rendering; this reviewer writes only the four assigned outputs.
