#set page(paper: "a4", margin: 17mm)
#set text(size: 9.5pt)
#set par(justify: false)
= Higher-arity trace without higher-degree rows
#text(size: 11pt)[Reviewed source-only construction and its limits]

#image("diagram.svg", width: 100%)

== Exact normalized construction
For finite target (a,b), the h=3,4,5 charts satisfy u=a+2v−q², with (v,q) respectively (A1,B0), (B0,A2), (A2,B1). Interval support gives −u=h*t+z modulo p for an integer 0≤z≤h(B−1), with repeated roots counted.

Use the invertible affine change z0=−u−h*t and w=2v+a−u. Its inverse is u=−h*t−z0 and v=(w−a−h*t−z0)/2. The old leading norm row becomes w−q²=0, up to sign. No new square equation or field variable is needed. Eliminating A0 via the target row requires no division by a or b and remains affine. All other norm, stratum, interval, rationality, sign and witness obligations remain.

== Counts and thresholds that determine usefulness
Let D_h=h(B−1) and R_h=min(p,D_h+1). After both pivots the parameter grids are pR3, p²R4 and p³R5, versus p²,p³,p⁴ after the target pivot alone. These are counts before remaining constraints, not model counts or dimensions; the note gives every nonempty stratum separately.

Integer sums are injective when D_h<p, but saturation already occurs at D_h=p−1. Aliases start at D_h≥p. In LSB order a depth-d range prefix is rejected only when 2^d>R_h; rejection before the final field bit requires R_h<2^(ell−1). The current compiler still requires full-width field blocks and only ranges below p. Its smaller-bound extension and the higher-arity authenticated transform are not implemented.

The affine change alone preserves the full highest-part ideal Hilbert function. This excludes pivot elimination, row changes, domain augmentation and Boolean compilation. Degree preservation is not a claim of reduced regularity.

== Complete direct baseline and next action
Enumerate ordered h−1 signed factor-base points, compute the final point as target minus their sum, reject identity for fixed affine arity, and test its x interval. This includes repeated points and requires O(|F|^(h−1)) group operations, with |F|≤2B, plus charged factor-base preparation and outputs. In the nonsaturated regime the coefficient grid scales as p^(h−2)B versus the direct O(B^(h−1)) candidate bound. These are count scales, not measured runtimes.

Do not scale a naive full coefficient grid on the p/R reduction alone. Pursue further partial pruning of the remaining full-field coefficients, with a complete matched baseline and explicit smaller-range checking. Next investigate remaining-coefficient pruning or support-sumset applicability, not exhaustive grid scaling. No imports, implementation, trials, retries or IDs occurred.

#text(size: 8pt)[Scope audit: original six coefficient cells use p17 coset_c=1, degrees[8,16], order[a2,a1,b1,b0]; these are not interval-width-B charts. Application needs separate containment/transport proof. The old k3-sharing prohibition remains unchanged. Exact hashes: scope-audit-bindings.json.]

#text(size: 8pt)[Sources: design-v1.md, degree-addendum-v1.md and independent-review.md; direct-baseline-addendum-v1.md and direct-baseline-review.md; exact source-bindings.json. Inspected normalization: charts.py; norm/target/interval: composition.py; transform scope: transform.py; field-width/degree guards: prime_sat_range_corrected_20261101/compiler.py. Main derivation and the separate direct baseline were independently accepted.]
