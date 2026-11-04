#set page(paper: "a4", margin: (x: 18mm, y: 17mm), footer: context align(right)[#text(size: 8pt, fill: rgb("#56616d"))[TASK-20261101-bc06d9 · #counter(page).display() / 5]])
#set text(font: "DejaVu Sans", size: 10pt, lang: "en")
#set par(justify: false, leading: 0.65em)
#set heading(numbering: none)
#let note(body) = block(fill: rgb("#edf3fa"), inset: 10pt, radius: 4pt, width: 100%, body)
#let small(body) = text(size: 8.5pt, body)
#align(left)[#text(size: 23pt, weight: "bold")[IC arity/oracle threshold]\
#text(size: 14pt, fill: rgb("#35536c"))[Independent review synthesis]]
#v(5pt)
2026-11-01 · BATCH-a68666 · TASK-20261101-bc06d9
#note[
Fresh machine verification passes. The named MITM inequality holds in its
real cost model. The bundled claim needs revision for attainment and
pointwise/optimized quantifiers.
]
= 1. Machine status and semantic fidelity
Hosted workflow *41275109694*, attempt 1, pins source
#small[`7e1827b530349c633d98c96185e8196669812cb4`].
The native target receipt reports successful build and axiom audit, no
forbidden constructs and no infrastructure failure. Its dedicated audit is:
#block(inset: 7pt, fill: rgb("#f5f6f8"))[
For real m ≥ 2, β > 0 and k ≥ m/2:\
*1/2 \< costAll(m, β, k).*
]
The audit reports only propext, Classical.choice and Quot.sound. The
894-theorem project audit and built module do not certify the entire bundled
English claim. Only the MITM declaration has the dedicated named-target audit.

#table(columns: (1.15fr, 1fr, 1.9fr), inset: 6pt, stroke: 0.4pt + rgb("#c7d1db"),
[*Component*], [*Machine status*], [*Fidelity / outcome*],
[Named MITM theorem], [Passed], [Faithful scoped; real-model inequality holds],
[Blanket attainment], [Not the named declaration], [Mismatch; explicit counterexample],
[Pointwise below-half iff], [Rational thresholds only], [Mismatch; requires optimization quantifier],
[Blind full envelopes], [Not newly formalized], [Symbolic derivation holds; complete domains],
[Algorithm / PFSE bridge], [Not supplied], [Open interfaces, not an algorithm theorem])

= Owned joints are not votes
*A / TASK-20261101-bd53ca:* breaks the exact bundled claim, while confirming
the named theorem at model scope.
*B / TASK-20261101-e90be2:* holds for a derivation from definitions alone;
B did not inspect or approve the producer theorem. Their findings agree on
nonattainment and on the need to distinguish quantifiers.

#small[Internal sources: A review §§ Clause-to-declaration map, Explicit breaking
artifacts; B derivation §§1–3,7. Full paths and SHA-256 bindings are in
independence-check.json and report.md. No external literature claim is added.]
#pagebreak()
= 2. Complete real-parameter envelopes
Domain: real m ≥ 2, β > 0, k ≥ 0. Write F = costAll, G = costOne.
#block(inset: 8pt, fill: rgb("#f5f6f8"))[
F = max(max(0, 1 − β(m−1)) + kβ, 2β)\
G = max(max(0, 1 − βm) + (1+k)β, 2β)\
d = m−1−k; q#sub[F] = max(k,2); q#sub[G] = max(k+1,2)\
*F = max(1−dβ, q#sub[F]β); G = max(1−dβ, q#sub[G]β).*
]
For either q, d+q > 0. The sign split is exhaustive:
#table(columns: (0.8fr, 1fr, 1.6fr), inset: 7pt, stroke: 0.4pt + rgb("#c7d1db"),
[*Regime*], [*Infimum*], [*All minimizers β > 0*],
[k \< m−1], [q/(d+q)], [Unique β = 1/(d+q)],
[k = m−1], [1], [0 \< β ≤ 1/q],
[k > m−1], [1], [None; approach β → 0+])
Below k=m−1, F has value 2/(m+1−k) for k≤2 and k/(m−1) for k≥2.
G has value 2/(m+1−k) for k≤1 and (1+k)/m for k≥1.
Shared boundary formulas agree. Beyond k=m−1 the infimum is 1,
*not* those rational branches.

