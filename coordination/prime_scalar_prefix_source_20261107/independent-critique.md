# Independent written mathematical critique

Verdict: **holds on the assigned mathematical joints, conditional on the stated prime-field and canonical-multilinear premises**. No mathematical bug was found in the proposed prefix predicate, search, restricted certificate, telescope, or projected/auxiliary split. Two wording clarifications below would prevent broader readings of the certificate family and empty-clause sentence. This is a written theory review, not implementation acceptance, empirical validation, official claim promotion, or a durable committed review receipt.

The only scientific inputs read were `derivation.md` and the subsequently authorized `refinement-v2.md` in this directory, `research/prime_sat_prefix_adapter_20261030/adapter.py`, and the displayed initial portion of `research/prime_sat_followup_20261029/encoding.py` through its census setup. No producer controls, results, previous reports, or other reviewers' reports were read. No candidate code, imports, tests, solver calls, or scientific jobs were executed. Shell operations were limited to locating/reading instructions and allowed sources, writing this critique, and hashing this output. Sources have internal provenance. The Coordinator's explicit staged-review assignment limits the usual literature search and committed-snapshot workflow: no novelty or external-literature conclusion is assessed, and this report remains staged for Coordinator disposition.

**Monotonicity and endpoints — holds.** Fix the full Boolean assignment a and the original generator list throughout the search. If R_d f_j=c is a nonzero constant, substitution at any later coordinate fixes c, so the same j witnesses every larger depth. At depth n, R_n f_j=f_j(a), proving P(n) exactly when a is polynomial-invalid. This is an existence statement over generators, not a promise that each generator becomes nonzero. If all generators evaluate to zero, P is false everywhere. Empty generator lists likewise never satisfy the premise. When n=0 the only depth is zero, and a nonzero original constant is necessary and sufficient for this predicate.

The proposed binary search maintains P(lo)=false, P(hi)=true, and every possible least true index in (lo,hi]. At gap greater than one the midpoint is strictly internal; the integer gap strictly decreases. Monotonicity then makes the terminal hi the least true depth. A true P(0) must return immediately. When invalidity has not already been established, the P(n) test is necessary; it cannot be inferred from a domain violation. A retained witness at the final true endpoint, or a final re-evaluation, is required to produce j and c. The note already separately charges final restriction.

A counterexample to omitting the premise is n=1, f=x_0, a_0=0: both P(0) and P(1) are false, and a search initialized with an unjustified true upper endpoint would produce an invalid certificate. For domain-only invalidity take n=1, m=0, auxiliary bound 1, f=0 and a_0=1. The assignment violates the domain, but no nonzero restricted generator exists.

**Canonical cancellation and family scope — holds.** For f=1+x_1-x_0 x_1 and a_0=1, collecting equal residual masks leaves exactly 1 at depth one. This remains true over F_2. Merely testing whether surviving input terms mention x_1 would miss the certificate. Conversely, f=x_1-x_0 x_1 restricts to zero at that same prefix; cancellation to a constant is insufficient unless the constant is nonzero. The canonical representation and explicit deletion of zero coefficients are therefore essential.

The least depth is relative to the fixed variable order and this particular family: one restricted original generator itself is a nonzero constant, with a scalar inverse multiplier. It is not least among arbitrary single-generator polynomial-multiplier certificates. For example over F_3, f=1+x_0 has no Boolean zero and satisfies (1+x_0)f=1 in the Boolean quotient, yet P(0) is false and at a_0=0 the proposed family first succeeds at depth one. This is an especially useful clarification because both certificates use only one original generator.

Nor is it least among multi-generator certificates: with f_1=x_0 and f_2=1-x_0, f_1+f_2=1 at depth zero, although neither is a nonzero constant until restriction. Nor is it least in arbitrary-coordinate explanations: for n=2, f=x_1 and a=(0,1), the fixed-order prefix has length two whereas the single literal x_1=1 already proves invalidity. The same example shows that strict improvement over the full depth cannot be guaranteed. In general f=x_(n-1) and a_(n-1)=1 forces d*=n for n>0.

**Restricted certificate and public checker — holds under prime p.** The vector with q_j=c^{-1} and all other q_i=0 gives the identity 1 directly, in both the polynomial ring on residual coordinates and its Boolean quotient. The adapter checks vector length, parses canonical residues, recomputes all original restrictions, and checks the summed quotient identity. Its mask-OR multiplication agrees with Boolean quotient multiplication; scalar multipliers do not invoke any distinction between quotient and ordinary multiplication.

