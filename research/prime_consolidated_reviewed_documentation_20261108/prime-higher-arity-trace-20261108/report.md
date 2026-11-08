# Higher-arity trace: expose a bounded parameter without raising row degree

Independent written review accepted the arity3/4/5 derivation, exact stratum-grid counts, projection inverse and invariant boundary. This is source-static mathematical design, not implementation or experimental evidence.

For finite target(a,b), all three normalized charts satisfy the leading norm equation u=a+2v−q², where u is the next-to-leading support coefficient. The pairs(v,q) are(A1,B0), (B0,A2), and(A2,B1) for arities3,4,5 respectively. Interval support implies −u=h*t+z modulo p with integer0<=z<=h(B−1).

The useful presentation is the invertible affine change z0=−u−h*t and w=2v+a−u. Its inverse is u=−h*t−z0 and v=(w−a−h*t−z0)/2. The old leading norm row becomes w−q²=0, up to sign; no square wire or field variable is added. The target row eliminates A0 with coefficient1, even for zero target coordinates. Every remaining source row and chart obligation is retained. In particular, quadratic rows stay quadratic.

Let D_h=h(B−1) and R_h=min(p,D_h+1). After both pivots, the unstratified parameter grids are pR3, p²R4 and p³R5, compared with p²,p³,p⁴ after the target pivot alone. These are preconstraint grid counts, not valid model counts or dimensions. Exact per-stratum counts are in design-v1.md.

The boundaries matter. Integer sums inject into residues when D_h<p. The domain already saturates at D_h=p−1, with no count reduction. Aliases begin at D_h>=p. With the existing LSB order, early range rejection at depth d requires2^d>R_h; rejection before the last field bit requires R_h<2^(ell−1). Current transforms implement only the k2 pivot, and the field compiler still allocates full field width and only canonical ranges below p. A new authenticated transform and explicit smaller-bound verifier are needed; no shorter bit block is assumed.

The affine change alone preserves the full highest-part ideal Hilbert function under its invertible linear part. That statement excludes target elimination, row changes, bounded-domain addition and Boolean compilation. The construction exposes a constrained search parameter; it does not prove regularity reduction.

A direct baseline enumerates ordered h−1 signed factor-base points, computes the final point by group subtraction and tests its x interval. It covers repeated points and costs O(|F|^(h−1)) group operations plus charged factor-base preparation, with|F|<=2B. The coefficient grid is Theta(p^(h−2)B) when nonsaturated, versus the direct O(B^(h−1)) candidate bound. Thus a naive full coefficient-grid campaign is not justified by the p/R factor; useful continuation needs pruning of remaining full-field coefficients. This is a count-scale comparison, not wall-time evidence. Its separate written review accepted the baseline and ranking consequence; intermediate identity sums remain allowed, only an identity final summand is rejected.

Next action: publish this reviewed component, then design further pruning of the remaining full-field coefficients or prove generalized support-sumset applicability to the retained coset cells; do not scale the reduced coefficient grid alone. Preserve all106+6/five-lead obligations, source strata, signed multiplicities, inverse projections and full witness/checking costs. No trials, retries, IDs or canonical mutations occurred.

Sources: design-v1.md; degree-addendum-v1.md; independent-review.md; direct-baseline-addendum-v1.md and its separate review; source-bindings.json. Exact inspected source is charts.py normalization, composition.py norm/target/interval constraints, transform.py applicability and the corrected range compiler's width/degree guards. next-bound-interface-note.md is an explicitly unreviewed implementation dependency, not accepted source code.

Factual scope audit: the original six coefficient cells are p17 coset_c=1 with degrees[8,16] and order[a2,a1,b1,b0], not interval-width-B charts. Applying this interval theorem to them requires a separate support-containment/transport proof. See scope-audit.md and exact scope-audit-bindings.json. The old software contract prohibits k3 sharing; no contract or implementation change is made here.
