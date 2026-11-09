# Independent second-moment mathematical review

Recommendation: accept the mathematical construction, controls and deterministic baselines with the saturation and scope qualifications below. No substantive defect was found in the coefficient identities, moment extrema, conditional recovery counts or baseline completeness arguments. This is written source-static review, not an empirical performance result, implemented checker validation, execution admission or official promotion.

## Frozen inputs and method

All supplied SHA-256 values were checked and matched:

- `design-v1.md`: `7d70d2e285b2a80bea3007b270f270a3e1b030dbf96d6beaa0dfcb56c08ae846`.
- `baseline-v1.md`: `adb5d8cc259baa8b64709fb09960bdf0f230d4ae966fba62dc238d70e1561cda`.
- `review-plan.json`: `a2870e3dfa7f671fe53d89a35aa3ed568486ab36b6cdbdf97b6cce7010561fad`.
- `controls-addendum-v1.md`: `ac77f640a7f2604f74313d5d546f49f8c4c3dd220ad41007bd159b90a76e3cd3`.

Inspected the normalized basis and chart specification in `research/prime_sat_shared_signed_chart_20261030/charts.py`, norm/target/interval generation in `research/prime_sat_full_chart_composition_20261101/composition.py`, and source degree/width checks in `research/prime_sat_range_corrected_20261101/compiler.py`. Checked the algebra and counting by hand. No imports, candidate execution, enumeration, tests, solver calls, implementation, Git operations, IDs or canonical edits occurred. Only this review file was written.

## Source coefficients and conditional recovery

For finite target, the source uses pole order h+1, normalizes the highest-pole basis element to one, and sets c=+1 for even pole order and -1 for odd pole order. Thus the three A/B-polynomial forms in the design match the source. Norm generation is exactly A²-f B_poly²=c(X-a)U, and the target row is A(a)=b B_poly(a).

- For h=3, the X³ coefficient is 2v-q²=u-a, and the X² coefficient is v²+2A0=j-au. The target equation gives A0=bq-a²-av. These establish the displayed j identity.
- For h=4, the X⁴ coefficient is q²-2v=a-u. The X³ coefficient is 2qA1-v²-alpha=au-j. The target equation gives A0=b(a+v)-a²q-aA1. Both trace and second-coefficient signs are correct.
- For h=5, the X⁵ coefficient is 2v-q²=u-a. The X⁴ coefficient is v²+2A1-2qB0=j-au. The target pivot A0=b(B0+aq)-a³-a²v-aA1 is correct.

These are identities in the stated prime field and do not divide by a or b. They do not dispense with the remaining norm, support, stratum or witness equations.

For h=3, substitution of v=(q²+u-a)/2 yields the design's quartic. Its equivalent expanded form is

    q⁴+(2u-6a)q²+8bq+u²-2au-3a²-4j=0.

The leading coefficient is one in every allowed characteristic. Therefore each fixed (u,j), hence fixed residue moment pair, admits at most four q values in F_p. Each retained q uniquely fixes v and A0 through these rows. This is a bound on candidate coefficient tuples, not proof of their feasibility, uniqueness of support, or an algorithm for finding all roots. Complete field-root extraction must retain every root, including repeated-root cases without confusing multiplicity with distinct coefficient candidates.

For h=4 and q nonzero, division by 2q gives a unique A1 and then A0. At q=0 the second coefficient instead fixes j0=au+v²+alpha, leaving A1 unconstrained by the reviewed rows. If its forced moment residue is allowed, all p A1 choices must reach subsequent checks. The normalized B_polynomial=X+v remains linear in this branch, since q is an A coefficient. The design correctly avoids dropping this branch or treating a rational pivot as affine.

For h=5, the denominator is only 2, so A1 is uniquely determined by (S,E,q,B0), including q=0. The original B-polynomial strata remain distinct and must be enforced.

## Integer moments, residue lifts and identifiability

Vieta gives u=-ht-S and j=C(h,2)t²+(h-1)tS+E modulo p. Each d_i occurs h-1 times in the mixed pair sum. The integer identity 2E=S²-Q is correct and is used before reduction modulo p.

The Q extrema are sharp. At fixed integer sum, repeatedly balancing any pair differing by at least two decreases Q until all entries differ by at most one, yielding Qmin=(h-r0)d²+r0(d+1)². Conversely, transferring mass between two interior entries toward an endpoint increases Q until at most one interior entry remains, yielding Qmax=cM²+r². The proposed configurations satisfy the box and sum constraints. At S=hM, c=h and r=0 correctly gives h full entries with no additional coordinate. For B=1 all offsets and both moments are zero; division by M must not be attempted. Parity ensures both E extrema are integers.

These extrema do not characterize attainable intermediate values. The h=3, B=4, S=3 control is correct: the three unordered partitions give E=0,2,3, with 1 absent. Its role is a hand-derived counterexample to interval exactness, not an exhaustive computation over instances.

A consecutive integer interval of W+1 values projects to exactly min(p,W+1) distinct residues. If W>=p-1 every field residue is admitted by that bound. For hM<p the S residue has a unique feasible integer lift. Otherwise all lifts in [0,hM] must be considered, and the safe condition is the union of their residue intervals. The mixed tS shift is unchanged modulo p across such lifts, but the conditional extrema need not be. The design correctly distinguishes these cases and charges lift handling.