Primality is an external premise, not something this adapter verifies: it explicitly returns `prime_field_verified: False`. An unconditional extension to arbitrary p>=2 would be false. Modulo 4, f=2 is nonzero and P(0) holds, but no scalar inverse exists and no multiplier can make 2q=1. No such extension is claimed in the derivation.

**Original-ring telescope, signs and degree — holds.** Write f^(k)=A_k+x_k B_k, where neither A_k nor B_k depends on x_k and the first k coordinates have already been substituted. Then f^(k+1)=A_k+a_k B_k, so g_k=B_k gives exactly f^(k)-f^(k+1)=(x_k-a_k)g_k. Summation cancels all intermediate restrictions and yields f_j-c. Rearranging gives the stated minus sign in front of the prefix-equation multipliers. For the elementary check f_j=x_0 and a_0=1, the formula is 1=x_0-(x_0-1); replacing the minus sign by plus fails over odd characteristic.

If D=deg(f_j), substitution does not increase degree and every nonzero g_k has degree at most D-1. Thus each nonzero product g_k(x_k-a_k), and c^{-1}f_j, has degree at most D. At D=0 all g_k vanish. This is the degree of the displayed certificate summands, not merely the degree-zero simplified result. There is no assertion here about the degree needed to convert an arbitrary nonmultilinear presentation. For instance x_0^2-x_0+1 reduces to the constant 1 in the Boolean quotient, but an ordinary-ring identity for that original presentation requires the Boolean equation x_0^2-x_0. Discarding it would incorrectly identify the original polynomial with 1 in the ordinary polynomial ring.

**Clause and projection semantics — holds, with one scope clarification.** The displayed ordered clause is false exactly when all first d bits match a. There are 2^(n-d) ambient Boolean extensions. All share the nonzero value c of the restricted generator, so none is a polynomial root. For d<=m every auxiliary witness of every projection matching that prefix lies in the cylinder and is invalid; excluding those projections is sound. For d>m, the conclusion only concerns the specified auxiliary subprefix.

An explicit d>m counterexample is n=2, m=1, f=x_1, a=(0,1), with no auxiliary bound. Here d*=2 and the sound full clause is x_0 OR NOT x_1. Projection x_0=0 still has the valid witness (0,0). Truncating the clause to x_0 would incorrectly delete that valid projection. At the boundary d=m=1, f=x_0 and a_0=1 gives a sound projection exclusion: neither auxiliary value can rescue that projection.

The statement that an empty clause is justified 'only by a nonzero-constant original generator' is correct **for this fallback's selected witness family**, not for the unchanged adapter's general certificate schema. The f_1=x_0, f_2=1-x_0 example above allows an empty clause without either original generator constant. Recommended wording: 'At d*=0 this fallback emits an empty clause using a nonzero-constant original generator.' This avoids accidentally narrowing the existing checker semantics.

A checked valid model licenses removal of its entire projection cylinder from further enumeration because that projection has already been recorded. It does not make the other full assignments in that cylinder valid. Complete projected-set equality requires both sound witnesses for recorded projections and coverage of the domain by invalid cylinders plus recorded-projection cylinders. The adapter visibly invokes a separate cover verifier; that verifier's implementation was outside the allowed source set and was not read or validated in this review. The logical coverage obligation in the derivation is correct. Domain restrictions change admissible coverage counts; the ambient count cannot be relabeled a count of admissible assignments.

**Costs — holds as a primitive-work accounting statement.** For n>=1, binary search uses at most ceil(log_2 n) internal predicate evaluations after endpoints. Each full predicate scan visits at most T original monomials, so the stated O(T log(n+1)) monomial visits, with endpoint handling, is valid. More uniformly including n=0, write O(T(1+log(n+1))). This does not constitute a total-runtime bound: scanning s generator headers costs O(s) per scan even if many polynomials are empty; modulus size affects arithmetic; n-bit masks and dictionary keys have costs; final restriction, inverse, vector allocation, clause serialization and checker/coverage work remain separate. The derivation explicitly separates most of these and claims only monomial visits/coefficient updates. Adding the s-header term would make a future implementation cost model less ambiguous.

Streaming one residual dictionary at a time bounds transient dictionary entry count by max_j T_j (not total resident input, certificate, or mask storage). Materializing all telescope multipliers can duplicate contributions across several coordinates, so the cheap restricted certificate does not automatically give an equally cheap explicit original-ring transport. No such cheap construction or speedup is claimed. None of these symbolic counts is a measured performance result.

