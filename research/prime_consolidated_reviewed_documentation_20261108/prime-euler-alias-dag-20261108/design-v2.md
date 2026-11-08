# Alias-tolerant Euler wires and a stepwise conditional PC checker

Status: source-only mathematical design. No implementation, imports, tests, trials, IDs or canonical mutation. The previous coordinate classification and Euler design remain frozen. This note corrects a dependency in the latter, without changing its algebraic identities.

## Correction of the earlier domain requirement
The prior design required canonical representatives for every circuit wire and consequently identified a product-domain checker as an implementation prerequisite. Canonicality is OPTIONAL for projected-set semantics. Actual adapter.py `_domain` accepts domain_cnf=[] with aux_bound=None; model verification deduplicates projections rather than requiring a unique auxiliary Boolean witness. Its model prefix (m,projection) covers the entire auxiliary fiber after a single genuine model is checked. Therefore the full-cube option already supports the needed alias-tolerant domain semantics. A new encoding arm/authenticated wrapper and DAG proof verifier are still necessary: the old EC wrapper builds only its frozen encodings, and its learned-entry format accepts flat multiplier arrays, not this DAG.

Sources: research/prime_sat_prefix_adapter_20261030/adapter.py `_domain`, `verify_transcript`, `verify_encoding_search`; research/prime_sat_costbridge_controls_20261029/prefix_cover.py `verify_cover`; research/prime_sat_followup_20261029/encoding.py `build`, `reconstruct`. Mathematical provenance: prior mathematical-note-v2.md and euler-membership-design-v1.md with independent critiques in ../prime-coordinate-scalar-classification-20261108/.

## Fully specified new-arm field and Boolean semantics
Use the coordinate quartic E plus the two Euler circuits (one for x and one for y), replacing the table membership generators. Assumptions remain verified prime p>3, nonsingular curve, target (r,t) with t!=0 and t²=r³+ar+b, s>=1, 2^s<=p. This construction does not modify the six coefficient-chart encodings.

Set k=ceil(log2 p) (equal to p.bit_length() for these odd primes), m=2s. Keep x and y in the first s bits and next s bits. Each Euler circuit uses K=ell+popcount(e) field wires, where e=(p-1)/2 and ell=bit_length(e). Lay out all K x-circuit wire blocks, followed by all K y-circuit wire blocks, each k bits, in fixed topological order. Thus n=2s+2Kk. Each wire has field value Z=sum_i 2^i z_i modulo p, with ALL k-bit strings allowed. Use domain_cnf=[] and aux_bound=None. No range clauses or comparator gates.

For each coordinate X, equations in order are U-X²=0; Q-UX-aX-b=0; then square/multiply gates for left-to-right binary powering Q^e (initial accumulator Q is an alias, not a new wire); finally W(W-1)=0. Keep original quartic first, then all x-circuit equations including acceptance, then all y-circuit equations including acceptance. This gives1+2(K+1) generators. Finite field wire equations are triangular and determine unique FIELD values given X, but not necessarily unique bit strings.

## Projection-equivalence proof with aliases
The map {0,1}^k -> F_p is surjective because integers0..p-1 are represented. Any Boolean solution maps to a field solution of every circuit equation. Induction through the circuit gives W=(X³+aX+b)^e. Euler's criterion makes W(W-1)=0 equivalent to square-or-zero curve RHS; aliases cannot change a field value or this conclusion.

Conversely any projected pair satisfying the old quartic and its membership predicates has a unique field-value circuit extension. Encode each field value by its canonical integer0..p-1; those k-bit witnesses exist and satisfy every new equation. Thus the new Boolean system has exactly the old membership arm's projected model set. The discriminant argument also shows the added predicates are redundant for the valid quartic chart, but equivalence with the membership arm alone suffices here. EC witness reconstruction remains the old separately checked operation.

Any field value has at most two k-bit representatives because p<2^k<2p; many wires can nevertheless yield exponentially many combinations of aliases. No auxiliary-search or SAT-cost reduction is asserted. The producer may select the canonical extension for emitted models, but the verifier MUST accept any genuine bit witness and reject duplicate projected models. Canonical output preference is not a domain restriction. Blocking all aliases of an already checked model by the depth-m projected model prefix is exactly projected enumeration, not a claim that every auxiliary string in the blocked fiber is a root.

## Conditional proof format: full x coordinate only
This first design admits only rejection prefixes depth=s fixing x=u; it leaves y and ALL auxiliary bits free. It does not support arbitrary subsets, shorter prefixes, or a y-only clause in the x-first interface. Existing valid model prefixes remain depth=m. A later mixed-proof design must separately bind additional accepted certificate kinds; none are implicit here.

For a full x assignment with nonsquare RHS, let c_j be the circuit's field values, computed independently by the verifier using the same declared gate schedule but not any producer-provided polynomial result. Let E_j=Z_j-c_j. The required topologically ordered proof nodes are:

1. E_U=G_U after restriction of X=u.
2. E_Q=G_Q+u E_U.
3. For each square/multiply gate j with parents a,b:
   E_j=G_j+Z_b E_a+c_a E_b.
   A square has a=b; both terms are retained.
