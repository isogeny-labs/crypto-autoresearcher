# Supplemental nonblind review of conditional prefix arcs

Recommendation: accept the arc-intersection argument as a necessary-superset rejection design, with one explicit notation clarification: define ell as the canonical field bit width, ell=ceil(log2 p)=bit_length(p) for the assumed odd prime. No algebraic defect was found under this interpretation. No rejection-frequency, runtime, native-checker acceptance or scientific promotion claim follows.

## Inputs and review procedure

Read and hash-checked the two frozen supplemental inputs:

- `prefix-arcs-addendum-v1.md`: `ebd2e2c308631350a2d138bfae53db8959991724765f34343a2dcea2c4a01792`.
- `review-procedure-supplement.json`: `d35b319188df1d7f250edff1b3e86dc3d1391d492a32faf30758f04e10715949`.

This is an independent nonblind source/math critique. Producer text and prior related review context were visible. The supplemental prior was recorded after the original dispatch. The original plan omitted the prior, joint-owner, blindness and proves-too-much fields recorded by this supplement. The supplement documents those omissions; it does not retroactively establish a compliant blinded procedure. No blind rederivation was performed and no native scientific review gate is discharged. The original main review is preserved unchanged.

The checks below are written reasoning about the supplied addendum and the already reviewed moment formulas. No imports, code implementation, tests, enumeration, solver calls, Git operations or scientific execution were used.

## Mathematical checks

1. **At most h integer lifts.** For canonical S0, a nonnegative sum with that residue has S=S0+lp with l nonnegative. Since M<p, the maximum sum hM is strictly less than hp. Thus l lies among 0,...,h-1, possibly with some or all entries absent. There are at most h lifts. In the injective-sum regime hM<p, S0>hM gives an empty list. All valid lifts must be included; choosing only the canonical lift would reproduce the previously identified unsound restriction.

2. **At most 2h canonical arcs.** For each nonempty integer interval [Emin,Emax], length at least p gives the entire residue field. Otherwise its cyclic residue image is a single canonical interval or the union of two intervals straddling zero. Keeping both pieces is essential in the wrapping case. At most h lifts therefore give at most 2h arcs before merging. Overlap does not threaten soundness and need not be removed for intersection testing. If any lift gives the full field, the union can immediately be represented by [0,p-1]. These are interval supersets of attainable moments, not exact support sets.

3. **The prefix-intersection criterion is exact.** Write H=2^d and 0<=r<H. A completion meets [L,U] exactly when some integer j satisfies L<=r+Hj<=U, equivalently

       ceil((L-r)/H) <= j <= floor((U-r)/H).

   Since H is positive, an integer exists precisely when the stated lower endpoint is at most the upper endpoint. L>=0 and r<H imply (L-r)/H>-1, hence its ceiling is at least zero. Thus there is no omitted nonnegative-j condition. U<=p-1 already enforces canonical field range. The divisions must implement mathematical floor and ceiling, including for negative numerators; truncation toward zero is not interchangeable with these operations.

4. **Empty and full unions behave correctly.** With no feasible S lift there is no admissible moment pair, so rejection is justified even at d=0. If an arc is the whole field, it intersects every prefix with a canonical completion. Noncanonical prefixes can still miss that arc, which is consistent with the original range domain. A full-field arc does not assert that every moment is attainable; it says this particular necessary interval test cannot reject a canonical-completable prefix.

5. **Depth-zero and full-depth controls are correct with the field-width definition.** At d=0, r=0 and H=1, so every nonempty canonical arc contains a completion. Hence only an empty union can reject at this depth. At d=ell with H>=p, a prefix r<p has exactly one canonical completion, r, and the criterion tests whether that residue lies in the arc union. If r>=p it has no canonical completion and misses every canonical arc. The addendum does not explicitly define ell; the intended field-width definition above should be stated in any implementation specification or subsequent report. A generic unspecified ell would not justify the claimed single-residue full-depth control.

6. **Wrapping control is sound.** A wrapped cyclic interval is tested through both of its canonical pieces. Rejecting only when both pieces miss, and when every other lift's pieces also miss, is exactly rejection of intersection with the full necessary union. Treating a wrap as an ordinary interval with reversed endpoints or retaining just one piece would be unsound; neither operation is authorized by the design.

7. **The predicate is one-sided for chart validity.** Every valid interval chart supplies a feasible integer first-moment lift and an attainable second moment lying in its interval bound. Therefore missing the union excludes every valid chart witness consistent with the fixed S0 and E prefix. Intersection merely leaves the possibility open. The earlier interval-hole and equal-moment/different-multiset controls remain applicable: neither exact attainability nor unique reconstruction is certified by passing this test. Keeping original q and other coefficient projections avoids the unrelated collapse of distinct coefficient candidates.

## Cost and clause checks

At most h lifts require at most h evaluations of the closed-form extrema and at most 2h intersection tests. With fixed h<=5, the number of arithmetic operations is O(h), and all relevant sums and second-moment endpoints have O(log p) bits: offsets are below p and second moments are bounded by a constant depending on h times p². Powers 2^d have the same bit-width order for d<=ell. This is an operation-count statement, not constant-time bit complexity. Integer multiplication, division, signed floor/ceiling, canonicalization, parsing, authentication, cache handling and clause construction remain charged. Reading fixed S bits and the E prefix accounts for O(ell) bit/literal processing independently of the O(h) arithmetic count.

The construction therefore avoids traversal of all moment pairs for this individual predicate. It supplies no bound on how often the predicate rejects, how many assignments a search visits, or its total runtime relative to the complete baselines.

Negating all fixed S0 bits together with the d assigned E-prefix bits is a sound semantic clause under the authenticated source, moment and canonical-range premises. Those literals need not be a contiguous global prefix, particularly when E is auxiliary and projected coefficient bits remain unassigned. The present prefix-only transcript interface does not automatically express or certify this clause. Likewise the semantic theorem is not automatically a RUP/DRAT derivation from the current CNF. A new authenticated lemma branch or a separately verified CNF derivation must supply the missing proof interface. All model, chart-stratum, witness and complete projected-coverage checks remain necessary.

Cache reuse must preserve the exact binding stated by the design; an arc list derived for a different fixed first-moment residue, interval or arity cannot silently be reused. A checked prefix that lacks canonical completions is already excluded by range constraints and must not be counted as new pruning of valid field assignments.

## Result

The supplied arc predicate correctly implements exact prefix intersection with the necessary interval union, after explicitly defining ell as the canonical field width. It is a sound bounded next proof design without a moment grid. The scope remains prospective interval charts; no coset-support transport, implementation admission, runtime allowance or native review-gate pass is supplied by this supplemental critique.
