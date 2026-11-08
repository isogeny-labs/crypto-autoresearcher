# Independent review: higher-arity bounded trace parameter

Verdict: **accept with qualifications as a source-static mathematical design and affine-invariance statement**. No concrete algebraic or counting defect was found in the dispatched claims. The coefficient-grid counts and partial-prefix counts are exact within their stated domains; they are not measured search improvements or counts of valid relations. The transform and smaller-range checker remain unimplemented dependencies.

## Inputs, provenance and scope

The frozen input hashes were checked by static reading and SHA-256 hashing:

- `design-v1.md`: `df7984e8f6cf5fb5006c0f7e6506856514fd39c7cdddf19ee40777eb1ca64aa2`.
- `review-plan.json`: `e723ab52737e1029a616a76531e96ad9a01902641255eee6ac473a3460a55d27`.
- `degree-addendum-v1.md`: `6bb49b231733cd240cd38ff1a36716a419c2eb40581be8a2f284338821dedcfc`.

The following internal primary sources were inspected as text, with these exact hashes:

- `research/prime_sat_shared_signed_chart_20261030/charts.py`, `basis` and `chart_spec`: `c808c7d3a5a2a96316a0c13c9faafd848406ef44e960a1bcc52bde700e6a818b`.
- `research/prime_sat_full_chart_composition_20261101/composition.py`, `descriptor`, `canonical_chart`, `_power_chain`, `compile_chart`: `354d6eef9695477f5c3ab2e9acc274241848f25a863dac30d2e5eb0def68c3b9`.
- `research/prime_sat_transform_integration_20261103/transform.py`, `build_transform` and compilation/authentication paths: `f78a9dae57be3cd8a6f0146b62ea19e2e4fc9665b0b514a2626a863fb4330948`.
- `research/prime_sat_range_corrected_20261101/compiler.py`, `substitute_equations`, `compile_range` and bit reconstruction: `8501e320de27169cebc35f678759b5e33a3d7c76c86dc4bb5caf329a2e12fdd7`.

This review checks the design against those sources, not external novelty or literature priority. It does not validate the separate rationality templates or signed-recovery implementation. No candidate imports, tests, enumeration, experiments, Git operations, identifiers or canonical edits occurred. Only this review was authored.

## Normalizations, trace and target pivots

`basis(d)` orders A_i by weight 2i and B_j by weight 2j+3. `chart_spec` sets d=h+1 for finite targets and c=(-1)^d. `canonical_chart` assigns coefficient one to the final basis element, registers earlier elements as projected variables in that order, and emits the norm and target equations stated in the design.

The highest relevant norm coefficients are therefore:

| h | normalized highest coefficient | coefficient of X^h in A²-fB_poly² | coefficient of X^h in c(X-a)U | residual |
|---|---|---|---|---|
| 3 | A2=1 | 2A1-B0² | u-a | 2A1+a-u-B0² |
| 4 | B1=1 | A2²-2B0 | a-u | A2²-(2B0+a-u) |
| 5 | A3=1 | 2A2-B1² | u-a | 2A2+a-u-B1² |

The curve coefficients alpha and beta do not enter these highest rows. Thus the common equation `u=a+2v-q²`, the signs of `w-q²`, and the Vieta trace `-u` are correct. The original projected orders in the note agree with the source.

The target equation has coefficient one on A0. Substituting each normalized A and B gives exactly the three displayed A0 formulas. There is no division by a or b; zero target coordinates introduce no pivot singularity. The only division in the subsequent trace change is by 2, justified by p>3.

## Strata and candidate-grid counts

The source emits B0=B1=0 for zero strata, B1=0 with B0 times an inverse equal to one for constant strata, and B1 times an inverse equal to one for linear strata. Hence h3 admits zero/constant only, h4 admits linear only, and h5 admits all three, exactly as stated. Impossible normalized strata must remain impossible under the transform.

After the target pivot, the old projected coefficient counts are p², p³ and p⁴. Replacing one free v by a range-R_h z0 and forcing the auxiliary w=q² yields pR3, p²R4 and p³R5. The precise nonempty strata give:

| h and stratum | old grid | new grid |
|---|---|---|
| 3 zero | p | R3 |
| 3 constant | p(p-1) | (p-1)R3 |
| 4 linear | p³ | p²R4 |
| 5 zero | p² | pR5 |
| 5 constant | p²(p-1) | p(p-1)R5 |
| 5 linear | p³(p-1) | p²(p-1)R5 |

These counts concern declared parameter tuples after the named pivots and stratum constraints, before imposing all other equations. They do not assert that every tuple admits interval, rationality or signed-divisor witnesses. The exact ratio R_h/p is valid for those grids only. Counting w as another free projected coordinate would invalidate the ratio; the proposed representation correctly keeps it auxiliary and forced.

## Interval implication and residue boundaries

The idempotent and modular product equations in `canonical_chart`, together with `_power_chain`, imply N^h=0 modulo U for h=3,4,5. At any algebraic-closure root xi of U, each idempotent evaluates to zero or one and N(xi)^h=0 implies N(xi)=0. Thus xi=t+d_i with 0<=d_i<B. This argument also applies to repeated roots; Vieta counts their multiplicities.