4. Require c_W=-1. For acceptance A=W(W-1), verify
   1=A/2-(W-2)E_W/2.

Every equality is in the Boolean quotient, and all generator leaves are the actual authenticated generators restricted by that EXACT depth-s prefix. Induction establishes each E_j lies in the restricted generator ideal; the final identity proves1 lies there. No ancestor multiplier polynomial is expanded. Each E_j itself is the sparse linear polynomial Z_j-c_j, not an unverified name or claimed field fact. The original quartic and all y-circuit generators are unused; an unused generator has zero coefficient logically.

A concrete verifier validates canonical integer masks/coefficient residues, declared dimensions/layout, generator identities and input hashes, exact prefix/clause agreement, and the frozen circuit schedule. It recomputes c_j and the expected sparse E_j, checks every local equality by direct Boolean-mask polynomial arithmetic, permits only earlier parent references with the exact gate indices, and finally checks the constant1 equality. Reject extra/omitted/reordered gates, foreign generator references, cycles, mismatched prefixes, wrong constants, malformed coefficients/masks, nonzero local residuals, or a non-minus-one output. Bound input bytes/nodes/terms by the declared schedule before allocating; refuse overlimits rather than partially accepting. No producer Boolean `verified` flag is authority.

This is a specialized PC DAG verifier, not evaluation alone: the checked polynomial recurrences establish ideal membership without assigning auxiliary bits. Scalar c_j computations specify the intended identities; explicit local polynomial equality checks anchor them to the supplied generators. A false prefix or stale source cannot be accepted merely because a claimed circuit evaluates to -1.

## Charged degree, work and storage bounds
After x is fixed, E_j is linear in k wire bits. G_U and G_Q become linear; other gates and acceptance have degree<=2. The local step multiplies two linear polynomials, and the final step does likewise, so the verified PC derivation has degree<=2 with retained extension variables. No assertion about flat expanded certificate degree, original-system elimination, or degree of regularity follows.

Each multiplication-step local check involves O(k²) field coefficient-pair operations plus O(k) additions for linear/scalar pieces; there are K wires and one final check. Thus O(K k²) FIELD TERM operations per full-coordinate conditional proof, without recursively expanding ancestor multipliers. Constants require O(K) field arithmetic, including constant2 inversion or its verified inverse. Counting both sides' actual terms and zero cancellations is mandatory; these are upper bounds, not measured counts.

This bound excludes neither costs nor input: separately charge parsing/byte validation; n-bit mask OR/hash/comparison; modular arithmetic bit complexity as a function of log p; generator authentication/building; O(s) prefix/clause processing; source hashing; input I/O; model evaluation, EC witness reconstruction and full coverage verification. It is a field-operation bound, not a bit-time bound. Since s<=k, authenticated construction of quartic and both gate circuits has O(K k²+s^4) term-pair work as a conservative bound for the existing quartic expansion; the quartic cost is not hidden in the per-proof O(K k²). Repeated authentication can be cached only against exact immutable generator/layout bindings with that caching cost recorded.

A streaming local check needs O(k²) temporary field terms; retaining all checked linear nodes/constants costs O(Kk) terms and indices. Parsing all expanded generator polynomials costs O(Kk²+s^4) stored terms under the straightforward representation (zero cancellations can reduce this). No constant-space total-check claim is made. The O(K) gate schedule is a compact DAG because parents refer to checked nodes, not expanded generator multiplier dictionaries.

## Transcript and complete-projection obligations
The new wrapper must authenticate the new arm, check all model polynomials, enforce unique projections, and invoke full-cube prefix coverage only AFTER each DAG rejection or genuine model is verified. A depth-s rejection proves no witness of ANY alias exists for that x fiber. A depth-m model prefix records existential success for that projected pair. The coverage trie accepts these cylinders independently of auxiliary multiplicity; no product-domain extension is needed.

This specialized rejection family covers nonsquare x fibers, not all invalid projected pairs. It cannot by itself justify a complete transcript when other bad pairs remain uncovered. Reject a false completeness claim; preserve censored/partial outcomes. Other rejection families require separately specified proof verification. The6 coefficient charts, all106+6 downstream controls, chart handling and five leads remain outside any new execution or completion claim.

## Useful-scope boundary
The Euler predicate depends only on the curve and coordinate, not on the target point. If the factor base has already been filtered to square-or-zero curve RHS, this predicate rejects no additional coordinate. This construction is a certified table-free representation of existing membership, not new target-dependent relation pruning. Any benefit must charge preprocessing, representation, proof and search overhead against the same prefiltered baseline; none is measured here.

## Bounded next action
Independently review the alias equivalence and local proof checker specification. If accepted, correct the earlier prerequisite explicitly: product-domain implementation is unnecessary for the full-cube alias-tolerant arm. The next source-only implementation proposal would own a new arm builder plus specialized DAG verifier/wrapper, with a frozen interface and counted terms; it would not alter existing arm semantics or weaken the old checker. No code, scientific slot, trial, retry, cloud operation, native ID or official status change is authorized by this note.
