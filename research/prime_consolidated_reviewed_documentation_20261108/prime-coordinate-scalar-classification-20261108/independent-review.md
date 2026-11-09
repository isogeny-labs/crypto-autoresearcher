# Independent written mathematical review

Recommendation: accept the stated mathematical classification and coverage corollary as source-static derivations, with the qualifications below. No substantive algebraic defect was found. This recommendation is not runtime validation, independent experimental replay, or official scientific promotion.

## Frozen inputs and method

Read and hash-checked inputs:

- `review-plan.json`: `dea45ee0eab62d956b8f21c4d2df29ec1e0984cb530b94bf1919cab95e3a507d`.
- `derivation-v1.md`: `9c0ab07b730b47b844bee73abd7d06df9c7159326fd9a48d87d2f0966d6cf976`.
- Additional frozen `coverage-addendum-v1.md`: `0defea22ad9011500bf11644709d3ea88c8e524eb9a03bfb26ea7955bb61c2e8`.

Inspected the cited encoding construction, certificate checker, prefix adapter, counted engine, and separate transform compiler as text. All checks below are handwritten mathematical reasoning and static source comparison. No candidate imports, symbolic execution, tests, experiments, solver/oracle calls, or Git operations were performed. Only this review file was written.

## Mathematical findings

1. **Scope and original-generator obstruction: correct.** Work over F_p with p prime greater than 3, s at least 1, 2^s at most p, and t nonzero. The builder checks the curve equation, nonsingularity, digit bound and nonzero target ordinate, but not primality. Its lifted auxiliary width is `p.bit_length()` and its domain excludes exactly the encoded integers at least p. Thus auxiliary values 0 and 1 remain admissible. Projected restrictions cannot remove the singleton coefficient 1 of auxiliary bit zero in L²-S, or the nonzero singleton coefficient C2^i in CL-H. Alternatively, holding projected values fixed and comparing L=0 with L=1 gives generator differences 1 and C. Neither original lifted generator is a scalar under a projected-only restriction, even on the allowed auxiliary domain. This is only a statement about individual original generators.

2. **Elimination signs and transport: correct.** Direct cancellation yields

   C²(L²-S) - (CL+H)(CL-H) = H²-C²S.

   Substitution of C²=4(r³+ar+b) gives exactly the quartic in `encoding.py`. If its Boolean restriction is a nonzero scalar c, the two proposed multipliers give identity 1. They must be reversed for `quadratic_aa`, whose generator list is reversed in the source. The unrestricted identity is an ordinary-polynomial identity; scalarity after bit restriction and the resulting checked certificate are interpreted in the Boolean quotient. No auxiliary assignment or use of the auxiliary range clauses is required for this identity.

3. **Degree bounds: correct upper bounds.** In bit variables L is linear, H has degree at most two, and both lifted generators have degree at most two. The multiplier degrees are at most zero and two; their products therefore have degree at most four before Boolean reduction. After either whole coordinate is fixed, H becomes affine and CL-H has degree at most one; both products then have degree at most two. Further cancellation can reduce these degrees. These bounds do not assert that a particular bounded PC search discovers the multipliers, nor measure regularity or runtime.

4. **Univariate coefficients and scalar-cylinder bound: correct.** Set D=ru+2r²+a and h=u-r. Then

   E(u,y)=h²y²+(-2hD-C²)y+D²-C²(u+r).

   The middle coefficient expands to the stated B. If h is nonzero the polynomial E(u,y)-c is genuinely quadratic; if h=0 it has nonzero linear coefficient -C². A bit subcube with two free y bits supplies four distinct coordinate values, because all encoded coordinates lie in [0,2^s) inside [0,p). Fixing any permitted x completion contradicts the at-most-two-root bound. Symmetry gives at most one free bit in each coordinate, hence at most four projected assignments. This argument applies to any scalar c, including zero; refutation additionally requires c nonzero. It gives a necessary bound without claiming attainable four-point cylinders.

5. **Ordered prefix and one-free-bit criterion: correct.** For s at least 2, an x-first prefix of depth less than s leaves all s y bits free and cannot be scalar. A scalar prefix must therefore fix all x bits and all but at most one y bit, giving depth at least 2s-1 and at most two projected assignments. For y=y0+wz, reduction by z²=z makes the coefficient of z equal to w(2Ay0+Aw+B), exactly as stated. The constant is Ay0²+By0+K. At u=r the coefficient is wB, which is nonzero. For s=1 the derivation correctly retains only the general bound. The lift transport has the same projected cylinders because its premise is scalarity of this same restricted E.