= Optimized versus pointwise
For either expression, its optimized value is below, equal to, or above 1/2
according as d is greater than, equal to, or less than q.
For F, optimized below-half means m>k+3 when k≤2, or 2k\<m−1 when k≥2.

For a fixed β, when d>q, the value is below 1/2 exactly on
1/(2d)\<β\<1/(2q). When d=q it equals 1/2 only at β=1/(2q).
When d\<q it exceeds 1/2 for every β>0.

F≤G pointwise; equality holds exactly for k≤1 or β≤1/m.
Their optimized values are equal exactly for k≤1 or k≥m−1.
Strict optimized inequality requires 1\<k\<m−1.

= MITM scope
k≥m/2 implies d\<q#sub[F], hence F>1/2 pointwise.
B derives the sharp optimized lower bounds:
#block(inset: 7pt, fill: rgb("#edf3fa"))[
I#sub[F] ≥ 4/(m+2) for 2≤m≤4; I#sub[F] ≥ m/(2(m−1)) for m≥4.\
I#sub[G] ≥ 1/2+1/m.
]
The gap above 1/2 can shrink as m grows; no positive uniform margin is
asserted for unbounded m. A lower bound of 1/2 nevertheless persists in this
model class. Source: B derivation §§1–5,8 (symbolic, not new Lean evidence).
#pagebreak()
= 3. Exact defects and nearby controls
These substitutions are copied/derived from the sealed reports, not numerical
trials or newly compiled counterexamples.
#table(columns: (0.8fr, 2.5fr), inset: 7pt, stroke: 0.4pt + rgb("#c7d1db"),
[*Test*], [*Result and scope*],
[F1: m=2,k=2], [F=max(1+β,2β), G=max(1+β,3β). Both exceed 1 for β>0 and tend to 1 as β→0+. Infimum 1; no minimizer. A and blind B agree.],
[F2: middle bound], [m=5,k=0 gives lower bound 0, never attained. Actual minimum 1/3 occurs at β=1/6. Attainment needs the missing regime restriction.],
[F3: pointwise iff], [m=5,k=1 satisfies m>k+3, but β=1 gives F=2; β=1/5 gives F=2/5. An optimized condition is not a pointwise iff. m=7,k=2,β=1 also gives 2.],
[F4: strictness], [m=3,k=2 gives both optima 1. Difference (1+k)/m−k/(m−1)=(m−1−k)/(m(m−1)); strictness requires k\<m−1.],
[F4: equality], [m=5,k=2,β=1/4 gives F=1/2. “Never below” does not imply “cannot reach.”],
[F5: lost domain], [m=2,k=3/2 gives unattained infimum 1, not the unqualified small-branch value 4/3. The theorem's k≤m−2 condition fails.])

= Planned controls retain changed hypotheses
- *Positive:* F(5,1/5,1)=2/5; an admitted subthreshold model oracle exists as a formula.
- *Boundary:* F(3,1/4,0)=1/2, not a strict tie at arbitrary β.
- *Drop H3:* attempts-only exponent 1/3 at m=3,k=0,β=1/3; full exponent 2/3.
- *Drop H1/H2:* modified costs can be 1/4 or 2/5; they are not original-model results.
- *Change H4:* at m=4, free oracle minimum 2/5 versus order-one minimum 1/2.
- *Exception scope:* there is no algorithm-to-H1–H4 coverage premise for the
  anomalous/pairing controls. No concrete curve fixture was run.

A's full declaration/hypothesis-delta table records the missing k≥2 in the
middle attainment clause, implied denominator positivity, fixed-parameter
specializations and the extra optimization quantifier. The named MITM
signature itself has no unexplained binder. H1–H4 are external modeling
obligations, not hidden theorem assumptions.

Affected target/header/note/lead bytes remain frozen. The separate corrective
task proposed on page 5 must record formalization errata and narrowed citations.
#pagebreak()
= 4. Formula-to-algorithm bridge remains explicit
#align(center)[#image("dependencies.svg", width: 98%, height: 116mm, fit: "contain")]
#small[Solid edges: cited machine check or sealed review. Dashed red edges:
missing implications, not verified algorithm coverage. Editable source:
dependencies.dot. No performance measurements are plotted.]