The identifiability control is also correct: (0,3,3) and (1,1,4) both have S=6 and E=9, while they are different unordered multisets. They lie in the B=8 interval, and zero padding preserves both moments for h=4 and h=5. This refutes reconstruction of a unique interval support multiset from these two moments alone. It does not assert simultaneous realizability for one fixed curve and target. The conditional coefficient quartic can coexist with this interval-domain noninjectivity because it uses additional source identities and claims only a candidate bound.

## Representation and enumeration counts

The displayed affine change and inverse are correct: substituting u=-ht-S0 into E0=j+(h-1)tu+C(h,2)t² cancels the shifts and recovers j=E0+(h-1)tS0+C(h,2)t². Its linear part is invertible without division by h. It remains valid when the characteristic divides h or C(h,2). Applying a genuinely invertible affine substitution to all degree-at-most-two field rows preserves that degree bound. It neither removes a variable nor automatically changes a projected variable into an auxiliary with valid recovery.

Solving for A1 in h=5 is quadratic and substituting it into quadratic rows can create degree four. The h=4 formula is rational on a verified nonzero-q branch. The source compiler explicitly requires field monomials of degree at most two and its canonical field bit width. Thus neither an eagerly expanded higher-degree system nor a new role/layout is automatically supported by the existing interface. Retaining a determined auxiliary and its equation avoids the asserted eager-degree increase, but still needs an authenticated representation design.

In the injective-S regime, A_h=sum_S min(p,W_h(S)+1) is exactly the size of the necessary residue-pair envelope, not the feasible moment set. The candidate counts follow:

- h=3: A3 quartic problems and at most 4A3 coefficient candidates.
- h=4: exactly (p-1)A4 formal nonzero-q parameter tuples before other rows. The zero branch contributes pN0, with N0 counting sums whose single forced E residue is admitted and 0<=N0<=hM+1.
- h=5: exactly p²A5 unstratified formal parameter tuples. The q=B1=0, B0=0 stratum contributes A5; q=0, B0 nonzero contributes (p-1)A5; q nonzero with arbitrary B0 contributes p(p-1)A5. These sum to p²A5.

The aggregate asymptotics are justified for fixed h and growing B under hM<p. There are O(B) sums and each width is O(B²). For a constant-fraction band S in [M/2,M], Qmax=S² and Qmin=S²/h+O(h), so widths are bounded below by a positive h-dependent constant times B² for sufficiently large B. There are Theta(B) such sums. After truncation at p this proves A_h=Theta(B min(p,B²)). If p grows faster than B², A_h=Theta(B³). These asymptotic statements exclude the separate B=1 boundary and do not assert parameter-family existence beyond their stated conditional regime.

Qualification: the sentence about reductions vanishing under saturation should be read rowwise. At a sum S with W_h(S)>=p-1, this second-moment interval test allows every E residue and contributes no E pruning. The first-moment restriction can still prune, and other S values can remain unsaturated; indeed the endpoint sums have width zero. Saturation does not mean every benefit of the entire moment construction vanishes. The quantitative A_h formula already expresses the correct behavior.

## Complete direct and meet-in-the-middle baselines

Let F contain every signed affine point above the B interval coordinates, with a zero ordinate included once. Complete square-root extraction gives |F|=n<=2B. Preparation and all representation costs must be charged separately as stated.

For h=3, every ordered choice (P1,P2) determines exactly one group point P3=R-P1-P2. Rejecting final identity is necessary because factors are affine. Otherwise, since group arithmetic returns a curve point and F contains both signs, its interval x membership is sufficient for membership in F. Every ordered affine solution triple appears once for its first ordered pair. Intermediate identities and repeated points cause no incompleteness. O(n²+N) operation/output accounting is valid; in this case N itself is at most n².

For h=4, each ordered quadruple has exactly one ordered 2+2 split. A complete ordered-pair table retaining collisions and identity keys makes the equal-range lookup exhaustive. Every matching second pair must be emitted; keeping only one witness per sum would be incorrect. Deterministic sorting plus binary searches and full output traversal gives O(n² log(n+1)+N) operations and O(n²) records, with group-key bit costs additional.

For h=5, the same argument applies to each ordered triple followed by every matching ordered pair. The unique ordered 3+2 split prevents duplicate generation for that ordered tuple. O(n³ log(n+1)+N) operations and O(n²) records include setup for n>=1, and n=0 is handled separately. Repeated factors and identity intermediate sums remain allowed. Identity is a sum-table key, not an affine factor.

These are complete baselines for the stated ordered group-relation task. Mapping their outputs to chart projections, unordered outputs or deduplicated models requires the separately charged conversions and chart/witness checks. Consequently their completeness does not authorize silently equating raw ordered-output N with a projected-model count. Likewise the moment envelope counts and group-operation counts are different operation types. The supplied comparison correctly concerns pre-output enumeration pressure; it cannot establish a runtime ratio without matched costs and evidence.

## Scope and recommendation

Retain the sharp conditional moment inequalities, safe lift union, identifiability controls and at-most-four h3 coefficient result as reusable mathematical components. The reviewed counts support the proposed decision against scaling the full moment-pair envelope solely on these interval bounds. They do not exclude a cheaper online necessary-condition check or a construction exploiting more structure.

The source inspected here is an interval-chart source of arity at most five. No transport to the retained six coset coefficient controls has been supplied or inferred. Their stated p17/degree8/16 inventory and the older k3-sharing prohibition are preserved as supplied scope constraints, not newly revalidated administrative facts. Existing all106+6/five-lead obligations and execution budgets remain unchanged. No native implementation, runtime or new scientific attempt is admitted by this review.