Every integer between zero and h(B-1) is a sum of h integers in [0,B-1], independently of whether that tuple yields a valid curve relation. Reduction of this integer interval has the stated image `[0,R_h-1]`, where R_h=min(p,D_h+1). This establishes the necessary domain bound, not an interval-support converse or attainment by actual charts.

The three thresholds are correct. D_h<p gives injectivity of integer sums. D_h=p-1 already fills all p residues despite injectivity. D_h>=p permits aliases and also fills all residues. Strict domain reduction requires D_h+1<p. Translation of the interval through zero modulo p does not alter these conclusions, because the d_i are interval offsets. Raw integer-sum encodings after saturation would create aliases rather than more original coefficient candidates.

## Affine substitution, degree and projected bijection

For old coordinates ordered (v,u), the linear part of `(z0,w)=(-u-ht,2v+a-u)` is `[[0,-1],[2,-1]]`, with determinant 2. Its stated inverse is exact. Replacing the existing pair by two new variables therefore adds no field variable, and substituting affine forms into polynomials of degree at most two preserves that upper bound. The target pivot is affine as well. Eliminating v directly through q² in other quadratic rows would be a different operation and can produce degree four; the proposed retained w avoids that problem.

All source equations, including stratum inverse equations and auxiliary product equations, must receive the substitution. Preserving only norm rows would not prove equivalence. A0 elimination removes its variable separately; variable-count preservation refers specifically to the pair change after that pivot.

Although the pair change mixes a projected and an auxiliary coordinate, the top norm row fixes old u from original projected coefficients. Therefore the forward projected map is `z0=q²-2v-a-ht` with other retained projected coefficients unchanged. In the reverse direction, w=q² and the inverse affine formula recover v, and the target pivot recovers A0. Both maps are independent of choices of other auxiliary witnesses. The interval implication places every old solution inside the new z0 bound. Literal substitution of every retained equation maps every new solution back to an old solution. This proves bijection of valid projected sets, not merely equivalence of full assignments.

## Highest-part Hilbert invariance

The addendum is correct with its stated scope. For any nonzero original polynomial f of degree d, substitution by the inverse affine map produces highest homogeneous part `f_d` composed with the inverse linear part. An invertible linear substitution is injective, so this component cannot disappear. The graded automorphism carries the ideal generated by the original highest parts to the ideal generated by the transformed highest parts. The graded quotient Hilbert functions agree degree by degree.

This proof requires transforming the full original generator list and using the same ambient number of field variables. Zero generators can be ignored. It does not extend automatically to A0 elimination, row replacement/removal, newly added bounded-domain equations, or Boolean compilation. It establishes neither identical algorithmic costs nor equality for every convention called degree of regularity. The addendum explicitly preserves these distinctions and correctly avoids attributing an intrinsic highest-part improvement to the affine change alone.

## Source gaps and exact prefix scope

The current `build_transform` supports nonidentity operations only for finite arity-two constant-B strata and binds their exact rows. It does not implement the proposed higher-arity formulas. `substitute_equations` requires every field value block to have `(p-1).bit_length()` bits and every source monomial to have degree at most two. For these odd primes that width equals ell. `compile_range` supplies the canonical bound below p, not a per-block bound below R_h. Thus the design fits the algebraic degree restriction but still requires an authenticated transform and a smaller-range constraint/proof mechanism.

The source assigns weight 2^j to position j within each block, so the LSB-prefix analysis applies. For d<=floor(log2 p)=ell-1, every one of the 2^d prefixes extends to a canonical field value by choosing that small integer itself. Consecutive allowed integers 0 through R_h-1 occupy min(R_h,2^d) prefixes. Exactly max(0,2^d-R_h) canonical-completable prefixes therefore fail only the proposed small bound. This verifies the strict early-rejection threshold 2^d>R_h. If R_h>=2^(ell-1), no such rejection occurs before the last field bit, even when R_h<p.

These are local prefix counts for a z0-first block, not a claim about solver propagation or realized runtime. At full width the canonical-domain comparison changes: only p strings are canonical, and p-R_h of those violate the smaller bound. The note correctly confines its partial-prefix formula to d<=ell-1.

In the alternative q-first layout, the map from z0 to v is injective, giving R_h allowed v values per fixed q. The existing projected orders put v before q in each of the three cases and also put A0 first, so the proposed contiguous-prefix use requires an explicit layout change. Explicit set construction costs O(R_h) field entries per q, with bit/mask/serialization costs additional. It is not the arity-two global bounded-slope construction.

## Acceptance qualifications and next design gate

No correction is required to the reviewed identities, counts or invariance statement. Before implementation admission, freeze the literal row maps and inverse, trusted source/layout/stratum bindings, removal identities for target or zero rows, and exact smaller-range certificate format. Hashes supplied by a producer alone are insufficient authentication. Primality remains a caller premise in the inspected sources and must remain an explicit trusted dependency.

Choose a descriptor with R_h<p for a domain-count benefit; additionally require R_h<2^(ell-1) if the claimed mechanism is rejection before the final bit in the proposed LSB layout. Preserve the remaining chart obligations and both stated baseline families. The justified next step is the bounded source design for that authenticated transform and range/coverage interface, with construction and verification costs specified. This review authorizes no experiments, slot reuse or canonical status change.
