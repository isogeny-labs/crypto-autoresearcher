# Independent static review of alias-tolerant Euler circuits and conditional PC DAG

Verdict: **accept with qualifications as a source-only mathematical design**. No defect was found in the two-direction projection argument, the corrected full-cube domain prerequisite, the conditional ideal-membership recurrence, or the stated field-term upper bound. This is a written review of proposed mathematics and two existing source files; it is not validation of an implemented new arm or DAG checker and confers no execution or official promotion.

## Frozen inputs and inspected sources

The two dispatched input hashes were verified by reading and SHA-256 hashing the files:

- `design-v2.md`: `d66b067f1e0f3416a3c7b1a511dc16f1390477207508b03243ab51304c33489d`.
- `review-plan-v2.json`: `caad56e9075b5fab9d5fddc6f09362ea3c9efa06a430de46c0b509acec765939`.

Source provenance is internal, retrieved by static file reading in this independent review:

- `research/prime_sat_prefix_adapter_20261030/adapter.py`: `cbc038001273d0a351b86f94d3ac0708eb698e51ab3d8bbef39d7798c4e8fc65`.
- `research/prime_sat_costbridge_controls_20261029/prefix_cover.py`: `10ef5f615218649660eaf62212e9dcb58045f08ebb414663a4c14ed63c090c2c`.

Review scope is the frozen note and these two cited source files. The earlier notes, discriminant proof, old membership builder and witness reconstruction implementation were not independently re-reviewed here. No novelty or literature-priority claim is assessed. No candidate was imported or executed, and no tests, Git operations, new identifiers or canonical changes were made. The only authored artifact is this review.

## Full-cube and projection semantics

The correction in design lines 5–6 is justified. `_domain` explicitly accepts an empty CNF when `bound is None`. `verify_transcript` evaluates every submitted model against every generator, extracts its low `m` bits, rejects repeated projections and adds `(m, projection)` to coverage. It does not require a unique auxiliary witness. `verify_cover` accepts an arbitrary terminal cylinder at that depth and, with `aux_bound=None`, performs no auxiliary-domain filtering.

This is sound projected enumeration: a checked witness establishes that a projected pair belongs to the answer set, so other auxiliary assignments above that pair need not be classified individually. For a projection absent from the reported models, full-cube coverage must instead cover every possible auxiliary witness with valid refutations. Thus a product-domain checker is not a prerequisite for this proposed arm. This conclusion does not authorize changing existing bounded-domain semantics.

The correction does not establish that the current wrapper already supports the arm. `verify_encoding_search` admits only `quartic`, `membership`, `quadratic` and `quadratic_aa`, and delegates their construction to the old builder. The current learned certificate is one flat multiplier polynomial per generator; its verifier has no DAG node semantics. Both implementation dependencies named in the design remain real.

## Projection equivalence and circuit counts

For odd prime `p`, `p < 2^k < 2p`, so reduction of k-bit integers modulo p is surjective and each residue has one or two representatives. Each triangular field equation fixes its output residue from already fixed parent residues. Consequently any satisfying Boolean extension obeys the specified field circuit even if some wires use the second representation.

Euler's criterion gives `W` in `{0,1,-1}` for the computed RHS and exponent `(p-1)/2`. Since p is odd, `W(W-1)=0` holds precisely in the square-or-zero cases. Conversely each accepted coordinate has canonical k-bit encodings for all uniquely determined field wire values. Preserving the same quartic therefore preserves exactly the projected solution set of the stated quartic-plus-membership system. This conclusion is conditional on the new builder actually authenticating that same quartic and the stated membership meaning; the old membership source was outside the assigned inspection scope.

The wire count is correct: U and Q contribute two wires, the remaining exponent bits contribute `ell-1` squarings and `popcount(e)-1` multiplies, yielding `K=ell+popcount(e)`. The initial Q accumulator requires no extra wire. Thus there are `2s+2Kk` bits and `1+2(K+1)` generators. All exponent edge cases under p>3 have positive exponent and a well-defined final W. The note's additional discriminant-redundancy sentence is not needed for this proof and is not separately endorsed by this restricted review.

## Conditional ideal-membership proof and degree

After restricting x to u, `G_U=U-u^2=E_U`. With `c_Q=u^3+au+b`,

`G_Q + u E_U = Q-Uu-au-b + u(U-u^2) = Q-c_Q`.

For a gate with `G_j=Z_j-Z_a Z_b` and independently recomputed `c_j=c_a c_b`,