**Authoritative refinement v2: incidence sweep — holds.** This addendum was supplied during the same written-review window. Its per-original-term invariant is sufficient: after batch i, every surviving original term has exactly its substituted coefficient and residual mask, while any term meeting a fixed zero is dead. Summing those contributions in D_j therefore computes precisely R_(i+1) f_j. Deleting a zero dictionary entry does not delete the underlying original terms. A later subtraction from a currently absent key must be interpreted as subtraction from zero, creating the appropriate nonzero residue when needed; dictionary operations must support this natural modular-update behavior. An implementation that instead skips an original term because its aggregate key is absent would break the invariant.

Checking at completed variable batches is sound. The supplied example 1-x_0*x_1 at a_0=1 correctly exhibits the unsound transient constant between subtraction and addition for one term. An implementation must preserve the completed-batch invariant before consulting the qualifying-generator set; the addendum explicitly requires that rule.

The count O(n+s+T+I) is valid for abstract bookkeeping: initialize s generator states and n buckets, initialize T term records, traverse I incidence entries, and perform at most two coefficient updates per live visited incidence. The number of touched-generator events over all batches is at most I, so maintaining qualification only for touched generators avoids an otherwise hidden ns rescan. Maintaining each generator's count of nonzero nonconstant keys requires constant bookkeeping per actual key update, including zero-to-nonzero and nonzero-to-zero transitions. A constant-key lookup and this count determine qualification. There are at most O(T) aggregate keys at batch boundaries, and only constant extra transient overhead per active update. Together with original term records and incidence buckets this supports the stated entry-count space bound. Bit extraction, masks, field operations, and hashing are explicitly excluded from a unit-cost runtime conclusion. No implementation or empirical cost is checked here.

Testing sequential depths returns the same least true index as the binary-search specification, by the established dictionary invariant. If no depth qualifies, the final scalar evaluations are all zero and the full assignment is polynomial-valid. The six examples in v2, including its strict cancellation example, quotient inverse, auxiliary witness, transient subtraction, and composite-modulus example, are algebraically correct under their stated premises. The cited FMCAD paper was not opened under this restricted review assignment; its attribution and novelty discussion are not independently verified by this critique.

The next theory edit should make the scalar-witness family and empty-clause qualification explicit, and optionally state the uniform binary-search endpoint/header overhead. V2 already makes the scalar family and sweep header overhead explicit. These are clarification requests; the assigned theorem statements hold with their present contextual restrictions. Any implementation, software acceptance, publication, or official transition remains a separate Coordinator action.

```yaml
review_attestation:
  actor: fresh_independent_mathematical_critic
  review_kind: written_theory_critique
  joints_owned:
    - monotonicity_invalidity_and_endpoints
    - binary_search_shortest_in_scalar_constant_generator_family
    - canonical_cancellation
    - restricted_certificate_and_prime_field_premise
    - telescope_signs_and_degree
    - projection_boundary_and_coverage_obligation
    - primitive_cost_scope
    - incidence_sweep_invariant_and_batch_boundary
    - incidence_sweep_bookkeeping_and_space
  sources_read:
    - AGENTS.md
    - docs/agent-contract-extended.md (literature-first and review-architecture excerpts)
    - agents/red-team.md
    - agents/validator.md
    - .agents/skills/review-evidence/SKILL.md (routing pointer only; not invoked)
    - .resume/prime-transform-prefix-theory-20261107/authorization.json
    - .resume/prime-transform-prefix-theory-20261107/derivation.md
    - .resume/prime-transform-prefix-theory-20261107/refinement-v2.md
    - research/prime_sat_prefix_adapter_20261030/adapter.py
    - research/prime_sat_followup_20261029/encoding.py (initial portion through census setup)
  read_sibling_reports: false
  read_producer_controls_or_results: false
  executed_candidate_code: false
  scientific_runs: 0
  solver_calls: 0
  official_claim_promotion: false
  verdict: holds_on_assigned_mathematical_joints_with_stated_premises
  clarification_requests:
    - specify scalar_inverse_single_generator_family
    - qualify_empty_clause_only_sentence_to_this_fallback
    - optionally_make_endpoint_and_generator_header_overhead_explicit
  limitations:
    - staged_uncommitted_theory_input_explicitly_authorized_by_coordinator
    - not_a_blind_rederivation_from_statement_alone
    - no_external_literature_or_novelty_assessment
    - coverage_verifier_implementation_not_in_allowed_read_scope
    - no_implementation_or_runtime_acceptance
```
