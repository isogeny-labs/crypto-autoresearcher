# Cheap conditional moment-prefix exclusion without a moment grid

This is an additional mathematical proof design, not an implemented native SAT proof format. Retain original coefficient projections, including q; E0 may remain an auxiliary. No h3 projection is collapsed to its moment pair.

Fix the FULL canonical first-moment residue S0 in0..p-1. Integer lifts in0..hM are S=S0+lp. Since M<p and h<=5, hM<hp, so there are at most h such lifts. If S0>hM when hM<p there are none, and that whole first-moment assignment is impossible.

For each lift, compute the exact Emin(S),Emax(S) formulas already derived. If the interval length is at least p, its residue set is the whole field. Otherwise its residue image is one canonical arc[L,U] inside[0,p-1], or two arcs if it wraps modulo p. There are at most2h arcs before optional merging. They describe the union of necessary interval supersets, NOT the exact attainable-moment set.

For a Boolean LSB prefix of E0 with depth0<=d<=ell and value0<=r<2^d, write H=2^d. Its canonical completions are integers r+Hj in[0,p-1]. It meets an arc[L,U] precisely when

    ceil((L-r)/H) <= floor((U-r)/H).

No separate lower bound j>=0 is missing: L>=0 and r<H imply ceil((L-r)/H)>=0. The arc upper bound automatically ensures the resulting integer is below p. If r>=p (possible at depthell), no canonical completion exists and all arcs miss. At d=0, r=0,H=1 and every nonempty arc intersects. If any lift interval has width>=p-1, the union is the whole field and no canonical-completable prefix can be rejected.

Therefore reject the conditional partial assignment iff EVERY arc misses. This test is exact for intersection with the necessary interval superset. A passing intersection is not evidence of an actual offset multiset or chart root. A rejected prefix has no admissible integer-moment witness and therefore no valid chart witness under the authenticated interval/source theorem.

Computing at most h lifts, their closed-form endpoints and at most2h intersection tests uses O(h) integer arithmetic operations. For fixed h<=5 their operands have O(log p) bits (E endpoints are O(h²p²)); multiplication/division/ceil/floor bit cost is charged, not declared constant time. No coefficient loop, offset tuple enumeration, field-root extraction or traversal of all moment pairs occurs in this predicate. Reading the fixed S block, E prefix, chart bindings and constructing the clause costs O(ell) literals/bit processing plus authentication. Repeated queries may cache arcs only for the same authenticated S0/curve/interval/arity binding, with cache costs recorded. No rejection-frequency or runtime-advantage claim is made.

The learned clause is the negation of the conjunction of ALL fixed S0 bits and the d assigned E-prefix bits. It excludes every remaining variable assignment because the moment premise is necessary. However these literals may not form a contiguous global prefix: E can be auxiliary while other projected coefficients remain unassigned. The current prefix-only transcript checker and DRAT/RUP mechanism do not automatically accept this semantic clause. A future authenticated lemma interface must bind exact source normalization, interval idempotent/nilpotent theorem, moment definitions, canonical field ranges, fixed S0 and E bits, independently recomputed arcs and the missing intersections; or an independently checked derivation from the original CNF is required. Full projected coverage, all other polynomial/model/witness checks and original chart strata remain unchanged.

Controls: empty lift list rejects at depth0; full-field arc rejects no canonical-completable prefix; wrapping arcs are both retained; d=ell checks a single canonical residue; noncanonical r>=p is excluded by the original field domain. The interval-hole and moment-collision controls from controls-addendum-v1.md ensure no passing predicate is promoted to exact support or a unique relation. This is the ranked next proof-design mechanism because it applies the bounds WITHOUT paying for a moment grid. It still needs separate source implementation/admission before any execution.