#table(columns: (1fr, 2.2fr), inset: 5pt, stroke: 0.4pt + rgb("#c7d1db"),
[*Interface*], [*Still required*],
[H1 / H2], [Yield distribution, hit probability, useful independent rank, target relations, stopping time and restarts],
[H3 / H4], [Actual bit-cost LA; oracle return semantics, success, output enumeration/verification, achieved cost],
[Growing arity], [m!, exact multiset correction, integer rounding, degree/row length and every m-dependent overhead uniformly],
[Full pipeline], [Family measure/sampler; setup, preprocessing, transfer, descent, recovery, final verification, peak/persistent memory, processors and communication])
For Y=L with probability μ/L, E[Y]=μ but Pr[Y>0]=μ/L: a mean does not
give a success law. Returned relation rows may all be duplicates.
Explicit output and compressed-output recovery must be priced.
For growing integer m, dropping m! needs m log m=o(n). Fixed-m
r#super[o(1)] terms are not automatically uniform in m=m(n).

With k=1, β=1/m, m>2 the formula gives F=G=2/m→0 as m grows.
This does not implement a solver or supply probability, rank, descent or memory.
The curve-algebra documentation constraint is retained: identities, conditional
model costs and total algorithmic costs are different objects.
#pagebreak()
= 5. Custody, independence and one next action
The source review outputs are sealed at
#small[`76320e68aef505292da6a9eff98aa219cca4ecc3`].
The full five-artifact snapshot is
#small[`5658c82b1de6f4fc6b44c864c91855c61c21d72e`],
parent #small[`446bf35095bf2744a817b0fad7dd3bd170bcb507`].
Native archive checks pass every declared hash, ancestry, parent and all
three IDs. The archived provisional pending-gate bytes remain unchanged;
later finalization and lifecycle commit
#small[`14886d001e60d6bd6fdecd145e79c0153b56ee98`]
make the synthesis dependency complete.

The externally pinned plan SHA-256 is
#small[`2ce285e77cd85699f47a9ee4826775fdfc2a077168000fbae30e805b81813e92`].
The checker composes one prospective addendum and returns:
#note[PASS: 2 reports; every joint owned and attested; blindness respected;
controls declared. Full command/stdout/stderr and exact hashes:
independence-check.json.]
A and B attest no sibling access. B read only the three isolated allowed
inputs; Coordinator compares now, after archive. Neither reviewer is
unblinded. Actual serving-model/effort/fork settings and backend isolation
remain unverified. The checker checks declarations, not their truthfulness.

The 67,574-byte target receipt is losslessly committed; native SHA-256:
#small[`75e52bc6bb7a034f81103166cf463d3f660b39b863177b797f7039f58394bc0a`].
Fresh maps match 75 workspace and 10 verifier entries. Historical PR2854
receipt mismatch is not relabeled. GitHub artifact 13072015323 has finite
expiry *2027-01-30T04:58:42Z*. Raw ZIP S3 archive is
*unavailable_not_attempted*; temporary copies are nondurable.
No permanent full-ZIP custody or independent kernel recheck is claimed.

= Exactly one bounded proposed action
*Versioned correction/formalization of the complete real-model target.*
Preserve frozen artifacts; record m=2,k=2 nonattainment in a dated correction,
map affected target/header/note/lead citations, and specify/prove the d/q
infimum, all minimizers and optimized/pointwise threshold regimes with F1–F5
and positive controls. Require later fresh verification and affected-joint
fidelity review before any model-to-PFSE use. This packet launches none of it.
See next-action.json.

#small[Scope/provenance: internal packet only; no new primary-literature claim or
experiment. No canonical DOT/SVG/Mermaid graph was present in the materialized
study/frontier scope; PFSE model/cost tables remain unchanged. Initial Typst
installation hit sandbox networking; an authorized network retry installed
Typst 0.15.0 in scratch. Source and PDF are documentation, not a speedup or
lower bound. Full report and exact controls: report.md. Visual check:
visual-inspection.json. Final archival is TASK-20261101-7e3b01, not this task.]

#note[No existence/nonexistence result is established. GOAL-ECDLP-001 remains open.
No source/proof/status, EV/DEC/H, commit/push/release or final publication change
is made by this synthesis.]