`G_j + Z_b(Z_a-c_a) + c_a(Z_b-c_b) = Z_j-c_a c_b = E_j`.

This cancellation holds also for a square, where a=b; dropping either of its two terms would generally be incorrect. When `c_W=-1`, `E_W=W+1`, and

`A-(W-2)E_W = W(W-1)-(W-2)(W+1)=2`.

Division by 2 is legal under the prime p>3 premise, proving the required identity. These identities hold already in the ordinary polynomial ring over the field, so also in its Boolean quotient. Every derived E_j is in the restricted ideal by induction; the final identity derives one without assigning auxiliary bits.

The degree-two claim is correct for this derivation using retained wire variables. Multiplication by a linear wire expression can be expanded into ordinary polynomial-calculus variable multiplications and linear combinations, each of degree at most two; the shorthand is not an unrestricted inference rule. The proof uses only the restricted x-circuit generators and acceptance equation. Its omission of the quartic and y-circuit is legitimate, and does not claim that all generators or all proofs of the full system have degree two. Expanded ancestor multipliers could have much higher degree and are not part of this bound.

## Cost, storage and implementation qualifications

With each E_j represented by at most k variable terms and a constant, a local product involves O(k²) coefficient pairs. Each gate polynomial has O(k²) terms; final acceptance and multiplication have the same bound. Summing K local steps gives O(Kk²) field-term work, provided the verifier uses the prescribed checked-node representation and never expands the ancestor multiplier dictionaries. This is an upper bound, not measured work or a runtime estimate.

The qualification in design lines 48–50 is necessary and substantially adequate: parsing, masks, arithmetic bit complexity, authentication, source hashing, transcript evaluation and coverage remain additional charged work. In particular, a naive call through the existing adapter would parse/restrict all generators and use flat certificates; the local bound is not a demonstrated property of that implementation. Restricting or rebuilding all authenticated generators, including the quartic, must remain outside the local bound and inside total accounting. For the stated quadratic circuit and quartic expansion, O(Kk²+s^4) is a conservative algebraic term-count bound; it is not independently measured construction work for the uninspected legacy builder.

The O(K) count for recomputing circuit constants treats field operations as primitives. An inverse of 2 may be supplied and verified with constant field work, or for odd p constructed as `(p+1)/2`; a generic inversion routine's cost must not silently be counted as a fixed number of bit operations. The stated mask costs matter because a monomial key can occupy n bits even when its degree is only two. Accordingly O(k²) temporary terms and O(Kk) retained linear terms are term counts, not byte-space bounds. Parsed input and authenticated generator storage are additional, as the note states.

The adversarial obligations are coherent but not an executable serialization contract yet. Before an implementation can be accepted, its exact schema must settle duplicate/unknown fields, duplicate masks, noncanonical integers, size enforcement before expensive allocation, exact circuit schedule, source/layout binding and handling of every certificate kind. A hash alone is insufficient authentication if the producer can substitute both the polynomial and its hash: the verifier must rebuild from or compare against its trusted frozen arm definition. These are implementation acceptance conditions, not counterexamples to the mathematics.

Primality is also an actual external premise. The inspected adapter explicitly returns `prime_field_verified=False`; its input checks do not discharge the new design's verified-prime requirement. The future authenticated wrapper must obtain that premise through a trusted validation path or state its conditional contract explicitly.

## Completeness and useful scope

A depth-s rejection proves absence of every auxiliary witness for that full x value, including all aliases. A depth-m model cylinder establishes existential success for one projected pair. The existing coverage trie can combine these kinds once their separate mathematical obligations are discharged. The proposed rejection family supplies no certificate for an invalid pair whose x RHS is square or zero. Complete-transcript acceptance therefore requires actual trie coverage; the design correctly preserves censored outcomes and requires a new specification for any additional rejection kind.

Membership depends on the curve and coordinate, not the target point. With a factor base already restricted to square-or-zero RHS, these rejection certificates remove no further coordinates. The reviewed contribution is a table-free membership representation and a compact conditional derivation for nonsquare full-x fibers. Evaluation of any practical benefit must retain the same prefiltered baseline and charge construction, preprocessing, parsing, proof, search and coverage work.

The bounded next design action is justified: explicitly record the removal of the alleged product-domain prerequisite, then specify the new arm builder and specialized DAG verifier/wrapper interface with the authentication and cost conditions above. This review approves neither implementation execution nor changes to other leads or canonical research status.