6. **Discriminant: correct.** From the compact coefficients above,

   B²-4AK = C²[4hD+C²+4h²(u+r)]
             = 4C²[hD+t²+h²(u+r)]
             = 4C²(u³+au+b).

   A nonzero nonsquare RHS cannot occur at u=r, where the RHS is t². In that nonsquare case A is nonzero and the discriminant is nonsquare, so E(u,y) has no field root.

7. **Membership semantics and local construction: correct.** Under the prime-field assumption the builder's predicate is exactly the indicator of nonzero nonsquare RHS. It is a Boolean-valued function represented over F_p. Its restriction is polynomial 1 in the Boolean quotient precisely when all surviving coordinate completions have predicate value 1, by uniqueness of multilinear representation on the Boolean cube. A full invalid x thus admits a certificate with multiplier 1 on M_x and zero on the other generators, excluding all 2^s partner values. Zero RHS is correctly allowed. This is broader pruning than direct scalar E for the nonsquare-coordinate case; it does not establish superiority over arbitrary polynomial certificates. The source builds each predicate with 2^(2s) entries and a transform on 2s bits. For any irrelevant bit, paired values are equal, so their Möbius difference is zero. A transform on the relevant s bits followed by mask embedding therefore yields the identical polynomial. This is an exact design argument, not an implementation or measurement.

8. **Coverage addendum: correct with its explicit restriction.** For each of M=2^s x values the nonzero polynomial E(x,y) has at most two roots, so every set of valid projected pairs satisfying E=0 has cardinality at most 2M. Hence at least M²-2M projected pairs are invalid. If every invalid pair is covered solely by the stated nonzero-scalar E cylinders or their explicit transport, the union bound forces at least ceil(N_bad/4) arbitrary-subcube clauses, or ceil(N_bad/2) prefix clauses for s at least 2. Overlap cannot improve this cardinality bound. For M at least 4, M²-2M is at least M²/2, giving concrete lower bounds M²/8 and M²/4 respectively and the stated uniform Omega(M²) consequence along growing eligible instances. No infinite parameter-family existence claim is needed for the per-instance inequalities. If invalid pairs with E=0 exist under a different validity convention, this restricted family cannot cover them at all; the conditional lower bound remains true but is not a coverage-existence theorem. When other proof families cover pairs, use the actual number left to this family rather than silently retaining the global N_bad bound.

## Source and integration qualifications

- The adapter checks canonical bitmask polynomials and computes products by bitwise mask union, matching the Boolean quotient. It requires the multiplier count to equal the generator count and verifies that their sum is exactly `{0: 1}`. Its learned-clause format fixes the contiguous initial bit segment. A standalone y-only or arbitrary-subset clause is not directly representable in that format. Prefix-compatible refinements remain possible, at a potentially different coverage cost.
- The source checks projected coverage separately from polynomial identities, validates model/domain membership, and reconstructs EC witnesses through the encoding wrapper. These are independent obligations; the elimination formula alone does not discharge complete transcript, chart, or witness validation. Auxiliary-dependent clauses cannot simply lose auxiliary literals.
- The counted fallback restricts all n bits and emits depth-n clauses. Its configured standard coordinate schedule is `{0,s,2s,n}`. In particular it does not schedule depth `2s-1` for s greater than 1. The proposed one-free-bit certificate would need producer/scheduling work even though the transcript checker can represent that prefix. The note's assertion that the construction is not yet implemented is supported.
- Certificate checking explicitly charges all generator/multiplier term pairs. Construction, inverse, predicate, transform, embedding and storage costs still require explicit accounting in any implementation. The review does not infer a runtime improvement from the smaller proposed truth table alone.
- The inspected separate transform compiler has its own projection, auxiliary and range-bit compilation. The coordinate theorem has not been proved for those coefficient charts. The numerical inventory “106 coordinate cells” and “six separate coefficient charts,” producer-slot custody, and overall five-lead completeness were not independently verified from the limited cited source scope. Treat those as supplied administrative context rather than findings of this review.

## Recommendation and allowed conclusion

Retain the two-generator identity, degree upper bounds, scalar-cylinder classification, one-free-bit condition, discriminant explanation, membership representation argument, and restricted-family counting corollary as independently checked written mathematics under the stated assumptions. No correction of their central formulas is required. Make the omitted `2s-1` scheduled depth explicit when designing a producer, and keep inventory/custody assertions separately evidenced.

The next source-only design can specify canonical multiplier construction, prefix selection and full cost accounting, or the support-local membership constructor. This review supplies no authorization to execute it and makes no statement about measured performance, broad PC lower bounds, or official research status.
