# J2 producer-visible authentication and integration critique

Verdict: the interface is coherent as a source-only design with explicit fail-closed dependencies. I found no authentication bypass permitted by its stated reconstruction rules. It is not an implemented schema or checker, and cannot currently accept an execution or completeness certificate. The concrete admission gaps below must be resolved in a later implementation handoff. This verdict covers J2 only; it does not substitute for J1's independent theorem review or any native gate or promotion.

Actual blindness: producer-visible. I read interface-v1.md, producer-proof-v1.md and review-plan.json before examining original sources. I did not read or contact J1, read sibling reports, import candidate code, run tests/solvers, edit Git/canonical records, allocate IDs, or execute scientific work. All attacks below are source-static thought controls, not executed results. No previous moment notes were used. A memory-registry keyword search returned no relevant entries. Source discovery listed filenames including old reports; their contents were not read.

Frozen-input SHA-256 checks matched:

- review-plan.json: 1ae601e6456227d7454a3e83eb64baee8b6f77ff9d78089e14484e8828766509
- interface-v1.md: d27231cd5b2a9f077dd5edf9156895e28a666cd4ec13e91caa72c31f56fb64b9
- producer-proof-v1.md: cee092d2c5ffa8f7fdad4104bdfa3486ed26878dd79a0887faa746926d041bac

## Original source evidence and files read

All paths below are relative to the repository. Provenance is internal, read directly in this review; hashes were computed from files, without executing them. Reads were focused on the named functions and relevant portions, not every transitive dependency.

| File | SHA-256 | Evidence used |
| --- | --- | --- |
| research/prime_sat_full_chart_composition_20261101/composition.py | 354d6eef9695477f5c3ab2e9acc274241848f25a863dac30d2e5eb0def68c3b9 | descriptor, canonical_chart, compile_chart, authenticate_chart, assignment/model recovery and complete_chart_transcript |
| research/prime_sat_shared_signed_chart_20261030/charts.py | c808c7d3a5a2a96316a0c13c9faafd848406ef44e960a1bcc52bde700e6a818b | chart_spec and signed-multiset construction context |
| research/prime_sat_range_corrected_20261101/compiler.py | 8501e320de27169cebc35f678759b5e33a3d7c76c86dc4bb5caf329a2e12fdd7 | typed parsing, substitute_equations, compile_range, compile_block, authenticate, encoding and complete_transcript |
| research/prime_sat_prefix_adapter_20261030/adapter.py | cbc038001273d0a351b86f94d3ac0708eb698e51ab3d8bbef39d7798c4e8fc65 | verify_transcript and function references |
| research/prime_sat_costbridge_controls_20261029/prefix_cover.py | 10ef5f615218649660eaf62212e9dcb58045f08ebb414663a4c14ed63c090c2c | complete combinatorial coverage implementation |
| research/prime_sat_transform_integration_20261103/chart_solver.py | 2191eb95ddcb165d285d03853dd46c5dc83eb19e2d742110291fc1c7a8b5d4ad | convert_range, verify_chart_answer, solve_chart integration and cost limitations |
| research/prime_sat_followup_20261029/encoding.py | 2b18f50238db633eb91ac33a36660c52620e81c5f6fa1c9c78d40c261e99041f | verify_search and references to legacy solve/verification functions |

Also read: repository AGENTS.md (terminal rendering partly truncated), docs/agent-contract-extended.md literature-first section, and .claude/skills/review-evidence/SKILL.md introductory routing/experiment workflow. The assigned source-only J2 review is neither experiment replay nor Lean verification; no experiment lifecycle or visual artifact was initiated beyond the coordinator's single-output scope. The original source files are the relevant primary implementation sources. No external literature claim or novelty conclusion is made. Transitive rationality, quotient, signed-recovery and original chart checker implementations were not fully audited; authentication must bind their accepted dependency closure before implementation admission.

## Authentication and layout attacks

The generic range compiler authenticates against caller-supplied arithmetic. Its successful typed comparison alone does not authenticate a full chart. A malicious caller can present an internally consistent range document for different low-degree equations. Interface section 2 closes this route only because it requires rebuilding the full chart from an independently trusted descriptor and allowed source version, then checking every row and layout. Calling compile_range/authenticate(kind='range') in isolation does not implement that requirement. The composition-level authenticate_chart is the source precedent for this stronger obligation.

For N original field variables, width ell and g range states per variable, compile_chart assigns all value bits first and all state bits afterward. Appending S and E changes the original state base from N*ell to (N+2)*ell: original state positions shift by 2*ell, although original value blocks remain in place under append-only ordering. A stale identity bit map therefore fails whenever g>0. In the special case g=0 there are no state bits, so such a control alone would not expose this bug. Test admission needs at least one g>0 descriptor. Map every original named value bit and named recurrence state, require an injective total map, and verify translated original polynomials. An arbitrary caller-provided permutation is not authority. The interface's named-block reconstruction and content comparison are sufficient if implemented this way.

Swapping support.u(h-1) with support.u(h-2), changing an E-row sign, renaming support variables, leaving moment bits unlinked, or omitting an original norm/interval/rationality row must fail exact reconstructed-source comparison before lemma admission. Merely recomputing fresh digests after the malicious edit does not repair that mismatch. Changed target, interval, arm, stratum or projection must likewise fail against the trusted descriptor, even if all submitted hashes are mutually consistent. The source calls arity `k`; the prose calls it `h`. The wire schema must make the equality k=h explicit and distinguish it from local compiler variables named h for the range-state count.

## Malformed and semantic-record controls

| Attempt | Required disposition and reason |
| --- | --- |
| Boolean where integer expected; negative/out-of-layout literal; duplicate JSON field, unknown key, duplicate name | Reject malformed record before hashing/coercion can erase the difference. Duplicate JSON keys require parser-level detection, not dict comparison after last-key-wins decoding. |
| Wrong moment row/sign, omitted original row, changed source/projection, stale bit map/digest | Reject binding mismatch; no lemma or model accepted under that binding. |
| Correctly formatted clause missing one S literal, dropping an auxiliary literal, reversing a literal sign, or using global-prefix numbering | Reject clause mismatch against exact layout-derived assignment negation. The old prefix checker cannot directly express the general S/E subcube. |
| Omitted lift or wrap arc; caller-supplied success flag/table | Recompute from authenticated parameters; reject an exclusion whose recomputed arcs intersect. No producer endpoint authority. |
| Wrong signed division | Use mathematical floor/ceiling. For arc [0,0], prefix=1,H=2 the correct quotients are ceil(-1/2)=0 and floor(-1/2)=-1, giving no intersection; truncation of both gives a false intersection. This particular bug loses pruning, rather than proving unsoundness, but still fails the specified predicate. |
| B=1 / M=0 | Avoid division by M. Only S=0,E=0 is feasible; S0=0 depth=0 cannot be excluded, while absent lifts permit exclusion. |
| Full-field arc / depth=0 / depth=ell | Full-field arc intersects every canonical-completable prefix; any nonempty arc intersects depth=0; a depth=ell prefix >=p has no canonical completion. Empty arcs are handled separately. |
| Residue in an interval hole | Passing the necessary bound is not a support witness; do not create a model or success count from it. |
| Invalid/incomplete assignment, bad signed witness, changed reported projection | Reject model and construct no block. Verify every polynomial and range equation and recover the mapped original assignment. |
| Duplicate projection with different auxiliaries | Deduplicate by exact original projected tuple. Do not count it twice. The future schema must choose deterministic reject-versus-idempotent handling. |
| Block omits a projected bit or includes arbitrary auxiliary bits | Reject mismatch; reconstruct ALL AND ONLY original projected value bits. A full-assignment block cannot stand for completed enumeration of its entire projection. |
| RAT-only clause supplied as semantic L | Reject unsupported lemma provenance. RAT preservation of satisfiability is not preservation of all projected roots. |
| Missing proof dependency, unsupported proof format, exhausted verification cap | Refuse completeness acceptance; retain only independently validated partial records with explicit incomplete/censored status. |
| Proof for different CNF, missing initial clauses, mismatched numbering, truncated/invalid proof | Reject the completeness claim; solver UNSAT status is insufficient. |

## Cache and resource critique

The stated arc key includes theorem/schema, extension digest, p,h,t,B,S0, and clause-result keys also include depth,prefix,layout. This prevents a cache entry for one target/source or bit numbering being silently reused for another merely because S0 agrees. Successful authentication must precede lookup of any success result; hashes must be recomputed from immutable owned bytes rather than trusted from producer fields. Failed, partially verified or subsequently mutated objects cannot populate or retain successful entries. The theorem/verifier version is part of semantic identity, including registered proof-family verifiers. Eviction changes performance, never acceptance.

At most h lifts and 2h arcs is a credible endpoint-work bound for fixed h<=5, since h(B-1)<hp. It is not total verification cost: bit complexity, ell literals, bounded parsing, chart reconstruction, dependencies, hashing, compilation, model/witness checking, cache memory, residual CNF construction and proof generation/checking remain payable. The implementation must enforce byte/bit-length limits before large integer allocation and arithmetic, not only after parsing. A huge numeral or proof can exhaust resources before a late row-count check. The current source counters omit some interrupted work: chart_solver explicitly reports cost_coverage.complete=False; composition records failed decoding but states interrupted-operation counts need outer instrumentation. The interface correctly does not claim existing counters are whole-cost evidence.

## Existing integration and outstanding admission defects

The current range completion adds polynomial-identity certificates for invalid range prefixes and delegates to adapter.verify_transcript; that verifier checks polynomial identities, models and a prefix-cover trie. prefix_cover itself explicitly verifies neither arithmetic nor SAT proofs. The legacy encoding.verify_search uses exhaustive Boolean assignments for its small-instance completion check. chart_solver calls range/complete-chart completion and distinguishes accepted partial output from verified_complete. None of these inspected acceptance paths supplies the proposed final residual-CNF DRAT checker. The interface is accurate about that limitation.

Three concrete design-to-implementation gaps remain, already acknowledged in broad terms but not resolved by this packet:

1. There is no executable exact wire schema, canonical serialization specification for all new records, parser-level duplicate-key policy, dependency-closure manifest, or full state-bit translation algorithm. The prose requirement to reconstruct trusted content is strong enough for design review, but implementation must supply these objects before acceptance is possible.
2. No accepted primality verifier/reference policy, final proof checker/version, allowed proof-family registry, or exact CNF/proof binding implementation is supplied. Finite-cap refusal and proof rejection need distinct recorded reasons; neither may become `complete` through a fallback to existing prefix acceptance.
3. Numeric parser/work/cache/proof caps and interrupted-work accounting are deferred. This is acceptable for source-only review, and remains a hard missing admission dependency for execution. The source-only packet supplies no measured cost, rejection frequency or implementation-control results.

Recommended disposition: retain this packet as a reviewed source-only interface, with J2 authentication/integration conditions stated above. Require the later implementation handoff to instantiate the schema, dependency closure, map reconstruction, rejection/refusal taxonomy and bounded proof checker; independently exercise the listed malformed and stale-cache controls then. This review neither grants that handoff nor changes any execution prohibition, six-coset support boundary, canonical status or publication custody.
